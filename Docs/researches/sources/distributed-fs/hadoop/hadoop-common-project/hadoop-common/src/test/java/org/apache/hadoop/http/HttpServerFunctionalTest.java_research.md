# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java

Purpose: this base class centralizes helpers for `HttpServer2` functional tests: creating local test servers, preparing webapp directories, stopping servers, deriving base URLs, reading responses, and testing large request headers.

Important APIs and types: exposes `LongHeaderServlet`, `createTestServer()` overloads, `createServer()` overloads, `createAndStartTestServer()`, `stop()`, `getServerURL()`, `readOutput()`, and `testLongHeader()`. It extends JUnit `Assertions`.

Control flow: creation helpers call `prepareTestWebapp()` when needed, then configure `HttpServer2.Builder` with localhost endpoint, find-port behavior, optional configuration, ACL, path specs, or X-Frame options. `readOutput()` streams a URL response into a string. `testLongHeader()` sends a 63 KiB header and expects HTTP 200.

State and persistence: creates the test webapp directory under `test.build.webapps` or `build/test/webapps`. Static `baseUrl` is shared by subclasses. Servers bind ephemeral local ports.

Dependencies and integration points: integrates `HttpServer2.Builder`, Jetty servlet API, Hadoop `Configuration`, `AccessControlList`, and `NetUtils`.

Risks: `prepareTestWebapp()` swallows `IOException` after mkdir attempts, so canonical-path failures may be hidden unless mkdir itself returns false. Static `baseUrl` can be overwritten by subclasses.

Test signals: used throughout HTTP tests to guarantee consistent local server construction, cleanup, URL derivation, and 64 KiB header coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/HttpServerFunctionalTest.java -->
