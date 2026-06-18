# sources/distributed-fs/ceph-client/fs/fat/fat.h

## Purpose
`fat.h` is the private header for the FAT core, msdos, vfat, and NFS export code. It defines mount options, in-core superblock and inode state, slot lookup structures, FAT-entry abstractions, inline helpers for mode/attribute/cluster conversion, and cross-file function declarations.

## Important APIs, Types, and Functions
- `struct fat_mount_options` captures parsed mount policy: uid/gid, masks, codepage, iocharset, timestamp offset, shortname behavior, error policy, NFS mode, UTF-8/unicode escape behavior, discard, flush, and FAT-specific flags.
- `struct msdos_sb_info` is the FAT superblock state: layout geometry, FAT table location, root directory info, FSINFO counters, locks, NLS tables, inode and directory hashes, special FAT/FSINFO inodes, and dirty-state tracking.
- `struct msdos_inode_info` extends VFS inodes with cluster cache, FAT chain start, on-disk directory-entry position, hash nodes, truncate lock, creation time, and metadata-buffer tracking.
- `struct fat_slot_info` describes a located directory entry and its VFAT slot span.
- Inline helpers include `MSDOS_SB()`, `MSDOS_I()`, `is_fat12/16/32()`, `fat_make_mode()`, `fat_make_attrs()`, `fat_checksum()`, `fat_clus_to_blknr()`, `fat_get_start()`, and `fat_set_start()`.

## Control Flow
The header is not executable control flow, but it defines the contracts that connect mount parsing, block mapping, directory entry mutation, FAT entry access, and VFS operations. Callers use `fat_get_start()` and `fat_set_start()` to handle FAT32 high cluster bits transparently, and use `fat_make_mode()` / `fat_make_attrs()` to translate between FAT attributes and Linux permission bits.

## State and Persistence
The central persistent bridge is `i_pos`, an encoded directory-entry location, and `i_start` / `i_logstart`, the first cluster for file data. `msdos_sb_info` mirrors persistent boot-sector and FSINFO fields such as FAT layout, root cluster, volume ID, free cluster counts, and dirty state. `msdos_inode_info::i_metadata_bhs` groups metadata buffers that need fsync.

## Dependencies and Integration Points
This header depends on Linux VFS, buffer-head, NLS, hash, ratelimit, msdos on-disk structures, and fs_context parser APIs. It is included by all FAT implementation files in this subset and is the main integration surface between the common FAT core and the msdos/vfat filesystem modules.

## Risks and Test Signals
Inline helpers encode subtle semantics. `fat_mode_can_hold_ro()` treats directory read-only differently based on `rodir`; changing it affects chmod and attribute ioctls. `fat_i_pos_read()` needs locking on 32-bit systems because `loff_t` is not atomically readable. Compile coverage across FAT, msdos, vfat, and NFS export modules is important, while KUnit validates `fat_checksum()` and timestamp helpers declared here.
