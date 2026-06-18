<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java

## Purpose
Tests `ObjectWritable` support for protocol buffer messages.

## Important APIs, Types, and Functions
Uses Hadoop shaded/thirdparty protobuf `DescriptorProtos.EnumValueDescriptorProto`, protobuf `Message`, `ObjectWritable.writeObject`, `ObjectWritable.readObject`, `DataOutputBuffer`, `DataInputBuffer`, and `Configuration`. Three tests call `doTest()` with 1, 2, and 3 protos.

## Control Flow and State
`doTest(numProtos)` builds `numProtos` enum-value descriptor messages named `testN` with number `N`, writes them to one buffer with declared protobuf class, resets an input buffer, reads them back in order, and asserts protobuf equality.

## Dependencies and Integration Points
Validates `ObjectWritable` special handling of protobuf messages used in Hadoop RPC/protocol surfaces. Depends on thirdparty protobuf shading.

## Risks and Test Signals
Risks include class name preservation, parser lookup for protobuf classes, and multiple-message stream boundaries. Signals are equality for one and multiple consecutive protobuf messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestObjectWritableProtos.java -->
