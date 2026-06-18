## sources/distributed-fs/beegfs/storage/source/app/App.cpp

Purpose: Implements the BeeGFS storage daemon lifecycle: configuration, target preinitialization and registration, network setup, component startup/shutdown, session persistence, and auxiliary library handling.

Important APIs/types/functions: `run()` constructs `Config` and dispatches `runNormal()`. `runNormal()` performs NUMA binding, storage locking, logging, UUID checks, node/target registration, management-info download, component init/start/join, session restore/delete/store, and shutdown cleanup. Other key methods initialize logging/data/network/storage/components/workers/listeners, register with mgmtd (`waitForMgmtNode()`, `preregisterNode()`, `preregisterTargets()`, `registerAndDownloadMgmtInfo()`), and handle signals/components.

Control flow: Startup locks target dirs before logging, waits for mgmtd heartbeat, obtains node and target numeric IDs, creates `StorageTargets`, downloads mappings/states/pools, applies local resync decisions, starts components, deletes old session files after restore, waits for termination, then stores sessions. Shutdown stops workers, fetchers, syncers, listeners, benchmarker, and closes ZFS.

State and persistence: Persists node numeric ID files, target numeric ID files, target format/session files through `StorageTarget`/`StorageTk`, and session backup files on clean shutdown. It locks PID and target directories, checks filesystem UUIDs if configured, and manages in-memory stores for nodes, targets, states, sessions, quotas, work queues, and resync.

Dependencies and integration: Central integration point for `Config`, `StorageTargets`, `InternodeSyncer`, `DatagramListener`, `StorageStatsCollector`, `StorageBenchOperator`, `BuddyResyncer`, `ChunkFetcher`, `ChunkStore`, `SessionStore`, `NodeStoreServers`, `TargetMapper`, `MirrorBuddyGroupMapper`, `TimerQueue`, RDMA/NIC discovery, and mgmtd messages.

Risks and test signals: Startup ordering is critical: target locks and registration must precede worker traffic. `registerAndDownloadMgmtInfo()` mutates downloaded states with local resync decisions before syncing the state store and sets offline timeouts for primary targets needing resync. Signal handler logs from signal context, which the comment recognizes as potentially unsafe. Tests should cover restart with existing target IDs, first-run target initialization disabled, UUID mismatch, mgmtd retry interruption, per-target vs global queues, session restore/store, and offline-timeout state publication.
