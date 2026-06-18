# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/http/TestHttpFileSystem.java

## Purpose
`TestHttpFileSystem` verifies basic HTTP filesystem open and status path resolution behavior.

## Important APIs, Types, And Functions
`setUp()` registers `HttpFileSystem` as `fs.http.impl`. `testHttpFileSystem()` uses `MockWebServer` to serve data and tests absolute URL, absolute path, and relative path opens. `testHttpFileStatus()` checks `getFileStatus()` path URI resolution. `assertSameData()` reads expected bytes.

## Control Flow
The open test enqueues three identical responses, starts the mock server, gets a Hadoop `FileSystem` for the server URI, opens `/foo` through three path forms, and checks the first recorded request path. The status test creates an HTTP filesystem for `http://www.example.com` and verifies all path forms resolve to `/foo`.

## State And Persistence
State is a per-test `Configuration`. Mock server state is in-memory and closed by try-with-resources.

## Dependencies And Integration Points
It depends on MockWebServer, Hadoop `HttpFileSystem`, `FileSystem`, `Path`, `IOUtils`, and URI/URL conversion.

## Risks
HTTP FS is read-only/simple; tests do not validate headers, errors, range requests, or redirects. Mock response reuse must be sufficient for all opens.

## Test Signals
Signals are exact body bytes for all path forms and `FileStatus` paths resolving to the expected HTTP URI.
