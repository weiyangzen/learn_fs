<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java

## Purpose
Tests `MapWritable` copy construction, nested maps, unknown class tracking, repeated deserialization safety, equality/hashCode, and string representation.

## Important APIs, Types, and Functions
Uses `MapWritable.put`, copy constructor, `entrySet`, `keySet`, `containsKey`, `get`, `getNewClasses`, `write`, `readFields`, `equals`, `hashCode`, and `toString`. It uses `Text`, `BytesWritable`, deprecated `UTF8`, `IntWritable`, and byte/data streams.

## Control Flow and State
The main test builds a map of text keys to bytes values, copies it, and compares all entries, then builds a map-of-maps and verifies nested copies. `testForeignClass()` verifies deprecated `UTF8` counts as one new class across copies. `testMultipleCallsToReadFieldsAreSafe()` serializes a one-entry map, mutates the instance, rereads the original bytes, and asserts stale entries were cleared. Equality tests compare same/different entries; `testToString()` checks `{5=value}`.

## Dependencies and Integration Points
Protects Hadoop's dynamic writable class-id mapping in map payloads, including nested maps and legacy `UTF8` support.

## Risks and Test Signals
Risks include class registry growth across copies, stale map entries after `readFields`, and equality/hash consistency. Signals are size equality, nested value compare, `getNewClasses()==1`, restored original map size, and deterministic string output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMapWritable.java -->
