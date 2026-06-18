# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/WebHdfsHandler.java

## Purpose

`WebHdfsHandler` is the Netty implementation of the DataNode side of WebHDFS data operations. It handles CREATE, APPEND, OPEN, GETFILECHECKSUM, and CORS preflight for CREATE by building a request UGI, creating DFSClients to the requested NameNode, and streaming data through Netty.

## Important APIs, Control Flow, and State

`channelRead0` validates the `/webhdfs/v1` prefix, parses parameters, obtains a UGI from `DataNodeUGIProvider`, records the HDFS path, injects a delegation token into the UGI when secure, and runs `handle` inside `ugi.doAs` with request logging in a finally block. `handle` dispatches by HTTP method plus `op`. `onCreate` sends `100 Continue`, resolves permission/unmasked permission, create flags, replication, block size, and create-parent, creates a DFSClient with `confForCreate`, opens an HDFS output stream, prepares `201 Created` with `Location` and CORS headers, and replaces itself with `HdfsWriter`. `onAppend` is similar but opens append and returns `200 OK`.

`onOpen` creates a DFSClient input stream, seeks to offset, computes visible content length bounded by optional length, sets octet-stream/CORS/close headers, and writes a `ChunkedStream` that closes the DFSClient when complete. `onGetFileChecksum` gets the checksum, serializes it as JSON, and closes. `allowCORSOnCreate` handles OPTIONS. State is request-local fields (`path`, `params`, `ugi`, `resp`), and persistence is the HDFS data/checksum state accessed through DFSClient.

## Dependencies, Integration, Risks, and Tests

Dependencies include Netty HTTP/streaming, `DFSClient`, WebHDFS parameter enums, HDFS security tokens, UGI, `JsonUtil`, `LimitInputStream`, and WebHDFS client config patterns. It integrates with `URLDispatcher`, `HdfsWriter`, `ExceptionHandler`, and the NameNode/DataNode WebHDFS redirect flow.

Risks include blocking DFSClient operations on Netty event-loop threads, response code logging defaulting to 500 if failure occurs before `resp`, unrestricted CORS headers, careful resource closing for open/checksum paths, create umask semantics via `confForCreate`, token injection duplication, and invalid operation mapping. Tests should cover each supported operation, method/op mismatch, secure and insecure UGI paths, create flags and permissions, ranged open lengths, checksum JSON, upload failure cleanup, CORS preflight, and request logging status.
