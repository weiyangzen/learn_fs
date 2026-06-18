# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/replication/ReplicationChecker.java

## Purpose
`ReplicationChecker` is a heartbeat executor that keeps file block replication levels aligned with file policy. It schedules job-service actions for under-replicated pinned blocks, over-replicated blocks, and blocks stored on the wrong medium for pinned files.

## Important APIs, types, and functions
Constructors wire `InodeTree`, `BlockMaster`, `SafeModeManager`, and a `ReplicationHandler`, defaulting to `DefaultReplicationHandler` backed by a job-master client pool. `heartbeat(long)` performs the periodic scan. `findMisplacedBlock(InodeFile, BlockInfo)` computes worker-host to desired-medium moves. Internal `check` handles `Mode.REPLICATE` and `Mode.EVICT`; `checkMisreplicated` handles medium migration. `mActiveJobToInodeID` tracks outstanding job ids and registers the `MASTER_REPLICA_MGMT_ACTIVE_JOB_SIZE` gauge.

## Control flow
Heartbeat skips safe mode and no-worker clusters unless test mode is enabled. It refreshes active job ids by querying job types `Evict`, `Move`, and `Replicate`, pruning completed jobs from the bimap. It scans pinned ids for under-replication, replication-limited ids for over-replication, and pinned ids again for medium mismatch. Each file is locked read-only through `InodeTree.lockFullInodePath`; block locations come from `BlockMaster.getBlockInfo`. Requests are accumulated per file, then submitted through `handler.setReplica` or `handler.migrate` until the active-job cap is reached.

## State and persistence behavior
State is in-memory only: active job id to inode id, plus registered metrics. The checker does not journal its progress. If the master restarts, job-service state and inode/block metadata are re-scanned on future heartbeats.

## Dependencies and integration points
It depends on inode metadata, block metadata, safe mode, job service replication handlers, Alluxio metrics, and job statuses. It integrates with pinned file tracking (`getPinIdSet`), replication-limited ids, block lost detection, and persistence state/durable replication constraints.

## Risks
The active job map prevents duplicate work per inode but is local to the checker and refreshed best-effort; job master RPC failures can leave stale entries until later refresh. Full path locking may add inode-tree contention. The medium-migration logic only targets the first pinned medium type. Unavailable block master or job service aborts the current scan early, delaying other files.

## Test signals
Tests should cover safe-mode/no-worker skipping, active job pruning, job cap enforcement, min/max/durable replication calculations, lost non-persisted block skip, job service busy/unavailable handling, medium mismatch movement, duplicate suppression by inode, and interruption behavior.
