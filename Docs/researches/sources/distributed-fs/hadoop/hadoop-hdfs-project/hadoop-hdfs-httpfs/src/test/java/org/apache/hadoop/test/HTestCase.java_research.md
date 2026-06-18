# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/HTestCase.java

Purpose: Common base class for HTTPFS tests, providing system-property initialization, JUnit extensions, scaled sleeps, and polling helpers.

Important APIs/types/functions: constants `TEST_WAITFOR_RATIO_PROP`, extensions `TestDirHelper`, `TestJettyHelper`, and `TestExceptionHelper`; `setWaitForRatio`, `getWaitForRatio`, nested `Predicate`, `sleep`, and `waitFor` overloads.

Control flow: static initialization loads test properties. Instance wait ratio defaults from `test.waitfor.ratio`. `sleep` scales time by the ratio. `waitFor` loops until a predicate returns true or timeout expires, logs progress roughly every five seconds, optionally fails on timeout, and wraps predicate exceptions in `RuntimeException`.

State and persistence: process-wide system properties and per-test extension state; no files directly, though registered helpers do.

Dependencies/integration: JUnit 5 extensions, Hadoop `Time`, and `SysPropsForTestsLoader`.

Risks and test signals: central infrastructure for timing-sensitive tests. Polling sleeps fixed 100 ms and console logging can slow very large test runs; exception wrapping may obscure original checked exception types.
