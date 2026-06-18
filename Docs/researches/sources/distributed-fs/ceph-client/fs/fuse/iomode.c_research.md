# sources/distributed-fs/ceph-client/fs/fuse/iomode.c

## Purpose
Coordinates per-inode FUSE I/O modes so cached page-cache access, uncached direct I/O, mmap fallback, and passthrough backing-file access do not run in unsafe combinations.

## Important APIs, Types, And Functions
`fuse_file_cached_io_open()` enters cached mode and blocks new parallel direct writes while waiting for existing uncached writers to drain. `fuse_inode_uncached_io_start()` starts an uncached section and optionally installs a `struct fuse_backing` on the inode. `fuse_inode_uncached_io_end()` drops uncached references, clears backing state when the counter returns to zero, and wakes waiters. `fuse_file_passthrough_open()` validates `FOPEN_PASSTHROUGH` combinations and opens a backing file. `fuse_file_io_open()` is the main open-time policy decision. `fuse_file_io_release()` releases cached or uncached mode references according to `ff->iomode`.

## Control Flow
Open requests bypass mode logic for DAX or servers without `OPEN`. Existing inode backing requires all future opens to request passthrough. Direct I/O without passthrough remains uncached but does not enter inode mode here; cached and passthrough opens take explicit references. Cached opens wait while `iocachectr` is negative and no backing file exists, set `FUSE_I_CACHE_IO_MODE`, and increment `iocachectr`. Passthrough opens first obtain a backing file then enter uncached mode; failure releases the backing handle.

## State And Persistence
The core state is `fi->iocachectr`: positive for cached users, zero for no mode, negative for uncached users. `FUSE_I_CACHE_IO_MODE` advertises cache-mode exclusion. `fuse_inode_backing(fi)` holds at most one backing object while passthrough is active. `ff->iomode` records the per-open reference that must be released.

## Dependencies And Integration Points
Depends on FUSE inode/file structures, direct-I/O wait queues, passthrough backing-file helpers, and `FOPEN_*` open flags returned by the server. Integrates with open/release paths and mmap/direct-I/O paths that need cache exclusion.

## Risks
Incorrect counter transitions can deadlock cached opens or allow page-cache and passthrough access to coexist. Server misuse of `FOPEN_PASSTHROUGH` or `FOPEN_PARALLEL_DIRECT_WRITES` intentionally turns into user-visible `EIO`. Multiple backing files for the same inode are rejected with `EBUSY`, so caller cleanup must be exact.

## Test Signals
Test concurrent cached opens and direct writes, passthrough first-open with later non-passthrough open rejection, multiple backing IDs on one inode, release balancing, `FOPEN_DIRECT_IO` flag normalization, and wait/wake behavior when uncached writers drain.
