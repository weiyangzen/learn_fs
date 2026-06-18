# sources/distributed-fs/ceph-client/include/linux/qnx6_fs.h

Purpose: defines on-disk QNX6 filesystem constants and structures used by the Linux QNX6 filesystem driver to parse superblocks, inodes, directory entries, long names, and Audi MMI variant metadata.

Important APIs and types: constants specify root inode, file status values, superblock/bootblock/directory/inode sizes, direct pointer count, indirect pointer depth, short/long filename sizes, and `QNX6_MOUNT_MMI_FS`. `struct qnx6_inode_entry` is the 128-byte on-disk inode. `struct qnx6_dir_entry`, `struct qnx6_long_dir_entry`, and `struct qnx6_long_filename` model directory records and long filename indirection. `struct qnx6_root_node` points to inode, bitmap, longfile, and unknown metadata trees. `struct qnx6_super_block` and `struct qnx6_mmi_super_block` represent standard and Audi MMI superblock layouts.

Control flow: mount code reads the boot/superblock area, validates magic/checksum/version/block size, chooses standard or MMI layout, then uses root nodes to find inode, bitmap, and long-name trees. Directory lookup interprets short entries directly or resolves long-name entries through the longfile area.

State and persistence: all structures are persistent on-disk filesystem metadata with filesystem-endian fields. In-memory state is derived by the QNX6 driver during mount and lookup.

Dependencies and integration points: depends on Linux integer/filesystem endian types and magic constants. It integrates the VFS inode/directory code with QNX6 disk format parsing.

Risks and test signals: risks include incorrect endian conversion, trusting malformed sizes/levels/pointers, long filename checksum errors, MMI layout confusion, and out-of-bounds indirect tree traversal. Test mounting standard and MMI QNX6 images, corrupted superblocks/checksums, long and short filenames, deleted/status variants, maximum file levels, and fuzzed directory entries.
