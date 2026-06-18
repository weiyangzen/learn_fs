# Research Report: subset-b-007981

This grouped report covers the HDDS/Ozone client block storage stream classes in `hadoop-hdds/client`. Each file section is bounded by reconciliation markers and is intended to be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockInputStream.java

## Purpose
`BlockInputStream` is the non-streaming, block-level read implementation used by higher key streams to read one Ozone block from container datanodes. It lazily retrieves block metadata, builds one `ChunkInputStream` per chunk, and then presents those chunks as one seekable `BlockExtendedInputStream`.

## Important APIs and Types
The main constructor accepts `BlockLocationInfo`, `Pipeline`, block token, `XceiverClientFactory`, refresh callback, and `OzoneClientConfig`. Public APIs include `initialize()`, `readWithStrategy(ByteReaderStrategy)`, `seek(long)`, `getPos()`, `close()`, `unbuffer()`, `getBlockID()`, `getLength()`, and testing accessors for chunk state. `getBlockData()` and `getBlockDataUsingClient()` perform the container `getBlock` RPC. `createChunkInputStream()` is a protected factory hook used by tests and subclasses.

## Control Flow
Reads first call `initialize()` if needed. Initialization acquires a read client, invokes `ContainerProtocolCalls.getBlock`, validates chunk lengths, updates under-construction length from datanode block data, computes `chunkOffsets`, and constructs lazy chunk streams. `readWithStrategy` loops over the active chunk, caps each request by chunk remaining bytes, delegates to `ByteArrayReader` or `ByteBufferReader`, advances `chunkIndex`, and requires exact reads from each chunk. `seek` either stores a pre-initialization block position or binary-searches `chunkOffsets`, resets prior/future chunks, and seeks the selected chunk.

## State and Persistence Behavior
State is in-memory only: `pipelineRef`, `tokenRef`, `xceiverClient`, `chunkStreams`, `chunkOffsets`, `chunkIndex`, `blockPosition`, retry count, and cached `blockData`. The class does not persist data; it reflects persisted container metadata returned by datanodes. `close` releases the read client and closes chunk streams; `unbuffer` stores position and releases clients/buffers without closing the logical stream.

## Dependencies and Integration Points
It depends on `BlockExtendedInputStream` retry helpers, `ContainerProtocolCalls`, `XceiverClientFactory`, `Pipeline`, `BlockLocationInfo`, `ChunkInputStream`, block tokens, and Ozone checksum config. `BlockInputStreamFactoryImpl` creates this for non-EC reads when streaming read is unavailable or disabled. `MultipartInputStream` can aggregate it as a `PartInputStream`.

## Risks
The implementation assumes chunk metadata is ordered and lengths are accurate; inconsistent chunk EOFs are treated as corruption. Retry behavior depends on distinguishing storage/security/connectivity exceptions and on the refresh callback returning usable block location data. Seek state is subtle because pre-initialization `blockPosition`, `chunkIndexOfPrevPosition`, and chunk-local positions must remain coherent. The validator deliberately tolerates a last zero-length EC chunk at block length for HDDS-10682, so future validation changes must preserve that compatibility.

## Test Signals
`TestBlockInputStream`, `DummyBlockInputStream`, and `DummyBlockInputStreamWithRetry` exercise initialization, seek/read behavior, retry/refresh paths, and mocked chunk failures. `TestChunkInputStream` indirectly validates chunk-level behavior used here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockOutputStream.java

## Purpose
`BlockOutputStream` is the core buffered writer for writing one Ozone block to container datanodes. It batches user writes into `ChunkBuffer`s, emits `WriteChunk` requests, periodically emits `PutBlock`, tracks asynchronous responses, and coordinates retry, flush, close, checksum, and client cleanup semantics. `RatisBlockOutputStream` and `ECBlockOutputStream` specialize commit behavior.

## Important APIs and Types
Key public APIs are `write(int)`, `write(byte[], int, int)`, `flush()`, `close()`, `waitForAllPendingFlushes()`, `writeOnRetry(long)`, `cleanup(boolean)`, and getters for block ID, buffer pool, failed servers, flushed length, and written length. Important extension hooks include `executePutBlock(boolean, boolean)`, `sendWatchForCommit(long)`, `updateCommitInfo(...)`, `waitOnFlushFuture()`, `releaseBuffersOnException()`, and `cleanup()`. `PutBlockResult` carries commit index and response.

## Control Flow
Writes allocate from `BufferPool`, copy bytes into `currentBuffer`, update `writtenDataLength`, and call `writeChunkIfNeeded()` when the buffer fills. Full buffers are sent using `writeChunkToContainer`, which computes checksum, creates `ChunkInfo`, validates monotonic offsets, updates `containerBlockData`, and sends async RPCs. `doFlushOrWatchIfNeeded()` emits `PutBlock` every flush period and records a future chain that waits for commit. `flush` and `close` call `handleFlushInternalSynchronized`, which flushes partial buffers, commits uncommitted chunks, or sends a forced EOF `PutBlock` on close. Piggybacking can combine `WriteChunk` and `PutBlock` when datanode versions support it.

## State and Persistence Behavior
The stream tracks the current block ID and BCSID, planned block size, EOF flag, previous chunk, chunk index/offset, buffer pool state, asynchronous IO exception, total write/put lengths, pending buffer list, checksum state, token string, replication index, and pending flush futures. Persistent effects are container chunk writes and committed block metadata. Incremental chunk-list mode keeps only newly sent chunks in `PutBlock` and uses a direct `lastChunkBuffer` to maintain partial chunk checksum state.

## Dependencies and Integration Points
It integrates with `ContainerProtocolCalls.writeChunkAsync` and `putBlockAsync`, `XceiverClientFactory`, `XceiverClientSpi`, `ContainerClientMetrics`, `Checksum`, `ChunkBuffer`, `DirectBufferPool`, `StreamBufferArgs`, and datanode version feature gates. `RatisBlockOutputStream` supplies commit watching and buffer release; `ECBlockOutputStream` changes putBlock semantics for EC metadata and does not use Ratis commit watching.

## Risks
Most risk is in asynchronous ordering and resource release. `ioException` causes later operations to fail with the original error, but futures may complete concurrently. `bufferList` is handed off to putBlock handling and must not be reused incorrectly. Incremental chunk-list checksum maintenance depends on exact partial/full chunk offset handling and `lastChunkBuffer` lifecycle. Interrupt handling wraps errors as `IOException`; callers relying on thread interrupt state should check it. Version-gated piggybacking must remain aligned with datanode compatibility.

## Test Signals
`TestBlockOutputStreamCorrectness` covers Ratis/EC chunk and putBlock correctness, checksum-related behavior, and stream construction. Buffer release and blocking assumptions are supported by `TestBufferPool`; integration behavior is also exercised by broader Ozone client write tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BufferPool.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BufferPool.java

## Purpose
`BufferPool` is a bounded, blocking pool of reusable `ChunkBuffer` instances for block writes. It prevents unbounded client memory usage by limiting concurrently allocated buffers and reusing released buffers.

## Important APIs and Types
Primary APIs are `allocateBuffer(int)`, `releaseBuffer(ChunkBuffer)`, `waitUntilAvailable()`, `clearBufferPool()`, `computeBufferData()`, `getAllocatedBuffers()`, `getNumberOfUsedBuffers()`, `isAtCapacity()`, and size/capacity getters. `empty()` returns a static zero-capacity pool used by some tests and EC code paths. The pool also exposes a `byteStringConversion()` strategy for turning `ByteBuffer`s into Ratis `ByteString`s.

## Control Flow
`allocateBuffer` takes an interruptible lock, asserts total created buffers do not exceed capacity, waits on `notFull` while allocated size equals capacity, then reuses a released buffer or allocates a new `ChunkBuffer`. `releaseBuffer` removes the exact object identity from the allocated list, clears it, appends it to the released list, clears `currentBuffer` if needed, and signals one waiter.

## State and Persistence Behavior
All state is in memory: buffer size, capacity, allocated list, released list, current buffer, lock, and condition. No data is persisted. `clearBufferPool` closes all tracked buffers and resets lists.

## Dependencies and Integration Points
`BlockOutputStream` allocates buffers for user writes and `CommitWatcher` releases them after commit. The pool uses `ChunkBuffer`, Ratis `Preconditions`, and `ByteStringConversion`.

## Risks
Callers must release only buffers obtained from this pool; identity-based removal intentionally rejects equivalent but different objects. Capacity zero pools cannot allocate without waiting forever, so they are only safe in paths that do not call allocation. Interruptions during allocation propagate through block stream error handling. Incorrect commit watcher behavior can starve writers blocked on `notFull`.

## Test Signals
`TestBufferPool` covers allocation, release, capacity blocking, concurrent waits, reallocation, empty state, and pool accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteArrayReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteArrayReader.java

## Purpose
`ByteArrayReader` adapts the generic `ByteReaderStrategy` interface to Java byte-array reads. It lets stream implementations share read-loop logic across `read(byte[], int, int)` and `read(ByteBuffer)`.

## Important APIs and Types
The constructor validates byte array, offset, and length. `readFromBlock(InputStream, int)` delegates to `InputStream.read(byte[], offset, numBytesToRead)`, advances its offset, reduces target length, and returns bytes read. `getTargetLength()` exposes remaining desired bytes.

## Control Flow
Higher-level streams pass this strategy into `ExtendedInputStream.read(ByteReaderStrategy)`. Each successful delegated read mutates the strategy so the next loop iteration appends data to the next byte-array position.

## State and Persistence Behavior
It stores only the target array reference, mutable offset, and mutable target length. It does not own buffers and performs no persistence.

## Dependencies and Integration Points
Used by `ExtendedInputStream.read(byte[], int, int)`, `BlockInputStream`, `MultipartInputStream`, and EC readers through the shared strategy interface.

## Risks
The method subtracts `numBytesRead` without handling `-1`; callers in this code generally avoid delegating when EOF is expected and verify exact reads, but this strategy is not defensive if used directly with an EOF-producing stream. Array-backed ownership remains with the caller.

## Test Signals
Coverage is mostly indirect through stream tests such as `TestBlockInputStream`, `TestECBlockInputStream`, and multipart/key stream tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteArrayReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferReader.java

## Purpose
`ByteBufferReader` adapts `ByteReaderStrategy` to `ByteBuffer` targets, allowing shared higher-level read loops to fill NIO buffers.

## Important APIs and Types
The constructor requires a non-null target buffer and captures its initial remaining bytes as `targetLen`. `readFromBlock(InputStream, int)` temporarily narrows the target buffer limit when the stream should read fewer bytes than the buffer has remaining, delegates to `ByteBufferReadable.read(ByteBuffer)`, restores the limit, and reduces `targetLen`. `getBuffer()` and `readImpl()` are package-visible hooks used by specialized positioned reads.

## Control Flow
The strategy asserts the underlying stream implements Hadoop `ByteBufferReadable`. This is true for `ChunkInputStream`, `ExtendedInputStream` subclasses, and the streaming block path. Limit narrowing ensures a read loop does not overrun EC cell/chunk boundaries even when the caller's buffer is larger.

## State and Persistence Behavior
State is the caller-supplied `ByteBuffer` and remaining target length. Mutations are normal buffer position advancement plus temporary limit changes. No persistence occurs.

## Dependencies and Integration Points
Used by `ExtendedInputStream.read(ByteBuffer)`, `MultipartInputStream.readFully`, `ECBlockInputStream`, and reconstructed EC stream wrappers.

## Risks
If the underlying `InputStream` is not `ByteBufferReadable`, `readImpl` fails via Ratis `Preconditions.assertInstanceOf`. Like `ByteArrayReader`, it assumes callers avoid unexpected EOF; subtracting `-1` would corrupt target length if used incorrectly.

## Test Signals
Indirectly tested through byte-buffer read variants in block, chunk, streaming, multipart, and EC stream tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferStreamOutput.java

## Purpose
`ByteBufferStreamOutput` is an output abstraction like `OutputStream`, but centered on `ByteBuffer` writes while retaining `Closeable` and Hadoop `Syncable` behavior.

## Important APIs and Types
It declares `write(ByteBuffer, int, int)`, `flush()`, inherits `close()`, `hflush()`, and `hsync()`, and provides a default `write(ByteBuffer)` implementation using a read-only duplicate of the input buffer.

## Control Flow
The default method avoids mutating the original buffer's position or limit by writing from a read-only duplicate over its current remaining span. Concrete classes decide whether byte-buffer or byte-array writes are primary.

## State and Persistence Behavior
The interface has no state. Persistence semantics are supplied by implementors such as byte-array or byte-buffer stream output adapters and Ozone key/block output streams.

## Dependencies and Integration Points
Implemented by `ByteArrayStreamOutput` and `ByteBufferOutputStream`; used wherever Ozone output APIs need both byte-array and byte-buffer surfaces plus sync semantics.

## Risks
Implementations must define offset semantics consistently. The default `write(ByteBuffer)` passes the duplicate's current position as `off`, so implementors should treat `off` as a buffer position, not necessarily a backing-array offset.

## Test Signals
No direct test surfaced in this subset; behavior is indirectly covered by client output stream tests that exercise byte-array and byte-buffer write paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteReaderStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteReaderStrategy.java

## Purpose
`ByteReaderStrategy` is the minimal strategy interface used to unify byte-array and `ByteBuffer` read loops in Ozone stream classes.

## Important APIs and Types
It declares `readFromBlock(InputStream, int)` and `getTargetLength()`. Implementations include `ByteArrayReader` and `ByteBufferReader`.

## Control Flow
`ExtendedInputStream` wraps standard read methods into strategies, then calls subclass `readWithStrategy`. Block, multipart, and EC streams can repeatedly ask a strategy how much remains and delegate bounded reads to the current child stream.

## State and Persistence Behavior
The interface has no state. Implementations usually hold caller buffers and mutate remaining byte counts.

## Dependencies and Integration Points
It decouples stream traversal logic from target buffer type across `BlockInputStream`, `MultipartInputStream`, `ECBlockInputStream`, and wrappers.

## Risks
The contract relies on implementations updating `getTargetLength()` accurately after each read. EOF handling is not specified in the interface, so callers must enforce their own read/EOF invariants.

## Test Signals
Covered indirectly by all stream read tests using both byte arrays and NIO buffers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteReaderStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ChunkInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ChunkInputStream.java

## Purpose
`ChunkInputStream` reads one container chunk and exposes it as a seekable, unbufferable, byte-buffer-readable `InputStream`. It performs partial chunk RPCs, checksum-boundary adjustment, checksum validation, and local buffer management.

## Important APIs and Types
Important APIs are `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `seek(long)`, `getPos()`, `close()`, `unbuffer()`, `getRemaining()`, `readChunk(ChunkInfo)`, and testing accessors. It stores `ChunkInfo`, block ID, datanode block ID, `XceiverClientFactory`, client, pipeline supplier, token supplier, checksum flag, `ByteBuffer[]` cache, buffer offsets, and chunk position markers.

## Control Flow
Reads acquire a read client and call `prepareRead`. If the desired position is not in current buffers, `readChunkFromContainer` computes the actual chunk byte range. With checksum verification enabled, it expands reads to checksum boundaries, sends `ContainerProtocolCalls.readChunk`, validates response size and checksum, then caches returned read-only byte buffers. `prepareRead` returns available bytes from the active buffer, and read methods copy from that buffer to the caller. Exhausted buffers are released incrementally or entirely.

## State and Persistence Behavior
State is in-memory cache and positioning only. `bufferOffsetWrtChunkData`, `buffersSize`, `bufferOffsets`, `bufferIndex`, `firstUnreleasedBufferIndex`, and `chunkPosition` jointly define the logical read position. `unbuffer` stores the logical position, drops cached buffers, and releases the client.

## Dependencies and Integration Points
Created by `BlockInputStream`. It depends on `ContainerProtocolCalls.readChunk`, `Checksum`, `ChecksumData`, `BufferUtils`, `Pipeline`, `XceiverClientFactory`, block tokens, and Hadoop seek/unbuffer/readable interfaces.

## Risks
Positioning is delicate when checksum-boundary reads return extra bytes before the requested position. EOF and released-buffer logic must keep `getPos()` correct after buffers are nulled. If datanodes return `data` versus `dataBuffers`, both size and checksum validation paths must remain equivalent. `ByteBuffer.capacity()` is used in some seek calculations, so unexpected buffer capacity/limit relationships could be risky.

## Test Signals
`TestChunkInputStream` and `DummyChunkInputStream` cover chunk reads, seeks, checksum-boundary behavior, cached buffer state, and error paths. `TestBlockInputStream` exercises it through block-level traversal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ChunkInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/CommitWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/CommitWatcher.java

## Purpose
`CommitWatcher` specializes `AbstractCommitWatcher` for `ChunkBuffer`-backed Ratis block writes. It watches commit indexes and releases committed write buffers back to `BufferPool`.

## Important APIs and Types
The constructor accepts a `BufferPool` and `XceiverClientSpi`. `releaseBuffers(long)` removes buffers associated with a committed log index, releases them to the pool, and accounts acknowledged data length. `cleanup()` delegates to the abstract watcher cleanup.

## Control Flow
`RatisBlockOutputStream` records commit index to buffer-list mappings after successful putBlock. When watch-for-commit completes, the abstract watcher calls `releaseBuffers`, which sums each buffer's position as acknowledged bytes and returns the buffer to the pool.

## State and Persistence Behavior
This class owns only a reference to `BufferPool`; commit maps and counters live in the abstract superclass. It affects in-memory buffer lifecycle, not persisted block data.

## Dependencies and Integration Points
Used only by `RatisBlockOutputStream`. It depends on Ratis client commit watching through `AbstractCommitWatcher` and on `BufferPool.releaseBuffer`.

## Risks
The code comment notes possible ordering issues when concurrent watch-for-commit executions update flushed length semantics. If buffers are released under the wrong index, writers may reuse data before replication is sufficiently acknowledged.

## Test Signals
Covered indirectly by `RatisBlockOutputStream` and `BlockOutputStream` tests that assert buffer release, acknowledged data length, flush, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/CommitWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ECBlockOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ECBlockOutputStream.java

## Purpose
`ECBlockOutputStream` specializes `BlockOutputStream` for one internal EC block. It writes chunks to a single datanode pipeline, manages EC block-group metadata, and attaches stripe checksum information where required.

## Important APIs and Types
It overrides `write(byte[], int, int)`, exposes `write(ByteBuffer)`, and provides EC-aware `executePutBlock` overloads for block group length with either peer block data or checksum bytes. It also overrides `executePutBlock(boolean, boolean)` to return a putBlock response future without Ratis commit watching. `getDatanodeDetails()` exposes the single target datanode.

## Control Flow
Writes wrap the caller data in `ChunkBuffer`, call `writeChunkToContainer`, and update written length. Before putBlock, the stream writes `BLOCK_GROUP_LEN_KEY_IN_PUT_BLOCK` metadata. For checksum propagation, it chooses checksum-bearing block data, trims checksum chunks based on `blockGroupLength` and EC chunk size, replaces current chunk `stripeChecksum` fields, or updates the final chunk checksum from a supplied `ByteString`. It then sends `putBlockAsync` and validates the response.

## State and Persistence Behavior
Additional state is the closest datanode and futures for current chunk and putBlock responses. Persistent effects are internal EC chunk writes and block metadata containing block-group length and stripe checksums. It inherits chunk list, checksum, token, and exception state from `BlockOutputStream`.

## Dependencies and Integration Points
Used by EC key/block write flows. It depends on `ECReplicationConfig`, container `BlockData`, `ChunkInfo`, `OzoneConsts.BLOCK_GROUP_LEN_KEY_IN_PUT_BLOCK`, and base async RPC helpers.

## Risks
Checksum selection is subtle: only parity and first replica behavior differs, and the method must handle empty chunks, dirty data, partial groups, and mismatched chunk counts. `maxDataSizeByGroup.get(blockGroupLength).get()` assumes matching block data exists. Unlike Ratis streams, commit index is returned as zero, so callers must not expect Ratis-style buffer release behavior.

## Test Signals
`TestBlockOutputStreamCorrectness` creates EC block output streams and validates EC checksum/block metadata behavior. Broader EC write tests should cover partial stripe and failure cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ECBlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ExtendedInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ExtendedInputStream.java

## Purpose
`ExtendedInputStream` is the shared base class for Ozone input streams that need `InputStream`, Hadoop `Seekable`, `CanUnbuffer`, `ByteBufferReadable`, and `StreamCapabilities` behavior.

## Important APIs and Types
It implements `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `read(ByteReaderStrategy)`, default `seek`, default `seekToNewSource`, `hasCapability`, and a default unsupported positioned `readFully(long, ByteBuffer)`. Subclasses implement `readWithStrategy(ByteReaderStrategy)`.

## Control Flow
Standard read overloads are converted into `ByteArrayReader` or `ByteBufferReader`, then delegated to subclass traversal logic. Single-byte read uses a one-byte array and unsigned conversion. Capabilities advertise byte-buffer read and unbuffer support.

## State and Persistence Behavior
The base class has no mutable stream state beyond inherited `InputStream` behavior. It persists nothing.

## Dependencies and Integration Points
Base class for `BlockExtendedInputStream` descendants, `MultipartInputStream`, EC stream wrappers, and other Ozone read abstractions. It uses Hadoop stream capability constants and Apache Commons `NotImplementedException`.

## Risks
Default `seek` throws `NotImplementedException`, so subclasses must override it if they expose seekable behavior. `readFully` default returns false rather than throwing, so callers must check the boolean to know positioned reads are unsupported.

## Test Signals
Covered indirectly by every subclass read test, including block, multipart, streaming, and EC tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ExtendedInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/MultipartInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/MultipartInputStream.java

## Purpose
`MultipartInputStream` concatenates multiple `PartInputStream` instances into one key-level stream. It supports read, seek, skip, available, close, unbuffer, and an optimized positioned-read path when all parts are `StreamBlockInputStream`s.

## Important APIs and Types
The constructor accepts a key name and list of `PartInputStream`s, computes `partOffsets`, total length, and whether the parts are streaming block streams. Key APIs are `readWithStrategy`, `seek`, `readFully(long, ByteBuffer)`, `initialize`, `getPos`, `available`, `skip`, `close`, `getLength`, and testing accessors.

## Control Flow
Reads loop over the current part, delegate bounded strategy reads, and advance `partIndex` when a part is exhausted. `seek` initializes block parts if needed, binary-searches `partOffsets`, resets previous and later parts, and seeks the selected part to the local offset. `readFully` for streaming block parts saves the old position, seeks to the requested position, uses a custom `ByteBufferReader` that invokes `StreamBlockInputStream.readFully`, then restores the old position.

## State and Persistence Behavior
State is in-memory: key, immutable parts list, total length, offsets, closed flag, current/previous part index, and initialized flag. It does not persist data; it coordinates underlying part streams.

## Dependencies and Integration Points
It composes `PartInputStream`, `BlockInputStream`, and `StreamBlockInputStream`, and is used by higher Ozone key input streams to read keys split over multiple blocks/parts.

## Risks
Seek reset behavior can be expensive for many parts and relies on each part's seek implementation being idempotent. The constructor enforces all-streaming type only by checking if the first part is streaming and asserting subsequent parts; mixed lists with first non-streaming do not trigger that assertion. Positioned read support returns false for non-streaming parts, so callers must handle fallback.

## Test Signals
Multipart/key input tests and `TestStreamBlockInputStream` indirectly validate stream-block positioned reads, seek, unbuffer, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/MultipartInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/PartInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/PartInputStream.java

## Purpose
`PartInputStream` defines the minimal contract for a stream that can be a part of `MultipartInputStream`.

## Important APIs and Types
It extends Hadoop `CanUnbuffer` and `Seekable`, declares `getLength()` and `close()`, and provides a default `getRemaining()` as `getLength() - getPos()`.

## Control Flow
`MultipartInputStream` treats each part as a seekable segment, using `getRemaining()` to decide when to advance to the next part and `seek` to position within a selected segment.

## State and Persistence Behavior
The interface has no state. Implementations maintain their own positions, buffers, and clients.

## Dependencies and Integration Points
Implemented by block-level input streams such as `BlockExtendedInputStream` descendants. It is the direct composition boundary for multipart reads.

## Risks
`getRemaining()` assumes `getPos()` never exceeds length. Implementations must keep position and length coherent after failed reads, unbuffer, and close.

## Test Signals
Covered through `MultipartInputStream`, block input, stream block input, and EC block input tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/PartInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/RatisBlockOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/RatisBlockOutputStream.java

## Purpose
`RatisBlockOutputStream` is the Ratis-specific block writer. It adds commit-index watching and `Syncable` flush semantics to `BlockOutputStream`.

## Important APIs and Types
The constructor builds the base stream and a `CommitWatcher`. Overrides include `getTotalAckDataLength`, `releaseBuffersOnException`, `sendWatchForCommit`, `updateCommitInfo`, `waitOnFlushFuture`, `cleanup`, `hflush`, and `hsync`. `getCommitIndex2flushedDataMap` is visible for tests.

## Control Flow
After base writes/putBlocks produce Ratis log indexes, this class maps those log indexes to the buffers flushed in that commit. `sendWatchForCommit` asynchronously waits for replication. When complete, `CommitWatcher` releases buffers and updates acknowledged length. `hsync`/`hflush` call base `handleFlush(false)` while the stream is open.

## State and Persistence Behavior
Ratis-specific state lives in `CommitWatcher`: commit-index maps and ack length. Persistent data effects are inherited from base write/putBlock RPCs; this class controls when local buffers can be reused.

## Dependencies and Integration Points
Used for RATIS replication write paths. It depends on `CommitWatcher`, `BufferPool`, `XceiverClientReply`, Hadoop `Syncable`, and the base block stream asynchronous flush pipeline.

## Risks
Correctness depends on every successful putBlock updating commit info with the right buffer list and every wait releasing buffers only after the desired replication criteria. `hsync` while a prior async flush is pending must preserve ordering through `lastFlushFuture`.

## Test Signals
`TestBlockOutputStreamCorrectness` and buffer pool tests cover Ratis block output behavior, flushes, commits, buffer release, and ack accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/RatisBlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBlockInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBlockInputStream.java

## Purpose
`StreamBlockInputStream` reads an entire block through the newer streaming gRPC read-block protocol rather than issuing per-chunk read RPCs. It supports normal reads, byte-buffer reads, seek, unbuffer, pre-read, response queueing, checksum verification, timeouts, and pipeline refresh on retryable errors.

## Important APIs and Types
Public APIs include `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, package `readFully(ByteBuffer, boolean)`, `seek`, `getPos`, `unbuffer`, `close`, and config getters for pre-read size, response data size, and timeout. The nested `StreamingReader` implements `StreamingReaderSpi` and handles gRPC observer callbacks.

## Control Flow
Reads call `dataAvailableToRead`, which initializes a `StreamingReader` and client stream if needed, then requests enough data through `readBlock`. `requestedLength` tracks bytes already requested from the server and may include configured pre-read. Responses are queued by `StreamingReader.onNext`, verified by checksum if enabled, and drained by `readFromQueue`, which adjusts for checksum-boundary offsets before returning a read-only `ByteBuffer`. `advancePosition` closes the stream at block EOF. `seek` closes the current stream, updates logical position, and sets `requestedLength` to the seek position.

## State and Persistence Behavior
State includes block ID/length, response sizing, pre-read settings, timeout, pipeline/token refs, client, current buffer, position, requested length, streaming reader, retry count, and refresh callback. It does not persist data; it consumes persisted block bytes from datanodes. Closing/unbuffering releases client resources and completes/cancels gRPC streams.

## Dependencies and Integration Points
Created by `BlockInputStreamFactoryImpl` when config enables stream reads and all datanodes support `STREAM_BLOCK_SUPPORT`. It uses `XceiverClientGrpc`, `StreamingReadResponse`, `ContainerProtocolCalls.buildReadBlockCommandProto`, `Checksum`, and block-location refresh helpers.

## Risks
Timeout and queue completion logic is critical: `poll` checks queue emptiness before `future.isDone()` to avoid dropping a response delivered just before completion. `readFromQueue` assumes `poll()` returns a non-null item; unexpected stream completion without data could cause null handling issues. Seek/close races are guarded by synchronization, but gRPC callbacks can arrive asynchronously. Checksum failure attempts to call request observer `onError` and release stream resources.

## Test Signals
`TestStreamBlockInputStream` covers custom configuration, stream close/cancel behavior, timeout/queue behavior, checksum and observer paths, and resource release. `BlockInputStreamFactoryImpl` tests cover selection of this class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBuffer.java

## Purpose
`StreamBuffer` is a thin wrapper around `ByteBuffer` used by the older streaming write commit watcher path.

## Important APIs and Types
It offers constructors from a whole buffer or a read-only slice defined by offset/length, `duplicate()`, `remaining()`, `position()`, `put(StreamBuffer)`, and `allocate(int)`.

## Control Flow
The slice constructor creates a read-only buffer view with adjusted position and limit. `put` copies from another wrapped buffer into this buffer. Commit watchers use `position()` to account acknowledged bytes.

## State and Persistence Behavior
State is only the wrapped `ByteBuffer`. No persistence occurs.

## Dependencies and Integration Points
Used by `StreamCommitWatcher` and streaming write-related code in the storage package. It is analogous to `ChunkBuffer` for paths that operate directly on `ByteBuffer`.

## Risks
The slice constructor stores a buffer with non-zero position; callers must understand that `remaining()` and `position()` reflect the view, not necessarily a standalone zero-based buffer. `put` mutates both destination and source wrapped buffer positions.

## Test Signals
No direct test surfaced in this subset; coverage is likely through streaming write tests if enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamCommitWatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamCommitWatcher.java

## Purpose
`StreamCommitWatcher` specializes `AbstractCommitWatcher` for `StreamBuffer` lists. It releases stream buffers from an external list once the associated Ratis commit index is replicated.

## Important APIs and Types
The constructor accepts an `XceiverClientSpi` and a shared `List<StreamBuffer>`. `releaseBuffers(long)` removes buffers tracked for a commit index, subtracts them from the shared list, and increments acknowledged data length by each buffer's position.

## Control Flow
When the abstract watcher completes a commit watch, this class removes the committed buffers from both the superclass index map and the caller-provided buffer list. It then updates total ack length.

## State and Persistence Behavior
The only local state is a reference to the shared buffer list. It does not persist data; it controls in-memory buffer retention.

## Dependencies and Integration Points
Used by streaming write paths that use `StreamBuffer` rather than `ChunkBuffer`. It depends on `AbstractCommitWatcher` and Ratis `XceiverClientSpi`.

## Risks
The shared list must be safe for the access pattern used by callers. Removal is by object equality, so duplicate/equal wrappers could cause surprising behavior if equality is later added to `StreamBuffer`.

## Test Signals
No direct test was identified. Behavior should be covered by any stream write tests that assert ack length and buffer list shrinking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamCommitWatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.hdds.scm.storage` as low-level IO streams for uploading and downloading chunks from the container service.

## Important APIs and Types
It declares only the package and package-level Javadoc. The package contains block/chunk input streams, block output streams, buffer pools, commit watchers, strategy adapters, and multipart stream composition.

## Control Flow
No runtime control flow exists in this file.

## State and Persistence Behavior
No state or persistence behavior exists in this file.

## Dependencies and Integration Points
The package is integrated by Ozone client IO factories and higher key streams that need container-level block and chunk access.

## Risks
The descriptor is documentation-only. Risk is limited to stale package documentation if the package grows beyond upload/download stream responsibilities.

## Test Signals
No direct tests are expected for package-info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BadDataLocationException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BadDataLocationException.java

## Purpose
`BadDataLocationException` is an `IOException` that carries one or more failed datanode locations and a failed EC location index. It lets EC read code report which replica/index failed so callers can retry with spare locations or fail over to reconstruction.

## Important APIs and Types
Constructors accept a message, a `DatanodeDetails`, a failed index, a cause, or a list of failed locations. Accessors are `getFailedLocations()`, `addFailedLocations(List<DatanodeDetails>)`, and `getFailedLocationIndex()`.

## Control Flow
`ECBlockInputStream` throws this when a direct internal block stream fails. `ECBlockInputStreamProxy` catches it, records failed datanodes, and creates a reconstruction reader if direct EC reading cannot continue.

## State and Persistence Behavior
State is an in-memory mutable list of `DatanodeDetails` and an integer index. No persistence occurs.

## Dependencies and Integration Points
Used by EC read classes in `org.apache.hadoop.ozone.client.io`. It depends on `DatanodeDetails` and standard `IOException`.

## Risks
`getFailedLocations()` returns the mutable internal list, so callers can mutate exception state. The default `failedLocationIndex` is zero, which is meaningful for EC; callers should only consult it for constructors that set it intentionally.

## Test Signals
`TestECBlockInputStream`, `TestECBlockInputStreamProxy`, and reconstructed EC tests exercise propagation of failed locations and failover behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BadDataLocationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactory.java

## Purpose
`BlockInputStreamFactory` abstracts creation of the correct block input stream implementation for a replication configuration.

## Important APIs and Types
It declares `create(ReplicationConfig, BlockLocationInfo, Pipeline, Token<OzoneBlockTokenIdentifier>, XceiverClientFactory, Function<BlockID, BlockLocationInfo>, OzoneClientConfig)`, returning `BlockExtendedInputStream`.

## Control Flow
Implementations decide among EC proxy readers, streaming block readers, and classic chunk-based block readers.

## State and Persistence Behavior
The interface has no state. Implementations may own helper factories and pools.

## Dependencies and Integration Points
Used by key input stream construction and EC readers that need to open standalone internal block streams. `BlockInputStreamFactoryImpl` is the primary implementation.

## Risks
The factory is part of recursive EC construction: EC direct/reconstruction readers use it to create internal standalone block streams. Implementations must avoid recursively creating EC readers for those standalone internal reads.

## Test Signals
`TestBlockInputStreamFactoryImpl`, `TestECBlockInputStream`, and EC stream utility factories validate factory decisions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactoryImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactoryImpl.java

## Purpose
`BlockInputStreamFactoryImpl` chooses the concrete block reader for a block: EC proxy reader for EC replication, streaming block reader when enabled and supported by all datanodes, or classic `BlockInputStream` otherwise.

## Important APIs and Types
Static `getInstance(ByteBufferPool, Supplier<ExecutorService>)` creates the factory with EC reconstruction dependencies. Constructors wire `ECBlockInputStreamFactoryImpl`. `create(...)` selects the stream. `createBlockInputStream(...)` explicitly creates a classic Ratis/standalone `BlockInputStream`.

## Control Flow
`create` checks `repConfig.getReplicationType()`. EC configs produce `ECBlockInputStreamProxy`. Non-EC configs check `config.isStreamReadBlock()` and all pipeline datanode versions against `STREAM_BLOCK_SUPPORT`; if true, it creates `StreamBlockInputStream`, otherwise `BlockInputStream`.

## State and Persistence Behavior
State is the EC helper factory. It does not persist data.

## Dependencies and Integration Points
It integrates Ozone client IO with `BlockInputStream`, `StreamBlockInputStream`, `ECBlockInputStreamProxy`, `ECBlockInputStreamFactoryImpl`, `ElasticByteBufferPool`, and datanode version gates.

## Risks
Feature selection is version-sensitive. A single older datanode disables streaming reads for the whole pipeline. EC creation delegates to a proxy that may create further internal streams; incorrect replication config passed to internal creation could cause recursion or wrong stream type.

## Test Signals
`TestBlockInputStreamFactoryImpl` validates stream selection for EC, stream-read support, and fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockInputStreamFactoryImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BoundedElasticByteBufferPool.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BoundedElasticByteBufferPool.java

## Purpose
`BoundedElasticByteBufferPool` is a bounded implementation of Hadoop `ByteBufferPool`. It reuses heap and direct buffers while capping total cached buffer capacity to avoid unbounded memory growth in long-lived clients such as S3 Gateway.

## Important APIs and Types
`getBuffer(boolean, int)` retrieves the smallest cached buffer with capacity at least the requested length or allocates a new buffer. `putBuffer(ByteBuffer)` clears and caches a returned buffer only if doing so would not exceed `maxPoolSize`. `getCurrentPoolSize()` is visible for tests. Internal `Key` sorts buffers by capacity then logical insertion timestamp.

## Control Flow
Two `TreeMap<Key, ByteBuffer>` instances separate heap and direct buffers. A synchronized `getBuffer` uses `ceilingEntry(new Key(length, 0))`, removes the selected buffer, decrements current pool size, clears it, and returns it. `putBuffer` rejects nulls and over-budget returns, then stores the buffer with a unique logical timestamp and increments current size.

## State and Persistence Behavior
State is in-memory buffer maps, max pool size, current cached capacity counter, and logical timestamp. No persistence occurs.

## Dependencies and Integration Points
Can be supplied to `BlockInputStreamFactoryImpl` and EC reconstruction streams through the `ByteBufferPool` interface. Uses Guava `ComparisonChain` and Apache Commons `HashCodeBuilder`.

## Risks
The pool accounts cached buffer capacity, not outstanding allocated buffers. Very large returned buffers may be dropped, which is intended but can increase allocation churn. All operations are synchronized; high-concurrency read reconstruction could contend on this pool.

## Test Signals
`TestBoundedElasticByteBufferPool` covers buffer reuse, direct/heap separation, max-size enforcement, and size accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BoundedElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteArrayStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteArrayStreamOutput.java

## Purpose
`ByteArrayStreamOutput` is an abstract adapter for output streams whose optimized primitive is `write(byte[], int, int)` but that also implement `ByteBufferStreamOutput`.

## Important APIs and Types
It implements `write(ByteBuffer, int, int)` and `write(int)`. Subclasses must provide optimized byte-array write behavior and may override byte-buffer writes. Non-array byte buffers are copied through a temporary byte array capped at 64 KiB.

## Control Flow
For array-backed buffers, the method writes the backing array directly. For non-array buffers, it repeatedly creates a read-only duplicate, positions/limits it to the current segment, copies into the reusable temporary array, and writes that array segment.

## State and Persistence Behavior
No instance state is defined. Persistence/output effects are supplied by subclass implementations.

## Dependencies and Integration Points
Implements `ByteBufferStreamOutput` and extends `OutputStream`, providing compatibility for Ozone output classes that primarily accept byte arrays.

## Risks
For array-backed buffers, the code passes `off` directly as an array offset; callers must ensure `off` matches backing-array coordinates rather than just `buffer.position()` for sliced buffers. The non-array path avoids mutating the original buffer but copies data.

## Test Signals
Indirectly covered through output stream tests that write direct/read-only `ByteBuffer`s and byte arrays.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteArrayStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteBufferOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteBufferOutputStream.java

## Purpose
`ByteBufferOutputStream` is the complementary abstract adapter for output streams whose optimized primitive is `write(ByteBuffer, int, int)` but that must also behave like an `OutputStream`.

## Important APIs and Types
It implements `write(byte[])`, `write(byte[], int, int)`, and `write(int)` by wrapping bytes in `ByteBuffer` and delegating to `ByteBufferStreamOutput` methods. Subclasses implement the byte-buffer write method.

## Control Flow
Byte-array writes create heap `ByteBuffer` wrappers over the caller array and pass them through the byte-buffer output path. Single-byte writes allocate a one-byte array.

## State and Persistence Behavior
No state is stored in this abstract class. Output effects are defined by subclasses.

## Dependencies and Integration Points
Implements `ByteBufferStreamOutput`, extends `OutputStream`, and uses Jakarta `@Nonnull` annotations.

## Risks
Wrapping the caller array means subclasses must complete or copy the data before returning if they retain buffers asynchronously. Single-byte writes allocate each call unless subclasses override.

## Test Signals
Indirectly covered by Ozone output classes that inherit this adapter and by byte-buffer write tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteBufferOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStream.java

## Purpose
`ECBlockInputStream` reads an EC block group directly when all required data locations are available. It maps logical block-group offsets to internal EC data block streams and reads one EC cell at a time.

## Important APIs and Types
Important APIs are `read(byte[], int, int)`, `read(ByteBuffer)`, `readWithStrategy`, `seek`, `getPos`, `getLength`, `getBlockID`, `hasSufficientLocations`, `currentStreamIndex`, `getOrOpenStream`, `internalBlockLength`, and `ecPipelineRefreshFunction`. It stores EC config, chunk/stripe size, block location info, data locations, spare locations, per-index internal streams, failed locations, position, and seek flag.

## Control Flow
The constructor extracts EC replica indexes from the block pipeline into `dataLocations` and spare lists. Reads use `currentStreamIndex()` to pick the data replica for the current logical EC cell, lazily open a standalone one-node block stream for that replica, bound the read by EC chunk boundary, caller buffer, and block remaining bytes, then advance logical position. If a direct stream fails, `BadDataLocationException` triggers replacement with a spare location and retry; otherwise the exception propagates to the proxy for reconstruction failover.

## State and Persistence Behavior
State is in-memory reader position, per-index stream cache, location arrays, failed location list, and seek flag. It reads persisted internal block data through standalone pipelines and does not persist data.

## Dependencies and Integration Points
Created by `ECBlockInputStreamFactoryImpl` for non-reconstruction EC reads. It uses `BlockInputStreamFactory` to create internal standalone block streams, `ECReplicationConfig`, `Pipeline` replica indexes, `StandaloneReplicationConfig`, and `BadDataLocationException`.

## Risks
Correct EC offset math is central: `internalBlockLength`, `currentStreamIndex`, and lazy `seekStreamIfNecessary` must align with EC chunk and stripe sizes. Spare location handling only retries if a spare exists for the same index; otherwise proxy-level reconstruction is needed. The direct reader assumes data locations are sufficient for the block length.

## Test Signals
`TestECBlockInputStream` covers internal block length, direct reads, seek behavior, spare datanode retry, and failure cases. `TestECBlockInputStreamProxy` covers proxy failover from this reader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactory.java

## Purpose
`ECBlockInputStreamFactory` abstracts creation of EC block readers, selecting between direct EC reads and reconstruction reads based on location availability.

## Important APIs and Types
It declares `create(boolean missingLocations, List<DatanodeDetails> failedLocations, ReplicationConfig, BlockLocationInfo, XceiverClientFactory, Function<BlockID, BlockLocationInfo>, OzoneClientConfig)`, returning `BlockExtendedInputStream`.

## Control Flow
Implementations inspect `missingLocations`: false creates a direct `ECBlockInputStream`; true creates a reconstruction wrapper around `ECBlockReconstructedStripeInputStream`, seeding known failed datanodes.

## State and Persistence Behavior
The interface has no state or persistence behavior.

## Dependencies and Integration Points
Used by `ECBlockInputStreamProxy`, with `ECBlockInputStreamFactoryImpl` as the implementation.

## Risks
The boolean controls a major behavior difference. Incorrectly passing false with missing locations can cause direct read failures; incorrectly passing true increases CPU and read overhead through reconstruction.

## Test Signals
`TestECBlockInputStreamProxy` and EC factory utility tests validate direct versus reconstruction selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactoryImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactoryImpl.java

## Purpose
`ECBlockInputStreamFactoryImpl` constructs either direct EC readers or reconstruction readers, wiring the required byte-buffer pool and reconstruction executor.

## Important APIs and Types
Static `getInstance` creates the factory. The constructor stores a base `BlockInputStreamFactory`, `ByteBufferPool`, and `Supplier<ExecutorService>`. `create(...)` returns `ECBlockInputStream` or `ECBlockReconstructedInputStream`.

## Control Flow
If `missingLocations` is true, it creates an `ECBlockReconstructedStripeInputStream`, adds known failed datanodes, then wraps it in `ECBlockReconstructedInputStream` to provide normal stream semantics. Otherwise it creates direct `ECBlockInputStream`.

## State and Persistence Behavior
Factory state consists of dependencies only. It does not persist data.

## Dependencies and Integration Points
Used by `BlockInputStreamFactoryImpl` and `ECBlockInputStreamProxy`. It integrates `ByteBufferPool`, reconstruction executor supplier, direct EC reader, stripe reconstruction reader, and normal reconstructed stream wrapper.

## Risks
Each reconstruction reader obtains an executor from the supplier; lifecycle ownership is not handled in this factory, so supplier behavior matters. Passing failed locations before initialization is required because the stripe reader rejects failed-datanode updates after reads begin.

## Test Signals
Covered by `TestECBlockInputStreamProxy`, `TestECBlockInputStream`, and reconstructed EC tests that use factory paths and test factories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamFactoryImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamProxy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamProxy.java

## Purpose
`ECBlockInputStreamProxy` is the top-level EC block-group reader. It chooses direct EC reading when enough data locations are available and fails over to reconstruction when locations are missing or direct reads fail.

## Important APIs and Types
Static helpers `expectedDataLocations` and `availableDataLocations` compute required and available data indexes. Public APIs include `read(byte[], int, int)`, `read(ByteBuffer)`, `seek`, `getPos`, `getRemaining`, `getLength`, `getBlockID`, `unbuffer`, and `close`.

## Control Flow
Construction calls `setReaderType()` to compare expected data locations against pipeline indexes, then `createBlockReader()`. Reads loop until the caller buffer fills or remaining bytes reach zero. If the active reader throws `BadDataLocationException` and it is not already a reconstruction reader, the proxy records failed locations, closes the direct reader, creates a reconstruction reader, seeks to the last position, resets the caller buffer to the mark, and retries. Seek failures in direct mode also trigger reconstruction failover.

## State and Persistence Behavior
State is the active `BlockExtendedInputStream`, reconstruction mode flag, failed location list, closed flag, and immutable construction dependencies. No persistence occurs.

## Dependencies and Integration Points
Created by `BlockInputStreamFactoryImpl` for EC replication configs. It depends on `ECBlockInputStreamFactory`, EC config, block location info, client factory, refresh callback, and client metrics for reconstruction totals/failures.

## Risks
Recursive retry after failover must preserve caller buffer marks and total read count. `failedLocations` is accumulated and passed into reconstruction; if it is incomplete, reconstruction may retry known-bad datanodes. Metrics are incremented only on reconstruction creation and reconstruction failure.

## Test Signals
`TestECBlockInputStreamProxy` covers expected/available location calculations, direct versus reconstruction reader creation, failover on bad locations, seek behavior, and close/unbuffer delegation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockInputStreamProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedInputStream.java

## Purpose
`ECBlockReconstructedInputStream` wraps `ECBlockReconstructedStripeInputStream` to expose normal `InputStream`/`ByteBufferReadable` semantics over reconstructed EC stripes.

## Important APIs and Types
It implements `read(byte[], int, int)`, `read(ByteBuffer)`, `seek`, `getPos`, `getLength`, `getRemaining`, `getBlockID`, `unbuffer`, and `close`. It uses a caller-independent `ByteBuffer[] bufs` of data buffers borrowed from a `ByteBufferPool`.

## Control Flow
Reads allocate one buffer per EC data chunk if needed. `selectNextBuffer` returns the next buffer with remaining data, or calls `readStripe()` to refill all buffers from the stripe reader. `readBufferToDest` copies bytes from selected stripe buffers into the caller buffer and advances logical position. At EOF, it frees buffers to reduce memory. `seek` positions the stripe reader to a stripe boundary, reads that stripe, advances buffer positions within the stripe to the requested offset, and updates `position`.

## State and Persistence Behavior
State is EC config, stripe reader, pooled buffers, byte-buffer pool, closed/unbuffer flags, and logical position. It does not persist data. `freeBuffers` returns borrowed buffers to the pool.

## Dependencies and Integration Points
Created by `ECBlockInputStreamFactoryImpl` when reconstruction is required. It relies on `ECBlockReconstructedStripeInputStream` for actual parallel reads and decoding, and on a `ByteBufferPool` for reusable stripe buffers.

## Risks
The wrapper assumes stripe buffers are returned ready to read. Seek forces a stripe read even if only a small offset is needed, which is expected but can be expensive. `readWithStrategy` is unimplemented, so callers must use byte-array or byte-buffer read paths that this class overrides.

## Test Signals
`TestECBlockReconstructedInputStream` covers normal reads, partial reads, EOF, seek, unbuffer, buffer reuse/freeing, and reconstructed stripe integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedStripeInputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedStripeInputStream.java

## Purpose
`ECBlockReconstructedStripeInputStream` reads full EC stripes when some data blocks are missing or marked bad. It can either reconstruct missing data chunks for client reads or recover specified data/parity chunks for offline recovery.

## Important APIs and Types
Main public APIs are `readStripe(ByteBuffer[])`, `recoverChunks(ByteBuffer[])`, `setRecoveryIndexes(Collection<Integer>)`, `addFailedDatanodes(Collection<DatanodeDetails>)`, `getFailedIndexes()`, `seek(long)`, `unbuffer`, and `close`. Important internal state includes decoder input/output buffers, missing/data/padding/parity index sets, selected indexes, internal buffer indexes, failed data indexes, byte-buffer pool, `RawErasureDecoder`, executor, and recovery indexes.

## Control Flow
Before the first read, `init()` creates the decoder, marks missing locations as failed, selects indexes, verifies sufficient locations, and allocates internal buffers. `read` validates caller buffers, assigns them to decoder inputs or outputs, clears internal buffers, sets limits for partial final stripes, and loads selected indexes in parallel using the executor. Failed reads mark indexes failed, seek back to the current stripe, reset caller buffers, and reinitialize with new selections. If indexes are missing, it pads short final-stripe buffers, flips inputs, decodes erased indexes into output buffers, and resets limits. Without missing indexes, it flips direct input buffers. Position advances by bytes in the stripe.

## State and Persistence Behavior
State is in-memory reconstruction working set. Internal buffers are borrowed from and returned to the `ByteBufferPool`. It does not persist data; it reads surviving data/parity internal blocks and reconstructs bytes in memory. At logical EOF it frees internal buffers and closes underlying streams without marking the reader closed.

## Dependencies and Integration Points
Extends `ECBlockInputStream` to reuse EC location handling and internal stream opening. It integrates with `RawErasureDecoder` from Ozone erasure-code utilities, `CodecUtil`, executor futures, `ByteBufferPool`, and `BadDataLocationException`.

## Risks
This is the highest-complexity reader in the subset. Index selection must choose enough data/padding/parity inputs and avoid failed/recovery indexes. Partial final stripes require precise limit and zero-padding behavior or decode output may contain garbage. Parallel reads rely on lower-level client timeouts; futures are waited without an additional timeout. `seek` only accepts stripe-aligned positions, so callers must use the wrapper for arbitrary seeks. Executor lifecycle is external.

## Test Signals
`TestECBlockReconstructedStripeInputStream` is extensive and covers missing indexes, parity selection, padding, full and partial stripes, offline recovery, failed datanodes, retries, insufficient locations, seek alignment, resource cleanup, and decoder integration. `TestECBlockReconstructedInputStream` covers wrapper-level behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ECBlockReconstructedStripeInputStream.java -->
