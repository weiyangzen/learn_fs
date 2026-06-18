# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RemoteException.java

## Purpose
`RemoteException` wraps an exception thrown by the remote RPC server, preserving the remote class name, message, and optional protobuf RPC error code for client-side unwrapping.

## Important APIs, Types, and Functions
Constructors accept class name, message, and optional `RpcErrorCodeProto`. `getClassName` and `getErrorCode` expose metadata. `unwrapRemoteException` variants instantiate matching `IOException` classes through a string constructor and set this wrapper as cause. `valueOf(Attributes)` builds from XML attributes.

## Control Flow
Clients catch `RemoteException`, optionally match known classes, and unwrap. Reflection failures return the wrapper unchanged. Error code `-1` represents unspecified or newer protobuf errors.

## State and Persistence Behavior
State is exception metadata only. It may be serialized through normal exception/RPC mechanisms but persists nothing itself.

## Dependencies and Integration Points
It integrates with RPC response headers, protobuf engines, SASL/RPC tests, and service clients that unwrap server exceptions.

## Risks and Test Signals
Risks include class-name compatibility, missing string constructors, reflection access, and unknown error-code numbers. Tests should cover unwrap success/failure, lookup filtering, XML construction, and `ServiceException` cause chains.
