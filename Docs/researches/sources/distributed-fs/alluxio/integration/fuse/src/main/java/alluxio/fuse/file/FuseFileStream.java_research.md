# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileStream.java

Purpose: common stream contract for JNI FUSE read, write, mixed, flush, truncate, status, and close operations.

Important APIs and flow: implementers provide `read(ByteBuffer,size,offset)`, `write`, `getFileStatus`, `flush`, `truncate`, and `close`. Nested `Factory` owns one `FuseReadWriteLockManager` and selects `FuseFileInStream` for `O_RDONLY`, `FuseFileOutStream` for `O_WRONLY`, and `FuseFileInOrOutStream` for other access modes.

State, dependencies, risks, and tests: factory state is shared lock manager plus file system/auth policy. It depends on JNR open flag constants even when used by JNI FUSE. Risks include platform flag mismatch, treating every non-read/non-write access mode as mixed, and one factory-level lock manager per filesystem rather than externally visible lock lifecycle. Tested indirectly by JNI filesystem open/create/read/write/truncate tests.
