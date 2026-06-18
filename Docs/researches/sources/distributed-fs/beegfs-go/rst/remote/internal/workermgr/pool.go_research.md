# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/pool.go

## Purpose
This file implements worker pools for BeeRemote. A pool contains workers of one type and provides round-robin assignment plus targeted update of existing work on the node that owns it.

## Important APIs, Types, and Functions
`Pool` stores node type, ordered workers, worker lookup map, next round-robin index, mutex, and shared worker config. `HandleAll` starts each node handler with config and an initial bulk work update. `StopAll` requests every node to stop. `assignToLeastBusyWorker` assigns a work request to an online node. `updateWorkRequestOnNode` sends an update to the originally assigned worker node.

## Control Flow
`HandleAll` sends `UNCHANGED` bulk updates on startup because offline work mutation is not yet supported. `assignToLeastBusyWorker` locks the pool, loops up to four passes, skips offline nodes, calls `SubmitWork` on online nodes, advances the round-robin cursor, retries other workers on send errors, and returns aggregate errors when all online attempts fail. `updateWorkRequestOnNode` locks, looks up the assigned node by ID, builds a `flex.UpdateWorkRequest`, and calls `UpdateWork`.

## State and Persistence Behavior
No durable state is written. The pool maintains only in-memory assignment cursor state. Assignment decisions are captured by the caller in persisted `worker.WorkResult.AssignedNode` and `AssignedPool`.

## Dependencies and Integration Points
The pool depends on `worker.Worker`, worker states/types, `common/types.MultiError`, and protobuf `flex`. It is owned by `workermgr.Manager`.

## Risks and Edge Cases
Despite the comment naming "least busy", assignment is currently round-robin and does not account for work size or active load. The whole pool lock is held during `SubmitWork`/`UpdateWork`, so slow RPCs serialize assignment/update operations for that pool. If all nodes are offline, it sleeps three times before failing, adding latency to job submission. `StopAll` starts stop requests in goroutines and does not wait by itself.

## Test Signals
No direct pool tests appear in this subset. Behavior is indirectly validated through job-manager tests using mock nodes.
