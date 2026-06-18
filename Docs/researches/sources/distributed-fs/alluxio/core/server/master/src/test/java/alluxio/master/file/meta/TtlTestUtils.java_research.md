# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlTestUtils.java

## Purpose
`TtlTestUtils` provides small inode factories for TTL bucket tests.

## Important APIs, Types, and Functions
`createFileWithIdAndTtl` creates an `Inode` wrapping a `MutableInodeFile` with `FileSystemMasterCommonPOptions.ttl` set. `createDirectoryWithIdAndTtl` has the same signature for directory tests.

## Control Flow, State, and Persistence
Both helpers construct `CreateFileContext` from `CreateFilePOptions`, set the TTL in common options, and return wrapped mutable inodes. No persistent state is touched.

## Dependencies and Integration Points
The helpers depend on gRPC file-create options, `CreateFileContext`, `MutableInodeFile`, and `Inode.wrap`.

## Risks
`createDirectoryWithIdAndTtl` currently also creates a `MutableInodeFile`, not a directory inode. Existing tests only require id and TTL behavior, but the helper name can mislead future tests that depend on inode type.

## Test Signals
The file itself has no tests; its signal is fixture reuse in `TtlBucketTest` and `TtlBucketListTest`.
