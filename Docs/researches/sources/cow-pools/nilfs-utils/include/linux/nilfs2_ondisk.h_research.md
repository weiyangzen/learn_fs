# File Research: sources/cow-pools/nilfs-utils/include/linux/nilfs2_ondisk.h

Bundled NILFS2 on-disk format header. It defines inode layout, super root, superblock layout, revision and feature flags, reserved inode numbers, block/segment size constraints, directory entries, segment summary format, B-tree node headers, direct node headers, DAT entries, checkpoints, checkpoint file header, segment usage entries, and sufile header.

It includes endian-encoded field types and inline helpers for checkpoint and segment usage flags. Important constants include `NILFS_SEGSUM_MAGIC`, `NILFS_SB_OFFSET_BYTES`, `NILFS_SB2_OFFSET_BYTES`, root metadata inode range, and minimum structure sizes for compatibility.
