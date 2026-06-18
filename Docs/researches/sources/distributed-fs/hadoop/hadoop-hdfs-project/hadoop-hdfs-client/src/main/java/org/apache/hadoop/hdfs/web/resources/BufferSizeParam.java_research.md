# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BufferSizeParam.java

## Purpose

`BufferSizeParam` models optional WebHDFS `buffersize` values for open/create/append flows.

## Important APIs, Types, And Functions

It extends `IntegerParam`, defines `NAME = "buffersize"` and default `NULL`, constructors from Integer/String, and `getValue(Configuration)`.

## Control Flow

Explicit values must be at least 1. Unset values resolve to `io.file.buffer.size` from configuration.

## State And Persistence

Only inherited parsed value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem` create, append, open, and read-runner URL construction.

## Risks

Omitted vs explicit buffer size can change URL behavior. Large values affect memory and HTTP stream buffering.

## Test Signals

Tests should cover default lookup, invalid zero/negative values, serialization, and open/read URL parameters.
