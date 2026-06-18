# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/TestMeanStatistic.java

Purpose: Tests `MeanStatistic` value semantics, empty handling, mutation, addition, copying, JSON serialization, and robustness against malicious negative sample counts.

Important APIs/types/functions: `MeanStatistic` constructors, `isEmpty`, `mean`, `copy`, `add`, `addSample`, `setSamples`, `setSum`, `toString`, `equals`, and `JsonSerialization<MeanStatistic>` via `serializer()`.

Control flow: Fixture fields define empty, one-sample sum-ten, and ten-sample sum-ten stats. Tests assert empty equality normalizes sample count zero regardless of sum, nonempty equality/mean, negative samples converting to empty, copy equality without identity, adding nonempty/empty stats, adding samples, zero-value samples, setters, negative sample setter emptying, JSON round trip excluding derived fields, and deserializing malicious JSON with negative samples to empty.

State/persistence: In-memory value objects; JSON strings are local variables.

Dependencies/integration: Protects statistics mean objects used by `IOStatisticsSnapshot` and store mean maps, including JSON wire form compatibility.

Risks: Floating-point comparisons are exact for simple values. Empty equality ignores sum, which is intentional but important for callers. Malicious JSON test covers negative samples but not overflow sums.

Test signals: Equality/non-identity assertions, exact means, string fragments, JSON field absence, JSON round-trip equality, and malicious negative sample normalization.
