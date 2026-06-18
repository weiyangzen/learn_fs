# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/CountingBloomFilter.java

Purpose: `CountingBloomFilter` implements a counting Bloom filter using 4-bit counters packed into `long` words, supporting approximate counts and deletion.

Important APIs/types/functions: `add(Key)` increments hashed buckets up to `BUCKET_MAX_VALUE` 15. `delete(Key)` verifies membership and decrements buckets between 1 and 14. `membershipTest`, `approximateCount`, `and`, `or`, `not`, `xor`, `toString`, `write`, and `readFields` implement filter behavior and serialization. `buckets2words` maps vector size to 64-bit storage count.

Control flow: each hashed position maps to `wordNum = h >> 4` and `bucketShift = (h & 0x0f) << 2`. Add saturates at 15. Delete first performs a probabilistic membership test and then decrements only non-saturated buckets. Approximate count returns the minimum counter across hashes.

State and persistence behavior: mutable `long[] buckets` plus inherited filter metadata. Writable output writes inherited header followed by all bucket words.

Dependencies and integration points: extends `Filter`, uses `Key` and Hadoop data streams. Suitable for Hadoop components needing approximate membership plus removal.

Risks: delete can create false negatives when membership was a false positive or counters are shared. Saturated buckets are never decremented, preserving overflow but skewing counts. Logical operations use bitwise AND/OR on packed counters, which is not the same as min/max counter algebra. `not` and `xor` are unsupported.

Test signals: tests should cover counter saturation, deletion of absent keys, approximate count bounds, serialization round trip, and unsupported operations.
