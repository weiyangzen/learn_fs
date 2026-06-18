<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java

## Purpose
`EnumDoubles` is the double-valued counterpart to `EnumCounters`, storing one double per enum constant by ordinal.

## APIs and Types
Constructor accepts enum class. Public final operations include `get`, `negation`, `set`, `reset`, `add`, `subtract`, plus equality, hash, and string formatting.

## Control Flow
Operations index directly by enum ordinal or iterate over the double array. Equality requires the same enum class and `Arrays.equals` over double values.

## State and Persistence
State is enum class plus double array. No persistence and no synchronization. There is no method exposing the backing array.

## Dependencies and Integration
It depends on Hadoop `Preconditions` and Java `Arrays`. It is used where enum-indexed floating point metrics or ratios are more suitable than integer counters.

## Risks
Floating point special cases follow Java array equality semantics, including NaN and signed zero behavior. Methods accepting another `EnumDoubles<E>` trust generic type correctness. `toString` assumes at least one enum constant.

## Test Signals
Tests should cover ordinal mapping, arithmetic, reset/negation, equality for NaN and signed zero if important, same versus different enum classes, and empty enum formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumDoubles.java -->
