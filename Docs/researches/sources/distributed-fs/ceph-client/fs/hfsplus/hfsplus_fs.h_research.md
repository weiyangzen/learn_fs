# sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_fs.h

## Purpose
`hfsplus_fs.h` is the central private interface for the HFS+ filesystem driver. It ties the Linux VFS-facing code to HFS+ on-disk structures from `hfsplus_raw.h`/`hfs_common.h`, declares the in-memory superblock, inode, B-tree, and search-state types, exposes cross-file function prototypes, and defines helper macros for dirty metadata, timestamp conversion, B-tree locking, and bounded B-node access.

## Important APIs, types, and functions
The main runtime types are `struct hfsplus_sb_info`, `struct hfsplus_inode_info`, `struct hfs_btree`, `struct hfs_bnode`, `struct hfs_find_data`, and `struct hfsplus_readdir_data`. `HFSPLUS_SB()` and `HFSPLUS_I()` recover private state from VFS objects. B-tree state includes catalog/extents/attributes tree identifiers, root/leaf/node counters, node size geometry, hash-cache state, and `tree_lock`; B-node state tracks record count, type, height, links, lock/error/new/dirty/deleted flags, refcount, and backing pages.

The header publishes the filesystem's internal API surface: attribute-tree functions, bitmap alloc/free, B-tree open/write/reserve/allocation, B-node read/write/copy/move/hash/refcount helpers, B-record search/insert/remove helpers, catalog compare/build/create/delete/rename helpers, extent mapping/truncation, inode read/write/fsync/fileattr helpers, mount option parsing/showing, partition-map probing, superblock commit, Unicode conversion/hash/compare helpers, and wrapper I/O helpers.

Inline helpers include `hfsplus_mark_inode_dirty()`, `hfsplus_min_io_size()`, `hfsplus_cat_thread_size()`, HFS+ timestamp conversions, `hfsplus_btree_lock_class()`, `is_bnode_offset_valid()`, and `check_and_correct_requested_length()`.

## Control flow
Most implementation files include this header and communicate through its structures. Mount setup fills `hfsplus_sb_info`, opens B-trees, and creates metadata inodes. VFS inode operations use `hfsplus_inode_info` to cache first and recently-used extents, resource-fork links, creation time, BSD flags, open-directory state, and physical size. B-tree code moves through `hfs_find_data`: callers provide a search key, find code binds a tree/B-node and record offsets, and record helpers read or update entries.

Dirtying is split by metadata domain. `hfsplus_mark_inode_dirty()` sets a domain bit on the inode private flags and then calls `mark_inode_dirty()`. Later writeback/fsync paths inspect the catalog, extents, allocation, and attributes dirty bits to decide which metadata inodes and trees must be flushed.

## State and persistence behavior
The header separates mutable superblock state by lock: allocation counters use `alloc_mutex`; volume-header counters such as `next_cnid`, `file_count`, and `folder_count` use `vh_mutex`; delayed sync work is protected by `work_lock`. Inode extent allocation state is protected by `extents_lock`; some inode flags are atomic bitops; `open_dir_list` has its own spinlock. Persistent state represented here includes the volume header, backup volume header, allocation bitmap, catalog/extents/attributes B-trees, fork extents, BSD file flags, CNIDs, and HFS+ timestamps.

Timestamp conversion intentionally maps 1904-based HFS+ timestamps to Linux time by subtracting `HFSPLUS_UTC_OFFSET` in unsigned 32-bit space, matching the driver's historic 1970-2106 behavior.

## Dependencies and integration points
The file depends on Linux VFS, buffer heads, block devices, fs context parsing, mutex/spinlock/list/RCU infrastructure, NLS tables, and HFS+ wire-format definitions. It is the integration point for `super.c`, `inode.c`, `catalog.c`, `extents.c`, `btree.c`, `bnode.c`, `bfind.c`, `brec.c`, `bitmap.c`, `attributes.c`, `unicode.c`, `options.c`, `ioctl.c`, `part_tbl.c`, and `wrapper.c`.

## Risks and test signals
Risks include stale or incorrectly scoped dirty bits, inconsistent lock ordering across catalog/extents/attributes trees, B-node offset correction hiding corruption, timestamp wrap surprises, resource-fork/main-inode confusion, and prototypes drifting from implementation behavior. Test signals should include mount/write/fsync/unmount cycles, concurrent metadata updates, B-tree node-size variants, corrupted B-node offsets, HFSX casefold mounts, resource fork operations, attribute-tree creation/failure paths, and timestamp edge cases around 1970 and 2106.
