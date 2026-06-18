# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJniFuseFileSystemTest.java

Purpose: isolated unit tests for the primary JNI FUSE filesystem using mocked Alluxio clients and native JNI structs.

Important APIs and flow: setup configures path cache size, mount root, and mount point, loads libfuse, creates mocked `FileSystemContext`/`FileSystem`, and allocates native `FuseFileInfo`. Tests cover chmod/chown variants, create and name limits, flush, getattr stat fields and incomplete-file waiting, getattr while current FUSE is writing, mkdir, open/read/incomplete-open, rename success/errors/name limit, rmdir/write/unlink, path resolver cache, and statfs from mocked block master info.

State, dependencies, risks, and signals: tests use Mockito/PowerMock, direct buffers, environment user/group lookup, and may skip when libfuse is unavailable. They provide strong behavioral signals for path translation, errno mapping, and async-release waiting. Risks are environment-sensitive uid/gid assertions, native library availability assumptions, limited coverage of truncate/symlink/utimens/readdir/release failure paths, and some mock setups using overloads that differ from production call sites.
