# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileInStream.java

Purpose: read-only implementation of `FuseFileStream` for completed Alluxio files.

Important APIs and flow: static `create` acquires a per-path read lock, waits for incomplete files to complete, fails missing/incomplete paths, opens a `FileInStream`, and records length. `read` validates buffer bounds, handles zero/EOF, seeks to the requested offset, reads into the JNI `ByteBuffer`, and returns bytes read. `write` and `truncate` throw; `flush` is no-op; `close` closes the stream and releases the lock once.

State, dependencies, risks, and tests: state includes the Alluxio input stream, immutable status length, URI, lock resource, and closed flag. It depends on Alluxio `FileSystem`, `FileInStream`, completion wait helper, and lock manager. Risks include synchronized read limiting parallelism per handle, fixed length not reflecting external updates, and error conversion through runtime exceptions. JNI/JNR tests cover read paths and incomplete-file open behavior indirectly.
