# Research: subset-b-007524

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java

## Purpose
`TestDFSShell` is the broad integration regression suite for HDFS-facing `FsShell` and related command behavior. It exercises shell commands against a shared `MiniDFSCluster` with permissions, xattrs, ACLs, snapshots, access-time precision, and small block sizes enabled. It also starts isolated clusters for scenarios that need special topology or configuration, such as corrupt replicas, low replication minimums, trash policy precedence, URI movement, and append-to-EC behavior.

## Important APIs, Types, and Helpers
- `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, and `FsShell` provide the main in-process HDFS command surface.
- Static helpers `writeFile`, `writeByte`, `mkdir`, `rmr`, `createLocalFile`, `createLocalFileWithRandomData`, `createTree`, `runCmd`, `runCount`, `confirmPermissionChange`, and `confirmOwner` keep command setup and assertions reusable.
- `getMaterializedReplicas` and `corrupt` inspect block reports and corrupt materialized replicas for checksum and `-get -ignoreCrc` coverage.
- XAttr constants `raw.a1`, `trusted.a1`, `user.a1` and their byte values are reused by copy-preserve and xattr permission tests.
- `TestGetRunner` abstracts repeated `-get` invocations with different expected exit codes and options.

## Control Flow and Coverage
The class uses `@BeforeAll` to create a two-datanode shared cluster and `@AfterAll` to shut it down. Tests then build filesystem state, invoke shell commands with `shell.run` or `ToolRunner.run`, capture `System.out` or `System.err` when output content matters, and assert both exit codes and filesystem side effects.

Major command groups covered:
- File creation, copying, and deletion: zero-size local/HDFS copy, recursive delete, `-put`, `-copyToLocal`, `-cp`, `-mv`, `-copyFromLocal`, force overwrite, permission-denied local source handling, and URI-qualified paths across multiple clusters.
- Listing and content display: `-ls`, `-lsr`, `-cat`, `-head`, `-tail`, `-tail -f`, `-text` with gzip, deflate, bzip2, sequence files, and plain text.
- Accounting and stats: `-du`, `-du -s`, `-du -x`, `-count`, snapshot-aware count and disk usage, `FileSystem#getUsed`, and `-stat` formatting tokens.
- Permissions and ownership: local and HDFS `-chmod`, sticky bit variants, recursive mode changes, `-chown`, `-chgrp`, owner/group name character handling, and `-test -e/-d/-z/-f/-s/-r/-w`.
- Preservation semantics: `-cp -p`, `-ptop`, `-ptopx`, `-ptopa`, `-ptoa`, directory attribute preservation, ACL preservation, sticky bit preservation, vanilla xattrs, trusted xattrs, and raw xattrs under `/.reserved/raw`.
- Data integrity and append: `-checksum -v`, corrupt-replica `-get` behavior with and without `-ignoreCrc`, `-appendToFile`, invalid append arguments, and `-appendToFile -n` for replicated and EC files.
- Extended attributes: `-setfattr`, `-getfattr`, case sensitivity, permission checks across users, trusted namespace privilege checks, missing xattr errors, and path access failures.
- Trash: client and server `fs.trash.interval` precedence, including disabled default behavior.
- Reserved paths: visibility and rejection behavior for `/.reserved`, raw path restrictions, mkdir/delete/copy/chmod/chown/symlink/snapshot operations on reserved names.

## State and Persistence Behavior
The suite mutates both shared HDFS namespace state and local test files under `TEST_ROOT_DIR`. Most tests create unique top-level directories or append a `counter` suffix; some reuse names and explicitly delete on exit. Snapshot tests persist historical content after live deletions and verify `-du`/`-count` with and without snapshot inclusion. Trash tests verify whether deleted files move under the current trash directory based on server/client configuration. Copy-preserve tests persist metadata and then compare ownership, permissions, ACLs, xattrs, raw xattrs, times, block counts, and replication.

Some tests temporarily replace global streams (`System.out`/`System.err`) and restore them in `finally`; failures before restoration could pollute later tests. Several isolated clusters persist storage while shut down and restarted to validate corrupted replica reads.

## Dependencies and Integration Points
The file integrates with HDFS shell commands, HDFS NameNode/DataNode services, `FSDirectory` reserved-name handling, ACL and xattr subsystems, checksum verification, snapshots, trash, block reports, block replica materialization, EC append policy, and local filesystem copy behavior. It also uses `UserGroupInformation.doAs` to exercise authorization paths and `SubjectInheritingThread` for `-tail -f`.

## Risks and Edge Cases
- Tests depend heavily on wall-clock timestamps, access-time precision, and `Thread.sleep`; timing changes can introduce flakes.
- Shared cluster state means path reuse or missing cleanup can create cross-test coupling.
- Capturing global stdout/stderr is process-wide and unsafe under parallel test execution.
- Reserved path and raw xattr checks are sensitive to path normalization and `/.reserved/raw` detection for relative paths.
- Corruption and restart tests assume replica materialization behavior and platform file-lock behavior.
- Append and EC tests are long-running and topology-sensitive.

## Test Signals
Strong signals include command exit-code assertions, output substring checks, direct filesystem metadata comparisons, corruption readback checks, ACL/xattr equality checks, and verification that failures produce user-facing messages rather than stack traces. The suite is especially useful for catching behavioral regressions in user-visible shell semantics rather than isolated method-level defects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java

## Purpose
This focused test verifies that Hadoop generic command-line options correctly configure `FsShell` when running HDFS commands. It checks `-fs`, `-conf`, and `-D fs.defaultFS=...` by creating `/data` in a `MiniDFSCluster`.

## Important APIs, Types, and Functions
- `MiniDFSCluster.Builder` creates the target HDFS cluster.
- `FileSystem.getDefaultUri(conf)` supplies the NameNode URI used in generic options.
- `FsShell` and `ToolRunner.run` execute `-mkdir /data`.
- `DFSUtilClient.getNNAddress` and `getNNUri` resolve the shell configuration back to a `FileSystem`.
- Helper methods `testFsOption`, `testConfOption`, `testPropertyOption`, and `execute` mutate the same argument array and verify side effects.

## Control Flow
`testDFSCommand` starts a cluster, obtains its NameNode URI, initializes a four-element argument array with command slots `-mkdir /data`, and runs the three generic option variants. `testConfOption` writes a temporary `hdfs-site.xml` containing `fs.defaultFS`, then invokes the same command path. `execute` runs the shell, resolves a filesystem from the shell configuration, asserts `/data` exists, and deletes it for the next variant.

## State and Persistence Behavior
Cluster state is short-lived and shut down in `finally`. The `/data` directory is created and removed for each option variant. `testConfOption` writes `build/test/minidfs/hdfs-site.xml` and deletes both the file and containing directory afterwards.

## Dependencies and Integration Points
The test bridges Hadoop generic options, `FsShell`, XML configuration loading, HDFS URI resolution, and `FileSystem` creation. It validates the command-line contract between `ToolRunner`, `Configured` tools, and HDFS shell commands.

## Risks
`execute` catches exceptions and prints stack traces without failing directly, so an exception before the assertion path may be masked unless a later assertion fails. The temporary config directory uses a fixed path, making parallel execution susceptible to directory-exists or cleanup races. The mutable shared `args` array is concise but easy to break if new command variants are added.

## Test Signals
The key signal is direct verification that `/data` exists after each generic option style and is removable before the next invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellGenericOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java

## Purpose
`TestDFSShellTouch` validates the HDFS implementation of the newer `-touch` shell command, especially explicit timestamp parsing and selective access/modification time updates for files and directories.

## Important APIs, Types, and Functions
- Shared `MiniDFSCluster`, `DistributedFileSystem`, and `FsShell` are initialized once for the class.
- `TouchCommands.Touch().getDateFormat()` is reused to format and parse timestamps in the same syntax accepted by the shell command.
- `shellRun` invokes `shell.run(args)`, logs the command, and returns the exit code.
- `FileStatus#getAccessTime` and `getModificationTime` are the verification surface.

## Control Flow
`testTouch` creates a file, then applies `-touch -t`, `-touch -a -t`, `-touch -m -t`, combined `-a -m`, missing timestamp failure, and `-c -t` behavior. Between selective updates, it stores the previous `FileStatus` and sleeps briefly so unchanged and changed fields can be distinguished.

`testTouchDirs` creates a directory and a child file, then repeats full, modification-only, and access-only updates against the directory itself. It verifies that directory timestamps are updated through the shell and cleans up both paths.

## State and Persistence Behavior
The tests persist timestamp metadata on HDFS files/directories, not contents. They create fixed relative paths (`newFile1`, `dir2/newFile2`, `dir2`) in the shell working directory and delete them at the end of each test. Timestamp precision depends on the date format used by the touch command and on the NameNode storing times exactly enough for equality comparisons.

## Dependencies and Integration Points
The file integrates `FsShell`, `org.apache.hadoop.fs.shell.TouchCommands`, HDFS `setTimes` behavior, timestamp parsing/formatting, and `FileStatus` metadata reads. It also uses AssertJ for fluent checks and `StringUtils.join` for logging.

## Risks
The tests depend on `Thread.sleep(500)` and millisecond timestamp equality after format/parse truncation. Fixed relative paths can collide in parallel runs. `-c` coverage is slightly indirect because it is invoked on an existing file even though the assertion message says non-existent file.

## Test Signals
Signals include exact exit-code checks and exact timestamp equality for both fields, plus unchanged-field assertions for `-a` and `-m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSShellTouch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java

## Purpose
This test verifies DataNode startup compatibility against NameNode version metadata across layout version, namespace ID, cluster ID, block pool ID, and filesystem state creation time combinations.

## Important APIs, Types, and Functions
- `StorageData` packages a `StorageInfo` and block pool ID for synthetic version files.
- `initializeVersions` generates the compatibility matrix: old/current/future layout versions, current/invalid namespace IDs, past/current/future cTimes, plus invalid cluster/block-pool scenarios.
- `isVersionCompatible` encodes expected compatibility rules and is the oracle for the test.
- `UpgradeUtilities` creates NameNode/DataNode storage directories and version files.
- `MiniDFSCluster` starts a NameNode without DataNodes, then starts one DataNode per matrix row.

## Control Flow
`testVersions` initializes upgrade utilities and storage-state configuration, creates current NameNode storage, starts a NameNode with no DataNodes, captures the actual NameNode version fields, and iterates through all `StorageData` variants. For each case it creates DataNode storage, writes a version file using the candidate metadata, attempts DataNode startup, and compares `cluster.isDataNodeUp()` to `isVersionCompatible`.

## State and Persistence Behavior
The test writes on-disk VERSION files and storage directory layouts through `UpgradeUtilities`. NameNode state persists for the whole test; DataNode directories are recreated for each case, and DataNodes are shut down after each attempt. Compatibility is stateful around layout versions, namespace IDs, cluster IDs, block pool IDs, and cTimes.

## Dependencies and Integration Points
It exercises startup checks in DataNode storage loading, NameNode/DataNode version compatibility, block-pool identity validation, upgrade-related layout-version rules, and cluster startup paths that use existing storage (`format(false)`, unmanaged data/name dirs).

## Risks
The oracle duplicates compatibility logic, so it can drift from production startup rules. `invalidClusterID` is set to the same string as `clusterID` in the version array, which weakens the intended invalid-cluster case unless overwritten by the live NameNode cluster ID. The test is expensive and uses a broad timeout.

## Test Signals
The primary signal is a matrix assertion: for every synthetic DataNode version file, actual DataNode liveness must match the encoded compatibility rules. Logs print every case's version tuple for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStartupVersions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java

## Purpose
`TestDFSStorageStateRecovery` verifies NameNode, DataNode, and block-pool recovery behavior for combinations of HDFS storage directories: `current`, `previous`, `previous.tmp`, and `removed.tmp`. It encodes expected recovery outcomes from the HDFS upgrade test plan.

## Important APIs, Types, and Functions
- `testCases` is the central truth table with input directory existence and expected recovery/current/previous outcomes.
- `createNameNodeStorageState`, `createDataNodeStorageState`, and `createBlockPoolStorageState` materialize storage states using `UpgradeUtilities`.
- `checkResultNameNode`, `checkResultDataNode`, and `checkResultBlockPool` verify directory existence and checksums against master storage contents.
- `createCluster` starts a `MiniDFSCluster` over preexisting unmanaged storage without formatting.
- `setUp` calls `UpgradeUtilities.initialize`; `tearDown` shuts down active clusters.

## Control Flow
`testNNStorageStates` iterates one and two storage-directory configurations over all NameNode cases, builds the input layout, starts the cluster when recovery should succeed, verifies post-recovery state, or expects startup failure. The empty-storage failure case also checks for the "NameNode is not formatted" message.

`testDNStorageStates` creates valid NameNode storage first, starts a NameNode-only cluster, then creates DataNode storage for each case and starts one DataNode. Empty DataNode storage is allowed to create/format `current`; other cases either verify checksums or assert the DataNode is down.

`testBlockPoolStorageStates` mirrors DataNode recovery at the block-pool directory level and asserts block-pool service liveness for failures.

## State and Persistence Behavior
The test is entirely about persistent on-disk storage state. It deliberately creates, removes, and recovers directories under configured name/data dirs, then compares checksums to ensure `previous` contents are not modified and `current` contents match expected master layouts. It disables DataNode scanning for speed and repeatability.

## Dependencies and Integration Points
It integrates with storage upgrade/recovery code, NameNode startup, DataNode startup, block-pool service startup, `FSImageTestUtil.findNewestImageFile`, `Storage.STORAGE_DIR_CURRENT/PREVIOUS`, and `UpgradeUtilities` checksum fixtures.

## Risks
The truth table is dense and has repeated case labels, so maintaining expected outcomes requires care. Several assertions only run when directories should exist; unexpected extra directories are not always explicitly rejected. The tests repeatedly start and stop clusters and can be slow or sensitive to leftover storage state if cleanup fails.

## Test Signals
Signals include startup success/failure, DataNode/BP service liveness, exact directory and VERSION/image/seen_txid checks for NameNode current state, and checksum comparisons for DataNode/current, block-pool/current, and previous directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStorageStateRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java

## Purpose
This slow integration suite validates `DFSStripedInputStream` read behavior for HDFS erasure-coded striped files. It covers block refresh, positional reads, stateful reads, DataNode failures, decoding, buffer-pool cleanup, block-reader range calculation, unbuffering, and retry behavior after injected read-strategy failures.

## Important APIs, Types, and Functions
- `getEcPolicy` returns the default EC policy and is intentionally overridable by subclasses.
- Setup derives `dataBlocks`, `parityBlocks`, `cellSize`, `blockSize`, and `blockGroupSize`, configures simulated datasets, starts `MiniDFSCluster`, disables DataNode heartbeats, enables the EC policy, and sets it on `/striped`.
- `DFSTestUtil.createStripedFile`, `cluster.injectBlocks`, `StripedBlockUtil.parseStripedBlockGroup`, and `SimulatedFSDataset.simulatedByte` build deterministic expected striped contents.
- `CodecUtil.createRawDecoder` and `RawErasureDecoder` compute expected reconstructed bytes when a DataNode is stopped.
- `DFSClientFaultInjector` observes block-reader creation ranges and injects retry failures.
- `emptyBufferPoolForCurrentPolicy`, `verifyPreadRanges`, and `verifySreadRanges` are local helpers for buffer-pool and range tests.

## Control Flow
`testRefreshBlock` parses located striped block groups and verifies that refreshing component blocks preserves identity, offsets, and locations. `testPread` injects component blocks for two block groups and reads from offsets around cells, stripes, block-group boundaries, and EOF, comparing byte-by-byte to manually generated expected data.

Failure read tests stop one DataNode and use a raw decoder to precompute reconstructed bytes. They verify both positional and stateful read paths across partial cells and full remainder reads. `testStatefulRead` runs byte-array and `ByteBuffer` stateful reads and restarts the cluster with an unaligned IO buffer for misaligned packet coverage.

Lifecycle and edge tests verify idempotent close, error propagation when `blockSeekTo` fails before a current block is set, no buffer allocation during close, reconstruction when the last incomplete cell participates in aligned-stripe decode, `unbuffer` releasing current stripe and parity buffers, exact block-reader ranges for pread/sread, and stateful retry when the first read strategy fails with more-than-parity simulated failures.

## State and Persistence Behavior
Each test gets a fresh cluster rooted at a JUnit `@TempDir`. It persists EC policy on directories, writes striped files, injects simulated block replicas into specific DataNodes, stops DataNodes, mutates IO buffer configuration in one branch, and resets the cluster as needed. Buffer-pool state is inspected and drained for the current EC policy. `DFSClientFaultInjector` is global and is restored in the retry test.

## Dependencies and Integration Points
The suite directly covers `DFSStripedInputStream`, `DFSInputStream`, `DFSClient`, NameNode block-location RPCs, EC raw decoders, simulated DataNode datasets, block-group parsing, `ElasticByteBufferPool`, `FSDataInputStream`, and the fault-injection hooks used by HDFS clients.

## Risks
Manual expected-byte generation duplicates striping layout assumptions and can drift with implementation changes. Some loops rely on positive reads and exact lengths; a zero read would hang without timeout. DataNode heartbeats are disabled, so tests rely on explicit block reports and synthetic state. Global `DFSClientFaultInjector` must be restored to avoid cross-test pollution.

## Test Signals
Signals include exact byte-array equality, component block metadata equality, decoded-data equality after DataNode failure, null buffer assertions after `unbuffer`, exact block-reader range lists, exception-message containment, and complete write/read equality for large retry coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamReadFailures.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamReadFailures.java

## Purpose
This test stresses striped-file reads when DataNode receiver thread capacity is constrained, ensuring concurrent EC reads either succeed or fail with the expected missing-block stripe exception.

## Important APIs, Types, and Functions
- Setup mirrors default EC read configuration: default EC policy, block size based on `stripesPerBlock`, native RS raw coder when available, a `MiniDFSCluster` with data plus parity nodes, disabled heartbeats, and EC policy set on `/`.
- `writeFile` writes deterministic bytes, waits for block groups to be reported, and validates data using `StripedFileTestUtil.checkData`.
- `testReadWithXceiverExhaustion` reconfigures each `DataNode` with `DFS_DATANODE_MAX_RECEIVER_THREADS_KEY = 2`, then launches concurrent stateful reads.

## Control Flow
The test writes ten EC files, each slightly larger than one stripe. It lowers each DataNode's receiver-thread limit, starts one thread per file behind a `CyclicBarrier`, reads all files concurrently with `StripedFileTestUtil.verifyStatefulRead`, waits on a `CountDownLatch`, joins all threads, and inspects collected exceptions. Only IOExceptions whose message indicates missing blocks in the stripe are tolerated.

## State and Persistence Behavior
The test persists ten striped files and mutates DataNode runtime configuration via reconfiguration. It maintains shared exception and thread lists and uses synchronization primitives to maximize simultaneous load. Cluster lifetime is per test through `@TempDir`.

## Dependencies and Integration Points
It exercises DataNode reconfiguration, DataXceiver accounting, concurrent `DFSStripedInputStream` stateful reads, EC block reporting, and `StripedFileTestUtil` validation under resource pressure.

## Risks
The reconfiguration-complete loop is logically weak: it sets completion true regardless of whether all xceiver counts reached the target after one pass. Concurrent exception collection uses a plain `ArrayList`, which is not thread-safe. Accepted failure is message-substring based and could become brittle. The test is tagged slow and can be timing-sensitive.

## Test Signals
The signal is absence of unexpected exceptions during synchronized concurrent reads, with explicit tolerance for known "missing blocks, the stripe is" IOExceptions when xceivers are exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamReadFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java

## Purpose
This subclass reruns the `TestDFSStripedInputStream` suite with a random non-default erasure coding policy, broadening read coverage beyond the default policy geometry.

## Important APIs, Types, and Functions
- Extends `TestDFSStripedInputStream`.
- Constructor selects `StripedFileTestUtil.getRandomNonDefaultECPolicy()` and logs it.
- Overrides `getEcPolicy` to return the selected policy so inherited setup uses different data/parity/cell-size parameters.

## Control Flow
There are no local test methods. JUnit inherits the parent class tests, and the overridden policy changes all parent setup calculations and expected-byte paths. The parent has a guard in `testBlockReader` to skip range expectations when the active policy is not the default `RS-6-3-1024k`.

## State and Persistence Behavior
State is a single instance-level `ErasureCodingPolicy` chosen at construction and then used for all inherited tests in that instance. All cluster, file, and buffer state is managed by the parent class.

## Dependencies and Integration Points
This integrates the parent striped input-stream suite with the broader EC policy catalog exposed by `StripedFileTestUtil`, validating that parent logic is policy-parametric.

## Risks
Random policy selection can make failures less reproducible unless logs are retained. Some inherited assertions may be implicitly tuned to default geometry; the parent skip in `testBlockReader` handles one known default-specific case.

## Test Signals
The signal is inherited read-suite success under a non-default EC policy, demonstrating that `DFSStripedInputStream` behavior is not coupled to one policy shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStream.java

## Purpose
`TestDFSStripedOutputStream` validates writing HDFS erasure-coded files across many file lengths and verifies stream capability, block-size validation, and close/lease recovery behavior for EC output streams.

## Important APIs, Types, and Functions
- `getEcPolicy` returns the default EC policy and supports subclass override.
- Setup derives EC geometry, configures block size, disables load-based redundancy consideration, sets native RS raw coder when available, starts a cluster with data+parity+2 DataNodes, enables EC policies, and sets the policy on root.
- `testOneFile` writes deterministic bytes with `DFSTestUtil.writeFile`, waits for block groups, and verifies contents with `StripedFileTestUtil.checkData`.
- Close-exception tests construct `DFSClient`/`DFSOutputStream` directly and spy `completeFile`.
- `isFileClosed` and `waitForFileClosed` poll file-closed state after recovery attempts.

## Control Flow
A series of short tests call `testOneFile` for boundary lengths: empty, smaller/equal/larger than one cell, smaller/equal/larger than one stripe, less/equal/more than a full block group, and multiple block groups. `testStreamFlush` verifies that EC streams do not advertise `hflush`/`hsync` capabilities but that calling `hflush`, `hsync`, and `hsync(UPDATE_LENGTH)` does not throw `UnsupportedOperationException`.

`testFileBlockSizeSmallerThanCellSize` expects file creation to fail if the requested block size is less than the EC cell size. The two close-exception tests inject an IOException from `completeFile` and compare behavior with `RECOVER_LEASE_ON_CLOSE_EXCEPTION_KEY` enabled versus default disabled.

## State and Persistence Behavior
Each test writes EC files in a fresh cluster and relies on block groups being reported before verification. Close-exception tests intentionally leave a file under lease and then either recover it or verify it remains unclosed. The root EC policy is set for the cluster, so all created files use `DFSStripedOutputStream` unless otherwise configured.

## Dependencies and Integration Points
The test touches `DFSStripedOutputStream`, `DFSOutputStream`, `DataStreamer`, HDFS EC policy administration, stream capability APIs, block-size validation in create paths, client lease recovery on close exception, and file-closed state observation.

## Risks
Length boundary coverage is broad but uses helper validation; failures may require inspecting `StripedFileTestUtil`. `testStreamFlush` validates no exception and capability flags, not durable flush semantics. Spy-based close tests depend on implementation method boundaries around `completeFile`.

## Test Signals
Signals include full data verification for many EC file geometries, capability assertions, expected IOException text for invalid block size, stream type assertions, lease-recovered flag assertions, and eventual file-closed polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java

## Purpose
This file targets hang/regression scenarios in `DFSStripedOutputStream` pipeline update and second-block-group allocation when EC writes encounter severe DataNode loss or add-block exceptions.

## Important APIs, Types, and Functions
- `MiniDFSCluster` creates small EC-specific clusters.
- `DistributedFileSystem` enables and assigns EC policies (`RS-3-2-1024k`, `XOR-2-1-1024k`).
- `FSDataOutputStream` performs byte-wise writes.
- `IOUtils.closeStream` is used in `finally` to assert that cleanup/close does not hang after failures.

## Control Flow
`testDFSStripedOutputStreamUpdatePipeline` writes to an EC file in an unbounded loop until it reaches 5 MiB, then stops three DataNodes. Any exception causes the partially written file to be deleted; the important final assertion is implicit: closing the stream must return.

`testECWriteHangWhenAddBlockWithException` writes one XOR EC block group, sets a quota on the directory to force an add-block failure on subsequent writes, deletes the file on exception, and closes the stream under a 90-second timeout.

## State and Persistence Behavior
The tests create EC directories and files, stop DataNodes during an active write, set namespace/storage quota, and delete files after expected error paths. Their persistence concern is stream and lease cleanup after failures, not final file contents.

## Dependencies and Integration Points
They exercise EC write pipeline update, DataStreamer failure handling, NameNode add-block error propagation, quota enforcement, close/abort cleanup, and timeout-based hang detection.

## Risks
The first test relies on an exception to break an otherwise `Integer.MAX_VALUE` loop; if behavior changes to keep accepting writes longer than expected, runtime could be high. It has no explicit timeout annotation. Assertions are mostly implicit through no hang/no uncaught exception, so diagnostics may be limited.

## Test Signals
Primary signals are timeout-free completion and successful stream close after pipeline failure or quota-triggered add-block failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java

## Purpose
This slow suite extends `TestDFSStripedOutputStreamWithFailureBase` to validate EC striped writes under DataNode failures, token expiry, insufficient live nodes, close exceptions in streamers, abort handling, and short-stripe edge cases.

## Important APIs, Types, and Functions
- Inherits EC geometry, cluster fields, `newHdfsConfiguration`, `setup`, `tearDown`, `getLength`, `getKillPositions`, `runTest`, and `runTestWithMultipleFailure` from `TestDFSStripedOutputStreamWithFailureBase`.
- The base uses a custom `ErasureCodingPolicy` with 64 KiB cells, computes block/group sizes, writes byte-by-byte, kills DataNodes at configured positions, tracks generation stamps, waits for block reports, and verifies data with `StripedFileTestUtil.checkData`.
- Local helpers include `testCloseWithExceptionsInStreamer`, which injects `IOException` into `StripedDataStreamer#getLastException`.
- Tests use `LambdaTestUtils.intercept` for expected IOExceptions and `datanodeReport(LIVE)` for topology assertions.

## Control Flow
`testMultipleDatanodeFailure56` selects one generated length and runs the inherited multi-failure matrix. `testBlockTokenExpired` enables block tokens, shortens retries, and runs one failure case for every other streamer with token expiration enabled. `testAddBlockWhenNoSufficientDataBlockNumOfNodes` stops DataNodes until fewer than `dataBlocks` live nodes remain, restarts NameNodes, and verifies create/write fails with an explanatory message.

Close-path tests intentionally fail initial close, inject streamer exceptions up to parity and above parity counts, and assert idempotent close behavior. `testCloseAfterAbort` aborts a striped stream then expects close to report lease timeout. `testAddBlockWhenNoSufficientParityNumOfNodes` stops fewer parity nodes, writes a short file, and verifies it remains readable. `testCloseWithExceptionsInStreamer` runs failures at partial-block DataNode indexes for cell-boundary and non-cell-boundary lengths. `runTestWithShortStripe` writes a one-cell partial stripe while killing all but one DataNode.

## State and Persistence Behavior
Each test sets up and tears down clusters manually rather than using JUnit per-test cluster setup. Tests mutate live DataNode topology, restart NameNodes, trigger heartbeats/block reports, inject stream exceptions, abort streams, and create EC files under the inherited `dir`. Token-expiry scenarios mutate block token lifetime in the NameNode block manager.

## Dependencies and Integration Points
Coverage spans `DFSStripedOutputStream`, `StripedDataStreamer`, block token security, block placement requirements, EC add-block logic, NameNode/DataNode liveness reporting, lease timeout/abort behavior, generation stamp tracking, and EC readback verification after write failures.

## Risks
The inherited base has many timing-sensitive operations: byte-wise writes, DataNode stops at exact positions, token expiration polling, heartbeats, block reports, and data verification after topology changes. Some tests call `setup`/`tearDown` manually inside test methods, so errors can leave partial state if `finally` is missed. The random-length test is disabled, reducing nondeterministic coverage.

## Test Signals
Signals include successful data verification after planned failures, exact live-DataNode counts, expected insufficient-node error messages, close idempotency across injected streamer exceptions, expected lease timeout after abort, and successful short-stripe readback despite many failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java -->
