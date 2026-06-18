# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStoragePolicy.java

## Purpose
`RouterStoragePolicy` handles storage policy `ClientProtocol` operations for federated paths. It resolves the path, enforces router operation checks, and forwards the storage policy calls to one or more target Namenodes.

## Important APIs and Types
The module exposes `setStoragePolicy`, `getStoragePolicies`, `unsetStoragePolicy`, `getStoragePolicy`, and `satisfyStoragePolicy`. It uses `RouterRpcServer`, `RouterRpcClient`, `RemoteLocation`, `RemoteMethod`, `RemoteParam`, and `BlockStoragePolicy`.

## Control Flow
Write-like path operations check `WRITE` or supported read categories, resolve remote locations with quota checks disabled where appropriate, and then use `isInvokeConcurrent(path)` to decide between concurrent fan-out for mount/all paths and sequential invocation for normal paths. `getStoragePolicies` is namespace-independent and calls `invokeAtAvailableNs` to query any available namespace.

## State and Persistence
No local state is stored beyond references to the server and client. Mutations are persisted by target Namenodes. The Router only performs routing and result forwarding.

## Dependencies and Integration Points
It integrates with `RouterRpcServer` operation safety, mount-table routing, disabled namespace filtering, and Namenode storage policy RPCs.

## Risks
`satisfyStoragePolicy` is checked as `READ` despite triggering Namenode work; callers rely on the upstream protocol classification. Concurrent fan-out can leave policies inconsistent on multi-destination paths if a subset fails. `getStoragePolicies` returning from the first available namespace assumes policy definitions are compatible across the federation.

## Test Signals
Tests should cover single-destination and multi-destination set/unset/satisfy, unavailable default namespace fallback for `getStoragePolicies`, read-only mount rejection for write operations, and behavior when policies differ across namespaces.
