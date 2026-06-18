# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/OptimizedCheckpointOutputStream.java

## Purpose
`OptimizedCheckpointOutputStream` writes compressed checkpoint files while updating a message digest.

## Important APIs, Types, And Functions
`BUFFER_SIZE` is 4MB. Constructors wrap `Files.newOutputStream` in a buffered stream, LZ4 frame output stream, and `DigestOutputStream`. `write(int)` and `close` delegate to the wrapped stream.

## Control Flow, State, Dependencies, Risks, And Tests
Callers write checkpoint bytes to this stream; close finalizes the LZ4 frame and output file. The digest is later saved by `Checkpointed`. Dependencies include LZ4, `FormatUtils`, Java NIO files, and `MessageDigest`. Risks include only overriding single-byte `write` while relying on `OutputStream` default array writes, partial files on exceptions, close being required for valid LZ4 frames, and buffer-size benchmark constructor misuse. Tests should cover array writes, read-back compatibility, digest sidecar verification, close/failure behavior, and custom buffer sizes.
