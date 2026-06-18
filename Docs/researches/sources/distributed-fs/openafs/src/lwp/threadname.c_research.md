# sources/distributed-fs/openafs/src/lwp/threadname.c

Purpose: legacy thread-name registry used by server logging, supporting both pthread and LWP process identifiers.

Important APIs/types/functions: `threadname` returns the registered name for the current thread/LWP or `"main"`. `registerthread` stores or updates a mapping from thread ID to name. `swapthreadname` replaces a registered name and optionally returns the old name.

Control flow: each lookup scans the fixed arrays linearly. Registration updates an existing slot or appends a new one until `MAX_THREADS`.

State and persistence: global arrays `ThreadId` and `ThreadName`, plus `nThreads`. No locking is present in this file, and no state persists outside the process.

Dependencies/integration: uses `pthread_self` under `AFS_PTHREAD_ENV`; otherwise uses `LWP_ThreadId`. This is separate from `opr/threadname.c`, which sets OS thread names.

Risks and test signals: fixed capacity of 128, global mutable state, no synchronization, and truncation to 63 characters. Tests are indirect through logging behavior in server/LWP code.
