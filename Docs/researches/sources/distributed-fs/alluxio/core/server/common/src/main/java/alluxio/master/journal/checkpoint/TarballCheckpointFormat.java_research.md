# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/TarballCheckpointFormat.java

## Purpose
`TarballCheckpointFormat` identifies RocksDB checkpoints stored as single-threaded tarball archives.

## Important APIs, Types, And Functions
`createReader` returns `TarballCheckpointReader`, which validates type `ROCKS_SINGLE`. `parseToHumanReadable` prints a message directing users to `bin/alluxio readJournal`.

## Control Flow, State, Dependencies, Risks, And Tests
The actual archive payload is opaque to this class; it only validates the checkpoint type and declines textual parsing. Persistent state is the tar.gz RocksDB backup data after the checkpoint header. Dependencies are `CheckpointInputStream` and Guava preconditions. Risks include no structural validation here, poor diagnostics for corrupt archives, and no human-readable output. Tests should cover correct/wrong type validation and readJournal integration elsewhere.
