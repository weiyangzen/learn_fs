# sources/distributed-fs/openafs/src/afs/afs_fetchstore.c

## Purpose
`afs_fetchstore.c` implements the Cache Manager's FetchData and StoreData transfer machinery between local cache chunks and the AFS fileserver. It abstracts UFS-backed disk cache and memory-cache data paths behind `storeOps` and `fetchOps`, handles 32-bit versus 64-bit fileserver RPC entry points, updates transfer statistics, and coordinates dcache/vcache state after successful stores and fetches.

## Important APIs, types, and functions
The store path centers on `struct storeOps`, `struct rxfs_storeVariables`, `rxfs_storeInit`, `afs_GenericStoreProc`, `afs_CacheStoreDCaches`, and the exported `afs_CacheStoreVCache`. UFS operations allocate a large transfer buffer and call `afs_osi_Read` plus `rx_Write`; memory-cache operations allocate Rx iovecs via `rx_WritevAlloc`, read from `afs_MemReadvBlk`, and write with `rx_Writev`. `rxfs_storeClose` ends `StoreData` or `StoreData64`, and `rxfs_storeDestroy` always closes the Rx call and frees buffers.

The fetch path centers on `struct fetchOps`, `struct rxfs_fetchVariables`, `rxfs_fetchInit`, `rxfs_fetchMore`, and exported `afs_CacheFetchProc`. UFS fetch reads from Rx into a large buffer and writes via `afs_osi_Write`; memory-cache fetch reads with `rx_Readv` and writes via `afs_MemWritevBlk`. `rxfs_fetchClose` obtains returned fetch status, callback, and volume sync before ending the Rx call.

`FillStoreStats` is shared by fetch and store despite the name; it updates `afs_stats_cmfullperf.rpc.fsXferTimes`, byte buckets, min/max byte counts, and elapsed-time aggregates.

## Control flow
Stores are initiated by `afs_CacheStoreVCache`, which scans a dcache list, groups contiguous locked chunks, computes the RPC base offset, byte count, and file length, then repeatedly obtains an AFS connection through `afs_Conn`. It starts a store with `rxfs_storeInit`, streams each dcache through `afs_CacheStoreDCaches`, invokes `afs_Analyze` for retryable failures, and falls back from `StoreData64` to `StoreData` on `RXGEN_OPCODE` when needed. On success it clears dirty dcache flags, releases dcache references, processes returned file status with `afs_ProcessFS`, and records maximum stored length for later mini-store extension decisions.

Fetches are initiated by `afs_CacheFetchProc`, which starts the RPC in `rxfs_fetchInit`, validates the server-reported length, streams data into the cache file or memory cache, advances `adc->validPos`, wakes waiters on valid data arrival, and closes the RPC to collect status/callback metadata. For foreign files, `rxfs_fetchMore` supports the AFS/DFS translator extension where the high bit announces additional length-prefixed data blocks.

## State and persistence behavior
This file mutates persistent cache chunk content through `afs_CFileOpen`, `afs_osi_Read`, `afs_osi_Write`, memory-cache block writes, and dcache flags such as `DWriting`, `DFEntryMod`, `IFDataMod`, `IFDirtyPages`, and `IFAnyPages`. Stores update server-side file contents and data versions; successful returned status is reconciled into the vcache with `afs_ProcessFS`. Fetches update `validPos` so readers can consume partial data as it arrives. Transfer statistics are retained in global in-memory stats structures.

## Dependencies and integration points
The module depends on Rx calls (`rx_NewCall`, `rx_Read`, `rx_Readv`, `rx_Write`, `rx_Writev`, `rx_EndCall`), fileserver stubs (`StartRXAFS_FetchData`, `StartRXAFS_FetchData64`, `EndRXAFS_*`), cache file APIs, memory-cache APIs, connection analysis/retry (`afs_Analyze`), dcache/vcache locks, and ICL tracing. It is part of the storeback/fetch pipeline used by higher-level cache manager code.

## Risks and edge cases
Key risks are protocol length validation, partial transfers, 64-bit fallback correctness, dcache lock/release balance, and dirty-flag consistency after failed stores. The code explicitly rejects server fetch lengths larger than requested or too large for signed 32-bit local handling. Older fileservers returning negative lengths are treated as zero. Store padding for short chunks is required when storing multi-chunk ranges. Memory-cache iovec allocation must be pinned/heap-backed for kernel Rx safety. `storeallmissing` records missing dcache anomalies that currently warn and continue.

## Test signals
Useful signals include FetchData/StoreData success and retry paths against 32-bit and 64-bit servers, memory cache versus UFS cache modes, partial fetch wakeups through `validPos`, dirty flag clearing after store, fallback on `RXGEN_OPCODE`, rejected oversized server responses, short-read/write error handling, and xstats/ICL transfer event counters.
