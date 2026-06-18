# subset-b-008058 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/RpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/RpcClient.java

## Purpose
`RpcClient` is the RPC-backed implementation of `ClientProtocol` for the Ozone Java client. It is the main client-side bridge from public `OzoneClient`, `ObjectStore`, `OzoneVolume`, and `OzoneBucket` operations to OM RPCs and datanode container IO. It owns the OM protocol proxy, xceiver client factory, client metrics handle, byte-buffer pool, KMS provider cache, stream builders, and OM-version feature gates used by keys, files, multipart uploads, S3 paths, tenants, snapshots, ACLs, object tagging, and lease recovery.

## Important APIs, Types, And Functions
The constructor wires `ConfigurationSource`, current `UserGroupInformation`, `ReplicationConfigValidator`, `OzoneClientConfig`, OM transport/proxy, `XceiverClientFactory`, `BoundedElasticByteBufferPool`, `BlockInputStreamFactory`, `ContainerClientMetrics`, memoized EC reconstruction and write executors, and server-default/KMS cache settings. `createOmTransport` and `createXceiverClientFactory` are `@VisibleForTesting` hooks heavily used by tests in this subset to inject `MockOmTransport` and `MockXceiverClientFactory`.

Volume and bucket APIs include `createVolume`, `setVolumeOwner`, `setVolumeQuota`, `getVolumeDetails`, `listVolumes`, `createBucket`, bucket property setters, `deleteBucket`, `getBucketDetails`, and `listBuckets`. These validate names and quotas, translate public argument objects into OM helper objects such as `OmVolumeArgs`, `OmBucketInfo`, and `OmBucketArgs`, and delegate persistence to `ozoneManagerClient`.

Key/file APIs include `createKey`, `rewriteKey`, `createKeyIfNotExists`, `rewriteKeyIfMatch`, stream variants, `getKey`, `getKeysEveryReplicas`, `deleteKey(s)`, `renameKey(s)`, `listKeys`, `getKeyDetails`, `headObject`, `createFile`, `createStreamFile`, `readFile`, and status listings. They build `OmKeyArgs`, call OM open/get/lookup APIs, and create `OzoneOutputStream`, `OzoneDataStreamOutput`, or `OzoneInputStream` instances around `KeyOutputStream`, `ECKeyOutputStream`, `KeyDataStreamOutput`, `KeyInputStream`, `ECBlockInputStream`, and crypto wrappers.

Multipart APIs cover initiation, part stream creation, completion with optional generation/ETag constraints, abort, part listing, and upload listing. Security/admin APIs cover delegation tokens, S3 secrets, tenant creation/deletion/user/admin operations, S3 context lookup, S3 auth thread locals, ACL operations, snapshots and snapshot diff jobs, bucket owner updates, timestamps, lease recovery, and object tagging.

## Control Flow
Construction first builds the OM transport and translator, retrieves service info, computes the minimum OM version visible in the service list, checks S3-auth version requirements when security is enabled, then creates the xceiver client manager and stream support objects. Most public mutating methods follow a pattern: validate public names/arguments, check `omVersion` for feature availability, build an OM helper/protobuf-friendly argument object, and call the OM protocol.

Write control flow goes through `createWriteKeyArgsBuilder` or `createStreamKeyArgsBuilder`, then `ozoneManagerClient.openKey` or `createFile`, then stream creation. `createKeyOutputStream` selects `ECKeyOutputStream.Builder` for EC replication and regular `KeyOutputStream.Builder` otherwise; both receive xceiver manager, OM client, unsafe byte-buffer setting, client config, metrics, write executor supplier, stream buffer args, and OM version. Data stream output uses `KeyDataStreamOutput` only for RATIS; non-RATIS falls back to normal output streams.

Read control flow resolves `OmKeyInfo` via optimized `getKeyInfo` when supported or legacy `lookupKey` otherwise. `getInputStreamWithRetryFunction` passes a retry callback that refreshes key location info from OM with container-cache refresh enabled. `createInputStream` then selects plain `KeyInputStream`, GDPR cipher wrapper, KMS crypto stream, or multipart crypto stream depending on file encryption info and metadata.

## State And Persistence Behavior
`RpcClient` itself does not persist Ozone metadata. Persistent state lives in OM and datanodes; this class constructs and submits requests that change volumes, buckets, keys, multipart uploads, tenants, ACLs, snapshots, tags, and lease state. Local state includes cached `KeyProvider`s keyed by URI, memoized executors, `serverDefaults` and update timestamp, byte-buffer pool capacity, metrics handle, delegation-token service text, `s3gUgi`, and thread-local S3 auth delegated through the OM client.

The key-provider cache closes providers through a removal listener. `close()` shuts down initialized executors, closes OM and xceiver clients, invalidates/cleans the key-provider cache, and releases metrics. Server defaults are refreshed lazily after `serverDefaultsValidityPeriod`.

## Dependencies And Integration Points
This file integrates with OM via `OzoneManagerClientProtocol` and `OzoneManagerProtocolClientSideTranslatorPB`, with SCM/datanodes via `XceiverClientFactory`, `KeyOutputStream`, and input stream factories, with KMS via `OzoneKMSUtil` and Hadoop `KeyProvider`, with security via `UserGroupInformation`, delegation tokens, S3 auth, and TLS trust manager setup, and with versioned OM behavior through `OzoneManagerVersion`.

Important feature gates include EC storage, optimized get-key-info, lightweight key/status listings, atomic rewrite/create, object tags, S3 part-aware get, S3 object tagging APIs, multipart pagination, and HBase lease recovery. Tests in this subset override `createOmTransport` and `createXceiverClientFactory` to make this production class run against in-memory OM and datanode mocks.

## Risks And Edge Cases
Many methods depend on OM-version comparisons; missing or stale service info can accidentally use a fallback path or reject a newer feature. Quota validation throws `IllegalArgumentException` despite declaring `OMException`, so callers must tolerate unchecked validation failures. `getKeysEveryReplicas` mutates the `keyInfo` location versions while iterating replicas, which is convenient for stream construction but risky if callers reuse that object. `setThreadLocalS3Auth` assumes `getThreadLocalS3Auth()` is non-null after delegation and can throw if passed null. `getKeyProvider()` logs and returns null on provider creation failure, pushing failure later into crypto paths.

The stream construction paths are sensitive to replication config type. EC writes depend on executor, byte-buffer-pool, preallocated block, and S3 credential plumbing. Encryption handling splits between KMS file encryption and metadata-driven GDPR symmetric encryption, and malformed metadata or missing JCE/KMS support will surface as IO failures.

## Test Signals
The files in this work item exercise `RpcClient` through injected mocks rather than external services. `TestOzoneClient` covers volume/bucket/key creation, deletion, RATIS writes, block allocation, and EC key creation. `TestBlockOutputStreamIncrementalPutBlock` covers hsync with incremental and full chunk lists. `TestOzoneECClient` stresses EC output-stream behavior, retries, partial stripes, block metadata, and reads. `TestFileChecksumHelper` and `TestReplicatedBlockChecksumComputer` cover checksum integration with mocked OM/xceiver clients. Snapshot, replication-config utility, and package tests cover adjacent client-facing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/RpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.client.rpc` as the package containing Ozone RPC client library classes.

## Important APIs, Types, And Functions
It exports no functions or runtime types beyond the package declaration and package-level Javadoc.

## Control Flow
There is no executable control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The package declaration ties classes such as `RpcClient` into the Ozone client RPC namespace.

## Risks And Edge Cases
Risk is limited to documentation drift if the package grows beyond RPC client library classes.

## Test Signals
No direct tests target this descriptor; compilation/package discovery validates it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockBlockAllocator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockBlockAllocator.java

## Purpose
`MockBlockAllocator` is a test interface for generating OM `KeyLocation` entries for new keys without SCM. It lets unit tests plug in different pipeline/block allocation strategies for RATIS or EC scenarios.

## Important APIs, Types, And Functions
The single method `allocateBlock(KeyArgs createKeyRequest, ExcludeList excludeList)` returns an iterable of `KeyLocation` protobuf objects. Implementations in this subset include `SinglePipelineBlockAllocator` and `MultiNodePipelineBlockAllocator`.

## Control Flow
The interface has no implementation control flow. Callers, especially `MockOmTransport`, invoke it during create-key and allocate-block request handling.

## State And Persistence Behavior
No state is defined at the interface level. Implementations maintain block counters, cached pipelines, or cluster-node cursors.

## Dependencies And Integration Points
It depends on OM protobuf `KeyArgs`/`KeyLocation` and SCM `ExcludeList`. It integrates the in-memory OM mock with client output streams that expect OM to return allocated blocks.

## Risks And Edge Cases
Implementations must honor enough of `KeyArgs` and `ExcludeList` to match the test being run. If an implementation ignores exclusion, EC retry tests can pass incorrectly or fail for the wrong reason.

## Test Signals
All client write tests using `MockOmTransport` indirectly depend on this contract. EC retry tests provide the strongest signal because they validate exclude-aware block reallocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockBlockAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockDatanodeStorage.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockDatanodeStorage.java

## Purpose
`MockDatanodeStorage` is an in-memory representation of one datanode's persisted container data for client unit tests. It stores block metadata, block-to-container indexes, chunk bytes, full block string data for assertions, and an optional injected failure.

## Important APIs, Types, And Functions
`setStorageFailed(IOException)` injects write failures. `putBlock` dispatches between full and incremental chunk-list updates by checking `OzoneConsts.INCREMENTAL_CHUNK_LIST` metadata. `putBlockIncremental` appends new chunks to existing block data and prunes the previous trailing partial chunk unless it is marked with `FULL_CHUNK_KV`. `putBlockFull` replaces block metadata and updates `containerBlocks`. `getBlock`, `listBlock`, `writeChunk`, `readChunkData`, `getAllBlockData`, and `getFullBlockData` provide the storage operations consumed by `MockXceiverClientSpi` and assertions.

## Control Flow
Write-chunk requests append bytes to a per-block `ByteString`, asserting that chunk offsets are sequential. Put-block requests either replace the block's chunk list or merge incremental chunk lists into an existing block. Read requests slice bytes from the stored block data according to chunk offset and length. Failure injection is checked in `writeChunk` before mutation.

## State And Persistence Behavior
All state is process-local and in-memory: `blocks`, `containerBlocks`, `fullBlockData`, `data`, and `exception`. It models persistence well enough for a single test run but has no synchronization, no deletion, and no durable storage. `fullBlockData` concatenates UTF-8 strings from written bytes and is used by EC tests to compare parity or partial-stripe content.

## Dependencies And Integration Points
It uses HDDS `BlockID`, datanode protobuf `BlockData`, `ChunkInfo`, `DatanodeBlockID`, and protobuf `ByteString`. `MockXceiverClientSpi` is the main caller, while EC and incremental put-block tests inspect the stored data directly.

## Risks And Edge Cases
The class uses Java `assert` for offset sanity, so checks can be disabled depending on JVM flags. `listBlock` assumes the container exists and will throw a null-pointer error otherwise. Incremental chunk merging has a TODO for validating offsets and lengths. `HashedMap` and ordinary `HashMap` state are not thread-safe, which can matter if async client writers interact concurrently in tests.

## Test Signals
`TestBlockOutputStreamIncrementalPutBlock` validates incremental and full chunk-list readback. `TestOzoneECClient` validates EC data/parity storage, block group length metadata, partial stripe data, retry behavior, and failure injection through this storage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockDatanodeStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockOmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockOmTransport.java

## Purpose
`MockOmTransport` implements `OmTransport` with in-memory OM state so Ozone client unit tests can run without an OM service. It handles a deliberately small set of OM commands needed by client write/read tests.

## Important APIs, Types, And Functions
The constructor accepts a `MockBlockAllocator`, defaulting to `SinglePipelineBlockAllocator`. `submitRequest` switches on OM command type and supports volume create/info/delete, bucket create/info, key create/commit/lookup/get-info, service list, open-file list, and allocate-block. `createKey` allocates initial locations and resolves replication from key args, bucket default replication, or RATIS THREE fallback. `commitKey` moves an open key to committed keys unless the request is hsync, preserving replication details and committing locations from `KeyArgs`. `getKeys` exposes committed key state for assertions.

## Control Flow
Requests enter `submitRequest`, dispatch to command-specific helpers, and are wrapped by `response`, which converts `MockOmException` into unsuccessful `OMResponse` statuses. `createVolume` initializes nested bucket/open-key/key maps. `createBucket` stores bucket info and initializes per-bucket key maps. `createKey` creates an open `KeyInfo` with allocated locations. `commitKey` reads the open key, optionally removes it, builds committed key info from request key locations and sizes, and stores it in `keys`.

## State And Persistence Behavior
State is all in-memory: `volumes`, `buckets`, `openKeys`, and `keys`. It models OM metadata persistence for a single test process. Hsync commits keep the open key present while writing committed key state, which is important for incremental hsync tests. No concurrency control, deletion cleanup beyond volume map removal, or full OM validation is provided.

## Dependencies And Integration Points
It integrates with `RpcClient` via the `createOmTransport` test override and with stream code through protobuf OM responses. It depends on `MockBlockAllocator` for pipeline and block allocation, `DefaultReplicationConfig`/`ReplicationConfig` for bucket defaults, and OM protobuf request/response classes.

## Risks And Edge Cases
Unsupported OM calls throw `IllegalArgumentException`, so tests must stay inside the modeled surface. Many nested map lookups assume volumes/buckets/keys exist. `deleteVolume` removes only `volumes`, leaving other maps behind. `serviceList` returns an empty response, so production code paths requiring rich service metadata may not be accurately modeled. Replication defaulting is simplified.

## Test Signals
Used by `TestOzoneClient`, `TestBlockOutputStreamIncrementalPutBlock`, `TestOzoneECClient`, and `TestFileChecksumHelper`. These tests validate volume/bucket creation, key open/commit/read, EC block allocation, default replication propagation, hsync behavior, and committed-key metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockOmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientFactory.java

## Purpose
`MockXceiverClientFactory` provides datanode xceiver clients backed by per-datanode `MockDatanodeStorage` instances. It replaces SCM/datanode networking in client unit tests.

## Important APIs, Types, And Functions
`acquireClient(Pipeline)` and `acquireClient(Pipeline, boolean topologyAware)` return `MockXceiverClientSpi` objects using storage for the first node or closest node. `acquireClientForReadData` uses the pipeline first node. `setFailedStorages` and `mockStorageFailure` queue or apply injected `IOException`s to selected datanodes. `getStorages` exposes the storage map for assertions.

## Control Flow
When a client is acquired, the factory creates or reuses storage for the target datanode. It then scans pending failure reasons and applies any failures whose datanode storage now exists. Failure injection can be requested before storage materialization; pending datanode sets are kept until applied.

## State And Persistence Behavior
The factory stores a concurrent map of datanode details to mock storage and a concurrent map of pending exception reasons to datanode sets. Close and release methods are no-ops. Persistence is in-memory only.

## Dependencies And Integration Points
It implements `XceiverClientFactory`, returns `MockXceiverClientSpi`, and integrates with `RpcClient` through test overrides. EC tests rely on `getStorages` for validating data/parity layout and on failure injection for retry behavior.

## Risks And Edge Cases
Exception objects are used as map keys for pending failures, so equality is by object identity unless an exception overrides it. Release/invalidation behavior is not modeled. Topology-aware acquisition is reduced to closest-node selection. Pending failure application iterates concurrent sets and removes items while iterating, which is supported by concurrent key sets but still test-model-specific.

## Test Signals
`TestOzoneECClient` validates failure injection, exclude-list behavior, retry allocation, and storage counts. `TestOzoneClient` and checksum tests use it for basic key IO and checksum block fetches.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientSpi.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientSpi.java

## Purpose
`MockXceiverClientSpi` is the mocked datanode RPC client used by unit tests. It translates container command protobuf requests into operations on a single `MockDatanodeStorage`.

## Important APIs, Types, And Functions
`sendCommandAsync` supports `WriteChunk`, `ReadChunk`, `PutBlock`, `GetBlock`, and `ListBlock`. Helper methods build response protobufs and wrap them in completed `XceiverClientReply` futures. `writeChunk` writes chunk bytes and optionally processes the embedded block data. `doPutBlock` computes committed block length, stores block metadata, and returns `GetCommittedBlockLengthResponseProto`.

## Control Flow
Each command type maps directly to storage operations. `WriteChunk` catches `ContainerNotOpenException` as `CLOSED_CONTAINER_IO` and other `IOException`s as `IO_EXCEPTION`; other command paths assume success unless storage assertions fail. `result` initializes a successful response and lets helpers add command-specific payloads.

## State And Persistence Behavior
The SPI itself holds immutable references to a `Pipeline` and `MockDatanodeStorage`. Persistent test data lives in the storage object. `connect`, `close`, release, replicated min commit index, and all-node command semantics are effectively no-ops or placeholders.

## Dependencies And Integration Points
It extends `XceiverClientSpi` and consumes HDDS datanode container protobufs. It is produced by `MockXceiverClientFactory` and exercised by `KeyOutputStream`, `ECKeyOutputStream`, `KeyInputStream`, and checksum helper code.

## Risks And Edge Cases
Only a subset of datanode commands is implemented. `sendCommandOnAllNodes` returns null, so tests requiring replicated fanout semantics cannot rely on it. Error handling is limited mostly to write chunk. It does not model network latency, asynchronous failures, leader/follower behavior, or commit index advancement.

## Test Signals
All in-memory key IO tests depend on this class. EC tests validate the behavior through actual write/read paths, while checksum tests use mocked or real xceiver responses to verify checksum computation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientSpi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MultiNodePipelineBlockAllocator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MultiNodePipelineBlockAllocator.java

## Purpose
`MultiNodePipelineBlockAllocator` is a deterministic test block allocator for pipelines with multiple datanodes, primarily EC tests. It pre-creates a mock cluster and allocates block pipelines using a sliding-window node selection model.

## Important APIs, Types, And Functions
The constructor receives configuration, required pipeline node count, and cluster size, then creates `DatanodeDetailsProto` members with stable UUID bits and RATIS ports. `getClusterDns` exposes those nodes for tests. `allocateBlock` builds a pipeline with replication info from `KeyArgs`, adds members through `addMembers`, sets EC config when needed, and returns one `KeyLocation` with a sequential local block ID and configured SCM block size.

## Control Flow
`addMembers` advances a `start` cursor through the cluster, skipping datanodes present in the provided `ExcludeList`. For EC, it also assigns replica indexes starting at 1. If it cannot find enough non-excluded nodes in one pass through the cluster, it throws `IllegalStateException`.

## State And Persistence Behavior
State includes `blockId`, `requiredNodes`, immutable `conf`, prebuilt `clusterDns`, and the mutable sliding-window `start` cursor. It creates deterministic but in-memory allocation state only.

## Dependencies And Integration Points
It implements `MockBlockAllocator` for `MockOmTransport`, uses `OzoneConfigKeys.OZONE_SCM_BLOCK_SIZE`, and integrates with EC output-stream tests that assert predictable block groups, failed-node exclusions, and retry allocation.

## Risks And Edge Cases
The allocator uses one fixed pipeline ID for all allocations and fixed container ID 1, simplifying reality. It does not model SCM capacity, pipeline lifecycle, rack awareness, or container selection. If excluded nodes grow too large, allocation fails immediately with `IllegalStateException`, which some tests intentionally assert.

## Test Signals
`TestOzoneClient.testPutKeyWithECReplicationConfig` and many `TestOzoneECClient` cases depend on deterministic multi-node allocation, including retry tests that expect storage counts and block group counts to match sliding-window allocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MultiNodePipelineBlockAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/OzoneClientTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/OzoneClientTestUtils.java

## Purpose
`OzoneClientTestUtils` contains shared test helpers for Ozone client tests. In this subset it provides key-content assertions.

## Important APIs, Types, And Functions
`assertKeyContent(OzoneBucket, String, String)` converts the expected string to UTF-8 bytes and delegates to the byte-array overload. `assertKeyContent(OzoneBucket, String, byte[])` reads the key from the bucket, asserts the read bytes equal the expected content, and returns `bucket.getKey(keyName)` for further checks.

## Control Flow
The helper opens an input stream with try-with-resources, reads exactly the expected number of bytes using Commons IO `IOUtils.readFully`, performs a JUnit array assertion, then fetches key details.

## State And Persistence Behavior
The class is stateless and has a private constructor to prevent instantiation.

## Dependencies And Integration Points
It depends on `OzoneBucket`, `OzoneKeyDetails`, Commons IO, UTF-8, and JUnit assertions. It is intended for tests that need both content verification and returned key metadata.

## Risks And Edge Cases
It reads only `expected.length` bytes and does not assert EOF afterward, so trailing bytes would not be detected by this helper alone.

## Test Signals
Compilation and any tests importing this utility validate it. Within this work item, similar explicit readback assertions are implemented directly in the tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/OzoneClientTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/SinglePipelineBlockAllocator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/SinglePipelineBlockAllocator.java

## Purpose
`SinglePipelineBlockAllocator` is a deterministic one-node block allocator for simple client unit tests. It models block allocation without SCM by returning sequential blocks in one stable pipeline.

## Important APIs, Types, And Functions
The constructor stores `OzoneConfiguration`. `allocateBlock` lazily creates a one-member pipeline from `KeyArgs` replication type/factor and EC config when applicable, reads the configured SCM block size, and returns one `KeyLocation` with container ID 1 and sequential local ID.

## Control Flow
On first allocation it builds and caches the pipeline. Every call then creates a new `KeyLocation` for the next `blockId`. `ExcludeList` is accepted by the signature but ignored.

## State And Persistence Behavior
State consists of `blockId`, cached `pipeline`, and configuration reference. There is no durable persistence.

## Dependencies And Integration Points
It implements `MockBlockAllocator` for `MockOmTransport`, uses HDDS/Ozone protobufs, and is the default allocator for most non-EC mock-client tests.

## Risks And Edge Cases
Ignoring `ExcludeList` makes it unsuitable for failure/retry tests. It reuses the first replication settings for the cached pipeline; subsequent calls with different replication args will still use the original pipeline.

## Test Signals
`TestOzoneClient`, `TestBlockOutputStreamIncrementalPutBlock`, and checksum tests use this allocator through `MockOmTransport` for basic RATIS-style writes and reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/SinglePipelineBlockAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestBlockOutputStreamIncrementalPutBlock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestBlockOutputStreamIncrementalPutBlock.java

## Purpose
This JUnit test verifies `BlockOutputStream` behavior when the client writes and hsyncs repeatedly with incremental chunk-list support both enabled and disabled.

## Important APIs, Types, And Functions
`parameters` supplies `true` and `false` for incremental chunk lists. `init` configures `OzoneClientConfig` with incremental chunk list and CRC32C checksums, enables hsync/HBase enhancements, sets bytes-per-checksum, and creates an `OzoneClient` whose `RpcClient` injects `MockOmTransport` and `MockXceiverClientFactory`. `writeSmallChunk` writes a 1 KiB buffer 4097 times with hsync after each write. `writeLargeChunk` writes a 1 MiB plus 1 byte buffer four times with hsync.

## Control Flow
Each parameterized test initializes the mock client, creates volume and bucket, writes repeated buffers through `bucket.createKey`, calls `hsync` after each write, closes the stream, then reads the key back sequentially and asserts each buffer matches.

## State And Persistence Behavior
Test state is local fields for client, key, volume, bucket, and in-memory configuration. Mock OM persists key metadata in `MockOmTransport`; mock datanodes persist chunks in `MockDatanodeStorage`. `@AfterEach` closes the client.

## Dependencies And Integration Points
This test integrates `RpcClient`, `OzoneOutputStream`, `OzoneInputStream`, mock OM/datanode classes, `OzoneClientConfig`, and hsync flags. It is an important signal for `MockDatanodeStorage.putBlockIncremental` and stream hsync semantics.

## Risks And Edge Cases
The read loop reuses `ByteBuffer` objects without explicit `clear`, relying on stream read behavior and full-buffer reads. The mock storage uses assertions for offset correctness. It does not test interrupted hsync, partial reads, or concurrent writes.

## Test Signals
The two parameterized methods cover incremental and non-incremental chunk list modes for small repeated hsyncs and large chunk-spanning hsyncs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestBlockOutputStreamIncrementalPutBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClient.java

## Purpose
`TestOzoneClient` is a network-free unit test suite for basic Ozone client operations over `RpcClient` using mock OM and datanode implementations.

## Important APIs, Types, And Functions
`init` creates a client with `SinglePipelineBlockAllocator`. `createNewClient` injects `MockOmTransport` and `MockXceiverClientFactory` into an anonymous `RpcClient`. `expectOmException` asserts OM exception result codes. Tests cover volume deletion, volume metadata/quota defaults, bucket creation timestamps, RATIS one-node key writes and reads, multi-write block allocation, and EC replication config writes with validation disabled and multi-node allocator.

## Control Flow
Tests create randomized volume/bucket/key names, execute public client APIs, then assert returned metadata, readback content, or expected exceptions. The EC test closes the default client, creates a special configuration with small block size and disabled replication validation, uses `MultiNodePipelineBlockAllocator`, writes EC keys, and verifies key metadata.

## State And Persistence Behavior
The test owns one `OzoneClient` and `ObjectStore` per test lifecycle. Persistent behavior is modeled by `MockOmTransport` maps and `MockDatanodeStorage`. Client close runs after each test.

## Dependencies And Integration Points
The suite exercises `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `RpcClient`, replication configs, mock allocators, and mock xceiver factory. It validates the public client facade against the mock protocol layer.

## Risks And Edge Cases
The mock OM omits many production validations and service metadata. The test writes strings created from zero byte arrays for allocation coverage, so content semantics are less meaningful there. EC validation is disabled intentionally to focus on client IO path rather than config policy.

## Test Signals
Provides broad smoke coverage for create/delete volume, create bucket, write/read key, block allocation on repeated writes, and EC key creation through the production `RpcClient` stream-building path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClientUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClientUtils.java

## Purpose
`TestOzoneClientUtils` verifies client-side utility behavior for file checksums and replication config resolution.

## Important APIs, Types, And Functions
The checksum tests call `OzoneClientUtils.getFileChecksumWithCombineMode` with negative length and empty key name. Replication tests cover `resolveClientSideReplicationConfig` with EC bucket defaults, null bucket defaults, invalid filesystem replication, non-EC defaults, configured client replication, and valid/invalid user-provided type/replication combinations through `validateAndGetClientReplicationConfig`.

## Control Flow
Each test constructs replication configs or mocks volume/bucket/protocol objects, calls the utility method under a specific combination, and asserts the expected config, null result, or exception.

## State And Persistence Behavior
The class has no persistent state. It has reusable replication config fields for EC, RATIS THREE, and RATIS ONE.

## Dependencies And Integration Points
It depends on `OzoneClientUtils`, `OzoneClientConfig.ChecksumCombineMode`, Hadoop `FileChecksum`, Ozone replication config types, `OzoneConfiguration`, and Mockito mocks for client protocol objects.

## Risks And Edge Cases
The tests assert intended null-return semantics for invalid or incomplete client-side replication inputs; changing utility behavior to throw instead would require updating callers. The checksum tests only cover input validation/empty key behavior, not successful checksum computation.

## Test Signals
Strong coverage for precedence rules: EC bucket defaults override client-side replication; valid filesystem replication can override non-EC bucket defaults; invalid or incomplete user/config inputs return null so OM can decide.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneClientUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneECClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneECClient.java

## Purpose
`TestOzoneECClient` is a comprehensive network-free suite for EC write/read behavior through the real Ozone client stream stack with mock OM and datanodes. It targets data/parity layout, bucket default EC config, partial stripes, block group metadata, retry behavior, exclusion rules, and preallocated block handling.

## Important APIs, Types, And Functions
Fixture fields define a 3 data / 2 parity EC layout with 1024-byte chunks, reusable input chunks, `MockXceiverClientFactory`, `MultiNodePipelineBlockAllocator`, `MockOmTransport`, and a raw RS encoder. `createNewClient` injects mocks into `RpcClient`. `writeIntoECKey` overloads create volume/bucket/key and write byte arrays with optional bucket default replication config. `validateContent`, `getMatchingStorage`, `getAllLocationInfoList`, and `waitForFlushingThreadToFinish` support assertions.

Tests cover data-node stored data, parity data matching the RS encoder, readback content, default bucket EC replication, single-write calls containing many chunks and offsets, chunks smaller than chunk size, block group length metadata in put-block, committed key info ordering and data size, several partial-stripe cases, 10+4 EC partial stripe overflow regression coverage, node failure behavior, stripe-write retries, failed/closed datanode exclude list contents, large writes with mid-stream failures, partial chunk retry on close, and preallocated-block discard preventing retry exhaustion.

## Control Flow
Most tests create a bucket, write EC data through `bucket.createKey`, close the stream, then inspect mock datanode storage, mock OM committed key metadata, or read content back. Failure tests write an initial stripe, wait for the flush thread to pass a checkpoint, inject datanode failures through `MockXceiverClientFactory`, continue writing, and then assert block group counts and content. Retry-specific tests configure max retry counts or cluster sizes to assert success, `IOException`, or `IllegalStateException`.

## State And Persistence Behavior
State is shared across each test instance fields but reset by JUnit lifecycle and client close. Mock OM stores volumes, buckets, open keys, and committed keys. Mock datanode storages store per-node bytes and block metadata. The allocator's sliding cursor determines which mock nodes receive successive block groups.

## Dependencies And Integration Points
The suite integrates `RpcClient`, `ECKeyOutputStream`, `OzoneOutputStream`, `OzoneInputStream`, `OzoneBucket`, EC replication configs, raw erasure encoder, mock OM/datanode layers, stream internals such as `BlockOutputStreamEntry` and `BlockStreamAccessor`, and client config keys such as block size and max EC stripe write retries.

## Risks And Edge Cases
The tests rely on deterministic ordering of `DatanodeDetails` and allocator nodes. They inspect stream internals and mock storage internals, so refactors can break tests without changing public behavior. Some key sizes passed to `createKey` are approximate or smaller than actual written content in retry/partial tests, reflecting current stream behavior rather than strict declared-size enforcement. Failure modeling is narrower than production because writes fail at mock storage and networking/pipeline state is simplified.

## Test Signals
This is the strongest signal in the subset for EC client correctness. It verifies data and parity bytes, EOF behavior, partial stripe padding, block group length metadata, key-location ordering, retry limits, exclude-list policy distinguishing failed vs closed containers, and correct reads after reallocation to new block groups.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneECClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneSnapshot.java

## Purpose
`TestOzoneSnapshot` verifies conversion from OM `SnapshotInfo` helper objects to public `OzoneSnapshot` DTOs.

## Important APIs, Types, And Functions
`getMockedSnapshotInfo` builds a Mockito `SnapshotInfo` with volume, bucket, name, creation time, status, UUID, path, checkpoint directory, referenced sizes, exclusive sizes, and deep-cleaning deltas. `testOzoneSnapshotFromSnapshotInfo` calls `OzoneSnapshot.fromSnapshotInfo` and compares it to an expected `OzoneSnapshot`.

## Control Flow
The test prepares a mocked `SnapshotInfo`, converts it, constructs the expected DTO, and uses `assertEquals`.

## State And Persistence Behavior
No persistent state is used; all data is in mocks and local values.

## Dependencies And Integration Points
It depends on `SnapshotInfo`, `OzoneSnapshot`, Mockito, JUnit, and `SNAPSHOT_ACTIVE`. It validates client-facing snapshot metadata mapping that `RpcClient.getSnapshotInfo` returns through `OzoneSnapshot.fromSnapshotInfo`.

## Risks And Edge Cases
The expected exclusive sizes include base exclusive size plus deep-cleaning deltas, so mapping changes in `OzoneSnapshot` must preserve that semantic or update this test. It does not cover null fields, inactive/deleted statuses, or multiple checkpoint versions.

## Test Signals
Provides direct DTO conversion coverage for snapshot size and identity fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestOzoneSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestFileChecksumHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestFileChecksumHelper.java

## Purpose
`TestFileChecksumHelper` verifies replicated and EC file checksum helper behavior, including empty block handling, one-block checksum fetches, cached checksum usage, and checksum computation after writing a real key through the mock client stack.

## Important APIs, Types, And Functions
`init` creates an `OzoneClient` with CRC32C checksum config, `MockOmTransport`, and `MockXceiverClientFactory`. `omKeyInfo` builds synthetic `OmKeyInfo` with RATIS or EC replication and optional cached checksum. `checksumHelper` selects `ReplicatedFileChecksumHelper` or `ECFileChecksumHelper`. `pipeline` builds a closed pipeline. `testEmptyBlock` and `testOneBlock` run for EC and RATIS. `buildValidResponse` creates a mocked datanode `GetBlock` response with chunk checksum data and EC stripe checksum when needed. `testPutKeyChecksum` writes a real key and computes its replicated checksum.

## Control Flow
For synthetic tests, Mockito supplies OM lookup results and xceiver responses. Helpers call `compute`, then tests inspect `getFileChecksum` and `getKeyLocationInfoList`. The real-key test writes data through `bucket.createKey`, constructs `ReplicatedFileChecksumHelper`, computes, and asserts CRC type and location count.

## State And Persistence Behavior
Synthetic tests have mocked state only. The real-key test persists volume/bucket/key metadata in `MockOmTransport` and chunk/block data in `MockDatanodeStorage`. Client state is closed after each test.

## Dependencies And Integration Points
It integrates checksum helper classes with `RpcClient`, `OzoneManagerProtocol`, `XceiverClientFactory`, `XceiverClientGrpc`, OM key-location metadata, datanode block checksum protobufs, and Hadoop checksum classes `MD5MD5CRC32FileChecksum` and `MD5MD5CRC32GzipFileChecksum`.

## Risks And Edge Cases
`buildValidResponse` uses artificial checksum bytes and does not validate against real data content. Empty-block tests expect MD5MD5CRC32 gzip checksum and null location list for negative length; changing helper semantics affects these assertions. The EC path depends on stripe checksum presence in chunk info.

## Test Signals
The parameterized tests cover both RATIS and EC helper selection. They assert empty-block checksum type, one-block location discovery, cached checksum handling, and real mock-stack checksum behavior with CRC32C.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestFileChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestReplicatedBlockChecksumComputer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestReplicatedBlockChecksumComputer.java

## Purpose
`TestReplicatedBlockChecksumComputer` verifies block-level checksum combination for replicated blocks in MD5-of-CRC mode and composite CRC mode.

## Important APIs, Types, And Functions
`testComputeMd5Crc` creates random chunk checksum bytes, computes the expected `MD5Hash.digest`, runs `ReplicatedBlockChecksumComputer.compute(MD5MD5CRC)`, and asserts output bytes. `testComputeCompositeCrc` uses `CrcComposer` to compute expected composite CRC32C output, runs `compute(COMPOSITE_CRC)`, and asserts output bytes. `buildBlockChecksumComputer` creates a single `ChunkInfo` with `ChecksumData` and returns a `ReplicatedBlockChecksumComputer`.

## Control Flow
Each test builds deterministic expected output from the same random checksum input, constructs a one-chunk block checksum computer, calls `compute`, and compares the resulting output buffer.

## State And Persistence Behavior
No persistent state is used. All data is local to the test method.

## Dependencies And Integration Points
It depends on `ReplicatedBlockChecksumComputer`, `AbstractBlockChecksumComputer`, `CrcComposer`, `CrcUtil`, Hadoop `MD5Hash` and `DataChecksum`, protobuf `ByteString`, and datanode checksum protobufs.

## Risks And Edge Cases
The tests cover a single chunk only. Multi-chunk composition, mixed checksum types, and invalid checksum lengths are not covered here. Random input is secure-random, but expected and actual derive from the same bytes, so the tests should remain deterministic in outcome.

## Test Signals
Validates the two primary replicated block checksum combine modes at the unit level.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestReplicatedBlockChecksumComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ozone.client.checksum` test classes for Ozone Client checksum APIs.

## Important APIs, Types, And Functions
It provides only package-level Javadoc and the package declaration.

## Control Flow
There is no executable control flow.

## State And Persistence Behavior
There is no state or persistence behavior.

## Dependencies And Integration Points
The declaration groups checksum tests such as `TestFileChecksumHelper` and `TestReplicatedBlockChecksumComputer` under the checksum test package.

## Risks And Edge Cases
Only documentation drift is relevant if the package contents change.

## Test Signals
Compilation validates the descriptor. Checksum behavior is tested in the sibling test classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->
