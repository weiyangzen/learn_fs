# sources/distributed-fs/ceph-client/fs/btrfs/zoned.h

## Purpose

`zoned.h` declares the Btrfs zoned-mode API and defines the per-device zoned information structure plus inline helpers. It lets the rest of Btrfs compile against zoned functionality whether `CONFIG_BLK_DEV_ZONED` is enabled or not, using real prototypes in zoned builds and conservative stubs otherwise.

## Important APIs, Types, And Functions

`struct btrfs_zoned_device_info` stores zone size, shift, count, maximum active zones, reserved active zones, active-zone budget, bitmaps for sequential/empty/active zones, optional zone cache, and cached superblock log zones. The header declares mount/device discovery, superblock log, allocation, reset, block-group loading, IO, active-zone, relocation, reclaim, and stats functions implemented in `zoned.c`.

When zoned support is disabled, inline stubs mostly return success for no-op functions on non-zoned filesystems, return `-EOPNOTSUPP` for operations that cannot be emulated, and reject a zoned filesystem in `btrfs_check_zoned_mode()`.

Inline helpers include `btrfs_dev_is_sequential()`, `btrfs_dev_is_empty_zone()`, zone empty bit setters, `btrfs_check_device_zone_type()`, `btrfs_check_super_location()`, `btrfs_can_zone_reset()`, metadata IO lock wrappers, tree-log/data-relocation lock and clear helpers, and `btrfs_zoned_bg_is_full()`.

## Control Flow And Integration

Mount and device open paths call the declared discovery and validation APIs. Allocation code uses allocatable-zone and active-zone helpers. Metadata writeback uses the zoned meta IO lock wrappers and write-pointer checks. Data writeback and ordered extent completion use zone append and physical-recording APIs. Relocation and reclaim use the reservation, release, finish, activate, and reset declarations.

The `#ifdef CONFIG_BLK_DEV_ZONED` boundary keeps call sites simple: most code can call zoned helpers unconditionally, and the header resolves them to no-ops or errors in non-zoned builds.

## State And Persistence Behavior

The header defines the in-memory state container for zone geometry, bitmaps, cache, and active-zone budget. Inline helpers mutate empty-zone bits and guard locks but do not persist state directly. Persistence is achieved by `zoned.c` through device write pointers, chunk/block-group metadata, and superblock log zones.

## Dependencies

It depends on Linux block zoned headers, atomic, spinlock, mutex, sequence-file support, and Btrfs `messages.h`, `volumes.h`, `disk-io.h`, `block-group.h`, and `btrfs_inode.h`. This coupling reflects the cross-cutting nature of zoned support across devices, IO, metadata writeback, and block-group allocation.

## Risks And Edge Cases

Stub behavior must match caller expectations in non-zoned builds; returning success for no-op paths is correct only when the filesystem is not zoned. Inline bit helpers assume positions align to the device zone size. `btrfs_check_device_zone_type()` must allow regular devices in zoned filesystems for emulation but reject zoned devices in non-zoned filesystems. Lock wrappers must only lock in zoned mode or they would impose unnecessary ordering constraints on regular filesystems.

## Test Signals

Build both with and without `CONFIG_BLK_DEV_ZONED`. Exercise non-zoned stubs by mounting regular filesystems in a kernel without zoned support and by rejecting zoned filesystems. Runtime zoned tests should validate inline helpers through allocation, reset, metadata writeback, tree-log clearing, data relocation serialization, and full block-group detection.
