# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java

Purpose: this test verifies `HttpServer2` lifecycle state reporting and context cleanup.

Important APIs and types: helper assertions use `HttpServer2.isAlive()` and `toString()` state descriptions `STATE_DESCRIPTION_ALIVE` and `STATE_DESCRIPTION_NOT_LIVE`. It uses inherited server creation and `stop()` helpers.

Control flow: tests check a created but unstarted server is not live, stopping an unstarted server is allowed, a started server reports live, a stopped server reports not live, stopping twice is idempotent, and servlet-context attributes are cleared after stop.

State and persistence: state is in the server instance and webapp context attributes. No durable files are written beyond inherited test webapp preparation.

Dependencies and integration points: integrates lifecycle methods of `HttpServer2`, context attribute access, and textual `toString()` diagnostics.

Risks: string-based assertions on `toString()` can break if diagnostics are reworded while behavior remains correct. The method name `testWepAppContextAfterServerStop` contains a typo but tests webapp context cleanup.

Test signals: validates idempotent stop behavior, live/not-live reporting, and cleanup of context state after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerLifecycle.java -->
