# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/HashFunction.java

Purpose: `HashFunction` adapts a Hadoop `Hash` implementation into `k` bounded Bloom filter positions.

Important APIs/types/functions: constructor validates positive `maxValue` and `nbHash`, resolves `Hash.getInstance(hashType)`, and rejects unknown hash types. `hash(Key)` returns an `int[]` of positions. `clear()` is a no-op retained for API symmetry.

Control flow: hashing extracts key bytes, rejects null and empty byte arrays, then repeatedly hashes the same bytes using the previous hash as seed (`initval`) and maps each result with `Math.abs(initval % maxValue)`.

State and persistence behavior: stores immutable-ish max value, hash count, and hash implementation reference after construction. No external persistence.

Dependencies and integration points: depends on `Key` and `org.apache.hadoop.util.hash.Hash` implementations such as Jenkins/Murmur.

Risks: `Math.abs(Integer.MIN_VALUE)` remains negative, but because modulo by positive `maxValue` occurs first, only a remainder of `Integer.MIN_VALUE` would be problematic; Java remainder magnitude is below divisor, so this is effectively safe except theoretical edge cases when maxValue permits that remainder. Distribution depends on chained seeding. Not synchronized, but current `clear` is no-op and hash implementations must be safe for use pattern.

Test signals: tests should verify constructor validation, unknown hash rejection, empty key rejection, deterministic positions, and bounds for all returned positions.
