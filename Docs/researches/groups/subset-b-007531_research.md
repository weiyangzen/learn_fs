# Research: subset-b-007531

Grouped source research for Hadoop HDFS tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs`. Each section preserves its source path for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuotaAllowOwner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuotaAllowOwner.java

Purpose: validates the `dfs.permissions.allow.owner.set.quota` permission feature for `DFSAdmin` quota commands. The test proves that a non-superuser who owns a parent directory may set and clear namespace and space quotas on subdirectories when the feature is enabled, while unrelated users and same-group non-owners cannot, and that the same owner path is denied when the feature is disabled.

Important APIs and types: `MiniDFSCluster`, `HdfsConfiguration`, `DistributedFileSystem`, `DFSAdmin`, `ContentSummary`, `UserGroupInformation.doAs`, `DFSConfigKeys.DFS_PERMISSIONS_ALLOW_OWNER_SET_QUOTA_KEY`, `DFSConfigKeys.DFS_BLOCK_SIZE_KEY`, and the shared `TestQuota.runCommand` helper. The class uses JUnit 5 `@BeforeAll`, `@AfterAll`, and per-test `@Test` methods around static cluster state.

Control flow: `setUpClass` enables owner quota delegation and starts a three-DN cluster via `restartCluster`. `createDirssAndSetOwner` creates a parent directory, assigns owner/group, and creates a child. Positive tests run `DFSAdmin -setQuota`, `-setSpaceQuota`, `-clrQuota`, and `-clrSpaceQuota` as the owner inside a `UserGroupInformation` context and check `ContentSummary`. Negative tests run the same commands as unrelated users and expect `TestQuota.runCommand(..., true)` failure. `testOwnerCanNotSetIfNotEanbled` flips the config, restarts the cluster, verifies denial, then restores the feature in `finally`.

State and persistence behavior: the test mutates filesystem namespace ownership and quota metadata in the NameNode and exercises restart-sensitive configuration by tearing down and rebuilding the `MiniDFSCluster` when the feature flag changes. It does not persist state across JVM runs, but it does verify that the permission decision is bound to live NameNode configuration and current user identity rather than to group membership alone.

Dependencies and integration points: integrates the HDFS permission checker, quota RPCs behind `DFSAdmin`, UGI impersonation, NameNode quota metadata, and the existing `TestQuota` command harness. It depends on `dfs` static state being refreshed after each cluster restart.

Risks and edge cases: the test is sensitive to cluster restart cleanup because static `conf`, `cluster`, and `dfs` are shared. It checks owner and non-owner cases but not nested ownership changes beyond one parent-child level. The method name `createDirssAndSetOwner` and test name `testOwnerCanNotSetIfNotEanbled` contain typos only. A failure here would signal privilege escalation risk for quota management or an accidental regression disabling legitimate owner delegation.

Test signals: command return status from `TestQuota.runCommand`, `UserGroupInformation.getCurrentUser()`, `ContentSummary.getQuota()`, `ContentSummary.getSpaceQuota()`, and explicit success/failure expectations for superuser, owner, unrelated user, same-group user, and disabled-feature cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuotaAllowOwner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRead.java

Purpose: covers HDFS client read semantics around EOF behavior, reserved paths, interrupted reads, and DFSInputStream retry logging when DataNode fetches throw `IOException`.

Important APIs and types: `MiniDFSCluster`, `DFSTestUtil`, `FSDataInputStream`, `ByteBuffer`, `DFSClient`, `DFSInputStream`, `ShortCircuitTestContext`, `HdfsClientConfigKeys.DFS_CLIENT_CACHE_READAHEAD`, `DFS_CLIENT_MAX_BLOCK_ACQUIRE_FAILURES_KEY`, `DFSClientFaultInjector`, Mockito `Answer`, `GenericTestUtils.LogCapturer`, and a custom `DelayedSimulatedFSDataset`.

Control flow: `testEOF` writes files of selected lengths, reads into a zero-length buffer before and at EOF, and verifies direct-buffer reads near block boundaries. The EOF tests run once with short-circuit local reads and once with remote block reader configuration. `testReadReservedPath` opens a non-existent `/.reserved/.inodes/file` and expects `FileNotFoundException`, guarding against a deadlock regression. `testInterruptReader` installs `DelayedSimulatedFSDataset`, starts a reader blocked in `getBlockInputStream`, interrupts it, and expects an interrupt-derived `IOException`. The read-buffer logging tests inject a configured number of `fetchFromDatanodeException` failures and count WARN log messages for recoverable and terminal read attempts.

State and persistence behavior: all state is ephemeral in MiniDFS clusters. The most important state is client-side: DFSClient dead-node retry bookkeeping, block-acquire refresh count, captured logs, and the static fault injector. The code resets Mockito and clears captured logs in `finally` to prevent cross-test leakage.

Dependencies and integration points: integrates block reader local and remote paths, DFSInputStream retry strategy, client fault injection hooks, simulated DataNode storage, reserved path resolution, and log-level plumbing. The `DelayedSimulatedFSDataset.Factory` plugs into `DFS_DATANODE_FSDATASET_FACTORY_KEY`.

Risks and edge cases: the zero-length `ByteBuffer` expectations distinguish beginning-of-file from EOF and can catch subtle `read(ByteBuffer)` contract regressions. The interrupt test is timing-sensitive because it sleeps before interrupting a blocked reader. Logging assertions depend on exact message text and counts, which intentionally make retry behavior observable but can break on logging refactors. Static `DFSClientFaultInjector` must be reset.

Test signals: JUnit assertions on read return values, expected `FileNotFoundException`, interrupt exception class, `BlockMissingException`, log counts for "Retry with the current or next available datanode", "Failed to read from all available datanodes for file", and "Exception when fetching file /testfile.dat at position=".
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDNFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDNFailure.java

Purpose: parameterized EC read test that verifies online striped-file decoding remains correct when a tolerable number of DataNodes are shut down before reading.

Important APIs and types: `ReadStripedFileWithDecodingHelper`, `MiniDFSCluster`, `DistributedFileSystem`, `FILE_LENGTHS`, `NUM_DATA_UNITS`, `NUM_PARITY_UNITS`, `BLOCK_SIZE`, JUnit 5 parameterized tests with `@MethodSource`, and `@Timeout(300)`.

Control flow: `getParameters` creates the cross product of helper-provided file lengths with failure counts from one through the EC parity count. Each test case calls `setup`, delegates to `ReadStripedFileWithDecodingHelper.testReadWithDNFailure`, logs contextual failure information for small versus large files, and tears down the cluster in `finally`.

State and persistence behavior: uses static cluster and filesystem references per parameter case, but each test case explicitly initializes and tears them down. State under test is live DataNode availability and the client-side EC decoder's ability to reconstruct unavailable internal blocks from remaining data/parity cells.

Dependencies and integration points: relies almost entirely on `ReadStripedFileWithDecodingHelper` for cluster policy setup, file creation, DataNode shutdown, and read verification. Integrates HDFS striped block locations, EC policy constants, and client decode paths.

Risks and edge cases: the initializer assigns `this.fileLength = fileLength` instead of `pFileLength`, and `this.dnFailureNum = dnFailureNum` instead of `pDnFailureNum`; the fields default to zero unless the compiler/runtime path is corrected elsewhere, making this test vulnerable to silently exercising an unintended parameter combination. IOException is logged but not rethrown, which may hide failures. The intent is still clear: cover every tolerable failure count for small and large striped files.

Test signals: successful completion of helper verification, timeout protection, and failure log context showing file type and failure count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDNFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecoding.java

Purpose: tests striped EC client read and NameNode block-management behavior when internal EC blocks are corrupt, invalidated, or need parity/data decoding during reads.

Important APIs and types: `ReadStripedFileWithDecodingHelper`, `StripedFileTestUtil`, `LocatedStripedBlock`, `StripedBlockUtil.parseStripedBlockGroup`, `BlockManager`, `FSNamesystem`, `NameNodeAdapter`, `DatanodeDescriptor`, `DataNodeTestUtils`, `MiniDFSCluster.getBlockFile`, `cluster.corruptBlockOnDataNodes`, and `GenericTestUtils.waitFor`.

Control flow: setup creates a helper-initialized EC cluster for each test. `testReportBadBlock` writes a short file, locates the first internal data block file, overwrites it, disables heartbeats to keep the corrupt replica record visible, performs stateful read, and asserts corrupt replica count. `testInvalidateBlock` deletes a striped file while a DN heartbeat is disabled and checks the internal block reaches invalidate queues. `testCorruptionECBlockInvalidate` corrupts two data blocks, verifies both are reported corrupt after decoded read, selectively reenables heartbeats, and waits for each corrupt internal block to be invalidated. The remaining tests verify stateful reads with multiple corrupt blocks and a mixed data/parity corruption case.

State and persistence behavior: mutates actual MiniDFS block files and NameNode corrupt-replica/invalidate-block state. Heartbeats are deliberately disabled to freeze NameNode state for assertions and must be restored in `finally`. The tests exercise transient block reports, IBRs, corrupt replica maps, invalidation queues, and EC reconstruction interactions.

Dependencies and integration points: integrates filesystem writes, client striped reads, local DataNode storage files, NameNode `BlockManager`, corruption reporting RPCs, invalidation scheduling, and EC block group parsing. It depends on helper constants for cell size and unit counts.

Risks and edge cases: direct on-disk corruption can be storage-layout sensitive. Heartbeat disabling can leak if cleanup fails. The corruption/invalidation test encodes a specific race/regression around two corrupt data blocks and IBR ordering, so it is sensitive to asynchronous timing and uses waits. More-than-one-corrupted-block loops only up to less than parity count, keeping within decode tolerance.

Test signals: decoded reads must match expected bytes, corrupt replica map size reaches expected counts, invalidation queues contain the expected internal `Block`, and wait loops converge without timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingCorruptData.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingCorruptData.java

Purpose: slow parameterized EC read suite that corrupts a tolerable number of data and parity internal blocks before reading and verifies the client decoder returns correct file contents.

Important APIs and types: `ReadStripedFileWithDecodingHelper.getParameters`, `initializeCluster`, `tearDownCluster`, `testReadWithBlockCorrupted`, `MiniDFSCluster`, `DistributedFileSystem`, JUnit 5 `@ParameterizedTest`, `@MethodSource`, `@BeforeAll`, `@AfterEach`, `@Timeout(300)`, and `@Tag("slow")`.

Control flow: static setup creates an EC cluster. Parameter rows supply file length, data-block deletion/corruption count, and parity-block count. The test stores parameters, calls `setup` again, constructs a source path using the counts, and delegates to the helper with `delete=false` so blocks are corrupted rather than removed. `tearDown` shuts the cluster after each case.

State and persistence behavior: manipulates DataNode block contents for striped files in a live MiniDFS cluster and relies on helper logic to preserve enough parity/data cells for online decode. Static cluster state is repeatedly reinitialized and torn down, so cleanup sequencing matters.

Dependencies and integration points: delegates core EC policy setup, corruption, and read verification to `ReadStripedFileWithDecodingHelper`, integrating with `StripedFileTestUtil` through that helper. It is a regression lane for the client read path rather than NameNode reconstruction.

Risks and edge cases: setup is annotated `@BeforeAll` but also called inside the test after parameter initialization; with `@AfterEach` teardown this can be confusing and may leak or double-create cluster state if earlier initialization is not closed. The matrix is tagged slow because it multiplies file lengths by corruption combinations.

Test signals: the helper must complete read verification for each tolerable corruption combination without IOException or content mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingCorruptData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingDeletedData.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingDeletedData.java

Purpose: slow parameterized EC read suite that deletes, rather than corrupts, a tolerable number of data and parity internal blocks and verifies online decoding can satisfy stateful reads.

Important APIs and types: `ReadStripedFileWithDecodingHelper.getParameters`, `initializeCluster`, `tearDownCluster`, `testReadWithBlockCorrupted`, `MiniDFSCluster`, `DistributedFileSystem`, JUnit 5 parameterized test support, `@BeforeAll`, `@AfterAll`, `@Timeout(300)`, and `@Tag("slow")`.

Control flow: setup initializes a shared EC MiniDFS cluster. Each parameterized invocation saves the file length and data/parity missing counts, builds a path like `/deleted_<data>_<parity>`, and delegates to the helper with `delete=true`. Teardown occurs once after all cases.

State and persistence behavior: tests missing block files and/or missing block locations in a live EC cluster. Because the cluster is shared across all parameter combinations, generated paths include counts to avoid collisions and keep state distinguishable.

Dependencies and integration points: helper-driven integration with EC policy setup, DataNode storage mutation, and striped read verification. This lane complements the corrupt-data variant by exercising missing-block behavior instead of checksum/corruption detection.

Risks and edge cases: shared cluster state means one failed or partially cleaned parameter case can affect later cases. Coverage is bounded to helper-provided tolerable combinations; unrecoverable deletion counts are not expected to pass.

Test signals: successful helper read verification across file lengths and data/parity deletion counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithDecodingDeletedData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithMissingBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithMissingBlocks.java

Purpose: verifies striped-file reads when the NameNode returns block locations with some internal blocks missing because the corresponding DataNodes are down.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `BlockLocation`, `DatanodeInfo`, `ErasureCodingPolicy`, `DatanodeReportType.DEAD`, `StripedFileTestUtil.verifySeek`, `verifyStatefulRead`, `verifyPread`, and `DFSTestUtil.writeFile`.

Control flow: setup configures EC block size, disables replication max streams, starts `data + parity + 2` DNs, enables default EC policy, and creates a separate `DFSClient`. The test writes one striped file, waits for reports, verifies length, then iterates missing data counts and parity counts within decode tolerance. `readFileWithMissingBlocks` captures initial block locations, stops selected DNs by matching xfer ports in the first block location, asserts the new location list shrank, runs seek/stateful/pread verification, then restarts all dead DNs.

State and persistence behavior: deliberately changes cluster liveness and NameNode block location output without deleting file metadata. Restarting dead DNs and triggering heartbeats resets the cluster before the next combination.

Dependencies and integration points: integrates filesystem block-location API, DataNode liveness tracking, dead-node reports, client striped seek/read/pread implementations, and default EC policy geometry.

Risks and edge cases: `missingData` loop ranges up to the number of data blocks, while `missingParity` is bounded by parity minus missing data; this models recoverable missing sets. The DataNode stop routine relies on `BlockLocation.getNames()` order and port matching. The test uses a single file repeatedly and must restore DNs after each case.

Test signals: reduced block-location count after DN shutdown, successful seek/stateful/pread content verification, and dead DataNodes restarting cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadStripedFileWithMissingBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadWhileWriting.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadWhileWriting.java

Purpose: tests visibility and lease recovery semantics when one client reads a file while another client has written and flushed but not closed it, then a different user appends after soft lease expiry.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSOutputStream.hflush`, `HdfsDataInputStream.getVisibleLength`, `UserGroupInformation`, `RecoveryInProgressException`, `RemoteException`, lease limits via `cluster.setLeasePeriod`, and `DFSTestUtil.getFileSystemAs`.

Control flow: the test starts a four-DN cluster, shortens heartbeat and soft lease limits, creates a file, writes half a block, and hflushes without closing. `checkFile` opens as another user, checks visible length, and reads expected byte values. The original lease renewer is interrupted; after sleeping beyond soft lease limit a different UGI opens a new filesystem and retries `append` until lease recovery completes, writes another half block, and closes. A final read checks the full block.

State and persistence behavior: exercises under-construction file length visibility, client lease renewal, soft lease expiry, append lease recovery, and completed-file length after close. The hard lease remains long so the scenario specifically depends on soft-limit takeover.

Dependencies and integration points: integrates DFS output hflush, HDFS visible length semantics, lease renewer, append recovery RPCs, UGI-based clients, and cross-user filesystem access.

Risks and edge cases: timing-sensitive due to sleep-based lease expiry and retry loops. `append` catches only `RecoveryInProgressException` wrapped in `RemoteException`. The test writes the same byte sequence twice with offset zero, so final read expects modulo half-block sequence repeated rather than a strictly increasing full-block sequence.

Test signals: `getVisibleLength() >= expectedsize`, byte-by-byte read equality, append eventually succeeds after recovery, and no unexpected RemoteException escapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReadWhileWriting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFile.java

Purpose: comprehensive EC reconstruction suite for HDFS striped files. It verifies data/parity internal block reconstruction across file lengths, failure types, task submission, NameNode scheduling, DataNode xmit accounting, timeout handling, and buffer-pool hygiene.

Important APIs and types: `ErasureCodingPolicy`, `MiniDFSCluster`, `DistributedFileSystem`, `LocatedStripedBlock`, `StripedBlockUtil.constructInternalBlock`, `BlockManager`, `BlockManagerTestUtil`, `BlockECReconstructionInfo`, `DataNodeFaultInjector`, `ElasticByteBufferPool`, `ErasureCodingTestHelper`, `ErasureCodeNative`, `NativeRSRawErasureCoderFactory`, `GenericTestUtils`, `LambdaTestUtils`, and `@TempDir`.

Control flow: setup derives EC geometry, configures small reconstruction read buffers, redundancy intervals, native RS coder if available, pending timeout, and optional validation. It starts enough DNs to hold one block group plus spare targets and maps DataNode IDs to cluster indices. The main reconstruction tests call `assertFileBlocksReconstruction` with combinations of parity-only, data-only, and random failures. That helper writes a striped file, records original internal block replicas, lengths, generation stamps, and bytes, shuts down or corrupts selected DataNodes, waits for reconstruction, finds target DNs, and asserts reconstructed replica length, metadata, and content.

State and persistence behavior: the suite mutates real MiniDFS block files, DataNode liveness, corrupt replica state, pending reconstruction queues, xmits-in-progress counters, and EC worker buffer pools. It also exercises NameNode task scheduling and timeout rescheduling. State is reset per test through cluster teardown, but individual tests may deliberately restart the cluster with modified configuration.

Dependencies and integration points: integrates NameNode `BlockManager` reconstruction scheduling, DataNode `ErasureCodingWorker`, DataTransfer reads, raw erasure coder selection, storage reports, block metadata files, DataNode fault injection, metrics/counters, and client-visible read validation via `StripedFileTestUtil`.

Risks and edge cases: direct file and metadata inspection is storage-layout sensitive but provides strong regression coverage. Random dead block selection can make failures less reproducible unless seeded externally. Several tests are asynchronous and depend on timeouts, barriers, and fault injectors; cleanup of `DataNodeFaultInjector` is critical. The suite intentionally covers short files, partial groups, all parity loss, all recoverable data loss, worker task submission with invalid task parameters, block writer initialization failure buffer cleanup, dead-source rescheduling, and stale reader futures.

Test signals: reconstructed block files must match original bytes and generation-stamp metadata; NameNode pending reconstruction counts drain without timeout; DataNode xmits weights match configured multipliers; buffer pool entries return with position zero; invalid EC task submission does not throw; and `StripedFileTestUtil.waitForReconstructionFinished` converges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithRandomECPolicy.java

Purpose: reuses the full `TestReconstructStripedFile` suite with a randomly selected non-default EC policy, broadening reconstruction coverage beyond the system default policy geometry.

Important APIs and types: subclassing `TestReconstructStripedFile`, `ErasureCodingPolicy`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, JUnit `@Tag("slow")`, and SLF4J logging.

Control flow: the constructor selects a non-default EC policy and logs it. `getEcPolicy` is overridden so the inherited setup, tests, helper methods, and assertions run with that policy's data/parity/cell-size parameters.

State and persistence behavior: inherits all MiniDFS cluster, block file, reconstruction queue, and DataNode state behavior from the parent suite. The only local state is the selected `ecPolicy` field.

Dependencies and integration points: depends on `StripedFileTestUtil` policy selection and the parent class honoring `getEcPolicy` for all derived geometry.

Risks and edge cases: random policy selection increases coverage but reduces reproducibility unless the helper logs enough policy detail for triage. Because all inherited tests execute, policies with smaller parity counts may skip assumption-guarded tests or alter failure matrix boundaries.

Test signals: all inherited reconstruction assertions pass under the chosen non-default EC policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithValidator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithValidator.java

Purpose: extends striped-file reconstruction tests with EC reconstruction validation enabled, specifically proving that polluted decoder outputs are rejected once and then correctly reconstructed by a later task.

Important APIs and types: `TestReconstructStripedFile` inheritance, `DataNodeFaultInjector.badDecoding`, `DataNodeMetrics.getECInvalidReconstructionTasks`, `ByteBuffer`, `AtomicBoolean`, and overridden `isValidationEnabled` and `getPendingTimeout`.

Control flow: constructor logs validator mode. `testValidatorWithBadDecoding` checks all DataNode invalid reconstruction counters start at zero, installs a fault injector that mutates decoder output buffers once, calls inherited `assertFileBlocksReconstruction` for all parity-unit data losses, then sums `ECInvalidReconstructionTasks` and expects exactly one invalid task. The injector is restored in `finally`.

State and persistence behavior: enables `DFS_DN_EC_RECONSTRUCTION_VALIDATION_KEY` through parent setup and shortens pending timeout to 10 seconds so failed reconstruction is rescheduled promptly. It mutates transient decoder buffers, DataNode metrics, and reconstruction task state.

Dependencies and integration points: integrates DataNode EC validation, metrics accounting, fault injection, and parent replica-content assertions. It depends on parent setup reading `isValidationEnabled` and `getPendingTimeout` polymorphically.

Risks and edge cases: the injector modifies output buffer contents in-place and must reset buffer marks correctly. The expected metric sum of one assumes only the first poisoned decode fails and later retry succeeds. A failure could indicate validation is disabled, metric accounting broke, or corrupted data was accepted.

Test signals: inherited reconstruction content checks pass, and cluster-wide `ECInvalidReconstructionTasks` metric sum is exactly one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReconstructStripedFileWithValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRenameWhileOpen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRenameWhileOpen.java

Purpose: verifies HDFS edit-log and fsimage persistence for files that remain open while their parent directory or file path is renamed, including restart and lease recovery scenarios.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream`, `FSEditLog`, Mockito `spy`, `DFSTestUtil.setEditLogForTesting`, `TestFileCreation`, `DFS_NAMENODE_HEARTBEAT_RECHECK_INTERVAL_KEY`, `DFS_HEARTBEAT_INTERVAL_KEY`, and `DFS_NAMENODE_SAFEMODE_THRESHOLD_PCT_KEY`.

Control flow: each test creates one or more open files, hflushes them, performs a rename while the stream remains open, shuts down and restarts the cluster without formatting once or twice, then verifies old paths are gone and new paths exist. `testWhileOpenRenameParent` also spies the edit log so `endCurrentLogSegment` is not called, creates and renames another file with a pending add-block operation, stops the NameNode before closing, and validates edit-log replay.

State and persistence behavior: exercises lease persistence in fsimage and edit logs, rename records for open files, pending add-block edit replay, and path reconstruction across NameNode restarts. Streams are intentionally not closed before shutdown to keep leases active.

Dependencies and integration points: integrates file creation helpers, NameNode edit log, lease manager, rename semantics, fsimage reload, edit replay, and MiniDFSCluster restart with `format(false)`.

Risks and edge cases: `checkFullFile` is currently a no-op because lease recovery validation is commented, so path existence is the primary signal. The tests use sleeps for IPC idle and restart timing. The first test modifies the NameNode edit log through a spy, a brittle but targeted way to force replay coverage.

Test signals: old open-file paths no longer exist, renamed paths exist after restart(s), independent file paths still exist, and cluster reload succeeds with active leases and pending add-block edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRenameWhileOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeFailureReplication.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeFailureReplication.java

Purpose: verifies write-pipeline behavior when DataNodes fail and `dfs.client.block.write.replace-datanode-on-failure.min.replication` controls whether the client can continue with fewer live replicas or must fail.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `HdfsDataOutputStream.getCurrentBlockReplication`, `ReplaceDatanodeOnFailure.write(Policy.ALWAYS, ...)`, `HdfsClientConfigKeys.BlockWrite.ReplaceDatanodeOnFailure.MIN_REPLICATION`, `SubjectInheritingThread`, `FSDataInputStream`, and rack-aware cluster setup.

Control flow: `setupCluster` configures the minimum replacement replication threshold and starts three DNs on one rack. The main helper starts one or more `SlowWriter` threads that write incrementing bytes and hflush, waits, stops DataNodes at a selected pipeline position, waits again, checks current block replication or expected failure, interrupts writers, closes streams, and verifies file contents. Dedicated tests fail the first or last DN, leave only one DN alive, and check behavior when live DNs are below the configured threshold.

State and persistence behavior: mutates active write pipelines, DataNode liveness, client block-output stream replication tracking, and partially written file contents. It does not require NameNode restart, but relies on block reports after DN failures.

Dependencies and integration points: integrates client-side pipeline replacement policy, DataTransfer write pipeline, hflush visibility, rack configuration, and DataNode stop behavior.

Risks and edge cases: slow writer timing and sleep durations make the suite timing-sensitive. Expected exception behavior depends on the precise threshold and best-effort flag. The content verifier returns after the first EOF, so it verifies files sequentially but exits the method on the first completed file; this limits multi-file verification depth.

Test signals: `getCurrentBlockReplication()` equals configured minimum for survivable cases, IOException is thrown when replacement cannot satisfy minimum replication, writers close cleanly, and file byte sequences match write order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeFailureReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeOnFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeOnFailure.java

Purpose: tests the default and configured `ReplaceDatanodeOnFailure` policies for client write pipelines, including active replacement with new DNs, append behavior with insufficient DNs, and best-effort replacement.

Important APIs and types: `ReplaceDatanodeOnFailure`, `Policy.ALWAYS`, `DataTransferProtocol.LOG`, `MiniDFSCluster`, `HdfsDataOutputStream`, `DatanodeInfo`, `GenericTestUtils.waitFor`, `SubjectInheritingThread`, `FSDataOutputStream`, and `FileStatus`.

Control flow: `testDefaultPolicy` exhaustively computes expected `satisfy` decisions for replication factors, existing pipeline sizes, append flags, and hflush flags. `testReplaceDatanodeOnFailure` starts writers, adds replacement DNs on another rack, stops an old DN, starts more writers, waits until all output streams report full replication, stops writers, and reads back content. `testAppend` validates that an empty file with replication 3 can be created on one DN and appended once, but a second append fails. `testBestEffort` enables always-replace without throwing on failure and verifies create/append can succeed with only one DN.

State and persistence behavior: exercises live pipeline composition, current block replication reporting, block placement across newly started DNs, and append state. Files are not persisted across cluster restart.

Dependencies and integration points: integrates client policy calculation, DataTransfer pipeline replacement, NameNode DataNode selection with load consideration disabled in one test, rack placement, and HDFS append semantics.

Risks and edge cases: the policy matrix is precise and catches semantic drift in default replacement conditions. Threaded writer tests are timing-sensitive and depend on replication reaching full count within 10 seconds. Append tests model under-provisioned clusters where logical file replication remains 3 even if physical availability is lower.

Test signals: boolean policy decisions match expected truth table, writer streams report replication 3, file contents match sequential writes, second append throws when replacement is not best effort, and best-effort append succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeOnFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplication.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplication.java

Purpose: broad replication suite covering rack-aware placement, bad-block reports during transfer, pending replication retry, mismatched replica lengths, corruption handling, late IBRs, and under-construction replication.

Important APIs and types: `MiniDFSCluster`, `DFSClient`, `ClientProtocol`, `LocatedBlocks`, `BlockLocation`, `DatanodeInfo`, `SimulatedFSDataset`, custom `CorruptFileSimulatedFSDataset`, `MaterializedReplica`, `BlockManagerTestUtil`, `InternalDataNodeTestUtils`, `GenericTestUtils.DelayAnswer`, `DataNodeTestUtils`, `MetricsAsserts`, and `AppendTestUtil`.

Control flow: `checkFile` waits for expected replication then verifies block topology paths and rack diversity. `runReplication` creates files with several replication factors on real or simulated storage and checks placement. Bad-block transfer tests use either a simulated dataset that throws on reads or missing/corrupt materialized replicas, then increase replication and assert the destination reports bad blocks and replication does not complete from corrupt sources. Retry tests corrupt/delete replicas on disk, restart with more DNs and short pending timeout, and wait for full replication. Later tests alter replica length, inject corrupt replicas, delay `blockReceivedAndDeleted`, and mark a block corrupt in an under-construction file.

State and persistence behavior: directly manipulates on-disk replicas, DataNode datasets, NameNode corrupt-block metadata, pending reconstruction queues, block reports, IBR timing, and DataNode replication metrics. Some tests persist state across cluster shutdown/restart with `format(false)`.

Dependencies and integration points: integrates rack-aware block placement, DataNode block transfer validation, checksum/corruption reporting, NameNode pending reconstruction, safe-mode thresholds during restart, IBR handling, metrics, and under-construction file behavior.

Risks and edge cases: tests are asynchronous and can time out if block reports or replication work do not schedule promptly. The simulated corrupt dataset throws after successful underlying reads to model transfer failure. Direct replica deletion/corruption is filesystem-layout sensitive. `testNoExtraReplicationWhenBlockReceivedIsLate` guards against over-replication caused by late IBRs by asserting `BlocksReplicated` remains zero.

Test signals: expected replica counts and rack topology, corrupt block flags, successful full replication after retries, truncation detected as corrupt while extension can replicate, no extra replication when IBRs arrive late, and proper replication of non-last blocks in under-construction files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReservedRawPaths.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReservedRawPaths.java

Purpose: tests the special `/.reserved/raw` namespace used to access encrypted HDFS data without decryption, plus path resolution, status/listing behavior, and access control around raw paths.

Important APIs and types: `MiniDFSCluster`, `HdfsAdmin`, `JavaKeyStoreProvider`, `CreateEncryptionZoneFlag.NO_TRASH`, `FSDirectory.resolvePath`, `INodesInPath`, `EncryptionZoneManager`, `FileSystemTestWrapper`, `FileContextTestWrapper`, `UserGroupInformation`, `AccessControlException`, and `DFSTestUtil.verifyFilesEqual/NotEqual`.

Control flow: setup configures a JKS key provider, starts a one-DN cluster, wires the client key provider to the NameNode provider, and creates an encryption key. Tests verify raw path resolution strips `/.reserved/raw` while setting `INodesInPath.isRaw`, raw encrypted bytes differ from decrypted EZ reads, raw non-EZ reads equal normal reads, status paths resolve to the same underlying inode, root and relative raw paths canonicalize, mkdir works as superuser through raw paths, non-admins can read/list but cannot create/mkdir raw paths, and `/.reserved` listing exposes `raw` and `.inodes` appropriately.

State and persistence behavior: creates encryption zones, encrypted and unencrypted files, permissions, and namespace entries. It does not restart the cluster, but it exercises raw path normalization against live FSDirectory state and key-provider-backed encryption metadata.

Dependencies and integration points: integrates HDFS encryption zones, raw reserved path resolver, FileSystem and FileContext wrappers, key provider flushing, permission checks, listing APIs, and FSDirectory constants.

Risks and edge cases: raw access is security-sensitive; tests distinguish read/list permissions from write/mkdir superuser requirements. Path construction includes unusual relative forms and a nested path under `/.reserved/raw` to catch normalization bugs. `assertPathEquals` uses access/modification times as inode identity proxies rather than comparing inode IDs directly.

Test signals: raw flag and resolved path values, byte equality/inequality, expected `AccessControlException` messages, `FileNotFoundException` for `/.reserved/.inodes`, listing names and recursive raw paths matching expected regexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReservedRawPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRestartDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRestartDFS.java

Purpose: validates that HDFS namespace, file contents, root metadata, directory owner/group metadata, and optional service RPC configuration survive two consecutive MiniDFSCluster restarts without formatting.

Important APIs and types: `MiniDFSCluster`, `DFSTestUtil.Builder`, `FileSystem`, `FileStatus`, `Path`, `DFS_NAMENODE_SERVICE_RPC_ADDRESS_KEY`, and JUnit assertions.

Control flow: `runTests` optionally enables a service RPC address, starts a four-DN cluster, creates 20 test files under `/srcdat`, records root and directory status, mutates root owner and directory group, then shuts down. It restarts with `format(false)`, checks files and metadata, records root mtime again, shuts down, and restarts a second time to verify the image written during the first restart is still correct. Two JUnit methods run this with and without service RPC enabled.

State and persistence behavior: explicitly tests fsimage/edit persistence across restarts, including owner/group mutations and root modification time preservation. The second restart checks that the post-restart image/checkpoint is not corrupted.

Dependencies and integration points: integrates MiniDFSCluster restart semantics, NameNode storage formatting flags, FileSystem status APIs, owner mutation, and `DFSTestUtil` file creation/check/cleanup.

Risks and edge cases: does not inspect block placement or replication beyond `DFSTestUtil.checkFiles`. The same `Configuration` object is reused and re-mutated for service RPC address. Failures usually indicate storage image/edit replay regressions.

Test signals: `files.checkFiles` returns true after each restart, root mtime and owner/group values match expectations, directory owner/group values match expectations, and cleanup succeeds after the final restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRestartDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgrade.java

Purpose: large slow suite for rolling-upgrade command handling, QJM/HA behavior, rollback/finalize/query semantics, checkpoint interactions, DataNode upgrade commands, JMX exposure, and secondary NameNode compatibility.

Important APIs and types: `DistributedFileSystem.rollingUpgrade`, `RollingUpgradeAction.PREPARE/QUERY/FINALIZE`, `RollingUpgradeInfo`, `DFSAdmin`, `MiniDFSCluster`, `MiniJournalCluster`, `MiniQJMHACluster`, `SafeModeAction`, `FSImage`, `NNStorage`, `SecondaryNameNode`, `CheckpointFaultInjector`, `NameNodeInfo` JMX `RollingUpgradeStatus`, `StartupOption`, and HA utilities.

Control flow: DFSAdmin tests validate CLI argument handling, safe-mode prepare, query, finalize, JMX status, restart persistence, and namespace visibility before/during/after upgrade. QJM tests start clusters sharing journal dirs, copy image dirs, transfer ownership to another NameNode, reject `-upgrade` during rolling upgrade, and finalize. Rollback helper tests repeatedly prepare, mutate namespace and truncate a file, roll edits/restart, then restart NameNode with `-rollingUpgrade rollback` and verify pre-upgrade state. Finalize/query/checkpoint tests run in multi-NN QJM HA topologies, check rollback image creation/removal, tail edits, restarts, and checkpoint files. Additional tests cover `DFSAdmin -shutdownDatanode upgrade`, edit-log tailer flags, and SecondaryNameNode checkpoints while rolling upgrade is prepared.

State and persistence behavior: heavily exercises fsimage rollback images, edit logs, QJM journal segments, HA standby checkpoint state, JMX rolling-upgrade state, DataNode shutdown state, and namespace rollback/finalize persistence. Many tests intentionally restart NameNodes and clusters with specific startup options.

Dependencies and integration points: integrates DFSAdmin CLI, NameNode RPC rolling-upgrade APIs, safe mode, QJM, HA tailing/checkpointing, FSImage rollback image management, JMX, DataNode admin commands, file truncate recovery, and SecondaryNameNode checkpointing.

Risks and edge cases: asynchronous HA tailing and checkpoint creation require waits and can be timing-sensitive. Some tests set `RECENT_IMAGE_CHECK_ENABLED` to skip image delta checks. `CheckpointFaultInjector` must be restored. Rolling-upgrade correctness is high risk because it gates downgrade/rollback safety and journal cleanup.

Test signals: DFSAdmin return codes, `RollingUpgradeInfo` fields, JMX bean null/non-null state, path existence after prepare/finalize/rollback, rollback image presence/absence, successful NameNode restarts with replayed finalize ops, checkpoint image txids, standby `isNeedRollbackFsImage` flag, and DataNode shutdown command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeDowngrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeDowngrade.java

Purpose: verifies the obsolete rolling-upgrade downgrade path is rejected, both for active HA rolling-upgrade state and for a newer/future fsimage layout version.

Important APIs and types: `MiniQJMHACluster`, `MiniDFSCluster`, `DistributedFileSystem`, `RollingUpgradeAction.PREPARE`, `RollingUpgradeInfo`, `NNStorage`, `NameNodeLayoutVersion`, Mockito `spy` and `doReturn`, `SafeModeAction`, and `Assertions.assertThrows`.

Control flow: `testDowngrade` wraps the whole HA scenario in an expected `IllegalArgumentException`. It starts HA QJM, prepares rolling upgrade, creates namespace changes, queries for rollback image preparation, then attempts `restartNameNode(..., "-rollingUpgrade", "downgrade")`. `testRejectNewFsImage` saves namespace, spies `NNStorage` to report a future service layout version, writes storage metadata, and attempts downgrade restart, also expecting `IllegalArgumentException`.

State and persistence behavior: manipulates rolling-upgrade state, rollback images, fsimage storage metadata, service layout version, and NameNode restart options. The tests intentionally assert rejection rather than successful namespace mutation.

Dependencies and integration points: integrates rolling-upgrade startup option parsing, HA/QJM, storage layout version checks, safe-mode namespace saving, and Mockito storage spying.

Risks and edge cases: because `assertThrows` wraps broad setup and cleanup, an unexpected earlier `IllegalArgumentException` would also satisfy the test unless stack/context is inspected. The storage spy writes a future layout version to disk, so cleanup through cluster shutdown is important.

Test signals: `IllegalArgumentException` is thrown when downgrade is requested in both obsolete-downgrade scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeDowngrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeRollback.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeRollback.java

Purpose: verifies rollback of rolling-upgrade state for standalone NameNode, QJM, and HA QJM deployments, including exact storage/journal file effects.

Important APIs and types: `MiniDFSCluster`, `MiniJournalCluster`, `MiniQJMHACluster`, `DistributedFileSystem`, `DFSAdmin`, `RollingUpgradeAction.PREPARE`, `RollingUpgradeInfo`, `NameNode.createNameNode`, `NNStorage`, `INode`, and storage file-name helpers for finalized/in-progress/trash edit logs and rollback images.

Control flow: helper `checkNNStorage` asserts expected finalized edits, in-progress edits, trashed edits, and image/rollback image files. `checkJNStorage` asserts finalized and `.trash` journal files. `testRollbackCommand` prepares rolling upgrade, creates `/bar`, checks pre-rollback storage, starts a NameNode with `-rollingUpgrade rollback`, verifies `/foo` remains and `/bar` is gone, then checks trashed edit/image state. QJM and HA tests run similar namespace prepare/mutate/rollback flows and validate journal dirs plus HA standby rollback image preparation.

State and persistence behavior: focuses on persistent NameNode storage and journal state: rollback fsimage files, discarded edit segments renamed to `.trash`, in-progress edit segments for future txids, and namespace contents after rollback. HA test restarts NN0 with rollback, shuts down NN1, transitions NN0 active, and verifies rolling upgrade can be prepared again after rollback.

Dependencies and integration points: integrates DFSAdmin rolling-upgrade prepare, NameNode startup rollback option, QJM journal storage, HA standby checkpointing, FSDirectory inode lookup, and `TestRollingUpgrade.queryForPreparation`.

Risks and edge cases: exact txid expectations make the tests sensitive to edit-log sequence changes. One loop in QJM uses `mjc.getCurrentDir(0, JOURNAL_ID)` for each journal index, which may limit per-JN validation. The TODO notes rollback may not succeed in all journal nodes, signaling known coverage or robustness concern.

Test signals: namespace path existence/non-existence after rollback, storage files and `.trash` segments exist at expected txids, both active and standby have rollback images before HA rollback, restart after rollback succeeds, and rolling upgrade can be prepared again.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeRollback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeMode.java

Purpose: validates HDFS safe mode behavior across manual safe mode, startup thresholds, replication queue initialization, under-construction blocks, operation restrictions, DataNode minimum threshold, utility APIs, and block-location behavior with zero locations.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `SafeModeAction`, `NameNodeAdapter`, `FSNamesystem`, `BlockManagerTestUtil`, `SafeModeException`, `RemoteException`, `FSDataOutputStream`, ACL and xattr APIs, `UserGroupInformation`, `ErasureCodingPolicy`, `ECSchema`, and metrics `StorageBlockReportNumOps`.

Control flow: setup creates a one-DN cluster with ACLs and xattrs enabled. `testManualSafeMode` creates files, restarts with zero DNs, enters manual safe mode, starts a DN, and verifies safe mode does not auto-exit until explicitly left. Other tests verify immediate exit when no blocks exist, replication queues initialize once threshold crosses, RBW blocks are not treated as missing on restart, mutation APIs fail with safe-mode exceptions while reads/access checks behave as expected, min DataNode thresholds keep NN in safe mode, `isInSafeMode` follows enter/leave, and block locations throw safe-mode exception only when no locations are available.

State and persistence behavior: exercises NameNode safe-mode flags, manual versus automatic safe-mode state, block safe counts, under-replicated queues, RBW/open-file block state, ACL/xattr and EC policy mutation restrictions, DataNode liveness, and startup after shutting down DNs/NameNode.

Dependencies and integration points: integrates NameNode startup safe-mode thresholds, block reports, replication queue initialization, filesystem operation permission paths, ACL/xattr subsystems, EC policy admin APIs, UserGroupInformation access checks, and metrics.

Risks and edge cases: many assertions depend on exact safe-mode status text, including newline formatting. Sleep-based waits and block-report counters can be timing-sensitive. The operation restriction test is broad and can reveal unrelated safe-mode enforcement regressions across quota, permissions, ACLs, xattrs, append, truncate, delete, rename, replication, and EC policy APIs.

Test signals: safe-mode GET/ENTER/LEAVE return values, exact status strings, safe block counts, replication queue counts, expected `SafeModeException` or `RemoteException` classes/messages, allowed read/getAclStatus/read-access operations, min-DN status message, and block-location success/failure under different safe-mode location availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFile.java

Purpose: verifies NameNode safe-block accounting for striped EC files, especially small block groups that require fewer than the full number of data units to be considered safe.

Important APIs and types: `ErasureCodingPolicy`, `MiniDFSCluster`, `NameNodeAdapter.getSafeModeSafeBlocks`, `LocatedBlocks`, `DatanodeInfo`, `StripedFileTestUtil`, `DFSTestUtil.writeFile`, and `DFS_BLOCKREPORT_INTERVAL_MSEC_KEY`.

Control flow: setup derives EC geometry, sets block size and frequent block reports, starts exactly `data + parity` DNs, enables the EC policy, and sets it on root. `testStripedFile0` writes a one-cell small block group requiring one storage; `testStripedFile1` writes a small group of `dataBlocks - 1` cells requiring that many storages. `doTest` also writes a larger two-block-group file so startup safe-mode has meaningful threshold, stops all DNs while preserving the small-file DNs first in the restart list, restarts the NameNode, then restarts DNs one by one and asserts safe-block count and final safe-mode exit at the expected points.

State and persistence behavior: tests safe-mode state after NameNode restart with all DataNodes down, then incremental block-report processing as DataNodes return. It observes safe block counts for striped blocks under EC minimum storage rules.

Dependencies and integration points: integrates EC block group location reporting, NameNode safe-mode safe-block calculations, DataNode restart/block report flow, and default EC policy geometry.

Risks and edge cases: ordering of stopped/restarted DNs is important because the first restarted DNs are those containing the small file. If block location ordering changes, the test could become flaky. It assumes the large file needs `dataBlocks` storages for its two blocks to count safe and exit safe mode.

Test signals: initial safe-mode true with zero safe blocks, no increment before `minStorages`, increment to one at `minStorages`, continued safe-mode until enough large-file storages report, and final safe-mode false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFileWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFileWithRandomECPolicy.java

Purpose: reuses `TestSafeModeWithStripedFile` with a random non-default EC policy to ensure safe-mode safe-block accounting works across different EC geometries.

Important APIs and types: subclassing `TestSafeModeWithStripedFile`, `ErasureCodingPolicy`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, and SLF4J logging.

Control flow: constructor selects and logs a non-default EC policy. `getEcPolicy` returns that policy, causing inherited setup and tests to compute data/parity counts, cell size, DataNode count, block size, and minimum storage expectations from the selected policy.

State and persistence behavior: inherits all striped safe-mode cluster state behavior from the parent class. Local state is only the selected EC policy.

Dependencies and integration points: depends on the parent suite using `getEcPolicy` polymorphically and on `StripedFileTestUtil` returning a valid enabled system policy.

Risks and edge cases: random policy selection improves breadth but can make failures less reproducible. Policies with different data/parity counts alter the timing and number of DataNode restarts needed to exit safe mode.

Test signals: inherited safe-mode safe-block assertions pass under the selected non-default EC policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFileWithRandomECPolicy.java -->
