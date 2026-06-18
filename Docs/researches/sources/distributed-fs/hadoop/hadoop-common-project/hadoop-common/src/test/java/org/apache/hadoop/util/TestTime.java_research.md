# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestTime.java

Purpose: Minimal JUnit coverage for Hadoop `Time.formatTime(long)`. It asserts that the helper uses the same date/time rendering as the expected Java `SimpleDateFormat` pattern.

Important APIs/types/functions: The test owns a `ThreadLocal<SimpleDateFormat>` initialized with pattern `yyyy-MM-dd HH:mm:ss,SSSZ`. `testFormatTime()` obtains `Time.now()` and compares `Time.formatTime(time)` with the formatter output for the same millisecond timestamp.

Control flow: There is one direct assertion and no setup/teardown. The `ThreadLocal` avoids sharing a non-thread-safe `SimpleDateFormat` if the test runner executes tests in parallel or the helper is reused.

State and persistence behavior: No persistent state beyond the thread-local formatter. The result depends on the JVM default timezone and locale, but both sides of the assertion run in the same process, so the test checks formatting contract rather than a fixed UTC string.

Dependencies and integration points: Depends on Hadoop `Time`, Java text formatting, and JUnit 5. This guards log/timestamp presentation utilities used across Hadoop common code.

Risks: Because it compares against local default timezone behavior, it will not catch accidental changes that still match a formatter created with the same default environment. It also does not test monotonic time helpers or duration formatting.

Test signals: A passing assertion confirms the visible timestamp pattern and millisecond input handling remain consistent with the documented format.
