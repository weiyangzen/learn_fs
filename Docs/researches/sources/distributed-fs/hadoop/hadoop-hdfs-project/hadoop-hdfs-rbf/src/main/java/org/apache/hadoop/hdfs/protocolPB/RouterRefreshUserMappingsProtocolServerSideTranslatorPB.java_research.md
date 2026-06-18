# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolServerSideTranslatorPB.java

Purpose: Router server-side protobuf adapter for `RefreshUserMappingsProtocol`, with async support for refreshing user-group and superuser group mappings.

Important APIs and types: extends `RefreshUserMappingsProtocolServerSideTranslatorPB`, stores `RouterRpcServer`, caches `isAsyncRpc`, and defines empty response protos for both refresh operations.

Control flow: sync mode delegates to the parent. Async mode schedules either `server.refreshUserToGroupsMappings()` or `server.refreshSuperUserGroupsConfiguration()` through `asyncRouterServer`, maps completion to the prebuilt empty response, and returns `null`.

State and persistence: no local persisted state. The operations refresh in-memory security/group mapping caches in the Router process.

Dependencies and integration points: integrates Router RPC refresh handling with Hadoop security protobuf protocol classes and the async Router server utility. It pairs with `RouterRefreshUserMappingsProtocolTranslatorPB`.

Risks: refresh calls are operationally sensitive because stale groups affect authorization. The implementation assumes the passed protocol implementation is a `RouterRpcServer`. Tests should cover both refresh methods in sync and async mode and confirm exceptions are surfaced to clients.
