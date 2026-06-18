# Research: subset-b-007982

Grouped source research for Apache Ozone HDDS client I/O tests and common module configuration/versioning files. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/InsufficientLocationsException.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/InsufficientLocationsException.java

**Purpose:** Defines the checked exception used by erasure-coded input streams when the client cannot assemble enough readable EC locations to satisfy a read. It is intentionally narrow and extends `IOException`, allowing callers in the Ozone read path to handle it through normal stream error contracts.

**Important APIs/types/functions:** `InsufficientLocationsException` provides the standard four `IOException` constructor shapes: no-arg, message, message-plus-cause, and cause. There is no custom state, serialization field, or behavior.

**Control flow:** The class has no internal branching. Runtime control flow is entirely at throw sites in EC read/reconstruction code, where this type differentiates location quorum failures from checksum, security, EOF, or generic I/O failures.

**State and persistence:** Stateless except for inherited throwable message/cause/stack trace. It is not persisted directly, but may cross API boundaries as part of client read failure reporting.

**Dependencies and integration points:** Depends only on `java.io.IOException`. It is integrated by EC read classes such as reconstructed stripe streams and by tests that assert insufficient EC locations fail deterministically.

**Risks:** Because the type carries no structured metadata, callers cannot inspect missing indexes or failed datanodes unless the thrower encodes details in the message or uses a different exception. Changes to its inheritance would be source and behavior incompatible with stream APIs.

**Test signals:** The listed EC reconstructed-stripe tests assert this exception when too many locations fail, when available blocks are shorter than required, and when all usable locations fail on first read.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/InsufficientLocationsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java

**Purpose:** Supplies package-level documentation for `org.apache.hadoop.ozone.client.io`, identifying it as the home of Ozone I/O classes.

**Important APIs/types/functions:** No exported types or functions are declared. The Java package declaration is the only executable language element.

**Control flow:** None. This file affects generated Javadoc and package metadata only.

**State and persistence:** No state, persistence, or runtime configuration behavior.

**Dependencies and integration points:** Integrated by Java tooling, Javadoc, IDE package browsing, and checkstyle/license checks. It anchors documentation for the same package that contains block input stream factories, EC stream implementations, and related exceptions.

**Risks:** Low runtime risk. The main maintenance risk is documentation drift if the package grows beyond generic I/O classes or is reorganized.

**Test signals:** No direct tests. Build and style tooling validate package-info compilation and license format.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestContainerClientMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestContainerClientMetrics.java

**Purpose:** Verifies `ContainerClientMetrics` acquisition/release reference counting and write-chunk metric accounting by total, pipeline, and leader datanode.

**Important APIs/types/functions:** `setup()` drains any existing static `referenceCount` before each test. `testRecordChunkMetrics()` calls `ContainerClientMetrics.acquire()`, builds three `Pipeline` instances with distinct `PipelineID` values and two leader `DatanodeID` values, records chunk writes of 10, 20, and 30 bytes, and asserts totals plus per-pipeline/per-leader counters. `testReleaseWithoutUse()` asserts `release()` throws when the reference count is zero. `testAcquireAndRelease()` checks single and double acquire/release transitions. `createPipeline()` constructs an open pipeline using a mocked `ReplicationConfig`.

**Control flow:** The tests exercise both normal reference-count paths and the error branch for releasing without a matching acquire. The metric test drives aggregation by pipeline id and leader id, including two pipelines sharing a leader.

**State and persistence:** Uses and mutates static `ContainerClientMetrics.referenceCount`. Metrics are in-memory counters; no persistence is involved. The `@BeforeEach` reset loop is important because static state can leak across tests.

**Dependencies and integration points:** Depends on HDDS pipeline and datanode ID types, Mockito for `ReplicationConfig`, and JUnit assertions. It integrates with the client write path indirectly by validating the metrics object used by block output streams.

**Risks:** Direct access to package-visible/static `referenceCount` makes the test sensitive to implementation refactors. The cleanup loop assumes repeated `release()` is safe while count is positive. The test does not release the metrics acquired in `testRecordChunkMetrics()`, relying on the next setup to drain.

**Test signals:** Strong signal for counter identity and lifecycle invariants, but limited to write chunk metrics; it does not validate metric registration/unregistration with the Hadoop metrics system.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestContainerClientMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestOzoneClientConfig.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestOzoneClientConfig.java

**Purpose:** Tests binding of `OzoneClientConfig` from `OzoneConfiguration`, including size parsing, HBase enhancement gating, write concurrency defaults, and stream-read options.

**Important APIs/types/functions:** `missingSizeSuffix()` sets `ozone.client.bytes.per.checksum` as a raw integer and verifies the config falls back to `OZONE_CLIENT_BYTES_PER_CHECKSUM_MIN_SIZE`. `testClientHBaseEnhancementsAllowedTrue()` and `testClientHBaseEnhancementsAllowedFalse()` show that `ozone.client.hbase.enhancements.allowed` gates incremental chunk lists, putblock piggybacking, and max concurrent writes. `testStreamReadConfigParsing()` validates numeric byte values and a duration string for stream read pre-read size, response size, and timeout.

**Control flow:** Each test creates a fresh `OzoneConfiguration`, sets keys, calls `conf.getObject(OzoneClientConfig.class)`, and asserts the post-processed object values. The HBase tests exercise the conditional normalization branch where related options are honored or reset.

**State and persistence:** Configuration is transient and in-memory. The behavior affects persisted runtime settings only when a site config supplies these keys.

**Dependencies and integration points:** Depends on HDDS config reflection/annotation processing, `OzoneConfigKeys`, `Duration`, and JUnit. Integrates with client write and read stream code that consumes `OzoneClientConfig`.

**Risks:** Silent fallback for a missing size suffix can hide operator mistakes; this test documents current compatibility behavior. Gated HBase enhancements create coupling between one master flag and several feature-specific settings.

**Test signals:** Good coverage for config parsing and post-processing. It does not test every annotated `OzoneClientConfig` field or invalid duration/size formats beyond the checksum suffix case.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/TestOzoneClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/client/TestHddsClientUtils.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/client/TestHddsClientUtils.java

**Purpose:** Validates SCM endpoint resolution, Ozone resource/key name validation, secure exception messages, and throwable-chain lookup helpers in `HddsClientUtils` and related HDDS utility paths.

**Important APIs/types/functions:** `testMissingScmClientAddress()` expects `ConfigurationException` when no SCM client endpoint exists. `testGetScmClientAddress()` covers host-only and host:port parsing. `testGetScmClientAddressForHA()` configures an SCM service ID, node list, per-node client ports, and per-node addresses, then verifies the resolved collection. Fallback tests cover `OZONE_SCM_CLIENT_ADDRESS_KEY`, `OZONE_SCM_NAMES`, and block-client address derivation via `SCMNodeInfo.buildNodeInfo`. `testVerifyResourceName()` and length-specific helpers assert valid bucket/volume-like names and rejection of IP addresses, dot/dash adjacency, uppercase, leading/trailing dots, and unicode fullwidth characters. `testNameTooLongCapped()` and `testInvalidCharactersNotReported()` verify log-safe exception messages. `testVerifyKeyName()` enumerates invalid and valid key characters, including the filesystem copy temp suffix. `testContainsException()` validates cause-chain search.

**Control flow:** Endpoint tests exercise precedence and fallback branches. Name tests exercise validation branches for length, syntax, invalid characters, and sanitized reporting. Throwable tests traverse nested causes until a matching class is found or absent.

**State and persistence:** Uses fresh `OzoneConfiguration` instances. No persistent state, but the tested configuration keys are externally persisted in deployment configs.

**Dependencies and integration points:** Uses `HddsUtils`, `HddsClientUtils`, `SCMNodeInfo`, `ConfUtils`, Hadoop `NetUtils`, Ozone constants, AssertJ, and JUnit. It protects client bootstrap behavior and object namespace validation used by user-facing APIs.

**Risks:** Endpoint resolution is sensitive to HA key suffixing and default-port semantics; tests document that some fallback ports embedded in source keys are ignored. Exception message sanitation is security relevant because invalid user-provided names can reach logs.

**Test signals:** Strong regression signal for SCM address parsing and namespace validation. It does not test DNS resolution, multiple service IDs, or all possible Unicode/control-character cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/client/TestHddsClientUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStream.java

**Purpose:** Provides a test double for `BlockInputStream` that avoids real datanode RPCs while preserving block/chunk read behavior for storage stream tests.

**Important APIs/types/functions:** The constructor delegates to `BlockInputStream` with a `BlockLocationInfo` built from a `BlockID` and length, plus pipeline, token, client factory, refresh function, and `OzoneClientConfig`. It stores a list of protobuf `ChunkInfo` entries and a map from chunk name to byte data. `getBlockData()` returns protobuf `BlockData` containing the injected chunks. `createChunkInputStream()` returns a `DummyChunkInputStream` over a clone of the mapped byte array. `checkOpen()` is overridden as a no-op.

**Control flow:** During test reads, `BlockInputStream.initialize()` obtains block metadata from the overridden `getBlockData()` and creates chunk streams through the overridden factory. Each chunk read uses local memory rather than RPC.

**State and persistence:** Holds in-memory chunk metadata and byte arrays. It clones per-chunk byte data before creating the dummy chunk stream, reducing accidental mutation between tests. No persistence.

**Dependencies and integration points:** Integrates with `BlockInputStream`, `BlockLocationInfo`, `DummyChunkInputStream`, protobuf container messages, pipeline/token/client factory types, and `OzoneClientConfig`.

**Risks:** The no-op `checkOpen()` bypasses close/open validation, so tests using it do not cover lifecycle failure behavior. Passing a null chunk map in specialized tests can be safe only when `createChunkInputStream()` is overridden.

**Test signals:** Enables focused tests for seeking, chunk boundary reads, and retry behavior without requiring a datanode or SCM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStreamWithRetry.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStreamWithRetry.java

**Purpose:** Extends `DummyBlockInputStream` to simulate a first metadata-read failure and verify pipeline refresh/retry behavior in `BlockInputStream`.

**Important APIs/types/functions:** The constructor installs a refresh function that sets an `AtomicBoolean`, builds a mocked `BlockLocationInfo`, and returns a fresh single-node `MockPipeline`. It accepts an optional `IOException` to throw on the first `getBlockData()` call. `getBlockData()` increments `getChunkInfoCount`; on the first call it throws the injected exception or a `StorageContainerException` with `CONTAINER_NOT_FOUND`, then delegates to the parent on later calls.

**Control flow:** The first block-data fetch fails, causing the production read code to invoke its refresh logic. The retry call succeeds because subsequent `getBlockData()` calls return the in-memory chunk list.

**State and persistence:** Tracks a per-instance integer counter and injected exception. The external `AtomicBoolean` records refresh invocation for assertions. No persistence.

**Dependencies and integration points:** Depends on Mockito, `StorageContainerException`, `MockPipeline`, protobuf container types, and the parent dummy stream. Integrates with retry tests in `TestBlockInputStream`.

**Risks:** The counter is not thread-safe beyond test usage. Refresh-function behavior is synthetic and always returns a mock pipeline, so it cannot validate real SCM location semantics.

**Test signals:** Provides targeted signal that `CONTAINER_NOT_FOUND` and selected transport failures cause refresh and retry rather than immediate failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyBlockInputStreamWithRetry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyChunkInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyChunkInputStream.java

**Purpose:** Provides a memory-backed `ChunkInputStream` test double that returns deterministic byte ranges split on checksum boundaries.

**Important APIs/types/functions:** The constructor delegates to `ChunkInputStream` with chunk metadata, block id, client factory, pipeline supplier, checksum flag, and a null token supplier, then clones the supplied chunk data. `readChunk(ChunkInfo)` reads `offset` and `len` from the request, slices `chunkData` into `ByteString` segments of `bytesPerChecksum`, stores those segments in `readByteBuffers`, and returns read-only `ByteBuffer` views through `BufferUtils`. `acquireClient()` and `releaseClient()` are no-ops. `getReadByteBuffers()` exposes the last low-level read segments.

**Control flow:** Higher-level `ChunkInputStream.read()` computes aligned `ChunkInfo` read requests; this override materializes exactly those requested segments locally. The recorded byte strings let tests verify how much backing data was fetched for partial reads.

**State and persistence:** Holds immutable-by-clone chunk data and a mutable list of the latest read segments, cleared on every `readChunk()` call. No persistence.

**Dependencies and integration points:** Integrates with `ChunkInputStream`, `BufferUtils`, protobuf `ChunkInfo`, Ratis third-party `ByteString`, and storage tests for checksum-boundary and seek behavior.

**Risks:** Does not exercise RPC client acquisition/release or token behavior. It assumes offsets/lengths fit into Java `int`, which is acceptable for the small test chunks.

**Test signals:** Strong signal for chunk seek/read algorithms, checksum-aligned fetching, buffer caching, and unbuffer behavior when paired with `TestChunkInputStream`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/DummyChunkInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockInputStream.java

**Purpose:** Tests `BlockInputStream` seek/read behavior across chunk boundaries, byte-array and `ByteBuffer` reads, retry/refresh rules, and unbuffered client release behavior.

**Important APIs/types/functions:** `setup()` builds five chunks of size 100 except the last at 50 bytes, disables checksum verification, and creates a `DummyBlockInputStream`. `createChunkList()` constructs protobuf `ChunkInfo` entries and a concatenated `blockData` oracle. `testSeek()`, `testRead()`, `testReadWithByteBuffer()`, `testReadWithDirectByteBuffer()`, and `testSeekAndRead()` validate position, chunk index, EOF, and data correctness. `testRefreshPipelineFunction()` uses `DummyBlockInputStreamWithRetry` and log capture to verify retry after a first failure. Parameterized tests distinguish exceptions that trigger refresh (`StorageContainerException(CONTAINER_NOT_FOUND)` and gRPC `UNAVAILABLE` wrapped in `ExecutionException`) from exceptions that do not (`SCMSecurityException`, checksum exception, generic `IOException`). `testRefreshOnReadFailureAfterUnbuffer()` ensures unbuffer releases the old read client before retrying with a refreshed pipeline.

**Control flow:** Reads start uninitialized, so early seeks update block position until initialization maps the position to a chunk index. Reads span chunks and update stream position. Retry tests force failures either in block metadata retrieval or chunk reads, then assert refresh function invocation and subsequent success only for whitelisted failure types.

**State and persistence:** Uses in-memory byte arrays, chunk metadata, mocked refresh function, and client factory mocks. No persistence. Internal stream state under test includes block position, chunk index, initialized state, and client references after unbuffer.

**Dependencies and integration points:** Depends on `BlockInputStream`, dummy stream classes, `BlockExtendedInputStream` logs, `XceiverClientFactory`, `XceiverClientSpi`, `MockPipeline`, protobuf messages, Ozone checksum classes, gRPC status classes, Mockito, AssertJ, and JUnit.

**Risks:** The dummy stream bypasses some real client lifecycle behavior, though `testRefreshOnReadFailureAfterUnbuffer()` covers release/acquire with the real base class. Random seek positions add coverage but can make exact failures less reproducible if a future bug is position-dependent.

**Test signals:** High-value unit signal for block read correctness, retry classification, and resource release around unbuffer and pipeline refresh.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockOutputStreamCorrectness.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockOutputStreamCorrectness.java

**Purpose:** Verifies that `BlockOutputStream` writes exactly the bytes supplied by callers for different write granularities, and that EC reconstruction `executePutBlock` remains compatible with chunks lacking `stripeChecksum`.

**Important APIs/types/functions:** `test(int writeSize)` parameterizes writes of 1 byte, 1 KiB, and 1 MiB over a 256 MiB random data buffer, repeating ten blocks through a `RatisBlockOutputStream`. `createBlockOutputStream()` configures `BufferPool`, `OzoneClientConfig`, `StreamBufferArgs`, and a mocked `XceiverClientManager` returning `MockXceiverClientSpi`. `MockXceiverClientSpi.sendCommandAsync()` asserts every `WriteChunk` payload byte matches the static `DATA` sequence and returns successful `PutBlock` responses with committed length. `testMissingStripeChecksumDoesNotMakeExecutePutBlockFailDuringECReconstruction()` constructs an EC pipeline for parity index 5 and calls `ECBlockOutputStream.executePutBlock(true, true, length, blockData)` using `BlockData` chunks without stripe checksum.

**Control flow:** The correctness test writes through buffering, flush, commit, and close paths; mock responses make the stream believe each async command succeeded. The EC test drives the reconstruction put-block branch and asserts no exception.

**State and persistence:** Uses static 256 MiB random data and per-client counters/indices to compare write order. No persistent output. Metrics are acquired through `ContainerClientMetrics`.

**Dependencies and integration points:** Integrates with Ratis and EC block output stream code, `BufferPool`, stream buffer configuration, container protobuf requests/responses, `ContainerClientMetrics`, and Ozone client versioning.

**Risks:** The large static data array and repeated writes are memory/time intensive for a unit test. The mock client validates payload order but does not simulate partial failures, retries, or real Ratis commit timing. Metrics acquired in helpers are not explicitly released in the test body.

**Test signals:** Strong byte-for-byte write-path signal across buffering sizes and a targeted compatibility signal for EC stripe-checksum schema evolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBlockOutputStreamCorrectness.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBufferPool.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBufferPool.java

**Purpose:** Tests `BufferPool` allocation, reuse, release validation, capacity accounting, and blocking behavior under concurrent allocation pressure.

**Important APIs/types/functions:** `testBufferPool()` covers `BufferPool.empty()` and capacities/buffer sizes of `(1,1)`, `(3,1MiB)`, and `(10,1KiB)`. Helpers assert empty/full states, allocate up to capacity, fill buffers with random data to make identities distinguishable, release/reallocate the same instances, release in mixed order, and reject double releases. `testBufferPoolConcurrently()` fills a pool, verifies an allocator thread blocks and can be interrupted, then verifies a blocked allocator receives a released buffer once another thread releases it.

**Control flow:** Allocation loops grow the pool until capacity; when full, `allocateBuffer()` waits until release or interruption. Release transitions buffers from used to available, resets positions, and notifies waiters.

**State and persistence:** Tests in-memory pool state: capacity, buffer size, used count, total pool size, current buffer pointer, and buffer contents/positions. No persistence.

**Dependencies and integration points:** Depends on `ChunkBuffer`, `GenericTestUtils` log capture, SLF4J level control, AssertJ, and JUnit. It protects storage write buffering used by block output streams.

**Risks:** Thread coordination uses a spin/sleep loop on an `AtomicBoolean`, which is simple but time-sensitive on overloaded machines. Logging assertions couple tests to message text.

**Test signals:** Good unit signal for pool identity reuse, capacity invariants, and interruptible blocking. It does not test high-contention fairness or memory pressure beyond fixed capacities.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestChunkInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestChunkInputStream.java

**Purpose:** Tests `ChunkInputStream` data correctness, checksum-boundary-aligned reads, seek behavior, unbuffer behavior, and reconnection to a changed pipeline/token.

**Important APIs/types/functions:** `setup()` creates a 100-byte chunk with CRC32 checksums every 20 bytes and a `DummyChunkInputStream`. `testFullChunkRead()` and `testPartialChunkRead()` assert returned bytes and low-level fetched buffers. `testSeek()` validates EOF message, pre-read `chunkPosition`, cached-buffer seeks, outside-cache seeks, and boundary release behavior. `testSeekAndRead()` validates sequential reads after seeking. `testUnbuffered()` ensures `unbuffer()` releases buffers but preserves logical position. `connectsToNewPipeline()` uses mocked `XceiverClientFactory` and `XceiverClientSpi` with mutable pipeline/token suppliers, calls `unbuffer()`, swaps both suppliers, reads, and verifies the new pipeline and token are used.

**Control flow:** Reads consult cached aligned buffers when possible and issue aligned read requests otherwise. Seek either adjusts within cached data or records a new chunk position. Unbuffer clears buffers and forces the next read to reacquire a client.

**State and persistence:** Uses in-memory chunk bytes, checksum metadata, cached read buffers, current position, and mutable supplier references. No persistence.

**Dependencies and integration points:** Integrates with `ChunkInputStream`, `DummyChunkInputStream`, container command response builders, `ByteStringConversion`, `ChunkBuffer`, pipelines, tokens, Mockito, and JUnit.

**Risks:** Dummy read behavior avoids actual checksum failure and RPC error paths. `connectsToNewPipeline()` is sensitive to the precise order of unbuffer and supplier changes.

**Test signals:** Strong signal for chunk position/caching semantics and for pipeline/token refresh after unbuffering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestChunkInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestStreamBlockInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestStreamBlockInputStream.java

**Purpose:** Tests custom stream-read configuration, stream permit/request completion behavior, close failure handling, and race conditions in queue draining for `StreamBlockInputStream`.

**Important APIs/types/functions:** `testCustomStreamReadConfigIsApplied()` asserts pre-read size, response data size, and timeout fields are copied from `OzoneClientConfig`. `testReleasesStreamPermitAtBlockEof()` reads to EOF and verifies `XceiverClientGrpc.completeStreamRead()` and request observer `onCompleted()` happen once. `testCancelsRequestStreamWhenOnCompletedThrows()` and `testCloseDoesNotFailWhenOnCompletedAndCancelThrow()` verify close cleanup remains robust when observer completion/cancel throw. `testPollDoesNotDropQueuedItemWhenFutureCompletesFirst()` drives a race where `onNext` and `onCompleted` both happen before polling. `testReadDoesNotDropQueuedItemsWhenFutureIsDoneOnSecondCall()` drives multiple queued responses followed by completion and asserts all queued data is read. Helpers build standalone pipelines and mocked streaming clients/responses.

**Control flow:** The stream initializes a gRPC streaming read, queues `ReadBlock` responses through `StreamingReaderSpi`, consumes queued responses into caller buffers, and completes/cancels the request stream on EOF or close. The race tests specifically require queue draining before treating a completed future as EOF.

**State and persistence:** In-memory state includes block position, queued streaming responses, future completion state, request observer lifecycle, and stream permit state in the client. No persistence.

**Dependencies and integration points:** Depends on `XceiverClientGrpc`, `StreamingReadResponse`, `StreamingReaderSpi`, gRPC `ClientCallStreamObserver`, protobuf `ReadBlockResponseProto`, pipelines, `OzoneClientConfig`, and Mockito. Integrates with datanode streaming block read support.

**Risks:** The race tests encode current bug/regression expectations and are sensitive to internal queue/future ordering. Mocked streaming callbacks do not cover real network scheduling but reproduce the problematic synchronous ordering.

**Test signals:** High-value signal for streaming read resource cleanup and for preventing data loss/NPE when completion races with queued responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestStreamBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/package-info.java

**Purpose:** Provides package-level documentation for storage stream tests, identifying the package as containing Ozone `InputStream` related tests.

**Important APIs/types/functions:** No runtime APIs. The file contains only package Javadoc and the package declaration `org.apache.hadoop.hdds.scm.storage`.

**Control flow:** None.

**State and persistence:** None.

**Dependencies and integration points:** Used by Java tooling and Javadoc for the test package containing block, chunk, buffer pool, output stream, and streaming read tests.

**Risks:** Runtime risk is none. Documentation could become too narrow because the package also includes output stream and buffer pool tests, not only input streams.

**Test signals:** Build/style validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/ECStreamTestUtil.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/ECStreamTestUtil.java

**Purpose:** Centralizes EC stream test fixtures: synthetic `BlockLocationInfo`/pipeline creation, deterministic data filling and validation, parity generation, index maps, and in-memory block stream factories with fault injection.

**Important APIs/types/functions:** `createKeyInfo()` builds closed pipelines with replica-index maps and block metadata. `zeroFill()` pads a buffer to its limit. `randomFill(ByteBuffer[], stripeSize, rand, length)` stripes random bytes across data buffers and finalizes limits; the single-buffer overload fills all remaining space. `assertBufferMatches()` validates buffer contents against a `SplittableRandom`. `generateParity()` normalizes data buffer positions/limits, zero-fills partial data buffers, invokes `CodecUtil.createRawEncoderWithFallback()`, and returns parity buffers. `createIndexMap()` creates random datanodes mapped to given EC indexes. `TestBlockInputStreamFactory` creates `TestBlockInputStream` instances by EC replica index and can fail selected indexes once. `TestBlockInputStream` reads from an injected `ByteBuffer`, supports seek, error on read, error on seek, and tracks EC replica index.

**Control flow:** Utilities are deterministic when callers reuse the same random seed. The factory maps requested single-node pipelines back to the current EC pipeline replica index, selects the corresponding data/parity buffer, optionally injects a first-read failure, and records created streams.

**State and persistence:** Holds in-memory maps/lists of streams, buffers, current pipeline, and fail-once indexes. `TestBlockInputStream` mutates buffer position as stream position. No persistence.

**Dependencies and integration points:** Depends on EC replication config, datanode/pipeline types, `BlockExtendedInputStream`, `BlockInputStreamFactory`, Ozone erasure-code raw encoders, and test random data. Used heavily by EC direct, proxy, reconstructed stream, and stripe tests.

**Risks:** Buffer position/limit manipulation is subtle; incorrect reset can invalidate later assertions. The test stream returns data from shared buffers, so callers must isolate or reset state between tests. Fault injection is simple and not thread-safe.

**Test signals:** Provides the foundation for validating EC reconstruction parity, read ordering, failover, and position semantics without a live cluster.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/ECStreamTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBlockInputStreamFactoryImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBlockInputStreamFactoryImpl.java

**Purpose:** Verifies `BlockInputStreamFactoryImpl` selects the correct concrete block input stream type for Ratis/non-EC, streaming-read-enabled, and EC replication configs.

**Important APIs/types/functions:** `testNonECGivesBlockInputStream(boolean)` parameterizes `streamReadBlockEnabled`; for Ratis THREE it expects `StreamBlockInputStream` when enabled and `BlockInputStream` otherwise, while preserving block ID and length. `testECGivesECBlockInputStream()` expects `ECBlockInputStreamProxy` for `ECReplicationConfig(3,2)`. Local `createKeyLocationInfo()` helpers build closed pipelines with random datanodes and replica indexes.

**Control flow:** The factory branches on replication config type first, then on non-EC stream-read configuration. Tests instantiate the selected stream but do not perform reads.

**State and persistence:** Uses transient `OzoneConfiguration` and synthetic `BlockLocationInfo`. No persistence.

**Dependencies and integration points:** Integrates with `BlockInputStreamFactoryImpl`, `BlockInputStream`, `StreamBlockInputStream`, `ECBlockInputStreamProxy`, HDDS replication configs, pipelines, and `OzoneClientConfig`.

**Risks:** The test spies pipeline replica index for non-EC path but does not validate client factory/token/refresh propagation. It verifies type selection, not operational behavior.

**Test signals:** Clear regression signal for factory dispatch when stream read support or EC support changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBlockInputStreamFactoryImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBoundedElasticByteBufferPool.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBoundedElasticByteBufferPool.java

**Purpose:** Tests `BoundedElasticByteBufferPool` FIFO reuse and maximum cached byte-size enforcement.

**Important APIs/types/functions:** `testLogicalTimestampOrdering()` puts three same-size buffers, records identity hash codes, retrieves three buffers of the same size, and asserts FIFO identity order plus zero pool size afterward. `testPoolBoundingLogic()` creates a 3 MiB pool, stores 2 MiB and 1 MiB buffers to exactly fill it, verifies a subsequent 3 MiB buffer is rejected, retrieves the first two by identity, and confirms a later 3 MiB request allocates a new instance rather than returning the rejected buffer.

**Control flow:** `putBuffer()` accepts a buffer only if `currentPoolSize + capacity <= maxPoolSize`; `getBuffer()` removes a matching cached buffer or allocates a new one. Ordering is driven by logical timestamps/FIFO behavior.

**State and persistence:** Tests in-memory cached buffer state and the exposed `currentPoolSize`. No persistence.

**Dependencies and integration points:** Depends on Java `ByteBuffer` and JUnit. Integrates with EC reconstructed stream buffer pooling where unbounded elastic pooling would otherwise retain excessive memory.

**Risks:** Identity hash code comparison is a proxy for object identity; `assertSame` would be more direct. Tests cover heap buffers only and do not cover direct buffers or mixed size ordering beyond the chosen cases.

**Test signals:** Good signal for memory bounding and stable FIFO reuse behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBoundedElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStream.java

**Purpose:** Tests direct EC block reads when enough data locations are available, including location sufficiency, per-replica block length calculation, reads across EC chunk boundaries, seeking, failure reporting, spare location fallback, pipeline refresh adaptation, and zero-byte-read handling.

**Important APIs/types/functions:** `setup()` uses EC 3-2 RS with 1 MiB cells. `testSufficientLocations()` checks when available data indexes are enough for small, full, and large blocks; parity-only reconstruction is not considered sufficient for direct reads. The block-size tests verify each per-index stream length for blocks shorter than one cell, spanning two/three cells, full stripes, and partial stripes. `testSimpleRead()`, `testSimpleReadUnderOneChunk()`, `testReadPastEOF()`, and `testReadCrossingMultipleECChunkBounds()` validate data ordering and EOF. Seek tests check EOF bounds, zero-length blocks, valid position mapping, and remaining bytes. Failure tests assert `BadDataLocationException` identifies failed datanodes and that spare same-index locations are tried before failing. `testEcPipelineRefreshFunction()` converts a refreshed EC pipeline to a single-node standalone pipeline for a specific replica index. `testZeroByteReadThrowsBadDataLocationException()` ensures a zero-byte short read throws rather than spinning.

**Control flow:** The stream maps logical block offsets to EC data indexes and per-index block streams. Reads pull data in EC cell order and update position. On direct-stream failures, it reports failed locations; if a spare location for the same replica index exists, it retries through another stream. Zero-byte reads are treated as inconsistent failure.

**State and persistence:** Uses synthetic pipelines, in-memory test streams, position counters, failure flags, and Ozone client config. No persistence.

**Dependencies and integration points:** Depends on `ECBlockInputStream`, `BadDataLocationException`, `ECStreamTestUtil`-like local test doubles, HDDS pipeline and datanode types, replication config, and JUnit.

**Risks:** Local `TestBlockInputStream` uses byte values based on stream creation order rather than actual EC data, so it validates ordering/position more than real content. Comments in the zero-byte test mention implementation requirements and signal a regression target.

**Test signals:** High-value signal for EC direct-read boundary math, error classification, and failover prerequisites used by `ECBlockInputStreamProxy`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStreamProxy.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStreamProxy.java

**Purpose:** Tests `ECBlockInputStreamProxy` dispatch between direct EC reads and reconstructed reads, position/remaining metadata, EOF behavior, failover after bad data locations, and seek behavior across stream replacement.

**Important APIs/types/functions:** `testExpectedDataLocations()` validates expected data indexes as a function of block length for EC 3-2 and 6-3. `testAvailableDataLocations()` counts available data indexes from pipeline replica indexes. Metadata tests assert block ID, length, position, and remaining. `testCorrectStreamCreatedDependingOnDataLocations()` checks whether the factory is invoked with `missingLocations=false` for direct reads or `true` for reconstruction. `testCanReadNonReconstructionToEOF()` and `testCanReadReconstructionToEOF()` read deterministic random data to EOF in both modes. `testCanHandleErrorAndFailOverToReconstruction()` injects a mid-read `BadDataLocationException`, verifies the caller buffer is effectively rewound by matching the same data sequence, and asserts failed datanodes are passed to the reconstruction factory. `testCanSeekToNewPosition()` verifies seeks on the active stream, fallback when direct seek fails, and failure when reconstructed seek also fails.

**Control flow:** On construction or first use, the proxy chooses direct or reconstruction based on location availability. During reads, a `BadDataLocationException` from the direct stream causes creation of a reconstruction stream with failed datanodes and continuation from the prior logical position. Seek delegates to the current stream and can trigger mode change on failure.

**State and persistence:** Tracks active stream mode, logical position, failed locations, and deterministic in-memory data. No persistence.

**Dependencies and integration points:** Uses `ECBlockInputStreamProxy`, `ECBlockInputStreamFactory`, `BlockExtendedInputStream`, `ECStreamTestUtil.TestBlockInputStream`, pipelines, replication config, and JUnit/AssertJ.

**Risks:** The test factory keys streams by boolean `missingLocations`, so repeated creations in the same mode overwrite the map entry. It verifies proxy-level behavior without real parity reconstruction.

**Test signals:** Strong signal for the proxy’s key responsibility: seamless direct-to-reconstruction failover while preserving user-visible stream semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockInputStreamProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedInputStream.java

**Purpose:** Tests the higher-level reconstructed EC block stream that wraps stripe-level reconstruction, ensuring normal stream APIs work across multiple stripes, partial final stripes, unbuffering, byte-at-a-time reads, byte-array reads, EOF, and seek.

**Important APIs/types/functions:** `createStripeInputStream()` builds an `ECBlockReconstructedStripeInputStream` with synthetic block info, current pipeline, elastic buffer pool, executor, and checksum-enabled config. Metadata tests validate `getLength()` and `getBlockID()`. `testReadDataByteBufferMultipleStripes()` reads a block containing three full stripes plus a partial chunk, checks deterministic data, EOF, then seeks to zero and reads again after buffers were freed. `testReadDataWithUnbuffer()` calls `unbuffer()` after each read. `testReadDataByteBufferUnderBufferSize()` validates small-block reads. `testReadByteAtATime()` and `testReadByteBuffer()` cover single-byte and byte-array APIs. `testSeek()` performs repeated random seeks and validates content from each new position, then asserts seeking past EOF fails.

**Control flow:** The wrapper asks the stripe stream for reconstructed stripe buffers, copies data into caller buffers according to current position, releases/reacquires buffers on EOF or unbuffer, and delegates seek to stripe-aligned reconstruction as needed.

**State and persistence:** Uses deterministic random seed state, in-memory data/parity buffers, an elastic byte buffer pool, and a fixed thread pool executor shut down after each test. No persistence.

**Dependencies and integration points:** Depends on `ECBlockReconstructedInputStream`, `ECBlockReconstructedStripeInputStream`, `ECStreamTestUtil.generateParity`, Hadoop `ByteBufferPool`, executor services, and EC replication config.

**Risks:** Executor cleanup is explicit; missing shutdown would leak threads. Random seek iterations improve coverage but can produce variable failing positions. Elastic pool behavior is not bounded in this test class.

**Test signals:** Strong end-to-end unit signal for reconstructed EC stream compatibility with standard `InputStream` and `ByteBufferReadable` style APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedStripeInputStream.java -->
## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedStripeInputStream.java

**Purpose:** Tests stripe-level EC reconstruction across full and partial stripes, missing data/parity combinations, recovery-index output selection, spare locations, failed-location exclusion, seek alignment, insufficient-location failures, and byte buffer pool edge cases.

**Important APIs/types/functions:** `recoveryCases()` enumerates no-recovery, one missing index, two data missing, data+parity missing, and parity-only recovery sets. `polluteByteBufferPool()` preloads larger buffers to guard against HDDS-7304-style assumptions about exact buffer capacity. `testSufficientLocations()` validates quorum logic with padding indexes, failed datanodes, and recovery index counts. `testReadFullStripesWithPartial()` parameterizes recovery cases over three full stripes plus a partial stripe and validates output buffer contents/positions. Partial-stripe tests cover one-, two-, and three-chunk final stripes, parity recovery, and multiple location maps. `testErrorThrownIfBlockNotLongEnough()`, `testErrorReadingBlockContinuesReading()`, and `testAllLocationsFailOnFirstRead()` assert `InsufficientLocationsException` in unrecoverable cases. `testNoErrorIfSpareLocationToRead()` verifies spare same-index replicas are used. `testSeek()` validates stripe-aligned seeking and remaining counts. `testSeekToPartialOffsetFails()` asserts non-stripe-aligned seek rejection. `testFailedLocationsAreNotRead()` ensures pre-marked failed datanodes are excluded from stream creation.

**Control flow:** The stripe stream chooses readable indexes, fills missing data/parity buffers, performs raw erasure decoding when recovery indexes are set or data indexes are missing, advances underlying streams one EC chunk per stripe, and updates logical block position. It refuses recovery when fewer than data-count usable locations remain or when requested seek positions are not stripe aligned.

**State and persistence:** Uses in-memory data/parity buffers, mutable recovery indexes, failed datanode sets, current position, buffer pool contents, and executor threads. No persistence.

**Dependencies and integration points:** Depends on `ECBlockReconstructedStripeInputStream`, `ECBlockInputStream` sufficiency semantics, `ECStreamTestUtil`, Ozone erasure coding, Hadoop `ByteBufferPool`, executor service, datanode/pipeline metadata, AssertJ, and JUnit.

**Risks:** This is a complex test matrix; failures can be caused by buffer position/limit mistakes as much as reconstruction logic. `polluteByteBufferPool()` highlights a real integration risk where pooled buffers may be larger than requested. Seek only supports stripe offsets, which is a documented limitation tested here.

**Test signals:** Very high signal for EC reconstruction correctness and failure handling, especially for partial stripes and degraded-location scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockReconstructedStripeInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/dev-support/findbugsExcludeFile.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/common/dev-support/findbugsExcludeFile.xml

**Purpose:** Defines SpotBugs/FindBugs exclusions for the `hdds-common` module.

**Important APIs/types/functions:** The XML root is `FindBugsFilter`. It excludes all bug reports for packages `org.apache.hadoop.hdds.protocol.proto`, `org.apache.hadoop.ipc_`, and `org.apache.hadoop.security_`. It also suppresses `DMI_HARDCODED_ABSOLUTE_FILENAME` specifically for class `org.apache.hadoop.ozone.OzoneConsts`.

**Control flow:** Build-time only. The SpotBugs Maven plugin reads this filter and suppresses matching findings from the analysis report.

**State and persistence:** Static build configuration persisted in source control. No runtime state.

**Dependencies and integration points:** Referenced by `hdds-common/pom.xml` through the `spotbugs-maven-plugin` `excludeFilterFile` configuration.

**Risks:** Package-level blanket exclusions can hide new static-analysis issues in generated or shaded namespaces. The `OzoneConsts` hardcoded-path suppression is narrow, but should be revisited if constants move or if real path bugs appear in that class.

**Test signals:** Build/static-analysis signal only; no JUnit coverage. Effectiveness is visible when the SpotBugs plugin runs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/pom.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/common/pom.xml

**Purpose:** Maven module descriptor for `hdds-common`, declaring its artifact identity, dependencies, resource filtering, generated version info, static-analysis filter, config annotation processing, import restrictions, and OS build extension.

**Important APIs/types/functions:** The module inherits from `hdds-hadoop-dependency-client` version `2.3.0-SNAPSHOT`, publishes `org.apache.ozone:hdds-common`, and packages a jar. Dependencies include Jackson, Guava, protobuf, re2j, commons libraries, OpenTelemetry, Hadoop common, HDDS config/interface client modules, Ratis clients/transports/metrics, Bouncy Castle, SLF4J, and test utilities. Build resources filter only `hdds-version-info.properties`. `hadoop-maven-plugins:version-info` runs in `generate-resources` over sibling Java/proto sources. SpotBugs uses `dev-support/findbugsExcludeFile.xml`. `maven-compiler-plugin` configures `hdds-config` as an annotation processor and invokes `ConfigFileGenerator` with `-AartifactId=${project.artifactId}`. The enforcer override bans `org.kohsuke.MetaInfServices` imports while allowing selected processors. `os-maven-plugin` is a build extension.

**Control flow:** Maven evaluates parent dependency management, resolves dependencies, generates version metadata before resources are packaged, runs annotation processing during compilation, and applies SpotBugs/enforcer rules during configured lifecycle phases.

**State and persistence:** Persistent build metadata. Generated version/config resources are build outputs, not checked-in runtime state.

**Dependencies and integration points:** Central integration point between HDDS common Java code, generated config docs/resources, SpotBugs, Hadoop/Ratis/protobuf/OpenTelemetry dependencies, and downstream modules consuming `hdds-common`.

**Risks:** Dependency breadth makes convergence and transitive conflicts important. Annotation processor configuration is required for config generation; breaking it can silently affect generated config artifacts. Resource filtering is intentionally narrow to avoid accidental token substitution.

**Test signals:** Maven build, compiler annotation processing, enforcer, and SpotBugs runs validate this file. Unit tests in dependent modules indirectly validate dependency availability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/core-site.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/core-site.xml

**Purpose:** Provides an empty Hadoop-style `core-site.xml` template for site-specific configuration overrides in the Ozone/HDDS distribution.

**Important APIs/types/functions:** The XML declares the Hadoop configuration stylesheet and an empty `<configuration>` root. It contains no `<property>` entries.

**Control flow:** Runtime/configuration loading only. Hadoop/Ozone configuration loaders can include this file and merge any site-specific properties if operators add them.

**State and persistence:** Persistent configuration template. As checked in, it contributes no runtime key/value state.

**Dependencies and integration points:** Used by Hadoop `Configuration`/Ozone configuration loading conventions and distribution packaging. Pairs with other conf files under `common/src/main/conf`.

**Risks:** Because it is empty, deployments must supply meaningful overrides elsewhere. Editing this template directly can affect packaged defaults globally.

**Test signals:** XML well-formedness and packaging are the primary signals; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/hadoop-policy.xml -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/hadoop-policy.xml

**Purpose:** Provides the default Hadoop service authorization policy file shipped with Ozone/HDDS, listing ACL properties for many Hadoop IPC protocols.

**Important APIs/types/functions:** The file is an XML `<configuration>` with properties such as `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.admin.operations.protocol.acl`, refresh protocols, HA/ZKFC/QJournal protocols, MapReduce history/job protocols, and YARN resource/application/container/localizer protocols. Every listed property defaults to `*`, meaning all users are allowed, with descriptions explaining ACL syntax.

**Control flow:** When Hadoop service-level authorization is enabled and `hadoop.policy.file` points to this file, protocol servers consult these ACL values to decide whether callers may invoke each service.

**State and persistence:** Persistent XML configuration defaults. The values are deployment state when packaged or copied into a configuration directory.

**Dependencies and integration points:** Integrated by Hadoop IPC authorization policy loading and referenced by `OZONE_POLICYFILE` defaults in environment configuration. It affects Ozone components that expose or depend on Hadoop protocols.

**Risks:** The permissive `*` defaults are convenient but insecure for hardened deployments unless overridden. Drift from upstream Hadoop protocol names can leave some protocols unintentionally unrestricted or unconfigured.

**Test signals:** XML parsing and runtime authorization integration are tested elsewhere; this file itself has no direct unit tests in the subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/ozone-env.sh -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/ozone-env.sh

**Purpose:** Shell environment template for Ozone commands and daemons, documenting and defaulting runtime environment variables for Java, classpath, logs, SSH fanout, daemon options, privileged execution, direct memory caps, and command-specific JVM options.

**Important APIs/types/functions:** The only active logic enables core dumps only when the hard core limit is non-zero, suppressing errors, and exports `OZONE_OS_TYPE` from `uname -s` if unset. The rest is commented configuration guidance for `JAVA_HOME`, `OZONE_HOME`, `OZONE_CONF_DIR`, heap sizes, `OZONE_OPTS`, client/server/daemon command opts, classpath handling, SSH options, worker host lists, log/pid directories, security logger, policy file, JSVC settings, Netty/Ratis Netty direct memory caps, component-specific options, build paths, and user locks.

**Control flow:** Sourced by Ozone shell launch scripts. Active commands run during shell initialization before command dispatch; commented exports become active only when operators edit or override them.

**State and persistence:** Persistent shell configuration template. Runtime state is environment variables inherited by Ozone processes.

**Dependencies and integration points:** Integrates with Ozone shell functions and daemon launch scripts, Java runtime, Hadoop logging properties, SSH/pdsh orchestration, JSVC, Netty, Ratis shaded Netty, and service policy files.

**Risks:** Shell syntax must remain portable enough for supported launch environments. Incorrect edits can affect every Ozone command. The core dump logic deliberately avoids noisy failures in containers. Direct-memory cap values require raw bytes because Netty parsers do not accept suffixes.

**Test signals:** Usually validated by packaging and shell command smoke tests rather than JUnit. Manual `ozone version`/daemon starts are important for changes here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/ozone-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/com/google/protobuf/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/com/google/protobuf/package-info.java

**Purpose:** Declares package documentation for `com.google.protobuf` within the module, indicating the package contains classes using protobuf internal APIs.

**Important APIs/types/functions:** No types or methods are declared. The file contains package Javadoc and the `package com.google.protobuf;` declaration.

**Control flow:** None at runtime. It affects package metadata and documentation.

**State and persistence:** No state or persistence.

**Dependencies and integration points:** The unusual package name signals that this module may contain helper classes placed in protobuf’s package to access package-private/internal protobuf APIs. It integrates with Java compiler package handling and documentation.

**Risks:** Defining classes under a third-party package can be fragile across dependency upgrades and may conflict with module boundaries or shaded packaging. This package-info itself is harmless, but it documents a sensitive integration area.

**Test signals:** Build/package compilation is the main signal. Compatibility with protobuf internals is tested by the actual classes in this package, not by this package-info file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/com/google/protobuf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ComponentVersion.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ComponentVersion.java

**Purpose:** Defines a common interface for HDDS component version enums, tying human-readable descriptions and protobuf wire values to the generic Ozone `Versioned` contract.

**Important APIs/types/functions:** `description()` returns a textual description for an enum value. `toProtoValue()` returns the integer value used in protocol messages. The default `version()` implementation delegates to `toProtoValue()`, satisfying `Versioned`.

**Control flow:** No branching beyond default method dispatch. Implementing enums supply concrete values.

**State and persistence:** Interface has no state. Implementing enum constants represent persisted/wire compatibility states because `toProtoValue()` is serialized in protocols.

**Dependencies and integration points:** Depends on `org.apache.hadoop.ozone.Versioned`. Implemented by `DatanodeVersion` in this subset and likely other component version enums. Used anywhere feature gates compare component versions.

**Risks:** Wire values must remain stable; changing `toProtoValue()` behavior in implementers can break compatibility. The interface assumes integer versions are sufficient for ordering and serialization.

**Test signals:** Indirectly covered by component version enum tests and protocol compatibility tests. No direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ComponentVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/DatanodeVersion.java -->
## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/DatanodeVersion.java

**Purpose:** Enumerates datanode protocol/feature versions and exposes the current datanode version for compatibility checks.

**Important APIs/types/functions:** Enum constants are `DEFAULT_VERSION(0)`, `SEPARATE_RATIS_PORTS_AVAILABLE(1)`, `COMBINED_PUTBLOCK_WRITECHUNK_RPC(2)`, `STREAM_BLOCK_SUPPORT(3)`, and `FUTURE_VERSION(-1)`. `CURRENT` is computed by `latest()` and `CURRENT_VERSION` exposes its integer. `BY_PROTO_VALUE` maps serialized integers to enum constants. `description()` and `toProtoValue()` implement `ComponentVersion`. `fromProtoValue(int)` returns the matching enum or `FUTURE_VERSION` for unknown newer values. `latest()` returns the second-to-last enum constant, intentionally excluding `FUTURE_VERSION`.

**Control flow:** Static initialization builds the lookup map and selects current version. Runtime conversion branches through `Map.getOrDefault`. Adding new versions before `FUTURE_VERSION` automatically advances `CURRENT`.

**State and persistence:** Enum constants and static lookup map are immutable runtime state. Integer proto values are persistent wire/state compatibility markers and must not be reused.

**Dependencies and integration points:** Implements `ComponentVersion` and therefore `Versioned`. Integrated by datanode/client compatibility logic, including stream block support gates tied to `STREAM_BLOCK_SUPPORT`.

**Risks:** New real versions must be inserted before `FUTURE_VERSION`; appending after it would break `latest()`. Duplicate proto values would fail during static map collection or create compatibility ambiguity. Unknown values intentionally collapse to `FUTURE_VERSION`, so callers must handle newer servers conservatively.

**Test signals:** No direct test in this subset. Stream-read tests indirectly depend on the feature represented by `STREAM_BLOCK_SUPPORT`, but not on this enum mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/DatanodeVersion.java -->
