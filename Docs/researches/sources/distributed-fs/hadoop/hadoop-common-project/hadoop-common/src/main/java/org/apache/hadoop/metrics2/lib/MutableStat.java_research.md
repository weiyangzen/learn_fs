## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableStat.java

Purpose: Mutable statistic metric for counts, averages, and optional extended min/max/stdev values.

Important APIs/types/functions: Constructors derive metric infos; `setExtended`, `setUpdateTimeStamp`, `add(value)`, `add(numSamples,sum)`, `snapshot`, `lastStat`, `resetMinMax`, and `getSnapshotTimeStamp` expose behavior.

Control flow: Adds update interval stats and min/max, marking changed. Snapshot accumulates total samples, emits counter and average, optionally emits stdev, interval/all-time min/max, and interval count, then copies interval stats to previous and resets them when changed.

State and persistence: Maintains interval and previous `SampleStat`, all-time min/max, total sample count, snapshot timestamp, extended flag, update timestamp flag, and changed flag.

Dependencies/integration: Base for `MutableRate`, used by metrics system snapshot/publish stats and many registries.

Risks/test signals: Aggregated `add(numSamples,sum)` can have variance limitations. Tests should cover no-sample snapshots, extended fields, min/max reset, timestamp updates, and changed semantics.
