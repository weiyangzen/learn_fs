<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java

Purpose: servlet that exports Hadoop metrics in Prometheus text format.

Important APIs, types, and functions: `getPrometheusSink()` retrieves `HttpServer2.PROMETHEUS_SINK` from the servlet context. `doGet()` forces `DefaultMetricsSystem.instance().publishMetricsNow()`, writes metrics via `PrometheusMetricsSink.writeMetrics()`, and flushes the response writer.

Control flow: `HttpServer2.addPrometheusServlet()` creates the sink, stores it in the web context, and maps this servlet at `/prom` when Prometheus support is enabled.

State and persistence: no local state. Metrics state lives in the default metrics system and the sink object.

Dependencies and integration points: integrates Hadoop metrics2 default system, Prometheus sink, and servlet context attributes.

Risks and test signals: a missing or wrong sink context attribute would cause null or class-cast failures. Tests should cover enabled/disabled registration, context attribute presence, publish-before-write behavior, and response content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/PrometheusServlet.java -->
