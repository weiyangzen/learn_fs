# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.c

## Purpose
`FhgfsOpsPages.c` implements BeeGFS address-space page-cache operations for paged/native cache modes: readpage/read_folio, readahead/readpages, writepage/writepages, page-vector batching, writeback completion, short-read handling, and page-backed inode size correction. It bridges Linux MM/VFS page callbacks to asynchronous BeeGFS page-vector remoting work.

## Important APIs, Types, And Functions
- Page-vector cache lifecycle: `FhgfsOpsPages_initPageListVecCache()` and `FhgfsOpsPages_destroyPageListVecCache()`.
- Internal batching: `struct FhgfsPageData`, `_FhgfsOpsPages_allocNewPageVec()`, and `_FhgfsOpsPages_sendPageVec()`.
- File-handle referencing: `_FhgfsOpsPages_referenceReadFileHandle()`, `_FhgfsOpsPages_referenceWriteFileHandle()`, and `_FhgfsOpsPages_referenceFileHandle()`.
- Write path: `FhgfsOpsPages_writePageCallBack()`, `_FhgfsOpsPages_writepages()`, `FhgfsOpsPages_writepage()`, `FhgfsOpsPages_writepages()`, and `FhgfsOpsPages_endWritePage()`.
- Read path: `FhgfsOpsPages_readPageCallBack()`, `FhgfsOpsPages_readpageSync()`, `FhgfsOps_read_folio()` or `FhgfsOpsPages_readpage()`, `_FhgfsOpsPages_readahead()` or `_FhgfsOpsPages_readpages()`, and `FhgfsOpsPages_readahead()` or `FhgfsOpsPages_readpages()`.
- Size/short-read handling: `__FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `FhgfsOpsPages_isShortRead()`, `FhgfsOpsPages_endReadPage()`, and `FhgfsOpsPages_writeBackPage()`.

## Control Flow
Initialization creates a slab cache for `FhgfsPageListVec` objects and a small mempool reserve; teardown destroys the mempool before the slab cache. Page-vector sending checks for null/empty vectors, queues non-empty vectors through `RWPagesWork_createQueue()`, and optionally allocates the next vector for continued batching.

Writeback begins from `write_cache_pages()` or a single-page writepage call. The callback references a write handle on first use, allocates a chunk page vector, clips the final page to `i_size`, ignores pages beyond truncation while clearing writeback state, pushes pages into the vector, sends full vectors asynchronously, sets page writeback, and leaves completion to worker callbacks. The final `_writepages` flush sends any remaining vector and releases the referenced file handle.

Readpage clears `PageUptodate`, writes back the target page first to avoid reading stale dirty data, and delegates to readahead/readpages. The read batching path references a read-capable handle, holds the inode while async work owns pages, pushes pages into chunk vectors, sends vectors to read workers, releases the handle, and drops the inode reference. Read completion zero-fills partial pages, flushes dcache, marks pages uptodate, records errors, adjusts inode size when reads extend past local `i_size`, and unmaps/unlocks/releases pages.

`__FhgfsOpsPages_incInodeFileSizeOnPagedRead()` handles metadata size lag: it refreshes the inode without flushing because locked pages could deadlock, asks the metadata server to refresh the entry if needed, refreshes again, and only increases local `i_size` under `i_lock` if the read still extends beyond known size.

## State And Persistence Behavior
Local state includes slab/mempool allocations, `FhgfsPageData` handle references and `RemotingIOInfo`, `FhgfsChunkPageVec` batches, page dirty/writeback/uptodate/error flags, inode dirty-page counters, inode size, and inode hold counts while async work is queued. Server-persistent behavior is indirect: queued `RWPagesWork` performs storage-node reads/writes, and size correction can request metadata refresh via `FhgfsOpsRemoting_refreshEntry()`.

## Dependencies And Integration Points
This file integrates with Linux MM helpers (`write_cache_pages`, `read_cache_pages`, folio/readahead APIs, writeback controls, page locking), BeeGFS `FhgfsChunkPageVec`, `FhgfsPage`, `RWPagesWork`, `FhgfsInode` handle/reference/counter APIs, `FhgfsOpsInode` refresh, `FhgfsOpsHelper` logging, `RemotingIOInfo`, and cache-mode address-space operation tables selected during inode creation.

## Risks
- Page lock and inode flush ordering is delicate; refresh paths explicitly avoid flushing while pages are locked to prevent deadlocks.
- Async queued page vectors must own page references correctly until completion; missing `get_page()`/release behavior can race page reuse.
- Writeback error handling must set mapping/page errors and decrement dirty counters exactly once.
- Clipping writes against `i_size` races with truncate and can either drop beyond-size pages or re-dirty them for retry.
- Kernel API variants for folios/readpages/writepage callbacks increase build-matrix risk.
- Mempool exhaustion paths must not leak page vectors or leave pages locked.

## Test Signals
Stress tests for mmap/page-cache writes, truncation during writeback, readahead across chunk boundaries, sparse and short reads, metadata size lag, injected `RWPagesWork_createQueue()` allocation failure, writeback error propagation, folio and pre-folio kernel builds, and dirty-page counter accounting are the most valuable signals.
