# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_olt.c` reads the FreeVxFS Object Location Table during mount and extracts the fileset-header inode and initial inode-list extent. The complete 105-line file was read for this report.

## Important APIs, Types, and Functions

The external API is `vxfs_read_olt(struct super_block *, u_long)`. Internal helpers are `vxfs_get_fshead()`, `vxfs_get_ilist()`, and `vxfs_oblock()`.

## Control Flow

`vxfs_read_olt()` reads the OLT extent from the location recorded in the superblock, validates the OLT magic, rejects multi-block OLTs, then scans records from the header size to the extent end. It handles `VXFS_OLT_FSHEAD` by recording `vsi_fshino` and `VXFS_OLT_ILIST` by recording `vsi_iext`. Mount continues only if both values were found.

## State and Persistence Behavior

The function populates `vxfs_sb_info.vsi_fshino` and `vsi_iext`. It reads but does not retain the OLT buffer after parsing.

## Dependencies and Integration Points

`vxfs_super.c` calls this after setting the final block size and before reading fileset headers. It uses OLT record layouts from `vxfs_olt.h` and endian helpers from `vxfs.h`.

## Risks and Edge Cases

The scanner advances by on-disk `olt_size` without robust bounds or zero-size validation, so malformed OLT records can break scanning. Multi-block OLTs are explicitly unsupported. Duplicate FSHEAD or ILIST records trigger `BUG_ON()` in helper functions.

## Test Signals

Fixture images should include valid OLT, bad magic, missing FSHEAD, missing ILIST, duplicate entries, multi-block OLT, and fuzzed record sizes.
