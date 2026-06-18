# sources/distributed-fs/ceph-client/fs/gfs2/bmap.h

## Purpose
Declares GFS2 block mapping, iomap, allocation, truncation, journal extent, and punch-hole APIs, plus the write reservation estimation helper.

## Important APIs, Types, And Functions
`gfs2_write_calc_reserv()` estimates data and indirect blocks needed for a write based on block size, dinode pointers, and indirect fanout. Externs include `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`, unstuffing, block mapping, iomap get/alloc, extent get/alloc, size changes, truncate resume, file deallocation, allocation-required checks, journal extent mapping/freeing, and `__gfs2_punch_hole()`.

## Control Flow
Only inline reservation calculation executes locally. It rejects directory inodes and accumulates indirect levels while data blocks exceed dinode direct pointers.

## State And Persistence
No header-local state. Declared functions mutate allocation, transaction, inode, journal, quota, and page-cache state.

## Dependencies And Integration Points
Includes iomap and inode headers and is consumed by aops, dir, file, inode, recovery, and journal code.

## Risks
Reservation underestimation can cause transaction exhaustion; overestimation reduces concurrency. Prototype drift risks subtle cross-file breakage.

## Test Signals
Compile all users, test reservation estimates for small/large writes and multiple block sizes, and exercise all exported mapping APIs through filesystem operations.
