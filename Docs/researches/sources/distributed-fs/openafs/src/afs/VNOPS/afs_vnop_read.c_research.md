# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_read.c

## Purpose
Implements cached file reads, read-ahead prefetch, and low-level reads from the configured UFS/memory cache backend.

## Important APIs, Types, and Functions
`afs_read` is the main read path, selected by `afs_rdwr` and platform vnode wrappers. `afs_PrefetchChunk` queues asynchronous fetches for the next chunk. `afs_UFSReadUIO` opens a cache file with `osi_UFSOpen` and dispatches to platform-specific `VOP_READ`, `VNOP_READ`, `VNOP_RDWR`, or `osi_rdwr`.

## Control Flow and State
`afs_read` creates a request, verifies the vcache unless `noLock` is set, checks NFS translator read access, then iterates from the uio offset across chunks. For each chunk it obtains or finds a dcache entry, waits for current fetches when needed, starts a background fetch when useful, falls back to synchronous `afs_GetDCache` if background fetch cannot start, and copies data from the cache backend into a partial uio. Short or sparse chunk regions are zero-filled using `afs_zeros`. After the loop, it releases the final dcache, may call `afs_PrefetchChunk`, checks the final error with `afs_CheckCode`, and destroys the request.

Reads do not modify server state. They update uio offsets/residuals, may wait on `tdc->validPos`, may set `DFFetchReq` or `DFNextStarted`, and use `DFFetching` plus dcache `versionNo` to decide whether cached bytes are current. They also respect `avc->vc_error` as a sticky writeback/read failure.

## Dependencies and Integration Points
Depends on chunk macros, dcache freshness checks, background daemon queues, dcache locks and mflags, cache backend `afs_cacheType->vreadUIO`, OS-specific cache-file VOPs, NFS translator credential checks, disconnected locks, and uio helper routines such as `afsio_partialcopy`, `afsio_skip`, and `afsio_free`.

## Risks and Test Signals
The EOF zero-fill pre-loop is effectively disabled by setting `len` to zero, so correctness depends on the chunk loop handling partial EOF. Waiting on `DFFetching` and `DFFetchReq` requires precise lock release and reacquire ordering. Reads with `noLock` bypass verification and use `afs_FindDCache`, so callers must already have coherence guarantees. Background daemon saturation changes behavior to synchronous fetch.

Test fully cached chunks, uncached chunks, concurrent fetch-in-progress chunks, EOF and partial EOF reads, sparse/zero-fill regions, background prefetch success and queue-full fallback, disconnected reads with unavailable dcache, NFS translator access denial, `noLock` VM reads, and platform cache backend read failures.
