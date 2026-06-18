# subset-b-007520 research

Grouped research report for Hadoop HDFS test sources. Each section preserves the original source path and is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AppendTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AppendTestUtil.java

## Purpose
`AppendTestUtil` is a small HDFS test helper focused on deterministic byte generation, append-file creation, and byte-for-byte verification. It supports append tests that need stable pseudo-random content, block-size constants, alternate-user access, and assertions that an appended file's length and content match the expected sequence.

## Important APIs, types, and functions
- Constants: `BLOCK_SIZE`, `NUM_BLOCKS`, and `FILE_SIZE` define small test file dimensions used by append-oriented tests.
- Random helpers: `randomBytes(long, int)`, `randomFilePartition(int, int)`, `nextInt`, and `nextLong` derive repeatable content from seeds and log the seed values for reproduction.
- User helper: `createHdfsWithDifferentUsername(Configuration)` builds a testing UGI with a modified username and returns a `FileSystem` through `DFSTestUtil.getFileSystemAs`.
- Data generation and validation: `write(OutputStream, int, int)`, `check(FileSystem, Path, long)`, `check(DistributedFileSystem, Path, int, int)`, `initBuffer(int)`, `checkFullFile(...)`, and private `checkData(...)`.
- Append scenario helper: `testAppend(FileSystem, Path)` creates a file, appends fixed content repeatedly, verifies length after each append, and re-reads every segment.

## Control flow
Class initialization chooses a random or configured global seed, logs it, and seeds a shared `Random`. Each thread receives its own `Random` seeded from the global generator under synchronization. File validation opens the target file, checks length either through `DFSInputStream.getFileLength()` or `FileStatus.getLen()`, then reads expected bytes and EOF. Full-file validation reads the entire file with positional `readFully` and compares against the expected buffer. `testAppend` runs a create-append-read loop: create initial content, append 48 more copies, check size after each close, then positional-read every copy.

## State and persistence behavior
The class has process-local random state in `SEED`, thread-local `RANDOM`, and mutable static `seed` used by `initBuffer`. Persistent effects are limited to files created, appended, or read through the supplied `FileSystem`. `createFile` returns an unclosed `FSDataOutputStream`, so callers own stream closure. The utility does not clean up paths except inside helpers that only read or assert.

## Dependencies and integration points
It depends on HDFS client classes (`DistributedFileSystem`, `DFSInputStream`), Hadoop `FileSystem` APIs, `UserGroupInformation`, JUnit assertions, and `DFSTestUtil`. It is integrated by append tests such as `FileAppendTest4`, which uses `initBuffer` and `checkFullFile` to validate append and `hflush` behavior under tiny block/checksum sizes.

## Risks and edge cases
`randomFilePartition` assumes `n` is large enough for the requested number of parts; invalid ranges can make `nextInt` fail. `initBuffer` uses a shared static `seed`, so tests in the same JVM can reuse content unexpectedly if they assume fresh randomness. `check(FileSystem, Path, long)` casts `length` to int in one diagnostic state assignment and reads one byte at a time, making it suitable for small test files but inefficient for large files. `testAppend` relies on `seed`; if `initBuffer` was never called, `seed` may remain `-1`, producing deterministic but perhaps unintended data.

## Test signals
The utility is itself test support. Strong signals are byte-for-byte assertions, length assertions after every append close, EOF validation, and reproducible seed logging. Failures include path, expected length, and byte index context to simplify debugging append corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/AppendTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/BenchmarkThroughput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/BenchmarkThroughput.java

## Purpose
`BenchmarkThroughput` is a command-line `Tool` that measures simple read/write throughput for local files, raw local Hadoop files, checksum local files, and a single-rack `MiniDFSCluster`. It is intended as a manual benchmark utility rather than a JUnit test.

## Important APIs, types, and functions
- `run(String[])` parses an optional repetition count, resolves benchmark configuration, creates local and HDFS files, and prints elapsed seconds.
- `writeLocalFile` / `readLocalFile` use Java `FileOutputStream` and `FileInputStream` against paths allocated by `LocalDirAllocator`.
- `writeFile` / `readFile` perform equivalent operations through a Hadoop `FileSystem`.
- `writeAndReadLocalFile` and `writeAndReadFile` wrap write/read pairs and best-effort cleanup.
- `main` runs the tool under `HdfsConfiguration` through `ToolRunner`.

## Control flow
The tool silences broad Hadoop logging to WARN, parses either zero or one argument, and reads `dfsthroughput.file.size` and `dfsthroughput.buffer.size` from the configuration. It chooses `mapred.temp.dir`, falling back to `hadoop.tmp.dir`, and initializes a `LocalDirAllocator`. For each repetition, it writes and reads a plain local file, a raw local `FileSystem` file, and a checksum local file. It then starts a `MiniDFSCluster`, waits for it to become active, benchmarks DFS reads/writes, shuts the cluster down, and removes the `dfs` subdirectory left in the local temp area.

## State and persistence behavior
Measurements are process-local and stored in `startTime`; file paths are allocated under the configured temp directory. The benchmark creates large temporary data files and deletes them after each write/read pair. The `MiniDFSCluster` persists data under `test.build.data` while active and is shut down in a `finally` block.

## Dependencies and integration points
The tool depends on Hadoop `Tool`, `Configured`, `LocalDirAllocator`, `ChecksumFileSystem`, `FileSystem`, `MiniDFSCluster`, `GenericTestUtils`, and `Time`. It integrates with Hadoop's generic options through `ToolRunner`, so standard configuration overrides can drive file size, buffer size, and temp directories.

## Risks and edge cases
The default file size is 10 GB, so accidental runs can consume disk and time. Write loops increment by `BUFFER_SIZE` and write a full buffer each iteration, so if the configured size is not a multiple of the buffer, it can write slightly more than the requested total. Read loops ignore the actual byte count except for EOF detection, so this is throughput smoke measurement rather than content verification. Cleanup uses best-effort deletion and ignores deletion failures for `FileSystem` files.

## Test signals
Signals are printed elapsed seconds for each operation and successful completion of filesystem create/open/delete paths. There are no assertions or correctness checks beyond exceptions from filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/BenchmarkThroughput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSClientAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSClientAdapter.java

## Purpose
`DFSClientAdapter` is a package-level test adapter that exposes otherwise internal HDFS client fields and methods to tests. It avoids reflection by living in the same package as `DistributedFileSystem`, `DFSClient`, and `DFSOutputStream`.

## Important APIs, types, and functions
- `getDFSClient`, `getClient`, and `setDFSClient` read or replace the `DistributedFileSystem.dfs` field.
- `stopLeaseRenewer` interrupts and joins the active lease renewer.
- `callGetBlockLocations` invokes `DFSClient.callGetBlockLocations`.
- `getNamenode` exposes the `DFSClient.namenode` protocol proxy.
- `getPreviousBlock` delegates to `DFSClient.getPreviousBlock`.
- `getFileId` exposes `DFSOutputStream.getFileId`.

## Control flow
All methods are direct static pass-throughs. The only control-flow branch is `stopLeaseRenewer`, which translates `InterruptedException` into `IOException` after calling `interruptAndJoin`.

## State and persistence behavior
The adapter mutates client state only through `setDFSClient` and `stopLeaseRenewer`. Those operations can change lease-renewal behavior, outstanding stream behavior, and subsequent RPC routing for the supplied `DistributedFileSystem`. It does not persist data itself.

## Dependencies and integration points
It depends on `DistributedFileSystem`, `DFSClient`, `DFSOutputStream`, `ClientProtocol`, `LocatedBlocks`, and `ExtendedBlock`. It is used by tests that need to force lease recovery, inspect previous blocks, call NameNode RPCs directly, or simulate unusual DFS client states.

## Risks and edge cases
Because it reaches into internal mutable fields, it can leave a filesystem instance in a state normal production code cannot create. Replacing a `DFSClient` may break ownership assumptions around leases, sockets, statistics, and cached configuration. Interrupting the lease renewer affects all streams tied to that client.

## Test signals
The adapter has no assertions of its own. Its signal is enabling tests to observe internal file IDs, NameNode block locations, previous-block state, and lease-renewer transitions that would otherwise be inaccessible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSClientAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSTestUtil.java

## Purpose
`DFSTestUtil` is a broad HDFS test support library. It creates deterministic files and clusters, waits for asynchronous NameNode/DataNode state, exposes protocol helpers, builds synthetic block and datanode metadata, runs HDFS command-line tools, manipulates internal NameNode state, and verifies replication, erasure coding, cache, storage policy, permissions, snapshots, trash, and fsck behavior.

## Important APIs, types, and functions
- File generation and checking: constructor/builder, inner `MyFile`, `createFiles`, `createFile` overloads, `calculateFileContentsFromSeed`, `checkFiles`, `getFileNames`, `cleanup`, `readFile*`, `writeFile`, `appendFile`, and `appendFileNewBlock`.
- Cluster and configuration: `formatNameNode`, `newHAConfiguration`, `addHAConfiguration`, `setFakeHttpAddresses`, `setFederatedConfiguration`, `setFederatedHAConfiguration`, `setupCluster`, and `setEditLogForTesting`.
- Replication and datanode waits: `waitReplication`, `waitForReplication`, `waitCorruptReplicas`, `waitForDecommission`, `waitForDatanodeStatus`, `waitForDatanodeDeath`, `waitForDatanodeState`, `firstDnWithBlock`, and capacity helpers.
- Block and protocol helpers: `getFirstBlock`, `getAllBlocks`, `getBlockToken`, `transferRbw`, `replaceBlock`, `changeReplicaLength`, `setPipeline`, `abortStream`, `getExpectedPrimaryNode`, NameNode proxy helpers, and block-report builders.
- Datanode metadata factories: `getLocalDatanodeID`, `getDatanodeInfo`, `getDatanodeDescriptor`, `createDatanodeStorageInfo(s)`, `toDatanodeDescriptor`, and `getLocalDatanodeRegistration`.
- Erasure coding helpers: `enableAllECPolicies`, `getECPolicyState`, `createStripedFile`, `addBlockToFile`, `flushInternal`, `flushBuffer`, and EC sections in `runOperations`.
- CLI and admin helpers: `toolRun`, `FsShellRun`, `DFSAdminRun`, `runFsck`, and `getNameNodeConnector`.
- Verification helpers: `verifyExpectedCacheUsage`, `checkComponentsEquals`, `verifyFilesEqual`, `verifyFilesNotEqual`, `verifyFileReplicasOnStorageType`, `verifyClientStats`, `verifyFilePermission`, `verifyDelete`, `verifySnapshotDiffReport`, `waitExpectedStorageType`, `waitForXattrRemoved`, and `waitForMetric`.
- Security and identity helpers: `MockUnixGroupsMapping`, `updateConfWithFakeGroupMapping`, `getFileSystemAs`, `login`, `createKey`, and `deleteKey`.

## Control flow
The instance-level file workflow seeds `MyFile` records with randomized names, sizes, and content seeds, writes them under a root path, and later replays the same seeds to validate content. The static `createFile` overloads ensure parent directories exist, choose create flags including optional lazy-persist and overwrite, then stream pseudo-random bytes until the requested length is written. Wait helpers use polling loops or `GenericTestUtils.waitFor` to observe eventually consistent NameNode/DataNode state.

Several helpers intentionally drive low-level HDFS control paths. `runOperations` executes a long sequence of filesystem mutations to produce edit log records across create, append, abandon block, storage policy, rename, delete, mkdir, snapshots, replication, permissions, owner, times, quotas, concat, truncate, symlink, lease recovery, cache directives, ACLs, xattrs, and erasure-coding policy operations. `createStripedFile` and `addBlockToFile` create NameNode metadata and synthetic incremental block reports without writing real DataNode bytes. `replaceBlock` and `transferRbw` open data-transfer sockets and send protocol messages directly.

## State and persistence behavior
Instance state tracks file-generation parameters and the generated `MyFile[]` until `cleanup` deletes the root and clears it. Static mutable state includes the random generator and fake group mapping. Persistent effects can be extensive: formatting NameNodes, creating and deleting HDFS files, changing leases and quotas, adding cache pools/directives, adding/removing EC policies, modifying key-provider state, changing block files on DataNodes with `RandomAccessFile`, and creating socket directories for short-circuit tests. Many helpers intentionally mutate internal NameNode or DataNode state for tests and must be isolated by `MiniDFSCluster` setup/teardown.

## Dependencies and integration points
The class integrates with most HDFS test infrastructure: `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `DFSOutputStream`, `DFSStripedOutputStream`, NameNode and FSNamesystem internals, block-management classes, DataNode protocol classes, data-transfer `Sender`, encryption key providers, snapshot diff APIs, storage policy satisfier, JMX, `FsShell`, `DFSAdmin`, and `DFSck`. It also uses JUnit assertions/assumptions, `GenericTestUtils`, Hadoop security UGI/group mapping, native IO, domain sockets, and third-party utility classes.

## Risks and edge cases
This is a high-power test utility with many internal mutations. Wait methods use fixed retry windows that may be flaky on slow systems. Helpers such as `setEditLogForTesting`, `createStripedFile`, `addBlockToFile`, `setDatanodeDead`, and `changeReplicaLength` can make cluster state unrealistic if used outside narrow tests. `toolRun` redirects global `System.out` and `System.err`, which can interfere with concurrent tests. Some methods use Java `assert`, so checks disappear unless assertions are enabled. Socket helpers assume protocol details and may hang or fail if datanode endpoints or status expectations differ. `getNameNodeConnector` loops until success and can run indefinitely if configuration is wrong.

## Test signals
Signals are primarily JUnit assertions, explicit timeout exceptions, `GenericTestUtils.waitFor` polling, and content comparisons. The utility verifies replication counts, corrupt replicas, datanode liveness, cache metrics, client block stats consistency, file equality/inequality, storage type placement, permissions, trash behavior, snapshot diff symmetry, JMX metrics, xattr removal, CLI return codes/output substrings, fsck return codes, and exact read lengths for synthetic content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DataNodeCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DataNodeCluster.java

## Purpose
`DataNodeCluster` is a standalone test/benchmark utility that starts many DataNodes, optionally simulated, in one JVM without starting a NameNode. It targets scenarios where an external NameNode is already running and needs a large set of connected DataNodes, optionally with injected synthetic blocks for NameNode-scale benchmarking.

## Important APIs, types, and functions
- `main(String[])` parses options, configures simulated storage, starts DataNodes through `MiniDFSCluster`, and optionally injects blocks.
- `printUsageExit` overloads report command syntax and exit.
- `getUniqueRackPrefix` creates a mostly unique rack prefix from local DNS, secure random, and current time.
- Command options include `-n`, `-bpid`, `-racks`, `-simulated`, `-inject`, `-r`, `-d`, and `-checkDataNodeAddrConfig`.

## Control flow
The program parses arguments into DataNode count, rack count, block pool ID, simulated dataset settings, injection settings, replication, and data directories. It validates positive DataNode/replication counts, replication not exceeding DataNodes, and required block pool ID and NameNode address. It sets `test.build.data`, formats DataNode directories with a bare `MiniDFSCluster`, builds optional rack assignments, starts DataNodes against the configured external NameNode, sleeps ten seconds for registration, then injects blocks if requested. Injection creates sequential `Block` arrays per source DataNode and injects replicas into that DataNode and its neighbors modulo the DataNode count.

## State and persistence behavior
The default DataNode data root is `/tmp/DataNodeCluster`, overridable by `-d`, and assigned to `test.build.data`. With non-simulated DataNodes, storage directories and block data persist there. With simulated storage, capacity is configured through `SimulatedFSDataset`. Injected block metadata is placed into DataNode datasets for the specified block pool ID but must correspond to NameNode namespace/edit-log state generated separately.

## Dependencies and integration points
The utility depends on `HdfsConfiguration`, `MiniDFSCluster`, `SimulatedFSDataset`, `FsDatasetSpi.Factory`, `CreateEditsLog`, `Block`, `StartupOption`, `DNS`, and `DFSUtil`. Its intended pair is `CreateEditsLog`, which can create matching edit logs for the external NameNode so injected DataNode block reports are meaningful.

## Risks and edge cases
The tool calls `System.exit` on invalid input and is not a reusable library entry point. `-inject` is valid only after simulated storage has been selected; option ordering matters because the check occurs during parsing. The ten-second sleep is heuristic and may not be enough for very large clusters or slow hosts. Defaulting to `/tmp/DataNodeCluster` risks clobbering prior test state. Rack prefix generation is probabilistic, not guaranteed unique.

## Test signals
Signals are console messages for selected NameNode authority, rack assignment, DataNode startup errors, injection ranges, and per-replica injection targets. There are no JUnit assertions; validation is through process success and downstream NameNode/DataNode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DataNodeCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ErasureCodeBenchmarkThroughput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ErasureCodeBenchmarkThroughput.java

## Purpose
`ErasureCodeBenchmarkThroughput` is a command-line `Tool` for measuring HDFS client throughput for replicated files versus erasure-coded files. It supports read, write, generated-data setup, and cleanup operations, with multiple concurrent client threads and either stateful or positional reads.

## Important APIs, types, and functions
- Constants define benchmark directories under `test.benchmark.data`, file naming, temporary suffixes, default EC policy, and a 128 MB random data buffer.
- `getEcPolicy` and `getFilePath(int, boolean)` expose the policy and deterministic path naming.
- `run(String[])` parses `<read|write|gen|clean> <sizeMB> <ec|rep> [numClients] [stf|pos]`, prepares directories, optionally tunes striped read threads, and dispatches.
- `setUpDir` creates replica and EC parent directories and sets or validates the EC policy.
- `doBenchmark` uses a fixed thread pool and `ExecutorCompletionService` to run one callable per client.
- `WriteCallable` writes generated or temporary files; `ReadCallable` performs stateful `ByteBuffer` reads or positional byte-array reads and validates byte count.

## Control flow
Startup validates the filesystem is a `DistributedFileSystem`, initializes the random data buffer once, parses command arguments, and always calls `setUpDir`. Clean mode lists files in the selected benchmark directory and deletes those whose path contains the generated base filename. Non-clean operations submit read or write callables for client IDs `0..numClients-1`, wait for all completions, sum non-negative byte counts, and print elapsed seconds plus aggregate MB/s. EC reads set the striped-read thread pool to `numClients * dataUnits` before benchmarking.

## State and persistence behavior
Generated files persist under `/tmp/benchmark/data` by default, split into `replica` and `ec` directories. Write-mode temporary files use `.tmp` and are registered with `deleteOnExit`; generated files are retained for later read benchmarks. Directory EC policy is persistent HDFS metadata. The process stores only in-memory random data and callable results.

## Dependencies and integration points
It depends on `DistributedFileSystem`, HDFS EC policy APIs, `StripedFileTestUtil`, `HdfsClientConfigKeys.StripedRead`, Hadoop `ToolRunner`, Java concurrency utilities, and `StopWatch`. It integrates with real HDFS clusters through `FileSystem.get(conf)` and can benchmark EC behavior configured by the cluster's default test EC policy.

## Risks and edge cases
Throughput divides by elapsed seconds; very small benchmarks can produce zero elapsed seconds and invalid/infinite throughput. The executor is not explicitly shut down, so the JVM process exit is relied on for cleanup. `cleanUp` filters using `path.toString().contains(fileName)`, which is broad and can delete any matching path in the selected directory. Existing generated files cause writes to return `0L`, so stale data can silently affect benchmark interpretation. The 128 MB static buffer creates nontrivial heap pressure.

## Test signals
The benchmark prints per-file operation start/finish messages and total throughput. Read callables assert that bytes read exactly equal requested size using `Preconditions.checkArgument`. Directory setup validates EC/non-EC policy expectations with preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ErasureCodeBenchmarkThroughput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/FileAppendTest4.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/FileAppendTest4.java

## Purpose
`FileAppendTest4` is a JUnit 5 append stress test that exhaustively checks combinations of initial file length and two appended byte ranges, including an `hflush` between append writes. It targets boundary behavior around checksum, packet, and block sizes.

## Important APIs, types, and functions
- Constants use very small settings: 4-byte checksums, 4-byte packets, 8-byte blocks, replication 3, and 5 DataNodes.
- `init(Configuration)` sets checksum, block size, and client packet size.
- `startUp` creates a `MiniDFSCluster` and obtains a `DistributedFileSystem`.
- `tearDown` shuts the cluster down.
- `testAppend` runs the exhaustive create/append/hflush/append/close/verify/delete loop.

## Control flow
Before all tests, the class initializes HDFS client settings and starts a five-DataNode mini cluster. The test allocates a deterministic content buffer large enough for the maximum file length. Three nested loops iterate `oldFileLen` from 0 through `2 * BLOCK_SIZE + 1`, and each appended segment from 0 through `BLOCK_SIZE`. For each combination, it creates a unique path, writes the initial prefix, closes it, reopens for append, writes the first append segment, calls `hflush`, writes the second segment, closes, verifies the complete file content, and deletes the file.

## State and persistence behavior
Class-level static fields hold the cluster, configuration, and filesystem for the whole test class. Each loop iteration creates and deletes one HDFS file. `hflush` persists the first append segment into the pipeline before the second append and close.

## Dependencies and integration points
The test depends on `MiniDFSCluster`, `DistributedFileSystem`, `HdfsConfiguration`, `HdfsClientConfigKeys`, `DFSConfigKeys`, `AppendTestUtil`, JUnit lifecycle annotations, and HDFS output stream semantics.

## Risks and edge cases
The nested loops create many files and append operations, making the test comprehensive but potentially slow. Tiny block/checksum/packet sizes exercise edge cases that production-sized buffers may not hit. If a failure occurs before deletion, temporary files may remain until cluster teardown. Static cluster state means failures in startup affect the whole class.

## Test signals
Signals are JUnit assertions inside `AppendTestUtil.checkFullFile`, file length checks, byte-for-byte content validation, and exceptions from create/append/hflush/close. The path name encodes the tested tuple, helping identify the failing boundary case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/FileAppendTest4.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ListingBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ListingBenchmark.java

## Purpose
`ListingBenchmark` is a skeletal benchmark entry point for NameNode listing-related experimentation. In its current form it only starts a formatted `MiniDFSCluster` with zero DataNodes and obtains the `NameNode`.

## Important APIs, types, and functions
- `main(String[])` constructs `HdfsConfiguration`, builds `MiniDFSCluster` with `.numDataNodes(0).format(true)`, and assigns `cluster.getNameNode()` to a local variable.

## Control flow
The program creates a fresh formatted NameNode-only mini cluster. There is no workload, listing call, output, cleanup, or argument parsing after obtaining the NameNode reference.

## State and persistence behavior
It formats a mini-cluster namespace using default test directories and leaves the cluster running until process exit. No HDFS files are created by this class.

## Dependencies and integration points
It depends on `HdfsConfiguration`, `MiniDFSCluster`, and `NameNode`. It appears intended as a future benchmark harness that would call NameNode listing APIs directly or through a filesystem client.

## Risks and edge cases
The absence of shutdown can leave temporary test resources until JVM exit. Because no benchmark operation is implemented, running the class does not produce useful performance data. Zero DataNodes is suitable for namespace-only tests but not block-location-sensitive listing scenarios.

## Test signals
The only signal is whether a formatted NameNode-only `MiniDFSCluster` can be constructed. There are no assertions, metrics, or printed results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/ListingBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/LogVerificationAppender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/LogVerificationAppender.java

## Purpose
`LogVerificationAppender` is a Log4j test appender that captures logging events in memory and counts events containing expected exception messages or rendered log text. Tests can attach it to a logger to verify that a path logged a warning/error without parsing external log files.

## Important APIs, types, and functions
- Extends `AppenderSkeleton`.
- `append(LoggingEvent)` stores events in an internal list.
- `getLog()` returns a defensive copy of captured events.
- `countExceptionsWithMessage(String)` scans throwable messages for a substring.
- `countLinesWithMessage(String)` scans rendered log messages for a substring.
- `requiresLayout()` returns false and `close()` is a no-op.

## Control flow
Log4j calls `append` for each event, and the appender records it. Counting methods iterate over a defensive copy returned by `getLog`, inspect either `ThrowableInformation` or `getRenderedMessage`, and increment counters for substring matches.

## State and persistence behavior
State is an in-memory `ArrayList<LoggingEvent>` for the lifetime of the appender. There is no persistence and no automatic clearing. The list is not synchronized, so concurrent logging and verification can race.

## Dependencies and integration points
The appender depends on Log4j 1.x `AppenderSkeleton`, `LoggingEvent`, and `ThrowableInformation`. It integrates with tests that attach custom appenders to Hadoop/HDFS loggers and then assert message counts.

## Risks and edge cases
`countExceptionsWithMessage` assumes `t.getThrowable().getMessage()` is non-null; a throwable with a null message can cause `NullPointerException`. The unsynchronized list can be unsafe with concurrent appenders. Since matching uses substring containment, broad text can overcount unrelated log events.

## Test signals
The test signal is the count of captured exception or rendered-message lines containing expected text. It allows tests to assert logging side effects without relying on filesystem log output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/LogVerificationAppender.java -->
