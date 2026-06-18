<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocal.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocal.java

Purpose: Large regression suite for modern short-circuit local block reads. It verifies `BlockReaderLocal` behavior across checksum validation, readahead sizes, direct and heap `ByteBuffer` reads, skip/read boundary behavior, corrupt block detection, mlock anchor state changes, NULL checksum files, zero-byte reads, multiple short-circuit cache slots, local read statistics, and erasure-coded read statistics.

Important APIs/types/functions: `runBlockReaderLocalTest` is the central harness. It starts a one-DataNode `MiniDFSCluster`, writes deterministic data with `DFSTestUtil`, opens block and metadata files directly, creates `ShortCircuitCache`, `ShortCircuitShm`, and `ShortCircuitReplica`, then builds `BlockReaderLocal` with `DfsClientConf.ShortCircuitConf`. Nested `BlockReaderLocalTest` subclasses implement specific read scenarios. `readFully`, `assertArrayRegionsEqual`, `forceAnchorable`, `forceUnanchorable`, `getMaxReadaheadLength`, `getVerifyChecksum`, and `ReadStatistics` are key signals.

Control flow: `@BeforeAll` creates a temporary domain socket directory and disables path validation. Each parameterized-style test calls the harness with checksum on/off, readahead default/short/zero, or short-circuit cache counts. The harness writes and reads the whole source file once, then iterates block-local file pairs, injecting corruption or config changes before invoking the nested test. Statistics tests use higher-level `HdfsDataInputStream`; EC statistics create separate EC and non-EC files and stop a DataNode to force decode.

State and persistence behavior: The tests create real HDFS block files, metadata files, short-circuit shared memory slots, and a temporary socket-backed file. They assert that local reads do not advance underlying file-channel positions. Corruption tests mutate the block file on disk. EC tests persist erasure coding policy on a directory and observe accumulated stream statistics.

Dependencies and integration points: Depends on `MiniDFSCluster`, domain socket support, short-circuit cache/shm classes, `DFSTestUtil`, `ClientContext`, `HdfsClientConfigKeys`, `DFSInputStream.tcpReadsDisabledForTesting`, and `StripedFileTestUtil`. It integrates client-side local block reading with DataNode-created block files and HDFS read-stat accounting.

Risks: Domain socket native loading gates many tests through assumptions. The harness touches low-level file descriptors and shared memory, so cleanup is important. Corrupting block files can produce different failure modes if checksum configuration changes. Multi-cache tests depend on file length and block size matching at least five blocks. EC statistics require enough DataNodes and may be timing-sensitive for decode-time counters.

Test signals: Passing tests mean `BlockReaderLocal` returns exact bytes for array and buffer reads, detects checksum corruption only when verification is enabled, handles zero-length reads at EOF consistently, maintains underlying file positions, records local and short-circuit read stats, reports EC block type and decode time, and enforces short-circuit cache count bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java

Purpose: Regression tests for the legacy short-circuit local block reader path and legacy DataNode local path RPC behavior.

Important APIs/types/functions: `getConfiguration` enables short-circuit reads, legacy `BlockReaderLocal`, block-local-path access user, disabled domain socket data traffic, and short retry windows. Tests use `DFSInputStream.tcpReadsDisabledForTesting`, `MiniDFSCluster`, `ClientDatanodeProtocol.getBlockLocalPathInfo`, `DFSUtilClient.createClientDatanodeProtocolProxy`, and `BlockLocalPathInfo`.

Control flow: `setupCluster` globally disables TCP reads for testing and domain socket path validation. `testStablePositionAfterCorruptRead` corrupts the only replica and verifies failed direct-buffer reads leave `position` and `limit` unchanged. `testBothOldAndNewShortCircuitConfigured` enables legacy and short-circuit settings together, closes the socket directory, and confirms reads still succeed. `testBlockReaderLocalLegacyWithAppend` captures a block generation stamp, appends one byte, then verifies local path info returns the new generation stamp for the original block handle.

State and persistence behavior: Creates temporary NameNode/DataNode storage, HDFS files, corrupted replicas, and appended block state. The append test persists a new generation stamp and validates that the DataNode resolves current metadata rather than stale client state.

Dependencies and integration points: Integrates `DistributedFileSystem`, NameNode block-location RPCs, DataNode client protocol, block tokens, and legacy local path access configuration.

Risks: Global `tcpReadsDisabledForTesting` is not reset here and can affect co-located tests if the test framework reuses JVM state. Native domain socket availability controls part of coverage. The socket-directory-close scenario is intentionally brittle and validates fallback semantics.

Test signals: Passing tests indicate legacy local reads preserve buffer state on checksum exceptions, coexist with newer short-circuit configuration, and expose up-to-date block generation stamps after append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java

Purpose: Tests `BlockReaderLocalMetrics` and `BlockReaderIoProvider` latency recording for short-circuit local file-channel reads.

Important APIs/types/functions: Uses `BlockReaderLocalMetrics.create`, `getShortCircuitReadRollingAverages`, `MetricsTestHelper.replaceRollingAveragesScheduler`, `BlockReaderIoProvider.read`, `FakeTimer`, Hadoop metrics assertions, and Mockito `FileChannel.read`.

Control flow: Each test creates a metrics instance, replaces the rolling average scheduler with short test windows, mocks one or more `FileChannel` reads to advance a fake timer, performs reads through `BlockReaderIoProvider`, waits until thread-local metric state is collected, then reads the `HdfsShortCircuitReads` metrics record and checks `[ShortCircuitLocalReads]RollingAvgLatencyMs`.

State and persistence behavior: Metrics are in-process Hadoop Metrics2 state with rolling average windows and thread-local samples. No filesystem state is persisted. The static `FakeTimer` advances monotonically across tests, which is acceptable because assertions compare deltas recorded by the provider.

Dependencies and integration points: Covers the client metrics path between short-circuit read IO, thread-local metric collection, rolling averages, and Metrics2 publication.

Risks: Random delays in `testSlowShortCircuitReadsAverageLatencyValue` can include zero-delay samples, making assertions intentionally lower-bound rather than exact. Async metrics collection requires `GenericTestUtils.waitFor`, so scheduler timing can affect flakiness.

Test signals: Passing tests indicate slow short-circuit reads are sampled, multiple providers contribute to the same rolling average, and the published latency is at least the expected average delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderRemote.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderRemote.java

Purpose: Focused test for remote block reader skip semantics over a real MiniDFS-backed block.

Important APIs/types/functions: `BlockReaderTestUtil`, `BlockReader`, `DistributedFileSystem`, `LocatedBlock`, `getBlockReader`, and `BlockReader.skip/read`.

Control flow: `setup` creates a one-DataNode test cluster, writes a 4 MiB deterministic file, fetches the first located block, and creates a `BlockReader`. `testSkip` repeatedly skips 1 to 100 bytes, reads one byte when not at EOF, and checks the byte against the original data. `shutdown` closes the utility cluster.

State and persistence behavior: Persists one HDFS file and reads its first block remotely. Reader position advances through alternating skip/read operations until EOF.

Dependencies and integration points: Exercises client remote block-reader logic, DataTransferProtocol-backed block reads, `BlockReaderTestUtil`, and DataNode serving of located block ranges.

Risks: Random skip pattern is not seeded, so exact iteration paths differ across runs, though coverage remains bounded by deterministic data. The test only covers one reader and one block.

Test signals: Passing indicates `BlockReaderRemote.skip` returns correct counts near EOF and positions subsequent reads at the expected byte.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderRemote.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java

Purpose: Verifies when `BlockReaderRemote` sends `Status.CHECKSUM_OK` back to the DataNode after client reads.

Important APIs/types/functions: Static `BlockReaderTestUtil`, Mockito `spy`/`verify`, `BlockReaderRemote.sendReadResult`, `Status.CHECKSUM_OK`, and `readAndCheckEOS`.

Control flow: `setupCluster` writes a 256 KiB file and stores the first `LocatedBlock`. Tests open spied remote readers for full-block, incomplete, partial-range, and unaligned-range reads. Full completion of the requested range must call `sendReadResult(CHECKSUM_OK)`; incomplete reads must not.

State and persistence behavior: Uses a shared MiniDFS cluster and file for all tests. The persistent signal is not filesystem mutation but the reader-to-DataNode verification message.

Dependencies and integration points: Integrates DFS client block reading, DataTransferProtocol checksum verification, and DataNode read-result signaling.

Risks: Mockito spies couple the test to `BlockReaderRemote` internals. The shared static cluster means setup failure affects every test.

Test signals: Passing indicates checksum success is acknowledged exactly when the requested byte range is fully consumed, including unaligned checksum-boundary ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java

Purpose: Adapts the generic `CryptoStreamsTestBase` suite to HDFS-backed streams.

Important APIs/types/functions: Extends `CryptoStreamsTestBase`; overrides `getOutputStream` and `getInputStream` to return `CryptoFSDataOutputStream` and `CryptoFSDataInputStream` wrapping `fs.create` and `fs.open`. Uses `CryptoCodec.getInstance`, `MiniDFSCluster`, `FileSystem.mkdirs`, and `FsPermission`.

Control flow: `init` starts a MiniDFS cluster and initializes the shared crypto codec. Each test method inherited from the base class gets a unique directory and file path in `setUp`, then base tests exercise crypto stream read/write behavior. `cleanUp` deletes the per-test directory, and `shutdown` stops the cluster.

State and persistence behavior: Persists encrypted stream bytes in HDFS files under unique `/pN/file` paths and deletes them after each test.

Dependencies and integration points: Connects Hadoop crypto stream wrappers to HDFS `FSDataInputStream`/`FSDataOutputStream` implementations, verifying the generic crypto contract over distributed storage.

Risks: Actual test methods are inherited, so failures may be reported from the base class. The test depends on a configured crypto codec being available for the current Hadoop configuration.

Test signals: Passing inherited tests indicate HDFS-backed crypto streams honor base stream semantics for buffering, encryption/decryption, position, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java

Purpose: Correctness suite for `DFSNetworkTopology`, especially storage-type-aware counts and random selection with scopes and exclusions.

Important APIs/types/functions: Uses static `DFSNetworkTopology CLUSTER`, `DFSTopologyNodeImpl.getChildrenStorageInfo`, `getSubtreeStorageCount`, `chooseRandomWithStorageType`, `chooseRandomWithStorageTypeTwoTrial`, `DatanodeDescriptor`, `DatanodeInfoBuilder`, `DatanodeStorageInfo`, and `StorageType`.

Control flow: `setupDatanodes` builds 25 datanodes across a multi-level topology with varied storage types, adds them to the cluster, and decommissions two nodes. Tests assert child storage maps at multiple levels, add and remove five nodes and verify counts, repeatedly select nodes for desired storage types, exercise excluded node sets and excluded scopes, verify wrapper `"~"` excluded-scope behavior, handle nonexistent scopes, and cover edge cases involving `DatanodeInfo` rather than `DatanodeDescriptor` in exclusions.

State and persistence behavior: In-memory topology is mutated by adding/removing nodes and setting decommission state. There is no disk persistence. Because `CLUSTER` is static and `setupDatanodes` adds nodes before each test, behavior depends on `DFSNetworkTopology.add` being idempotent for existing node identity or tests would accumulate state.

Dependencies and integration points: Covers HDFS block-placement support code, Hadoop network topology abstractions, storage media counts, and DataNode descriptor identity/equality behavior.

Risks: Random selection is validated by membership over repeated trials, not exact distribution. Static cluster reuse can hide or amplify state leakage. Several tests depend on hard-coded host/rack mappings and comments must stay aligned with arrays.

Test signals: Passing indicates storage counts propagate correctly, node removals decrement ancestor counts, storage-type selection respects desired scope, excluded scope, and excluded nodes, and null/nonexistent cases are safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java

Purpose: Disabled benchmark-style comparison between generic `NetworkTopology.chooseRandom` with retry filtering and `DFSNetworkTopology.chooseRandomWithStorageType`.

Important APIs/types/functions: `NetworkTopology`, `DFSNetworkTopology`, `DFSTestUtil.createDatanodeStorageInfos`, `DatanodeDescriptor.hasStorageType`, `addNodeByTypes`, `getRandLocation`, `getRandType`, `printMemUsage`, and constants `NODE_NUM=2000`, `OP_NUM=20000`.

Control flow: `init` precomputes random racks and hosts. Each disabled test creates both topology implementations, fills the `types` array with a distribution, adds identical nodes to both clusters, sleeps for measurement stability, then times old retry-based selection and/or direct storage-aware selection. Scenarios cover uniform types, unbalanced archive minority, all same type, configurable percentage, and a mixed first-generic-then-storage-aware approach.

State and persistence behavior: All state is synthetic and in-memory. Timing samples are stored in `records`; memory usage is logged through `Runtime`.

Dependencies and integration points: Used as exploratory performance evidence for HDFS storage-type-aware placement. It is not a CI correctness gate because the class is annotated `@Disabled`.

Risks: Random topology and type distribution make numbers non-reproducible unless seeded externally. Assertions only guard non-null/type correctness during benchmarking. Sleep and JVM memory logging are approximate.

Test signals: When manually enabled, log output showing total time, average time, average trials, and memory usage is the useful signal. Normal CI should skip it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/net/TestDFSNetworkTopologyPerformance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java

Purpose: Ensures every public method exposed through `NamenodeProtocols` has retry semantics annotations.

Important APIs/types/functions: Reflection over `NamenodeProtocols.class.getMethods`, `Idempotent`, and `AtMostOnce`.

Control flow: Single test iterates all public protocol methods and asserts each has either `@Idempotent` or `@AtMostOnce`.

State and persistence behavior: No mutable state or persistence. It is a static API contract check.

Dependencies and integration points: Guards NameNode RPC protocol declarations used by Hadoop IPC retry handling.

Risks: Reflection includes inherited public methods from the protocol aggregate, so newly added public methods must be annotated immediately. The test does not validate annotation correctness, only presence.

Test signals: Passing means protocol retry metadata is complete for all public NameNode protocol methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestAnnotations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestBlockListAsLongs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestBlockListAsLongs.java

Purpose: Tests block report encoding/decoding in `BlockListAsLongs`, including old long-list format, new protobuf byte-buffer format, replica states, fuzzed large reports, and DataNode capability negotiation.

Important APIs/types/functions: `BlockListAsLongs.encode`, `decodeBuffers`, `decodeLongs`, `getBlockListAsLongs`, `getBlocksBuffers`, `BlockReportReplica`, `FinalizedReplica`, `ReplicaBeingWritten`, `ReplicaWaitingToBeRecovered`, `NamespaceInfo.Capability.STORAGE_BLOCK_REPORT_BUFFERS`, and `DatanodeProtocolClientSideTranslatorPB.blockReport`.

Control flow: Simple tests assert exact long-array layout for empty, finalized, under-construction, and mixed reports. `checkReport` encodes replicas, decodes via both buffer and long paths, and validates every replica by block id, length, generation stamp, and state. `testFuzz` validates 100000 random finalized/RBW replicas. `testDatanodeDetect` captures outgoing block report protobufs from a mocked PB proxy and verifies capability-dependent new-style or old-style report fields.

State and persistence behavior: All state is in-memory block and replica metadata. The DataNode protocol test mutates `NamespaceInfo` capability masks to simulate server compatibility.

Dependencies and integration points: Guards DataNode-to-NameNode block report serialization, protobuf translators, storage reports, and compatibility with older NameNode capability sets.

Risks: `testFuzz` switch currently uses `rand.nextInt(2)`, so the `ReplicaWaitingToBeRecovered` case in that fuzz path is unreachable, though mixed tests cover it. Exact long-array assertions are sensitive to intentional wire-format changes.

Test signals: Passing means both block report formats round-trip correctly and DataNodes select the expected report representation from namespace capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestBlockListAsLongs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java

Purpose: Validates layout-version feature inheritance, reserved release compatibility, NameNode/DataNode feature ordering, and minimum compatible layout-version policy.

Important APIs/types/functions: `LayoutVersion.Feature`, `FeatureInfo`, `LayoutFeature`, `NameNodeLayoutVersion`, `DataNodeLayoutVersion`, `LayoutVersion.updateMap`, `getMinimumCompatibleLayoutVersion`, and Mockito-created invalid `LayoutFeature`.

Control flow: Tests iterate common and NameNode feature enums to ensure every feature supports its ancestor set. Specific release tests assert reserved release versions support delegation tokens or concat. NameNode/DataNode first feature tests ensure feature-specific enums inherit all non-reserved common features. Minimum-compatible tests check the truncate-era compatibility group, require descending enum order by minimum compatible layout version, assert out-of-order updates fail fast, and pin the current minimum compatible layout version. `testSNAPSHOT` enforces that snapshot support implies fsimage name optimization support.

State and persistence behavior: No runtime persistence. The file guards serialized filesystem image/edit-log compatibility metadata embedded in enums.

Dependencies and integration points: Directly protects rolling upgrade, downgrade, fsimage, and edit-log layout compatibility contracts for NameNode and DataNode code.

Risks: Intentional compatibility-breaking changes must update pinned expectations. Enum ordering is semantic here, so refactors can fail tests even without behavior changes.

Test signals: Passing indicates layout feature ancestry and minimum-compatible version rules remain coherent and downgrade policy has not changed accidentally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java

Purpose: Verifies `LocatedBlock.addCachedLoc` rejects cached locations when the block has no storage locations.

Important APIs/types/functions: `LocatedBlock`, `ExtendedBlock`, `DatanodeInfo.EMPTY_ARRAY`, `DatanodeDescriptor`, and `DatanodeID`.

Control flow: Single test constructs a `LocatedBlock` with an empty location array, creates a `DatanodeDescriptor`, calls `addCachedLoc`, and expects `IllegalArgumentException`.

State and persistence behavior: In-memory protocol object only.

Dependencies and integration points: Guards client/protocol block-location invariants used by cache reporting and block metadata propagation.

Risks: The test uses manual try/fail rather than `assertThrows`, but behavior is clear. It only covers the empty-location error path.

Test signals: Passing means cached locations cannot be attached to a `LocatedBlock` lacking base datanode locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/TestLocatedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java

Purpose: Tests `PacketReceiver` packet sizing, parsing of checksum/data slices, and one-call packet mirroring.

Important APIs/types/functions: `PacketHeader`, `PacketReceiver.receiveNextPacket`, `getDataSlice`, `getChecksumSlice`, `getHeader`, `mirrorPacketTo`, `MAX_PACKET_SIZE`, and `HdfsClientConfigKeys.DFS_DATA_TRANSFER_MAX_PACKET_SIZE_DEFAULT`.

Control flow: `prepareFakePacket` writes a header, checksum bytes, and data bytes into a byte array. `testPacketSize` pins max-packet default alignment. `testReceiveAndMirror` reuses one receiver for packets of different sizes to force buffer reallocation, then `doTestReceiveAndMirror` validates parsed slices, header fields, and mirrored output bytes. Mockito verifies mirroring writes the full packet in one `OutputStream.write` call.

State and persistence behavior: In-memory byte buffers only. The receiver internally resizes and reuses buffers across packet sizes.

Dependencies and integration points: Guards DataTransferProtocol packet parsing and forwarding, relevant for DataNode pipeline mirroring and TCP/Nagle interaction avoidance.

Risks: The one-write assertion couples implementation to performance behavior. Packet construction must stay in sync with `PacketHeader` layout.

Test signals: Passing means packet slices match original payloads, header metadata is preserved, and mirror output is byte-identical with a single write call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/TestPacketReceiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java

Purpose: Shared fixture for SASL data-transfer tests that need Kerberos principals, keytabs, and HTTPS-only secure HDFS configuration.

Important APIs/types/functions: `MiniKdc`, `KeyStoreTestUtil`, `SecurityUtil.setAuthenticationMethod`, `createSecureConfig`, and getters for generated user/HDFS keytabs and principals.

Control flow: `initKdc` creates a test directory, starts MiniKdc, generates a random user principal and an `hdfs/localhost` plus `HTTP/localhost` principal, and stores keytab paths. `shutdownKdc` stops KDC, deletes base directory, and cleans SSL config. `createSecureConfig` sets Kerberos auth, NameNode/DataNode principals and keytabs, SPNEGO principal, block tokens, requested data transfer QOPs, HTTPS-only policy, ephemeral HTTPS addresses, SASL retry count, and SSL resources.

State and persistence behavior: Persists temporary keytab files, KDC state, and generated SSL config under test directories, then deletes them at suite end.

Dependencies and integration points: Used by SASL data-transfer integration tests to start secure `MiniDFSCluster` instances with realistic Kerberos and SSL settings.

Risks: Class-level static directories and SSL paths are shared by subclasses. Cleanup must run or credentials/config files can remain. MiniKdc startup can be environment-sensitive.

Test signals: Subclass success indicates this fixture produced valid principals, keytabs, SSL resources, and HDFS security configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java

Purpose: Tests blacklist-file behavior for `BlackListBasedTrustedChannelResolver` on client and server trust decisions.

Important APIs/types/functions: `BlackListBasedTrustedChannelResolver`, client/server fixed blacklist config keys, `isTrusted()`, `isTrusted(InetAddress)`, Apache `FileUtils`, and `GenericTestUtils.getTestDir`.

Control flow: `setup` writes a temporary blacklist file containing two IPs and creates a resolver. Client test appends the local host address, sets the client blacklist path, and expects the current channel to be untrusted. Server test sets the server blacklist path, verifies default local trust, and verifies a listed remote address is untrusted. `cleanUp` deletes the file.

State and persistence behavior: Persists a temporary text blacklist file under the test directory.

Dependencies and integration points: Covers data-transfer SASL trust-bypass decisions driven by fixed IP blacklist files.

Risks: Client test depends on resolving `InetAddress.getLocalHost().getHostAddress()` and matching resolver behavior. File append uses platform default charset through `FileUtils`.

Test signals: Passing means configured blacklist files are loaded and trusted-channel decisions change for listed client/server addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java

Purpose: Verifies SASL server callback handling can delegate unsupported callbacks to configured custom handlers or handler methods.

Important APIs/types/functions: `CustomizedCallbackHandler`, `CustomizedCallbackHandler.Cache`, `SaslDataTransferServer.SaslServerCallbackHandler`, `SaslRpcServer.SaslDigestCallbackHandler`, `HADOOP_SECURITY_SASL_CUSTOMIZEDCALLBACKHANDLER_CLASS_KEY`, and `LambdaTestUtils.intercept`.

Control flow: Static helpers reset callback state and assert exact callback object identity. `testCustomizedCallbackHandler` first verifies no handler causes `UnsupportedCallbackException`, then configures a class implementing `CustomizedCallbackHandler` and confirms callbacks are delegated for both data-transfer and RPC digest handlers. `testCustomizedCallbackMethod` configures plain objects with a reflective `handleCallbacks` method and verifies success and wrapped failure behavior.

State and persistence behavior: Uses static `AtomicReference<List<Callback>>` and clears the callback-handler cache between scenarios. No filesystem state.

Dependencies and integration points: Guards Hadoop security extensibility used by SASL data transfer and RPC callback stacks.

Risks: Relies on reflection/cache behavior and exact object identity. Exceptions from custom methods are observed as `IOException` in the data-transfer wrapper.

Test signals: Passing means custom callback classes and callback-method objects are discovered, cached, invoked, and failure-propagated as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestCustomizedCallbackHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java

Purpose: End-to-end and unit-level coverage for SASL-protected HDFS DataTransferProtocol operation.

Important APIs/types/functions: Inherits `createSecureConfig`; uses `MiniDFSCluster`, `DFS_DATA_TRANSFER_PROTECTION_KEY`, `DFS_HTTP_POLICY_KEY`, `IGNORE_SECURE_PORTS_FOR_TESTING_KEY`, `SaslDataTransferClient`, `DataTransferSaslUtil`, `TrustedChannelResolver`, `DataEncryptionKeyFactory`, `DFSUtilClient.peerFromSocketAndKey`, and `DataNode` logs.

Control flow: QOP tests start a secure three-DataNode cluster, set client QOP to authentication/integrity/privacy, write/read a multi-block file, and verify block locations. Negative tests cover no common QOP, server SASL with no client SASL, DataNode abort when SASL is disabled under secure ports, HTTP policy rejection, HTTPS privacy acceptance, and secure-port ignore testing. Socket tests validate read timeout during SASL handshake and check trust combinations: partially trusted or untrusted channels must request an encryption key, fully trusted channels must not.

State and persistence behavior: Each test may start a MiniDFS cluster and create `/file1`. `shutdown` cleans `FileSystem` and cluster. Socket tests open local server/client sockets but do not accept full protocol handshakes.

Dependencies and integration points: Integrates Kerberos/SSL fixture, block tokens, DataTransferProtocol client/server negotiation, HTTP policy security checks, file IO, and trusted channel resolver logic.

Risks: Secure cluster startup is heavy and environment-sensitive. Some socket tests bind fixed port `10002`, which can conflict. Negative assertions inspect exception/log text.

Test signals: Passing indicates QOP negotiation works, insecure configurations are rejected, data reads succeed under all supported QOPs, timeouts are honored, and trust decisions correctly bypass or require SASL/encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java

Purpose: Verifies SASL data-transfer clients can recover from expired block tokens for normal sequential reads, positioned reads, and hedged positioned reads.

Important APIs/types/functions: `SecurityTestUtil.setBlockTokenLifetime`, `SecurityTestUtil.isBlockTokenExpired`, `DFSInputStream.getAllBlocks`, `FSDataInputStream.read`, positioned `read(long, byte[], int, int)`, `HedgedRead.THREADPOOL_SIZE_KEY`, and `Retry.WINDOW_BASE_KEY`.

Control flow: `before` creates random two-block data, starts a secure three-DataNode cluster, writes `/file1`, then shortens block token lifetime to one second. Each test opens a new client `FileSystem`, waits until cached block tokens in the wrapped `DFSInputStream` expire, then reads the full file through a different path: sequential `blockSeekTo`, positioned byte-range fetch, or hedged fetch. Read bytes are compared to original random data.

State and persistence behavior: Persists random file data in HDFS and mutates the NameNode block token secret manager lifetime. Each test shuts down its cluster.

Dependencies and integration points: Covers SASL data transfer, block-token renewal/retry paths, positioned reads, and hedged read client configuration.

Risks: Waiting for expiration polls every 100 ms and depends on token timestamp behavior. Setting `Retry.WINDOW_BASE_KEY` to `Integer.MAX_VALUE` in one client changes retry timing substantially.

Test signals: Passing means expired cached block tokens are refreshed or retried successfully without corrupting read results across all targeted read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestPBHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestPBHelper.java

Purpose: Broad conversion suite for `PBHelper` and `PBHelperClient`, ensuring HDFS protocol/server objects round-trip to protobuf representations and back.

Important APIs/types/functions: Covers conversions for `NamenodeRole`, `StorageInfo`, `NamenodeRegistration`, `DatanodeID`, `Block`, `BlockType`, `BlockWithLocations`, `ExportedBlockKeys`, `CheckpointSignature`, `RemoteEditLogManifest`, `ExtendedBlock`, `RecoveringBlock`, `BlockRecoveryCommand`, tokens, `NamespaceInfo`, `LocatedBlock`, `DatanodeRegistration`, `DatanodeStorage`, `BlockCommand`, checksum enums, ACLs, EC reconstruction commands, `DatanodeInfo`, slow peer/disk reports, `FsServerDefaults`, `AddErasureCodingPolicyResponse`, and `ErasureCodingPolicy`.

Control flow: Tests construct representative Java objects, convert to protobuf using helper methods, convert back, and compare fields. Helper comparison methods check nested arrays, tokens, storage IDs/types, EC policies, and datanode metrics. Backward-compatibility tests build protobufs missing newer optional fields, such as `keyProviderUri` or non-DFS usage, and verify defaulted conversion. EC policy tests distinguish built-in policies, where optional fields should be omitted, from custom policies, where name/schema/cell size must be present.

State and persistence behavior: Pure in-memory object/protobuf conversion. No external persistence.

Dependencies and integration points: Guards HDFS RPC wire compatibility across NameNode, DataNode, client, block management, ACL, erasure coding, and slow-node reporting protocols.

Risks: The file is large and mixes many protocol surfaces; a helper comparison bug can hide a conversion issue. Some comparisons appear suspicious, such as comparing located-block lists against a fixed index in one loop, so the suite should not be the only coverage for those conversions.

Test signals: Passing means current protobuf adapters preserve required fields, tolerate expected old-proto omissions, and reject malformed EC policy protos with missing required information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestPBHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java

Purpose: Test utility that starts and manages an in-process quorum of HDFS JournalNodes.

Important APIs/types/functions: `MiniJournalCluster.Builder`, `JNInfo`, `getQuorumJournalURI`, `start`, `shutdown`, `restartJournalNode`, `waitActive`, `setNamenodeSharedEditsConf`, and storage directory helpers. Uses `JournalNode`, `QuorumJournalManager`, `DFSConfigKeys`, and `DefaultMetricsSystem.setMiniClusterMode`.

Control flow: Builder validates optional fixed HTTP/RPC port arrays, resolves a base directory, optionally deletes per-node storage directories, creates each `JournalNode` with node-specific edits dir and ports, starts it, and records bound IPC/HTTP addresses. `waitActive` repeatedly creates a `QuorumJournalManager` against each node's config and calls `hasSomeData` until IPC responds. Restart stops a selected node, reuses bound addresses, and starts a new `JournalNode`.

State and persistence behavior: Persists JournalNode edits directories under `journalnode-N`, plus per-journal `current` and `previous` subdirectories. `format(true)` deletes existing node storage at construction. Shutdown stops nodes but does not delete storage.

Dependencies and integration points: Shared fixture for QJM tests and HA clusters, bridging NameNode shared edits config with JournalNode quorum URIs.

Risks: `start` can be called after constructor-started nodes and may double-start if callers misuse it. Fixed port arrays can conflict. `shutdown` aggregates failures and throws after attempting all stops.

Test signals: Consumers treat successful `waitActive`, correct quorum URI authority, restart success, and file existence in quorum storage as health signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniJournalCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java

Purpose: Test utility that composes a `MiniJournalCluster` with an HA `MiniDFSCluster` using QJM shared edits.

Important APIs/types/functions: `MiniQJMHACluster.Builder`, `createDefaultTopology`, `initHAConf`, `getDfsCluster`, `getJournalCluster`, and `shutdown`. Uses `MiniDFSNNTopology`, `NameNode.initializeSharedEdits`, `HATestUtil.setFailoverConfigurations`, and `ConfiguredFailoverProxyProvider`.

Control flow: Builder defaults to zero DataNodes and two NameNodes. Construction retries on `BindException`, selecting a random base port, starting three JournalNodes, setting their shared edits config, creating a NameNode topology, initializing HA configuration, starting MiniDFS once to format local namespace dirs, shutting down NameNodes, initializing shared edits, applying optional startup options, and restarting NameNodes.

State and persistence behavior: Persists JournalNode shared edits and MiniDFS NameNode storage under configured base directories. `forceRemoteEditsOnly` makes the QJM URI both edits dir and required edits dir.

Dependencies and integration points: Provides reusable HA/QJM integration setup for tests of failover, shared edits, and NameNode fencing.

Risks: Infinite retry loop on repeated bind conflicts has no explicit cap. Random port selection reduces but does not eliminate collisions. Shutdown assumes both cluster fields are initialized.

Test signals: A built instance with active NameNodes and active JournalNodes indicates HA configuration, shared edits initialization, and failover proxy settings are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/MiniQJMHACluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java

Purpose: Static helper library for QJM tests that need synthetic edit-log transactions, segment writing, quorum file checks, edit verification, and recovery assertions.

Important APIs/types/functions: `FAKE_NSINFO`, `JID`, `createTxnData`, `createGabageTxns`, `writeSegment`, `writeOp`, `writeTxns`, `verifyEdits`, `assertExistsInQuorum`, and `recoverAndReturnLastTxn`.

Control flow: Transaction data helpers serialize `FSEditLogOp` mkdir operations or garbage mkdir ops into byte arrays. `writeSegment` starts a QJM log segment, asserts the in-progress edits file exists in quorum, writes transactions, and optionally finalizes the segment. `verifyEdits` walks a list of `EditLogInputStream`s, advancing streams when one is exhausted, and asserts exact transaction ids and op codes. Recovery calls `recoverUnfinalizedSegments`, selects input streams, and returns the last recovered txid.

State and persistence behavior: Writes real edit-log segments through `QuorumJournalManager` and checks JournalNode storage directories in a quorum. Other helpers build in-memory serialized edit data.

Dependencies and integration points: Supports QJM client/server tests, `MiniJournalCluster`, NameNode edit-log operation classes, `NNStorage` file naming, and `NameNodeLayoutVersion`.

Risks: `assertExistsInQuorum` loops over exactly three nodes rather than `cluster.getNumNodes`, so it assumes the default cluster size. `createGabageTxns` typo is in API name and likely retained for compatibility.

Test signals: Passing consumers can rely on exact edit ranges, finalized/in-progress segment persistence, and recovery-visible transaction ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java

Purpose: Tests `MiniJournalCluster` startup, quorum URI generation, storage directory configuration, and fixed port validation/binding.

Important APIs/types/functions: `MiniJournalCluster.Builder`, `waitActive`, `getQuorumJournalURI`, `getJournalNode`, `setHttpPorts`, `setRpcPorts`, `NetUtils.getFreeSocketPorts`, and `LambdaTestUtils.intercept`.

Control flow: `testStartStop` starts a default three-node cluster, waits for activity, verifies quorum URI has three authorities, and checks node 0 edits dir under MiniDFS base directory. `testStartStopWithPorts` first asserts mismatched port-array sizes throw expected `IllegalArgumentException`s, then allocates six free ports, starts a cluster with three fixed HTTP and three fixed RPC ports, verifies bound ports match, and rechecks storage dir configuration.

State and persistence behavior: Creates JournalNode directories under MiniDFS base directory and starts real JournalNode RPC/HTTP services. Try-with-resources or finally shutdown stops services.

Dependencies and integration points: Validates the QJM fixture used by NameNode/QJM tests and the port-selection helper used for deterministic network bindings.

Risks: Free ports can be stolen between discovery and binding. The assertion message "should not be zero" has a double negative but checks the right value.

Test signals: Passing means default and fixed-port mini journal clusters start, become IPC-active, expose expected ports, and validate builder arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestMiniJournalCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java

Purpose: Integration tests for a NameNode using Quorum Journal Manager as its edits directory.

Important APIs/types/functions: `MiniJournalCluster`, `MiniDFSCluster`, `NameNode.format`, `ExitUtil`, `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `manageNameDfsDirs(false)`, and `RemoteException` fencing assertions.

Control flow: Each test starts JournalNodes in `startJNs` and stops them after. `testLogAndRestart` configures local image dir plus QJM edits dir, starts a zero-DataNode cluster, creates a directory, restarts the NameNode, verifies persistence, writes another directory, restarts again, and verifies both edits. `testNewNamenodeTakesOverWriter` formats one NN, copies its image dir to a second NN, starts the first, writes an edit, starts the second against the same quorum, verifies it sees the edit, then verifies the old NN is fenced when it tries to write. `testMismatchedNNIsRejected` formats QJM with one namespace, reformats only local storage, and expects restart against old JournalNodes to fail.

State and persistence behavior: Persists NameNode image directories, QJM edit logs, copied namespace state, and directory creation edits. It deliberately creates namespace mismatch and writer-fencing scenarios.

Dependencies and integration points: Exercises NameNode startup/restart, QJM shared edits, JournalNode namespace validation, edit persistence, and fencing semantics.

Risks: `testNewNamenodeTakesOverWriter` leaves `cluster.shutdown()` commented in `finally`, relying on process/test cleanup. Tests inspect exception text and use global `ExitUtil.disableSystemExit`.

Test signals: Passing means QJM edits survive restarts, a new NameNode can recover and take over the writer role, old writers are fenced, and mismatched local/QJM namespaces are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestNNWithQJM.java -->
