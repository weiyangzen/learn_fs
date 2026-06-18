# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FileStatTest.java

Purpose: validates Alluxio JNI `FileStat` struct layout against the JNR FUSE `ru.serce.jnrfuse.struct.FileStat` layout and verifies direct-buffer data consistency.

Important APIs and control flow: `offset` creates `FileStat.of(ByteBuffer.allocate(256))` and a JNR stat with `Runtime.getSystemRuntime()`, then compares offsets for device, inode, nlink, mode, uid/gid, rdev, size, block fields, and atime/mtime/ctime seconds/nanoseconds. `dataConsistency` writes `st_mode` and `st_size`, reads them through accessors and through raw `ByteBuffer` offsets.

State, dependencies, integration, risks, tests: state is native-layout memory represented by heap and direct byte buffers. Dependencies include JNR runtime and platform struct definitions. This test is a guardrail for ABI compatibility with libfuse. Risk: it assumes the current platform struct layout; cross-platform differences may need platform-specific expectations.
