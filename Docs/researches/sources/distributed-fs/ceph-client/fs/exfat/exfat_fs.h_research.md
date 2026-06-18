# sources/distributed-fs/ceph-client/fs/exfat/exfat_fs.h

## Purpose
`exfat_fs.h` is the private in-kernel contract for the exFAT driver. It defines driver-wide constants, conversion macros, in-memory superblock and inode structures, directory/name helper structures, attribute/mode conversion helpers, cluster/FAT/bitmap geometry helpers, operation-table declarations, and prototypes for all exFAT implementation files.

## Important APIs, types, and functions
Important types include `enum exfat_error_mode`, `struct exfat_dentry_namebuf`, `struct exfat_uni_name`, `struct exfat_chain`, `struct exfat_hint_femp`, `struct exfat_hint`, `struct exfat_entry_set_cache`, `struct exfat_dir_entry`, `struct exfat_mount_options`, `struct exfat_sb_info`, and `struct exfat_inode_info`.

Important helpers include `EXFAT_SB()`, `EXFAT_I()`, `exfat_forced_shutdown()`, `exfat_mode_can_hold_ro()`, `exfat_make_mode()`, `exfat_make_attr()`, `exfat_save_attr()`, `exfat_is_last_sector_in_cluster()`, `exfat_cluster_to_sector()`, `exfat_sector_to_cluster()`, `is_valid_cluster()`, `exfat_ondisk_size()`, `exfat_cluster_walk()`, and `exfat_chain_advance()`.

Macros define entry-set indices, dentry type classes, max name sizes, cluster/block/dentry conversions, FAT entry offsets, allocation bitmap offsets, directory cache sizing, and the `EXFAT_FLAGS_SHUTDOWN` runtime flag. Prototypes expose superblock, FAT, bitmap, file, namei, cache, dir, inode, NLS, and misc APIs.

## Control flow
The header has no independent runtime flow, but it defines common call contracts. Code generally converts VFS objects to exFAT objects with `EXFAT_SB()`/`EXFAT_I()`, uses geometry macros to translate file offsets to clusters/sectors/dentries, walks chains through `exfat_cluster_walk()`/`exfat_chain_advance()`, and uses prototypes grouped by source file to coordinate operations.

## State and persistence behavior
`struct exfat_sb_info` is the central mounted-volume state: sector/cluster geometry, FAT and data starts, root cluster, volume flags, boot-sector buffer, allocation bitmap buffers, upcase table, allocation search pointer, used-cluster count, shutdown flags, global `s_lock`, `bitmap_lock`, mount options, NLS table, ratelimit state, and inode hash table.

`struct exfat_inode_info` extends VFS inodes with on-disk directory location, type/attr/start cluster/flags, lookup and bmap hints, cluster cache LRU state, directory-entry position hash, valid size, truncate lock, and creation time. Persistent values are mirrored from directory entries and stream extensions; hints, caches, locks, hash nodes, and shutdown flags are runtime-only.

## Dependencies and integration points
The header pulls in Linux VFS, NLS, block device, ratelimit, backing-device, and UAPI exFAT definitions, plus raw on-disk definitions through implementation files. Every exFAT source file depends on this header for shared structures and prototypes. It is the integration point between VFS operation tables, address-space operations, mount option parsing, FAT allocation, bitmap allocation, directory entry handling, and filename conversion.

## Risks and test signals
Risks include macro arithmetic overflow or off-by-one conversion errors, lock contract drift, misuse of persisted versus runtime inode fields, inconsistent `ALLOC_NO_FAT_CHAIN` versus `ALLOC_FAT_CHAIN` semantics, and ABI-visible changes to ioctl or mount option behavior via UAPI. Tests include compile coverage of all objects, 32-bit/64-bit arithmetic, maximum cluster and directory sizes, no-FAT and FAT-chain files, read-only/shutdown paths, mode/attribute conversions under different masks, and lockdep around `s_lock`, `bitmap_lock`, cache LRU, and truncate lock.
