# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java

Purpose: this test verifies that a global `FilterInitializer` applies a servlet filter to all relevant `HttpServer2` paths, including static, servlet, JSP-like, and default endpoints.

Important APIs and types: nested `RecordingFilter` implements `Filter` and records request URIs in static `RECORDS`. Its `Initializer` calls `container.addGlobalFilter(...)`. The static `access()` helper opens URLs and drains or ignores responses.

Control flow: `testServletFilter()` configures the initializer, starts a test server, accesses a list of paths, stops the server, then removes each expected URI from `RECORDS`. It expects one extra `/index.html` record because `/` redirects.

State and persistence: static `RECORDS` is the main state; it is a `TreeSet` of observed URIs. The server is local and ephemeral. No durable files are written.

Dependencies and integration points: integrates servlet filters, `FilterContainer.addGlobalFilter`, default Hadoop HTTP endpoints, static content serving, redirects, and `NetUtils`.

Risks: static `RECORDS` is not cleared inside the test, so repeated execution in the same JVM could retain prior entries. The test tolerates HTTP errors when paths are missing because it only needs filter invocation.

Test signals: confirms global filters see all configured URL classes and root redirect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestGlobalFilter.java -->
