# sources/distributed-fs/ceph-client/fs/qnx6/super_mmi.c

## Purpose
`super_mmi.c` handles QNX6 MMI filesystem superblock layout, where mirrored superblocks have a slightly different structure and fixed offset semantics.

## Important APIs, types, and functions
Important functions are `qnx6_mmi_fill_super` and `qnx6_mmi_copy_sb`.

## Control flow
It reads superblock 1, validates magic and CRC, derives the second superblock location from block count and superblock area, switches to the filesystem block size, rereads superblock 1, reads/checks superblock 2, chooses the newer serial, copies MMI fields into a normal `qnx6_super_block` shape, stores the active buffer in `qnx6_sb_info`, and sets `s_blks_off`.

## State and persistence
It reads mirrored on-disk superblocks and stores the selected active one in runtime superblock state. No writes occur.

## Dependencies and integration points
It depends on buffer heads, CRC32, QNX6 endian helpers, MMI on-disk structures, and `qnx6_fill_super` when the `mmi_fs` mount option is set.

## Risks and test signals
Risks include checksum diagnostic typo, block-size change invalidating buffer heads, serial comparison errors, missing endian detection for MMI, and memory allocation failure for the temporary converted superblock. Test signals include valid MMI images with either mirror active, corrupt magic/checksum in each mirror, alternate block sizes, and mount failure cleanup.
