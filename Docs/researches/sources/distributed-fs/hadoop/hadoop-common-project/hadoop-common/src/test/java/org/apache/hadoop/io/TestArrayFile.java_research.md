<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java

## Purpose
Tests `ArrayFile`, a map-like file of indexed values backed by Hadoop `MapFile`/`SequenceFile` mechanics.

## Important APIs, Types, and Functions
Uses `ArrayFile.Writer`, `ArrayFile.Reader`, `MapFile.delete`, `RandomDatum`, `LongWritable`, `CompressionType.RECORD`, `Progressable`, and local/default `FileSystem`. Helpers `generate`, `writeTest`, and `readTest` create random values, write them with index interval 100, and read them forward/backward by numeric index.

## Control Flow and State
`testArrayFile()` writes 10,000 random records and validates indexed reads in both directions. `testEmptyFile()` writes no records and asserts index 0 returns null. `testArrayFileIteration()` writes ten long values, iterates with `next`, seeks to key 6, checks subsequent key/value 7, and asserts out-of-range seek false. The `main` method is a manual CLI harness for large create/check runs.

## Dependencies and Integration Points
Persists data under `GenericTestUtils` temp paths on local/default filesystems. It exercises `ArrayFile`'s use of `MapFile` index intervals and `SequenceFile` compression options.

## Risks and Test Signals
Risks include leftover temp data, filesystem selection differences, and broad `catch` blocks that hide root causes behind generic failures. Signals are exact random datum equality, null for empty/out-of-range access, stable iteration order, and seek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayFile.java -->
