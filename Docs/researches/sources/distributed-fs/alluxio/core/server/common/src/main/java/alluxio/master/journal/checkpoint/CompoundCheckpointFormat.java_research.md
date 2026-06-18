# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CompoundCheckpointFormat.java

## Purpose
`CompoundCheckpointFormat` stores multiple named component checkpoints inside one checkpoint stream using Kryo chunked encoding.

## Important APIs, Types, And Functions
`createReader` returns `CompoundCheckpointReader`. `parseToHumanReadable` iterates entries and delegates each nested stream to its own `CheckpointFormat`. The reader uses `PatchedInputChunked`, reads a `CheckpointName` string, then wraps the same stream in a nested `CheckpointInputStream`.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is `[componentName, checkpointTypeAndBytes]` per Kryo chunk. `nextCheckpoint` skips chunks after the first and returns entries valid only until the next call. Dependencies include Kryo chunked streams, `CheckpointName.valueOf`, nested checkpoint streams, and `PatchedInputChunked`. Risks include unknown names failing restore, callers closing nested streams, chunk boundary corruption, and future format compatibility. Tests should cover multi-component round trips, human-readable delegation, EOF handling, unknown names, truncated chunks, and entry validity across iterations.
