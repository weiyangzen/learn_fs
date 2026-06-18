# sources/distributed-fs/ceph-client/fs/ext2/ext2.h

Purpose: Central ext2 private header defining in-memory superblock/inode state, on-disk ext2 structures, feature/mount flags, directory formats, allocation types, helper macros, and cross-file prototypes.

Important APIs/types/functions: Defines `ext2_sb_info`, `ext2_inode_info`, `ext2_group_desc`, `ext2_inode`, `ext2_super_block`, `ext2_dir_entry(_2)`, reservation types, `EXT2_SB`, `EXT2_I`, `ext2_mask_flags`, `ext2_group_first_block_no`, `ext2_group_last_block_no`, feature macros, mount option macros, bitmap little-endian aliases, ioctl constants, and prototypes for block, inode, dir, file, ioctl, namei, super, and symlink operations.

Control flow: Header inline logic masks inherited inode flags by inode type, maps group numbers to first/last physical blocks, verifies superblock offsets at build time, and exposes compile-time constants used throughout mount, allocation, block mapping, and namespace operations.

State and persistence behavior: `ext2_sb_info` holds mounted filesystem geometry, group descriptors, mount options, counters, locks, xattr cache, DAX device, and reservation tree. `ext2_inode_info` embeds VFS inode plus raw block pointers, flags, xattr block, deletion time, group, reservation info, xattr semaphore, metadata lock, truncate mutex, quota pointers, and metadata buffer tracking. On-disk structures encode superblock, group descriptor, inode, and directory layout.

Dependencies and integration points: Bridges all ext2 compilation units with Linux VFS, buffer heads, blockgroup locks, percpu counters, rbtrees, memory management, xattr/ACL code, DAX, quota, iomap, and export operations. Feature macros must align with ext2/ext3 on-disk compatibility semantics.

Risks: Structural definitions are ABI with disk images; field or endian mistakes corrupt filesystems. Lock comments describe critical serialization contracts for truncation vs block allocation and xattr access. Feature masks determine mount compatibility. `EXT2_CURRENT_REV` remains old revision while dynamic revision support is managed by superblock code.

Test signals: Compile-time offset checks; mount images with old/dynamic revisions and feature combinations; inode flag inheritance tests; large-file feature setting; DAX mount behavior; big-endian bitmap/inode compatibility.
