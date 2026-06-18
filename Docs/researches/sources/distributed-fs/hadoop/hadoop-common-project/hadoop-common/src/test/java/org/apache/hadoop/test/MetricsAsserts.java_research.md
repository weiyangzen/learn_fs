# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MetricsAsserts.java

Purpose: Mockito-based helpers for Hadoop metrics source tests.

Important APIs/types/functions: `mockMetricsSystem`, `mockMetricsRecordBuilder`, `getMetrics`, matchers `eqName` and `anyInfo`, gauge/counter/tag getters and assertions for int/long/double/float/string, greater-than assertions, `assertQuantileGauges`, and `assertInverseQuantileGauges`.

Control flow: `mockMetricsSystem` installs a mocked `MetricsSystem` into `DefaultMetricsSystem`. `mockMetricsRecordBuilder` creates a builder mock that logs method calls and returns itself for fluent methods or its parent collector. `getMetrics` invokes a source against the mock collector. Getter methods capture values using `ArgumentCaptor` and assert exactly one captured metric where appropriate.

State and persistence behavior: mutates global `DefaultMetricsSystem` instance when mocking. Captured metric state is Mockito in-memory state. No durable state.

Dependencies and integration points: integrates Hadoop metrics2 APIs, mutable quantiles, Interns `info`, Mockito matchers/captors, and JUnit assertions.

Risks and test signals: global metrics-system replacement can leak if tests do not isolate it. Signals are strong for exact metric names because matchers compare `MetricsInfo.name()` and require one captured value for most getters.
