# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolTranslatorPB.java

Purpose: client-side Router translator for the security refresh-user-mappings protocol, adding async IPC paths for administrative refresh operations.

Important APIs and types: extends `RefreshUserMappingsProtocolClientSideTranslatorPB`, stores `RefreshUserMappingsProtocolPB rpcProxy`, and overrides `refreshUserToGroupsMappings()` and `refreshSuperUserGroupsConfiguration()`.

Control flow: sync mode delegates to the standard translator. Async mode builds the corresponding empty request proto and uses `asyncIpcClient` to invoke the PB proxy; completion returns `null` for both void operations.

State and persistence: no local state beyond the proxy. Refresh effects happen in the remote Router service's caches.

Dependencies and integration points: pairs with the Router server-side refresh translator and Hadoop security protocol PB classes. It is used by admin clients when asynchronous IPC is enabled.

Risks: callers expect refresh completion or failure, so async error propagation must match the synchronous translator. Tests should verify both methods complete successfully and preserve exception behavior in async mode.
