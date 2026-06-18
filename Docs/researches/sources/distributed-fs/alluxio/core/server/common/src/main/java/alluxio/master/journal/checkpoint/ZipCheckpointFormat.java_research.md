# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/ZipCheckpointFormat.java

## Purpose
`ZipCheckpointFormat` identifies RocksDB checkpoints stored as parallel-created zip archives.

## Important APIs, Types, And Functions
`createReader` returns `ZipCheckpointReader`, which validates type `ROCKS_PARALLEL`. `parseToHumanReadable` prints that no string representation is available.

## Control Flow, State, Dependencies, Risks, And Tests
Like the tarball format, this class treats archive bytes as opaque after validating the type header. Persistent state is a zip-format RocksDB checkpoint. Dependencies are `CheckpointInputStream` and preconditions. Risks include no archive validation, typo in the nested class comment saying tarball-based, and limited inspectability. Tests should cover type validation, parse message, corrupt archive handling in the actual restore layer, and readJournal integration.
