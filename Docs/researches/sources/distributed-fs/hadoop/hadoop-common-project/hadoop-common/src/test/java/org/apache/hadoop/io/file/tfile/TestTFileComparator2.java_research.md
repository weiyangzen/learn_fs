
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparator2.java

Purpose: Verifies TFile can use a Java class comparator for serialized `LongWritable` keys and preserve comparator-defined sorted order.

Important APIs and types: Uses comparator string `jclass:` plus `LongWritable.Comparator`, `TFile.Writer.prepareAppendKey()`, `prepareAppendValue()`, `LongWritable.write()`, `TFile.Reader.Scanner`, and `BytesWritable`.

Control flow: The test writes 10,000 entries with keys equal to `(i - NENTRY/2)^3`, which are sorted numerically by `LongWritable.Comparator`, and values `value-i`. It reads sequentially and asserts values appear in the original loop order.

State and persistence: Creates a gzip-compressed temp TFile and reads it back. The file is not explicitly deleted in this test.

Dependencies and integration points: Exercises jclass comparator loading and Writable binary comparator semantics inside TFile sorted writing.

Risks: Missing cleanup can leave temp files. The test validates values rather than decoded keys, so comparator order is inferred from successful write/read sequencing.

Test signals: Covers non-memcmp comparator integration with serialized Hadoop Writable keys.
