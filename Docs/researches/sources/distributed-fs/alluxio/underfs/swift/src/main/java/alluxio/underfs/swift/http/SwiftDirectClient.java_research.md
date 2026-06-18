# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/http/SwiftDirectClient.java

## Purpose
`SwiftDirectClient` provides direct HTTP PUT upload setup for Swift objects, bypassing JOSS upload limitations while still using JOSS `Access` for public URL and auth token.

## APIs and Control Flow
`put(Access, String)` builds a URL from `access.getPublicURL()` and the object name, opens a URL connection, verifies it is an `HttpURLConnection`, sets method `PUT`, adds `X-Auth-Token`, content type, input/output flags, `Connection: close`, read timeout, `Transfer-Encoding: chunked`, and an 8 MiB chunked streaming mode. It connects and returns a `SwiftOutputStream`.

## State, Dependencies, and Integration
The class is stateless and thread-safe. It depends on JDK URL connections, JOSS `Access`, SLF4J, and `SwiftOutputStream`. `SwiftUnderFileSystem.createObject` calls it for all non-simulation object writes.

## Risks and Test Signals
Object names are concatenated into the URL without explicit URL encoding, so keys containing unsafe characters depend on prior normalization or backend tolerance. The fixed read timeout and chunk size are not configurable here. There is no listed direct unit test for request headers or URL formation.
