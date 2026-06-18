# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolClientSideTranslatorPB.java

## Purpose

This client-side translator adapts the Java `RefreshAuthorizationPolicyProtocol` interface to the protobuf-based Hadoop IPC stub.

## Important APIs, Types, and Functions

It implements `ProtocolMetaInterface`, `RefreshAuthorizationPolicyProtocol`, and `Closeable`. Key methods are the constructor taking `RefreshAuthorizationPolicyProtocolPB`, `refreshServiceAcl`, `isMethodSupported`, and `close`.

## Control Flow

`refreshServiceAcl` sends a cached empty `RefreshServiceAclRequestProto` through `rpcProxy.refreshServiceAcl` using a null controller and Hadoop's shaded protobuf IPC helper. `isMethodSupported` delegates to `RpcClientUtil`; `close` stops the proxy.

## State and Persistence Behavior

State is only the RPC proxy reference and static empty request object. No persistence exists.

## Dependencies and Integration Points

It depends on Hadoop IPC `RPC`, `RpcClientUtil`, protobuf request types, and the PB protocol interface. It is used by admin clients invoking authorization-policy refresh.

## Risks and Edge Cases

The translator has no retry logic beyond the RPC layer. Failure conversion relies on `ShadedProtobufHelper.ipc`. Callers must close it to stop the proxy.

## Test Signals

Tests should verify one RPC call is issued, IOException propagation, method support lookup arguments, and `close` stopping the proxy.
