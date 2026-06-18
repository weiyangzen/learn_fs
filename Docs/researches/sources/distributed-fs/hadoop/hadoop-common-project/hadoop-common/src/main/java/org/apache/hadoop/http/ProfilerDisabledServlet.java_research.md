<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java

Purpose: fallback servlet for `/prof` when async-profiler is not configured at server startup.

Important APIs, types, and functions: `doGet()` sets HTTP 500, applies `ProfileServlet.setResponseHeader()`, and writes a diagnostic message with setup guidance.

Control flow: `HttpServer2.addAsyncProfilerServlet()` installs this servlet when neither `ASYNC_PROFILER_HOME` nor `async.profiler.home` is set.

State and persistence: no state and no persistent effects.

Dependencies and integration points: tied to `ProfileServlet` response-header conventions and `HttpServer2` profiler enablement.

Risks and test signals: this endpoint intentionally exposes setup guidance. Tests should verify disabled installation, HTTP status, CORS/text headers, and message content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfilerDisabledServlet.java -->
