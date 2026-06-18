<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/add_replica.go -->
## sources/control-plane/longhorn-engine/app/cmd/add_replica.go

### Purpose
`add_replica.go` defines Longhorn Engine CLI commands for adding replicas, starting an engine with replicas, reporting rebuild status, and verifying rebuilt replicas.

### Important APIs, Types, And Functions
`AddReplicaCmd` exposes `add-replica`/`add` with flags `restore`, `size`, `current-size`, `fast-sync`, `sync-local`, `file-sync-http-client-timeout`, `grpc-timeout-seconds`, and `replica-instance-name`. `addReplica` validates input and calls `sync.Task` methods. `StartWithReplicasCmd` and `startWithReplicas` start with a replica list. `RebuildStatusCmd`/`rebuildStatus` print JSON rebuild status. `VerifyRebuildReplicaCmd`/`verifyRebuildReplica` validate a rebuilt replica address/instance name.

### Control Flow
Each command action calls a helper and logs fatal on error. Helpers read global `url`, `volume-name`, and `engine-instance-name`, create a cancellable context, instantiate `sync.NewTask`, parse size flags with `units.RAMInBytes`, validate required args, and dispatch to the appropriate sync task method. `addReplica` uses `AddRestoreReplica` for restore/DR volumes and `AddReplica` otherwise, passing file sync timeout, fast-sync flag, nil progress callback, and gRPC timeout. Rebuild status marshals the returned map with indentation and prints to stdout.

### State, Persistence, And Dependencies
The command itself persists no local state, but `sync.Task` operations mutate Longhorn engine/controller replica state and may initiate rebuild/sync operations over network/gRPC/HTTP. Dependencies include urfave/cli, docker/go-units, logrus, JSON, context, and `pkg/sync`.

### Integration Points
These commands are part of the Longhorn Engine CLI used by managers/operators to add replicas during normal rebuild, restore/DR workflows, engine startup, and rebuild verification. They rely on global CLI flags defined elsewhere for controller URL and instance identity.

### Risks
The `sync-local` flag is declared but not used in `addReplica`, which may be dead or pending behavior. Contexts are cancelable but have no timeout here; long operations depend on sync task internals and the optional gRPC timeout flag. Size parsing accepts human-readable units from docker/go-units, so unit semantics should match Longhorn expectations. Fatal logging exits the process on command errors.

### Test Signals
Tests should cover missing replica/size/current-size errors, invalid size strings, restore versus normal dispatch, propagation of fast-sync/file-sync/gRPC timeout/replica-instance-name flags, JSON status output, verify command missing argument, and the unused `sync-local` flag decision.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/add_replica.go -->
