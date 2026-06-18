
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/NanoTimer.java

Purpose: Small nanosecond-resolution stopwatch and formatting helper used by TFile performance-style tests.

Important APIs and types: Provides `start()`, `stop()`, `read()`, `reset()`, `isStarted()`, `toString()`, and static `nanoTimeToString(long)`. Uses `System.nanoTime()`.

Control flow: `start()` records the current time only when not already started. `stop()` accumulates elapsed time only when started. `read()` and `toString()` return error indicators if never started. Formatting scales nanoseconds through microseconds, milliseconds, seconds, minutes, hours, and days.

State and persistence: Maintains `last`, `started`, and cumulative elapsed nanoseconds in memory. It is not thread-safe and has no persistence.

Dependencies and integration points: Used by `TestTFileSeek` for file creation and seek timing.

Risks: `read()` does not include an active interval until `stop()` is called. The class is intended for tests, not production metrics.

Test signals: Enables human-readable timing output for benchmark tests; no assertions directly target it in this subset.
