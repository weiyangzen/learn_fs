# sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils.go

## Purpose
This small utility file converts internal worker-result state into the protobuf shape returned by BeeRemote job APIs.

## Important APIs, Types, and Functions
`getProtoWorkResults(workResults map[string]worker.WorkResult) []*beeremote.JobResult_WorkResult` iterates over stored `worker.WorkResult` values and builds `beeremote.JobResult_WorkResult` messages. It carries through the latest `flex.Work`, assigned worker node ID, and assigned pool as a string.

## Control Flow
The function allocates an empty result slice, iterates over the map, builds one protobuf result for each entry, appends it, and returns the slice. Map iteration order is deliberately unspecified.

## State and Persistence Behavior
The function is read-only and performs no persistence. It copies pointers from persisted `WorkResult` structures into response messages, so callers receive the stored work object without re-synthesizing request details.

## Dependencies and Integration Points
It depends on `remote/internal/worker` for the internal result type and on `beeremote` protobufs for response construction. `manager.go` uses this helper in submission, update, duplicate-conflict, and sentinel-error responses.

## Risks and Edge Cases
Because Go map iteration is nondeterministic, response order is not stable. Callers and tests must match by request ID rather than slice index unless they control the map shape. The helper does not filter nil work results, so corrupted internal state could propagate nil protobuf fields into responses.

## Test Signals
`utils_test.go` validates status, message, assigned node, and assigned pool conversion while accounting for nondeterministic map order via request IDs.
