# subset-b-007521 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSCluster.java

## Purpose
`MiniDFSCluster` is the central in-process HDFS test harness. It builds one or more NameNodes plus a configurable set of DataNodes inside a single JVM, manages temporary name/data directories, exposes client handles, and offers fault-injection helpers used by many HDFS tests.

## Important APIs, Types, and Functions
- `MiniDFSCluster.Builder` is the primary API. It configures NameNode ports, DataNode counts, storage types/capacities, format/restart behavior, HA/federation topology, host/rack mappings, DN config overlays, fsync skipping, and address binding checks before calling `build()`.
- `DataNodeProperties` captures a stopped/restartable DN: `DataNode`, saved `Configuration`, startup args, secure resources, and IPC port.
- `NameNodeInfo` tracks each NN instance with its nameservice ID, NN ID, startup option, and NN-specific configuration.
- `initMiniDFSCluster(...)` is the constructor core: disables `System.exit`, enables symlinks, chooses base/data dirs, normalizes test config, formats/starts NameNodes, starts DataNodes, waits for activity, and refreshes proxy-user config.
- `configureNameNodes`, `configureNameService`, `initNameNodeConf`, `createNameNode`, and `copyNameDirs` translate `MiniDFSNNTopology` into HDFS config keys, shared edits directories, formatted storage, and live NameNode instances.
- `startDataNodes(...)` overloads create per-DN configs, storage directories, simulated datasets, static rack mappings, secure resources, and daemon threads.
- Lifecycle helpers include `shutdown`, `shutdownDataNodes`, `shutdownNameNode`, `restartNameNode`, `restartDataNode`, `restartDataNodes`, `waitClusterUp`, `waitActive`, and `waitFirstBRCompleted`.
- Fault helpers include `corruptBlockOnDataNodes`, `corruptBlockOnDataNodesByDeletingBlockFile`, `corruptReplica`, `corruptMeta`, `deleteMeta`, `truncateMeta`, `changeGenStampOfBlock`, `setDataNodeDead`, and `injectBlocks`.
- Inspection helpers expose NameNode RPCs, namesystems, block reports, materialized replicas, block/metadata file paths, filesystem clients, NameNode ports, HTTP URIs, storage directories, and lease/recovery knobs.
- Security/provided-storage helpers are `setupNamenodeProvidedConfiguration` and `setupKerberosConfiguration`.

## Control Flow
The builder fills defaults, including scanner shutdown timeout, disabled load-aware redundancy selection, default dataset factory storage count, and round-robin volume policy spacing. The protected builder constructor fills a simple single-NN topology if absent, duplicates 1D storage type/capacity inputs across DataNodes, then delegates to `initMiniDFSCluster`.

`initMiniDFSCluster` wraps startup in a success guard. It mutates the supplied configuration for replication, maintenance replication, safemode extension, decommission interval, topology mapping, HA checkpoint/log-roll behavior, and edit-log fsync behavior. It configures and starts NameNodes first. If formatting is requested, it deletes stale DataNode data. It returns early for `StartupOption.RECOVER`; otherwise it starts DataNodes and waits for the cluster to become active. Any startup failure triggers `shutdown`.

NameNode setup is topology-driven. `configureNameNodes` writes nameservice and HA keys globally. `configureNameService` formats the first NN in an HA nameservice, copies its name dirs to later NNs to preserve cluster/block-pool IDs, starts each NN with an NN-specific config, and writes actual bound ports back to both NN and global configs.

DataNode startup validates array lengths, chooses hostnames, applies per-DN overlays, creates managed storage directories when requested, optionally configures simulated capacity, registers host/rack static mappings, handles secure DN resources, retries KDC/SASL replay-prone starts, starts the daemon, records `DataNodeProperties`, waits for all NNs to become active, and optionally applies per-volume test capacities.

Shutdown closes tracked filesystem handles, stops DNs, stops and joins NNs, clears shutdown hooks, and either deletes or schedules deletion of the cluster base dir. Restart paths remove nodes from internal lists, optionally preserve ports, recreate daemons from saved configs, and restore capacity overrides.

## State and Persistence Behavior
The class owns mutable cluster state in `conf`, `namenodes`, `dataNodes`, `numDataNodes`, `base_dir`, `data_dir`, `waitSafeMode`, `federation`, `fileSystems`, and `storageCap`. It also increments a static `instanceCount` to disambiguate clusters in a single JVM.

Persistent state is intentionally test-local. NameNode name dirs live under `name-<ns>-<slot>`; secondary/checkpoint dirs under `namesecondary-*`; shared HA edits under `shared-edits-<min>-through-<max>`; DN data under `data/data<N>`. Formatting deletes those dirs; HA formatting copies the first NN dirs; shutdown may delete the base dir immediately or on JVM exit. Block corruption helpers directly mutate block and metadata files through `FsDatasetTestUtils.MaterializedReplica`.

The class also mutates global/static test state: `ExitUtil.disableSystemExit`, `FileSystem.enableSymlinks`, `DefaultMetricsSystem.setMiniClusterMode`, `StaticMapping`, `NetUtils` static resolution, `EditLogFileOutputStream` fsync behavior, `ShutdownHookManager`, proxy-user configuration, and optional `SimulatedFSDataset` factory. Tests that reuse JVM state can be affected by these global changes.

## Dependencies and Integration Points
This harness integrates with `NameNode`, `DataNode`, `FSNamesystem`, `DFSClient`, `DFSAdmin`, `DFSTestUtil`, `NameNodeAdapter`, `DataNodeTestUtils`, `BlockManagerTestUtil`, `FsDatasetTestUtils`, `SimulatedFSDataset`, `StaticMapping`, security/Kerberos utilities, SSL test utilities, and HDFS configuration key families. `MiniDFSNNTopology` is the main input model for HA/federation. Many tests consume this class through `Builder`, `getFileSystem`, `getNamesystem`, restart helpers, and corruption helpers.

## Risks and Edge Cases
- The class heavily mutates caller-supplied `Configuration` objects and several process-wide singletons; test ordering can matter if cleanup is incomplete.
- Array-length validation and index use are critical for storage types, storage capacities, overlays, ports, racks, and hosts.
- Several waits use polling and fixed timeouts, so slow CI or asynchronous block reports can cause flakes.
- `getNN(int)` returns `null` for invalid indexes, which can become later `NullPointerException`s rather than immediate argument errors.
- `getBlockFile(int, ...)` and `getBlockMetadataFile(int, ...)` loop over storage dirs `0..1`, while the configurable `storagesPerDatanode` can differ from two.
- Direct block-file corruption bypasses normal HDFS invariants by design; callers must ensure they target materialized local replicas, not simulated datasets unless supported.
- `shutdownNameNode` clears fields inside `NameNodeInfo`; restart relies on saved `conf` and `startOpt` remaining valid.
- Security startup has retry logic only around SASL replay symptoms; other secure-resource failures are printed and may surface later.

## Test Signals
The file is itself test infrastructure. Strong signals are its assertions/preconditions, exceptions on invalid topology/storage config, startup/shutdown success, `waitActive` registration checks, restart paths, and failure-injection helpers. Downstream tests validate it indirectly by successfully creating clusters, simulating HA/federation, corrupting replicas, injecting simulated blocks, triggering reports, and restarting nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSClusterWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSClusterWithNodeGroup.java

## Purpose
`MiniDFSClusterWithNodeGroup` extends `MiniDFSCluster` to support network-topology tests that include node groups below racks. It lets tests map DataNodes to rack plus node-group paths while still using MiniDFSCluster lifecycle behavior.

## Important APIs, Types, and Functions
- Static `setNodeGroups(String[])` stores node-group assignments used during parent-class initialization.
- The constructor accepts a normal `MiniDFSCluster.Builder` and delegates to `super(builder)`.
- The main `startDataNodes(...)` overload adds `String[] nodeGroups` between racks and hosts and otherwise mirrors much of `MiniDFSCluster.startDataNodes`.
- Simpler overloads pass `nodeGroups` through for tests.
- The overridden parent-signature `startDataNodes(...)` injects static `NODE_GROUPS` so builder-driven cluster initialization can use node groups.

## Control Flow
Startup validation checks storage capacity/simulated capacity exclusivity, storage type/capacity array lengths, `StartupOption.RECOVER`, host config behavior, rack length, node-group length, host length, and simulated capacity length. It generates hostnames when racks are provided without hosts, prepares rollback args when needed, then loops over the requested DataNodes.

For each DN it clones config, sets loopback addresses, creates managed storage dirs, enables simulated capacity if requested, sets hostnames, and records topology mappings. If node groups are absent, it maps host and transfer address to the rack. If node groups are present, it concatenates rack and node-group strings and maps both the hostname and IP:port service to that combined topology path. It then instantiates and runs the DataNode, records `DataNodeProperties`, increments the cluster count, waits active, and applies optional volume capacity overrides.

## State and Persistence Behavior
The class adds static mutable state through `NODE_GROUPS`, which is consumed by the override called from the base constructor. Per-instance runtime state is inherited: `dataNodes`, `numDataNodes`, storage dirs, base dirs, and topology mappings. Persistent storage layout is the same as `MiniDFSCluster`; the only semantic difference is the topology path registered in `StaticMapping`.

## Dependencies and Integration Points
It depends on inherited MiniDFSCluster internals, especially protected `dataNodes`, `numDataNodes`, `storagesPerDatanode`, `makeDataNodeDirs`, `setupDatanodeAddress`, and `waitActive`. It integrates with `StaticMapping`, `NetUtils`, `DataNode`, `SecureDataNodeStarter`, `SimulatedFSDataset`, and `FsVolumeImpl`. Tests using rack/node-group placement policies depend on this subclass to represent node-group locality.

## Risks and Edge Cases
- `NODE_GROUPS` is static, so concurrent or sequential tests can leak node-group assignments unless reset.
- Rack and node-group strings are concatenated directly; callers must include expected separators in values if topology paths require them.
- The storage-capacity application block increments `curDatanodesNum` before looping and then indexes `dns[i]`, which is suspicious because `dns` is zero-based for the newly started DNs. This path looks error-prone for non-null `storageCapacities`.
- This subclass does not include all newer base-class features, such as DN config overlays or explicit HTTP/IPC port arrays, in its node-group-specific overload.
- Secure startup catches secure-resource exceptions by printing stack traces and continuing, matching older test style but making failures less explicit.

## Test Signals
The main signal is whether placement-policy tests observe expected rack/node-group paths through HDFS block placement. Constructor-driven startup also verifies that the parent override correctly uses `NODE_GROUPS`. Capacity override tests would be especially valuable because that path appears fragile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSClusterWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSNNTopology.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSNNTopology.java

## Purpose
`MiniDFSNNTopology` is a small configuration model used by `MiniDFSCluster` to describe NameNode layouts for tests: single NameNode, HA, federation, and HA federation.

## Important APIs, Types, and Functions
- `simpleSingleNN(int nameNodePort, int nameNodeHttpPort)` creates one unnamed nameservice with one unnamed NN.
- `simpleHATopology()` and `simpleHATopology(int)` create one nameservice, `minidfs-ns`, with multiple NN IDs.
- `simpleHATopology(int nnCount, int basePort)` creates HA NNs with explicit alternating IPC/HTTP ports.
- `simpleFederatedTopology(int)` and `simpleFederatedTopology(String)` create federated single-NN nameservices.
- `simpleHAFederatedTopology(int)` creates multiple nameservices, each with two NNs.
- Instance methods include `setFederation`, `addNameservice`, `countNameNodes`, `getOnlyNameNode`, `isFederated`, `isHA`, `allHttpPortsSpecified`, `allIpcPortsSpecified`, and `getNameservices`.
- Nested `NSConf` stores nameservice ID plus a list of `NNConf`.
- Nested `NNConf` stores NN ID, HTTP port, IPC port, and optional cluster ID override.

## Control Flow
Factory methods build topologies by chaining `addNameservice` and `addNN`. `addNameservice` rejects empty nameservices. `isFederated` returns true when more than one nameservice exists or when the explicit federation flag is set. `isHA` scans for any nameservice with more than one NN. Port-specified checks scan all NNs for nonzero HTTP/IPC ports.

## State and Persistence Behavior
The object is an in-memory mutable builder-style model. It does not persist anything itself. Its state is later consumed by `MiniDFSCluster.configureNameNodes` and `configureNameService`, which translate IDs and ports into HDFS configuration keys and on-disk name/shared-edits directories.

## Dependencies and Integration Points
It uses Hadoop `Preconditions` and `Lists`. Its primary integration is `MiniDFSCluster.Builder.nnTopology(...)`; `MiniDFSCluster` depends on the topology to decide federation, HA, config keys, shared edits, formatting strategy, and default FS behavior.

## Risks and Edge Cases
- Several factory methods use `null` nameservice or NN IDs intentionally for non-federated/non-HA layouts; downstream code must tolerate these nulls.
- `simpleFederatedTopology(String)` splits on commas without trimming, so whitespace in input becomes part of nameservice IDs.
- The `federation` boolean can force federated behavior even with one nameservice.
- Default ports are zero, meaning ephemeral ports; HA checkpoint/log-roll behavior may be disabled by `MiniDFSCluster` when explicit ports are absent.

## Test Signals
Useful tests are topology-shape checks: NN counts, HA/federation booleans, explicit port detection, rejection of empty nameservices, and correct generated IDs for federated/HA factories. Most coverage is indirect through MiniDFSCluster HA and federation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSNNTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailure.java

## Purpose
This JUnit 5 parameterized test drives `TestDFSStripedOutputStreamWithFailureBase` with randomly selected write lengths to exercise striped HDFS output-stream behavior under a single DataNode failure.

## Important APIs, Types, and Functions
- `data()` returns eleven parameter rows, each containing a random integer from `RANDOM.nextInt(220)`.
- `initParameterizedTestDFSStripedOutputStreamWithFailure(int)` stores the parameter in `base`.
- `runTestWithSingleFailure(int)` is the parameterized test. It normalizes the base index, looks up a length via inherited `getLength`, probabilistically skips most cases, and calls inherited `runTest(length)`.
- The class inherits shared random state, candidate `lengths`, EC schema handling, and actual failure test mechanics from `TestDFSStripedOutputStreamWithFailureBase`.

## Control Flow
JUnit obtains parameters from `data`. Each invocation stores `pBase`, assumes it is non-negative, wraps it modulo `lengths.size()` when needed, fetches a candidate length, skips null lengths, then uses a one-in-sixteen random gate to decide whether to run. When selected, it prints the chosen index and length and delegates to the base implementation.

## State and Persistence Behavior
The class has one mutable instance field, `base`, used only during a test invocation. It does not persist data itself; persistence is whatever the inherited test writes into MiniDFSCluster. Random selection makes the executed subset non-deterministic unless the inherited `RANDOM` is seeded externally.

## Dependencies and Integration Points
It depends on JUnit Jupiter parameterized tests, assumptions, timeout handling, SLF4J logging, and the base striped-output failure test class. It integrates with `StripedFileTestUtil` and MiniDFSCluster indirectly through the base class.

## Risks and Edge Cases
- Heavy use of randomness and assumptions means many generated cases are skipped; coverage varies per run.
- The modulo guard only checks `base > lengths.size()`, not `>=`; if `base == lengths.size()`, inherited `getLength` must handle the boundary safely.
- The test timeout is broad at 240 seconds, reflecting potentially slow failure recovery.

## Test Signals
A successful selected invocation means the base class can write a striped file for that length while tolerating a single DataNode failure. Skips are expected test signals rather than failures. Reproducing failures requires logging the selected index/length and any inherited random seed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java

## Purpose
This subclass reruns the striped-output failure parameterized test using a randomly chosen non-default erasure-coding policy. Its goal is to extend failure coverage beyond the default EC policy.

## Important APIs, Types, and Functions
- The constructor selects `StripedFileTestUtil.getRandomNonDefaultECPolicy().getSchema()` and logs the schema.
- `getEcSchema()` overrides the inherited schema provider and returns the selected `ECSchema`.

## Control Flow
Object construction chooses one non-default system EC policy. The inherited parameterized test then supplies random length indexes and delegates to the base failure scenario, but all inherited EC setup should see the overridden schema.

## State and Persistence Behavior
The only state is final per-instance `schema`. It does not persist directly. The selected schema influences the MiniDFSCluster and files created by the inherited test. Because the policy is random, separate instances or test runs can exercise different data/parity/cell combinations.

## Dependencies and Integration Points
The class depends on `StripedFileTestUtil`, `ECSchema`, SLF4J, and all inherited behavior from `ParameterizedTestDFSStripedOutputStreamWithFailure` and its base. It integrates with Hadoop system EC policy definitions.

## Risks and Edge Cases
- Random non-default policy selection makes failures harder to reproduce unless logs capture the schema.
- It assumes at least two system EC policies exist; `getRandomNonDefaultECPolicy` indexes from `1` to `policies.size() - 1`.
- Some non-default policies may have different performance or DataNode count requirements than the default, increasing timeout/flakiness risk.

## Test Signals
Passing runs indicate the striped output stream failure handling is not tied only to the default EC schema. The logged schema is the key diagnostic signal for reproducing any failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ParameterizedTestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ReadStripedFileWithDecodingHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ReadStripedFileWithDecodingHelper.java

## Purpose
`ReadStripedFileWithDecodingHelper` is an abstract utility base for tests that verify online reading and decoding of striped erasure-coded files when DataNodes or internal blocks are unavailable.

## Important APIs, Types, and Functions
- Constants derive the default EC policy, data/parity unit counts, cell size, block size, block-group size, DataNode count, and representative file lengths.
- `initializeCluster()` creates a MiniDFSCluster with enough DataNodes, enables the default EC policy, and sets it on root.
- `tearDownCluster()` shuts down a cluster.
- `findFirstDataNode` and `findDataNodeAtIndex` map block-location names back to MiniDFSCluster DN indexes by transfer port.
- `getParameters()` returns a cross product of file lengths, data-block deletion count, and parity-block deletion count constrained by parity capacity.
- `verifyRead()` performs length, positional read, stateful byte-array read, stateful `ByteBuffer` read, and seek validation through `StripedFileTestUtil`.
- `testReadWithDNFailure()` writes deterministic bytes, waits for block reports, shuts down DNs that hold internal data blocks, and verifies the file can still be read.
- `testReadWithBlockCorrupted()` writes a file, corrupts or deletes selected internal blocks, and verifies decoding reads.
- `corruptBlocks()` chooses random data/parity internal block indexes in the last striped block group, constructs internal `ExtendedBlock`s, and corrupts or deletes them through MiniDFSCluster.
- `getLocatedBlocks()` exposes DFSClient located-block lookup.

## Control Flow
Cluster initialization sets block size and replication stream limits, builds `NUM_DATA_UNITS + NUM_PARITY_UNITS + 3` DNs, enables EC, and sets root policy. Failure tests write deterministic content, force block-group reporting, identify block locations, induce DN shutdown or internal-block corruption, then call the shared read verifier. Corruption selection combines random data and parity indexes while asserting the total missing count does not exceed parity units.

## State and Persistence Behavior
The class holds no instance state; static constants shape files and clusters. It writes files into MiniDFSCluster, mutates DataNode liveness by shutdown, and mutates block files through corruption/deletion. File data is deterministic via `StripedFileTestUtil.generateBytes`, allowing read verification after recovery/decoding.

## Dependencies and Integration Points
It depends on MiniDFSCluster, `DistributedFileSystem`, `DFSTestUtil`, `StripedFileTestUtil`, `StripedBlockUtil`, `LocatedStripedBlock`, block-management logs, `GenericTestUtils`, and JUnit assertions. It turns up debug logging for placement, block management, and NameNode state transitions.

## Risks and Edge Cases
- DN lookup matches port substrings in block-location names; ambiguous string matches are unlikely but possible in malformed names.
- Random block-index selection makes corruption scenarios non-reproducible without additional logging.
- The corruption logic targets the last located striped block; tests for multi-group files rely on last-group decoding behavior.
- The helper assumes the missing data/parity count is within EC parity capacity; assertions enforce this before corruption.
- Shutting down `DataNode` instances directly does not remove them from MiniDFSCluster's `dataNodes` list, which is acceptable for read-failure simulation but differs from `cluster.stopDataNode`.

## Test Signals
Passing `verifyRead` after DN shutdown or block corruption confirms EC client-side/server-side decoding can satisfy length, positional read, streaming read, `ByteBuffer` read, and seek semantics. Timeout or assertion failures identify placement/reporting, corruption, or decoding regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ReadStripedFileWithDecodingHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/StripedFileTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/StripedFileTestUtil.java

## Purpose
`StripedFileTestUtil` is a shared utility class for HDFS erasure-coded striped-file tests. It generates deterministic data, validates read/seek behavior, inspects striped block groups, verifies parity bytes, waits for reporting/reconstruction, and supplies EC policies for parameterized tests.

## Important APIs, Types, and Functions
- `generateBytes(int)` and `getByte(long)` define deterministic file content using a modulo-29 pattern.
- `verifyLength`, `verifyPread`, `verifyStatefulRead` for byte arrays and `ByteBuffer`, `verifySeek`, and `assertSeekAndRead` validate file contents through multiple read APIs and boundary seeks.
- `killDatanode` and `getDatanodes` work with `DFSStripedOutputStream` and `StripedDataStreamer` to stop the DN currently used by a streamer.
- `getRealDataBlockNum` and `getRealTotalBlockNum` calculate internal block counts for partial stripes.
- `waitBlockGroupsReported` polls located blocks until expected internal block locations are reported.
- `randomArray` returns unique random integers in a range for block selection.
- `verifyLocatedStripedBlocks` asserts block groups are `LocatedStripedBlock`s with distinct locations and complete block-index sets.
- `checkData` parses striped block groups, reads internal blocks with `BlockReader`, verifies data-block bytes, fills killed data for parity verification, and calls `verifyParityBlocks`.
- `verifyParityBlocks` recomputes parity using Hadoop raw erasure encoders and compares expected parity blocks.
- `waitForReconstructionFinished` and `waitForAllReconstructionFinished` poll until reconstructed located-block counts reach expectations.
- `getLocatedBlocks`, `getDefaultECPolicy`, `getRandomNonDefaultECPolicy`, and `getECPolicies` expose common EC test inputs.

## Control Flow
Read verification writes expected data once and exercises positional reads from offsets around cell, stripe, block-group, and EOF boundaries. Stateful reads stream the full file into arrays/buffers and compare to expected bytes. Seek verification checks valid positions and, except for WebHDFS streams, asserts negative and past-EOF seeks fail.

Block-group reporting polls DFSClient located blocks up to 40 times and compares each block group's reported locations to the expected internal block count minus known dead DNs. `checkData` parses each striped block group into internal blocks, calculates each internal block's expected size, reads live blocks directly, verifies data bytes by translating internal offsets to file offsets, and recomputes parity for available parity blocks.

Reconstruction waits poll for enough located storage entries on the last block group or across all groups. EC policy helpers read system policies and package them for parameterized tests.

## State and Persistence Behavior
The class is stateless except for logging. It reads from and writes to HDFS through callers, stops DataNodes through MiniDFSCluster, and may directly read internal blocks through block readers. Randomness appears in `randomArray` and `getRandomNonDefaultECPolicy`, which affects reproducibility.

## Dependencies and Integration Points
It integrates with `DistributedFileSystem`, `FSDataInputStream`, `DFSStripedOutputStream`, `StripedDataStreamer`, `BlockReaderTestUtil`, `LocatedStripedBlock`, `StripedBlockUtil`, `SystemErasureCodingPolicies`, `CodecUtil`, raw erasure encoders, WebHDFS input streams, MiniDFSCluster, and JUnit assertions. Many EC tests depend on these helpers for common correctness checks.

## Risks and Edge Cases
- `randomArray` returns `null` for invalid ranges, and callers must assert/check that.
- `verifyPread` clamps offsets, so very small files still get repeated edge reads at valid offsets.
- `getDatanodes` spins until streamer nodes appear and can return `null` only on interruption.
- `checkData` assumes `killedList` is non-null and uses direct block reads, so it is sensitive to block-location availability and internal block sizing calculations.
- `verifyParityBlocks` normalizes shorter data blocks by padding to the first data block length; mistakes here could hide or expose parity-size bugs depending on last-block-group shape.
- `getRandomNonDefaultECPolicy` assumes at least one non-default policy exists.

## Test Signals
The utility's assertions are high-signal correctness checks for EC read paths: exact bytes, length, seek exceptions, unique placement, complete internal block indexes, generation-stamp monotonicity, direct internal block sizes, parity recomputation, and reconstruction location counts. Timeouts indicate reporting or reconstruction regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/StripedFileTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAbandonBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAbandonBlock.java

## Purpose
`TestAbandonBlock` verifies NameNode block-abandon behavior used when DFS clients fail pipeline creation or lose a DataNode while writing. It checks both idempotent abandon semantics and quota accounting.

## Important APIs, Types, and Functions
- `setUp()` creates a two-DataNode MiniDFSCluster and obtains a `DistributedFileSystem`.
- `tearDown()` closes the filesystem and shuts down the cluster.
- `testAbandonBlock()` writes an unclosed file, flushes it, obtains the file ID from `DFSOutputStream`, calls `ClientProtocol.abandonBlock` twice for the last block, closes the file, restarts the NameNode, and checks the block count dropped by one.
- `testQuotaUpdatedWhenBlockAbandoned()` sets a disk-space quota, writes with replication two, shuts down one DataNode, and ensures close does not throw `QuotaExceededException` when abandonment reallocates space.

## Control Flow
Each test starts from a fresh cluster. The first test creates a partial block, flushes it so the NameNode knows about it, fetches located blocks, abandons the last located block twice to prove idempotence, then closes and restarts the NameNode to verify the abandoned block is not persisted in namespace state. The quota test forces a write pipeline disruption by shutting down a DN, then closes the stream and fails if quota accounting still includes abandoned pending space.

## State and Persistence Behavior
The tests mutate HDFS namespace and block state. `testAbandonBlock` explicitly checks persistence by restarting the NameNode before re-reading block locations. `testQuotaUpdatedWhenBlockAbandoned` mutates root quota and live DN state. Local test cluster state is cleaned up in `tearDown`.

## Dependencies and Integration Points
Dependencies include MiniDFSCluster, `DistributedFileSystem`, `DFSClientAdapter`, `DFSOutputStream`, NameNode `ClientProtocol`, `LocatedBlocks`, `LocatedBlock`, HDFS quota constants, and JUnit lifecycle/assertions.

## Risks and Edge Cases
- The first test keeps using the original `DFSClient` after restarting the NameNode; cached RPC behavior must reconnect correctly.
- The assertion compares original block count to post-restart count plus one, so it is sensitive to additional block allocation during close.
- Quota behavior depends on pipeline failure induced by direct `DataNode.shutdown`, not `cluster.stopDataNode`, so MiniDFSCluster's bookkeeping still includes the DN.

## Test Signals
Passing signals: duplicate `abandonBlock` calls are harmless; abandoned blocks disappear after NameNode restart; quota is decremented for abandoned pending blocks and does not fail stream close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAbandonBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAclsEndToEnd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAclsEndToEnd.java

## Purpose
`TestAclsEndToEnd` validates KMS and key ACL enforcement through the full HDFS encryption-zone path. It starts real MiniKMS and MiniDFSCluster instances, switches proxy users, creates keys/zones/files, reads encrypted files, and deletes keys under allowed and denied ACL configurations.

## Important APIs, Types, and Functions
- Static setup `captureUser()` records the real UGI and user name for proxy-user configuration.
- `getKeyProviderURI()` converts the MiniKMS URL into a KMS provider URI.
- `writeConf(File, Configuration)` writes `kms-site.xml`, `kms-acls.xml`, and an empty `core-site.xml` because MiniKMS consumes config from files.
- `setup(Configuration, boolean resetKms, boolean resetDfs)` optionally creates/reuses a KMS dir, writes KMS config, starts MiniKMS, configures HDFS key-provider path and proxy users, then starts MiniDFSCluster.
- `teardown()` restores the login user, shuts down DFS, and stops MiniKMS.
- `getBaseConf`, `setBlacklistAcls`, and `setKeyAcls` build common KMS ACL matrices.
- Full-flow tests `testGoodWithWhitelist`, `testGoodWithKeyAcls`, and variants without blacklists call `doFullAclTest`.
- Focused matrix tests cover `testCreateKey`, `testCreateEncryptionZone`, `testCreateFileInEncryptionZone`, `testReadFileInEncryptionZone`, and `testDeleteKey`.
- Operation wrappers `createKey`, `createEncryptionZone`, `createFile`, `compareFile`, and `deleteKey` run actions as a target `UserGroupInformation`.
- `doUserOp` sets the login user, runs a privileged action, logs `IOException`, and returns success/failure as a boolean.

## Control Flow
The full ACL test creates proxy users for HDFS, key admin, and a normal user. It starts MiniKMS/MiniDFS with a provided ACL config, verifies key creation is limited to the key admin, creates an HDFS directory owned by the normal user, verifies only HDFS can create an encryption zone using the key, verifies only the normal user can create/read files in the zone, deletes the zone, and verifies only the key admin can delete the key.

Focused tests often use a two-phase pattern: first start with permissive setup ACLs to create a key, zone, or file; then tear down and restart with the same KMS/DFS data but a new ACL configuration to test one operation in isolation. The matrices compare whitelist ACLs, default key ACLs, key-specific ACLs overriding defaults, blacklists, missing KMS ACLs represented by a single space, missing key ACLs, and permissive default KMS ACL behavior.

## State and Persistence Behavior
The test persists KMS keystore data under `kmsDir` and HDFS namespace/data under the MiniDFSCluster base dir. Many scenarios intentionally reuse KMS data (`resetKms=false`) and sometimes DFS data (`resetDfs=false`) across service restarts to isolate ACL behavior from object creation. It also mutates global login user state through `UserGroupInformation.setLoginUser`, restoring it in teardown.

The file comments call out a persistence nuance: blank ACL values written through XML are treated as unset, so tests use `" "` to preserve a value that KMS later trims to blank. File contents are a fixed text string written into encryption zones.

## Dependencies and Integration Points
The test integrates HDFS encryption zones, MiniKMS, KMS ACL config, `KeyAuthorizationKeyProvider`, KMS client provider URIs, Java key stores, MiniDFSCluster, proxy-user settings, DFS delegation-token key behavior, UGI proxy users, DFS key creation helpers, and direct NameNode key-provider deletion. It is an end-to-end bridge between KMS authorization and HDFS encrypted file operations.

## Risks and Edge Cases
- There is no JUnit `@AfterEach`; cleanup is manual in each test/finally block. A setup failure before `miniKMS` exists or before `fs` exists could make teardown paths fragile.
- Global login-user mutation can leak across tests if teardown is skipped.
- Tests rely on KMS/DFS data reuse across restarts; accidental reset flags can invalidate scenarios.
- Assertions such as `new File(kmsDir, "kms.keystore").length() == 0` appear before `setup(conf)` in some tests, so they rely on prior static/instance state and may be brittle under unusual test-instance lifecycles.
- Boolean wrappers collapse all `IOException`s into denied/failed outcomes; they prove authorization at a high level but may hide a non-ACL I/O problem unless logs are inspected.
- Direct key deletion through `cluster.getNameNode().getNamesystem().getProvider().deleteKey` bypasses higher-level filesystem APIs by design.

## Test Signals
Passing tests confirm KMS ACLs, key ACLs, default ACLs, blacklists, and key-specific override semantics across key creation, encryption-zone creation, encrypted file creation, encrypted file read, and key deletion. Failure messages identify the ACL dimension being tested; logs from `doUserOp` provide the concrete `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAclsEndToEnd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendDifferentChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendDifferentChecksum.java

## Purpose
`TestAppendDifferentChecksum` verifies HDFS append behavior when a file is written with one checksum configuration and appended with another. It focuses on checksum algorithm changes, while chunk-size switching remains disabled.

## Important APIs, Types, and Functions
- `setupCluster()` creates a one-DataNode MiniDFSCluster with 4096-byte blocks and disables HDFS filesystem caching.
- `teardown()` shuts down the cluster after all tests.
- `testSwitchChunkSize()` is disabled because appending with a different bytes-per-checksum chunk size is not implemented.
- `testSwitchAlgorithms()` writes with CRC32 and appends with CRC32C, then verifies reads through both clients.
- `testAlgoSwitchRandomized()` repeatedly appends random-length segments using randomly selected CRC32 or CRC32C clients for roughly five seconds, then validates the entire file through both clients.
- `createFsWithChecksum(String type, int bytes)` clones the cluster config and sets checksum type and bytes-per-checksum.
- `appendWithTwoFs(Path, FileSystem, FileSystem)` writes one deterministic segment with the first FS and appends a second segment with the second FS.

## Control Flow
The cluster is shared for the class. Tests create separate `FileSystem` clients with different checksum settings. The simple algorithm-switch test writes two fixed 1500-byte segments and uses `AppendTestUtil.check` to verify expected deterministic contents. The randomized test creates an empty file, loops until the runtime budget expires, appends a random segment length below 500 bytes using a random checksum client, tracks total length, and verifies final content with both clients.

## State and Persistence Behavior
The tests persist files in MiniDFSCluster and rely on HDFS storing checksum metadata per block/chunk such that readers use on-disk checksums rather than their current client preference. The randomized test's file length and segment sequence are driven by a time-based seed printed to stdout.

## Dependencies and Integration Points
Dependencies include MiniDFSCluster, HDFS checksum config keys, `FileSystem`, `FSDataOutputStream`, `AppendTestUtil`, Hadoop `Time`, `IOUtils`, JUnit lifecycle/timeout/disabled annotations, and Java `Random`.

## Risks and Edge Cases
- The randomized test is time-based and seed-based, so coverage and failure reproduction depend on the printed seed.
- The timeout is twice the runtime budget, leaving limited room for slow CI.
- The disabled chunk-size test documents a known unsupported behavior, so algorithm-switch support must not be confused with bytes-per-checksum switching.
- Created checksum-specific FileSystem instances are not explicitly closed in each test, though filesystem caching is disabled.

## Test Signals
Passing algorithm-switch tests show appends with CRC32 and CRC32C can coexist and be read correctly by clients configured for either algorithm. The disabled test is a signal that checksum chunk-size switching remains intentionally unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendDifferentChecksum.java -->
