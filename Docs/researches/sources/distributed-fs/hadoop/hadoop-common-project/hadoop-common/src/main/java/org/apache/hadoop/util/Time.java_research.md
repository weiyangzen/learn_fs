# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Time.java

Purpose: `Time` centralizes wall-clock and monotonic time utilities plus a Hadoop-standard timestamp formatter.

Important APIs/types/functions: `now()` returns `System.currentTimeMillis`. `monotonicNow()` returns `System.nanoTime()` converted to milliseconds. `monotonicNowNanos()` returns raw `System.nanoTime`. `formatTime(long)` formats milliseconds with a thread-local `SimpleDateFormat` pattern `yyyy-MM-dd HH:mm:ss,SSSZ`. `getUtcTime()` returns the current UTC calendar time in milliseconds.

Control flow: calls are direct wrappers, except `DATE_FORMAT` lazily creates a formatter per thread.

State and persistence behavior: static thread-local formatters persist per thread until thread termination. No external persistence.

Dependencies and integration points: used throughout Hadoop for interval measurement and human-readable logs. `Timer` delegates to it and system monitoring code uses monotonic time for refresh intervals.

Risks: `now()` is explicitly unsuitable for durations because wall time can move. `formatTime` uses the formatter default timezone rather than forcing UTC; `getUtcTime` only affects returned current time. `monotonicNow` may be negative and callers must handle arbitrary origin values.

Test signals: tests should verify monotonic wrapper use for intervals, formatting pattern stability, and timezone expectations.
