# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftOutputStream.java

## Purpose
`SwiftOutputStream` wraps an `HttpURLConnection` output stream for direct Swift PUT uploads. It exists because `SwiftDirectClient` bypasses JOSS for object creation and needs an `OutputStream` facade compatible with Alluxio object creation.

## APIs and Control Flow
The constructor opens `httpCon.getOutputStream()` and stores both the delegate stream and connection. `write(int)`, `write(byte[])`, `write(byte[], int, int)`, and `flush()` delegate unchanged. `close()` closes the request body, reads either `getErrorStream()` for HTTP status >= 400 or `getInputStream()` otherwise, closes that response stream, logs close errors, and disconnects the HTTP connection.

## State, Dependencies, and Integration
State is the delegate stream and `HttpURLConnection`. It is constructed by `SwiftDirectClient.put`, which sets method, token, content type, chunked transfer, and timeouts. The class depends only on JDK networking and SLF4J and is explicitly not thread-safe.

## Risks and Test Signals
A failed Swift response status is logged but not surfaced to the caller unless stream handling throws, so callers may treat failed uploads as successful. The catch block can close `is` and swallow the original exception after logging. `SwiftOutputStreamTest` covers constructor failure, write and flush delegation, choosing error vs input stream by response code, and disconnect on close.
