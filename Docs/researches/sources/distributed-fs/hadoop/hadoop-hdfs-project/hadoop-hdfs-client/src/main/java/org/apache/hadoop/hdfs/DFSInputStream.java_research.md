# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInputStream.java

## Purpose
`DFSInputStream` is the replicated-file HDFS input stream. It resolves file blocks through `DFSClient`, chooses DataNodes, builds `BlockReader`s, performs sequential and positional reads, handles retry/token/encryption refresh, reports checksum failures, tracks read statistics, supports zero-copy reads, and participates in dead-node detection and located-block refresh.

## Important APIs, Types, and Functions
The class extends `FSInputStream` and implements `ByteBufferReadable`, `ByteBufferPositionedReadable`, `CanSetDropBehind`, `CanSetReadahead`, `CanUnbuffer`, `HasEnhancedByteBufferAccess`, and `StreamCapabilities`. Key state is split between synchronized stateful-read fields (`currentNode`, `currentLocatedBlock`, `pos`, `blockEnd`, `blockReader`) and `infoLock`-protected shared fields (`locatedBlocks`, `lastBlockBeingWrittenLength`, `fileEncryptionInfo`, `cachingStrategy`, `lastRefreshedBlocksAt`). It also keeps per-stream `ReadStatistics`, local dead nodes, failure count, and tracked zero-copy buffers.

Important methods include `openInfo`, `fetchAndCheckLocatedBlocks`, `getLastBlockLength`, `readBlockLength`, `getBlockAt`, `fetchBlockAt`, `getBlockRange`, `blockSeekTo`, `getBlockReader`, `readWithStrategy`, `pread`, `fetchBlockByteRange`, `actualGetFromOneDataNode`, `hedgedFetchBlockByteRange`, `reportCheckSumFailure`, `seek`, `seekToNewSource`, zero-copy `read(ByteBufferPool, int, EnumSet<ReadOption>)`, `releaseBuffer`, and `refreshBlockLocations`.

## Control Flow
Construction stores the provided initial `LocatedBlocks`, applies the default read caching strategy, and calls `openInfo(false)`. `openInfo` ensures block metadata is current and, for an under-construction last block, asks DataNodes for visible replica length with bounded retries. `fetchAndCheckLocatedBlocks` rejects block-list changes compared with an existing list.

Sequential reads call `readWithStrategy`, which checks client/stream state, registers for block refresh if needed, seeks to a block when the cursor is past `blockEnd` or no current node exists, reads through the current `BlockReader`, advances `pos`, updates read statistics, and reports checksum failures. On failures it retries the current node once for transient read errors, otherwise marks nodes dead and seeks a new source.

Positioned reads call `pread`, clamp length to EOF, map the range to `LocatedBlock`s, and read each block either through normal `fetchBlockByteRange` or through `hedgedFetchBlockByteRange` when hedged reads are enabled and the block is not striped. Hedged reads submit one read, wait for the configured threshold, submit reads to other DataNodes if needed, accept the first successful future, and cancel the rest without interrupting running HDFS reads.

`blockSeekTo` resolves the target block, chooses a valid DataNode, and constructs a `BlockReader`. It refreshes an encryption key once for `InvalidEncryptionKeyException`, refetches a block token once for token failures, and otherwise marks failed nodes dead before trying another. Zero-copy reads try `BlockReader.getClientMmap` when short-circuit mmap is enabled, fall back to pooled ByteBuffer reads, and require callers to return buffers through `releaseBuffer`.

## State and Persistence
The stream owns only client-side mutable read state; file data and block metadata persist in HDFS. `locatedBlocks` is a cache refreshed by explicit fetches or by `LocatedBlocksRefresher`. Dead nodes are tracked locally and can be merged with `DFSClient`'s shared `DeadNodeDetector`. `extendedReadBuffers` tracks outstanding buffers by identity so `close()` can warn about leaks and `releaseBuffer()` can return pooled buffers or close mmaps. Caching strategy changes close the current block reader so new settings take effect.

## Dependencies and Integration Points
The stream depends on `DFSClient` for configuration, NameNode block locations, data-transfer peer creation, stats, dead-node detector, block refresher, and checksum failure reporting. Data-node access goes through `BlockReaderFactory`, `ClientDatanodeProtocol` for visible length, `Token<BlockTokenIdentifier>`, `CachingStrategy`, `StorageType`, and `DFSUtilClient` helpers. Higher-level users receive it through `DFSClient.open` unless erasure coding selects `DFSStripedInputStream`.

## Risks
Lock ordering is delicate: comments require avoiding acquisition of `this` while holding `infoLock`, and block refresh can re-enter seek logic. `deadNodes` uses a concurrent map as a temporary parallel-access mitigation, so positioned reads and sequential reads still need careful concurrency testing. Hedged reads allocate per-attempt ByteBuffers and cancel without interruption, which avoids noisy partial-read errors but can leave background reads running briefly. Stale block tokens, encryption keys, or located blocks must be refreshed exactly once per failure class before failing over. Zero-copy callers that forget `releaseBuffer` can retain mmap resources until close. Under-construction block length handling depends on DataNode reports and retry timing.

## Test Signals
`TestPread` exercises positional reads, hedged reads, delayed reads, metrics, and fault injection. `TestRead`, `TestDFSInputStream`, and `TestDFSInputStreamBlockLocations` cover read retry behavior, block-location refresh, and local/remote block decisions. `TestLocatedBlocksRefresher` covers refresher registration/deregistration. `TestDeadNodeDetection` validates local and shared dead-node handling. Checksum and corruption paths are covered by `TestCrcCorruption`; token refresh and SASL interactions are covered by data-transfer token tests such as `TestSaslDataTransferExpiredBlockToken`.
