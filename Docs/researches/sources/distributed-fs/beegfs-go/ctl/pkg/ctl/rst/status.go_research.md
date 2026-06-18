# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/status.go

## Purpose
Computes remote synchronization status for paths either from BeeRemote job database state or by verifying remote storage targets directly. It supports iterative/list input, recursive path/database merge, and remote verification modes.

## Important APIs, Types, And Functions
Exports `GetStatusCfg`, `GetStatusResult`, `PathStatus`, status constants, `PathStatus.String`, and `GetStatus`. Internal flow is split across `statusInfoVerifyRemoteWalk`, `statusInfoIterativeWalk`, `statusInfoRecursiveWalk`, `runWorkers`, `worker`, `getPathStatusFromTarget`, and `getPathStatusFromDatabase`.

## Control Flow
`GetStatus` streams paths lexicographically through `util.StreamPaths`, consumes the first path for setup, then starts a status-info stage and worker stage. Verification mode passes each path directly to workers. Iterative mode calls `GetJobs` once per path. Recursive mode opens one prefix stream from BeeRemote and merge-walks sorted filesystem paths with sorted database paths, producing matched or unmatched status info.

Workers load cached mappings, a BeeGFS client, and optionally RST provider clients. Database status checks lstat the path, reject directories/non-regular files, resolve remote targets either from config or entry metadata, compare latest relevant job per target against current file mtime, and produce synchronized/offloaded/unsynchronized/no-target/not-attempted statuses. Remote verification uses `rst.GetLockedInfo`, optional configured targets, stub-content fallback for offloaded unreadable files, and `rst.Provider.GetRemotePathInfo` to compare remote size/mtime.

## State And Persistence
No persistent mutations. It reads filesystem metadata, entry metadata, BeeRemote job DB, and remote object metadata. It uses Viper when converting status to emoji/text and uses cached mappings through `util.GetCachedMappings`.

## Dependencies And Integration Points
Integrates `ctl/pkg/util` path pipelines, `rst/getjobs.go`, `rst/getstubcontents.go`, `entry.GetEntry`, BeeGFS filesystem provider, common RST helper functions, remote storage providers, gRPC code handling, protobuf timestamps, and Viper debug/emoji flags.

## Risks And Edge Cases
Recursive status requires sorted filesystem and database paths; violating that ordering produces false not-found outcomes. In `getPathStatusFromDatabase`, `job := jobResult.GetJob()` is executed before checking `jobResult == nil`; a configured target with no matching job can panic instead of returning the intended "Path has no jobs" message. Mtime comparison uses exact `time.Equal`, which may be sensitive to precision differences. `PathStatus.String` depends on global Viper state. Remote verification returns a warning offloaded state for older BeeRemote services missing `GetStubContents`.

## Test Signals
No direct tests. This file needs focused tests for recursive merge ordering, no-job target handling, offloaded stubs, remote verification not-found handling, directory/non-regular classification, and debug versus non-debug reasons.
