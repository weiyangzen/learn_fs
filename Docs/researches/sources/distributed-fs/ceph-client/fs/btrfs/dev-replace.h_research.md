# sources/distributed-fs/ceph-client/fs/btrfs/dev-replace.h

## Purpose

`dev-replace.h` declares the internal Btrfs device-replacement API used by mount, transaction commit, ioctl handling, unmount, resume, block mapping, and bio accounting code.

## Important APIs, Types, and Functions

The header forward declares ioctl arguments, filesystem and transaction structures, device replace state, block groups, and devices. It declares initialization, transaction writeback, ioctl start, status, cancel, unmount suspend, async resume, ongoing-state query, zoned block-group copy completion, and bio counter helpers. It also provides `btrfs_bio_counter_dec()` as an inline wrapper around `btrfs_bio_counter_sub()`.

## Control Flow

There is no substantial executable control flow beyond the decrement inline. The API shape mirrors the replacement lifecycle: initialize from disk, start through ioctl, persist changes during transaction commit, report status, cancel/suspend/resume as lifecycle events require, and coordinate block I/O with replacement removal.

## State and Persistence Behavior

The header owns no state. It exposes functions that operate on `fs_info->dev_replace` and device tree persistent state. The bio counter helpers indicate that replacement finishing/removal synchronizes with in-flight bios.

## Dependencies and Integration Points

Integration points include ioctl definitions, transaction commit, device management, block group handling, unmount/remount paths, and low-level bio mapping. The `__pure` ongoing query can be used by fast paths that only inspect replacement state.

## Risks and Edge Cases

Callers must use the lifecycle APIs under the expected mount/exclusive-operation context; direct manipulation of `struct btrfs_dev_replace` would bypass locking and persistence. Bio counter increment/decrement must remain balanced or finishing can hang waiting for in-flight bios.

## Test Signals

Compile coverage should catch signature drift. Runtime tests should watch for balanced bio counters, correct state after mount/replay/resume, and proper interaction between ioctl operations and transaction writeback.
