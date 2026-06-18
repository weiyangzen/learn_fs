# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VIntWritable.java

## Purpose

`VIntWritable.java` is a mutable `WritableComparable` wrapper for an `int` serialized with Hadoop's zero-compressed variable-length integer encoding.

## Important APIs, types, and functions

- Constructors create empty or initialized wrappers.
- `set(int)` and `get()` mutate and read the primitive.
- `readFields()` delegates to `WritableUtils.readVInt()`.
- `write()` delegates to `WritableUtils.writeVInt()`.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.

## Control flow

All serialization logic is delegated to `WritableUtils`; object comparison is direct integer comparison with explicit ternary return values.

## State and persistence behavior

The only mutable state is `private int value`. Persisted size ranges from one to five bytes depending on value magnitude and sign. Hash code is the integer value itself, stable across JVMs.

## Dependencies and integration points

The class depends on `WritableComparable` and `WritableUtils`. Unlike several fixed-width writables, it does not register a custom raw comparator in this file, so generic comparator paths may deserialize objects unless another comparator is supplied.

## Risks and edge cases

- Variable-length encoding does not preserve numeric ordering lexicographically, so raw byte comparison would be wrong unless decoded.
- Mutability creates the usual key-in-collection risk.
- Javadoc says one to five bytes, which is correct for int values through `WritableUtils.writeVLong()`.

## Test signals

Tests should cover round-trips for `Integer.MIN_VALUE`, negative threshold values, `-112`, `-111`, `0`, `127`, `128`, and `Integer.MAX_VALUE`, plus equality, hash, comparison, and encoded size expectations.
