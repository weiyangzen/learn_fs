<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java

Purpose: MapFile variant with an auxiliary dynamic Bloom filter to avoid expensive lookups for keys that are definitely absent.

Important APIs, types, and functions: `delete()` removes data, index, bloom file, and directory. `Writer` initializes a `DynamicBloomFilter` from configuration, adds each appended serialized key to the filter, and writes `bloom` on close. `Reader` loads the bloom file if present, `probablyHasKey()` tests membership, `get()` skips `MapFile.get()` when membership is false, and `getBloomFilter()` exposes the filter.

Control flow: writes go to the normal MapFile plus in-memory bloom filter; close persists the filter. Reads attempt to load the filter and fall back to normal MapFile behavior if it is unavailable.

State and persistence: writer stores filter parameters, reusable buffers, filesystem and directory. reader stores loaded filter and reusable key serialization buffers. Persistent state is a MapFile directory plus a `bloom` file.

Dependencies and integration points: depends on `MapFile`, `SequenceFile`, Hadoop `FileSystem`, compression codecs, `DynamicBloomFilter`, `Key`, and hash configuration.

Risks and test signals: Bloom filters can have false positives but not false negatives if key serialization is identical. Missing/corrupt bloom files degrade to full MapFile lookup. Tests should cover bloom creation, absent-key short circuit, fallback on missing bloom, compression options, delete cleanup, and configuration of size/error rate/hash type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BloomMapFile.java -->
