# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolServerSideTranslatorPB.java

## Purpose

This server-side translator adapts protobuf refresh-user-mappings RPC calls to a Java `RefreshUserMappingsProtocol` implementation.

## Important APIs, Types, and Functions

It implements `RefreshUserMappingsProtocolPB`, stores an `impl`, and exposes `refreshUserToGroupsMappings` and `refreshSuperUserGroupsConfiguration`.

## Control Flow

Each RPC method invokes the matching Java implementation method, catches `IOException`, wraps it in `ServiceException`, and returns a cached empty response proto.

## State and Persistence Behavior

State is the implementation reference and static empty responses. Actual mapping state is owned by the implementation.

## Dependencies and Integration Points

It depends on generated refresh-user-mappings protobuf types, `ServiceException`, and the Java refresh protocol. Hadoop daemons use it when exposing admin refresh RPCs.

## Risks and Edge Cases

Request messages are ignored; adding request fields would require protocol changes. Implementation errors are all represented as protobuf service failures.

## Test Signals

Tests should verify both delegate calls, response construction, and IOException-to-ServiceException conversion.
