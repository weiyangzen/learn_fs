# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyInProgressTail.java

Purpose: validates standby tailing of in-progress edit logs through QJM, including default disabled behavior, enabled catch-up, failover catch-up across multiple segments, non-uniform configuration, journal cache use, corrupt cache fallback, and operation without cache.

Important APIs and types: `MiniQJMHACluster`, `MiniDFSCluster`, `DFS_HA_TAILEDITS_INPROGRESS_KEY`, `QJM_RPC_MAX_TXNS_KEY`, `JournalTestUtil.corruptJournaledEditsCache`, `NNStorage.getInProgressEditsFileName`, `NameNodeAdapter.getFileInfo`, `EditLogTailer.doTailEdits`, and JournalNode edit cache settings.

Control flow: setup enables in-progress tailing, slows normal tailing to 20 minutes, limits QJM RPC transaction batches, allows standby reads, and starts QJM HA. `testDefault` restarts with in-progress tailing disabled and confirms the standby neither has local edit files nor sees unfinalized edits until failover. Enabled tests create mkdir edits, wait until standby sees paths before log rolls, restart standby without finalizing shared edits, and verify state survives. Additional tests exercise partially started tailing, initial tail of finalized plus in-progress segments, new in-progress segments after prior tailing, transition-to-active catch-up across three rolled segments, active without in-progress tailing, cache-only serving after deleting finalized edit files, corrupt cache fallback across remaining JournalNodes, and disabled cache fallback to log files.

State and persistence behavior: tracks local NameNode edits directories, shared QJM logs, in-progress and finalized segment names, JournalNode edit caches, committed txid visibility, and standby namespace file info.

Dependencies and integration points: integrates QJM JournalNodes, HA edit tailer, storage directory inspection, manual RPC mkdir/roll operations, DFSUtil nameservice lookup, and test utilities for cache corruption.

Risks and test signals: risks include double replay from mid-segment restart, failure to tail current edits, relying incorrectly on local standby edit files, failover with under-tailed segments, and cache corruption causing lost edits. Signals include `assertNoEditFiles`, `assertEditFiles`, repeated `waitForFileInfo` with manual tailing, deletion/corruption of journal artifacts, and final namespace visibility checks.
