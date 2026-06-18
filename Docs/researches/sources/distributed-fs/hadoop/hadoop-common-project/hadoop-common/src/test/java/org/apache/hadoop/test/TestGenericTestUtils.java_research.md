# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TestGenericTestUtils.java

Purpose: self-tests key behaviors of `GenericTestUtils`.

Important APIs/types/functions: extends `GenericTestUtils`; tests `assertExceptionContains`, `LogCapturer`, `waitFor`, and `toLevel`; nested `BrokenException` returns null from `toString`.

Control flow: exception tests verify null throwable, null `toString`, wrong text with nested cause, and successful text matching. Log tests capture SLF4J output, assert contents, clear buffer, stop capture, and verify no further output. Wait tests validate null supplier and invalid timing arguments. Level tests verify valid and invalid string conversion with default fallback.

State and persistence behavior: uses in-memory log capture buffers and no durable state.

Dependencies and integration points: validates the utility class used widely across Hadoop tests, with JUnit timeouts on log capture paths.

Risks and test signals: protects error-message constants and capture cleanup behavior. Narrow coverage leaves many `GenericTestUtils` helpers untested here, but the covered areas are high reuse.
