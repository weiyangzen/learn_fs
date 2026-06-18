# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableComparable.java

## Purpose

`WritableComparable.java` combines Hadoop's `Writable` binary serialization contract with Java's `Comparable` ordering contract. It is the standard interface for Hadoop keys.

## Important APIs, types, and functions

- `WritableComparable<T>` extends `Writable` and `Comparable<T>`.
- It declares no additional methods.
- Javadoc emphasizes stable `hashCode()` across JVM instances because Hadoop partitioning often uses key hashes.

## Control flow

There is no local control flow. Implementations must supply serialization plus `compareTo()`.

## State and persistence behavior

State is implementation-specific. Persisted bytes must be consistent with comparison semantics where raw comparators or sorting are involved.

## Dependencies and integration points

The interface integrates with `WritableComparator`, `RawComparator`, MapReduce sort/shuffle, partitioning, `SequenceFile.Sorter`, and collection-like writable containers.

## Risks and edge cases

- Bad `compareTo()`/`equals()`/`hashCode()` consistency can corrupt sort, grouping, partitioning, or Java collection behavior.
- The interface cannot enforce deterministic hash codes; implementers must avoid identity-based defaults.
- Mutable keys can break sorted collections or partitioning if mutated after use.

## Test signals

Implementation tests should verify serialization round-trip, comparison transitivity, equality/hash consistency, deterministic hash across instances, and raw comparator equivalence when a raw comparator exists.
