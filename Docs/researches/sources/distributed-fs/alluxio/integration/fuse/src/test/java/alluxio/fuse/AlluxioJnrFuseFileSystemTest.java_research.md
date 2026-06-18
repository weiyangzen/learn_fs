# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/AlluxioJnrFuseFileSystemTest.java

Purpose: isolated unit tests for the legacy JNR FUSE filesystem.

Important APIs and flow: setup creates mocked `FileSystem`, enables user/group translation, builds `AlluxioJnrFuseFileSystem`, and allocates JNR `FuseFileInfo`. Tests mirror many JNI cases: chmod/chown variants, create/name limit, flush, getattr, incomplete-file getattr/open waits, mkdir, open/read/read offsets, rename success/errors/name limit, rmdir/write duplicate suppression/unlink, path translation, and statfs via mocked block master client.

State, dependencies, risks, and signals: tests use JNR runtime memory, Mockito/PowerMock, and local user/group lookup. They document legacy differences such as incomplete-open returning `EFAULT`, 4 KiB statfs block size, and true JNR pointer read behavior. Coverage gaps include truncate unsupported path, release close failures, readdir, and write offset edge cases beyond duplicate lower-offset write.
