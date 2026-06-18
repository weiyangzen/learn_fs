# sources/distributed-fs/ceph-client/fs/fuse/dev_uring_i.h

## Purpose
`dev_uring_i.h` defines the private data structures and inline integration points for the optional FUSE io_uring transport.

## Important APIs, Types, and Functions
- `enum fuse_ring_req_state` enumerates entry lifecycle states from invalid through commit, available, assigned request, userspace, teardown, and released.
- `struct fuse_ring_ent` binds userspace header/payload buffers, a queue, an `io_uring_cmd`, list node, state, and assigned `fuse_req`.
- `struct fuse_ring_queue` owns per-CPU entry lists, request queues, background queues, a processing hash, active background count, lock, and stopped flag.
- `struct fuse_ring` owns the connection pointer, queue array, max payload size, stop waitqueue, async teardown work, queue refcount, and readiness.
- Prototypes connect `dev_uring.c` to FUSE core.
- Inline stubs preserve buildability when `CONFIG_FUSE_IO_URING` is disabled.

## Control Flow
When enabled, core FUSE code calls the declared helpers for readiness checks, request queueing, pending request removal, timeout scans, abort, stop waiting, and destruction. The inline `fuse_uring_abort()` checks for a ring and live queue refs, then ends queued requests and stops queues. `fuse_uring_wait_stopped_queues()` waits for all queue refs to reach zero. When disabled, all helpers become no-op or false-returning stubs.

## State and Persistence
The header defines in-memory state only. Queue refs intentionally outlive active entries until teardown releases all io_uring-visible objects. No state persists beyond connection destruction.

## Dependencies and Integration Points
It depends on `fuse_i.h`, `CONFIG_FUSE_IO_URING`, io_uring command types through the implementation, and FUSE core request fields such as `ring_queue` and `ring_entry`.

## Risks
The header encodes the locking and lifetime model used by `dev_uring.c`; misuse of entry states or queue locks can lead to stale direct pointers from cancel paths. Disabled stubs must match enabled semantics enough that core code can call them unconditionally without behavioral surprises.

## Test Signals
Compile both enabled and disabled configs, confirm abort/wait paths do not hang with no ring, and validate that queue refs reach zero after daemon cancellation or connection abort.
