# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProgress.java

Purpose: verifies `Progress` clamps invalid or out-of-range progress values.

Important APIs and types: `Progress.set(float)` and `Progress.getProgress()`.

Control flow: the test sets `NaN`, negative infinity, and `-1` and expects reported progress `0`. It sets `1.1` and positive infinity and expects reported progress `1`.

State and persistence: state is the single in-memory progress float. No persistence or dependencies beyond JUnit.

Dependencies and integration points: progress values are surfaced by Hadoop task/reporting code, so normalization prevents invalid telemetry from propagating.

Risks: accepting NaN can poison downstream calculations; not clamping can render progress UI or scheduling math invalid. Test signals are exact floating-point equality with zero delta.
