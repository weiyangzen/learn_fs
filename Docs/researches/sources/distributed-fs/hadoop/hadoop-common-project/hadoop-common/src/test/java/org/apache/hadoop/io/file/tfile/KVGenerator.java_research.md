
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KVGenerator.java

Purpose: Test utility that generates pseudo-random `BytesWritable` key/value pairs for TFile seek and benchmark workloads.

Important APIs and types: Constructor accepts `Random`, sorted flag, key/value/word-length `RandomDistribution.DiscreteRNG` instances, and dictionary size. Public `next(BytesWritable key, BytesWritable value, boolean dupKey)` emits a key and value.

Control flow: The constructor builds a random dictionary and initializes `lastKey`. `fillKey()` chooses a key length, fills bytes after a 4-byte prefix with dictionary words, increments the prefix if sorted ordering would otherwise regress, copies the prefix, and stores `lastKey`. `fillValue()` fills values similarly. `dupKey` reuses the previous key.

State and persistence: Maintains random dictionary, prefix bytes, and last key across calls. No file persistence.

Dependencies and integration points: Used by TFile seek/performance tests with `RandomDistribution` and Hadoop `BytesWritable`.

Risks: Prefix overflow throws at runtime. Sorted ordering depends on comparing bytes after the fixed prefix only.

Test signals: Supports realistic repeated-word key/value generation for compression and seek behavior.
