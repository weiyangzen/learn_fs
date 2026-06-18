# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSnapshot.java

## Purpose
`RouterSnapshot` implements Router-side handling for snapshot-related `ClientProtocol` calls. It resolves federation paths to remote locations and forwards snapshot operations to the appropriate Namenodes while translating returned paths back to the federated namespace when needed.

## Important APIs and Types
The module exposes `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, and `getSnapshotDiffReportListing`. It uses `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `RemoteMethod`, `RemoteParam`, `RemoteResult`, and HDFS snapshot result types.

## Control Flow
Write operations check `OperationCategory.WRITE`, resolve locations with `getLocationsForPath(..., true, false)`, create a `RemoteMethod`, and either invoke all destinations concurrently for multi-destination/mount paths or sequentially otherwise. Reads check `READ`, either fan out to all namespaces for global listings or resolve the snapshot root and query the selected locations. `createSnapshot` and `getSnapshotListing` rewrite returned paths from remote destination prefixes to federated source prefixes.

## State and Persistence
This class owns no durable state. It mutates snapshot state in remote Namenodes through forwarded RPCs and rewrites in-memory response objects before returning them to clients.

## Dependencies and Integration Points
It integrates with `ClientProtocol` through `RouterClientProtocol`/`RouterRpcServer`, mount-table routing through `RouterRpcServer.getLocationsForPath`, namespace discovery through `ActiveNamenodeResolver`, and Hadoop snapshot types such as `SnapshotDiffReport` and `SnapshotStatus`.

## Risks
Concurrent snapshot operations on multi-destination paths can leave partial state if some subclusters succeed and others fail. Several concurrent-read paths return the first result only, which may hide divergent snapshot state. Path rewriting uses `replaceFirst`, so unexpected regex-sensitive characters or mismatched prefixes could produce incorrect client-visible paths.

## Test Signals
Tests should cover snapshot creation path rewriting, multi-destination allow/disallow/delete/rename behavior, snapshottable listing merge, snapshot listing parent path rewrite, diff report fan-out, and partial failure semantics for concurrent mount entries.
