# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterUserProtocol.java

## Purpose
`RouterUserProtocol` implements user/group refresh and group lookup protocols for the Router. It either handles the request locally when no namespaces are available or forwards it to all resolved Namenodes.

## Important APIs and Types
It implements `RefreshUserMappingsProtocol` and `GetUserMappingsProtocol` with `refreshUserToGroupsMappings`, `refreshSuperUserGroupsConfiguration`, and `getGroupsForUser`. It uses `Groups`, `ProxyUsers`, `UserGroupInformation`, `ActiveNamenodeResolver`, `FederationNamespaceInfo`, `RemoteMethod`, and `RouterRpcServer.merge`.

## Control Flow
All methods call `rpcServer.checkOperation(OperationCategory.UNCHECKED)`. Refresh calls discover namespaces; if none exist, they refresh local Router caches, otherwise they invoke the corresponding protocol method concurrently across namespaces. `getGroupsForUser` falls back to local UGI group resolution when no namespace exists, otherwise it concurrently queries all namespaces and merges the returned string arrays into a unique array.

## State and Persistence
The module holds only server/client/resolver references. Refresh operations mutate local security caches or remote Namenode caches, not durable application data.

## Dependencies and Integration Points
It is exposed through `RouterRpcServer` protobuf protocol registration and selected as the user protocol module in sync mode. Async mode uses `RouterAsyncUserProtocol`.

## Risks
Concurrent refresh requires all target Namenodes to be reachable unless lower layers relax failures. Merging group arrays loses namespace provenance and ordering may depend on map iteration. Local fallback behavior when namespace discovery is empty must match admin expectations.

## Test Signals
Tests should cover local fallback with no namespaces, concurrent remote refresh, group merging/deduplication, and exception behavior when one namespace fails.
