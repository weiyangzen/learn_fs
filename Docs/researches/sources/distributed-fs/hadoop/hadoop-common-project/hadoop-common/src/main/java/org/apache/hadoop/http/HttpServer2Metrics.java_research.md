<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java

Purpose: Hadoop metrics2 adapter around Jetty `StatisticsHandler`. It exposes Jetty request, dispatch, async, response, byte, and timing counters as Hadoop metrics.

Important APIs, types, and functions: annotated metric getters delegate to `StatisticsHandler` methods such as `getRequests()`, `getRequestsActive()`, `getRequestTimeMean()`, `getResponses4xx()`, and `getResponsesBytesTotal()`. `create()` registers a source named `HttpServer2-<port>`. `remove()` unregisters that source name.

Control flow: `HttpServer2.start()` creates this object after the server starts and a port is known. Metrics polling calls annotated getters, which read live Jetty counters.

State and persistence: stores the statistics handler and port. Metrics are in process memory and exported through Hadoop metrics sinks.

Dependencies and integration points: depends on Jetty statistics and Hadoop metrics2 default system.

Risks and test signals: duplicate registration is avoided by removing the old source name before registering. Tests should cover repeated server starts on the same port, non-default ports, metric values after sample requests, and unregister on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpServer2Metrics.java -->
