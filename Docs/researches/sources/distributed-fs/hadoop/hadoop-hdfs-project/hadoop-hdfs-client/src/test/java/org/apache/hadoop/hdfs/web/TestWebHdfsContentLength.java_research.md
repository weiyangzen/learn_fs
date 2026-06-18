## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsContentLength.java

Purpose: this socket-level test verifies WebHDFS client HTTP request headers, especially `Content-Length` and `Transfer-Encoding`, for GET/PUT/POST/DELETE operations and redirect upload flows.

Important APIs and types: it uses a raw `ServerSocket`, `FileSystem` for a `webhdfs://` URI, `FSDataOutputStream`, regex extraction of `Content-Length|Transfer-Encoding`, and single-thread executor futures that capture incoming HTTP requests.

Control flow: setup binds a local socket, constructs redirect and error HTTP responses, and opens a WebHDFS filesystem. Each test schedules one or more accept/read tasks, invokes a filesystem operation expected to fail, and inspects the captured request headers. GET/status/open/delete should not send content length; mkdirs and concat send `Content-Length: 0`; redirected create/append first send zero-length control requests then stream data with chunked transfer encoding.

State and persistence: state is local socket binding, captured request strings, configured path, and executor. No HDFS state is persisted because the fake server always errors or redirects.

Dependencies and integration points: integrates Java HTTP client behavior, WebHDFS operation mapping, redirect handling, and upload streaming semantics at the raw HTTP wire level.

Risks: Java HTTP implementation can split chunked headers/body, so the helper consumes the whole socket input to avoid client hangs. The class-level timeout bounds network stalls.

Test signals: verifies correct absence/presence of content length, zero-length control requests for mutating non-upload operations, and chunked transfer for redirected create/append data streams.
