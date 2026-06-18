# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSMainOperationsBaseTest.java

## Purpose
`FSMainOperationsBaseTest` is a broad abstract contract suite for `FileSystem` implementations, covering status, working directory, mkdirs, listings, globbing, read/write/delete, rename semantics, stream close idempotence, wrapped streams, and raw-local copy behavior.

## Important APIs, Types, and Functions
It extends `FileSystemTestHelper` and requires subclasses to implement `createFileSystem()`. Important hooks include `renameSupported()` and `unwrapException(IOException)`. It exercises `FileSystem.getStatus`, `setWorkingDirectory`, `mkdirs`, `getFileStatus`, `listStatus`, `globStatus`, `create`, `open`, `delete`, `rename(Path, Path, Options.Rename...)`, permissions, `FSDataInputStream`, `FSDataOutputStream`, `RawLocalFileSystem.copyToLocalFile`, and helper filters `DEFAULT_FILTER` and `TEST_X_FILTER`.

## Control Flow
`setUp()` creates the filesystem and a test root; `tearDown()` deletes it. Early tests validate status and working-directory resolution for `.`, `..`, relative, and absolute paths. Makedir tests verify parent creation and failure under existing files. Listing and glob tests create deterministic directory trees and assert null versus empty-array semantics, wildcard matches, and filter results. Write/read/delete tests cover empty through two-block files. Delete tests cover nonexistent files, nonrecursive directory failure, recursive delete, and empty directory delete. Rename tests cover missing paths, missing parents, parent-as-file, file/directory self-renames, overwrite behavior, non-empty destination constraints, and directory-to-file failures. Stream tests assert double close is harmless and wrapped input streams are exposed. The raw-local copy test verifies `copyToLocalFile(..., useRawLocalFileSystem=true)` avoids CRC sidecar creation.

## State and Persistence
The suite creates and deletes many files and directories under the subclass filesystem's test root. Static data contains deterministic byte content for read/write verification. Working directory state is mutated during tests.

## Dependencies and Integration Points
Dependencies include `FileSystem`, `Path`, `FileStatus`, `PathFilter`, `Options.Rename`, `FsPermission`, `RawLocalFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, and subclass filesystem implementations such as local, HDFS, or object stores.

## Risks and Edge Cases
This is a compatibility baseline, so backend differences around rename support, exception wrapping, permissions, glob null/empty semantics, recursive directory behavior, overwrite rules, and CRC creation are high risk. Some object stores or non-POSIX filesystems may need hook overrides.

## Test Signals
Passing subclasses signal conformance to core `FileSystem` operations: path resolution, metadata, listing/glob filtering, file IO lengths/content, deletion contracts, rename edge cases, close idempotence, wrapped stream access, and raw local copy behavior.
