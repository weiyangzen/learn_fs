# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/updatejob.go

## Purpose
Updates BeeRemote job state for a single path/job or recursively for a path prefix.

## Important APIs, Types, And Functions
Exports `UpdateJobCfg`, `UpdateJobsResponse`, and `UpdateJobsByPaths`.

## Control Flow
Validates that recursive update is not combined with a specific job ID, resolves the path relative to the BeeGFS mount, builds `UpdateJobsRequest` with new state, force flag, path, optional job ID, and optional remote-target filter. For non-recursive updates it launches a goroutine that sends a unary `UpdateJobs` RPC and emits one response. For recursive updates it opens `UpdatePaths` stream and emits each update result until EOF.

## State And Persistence
Persistent effect is BeeRemote job DB state changes. Local state is the response channel and request-local remote target map.

## Dependencies And Integration Points
Depends on BeeGFS mount path resolution, BeeRemote client, BeeRemote update protobuf builders, and remote target IDs fitting uint32.

## Risks And Edge Cases
Like `GetJobs`, it tolerates `filesystem.ErrUnmounted` from client acquisition but still uses the returned provider. Recursive streaming errors terminate the channel after one error response. Remote targets are deduplicated into a map and values above `math.MaxUint32` are rejected.

## Test Signals
No direct tests. Tests should cover mutually exclusive options, path conversion, job ID setting, remote target bounds, unary and stream error paths.
