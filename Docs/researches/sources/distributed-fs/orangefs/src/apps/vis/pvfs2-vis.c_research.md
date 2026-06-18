<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c

## Purpose
Provides the shared polling backend for visualization programs. It initializes OrangeFS management access, gathers I/O server performance samples, stores them in a global buffer, and signals consumers when new samples arrive.

## Important APIs, Types, And Functions
Exports `pvfs2_vis_start`, `pvfs2_vis_stop`, `pint_vis_shared`, `pint_vis_error`, `pint_vis_mutex`, and `pint_vis_cond`. Internal `poll_thread_args` carries filesystem ID, credentials, server addresses, temp matrices, next IDs, end times, server count, history count, and sleep interval. `poll_for_updates` is the background thread.

## Control Flow
Start initializes PVFS defaults, resolves a mount path, generates credentials, counts I/O servers, allocates temp sample matrices and shared matrices, repeatedly polls until the initial `HISTORY` samples are valid, copies initial data, then launches a thread. The thread polls `PVFS_mgmt_perf_mon_list`, shifts new valid samples into the shared ring, updates end times, signals the condition, unlocks, and sleeps.

## State And Persistence
All state is process memory: global shared buffer, synchronization objects, thread ID, allocated matrices, and PVFS system state. `pvfs2_vis_stop` cancels the thread and finalizes PVFS.

## Dependencies And Integration Points
Depends on pthreads, `pvfs2.h`, `pvfs2-mgmt.h`, and management perf monitor APIs. Used by `pvfs2-vis-bw-2d.c` and `simple.c`.

## Risks And Test Signals
Risks include memory leaks on partial allocation failures, no cleanup of `args`, cancellation without joining, condition signaling with questionable mutex handling on error, credential refresh absence in the polling loop, and API signature sensitivity across OrangeFS versions. Test signals are startup on valid/invalid mount, polling multiple servers, consumer wakeups, stop/finalize behavior, and induced management-call failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.c -->
