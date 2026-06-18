# subset-b-007528 Research

Grouped source research for Hadoop HDFS tests covering external block readers, checksum input/output paths, image fetch, append and lease recovery behavior, file checksum semantics, corruption handling, file creation, and restart visibility. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExternalBlockReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExternalBlockReader.java

## Purpose

`TestExternalBlockReader.java` validates DFSClient integration with configured external `ReplicaAccessorBuilder` implementations. The complete 337-line test file was read. It covers both safe fallback when the external builder class is misconfigured and the positive path where HDFS reads a block through a synthetic short-circuit replica accessor.

## Important APIs, Types, and Functions

Key APIs are `HdfsClientConfigKeys.REPLICA_ACCESSOR_BUILDER_CLASSES_KEY`, `ReplicaAccessorBuilder`, `ReplicaAccessor`, `MiniDFSCluster`, `DistributedFileSystem`, `HdfsDataInputStream`, `ReadStatistics`, `DFSTestUtil.createFile`, and `DFSTestUtil.getFirstBlock`. The nested `SyntheticReplicaAccessorBuilder` records file name, block ID, block pool ID, generation stamp, checksum flag, client name, short-circuit permission, visible length, and configuration. The nested `SyntheticReplicaAccessor` implements positional reads into deterministic bytes, `ByteBuffer` reads, close accounting, locality flags, network distance, generation stamp reporting, and error accumulation.

## Control Flow

`testMisconfiguredExternalBlockReader` starts a one-node cluster with a nonexistent builder class, creates `/a`, reads the whole file, and verifies that normal HDFS reading still returns seed-derived contents. `testExternalBlockReader` configures the nested builder, tags the test with a UUID, creates a two-block-ish file, seeks and reads ranges that cross the block split, then verifies read statistics and builder state. The builder deliberately returns `null` for replicas with visible length under 1024 so DFSClient can fall back to normal readers for smaller fragments.

## State and Persistence Behavior

The persistent state is only MiniDFSCluster block data. Test-only state is the static `accessors` map keyed by UUID and each accessor's counters. It checks no file-backed persistence, but it validates that block metadata passed into external accessors matches the NameNode/DataNode state.

## Dependencies and Integration Points

The test integrates DFSClient block reader selection, short-circuit/local read accounting, block tokens via builder setter coverage, `NetUtils.getLocalHostname`, and deterministic `DFSTestUtil` file content generation.

## Risks and Edge Cases

Important risks are broken fallback from invalid builder class names, incorrect visible-length handling at block boundaries, leaked external accessors, wrong generation stamp or block pool metadata, and read-statistics drift when an accessor returns `null`.

## Test Signals

Signals are exact byte equality, `ReadStatistics` totals, accessor construction count, captured builder fields, close count, total synthetic bytes read, empty synthetic error string, EOF behavior at `TEST_LENGTH`, and successful cluster shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestExternalBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSInputChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSInputChecker.java

## Purpose

`TestFSInputChecker.java` exercises checksum-aware input stream reads for HDFS and local filesystems. The complete 382-line file was read. It verifies reads, seeks, skips, checksum verification toggling, `seek` plus read behavior, and explicit local checksum/data corruption detection.

## Important APIs, Types, and Functions

Key APIs are `FSDataInputStream`, `FSDataOutputStream`, `FileSystem`, `LocalFileSystem`, `ChecksumException`, `IOUtils.readFully`, `IOUtils.skipFully`, `FsPermission`, and `MiniDFSCluster`. Constants set tiny checksum and block geometry: `BYTES_PER_SUM=10`, `BLOCK_SIZE=20`, `HALF_CHUNK_SIZE=5`, and `FILE_SIZE=39`. Helpers include `writeFile`, `checkReadAndGetPos`, `checkSeek`, `checkSkip`, `testChecker`, `testFileCorruption`, `checkFileCorruption`, `testSeekAndRead`, and `readAndCompare`.

## Control Flow

`testFSInputChecker` seeds expected bytes, configures HDFS block and checksum sizes, runs the checker against HDFS with checksum verification enabled and disabled, then repeats against `LocalFileSystem` and adds corruption checks. `checkReadAndGetPos` reads across checksum and block boundaries while checking `getPos`. `checkSeek` probes checksum-aligned, non-aligned, same-chunk, and EOF seeks. `checkSkip` validates successful skips and exact `EOFException` messages for over-skips. Local corruption rewrites either the `.crc` sidecar or the data file through `RandomAccessFile` and expects `ChecksumException`.

## State and Persistence Behavior

The tests create temporary `try.dat` files and local `.crc` sidecars, then delete them. HDFS state is transient MiniDFSCluster block data. The class keeps per-test expected bytes, actual buffers, stream handle, and deterministic random state.

## Dependencies and Integration Points

It covers `FSInputChecker` behavior indirectly through HDFS and local filesystem streams, local checksum sidecar handling, HDFS checksum configuration, and shared Hadoop IO utilities.

## Risks and Edge Cases

Risks include off-by-one positions around checksum chunks, incorrect skip EOF accounting, stale checksum verification flags on `FileSystem`, and local corruption paths that must throw checksum errors without masking other IO failures.

## Test Signals

Signals are byte-for-byte comparisons with buffer erasure after checks, exact stream positions, expected `EOFException` messages, `markSupported=false`, no cleanup leftovers, and positive `ChecksumException` detection for corrupted checksum and data files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSInputChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSOutputSummer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSOutputSummer.java

## Purpose

`TestFSOutputSummer.java` validates checksum generation while writing HDFS files with different write shapes and checksum types. The complete 168-line file was read. It ensures `FSOutputSummer` produces readable data and file checksums for whole-buffer, checksum-chunk, and irregular partial-chunk writes.

## Important APIs, Types, and Functions

Key APIs are `FSDataOutputStream`, `FSDataInputStream`, `FileSystem.getFileChecksum`, `MiniDFSCluster`, `DFS_BYTES_PER_CHECKSUM_KEY`, `DFS_CHECKSUM_TYPE_KEY`, and `IO_FILE_BUFFER_SIZE_KEY`. Constants mirror the input checker: `BYTES_PER_CHECKSUM=10`, `BLOCK_SIZE=20`, `HALF_CHUNK_SIZE=5`, `FILE_SIZE=39`, and two DataNodes. Helpers are `writeFile1`, `writeFile2`, `writeFile3`, `checkFile`, `checkAndEraseData`, `cleanupFile`, and `doTestFSOutputSummer`.

## Control Flow

`testFSOutputSummer` invokes `doTestFSOutputSummer` for `CRC32`, `CRC32C`, and `NULL`. Each run starts a two-node cluster, seeds the expected bytes, and writes the same path three ways: all data at once, exact checksum chunks plus a tail, and deliberately uneven writes that cross checksum and block boundaries. `checkFile` reads the file back with `readFully(0, actual)` and asks HDFS for a file checksum before cleanup. `TestDFSCheckSumType` separately repeats a NULL-checksum write path.

## State and Persistence Behavior

State is transient per-cluster file data plus checksum metadata generated by HDFS. The test keeps expected and actual arrays as object fields and deletes the file after each write variant.

## Dependencies and Integration Points

It integrates client write buffering, DFS checksum type selection, DataNode block storage, file checksum RPCs, and MiniDFSCluster write/read paths.

## Risks and Edge Cases

Risks include incorrect checksum chunk finalization when writes are smaller than a checksum chunk, null-checksum behavior diverging from CRC modes, and full-block flush behavior failing before close.

## Test Signals

Signals are exact byte equality after each write pattern, successful `getFileChecksum`, file existence before cleanup, file absence after cleanup, and cluster success across all checksum types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFSOutputSummer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFetchImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFetchImage.java

## Purpose

`TestFetchImage.java` verifies `hdfs dfsadmin -fetchImage` against an HA MiniDFSCluster. The complete 183-line file was read. It checks that the image downloaded from the active NameNode matches the highest fsimage stored in the cluster before and after namespace changes and active NameNode failover.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSNNTopology.simpleHATopology`, `MiniDFSCluster.transitionToActive`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `DFSAdmin.run`, NameNode RPC `setSafeMode` and `saveNamespace`, `MD5FileUtils.computeMd5ForFile`, `MD5Hash`, and `FileUtil.fullyDelete`. Helpers are `setupImageDir`, `cleanup`, `setupCluster`, `testFetchImageInternal`, `runFetchImage`, and `getHighestFsImageOnCluster`.

## Control Flow

Before each test it creates an HA cluster with one DataNode, low heartbeat and tail-edits intervals, and 1 KiB block size. `testFetchImageHA` transitions NN0 active, fetches the initial image, creates two directories, enters safe mode, saves namespace, leaves safe mode, and fetches again. It then waits for standby catch-up, transitions NN1 active, and repeats with new directories. `runFetchImage` executes `DFSAdmin -fetchImage <dir>`, then computes MD5 checksums of the downloaded image and the highest-transaction-ID fsimage found under NN0 name directories.

## State and Persistence Behavior

Persistent state under test is NameNode fsimage files in name directories plus the downloaded image directory under `target/fetched-image-dir`. The fixture creates and fully deletes that directory across the class.

## Dependencies and Integration Points

The file touches HA failover configuration, NameNode namespace checkpointing, DFSAdmin command execution, safe mode RPCs, fsimage filename parsing, and MD5 verification utilities.

## Risks and Edge Cases

Risks include fetching from the wrong active service, stale standby images after failover, incorrect highest transaction ID selection, and leftover downloaded images confusing comparisons.

## Test Signals

Signals are `DFSAdmin.run` return code `0`, exact MD5 equality between source and fetched image, successful safe mode save/leave calls, and both active-NameNode phases completing within the 30-second timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFetchImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend.java

## Purpose

`TestFileAppend.java` is a broad append regression suite for HDFS client, NameNode, and DataNode append mechanics. The complete 751-line file was read. It covers hflush visibility, repeated appends, soft-limit lease takeover, generation-stamp rejection of stale replicas, appending corrupt blocks, DataNode replica hardlink detachment, and concurrent append/read checksum behavior.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.append`, `DistributedFileSystem.append` with `CreateFlag.APPEND` and `CreateFlag.NEW_BLOCK`, `FSDataOutputStream.hflush`, `LocatedBlocks`, `BlockLocation`, `DFSClient`, `AlreadyBeingCreatedException`, `FsDatasetTestUtil.breakHardlinksIfNeeded`, `FsDatasetSpi.append`, `ReplicaBeingWritten`, `ReplicaOutputStreams`, `FsDatasetUtil.computeChecksum`, and `DFSTestUtil`. Helpers include `writeFile`, `checkFile`, and several tests named by append scenario.

## Control Flow

The tests create MiniDFSClusters with targeted replication and timeout settings. Simple and complex flush tests write partial data, hflush repeatedly, verify full blocks before close, then verify full contents after close. `testAppendTwice` and `testAppend2Twice` leave one append open and expect another client to receive `AlreadyBeingCreatedException`. `testMultipleAppends` repeatedly appends small random ranges and validates final contents. Lease soft-limit tests let an unclosed writer age out and verify the second client append does not duplicate data. Stale replica tests stop and restart DataNodes after generation-stamp bumps and inspect block locations. `testConcurrentAppendRead` directly converts a finalized replica to RBW, writes extra block bytes and recomputes on-disk checksum, then verifies BlockSender uses in-memory RBW checksum state.

## State and Persistence Behavior

State includes HDFS files, lease ownership, block generation stamps, block location metadata, DataNode block and meta files, and hardlinks on local block files. Some tests restart the NameNode to ensure appended block edits replay.

## Dependencies and Integration Points

The suite integrates DFSClient append semantics, NameNode leases, block placement and reports, DataNode FsDataset internals, file checksum metadata, and `AppendTestUtil` deterministic contents.

## Risks and Edge Cases

Risks include accepting stale replicas after failed append, invisible or duplicated data after lease recovery, checksum mismatch for RBW reads, full-block append edit-log gaps, and flaky timing around replication or block reports.

## Test Signals

Signals are full-file byte checks, exact block counts and block sizes, expected remote exception class names, absence of restarted stale DataNode in locations, NameNode restart replay checks, timeout-bound append to corrupt block, and one-byte read length for concurrent RBW read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend2.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend2.java

## Purpose

`TestFileAppend2.java` extends append coverage with permission checks, append-to-new-block behavior, concurrent random append workloads, and small append checksum recalculation. The complete 580-line file was read.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.append`, `DistributedFileSystem.append(EnumSet<CreateFlag>)`, `CreateFlag.NEW_BLOCK`, `FsPermission`, `UserGroupInformation.createUserForTesting`, `AccessControlException`, `SubjectInheritingThread`, `LocatedBlock`, and `HdfsClientConfigKeys` timeout settings. The nested `Workload` class removes random paths from a shared pool, appends random lengths, waits for NameNode length visibility, validates bytes, and returns paths to the pool. Helpers include `testComplexAppend` and `testAppendLessThanChecksumChunk`.

## Control Flow

`testSimpleAppend` creates a file, writes 186 bytes, appends through 607 bytes, then appends the rest and validates contents. It also verifies append to a missing file and POSIX-style permission behavior where write permission on the file, not parent write permission, controls append. `testSimpleAppend2` repeats using `APPEND|NEW_BLOCK` and validates the resulting many small block sizes. `testComplexAppend` creates 50 files with random replication, starts 10 worker threads, and performs many small appends against random files. `testAppendLessThanChecksumChunk` writes 200 bytes, appends 300 bytes, hflushes while open, and reads the partial file to catch checksum overwrite mistakes below the default 512-byte checksum chunk.

## State and Persistence Behavior

State under test is file length and content across repeated close/reopen append cycles, per-file permissions, shared test path pool, and block boundaries introduced by `NEW_BLOCK`.

## Dependencies and Integration Points

The file integrates DFS permissions, UGI-authenticated filesystem instances, DataNode handler concurrency, client socket/write timeouts, NameNode metadata length updates, and `AppendTestUtil` content verification.

## Risks and Edge Cases

Risks include `getPos` returning zero on append streams, append permission accidentally depending on parent directory write permission, corrupt checksum after sub-chunk append, and races in shared workload bookkeeping or NameNode length propagation.

## Test Signals

Signals include full-file byte validation, expected `FileNotFoundException` and `AccessControlException`, exact `NEW_BLOCK` block sizes, worker `globalStatus`, file length equality after each append, and successful partial-read while an append stream remains open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend3.java

## Purpose

`TestFileAppend3.java` implements append scenarios from HADOOP-2658 and related partial-checksum regressions. The complete 629-line file was read. It validates append at block boundaries, non-boundaries, simultaneous append exclusion, corrupted replicas, rename while appending, partial CRC chunk append, small append races, and mixed `NEW_BLOCK`/normal append sequences.

## Important APIs, Types, and Functions

Important APIs include `DistributedFileSystem.append`, `CreateFlag.NEW_BLOCK`, `LocatedBlocks`, `LocatedBlock`, `ExtendedBlock`, `DataNodeTestUtils.getFSDataset`, `InterDatanodeProtocol`, Mockito `spy/when`, `DFSClientAdapter`, and `SubjectInheritingThread`. Static fixture setup creates one 5-DataNode cluster with `BLOCK_SIZE=64 KiB`, replication 3, and 512 bytes per checksum.

## Control Flow

The TC tests use a shared cluster. TC1 appends half a block after exactly one full block. TC2 appends after a 1.5-block file and, for `NEW_BLOCK`, asserts separate block sizes. TC5 opens one append stream and verifies other clients cannot append until it closes. TC7 truncates one replica's data to zero before appending and verifies remaining replicas preserve readability. TC11 appends, hflushes, renames the file before close, then checks DataNode stored block sizes match NameNode located block sizes. TC12 and `testAppendToPartialChunk` focus on appending to partial checksum chunks over multiple hflushes. `testSmallAppendRace` delays `DFSClient.getFileInfo` with Mockito and runs concurrent small append attempts to expose stale file status bugs.

## State and Persistence Behavior

State includes open leases, renamed under-construction files, corrupted materialized replicas, block sizes on DataNodes, static cluster/filesystem state, and file content across repeated appends.

## Dependencies and Integration Points

The suite links DFSClient append paths, inter-DataNode recovery logging, DataNode datasets, Mockito-injected client delays, and append helper content generation.

## Risks and Edge Cases

Risks include stale file status across checksum chunk boundaries, not rejecting simultaneous appenders, mismatched DataNode and NameNode block lengths after rename, and partial checksum chunk corruption when `NEW_BLOCK` leaves a middle block incomplete.

## Test Signals

Signals are `AppendTestUtil.check` byte verification, expected IO failures for concurrent append, exact located block counts and sizes, matching DataNode stored block byte counts, and no checksum failures during repeated small append races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend4.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend4.java

## Purpose

`TestFileAppend4.java` focuses on append and sync recovery around HDFS-200 and HDFS-142. The complete 396-line file was read. It tests lease recovery after a writer finalizes a block but stalls before `completeFile`, recovery followed by a different lease holder writing, needed-replication updates for appended blocks, and failure behavior when the last block has no live locations.

## Important APIs, Types, and Functions

Key APIs are `NamenodeProtocols.complete`, `DFSClient.create`, `FSDataOutputStream.append`, `GenericTestUtils.DelayAnswer`, Mockito `spy/doAnswer`, `LeaseExpiredException`, `cluster.setLeasePeriod`, `DFSTestUtil.waitReplication`, `LocatedBlocks`, `FSDirectory`, and `INodeFile`. The helper `recoverFile` repeatedly opens the file for append under a short lease period, closes the recovered stream, and fails if recovery takes longer than a minute.

## Control Flow

Each test configures short heartbeats, reconstruction intervals, and client socket retries. `testRecoverFinalizedBlock` spies the NameNode RPC, delays `complete`, closes a DFSClient stream on a separate thread until the delay triggers, interrupts the lease renewer, and has another user recover the file; when the original close resumes it must fail because the file is no longer open. `testCompleteOtherLeaseHoldersFile` repeats but has the new lease holder append data before releasing the old close, expecting a lease-owner mismatch. Replication and insufficient-location tests create files, append, start/stop DataNodes, wait for replication state, and inspect the inode to ensure failed append leaves the file closed.

## State and Persistence Behavior

State includes delayed NameNode completion RPCs, lease-renewer thread state, NameNode lease ownership, block replication queues, and inode under-construction flags.

## Dependencies and Integration Points

The test integrates DFSClient lease renewal, NameNode protocol completion, block manager replication accounting, DataNode liveness recognition, and low-level namespace inspection through `FSDirectory`.

## Risks and Edge Cases

Risks include old writers completing files after lease recovery, recovery taking too long, appended blocks not entering needed-replication queues, and failed append transitions leaving an inode under construction.

## Test Signals

Signals are expected `LeaseExpiredException` messages, successful recovery append open, `DFSTestUtil.waitReplication` to replication 2, expected IO failure for insufficient locations, and `!inode.isUnderConstruction()` after failed append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppend4.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppendRestart.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppendRestart.java

## Purpose

`TestFileAppendRestart.java` verifies append edit-log persistence and compatibility across NameNode restarts. The complete 218-line file was read. It is primarily a regression suite for HDFS-2991, where append at block boundaries could miss required edit-log operations.

## Important APIs, Types, and Functions

Key APIs are `FSImageTestUtil.countEditLogOpTypes`, `FSEditLogOpCodes`, `NNStorage.getInProgressEditsFileName`, `StartupOption.UPGRADE`, `FileUtil.unTar`, `AppendTestUtil.write`, and `AppendTestUtil.check`. The helper `writeAndAppend` creates a file with 4096-byte blocks, writes an initial length, appends another length, closes, and asserts the total file length.

## Control Flow

`testAppendRestart` disables persistent IPC so a DFSClient can survive restart, starts a one-DataNode cluster, writes/appends at an exact block boundary, and checks edit-log counts for `OP_ADD`, `OP_APPEND`, two `OP_ADD_BLOCK`, and two `OP_CLOSE` operations. It then writes/appends at a non-block boundary and expects an additional `OP_UPDATE_BLOCKS`. After NameNode restart, it verifies both files' readable lengths. `testLoadLogsFromBuggyEarlierVersions` untars a Hadoop 0.23-era fsimage/edit-log fixture and boots with upgrade to prove old buggy append logs load to the expected file length. `testAppendWithPipelineRecovery` appends after stopping a DataNode in a 4-node rack-aware pipeline, restarts the NameNode, and checks file content length.

## State and Persistence Behavior

This file is explicitly about edit-log and fsimage persistence. It reads in-progress edits, imports archived name directories, upgrades old image format, restarts NameNode, and validates replayed file length.

## Dependencies and Integration Points

It integrates NameNode storage layout, FSImage test utilities, append edit op semantics, pipeline recovery, rack-aware MiniDFSCluster setup, and test-cache archived images.

## Risks and Edge Cases

Risks include missing `OP_ADD`/`OP_APPEND`/`OP_UPDATE_BLOCKS` on append, inability to load historical buggy logs, and pipeline recovery edits failing after restart.

## Test Signals

Signals are exact edit-op counts, exact file status lengths, `AppendTestUtil.check` after restart, archive directory existence, and successful upgrade-mode startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileAppendRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileChecksum.java

## Purpose

`TestFileChecksum.java` is a slow parameterized HDFS checksum suite for replicated and erasure-coded files. The complete 830-line file was read. It compares MD5-of-CRC and composite CRC behavior over whole files, byte ranges, striped layouts, missing data blocks, reconstruction failures, mixed bytes-per-checksum blocks, and reconstruction cleanup failure paths.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.getFileChecksum(Path)` and `getFileChecksum(Path,int)`, `ChecksumCombineMode.MD5MD5CRC`, `ChecksumCombineMode.COMPOSITE_CRC`, `StripedFileTestUtil.getDefaultECPolicy`, `DistributedFileSystem.setErasureCodingPolicy`, `DFSClient.getLocatedBlocks`, `DataNodeFaultInjector`, `LocatedBlock`, and `DatanodeInfo`. `setup` creates enough DataNodes for data plus parity plus extras, enables block access tokens, configures combine mode, and prepares `/striped`. Helpers include `testStripedFileChecksum`, `testStripedFileChecksumWithMissedDataBlocksRangeQuery`, `getFileChecksum`, `prepareTestFiles`, `shutdownDataNode`, and `getDataNodeToKill`.

## Control Flow

Each parameterized test initializes a fresh cluster for one combine mode. The first group writes identical striped files and compares checksums for ranges around zero, stripe, cell, block-group, and full-file boundaries. Replicated-versus-striped tests assert equality only for composite CRC. Missing-block tests kill a DataNode hosting part of the first block group, compute checksum through reconstruction, restart the DataNode, and compare with normal checksums. Twenty range-query tests cover sizes from 1 byte through twice file size, including small files. Reconstruction failure injects an IOException on the first reconstruction task and expects retry through another DataNode. Mixed bytes-per-checksum verifies composite CRC can combine blocks with different CRC chunk sizes while MD5MD5CRC throws.

## State and Persistence Behavior

State includes per-test MiniDFSCluster files, EC policy on `/striped`, DataNode liveness, block access tokens, and injected global `DataNodeFaultInjector` state restored in `finally`.

## Dependencies and Integration Points

The suite integrates striped block checksum helpers, EC reconstruction, block tokens, file checksum combine modes, DataNode shutdown/restart, and DFSClient located-block selection.

## Risks and Edge Cases

Risks include checksum range normalization past EOF, inconsistent composite CRC across block sizes/layouts, leaked reconstruction state after initialization failure, and global fault injector not restored.

## Test Signals

Signals are equality or inequality of `FileChecksum` objects by combine mode, expected IOException for MD5 with mixed bytes-per-checksum, expected exception when too many DataNodes are down, restart of killed DataNodes, and 90-second timeouts for slow checksum paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileConcurrentReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileConcurrentReader.java

## Purpose

`TestFileConcurrentReader.java` verifies that readers can safely observe files while another client is still writing or flushing unfinished blocks. The complete 466-line file was read. It targets visible hflush data, immediate opens of newly growing files, packet buffer sizing, and checksum correctness while tailing unfinished blocks.

## Important APIs, Types, and Functions

Key APIs are `FSDataOutputStream.hflush`, `FSDataInputStream`, `FileSystem.getFileBlockLocations`, `DFS_DATANODE_TRANSFERTO_ALLOWED_KEY`, `ChecksumException`, `SubjectInheritingThread`, and `MiniDFSCluster`. The `SyncType` enum distinguishes `SYNC` and disabled append variants. Helpers include `writeFileAndSync`, `checkCanRead`, `assertBytesAvailable`, `waitForBlocks`, `runTestUnfinishedBlockCRCError`, `validateSequentialBytes`, and `tailFile`.

## Control Flow

Setup creates a cluster for each test. `testUnfinishedBlockRead` writes half a block, hflushes, waits for block visibility, and reads before close. `testUnfinishedBlockPacketBufferOverrun` writes one byte less than a checksum chunk to catch BlockSender packet-size bugs. `testImmediateReadOfNewFile` starts a writer repeatedly writing and hflushing a large file while another thread opens and closes it 100 times. CRC-error tests run with `transferTo` both enabled and disabled and with default or very small writes: one thread writes sequential byte chunks with hflush; another repeatedly opens, seeks to the last read position, tails available bytes, and validates sequence.

## State and Persistence Behavior

State includes unfinished block data, hflushed visible length, thread booleans for writer/tailer coordination, and transient cluster block locations. No durable restart path is covered.

## Dependencies and Integration Points

The test integrates BlockSender transfer-to and normal copy paths, HDFS visible-length semantics, lease manager logging, `TestFileCreation.createFile`, and sequential-byte validation from `DFSTestUtil`.

## Risks and Edge Cases

Risks include readers seeing checksum errors for partial last chunks, one-packet transfer buffer overrun, clients failing to open files while blocks are being created, and off-by-one tail positions.

## Test Signals

Signals include successful pre-close reads, null `errorMessage` from opener thread, `assertFalse(error)` after writer and tailer join, sequential byte validation, absence of `ChecksumException`, and test-level timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileConcurrentReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCorruption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCorruption.java

## Purpose

`TestFileCorruption.java` tests HDFS and local filesystem behavior when block or checksum corruption is reported or introduced. The complete 330-line file was read. It covers deleted replicas, local checksum corruption, corrupt reports for unknown blocks, disk-failure storage state, and replication accounting during batched incremental block reports.

## Important APIs, Types, and Functions

Key APIs are `DFSTestUtil`, `BlockListAsLongs`, `BlockReportReplica`, `ExtendedBlock`, `BlockManager.findAndMarkBlockAsCorrupt`, `DatanodeStorageInfo`, `DatanodeStorage`, `FSNamesystem` write locks, `ChecksumException`, and `GenericTestUtils.waitFor`. Helpers include `markAllBlocksAsCorrupt`, `updateAllStorages`, and `getFirstBlock`.

## Control Flow

`testFileCorruption` creates 20 files on a three-node cluster, deletes all blocks from one DataNode's materialized replicas, and verifies files remain readable through other replicas. `testLocalFileCorruption` overwrites a local file after Hadoop created its checksum and expects a logged `ChecksumException` rather than null-pointer fallout. `testArrayOutOfBoundsException` has a third DataNode report a corrupt block not present in the block map and then opens the file to catch indexing regressions. `testCorruptionWithDiskFailure` marks storages failed, marks all block storages corrupt, and verifies open does not crash. `testSetReplicationWhenBatchIBR` delays incremental block reports, raises replication above live DataNode count, and checks low-redundancy and missing-block counts.

## State and Persistence Behavior

State includes DataNode block files, local checksum files, NameNode corrupt-replica maps, storage states, block report queues, and low-redundancy counters. Changes are cluster-local and cleaned by shutdown.

## Dependencies and Integration Points

It integrates DataNode block reports, NameNode block manager corruption tracking, local filesystem checksum verification, storage failure metadata, and replication monitor accounting.

## Risks and Edge Cases

Risks include crashes on corrupt reports from non-holder DataNodes, treating failed storages as missing blocks incorrectly, stale block reports hiding under-replication, and local checksum exceptions masking other errors.

## Test Signals

Signals are `util.checkFiles` success after replica deletion, caught/ignored `ChecksumException`, successful file opens after corrupt marking, low-redundancy count `1`, missing-block count `0`, and no array-index failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCorruption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreation.java

## Purpose

`TestFileCreation.java` is the central HDFS file-creation regression suite. The complete 1,439-line file was read. It spans server defaults, client default caching, file and directory creation rules, overwrite, delete-on-exit, failure cleanup, lease persistence, non-recursive creation, simulated storage, concurrent writes, close semantics, non-canonical paths, file ID checks, and block cleanup after overwrite.

## Important APIs, Types, and Functions

Key APIs are `FileSystem.create`, `createNonRecursive`, `DistributedFileSystem`, `DFSClient`, `HdfsDataOutputStream`, `FsServerDefaults`, `MiniDFSCluster`, `SimulatedFSDataset`, `LeaseManager`, `NameNodeAdapter`, `BlockManager`, `LocatedBlocks`, `NamenodeProtocols.create/complete`, and metrics assertions. Public helpers `createFile`, `create`, `writeFile`, `testFileCreationNonRecursive`, and `createNonRecursive` are reused by neighboring tests.

## Control Flow

Server-default tests configure NameNode defaults, use Mockito to alter `FSNamesystem.getServerDefaults`, and verify client cache staleness or expiry. `checkFileCreation` validates root existence, directory overwrite rejection, file creation, quota/content length accounting, hostname and local interface settings, and simulated-storage usage. Failure tests kill DataNodes or create with insufficient replication, then confirm bad allocations are removed. Lease tests keep files open across renames and two NameNode restarts, then rewrite DFSOutputStream `src` fields to continue writing renamed files. Other tests cover DFSClient death, non-recursive parent errors, concurrent files, sync-on-close, hard lease expiry, filesystem close with open files, close timeout after DataNode loss, direct RPC rejection of non-canonical paths versus `Path` normalization, complete file ID mismatch, and overwrite block deletion through restart and checkpoint.

## State and Persistence Behavior

The file heavily exercises persistent namespace state: leases in fsimage, edit replay after restart, block maps, marked-delete queues, quotas, file status lengths, storage usage, and checkpointed overwrite results.

## Dependencies and Integration Points

It integrates NameNode RPCs, DFSClient output streams, block manager internals, DataNode datasets, metrics, permissions-disabled overwrite behavior, UGI, reflection against `DFSOutputStream.src`, and test utilities across HDFS.

## Risks and Edge Cases

Risks include lease loss after restart or rename, stale server defaults, corrupted edits from non-canonical RPC paths, blocks left in block maps after overwrite, close hangs under replication minimum, and accidental parent creation in non-recursive mode.

## Test Signals

Signals include exact defaults, metrics counters, file lengths, content summaries, simulated dataset usage, expected exception types/messages, located block counts, safe block cleanup assertions, byte equality after restart/checkpoint, and timeout-limited close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationClient.java

## Purpose

`TestFileCreationClient.java` tests DFSClient-triggered lease recovery while multiple slow writers are actively flushing files and a DataNode fails. The complete 150-line file was read.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSCluster`, `FileSystem.create/open`, `FSDataOutputStream.hflush`, `SubjectInheritingThread`, `DFS_DATANODE_HANDLER_COUNT_KEY`, `DFS_REPLICATION_KEY`, `DataNode`, `LeaseManager`, `FSNamesystem`, and `InterDatanodeProtocol` logging. The nested `SlowWriter` thread creates one path, writes increasing byte values, hflushes after every byte, sleeps, and closes in `finally`.

## Control Flow

`testClientTriggeredLeaseRecovery` starts a three-DataNode cluster with replication 3 and one DataNode handler. It creates ten `SlowWriter` threads under `/wrwelkj`, starts them, lets them write for a second, stops one random DataNode, and lets writing continue for several more seconds. In `finally`, it flips each writer's `running` flag, interrupts and joins all threads, then verifies every produced file by reading from byte 0 to EOF and asserting byte value equals its sequence index.

## State and Persistence Behavior

State consists of ten open HDFS files, per-writer output streams, hflushed bytes, DataNode liveness, and recovered pipeline/lease state. There is no restart persistence, but data must remain readable after client-side recovery from a DataNode stop.

## Dependencies and Integration Points

The test integrates DFSClient write-pipeline recovery, lease recovery, hflush visibility, DataNode handler pressure, and inter-DataNode recovery protocols.

## Risks and Edge Cases

Risks include writer threads swallowing failures while producing truncated files, lease recovery not triggering when a DataNode dies mid-write, and byte values exceeding single-byte expectations if writers run too long.

## Test Signals

Signals are successful joins, non-throwing writer close paths, file status lengths printed for each writer, and sequential byte equality for every file read to EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationDelete.java

## Purpose

`TestFileCreationDelete.java` verifies lease persistence and cleanup when a parent directory containing an open file is deleted before NameNode restart. The complete 92-line file was read.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSCluster`, `FileSystem.delete`, `FSDataOutputStream.hflush`, `TestFileCreation.createFile`, `TestFileCreation.writeFile`, `DFS_HEARTBEAT_INTERVAL_KEY`, and `DFS_NAMENODE_HEARTBEAT_RECHECK_INTERVAL_KEY`.

## Control Flow

The test starts a cluster with short heartbeat settings and low IPC idle time. It creates `/foo/file1`, writes and hflushes 1000 bytes while leaving the stream open, then creates `/file2` similarly. It deletes `/foo` recursively, shuts the cluster down without formatting, waits across client idle windows, restarts, shuts down again, waits longer, and restarts once more from the same storage. After obtaining a new filesystem handle, it asserts `/foo/file1` does not exist and `/file2` still exists.

## State and Persistence Behavior

The test is about fsimage/edit-log persistence of open-file leases after deletion. File1's parent deletion must remove that lease/path across restarts, while unrelated open file2 must survive as a persistent lease-backed file.

## Dependencies and Integration Points

It depends on `TestFileCreation` helpers, MiniDFSCluster reuse of name/data dirs with `format(false)`, NameNode lease serialization, delete edit replay, and hflush-created block state.

## Risks and Edge Cases

Risks include resurrecting deleted under-construction files after restart, losing unrelated open files during lease replay, and null filesystem cleanup if setup fails before assignment.

## Test Signals

Signals are final `!fs.exists(file1)` and `fs.exists(file2)` assertions after two unformatted restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationEmpty.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationEmpty.java

## Purpose

`TestFileCreationEmpty.java` checks that lease expiry over multiple empty files does not throw `ConcurrentModificationException`. The complete 84-line file was read.

## Important APIs, Types, and Functions

Key APIs are `Thread.setDefaultUncaughtExceptionHandler`, `ConcurrentModificationException`, `LeaseManager.LOG`, `MiniDFSCluster`, `cluster.setLeasePeriod`, and `TestFileCreation.createFile`.

## Control Flow

The test installs a temporary default uncaught exception handler that records any `ConcurrentModificationException`. It starts a three-DataNode cluster, creates three empty files (`/foo`, `/foo2`, `/foo3`) through `TestFileCreation.createFile` without closing the returned streams, sets both soft and hard lease periods to one second, waits five lease periods, and asserts the flag was not set. The original exception handler is restored in `finally`.

## State and Persistence Behavior

State is in-memory lease manager state for three zero-length under-construction files. There is no restart, but lease expiry mutates the lease collection while scanning it.

## Dependencies and Integration Points

The test targets NameNode `LeaseManager` empty-file release behavior and MiniDFSCluster lease-period control.

## Risks and Edge Cases

Risks include global uncaught exception handler leakage, lease scans modifying collections during iteration, and false negatives if lease recovery does not run during the sleep window.

## Test Signals

Signals are absence of uncaught `ConcurrentModificationException` after lease expiry, handler restoration, and clean cluster shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCreationEmpty.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileLengthOnClusterRestart.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileLengthOnClusterRestart.java

## Purpose

`TestFileLengthOnClusterRestart.java` verifies visible file length after `hsync` and NameNode restart, and verifies safe-mode behavior when DataNodes have not registered. The complete 99-line file was read.

## Important APIs, Types, and Functions

Key APIs are `FSDataOutputStream.hsync`, `HdfsDataInputStream.getVisibleLength`, `MiniDFSCluster.restartNameNode`, `cluster.shutdownDataNodes`, `DistributedFileSystem.isInSafeMode`, and `DFS_BLOCK_SIZE_KEY`.

## Control Flow

The test configures 512-byte blocks, starts a two-DataNode cluster, creates `/tmp/TestFileLengthOnClusterRestart/test`, writes 1030 bytes, and calls `hsync`. It restarts the NameNode with DataNodes available, waits active, opens the file, and asserts `getVisibleLength()` equals 1030. It then shuts down all DataNodes, restarts only the NameNode without formatting, loops until `dfs.isInSafeMode()` reports true, and verifies opening the path fails with an IOException whose message contains "Name node is in safe mode".

## State and Persistence Behavior

The persistent state is the hsynced file length in NameNode metadata and block reports. The second phase intentionally lacks DataNode registrations, so the NameNode remains in safe mode even though namespace metadata exists.

## Dependencies and Integration Points

It integrates DFSOutputStream hsync visibility, HDFS client visible-length reporting, NameNode restart, safe-mode detection, and DataNode registration timing.

## Risks and Edge Cases

Risks include file length reverting to block-report length after restart, open incorrectly succeeding while safe mode prevents block access, and the safe-mode polling loop spinning if the NameNode never starts.

## Test Signals

Signals are exact visible length `1030`, successful detection of safe mode, expected IOException on open, and message substring validation for safe mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileLengthOnClusterRestart.java -->
