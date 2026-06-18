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
