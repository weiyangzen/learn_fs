# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestLeakReporter.java

## Purpose
`TestLeakReporter` validates `LeakReporter`, which logs leaked resources and invokes a close action exactly once when a probe says a resource is still open.

## Important APIs, Types, And Functions
Tests instantiate `LeakReporter(message, probe, closeAction)`, call `close()`, inspect `isClosed()`, and use `THREAD_FORMAT`. Helpers include `expectClose()`, `closed()`, `raiseNPE()`, and `assertCloseCount()`.

## Control Flow
`testLeakInvocation()` changes the current thread name, captures root logs, closes a reporter whose probe returns true, verifies close count and logged warning/info content including old thread info and stack trace, then closes again to verify idempotence. Other tests verify no action when probe returns false, swallowed probe failure, and swallowed close-action failure while still marking closed.

## State And Persistence
State is `closeCount` and captured logs. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on SLF4J, `GenericTestUtils.LogCapturer`, AssertJ, and `AbstractHadoopTestBase`. LeakReporter is likely used by stream/resource wrappers.

## Risks
Log-content assertions can be brittle across logging format changes. Swallowing probe/close exceptions prevents cleanup failures from cascading but can hide real cleanup bugs.

## Test Signals
Signals are one close callback on first leak close, no reentrant callback, expected log fragments, no callback when not leaked, and closed state after close-action exception.
