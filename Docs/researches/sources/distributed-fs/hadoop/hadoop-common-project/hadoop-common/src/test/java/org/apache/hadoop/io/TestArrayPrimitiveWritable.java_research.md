<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java

## Purpose
Validates compact serialization of Java primitive arrays via `ArrayPrimitiveWritable` and `ObjectWritable`, including compatibility with older non-compact array encoding.

## Important APIs, Types, and Functions
Uses static primitive arrays for boolean, char, byte, short, int, long, float, and double. `DataOutputBuffer`/`DataInputBuffer` are reset per test. `testMany()` writes each array both through `ObjectWritable.writeObject(..., allowCompactArrays=true)` and direct `ArrayPrimitiveWritable.write`, then reads with `ObjectWritable.readObject` and `ArrayPrimitiveWritable.readFields`. `testObjectLabeling()` inspects serialized class labels using deprecated `UTF8.readString`. `testOldFormat()` writes through old `ObjectWritable.writeObject` and reads individual boxed elements.

## Control Flow and State
The test maintains a result array twice the primitive type count. It checks component types before deep value equality, then explicitly validates label names for internal compact arrays and direct `ArrayPrimitiveWritable` objects.

## Dependencies and Integration Points
Exercised APIs include `ObjectWritable`, `ArrayPrimitiveWritable.Internal`, deprecated `UTF8`, and primitive-array reflection. It protects wire compatibility for RPC/object serialization paths.

## Risks and Test Signals
Risk areas are class label compatibility, compact-array opt-in semantics, primitive component type preservation, and deprecated format support. Signals are exact labels, length fields, component types, and array value equality across all primitive categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestArrayPrimitiveWritable.java -->
