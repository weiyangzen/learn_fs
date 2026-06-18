# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VLongWritable.java

## Purpose

`VLongWritable.java` is a mutable `WritableComparable` wrapper for a `long` serialized with Hadoop's zero-compressed variable-length integer encoding.

## Important APIs, types, and functions

- Constructors create empty or initialized wrappers.
- `set(long)` and `get()` mutate and read the primitive.
- `readFields()` delegates to `WritableUtils.readVLong()`.
- `write()` delegates to `WritableUtils.writeVLong()`.
- `equals()`, `hashCode()`, `compareTo()`, and `toString()` provide value semantics.

## Control flow

Serialization and deserialization are delegated to `WritableUtils`; comparison reads the two long fields and returns `-1`, `0`, or `1`.

## State and persistence behavior

State is a single mutable `long`. Persisted size ranges from one to nine bytes. `hashCode()` truncates to the low 32 bits, which is stable but collision-prone for values that differ only in high bits.

## Dependencies and integration points

The class depends on `WritableComparable` and `WritableUtils`. It is useful where compact long storage matters, such as counters, offsets, or sequence metadata.

## Risks and edge cases

- The class javadoc says values take between one and five bytes, which is incorrect for long values; `WritableUtils.writeVLong()` can emit up to nine bytes.
- No raw comparator is registered here; bytewise comparison of encoded vlongs would not match numeric ordering.
- Hash truncation is compatible with old Hadoop behavior but weak for partitioning high-bit-heavy values.

## Test signals

Tests should cover round-trips and encoded sizes for `Long.MIN_VALUE`, `Long.MAX_VALUE`, `-113`, `-112`, `127`, `128`, large high-bit values, comparison ordering, and hash collision expectations.
