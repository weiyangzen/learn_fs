# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Key.java

Purpose: `Key` is the WritableComparable key representation for Bloom filters, storing raw bytes plus a weight used by retouched filters.

Important APIs/types/functions: constructors set bytes with default weight `1.0` or explicit weight. `set`, `getBytes`, `getWeight`, `incrementWeight`, `equals`, `hashCode`, `write`, `readFields`, and `compareTo` implement state access, serialization, and ordering.

Control flow: `set` rejects null byte arrays and stores the reference directly. Comparison first orders by byte-array length, then byte values, then casts weight difference to `int`. Serialization writes byte length, bytes, and double weight.

State and persistence behavior: mutable byte-array reference and mutable weight. Writable state persists both.

Dependencies and integration points: implements Hadoop `WritableComparable` and is consumed by all Bloom filter implementations.

Risks: byte arrays are not defensively copied, so external mutation changes key identity/hash. `compareTo` casts double difference to int, so small weight differences under 1.0 compare as equal even when `hashCode` differs, potentially violating sorted collection expectations. `hashCode` XORs byte and weight hashes and is weak for collisions.

Test signals: tests should cover serialization, equality/hash consistency for exact weights, mutable array effects, comparison ordering, and fractional weight comparison behavior.
