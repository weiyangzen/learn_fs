# sources/distributed-fs/ceph-client/fs/fs_pin.c

## Purpose
`fs_pin.c` implements generic filesystem/mount pin lists and kill synchronization. Pins are attached to both a superblock and a mount so teardown code can locate callback-bearing objects that must be killed before the mount or group disappears.

## Important APIs, Types, and Functions
- `pin_insert()` adds an `fs_pin` to `s_pins` and `mnt_pins`.
- `pin_remove()` removes both hlist links and wakes waiters after marking the pin done.
- `pin_kill()` runs a pin's `kill()` callback exactly once, or waits uninterruptibly while another thread kills it.
- `mnt_pin_kill()` drains all pins on a `struct mount`.
- `group_pin_kill()` drains all pins from a superblock/group hlist.

## Control Flow
Insertion and removal are serialized by the global `pin_lock`. Killers repeatedly take an RCU read lock, sample the first hlist node with `READ_ONCE()`, and call `pin_kill()`. `pin_kill()` uses the pin waitqueue lock to transition `done` from unset to `-1` for the killer, calls the supplied callback outside RCU, or sleeps until `pin_remove()` sets `done` positive and wakes waiters.

## State and Persistence
State lives in `struct fs_pin`: two hlist links, a waitqueue, a `done` field, and a kill callback. There is no on-disk state. The object lifetime is externally owned, and waiters rely on the `done` protocol and RCU to avoid use-after-free while a kill callback is in progress.

## Dependencies and Integration Points
The file depends on VFS mount internals (`mount.h`), superblock pin lists, spinlocks, waitqueues, and RCU. It is an infrastructure primitive for code that pins mounts or superblocks until asynchronous cleanup can safely run.

## Risks
Correctness depends on the kill callback eventually calling `pin_remove()` or otherwise completing the state transition. A callback that sleeps indefinitely will block all drainers. The global lock is small-scope but serializes all pin list mutation. Kill paths use uninterruptible sleep, so deadlocks in callback teardown show up as stuck tasks.

## Test Signals
Stress mount teardown, namespace teardown, repeated concurrent killers, and callback paths that remove pins during drain. Lockdep/RCU diagnostics and hung-task detection are the primary signals.
