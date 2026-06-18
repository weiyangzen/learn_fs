# sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystemFactory.java

## Purpose
`WebUnderFileSystemFactory` registers Web UFS support for `http://` and `https://` paths.

## APIs and Control Flow
`create` validates a non-null path and constructs `WebUnderFileSystem` with an `AlluxioURI` and UFS configuration. `supportsPath` accepts non-null paths starting with `Constants.HEADER_HTTP` or `Constants.HEADER_HTTPS`.

## State, Dependencies, and Integration
The factory is stateless and thread-safe. It depends on Alluxio URI and UFS factory APIs and is consumed by the factory registry.

## Risks and Test Signals
There is no validation that a URL is reachable or syntactically complete before constructing the UFS. `WebUnderFileSystemFactoryTest` confirms registry support for HTTP/HTTPS and rejects a near-miss `httpx://` scheme.
