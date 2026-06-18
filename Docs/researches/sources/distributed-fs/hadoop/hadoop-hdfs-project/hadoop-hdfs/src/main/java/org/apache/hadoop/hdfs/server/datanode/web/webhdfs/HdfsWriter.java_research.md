# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/HdfsWriter.java

## Purpose

`HdfsWriter` streams HTTP request body chunks into a DFSClient output stream for WebHDFS CREATE and APPEND operations, then emits the prebuilt success response.

## Important APIs, Control Flow, and State

The handler stores a `DFSClient`, target `OutputStream`, and response. `channelRead0` writes each `HttpContent` buffer into the output stream. When it sees `LastHttpContent`, it closes the stream and client through `releaseDfsResourcesAndThrow`, sets `Connection: close`, writes the success response, and closes the channel. `channelInactive` closes resources if the client disconnects. `exceptionCaught` closes resources, converts the error through `ExceptionHandler`, writes a close response, and logs debug details.

State is per upload request: open DFSClient/output stream until completion or failure. The persisted result is the HDFS file data written by DFSClient; cleanup behavior after partial writes depends on DFSClient/HDFS semantics.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty `HttpContent`, `DFSClient`, `IOUtils`, and `ExceptionHandler`. It is installed by `WebHdfsHandler.onCreate` and `onAppend` after sending `100 Continue`.

Risks include blocking stream writes on Netty event-loop threads, partial HDFS files after client disconnect, exceptions during close being converted after data was written, and not explicitly flushing before success response beyond Netty flush callbacks. Tests should cover chunked upload, append, close on last chunk, client disconnect cleanup, output stream failure, and success/error response headers.
