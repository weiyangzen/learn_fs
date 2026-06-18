<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs

Purpose: starts or restarts buddy target resync for metadata or storage buddy groups.

Important APIs/types/functions: `start_resync()` resolves a buddy group, identifies source primary and destination secondary target plus source node UID, checks current resync status via meta/storage BeeMsg requests, optionally calls nested `override_last_buddy_comm()`, marks destination target `NeedsResync`, and broadcasts `RefreshTargetStates`.

Control flow: metadata resync only supports full non-restart resync and rejects timestamps. Storage resync can override last buddy communication timestamp; restart requires a timestamp and waits up to 180 seconds for the existing resync to stop, polling every two seconds. The actual resync begins when nodes fetch refreshed target state.

State and persistence: mutates destination target consistency in SQLite. It sends BeeMsg stats/override requests to the source node and refresh notifications to the cluster.

Dependencies and integration points: mirroring license, buddy group/target DB views, storage/meta resync BeeMsg types, `tokio::time`, and target-state refresh mechanics.

Risks: the code documents a race where storage nodes may overwrite the communication timestamp before resync starts. Polling is described as simple but imperfect. DB state change and source-node override are separate effects.

Test signals: no direct tests. Coverage should include meta rejection cases, storage running/not-running states, restart timeout, override failure, and final DB state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs -->
