<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java

## Purpose
Broad regression suite for `SequenceFile`: write/read, raw APIs, compression modes, sorting, merging, metadata, close/error behavior, writer creation semantics, serialization availability, stream capabilities, writable-name aliases, and a manual CLI harness.

## Important APIs, Types, and Functions
Uses `SequenceFile.createWriter`, `SequenceFile.Reader`, `SequenceFile.Sorter`, `SequenceFile.Metadata`, `CompressionType.NONE/RECORD/BLOCK`, `DefaultCodec`, `RandomDatum`, `WritableComparator`, `StreamCapabilities.HSYNC/HFLUSH`, `WritableName`, custom `Serialization`, `Serializer`, and `Deserializer`. Helpers `writeTest`, `readTest`, `sortTest`, `checkSort`, `mergeTest`, `newSorter`, `readMetadata`, `writeMetadataTest`, and `sortMetadataTest` implement repeated file-format workflows.

## Control Flow and State
`testZlibSequenceFile()` runs a full compressed sequence-file workflow with random seed, writing 10k records in no, record, and block compression, then reading, sorting, checking sort order, and merging in fast and normal modes. `readTest()` alternates raw and object APIs. Metadata tests write/read metadata under all compression modes and sort with metadata. Close tests verify double close does not corrupt codec-pool reuse and erroneous/zero-length readers close streams and throw EOF. Creation tests cover existing files, recursive parent creation, and using the supplied filesystem. Serialization tests assert missing serializer/deserializer errors, hflush/hsync capabilities on raw local FS, and aliasing a serialized class name to another compatible type. The `main` method parses CLI options for manual create/read/sort/merge checks.

## Dependencies and Integration Points
Integrates local/raw filesystems, compression codecs, codec pool behavior, Hadoop serialization framework, Avro reflect serialization as a negative configuration, writable name registry, and sequence-file sort/merge internals. This is a central persistence-format compatibility suite.

## Risks and Test Signals
Risks include long runtime and random seed reproducibility, unannotated `testSorterProperties()` not running as a JUnit test, filesystem temp cleanup, global `WritableName` alias side effects, and exact error-message coupling. Signals include record/value equality, raw API coverage, sorted TreeMap comparison, metadata equality, codec-pool double-close safety, closed stream after constructor failure, EOF on zero-length input, explicit serializer error prefixes, nonzero file length after sync operations, and alias-based deserialization values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFile.java -->
