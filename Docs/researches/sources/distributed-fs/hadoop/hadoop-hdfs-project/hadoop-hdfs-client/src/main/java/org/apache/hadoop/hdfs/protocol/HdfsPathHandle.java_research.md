# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPathHandle.java

## Purpose
`HdfsPathHandle` is an opaque HDFS `PathHandle` implementation that can bind a path to optional inode ID and modification time constraints.

## APIs and Behavior
One constructor accepts a path plus optional inode ID and mtime. Another parses a protobuf `HdfsPathHandleProto` from a `ByteBuffer`. `verify(HdfsLocatedFileStatus)` rejects unresolved handles, content changes when `mtime` is constrained, and wrong files when `inodeId` is constrained. `bytes()` serializes the handle to a read-only protobuf byte buffer. Equality and hash code compare only path, while `toString()` emits JSON-like fields.

## State, Dependencies, and Integration
The class is immutable and serializable. It depends on protobuf-generated `HdfsPathHandleProto`, `PathHandle`, and `InvalidPathHandleException`. It integrates with APIs that reopen files using stable handles rather than only paths.

## Risks and Test Signals
Equality ignoring inode ID and mtime can conflate handles with different validation strength. Tests should cover protobuf round-trips, null byte-buffer errors, verify success/failure for changed mtime and inode, read-only byte buffers, and equality/hash behavior for constrained versus unconstrained handles on the same path.
