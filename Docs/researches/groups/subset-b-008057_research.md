# subset-b-008057 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntryPool.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntryPool.java

Purpose: This class is the replicated key-write block manager behind `KeyOutputStream`. It owns communication with OM for block allocation, collects block location metadata for commit and hsync, maintains preallocated block entries, and shares a `BufferPool` across the underlying block streams.

Important APIs and types: The central APIs are `addPreallocateBlocks`, `allocateBlockIfNeeded`, `commitKey`, `hsyncKey`, `discardPreallocatedBlocks`, `getLocationInfoList`, `getMetadata`, and `cleanup`. It builds `BlockOutputStreamEntry` objects from `OmKeyLocationInfo`, uses `OzoneManagerProtocol.allocateBlock`, `commitKey`, `commitMultipartUploadPart`, and `hsyncKey`, and stores write context in `OmKeyArgs.Builder`, `ExcludeList`, `StreamBufferArgs`, `BufferPool`, `ContainerClientMetrics`, and `OmMultipartCommitUploadPartInfo`.

Control flow: Construction copies key identity from `OpenKeySession`, builds a shared buffer pool, and initializes an expiring exclude list. Preallocated blocks are added only for the current open version. Writes call `allocateBlockIfNeeded`, which advances past closed entries and asks OM for another block when the entry list is exhausted. Commit and hsync rebuild `OmKeyArgs` with data size, metadata, and non-empty locations; hsync avoids duplicate OM calls when the last block ID has not changed.

State and persistence behavior: Runtime state is the ordered stream-entry list, current stream index, shared buffer contents, metadata map, multipart commit result, and `lastUpdatedBlockId`. Persistent changes happen only through OM calls: allocated blocks, committed key or multipart part state, and hsync visibility. Empty stream entries are intentionally omitted from commit location metadata.

Dependencies and integration points: It integrates `KeyOutputStream`, `ECBlockOutputStreamEntryPool`, OM protocol, SCM client metrics, xceiver client factory, stream buffer settings, block tokens, pipelines, and container/pipeline exclusion used by retry handling.

Risks: The class is synchronization-sensitive around `streamEntries` and `currentStreamIndex`. `buildKeyArgs` mutates the builder by adding all metadata each time, so repeated calls rely on builder metadata semantics. Hsync deduplication by last block ID can skip OM updates when only length changes inside the same block. `discardPreallocatedBlocks` assumes unused entries have zero current position.

Test signals: Useful tests assert preallocated version filtering, allocation with exclude lists, commit location lists excluding zero-byte blocks, multipart commit info propagation, hsync error for multipart keys, hsync latency metric paths, duplicate hsync suppression, buffer cleanup, and removal of unused blocks for excluded containers or pipelines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntryPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/CipherOutputStreamOzone.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/CipherOutputStreamOzone.java

Purpose: This is a small Ozone-specific wrapper around `javax.crypto.CipherOutputStream` that preserves access to the wrapped stream and forwards key metadata operations through encryption.

Important APIs and types: The public API is the constructor taking `OutputStream` and `Cipher`, the protected constructor for subclasses/tests, `getWrappedStream`, and `getMetadata`. It implements `KeyMetadataAware` and depends on the wrapped stream also implementing that interface.

Control flow: Construction delegates to `CipherOutputStream` and stores the original output stream. Metadata requests unwrap one level and cast the wrapped stream to `KeyMetadataAware`.

State and persistence behavior: It stores only the wrapped stream reference. Persistence is delegated to the downstream key output stream, including metadata and commit behavior.

Dependencies and integration points: `OzoneOutputStream` and `OzoneDataStreamOutput` know how to unwrap this class, similar to Hadoop `CryptoOutputStream`, so encrypted outputs still expose commit metadata and pre-commit hooks.

Risks: `getMetadata` can throw `ClassCastException` if the wrapped stream is not `KeyMetadataAware`. The `output` field is not final even though it behaves as immutable after construction.

Test signals: Tests should cover metadata passthrough through cipher wrapping, wrapped-stream identity, close/write delegation inherited from `CipherOutputStream`, and failure behavior when wrapping an incompatible stream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/CipherOutputStreamOzone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntry.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntry.java

Purpose: This `BlockOutputStreamEntry` subclass represents one erasure-coded block group. It fans a logical EC block group into one `ECBlockOutputStream` per data or parity replica and exposes cursor operations used by `ECKeyOutputStream` while writing stripes.

Important APIs and types: Important methods include `checkStream`, `getOutputStream`, `useNextBlockStream`, `forceToFirstParityBlock`, `resetToFirstEntry`, `markFailed`, `executePutBlock`, `streamsWithWriteFailure`, `streamsWithPutBlockFailure`, `calculateChecksum`, and `updateBlockGroupToAckedPosition`. It depends on `ECReplicationConfig`, single-node `Pipeline` construction, `ECBlockOutputStream`, protobuf chunk metadata, and async response futures.

Control flow: Lazy initialization creates an array of streams for all required EC nodes, each with a single-node pipeline carrying the original EC pipeline ID and replica index. The current stream cursor advances across data cells and parity cells. Data writes increment logical position; parity writes intentionally do not. After stripe writes, failures are detected from chunk or putBlock futures, checksums are concatenated from the latest chunk entries, putBlock is executed for every initialized stream, and close updates the block group ID from the first stream.

State and persistence behavior: Runtime state includes the stream array, current internal stream index, logical length, and last successful block-group ack length. Persistent effects are the data/parity chunks and putBlock metadata written by the underlying `ECBlockOutputStream`s. The class also updates block commit sequence information from the underlying stream.

Dependencies and integration points: It is created by `ECBlockOutputStreamEntryPool` and driven by `ECKeyOutputStream`. It integrates EC replication metadata, datanode replica indexes, xceiver client management, buffer pooling, tokens, metrics, and container protocol futures.

Risks: Failure detection treats null futures as failed; incomplete stream initialization can affect close and checksum behavior. `underlyingBlockID` assumes stream 0 exists when data has been written. The TODO around `getWrittenDataLength` notes retry accounting may be incomplete for parity or duplicate writes. Checksum concatenation relies on chunk-list alignment across data and parity streams.

Test signals: Strong tests cover single-node pipeline replica indexes, data-only position accounting, parity cursor transitions, flush/close over initialized streams only, write and putBlock future failure detection, failed server aggregation, checksum construction for partial stripes, and ack length updates after successful putBlock.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntryPool.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntryPool.java

Purpose: This class specializes `BlockOutputStreamEntryPool` for erasure-coded writes by creating `ECBlockOutputStreamEntry` instances instead of replicated `BlockOutputStreamEntry` instances.

Important APIs and types: It overrides `createStreamEntry` and narrows `getCurrentStreamEntry` to `ECBlockOutputStreamEntry`. Its builder input is `ECKeyOutputStream.Builder`, and it maps `OmKeyLocationInfo` fields into `ECBlockOutputStreamEntry.Builder`.

Control flow: All allocation, commit, hsync, metadata, exclude-list, and cleanup behavior remains inherited. Only entry instantiation changes: block ID, key, xceiver manager, pipeline, config, length, buffer pool, token, metrics, stream buffer arguments, and executor supplier are copied into the EC builder.

State and persistence behavior: State is inherited from the base pool. Persistent effects are still OM block allocation and key commit, but underlying entries write EC block groups rather than single replicated blocks.

Dependencies and integration points: This is the adapter between `ECKeyOutputStream` and the generic block pool. It also relies on base-class accessors for protected construction context.

Risks: The override does not propagate the `forRetry` flag into the EC entry builder, unlike the replicated pool; this is acceptable only if EC retry behavior is entirely stripe-level. The narrowed cast in `getCurrentStreamEntry` assumes the pool never contains replicated entries.

Test signals: Tests should verify EC builders create EC entries with the expected pipeline/config/token state, inherited preallocation and allocation work for EC locations, and `getCurrentStreamEntry` returns null or an EC entry safely.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockOutputStreamEntryPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECKeyOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECKeyOutputStream.java

Purpose: This final output stream implements erasure-coded key writes. It buffers client bytes into EC data cells, generates parity cells, asynchronously flushes stripes to datanodes, retries failed stripes on new block groups, and commits the logical key length to OM.

Important APIs and types: Public behavior comes from `write`, `close`, unsupported `flush`/`hflush`/`hsync`, `setPreCommits`, and testing hooks `insertFlushCheckpoint` and `getFlushCheckpoint`. Internally it uses `ECChunkBuffers`, `ArrayBlockingQueue`, `RawErasureEncoder`, `ECBlockOutputStreamEntryPool`, `ECBlockOutputStreamEntry`, `ECBlockOutputStream`, `ByteBufferPool`, S3 auth thread-local propagation, and `OzoneClientConfig` EC retry/queue settings.

Control flow: Writes fill the current data cell; when all data cells in a stripe are full, `generateParityCells` pads partial data, flips buffers, encodes parity, queues the stripe, and starts a fresh buffer set. A background flush task takes stripes, writes data cells, writes parity cells, executes putBlock, checks write and putBlock futures, and retries after excluding failed pipelines/datanodes and rolling back offset. Close queues a final partial stripe if needed, sends an EOF marker, waits for the flush future, runs pre-commit hooks, commits the key, closes the current entry, and cleans the pool.

State and persistence behavior: Runtime state includes current EC buffers, queue, chunk index, logical `offset`, ingested `writeOffset`, flush checkpoint, closed/closing flags, and background flush future. Persistent state is written through datanode chunk/putBlock calls and OM `commitKey`. Stripe retries discard preallocated blocks on the failed pipeline and rewrite still-buffered stripe data.

Dependencies and integration points: It integrates the generic `KeyOutputStream` constructor only for pool/commit plumbing, then implements its own EC write path. It touches erasure-code raw coder selection, xceiver/block stream APIs, OM commit, S3 authentication context, client byte-buffer pooling, and container exclusion logic.

Risks: Flush, hflush, and hsync are unsupported or no-op, which callers must understand. Background failure surfaces through `flushFuture.get`, so write calls check for early flush-thread termination while enqueueing. Offset rollback assumes data buffer limits accurately reflect logical bytes. Partial-stripe padding and checksum collection are subtle and high-risk. Closing while writes are in progress sets `closing` and prevents stream reopening.

Test signals: Valuable tests cover full and partial stripe encoding, parity padding, queue backpressure, flush checkpoint ordering, S3 auth propagation to the flush thread, retry count exhaustion, failed datanode/pipeline exclusion, offset/writeOffset equality at close, buffer release to the pool, pre-commit execution, and unsupported sync semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/ECKeyOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyCommitOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyCommitOutput.java

Purpose: This package-private interface captures commit-time operations common to key output implementations that also expose key metadata.

Important APIs and types: It extends `KeyMetadataAware` and declares `setPreCommits(List<CheckedRunnable<IOException>>)` plus `getCommitUploadPartInfo`. The pre-commit hook type comes from Ratis and can throw `IOException`; multipart commit info is `OmMultipartCommitUploadPartInfo`.

Control flow: Wrappers such as `OzoneOutputStream` and `OzoneDataStreamOutput` detect this interface and install pre-commit callbacks before the underlying key stream closes and commits to OM.

State and persistence behavior: The interface has no state. Implementations store pre-commit hooks and expose multipart upload part commit results after OM commit.

Dependencies and integration points: Implemented by `KeyOutputStream` and `KeyDataStreamOutput`; EC output inherits the same commit contract. It is the bridge between public wrapper streams and internal key commit implementations.

Risks: Since it is package-private, only same-package wrappers can rely on it. Hook order and exception behavior are implementation-specific but affect whether OM commit occurs.

Test signals: Tests should verify wrappers find `KeyCommitOutput` through direct and encrypted streams, pre-commit hooks run before commit, exceptions prevent commit, and multipart commit info is returned after close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyCommitOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyDataStreamOutput.java

Purpose: This output stream writes keys from `ByteBuffer` inputs through `BlockDataStreamOutputEntryPool`. It is the data-stream counterpart to `KeyOutputStream`, using SCM byte-buffer stream abstractions while preserving OM allocation, retry, hsync, and commit semantics.

Important APIs and types: Main methods are `write(ByteBuffer,int,int)`, `addPreallocateBlocks`, `flush`, `hsync`, `hflush`, `close`, `setPreCommits`, `getCommitUploadPartInfo`, `getMetadata`, and test accessors for entries, locations, xceiver manager, client ID, and exclude list. It uses `AbstractDataStreamOutput`, `BlockDataStreamOutputEntry`, `BlockDataStreamOutputEntryPool`, `BlockDataStreamOutput`, `OzoneClientConfig`, `ExcludeList`, and OM helper types.

Control flow: Construction builds an entry pool from the open key session and retry policy. Writes allocate a current block, write as much as fits, close full blocks, and update logical offsets. On IOException it determines retry/container exclusion, updates acked position, optionally issues putBlock/watchForCommit, excludes failed datanodes/pipelines/containers, cleans the failed stream, discards invalid preallocations, and rewrites buffered data through retry. Flush, hsync, full-block close, and close all dispatch through `handleFlushOrClose`.

State and persistence behavior: Runtime state includes closed flag, offset, writeOffset, client ID, pre-commit hooks, and the entry pool. Persistent state is datanode chunk/block metadata plus OM key or multipart-part commit state. Hsync updates OM visibility at `writeOffset` after the data stream hsync succeeds.

Dependencies and integration points: Used by `OzoneDataStreamOutput` for byte-buffer writes and by `ClientProtocol.createStreamKey`/file stream APIs. It integrates SCM data-stream output, retry policy from `HddsClientUtils`, block preallocation, OM commit, and key metadata propagation.

Risks: The class comments say multi-thread access is not supported, unlike `KeyOutputStream` which has explicit lock/semaphore logic. Exception handling has subtle offset and buffered-data invariants. `chunkSize` is passed in the constructor but not used directly here, so behavior depends on the entry pool. Closing after exception skips offset equality checks.

Test signals: Tests should cover ByteBuffer offset/length writes across block boundaries, hsync position checks, retry after partial writes, exclude-list updates, full-block close, pre-commit ordering, multipart info return, metadata propagation, and cleanup on failed close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyInputStream.java

Purpose: This read stream composes a key from lazily initialized block input streams and delegates multipart-style offset reads to `MultipartInputStream`.

Important APIs and types: The key factories are `getFromOmKeyInfo` and `getStreamsFromKeyInfo`; runtime overrides are `getNumBytesToRead`, `checkPartBytesRead`, and `getPartStreams`. It uses `OmKeyInfo`, `OmKeyLocationInfo`, `BlockExtendedInputStream`, `BlockInputStreamFactory`, `BlockLocationInfo`, `XceiverClientFactory`, retry functions that refresh OM key info, and `LengthInputStream`.

Control flow: Factory methods extract latest-version block locations, create a `BlockExtendedInputStream` for each location without initializing it, and wrap the resulting `KeyInputStream` with its computed length. If a retry function is supplied, each block stream receives a resolver that refreshes the key and finds a matching block ID. Multipart parts can be split by `partNumber` into separate `LengthInputStream`s. The last block is marked under construction for hsync-created files.

State and persistence behavior: Runtime state is the ordered list of part streams inherited from `MultipartInputStream`. There are no writes; persistence is datanode block reads and possible OM metadata refresh through the retry callback.

Dependencies and integration points: Used by client read APIs and `OzoneInputStream`. It integrates OM key metadata, datanode block input stream factories, hsync metadata (`OzoneConsts.HSYNC_CLIENT_ID`), and multipart part grouping.

Risks: `partsToBlocksMap.values()` does not guarantee sorted part order unless the grouping map ordering happens to match expectations; callers may need deterministic part ordering elsewhere. `checkPartBytesRead` treats any short read as corruption/data loss. Retry block lookup returns null if refreshed key info lacks the same block ID.

Test signals: Tests should verify latest-version filtering, lazy block stream creation, hsync under-construction marking on the last block, retry location refresh, exact short-read exception messages, ByteReaderStrategy sizing, and multipart part grouping correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyMetadataAware.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyMetadataAware.java

Purpose: This interface identifies streams that expose mutable key metadata associated with an Ozone key write.

Important APIs and types: It declares only `Map<String, String> getMetadata()`.

Control flow: Output wrappers and cipher wrappers use this interface to retrieve the metadata map from the underlying key stream even when the stream is wrapped.

State and persistence behavior: The interface has no state. Implementations usually return a live metadata map that is later merged into `OmKeyArgs` before OM commit or hsync.

Dependencies and integration points: Implemented by key output streams, wrapper streams, and `CipherOutputStreamOzone`. It supports metadata additions by higher layers without exposing concrete stream classes.

Risks: The contract does not specify mutability, nullability, or thread safety. Some wrappers cast blindly to this interface, so incompatible stream composition fails at runtime.

Test signals: Tests should verify metadata map identity through wrapper layers, mutation before close reaches OM commit arguments, and clear failure behavior for non-aware wrapped streams.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyMetadataAware.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStream.java

Purpose: This is the main replicated byte-array key writer. It writes client bytes to one or more datanode block streams, handles retry and exclusion after failures, supports flush and hsync for RATIS keys, executes pre-commit hooks, and commits the final key to OM.

Important APIs and types: Key methods include `write`, `flush`, `hflush`, `hsync`, `close`, `addPreallocateBlocks`, `handleWrite`, `setPreCommits`, `getCommitUploadPartInfo`, `getMetadata`, and builder setters for OM, xceiver, config, replication, metrics, executor, multipart, and OM version. It depends on `BlockOutputStreamEntryPool`, `BlockOutputStreamEntry`, `KeyOutputStreamSemaphore`, `RetryPolicy`, `ExcludeList`, `OzoneManagerVersion`, Ratis exceptions, SCM container exceptions, and `Syncable`.

Control flow: `write` acquires the per-key semaphore, validates arguments, takes the write lock, writes chunks into the current block entry, closes full blocks, and advances `offset`/`writeOffset`. On IOException it waits for pending flushes, determines retry versus container exclusion, records failed datanodes and pipelines/containers in the exclude list, cleans the failed stream, discards invalid preallocated blocks, sleeps per retry policy, and rewrites buffered data into a newly allocated block. Flush and hsync use `handleFlushOrClose`; close flushes/closes, validates offsets when no exception occurred, runs pre-commit hooks, commits to OM, and clears the pool.

State and persistence behavior: Runtime state includes closed flag, exception flag, retry count, committed offset, ingested writeOffset, client ID, stream buffer settings, metrics, OM version, write lock/condition, semaphore, and pre-commit hooks. Persistent state is datanode block data plus OM key, multipart-part, or hsync metadata. Failed streams are not rolled back if an earlier block in a multi-block write already succeeded.

Dependencies and integration points: It is wrapped by `OzoneOutputStream` and may be wrapped by encryption streams. It coordinates with OM block allocation/commit through the pool, SCM datanode streams through entries, client retry config, metrics, and HBase-support-gated hsync.

Risks: The class explicitly does not support general multi-thread access despite some concurrency controls; condition/semaphore interactions are subtle. Retry offset accounting depends on `getWrittenDataLength` and buffer pool invariants. Hsync only supports RATIS with replication factor greater than one and sufficient OM version. `markStreamClosed` aggressively clears the pool, making later errors terminal.

Test signals: Tests should cover argument validation, block-boundary writes, full-block close, concurrent write semaphore queueing, retry after partial writes, failed datanode/pipeline/container exclusion, preallocated block discard, hsync gating by replication and OM version, OM hsync/commit metrics, pre-commit failure behavior, multipart commit info, and cleanup after errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStreamSemaphore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStreamSemaphore.java

Purpose: This helper encapsulates optional per-key write concurrency limiting for `KeyOutputStream`.

Important APIs and types: The constructor accepts `maxConcurrentWritePerKey`; `acquire`, `release`, and `getQueueLength` wrap a Java `Semaphore`.

Control flow: Positive concurrency creates a semaphore with that many permits. Zero is rejected as invalid configuration. Negative values disable limiting by leaving the semaphore null. `acquire` blocks until a permit is available and converts interruption into `InterruptedIOException` while restoring the interrupt flag; `release` is a no-op when disabled.

State and persistence behavior: Runtime state is only the semaphore and its queued/acquired permits. It has no persistence.

Dependencies and integration points: Used by `KeyOutputStream.write`, `flush`, and `hsync` to bound concurrent operations per key. It logs trace-level acquire/release events.

Risks: Callers must release in `finally` to avoid permit leaks. Negative values completely disable concurrency control, so configuration semantics must be intentional. The constructor is package-private, limiting direct external validation.

Test signals: Tests should cover positive permit blocking/queue length, zero rejecting config, negative no-op behavior, interruption converting to `InterruptedIOException`, and release not throwing when disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStreamSemaphore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneCryptoInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneCryptoInputStream.java

Purpose: This encrypted-bucket read stream wraps Hadoop `CryptoInputStream` and implements `PartInputStream` with a known part length. It adjusts reads to crypto buffer boundaries so decryption remains correct while callers receive exactly the requested range.

Important APIs and types: Public methods are the constructor, `getLength`, `getBufferSize`, and `read(byte[],int,int)`. Internal helpers `getNumBytesToRead`, `adjustReadPosition`, and `adjustNumBytesToRead` manage boundary alignment. It uses `LengthInputStream`, `CryptoCodec`, key/IV material, `CryptoStreamUtils`, and `PartInputStream` position/remaining methods.

Control flow: Reads compute the maximum bytes to read based on requested length, stream remaining bytes, and crypto buffer size. If current position is not buffer-aligned, the stream seeks backward and later discards leading bytes. If requested length ends before the buffer boundary, it reads more and later discards trailing bytes, seeking back by the trailing adjustment. Short reads after accounting for crypto boundaries throw an IOException.

State and persistence behavior: Runtime state includes fixed length, buffer size, key name, part index, and one-read adjustment counters. There are no writes or persistence. Position changes are delegated to the wrapped seekable crypto stream.

Dependencies and integration points: Used when reading keys in encrypted buckets, normally above `KeyInputStream`/`LengthInputStream`. It integrates Hadoop crypto codecs with Ozone multipart block reads and strict part-length accounting.

Risks: Boundary handling uses temporary byte arrays and copies, which can be expensive. Adjustment counters must reset after every adjusted read. Seeking backward for trailing bytes changes the underlying stream position in a non-obvious way. The code assumes `super.read` returns the full adjusted request or else treats it as corruption.

Test signals: Tests should cover aligned reads, unaligned start reads, unaligned end reads, both start and end adjustments together, end-of-part behavior, position after trailing adjustment, short-read exceptions, and crypto buffer size configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneCryptoInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneDataStreamOutput.java

Purpose: This public byte-buffer output wrapper exposes Ozone data-stream writes while preserving optional `Syncable`, metadata, multipart, and pre-commit behavior from the underlying stream.

Important APIs and types: Main methods are constructors for syncable and byte-buffer outputs, `write(ByteBuffer,int,int)`, `flush`, `close`, `hsync`, `hflush`, `getCommitUploadPartInfo`, `getKeyDataStreamOutput`, `setPreCommits`, `getByteBufStreamOutput`, and `getMetadata`. It uses `ByteBufferStreamOutput`, `Syncable`, `KeyCommitOutput`, `KeyDataStreamOutput`, `CryptoOutputStream`, and `CipherOutputStreamOzone`.

Control flow: Writes and close/flush delegate to the wrapped `ByteBufferStreamOutput`. Hsync either degrades to flush when disabled, or flushes the byte-buffer stream before invoking the syncable target. Commit-related calls unwrap nested `OzoneOutputStream`, Hadoop crypto, or Ozone cipher wrappers to find a `KeyCommitOutput` or `KeyDataStreamOutput`.

State and persistence behavior: State is the wrapped byte-buffer output, selected syncable, and `enableHsync` flag. Persistent key data and OM commit state are controlled by the wrapped implementation.

Dependencies and integration points: Returned by `ClientProtocol.createStreamKey`, multipart stream APIs, and stream file APIs. It bridges public client code with internal key data-stream implementations and encryption wrappers.

Risks: The `OzoneDataStreamOutput(Syncable, boolean)` constructor requires the syncable to also be an `OzoneDataStreamOutput`, which is stricter than the doc wording. `getMetadata` blindly casts the byte-buffer stream to `KeyMetadataAware`. Hsync behavior depends on feature flag configuration and wrapper identity.

Test signals: Tests should cover direct and wrapped `KeyDataStreamOutput` discovery, pre-commit forwarding, hsync disabled versus enabled behavior, flush before external syncable hsync, metadata passthrough, multipart commit info forwarding, and unsupported/incompatible stream failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneInputStream.java

Purpose: This public input wrapper exposes Ozone key reads as a standard `InputStream` plus Hadoop `ByteBufferReadable`, `CanUnbuffer`, and `Seekable` interfaces when supported by the underlying stream.

Important APIs and types: It implements `read`, byte-array read, `read(ByteBuffer)`, `close`, `available`, `skip`, `getInputStream`, `unbuffer`, `seek`, `getPos`, and `seekToNewSource`. It delegates to `InputStream`, `ByteBufferReadable`, `CanUnbuffer`, and `Seekable`.

Control flow: Standard reads always delegate. ByteBuffer reads require the wrapped stream to implement `ByteBufferReadable`; seek methods require `Seekable`; unbuffer is optional and only invoked when supported.

State and persistence behavior: Runtime state is only the wrapped input stream reference. There is no persistence or buffering in this wrapper.

Dependencies and integration points: Returned by `ClientProtocol.getKey`, file reads, S3 key details readers, and replica-read APIs. It usually wraps `KeyInputStream` or `OzoneCryptoInputStream`.

Risks: The default constructor leaves `inputStream` null and is only safe for tests or serialization-like usage. Unsupported ByteBuffer or seek operations fail at runtime. Close is synchronized but other delegated operations are not.

Test signals: Tests should cover delegation of normal reads, ByteBuffer read support and unsupported exceptions, seek/getPos/seekToNewSource delegation, unbuffer optional behavior, and null default-constructor safety assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneOutputStream.java

Purpose: This public byte-array output wrapper exposes Ozone key writes as an `OutputStream` with optional Hadoop `Syncable`, metadata access, multipart commit info, pre-commit forwarding, and hsync behavior.

Important APIs and types: Important methods are constructors, `write`, `flush`, `close`, `hflush`, `hsync`, `getCommitUploadPartInfo`, `getOutputStream`, `getKeyOutputStream`, `setPreCommits`, and `getMetadata`. It unwraps Hadoop `CryptoOutputStream` and `CipherOutputStreamOzone` to find `KeyOutputStream`, `KeyCommitOutput`, or `KeyMetadataAware`.

Control flow: Writes/flush/close delegate to the wrapped output. Hsync flushes when disabled; when enabled it flushes the wrapper if the syncable target is separate, then calls `syncable.hsync`. Commit-related methods unwrap encryption layers before forwarding to the internal key stream.

State and persistence behavior: State is the wrapped output stream, optional syncable, and hsync feature flag. Data persistence and OM commit are performed by the wrapped stream during close or sync.

Dependencies and integration points: Returned by `ClientProtocol.createKey`, multipart create, and file create APIs. It is the main public wrapper around `KeyOutputStream` and encrypted output streams.

Risks: Metadata and pre-commit calls fail at runtime if the wrapped stream is not backed by the expected interfaces. Hsync silently behaves as flush when disabled, preserving prior behavior but potentially surprising callers expecting durability. `getKeyOutputStream` only finds direct unwrapped `KeyOutputStream`, not other `KeyCommitOutput` implementations.

Test signals: Tests should cover write/flush/close delegation, hsync enabled/disabled paths, encrypted stream unwrapping, metadata propagation, pre-commit forwarding, multipart commit info forwarding, and unsupported wrapped-stream error messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.client.io` contains Ozone I/O classes.

Important APIs and types: It defines package-level Javadoc only and introduces no classes or methods.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: The package contains the public stream wrappers and internal key/block stream coordination classes researched in this group.

Risks: The descriptor is minimal, so package-level documentation does not explain important distinctions such as replicated versus EC writes, byte-array versus byte-buffer output, or encryption wrappers.

Test signals: No direct tests are needed beyond compile/Javadoc checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.client` contains Ozone Client classes.

Important APIs and types: It defines package-level Javadoc only.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: The package hosts user-facing client domain objects such as volumes, buckets, keys, multipart upload descriptors, tenants, and snapshots that are returned by `ClientProtocol`.

Risks: The package comment is broad and does not describe the client protocol, object model, or stream APIs in detail.

Test signals: Compile/Javadoc generation is the only meaningful signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/ClientProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/ClientProtocol.java

Purpose: This is the main client-facing Ozone protocol interface. Implementations, especially the RPC client, expose volume, bucket, key, multipart upload, security, tenant, filesystem, ACL, snapshot, tag, KMS, and lease-recovery operations against an Ozone cluster.

Important APIs and types: The interface includes volume operations (`createVolume`, `listVolumes`, quotas, owner), bucket operations (`createBucket`, storage/versioning/quota/encryption/replication/owner), key operations (`createKey`, conditional create/rewrite, stream variants, read/get info/head/list/delete/rename), multipart APIs, delegation tokens and S3 secrets, tenant administration, server defaults and KMS provider access, filesystem-style status/create/read/write/list, ACL management, S3 auth thread-local methods, replica reads, snapshots and snapshot diff jobs, times, lease recovery, and object tagging. It returns public client types such as `OzoneVolume`, `OzoneBucket`, `OzoneKeyDetails`, `OzoneOutputStream`, `OzoneDataStreamOutput`, `OzoneInputStream`, and OM helper response types.

Control flow: As an interface it has no implementation control flow, but it defines the sequencing contract for many operations: create/open returns an output stream whose close commits data, multipart initiation creates upload IDs and part streams before completion, conditional writes enforce generation or ETag checks at open and commit time, list APIs use previous markers and max result limits, and snapshot diff can be submitted, queried, cancelled, or listed.

State and persistence behavior: Implementations persist metadata in OM and data in datanodes through returned streams. The interface covers durable namespace mutations for volumes, buckets, keys, directories, snapshots, tenants, secrets, ACLs, quotas, tags, and leases. Thread-local S3 auth is client-side request context rather than cluster persistence.

Dependencies and integration points: It is annotated with Kerberos server principal information and bridges higher-level client objects to `OzoneManagerProtocol`. It is consumed by Ozone client APIs, S3 gateway paths, filesystem adapters, admin tools, and stream classes researched in this group.

Risks: The interface is very broad, so compatibility is high-risk: adding or changing methods affects all protocol implementations. Deprecated replication-type/factor overloads coexist with `ReplicationConfig` variants. Conditional write semantics require enforcement both at open and commit. Thread-local S3 auth must be cleared to avoid credential leakage across reused threads.

Test signals: Integration tests should cover each method family through the RPC implementation, including pagination markers, quota and ACL results, stream close committing keys, multipart conditional completion, encryption/KMS provider retrieval, tenant state transitions, snapshot diff job lifecycle, lease recovery, tag CRUD, S3 auth isolation, and deprecated overload compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/ClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.client.protocol` contains Ozone client protocol library classes.

Important APIs and types: It defines package-level Javadoc only.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: The package currently contains the `ClientProtocol` interface researched in this group, which is implemented by protocol-specific clients.

Risks: The documentation is minimal and does not summarize the protocol surface or implementation expectations.

Test signals: Compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/OzoneKMSUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/OzoneKMSUtil.java

Purpose: This final utility class centralizes client-side KMS and encryption-at-rest helpers for Ozone RPC clients, including decrypting encrypted data encryption keys, locating KMS provider URIs, creating key providers, validating crypto protocol versions, and resolving crypto codecs.

Important APIs and types: Important methods are `decryptEncryptedDataEncryptionKey`, `getKeyProviderMapKey`, `bytes2String`, `getKeyProviderUri`, `getKeyProvider`, `getCryptoProtocolVersion`, `checkCryptoProtocolVersion`, and `getCryptoCodec`. It uses Hadoop `KeyProvider`, `KeyProviderCryptoExtension`, `FileEncryptionInfo`, `CryptoProtocolVersion`, `CipherSuite`, `CryptoCodec`, `Credentials`, `UserGroupInformation`, `KMSUtil`, and Ozone `ConfigurationSource`.

Control flow: Decryption wraps file encryption info into an `EncryptedKeyVersion` and calls the crypto extension. KMS URI lookup first checks UGI credentials keyed by the Ozone namespace URI, then client configuration when no server KMS URI is supplied, then the OM-provided server URI when non-empty; resolved URIs are cached back into credentials. Codec lookup rejects unknown cipher suites and reports a specific OM exception if no codec is configured.

State and persistence behavior: The class has no instance state. It mutates UGI `Credentials` by storing the key-provider URI secret for a namespace, enabling tasks to reuse the provider mapping. Other behavior is validation or provider/codec construction.

Dependencies and integration points: Used by RPC client encryption paths and encrypted bucket reads/writes. It bridges Ozone configuration to Hadoop KMS and crypto APIs and supports `OzoneCryptoInputStream`/encrypted output setup through decrypted keys and codecs.

Risks: The static `keyProviderUriKeyName` is mutable only inside the class but not final. URI precedence is important: cached credentials can override later config/server changes. Empty `kmsUriSrv` deliberately means no server URI, while null means fall back to client config. Error messages expose crypto suite/protocol details but not key material.

Test signals: Tests should cover null key provider failure, successful encrypted key decryption, namespace credential cache hit/miss, client-config versus server-URI precedence, credential write-back, null server provider rejection, unsupported crypto protocol rejection, unknown cipher suite rejection, missing codec OMException, and UTF-8 byte conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/OzoneKMSUtil.java -->
