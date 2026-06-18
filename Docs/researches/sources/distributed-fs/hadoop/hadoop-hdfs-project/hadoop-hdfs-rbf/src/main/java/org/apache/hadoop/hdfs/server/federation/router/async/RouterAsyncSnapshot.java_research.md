# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncSnapshot.java

## Purpose
`RouterAsyncSnapshot` implements the snapshot-related `ClientProtocol` surface for the async router. It mirrors `RouterSnapshot` behavior while composing remote calls through the async RPC client and translating paths between global mount paths and destination NameNode paths.

## Important APIs, Types, And Functions
The module overrides `createSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, and `getSnapshotDiffReportListing`. It uses `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `RemoteResult`, `SnapshotStatus`, `SnapshottableDirectoryStatus`, `SnapshotDiffReport`, and `SnapshotDiffReportListing`. `DFSUtil.bytes2String` and `DFSUtil.string2Bytes` are used when rewriting snapshot listing parent paths.

## Control Flow
Each public method first calls `rpcServer.checkOperation` with the correct NameNode operation category. Path-scoped methods resolve remote locations with `getLocationsForPath`. If the path is configured for concurrent invocation, the method calls `rpcClient.invokeConcurrent` and transforms the returned map; otherwise it calls `invokeSequential` and transforms the chosen `RemoteResult`. Snapshot creation rewrites the returned destination path back to the source mount path. Listing calls merge namespace arrays or select the first routed result depending on operation semantics.

## State, Persistence, And Dependencies
The class keeps references to `RouterRpcServer`, `RouterRpcClient`, and `ActiveNamenodeResolver`. Snapshot state itself is persisted by destination NameNodes, not by this module. The module depends on router mount-table resolution and on NameNode snapshot APIs.

## Integration Points
It is plugged into the async `RouterRpcServer` client protocol implementation. It uses the resolver for all namespaces in `getSnapshottableDirListing`, router merge utilities for array responses, and `RemoteParam` to inject per-location destination paths into reflected NameNode calls.

## Risks
Concurrent path rewrites assume a representative first result and location, which is correct only when the resolved operation maps to equivalent destinations. `replaceFirst` treats the first argument as a regex, so unusual path characters could matter. `getSnapshotListing` has different replacement directions in concurrent and sequential branches, making regression tests important.

## Test Signals
Snapshot tests should cover mount-path rewriting for create and list, concurrent versus sequential invocation, empty or multi-namespace snapshottable listings, diff report listing pagination, and failure behavior when one namespace lacks snapshot support.
