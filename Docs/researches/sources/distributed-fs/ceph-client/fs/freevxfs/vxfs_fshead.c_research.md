# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.c` reads FreeVxFS fileset headers during mount and resolves the primary inode list and structural inode list. The complete 166-line file was read for this report.

## Important APIs, Types, and Functions

The external API is `vxfs_read_fshead(struct super_block *)`. Internal helpers are diagnostic `vxfs_dumpfsh()` and `vxfs_getfsh()`. It uses `struct vxfs_fsh`, `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_bread()`, and inode type predicates.

## Control Flow

`vxfs_read_fshead()` first reads the fileset-header inode from the initial inode-list extent discovered in the OLT. It verifies the inode is a fileset header, reads structural and primary fileset header blocks from that inode, then loads the structural inode-list inode and primary inode-list inode. Each list inode is checked for the inode-list type before mount can continue.

## State and Persistence Behavior

The function populates `vxfs_sb_info` fields `vsi_fship`, `vsi_stilist`, and `vsi_ilist`, which remain pinned until unmount. Temporary copied `struct vxfs_fsh` buffers are heap allocated and freed after the relevant inode numbers are extracted.

## Dependencies and Integration Points

This file sits between OLT discovery in `vxfs_olt.c` and normal inode lookup in `vxfs_inode.c`. `vxfs_super.c` calls it after block size and OLT setup, before loading the root inode.

## Risks and Edge Cases

Malformed fileset headers can leak references if cleanup paths regress; current code carefully frees `pfp`, `sfp`, and iputs loaded inodes on failure. It trusts several on-disk fields after type checks, so fuzzed images can still force odd inode-list reads.

## Test Signals

Fixture mounts should cover valid primary/structural fileset headers, missing fileset-header inode, wrong inode type, unreadable header blocks, invalid inode-list type, and cleanup under mount failure with kmemleak enabled.
