# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/InputStreamEntity.java

## Purpose
`InputStreamEntity` is a JAX-RS `StreamingOutput` wrapper for returning bytes from an `InputStream` with a configurable copy buffer.

## Important APIs, Types, and Functions
The class stores an `InputStream is` and `int offset`. `write(OutputStream os)` allocates a byte buffer of `offset` length, loops on `is.read(buffer)`, and writes each block to the response output stream.

## Control Flow
When Jersey writes the response, `write` streams all bytes from the source input to the servlet output. It closes the input stream in a `finally` block after copying completes or fails.

## State and Persistence
State is the source stream and buffer size. The class does not persist data; it performs transient network/file stream copying.

## Dependencies and Integration Points
HttpFS server operations that return file contents use this kind of `StreamingOutput`. It complements `FileSystemReleaseFilter`: the filesystem must remain open through streaming and be released after response completion.

## Risks
The field name `offset` is misleading because it is used as buffer size. A zero or negative buffer size would fail at runtime. The output stream is not closed, which is correct for servlet containers, but callers must understand ownership. Copying is blocking and unthrottled.

## Test Signals
`BaseTestHttpFSWith.testOpen` writes a byte through the proxied filesystem and reads it through HttpFS, validating the streaming response path at a high level.
