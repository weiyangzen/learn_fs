# sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h` declares inode item, inode reference, extended reference, lookup, and truncate helper APIs for Btrfs. It also defines the truncate-control structure used to parameterize item removal and file extent truncation. The file was read as a complete 116-line header.

## Important APIs, Types, and Functions

The header defines `BTRFS_NEED_TRUNCATE_BLOCK`, returned when the caller must truncate the final block outside `btrfs_truncate_inode_items()`. `struct btrfs_truncate_control` carries inputs (`inode`, `new_size`, `ino`, `min_type`, `skip_ref_updates`, `clear_extent_range`) and outputs (`extents_found`, `last_size`, `sub_bytes`) for truncation. Inline helpers `btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` convert between the on-disk u64 inode flag representation and split runtime flag fields. `btrfs_extref_hash()` computes extended inode ref key offsets using CRC32C over parent objectid and name.

Declared APIs include `btrfs_truncate_inode_items`, `btrfs_insert_inode_ref`, `btrfs_del_inode_ref`, `btrfs_insert_empty_inode`, `btrfs_lookup_inode`, `btrfs_lookup_inode_extref`, `btrfs_find_name_in_backref`, and `btrfs_find_name_in_ext_backref`.

## Control Flow

This header does not implement the full flows, but it defines how callers drive them. Creation paths call `btrfs_insert_empty_inode()` and then update inode fields. Link/unlink paths insert or delete inode refs by name, with implementation fallback to extended refs as needed. Truncate and eviction paths fill `btrfs_truncate_control`, call `btrfs_truncate_inode_items()`, inspect output counters, and handle `BTRFS_NEED_TRUNCATE_BLOCK` or `-EAGAIN` where appropriate. Inline flag helpers are pure conversions.

## State and Persistence Behavior

The header describes persistent btree item manipulation but owns no storage. `btrfs_truncate_control` is caller-owned transient state that reports how much inode byte accounting should be adjusted and where truncation stopped. Inode flag combination/splitting maps runtime flags to the on-disk inode item flag field. Extended reference hash values are persisted as key offsets for `BTRFS_INODE_EXTREF_KEY` items.

## Dependencies and Integration Points

The header includes Linux types and CRC32C and forward declares fscrypt strings, extent buffers, transactions, roots, paths, keys, inode/extref types, Btrfs inodes, and the truncate control. It integrates with directory/link management, inode creation, inode lookup, file truncation, free-space cache inode truncation, and fscrypt-aware filename handling.

## Risks and Edge Cases

`btrfs_extref_hash()` is a keying helper, not a uniqueness guarantee; implementations must scan hash-collision records. Callers of `btrfs_truncate_inode_items()` must set `inode` when `clear_extent_range` is true. `skip_ref_updates` can be dangerous outside specialized contexts. The split/combined inode flags must stay compatible with on-disk format and runtime read-only flag handling.

## Test Signals

Compile coverage should include fscrypt-name users, truncate callers, and inode ref callers. Runtime signals include hard-link and unlink tests, extended inode ref overflow/collision tests, inode flag round-trip tests, truncate-control behavior for normal file truncate and free-space cache inode truncate, and crash-consistency checks for inode ref and file extent item mutation.
