# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterCacheAdmin.java

## Purpose
`RouterCacheAdmin` implements router-side forwarding for HDFS cache directive and cache pool client protocol operations.

## Important APIs, Types, And Functions
- `addCacheDirective`, `modifyCacheDirective`, `removeCacheDirective`, and `listCacheDirectives` handle cache directives.
- `addCachePool`, `modifyCachePool`, `removeCachePool`, and `listCachePools` handle cache pools.
- Protected invoke methods expose map-returning behavior for tests and subclasses.
- `getRemoteMap` maps each `RemoteLocation` to the original `CacheDirectiveInfo` so `RemoteMethod` can rebuild it with destination paths.

## Control Flow
Directive operations with a path resolve router locations and invoke remote methods against those locations. Directive modification without a path, directive removal by ID, and all cache pool operations fan out across all namespaces from `ActiveNamenodeResolver`. Public list/add methods return the first value from the remote response map for single logical results.

## State And Persistence
The class stores references to `RouterRpcServer`, `RouterRpcClient`, and `ActiveNamenodeResolver`. Cache directive and pool state is persisted by downstream NameNodes, not by the router class.

## Dependencies And Integration Points
It depends on HDFS cache protocol classes, `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `FederationNamespaceInfo`, and NameNode operation categories. `RouterClientProtocol` delegates cache-related `ClientProtocol` calls to this module.

## Risks And Edge Cases
Returning the first response for add/list operations assumes responses are equivalent or the relevant operation targets one logical location. Namespace-wide operations can partially fail depending on `invokeConcurrent` flags. `getRemoteMap` maps every location to the same directive object and relies on `RemoteMethod` special handling to rewrite the path per destination. Cache directive IDs are NameNode-local, so remove/modify semantics across namespaces require careful client expectations.

## Test Signals
Router client protocol, cache admin, and multi-destination tests indirectly exercise this module. Coverage should include path-remapping of cache directives and namespace-wide pool operations.
