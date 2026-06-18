# subset-b-008006 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandler.java

## Purpose
`TestKeyValueHandler` is a broad unit/integration test suite for `KeyValueHandler`, the datanode-side handler for key-value container commands. It validates command dispatch, volume layout selection, container lifecycle transitions, deletion cleanup, checksum reconciliation, closed-container recovery writes, ICR emission, and read-block metrics.

## Important APIs, types, and functions
The suite exercises `KeyValueHandler.dispatchRequest`, `handleCreateContainer`, `handleCloseContainer`, `deleteContainer`, `markContainerForClose`, `closeContainer`, `reconcileContainer`, `updateContainerChecksum`, `handleGetContainerChecksumInfo`, `readBlock`, `writeChunkForClosedContainer`, and `putBlockForClosedContainer`. It builds `ContainerCommandRequestProto` messages for `CreateContainer`, `ReadContainer`, `UpdateContainer`, `DeleteContainer`, `CloseContainer`, `PutBlock`, `GetBlock`, `ReadChunk`, `WriteChunk`, `PutSmallFile`, `GetSmallFile`, `FinalizeBlock`, and checksum/read-block commands. Test support types include `ContainerSet`, `MutableVolumeSet`, `HddsVolume`, `KeyValueContainerData`, `KeyValueContainer`, `ContainerChecksumTreeManager`, `ContainerMerkleTreeWriter`, `OnDemandContainerScanner`, and `ContainerMetrics`.

## Control flow
Setup creates a mocked `HddsDispatcher` wired to a mocked `KeyValueHandler`, a mocked `ContainerSet`, and a temporary datanode/metadata directory. Dispatch tests send each command type through `KeyValueHandler.dispatchRequest` and verify the correct handler method or unsupported-operation path. Lifecycle tests create real temporary volumes and containers, then mutate states such as `INVALID`, `RECOVERING`, `OPEN`, `CLOSING`, and `CLOSED` before invoking close/delete paths. Failure tests inject `StorageContainerException`, impossible deleted-container directories, failed volumes, mocked clocks for delete timeouts, and an override that forces unreferenced file deletion to fail.

## State and persistence behavior
The tests assert that create failures release committed bytes, delete removes containers from `ContainerSet`, failed delete moves trigger `checkVolumeAsync`, failed-volume deletes log without normal cleanup, and delete decrements cached volume used space by `containerData.getBytesUsed()`. Checksum tests persist and read container Merkle-tree files, update container data checksums, and verify checksum values are reflected in ICR reports. Closed-container paths persist block data and bytes-used metadata while preserving or updating BCSID according to overwrite flags.

## Dependencies and integration points
The file integrates Ozone container metadata, volume selection, metrics, token-free dispatcher flow, checksum tree management, datanode state context, incremental container reports, and the on-demand scanner registered on `ContainerSet`. It also relies on `ContainerLayoutTestInfo.ContainerTest` to run selected cases across `FILE_PER_BLOCK` and `FILE_PER_CHUNK` layouts.

## Risks and edge cases
Covered risks include dispatching create requests to the wrong datanode or replica, leaking committed space on failed container creation, deleting containers on failed volumes, volume-scan triggering on deletion failures, invalid close transitions, recovering-container scan triggers, stale or missing checksum state, invalid states for checksum info, timeout-sensitive deletes, and bytes-used errors during closed-container recovery writes.

## Test signals
Assertions combine Mockito invocation counts, `ContainerProtos.Result` checks, filesystem existence checks, RocksDB metadata reads, metric counter assertions for `bytesReadBlock`, and checksum-tree comparison helpers. A failure here usually signals a regression in datanode command routing, container lifecycle persistence, checksum reporting, or volume accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandlerWithUnhealthyContainer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandlerWithUnhealthyContainer.java

## Purpose
This suite verifies `KeyValueHandler` behavior when containers are unhealthy or when requests target a mismatched EC replica index. It establishes which operations remain readable, which fail with container-state errors, and how marking a container unhealthy behaves on failed versus healthy volumes.

## Important APIs, types, and functions
The tests call `handleReadContainer`, `handleGetBlock`, `handleGetCommittedBlockLength`, `handleReadChunk`, `handleFinalizeBlock`, `handleGetSmallFile`, generic `handle` with a `PutBlock` request, and `markContainerUnhealthy`. Helpers construct dummy handlers with mocked `ContainerSet`, `MutableVolumeSet`, `ContainerMetrics`, `IncrementalReportSender`, `DatanodeStateMachine`, and `ContainerChecksumTreeManager`. Container data is mocked to expose states, BCSID, replica indexes, and container protobuf metadata.

## Control flow
Each operation is invoked directly against a `KeyValueContainer` backed by mocked `KeyValueContainerData`. Unhealthy containers allow `ReadContainer` to return `SUCCESS`, while block/chunk/small-file reads generally fall through to `UNKNOWN_BCSID` due to missing block metadata. `FinalizeBlock` is expected to return `CONTAINER_UNHEALTHY`. Parameterized tests iterate every `ClientVersion` and replica IDs 0 through 5 to verify requests with nonzero replica IDs fail with `CONTAINER_NOT_FOUND` when they mismatch the container replica index.

## State and persistence behavior
The unhealthy mark test builds a real `KeyValueContainerData` with metadata path, DB file, and `HddsVolume`. When the volume state is `FAILED`, `markContainerUnhealthy` must not create the checksum file and must not send an ICR. When the same volume is switched to `NORMAL`, the checksum sidecar file is expected to exist and the ICR sender is invoked at most once.

## Dependencies and integration points
The suite sits at the boundary between request handling, EC replica-index routing, checksum tree sidecar creation, storage-volume state, and incremental container reports. It also uses `ContainerTestHelper` request builders and `MockPipeline` to create a malformed `PutBlock` path that previously risked an NPE.

## Risks and edge cases
Key risks are accidentally rejecting safe read-container requests, returning the wrong error code for unhealthy states, treating replica ID 0 as a strict mismatch, creating checksum files on failed volumes, sending ICRs for containers that cannot be safely persisted, and internal errors from incomplete container mocks.

## Test signals
The strongest signals are exact `ContainerProtos.Result` assertions, file existence checks for `ContainerChecksumTreeManager.getContainerChecksumFile`, and Mockito `never`/`atMostOnce` checks for ICR sends.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestKeyValueHandlerWithUnhealthyContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestTarContainerPacker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestTarContainerPacker.java

## Purpose
`TestTarContainerPacker` validates tar-based container replication packaging and unpacking for key-value containers across all test schema/layout combinations and every `CopyContainerCompression` mode. It checks descriptor-first archive layout, metadata DB/chunk extraction, checksum sidecar preservation, stream closure, and path traversal defenses.

## Important APIs, types, and functions
The tests exercise `TarContainerPacker.pack`, `decompress`, `unpackContainerDescriptor`, `unpackContainerData`, `compress`, `getDbPath`, and constants such as `CONTAINER_FILE_NAME`, `DB_DIR_NAME`, and `CHUNKS_DIR_NAME`. It builds `KeyValueContainerData` and `KeyValueContainer` objects, writes synthetic DB/chunk files, writes the container descriptor YAML, and uses `ContainerChecksumTreeManager` plus `ContainerMerkleTreeWriter`.

## Control flow
`getLayoutAndCompression` generates a Cartesian product of `ContainerTestVersionInfo.getLayoutList()` and `CopyContainerCompression.values()`. The main `pack` test creates a source container tree with metadata DB, chunk file, descriptor, and checksum file; packs it; inspects the tar stream to ensure the descriptor is first; reads only the descriptor; then unpacks data into a destination container path. Additional tests create single-file tar archives with nested relative DB or chunk paths and with traversal-style `../` paths.

## State and persistence behavior
Unpacking must materialize DB and chunk files under the destination container root, preserve source container ID in destination metadata, persist the checksum file, and rewrite the destination container descriptor so its state contains `RECOVERING`. Checksum state is verified by comparing the source and destination Merkle trees. Spy streams assert pack/unpack closes input/output exactly once.

## Dependencies and integration points
The suite integrates Apache Commons Compress tar streams, Ozone replication compression, archive inclusion via `Archiver.includeFile`, checksum tree serialization, and container descriptor files used by datanode startup. It also depends on schema-version injection through `ContainerTestVersionInfo.setTestSchemaVersion`.

## Risks and edge cases
Important risks are malformed archive ordering, resource leaks, losing checksum sidecar state during replication, extracting files outside the destination root via relative paths, and accepting nested valid paths incorrectly. The tests explicitly distinguish `sub/dir/file` as valid from `../file` as invalid.

## Test signals
Signals include tar entry inspection, descriptor byte-for-byte comparison, stream-close assertions, existence/content checks for unpacked files, destination state checks, and Merkle-tree equality through `assertTreesSortedAndMatch`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestTarContainerPacker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/helpers/TestChunkUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/helpers/TestChunkUtils.java

## Purpose
This file tests low-level `ChunkUtils` file IO behavior: concurrent reads, concurrent writes and reads guarded by striped locks, serial reads, overwrite validation, missing-file error mapping, and the read path for small, boundary, large, empty, and randomized files.

## Important APIs, types, and functions
The suite calls `ChunkUtils.writeData`, `ChunkUtils.readData`, `ChunkUtils.setStripedLock`, and `ChunkUtils.validateChunkForOverwrite`. It uses `ChunkBuffer`, `ChunkInfo`, `StorageContainerException`, `MappedBufferManager`, Guava `Striped.readWriteLock`, Java `FileChannel`, thread pools, `CompletableFuture`, and `GenericTestUtils.waitFor`.

## Control flow
`readData` is a helper that invokes `ChunkUtils.readData` with a 1 MiB buffer capacity, a 32 KiB mapped-buffer threshold, checksum disabled, and a shared `MappedBufferManager`. Concurrency tests write known bytes to a file, then fan out ten reader tasks or ten asynchronous writer/readback pairs. `testReadData` repeatedly writes deterministic random byte streams and then reads them back through one or more buffers, reseeding the RNG to verify byte equality without storing the whole file.

## State and persistence behavior
The tests create temporary files under JUnit `@TempDir`, persist byte ranges at explicit offsets, and assert that returned `ChunkBuffer` views expose the expected number of `ByteBuffer` segments and remaining byte counts. `validateChunkForOverwrite` uses both `File` and `FileChannel` overloads to decide whether a write at offset 3 over a four-byte file is an overwrite extension candidate and offset 5 is not.

## Dependencies and integration points
This suite is below the container abstraction and feeds chunk-manager tests. It validates assumptions used by file-per-block and file-per-chunk strategies, especially buffer segmentation, mapped-buffer threshold behavior, locking, and conversion of missing files to `UNABLE_TO_FIND_CHUNK`.

## Risks and edge cases
Risks include race conditions between readers and writers, returning buffers with wrong positions, failing to handle empty files, off-by-one segment counts at `MAPPED_BUFFER_THRESHOLD`, incorrectly classifying overwrites, and surfacing generic IO exceptions instead of container protocol result codes.

## Test signals
The tests assert byte-array equality, buffer counts, remaining lengths, success/fail counters, exception result code `UNABLE_TO_FIND_CHUNK`, and deterministic random data matches across multiple file sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/helpers/TestChunkUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/AbstractTestChunkManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/AbstractTestChunkManager.java

## Purpose
`AbstractTestChunkManager` is the shared fixture for chunk-manager implementation tests. It creates a formatted temporary `HddsVolume`, a real `KeyValueContainer`, default block/chunk/data fixtures, and reusable assertions for chunk file counts, file closure, and volume IO metrics.

## Important APIs, types, and functions
Subclasses implement `getStrategy()` returning `ContainerLayoutTestInfo`, which controls layout-specific configuration and chunk-manager construction. `createTestSubject()` builds a `BlockManagerImpl` and delegates to `getStrategy().createChunkManager(true, blockManager)`. Helper methods expose `KeyValueContainer`, `KeyValueContainerData`, `BlockID`, `ChunkInfo`, test `ByteBuffer`, and `BlockManager`.

## Control flow
The `@BeforeEach setUp` method configures the selected strategy, creates/formats an `HddsVolume`, mocks a `MutableVolumeSet` and `RoundRobinVolumeChoosingPolicy`, constructs `KeyValueContainerData` with configured layout, creates the container on disk, and initializes test bytes. The fixture stores a header prefix in the data buffer and positions the buffer after the header so chunk-manager writes test only the payload bytes.

## State and persistence behavior
Container directories, metadata paths, and chunk paths are real filesystem artifacts. `checkChunkFileCount` enumerates the chunk directory. `checkWriteIOStats` and `checkReadIOStats` assert volume-level byte/op counters. `checkChunkFilesClosed` uses `lsof` to verify chunk files are no longer open after finish/commit paths.

## Dependencies and integration points
The fixture integrates container layout abstraction, block manager persistence, volume formatting, volume choosing policy, JUnit temp directories, Mockito, and OS-level `lsof`. It underpins dummy, file-per-chunk, file-per-block, and shared chunk-manager tests.

## Risks and edge cases
The fixture itself can skip file-closure tests when `lsof` is unavailable by aborting. Incorrect buffer positioning would cascade into many chunk length assertions. Because it uses real volume stats, tests can catch regressions in IO accounting as well as filesystem layout.

## Test signals
Downstream tests rely on this fixture for exact file-count assertions, chunk data equality after rewinding to payload start, read/write op count checks, and detection of leaked file handles.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/AbstractTestChunkManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/CommonChunkManagerTestCases.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/CommonChunkManagerTestCases.java

## Purpose
`CommonChunkManagerTestCases` defines behavior expected of real chunk-manager strategies. It covers invalid write sizes, oversized reads, write/read/delete lifecycle, missing chunks, repeated chunk IO, and finishing writes.

## Important APIs, types, and functions
The class calls `ChunkManager.writeChunk`, `readChunk`, `deleteChunk`, and `finishWriteChunks`, plus `BlockManager.putBlock` for read validation. It uses `WRITE_STAGE`, `COMBINED_STAGE`, `OZONE_SCM_CHUNK_MAX_SIZE`, `StorageContainerException`, `ContainerProtos.Result`, `BlockData`, `ChunkInfo`, and strategy-specific `getLayout().getChunkFile`.

## Control flow
Each test obtains the implementation via `createTestSubject()`. Invalid-length writes set a declared chunk length that does not match the prepared data buffer and expect `INVALID_WRITE_SIZE`. Oversized read manually writes a chunk file larger than `OZONE_SCM_CHUNK_MAX_SIZE`, bypassing the write path, and expects read failure. Normal write/read tests write a chunk, persist block metadata, then read and compare bytes. Multi-write tests create 100 chunk names and offsets and verify aggregate stats.

## State and persistence behavior
The tests assert chunk files are created or deleted on disk, block metadata is inserted before read validation, and volume IO stats match byte totals and operation counts. `finishWriteChunks` uses a mocked `BlockData` with the fixture block ID and then verifies chunk files are closed.

## Dependencies and integration points
These tests are inherited by file-per-block and file-per-chunk strategies, ensuring both strategy-specific implementations satisfy the same container protocol contract. They integrate storage exceptions, layout-specific chunk path generation, and block metadata dependencies for reads.

## Risks and edge cases
Covered risks include accepting mismatched buffer lengths, allowing reads larger than the configured max, partial delete requests being accepted, misreporting missing chunks, leaking temporary files after finish, and cumulative IO-stat drift across repeated writes.

## Test signals
Strong signals are protocol result codes (`INVALID_WRITE_SIZE`, `UNSUPPORTED_REQUEST`, `UNABLE_TO_FIND_CHUNK`), chunk file counts, byte-for-byte buffer comparison, and volume read/write byte/op counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/CommonChunkManagerTestCases.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestBlockManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestBlockManagerImpl.java

## Purpose
This suite tests `BlockManagerImpl` block metadata persistence, BCSID handling, list behavior, closed-container put-block semantics, and incremental chunk-list merging for hsync-style writes.

## Important APIs, types, and functions
The tests use `BlockManagerImpl.putBlock`, `putBlockForClosedContainer`, `getBlock`, and `listBlock`, plus `BlockUtils.getDB` to inspect RocksDB metadata. Test data is built with `BlockData`, `BlockID`, `ChunkInfo`, `INCREMENTAL_CHUNK_LIST`, and `BlockManagerImpl.FULL_CHUNK`. Layout/schema coverage is provided by `ContainerTestVersionInfo.ContainerTest`.

## Control flow
`initTest` selects layout/schema, initializes an `HddsVolume`, creates a `KeyValueContainer`, and prepares two block records. Basic tests put blocks with and without BCSID, read them back, and list them. Closed-container tests close the container, then put blocks with different BCSID values and overwrite flags while inspecting in-memory and persisted metadata. Flush tests simulate repeated hsyncs that either extend a partial chunk or merge full chunks with a trailing incremental chunk.

## State and persistence behavior
The suite verifies `blockCount`, `blockCommitSequenceId`, block table rows, metadata table keys for block count and BCSID, and bytes-used metadata. It specifically asserts that `putBlockForClosedContainer` can persist blocks with higher BCSID without making them readable until container BCSID is overwritten, and that simple put-block operations without corresponding write-chunk calls do not alter persisted bytes used.

## Dependencies and integration points
The tests integrate key-value container creation, schema-aware DB stores, block metadata encoding, chunk metadata lists, schema-v1 assumptions, and cache shutdown via `BlockUtils.shutdownCache`. They are central for datanode recovery and hsync semantics.

## Risks and edge cases
Risks include double-counting blocks on overwrite, decreasing container BCSID, exposing blocks whose BCSID is newer than the container, losing full chunk markers during incremental merge, and updating bytes-used from block metadata alone.

## Test signals
Signals include exact block count/BCSID values in both `KeyValueContainerData` and RocksDB metadata, `StorageContainerException` on reads gated by BCSID, chunk list lengths/offsets/lengths after flush merges, and schema-v1 skip assumptions for incremental-list behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestBlockManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestChunkManagerDummyImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestChunkManagerDummyImpl.java

## Purpose
This small suite validates the dummy chunk-manager strategy used by tests or non-persistent paths. It confirms the dummy implementation accepts writes without creating files and returns non-null data for reads regardless of underlying chunk existence.

## Important APIs, types, and functions
The class extends `AbstractTestChunkManager`, selects `ContainerLayoutTestInfo.DUMMY`, and calls `ChunkManager.writeChunk` and `readChunk`. It uses the shared fixture block ID, chunk info, prepared data buffer, and `WRITE_STAGE`.

## Control flow
`dummyManagerDoesNotWriteToFile` creates the dummy subject, writes the fixture chunk, and immediately checks that the chunk directory remains empty. `dummyManagerReadsAnyChunk` reads from the dummy manager without preparing a file and asserts the returned `ChunkBufferToByteString` is non-null.

## State and persistence behavior
The intended behavior is explicitly non-persistent. The container and chunk directory exist because the abstract fixture creates them, but dummy writes do not create chunk files and dummy reads do not depend on filesystem state.

## Dependencies and integration points
The suite depends on the shared chunk-manager fixture for a real container context while checking that the dummy strategy bypasses real storage effects. This protects tests or flows that intentionally use a no-op chunk implementation.

## Risks and edge cases
The main risk is a dummy implementation accidentally inheriting real file-writing behavior or returning null on reads, which would break tests expecting non-storage semantics.

## Test signals
Signals are simple but precise: chunk file count remains zero after write, and read returns a non-null buffer object.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestChunkManagerDummyImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerBlockStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerBlockStrategy.java

## Purpose
`TestFilePerBlockStrategy` tests the file-per-block chunk layout and inherits the common chunk-manager contract. Its local tests focus on multi-write block files, partial reads, closed-container recovery writes, bytes-used accounting for overwrites and extensions, block persistence for closed containers, and checksum updates.

## Important APIs, types, and functions
The suite uses `ChunkManager.writeChunk`, `readChunk`, `deleteChunk`, `KeyValueHandler.writeChunkForClosedContainer`, `putBlockForClosedContainer`, `updateAndGetContainerChecksumFromMetadata`, `BlockUtils.getDB`, and `ContainerLayoutTestInfo.FILE_PER_BLOCK`. It also uses `ContainerTestHelper.getChunk`, `setDataChecksum`, `ChunkBuffer`, `ChunkBufferToByteString`, and `verifyAllDataChecksumsMatch`.

## Control flow
One test writes 1024 small ranges into the same block file at increasing offsets and reads the whole region back, comparing file hashes. Partial-read tests write a single chunk and read both full and sliced ranges. Closed-container tests first close a container through `markContainerForClose` and `closeContainer`, then allow recovery writes and block puts; the same operations are asserted to fail for non-closed states. Bytes-used tests write initial data, then overwrite from a midpoint with a longer buffer and expect only the extension delta to be charged.

## State and persistence behavior
The file-per-block strategy stores multiple logical chunks in one block file, so offset and length handling directly affects file size, volume used space, container `bytesUsed`, and `statistics.writeBytes`. Closed-container put-block tests inspect RocksDB block rows and metadata table bytes-used values after appending chunks and replacing the last chunk with a larger one. Container data checksum is updated after metadata changes and verified against persisted metadata.

## Dependencies and integration points
The tests integrate chunk IO, closed-container reconstruction, container state transitions, volume and metadata configuration, `MutableVolumeSet`, `ContainerSet`, DB stores, and checksum validation. They exercise recovery behavior that spans `KeyValueHandler`, `ChunkManager`, and `BlockManager`.

## Risks and edge cases
Covered risks include accepting partial delete with nonzero offset, corrupting readback across many writes, slicing wrong byte ranges, allowing recovery writes in non-closed states, double-counting overwrites, not charging extension deltas, stale data checksums, and block-count drift on repeated closed-container put-blocks.

## Test signals
Signals include SHA digest equality, ByteString equality for full/partial reads, protocol result `UNSUPPORTED_REQUEST`, IOException assertions for invalid states, exact bytes-used/statistics values, RocksDB row comparisons, and checksum verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerBlockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerChunkStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerChunkStrategy.java

## Purpose
This suite tests file-per-chunk-specific behavior while inheriting common chunk-manager tests. It focuses on two-stage write/commit handling and compatibility with old chunk files whose physical file length includes the chunk offset.

## Important APIs, types, and functions
The class selects `ContainerLayoutTestInfo.FILE_PER_CHUNK`, uses `ChunkManager.writeChunk` and `deleteChunk`, and references `WRITE_STAGE`, `COMMIT_STAGE`, `ContainerLayoutVersion.FILE_PER_CHUNK.getChunkFile`, `OzoneConsts.CONTAINER_TEMPORARY_CHUNK_PREFIX`, and `ChunkUtils.writeData`.

## Control flow
`testWriteChunkStageWriteAndCommit` writes fixture data in `WRITE_STAGE`, expects a temporary chunk file, then writes the same chunk in `COMMIT_STAGE`, expecting the temp file to be renamed to the final chunk file without an additional IO-stat increment. `deletesChunkFileWithLengthIncludingOffset` manually writes a chunk file at offset 1024 so its file length is `offset + len`, then calls `deleteChunk` with that historical chunk info.

## State and persistence behavior
In file-per-chunk layout, each logical chunk becomes a separate file. During write stage the file is temporary and includes term/index suffixes; during commit it becomes the final chunk name. The compatibility delete test verifies deletion accepts a file whose physical length is larger than the logical chunk length because old clients/datanodes wrote offset-inclusive files.

## Dependencies and integration points
The suite integrates layout-specific chunk naming, temporary-file promotion, Ozone chunk name delimiters, and shared volume IO counters from the abstract fixture. It protects interop behavior between old and new datanode/client versions.

## Risks and edge cases
Risks include leaving temporary files after commit, double-counting commit IO, failing to delete old-format chunk files, or confusing logical chunk length with physical file length.

## Test signals
Signals are final and temporary file existence checks, chunk directory file count, file length assertions, and write IO stats remaining stable across commit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerChunkStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestKeyValueStreamDataChannel.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestKeyValueStreamDataChannel.java

## Purpose
`TestKeyValueStreamDataChannel` verifies the Ratis data-stream write path used for streamed key-value writes. It tests serialization of appended `PutBlock` requests, space-availability failure behavior, buffer splitting/reassembly, and close-time extraction of the trailing put-block proto.

## Important APIs, types, and functions
The suite exercises `KeyValueStreamDataChannel.readProtoLength`, `writeBuffers`, `writeFully`, `assertSpaceAvailability`, and `write`, plus static helpers from `BlockDataStreamOutput`: `PUT_BLOCK_REQUEST_LENGTH_MAX`, `executePutBlockClose`, and `getProtoLength`. It defines test `Output` and `Reply` implementations of Ratis `DataStreamOutput` and `DataStreamReply`.

## Control flow
`testSerialization` builds a data buffer followed by the serialized `PUT_BLOCK_PROTO` and four-byte proto length, then reads the request back and rewinds the `ByteBuf` writer index to expose only data. `testVolumeFullCase` constructs a channel over a temp file with a mocked full `HddsVolume`, expecting `StorageContainerException` both from explicit space checking and `write`. `testBuffers` runs many combinations of output buffer max size and data size in parallel, writing random byte ranges and then closing with `executePutBlockClose`.

## State and persistence behavior
The in-memory `ByteBuf` in `Output` collects only application data; the appended put-block request is consumed at close and not left in the data output. The volume-full test checks no write proceeds when the mocked volume has zero available capacity. Reference-counted buffers are retained and released around write calls.

## Dependencies and integration points
This file integrates Ozone container command protobufs, Ratis `ContainerCommandRequestMessage`, Netty `ByteBuf`, Ratis stream APIs, volume usage, and container metrics. It protects the wire-format contract between streaming data and terminal put-block metadata.

## Risks and edge cases
Risks include miscomputing the four-byte proto length location, corrupting data when writes split across buffer boundaries, writing put-block bytes into user data, leaking reference-counted buffers, and allowing stream writes when a container volume is full.

## Test signals
Signals include exact proto equality, output data byte-for-byte equality, successful replies with correct bytes written, close replies carrying the parsed put-block request, and exceptions for full-volume writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestKeyValueStreamDataChannel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestMappedBufferManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestMappedBufferManager.java

## Purpose
This test verifies the caching semantics of `MappedBufferManager.computeIfAbsent`. It ensures a buffer already cached for a file/position/size key is reused instead of replaced by a later supplier.

## Important APIs, types, and functions
The file constructs `MappedBufferManager(100)` and calls `computeIfAbsent(file, position, size, supplier)`. It uses `ByteBuffer.allocate` for two different candidate buffers and JUnit `assertEquals`.

## Control flow
The first call stores `buffer1` for a path, position zero, and size 1024. The second call uses an equivalent path string, same position and size, but a supplier for `buffer2` of a different capacity. The expected return is still `buffer1`.

## State and persistence behavior
The state under test is the manager's in-memory mapping from file/position/size to `ByteBuffer`. No filesystem access is performed even though the key looks like a real chunk file path.

## Dependencies and integration points
`MappedBufferManager` is used by chunk read utilities for memory-mapped or cached buffers. This test protects cache-key behavior relied on by repeated reads of the same chunk range.

## Risks and edge cases
The main risk is replacing a cached buffer on a repeated lookup, which could defeat reuse and increase memory churn. It also implicitly checks that identical file strings are treated as identical keys.

## Test signals
The single signal is object equality: both `computeIfAbsent` calls return the original `buffer1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestMappedBufferManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java

## Purpose
This package-info file documents the test package `org.apache.hadoop.ozone.container.keyvalue` as "Chunk Manager Checks." It provides package-level documentation rather than executable code.

## Important APIs, types, and functions
There are no classes, methods, or fields. The only semantic content is the Javadoc package comment and the package declaration.

## Control flow
No runtime control flow exists.

## State and persistence behavior
No state is stored or persisted by this file.

## Dependencies and integration points
The file attaches documentation to the `org.apache.hadoop.ozone.container.keyvalue` test package and is discovered by Java documentation tooling.

## Risks and edge cases
The only practical risk is stale or overly narrow package documentation if the package expands beyond chunk-manager checks.

## Test signals
There are no direct test signals. Its presence supports package documentation and compiler/package consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerDataScanner.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerDataScanner.java

## Purpose
This suite tests `BackgroundContainerDataScanner`, the per-volume scanner that reads container data and detects corrupt chunks. It validates scan scheduling, unhealthy marking, metrics, checksum update behavior, failed-volume shutdown, clean shutdown during blocked scans, DB-close concurrency, Merkle-tree writing, and "too many open files" suppression.

## Important APIs, types, and functions
The tests call `scanner.runIteration`, `start`, `shutdown`, `isAlive`, and `getMetrics`. They verify `Container.scanData`, `controller.markContainerUnhealthy`, `updateDataScanTimestamp`, `updateContainerChecksum`, `StorageVolumeUtil.onFailure`, and `ContainerDataScannerMetrics`. They use `DataScanResult`, `ContainerScanError`, `FailureType.CORRUPT_CHUNK`, `ContainerMerkleTreeWriter`, `DatanodeStoreSchemaThreeImpl`, and raw table iterators.

## Control flow
The inherited scanner fixture supplies healthy, corrupt-data, corrupt-metadata, open, and deleted containers. Tests manipulate last-scan timestamps to confirm recent containers are skipped and stale/unscanned containers are scanned. Unhealthy detection marks only data-corrupt eligible containers, not open or deleted containers. Failed-volume tests either prevent any iteration from starting or simulate failure mid-iteration, expecting thread termination.

## State and persistence behavior
The scanner updates data-scan timestamps only for containers it scans and writes Merkle-tree checksum data for closed/non-deleted scanned containers. Metrics track iterations, scanned containers, and newly unhealthy containers. The DB-close test opens an iterator inside `scanData`, stops the store concurrently, then releases iteration and expects no exception to escape.

## Dependencies and integration points
The suite integrates scanner scheduling, volume health, controller callbacks, container checksum persistence, metrics registration, RocksDB table iteration, throttling/cancelation parameters, and static volume-failure handling. It contrasts with the metadata scanner by expecting data scanner shutdown when its volume fails.

## Risks and edge cases
Covered risks include rescanning unhealthy containers incorrectly, marking containers unhealthy due only to file-descriptor exhaustion, updating checksums after suppressed scans, hanging on shutdown, crashing when volume failure closes DB resources mid-scan, and continuing data scanning after volume failure.

## Test signals
Signals include Mockito verification of scan methods and controller callbacks, metrics counters, thread liveness checks, `assertDoesNotThrow` around concurrent DB close, and absence of checksum/timestamp updates for suppressed or ineligible containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerDataScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerMetadataScanner.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerMetadataScanner.java

## Purpose
This suite tests `BackgroundContainerMetadataScanner`, the process-level scanner for container metadata. It validates timestamp-based scheduling, unhealthy metadata detection, metrics, failed-volume skipping without scanner shutdown, shutdown during a blocked metadata scan, and suppression of "too many open files" metadata-only failures.

## Important APIs, types, and functions
The tests call `scanner.runIteration`, `start`, `shutdown`, `isAlive`, and `getMetrics`. They verify `Container.scanMetaData`, `controller.markContainerUnhealthy`, `StorageVolumeUtil.onFailure`, and `ContainerMetadataScannerMetrics`. They use `MetadataScanResult`, `ContainerScanError`, `FailureType.CORRUPT_CONTAINER_FILE`, and shared `TestContainerScannersAbstract` fixtures.

## Control flow
Recent containers are skipped, stale and unscanned containers are scanned, and scanner metrics are checked after a single iteration. Metadata corruption is expected to mark `openCorruptMetadata` unhealthy, while data corruption alone is not detected by this scanner. Rescan tests first transition a mock container to unhealthy, then run another iteration and confirm metrics do not double-count newly unhealthy containers.

## State and persistence behavior
Unlike the data scanner, this scanner does not update container checksums, so an injected `updateContainerChecksum` failure must not affect metadata-scanner behavior. When the backing volume is failed, queued containers on that volume are skipped, metrics record no scanned/unhealthy containers, but the metadata scanner thread remains alive until explicitly shut down.

## Dependencies and integration points
The file integrates metadata scanning, global scanner lifecycle, volume health checks, controller unhealthy marking, metrics registration/unregistration, and static volume failure notification. It shares abstract scanner fixtures with the data scanner but asserts different policy decisions.

## Risks and edge cases
Risks include treating data corruption as metadata corruption, shutting down the whole metadata scanner because one volume failed, marking containers unhealthy during file-descriptor exhaustion, double-counting unhealthy metrics on rescan, and failing to unregister metrics on shutdown.

## Test signals
Signals are method invocation counts on `scanMetaData` and `markContainerUnhealthy`, metrics values, metrics-system source registration checks, scanner liveness after failed-volume encounter, and explicit non-invocation of unhealthy marking for too-many-open-files-only results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerMetadataScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerReader.java

## Purpose
`TestContainerReader` validates datanode startup loading of key-value containers from disk. It checks metadata reconstruction, pending-delete counters, committed-space accounting, load-exception handling, invalid DB handling, parallel volume readers, duplicate/conflicting container resolution, deleted/recovering cleanup, EC replica-index selection, and checksum restoration.

## Important APIs, types, and functions
The suite exercises `ContainerReader.run`, `readVolume`, `KeyValueContainer.create`, `BlockUtils.getDB`, `ContainerCache.shutdownCache`, `ContainerSet`, `WitnessedContainerMetadataStore`, `ContainerCreateInfo`, and checksum helpers. It manipulates `DatanodeStoreSchemaOneImpl`, `DatanodeStoreSchemaTwoImpl`, and `DatanodeStoreSchemaThreeImpl` delete/block/metadata tables, plus `ContainerChecksumTreeManager` and `KeyValueHandler.updateContainerChecksum`.

## Control flow
Setup creates a real `HddsVolume`, two containers, block metadata, and pending-deletion records using schema-specific table formats. Reader tests start `ContainerReader` threads and join them, then inspect loaded container data. Multi-reader tests configure ten volumes, create 100 containers with deliberate conflicts, start one reader per volume, and verify winner selection. Checksum tests create containers with Merkle tree sidecars, no sidecars, or empty sidecars before reader startup.

## State and persistence behavior
The reader must reconstruct `blockCount`, `bytesUsed`, pending-delete block count/bytes, BCSID, committed-space flags, replica indexes, and data checksums from disk. Invalid or missing DB paths prevent loading and committed-byte increases. Marked `DELETED` containers are removed and their schema-v3 DB metadata entries are cleaned up. Ratis replicated `RECOVERING` containers are deleted on startup, while EC recovering containers can be marked unhealthy.

## Dependencies and integration points
This file spans container disk layout, volume sets, DB schema versions, container-create metadata, deleted-block transaction tables, container cache behavior, EC replica metadata, and checksum sidecar/RocksDB fallback. It is one of the strongest startup integration tests in this subset.

## Risks and edge cases
Risks include loading duplicate containers nondeterministically, deleting the wrong duplicate, ignoring higher BCSID or closed-state preference, mishandling EC replicas with same/different replica indexes, leaving deleted containers on disk or in DB, counting committed space for containers that failed to load, and failing to populate data checksum from Merkle trees or fallback metadata.

## Test signals
Signals include container counts, existence/removal of conflicting paths, committed-byte totals, container state assertions, replica-index assertions, cache size remaining zero, RocksDB metadata key counts, log text for missing DBs, and `verifyAllDataChecksumsMatch` across checksum scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannerConfiguration.java

## Purpose
This suite verifies configuration binding and validation for `ContainerScannerConfiguration`, including metadata scan interval, data scan interval, minimum per-container scan gap, background bandwidth, and on-demand bandwidth.

## Important APIs, types, and functions
The tests use `OzoneConfiguration`, `conf.getObject(ContainerScannerConfiguration.class)`, scanner configuration keys, defaults, and `StorageUnit.MB.toBytes`.

## Control flow
`acceptsValidValues` sets positive interval and bandwidth values and expects getters to return them unchanged. `overridesInvalidValues` sets negative intervals and bandwidths and expects defaults. `isCreatedWitDefaultValues` builds the object from an empty configuration and expects scanning enabled with all default values.

## State and persistence behavior
No filesystem state is used. The state under test is the configuration object generated from `OzoneConfiguration` and its validation/defaulting logic.

## Dependencies and integration points
The tested configuration feeds background data scanners, metadata scanners, and on-demand scanner throttling. Correct validation prevents disabled or nonsensical scanner scheduling due to bad configuration.

## Risks and edge cases
Risks include accepting negative intervals or bandwidths, overriding valid values, defaulting on-demand bandwidth incorrectly, and accidentally disabling scanning by default.

## Test signals
Signals are exact getter values for valid inputs, exact default constants for invalid inputs, and `isEnabled()` being true for default configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannerConfiguration.java -->
