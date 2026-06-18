<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java

## Purpose
`EnumCounters` stores one long counter per enum constant, indexed by ordinal, with arithmetic and aggregate helpers.

## APIs and Types
Constructors accept an enum class with optional default value. Public methods include `get`, `asArray`, `negation`, `set`, `reset`, `add`, `subtract`, `sum`, `deepCopyEnumCounter`, `allLessOrEqual`, `anyGreaterOrEqual`, plus equality, hash, and string formatting.

## Control Flow
Construction validates `enumClass.getEnumConstants()` and allocates a long array. Operations directly index by `e.ordinal()` or iterate over the full counter array. Copy/arithmetic against another `EnumCounters<E>` assumes the same enum shape; `equals` additionally checks enum class identity.

## State and Persistence
State is enum class and long array. `asArray` returns a cloned array, so direct external mutation is avoided. No persistence or synchronization.

## Dependencies and Integration
It depends on Hadoop `Preconditions` and Apache Commons `ArrayUtils`. `ConstEnumCounters` subclasses it for immutable default vectors.

## Risks
Methods accepting another `EnumCounters<E>` do not runtime-check enum class before indexing, so raw-type misuse can corrupt logic or throw length issues. Counter overflow is unchecked. `toString` assumes at least one enum constant; empty enums would cause substring failure.

## Test Signals
Tests should cover default and custom initialization, ordinal mapping, array copy isolation, arithmetic operations, equality across same/different enum classes, deep copy independence, threshold helpers, overflow behavior if relevant, and empty enum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/EnumCounters.java -->
