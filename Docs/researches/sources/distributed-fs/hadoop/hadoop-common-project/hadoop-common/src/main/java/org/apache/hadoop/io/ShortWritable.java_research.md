# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ShortWritable.java

## Purpose

`ShortWritable.java` is Hadoop's mutable `WritableComparable` wrapper for a Java `short`. It serializes as a fixed two-byte big-endian `DataOutput.writeShort()` value and supplies object and raw-byte comparison support.

## Important APIs, types, and functions

- `ShortWritable()` and `ShortWritable(short)` construct empty or initialized values.
- `set(short)` and `get()` mutate and read the wrapped primitive.
- `readFields(DataInput)` and `write(DataOutput)` implement fixed-width binary serialization.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.
- Nested `Comparator` extends `WritableComparator` and compares serialized shorts using `readUnsignedShort()` then casting to `short`.
- The static initializer registers the optimized comparator with `WritableComparator.define()`.

## Control flow

Serialization and deserialization are single primitive operations. Object comparison reads the two instance fields and returns `-1`, `0`, or `1`. Raw comparison decodes two bytes from each serialized key, casts them to signed shorts, and applies the same ordering without object allocation.

## State and persistence behavior

The only mutable state is `private short value`. Persisted form is exactly two bytes. The hash code is the signed short widened to `int`, so it is stable across JVMs.

## Dependencies and integration points

This class depends on the `WritableComparable` contract and `WritableComparator` utilities. It can be used as a MapReduce key/value and benefits from the registered raw comparator in sort paths.

## Risks and edge cases

- The raw comparator must preserve signed short ordering; the implementation reads unsigned bytes then casts to `short`, which is intentional.
- There is no null handling in `compareTo()`.
- Mutability means instances used as keys in Java collections can break collection invariants if mutated after insertion.

## Test signals

Tests should round-trip boundary values (`Short.MIN_VALUE`, `-1`, `0`, `1`, `Short.MAX_VALUE`), compare object and raw comparator ordering, verify hash/equality, and confirm serialized length is two bytes.
