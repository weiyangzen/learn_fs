# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java

Purpose: this functional test covers the enabled/test-run behavior of async profiler servlets `/prof` and `/prof-output-hadoop`.

Important APIs and types: setup calls `ProfileServlet.setIsTestRun(true)`, sets `async.profiler.home` to a random UUID string, starts a test server, and uses profile servlet CORS and refresh headers.

Control flow: `testQuery()` reads `/prof` and expects a started-profiling message plus async-profiler guidance. It opens `/prof` again to assert allowed methods, HTTP 202 Accepted, CORS origin, and a refresh header pointing at a generated profiler output path. It then reads and checks `/prof-output-hadoop` returns HTTP 200.

State and persistence: global test-run flag and JVM property are modified in setup and restored in cleanup. The server is local and stopped after all tests. Profiler output is simulated by test-run mode rather than requiring a real async-profiler installation.

Dependencies and integration points: integrates `ProfileServlet`, `ProfileOutputServlet`, default server registration, CORS headers, and refresh/redirect behavior.

Risks: depends on global static servlet test mode and a JVM system property, so cleanup is essential. Assertions include output text and header prefix details.

Test signals: validates enabled profile endpoint response, CORS metadata, accepted status, refresh target, and output endpoint availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestProfileServlet.java -->
