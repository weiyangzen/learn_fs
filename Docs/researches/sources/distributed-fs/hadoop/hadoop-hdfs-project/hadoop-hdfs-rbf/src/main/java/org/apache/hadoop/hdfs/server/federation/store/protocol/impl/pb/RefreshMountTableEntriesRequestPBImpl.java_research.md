<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshMountTableEntriesRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshMountTableEntriesRequestPBImpl.java

## Purpose
Empty PB request used to tell a Router to reload mount table entries from the State Store into its local cache.

## APIs, Types, and Functions
Implements `PBRecord` for `RefreshMountTableEntriesRequestProto`. The constructor can accept an existing proto. `getProto()` explicitly calls `getBuilder()` before `build()` so an empty request still produces a concrete protobuf.

## Control Flow, State, and Persistence
No request fields are persisted. The important flow is cache invalidation: admin or balancing code creates this request, sends it through `MountTableManager.refreshMountTableEntries()`, and the server refreshes local mount-table caches.

## Dependencies and Integration
Used by `RouterAdmin.refreshRouterCache()`, `MountTableRefresherThread`, and balancing procedures. It depends on the generated proto and common PB translator.

## Risks and Test Signals
Because the request is empty, all semantics are in the RPC endpoint. Test signals include `TestRouterMountTableCacheRefresh` and admin refresh command tests that verify cache freshness after add/update/remove operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshMountTableEntriesRequestPBImpl.java -->
