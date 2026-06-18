<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java

## Purpose
`RouterClientProtocol` is the router-side implementation of HDFS `ClientProtocol`. It is the main translation layer between client RPCs and Router-Based Federation: it checks operation category, resolves the federated path to one or more `RemoteLocation`s, chooses sequential, concurrent, or single-namespace dispatch through `RouterRpcClient`, and synthesizes router-visible results such as virtual mount-point statuses, merged listings, datanode reports, content summaries, and open-file listings.

## Important APIs, Types, and Functions
The constructor wires the `RouterRpcServer`, `RouterRpcClient`, `FileSubclusterResolver`, `ActiveNamenodeResolver`, feature modules for erasure coding/cache/snapshot/storage policy, the security manager, and `RouterFederationRename`. It selects async helper implementations when `rpcServer.isAsync()` is true.

Client-facing methods cover file lifecycle (`create`, `append`, `addBlock`, `complete`, `truncate`, `delete`, `mkdirs`), metadata (`getFileInfo`, `getListing`, `getLocatedFileInfo`, `setPermission`, ACL and xattr operations), cluster-wide admin reads/writes (`getStats`, `setSafeMode`, `rollEdits`, `refreshNodes`, `setBalancerBandwidth`), feature delegates (`RouterSnapshot`, `RouterCacheAdmin`, `RouterStoragePolicy`, `ErasureCoding`), quota (`setQuota`, `getQuotaUsage`), and federation-specific helpers (`getRenameDestinations`, `aggregateContentSummary`, `getMountPointStatus`, `getLocationsForContentSummary`, `mergeAndSortOpenFileListResults`).

Several protocol methods are intentionally not implemented or not supported through the router: `getDelegationTokens` returns `null`, `getBatchedListing` throws, `upgradeStatus` throws, and edit-log/encryption-key related APIs return `null` after restricted `checkOperation` calls.

## Control Flow
Every public RPC begins with `rpcServer.checkOperation` using the matching NameNode operation category. Path-based methods usually call `rpcServer.getLocationsForPath`, build a reflective `RemoteMethod`, and dispatch through `rpcClient.invokeSequential`, `invokeConcurrent`, `invokeSingle`, `invokeSingleBlockPool`, or `invokeAll`.

Write creation first handles `/.../_all` style parent creation, chooses a create location via `rpcServer.getCreateLocation`, and retries alternate destinations only when `checkFaultTolerantRetry` sees a connection/no-namenode failure and the path is fault tolerant. Rename first filters source/destination pairs with matching nameservices. If none remain, it delegates cross-namespace rename to `RouterFederationRename`; multi-destination directory renames require all source locations to remain eligible.

Listing is federated. `getListingInt` concurrently reads downstream directory listings, `getListing` merges them by local name, trims entries past the lowest downstream batch boundary to preserve pagination correctness, injects virtual mount points from the resolver, and honors `allowPartialList` for non-`FileNotFoundException` failures. `getFileInfo` similarly falls back to mount point metadata when no downstream file exists. Content summary recursively gathers direct and child mount locations, removes descendant redundancy per namespace, invokes downstream summaries, and aggregates counts.

Block-oriented operations route by block pool when possible. `addBlock`, `getAdditionalDatanode`, `abandonBlock`, `complete`, `updateBlockForPipeline`, `updatePipeline`, and `reportBadBlocks` use an `ExtendedBlock` or block pool id to target the owning namespace. Cluster-wide methods invoke all registered namespaces and aggregate values, with a few methods using `requireResponse` or standby calls depending on semantics.

## State and Persistence Behavior
The class itself persists no durable state. It caches `FsServerDefaults` in volatile fields for `serverDefaultsValidityPeriod`, keeps configuration-derived flags such as `allowPartialList`, mount-status timeout, default nameservice behavior, superuser/group reporting identity, and exposes the live cross-namespace rename counter through `RouterFederationRename`.

Persistent state is read or changed through collaborators: namespace metadata through downstream NameNodes, mount table metadata through the resolver, quota through `Quota`, delegation tokens through `RouterSecurityManager`, and federation rename jobs through the FedBalance scheduler. Virtual `HdfsFileStatus` objects for mount points are synthesized in memory and may overlay downstream status details.

## Dependencies and Integration Points
Primary dependencies are `RouterRpcServer`, `RouterRpcClient`, `FileSubclusterResolver`/`MountTableResolver`, `ActiveNamenodeResolver`, `RemoteLocation`, `RemoteMethod`, `RemoteResult`, `NameNode.OperationCategory`, and HDFS protocol model classes. Feature calls integrate with `RouterSnapshot`, `RouterCacheAdmin`, `RouterStoragePolicy`, `ErasureCoding`, and async variants. Quota integration goes through `rpcServer.getQuotaModule()`. Federation rename integrates with `RouterFederationRename` and FedBalance.

## Risks
Dispatch semantics vary by method; using sequential dispatch where all destinations must be mutated, or concurrent dispatch where first-success is expected, can cause inconsistent federation state. Listing pagination is sensitive to the `lastName` and `remainingEntries` logic and can skip or duplicate entries if downstream batches are merged incorrectly. Virtual mount-point status may mask downstream failures because it catches `IOException` and falls back to mount table defaults. Several protocol methods return `null` rather than throwing, so client compatibility depends on callers tolerating unsupported APIs. Recursive content-summary location discovery can be expensive on deep mount trees. Fault-tolerant retry is deliberately limited to availability-style exceptions; expanding it could duplicate writes.

## Test Signals
Useful tests should cover path resolution and operation-category checks for representative read/write/admin calls, create/mkdir retry behavior on fault-tolerant mounts, same-namespace and cross-namespace rename cases, multi-destination directory rename rejection, directory listing pagination with overlapping downstream entries and mount points, `allowPartialList` behavior, mount-point status synthesis from mount table and downstream status, block-pool routing, content summary deduplication, open-file merge ordering, quota delegation, async feature-module construction, and unsupported/null-return protocol methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java -->
