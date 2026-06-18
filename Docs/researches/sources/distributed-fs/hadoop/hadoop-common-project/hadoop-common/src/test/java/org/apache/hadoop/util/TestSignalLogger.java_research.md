# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestSignalLogger.java

Purpose: verifies Unix-only registration semantics for `SignalLogger`.

Important APIs and types: `SignalLogger.INSTANCE.register(Logger)`, SLF4J `Logger`, Apache Commons `SystemUtils.IS_OS_UNIX`, and JUnit assumptions.

Control flow: the test runs only on Unix. It registers the singleton signal logger once, then attempts a second registration and expects `IllegalStateException`.

State and persistence: mutates singleton signal-handler registration state for the JVM process. No files are involved.

Dependencies and integration points: integrates JVM signal handling with Hadoop logging for diagnostics on Unix platforms.

Risks: global singleton state means test ordering can matter if another test registers signals first; non-Unix platforms skip coverage. Test signals are assumption gating and the double-registration exception.
