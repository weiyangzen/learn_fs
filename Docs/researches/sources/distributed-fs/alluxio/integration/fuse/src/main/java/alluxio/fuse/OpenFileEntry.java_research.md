# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/OpenFileEntry.java

Purpose: legacy open-file table entry for JNR FUSE. It stores fd id, mutable path, either input or output stream, and the next write offset.

Important APIs and flow: constructor enforces valid id/path and at least one stream. `getIn`/`getOut` identify read-only versus write-only mode; `getWriteOffset`/`setWriteOffset` support duplicate-write suppression; `setPath` supports rename; `close` closes both non-null streams and resets offset.

State, dependencies, risks, and tests: state is mutable and annotated not thread-safe; JNR synchronizes on entries during read/release but not all metadata operations. Risks include stale path index in `IndexedSet` after `setPath` if the collection does not reindex mutable fields, and no enforcement that only one stream is non-null. JNR filesystem tests indirectly exercise fd lookup, write offset handling, and release/flush.
