# sources/distributed-fs/ceph-client/fs/btrfs/disk-io.h

## Purpose
`disk-io.h` is the public internal interface for Btrfs disk I/O, root management, superblock handling, mount lifecycle, metadata buffering, log-tree setup, transaction cleanup, and root objectid allocation.

## Important APIs, types, and functions
The header defines superblock mirror constants `BTRFS_SUPER_MIRROR_MAX`, `BTRFS_SUPER_MIRROR_SHIFT`, fixed `BTRFS_BDEV_BLOCKSIZE`, and helper `btrfs_sb_offset`. It declares mount/lifecycle APIs (`open_ctree`, `close_ctree`, `btrfs_init_fs_info`, `btrfs_free_fs_info`, `btrfs_start_pre_rw_mount`), metadata read/write validation (`read_tree_block`, `btrfs_find_create_tree_block`, `btrfs_validate_extent_buffer`, `btrfs_buffer_uptodate`, `btrfs_read_extent_buffer`, `btree_csum_one_bio`, `btrfs_mark_buffer_dirty`), superblock work (`btrfs_check_super_csum`, `btrfs_validate_super`, `btrfs_check_features`, `write_all_supers`, `btrfs_commit_super`), root APIs (`btrfs_read_tree_root`, `btrfs_insert_fs_root`, `btrfs_get_fs_root`, `btrfs_get_new_fs_root`, `btrfs_get_fs_root_commit_root`, `btrfs_global_root_*`, `btrfs_csum_root`, `btrfs_extent_root`, `btrfs_put_root`, `btrfs_create_tree`), and cleanup/objectid helpers.

## Control flow
Callers use the declarations to enter the filesystem through `open_ctree`, fetch or create roots during normal operation, validate/read metadata blocks during tree walks, mark metadata dirty under active transactions, balance dirty btree pages, commit superblocks, and leave through `close_ctree`. Inline `btrfs_grab_root` increments a root ref only if the root is still alive, which is the common fast path for root-cache lookups.

## State and persistence
The header has no storage of its own, but its API governs persistent metadata and runtime state in `fs_info`, roots, extent buffers, superblocks, and transactions. `btrfs_sb_offset` encodes the fixed locations of primary and backup superblock mirrors, which are part of the on-disk format contract.

## Dependencies and integration points
It includes Btrfs core definitions from `ctree.h`, bio support, and ordered-data declarations, and forward-declares core VFS/block/Btrfs structures. It is included across tree walking, transaction, block-group, export, and mount code that needs common disk I/O and root access.

## Risks and test signals
API misuse risks include taking roots without balancing `btrfs_put_root`, marking buffers dirty outside a matching transaction, reading tree blocks with an incomplete parent check, and using global-root helpers with the wrong root key for extent-tree-v2. Test signals include compile coverage across Btrfs, root ref leak checks, metadata read corruption tests, superblock mirror offset tests, and transaction dirty-buffer assertions under debug builds.
