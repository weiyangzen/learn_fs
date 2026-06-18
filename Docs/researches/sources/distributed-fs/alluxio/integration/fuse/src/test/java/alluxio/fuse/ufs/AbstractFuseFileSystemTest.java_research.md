# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/AbstractFuseFileSystemTest.java

Purpose: shared FUSE filesystem fixture for local/S3 UFS integration-style tests of `AlluxioJniFuseFileSystem`. It extends `AbstractTest` and constructs the FUSE layer on top of a `UfsBaseFileSystem`.

Important APIs and control flow: `beforeActions` creates `AlluxioJniFuseFileSystem` with `FuseOptions.create(Configuration.global(), FileSystemOptions.create(... Optional.of(mUfsOptions)), false)`, allocates a direct `FileStat`, and opens a `CloseableFuseFileInfo`. `afterActions` cleans the direct buffer and closes file-info resources. Helpers `createEmptyFile` and `createFile` use `create`, `write`, and `release` with `O_WRONLY`.

State, dependencies, integration, risks, tests: state includes native-ish FUSE structs backed by direct buffers and open file handles encoded in `FuseFileInfo`. Dependencies include libfuse-compatible structures, `BufferUtils`, JNR open flags, and inherited UFS setup. Risk centers on cleanup correctness: missing `release` or buffer cleanup can leak native resources across tests.
