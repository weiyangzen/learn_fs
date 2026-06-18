# sources/distributed-fs/openafs/src/bozo/bnode.c

## Purpose
Implements the generic BOS bnode process supervisor. It registers bnode types, creates/deletes instances, starts/stops child processes, tracks exits/timeouts/retry state, saves cores, and runs notifier programs.

## Important APIs, Types, and Functions
Public functions include `bnode_Init`, `bnode_Register`, `bnode_Create`, `bnode_Delete`, `bnode_FindInstance`, `bnode_SetStat`, `bnode_SetFileGoal`, `bnode_WaitStatus`, `bnode_WaitAll`, `bnode_SetTimeout`, `bnode_InitBnode`, `bnode_NewProc`, `bnode_StopProc`, `bnode_ParseLine`, and core/status accessors. Static globals are `allBnodes`, `allProcs`, `allTypes`, `bproc_cv`/`bproc_pid`, and `bnode_stats`.

## Control Flow
Initialization starts a detached pthread or LWP manager and registers signal handlers. The manager sleeps until the next timeout or SIGCHLD, calls bnode timeout methods, reaps children with `waitpid`, records exit/signal state, runs notifiers, applies exponential retry delay on rapid failures, invokes `BOP_PROCEXIT`, and wakes waiters.

## State and Persistence
In-memory state lives in global queues and fields in `struct bnode`/`struct bnode_proc`. File-persistent state is written through `WriteBozoFile` when file goals or bnode definitions change. Core dumps are renamed into configured core/log paths. Notifier data is streamed to an external program.

## Dependencies and Integration Points
Uses bnode operation vectors from concrete bnode types, `bnode_internal.h` locking, LWP or pthread/softsig infrastructure, process management `spawnprocve_sig`, audit logging, BOS prototype functions, and AFSDIR path constants.

## Risks and Test Signals
`bnode_ParseLine` leaks already-created tokens if a later token exceeds 256 bytes. `bnode_Register` ignores `anparms` and stores type name pointers without copying. `bnode_NewProc` stores `comLine` and `coreName` pointers without ownership copying. Tests should cover rapid crash backoff, notifier invocation, timeout rescheduling, delete with refcounts, pid-file/core behavior through concrete ops, and signal/shutdown handling in both pthread and LWP builds.
