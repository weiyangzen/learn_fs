<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java

## Purpose
Focused test for `SequenceFile` with Java serialization of non-Writable key/value classes.

## Important APIs, Types, and Functions
Uses `Configuration` key `io.serializations=JavaSerialization`, local `FileSystem`, `SequenceFile.createWriter(fs, conf, file, Long.class, String.class)`, and legacy `SequenceFile.Reader`.

## Control Flow and State
Each test setup creates fresh configuration and local filesystem; teardown closes it. The test deletes any existing temp file, writes two Long/String pairs, closes, reads keys and current values through object APIs, asserts both values in order, and asserts EOF via null key.

## Dependencies and Integration Points
Validates `SequenceFile` integration with Hadoop's Java serialization plugin rather than the default writable serializer.

## Risks and Test Signals
Risks are serializer configuration drift and temp file reuse. Signals are exact object key/value equality and null at end of file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSequenceFileSerialization.java -->
