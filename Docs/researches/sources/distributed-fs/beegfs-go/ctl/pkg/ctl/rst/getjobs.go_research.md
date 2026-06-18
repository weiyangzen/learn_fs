# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getjobs.go

## Purpose
Queries BeeRemote job records by job ID/path, exact path, or path prefix and streams grouped job results back to callers.

## Important APIs, Types, And Functions
Exports `GetJobsConfig`, `GetJobsResponse`, `ErrGetJobsStreamUnavailable`, and `GetJobs`. `exactPath` is intentionally package-private for internal status use.

## Control Flow
`GetJobs` resolves the input path to a BeeGFS mount-relative path, builds include flags from config/debug options, selects one protobuf query variant, obtains `BeeRemoteClient`, opens the `GetJobs` stream, then starts a goroutine that receives until EOF. gRPC `Unavailable` is mapped to `ErrGetJobsStreamUnavailable`; `NotFound` is mapped to `rst.ErrEntryNotFound`.

## State And Persistence
No local persistence. It reads BeeRemote's job database through streaming RPC. Response channel ownership remains with the caller; this function closes it when streaming ends.

## Dependencies And Integration Points
Depends on `config.BeeGFSClient`, `config.BeeRemoteClient`, Viper debug config, common filesystem mount helpers, BeeRemote protobuf API, and gRPC status codes.

## Risks And Edge Cases
The function calls `beegfs.GetRelativePathWithinMount` even when `config.BeeGFSClient` returned `filesystem.ErrUnmounted`; this assumes a non-nil provider is still returned for unmounted/deleted paths. `ByExactPath` uses mount-relative path except package-private `exactPath` in one branch assigns `cfg.Path` directly, so callers must be careful about absolute versus in-mount semantics. Stream errors are fatal and terminate the channel.

## Test Signals
No direct tests. Needed coverage includes query selection, unmounted path behavior, gRPC error mapping, and channel close semantics.
