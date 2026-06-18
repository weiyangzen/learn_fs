# sources/distributed-fs/openafs/src/volser/physio.c

## Purpose
Provides physical directory I/O and `DirHandle` utility routines used by volser/salvage-style directory manipulation.

## Important APIs And Functions
`ReallyRead` reads one AFS directory page from an inode handle and distinguishes physical errors from logical short reads through `physerr`. `ReallyWrite` writes one directory page and sets external `VolumeChanged`. `SetSalvageDirHandle`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, and `FidCpy` manage `DirHandle` identity and handle references. `Die` prints and panics.

## Control Flow And State
Each read/write opens the inode handle, performs page-sized positioned I/O, then closes or really closes on errors. `SetSalvageDirHandle` increments a static cache-check value so new handles force directory cache refresh semantics.

## Persistence And Integration
This file directly persists directory pages through `FDH_PREAD` and `FDH_PWRITE`. It integrates with `afs_dir` code via expected physical I/O hooks, inode handles, and `DirHandle` from `vol.h`.

## Risks And Test Signals
Risks include short read/write handling, leaked handles on error paths, global `VolumeChanged` coupling, and `private int SalvageCacheCheck` portability. Test signals include page read/write success, short I/O simulation, handle copy/release reference behavior, directory mutation paths in `vol_split.c`, and error propagation through `physerr`.
