# sources/control-plane/longhorn-engine/pkg/replica/server.go

Purpose: provides a concurrency-safe service wrapper around `Replica`, enforcing replica state transitions and exposing the `types.DataProcessor` data path.

Important APIs/types/functions: `Server` stores context, active replica, directory, sector/backing settings, revision/unmap/snapshot flags, and encryption flag. `NewServer` constructs it. Lifecycle methods include `Create`, `Open`, `Reload`, `Status`, `Close`, and `Delete`. Management methods delegate snapshot/revert/expand/disk/revision/flag operations. Data methods `WriteAt`, `ReadAt`, `UnmapAt`, and `PingResponse` are used by dataconn.

Control flow: `Create` only acts from initial state and closes the newly created replica. `Open` refuses if already open, reads closed status info, and constructs a new replica. `Status` reads `volume.meta` when closed and maps dirty/rebuilding/error fields to replica states. Mutating methods lock the server and usually no-op when no replica is open. Data methods take an `RLock` and fail if the replica no longer exists.

State and persistence: owns the live `Replica`; durable state is in replica disk files and metadata. Server-level flags persist only while the process runs unless written through replica metadata elsewhere.

Dependencies and integration points: used by gRPC management server and data server. Integrates backing files, Longhorn replica states, and dataconn data processor expectations.

Risks: several management calls silently no-op when no replica is open, which can hide caller sequencing bugs. `Delete` only deletes when `s.r` is non-nil, so closed-on-disk replicas are not removed through this path. `Status` recovery around invalid/missing metadata is subtle and can classify empty metadata as initial. `PingResponse` depends on state but does not verify data-path health beyond metadata state.

Test signals: broad indirect coverage through `replica_test.go`, but server state machine and closed-replica delete/no-op behavior are not directly tested here.
