# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointInputStream.java

## Purpose
`OptimizedCheckpointInputStream` reads compressed checkpoint files while updating a message digest.

## Important APIs, Types, And Functions
The constructor wraps `Files.newInputStream` in a 4MB `BufferedInputStream`, `LZ4FrameInputStream`, and `DigestInputStream`, then passes it to `CheckpointInputStream`.

## Control Flow, State, Dependencies, Risks, And Tests
Reading the stream decompresses LZ4 data and updates the provided digest over the compressed/decompressed stream as configured by wrapper order, then `CheckpointInputStream` consumes the type id. Persistent state is the checkpoint file plus MD5 sidecar verified by `Checkpointed`. Dependencies include LZ4, Java NIO files, `MessageDigest`, and `OptimizedCheckpointOutputStream.BUFFER_SIZE`. Risks include wrapper-order checksum expectations, decompression failures, open file handles, and type header errors. Tests should cover write/read compatibility, checksum verification integration, corrupt LZ4 frames, missing files, and all checkpoint types.
