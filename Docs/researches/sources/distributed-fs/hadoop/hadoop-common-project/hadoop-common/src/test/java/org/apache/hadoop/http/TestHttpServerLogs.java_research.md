# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java

Purpose: this functional test checks whether the `/logs` servlet is registered according to `HADOOP_HTTP_LOGS_ENABLED`.

Important APIs and types: `startServer(Configuration)` creates and starts a test server, sets `baseUrl`, and uses `HttpServerFunctionalTest` helpers. Tests use Apache `HttpStatus`, `CommonConfigurationKeysPublic.HADOOP_HTTP_LOGS_ENABLED`, and `NetUtils`.

Control flow: `testLogsEnabled()` enables logs, starts the server, requests `/logs`, and expects HTTP 200. `testLogsDisabled()` disables logs, starts the server, requests `/logs`, and expects HTTP 404. Cleanup stops a live server after all tests.

State and persistence: static `server` and `baseUrl` are overwritten by each test. No log files are inspected; the test only checks endpoint availability.

Dependencies and integration points: integrates `HttpServer2` default servlet registration with public configuration keys.

Risks: because `server` is static and each test calls `startServer()`, a prior started server must be stopped by cleanup or test isolation. The tests do not verify log content, only servlet routing.

Test signals: confirms `/logs` is present or absent based on configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLogs.java -->
