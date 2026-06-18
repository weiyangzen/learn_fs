# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshUserMappingsProtocol.proto

## Purpose
`RefreshUserMappingsProtocol.proto` defines RPCs for refreshing cached user-to-group mappings and superuser proxy group configuration in Hadoop daemons.

## Important APIs, types, and functions
Messages are empty request/response pairs for `RefreshUserToGroupsMappings` and `RefreshSuperUserGroupsConfiguration`. The service `RefreshUserMappingsProtocolService` exposes `refreshUserToGroupsMappings` and `refreshSuperUserGroupsConfiguration`.

## Control flow
Admin clients invoke the desired refresh method. The server invalidates or reloads its group mapping cache or proxy-user group configuration and returns an empty response on success. Errors are represented as RPC exceptions.

## State and persistence
The proto carries no data, but it triggers mutation of server-side security caches. Persistent definitions remain in external configuration or OS identity services.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.RefreshUserMappingsProtocolProtos` and integrates with `RefreshUserMappingsProtocol`, client/server PB translators, `Groups`, and proxy-user authorization code.

## Risks and test signals
Risks include unauthorized cache invalidation, stale mappings if refresh silently fails, race conditions with concurrent authorization checks, and ambiguity from empty success responses. Test signals include cache refresh tests, proxy-user configuration reload tests, RPC authorization checks, and concurrent lookup behavior during refresh.
