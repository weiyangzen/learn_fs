<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java

## Purpose
Tests `BloomMapFile`, a `MapFile` variant with bloom-filter membership checks. It covers membership accuracy, varying key sizes, delete/get operations, constructor variants, and reader behavior when bloom filter loading fails.

## Important APIs, Types, and Functions
Uses `BloomMapFile.Writer`, `BloomMapFile.Reader`, `MapFile.Writer` options, `MapFile.Reader.comparator`, `SequenceFile.CompressionType`, local filesystem paths, `IOUtils.cleanupWithLogger`, and a mocked `CompressionCodec`. `setUp()` deletes and recreates a temp root. `checkMembershipVaryingSizedKeys()` writes `Text` keys and checks reverse-order membership.

## Control Flow and State
`testMembershipTest()` writes even integer keys up to 1998 with bloom size 2048, then scans 0-1999 to assert zero false negatives and fewer than two false positives. Other tests write short key sets, delete files, mock path filesystem lookup failure to get null bloom filter, verify `get` returns values for present keys and null for absent keys, and instantiate many deprecated/current writer constructors.

## Dependencies and Integration Points
Integrates MapFile storage, bloom filter side data, Hadoop local filesystem, Mockito spies, and compression option plumbing. It shares temp path naming with `TestMapFile`.

## Risks and Test Signals
Bloom filters are probabilistic, so the false-positive threshold is a statistical test. Varying-sized keys guard serialization boundaries. Constructor tests mostly assert non-null and may miss deeper compressed-stream behavior because the codec returns mocks/nulls. Signals include no false negatives, bounded false positives, null fallback on bloom filter IO failure, and expected get/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBloomMapFile.java -->
