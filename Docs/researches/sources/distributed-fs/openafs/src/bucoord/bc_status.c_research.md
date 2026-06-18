# sources/distributed-fs/openafs/src/bucoord/bc_status.c

`bc_status.c` implements backup coordinator status watching for scheduled and active tape coordinator tasks. It maintains a global queue of `statusS` nodes, polls butc task status, sends abort requests, starts scheduled dumps, reports completion, and exposes wait/job-number helpers.

Important APIs include `statusWatcher`, `cmdDispatch`, `bc_jobNumber`, `waitForTask`, and helper `nextItem`. Globals include `statusHead`, `statusQueueLock`, `cmdLineLock`, `lastTaskCode`, and `cmdLine`. Macros `SET_FLAG` and `CLEAR_FLAG` update the current status node under lock.

Control flow in `statusWatcher` loops forever, cycling through status nodes. It sleeps if the queue is empty, handles pre-start aborts, starts scheduled dumps by moving `cmdLine` into a new LWP `cmdDispatch`, handles local abort/contact-lost cases, connects to butc through `bc_GetConn`, validates `CheckTCVersion`, sends `TC_RequestAbort` when needed, polls `TC_GetStatus`, updates local flags and progress, reports task completion/abort/error, calls `TC_EndStatus`, and deletes or preserves nodes based on `NOREMOVE`. `waitForTask` sleeps and polls local queue flags until the requested task is done or removed.

State and persistence are in-memory queue state plus scheduled command lines; durable backup metadata lives in downstream budb/butc services, not here. Dependencies include LWP, Rx, bubasics status flags, tcdata/butc RPCs, command parser/dispatcher, `bc_globalConfig`, locks, and bucoord internal prototypes.

Risks include concurrency on global `cmdLine`, queue-node lifetime while locks are dropped, contact-lost retry behavior, output from background watcher interleaving with command output, and apparent `delaytime`/`delayTime` case mismatch in pthread branches that would matter when `AFS_PTHREAD_ENV` is enabled. Test signals include scheduled dump dispatch, abort before start, abort after start, TC_NODENOTFOUND cleanup, CONTACT_LOST recovery, `NOREMOVE` behavior, and `waitForTask` completion semantics.
