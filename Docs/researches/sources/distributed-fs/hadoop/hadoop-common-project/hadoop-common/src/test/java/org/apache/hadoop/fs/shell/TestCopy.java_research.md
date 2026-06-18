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
