<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java

## Purpose
Tests `BooleanWritable` serialized comparator ordering and common object methods.

## Important APIs, Types, and Functions
`writeWritable()` serializes a `Writable` to `DataOutputBuffer`; `compare()` invokes `WritableComparator.compare` on buffer bytes. Tests use `WritableComparator.get(BooleanWritable.class)`, `equals`, `hashCode`, `compareTo`, and `toString`.

## Control Flow and State
The comparator test serializes true/false values and asserts equality against same buffers, true greater than false, and false less than true. Common-method tests create fresh instances for equality, hash, comparison, and string assertions.

## Dependencies and Integration Points
Validates Hadoop's raw comparator registry and object-level writable semantics used in sorted file formats and collections.

## Risks and Test Signals
Signals are exact comparator return signs, hash equality/inequality for true/false, and string `"true"`. Risks are minimal, though assertions use sign-specific values for raw comparator output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestBooleanWritable.java -->
