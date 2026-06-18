# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java

Purpose: this test covers the default disabled `/prof` endpoint when async profiling is not enabled.

Important APIs and types: uses `HttpServerFunctionalTest` helpers, `ProfileServlet.ACCESS_CONTROL_ALLOW_METHODS`, `ACCESS_CONTROL_ALLOW_ORIGIN`, and `HttpServletResponse` status constants.

Control flow: class setup starts a default test server and records `baseUrl`. `testQuery()` expects reading `/prof` to fail with an internal-server-error URL message, then separately opens a connection to assert CORS headers. `testRequestMethods()` sends PUT, POST, DELETE, and GET to `/prof` and verifies method-not-allowed for mutating verbs and internal server error for GET.

State and persistence: only an in-process `HttpServer2` is started and stopped. No profiler files are expected because profiling is disabled.

Dependencies and integration points: integrates `ProfileServlet` registration in default `HttpServer2` webapp and CORS header behavior.

Risks: asserting the IOException message contains a specific URL/status fragment may vary across JDK URLConnection implementations. The GET failure is expected behavior for disabled profiling, not a test infrastructure failure.

Test signals: validates disabled profile servlet status codes and CORS metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestDisabledProfileServlet.java -->
