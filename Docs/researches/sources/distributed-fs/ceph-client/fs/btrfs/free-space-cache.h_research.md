# sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h` declares the in-memory free-space cache data structures and public APIs used by Btrfs block-group allocation, cache v1 persistence, clustering, and discard/trim handling. It is the contract between `free-space-cache.c` and block-group, extent-tree, transaction, discard, and sanity-test code. The file was read as a complete 180-line header.

## Important APIs, Types, and Functions

The header defines `enum btrfs_trim_state` with `UNTRIMMED`, `TRIMMED`, and special bitmap-only `TRIMMING` states. `struct btrfs_free_space` is the node stored in offset and bytes rb-trees and represents either a plain free extent or a bitmap-backed region. `struct btrfs_free_space_ctl` owns the rb-trees, counters, bitmap thresholds, discardable statistics, block-group pointer, writeout mutex, and active trimming ranges. `struct btrfs_free_space_op` supplies the `use_bitmap()` policy callback. `struct btrfs_io_ctl` carries cache v1 inode page state for serialization and validation.

Exported functions cover slab lifecycle, cache inode lookup/create/remove/truncate, cache v1 load/write/wait, free-space ctl initialization, add/remove free ranges, free-space cache teardown, trim-state checks, allocator search, diagnostic dumping, cluster setup/allocation/return, trim operations for whole block groups/extents/bitmaps, fully remapped block-group trim, cache v1 active state changes, and sanity-test helpers.

## Control Flow

This header does not implement complex runtime flow, but it exposes the entry points used in the normal sequence: initialize per-block-group `btrfs_free_space_ctl`, load cache v1 or rebuild free space, add/remove free ranges as extents are allocated and freed, optionally form and consume clusters, write cache v1 during transaction commit, and trim or discard untrimmed free ranges. Inline helpers provide cheap trim-state checks and signal/freezer interruption detection for trim loops.

## State and Persistence Behavior

The state declared here is runtime state except for `btrfs_io_ctl`, which describes the transient page cursor used to persist or reload the v1 free-space cache inode. `discardable_extents` and `discardable_bytes` are arrays indexed by `BTRFS_STAT_CURR` and `BTRFS_STAT_PREV` so callers can publish delta-style discard statistics. The cache v1 persistence APIs manipulate hidden free-space inodes and their tree-root header items, while the rb-tree/bitmap structures themselves are in-memory caches.

## Dependencies and Integration Points

The header includes Linux rb-tree, list, spinlock, mutex, freezer, and `fs.h` definitions. It forward declares inode, page, path, transaction, block-group trim, and fs_info types to avoid over-including allocator internals. Integration points are block-group allocation, transaction commit, the discard controller, free-space cache v1 mount options, the Btrfs trim ioctl path, and optional sanity tests.

## Risks and Edge Cases

Callers must hold the correct locks around `btrfs_free_space_ctl` and cluster mutation; the header exposes structures with many counters that can drift if updates skip the implementation helpers. `BTRFS_TRIM_STATE_TRIMMING` is meaningful only for bitmap trim progression, so treating it like a durable trimmed state would lose discard work. The `btrfs_io_ctl` page array and cursor fields are tightly coupled to the v1 on-disk format and should not be reused generically.

## Test Signals

Compile coverage should validate all prototypes against their definitions and include-order use from block-group, extent-tree, discard, and tests. Runtime signals come from free-space cache sanity tests, allocation/free round trips, trim interruption tests using fatal signal or freezer paths, and mount tests that enable, disable, clear, and rewrite cache v1.
