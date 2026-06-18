# sources/distributed-fs/ceph-client/include/uapi/linux/minix_fs.h

## Purpose
Defines Minix filesystem on-disk constants and structs for inode, superblock, and directory entry layouts across Minix v1/v2/v3 variants.

## Important APIs, Types, And Functions
Exports root inode, link limits, map slots, clean/error flags, `minix_inode`, `minix2_inode`, `minix_super_block`, `minix3_super_block`, `minix_dir_entry`, and `minix3_dir_entry`.

## Control Flow
Filesystem code reads the superblock, detects version/magic externally, then interprets inode and directory layouts according to the variant. Directory entries use flexible names after the inode field.

## State, Persistence, And Dependencies
These structs map persistent on-disk bytes. Dependencies are `linux/types.h` and `linux/magic.h`; block-size macro availability affects `MINIX_INODES_PER_BLOCK`.

## Integration Points
Used by Minix filesystem mounting, fsck tools, and disk image parsers.

## Risks
Layouts differ substantially between v1 and v2/v3, including inode size, time fields, uid/gid widths, and zone pointer widths. Flexible directory names require external record-size knowledge.

## Test Signals
Mount/read known Minix v1/v2/v3 images, validate superblock parsing, inode size/layout, root inode handling, link limits, and directory entry traversal.
