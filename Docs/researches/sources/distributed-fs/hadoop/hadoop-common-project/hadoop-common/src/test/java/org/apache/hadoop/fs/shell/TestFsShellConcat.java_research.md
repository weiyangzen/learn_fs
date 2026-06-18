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
