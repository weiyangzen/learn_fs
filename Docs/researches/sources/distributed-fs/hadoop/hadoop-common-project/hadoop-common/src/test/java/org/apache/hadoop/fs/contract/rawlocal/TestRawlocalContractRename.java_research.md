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
