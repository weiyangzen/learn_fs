# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NamenodeFsck.java

## Purpose
`NamenodeFsck` is the server-side implementation behind the HTTP fsck servlet and `DFSck` client. It scans paths, directories, snapshots, files, blocks, replicas, storage policies, and erasure-coded block groups to report health. Optional modes list corrupt files, inspect block IDs, move salvageable data to `/lost+found`, delete corrupt files, or queue mis-replicated blocks for replication.

## Important APIs, types, and functions
The constructor parses servlet parameters including `path`, `move`, `delete`, `files`, `blocks`, `locations`, `racks`, `replicadetails`, `upgradedomains`, `maintenance`, `storagepolicies`, `openforwrite`, `listcorruptfileblocks`, `startblockafter`, `includeSnapshots`, `blockId`, and `replicate`. Major methods are `fsck`, `blockIdCK`, `check`, `checkDir`, `getBlockLocations`, `collectFileSummary`, `collectBlocksSummary`, `copyBlocksToLostFound`, `copyBlock`, `bestNode`, and `lostFoundInit`. Nested `Result`, `ReplicationResult`, and `ErasureCodingResult` accumulate and render counters.

## Control flow
`fsck` handles block-ID requests separately with superuser privilege and block-manager read access. Normal fsck logs the request, loads snapshot roots when requested, resolves the path, optionally lists corrupt file blocks, initializes storage policy summary, then recursively checks entries. Directory traversal uses batched listings and can descend into `.snapshot`. File traversal gets block locations under a namesystem read lock, separates replicated from EC results, and validates each block's replica counts, placement, corruption, missing state, maintenance/decommission state, and optional storage policy summary.

## State and persistence behavior
Most state is per-request counters and output flags. Persistent side effects are limited to `-move`, `-delete`, and `-replicate`: creating `/lost+found` files, deleting corrupt files through RPC, and queueing block-manager replication work. Final strings such as `is HEALTHY`, `is CORRUPT`, `does not exist`, and `FAILED` are consumed by `DFSck` and tests.

## Dependencies and integration points
It depends on `NameNode`, `FSNamesystem`, `NameNodeRpcServer`, `BlockManager`, `NetworkTopology`, `BlockPlacementPolicies`, `DFSClient`, `BlockReaderFactory`, DataNode descriptors, block tokens, storage policies, EC metadata, tracing, and `FsckServlet`.

## Risks and invariants
Fsck must preserve client-visible output strings, avoid slow DataNode I/O under namespace locks, distinguish open under-construction files from corrupt complete files, and treat salvage/delete as permission-checked destructive operations. Placement and missing-block logic must differ correctly for replicated and striped blocks. Salvage can partially copy data; failures mark `internalError` so the run reports failure.

## Test signals
`TestFsck`, `TestHAFsck`, encryption-zone fsck tests, EC fsck tests, decommission/maintenance/stale replica tests, and `DFSck` parsing are primary. Cover healthy/corrupt/nonexistent paths, missing/corrupt blocks, open files, snapshots, block ID lookup, storage policy summaries, lost+found salvage, delete, and replication queueing.
