# subset-b-007545 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaCachingGetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaCachingGetSpaceUsed.java

## Purpose

`TestReplicaCachingGetSpaceUsed` verifies the DataNode `ReplicaCachingGetSpaceUsed` integration with `FsDatasetImpl`. It checks that DataNode DFS-used accounting includes both block and metadata file bytes for finalized replicas and replicas being written, and that `FsDatasetSpi.deepCopyReplica` is safe while replicas are being created concurrently.

## Important APIs and types

- `MiniDFSCluster`, `DistributedFileSystem`, `DFSInputStream`, `LocatedBlock`, and `ExtendedBlock` create real HDFS files and inspect block identities.
- `ReplicaCachingGetSpaceUsed` is selected through `fs.getspaceused.classname`, with `FS_DU_INTERVAL_KEY` and zero jitter making refresh timing predictable.
- `DataNode.getFSDataset().getDfsUsed()` is the primary accounting signal.
- `FsDatasetSpi.deepCopyReplica(String bpid)` exposes a snapshot of replicas for a block pool.
- `ModifyThread extends SubjectInheritingThread` repeatedly creates files while the main thread deep-copies the replica set.

## Control flow

Setup starts a one-node cluster configured to use `ReplicaCachingGetSpaceUsed`. The finalized test writes 20 KB, closes the stream, opens the file through the DFS client, sums block lengths and metadata stream lengths for all located blocks, sleeps long enough for the cached-space refresh, and expects `getDfsUsed()` to match that sum.

The RBW test keeps the output stream open after `hsync`, obtains the same block and metadata totals, waits for refresh, and expects the same accounting while the replica is still in RBW state. It then closes the stream, waits again, and asserts the value is unchanged across RBW-to-finalized transition.

The deep-copy test starts a background writer under `/testFsDatasetImplDeepCopyReplica`, then repeatedly calls `deepCopyReplica` until non-empty snapshots are observed ten times. Any `IOException` during snapshotting fails the test.

## State and persistence behavior

The tests create actual block and metadata files under a temporary MiniDFSCluster data directory. DFS-used state is cached and refreshed asynchronously, so tests rely on sleeps longer than the configured one-second interval. The RBW test is skipped on Windows. The modify thread deletes its test directory when stopped, but its `shouldRun` flag is a plain boolean, so visibility depends on normal test timing rather than explicit synchronization.

## Dependencies and integration points

This file integrates DataNode storage layout, metadata streams, HDFS write and sync paths, cached disk-usage accounting, block-pool replica snapshotting, and subject-preserving test threads. It is a regression surface for replacing shell `du` style accounting with replica-aware cached accounting.

## Risks and edge cases

- Refresh timing is sleep-based; slow hosts can still flake despite the low interval.
- Metadata length is read from DataNode internals rather than from filesystem enumeration.
- The concurrent writer swallows IOExceptions, so the deep-copy test only detects failures surfaced by `deepCopyReplica`.
- Non-volatile thread stop state can delay shutdown under unusual scheduling.

## Test signals

Strong signals are exact `blockLength + metaLength` accounting for finalized and RBW replicas, invariant accounting after close/finalization, Windows skip for RBW behavior, and repeated deep-copy calls under concurrent replica creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaCachingGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaMap.java

## Purpose

`TestReplicaMap` is a focused unit test for `ReplicaMap`, the in-memory block-pool-to-replica index used by DataNode storage. It verifies lookup, insertion argument validation, removal semantics, and the difference between merging another map and replacing current contents.

## Important APIs and types

- `ReplicaMap.add`, `get`, `remove`, `mergeAll`, and `addAll` are the behaviors under test.
- `Block` carries block ID, length, and generation stamp.
- `FinalizedReplica` is used as the concrete `ReplicaInfo` payload inserted into the map.
- The tests use a single block pool ID, `BP-TEST`, and one baseline block with matching ID and generation stamp.

## Control flow

`setup` inserts one finalized replica for the shared block. `testGet` verifies null-block rejection, successful lookup by full block, failure for generation-stamp mismatch, failure for block-ID mismatch, successful lookup by block ID, and null for an unknown block ID.

`testAdd` verifies that adding a null replica throws `IllegalArgumentException`. `testRemove` mirrors lookup behavior for null input and mismatch cases, checks successful remove by `Block`, checks removal miss by invalid ID, re-adds the replica, and checks successful remove by block ID.

`testMergeAll` builds a second map containing a new block and calls `mergeAll`, expecting both old and new entries to exist. `testAddAll` uses the same source map but expects only the source entry afterward, documenting replacement semantics.

## State and persistence behavior

All state is in-memory. The map is reset before each test by the test instance lifecycle and `@BeforeEach`. No filesystem state, cluster, or DataNode is created.

## Dependencies and integration points

The file is directly coupled to the `ReplicaMap` contract used by `FsDatasetImpl.volumeMap`. It verifies exact generation-stamp matching for operations that take a `Block`, which matters during recovery and replica state transitions where block IDs can match but generation stamps differ.

## Risks and edge cases

- It uses only one block pool and does not verify isolation across multiple block pools.
- It does not cover duplicate block IDs, replacement return values, iteration, or concurrent access.
- `fail` plus catch blocks assert only exception type by control flow, not message content.

## Test signals

The useful signals are strict null validation, exact match rules for block ID plus generation stamp, independent block-ID lookup/removal, and explicit distinction between additive `mergeAll` and replacing `addAll`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReplicaMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReservedSpaceCalculator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReservedSpaceCalculator.java

## Purpose

`TestReservedSpaceCalculator` validates the reserved-space policy selection and configuration precedence for DataNode volumes. It covers absolute byte reservation, percentage reservation, conservative and aggressive combined policies, per-storage-type overrides, per-directory overrides, and invalid calculator configuration.

## Important APIs and types

- `ReservedSpaceCalculator.Builder` wires `Configuration`, mocked `DF` capacity, `StorageType`, and optional directory into a calculator instance.
- Calculator implementations under test are `ReservedSpaceCalculatorAbsolute`, `ReservedSpaceCalculatorPercentage`, `ReservedSpaceCalculatorConservative`, and `ReservedSpaceCalculatorAggressive`.
- Configuration keys include `DFS_DATANODE_DU_RESERVED_KEY`, `DFS_DATANODE_DU_RESERVED_PERCENTAGE_KEY`, and `DFS_DATANODE_DU_RESERVED_CALCULATOR_KEY`.
- `StorageType` variants include `DISK`, `SSD`, `ARCHIVE`, `NVDIMM`, and `RAM_DISK`.

## Control flow

Each test sets the calculator class in configuration, populates global, storage-type-specific, or directory-specific keys, stubs `DF.getCapacity()`, builds a calculator, and asserts `getReserved()`.

Absolute tests assert direct byte values from global and storage-type keys. Percentage tests assert capacity-derived byte values, including integer truncation. Conservative policy chooses the larger of absolute and percentage results; aggressive policy chooses the smaller. Directory tests establish precedence: directory plus storage type, directory-only, storage-type-only, then global fallback. The invalid calculator test sets the class key to a bogus string and expects `IllegalStateException`.

## State and persistence behavior

The file is stateless beyond a new `Configuration` and Mockito `DF` per test. It does not touch real disks; all capacity state is mocked. Directory paths are literal configuration suffixes, not actual filesystem locations.

## Dependencies and integration points

The calculator feeds DataNode volume capacity accounting, especially `FsVolumeImpl` availability decisions. It integrates Hadoop configuration lookup, storage-type suffix conventions, directory-specific override parsing, and `DF` capacity reporting.

## Risks and edge cases

- Directory override parsing uses raw path suffixes, so path normalization and platform separator differences are not covered.
- Negative, over-100 percentage, negative absolute, and capacity overflow cases are absent.
- The test name `testReservedSpaceAggresivePerStorageType` preserves a misspelling but still exercises the aggressive policy.
- Mocked `DF` avoids real filesystem behavior such as changing capacity during runtime.

## Test signals

Strong signals are policy-specific expected numbers, exact override precedence, multiple storage types, truncation behavior for percentages, and explicit failure on invalid calculator class configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestReservedSpaceCalculator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestScrLazyPersistFiles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestScrLazyPersistFiles.java

## Purpose

`TestScrLazyPersistFiles` validates lazy-persisted RAM_DISK replicas when read through HDFS short-circuit read paths. It checks reads before and after eviction, interaction with open short-circuit handles, legacy reader fallback behavior, and checksum detection when block or metadata files are corrupted after lazy persistence.

## Important APIs and types

- The class extends `LazyPersistTestCase`, using its cluster builder, file creation, storage-type assertions, eviction trigger, and read verification helpers.
- `HdfsDataInputStream` read statistics expose total bytes and short-circuit bytes.
- `StorageType.RAM_DISK` and `StorageType.DEFAULT` represent pre- and post-eviction locations.
- `BlockMetadataHeader.getHeaderSize()` distinguishes RAM_DISK metadata header-only files from lazy-persisted checksum metadata.
- `DomainSocket`, `NativeCodeLoader`, and `NativeIO.POSIX` gate the test environment.

## Control flow

`@BeforeAll` disables domain socket bind-path validation. `@BeforeEach` assumes native code, non-Windows, working domain sockets, and block size aligned to OS page size. The basic SCR test creates a lazy-persist file, waits for `RamDiskBlocksLazyPersisted`, opens it, reads a buffer by position, and asserts all bytes were short-circuit reads.

The eviction-with-open-handle test reads once from an open SCR handle, triggers eviction, reads again through the same stream, and expects both reads to count as short-circuit bytes. The after-eviction helper runs for modern and legacy readers: it verifies RAM_DISK read, confirms metadata length is header-only, triggers eviction, waits for DEFAULT storage, checks metadata now includes checksum data, and verifies random file contents.

Corruption tests run for modern and legacy SCR paths. After lazy persistence and eviction, they corrupt either the block file or metadata file through `MiniDFSCluster` helpers and assert `ChecksumException` when reading the file buffer.

## State and persistence behavior

The tests create real block and checksum files in a MiniDFSCluster configured with faked RAM_DISK backed by local disk. State transitions include lazy-persist metrics, replica storage-type migration from RAM_DISK to DEFAULT, metadata file growth, client context state for legacy SCR, and on-disk corruption.

## Dependencies and integration points

This file integrates HDFS lazy persistence, DataNode eviction, local block readers, domain sockets, native IO page alignment, checksum metadata, client read statistics, and cluster corruption helpers. It is Linux/native-code-specific by design.

## Risks and edge cases

- Environment assumptions skip broad platforms; failures may hide on Windows or without native code.
- The test uses faked RAM_DISK on physical disk, not true memory hardware.
- Metric waits and eviction timing can be sensitive to slow CI.
- Legacy SCR behavior is checked only for not disabling the client context after a successful after-eviction read.

## Test signals

Strong signals include short-circuit byte counters, storage-type assertions before and after eviction, metadata header-size checks, open-handle survival through eviction, legacy reader non-disablement, and `ChecksumException` for both block and metadata corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestScrLazyPersistFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestSpaceReservation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestSpaceReservation.java

## Purpose

`TestSpaceReservation` is a slow MiniDFSCluster suite for DataNode reserved-space accounting for replicas in progress. It ensures RBW and temporary replica reservations reserve a full-block remainder, shrink as bytes are written, release on close, abort, errors, pipeline and lease recovery, re-replication, and replica finalization, and appear in JMX volume info.

## Important APIs and types

- `FsVolumeImpl.getReservedForReplicas()`, `reserveSpaceForReplica`, `getRecentReserved`, and test capacity overrides are central signals.
- `FSDataOutputStream`, `DFSOutputStream`, `DFSTestUtil.abortStream`, append, hsync/hflush, and lease recovery exercise client write paths.
- `BlockPoolSlice.createRbwFile` and `createTmpFile` are mocked through reflection into `FsVolumeImpl.bpSlices` to force file creation failures.
- `DataNodeFaultInjector` simulates mirror connection failure during pipeline recovery.
- `FsDatasetImpl.finalizeNewReplica` and `ReplicaInfo.getBytesReserved()` validate per-replica state cleanup.
- JMX `Hadoop:service=DataNode,name=DataNodeInfo` exposes `VolumeInfo`.

## Control flow

Shared helpers initialize HDFS configuration with fast DU refresh and scanner disabled, start clusters with one storage per DataNode, optionally cap volume capacity, and retain a reference to the single test volume. The base create/append helper writes a random partial block, asserts the reserved remainder, closes and verifies release, appends and verifies reservation, writes again and verifies the reservation shrinks.

Limited-space and EOF tests assert block allocation failure when two writers exceed capacity and that aborted writers release reservations on every replica in a three-node pipeline. RBW and temporary file creation error tests inject `IOException` from `BlockPoolSlice`, then verify reservation release happens once and does not clear unrelated pre-existing reservations.

Other tests assert JMX contains reserved-space fields, re-replication reserves exactly the source byte count for temporary replicas and releases it, concurrent writer stress leaves no leak, append close and abort restore only still-open reservations, mirror failure during pipeline recovery releases all reservations, lease recovery after a stopped DataNode leaves zero reservation, and finalizing a new replica clears both volume and `ReplicaInfo` reserved-byte counters.

## State and persistence behavior

The suite creates real clusters, data files, block replicas, JMX state, and DataNode volume state. It mutates capacity for testing, global `DataNodeFaultInjector`, reflected block-pool slice maps, and DataNode configuration during cleanup. Shutdown closes volume references, clients, filesystem, cluster, and restores the fault injector.

## Dependencies and integration points

It integrates HDFS create, append, close, abort, hflush/hsync, re-replication, block reports, pipeline recovery, lease recovery, DataNode JMX, `FsDatasetImpl`, `FsVolumeImpl`, `BlockPoolSlice`, and `ReplicaInfo`. It is a high-value regression suite for disk-full avoidance and reservation leak prevention.

## Risks and edge cases

- Many assertions depend on asynchronous cleanup and use `GenericTestUtils.waitFor`.
- Reflection into `bpSlices` tightly couples tests to `FsVolumeImpl` internals.
- The one-volume setup simplifies allocation behavior and may not cover multi-volume selection races.
- The stress test is time-based and can miss rare reservation leaks.
- Some failure messages contain historical typos but are not semantically relevant.

## Test signals

Strong signals are exact reservation byte counts, zero-reservation waits across all DataNodes, forced RBW/tmp creation failures, JMX field presence, temporary replica `recentReserved`, concurrent stress leak check, append abort/close accounting, injected pipeline failure, lease recovery, and finalization cleanup of both volume and replica state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestSpaceReservation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestWriteToReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestWriteToReplica.java

## Purpose

`TestWriteToReplica` validates `FsDatasetImpl` and `FsDatasetSpi` behavior when writing to, appending to, recovering, and recreating replicas in different states. It also verifies replica-map persistence across quick DataNode restart in a federated cluster and RBW recovery behavior for inconsistent on-disk length metadata.

## Important APIs and types

- Replica states are represented by test indexes for `FINALIZED`, `TEMPORARY`, `RBW`, `RWR`, `RUR`, and `NON_EXISTENT`.
- `FsDatasetTestUtils` creates finalized, temporary, RBW, waiting-to-be-recovered, and under-recovery replicas.
- APIs under test include `append`, `recoverAppend`, `recoverClose`, `recoverRbw`, `createRbw`, `createTemporary`, and `getReplicaInfo`.
- Exceptions distinguish invalid states: `ReplicaNotFoundException`, `ReplicaAlreadyExistsException`, and `DiskOutOfSpaceException`.
- `ReplicaMap.addAll`, `replicas`, `get`, and `remove` are used to compare pre- and post-restart maps.

## Control flow

Each primary test starts a MiniDFSCluster, builds six blocks, creates replicas in all relevant states, and calls a helper. Append tests first force disk-out-of-space by manipulating volume accounting, then verify successful append only for finalized replicas and recovery append for finalized and RBW replicas. Temporary, RWR, RUR, and non-existent cases must throw state-appropriate exceptions.

Close recovery allows finalized and RBW replicas but rejects temporary, RWR, RUR, and non-existent replicas. RBW tests reject recovery of non-RBW states, reject `createRbw` when any existing state already owns the block, recover existing RBW successfully, and allow `createRbw` for a non-existent block. Temporary creation rejects existing states, allows a non-existent block, rejects duplicate creation with the same generation stamp, and allows recreation when the generation stamp is newer.

The restart test creates a federated two-name-node cluster, collects block pool IDs and volumes, creates multiple replica states per pool and volume, snapshots `volumeMap`, restarts the DataNode, and verifies finalized replicas remain finalized while RBW/RWR/RUR convert to RWR and temporary replicas are not persisted. The inconsistent RBW test lowers in-memory bytes-on-disk and verifies recovery can reconcile it when data exists, then truncates the file and expects recovery failure.

## State and persistence behavior

The tests create actual replica files in randomized MiniDFSCluster directories. Restart behavior persists finalized and recovery-relevant replicas while intentionally dropping temporary pipeline replicas. Generation stamps are mutated in test block objects after successful transitions. The inconsistent RBW test edits the block file length through `RandomAccessFile`.

## Dependencies and integration points

This file integrates low-level DataNode dataset state machines, replica file layout, block pools, federation, generation stamps, disk-space checks, DataNode restart recovery, and on-disk metadata reconciliation.

## Risks and edge cases

- The tests depend on exact exception message prefixes, which can make harmless wording changes noisy.
- The setup creates one representative block per state, not all combinations of length and generation-stamp mismatch.
- Direct volume accounting manipulation for disk-out-of-space is implementation-specific.
- Restart assertions encode current conversion semantics for RBW/RWR/RUR to RWR.

## Test signals

Strong signals are the state matrix for append/close/RBW/tmp creation, disk-out-of-space validation, duplicate and newer-generation temporary behavior, federation-aware replica-map persistence, intentional non-persistence of temporary replicas, and RBW recovery distinction between inconsistent metadata and truly truncated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestWriteToReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestDataNodeOutlierDetectionViaMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestDataNodeOutlierDetectionViaMetrics.java

## Purpose

`TestDataNodeOutlierDetectionViaMetrics` verifies that `DataNodePeerMetrics` detects slow downstream DataNode peers from rolling send-packet latency samples and returns no outliers when all peers are fast.

## Important APIs and types

- `DataNodePeerMetrics.addSendPacketDownstream` records per-peer latency samples.
- `dumpSendPacketDownstreamAvgInfoAsJson` triggers rolling-average snapshot publication.
- `getOutliers` returns a map from peer name to `OutlierMetrics`.
- `MetricsTestHelper.replaceRollingAveragesScheduler` shortens rolling-average windows for test runtime.
- Constants define 10 fast peers, one 20-second slow peer, and fast latencies below 5 ms.

## Control flow

Setup enables trace logging and creates an `HdfsConfiguration`. The outlier test constructs metrics, replaces the rolling scheduler with ten three-second windows, injects many samples for ten fast peers, injects many samples for one slow peer, dumps rolling averages, waits until outliers become non-empty, and asserts exactly the slow peer appears.

The no-outlier test uses the same scheduler and fast-peer injection, triggers a snapshot, and asserts the outlier map is empty. Helper methods add twice the configured minimum sample count per peer, ensuring both sample-count and minimum-peer thresholds are satisfied.

## State and persistence behavior

State is held in memory inside rolling-average metrics and the outlier cache. No cluster or filesystem is used. Random fast-node latencies make exact averages non-deterministic while staying far below the slow-node threshold.

## Dependencies and integration points

The test bridges Hadoop metrics rolling averages, DataNode peer latency recording, and the `OutlierDetector` statistical logic that produces `OutlierMetrics` for NameNode or operator reporting.

## Risks and edge cases

- Detection is asynchronous and uses a long wait timeout.
- Random fast latencies can make debugging harder, though the range is intentionally tiny.
- Only one extreme slow peer is tested; borderline outliers and changing latency over windows are not covered.
- The JSON dump is used as a trigger, but the JSON content itself is not parsed here.

## Test signals

Strong signals are minimum-peer coverage, minimum-sample coverage, scheduler replacement, explicit snapshot trigger, eventual detection of exactly one named outlier, and empty result under a fast-only population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestDataNodeOutlierDetectionViaMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestSlowNodeDetector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestSlowNodeDetector.java

## Purpose

`TestSlowNodeDetector` is the direct unit test for `OutlierDetector`. It validates median and median absolute deviation calculations and the slow-node selection rules that combine minimum peer count, low-latency threshold, median multiplier, and MAD-based statistical outliers.

## Important APIs and types

- `OutlierDetector.getOutliers(Map<String, Double>)` returns high-latency outlier nodes.
- Static helpers `computeMedian` and `computeMad` are tested against a matrix of generated numeric lists.
- `LOW_THRESHOLD` is 1000 and `MIN_OUTLIER_DETECTION_PEERS` is 3.
- Guava immutable collections and Apache `Pair` encode expected matrices.

## Control flow

Setup constructs an `OutlierDetector` and enables trace logging. The outlier matrix covers too few peers, statistical outliers below the low threshold, outliers above the low threshold, values inside and outside the median-multiplier limit, multi-node sets with high and low outliers, and cases where only high outliers should be returned.

Median and MAD tests sort a copy of each input list before invoking the static helpers, compare against expected values using a 0.001 percent error tolerance, and special-case one-element MAD near zero. Empty-list tests assert `IllegalArgumentException`, though the MAD test currently calls `computeMedian` in its lambda, which still validates empty-list rejection but not the intended method.

## State and persistence behavior

All state is in-memory immutable test data. There is no metrics scheduler or DataNode. The detector instance is recreated before each test.

## Dependencies and integration points

The file is the statistical core companion to `DataNodePeerMetrics` tests. It defines the expected behavior used to flag slow packet-sending peers and shapes the semantics of `OutlierMetrics` production.

## Risks and edge cases

- Expected floating-point values are hard-coded; algorithm changes require careful recalculation.
- The empty MAD test appears to invoke `computeMedian`, leaving direct empty-list `computeMad` behavior less explicitly covered.
- Input lists are sorted by the tests before median/MAD calls, so unsorted input handling is not asserted here.
- Low outliers are intentionally ignored because the detector targets slow nodes only.

## Test signals

Strong signals are matrix-driven outlier expectations, threshold and median-multiplier coverage, median/MAD numeric accuracy across list sizes one through ten, and explicit empty-input exception checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/metrics/TestSlowNodeDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpServer.java

## Purpose

`TestDatanodeHttpServer` verifies that `DatanodeHttpServer` honors the configured HDFS HTTP policy by enabling HTTP, HTTPS, or both endpoints and leaving disabled endpoint addresses null.

## Important APIs and types

- JUnit parameterized class runs the same test for `HttpConfig.Policy.HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`.
- `KeyStoreTestUtil` creates temporary SSL configuration and keystores.
- `URLConnectionFactory` opens HTTP or HTTPS URLs with the generated SSL client configuration.
- `DatanodeHttpServer.start`, `getHttpAddress`, `getHttpsAddress`, and `close` are the direct server lifecycle APIs.

## Control flow

`@BeforeAll` creates a temp base directory, generates SSL config, creates a URL connection factory, and points DFS client/server keystore resource keys at the generated files. The parameterized test sets the HTTP policy and both DataNode HTTP/HTTPS bind addresses to `localhost:0`, starts a `DatanodeHttpServer`, and checks access for enabled schemes. `canAccess` opens the root URL, expects HTTP 200, reads the response, and requires the admin page text `Hadoop Administration`. Disabled schemes are expected to have null server addresses.

## State and persistence behavior

The test writes temporary keystores and SSL XML resources under a generated test path and cleans them in `@AfterAll`. Server sockets bind to ephemeral local ports. No DataNode dataset is required because the server is constructed with null DataNode dependencies for this policy check.

## Dependencies and integration points

It connects Hadoop HTTP policy configuration, SSL resource generation, DataNode HTTP server endpoint creation, URL connection behavior, and the common admin web UI response.

## Risks and edge cases

- `canAccess` catches all exceptions and returns false, so failure diagnostics are collapsed.
- The page-content assertion depends on the admin page text.
- It does not test WebHDFS endpoints, authentication filters, or TLS certificate details.
- Static configuration is shared across parameterized instances, so mutations must remain policy-local.

## Test signals

Strong signals are all three policy modes, real socket binding, real HTTP/HTTPS requests through Hadoop SSL config, null checks for disabled endpoints, and response-code plus admin-page validation for enabled endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpXFrame.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpXFrame.java

## Purpose

`TestDatanodeHttpXFrame` validates X-Frame-Options handling on the DataNode HTTP server. It ensures the header is emitted with the default `SAMEORIGIN` value when enabled, omitted when disabled, and rejected when configured with an invalid option value.

## Important APIs and types

- `DFS_XFRAME_OPTION_ENABLED` and `DFS_XFRAME_OPTION_VALUE` control the behavior.
- `MiniDFSCluster` starts a real DataNode web server.
- `HttpServer2.XFrameOption.SAMEORIGIN` is the expected default value.
- `HttpURLConnection` fetches the DataNode info port root page and reads response headers.

## Control flow

Each test creates a one-DataNode cluster with the desired X-Frame settings. The enabled test connects to `http://localhost:<infoPort>`, reads the `X-FRAME-OPTIONS` header, asserts it exists, and checks it ends with `SAMEORIGIN`. The disabled test asserts the header is absent. The invalid-value test expects cluster creation to throw `IllegalArgumentException` when the option value is set to `Hadoop`.

## State and persistence behavior

The cluster and DataNode HTTP server are real and are shut down after each test. No files are intentionally created beyond MiniDFSCluster test data.

## Dependencies and integration points

The test integrates HDFS X-Frame config keys, `HttpServer2` option parsing, DataNode info server startup, and HTTP response headers. It protects clickjacking-related admin UI hardening.

## Risks and edge cases

- The test uses the root page only; it does not verify every DataNode servlet path.
- It checks `endsWith` instead of exact equality, allowing extra header prefix text.
- The method name `testNameNodeXFrameOptionsDisabled` is misleading because it creates a DataNode cluster.
- Invalid value coverage uses one invalid string only.

## Test signals

Strong signals are real HTTP response header inspection, both enabled and disabled modes, default SAMEORIGIN value, invalid configuration rejection, and cluster cleanup after each test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpXFrame.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestHostRestrictingAuthorizationFilterHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestHostRestrictingAuthorizationFilterHandler.java

## Purpose

`TestHostRestrictingAuthorizationFilterHandler` validates the Netty wrapper around `HostRestrictingAuthorizationFilter` for DataNode WebHDFS requests. It checks default reject-all behavior, allowed GET request pass-through, channel reuse, multi-channel sharing of one filter instance, and unconditional allowance for `GETFILECHECKSUM`.

## Important APIs and types

- `HostRestrictingAuthorizationFilterHandler.initializeState(Configuration)` builds the underlying ACL filter.
- Configuration key is the HDFS-prefixed restriction key from `HostRestrictingAuthorizationFilter`.
- Netty `EmbeddedChannel`, `DefaultFullHttpRequest`, and `DefaultHttpResponse` simulate inbound HTTP processing.
- `WebHdfsFileSystem.PATH_PREFIX` provides the WebHDFS URI prefix.
- `CustomEmbeddedChannel.remoteAddress0` supplies deterministic client IPs.

## Control flow

`testRejectAll` installs a default handler without ACL rules, sends a WebHDFS `OPEN` request, expects `writeInbound` false, polls a forbidden response, and verifies the channel closes. `testMultipleAcceptedGETsOneChannel` configures `*,*,/allowed`, sends three allowed `OPEN` requests through one channel, and expects all to pass inbound. `testMultipleChannels` shares one initialized filter across three channels with different remote addresses and verifies closing one channel does not affect another. `testAcceptGETFILECHECKSUM` sends a checksum request through the default handler and expects it to pass.

## State and persistence behavior

All state is in-memory Netty channel state and filter configuration. No server socket or cluster starts. The shared filter instance carries ACL state but should not carry channel-specific state.

## Dependencies and integration points

This file integrates DataNode Netty WebHDFS request handling, host/path authorization rules, remote-address extraction, and special-casing of checksum operations.

## Risks and edge cases

- ACL coverage is minimal: one allow rule and the no-rule default.
- It does not test non-GET methods, proxy headers, IPv6, hostnames, or malformed paths.
- Rejected request body/resource release behavior is not asserted.
- The checksum allowance is tested independent of path ACLs, which is intentional but security-sensitive.

## Test signals

Strong signals are forbidden response status and channel close on reject, repeated accepted requests on one channel, shared filter behavior across channels, and explicit checksum pass-through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestHostRestrictingAuthorizationFilterHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestDataNodeUGIProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestDataNodeUGIProvider.java

## Purpose

`TestDataNodeUGIProvider` verifies WebHDFS DataNode-side `UserGroupInformation` construction and cache behavior for secure token-based requests and insecure user-parameter requests. It also checks the secure no-token path delegates to non-token UGI construction.

## Important APIs and types

- `DataNodeUGIProvider.init`, `ugi`, `clearCache`, `ugiCache`, and `nonTokenUGI` are under test.
- `ParameterParser` reads query parameters from Netty `QueryStringDecoder`.
- `DelegationTokenIdentifier`, `DelegationTokenSecretManager`, and `Token` synthesize WebHDFS delegation tokens.
- `SecurityUtil`, `UserGroupInformation`, and `WebHdfsFileSystem` configure secure or insecure identity context.
- `DFS_WEBHDFS_UGI_EXPIRE_AFTER_ACCESS_KEY` controls cache expiry.

## Control flow

Setup creates WebHDFS test configuration, sets cache expiry to five seconds, and initializes the provider. The secure-cache test enables Kerberos, creates a proxy login user, obtains a WebHDFS filesystem and two delegation tokens, builds two `OPEN` URIs that differ only by delegation token, and verifies repeated `ugi()` calls for the same token return equal UGI objects while different tokens produce distinct UGIs. It then clears one provider cache reference, waits for global cache expiration without touching entries, and verifies new calls produce different UGIs.

The insecure-cache test builds two URIs with different `user.name` values, verifies same-user cache hits and different-user cache separation, waits for expiry, and verifies new UGI instances are returned. The secure-null-token test enables Kerberos but supplies user parameters rather than a delegation token, spies the provider, invokes `ugi`, and verifies `nonTokenUGI` is called with parsed username, doAs user, and resolved remote user.

## State and persistence behavior

State is in the static UGI cache, global UGI security configuration, login user, and in-memory delegation token secret manager threads. The test intentionally waits for cache expiration and calls Guava-style `cleanUp` to avoid refreshing access times.

## Dependencies and integration points

It integrates DataNode WebHDFS parameter parsing, secure delegation-token identity, insecure pseudo-auth identity, UGI cache expiry, token service assignment, and default web user fallback logic.

## Risks and edge cases

- Security and login user configuration are global JVM state and may affect neighboring tests if not isolated by the harness.
- The token secret manager is started but not explicitly stopped in this file.
- Equality of UGI objects is used as the cache signal; object identity is not directly asserted.
- Expiration waits are time-based and can slow test execution.

## Test signals

Strong signals are token-keyed cache hits, token separation, user-keyed insecure cache hits, user separation, expiry-driven cache misses, explicit cache cleanup, and verification that secure no-token requests use the non-token UGI path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestDataNodeUGIProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestParameterParser.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestParameterParser.java

## Purpose

`TestParameterParser` validates selected WebHDFS DataNode query parsing behavior: HA delegation-token deserialization, absent-token handling, path decoding, create flag parsing, and offset parsing defaults and failures.

## Important APIs and types

- `ParameterParser.delegationToken`, `path`, and `createFlag` are the direct parser APIs.
- `QueryStringDecoder` supplies decoded request URIs.
- `NamenodeAddressParam`, `DelegationParam`, `OffsetParam`, and `CreateFlag` provide WebHDFS parameter semantics.
- `HAUtilClient.isTokenForLogicalUri` checks that HA logical-name token services are preserved.

## Control flow

The HA token test creates an HA configuration for logical name `minidfs`, encodes an empty delegation token into a WebHDFS URI with `namenoderpcaddress=minidfs`, parses it, and asserts the resulting token is for a logical URI. The null-token test uses a URI without delegation parameters and expects `delegationToken()` to return null.

The path test passes an escaped path containing `%25`, `+`, `%26`, and `%3D` before query parameters and expects the parser path to decode to `/test%+1&=test`. Create-flag tests cover multiple comma-separated values, one value, absent parameter, create plus overwrite, empty value, and malformed trailing comma cases that should throw an enum-related exception. The offset test verifies explicit numeric offset, null defaulting to zero, and nonnumeric failure.

## State and persistence behavior

The tests are pure parser tests with local `Configuration` instances and no filesystem or network state. Tokens are encoded strings only; they are not validated against a live secret manager.

## Dependencies and integration points

This file integrates Netty URI decoding with WebHDFS parameter classes, HA logical URI token handling, HDFS create flags, and offset parameter validation. It guards DataNode WebHDFS request routing correctness before operations reach the filesystem.

## Risks and edge cases

- Create-flag assertions compare `toString` for multi-value sets in some cases rather than set equality.
- Malformed create flags are checked by message substring, which depends on enum parser wording.
- It covers offset directly through `OffsetParam` in one case rather than only through `ParameterParser`.
- It does not cover every WebHDFS parameter parsed by `ParameterParser`.

## Test signals

Strong signals are HA logical token recognition, null-token default, percent and plus path decoding, multiple valid create-flag shapes, malformed create-flag rejection, default offset zero, and nonnumeric offset rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestParameterParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerTestUtil.java

## Purpose

`DiskBalancerTestUtil` is a shared test helper for disk balancer suites. It creates randomized disk balancer model objects, synthetic clusters, imbalanced MiniDFSClusters, counts blocks per volume, and moves blocks between volumes to force planner and mover scenarios.

## Important APIs and types

- Model factories create `DiskBalancerVolume`, `DiskBalancerVolumeSet`, `DiskBalancerDataNode`, and `DiskBalancerCluster`.
- Constants `MB`, `GB`, and `TB` standardize model sizes.
- `NullConnector` feeds synthetic nodes into `DiskBalancerCluster`.
- `newImbalancedCluster` creates a real MiniDFSCluster with two disk volumes and moves all blocks to one destination volume.
- `getBlockCount` iterates `FsVolumeSpi.BlockIterator` for each block pool.
- `moveAllDataToDestVolume` calls `FsDatasetSpi.moveBlockAcrossVolumes` for every block on a source volume.

## Control flow

Random model helpers generate names, storage types, capacities, reserved bytes below 20 percent of capacity, and used bytes less than capacity minus reserved. Volume sets and data nodes are built by repeatedly adding random volumes by storage type. `createRandCluster` populates a `NullConnector`, calls `readClusterInfo`, and returns the resulting cluster model.

The MiniDFSCluster helper enables disk balancer, configures block and checksum sizes, writes a file, waits for replication, restarts DataNodes, obtains source and destination volumes for each DataNode, asserts source has blocks, moves all data from source to destination, asserts source is empty, restarts again, and returns the intentionally imbalanced cluster. Block counting can optionally assert each block pool has blocks.

## State and persistence behavior

Model helpers are in-memory and randomized from monotonic time. MiniDFSCluster helpers create actual block files and mutate their volume locations by moving blocks. Restart calls persist the resulting imbalance to DataNode storage.

## Dependencies and integration points

The helper bridges disk balancer model classes, connector abstractions, MiniDFSCluster, HDFS block creation, `FsDatasetSpi` volume movement, and `FsVolumeSpi` block iterators. Many disk balancer tests rely on it for reproducible imbalance setup.

## Risks and edge cases

- Random model data can make scale and serialization tests less deterministic.
- `newImbalancedCluster` requires exactly two storage capacities.
- Deprecated `new Double(temp).longValue()` style appears but only affects test utility implementation.
- Moving all blocks directly through the dataset bypasses planner validation and assumes volume references remain valid during iteration.

## Test signals

As a utility, its signals are indirect: generated models have valid capacities and usage, clusters can be serialized and planned, source volume block counts drop to zero after movement, destination volumes accumulate blocks, and restarted clusters preserve the forced imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestConnectors.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestConnectors.java

## Purpose

`TestConnectors` validates disk balancer cluster connectors for live NameNode discovery and JSON serialization/parsing of discovered cluster topology.

## Important APIs and types

- `ConnectorFactory.getCluster(URI, Configuration)` creates a `ClusterConnector` from an HDFS filesystem URI.
- `DiskBalancerCluster.readClusterInfo` loads DataNode and volume topology.
- `DiskBalancerCluster.toJson` and `parseJson` round-trip cluster model data.
- `MiniDFSCluster` supplies a live three-DataNode test cluster with default two volumes per DataNode.

## Control flow

Setup starts a three-DataNode MiniDFSCluster. The NameNode connector test waits for active cluster state, gets a connector for the filesystem URI, reads cluster info, and asserts the discovered node count is three and the first node has two volumes. The JSON connector test reads the same live topology, serializes it to JSON, parses it back, and asserts the node count is preserved.

## State and persistence behavior

The only persistent state is MiniDFSCluster test storage, removed by cluster shutdown. The JSON string is in-memory and not written to disk.

## Dependencies and integration points

This file connects NameNode-reported DataNode storage topology to the disk balancer model layer and validates that JSON connector semantics can represent that topology.

## Risks and edge cases

- It checks counts only, not detailed volume fields after JSON parse.
- Default volume count assumptions depend on MiniDFSCluster defaults.
- It does not test file-based JSON connector loading directly.

## Test signals

Strong signals are live connector discovery from an HDFS URI, expected DataNode count, expected per-node volume count, and successful JSON round-trip at the cluster model level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestConnectors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDataModels.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDataModels.java

## Purpose

`TestDataModels` validates the disk balancer data model objects: random volume creation, volume sets, DataNode density, sorted queues, balancing-needed decisions, JSON serialization, and clamping of used bytes to capacity.

## Important APIs and types

- `DiskBalancerVolume` fields include UUID, path, storage type, transient flag, failed flag, capacity, reserved, and used.
- `DiskBalancerVolumeSet` groups volumes by storage type and computes balancing need.
- `DiskBalancerDataNode` holds volume sets and node density.
- `DiskBalancerCluster.toJson` and model `parseJson` round-trip cluster and volume data.
- `DiskBalancerTestUtil` creates random but valid model objects.

## Control flow

Creation tests assert random volumes have non-null identity fields, nonfailed/nontransient defaults for disk, positive capacity, valid reserved space, and used plus reserved below capacity. Volume-set and DataNode tests assert expected counts and non-null density.

Queue tests fetch a sorted queue from the DISK volume set, repeatedly read the first element into lists, reverse one list, and compare capacity/reserved/used fields, documenting current queue ordering behavior. Balancing tests build hand-configured two-volume nodes: equal spread needs no balancing, transient RAM_DISK volumes do not need balancing, failed disks suppress balancing, and uneven SSD usage needs balancing. Serialization tests round-trip a volume and a random cluster. The usage-limit test asserts used bytes are clamped to capacity, though its second assertion compares `v1` rather than `v2`, which weakens the intended below-capacity check.

## State and persistence behavior

All state is in-memory model state. Randomized values are generated per test. No filesystem or cluster is used.

## Dependencies and integration points

These models are consumed by connectors, planner, and DataNode disk balancer execution. The tests guard capacity math, transient/failed disk exclusion, JSON stability, and model validity expected by planner algorithms.

## Risks and edge cases

- Random inputs can occasionally obscure deterministic planner properties.
- The disk queue test appears not to remove queue entries while iterating, so it may compare repeated first elements rather than the full sorted order.
- The final usage-limit assertion likely references the wrong variable, reducing coverage for used-below-capacity behavior.
- Equality for cluster serialization depends on model `equals` implementations.

## Test signals

Strong signals are model field validity, volume grouping counts, no-balance decisions for equal/transient/failed disks, positive balance decision for uneven spread, JSON round-trips, and capacity clamp for overused volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDataModels.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancer.java

## Purpose

`TestDiskBalancer` is the broad integration suite for DataNode disk balancer planning and execution. It validates NameNode topology discovery, end-to-end block movement, federated clusters, bandwidth delay computation, multi-step balancing, behavior with one empty nameservice, and resilience when a volume is removed during plan execution.

## Important APIs and types

- `DiskBalancerCluster`, `ConnectorFactory`, and `DiskBalancerDataNode` discover and model cluster topology.
- `NodePlan`, `DiskBalancerWorkStatus`, `DiskBalancerWorkItem`, and `DiskBalancer.VolumePair` represent execution plans and state.
- `DataNode.submitDiskBalancerPlan`, `queryDiskBalancerPlan`, and `getDiskBalancerStatus` exercise the DataNode RPC/JMX-facing surface.
- `DiskBalancer.DiskBalancerMover.computeDelay` enforces bandwidth throttling.
- Nested `ClusterBuilder` and `DataMover` construct imbalanced clusters, generate plans, execute them, and verify results.

## Control flow

The connectivity test starts two DataNodes, reads cluster info from the NameNode connector, matches model fields to the live DataNode ID/IP/host/volume count, then shuts down a DataNode and checks `getDiskBalancerStatus()` returns an empty string instead of throwing.

End-to-end tests create one-node clusters with multiple storage volumes and many blocks, move all blocks to one source disk, compute a plan from current cluster info, submit it, parse JMX status JSON, wait for `PLAN_DONE`, verify every volume has data, and check tolerance against planned bytes. Variants cover federated two-namespace data, one empty nameservice with expected log output for null next block, and three disks producing two plan steps.

The compute-delay test spies the dataset and uses a mocked work item with 10 MB/s bandwidth to assert 20 MB copied in 1.2 seconds yields an 800 ms delay. The disk-removal test spies mover execution, pauses after work-plan creation, reconfigures `dfs.datanode.data.dir` to remove one disk, resumes copy, waits for `PLAN_DONE`, and asserts disk errors stay within the configured maximum.

## State and persistence behavior

The suite creates real MiniDFSCluster storage, writes files, moves blocks across volumes, restarts DataNodes, submits background disk balancer plans, reads JMX-style status JSON, captures logs, and reconfigures DataNode data directories. Block movement persists to local test data directories.

## Dependencies and integration points

It integrates HDFS file creation, NameNode topology reporting, federation, DataNode volume references, disk balancer planning, DataNode plan submission, JMX status serialization, mover throttling, live reconfiguration, and block iterators.

## Risks and edge cases

- End-to-end waits are time-based and can be slow or flaky under constrained IO.
- Helpers directly move blocks before planning, which bypasses normal workload-driven imbalance creation.
- Tolerance verification uses block counts and planned bytes approximation.
- Disk-removal handling uses Mockito spies and latches, tightly coupling to mover internals.

## Test signals

Strong signals are live topology matching, real block movement to completion, parsed status consistency, final `PLAN_DONE`, all-volumes-have-data checks, federated block-pool handling, expected empty-nameservice log, multi-step plan count, exact compute-delay math, and bounded error count during volume removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerRPC.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerRPC.java

## Purpose

`TestDiskBalancerRPC` validates DataNode disk balancer RPC-facing methods: plan submission, validation failures, cancellation, settings lookup, status query, and direct block movement across volumes.

## Important APIs and types

- `DataNode.submitDiskBalancerPlan`, `cancelDiskBalancePlan`, `queryDiskBalancerPlan`, and `getDiskBalancerSetting` are the primary RPC-like methods.
- `DiskBalancerException.Result` distinguishes invalid hash, invalid version, invalid plan, no such plan, and unknown setting.
- `DiskBalancerWorkStatus.Result` values include `NO_PLAN`, `PLAN_UNDER_PROGRESS`, and `PLAN_DONE`.
- `RpcTestHelper` builds a `NodePlan` using `ConnectorFactory`, `DiskBalancerCluster`, `DiskBalancerDataNode`, and `GreedyPlanner`.
- `DigestUtils.sha1Hex(plan.toJson())` computes the accepted plan hash.

## Control flow

Setup enables disk balancer and starts two DataNodes. Most tests call `RpcTestHelper.invoke`, which restarts DataNode 0, reads cluster topology, selects that DataNode, balances its DISK volume set into a `NodePlan`, sets plan version one, and hashes the JSON. Submission with matching hash/version succeeds. Mutated hash, incremented version, and empty plan content each throw the expected `DiskBalancerException.Result`.

Cancellation succeeds after a valid submit; cancellation with a mutated or empty hash yields `NO_SUCH_PLAN`. Settings tests parse the volume-name JSON into a map and expect two entries, reject an unknown setting, and verify the bandwidth setting reports `10` after a submitted plan. Query tests distinguish submitted from no-plan state. The movement test creates a one-node cluster with a file, moves all blocks from one volume to another using `DiskBalancerTestUtil`, and asserts the source volume is empty.

## State and persistence behavior

The tests create real clusters and submit real DataNode disk balancer plans, though most validation is at the RPC/plan level rather than waiting for long movement. The movement test mutates on-disk block placement. `tearDown` shuts down the current cluster.

## Dependencies and integration points

This file connects DataNode RPC surface validation, plan hashing/versioning, disk balancer settings serialization, planner output, and dataset volume movement. It complements mock-mover tests by exercising DataNode wrappers.

## Risks and edge cases

- Some tests create a new cluster inside a method while setup already created one, increasing lifecycle complexity.
- Query after submit accepts either under-progress or done, reflecting asynchronous execution.
- Volume mapping assertion checks count but not path-to-UUID correctness.
- Plan generation depends on current cluster topology being imbalanced enough to create steps.

## Test signals

Strong signals are accepted valid plan submission, explicit result codes for invalid hash/version/plan/cancel/setting, volume mapping JSON parse, bandwidth setting decode, query status before and after submit, and source volume block count zero after direct movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerRPC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerWithMockMover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerWithMockMover.java

## Purpose

`TestDiskBalancerWithMockMover` tests the `DiskBalancer` coordinator with a controllable `BlockMover` implementation. It focuses on enablement checks, plan submission lifecycle, duplicate submission rejection, old and invalid plans, cancellation, invalid hashes, custom bandwidth propagation, and background execution without relying on real block copies.

## Important APIs and types

- `DiskBalancer.queryWorkStatus`, `submitPlan`, and `cancelPlan` are under test.
- `TestMover implements DiskBalancer.BlockMover` and exposes sleep, delay, runnable, exit, and run-count controls.
- `DiskBalancerWorkStatus` and `DiskBalancerWorkItem` expose result and per-step bandwidth.
- Helper builders create `DiskBalancer`, load a JSON disk balancer cluster resource, and build a `NodePlan` with live test volume paths and UUIDs.
- `DigestUtils.sha1Hex` computes plan IDs.

## Control flow

Setup starts a three-DataNode cluster with two storage volumes per DataNode and records DataNode UUID plus source/destination volume paths and storage IDs. Disabled and enabled tests build a `DiskBalancer` around `TestMover` and assert disabled query throws `DISK_BALANCER_NOT_ENABLED` while enabled query reports `NO_PLAN`.

The mock helper restarts the DataNode, creates a runnable `TestMover`, loads `/diskBalancer/data-cluster-3node-3disk.json`, generates a greedy plan for the current node ID, and rewrites plan step volume names and UUIDs to match live volumes. Submission tests verify a stuck mover causes second submit to throw `PLAN_ALREADY_IN_PROGRESS`, a normal submit eventually reaches `PLAN_DONE` and increments run count, plans older than 32 hours are rejected, version zero is rejected, null plan JSON is rejected, and a mutated hash is rejected.

The cancellation test submits a sleeping plan, cancels it, verifies `PLAN_CANCELLED`, submits again, and verifies cancelling with a wrong hash throws `NO_SUCH_PLAN`. The custom bandwidth test sets every `MoveStep` bandwidth to 100, submits the plan, and asserts the current work item carries that bandwidth.

## State and persistence behavior

Cluster storage exists but block movement is mocked. Disk balancer state is in-memory inside the `DiskBalancer` instance: current plan ID, status, background worker, and work entries. `TestMover` state is controlled by atomics/volatile fields and run count. Cluster shutdown occurs after each test.

## Dependencies and integration points

The file integrates plan JSON resources, planner output, live DataNode volume identity, `DiskBalancer` lifecycle validation, background worker status, and bandwidth propagation to work items.

## Risks and edge cases

- Mock mover does not validate actual block movement or dataset side effects.
- Sleep-based stuck-plan control must be cleared to avoid lingering background work.
- The cancellation test places cleanup calls inside a lambda after the expected exception path, so those statements are not reached when the wrong-hash cancellation throws.
- The plan resource must stay consistent with helper assumptions about disk layout.

## Test signals

Strong signals are explicit exception result codes for disabled, duplicate, old, invalid-version, null-plan, invalid-hash, and wrong-cancel cases; eventual `PLAN_DONE` with mover run count; `PLAN_CANCELLED`; and work-item bandwidth equal to custom step bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestDiskBalancerWithMockMover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestPlanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestPlanner.java

## Purpose

`TestPlanner` validates the disk balancer greedy planner and connector loading. It covers planning from JSON cluster fixtures, empty and single-volume edge cases, equal and unequal volume usage, threshold behavior, different disk sizes, scale, node-plan serialization, and large disk layouts.

## Important APIs and types

- `GreedyPlanner.balanceVolumeSet` generates `Step` entries in a `NodePlan`.
- `DiskBalancerCluster.computePlan` computes plans for selected nodes.
- `NullConnector` feeds synthetic model nodes directly; JSON connector loads `/diskBalancer/data-cluster-3node-3disk.json`.
- `DiskBalancerVolume`, `DiskBalancerVolumeSet`, and `DiskBalancerDataNode` model capacity and used data.
- `Step.getSourceVolume`, `getDestinationVolume`, `getBytesToMove`, `getSizeString`, and `getIdealStorage` expose planned movement.

## Control flow

Fixture-based tests load a three-node JSON cluster, read cluster info, select nodes, and invoke either direct volume-set balancing or cluster-level `computePlan`. Edge tests assert planner construction with null node works, empty clusters return non-null plan lists, and one-volume nodes produce no steps.

Synthetic volume tests build SSD volumes with controlled capacities and used sizes. Two-volume and three-volume equalization tests expect one move from the fullest to emptiest volume with a 10 GB size string. Equal disks produce no moves. A single full disk with two empty disks produces two roughly 33 GB moves. Threshold tests show 10 percent tolerance suppresses movement while one percent creates two roughly 18.6-18.8 GB moves. Different disk sizes produce moves to larger and smaller destinations proportional to ideal storage and assert ideal storage near 0.05714.

Connector, scale, serialization, and large-disk tests verify JSON resource connector class, a 256-disk random model producing some but fewer-than-disk-count steps, `NodePlan` JSON parse preserving step count, and a large mixed-capacity layout producing more than two steps.

## State and persistence behavior

Most tests are in-memory model tests. JSON fixture reads are classpath resource reads only. Random scale and serialization tests use random volumes generated by `DiskBalancerTestUtil`.

## Dependencies and integration points

This file is the planner algorithm regression suite for disk balancer. It integrates connector factory selection, model capacity/usage math, threshold semantics, move-step formatting, ideal storage computation, and node-plan JSON serialization.

## Risks and edge cases

- Some assertions depend on formatted size strings rather than raw bytes.
- Random scale test can theoretically produce no steps, though the test calls that unlikely.
- Planner tests focus on SSD volume sets except fixture tests; DISK-specific behavior is covered elsewhere.
- Regexes for rounded size strings encode current formatting precision.

## Test signals

Strong signals are expected source/destination choices, expected step counts, no-plan behavior for empty/equal/single-volume cases, threshold suppression and activation, proportional planning for different disk sizes, connector class resolution, scale bounds, node-plan serialization, and large-layout multi-step planning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestPlanner.java -->
