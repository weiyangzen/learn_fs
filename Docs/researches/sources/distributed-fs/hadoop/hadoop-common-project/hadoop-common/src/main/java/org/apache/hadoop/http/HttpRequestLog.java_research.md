<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java

Purpose: factory for Jetty request log instances backed by SLF4J. It maps common Hadoop HTTP server names to component-specific request loggers.

Important APIs, types, and functions: static `serverToComponent` maps `cluster` to `resourcemanager`, `hdfs` to `namenode`, and `node` to `nodemanager`. `getRequestLog(name)` creates a `Slf4jRequestLogWriter`, sets logger `http.requests.<component>`, and returns a `CustomRequestLog` with extended NCSA format.

Control flow: `HttpServer2.initializeWebServer()` asks for a request log by server name, then wraps it in Jetty `RequestLogHandler`.

State and persistence: immutable static map only. Actual request log persistence is controlled by the SLF4J/logging backend.

Dependencies and integration points: integrates Jetty request logging with Hadoop component logger names.

Risks and test signals: log volume and privacy are controlled outside this class. Tests should verify server-name mapping, logger naming, and that the returned request log writes extended NCSA-compatible records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpRequestLog.java -->
