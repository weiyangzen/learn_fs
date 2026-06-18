# sources/distributed-fs/ceph-client/fs/gfs2/aops.h

## Purpose
Declares the GFS2 address-space helper functions exported from `aops.c`.

## Important APIs, Types, And Functions
`adjust_fs_space()` updates filesystem free-space accounting after rindex growth. `gfs2_jdata_writeback()` writes journaled-data mapping contents under writeback control.

## Control Flow
No local runtime flow; this header provides declarations.

## State And Persistence
No state in the header. Declared functions mutate statfs/journal/page-cache state in `aops.c`.

## Dependencies And Integration Points
Includes `incore.h` and is consumed by bmap/grow and GFS2 writeback code.

## Risks
Prototype drift would break cross-file callers. Keeping only necessary declarations avoids broader include coupling.

## Test Signals
Compile all GFS2 objects and exercise filesystem grow plus jdata writeback callers.
