<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java

## Purpose
`Holder<T>` is a minimal mutable wrapper around a value, useful when callers need a replaceable reference in collections or closures.

## APIs and Types
It exposes public field `held`, constructor `Holder(T held)`, and `toString`.

## Control Flow
Construction assigns the field. `toString` delegates to `String.valueOf`, producing `"null"` for null values.

## State and Persistence
State is the public mutable field. No persistence, validation, or synchronization.

## Dependencies and Integration
It has no external dependencies. It is a small utility for avoiding repeated lookups or emulating pass-by-reference.

## Risks
Public mutability makes invariants caller-owned. It does not implement `equals`/`hashCode`, so holder identity is used in collections. Thread visibility is not guaranteed without external synchronization.

## Test Signals
Tests are minimal: construction, mutation, null `toString`, and identity equality expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Holder.java -->
