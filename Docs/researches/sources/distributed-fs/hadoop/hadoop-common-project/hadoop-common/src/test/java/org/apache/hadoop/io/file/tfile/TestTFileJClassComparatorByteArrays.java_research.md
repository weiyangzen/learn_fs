
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileJClassComparatorByteArrays.java

Purpose: Runs the byte-array TFile base suite with gzip compression and a custom Java class comparator.

Important APIs and types: Extends `TestTFileByteArrays`, calls `init(GZ, "jclass: org.apache.hadoop.io.file.tfile.MyComparator")`, and defines package-local `MyComparator implements RawComparator<byte[]>, Serializable`.

Control flow: `setUp()` configures the inherited writer to use the custom comparator before delegating to the base setup. All test methods are inherited from `TestTFileByteArrays`. `MyComparator` delegates both raw and object comparisons to `WritableComparator.compareBytes()`.

State and persistence: Uses the inherited temp file lifecycle and compression/block-count settings.

Dependencies and integration points: Exercises TFile jclass comparator reflection against a comparator defined in the test source file.

Risks: The comparator string includes whitespace after `jclass:`, so parser trimming behavior is implicitly tested. The package-local comparator class is shared by none-codec jclass tests too.

Test signals: Confirms custom comparator loading works with the full byte-array behavior matrix.
