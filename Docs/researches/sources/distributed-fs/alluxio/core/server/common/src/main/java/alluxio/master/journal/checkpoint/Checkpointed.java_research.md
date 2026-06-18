# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/Checkpointed.java

## Purpose
`Checkpointed` is the base interface for master components that can write and restore metadata snapshots.

## Important APIs, Types, And Functions
Implementations provide `getCheckpointName`, stream `writeToCheckpoint`, and stream `restoreFromCheckpoint`. Default file-based methods run asynchronously, wrap output/input in optimized LZ4 plus MD5 streams, save or verify `.md5` files, and convert failures to `AlluxioRuntimeException`.

## Control Flow, State, Dependencies, Risks, And Tests
File checkpoint writes compute MD5 while writing compressed data, then persist the MD5 sidecar. Restore recomputes and verifies after loading. Persistent state is a file named by `CheckpointName` plus saved MD5. Dependencies include Ratis `MD5Hash`/`MD5FileUtil`, `OptimizedCheckpoint*Stream`, futures, and executor services. Risks include async exceptions hidden in futures, partial files on failure, MD5 sidecar mismatch, directory permissions, and interruption handling left to implementations. Tests should cover successful async write/restore, checksum mismatch, implementation exceptions, executor behavior, and file naming.
