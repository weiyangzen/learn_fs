# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java

Purpose: this test is intended to verify that non-global filters are applied only to configured path specs.

Important APIs and types: nested `RecordingFilter` records request URIs in static `RECORDS`, and its initializer calls `container.addFilter(...)`. `testPathSpecFilters()` builds a test server with path specs `"/path"` and `"/path/*"`.

Control flow: the test starts a server, accesses filtered paths and unfiltered paths, stops the server, then asserts only filtered paths were recorded. The access helper drains successful responses and ignores IOExceptions for missing pages.

State and persistence: static `RECORDS` tracks observed filtered URIs. The server is local and temporary; no durable state is touched.

Dependencies and integration points: integrates `HttpServer2` path-spec handling, filter initializers, servlet filter dispatch, and URL access through `NetUtils`.

Risks: the method lacks a visible `@Test` annotation in the source, so under JUnit 5 it may not execute unless another mechanism discovers it. Static `RECORDS` is not cleared before use.

Test signals: when executed, it proves filters registered with path specs apply to `/path` and descendants but not `/` or wildcard literal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestPathFilter.java -->
