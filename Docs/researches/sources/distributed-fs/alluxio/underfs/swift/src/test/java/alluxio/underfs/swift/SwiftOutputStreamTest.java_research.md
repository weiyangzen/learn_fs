# sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftOutputStreamTest.java

## Purpose
This PowerMock/JUnit test suite verifies the thin delegation and close behavior of `SwiftOutputStream`.

## Important Tests
`testConstructor` forces `HttpURLConnection.getOutputStream()` to throw and expects an `IOException` containing the original message. `testWrite1`, `testWrite2`, and `testWrite3` verify delegation to the wrapped output stream. `testCloseError` checks that HTTP 400 causes `getErrorStream()` and disconnect. `testCloseSuccess` checks that HTTP 200 uses `getInputStream()` and disconnect. `testFlush` verifies flush delegation.

## Dependencies and Integration
The suite uses PowerMock runner, Mockito verification, and `ExpectedException`. It mocks the HTTP connection and output stream rather than making network calls.

## Signals and Gaps
The tests document the current behavior that close inspects the response stream but does not assert failure for HTTP 400. They do not cover null response/error streams, double close behavior, response stream close failures, or status codes such as 201/202 that are expected for Swift writes.
