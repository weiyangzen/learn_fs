# sources/distributed-fs/ceph-client/fs/btrfs/file-item.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file-item.h` is the public interface for Btrfs file extent item and checksum item helpers implemented mostly by `file-item.c`. It exposes inline layout helpers for inline file extents and prototypes used by bio submission, ordered extent completion, tree logging, file extent replacement, inode truncation, and extent-map construction. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

The layout macro `BTRFS_FILE_EXTENT_INLINE_DATA_START` defines where inline extent payload begins inside `struct btrfs_file_extent_item`. Inline helpers include `BTRFS_MAX_INLINE_DATA_SIZE()`, `btrfs_file_extent_inline_item_len()`, `btrfs_file_extent_inline_start()`, and `btrfs_file_extent_calc_inline_size()`. They abstract the relationship between B-tree item size, file extent header size, filesystem node size, and inline payload bytes.

Declared checksum APIs include `btrfs_del_csums()`, `btrfs_lookup_bio_sums()`, `btrfs_insert_data_csums()`, `btrfs_csum_one_bio()`, `btrfs_alloc_dummy_sum()`, `btrfs_lookup_csums_range()`, `btrfs_lookup_csums_list()`, and `btrfs_lookup_csums_bitmap()`. Declared file extent APIs include `btrfs_insert_hole_extent()`, `btrfs_lookup_file_extent()`, `btrfs_extent_item_to_extent_map()`, `btrfs_inode_clear_file_extent_range()`, `btrfs_inode_set_file_extent_range()`, `btrfs_inode_safe_disk_i_size_write()`, and `btrfs_file_extent_end()`.

The header forward-declares the involved Btrfs and block-layer structures rather than including their full definitions: `extent_map`, `btrfs_file_extent_item`, `btrfs_fs_info`, `btrfs_path`, `btrfs_bio`, `btrfs_trans_handle`, `btrfs_root`, `btrfs_ordered_sum`, and `btrfs_inode`.

## Control Flow

The header has no standalone runtime flow. It defines the callable surface for several flows: bio reads preload checksum buffers through `btrfs_lookup_bio_sums()`, write bios attach ordered sums through `btrfs_csum_one_bio()` or `btrfs_alloc_dummy_sum()`, ordered extent completion persists sums through `btrfs_insert_data_csums()`, tree-log code deletes and reinserts checksum ranges, and file extent mutation paths update file-extent maps and `disk_i_size` using the inode/file extent helpers.

The inline helpers are used wherever inline extents are created, copied, or interpreted. Their control role is to keep item-size calculations centralized so callers do not duplicate offset arithmetic against the on-disk `btrfs_file_extent_item` format.

## State and Persistence Behavior

This header owns no storage and performs no persistence directly. Its declared functions operate on persistent Btrfs metadata through transaction handles and B-tree paths, and on runtime structures such as `struct btrfs_bio`, ordered sums, extent maps, and inode extent-state trees. The inline-size helpers encode on-disk layout constraints, so changes to them affect how inline file data is packed in B-tree leaves.

## Dependencies and Integration Points

The header includes Linux block/list definitions, the UAPI Btrfs tree format, `ctree.h`, and `ordered-data.h`. It is included by Btrfs bio, inode, file, tree-log, reflink, extent-map, and writeback code that needs checksum or file-extent item helpers.

Integration points are transaction-safe B-tree mutation, ordered extent checksum lifetime, file extent map caching, inline extent creation, tree-log replay, reflink checksum logging, and `NO_HOLES` versus explicit-hole behavior.

## Risks and Edge Cases

The main risks are interface contract drift and layout drift. The inline data offset must match the UAPI on-disk structure; a wrong size calculation can corrupt inline file extent items or reject valid inline writes. The prototypes expose functions with strict alignment, locking, and transaction expectations that are not enforceable by the compiler. Callers must also respect checksum buffer sizing and list ownership conventions.

## Test Signals

Compile coverage across Btrfs is the first signal because this header is a shared ABI inside the filesystem. Runtime signals include inline extent write/read tests, compressed inline extents, checksum lookup and insertion tests, log replay with checksums, hole punching/truncation with explicit holes and `NO_HOLES`, and large sectorsize/subpage coverage that stresses the inline length and sectorsize alignment helpers.
