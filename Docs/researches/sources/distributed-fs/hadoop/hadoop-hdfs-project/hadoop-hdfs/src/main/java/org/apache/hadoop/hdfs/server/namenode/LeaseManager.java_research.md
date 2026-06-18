<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java

## Purpose

`LeaseManager` tracks write leases for under-construction files and drives lease recovery when clients stop renewing. It also lists open files and supports snapshot creation paths that need leased inode resolution.

## Important APIs and Types

State is held in `leases` from holder string to `Lease` and `leasesById` from inode id to `Lease`. Public/package APIs add, remove, reassign, and renew leases; count leases and paths; list under-construction files; collect leased `INodesInPath`; set lease periods; and start/stop or trigger the monitor. The nested `Lease` stores holder, last update time, and inode ids. The nested `Monitor` periodically checks hard-expired leases.

## Control Flow, State, and Persistence

Lease operations are synchronized, while namespace operations require external FSNamesystem locks. The monitor sleeps for the configured recheck interval, prefilters hard-expired leases without the FS lock, then takes the global write lock and calls `checkLeases` outside safe mode. `checkLeases` copies inode ids before iteration, resolves each inode to `INodesInPath`, removes deleted or invalid entries, and invokes `FSNamesystem.internalReleaseLease` with a rotating internal lease holder. It limits lock hold time and syncs the edit log if block recovery was started. Open-file listing uses inode id as a cursor and returns a non-consistent batched view.

## Dependencies and Integration Points

It depends on `FSNamesystem`, `FSDirectory`, `INodeFile`, `INodesInPath`, `BlockInfo`, `OpenFileEntry`, `BatchedListEntries`, DFS lease configuration keys, NameNode locking modes, edit-log syncing, and DataNode block recovery initiated through `internalReleaseLease`.

## Risks and Test Signals

Risks include races with deleted files, lock-order mistakes, stale lease indexes, long write-lock holds during mass expiry, non-consistent open-file pagination, and false leases on non-UC files. Tests should cover add/renew/remove/reassign consistency across both maps, expired hard-limit recovery, deleted inode cleanup, internal lease holder rotation, max lock-hold break behavior, open-file batching/filtering, parallel leased-path collection, safe-mode monitor behavior, and edit-log sync when recovery starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java -->
