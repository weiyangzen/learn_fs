# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/manager.go

## Purpose
This file implements BeeRemote's worker manager: it configures remote storage targets, groups worker nodes into pools by type, submits generated work requests to the right pool, updates outstanding work during job cancellation, and exposes stub-content lookup.

## Important APIs, Types, and Functions
`Config` is currently empty. `Manager` stores node pools, a worker-node wait group, RST providers, the BeeGFS mount provider, and required feature set. `JobSubmission` groups all work requests for one job. `JobUpdate` describes a requested update over existing work results. `NewManager` initializes RST providers and worker pools. `Start`, `SubmitJob`, `UpdateJob`, `GetStubContents`, and `Stop` are the core methods.

## Control Flow
`NewManager` builds an RST map from config, rejects the reserved job-builder RST ID, adds a job-builder client, creates worker nodes, and organizes them into pools with shared `UpdateConfigRequest`. `Start` refuses to run with no valid pools and starts all pool handlers. `SubmitJob` maps each `flex.WorkRequest` type to a worker pool, assigns it, records assignment metadata, and if any request fails to schedule it immediately calls `UpdateJob` to cancel scheduled or created requests. `UpdateJob` iterates existing work results, handles unassigned created requests locally, contacts the assigned pool/node for cancellation, and updates statuses/messages.

## State and Persistence Behavior
The worker manager itself persists no database state, but it produces the `worker.WorkResult` map that the job manager persists. It owns long-lived RST clients and worker node clients. The job-builder RST provider is synthetic and added alongside configured RSTs.

## Dependencies and Integration Points
It depends on `common/rst` providers, `common/filesystem`, `remote/internal/worker`, protobuf `beeremote` and `flex`, and zap logging. It is called by `job.Manager` for job scheduling, cancellation, RST config listing, and stub-content parsing.

## Risks and Edge Cases
Partial scheduling failure triggers best-effort cancellation; if cancellation is not confirmed, the job becomes unknown and requires user action. Unsupported work request types map to `worker.Unknown` and become failed results. The manager logs but tolerates invalid worker configs if at least one valid pool remains. `Stop` starts `node.Stop` calls asynchronously through pools but does not wait on `nodeWG` itself in this method.

## Test Signals
There are no direct tests for this file in the subset, but job-manager tests exercise successful scheduling, scheduling failure, cancellation success/failure, and unknown-state outcomes through mock workers.
