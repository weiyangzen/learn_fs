# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.c

## Purpose
`xfs_dir2.c` is the generic XFS directory front end. It initializes directory/attribute geometry at mount time, selects the active directory format, dispatches create/lookup/remove/replace operations to shortform/block/leaf/node implementations, validates inode numbers and names, handles directory block growth/shrink, supports ascii-ci hashing/comparison, provides optional live update hooks, and implements higher-level child link/unlink/rename/exchange semantics including parent pointer updates.

## Important APIs, Types, And Functions
Global names `xfs_name_dot` and `xfs_name_dotdot` represent `"."` and `".."`. `xfs_mode_to_ftype()` maps inode mode to on-disk dirent type. `xfs_da_mount()` and `xfs_da_unmount()` allocate and free `m_dir_geo` and `m_attr_geo`. `xfs_dir2_format()` detects shortform, block, leaf, or node format from inode fork format and data-fork EOF.

Directory operation entry points include `xfs_dir_init()`, `xfs_dir_createname()`, `xfs_dir_lookup()`, `xfs_dir_removename()`, `xfs_dir_replace()`, and `xfs_dir_canenter()`, with `_args` variants for prebuilt `xfs_da_args`. Utility functions include `xfs_dir2_grow_inode()`, `xfs_dir2_shrink_inode()`, `xfs_dir2_namecheck()`, `xfs_dir2_hashname()`, and `xfs_dir2_compname()`. Higher-level child APIs include `xfs_dir_create_child()`, `xfs_dir_add_child()`, `xfs_dir_remove_child()`, `xfs_dir_exchange_children()`, and `xfs_dir_rename_children()`.

## Control Flow
Mount setup computes directory geometry from superblock blocklog and dirblklog, selecting v2/v3 header sizes based on CRC support, then derives data/leaf/free logical block locations. Attribute geometry is one filesystem block and reuses node header sizing.

Normal directory operations allocate an `xfs_da_args`, fill name, hash, filetype, fork, transaction, owner, and block reservation fields, and dispatch by `xfs_dir2_format()`. Lookups take a data-map shared lock, translate the internal `-EEXIST` lookup success convention into zero, and optionally return the real case-insensitive name. Add with `inum == 0` becomes a space-only `JUSTCHECK`.

Child create/add/remove/rename functions wrap raw dirent updates with link count maintenance, timestamp logging, `.`/`..` initialization or replacement, unlinked-list removal for `O_TMPFILE`/whiteouts, parent pointer attr operations, and live update hook calls.

## State And Persistence
Persistent state includes directory fork format, directory blocks, link counts, inode timestamps, parent pointer attributes, and directory inode size. `xfs_dir2_grow_inode()` grows data/free spaces and updates `i_disk_size` for data space. `xfs_dir2_shrink_inode()` unmaps blocks and reduces `i_disk_size` only when the removed data block was the trailing block. In-memory mount geometry persists for the mount lifetime.

## Dependencies And Integration Points
This file integrates VFS directory operations with shortform/block/leaf/node directory files, DA btree mapping, bmap, transactions, inode link helpers, parent pointer attr code, AG inode unlink helpers, health/error injection, and optional live hooks for online fsck. It depends on inode locks being held by higher layers for mutation APIs.

## Risks
Format detection must match actual fork layout; an incorrect EOF or `i_disk_size` can route updates to the wrong implementation. Link count and `..` update ordering during rename/exchange is subtle, especially for cross-directory directory renames and whiteouts. Parent pointer updates must remain consistent with dirent changes. `xfs_dir2_shrink_inode()` can return `-ENOSPC` when a no-reservation removal would require bmap btree changes; callers must leave an empty but consistent block.

## Test Signals
Tests should cover transitions among shortform, block, leaf, and node directories; ascii-ci exact and case-only lookups; invalid inode/name rejection; directory creation/removal with link count checks; `O_TMPFILE` link insertion; whiteout rename; cross-directory rename of directories with `..` updates; exchange of files/directories; parent pointer enabled and disabled modes; live hook enablement; and no-space removals that cannot shrink mappings.
