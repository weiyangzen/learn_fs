# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/ByteRangeInputStream.java

## Purpose

`ByteRangeInputStream` adapts HTTP byte-range reads to the `FSInputStream` contract. It hides repeated HTTP connection creation when callers seek, positioned-read, or read fully from WebHDFS-like endpoints.

## Important APIs, Types, And Functions

The main extension point is `URLOpener.connect(offset, resolved)`, plus subclass hook `getResolvedUrl(HttpURLConnection)`. State is tracked with `StreamStatus` values `NORMAL`, `SEEK`, and `CLOSED`. Core methods are `getInputStream`, `openInputStream`, `read`, `seek`, positioned `read`, `readFully`, `getPos`, `close`, and `available`.

## Control Flow

Construction immediately opens the first stream. `seek` records a new start/current position and puts the stream in `SEEK`. The next read closes the old stream, opens either the original or resolved URL with the requested offset, updates `fileLength` from `Content-Length` unless transfer encoding is chunked, and wraps non-chunked streams in `BoundedInputStream`. Positioned reads open temporary streams and do not disturb the main stream state.

## State And Persistence

State is in-memory: current input stream, original/resolved URL openers, `startPos`, `currentPos`, optional `fileLength`, and status. No persistence exists. `fileLength` may be unknown for chunked transfer encoding.

## Dependencies And Integration Points

It depends on `HttpURLConnection`, commons-io `BoundedInputStream`, Hadoop `FSInputStream`, `FSExceptionMessages`, and Guava HTTP header constants. `WebHdfsFileSystem.OffsetUrlInputStream` extends it for WebHDFS open redirects.

## Risks

Header parsing assumes exact map keys from `HttpURLConnection`; case behavior depends on the JDK header map. Non-chunked responses without `Content-Length` fail. Negative seeks throw `EOFException`, but seeking beyond EOF is detected only when the server response or read length exposes it. `available` delegates to the current HTTP stream and can force a connection.

## Test Signals

Tests should cover first open, seek then read, positioned read isolation, chunked vs non-chunked responses, missing `Content-Length`, premature EOF detection, close behavior, and resolved URL reuse.
