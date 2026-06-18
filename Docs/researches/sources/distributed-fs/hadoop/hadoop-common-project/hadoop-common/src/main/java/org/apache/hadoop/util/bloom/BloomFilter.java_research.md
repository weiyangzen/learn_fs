# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/BloomFilter.java

Purpose: `BloomFilter` implements a classic mutable Bloom filter over a `BitSet`, providing probabilistic set membership with no false negatives before destructive operations such as `not`.

Important APIs/types/functions: constructors support Writable deserialization and explicit `vectorSize`, `nbHash`, and `hashType`. `add(Key)` sets all hashed positions. `membershipTest(Key)` checks all hashed positions. `and`, `or`, `xor`, and `not` mutate this filter. `getVectorSize`, `toString`, `write`, `readFields`, and private `getNBytes` provide introspection and serialization.

Control flow: add/test call `HashFunction.hash`, clear the hash function no-op, and iterate `nbHash` positions. Logical operations validate non-null compatible `BloomFilter` instances with matching vector size and hash count. Serialization writes the `Filter` header then packs bits into bytes using little bit order within each byte; deserialization reconstructs the `BitSet`.

State and persistence behavior: in-memory state is inherited filter dimensions/hash function plus a mutable `BitSet`. Persistent state is Hadoop `Writable` data: filter header plus packed bit vector.

Dependencies and integration points: extends `Filter`, uses `Key`, `HashFunction`, `BitSet`, and Hadoop Writable data streams. Public/stable for HDFS and MapReduce-style probabilistic filtering.

Risks: not thread-safe. Logical compatibility does not verify `hashType`, only vector size and hash count. `not` invalidates normal Bloom filter no-false-negative semantics. Serialization format must remain compatible with old `Filter` header behavior.

Test signals: tests should cover add/test, null key exceptions, logical operations compatibility failures, bit-level read/write round trips, and hash-type mismatch behavior.
