<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java

## Purpose
`ConstEnumCounters` is an immutable-flavored subclass of `EnumCounters` initialized to a constant value for every enum constant.

## APIs and Types
It extends `EnumCounters<E>`, defines runtime `ConstEnumException`, and overrides all mutating methods (`negation`, `set`, `reset`, `add`, `subtract`) as final methods throwing a shared exception.

## Control Flow
Construction calls the superclass zero-initializing constructor, then a private `forceReset` calls `super.reset(defaultVal)` before mutation is disabled through overrides.

## State and Persistence
State is inherited counter array. There is no persistence. The object is not strictly immutable against inherited methods not overridden in the future or reflection, but public current mutators are blocked.

## Dependencies and Integration
It depends on `EnumCounters` and is useful where a constant all-enum counter vector should be shared without accidental mutation.

## Risks
The shared exception instance has one creation stack trace, which may reduce diagnostic detail. Subclass immutability depends on keeping overrides aligned with superclass mutators. The inherited `asArray` returns a copy, which is safe.

## Test Signals
Tests should verify default values, every mutator throws, read methods still work, equality/hash/toString inherited behavior, and that future superclass mutators are added to this subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/ConstEnumCounters.java -->
