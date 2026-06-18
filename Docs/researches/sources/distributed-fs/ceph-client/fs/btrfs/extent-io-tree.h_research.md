# sources/distributed-fs/ceph-client/fs/btrfs/extent-io-tree.h

## Purpose
`extent-io-tree.h` defines the range-state bits, owner identifiers, core data structures, and public helpers for Btrfs extent I/O trees. These trees are the shared mechanism for tracking per-byte in-memory state across inode I/O, metadata, transaction, relocation, logging, and device-allocation paths.

## Important APIs, types, and functions
The header defines state bits such as `EXTENT_DIRTY`, `EXTENT_LOCKED`, `EXTENT_DIO_LOCKED`, `EXTENT_DELALLOC`, `EXTENT_BOUNDARY`, reservation-clearing bits, `EXTENT_DELALLOC_NEW`, `EXTENT_FINISHING_ORDERED`, `EXTENT_ADD_INODE_BYTES`, `EXTENT_CLEAR_ALL_BITS`, and control bit `EXTENT_NOWAIT`. It also aliases device-allocation states `CHUNK_ALLOCATED`, `CHUNK_TRIMMED`, and `CHUNK_STATE_MASK`. Owner IDs include filesystem pinned/excluded extents, btree inode I/O, inode I/O, relocation blocks, transaction dirty pages, root dirty log pages, file extents, log csum ranges, selftests, and device allocation state. Core structures are `struct extent_io_tree` and `struct extent_state`; public helpers cover init/release, set/clear/convert, lock/try-lock/unlock, DIO locks, queries, counting, changeset recording, cached traversal, and slab-cache lifecycle.

## Control flow
Callers initialize a tree with an owner, then set, clear, convert, query, or lock inclusive byte ranges. Inline wrappers specialize common operations such as normal extent locks, DIO locks, unlocks, and clearing dirty/delalloc accounting bits. The implementation uses owner information to interpret the union field as either `fs_info` or inode and to route inode-owned state changes through delalloc accounting hooks.

## State and persistence
The data structures describe runtime-only state: an rb-tree of range records protected by a spinlock, plus each range's waitqueue/refcount/bitmask. The owner value is essential for safe interpretation of the union pointer. Although not persisted directly, these states gate persistent writeback, transaction cleanup, metadata dirty tracking, and allocation/discard decisions.

## Dependencies and integration points
The header depends on Linux rbtree, spinlock, refcount, list, waitqueue, and Btrfs misc helpers. It is included by extent I/O, disk I/O, inode, transaction, block-group/device allocation, relocation, and selftest code that needs shared range-state management.

## Risks and test signals
Risks include adding new bits in the wrong position relative to `EXTENT_NOWAIT`, confusing control bits with stored state bits, using `EXTENT_LOCKED`/`EXTENT_BOUNDARY` semantics for device allocation trees, passing the wrong owner, leaking cached `extent_state` references, and treating inclusive `end` values as exclusive. Test signals include compile coverage for all inline wrappers, extent-state selftests, direct and buffered writeback tests, DIO lock tests, device allocation state tests, and debug builds that check range oddities and leaks.
