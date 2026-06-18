# Research: subset-b-007392

Grouped source research for Hadoop common filesystem tests and load generator utilities. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestExecutorServiceFuturePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestExecutorServiceFuturePool.java

## Purpose
Tests `ExecutorServiceFuturePool`, the prefetch package adapter that submits runnable and supplier-style work to a Java `ExecutorService` and returns `Future<Void>` handles. The file verifies both successful task execution and exception propagation through returned futures.

## Important APIs, Types, and Functions
The test class extends `AbstractHadoopTestBase` and uses JUnit 5 lifecycle methods. `setUp()` creates a fixed thread pool of size 3 with `Executors.newFixedThreadPool(3)`, and `tearDown()` always calls `shutdownNow()` to stop worker threads. Test methods instantiate `ExecutorServiceFuturePool` and exercise `executeRunnable(Runnable)` and `executeFunction(Supplier<T>)`. Success tests use an `AtomicBoolean` as the observable side effect and `Future.get(30, TimeUnit.SECONDS)` as the synchronization point. Failure tests use `LambdaTestUtils.interceptFuture` to assert that an `IllegalStateException` with message `deliberate` emerges from the asynchronous future.

## Control Flow
Each test builds a fresh pool wrapper over the shared executor. Success flows submit a closure, wait up to 30 seconds, then assert that the closure ran. Failure flows submit a closure that throws and then delegate to `interceptFuture`, which unwraps future completion failures and checks type/message. There is no retry or pooling logic in the test itself; it is focused on delegation semantics.

## State and Persistence
The only persistent-in-test state is `executorService`; it is recreated for every test and shut down after each test. `AtomicBoolean` instances are local and used only to detect task execution. No filesystem or external state is touched.

## Dependencies and Integration Points
The test integrates with Java concurrency primitives, JUnit 5, Hadoop test helpers, and the production `ExecutorServiceFuturePool`. It is a direct unit test of the prefetch executor abstraction used by asynchronous prefetch code.

## Risks and Edge Cases
The 30 second timeout prevents deadlocked futures from hanging the suite indefinitely. The tests cover both runnable and function entry points but do not validate cancellation, executor rejection, shutdown behavior, or thread naming. They also assume exception type/message are preserved through future wrapping.

## Test Signals
Passing tests signal that submitted work actually executes, returned futures complete, and failures remain inspectable to callers. They give regression coverage for asynchronous error propagation in prefetch infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestExecutorServiceFuturePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestFilePosition.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestFilePosition.java

## Purpose
Exercises `FilePosition`, a prefetch helper that tracks the current file offset relative to a `BufferData` block, validates buffer boundaries, and records read statistics. The tests concentrate on argument validation, valid/invalid lifecycle, offset math, buffer consumption counters, and EOF boundary behavior.

## Important APIs, Types, and Functions
The class uses `ByteBuffer.allocate`, `BufferData`, and `FilePosition`. Production methods under test include the constructor, `setData`, `invalidate`, `isValid`, `buffer`, `absolute`, `relative`, `setAbsolute`, `isWithinCurrentBuffer`, `blockNumber`, `isLastBlock`, `bufferStartOffset`, `incrementBytesRead`, `numBytesRead`, `numSingleByteReads`, `numBufferReads`, and `bufferFullyRead`. Assertions use both JUnit and AssertJ, with `LambdaTestUtils.intercept` validating exact validation failures.

## Control Flow
`testArgChecks` first proves legal constructor and `setData` combinations, then checks negative file size, non-positive block size, missing buffer access, null `BufferData`, negative offsets, and read offsets outside `[startOffset, startOffset + buffer.capacity()]`. `testValidity` transitions from invalid to valid after `setData`, then back to invalid after `invalidate`. `testOffsets` verifies absolute and relative offset math, current-buffer membership, block number calculation from `bufferStartOffset / bufferSize`, and last-block detection near EOF. `testBufferStats` increments read counters, distinguishes single-byte reads from larger buffer reads, and verifies `bufferFullyRead` after consuming all bytes from the `ByteBuffer`. `testBounds` checks the important EOF case: offset exactly equal to file size is treated as within the current buffer and can be set as the absolute position.

## State and Persistence
`FilePosition` holds transient state only: current `BufferData`, start/read offsets, validity, counters, and the `ByteBuffer` position. No external persistence exists. The tests intentionally reset state with `setData` to ensure counters return to zero for a new buffer.

## Dependencies and Integration Points
This test sits in the prefetch implementation package and has package-level access to helpers. It integrates with `BufferData`, `SampleDataForTests` only indirectly through package conventions, Java NIO buffers, and Hadoop test exception utilities. The production behavior feeds prefetch stream positioning and block boundary decisions.

## Risks and Edge Cases
Boundary correctness is the key risk. An off-by-one at EOF or buffer end would break reads at file boundaries. Counter reset behavior matters because stale counters could distort prefetch heuristics. The test does not cover concurrent access or varying `BufferData` block numbers beyond simple cases.

## Test Signals
Passing tests show that `FilePosition` rejects invalid initialization, requires a current buffer before exposing buffer-derived properties, computes offsets consistently, resets statistics per buffer, and accepts EOF as a valid absolute position.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestFilePosition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestRetryer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestRetryer.java

## Purpose
Tests `Retryer`, a small timing/counting helper used by prefetch code to decide whether retries should continue and whether status should be emitted at configured intervals.

## Important APIs, Types, and Functions
The production constructor `Retryer(int perRetryDelay, int maxDelay, int statusUpdateInterval)` is validated. Runtime methods under test are `continueRetry()` and `updateStatus()`. The test uses `LambdaTestUtils.intercept` for exact validation messages and JUnit booleans for state transitions.

## Control Flow
`testArgChecks` accepts a nominal `(10, 50, 500)` configuration and rejects non-positive retry delay, max delay smaller than per-retry delay, and non-positive status update interval. `testRetry` uses small integers: per-retry delay 1, status interval 3, max delay 10. It calls `continueRetry()` ten times and expects true each time, while `updateStatus()` returns true only at intervals divisible by 3. The eleventh `continueRetry()` returns false.

## State and Persistence
`Retryer` stores internal elapsed/retry state across method calls. There is no filesystem or process state. The test relies on deterministic counter progression rather than wall-clock sleeping.

## Dependencies and Integration Points
The class integrates with the prefetch package and Hadoop test base. It protects retry loops that likely wait for asynchronous prefetch conditions and log status periodically.

## Risks and Edge Cases
The main risks are off-by-one retry termination and mismatched status cadence. Tests do not cover larger `perRetryDelay` values beyond constructor validation, thread interruption, or actual sleeping behavior if production code sleeps elsewhere.

## Test Signals
Passing tests signal strict validation of retry configuration and predictable retry/status cadence up to the configured maximum delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestRetryer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestValidate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestValidate.java

## Purpose
Provides broad unit coverage for the prefetch package `Validate` utility. It locks down argument validation behavior and exact failure messages for null checks, positivity, range checks, list/array cardinality, equality, multiplicity, ordering, and filesystem path existence/type checks.

## Important APIs, Types, and Functions
The tests target static methods on `Validate`: `checkNotNull`, `checkPositiveInteger`, `checkNotNegative`, `checkRequired`, `checkValid`, `checkNotNullAndNotEmpty` overloads for strings, object arrays, primitive arrays, and lists, `checkNotNullAndNumberOfElements`, `checkValuesEqual`, `checkIntegerMultiple`, `checkGreater`, `checkGreaterOrEqual`, `checkWithinRange` for integer and double values, `checkPathExists`, `checkPathExistsAsDir`, and `checkPathExistsAsFile`. Test data comes from `SampleDataForTests`, and assertions use `LambdaTestUtils.intercept` plus `ExceptionAsserts.assertThrows`.

## Control Flow
Each test follows the same pattern: first assert that valid inputs do not throw, then assert that invalid inputs throw `IllegalArgumentException` with a precise message. The final path test creates a temporary file, derives its parent directory, and then checks existence plus file-vs-directory mismatches.

## State and Persistence
The validation utility is stateless. The only external state is the temporary file created via `Files.createTempFile`; it is used to test actual filesystem existence and type predicates. No persistent repository state is changed.

## Dependencies and Integration Points
`Validate` is a foundational internal helper for prefetch classes, so exact message stability affects tests such as `TestFilePosition` and `TestRetryer`. It depends on Java arrays/lists and `java.nio.file` for path validation. The tests also use Hadoop-specific exception assertion helpers.

## Risks and Edge Cases
The suite covers many overloads, including primitive arrays where null/empty handling can diverge. Exact-message assertions are useful for diagnostics but make tests sensitive to message wording. The path checks use the host filesystem and can be affected by unusual temp directory behavior, though the scenario is simple.

## Test Signals
Passing tests indicate that prefetch validation failures remain deterministic, descriptive, and consistent across data types and filesystem path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestValidate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/DataGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/DataGenerator.java

## Purpose
Implements a test utility `Tool` that materializes a namespace described by `StructureGenerator` output files. It reads directory and file structure descriptions from a local input directory, creates the namespace under a configured Hadoop `FileContext` root, and fills generated files with byte `a`.

## Important APIs, Types, and Functions
`DataGenerator` extends `Configured` and implements `Tool`. Important fields are `inDir`, `root`, `fc`, `BLOCK_SIZE`, `DEFAULT_ROOT`, and `USAGE`. `run` orchestrates `init`, `genDirStructure`, and `genFiles`. `init` parses `-root` and `-inDir` and initializes `FileContext.getFileContext(getConf())`. `genDirStructure` reads `StructureGenerator.DIR_STRUCTURE_FILE_NAME`; `genFiles` reads `StructureGenerator.FILE_STRUCTURE_FILE_NAME`; `genFile` uses `FileContext.create` with `CreateFlag.CREATE`, `CreateFlag.OVERWRITE`, `CreateOpts.createParent`, a 4096 byte buffer, and replication factor 3.

## Control Flow
Command-line parsing is linear and consumes the next token for recognized options. Unknown options print usage, print generic Hadoop command usage, and call `System.exit(-1)`. Directory generation iterates each line from `dirStructure` and calls `fc.mkdir(new Path(root + line), DEFAULT_PERM, true)`. File generation splits each line by a single space, expects exactly two tokens, multiplies the floating block count by `BLOCK_SIZE`, then writes one byte per resulting length.

## State and Persistence
The tool persists directories and files into the configured filesystem under `root`, defaulting to `/testLoadSpace`. It also reads local description files from `inDir`, defaulting to the current directory. It has no cleanup path; generated namespace remains for load tests.

## Dependencies and Integration Points
This is paired with `StructureGenerator` and feeds `LoadGenerator`, which expects files named with `StructureGenerator.FILE_NAME_PREFIX` and directories under the same root. It integrates with Hadoop `ToolRunner`, `Configuration`, `FileContext`, `Path`, and create options.

## Risks and Edge Cases
Resource handling is weak: readers are not closed explicitly. `new Path(root + line)` relies on `Path.toString()` concatenation and the structure file using leading slash-like relative names. Byte-at-a-time writing is intentionally simple but inefficient for large generated files. Unknown option handling exits the JVM, making direct unit testing awkward.

## Test Signals
There are no JUnit assertions in this source; it is itself a support utility. Correctness is signaled by successful namespace creation and by downstream `LoadGenerator` being able to discover non-empty directories and `_file_` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/DataGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/LoadGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/LoadGenerator.java

## Purpose
Implements the core NameNode/filesystem load generator used by Hadoop tests and benchmarks. It can run as a standalone `Tool` or be subclassed for MapReduce-based generation. The tool creates concurrent client threads that randomly read files, create/delete temporary files, or list directories according to configured probabilities and durations.

## Important APIs, Types, and Functions
`LoadGenerator` extends `Configured` and implements `Tool`. Static configuration/state includes `root`, `fc`, `maxDelayBetweenOps`, `numOfThreads`, `durations`, `readProbs`, `writeProbs`, `currentIndex`, `totalTime`, `startTime`, file/dir tables, `seed`, `scriptFile`, and `flagFile`. Operation metrics are indexed by `OPEN`, `LIST`, `CREATE`, `WRITE_CLOSE`, and `DELETE`. The inner `DFSClientThread` extends `SubjectInheritingThread` and implements `work`, `delay`, `nextOp`, `read`, `write`, `list`, and `genFile`. Public orchestration includes `run`, `generateLoadOnNN`, `parseArgs`, `loadScriptFile`, `printResults`, and `main`.

## Control Flow
`run` parses arguments, prints target filesystem information, calls `generateLoadOnNN`, and prints aggregate results. `generateLoadOnNN` seeds a shared `Random`, initializes `FileContext`, recursively populates directory and file tables, waits at a start-time barrier, starts `numOfThreads` workers, and then stops workers based on fixed duration, script durations, or a flag file. Script mode advances `currentIndex` after each duration line. After joining workers, it merges per-thread execution times and operation counts, then returns a negative test failure code if any thread failed.

## State and Persistence
The class uses substantial static mutable state, including worker control (`shouldRun`), probability arrays, file/dir tables, and metrics. Filesystem state is read from the generated test namespace and temporarily modified by write operations: each write creates a uniquely named file in a random directory, fills it with `a`, then deletes it. A configured flag file can externally stop the run. Static state may leak between repeated in-process invocations unless reset by callers.

## Dependencies and Integration Points
It depends on `DataGenerator.DEFAULT_ROOT` and `StructureGenerator.FILE_NAME_PREFIX`, Hadoop `FileContext`, `FileStatus`, `CreateFlag`, `CreateOpts`, `ToolRunner`, `Time`, `Preconditions`, `IOUtils`, and SLF4J. `LoadGeneratorMR` in MapReduce is explicitly cited as a subclassing integration point.

## Risks and Edge Cases
Randomness is shared across threads, which can cause contention and nondeterminism. The file write loop uses `Math.min(fileSize, WRITE_CONTENTS.length)` rather than remaining bytes, so for file sizes larger than one buffer it can overshoot the intended amount; with the small default block size this may rarely matter but is a code risk. `System.exit` in script loading on open failure is hostile to embedding. Static state and arrays mean repeated tests need careful reset. Empty namespaces or namespaces without `_file_` files are rejected.

## Test Signals
This utility has operational output rather than JUnit assertions. Useful signals are nonzero operation counts, printed average latencies, positive throughput when `totalTime` is set, and exit code `-ERR_TEST_FAILED` when any worker records an exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/LoadGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/StructureGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/StructureGenerator.java

## Purpose
Generates randomized directory and file structure description files consumed by `DataGenerator` and `LoadGenerator`. It models an in-memory tree, writes leaf directory paths to `dirStructure`, and writes generated file paths plus sizes to `fileStructure`.

## Important APIs, Types, and Functions
Main tunables are `maxDepth`, `minWidth`, `maxWidth`, `numOfFiles`, `avgFileSize`, `outDir`, and `seed`. Constants define default output directory, structure file names, and `_file_` prefix. `run` calls `init`, `genDirStructure`, `output`, `genFileStructure`, and `outputFiles`. The nested `INode` stores a directory name and child list with `output`, `outputFiles`, and `getLeaves`; nested `FileINode` overrides `outputFiles` and stores `numOfBlocks`.

## Control Flow
`init` parses numeric and path options, validates positive depth/file count/average size, non-negative minimum width, and `maxWidth >= minWidth`, then creates a `Random` from `-seed` or the current time. Recursive `genDirStructure(rootName, maxDepth)` decrements depth, chooses a child count in `[minWidth, maxWidth]`, chooses each child depth in roughly `[2*remainingDepth/3, remainingDepth]`, and adds `dir<i>` children. `genFileStructure` collects leaf directories and, for each requested file, picks a leaf and samples a Gaussian size shifted by `avgFileSize`, retrying until non-negative.

## State and Persistence
The generated tree is held in `root`. Persistent outputs are two local files under `outDir`: `dirStructure` and `fileStructure`. File size values are double block counts, not byte lengths; `DataGenerator` later multiplies by its `BLOCK_SIZE`.

## Dependencies and Integration Points
The generator uses Java `File`, `PrintStream`, `Random`, and Hadoop `ToolRunner.printGenericCommandUsage` for usage display. It is the producer for `DataGenerator` and indirectly for `LoadGenerator`, which depends on `_file_` naming.

## Risks and Edge Cases
`minWidth` is allowed to be zero, despite the error message saying positive, so the tree can become sparse. If no leaves are generated unexpectedly, file placement would fail. Output streams are manually closed and not guarded by try-with-resources. Gaussian sampling can loop if average size is extremely small and negative samples repeat, though termination is practically likely.

## Test Signals
Signals are structural: `dirStructure` should list leaf directories, `fileStructure` should list `_file_<n>` entries with non-negative block counts, and seeded runs should be reproducible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/StructureGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestAcl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestAcl.java

## Purpose
Tests basic value semantics and string formatting for Hadoop ACL domain objects: `AclEntry` and `AclStatus`.

## Important APIs, Types, and Functions
The `@BeforeAll` setup builds a matrix of `AclEntry` objects with different `AclEntryType`, `AclEntryScope`, names, and `FsAction` permissions. It also builds several `AclStatus` instances with owners, groups, sticky bit state, and entries. Tests exercise builder defaults, `equals`, `hashCode`, `getScope`, and `toString`.

## Control Flow
Setup constructs equivalent pairs (`ENTRY1`, `ENTRY2`; `STATUS1`, `STATUS2`) and distinct entries/statuses. Equality tests verify reflexivity, symmetric equality for equivalent values, inequality for different type/scope/name/permission combinations, and non-equality against null or unrelated objects. Hash tests assert equal values share hash codes and selected distinct values do not. Scope tests verify unspecified scope defaults to `ACCESS`. Formatting tests compare exact ACL entry strings and `AclStatus` strings.

## State and Persistence
All state is static in-memory test fixtures. Builders are reused in setup to ensure separate but equal objects are produced. There is no filesystem state.

## Dependencies and Integration Points
The file targets the permission package classes that are consumed by filesystem ACL APIs and FsShell ACL commands. It depends on JUnit 5 and Hadoop permission enums.

## Risks and Edge Cases
The test covers representative ACL variants, including default entries, mask entries, owner/group/other entries, and named users/groups, but does not validate parsing or ACL normalization rules. Exact `toString` assertions make display format changes intentional.

## Test Signals
Passing tests signal stable ACL equality/hash behavior, default access scope, and user-facing string output for ACL diagnostics and shell commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestFsPermission.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestFsPermission.java

## Purpose
Provides exhaustive and table-driven coverage for `FsAction` and `FsPermission`, including octal and symbolic permission conversion, sticky bit rendering, umask parsing, invalid umasks, and masking of file-type bits in integer constructors.

## Important APIs, Types, and Functions
The file imports all `FsAction` enum values and tests `implies` and `and`. It constructs `FsPermission` from shorts, ints, symbolic strings, action triples, sticky bit flags, and `Configuration` umask settings. Methods under test include `toShort`, `toOctal`, `toString`, `valueOf`, `getStickyBit`, `getOtherAction`, and `getUMask`. A large static `SYMBOLIC` table maps symbolic umask forms to octal masks.

## Control Flow
`testFsAction` verifies implication and bitwise intersection semantics. `testConvertingPermissions` iterates all short modes through `01777`, validates octal string construction, then iterates all user/group/other `FsAction` combinations with sticky bit and expects monotonically increasing short values. `testSpecialBitsToString` checks `t`/`T`/`x`/`-` rendering in the other-execute position. `testFsPermission` synthesizes all ten permission bits into `-rwxrwxrwx`-style strings and validates `valueOf`. Symbolic-constructor tests exercise `+rwx`, `+rwrt`, duplicate letters, removals, and sticky bit. Umask tests cover all action triples, symbolic mappings, bad values, and exception messages. `testIntPermission` verifies that Unix file-type bits are masked while sticky bit remains.

## State and Persistence
State is local to tests except for `Configuration` objects used to store `FsPermission.UMASK_LABEL`. There is no filesystem persistence.

## Dependencies and Integration Points
`FsPermission` is central to Hadoop filesystem metadata, shell output, ACL interaction, and file creation defaults. These tests integrate with `Configuration` to cover the public umask contract.

## Risks and Edge Cases
The suite is strong on combinatorial conversion. Exact assumptions about enum order and numeric progression are embedded in `testConvertingPermissions`; changes to enum ordering would be visible. The huge symbolic table is generated externally and acts as a compatibility oracle for Unix `umask -S`.

## Test Signals
Passing tests signal that permission math, parsing, formatting, sticky bit handling, and umask compatibility remain stable across the full permission bit space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestFsPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/protocolPB/TestFSSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/protocolPB/TestFSSerialization.java

## Purpose
Verifies serialization round trips for filesystem metadata, especially `FileStatus` boolean feature flags for ACL, encryption, and erasure coding.

## Important APIs, Types, and Functions
The file tests Hadoop writable serialization via `FileStatus.write` and `readFields` using `DataOutputBuffer` and `DataInputBuffer`, plus protobuf conversion through `PBHelper.convert(FileStatus)` and `PBHelper.convert(FileStatusProto)`. `checkFields` compares all important `FileStatus` fields.

## Control Flow
`testWritableFlagSerialization` iterates all eight combinations of `acl`, `crypt`, and `ec` flags. For each combination it builds a `FileStatus`, writes it to a data buffer, reads into a fresh `FileStatus`, checks object equality, and verifies individual fields. `testUtilitySerialization` builds a `FileStatus` with an immutable `FsPermission`, converts to `FileStatusProto`, converts back, and applies the same equality/field checks.

## State and Persistence
State is entirely in-memory buffers and protobuf objects. No filesystem calls are made; `Path` values are synthetic.

## Dependencies and Integration Points
This test targets the protocol bridge between filesystem Java objects and protobuf/writable encodings used by Hadoop RPC and persisted metadata exchange. It depends on `FSProtos.FileStatusProto`, `PBHelper`, `FileStatus`, `Path`, and `FsPermission`.

## Risks and Edge Cases
Flag loss during serialization is the primary risk. The writable test covers all flag combinations, while the protobuf test covers a representative unflagged status. It does not cover symlink fields beyond null, directory statuses, or protobuf preservation of ACL/encryption/EC flags if those are set.

## Test Signals
Passing tests indicate that core `FileStatus` fields survive writable and protobuf round trips, and that ACL/encryption/erasure-coded booleans are not dropped by writable serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/protocolPB/TestFSSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/sftp/TestSFTPFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/sftp/TestSFTPFileSystem.java

## Purpose
Integration-tests Hadoop `SFTPFileSystem` against an embedded Apache MINA SSHD SFTP server backed by the local filesystem. It validates basic file operations, metadata mapping, connection pooling, and close behavior.

## Important APIs, Types, and Functions
The test configures `SshServer`, `UserAuthPasswordFactory`, a password authenticator accepting `user/password`, `SimpleGeneratorHostKeyProvider`, and `SftpSubsystemFactory`. Hadoop APIs include `FileSystem.get`, `LocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, and `Path`. Helper `touch` creates files through either local or SFTP filesystem. Assertions inspect `((SFTPFileSystem) sftpFs).getConnectionPool().getLiveConnCount()`.

## Control Flow
`@BeforeAll` skips Windows, starts SSHD on an OS-assigned port, configures `fs.sftp.impl`, sets the SFTP port, disables FS cache, creates a clean local test directory, and stores local filesystem handles. Each test obtains a fresh `sftpFs`; `@AfterEach` closes it. Tests create/delete files, verify existence from both local and SFTP views, read bytes, compare status paths and lengths, assert failure for deleting non-empty directories and invalid renames, compare access/modify times truncated to seconds, create directories, and verify filesystem close drains the connection pool and is reentrant.

## State and Persistence
Persistent test state is a temporary local directory under `GenericTestUtils.getTestDir()`. The embedded SFTP server exposes that filesystem to SFTP operations. Tests clean up files they create and `@AfterAll` deletes the whole test directory and stops SSHD.

## Dependencies and Integration Points
This file bridges Hadoop filesystem abstraction with Apache SSHD/SFTP. It depends on platform assumptions, test directory helpers, SFTP connection pool internals, and local filesystem timestamp semantics.

## Risks and Edge Cases
The test is skipped on Windows. Timestamp assertions account for SFTP second-level precision by truncating milliseconds. Network/server startup and local host behavior can make tests more integration-sensitive than pure unit tests. Connection count expectations assume one live connection per active filesystem operation series.

## Test Signals
Passing tests signal that SFTP create/open/delete/rename/list-status metadata operations work against a real SFTP protocol endpoint and that `SFTPFileSystem.close()` reliably closes pooled connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/sftp/TestSFTPFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestAclCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestAclCommands.java

## Purpose
Tests FsShell ACL command validation and ACL specification parsing, and verifies that `ls` remains tolerant when ACL status RPCs are unavailable or unsupported.

## Important APIs, Types, and Functions
The class uses `FsShell` via `ToolRunner.run`, `AclEntry.parseAclSpec`, `AclEntry.Builder`, `AclStatus`, `FsAction`, `FsPermission`, and a nested `StubFileSystem`. The stub overrides basic `FileSystem` methods and `getAclStatus` to optionally throw a `RemoteException` wrapping `RpcNoSuchMethodException`.

## Control Flow
Setup creates a temporary path and fresh `Configuration`. Validation tests run `-getfacl` and `-setfacl` with missing paths, missing options, missing ACL specs, extra arguments, conflicting option shapes, invalid removal specs containing permissions, and empty ACL specs, expecting nonzero command results. Parsing tests compare parsed ACL entries with expected builder-created lists, both with required permissions and without permissions. The `ls` tests configure `stubfs:///` as default and confirm `FsShell -ls /` succeeds when `getAclStatus` throws "no such RPC" or when ACLs are not implemented.

## State and Persistence
Only temporary paths and in-memory stub filesystem data are used. The stub returns a root status and one listed directory entry; it does not persist changes.

## Dependencies and Integration Points
The file integrates the ACL parser, FsShell command parsing, `Ls`, and filesystem ACL APIs. It protects compatibility with older filesystems that lack ACL RPC support.

## Risks and Edge Cases
The validation cases focus on command-line shape rather than actual ACL mutation on a real filesystem. `testSetfaclValidations` includes a duplicate command for `-m path`, likely intended to cover conflicts but functionally repeats a missing spec check. The stub is minimal and may not represent all filesystem error behavior.

## Test Signals
Passing tests indicate that ACL command input validation rejects malformed invocations, ACL specs parse into ordered `AclEntry` lists, and `ls` does not fail just because ACL status cannot be fetched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestAclCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCommandFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCommandFactory.java

## Purpose
Unit-tests `CommandFactory`, the FsShell registry responsible for mapping command names and aliases to `Command` instances.

## Important APIs, Types, and Functions
The test creates `CommandFactory(conf)`, calls `registerCommands(Class<?>)`, `addClass`, `getNames`, and `getInstance`. Nested commands extend `FsCommand`. `TestRegistrar.registerCommands` registers `TestCommand1` as `tc1` and `TestCommand2` under `tc2` and `tc2.1`. `TestCommand4` declares `NAME`, `USAGE`, and `DESCRIPTION`.

## Control Flow
`testSetup` initializes an empty factory before each test. `testRegistration` confirms no initial names, then verifies registered names preserve insertion order and aliases, then adds additional command classes by explicit string and by `TestCommand4.NAME`. `testGetInstances` verifies unknown names return null, known names instantiate the expected class, command instances record the requested command name, aliases instantiate the same class with alias name, and static usage/description fields are reflected in instance metadata.

## State and Persistence
State is a static factory reference and static `Configuration`; no filesystem or external resources are used. The factory is recreated per test to avoid registry leakage.

## Dependencies and Integration Points
`CommandFactory` is an FsShell integration point used to assemble available shell commands. Reflection over registrar and command classes is central to the behavior tested here.

## Risks and Edge Cases
The test covers basic happy-path registration and lookup but does not test duplicate names, malformed registrar methods, command constructor failures, or configuration propagation beyond instance creation.

## Test Signals
Passing tests signal stable command registry ordering, alias support, unknown-command handling, reflective instantiation, and static command metadata discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCommandFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopy.java

## Purpose
Tests the low-level copy-to-target stream behavior used by FsShell `put`, especially temporary `_COPYING_` handling, cleanup on failure, overwrite behavior, and interruption paths.

## Important APIs, Types, and Functions
The test targets `CopyCommands.Put.copyStreamToTarget(FSDataInputStream, PathData)`. It uses Mockito to mock a backing `FileSystem`, `FSDataOutputStream`, `FSInputStream`, and `FileStatus`. A nested `MockFileSystem` extends `FilterFileSystem` to route `mockfs:/` operations to the mock. Helpers include `whenFsCreate` for expected temp-path create calls and `tryCopyStream` to capture exceptions.

## Control Flow
Setup configures `fs.mockfs.impl`, creates `PathData` for `mockfs:/file`, and initializes `Put`. Successful copy creates `mockfs:/file._COPYING_`, closes streams, renames temp to final, avoids final/temp existence checks on success, and does not close the filesystem. Overwrite mode first marks the target as existing, deletes it, then renames temp. Failure tests simulate interrupted create, write failure, interrupted copy bytes, and interrupted rename; all should avoid final rename and clean up the temp path where appropriate.

## State and Persistence
All filesystem state is mocked. The important logical state is the temp path `file._COPYING_`, final path, overwrite flag, and mocked status refresh on `PathData`.

## Dependencies and Integration Points
This unit protects `CopyCommands.Put` and indirectly all shell copy commands that use the same stream-to-temp-then-rename protocol. It relies on Hadoop `PathData`, `FilterFileSystem`, permissions passed to create, and Mockito verification.

## Risks and Edge Cases
S3-style behavior is explicitly protected by verifying that successful copy does not call `exists` on the temp path, avoiding polluted object-store caches. Failure cleanup is sensitive to interruption type and stream close order. The test does not copy real data beyond EOF/zero or mocked write failures.

## Test Signals
Passing tests indicate that copy operations are atomic-ish through temp rename, cleanup partial outputs on failures, preserve interruption semantics, and avoid unnecessary filesystem probes on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyFromLocal.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyFromLocal.java

## Purpose
Tests multithread option behavior for FsShell `copyFromLocal`. It verifies default single-thread execution, explicit thread count usage, invalid thread fallback, and executor completion state.

## Important APIs, Types, and Functions
The file uses `CopyCommands.CopyFromLocal`, `CommandWithDestination`, `CopyCommandWithMultiThread` internals via subclass methods, `ThreadPoolExecutor`, local `FileSystem`, `LocalFileSystem`, `Path`, `FileSystemTestHelper`, and random directory/file generation. The nested `TestMultiThreadedCopy` overrides `processArguments`.

## Control Flow
`@BeforeAll` configures a local filesystem with path-only working directory. `initialize` creates a random source tree under `fromDir`, a target `toDir`, and files filled with repeated integer/character data. Each test creates a new randomized directory. `testCopyFromLocal` runs without `-t` and expects one thread and no completed executor tasks because multithreading is unnecessary. `testCopyFromLocalWithThreads` passes `-t <availableProcessors*2+1>` and expects that many threads plus completed tasks equal generated file count. `testCopyFromLocalWithThreadWrong` passes `-t 0` and expects fallback to one thread.

## State and Persistence
The local test root persists for the test class and is deleted in `@AfterAll`. Each test creates a new subdirectory and files. Executor state is inspected after copy completion and expected to be terminated when used.

## Dependencies and Integration Points
This file integrates FsShell copy command parsing with local filesystem recursive copy behavior and the shared multithread copy base class.

## Risks and Edge Cases
Random generation can produce zero directories or zero files, so the expected completed task count may be zero even in threaded mode. Timeout guards catch deadlocks. The test checks executor state rather than byte-for-byte copied content.

## Test Signals
Passing tests signal correct `-t` parsing, invalid-thread fallback, multithread executor shutdown, and task accounting for recursive copy-from-local operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyFromLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyPreserveFlag.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyPreserveFlag.java

## Purpose
Tests the `-p` preserve flag across FsShell copy commands: `put`, `copyFromLocal`, `get`, and `cp`, including combinations with queue size and thread options.

## Important APIs, Types, and Functions
The test uses `CopyCommands.Put`, `CopyCommands.CopyFromLocal`, `CopyCommands.Get`, and `CopyCommands.Cp`. It configures `LocalFileSystem`, fixed source modification/access times, and a non-default `FsPermission`. Helpers `assertAttributesPreserved` and `assertAttributesChanged` inspect `FileStatus` permission and timestamps.

## Control Flow
Each test setup creates a local working root, source directory/file, target directory, writes sample data, sets file and directory permissions, and sets timestamps. `run` executes a command with the local configuration and expects exit code 0. Tests run commands with and without `-p`, with `-q 100`, with `-t 10`, and for directory `cp`. Special-character path coverage uses a source directory containing a space. Preserve-enabled cases assert target modification time, access time, and permissions equal the source fixtures; non-preserve cases assert they differ.

## State and Persistence
State is local filesystem metadata under a temporary root. It is deleted after each test. The preserved state includes times and permissions, which are the behavior under test.

## Dependencies and Integration Points
This is cross-command coverage for `CommandWithDestination` copy attribute propagation. It also verifies queue-size options on `Put` and `Get` remain compatible with preservation.

## Risks and Edge Cases
Local filesystem timestamp precision and default permissions can affect "changed" assertions, but fixed times are intentionally far from current time. The tests cover attributes but not ownership/group preservation. Directory preserve behavior is checked for `cp`.

## Test Signals
Passing tests signal that `-p` consistently preserves time and permission metadata while default copy paths create fresh metadata, even with thread and queue options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyPreserveFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyToLocal.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyToLocal.java

## Purpose
Tests multithread option and queue-size behavior for FsShell `copyToLocal`.

## Important APIs, Types, and Functions
The test uses `CopyCommands.CopyToLocal`, the shared `CopyCommandWithMultiThread.DEFAULT_QUEUE_SIZE`, local `FileSystem`, and `ThreadPoolExecutor`. The nested `MultiThreadedCopy` overrides `processArguments` to inspect parsed thread count, queue size, executor task count, active count, and termination.

## Control Flow
Class setup configures `LocalFileSystem`, strips URI scheme from the test root, sets it as default URI/working directory, and cleans up at class end. Per-test setup creates randomized source and target directories with optional nested files. Tests cover default copy, `-t 5`, invalid `-t 0`, `-t 5 -q 256`, invalid queue size `-q 0`, and a single-file copy with `-t 5`. Directory copies with multithreading expect completed tasks equal generated file count; single-file and non-threaded cases expect no executor.

## State and Persistence
Temporary local filesystem state is created under the class test root and deleted in `@AfterAll`. Executor lifecycle is transient and asserted after command completion.

## Dependencies and Integration Points
This integrates copy command option parsing, recursive traversal, executor creation, and local filesystem copy destination handling.

## Risks and Edge Cases
Randomized setup can produce zero files, reducing task-count signal. The test validates executor mechanics and option fallback, not full content comparison. Timeout annotations guard against stuck executor shutdown.

## Test Signals
Passing tests indicate that `copyToLocal` honors valid thread/queue settings, falls back on invalid values, avoids multithreading for single-file copies, and terminates executors after recursive work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCopyToLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCount.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCount.java

## Purpose
Unit-tests FsShell `count` option parsing, output headers, content summary formatting, quota usage formatting, storage-type quota selection, command metadata, and snapshot header support.

## Important APIs, Types, and Functions
The test targets `Count.processOptions`, `processPath`, `getCommandName`, `isDeprecated`, `getReplacementCommand`, `getName`, `getUsage`, and `getDescription`. It uses mocked `PrintStream`, mocked `FileSystem`, `PathData`, `ContentSummary`, `QuotaUsage`, and `StorageType`. Nested `MockContentSummary` and `MockQuotaUsage` override `toString` variants to expose which flags were passed.

## Control Flow
Setup registers `mockfs` and wraps Mockito `mockFs` with `MockFileSystem`. Option tests build `LinkedList<String>` arguments and assert internal flags: `-h`, `-q`, `-t`, no options, and missing path. Header tests verify exact `-v` output for no quota, quota, quota by all storage types, quota by SSD, combined `-q -t -v -h`, multiple storage types, and snapshot `-s`. Path tests configure `PathData`, run `processOptions`, call `processPath`, and verify the mocked output string reflects raw bytes vs human-readable, quota vs no quota, quota usage only, and selected storage types. Metadata tests assert exact command name, usage, and description strings.

## State and Persistence
All filesystem state is mocked. `PathData` uses `mockfs:/test`, while `MockFileSystem` returns controlled `MockContentSummary` and `MockQuotaUsage` objects. No external persistence is used.

## Dependencies and Integration Points
This test protects `Count` command behavior that users and scripts depend on, especially column headers and option interactions involving quota, storage type, erasure coding, snapshots, and human-readable output.

## Risks and Edge Cases
Exact string assertions make formatting regressions visible but also require updates for intentional CLI text changes. The test does not verify real `ContentSummary` numeric values; it verifies delegation flags and output assembly. Storage type set expectations depend on supported enum values including SSD, DISK, ARCHIVE, PROVIDED, and NVDIMM.

## Test Signals
Passing tests signal stable `count` CLI parsing and output contracts, including header text, path suffixing, quota usage delegation, storage-type filtering, and command help metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCpCommand.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCpCommand.java

## Purpose
Tests multithread and queue-size option handling for FsShell `cp`, mirroring the recursive copy behavior used by local copy commands but for filesystem-to-filesystem copies.

## Important APIs, Types, and Functions
The test uses `CopyCommands.Cp`, `CopyCommandWithMultiThread.DEFAULT_QUEUE_SIZE`, local filesystem setup, and `ThreadPoolExecutor`. Nested `MultiThreadedCp` overrides `processArguments` to assert parsed thread count, queue size, completed task count, active count, and executor termination.

## Control Flow
Class setup configures a local filesystem and working directory. Per-test setup creates randomized `fromDir` and `toDir` trees under a unique directory. Tests run default `cp`, threaded `-t 5`, invalid `-t 0`, threaded with queue `-q 256`, invalid queue `-q 0`, and a single-file copy with `-t 5`. Recursive directory copies with multithreading expect completed tasks equal generated file count; single-file/default paths expect no executor.

## State and Persistence
Temporary local filesystem state is class-scoped and deleted after all tests. Generated file content is simple repeated integer/newline data. Executor state is checked after each command completes.

## Dependencies and Integration Points
This tests the `Cp` command as a subclass of the shared multithread copy framework and ensures option parsing stays aligned with `copyToLocal`.

## Risks and Edge Cases
Random file generation can yield low or zero task counts. The test checks copy execution success and executor state, not full byte-for-byte target verification. Timeout annotations bound deadlock risk.

## Test Signals
Passing tests indicate that `cp` respects valid `-t`/`-q` settings, falls back for invalid values, avoids executor setup for simple copies, and shuts down executor work cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCpCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestFsShellConcat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestFsShellConcat.java

## Purpose
Tests FsShell `-concat`, including successful wildcard source concatenation and user-facing failure when the destination filesystem does not support concat.

## Important APIs, Types, and Functions
The test uses `FsShell`, `LocalFileSystem`, `Concat.setTestFs`, Mockito `FileSystem.concat`, `ContractTestUtils`, and `IOUtils.copyBytes`. Helper `mockConcat` simulates concat by renaming the target to a backup, recreating the target, copying backup content plus each source file into it, and deleting sources.

## Control Flow
Before each test, it creates a fresh local test root, empty destination file, and ten source files named `file-00` through `file-09` with random one-byte content. `testConcat` first reads source files to build expected content, injects a mocked filesystem whose `concat` delegates to `mockConcat`, runs `shell.run("-concat", dst, file-*)`, and verifies only the destination remains, length matches, and bytes equal expected content. `testUnsupportedFs` injects a filesystem whose `concat` throws `UnsupportedOperationException`, captures `System.err`, expects exit code 1, and checks the error mentions the destination scheme.

## State and Persistence
State is local temporary filesystem data under a test root. `Concat.setTestFs` is a test hook that changes command behavior for the test process.

## Dependencies and Integration Points
This file integrates FsShell command dispatch, glob expansion, concat command behavior, filesystem concat capability, and local file content verification.

## Risks and Edge Cases
The random source bytes make content unpredictable but expected bytes are computed before concat. The test hook must not leak mocked filesystem state across tests. The simulated concat is a local approximation rather than real HDFS concat constraints.

## Test Signals
Passing tests signal that `-concat` forwards target and expanded source paths correctly, produces expected content effects under concat, deletes sources in the simulated path, and reports unsupported filesystems with a clear error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestFsShellConcat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestLs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestLs.java

## Purpose
Comprehensively tests FsShell `ls` option parsing, listing formatting, ordering, path-only output, local default filesystem warnings, command metadata, and unsupported erasure-coding policy display behavior.

## Important APIs, Types, and Functions
The file targets `Ls.processOptions`, `processArguments`, `isDeprecated`, `getReplacementCommand`, and `getName`. It uses Mockito-backed `MockFileSystem`, `PathData`, `FileStatus`, `AclStatus`, `FsPermission`, and a nested `TestFile` fixture that synthesizes file/directory metadata, contents, path data, and expected output lines. Static configuration sets `fs.defaultFS` to `mockfs:///`.

## Control Flow
Option tests cover defaults and each flag: `-C` path-only, `-d` no directory recursion, `-h`, `-R`, `-r`, `-S`, `-t`, `-u`, `-e`, plus precedence cases where `-d` overrides recursion and `-t` overrides size ordering. Listing tests build `TestFile` instances, set directory contents through mock `listStatus`, compute expected column formats, run `processArguments`, and verify exact output order through Mockito `InOrder`. Covered listing scenarios include single file, multiple files, one directory, multiple directories, lexicographic default ordering, reverse ordering, mtime ordering, reverse mtime, independent ordering per directory, large mtime gaps, size ordering, reverse size, large size gaps, atime display/order, reverse atime order, and `-C` path-only output.

## State and Persistence
All filesystem state is mocked through `MockFileSystem` and `TestFile` status objects. `NOW` anchors generated modification/access times. `displayWarningOnLocalFileSystem` captures an in-memory error stream and runs `Ls` against `file:///.` to check warning configuration.

## Dependencies and Integration Points
`ls` is a high-visibility CLI command, and this test protects its output contract. It integrates with ACL status fetching by defaulting to empty ACL entries, FileStatus formatting, path qualification, and configuration key `HADOOP_SHELL_MISSING_DEFAULT_FS_WARNING_KEY`.

## Risks and Edge Cases
Sorting comparisons are the main risk, especially with large timestamp/length gaps where integer overflow could corrupt ordering. Exact output format assertions make CLI compatibility changes deliberate. The `-e` tests expect `UnsupportedOperationException` when EC policy display is requested but unsupported by the synthetic status/filesystem setup.

## Test Signals
Passing tests signal stable `ls` flag parsing, precedence, per-directory sorting, date/length formatting, path-only mode, local FS warning behavior, command metadata, and failure behavior for unsupported EC-policy display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestMove.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestMove.java

## Purpose
Tests selected FsShell move/rename behavior: preventing implicit overwrite when moving into an existing directory that already contains the source basename, and rejecting unsupported threading option on `moveFromLocal`.

## Important APIs, Types, and Functions
The file uses `MoveCommands.Rename`, `MoveCommands.MoveFromLocal`, `CommandFormat.UnknownOptionException`, `PathExistsException`, mocked `FileSystem` and `FileStatus`, and a nested `InstrumentedRenameCommand` that captures `displayError` exceptions instead of printing them. `MockFileSystem` extends `FilterFileSystem` to route `mockfs` operations to the mock.

## Control Flow
Setup registers `mockfs` and resets the mock before each test. `testMoveTargetExistsWithoutExplicitRename` creates source, target directory, and duplicate destination statuses for both unqualified and authority-qualified paths, configures the mock filesystem URI, enables overwrite on the command, runs `Rename`, and asserts the captured error is `PathExistsException`. `testMoveFromLocalDoesNotAllowTOption` directly invokes `MoveFromLocal.run("-t", "2", null, null)` and expects `UnknownOptionException`.

## State and Persistence
All state is in Mockito mocks and command objects. No real filesystem mutations occur.

## Dependencies and Integration Points
This protects move command semantics in `MoveCommands`, especially path qualification behavior when resolving a duplicate destination inside a target directory. It also ensures move commands do not accidentally accept copy-only multithread options.

## Risks and Edge Cases
The first test is narrow but important: overwrite mode should not silently replace an existing child when the user did not explicitly name that child. The run result is not asserted directly; the captured error type is the signal. The second test passes null positional arguments because option parsing fails before path processing.

## Test Signals
Passing tests signal that move preserves no-implicit-overwrite safety and that `moveFromLocal` rejects the `-t` option with the expected parser exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestMove.java -->
