
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsJClassComparatorByteArrays.java

Purpose: Runs the byte-array TFile base suite with no compression and the custom `MyComparator` jclass comparator.

Important APIs and types: Extends `TestTFileByteArrays`, uses `Compression.Algorithm.NONE`, comparator string `jclass: org.apache.hadoop.io.file.tfile.MyComparator`, and expected block counts 24 and 24.

Control flow: `setUp()` configures inherited writer settings and calls the base setup. Inherited tests then exercise all byte-array sorted file, metadata, scanner, and negative behavior with a reflection-loaded comparator instead of direct memcmp.

State and persistence: Uses the inherited temp file named by subclass and deletes after each test.

Dependencies and integration points: Reuses the `MyComparator` class declared in `TestTFileJClassComparatorByteArrays.java`, so compilation/package visibility matter.

Risks: The comparator class lives in another test file; moving or renaming it breaks this test. No compression makes block sizing deterministic but still tied to payload sizes.

Test signals: Validates custom comparator behavior independent of compression.
