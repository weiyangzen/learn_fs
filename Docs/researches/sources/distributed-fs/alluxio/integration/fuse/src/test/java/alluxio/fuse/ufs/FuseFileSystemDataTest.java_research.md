# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/FuseFileSystemDataTest.java

Purpose: exercises data-plane behavior of `AlluxioJniFuseFileSystem` over UFS, covering create/open/write/read/release/truncate semantics and expected FUSE error codes.

Important APIs and control flow: tests use `mFileInfo.flags` with `O_WRONLY`, `O_RDONLY`, `O_RDWR`, and `O_TRUNC`; call `create`, `open`, `write`, `read`, `getattr`, `truncate`, `release`, and `unlink`; and assert codes such as `ENAMETOOLONG`, `ENOENT`, `EEXIST`, `EOPNOTSUPP`, and `ETIME`. The helper `createOpenTest` runs each scenario through open/create and optionally read-write open paths.

State, dependencies, integration, risks, tests: state includes FUSE file handles, staged incomplete writes, and file length reflected through `FileStat.st_size`. The tests signal important guarantees: no random writes, incomplete files cannot be read before release, sequential writes grow size, truncation supports zero and future extension in some contexts, and release can happen on a different thread. Risk: thread executor is not explicitly shut down; external S3 mode may behave differently for edge metadata operations.
