# sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.h

## Purpose

`delalloc-space.h` is the public Btrfs internal interface for delayed allocation data and metadata reservation helpers. It exposes the reservation, release, and adjustment operations implemented in `delalloc-space.c` to write paths, direct I/O, ordered extent handling, and extent-state cleanup code.

## Important APIs, Types, and Functions

The header forward declares `extent_changeset`, `btrfs_inode`, and `btrfs_fs_info`, includes Linux integer types, and declares the core API: data-only reservation/allocation helpers, data reservation release with and without qgroup accounting, full delalloc reserve/release helpers, metadata-only reserve/release helpers, extent-lifecycle release, and reserved-extent shrink adjustment.

## Control Flow

There is no executable control flow in this header. Its declarations encode the expected call patterns: callers either reserve data plus metadata with `btrfs_delalloc_reserve_space()` and release with `btrfs_delalloc_release_space()`, or they reserve pieces separately when direct I/O, preallocation, or lower-level cleanup needs finer control.

## State and Persistence Behavior

The header owns no state. The pointer types in its signatures show that callers must pass inode-owned reservation state and optional `extent_changeset` records so the implementation can account per-inode, per-space-info, and per-qgroup reservations.

## Dependencies and Integration Points

Integration points are Btrfs inode write paths, quota groups, direct I/O, ordered extents, extent-state hooks, and ENOSPC reservation logic. The header is intentionally narrow so most call sites do not need the implementation's block-reserve and space-info internals.

## Risks and Edge Cases

The API splits quota-aware and noquota releases; choosing the wrong release function can either leak qgroup reservation or free quota that was not accurately tracked. Metadata reservation and extent release are separate calls because `outstanding_extents` has staged ownership, so API users must follow the documented lifecycle.

## Test Signals

Compile coverage should catch signature drift across write/direct-I/O users. Behavioral coverage should verify balanced reserve/release calls for buffered writes, direct writes, partial writes, failed writes, qgroup-enabled filesystems, and NODATASUM inodes.
