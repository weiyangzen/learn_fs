## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRate.java

Purpose: Convenience mutable rate metric implemented as a `MutableStat` for operation latency/throughput samples.

Important APIs/types/functions: Constructors derive sample and value labels, and inherited `add`/`snapshot` record counts and average time or extended stats.

Control flow: Calls flow through `MutableStat`; adding a sample marks changed and snapshot emits count/average and optional extended gauges.

State and persistence: Inherited interval and previous sample statistics, min/max, total sample count, and changed flag.

Dependencies/integration: Created by registry `newRate`, `MutableRates`, sink adapter latency, and aggregated rates.

Risks/test signals: Name-derived metric info affects external schemas. Tests should cover extended flag and timestamp update inherited from `MutableStat`.
