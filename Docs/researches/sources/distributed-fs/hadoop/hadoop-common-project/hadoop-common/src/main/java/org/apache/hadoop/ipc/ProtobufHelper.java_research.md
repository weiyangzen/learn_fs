# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufHelper.java

## Purpose
`ProtobufHelper` is a deprecated compatibility facade for protobuf-related IPC helpers. It delegates shaded protobuf operations to `ShadedProtobufHelper` while retaining legacy unshaded `com.google.protobuf.ServiceException` handling.

## Important APIs, Types, and Functions
`getRemoteException(ServiceException)` delegates to shaded helper. The overloaded deprecated unshaded version extracts an `IOException` cause or wraps the service exception. ByteString helpers and token conversion helpers (`tokenFromProto`, `protoFromToken`) also delegate.

## Control Flow
All modern paths are pass-through. Legacy exception extraction checks the cause for null and `IOException` type before returning or wrapping.

## State and Persistence Behavior
The class has no state. Token conversion creates protobuf representations of token fields but does not persist them.

## Dependencies and Integration Points
It depends on shaded protobuf helper APIs, Hadoop `Token`, `TokenProto`, and legacy protobuf classes. External applications may still call it, but Hadoop internals should not.

## Risks and Test Signals
The key risk is runtime dependency on unshaded protobuf 2.5 for deprecated APIs. Tests should cover shaded and unshaded service exceptions, empty byte arrays, fixed strings, and token round trips.
