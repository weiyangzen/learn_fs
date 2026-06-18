# sources/distributed-fs/eos/mgm/wfe/WFE.cc

## Purpose
Implements the MGM workflow engine. It scans persistent workflow queues under the proc workflow path, schedules asynchronous jobs, executes mail/bash/web-notify/protobuf actions, integrates with CTA tape workflows, updates workflow result queues, and publishes active-job statistics.

## Important APIs, types, and functions
`WFE` starts/stops an assisted scanner thread and owns a shared `XrdScheduler`. `WFEr()` is the scan loop. `Job::Save()`, `Load()`, `Move()`, `Results()`, and `Delete()` implement durable queue entries. `Job::DoIt()` dispatches `mail`, `bash`, `notify`, and tape `proto` methods. `HandleNotifyEvents()` sends JSON web notifications. `HandleProtoMethodEvents()` dispatches tape events including prepare, abort_prepare, evict_prepare, create, delete, close, archived, retrieve_failed, archive_failed, offline, and update_fid. `IdempotentPrepare()`, `SendProtoWFRequest()`, `MoveToRetry()`, `MoveWithResults()`, `CollectAttributes()`, and `MoveFromRBackToQ()` are central helpers.

## Control flow
`WFEr()` waits for namespace boot, reads default-space `wfe`, `wfe.interval`, `wfe.ntx`, and `wfe.keepTIME`, and on the master scans today's and yesterday's `q` and `e` queue directories. Ready async jobs are moved to `r`, scheduled, and counted; sync jobs are skipped by the scanner. Old workflow day directories are cleaned periodically. A job file name encodes time, fid, and event; xattrs store action, VID, error message, and retry count.

## State and persistence behavior
Durable workflow state lives in namespace files under `MgmProcWorkflowPath/<day>/<queue>/<workflow>/`. Queue names include queued, running, error/retry, done, failed, and gone/unknown paths (`q`, `r`, `e`, `d`, `f`, `g`). Result xattrs include `sys.wfe.retc`, `sys.wfe.log`, `sys.wfe.errmsg`, `sys.wfe.retry`, `sys.action`, and `sys.vid`. Proto handlers mutate file xattrs such as retrieve request IDs/times/errors, archive errors, CTA objectstore request IDs, archive metadata, and tape locations. Delete removes tape namespace locations before notifying CTA.

## Dependencies and integration points
WFE is deeply integrated with global `gOFS`, `FsView`, namespace prefetching and locks, `ProcCommand`, `ShellCmd`, `WebNotify`, `WFEClient`, CTA protobuf APIs, EOS/CTA reporting helpers, file metadata services, xattr helpers, quota/stat timing, and `EvictCmd`. Bash workflows execute scripts from `/var/eos/wfe/bash/` only when the configured executable has no slash.

## Risks and test signals
The code is concurrency- and side-effect-heavy. Risks include scheduler lifetime leaks, queue moves that save then fail to delete old entries, shell argument injection through substituted metadata, long bash timeouts, many manual placeholder replacement loops, async active-job accounting on early returns, retry attr parse failures, stale jobs in `r` after crashes, and complex tape state races around prepare IDs, archive IDs, and tape location removal. Tests should cover queue persistence and recovery, `MoveFromRBackToQ()`, sync versus async behavior, throttle limits, malformed job filenames/xattrs, bash placeholder substitution and xattr result tags, notify JSON formation, proto endpoint missing, CTA response-code mapping, idempotent prepare with duplicate request IDs, abort with remaining request IDs, archive ID mismatch, delete without archive file id, file-archived GC drop-stripes policy, and retry exhaustion.
