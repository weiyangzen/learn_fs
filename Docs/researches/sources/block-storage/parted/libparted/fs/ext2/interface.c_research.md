# File Research: sources/block-storage/parted/libparted/fs/ext2/interface.c

Filesystem registration and probing for ext2, ext3, and ext4. `_ext2_generic_probe()` reads enough sectors from the start of the geometry to access the superblock at byte offset 1024, verifies the ext magic, computes block size and total length, then classifies the filesystem by feature flags.

Ext4 is detected from modern incompatible/readonly-compatible features such as extents, 64-bit, flex_bg, huge file, GDT checksum, or dir_nlink. Ext3 is detected by the journal compatible feature when ext4 features are absent. The caller’s expected version determines whether the match is accepted.

The probe handles backup/group superblocks: if a dynamic revision superblock reports a nonzero block group number, it computes the original filesystem start, initializes a temporary geometry, and recursively probes from that base. Otherwise it returns a geometry sized by block count and block size. The file registers three types: `ext2`, `ext3`, and `ext4`.
