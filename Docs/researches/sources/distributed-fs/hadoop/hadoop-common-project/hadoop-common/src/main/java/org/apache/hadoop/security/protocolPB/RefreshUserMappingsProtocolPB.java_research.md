# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/protocolPB/RefreshUserMappingsProtocolPB.java

## Purpose

`RefreshUserMappingsProtocolPB` is the protobuf IPC protocol interface for refreshing user/group and proxy-user mappings.

## Important APIs, Types, and Functions

It extends generated `RefreshUserMappingsProtocolService.BlockingInterface` and carries Kerberos and protocol metadata with protocol name `org.apache.hadoop.security.RefreshUserMappingsProtocol` and version `1`.

## Control Flow

No implementation exists in this interface; generated protobuf service methods are implemented by server-side translators.

## State and Persistence Behavior

The interface owns no state or persistence.

## Dependencies and Integration Points

It integrates generated protobuf services with Hadoop IPC registration and secure principal lookup.

## Risks and Edge Cases

Changing protocol name/version or Kerberos key metadata would break wire compatibility or secure RPC setup.

## Test Signals

Tests should cover protocol metadata, translator compatibility, and secure RPC registration.
