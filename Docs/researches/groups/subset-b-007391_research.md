# subset-b-007391 Research

Grouped research for Hadoop filesystem contract, FTP/SFTP/http filesystem, vectored read, flag set, leak reporter, future IO, and prefetch unit tests. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContractTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContractTestBase.java

## Purpose
`AbstractFSContractTestBase` is the common JUnit 5 base for Hadoop filesystem contract tests. It creates the concrete `AbstractFSContract`, initializes the target `FileSystem`, verifies the configured scheme matches the real filesystem URI, creates a per-contract test directory, and cleans it up after each test.

## Important APIs, Types, And Functions
Subclasses implement `createContract(Configuration)`. The base exposes `getContract()`, `getFileSystem()`, `path()`, `methodPath()`, `absolutepath()`, `skipIfUnsupported()`, `isSupported()`, `assertPathExists()`, `assertPathDoesNotExist()`, `assertIsFile()`, `assertIsDirectory()`, `mkdirs()`, `assertDeleted()`, and `rename()`. The `TestName` extension makes method names available for unique paths and thread names.

## Control Flow
`setup()` builds a fresh configuration, creates and initializes the contract, aborts disabled contract suites, obtains the test filesystem, checks `contract.getScheme()` against `fileSystem.getUri().getScheme()`, and creates the contract test root. `teardown()` deletes the test root through `ContractTestUtils.cleanup()` and invokes `contract.teardown()`. Helper assertions delegate to the filesystem and improve diagnostics with listings.

## State And Persistence
Per-test mutable state is `contract`, `fileSystem`, and `testPath`. Persistent effects are only filesystem objects created beneath the contract test path; teardown attempts recursive cleanup. Thread names are changed for log diagnostics.

## Dependencies And Integration Points
The class integrates with `AbstractFSContract`, `ContractOptions`, `ContractTestUtils`, JUnit Jupiter lifecycle/timeout APIs, `TestAbortedException`, and Hadoop `FileSystem`/`Path` primitives. All concrete contract test classes in this subset inherit this setup path.

## Risks
Scheme mismatch detection prevents accidentally running a remote or destructive contract suite against local FS. Cleanup failures can leak test directories. Contract tests that intentionally operate near root must use explicit safety options because root operations are guarded elsewhere.

## Test Signals
Good signals are a non-null filesystem, matching URI scheme, successful test-root creation, skipped disabled suites, and teardown logs with no residual paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContractTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractOptions.java

## Purpose
`ContractOptions` centralizes configuration keys used by filesystem contract tests. It defines feature flags, limits, behavioral quirks, and test tuning options so contract XML resources and test classes use stable names.

## Important APIs, Types, And Functions
This is an interface of constants, not an executable API. Important groups include creation behavior (`CREATE_OVERWRITES_DIRECTORY`, delayed visibility, file-under-file), namespace behavior (`IS_CASE_SENSITIVE`, `IS_BLOBSTORE`), rename semantics, capability flags for append, setTimes, seek, positioned reads, file references, content checks, hflush/hsync, vectored IO behavior, block locality, concat, root-test permission, max path/file sizes, and random seek count.

## Control Flow
There is no runtime control flow. `AbstractFSContract` implementations combine `FS_CONTRACT_KEY`, filesystem scheme, and these option names to load boolean or scalar capabilities from XML resources and configuration overlays.

## State And Persistence
The file has no mutable state. Its constants shape persisted test configuration in XML and runtime `Configuration` objects.

## Dependencies And Integration Points
Every contract class and many abstract contract suites depend on these keys to decide whether to run, skip, or alter expectations. Local and raw local contracts adjust some keys at runtime based on host platform.

## Risks
Renaming or changing key spelling breaks existing contract XML resources. Wrong defaults can either hide filesystem bugs by skipping tests or cause false failures where a backend deliberately lacks a feature.

## Test Signals
Signals are contract-loaded tests finding expected keys, feature-gated tests skipping only when intended, and XML resources using the same constant names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractTestUtils.java

## Purpose
`ContractTestUtils` is the shared test utility library for Hadoop filesystem contract suites. It creates deterministic datasets, writes and reads files, validates byte-for-byte results, asserts path state, handles cleanup safely, builds synthetic directory trees, verifies vectored read results, converts iterators, and records simple performance timings.

## Important APIs, Types, And Functions
Important file APIs include `writeAndRead()`, `writeDataset()`, `readDataset()`, `readDatasetSingleByteReads()`, `readNBytes()`, `verifyFileContents()`, `verifyRead()`, `compareByteArrays()`, `dataset()`, `writeTextFile()`, `createFile()`, `appendFile()`, `touch()`, `file()`, and `createAndVerifyFile()`. Path helpers include `cleanup()`, `rm()`, `rename()`, `rejectRootOperation()`, `deleteChildren()`, `listChildren()`, `assertDeleted()`, `assertRenameOutcome()`, `assertPathExists()`, `assertPathDoesNotExist()`, `assertIsFile()`, `assertIsDirectory()`, `assertMkdirs()`, and capability assertions for `StreamCapabilities` and `PathCapabilities`. Vectored helpers include `range()`, `totalReadSize()`, `validateVectoredReadResult()`, `returnBuffersToPoolPostRead()`, and `assertDatasetEquals()`. Nested `TreeScanResults` tracks files, directories, and other entries; `NanoTimer` records elapsed time and bandwidth.

## Control Flow
Most helpers perform an operation, then immediately verify observable filesystem state. Write helpers close streams in `finally`/try-with-resources and then assert length. Read helpers loop until requested bytes are obtained or throw `EOFException`. Cleanup shields callers from null filesystems and logs deletion failures. Tree creation recurses depth-first and records expected entries for later comparison. Vectored read validation waits for every range future and compares returned `ByteBuffer` contents to the original dataset at each offset.

## State And Persistence
The class itself is stateless except for constants. Files, directories, stream statistics, and temporary datasets are the persistent side effects. `TreeScanResults` stores path lists and counts; `NanoTimer` stores start/end timestamps.

## Dependencies And Integration Points
It depends on Hadoop `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileRange`, `RemoteIterator`, `IOStatistics`, `ByteBufferPool`, `FutureIO`, AssertJ, JUnit assertions, and SLF4J. Abstract contract suites call these methods for setup, validation, and diagnostics.

## Risks
Root operation guards are critical because many contract suites can target real filesystems. Several helpers assume strong consistency unless a caller explicitly uses eventual helpers. Vectored helpers must return buffers to pools after validation or tests may leak memory. `compareByteArrays()` logs only a small window around the first mismatch, so large corruption patterns may need extra diagnostics.

## Test Signals
Strong signals are exact byte comparisons, verified path existence/deletion, duplicate-free tree comparisons, expected IOStatistics keys/counters, successful vectored futures within the five-minute timeout, and cleanup logs without root-operation rejection surprises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/FTPContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/FTPContract.java

## Purpose
`FTPContract` binds the generic Hadoop contract framework to the FTP filesystem. It loads FTP-specific contract options and requires a configured test directory.

## Important APIs, Types, And Functions
The class extends `AbstractBondedFSContract`, defines `CONTRACT_XML = "contract/ftp.xml"` and `TEST_FS_TESTDIR = "test.ftp.testdir"`, returns scheme `ftp`, and implements `getTestPath()` from the configured test directory.

## Control Flow
Construction loads `contract/ftp.xml`. During base setup, `AbstractBondedFSContract` initializes from configuration, then `getTestPath()` reads `test.ftp.testdir`, asserts it is present, and returns it as a Hadoop `Path`.

## State And Persistence
There is no meaningful mutable state beyond unused private fields. Persistent state is on the configured FTP server under the test directory.

## Dependencies And Integration Points
FTP contract test classes instantiate this contract. It depends on external FTP configuration and the `FTPFileSystem` implementation selected by Hadoop configuration.

## Risks
Missing `test.ftp.testdir` fails setup. A misconfigured FTP URI or credentials can run tests against the wrong server or fail before contract behavior is exercised.

## Test Signals
Setup should load FTP contract options, resolve an `ftp` filesystem, and create/delete files below the configured FTP test directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/FTPContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractCreate.java

## Purpose
`TestFTPContractCreate` runs the generic create-file contract suite against `FTPContract`.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest` and overrides `createContract(Configuration)` to return `new FTPContract(conf)`.

## Control Flow
All test flow is inherited: the abstract suite creates files, tests overwrite behavior, parent-directory expectations, stream semantics, and error handling according to FTP contract options.

## State And Persistence
State is inherited from the base class and consists of files created under the FTP test directory. There is no local state in this subclass.

## Dependencies And Integration Points
The class integrates FTP configuration/resource loading with `AbstractContractCreateTest`.

## Risks
FTP servers may expose different overwrite or parent creation behavior than POSIX filesystems; contract XML must describe those differences accurately.

## Test Signals
Signals are inherited create-contract assertions passing or skipping based on FTP feature flags, with cleanup removing created remote files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractDelete.java

## Purpose
`TestFTPContractDelete` runs the generic delete contract suite against FTP.

## Important APIs, Types, And Functions
The only local API is `createContract(Configuration)`, returning `FTPContract`. The inherited suite supplies delete tests for files, directories, missing paths, recursive flags, and root-safety behavior.

## Control Flow
Base setup creates an FTP-backed test directory. The inherited delete tests create filesystem entries, call `FileSystem.delete()`, and assert return values plus final path state.

## State And Persistence
The class has no fields. Persistent effects are FTP objects created and removed by inherited tests.

## Dependencies And Integration Points
It connects `AbstractContractDeleteTest` to `FTPContract` and the configured FTP server.

## Risks
FTP delete semantics and server permissions can vary; false failures may indicate wrong FTP user permissions rather than Hadoop API regressions.

## Test Signals
Passing tests show delete return values and namespace effects match the FTP contract resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractMkdir.java

## Purpose
`TestFTPContractMkdir` binds the generic directory-creation contract tests to FTP.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and returns `FTPContract` from `createContract()`.

## Control Flow
Inherited tests create directories, repeated directories, nested parents, and file/directory conflict cases, with expectations controlled by FTP contract options.

## State And Persistence
No subclass state is stored. FTP directories are created under the configured test root and cleaned by the base class.

## Dependencies And Integration Points
It integrates FTP contract XML with the common mkdir suite.

## Risks
FTP servers can normalize paths or deny directory creation based on user home/root restrictions, so test setup must match the configured test directory.

## Test Signals
Signals are `mkdirs()` outcomes and subsequent `FileStatus` checks matching the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractOpen.java

## Purpose
`TestFTPContractOpen` runs common open/read contract behavior against FTP.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and returns `FTPContract`. The actual assertions are inherited.

## Control Flow
Inherited tests create files, open them through `FileSystem.open()`, read expected data, and test missing path or directory-open behavior as described by contract options.

## State And Persistence
Only inherited test files under the FTP test directory persist during a test.

## Dependencies And Integration Points
It connects FTP to the generic open suite and exercises the FTP input stream path in `FTPFileSystem`.

## Risks
Network transfer mode, server data connection policy, and user permissions can affect read behavior independently of Hadoop contract logic.

## Test Signals
Successful full-data reads and expected failures for invalid opens indicate FTP stream integration is working.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractRename.java

## Purpose
`TestFTPContractRename` runs rename contract tests against FTP while accounting for FTPFileSystem's same-directory rename limitation.

## Important APIs, Types, And Functions
It extends `AbstractContractRenameTest`, returns `FTPContract`, and overrides `testRenameDirIntoExistingDir()` plus `testRenameFileNonexistentDir()`. `verifyUnsupportedDirRenameException(IOException)` accepts failures containing `FTPFileSystem.E_SAME_DIRECTORY_ONLY`.

## Control Flow
Most rename tests are inherited. Two inherited scenarios that require cross-directory or destination-parent behavior are expected to fail for FTP; the override calls `super`, fails if it unexpectedly succeeds, and accepts only the known same-directory-only exception.

## State And Persistence
State is inherited test paths on the FTP server. The helper has no fields.

## Dependencies And Integration Points
The test depends directly on `FTPFileSystem.E_SAME_DIRECTORY_ONLY`, so it is tightly coupled to FTP rename diagnostics.

## Risks
Changing FTPFileSystem error text can break this test even if behavior is unchanged. Conversely, accepting only message text may miss distinct failures with the same substring.

## Test Signals
Passing signals include ordinary same-directory rename behavior and deliberate acceptance of unsupported cross-directory rename cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/LocalFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/LocalFSContract.java

## Purpose
`LocalFSContract` describes Hadoop's checksummed local filesystem for the contract test framework. It loads `contract/localfs.xml`, obtains a local filesystem instance, and adjusts capabilities for platform differences.

## Important APIs, Types, And Functions
Key methods are `getContractXml()`, `init()`, `adjustContractToLocalEnvironment()`, `getLocalFS()`, `getTestFileSystem()`, `getScheme()`, `getTestPath()`, and `getTestDataDir()`. `CONTRACT_XML` names the default contract resource, and `testDataDir` comes from `FileSystemTestHelper`.

## Control Flow
Construction registers the contract XML. `init()` calls `super.init()`, creates `fs` via `FileSystem.getLocal(getConf())`, then updates configuration for Windows and macOS case sensitivity/permission behavior. `getTestPath()` qualifies the test data directory against the filesystem.

## State And Persistence
The contract stores the local `FileSystem` and test data root string. Persistent state is real local files under the Hadoop test root.

## Dependencies And Integration Points
It integrates with `AbstractFSContract`, `FileSystemTestHelper`, `Shell.WINDOWS`, `ContractOptions`, and many localfs test subclasses.

## Risks
Platform adjustment is essential: NTFS and default HFS+ differ from POSIX case and permission expectations. The checked local filesystem wraps raw local IO with checksum side files, so tests must distinguish local vs raw local behavior.

## Test Signals
Signals include a `file` scheme filesystem, valid test directory qualification, and expected platform-specific contract flags in configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/LocalFSContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractAppend.java

## Purpose
`TestLocalFSContractAppend` runs the generic append contract suite against the checksummed local filesystem.

## Important APIs, Types, And Functions
It extends `AbstractContractAppendTest` and returns `LocalFSContract` from `createContract()`.

## Control Flow
Inherited tests create files, append data through `FSDataOutputStream`, verify final contents, and exercise edge cases such as appending to missing paths or open-file rename behavior as supported.

## State And Persistence
No local fields are stored. Files and local checksum side files may be created under the test root.

## Dependencies And Integration Points
The class connects `AbstractContractAppendTest` to `LocalFileSystem`.

## Risks
Checksum side files can affect raw file observations and cleanup. Platform filesystem semantics can alter append and rename behavior.

## Test Signals
Final file contents, lengths, and expected append failures are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractBulkDelete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractBulkDelete.java

## Purpose
`TestLocalFSContractBulkDelete` validates local filesystem behavior through the generic bulk-delete contract suite.

## Important APIs, Types, And Functions
The class extends `AbstractContractBulkDeleteTest` and constructs `LocalFSContract`.

## Control Flow
Inherited tests build sets of files/directories and exercise the filesystem bulk deletion contract, checking accepted inputs, missing paths, recursive behavior, and resulting namespace state.

## State And Persistence
It stores no fields. Test data persists only under the local test directory until cleanup.

## Dependencies And Integration Points
It integrates local filesystem behavior with contract-level bulk delete expectations.

## Risks
Bulk delete can be sensitive to root-operation guards and local filesystem permissions. Failures may leave many temporary paths if cleanup is interrupted.

## Test Signals
Signals are correct deleted/not-deleted path sets and clean final directory state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractBulkDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractContentSummary.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractContentSummary.java

## Purpose
`TestLocalFSContractContentSummary` applies the generic content-summary contract tests to local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractContentSummaryTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create directory/file trees, call content summary APIs, and compare counts and lengths to expected values.

## State And Persistence
There is no subclass state. File trees are created under the local test root.

## Dependencies And Integration Points
It exercises local filesystem `getContentSummary()` through the contract framework.

## Risks
Checksum side files should not be counted as user data by content summary. Platform path quirks can affect directory traversal.

## Test Signals
Expected file counts, directory counts, and byte totals should match the generated tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractContentSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractCreate.java

## Purpose
`TestLocalFSContractCreate` runs the generic create contract suite against local FS and adds a regression check for sync semantics when checksum writing is disabled.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest`, returns `LocalFSContract`, and defines `testSyncablePassthroughIfChecksumDisabled()`. That test wraps the raw filesystem in a `LocalFileSystem`, calls `setWriteChecksum(false)`, and invokes inherited `validateSyncableSemantics()`.

## Control Flow
Generic create tests are inherited. The custom test obtains the current `LocalFileSystem`, constructs a new `LocalFileSystem` around its raw FS, disables checksum output, then verifies `Syncable` semantics and immediate metadata updates.

## State And Persistence
The test creates local files under the test root. The temporary `LocalFileSystem` wrapper is closed with try-with-resources.

## Dependencies And Integration Points
It depends on `LocalFileSystem`, raw local FS passthrough, and abstract create-suite sync validation.

## Risks
Checksum-disabled local FS must not accidentally keep the same delayed/checksum behavior. On unsupported platforms, raw local metadata timing can vary.

## Test Signals
The custom signal is successful sync/hsync/hflush-style validation with immediate file status visibility after checksumming is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractDelete.java

## Purpose
`TestLocalFSContractDelete` runs generic delete contract tests against checksummed local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractDeleteTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create files and directories, delete them with recursive and non-recursive flags, and assert return values and final statuses.

## State And Persistence
The class has no fields. Local files and checksum side files are created transiently.

## Dependencies And Integration Points
It exercises `LocalFileSystem.delete()` through contract expectations.

## Risks
Deleting user data must also handle checksum side files; leftover checksum artifacts can pollute later tests.

## Test Signals
Correct delete return values and `FileNotFoundException`/absence checks after deletion are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetEnclosingRoot.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetEnclosingRoot.java

## Purpose
`TestLocalFSContractGetEnclosingRoot` verifies local filesystem behavior for resolving the enclosing filesystem root of paths.

## Important APIs, Types, And Functions
It extends `AbstractContractGetEnclosingRoot` and returns `LocalFSContract`.

## Control Flow
The inherited suite creates or resolves local paths and checks that the filesystem reports the expected enclosing root for qualified and relative paths.

## State And Persistence
No subclass state is kept; any path creation is inherited and under the test directory.

## Dependencies And Integration Points
The class connects local FS to root-resolution contract behavior.

## Risks
Windows drive roots, URI qualification, and path normalization can change expected roots.

## Test Signals
Expected root `Path` values for local paths should match platform semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetEnclosingRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetFileStatus.java

## Purpose
`TestLocalFSContractGetFileStatus` applies the generic file-status contract tests to local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractGetFileStatusTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests check `getFileStatus()` on files, directories, missing paths, and probably root-related cases, asserting type, length, and exception behavior.

## State And Persistence
No local state. Files/directories are created under the local test root.

## Dependencies And Integration Points
It tests `LocalFileSystem.getFileStatus()` through common contract assertions.

## Risks
Checksum side files and platform permission/mtime behavior must not leak into user-visible status expectations.

## Test Signals
Signals are correct `FileStatus` file/directory flags, lengths, path qualification, and missing-path exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractLoaded.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractLoaded.java

## Purpose
`TestLocalFSContractLoaded` is a focused sanity test ensuring local FS contract resources are available and populated.

## Important APIs, Types, And Functions
It extends `AbstractFSContractTestBase`, creates `LocalFSContract`, and defines `testContractWorks()` plus `testContractResourceOnClasspath()`.

## Control Flow
Base setup initializes local FS. `testContractWorks()` computes the key for `SUPPORTS_ATOMIC_RENAME`, asserts it is present, and checks `isSupported()` returns true. `testContractResourceOnClasspath()` asks the classloader for `LocalFSContract.CONTRACT_XML` and asserts a URL is found.

## State And Persistence
Only inherited contract setup state is used. No files beyond the base test directory are intentionally created.

## Dependencies And Integration Points
It depends on local contract XML packaging and `AbstractFSContract` key resolution.

## Risks
Classpath/resource packaging errors can cause broad contract suites to behave incorrectly; this test isolates that failure mode.

## Test Signals
Signals are a non-null XML resource URL and a true atomic rename capability loaded from configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractLoaded.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractMkdir.java

## Purpose
`TestLocalFSContractMkdir` runs generic directory creation tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests exercise `mkdirs()` for new, existing, nested, and conflicting paths.

## State And Persistence
No subclass fields. Created local directories persist until teardown.

## Dependencies And Integration Points
It validates local `mkdirs()` through the shared contract suite.

## Risks
Case-insensitive platforms may collapse paths that are distinct on POSIX.

## Test Signals
Correct return values and `FileStatus.isDirectory()` checks are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractOpen.java

## Purpose
`TestLocalFSContractOpen` runs common open/read contract tests against checksummed local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create local files, open them, read data, and validate errors for missing files or invalid open targets.

## State And Persistence
No subclass state. Local data and checksum files are created under the test root.

## Dependencies And Integration Points
It exercises `LocalFileSystem.open()` and checksum validation through the contract layer.

## Risks
Corrupt checksum side files can turn ordinary open/read tests into checksum failures.

## Test Signals
Read byte equality and expected failure types for invalid opens are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractRename.java

## Purpose
`TestLocalFSContractRename` runs generic rename contract tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractRenameTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests validate file and directory rename behavior, destination handling, missing source behavior, and overwrite semantics according to local contract flags.

## State And Persistence
The subclass stores no state. Test paths are local files/directories created and renamed under the test root.

## Dependencies And Integration Points
It exercises `LocalFileSystem.rename()` through contract expectations.

## Risks
Windows rename behavior differs for open files and destination directories; contract flags and local raw fallback behavior must account for this.

## Test Signals
Signals are returned boolean values, source absence, destination presence, and preserved file contents after rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSeek.java

## Purpose
`TestLocalFSContractSeek` runs common seek/positioned read contract tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests generate datasets, seek to offsets, read and compare bytes, and check EOF/negative/closed-stream behavior according to contract flags.

## State And Persistence
No subclass state. Test files and checksum files are local and temporary.

## Dependencies And Integration Points
It exercises seek support in `LocalFSFileInputStream` via Hadoop FS abstractions.

## Risks
Checksum wrappers can affect positioned reads and EOF checks; platform buffering can mask closed-stream behavior.

## Test Signals
Signals include exact byte equality after seeks and expected exceptions for invalid positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSetTimes.java

## Purpose
`TestLocalFSContractSetTimes` validates local FS timestamp mutation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractSetTimesTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create files/directories, call `setTimes()`, then read `FileStatus` to validate mtime/atime behavior and unsupported cases.

## State And Persistence
No subclass fields. Timestamp changes are applied to local temporary files.

## Dependencies And Integration Points
It exercises `LocalFileSystem.setTimes()` and platform filesystem timestamp resolution.

## Risks
Different OS/filesystem timestamp precision can cause flaky exact comparisons.

## Test Signals
Signals are observed modification/access times matching expected contract tolerance and failures for missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractSetTimes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractStreamIOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractStreamIOStatistics.java

## Purpose
`TestLocalFSContractStreamIOStatistics` validates IOStatistics exposed by local FS input and output streams.

## Important APIs, Types, And Functions
It extends `AbstractContractStreamIOStatisticsTest`, creates `LocalFSContract`, and overrides `inputStreamStatisticKeys()`, `outputStreamStatisticKeys()`, `readBufferSize()`, and `streamWritesInBlocks()`. Expected counters include read bytes, read exceptions, seek operations, skip operations/bytes, write bytes, and write exceptions.

## Control Flow
The inherited suite performs stream reads/writes/seeks/skips and checks that listed counters exist and move in the expected direction. This subclass constrains buffer size to 1024 and says writes occur in blocks.

## State And Persistence
No subclass state. IOStatistics are in stream objects and filesystem statistics while files are local temporary data.

## Dependencies And Integration Points
It depends on `StreamStatisticNames` and local FS stream instrumentation.

## Risks
Exact counter values may vary with buffering, so abstract tests must understand local block writes. Missing keys are instrumentation regressions.

## Test Signals
Signals are presence and monotonic movement of the expected IOStatistics counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractStreamIOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractVectoredRead.java

## Purpose
`TestLocalFSContractVectoredRead` runs the generic vectored-read suite against local FS and adds checksum/statistics regression coverage.

## Important APIs, Types, And Functions
It is a parameterized class over buffer type, extends `AbstractContractVectoredReadTest`, creates `LocalFSContract`, and defines `testChecksumValidationDuringVectoredRead()`, `testChecksumValidationDuringVectoredReadSmallFile()`, `tesChecksumVectoredReadBoundaries()`, and an override of `testVectoredReadMultipleRanges()`. `validateCheckReadException()` corrupts the raw file after creating a checksummed local file. `assertionsWithinTestVectoredReadMultipleRanges()` verifies stream and global bytes-read counters.

## Control Flow
The checksum tests create a file through `LocalFileSystem` so a checksum file is generated, run `readVectored()` and validate futures, then overwrite the data through raw local FS and expect `ChecksumException` during result validation. The multiple-range override records global bytes-read before the inherited test, then checks vectored operation count and byte counters.

## State And Persistence
`initialBytesRead` records global filesystem byte count. Test files and checksum side files are local temporary state.

## Dependencies And Integration Points
It depends on `FSDataInputStream.readVectored()`, `FileRange`, local checksum files, `ContractTestUtils.validateVectoredReadResult()`, IOStatistics counters, and `FileSystem.getAllStatistics()`.

## Risks
Checksum validation through vectored reads is easy to bypass if reads use raw data incorrectly. Global statistics are process-wide and may include CRC-file reads, so assertions use lower bounds rather than exact values.

## Test Signals
Signals are successful vectored reads with valid checksums, `ChecksumException` after raw corruption, one vectored operation counter increment, and bytes-read counters increasing by at least requested range lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractVectoredRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/RawlocalFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/RawlocalFSContract.java

## Purpose
`RawlocalFSContract` describes the raw local filesystem, bypassing the checksum wrapper used by `LocalFileSystem`.

## Important APIs, Types, And Functions
It extends `LocalFSContract`, sets `RAW_CONTRACT_XML = "contract/rawlocal.xml"`, overrides `getContractXml()`, overrides `getLocalFS()` to return `FileSystem.getLocal(getConf()).getRawFileSystem()`, and exposes `getTestDirectory()` as a `java.io.File`.

## Control Flow
Construction delegates to `LocalFSContract`, but contract XML resolution uses rawlocal XML. During initialization, inherited `LocalFSContract.init()` calls the overridden `getLocalFS()`, producing the raw filesystem before platform adjustment.

## State And Persistence
State is inherited `fs`/test directory. Persistent files are direct OS files with no Hadoop checksum side files.

## Dependencies And Integration Points
Raw local contract test classes use this contract to compare direct OS filesystem behavior with checked local FS behavior.

## Risks
Raw local behavior exposes platform-specific semantics directly, especially Windows open-file rename and case sensitivity. Tests must not assume checksum files exist.

## Test Signals
Signals are a `file` scheme raw filesystem and contract behavior matching `contract/rawlocal.xml`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/RawlocalFSContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractBulkDelete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractBulkDelete.java

## Purpose
`TestRawLocalContractBulkDelete` runs bulk-delete contract behavior against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractBulkDeleteTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create sets of raw local files/directories, perform bulk deletes, and assert final namespace state.

## State And Persistence
No subclass state. Raw OS files are temporary.

## Dependencies And Integration Points
It exercises raw local deletion without checksum wrappers.

## Risks
Local OS permissions, locked files, and root-safety checks can influence delete outcomes.

## Test Signals
Signals are expected deleted path sets and clean post-test directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractBulkDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractUnderlyingFileBehavior.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractUnderlyingFileBehavior.java

## Purpose
`TestRawLocalContractUnderlyingFileBehavior` records a baseline Java `File` behavior used by raw local filesystem contract expectations.

## Important APIs, Types, And Functions
It extends JUnit `Assertions`, has a static `testDirectory`, initializes it in `before()`, and defines `testDeleteEmptyPath()`.

## Control Flow
`before()` constructs `RawlocalFSContract`, resolves its test directory, creates it, and asserts it is a directory. The test creates a nonexistent child `File`, verifies it does not exist, then asserts `File.delete()` returns false.

## State And Persistence
Static state is the OS test directory. The nonexistent child is not created.

## Dependencies And Integration Points
It uses `java.io.File` directly rather than Hadoop FS APIs, grounding expectations for raw local delete of missing paths.

## Risks
The test assumes standard Java `File.delete()` behavior. Security manager or permission changes could alter setup.

## Test Signals
The signal is `delete()` returning false for a missing local path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractUnderlyingFileBehavior.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractVectoredRead.java

## Purpose
`TestRawLocalContractVectoredRead` runs the generic vectored-read contract suite against raw local FS for each configured buffer type.

## Important APIs, Types, And Functions
It is parameterized with `@ParameterizedClass`/`@MethodSource("params")`, extends `AbstractContractVectoredReadTest`, forwards the buffer type to `super`, and creates `RawlocalFSContract`.

## Control Flow
All vectored-read scenarios are inherited: range validation, data reads, buffer allocation mode, EOF behavior, and result validation run against raw local files.

## State And Persistence
No local fields beyond inherited parameterized state. Raw local test files are temporary.

## Dependencies And Integration Points
It exercises raw local `FSDataInputStream.readVectored()` without checksum wrappers.

## Risks
Direct/raw reads do not perform checksum validation, so this test complements but does not replace local FS checksum tests.

## Test Signals
Signals are correct data buffers for all ranges and buffer types, plus expected range/EOF exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawLocalContractVectoredRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractAppend.java

## Purpose
`TestRawlocalContractAppend` runs append contract tests against raw local FS and skips an unsupported Windows open-file rename case.

## Important APIs, Types, And Functions
It extends `AbstractContractAppendTest`, creates `RawlocalFSContract`, and overrides `testRenameFileBeingAppended()`. The override uses AssertJ assumptions to skip when `Path.WINDOWS` is true before calling `super`.

## Control Flow
Inherited append tests run normally. For rename-while-appending, the test aborts on Windows, where open file handles prevent the behavior, and otherwise executes the inherited scenario.

## State And Persistence
No subclass fields. Raw local files are created, appended, and possibly renamed during tests.

## Dependencies And Integration Points
It depends on raw local filesystem semantics and `Path.WINDOWS` platform detection.

## Risks
Skipping only Windows avoids false negatives, but other filesystems mounted locally could also have restrictive open-file rename behavior.

## Test Signals
Signals include byte-for-byte append validation and platform-appropriate handling of open-file rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractCreate.java

## Purpose
`TestRawlocalContractCreate` runs generic create contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create files, validate overwrite and parent behavior, and check stream semantics without checksum wrapping.

## State And Persistence
No subclass state. Raw OS files are created under the test root.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.create()` through the contract framework.

## Risks
Raw local create behavior varies with OS permissions and path normalization.

## Test Signals
Signals are successful data writes, expected overwrite outcomes, and correct file lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractDelete.java

## Purpose
`TestRawlocalContractDelete` runs generic delete contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractDeleteTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call raw local `delete()` on files/directories/missing paths and assert behavior according to rawlocal contract XML.

## State And Persistence
No subclass state. Temporary OS files/directories are created and removed.

## Dependencies And Integration Points
It exercises raw local deletion without checksum side-file cleanup considerations.

## Risks
Open files and permissions can produce platform-specific delete failures.

## Test Signals
Signals are expected delete return values and absence of deleted paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetEnclosingRoot.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetEnclosingRoot.java

## Purpose
`TestRawlocalContractGetEnclosingRoot` verifies root resolution for raw local paths.

## Important APIs, Types, And Functions
It extends `AbstractContractGetEnclosingRoot` and creates `RawlocalFSContract`.

## Control Flow
Inherited root-resolution cases run against raw local FS.

## State And Persistence
The subclass stores no state. Any test paths are temporary local paths.

## Dependencies And Integration Points
It connects raw local filesystem to generic root-resolution contract behavior.

## Risks
Windows drive letters and URI/path qualification can produce platform-specific root values.

## Test Signals
Signals are expected enclosing root paths for qualified raw local paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetEnclosingRoot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetFileStatus.java

## Purpose
`TestRawlocalContractGetFileStatus` runs generic status tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractGetFileStatusTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create paths and validate `getFileStatus()` type, length, path qualification, and missing-path behavior.

## State And Persistence
No subclass fields. Raw OS files/directories are temporary.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.getFileStatus()`.

## Risks
Symlinks, permissions, and platform path casing can alter visible status.

## Test Signals
Signals include correct file/directory flags and expected exceptions for missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractMkdir.java

## Purpose
`TestRawlocalContractMkdir` validates raw local directory creation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call `mkdirs()` for common success and conflict cases.

## State And Persistence
No subclass state. Temporary raw local directories are created and cleaned.

## Dependencies And Integration Points
It exercises raw local `mkdirs()` behavior.

## Risks
Case-insensitive local filesystems and permissions can affect expected outcomes.

## Test Signals
Signals are correct `mkdirs()` return values and directory statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractOpen.java

## Purpose
`TestRawlocalContractOpen` runs generic open/read tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create files, open streams, read and compare contents, and validate invalid open behavior.

## State And Persistence
No subclass fields. Raw local files are temporary.

## Dependencies And Integration Points
It exercises raw local input stream behavior without checksum validation.

## Risks
Direct OS reads may behave differently around locked or deleted files on Windows.

## Test Signals
Signals are byte equality and expected missing-path/directory-open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractPathHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractPathHandle.java

## Purpose
`TestRawlocalContractPathHandle` runs durable path-handle contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractPathHandleTest`, has a default constructor, and creates `RawlocalFSContract`.

## Control Flow
Inherited tests obtain path handles, mutate or rename files as required by the abstract suite, and check reference/content constraints.

## State And Persistence
No subclass state. Raw local files are created and mutated by inherited tests.

## Dependencies And Integration Points
It exercises path-handle support advertised by the rawlocal contract.

## Risks
Path-handle durability depends on file identity semantics of the host filesystem.

## Test Signals
Signals are path handles resolving correctly or rejecting changed content according to contract flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractPathHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractRename.java

## Purpose
`TestRawlocalContractRename` runs raw local rename contract tests and directly exercises the Windows fallback helper for empty destination directories.

## Important APIs, Types, And Functions
It extends `AbstractContractRenameTest`, creates `RawlocalFSContract`, and defines `testRenameWithNonEmptySubDirPOSIX()`. The custom test calls `RawLocalFileSystem.handleEmptyDstDirectoryOnWindows(src, srcFile, dst, dstFile)`.

## Control Flow
The custom test builds a source directory with a file and nested subdirectory, creates an empty destination directory, calls the fallback helper directly, then asserts POSIX-style final layout: source contents moved into destination and source file removed.

## State And Persistence
Temporary raw local directories/files are created under the test path. No fields are stored.

## Dependencies And Integration Points
It depends on `RawLocalFileSystem.pathToFile()` and the fallback rename implementation added for HADOOP-9805.

## Risks
The test invokes a Windows-specific fallback even on non-Windows platforms to avoid coverage gaps. It assumes POSIX behavior after fallback and may be sensitive to local filesystem permissions.

## Test Signals
Signals are moved files appearing under destination, nested subdir preservation, and source path absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSeek.java

## Purpose
`TestRawlocalContractSeek` runs common seek tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create datasets, perform seek/read/positioned-read operations, and check EOF/negative/closed-stream behavior.

## State And Persistence
No subclass state. Raw local files are temporary.

## Dependencies And Integration Points
It exercises raw local input stream seeking.

## Risks
Platform stream behavior after close or EOF can differ from remote filesystems but should match rawlocal contract flags.

## Test Signals
Signals are exact byte comparisons after seeks and expected exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSetTimes.java

## Purpose
`TestRawlocalContractSetTimes` validates raw local timestamp mutation through the generic contract suite.

## Important APIs, Types, And Functions
It extends `AbstractContractSetTimesTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests call `setTimes()` on raw local files/directories and assert observed status timestamps.

## State And Persistence
No subclass state. Temporary OS file timestamps are changed.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.setTimes()`.

## Risks
Filesystem timestamp precision and access-time mount options can affect assertions.

## Test Signals
Signals are expected mtime/atime values or documented unsupported behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSetTimes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/SFTPContract.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/SFTPContract.java

## Purpose
`SFTPContract` provides an embedded SFTP server-backed filesystem contract for tests, avoiding dependence on an external SFTP service.

## Important APIs, Types, And Functions
It extends `AbstractFSContract`, loads `contract/sftp.xml`, uses `TEST_URI = sftp://user:password@localhost`, and implements `init()`, `teardown()`, `getTestFileSystem()`, `getScheme()`, and `getTestPath()`.

## Control Flow
`init()` creates an Apache SSHD `SshServer`, binds port 0, configures generated host keys, password auth for `user/password`, installs an SFTP subsystem, starts the server, then writes SFTP FS implementation, port, and cache-disable settings into the configuration. `getTestFileSystem()` resolves the test URI through that configuration. `teardown()` stops the server.

## State And Persistence
The contract stores `conf`, `testDataDir`, and the live `SshServer`. Files are persisted under the server's backing local directory through SFTP during a test.

## Dependencies And Integration Points
It integrates `SFTPFileSystem` with Apache SSHD server/auth/subsystem classes and contract tests such as seek.

## Risks
Server lifecycle must be balanced or tests leak ports/threads. Using a fixed localhost URI with a configured port relies on `fs.sftp.host.port` and disabled cache to avoid stale connections.

## Test Signals
Signals are successful SSHD startup on an ephemeral port, authenticated SFTP FS resolution, and clean server stop in teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/SFTPContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/TestSFTPContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/TestSFTPContractSeek.java

## Purpose
`TestSFTPContractSeek` runs common seek tests against the embedded SFTP contract.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `SFTPContract`.

## Control Flow
Inherited tests run after `SFTPContract` starts an embedded server. They create test files over SFTP, seek/read ranges, and verify contract-defined EOF and invalid-position behavior.

## State And Persistence
No subclass fields. Remote-visible files are backed by the embedded server and cleaned after tests.

## Dependencies And Integration Points
It exercises `SFTPFileSystem` seek support through Apache SSHD.

## Risks
Network-style streams may not support all seek behavior efficiently; server startup/caching misconfiguration can make failures look like seek issues.

## Test Signals
Signals are exact data after seeks and clean embedded server lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/TestSFTPContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/FtpTestServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/FtpTestServer.java

## Purpose
`FtpTestServer` is a small embedded Apache FTPServer wrapper used by FTP filesystem tests.

## Important APIs, Types, And Functions
Constructor accepts a root `Path`, creates a `UserManager`, builds an `FtpServer`, and stores fields. Public methods are `start()`, `getFtpRoot()`, `getPort()`, `stop()`, and `addUser(String, String, Authority...)`. `createServerFactory()` configures a default listener on port 0.

## Control Flow
Construction creates the server but does not start it. `start()` starts the server, extracts the assigned listener port from `DefaultFtpServer`, and returns `this`. `addUser()` creates a per-user home directory under the FTP root, sets credentials/authorities, saves it in the manager, and returns the `BaseUser`. `stop()` is idempotent around `server.isStopped()`.

## State And Persistence
State includes selected port, FTP root path, user manager, and server. Persistent effects are per-user home directories and files created through FTP tests.

## Dependencies And Integration Points
It depends on Apache FTPServer factories, listeners, user manager, `BaseUser`, and ftplet authorities. `TestFTPFileSystem` uses it for isolated tests.

## Risks
User home creation can fail if the root is missing or permissions are wrong. Server lifecycle leaks can leave bound ports or temp directories.

## Test Signals
Signals are successful port assignment, user creation with correct authorities, and server stop during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/FtpTestServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/TestFTPFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/TestFTPFileSystem.java

## Purpose
`TestFTPFileSystem` directly tests core `FTPFileSystem` behavior outside the generic contract suites.

## Important APIs, Types, And Functions
Lifecycle methods `setUp()` and `tearDown()` create and remove a temp FTP root and embedded `FtpTestServer`. Tests cover create with and without write permissions, default port, transfer mode parsing, data connection mode parsing, permission-to-`FsAction` conversion, timeout configuration, and fully qualified path rename. Helpers include `getFTPFileOf()`, `enhancedAssertEquals()`, and `touch()`.

## Control Flow
Each test starts a fresh FTP server. Permission tests create users with or without `WritePermission`, configure `fs.defaultFS`, host, port, credentials, and disabled cache, then attempt writes/reads or expect an `IOException`. Mode tests configure strings and inspect `FTPClient` constants. The rename test creates qualified root-relative paths and verifies `fs.rename()` succeeds.

## State And Persistence
State is `server` and `testDir` per test. Temporary FTP home directories and files are recursively deleted in teardown.

## Dependencies And Integration Points
It depends on Commons Net FTP constants/client, Apache FTPServer users/permissions, Hadoop `FTPFileSystem`, `FileSystem`, `Path`, `FsAction`, and `LambdaTestUtils`.

## Risks
Tests are sensitive to FTP server permission semantics and cache disabling. String-based transfer/data-mode parsing defaults invalid values silently, so regressions could be missed if invalid inputs still map to defaults.

## Test Signals
Signals include round-trip written bytes, expected write-denied error text, default port equal to Commons Net FTP default, parsed mode constants, exact permission mapping, configured keepalive timeout, and successful qualified-path rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/TestFTPFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/http/TestHttpFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/http/TestHttpFileSystem.java

## Purpose
`TestHttpFileSystem` verifies basic HTTP filesystem open and status path resolution behavior.

## Important APIs, Types, And Functions
`setUp()` registers `HttpFileSystem` as `fs.http.impl`. `testHttpFileSystem()` uses `MockWebServer` to serve data and tests absolute URL, absolute path, and relative path opens. `testHttpFileStatus()` checks `getFileStatus()` path URI resolution. `assertSameData()` reads expected bytes.

## Control Flow
The open test enqueues three identical responses, starts the mock server, gets a Hadoop `FileSystem` for the server URI, opens `/foo` through three path forms, and checks the first recorded request path. The status test creates an HTTP filesystem for `http://www.example.com` and verifies all path forms resolve to `/foo`.

## State And Persistence
State is a per-test `Configuration`. Mock server state is in-memory and closed by try-with-resources.

## Dependencies And Integration Points
It depends on MockWebServer, Hadoop `HttpFileSystem`, `FileSystem`, `Path`, `IOUtils`, and URI/URL conversion.

## Risks
HTTP FS is read-only/simple; tests do not validate headers, errors, range requests, or redirects. Mock response reuse must be sufficient for all opens.

## Test Signals
Signals are exact body bytes for all path forms and `FileStatus` paths resolving to the expected HTTP URI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/http/TestHttpFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFlagSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFlagSet.java

## Purpose
`TestFlagSet` validates `FlagSet`, a typed enum-backed feature/capability set used to parse configuration and expose path capability names.

## Important APIs, Types, And Functions
The test uses `FlagSet.createFlagSet()`, `FlagSet.buildFlagSet()`, `enable()`, `disable()`, `set()`, `makeImmutable()`, `copy()`, `flags()`, `enabled()`, `hasCapability()`, `pathCapabilities()`, `toString()`, and `toConfigurationString()`. Test enums are `SimpleEnum` and `OtherEnum`; capability names are `key.a`, `key.b`, and `key.c`.

## Control Flow
Tests mutate a base flag set, verify enable/disable and setter behavior, freeze it and expect setters to throw, parse comma/whitespace config entries, ignore or reject unknown values based on the flag, handle duplicates, expand `*`, serialize/parse round trips, and validate equality/hash/copy semantics. Null enum class or prefix creation is expected to throw.

## State And Persistence
`flagSet` is a mutable test field reset by new test instances. Configuration state is in transient `Configuration(false)` objects.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, AssertJ, `LambdaTestUtils.intercept`, and `AbstractHadoopTestBase`. Production users of `FlagSet` rely on these guarantees for capability reporting.

## Risks
Order-sensitive assertions on `flags()` and string output require stable enum ordering. Mutability rules are security-relevant because immutable sets must not be altered after publication.

## Test Signals
Signals include exact enabled flag sets, exact capability lists, expected parse failures, immutable mutation exceptions, and equality/hash behavior across mutable and immutable instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFlagSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java

## Purpose
`TestFutureIO` documents and validates which thread executes synchronous future-evaluation helpers compared with `CompletableFuture.supplyAsync()`.

## Important APIs, Types, And Functions
It uses a `ThreadLocal<AtomicInteger>` field, `setup()`, `testEvalInCurrentThread()`, `testEvalAsync()`, `getLocal()`, and `getLocalValue()`. The production API under test is `LambdaUtils.eval()`.

## Control Flow
`setup()` initializes the thread-local counter to 1. `testEvalInCurrentThread()` calls `LambdaUtils.eval()` with a completed future and a lambda that increments the thread-local; both local and returned values become 3, proving same-thread execution. `testEvalAsync()` uses `CompletableFuture.supplyAsync()`, leaving the caller thread local at 1 while the async task returns 3.

## State And Persistence
State is only per-test thread-local data. There is no persistent filesystem state.

## Dependencies And Integration Points
It depends on Java `CompletableFuture`, `AtomicInteger`, Hadoop `LambdaUtils`, and `HadoopTestBase`.

## Risks
Thread-affinity behavior matters for callers relying on thread-local context. If `LambdaUtils.eval()` becomes asynchronous, this test should fail.

## Test Signals
The signal is the contrast between caller-thread local value after `eval()` and after `supplyAsync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestLeakReporter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestLeakReporter.java

## Purpose
`TestLeakReporter` validates `LeakReporter`, which logs leaked resources and invokes a close action exactly once when a probe says a resource is still open.

## Important APIs, Types, And Functions
Tests instantiate `LeakReporter(message, probe, closeAction)`, call `close()`, inspect `isClosed()`, and use `THREAD_FORMAT`. Helpers include `expectClose()`, `closed()`, `raiseNPE()`, and `assertCloseCount()`.

## Control Flow
`testLeakInvocation()` changes the current thread name, captures root logs, closes a reporter whose probe returns true, verifies close count and logged warning/info content including old thread info and stack trace, then closes again to verify idempotence. Other tests verify no action when probe returns false, swallowed probe failure, and swallowed close-action failure while still marking closed.

## State And Persistence
State is `closeCount` and captured logs. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on SLF4J, `GenericTestUtils.LogCapturer`, AssertJ, and `AbstractHadoopTestBase`. LeakReporter is likely used by stream/resource wrappers.

## Risks
Log-content assertions can be brittle across logging format changes. Swallowing probe/close exceptions prevents cleanup failures from cascading but can hide real cleanup bugs.

## Test Signals
Signals are one close callback on first leak close, no reentrant callback, expected log fragments, no callback when not leaked, and closed state after close-action exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestLeakReporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestVectoredReadUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestVectoredReadUtils.java

## Purpose
`TestVectoredReadUtils` validates the low-level helper logic behind Hadoop vectored reads: buffer slicing, range sorting/validation, range merging, positioned reads into heap/direct buffers, future completion, EOF validation, and vector buffer pool adaptation.

## Important APIs, Types, And Functions
Production APIs under test include `VectoredReadUtils.sliceTo()`, `roundDown()`, `roundUp()`, `sortRangeList()`, `sortRanges()`, `validateAndSortRanges()`, `isOrderedDisjoint()`, `mergeSortedRanges()`, `readRangeFrom()`, and `readVectored()`, plus `CombinedFileRange` and `VectorIOBufferPool`. The local `Stream` interface combines `PositionedReadable` and `ByteBufferPositionedReadable`.

## Control Flow
Early tests validate slicing without copies when offsets match and shared backing arrays when slicing subranges. Sorting/merging tests construct overlapping, duplicate, consecutive, gapped, and aligned ranges, then assert merged `CombinedFileRange` start/length/underlying references. Read tests use Mockito streams to fill buffers or throw IOEs and then assert futures complete successfully or exceptionally. EOF tests validate negative offsets, negative lengths, reads at/over EOF, whole-file reads, and zero-length vectored reads. Buffer-pool tests adapt an `ElasticByteBufferPool` to vector IO get/put lambdas and confirm release behavior.

## State And Persistence
All state is in memory: `ByteBuffer`s, `FileRange` futures, mocked streams, and buffer pools. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on Hadoop vectored read abstractions, Mockito, AssertJ, Java futures, `ByteBufferPool`, and test future assertions. Filesystem stream implementations rely on this utility for correctness and efficient coalescing.

## Risks
Range merging must not merge overlapping or duplicate user ranges incorrectly, because returned buffers must map back to original references and offsets. Direct vs heap allocation must both work. EOF validation must match contract tests or backends will disagree on exception timing.

## Test Signals
Signals include exact merged ranges, preserved underlying references, expected exceptions for invalid ranges, completed/failed futures on success/IOE, buffers filled with deterministic bytes, zero-length range buffers with limit 0, and buffer-pool size changes after put/get/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestVectoredReadUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/ExceptionAsserts.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/ExceptionAsserts.java

## Purpose
`ExceptionAsserts` is a tiny prefetch-test helper that wraps Hadoop's `LambdaTestUtils.intercept()` for exception assertions.

## Important APIs, Types, And Functions
It is a final utility class with a private constructor and two overloaded `assertThrows()` methods: one checks exception type plus partial message, the other checks only type.

## Control Flow
Both methods delegate directly to `intercept()`. There is no additional branching beyond overload selection.

## State And Persistence
The class has no state and no side effects except throwing assertion failures through the underlying test utility.

## Dependencies And Integration Points
Prefetch unit tests use this helper for concise argument/state validation. It depends on `LambdaTestUtils.VoidCallable`.

## Risks
The comment references older JUnit migration concerns while the file is now in JUnit 5 era; behavior still depends on Hadoop's intercept implementation rather than JUnit assertions.

## Test Signals
Signals are precise exception class and message substring matching in prefetch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/ExceptionAsserts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/SampleDataForTests.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/SampleDataForTests.java

## Purpose
`SampleDataForTests` centralizes common null, empty, and non-empty sample arrays/lists for prefetch tests.

## Important APIs, Types, And Functions
It is a final utility class with a private constructor and public constants for object, byte, short, int, long arrays, plus lists: `NULL_*`, `EMPTY_*`, `NON_EMPTY_*`, `EMPTY_LIST`, and `VALID_LIST`.

## Control Flow
There is no runtime flow; constants are initialized at class load.

## State And Persistence
State is static final in-memory sample data. The empty/valid lists are mutable list instances from `ArrayList`/`Arrays.asList`, so tests should not mutate them unexpectedly.

## Dependencies And Integration Points
It imports Java collections only and is intended for use by prefetch validation tests.

## Risks
Shared mutable constants can cause cross-test pollution if modified. Primitive array constants with length 1 do not encode meaningful contents, only presence.

## Test Signals
Signals are clearer argument-check tests using standardized null/empty/non-empty inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/SampleDataForTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockCache.java

## Purpose
`TestBlockCache` validates the prefetch block cache implementation, especially argument checks and put/get data preservation.

## Important APIs, Types, And Functions
It tests the `BlockCache` interface via `SingleFilePerBlockCache`, using `put()`, `get()`, `size()`, and `containsBlock()`. `assertBuffersEqual()` compares buffer limits and contents.

## Control Flow
`testArgChecks()` constructs a cache, then expects null buffer put and null statistics construction to fail. `testPutAndGet()` fills a 16-byte buffer, stores block 0, verifies size/contains, reads into a different buffer and compares bytes, then repeats for block 1.

## State And Persistence
The cache may persist block data through local temp files selected by `LocalDirAllocator(HADOOP_TMP_DIR)`. Test buffers are in memory.

## Dependencies And Integration Points
It depends on prefetch cache classes, `EmptyPrefetchingStatistics`, Hadoop `Configuration`, `LocalDirAllocator`, and JUnit assertions.

## Risks
Tests verify only simple capacity-two storage, not eviction, cleanup of cache files, or concurrent access. Buffer position/limit handling is important for correctness.

## Test Signals
Signals are cache size changes, `containsBlock()` results, distinct output buffer identity, and exact byte equality after retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockData.java

## Purpose
`TestBlockData` validates block metadata calculations and per-block state transitions for prefetching.

## Important APIs, Types, And Functions
It constructs `BlockData(fileSize, blockSize)` and tests `getFileSize()`, `getBlockSize()`, `getNumBlocks()`, `isLastBlock()`, `isValidOffset()`, `getSize()`, `getBlockNumber()`, `getStartOffset()`, `getRelativeOffset()`, `getState()`, `setState()`, and `getStateString()`.

## Control Flow
`testArgChecks()` checks valid constructors and invalid negative/zero arguments or out-of-range block numbers. `testComputedFields()` runs helper cases for zero and nonzero file sizes. The helper verifies zero-file methods reject invalid ranges, computes expected block counts and last block size, iterates offsets to validate mapping to blocks/relative offsets, and exercises state transitions through `NOT_READY`, `QUEUED`, `READY`, and `CACHED`.

## State And Persistence
State is in-memory block metadata and state array inside `BlockData`. No persistence occurs.

## Dependencies And Integration Points
It depends on `ExceptionAsserts`, Hadoop test intercepts, and `BlockData.State`. Prefetch scheduling/cache code relies on these calculations.

## Risks
Off-by-one errors at EOF or last block size can corrupt prefetch reads. Zero-length files have intentionally empty valid ranges that must be handled carefully.

## Test Signals
Signals are exact block counts, start/relative offsets, last-block detection, and accepted/rejected state access for edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockOperations.java

## Purpose
`TestBlockOperations` validates operation tracing for prefetch block operations.

## Important APIs, Types, And Functions
It tests `BlockOperations` methods `getPrefetched()`, `getCached()`, `getRead()`, `release()`, `requestPrefetch()`, `prefetch()`, `requestCaching()`, `addToCache()`, `cancelPrefetches()`, `close()`, `end()`, and `getSummary(false)`.

## Control Flow
`testArgChecks()` ensures negative block numbers are rejected for block-numbered operations. `testGetSummary()` uses reflection to invoke each operation method, ends the returned `Operation`, and checks the summary begins with the expected short code followed by its end marker.

## State And Persistence
State is an in-memory operation log inside `BlockOperations`. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on Java reflection, `BlockOperations.Operation`, and Hadoop test intercepts. The production class likely feeds debug summaries for prefetch state machines.

## Risks
Reflection means method renames break tests at runtime. Summary format is part of diagnostic behavior; changing short codes requires coordinated test updates.

## Test Signals
Signals are negative-argument exceptions and summary prefixes such as `GP(42);EGP(42);` or `CP;ECP;`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBoundedResourcePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBoundedResourcePool.java

## Purpose
`TestBoundedResourcePool` validates the generic bounded resource pool used by prefetch buffers/resources.

## Important APIs, Types, And Functions
The nested `BufferPool` extends `BoundedResourcePool<ByteBuffer>` and implements `createNew()` with `ByteBuffer.allocate(10)`. Tests use `acquire()`, `release()`, `numCreated()`, and `numAvailable()`.

## Control Flow
Argument tests check invalid pool sizes, null release, and releasing an item not owned by the pool. Single acquire/release verifies a released buffer is reused without creating another. Multiple acquire/release obtains the full pool, tracks identity uniqueness, releases each buffer idempotently, and reacquires the same identities.

## State And Persistence
State is in-memory pool ownership, available count, and created count. No persistence.

## Dependencies And Integration Points
It depends on `BoundedResourcePool`, `ByteBuffer`, identity sets, and JUnit assertions.

## Risks
Ownership tracking must distinguish equal resources by identity. Double release should be harmless but releasing foreign resources must fail.

## Test Signals
Signals are created/available counters, identity reuse, rejection of foreign/null items, and no counter inflation on repeated release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBoundedResourcePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferData.java

## Purpose
`TestBufferData` validates lifecycle, state transitions, action futures, read-only protection, and checksum integrity for prefetch buffer blocks.

## Important APIs, Types, And Functions
It constructs `BufferData(blockNumber, ByteBuffer)` and tests `getState()`, `setPrefetch()`, `setCaching()`, `getActionFuture()`, `updateState()`, `setReady()`, `getChecksum()`, `getBuffer()`, `setDone()`, `throwIfStateIncorrect()`, and static `getChecksum()`. The nested `StateChanger` functional interface drives invalid transition checks.

## Control Flow
Argument tests reject negative block numbers, null buffers/futures/states, and state mismatches. Valid state tests move from `BLANK` to `PREFETCHING`, `CACHING`, and `READY`, checking future replacement. Invalid tests attempt `setPrefetch()` or `setCaching()` from all disallowed states. `testSetReady()` records checksum, makes the buffer read-only, rejects repeated ready, mutates the backing array, and expects `setDone()` to detect checksum drift. `testChecksum()` verifies checksum ignores unused buffer capacity beyond limit.

## State And Persistence
State is in-memory buffer data, state enum, future reference, and checksum. No persistence.

## Dependencies And Integration Points
It depends on `CompletableFuture`, `ByteBuffer`, `ReadOnlyBufferException`, `ExceptionAsserts`, and the prefetch state machine.

## Risks
The backing array can still be mutated after a read-only view is exposed; checksum verification catches this late corruption. Incorrect state transitions can race prefetch/caching logic.

## Test Signals
Signals are exact state values, future identity changes, read-only buffer exceptions, checksum nonzero/stability, and expected illegal-state messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferPool.java

## Purpose
`TestBufferPool` validates the prefetch-specific pool of `BufferData` objects.

## Important APIs, Types, And Functions
It constructs `BufferPool(size, bufferSize, PrefetchingStatistics)` and tests `acquire(blockNumber)`, `tryAcquire(blockNumber)`, `release(BufferData)`, `getAll()`, `numCreated()`, and `numAvailable()`. Helper `acquire()` asserts same block acquisition returns the same `BufferData`.

## Control Flow
Argument tests reject invalid pool/buffer sizes, null statistics, negative block numbers, and null release. `testGetAndRelease()` verifies initial empty iteration, acquires two buffers, sees `tryAcquire()` return null when full, iterates two active entries, releases only after setting state to `READY`, and observes availability restored. `testRelease()` verifies release is rejected from `BLANK`, `PREFETCHING`, and `CACHING`, but accepted from `READY`.

## State And Persistence
State is in-memory buffer ownership, block-number mapping, active buffer collection, and pool counters. No persistence.

## Dependencies And Integration Points
It depends on `BufferPool`, `BufferData.State`, `PrefetchingStatistics`, and `EmptyPrefetchingStatistics`. Prefetch readers rely on this pool to avoid over-allocation.

## Risks
Releasing buffers before they are ready can expose partially filled data. Same-block acquisition identity must be stable while a block is active.

## Test Signals
Signals are active iteration counts, null `tryAcquire()` at capacity, same-object acquire for the same block, counter changes after release, and release rejection for unsafe states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferPool.java -->
