# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/InodeProtosCheckpointFormat.java

## Purpose
`InodeProtosCheckpointFormat` reads and renders checkpoints made of delimited `InodeMeta.Inode` protobufs.

## Important APIs, Types, And Functions
`createReader` returns an `InodeProtosCheckpointReader` that validates type `INODE_PROTOS`. `read` returns an optional parsed delimited inode. `parseToHumanReadable` prints separators and each inode protobuf text.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a checkpoint type header followed by repeated delimited inode protos. Dependencies include generated `InodeMeta`, Guava `Preconditions`, and `Strings`. Risks include malformed or partially written protobufs, large text output, and type mismatches. Tests should cover empty checkpoints, multiple inode reads, human-readable output, wrong type rejection, and truncated proto handling.
