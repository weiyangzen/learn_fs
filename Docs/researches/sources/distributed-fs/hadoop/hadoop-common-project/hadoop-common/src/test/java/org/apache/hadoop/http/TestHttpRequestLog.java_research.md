# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java

Purpose: this small unit test verifies the request-log factory for `HttpServer2`.

Important APIs and types: calls `HttpRequestLog.getRequestLog("test")` and asserts the returned Jetty `RequestLog` is a `CustomRequestLog` using a `Slf4jRequestLogWriter` and `CustomRequestLog.EXTENDED_NCSA_FORMAT`.

Control flow: single test method obtains the log and checks type and format. No server is started.

State and persistence: no persistent state. The test only inspects constructed logging objects.

Dependencies and integration points: integrates Hadoop `HttpRequestLog` with Jetty request-log APIs and SLF4J writer selection.

Risks: tightly coupled to Jetty implementation classes and the exact selected log format. Jetty upgrades that change class names or defaults can break it.

Test signals: confirms request logging is configured and uses extended NCSA format through SLF4J.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpRequestLog.java -->
