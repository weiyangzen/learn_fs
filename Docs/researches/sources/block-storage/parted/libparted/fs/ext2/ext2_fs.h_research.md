# File Research: sources/block-storage/parted/libparted/fs/ext2/ext2_fs.h

Local ext2/ext3/ext4 on-disk structure header. It defines magic values, block constants, special inode numbers, directory file type values, error policy constants, and feature flags used to distinguish ext3 and ext4.

Structures include `ext2_dir_entry_2`, `ext2_group_desc`, `ext2_inode`, and the packed `ext2_super_block`. The superblock layout covers classic ext2 fields plus dynamic revision fields, feature masks, UUID, volume name, last mounted path, compression bitmap, and journal metadata. Accessor macros convert little-endian fields for directory entries, group descriptors, inodes, and superblock fields.

The probe code relies especially on `EXT2_SUPER_MAGIC`, block count, log block size, blocks per group, group number, first data block, revision level, and feature masks. This header is disk-layout sensitive; packed structure and endian macros are essential to portability.
