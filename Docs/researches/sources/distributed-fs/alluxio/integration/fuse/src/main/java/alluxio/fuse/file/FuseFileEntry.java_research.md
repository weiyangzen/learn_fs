# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/file/FuseFileEntry.java

Purpose: thread-safe container used by JNI FUSE to bind a FUSE file handle id and mount-relative path to a `FuseFileStream`.

Important APIs and flow: constructor validates non-negative id, non-empty path, and non-null stream. Getters expose id/path/stream; `close` delegates to the stream. `AlluxioJniFuseFileSystem` stores entries in an `IndexedSet` by id and path.

State, dependencies, risks, and tests: state is immutable except the underlying stream. It depends on `FuseFileStream` and Guava preconditions. Risks include path immutability, so open entries are not updated by rename in JNI mode, and path index uniqueness may conflict with multiple opens of the same path. Tested indirectly through JNI open/read/write/release paths.
