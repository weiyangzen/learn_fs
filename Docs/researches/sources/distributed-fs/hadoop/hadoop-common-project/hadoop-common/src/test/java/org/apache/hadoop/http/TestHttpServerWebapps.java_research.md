# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java

Purpose: this test validates webapp resource resolution for `HttpServer2`.

Important APIs and types: uses `createServer(String webapp)` and `stop()` from `HttpServerFunctionalTest`, with `FileNotFoundException` expected for missing resources.

Control flow: `testValidServerResource()` creates the standard `test` webapp server and stops it. `testMissingServerResource()` attempts to create `NoSuchWebapp`, expects `FileNotFoundException`, and fails if a server is returned.

State and persistence: no persistent server state; inherited helper may prepare the test webapp directory. Missing-webapp test only observes classpath/resource lookup.

Dependencies and integration points: integrates `HttpServer2` webapp lookup with test resource packaging.

Risks: depends on build/test resources being available on the classpath. If an invalid webapp is accidentally added, the negative test would fail.

Test signals: confirms valid webapp resources load and missing webapp names fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWebapps.java -->
