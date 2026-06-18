# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshAuthorizationPolicyProtocolServerSideTranslatorPB.java

## Purpose

This server-side translator adapts protobuf refresh-authorization RPC calls to a Java `RefreshAuthorizationPolicyProtocol` implementation.

## Important APIs, Types, and Functions

It implements `RefreshAuthorizationPolicyProtocolPB`, stores an `impl`, and exposes `refreshServiceAcl(RpcController, RefreshServiceAclRequestProto)`.

## Control Flow

The RPC method calls `impl.refreshServiceAcl()`, wraps any `IOException` in `ServiceException`, and returns a cached empty response proto.

## State and Persistence Behavior

State is only the delegated implementation and static response instance. Persistence is handled by the implementation being refreshed.

## Dependencies and Integration Points

It depends on generated protobuf request/response types, `ServiceException`, and the Java refresh protocol. Hadoop RPC servers use it to expose refresh operations.

## Risks and Edge Cases

All implementation failures are collapsed into `ServiceException`. The request payload is ignored, so future request fields would require protocol evolution.

## Test Signals

Tests should verify delegate invocation, empty response return, and IOException-to-ServiceException conversion.
