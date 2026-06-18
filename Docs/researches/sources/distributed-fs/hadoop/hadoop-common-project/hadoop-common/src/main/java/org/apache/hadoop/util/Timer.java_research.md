# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Timer.java

Purpose: `Timer` is an overridable object wrapper around `Time`, intended for dependency injection in code that needs test-controlled clocks.

Important APIs/types/functions: instance methods `now`, `monotonicNow`, and `monotonicNowNanos` delegate to `Time`.

Control flow: no branching; subclasses can override methods to inject fake time.

State and persistence behavior: no fields and no persistence.

Dependencies and integration points: integrates with code that would otherwise call static time methods directly, improving testability for timeout and retry logic.

Risks: callers must choose wall-clock versus monotonic APIs correctly; the wrapper does not enforce duration-safe usage.

Test signals: unit tests can subclass `Timer` and verify consumers honor injected values.
