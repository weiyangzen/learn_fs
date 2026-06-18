# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/CreateFileEntry.java

Purpose: legacy closeable container for an output stream opened during file creation. It stores fd id, mutable path, and output stream.

Important APIs and flow: constructor validates non-`-1` id, non-empty path, and non-null output stream. Getters expose id/path/out; `setPath` supports rename updating open-file metadata; `close` closes the output stream.

State, dependencies, risks, and tests: state is the mutable path and stream reference. It depends only on `OutputStream` and Guava preconditions. It is not thread-safe and appears superseded by `OpenFileEntry`/`FuseFileEntry` in current implementations. No assigned direct test covers it.
