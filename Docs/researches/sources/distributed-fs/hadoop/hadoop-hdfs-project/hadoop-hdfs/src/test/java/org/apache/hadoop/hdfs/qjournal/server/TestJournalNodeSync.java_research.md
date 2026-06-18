# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeSync.java

Purpose: Slow HA integration suite for `JournalNodeSyncer` repair. It verifies missing edit logs are restored after deletion, downtime, formatting, disk wipe, and rolling upgrade scenarios.

Important APIs/types/functions: `MiniQJMHACluster`, `MiniDFSCluster`, `MiniJournalCluster`, `JournalNodeSyncer`, `generateEditLog`, `deleteEditLog`, `deleteEditLogsFromRandomJN`, `editLogExists`, `jnFormatted`, `DFS_JOURNALNODE_ENABLE_SYNC_KEY`, `DFS_JOURNALNODE_SYNC_INTERVAL_KEY`, and rolling-upgrade APIs.

Control flow: Setup enables sync and sync-format, starts a two-NameNode HA QJM cluster, and transitions NN0 active. Tests verify self-exclusion for same-host multi-port and wildcard URIs, create finalized edit segments, delete selected files, and wait for sync to restore them. Downtime tests stop/restart a JN while edits roll. Format and disk-wipe tests require reformat and refill. Rolling-upgrade test prepares, restarts standby with rolling-upgrade flags, fails over, deletes logs, verifies repair, and finalizes.

State and persistence behavior: Finalized edit-log files and journal formatting metadata are the key state. Tests delete real files and require them to reappear; metrics validate repair path usage when queueing is disabled.

Dependencies and integration points: HA NameNode edit rolling, JournalNodeSyncer download, QJM committed txid behavior, storage formatting, and rolling upgrade state.

Risks: Repair failures can leave rejoined or reformatted JournalNodes permanently behind. Tests are timing-sensitive due to background polling.

Test signals: Passing proves syncers start when configured, avoid self-sync, restore missing logs, recover after downtime/format/disk wipe, and work during rolling upgrades.
