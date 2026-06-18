# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemMetadataTest.java

Purpose: metadata-plane tests for `AlluxioJniFuseFileSystem` over local/S3 UFS. It validates directory/file lifecycle, rename behavior, statfs, duplicate directory creation, and chmod.

Important APIs and control flow: tests call `mkdir`, `getattr`, `unlink`, `rmdir`, `rename`, `statfs`, and `chmod`. They assert `ENOENT` and `ENAMETOOLONG` for missing/long paths, successful recursive-like deletion of non-empty directories, renames over existing files/directories, and root statfs success. `chmod` is guarded by `Assume.assumeTrue(mIsLocalUFS)` because S3 lacks POSIX modes.

State, dependencies, integration, risks, tests: state is UFS metadata and direct `FileStat`/`Statvfs` buffers. Dependencies include `AlluxioJniRenameUtils.NO_FLAGS`, `Mode`, and libfuse structs. Test signals show the UFS FUSE adapter tolerates idempotent directory creation and limited rename flags. Risks include broad success expectations for non-empty directory deletion and minimal assertions around rename destination contents.
