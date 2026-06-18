# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncStoragePolicy.java

## Purpose
`RouterAsyncStoragePolicy` provides async router implementations for storage policy reads from HDFS client protocol.

## Important APIs, Types, And Functions
It overrides `getStoragePolicy(String)` and `getStoragePolicies()`. It uses `BlockStoragePolicy`, `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `RouterRpcServer`, and `RouterRpcClient`.

## Control Flow
`getStoragePolicy` checks a READ operation with path resolution enabled, resolves the target path to remote locations, builds a `getStoragePolicy` remote method with a per-location path parameter, invokes sequentially, and returns the async placeholder for `BlockStoragePolicy`. `getStoragePolicies` checks READ, builds a no-argument remote method, invokes any available namespace asynchronously through the RPC server helper, and returns the async placeholder array.

## State, Persistence, And Dependencies
No local persistence exists. Storage policy data lives in NameNodes. The class holds only RPC server/client references and depends on router path resolution and available-namespace selection.

## Integration Points
The module is selected by the async router protocol path in place of `RouterStoragePolicy`. It delegates all downstream communication to `RouterRpcClient` or `RouterRpcServer.invokeAtAvailableNsAsync`.

## Risks
Callers must retrieve the actual result through the async response machinery because public methods return `asyncReturn` placeholders. Multi-destination paths use sequential semantics, so first valid location selection and error localization should match the synchronous parent.

## Test Signals
Tests should verify single-path storage policy lookup across mounted paths, no-namespace behavior for `getStoragePolicies`, permission/category checks, and parity with synchronous router responses.
