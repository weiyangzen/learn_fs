# sources/distributed-fs/lizardfs/src/mount/writedata.cc

## Purpose
Implements the mount client's asynchronous write-back engine. It accepts FUSE/client writes into per-inode `WriteCacheBlock` chains, schedules background workers to lock LizardFS chunks through the master, streams block operations to chunkservers through `ChunkWriter`, handles retries and delayed requeueing, and provides flush/truncate/end APIs used by the mount/client layer.

## Important APIs, Types, And Functions
The central private type is `inodedata`, which tracks inode id, cached max file length, status, queue flags, flush/write wait counters, reference count, retry count, minimum worthwhile batch size, pending block chain, current `WriteChunkLocator`, data-arrival pipe, and timers. `InodeChunkWriter` owns one queued inode job and drives `processJob`, `processDataChain`, journal return, and "is this block worth sending" decisions. Public entry points are `write_data_init`, `write_data_term`, `write_data_new`, `write_data_end`, `write_data_flush`, `write_data_flush_inode`, `write_data_getmaxfleng`, `write_data_truncate`, and `write_data`.

## Control Flow
`write_data_init` initializes global cache counters, inode hash table, a producer-consumer queue, the delayed queue worker, and write worker threads. `write_data_new` returns/refcounts inode state. `write_data` blocks behind active flushes, updates `maxfleng`, then decomposes the input into chunk/block ranges via `write_blocks` and `write_block`. `write_block` expands the last writable cache block when possible; otherwise it waits for global/per-inode cache allowance, appends a block, and enqueues or wakes workers. Workers pull `inodedata` from `jqueue`; `InodeChunkWriter` chooses the front chunk, obtains or resumes a chunk locator, initializes `ChunkWriter`, drains worthwhile cache blocks into the writer under a time/window policy, finishes and unlocks the chunk, then either requeues, delays, or completes the inode. Flushes increment `flushwaiting`, expedite delayed jobs, and wait until `inqueue` clears.

## State And Persistence Behavior
All mutable write state is in process memory and protected by `gMutex`; persistence happens only when worker operations reach chunkservers and the master receives write/truncate completion messages through locator/master APIs. `freecacheblocks` is the global write cache budget in block units, while `gCachePerInodePercentage` prevents one inode from consuming too much free cache. `lastWriteToDataChain` and `lastWriteToChunkservers` force old partial data to flush even without explicit flush calls. `write_data_truncate` is a special two-phase flow: it flushes current writes, asks the master for truncate metadata/lock, optionally writes zeroes after the new EOF to update xor/EC parity, then calls `fs_truncateend`.

## Dependencies And Integration Points
Depends on common queueing, sockets, CRC/datapack, `ChunkConnectorUsingPool`, `ChunkWriter`, `WriteCacheBlock`, `WriteChunkLocator`, master communication helpers (`fs_truncate`, `fs_truncateend`, chunk lock/unlock), read invalidation (`read_inode_ops`), global chunkserver stats, protocol constants from `MFSCommunication.h`, and tweak registration for `WriteMaxRetries`. The header exposes this module to mount/client file operations.

## Risks And Edge Cases
The module is concurrency-heavy: condition variables, delayed queues, pipes, queue shutdown, and refcounted `inodedata` deletion all rely on strict lock discipline. Error mapping compresses several lower-level write failures into `EBADF`, `QUOTA`, `NOSPACE`, or `IO`, so diagnostics can be lossy. Retry behavior keeps locators and unwritten journals for recoverable errors; incorrect journal/block accounting would corrupt cache pressure or write order. Partial blocks are intentionally delayed unless a flush/age/multiblock condition forces them out, which affects latency. Truncate parity zeroing depends on correct old length, lock id, and EC stripe bounds. The Windows/Cygwin pipe path disables wake-up optimization and may have higher write latency.

## Test Signals
No direct unit test is listed for this file in the subset. Indirect coverage should come from mount write/read/truncate integration tests, chunkserver protocol tests, EC/xor write tests, and stress tests that exercise retry, flush, delayed queue, and shutdown behavior.
