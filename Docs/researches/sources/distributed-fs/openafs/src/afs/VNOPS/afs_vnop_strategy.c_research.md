# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_strategy.c

## Purpose
Provides a legacy buffer strategy entry point for platforms that route VM/page I/O through buffer objects instead of directly through read/write vnode calls.

## Important APIs, Types, and Functions
`afs_ustrategy` converts a `struct buf` into a one-element `uio` and dispatches to `afs_rdwr` or `afs_nlrdwr` for reads and writes. It handles platform-specific buffer fields such as `b_un.b_addr`, `b_data`, `b_saveaddr`, `b_blkno`, `b_lblkno`, `b_iocmd`, `b_flags`, and completion callbacks.

## Control Flow and State
The function extracts the vcache from `abp->b_vp`, chooses credentials from the caller or platform current user area, builds a kernel-space uio at the block offset, and branches on read versus write. Reads call `afs_rdwr(..., UIO_READ, ...)`, zero-fill any residual bytes in the buffer, and perform AIX page-protection handling beyond EOF. Writes compute the write length, sometimes trimming to current file length on AIX, and call `afs_rdwr(..., UIO_WRITE, ...)`. It records buffer errors on BSD-like platforms and calls the appropriate `iodone`, `biodone`, or `b_iodone`.

This file does not maintain independent state. It drives normal read/write paths, so persistence is delegated to `afs_write`, close, fsync, and background store behavior. Buffer residuals and error fields are updated according to platform requirements.

## Dependencies and Integration Points
Compiled only when not using HPUX, SGI, Linux, or Darwin80-specific alternatives. Depends on `afs_rdwr` wrappers in `afs.h`, platform buffer layouts, uio setup macros, credential APIs, and kernel I/O completion functions.

## Risks and Test Signals
Correct block offset calculation is platform-specific and differs for `b_blkno` versus `b_lblkno`. Credential selection from global user state is noted as questionable in comments. Residual zero-fill must use the correct buffer address field. Some platforms need explicit buffer error flags while others rely on completion callbacks.

Test platform build coverage, buffer reads before/after EOF, residual zero-fill, buffer writes at block offsets, error propagation to `b_error` and `B_ERROR`, completion callback invocation, AIX credential and page-protection paths, and consistency with direct `afs_read`/`afs_write`.
