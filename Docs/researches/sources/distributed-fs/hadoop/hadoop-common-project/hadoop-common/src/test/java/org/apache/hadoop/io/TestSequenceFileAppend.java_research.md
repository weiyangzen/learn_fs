<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java

## Purpose
Tests append support for `SequenceFile` with Java serialization and compression compatibility checks.

## Important APIs, Types, and Functions
Uses static `Configuration` with `JavaSerialization`, raw local file system, `SequenceFile.createWriter`, `Writer.appendIfExists(true)`, `Writer.compression`, `Writer.metadata`, `SequenceFile.Reader`, `GzipCodec`, `DefaultCodec`, `JavaSerializationComparator`, and `SequenceFile.Sorter`. Helpers `verify2Values()` and `verifyAll4Values()` read object keys/values with `Reader.next((Object)null)` and `getCurrentValue`.

## Control Flow and State
Lifecycle opens a raw local FS once. `testAppend()` writes two Long/String records with metadata, appends two more, verifies metadata remains original despite mutated metadata object, and rejects mismatched compression options. Compression-specific tests repeat append for record, block, and none compression; native profile is assumed for gzip cases. `testAppendSort()` writes unsorted appended blocks, sorts the result, and verifies ordered values.

## Dependencies and Integration Points
Integrates sequence-file append header validation, compression codec compatibility, Java serialization, raw local FS append support, metadata persistence, and sorting of appended files.

## Risks and Test Signals
Risks include native gzip availability, reuse of the same filename in record/block compression tests, and exact compatibility rules for `NONE` with codec option ignored. Signals are two-record and four-record reads, metadata value immutability, expected `IllegalArgumentException` on mismatched compression, and sorted output verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileAppend.java -->
