<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.c -->
# sources/distributed-fs/openafs/src/tests/fs_lib.c

## Purpose
Provides reusable test helpers around AFS cache-manager `pioctl` operations.

## Important APIs, Types, and Functions
functions: fs_getfid, fs_nop, fs_getfilecellname, fs_setcrypt, fs_getcrypt, fs_connect, fs_setfprio, fs_getfprio, fs_setmaxfprio, fs_getmaxfprio, fs_getfilecachestats, fs_getaviatorstats, fs_gcpags, fs_calculate_cache, fs_invalidate, debug; AFS calls/macros: fs_lib, fs_getfid, pioctl, VIOCGETFID, fs_nop, VIOCNOP, fs_getfilecellname, VIOC_FILE_CELL_NAME, VIOC_SETRXKCRYPT, fs_setcrypt, VIOC_GETRXKCRYPT, fs_getcrypt, VIOCCONNECTMODE, fs_connect, VIOC_FPRIOSTATUS, fs_setfprio

## Control Flow
Each public wrapper initializes `struct ViceIoctl`, fills input/output buffers for one Venus command, calls `pioctl`, and returns errno-style status; mount-point helpers split paths before issuing mount-point stat/delete ioctls.

## State and Persistence Behavior
Mostly stateless, but functions can change cache-manager state: crypt level, connect mode, fetch priority, sysname, cache size, debug flags, mount points, cache flushing, callback invalidation, and PAG garbage collection.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting; AFS interfaces fs_lib, fs_getfid, pioctl, VIOCGETFID, fs_nop, VIOCNOP, fs_getfilecellname, VIOC_FILE_CELL_NAME, VIOC_SETRXKCRYPT, fs_setcrypt

## Risks and Test Signals
Many functions are conditional on OpenAFS/Arla ioctl defines and some use legacy compatibility probes; wrong buffer sizing or renumbered ioctl assumptions can produce false test failures across client versions.

## Source Notes
Read as C program; 843 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.c -->
