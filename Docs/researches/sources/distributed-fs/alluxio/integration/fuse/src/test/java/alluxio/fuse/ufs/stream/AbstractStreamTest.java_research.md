# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/ufs/stream/AbstractStreamTest.java

Purpose: shared stream fixture for `FuseFileStream` tests over local/S3 UFS. It extends the UFS `AbstractTest`, installs a `LaunchUserGroupAuthPolicy`, and creates a `FuseFileStream.Factory`.

Important APIs and control flow: `beforeActions` builds and initializes auth, then passes the filesystem and auth policy to the stream factory. `getTestFileUri` returns a unique path under the UFS root. `writeIncreasingByteArrayToFile` creates a file recursively with increasing bytes. `checkFile` validates `URIStatus.length`, reads the file through `FileInStream`, and compares bytes with `BufferUtils`.

State, dependencies, integration, risks, tests: state is per-test UFS content under unique URIs and the stream factory. Dependencies include Alluxio file streams, gRPC file options, `Mode`, and `BufferUtils`. This class centralizes deterministic byte-content assertions. Risk is that auth is launch-user only, so stream tests do not exercise system-user/group policy interactions.
