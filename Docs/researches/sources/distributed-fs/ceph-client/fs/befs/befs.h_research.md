# sources/distributed-fs/ceph-client/fs/befs/befs.h

Purpose: central BeFS internal header defining in-memory superblock/inode state, error codes, debug prototypes, and address conversion helpers.

Important APIs/types/functions: `struct befs_mount_options`, `struct befs_sb_info`, `struct befs_inode_info`, `enum befs_err`, `BEFS_SB`, `BEFS_I`, `iaddr2blockno`, `blockno2iaddr`, and `befs_iaddrs_per_block`.

Control flow: included by most BeFS implementation files so they can convert between VFS objects and BeFS-private state and between BeFS allocation-group addresses and linear block numbers.

State and persistence: `befs_sb_info` mirrors persistent superblock fields plus mount options and loaded NLS table. `befs_inode_info` mirrors persistent inode addresses, flags, type, and either datastream or short symlink data.

Dependencies and integration: includes on-disk types from `befs_fs_types.h` and endian conversion helpers from `endian.h`; ties VFS inode embedding to BeFS metadata.

Risks: address conversion depends on validated `ag_shift` and block geometry. Any mismatch between on-disk and in-memory fields can produce bad block reads.

Test signals: mount images with different block sizes/ag shifts, stat regular files/directories/symlinks, and verify converted inode/block addresses through debug output.
