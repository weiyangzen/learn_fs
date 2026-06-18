<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control.go -->
## sources/control-plane/longhorn-engine/pkg/controller/control.go

Purpose: central Longhorn engine controller: manages replica backends, frontend lifecycle, snapshots, expansion, read/write/unmap routing, rebuild interactions, error handling, metrics, and filesystem freeze support.

Important APIs/types/functions: `Controller` stores volume size, replicas, backend replicator, frontend, upgrade/revision/salvage flags, shared timeouts, snapshot limits, rebuild sync limit, gRPC server, metrics, and expansion errors. Constructors and lifecycle methods include `NewController`, `StartGRPCServer`, `WaitForShutdown`, `Start`, `Shutdown`, `StartFrontend`, `ShutdownFrontend`, `AddReplica`, `RemoveReplica`, `SetReplicaMode`, and `ListReplicas`. I/O methods are `ReadAt`, `WriteAt`, `UnmapAt`. Policy methods include snapshot creation/freeze, expansion, revision counter checks/salvage, unmap flag propagation, snapshot limit setters, no-space handling, and metrics helpers.

Control flow: `Start` validates duplicate addresses, creates backends, filters invalid state/size/sector mismatches, adds good replicas as RW and missing/bad ones as ERR, then validates flags/revision counters and starts the frontend. Writes use read lock, validate bounds, and either write normally or read-modify-write aligned sectors when a WO rebuilding replica exists. Snapshots optionally bind-mount/freeze a mounted filesystem, sync if not frozen, re-check limits under lock, and snapshot all backends. Expansion marks `isExpanding`, runs async sync and backend expansion, records partial failure information, then expands frontend and clears state. Errors from `BackendError` can mark replicas ERR, with special ENOSPC handling that preserves a consistent maximal written-byte group.

State and persistence: controller state is in memory, while backend operations persist data, snapshots, revision counters, and flags in replicas. Metrics rotate every second in a goroutine. Expansion errors are retained in memory for API reporting.

Dependencies and integration points: integrates backend factories, `replicator`, frontend implementations, gRPC server, mount utilities, namespace sync, Longhorn disk utilities, identity/rpc layers, and type/error helpers.

Risks: high-concurrency lock ordering is critical. Snapshot freeze touches host/container mount state. Async expansion means API success only means expansion started. ENOSPC policy is subtle and must preserve data consistency. Visible duplicate lock/context snippets in this checkout should be checked by `go test`; if real, they would deadlock or fail compilation. `metricsStart` has an endless goroutine without stop semantics.

Test signals: `control_test.go` covers size selection, WO write alignment, and ENOSPC categorization/retention. Integration tests are needed for frontend startup, replica state transitions, snapshot freeze, expansion, and rebuild.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control.go -->
