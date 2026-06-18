<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h

## Purpose
`meta_io.h` declares GFS2 metadata buffer I/O helpers and small buffer manipulation utilities used throughout the filesystem.

## Important APIs, types, and functions
Inline helpers are `gfs2_buffer_clear`, `gfs2_buffer_clear_tail`, `gfs2_buffer_copy_tail`, `gfs2_mapping2sbd`, and `gfs2_meta_inode_buffer`. It declares `gfs2_meta_aops`, `gfs2_rgrp_aops`, `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_getbuf`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`. The `REMOVE_JDATA` and `REMOVE_META` enum values select accounting behavior in `gfs2_remove_from_journal`. `buffer_busy` tests dirty, locked, or pinned buffer state.

## Control Flow
The header has no standalone flow. Callers use `gfs2_getbuf` and `gfs2_meta_read` to access metadata, `gfs2_meta_buffer` or `gfs2_meta_inode_buffer` when metatype validation is required, and `gfs2_journal_wipe` when blocks are freed or inode creation is abandoned.

## State and Persistence
The inline buffer helpers directly mutate buffer data. `gfs2_mapping2sbd` interprets mappings owned by `gfs2_meta_aops` as glock address spaces and other mappings as inode-backed filesystem mappings. The declared functions manage persistent metadata and journal visibility through buffer-head state and disk I/O.

## Dependencies and Integration Points
Includes Linux buffer-head and string helpers plus `incore.h`. It is included by most metadata-heavy GFS2 files, including bmap, dir, xattr, quota, log/lops, recovery, rgrp, inode, and superblock code.

## Risks
The tail-copy helper assumes `from_head >= to_head` and uses buffer sizes directly; incorrect offsets would corrupt metadata. `gfs2_mapping2sbd` relies on address-space operations identity. `buffer_busy` is a compact predicate used by log/AIL code, so semantic changes to buffer flags would affect journal tail advancement.

## Test Signals
Compile coverage, metadata block allocation and zeroing, stuffed-to-unstuffed transitions, directory/xattr metadata copies, journal wipe tests, and lockdep/KASAN around buffer offset helpers are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/meta_io.h -->
