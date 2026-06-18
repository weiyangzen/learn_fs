# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ChunkedEncodingInputStream.java

## Purpose
`ChunkedEncodingInputStream` decodes AWS S3 `aws-chunked` streaming request bodies into raw object bytes. It strips chunk headers and signatures while presenting a normal `InputStream` to callers.

## Important APIs, Types, and Functions
The class extends `FilterInputStream` and overrides `read()` and `read(byte[], int, int)`. Internal state is `mCurrentChunkLength` and `mCurrentChunkIdx`. `decodeChunkHeader` reads the next hexadecimal chunk length up to `;` and skips the fixed-size signature suffix.

## Control Flow, State, and Persistence
Before each read, the stream checks whether the current chunk is exhausted. If so, it parses a new header, resets the chunk index, and skips 82 bytes after the hex length. Bulk reads are capped at the current chunk boundary so callers never receive header bytes. A zero-length or exhausted chunk causes `read(byte[], ...)` to return `-1`. State is in-memory cursor state over the wrapped input stream.

## Dependencies and Integration Points
It is part of the S3 proxy upload path for clients using SigV4 streaming/chunked transfer. It depends only on Java I/O and Alluxio's S3 proxy package.

## Risks
The implementation does not verify chunk signatures. The fixed 82-byte skip assumes a specific `;chunk-signature=` layout and 64-character signature. `skip` returning zero could loop indefinitely on some streams. Malformed hex length throws `NumberFormatException`, not `IOException`. Single-byte reads do not explicitly stop at a zero-length terminal chunk until underlying reads indicate EOF.

## Test Signals
Useful tests should include valid multi-chunk streams, zero-length terminal chunks, bulk reads crossing chunk boundaries, malformed headers, short signatures, and streams whose `skip` returns partial or zero progress.
