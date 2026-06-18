# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/context.go

## Purpose
This file defines the shared context object passed to disruption controllers and a mutex-protected boolean helper.

## Important APIs, Types, and Functions
`Context` carries `ClusterdContext`, `ReconcileCanaries`, and `OpManagerContext`. `LockingBool` stores a boolean plus `sync.Mutex`. `Get` returns the current value under lock, and `Update` sets it under lock.

## Control Flow, State, and Persistence
The state is in-memory only. `LockingBool` serializes concurrent access inside a single operator process and does not persist across restarts.

## Dependencies and Integration Points
`Context` is constructed in the Ceph CR manager and passed to `clusterdisruption.Add` and its reconciler. `ClusterdContext` provides Kubernetes and Ceph execution dependencies; `OpManagerContext` carries cancellation from the manager.

## Risks
`LockingBool` is simple and safe for process-local coordination, but it is not a distributed lock. Any behavior depending on it must tolerate operator restarts and multiple manager instances being prevented by higher-level leader election or deployment assumptions.

## Test Signals
No direct tests are in this subset. Useful tests would exercise concurrent `Get`/`Update` under race detection if this boolean controls future reconciliation gates.
