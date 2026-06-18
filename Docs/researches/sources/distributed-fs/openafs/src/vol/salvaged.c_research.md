# sources/distributed-fs/openafs/src/vol/salvaged.c

## Purpose
Implements the demand-attach online salvage server executable (`salvageserver`) and its client mode. In server mode it accepts SALVSYNC work, forks bounded child salvagers, reaps them, updates scheduler state, and merges per-child logs. In client mode it submits a volume salvage request to an already-running salvageserver and polls until completion.

## Important APIs, Types, And Functions
Important functions are `handleit`, `main`, `SalvageClient`, `SalvageServer`, `DoSalvageVolume`, `SalvageChildReaperThread`, `Reap_Child`, `SalvageLogCleanupThread`, `SalvageLogCleanup`, `SalvageLogScanningThread`, and `ScanLogs`. Runtime structures include `log_cleanup_node`, `log_cleanup_queue`, `pending_q`, `current_workers`, `worker_lock`, `worker_cv`, and `child_slot`.

## Control Flow
`main` validates server paths/root privileges, registers command syntax, and dispatches to `handleit`. Client mode initializes enough volume package state to use SALVSYNC, sends `SALVSYNC_SALVAGE`, then polls with `SALVSYNC_QUERY` every two seconds until done/error/unknown. Server mode opens logging, obtains a shared salvage lock, initializes the volume package and directory package, starts reaper/log cleanup/log scanning threads, and loops on `SALVSYNC_getWork`. For each node it finds a free slot, forks, runs `DoSalvageVolume` in the child, records pid in the parent, and throttles by `Parallel`.

## State And Persistence
Persistent effects are salvage repairs performed by child processes and log files under the server log directory. Runtime scheduling state is split between this file's child slots/condition variables and `salvsync-server.c`'s queues. Child logs are named `SalvageLog.<pid>`, later appended into the main log and unlinked. Server restart handling scans for existing pid logs and waits for those pids to disappear before cleanup.

## Dependencies And Integration Points
This file requires `AFS_DEMAND_ATTACH_FS` and rejects NT. It integrates with `salvsync.h`, `vol-salvage.h`, `partition.c`, `fssync.h`, volume package initialization, process management, OpenAFS command parsing, logging, and directory salvage I/O. It is the executable counterpart to the SALVSYNC server thread.

## Risks And Test Signals
Risks include fork/reaper races, in-memory worker-slot loss after crashes, child log cleanup issues, waiting forever for stale pid logs, partition id lookup failures, and no online salvager support outside DAFS. Test signals include client request/poll success, parallel worker throttling, child failure propagation, log merge after normal and restarted salvageserver runs, invalid partition/volume handling, and signal/core reporting.
