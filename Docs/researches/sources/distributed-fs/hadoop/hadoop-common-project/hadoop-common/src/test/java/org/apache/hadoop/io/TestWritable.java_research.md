<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java

Purpose: Unit coverage for Hadoop `Writable`, primitive writable wrappers, comparator lookup/configuration, and `WritableComparator.newKey()` configuration propagation.

Important APIs/types/functions: `SimpleWritable` persists a random `int state` through `write` and `readFields`. `SimpleWritableComparable` adds `WritableComparable` and `Configurable` behavior. Static `testWritable(Writable before, Configuration conf)` serializes via `DataOutputBuffer`, deserializes through `ReflectionUtils.newInstance`, and asserts equality. `FrobComparator` and `Frob` register a custom comparator through `WritableComparator.define`.

Control flow: primitive and custom Writable tests call `testWritable`. Comparator tests fetch comparators with and without explicit `Configuration`, assert registered comparator type, and assert that configuration is retained or replaced as expected. `testShortWritableComparator` compares positive, negative, and equal cases both directly and through `WritableComparator.get`. `testConfigurableWritableComparator` gets a comparator for a configurable key, calls `newKey`, and checks the key inherits the comparator configuration.

State and persistence behavior: state is serialized in memory only. Comparator definitions are global static registry state inside `WritableComparator`; this file deliberately exercises cached comparator configuration behavior.

Dependencies and integration points: integrates with `DataInputBuffer`, `DataOutputBuffer`, `ReflectionUtils`, `WritableComparator`, `ByteWritable`, `ShortWritable`, `DoubleWritable`, `Configuration`, and the `Configurable` interface.

Risks and edge cases: static comparator cache state may interact with other tests for the same key class, though `Frob` is local. The method `testGetComparator` lacks `@Test`, so it may not run unless called elsewhere. `testShortWritable` constructs `ShortWritable((byte)256)`, which truncates to zero and may be intentional legacy behavior but is not a strong boundary check for `short`.

Test signals: confirms Writable round trips, short comparator semantics, comparator configuration caching/replacement, and propagation of config into configurable key instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java -->
