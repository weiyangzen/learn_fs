<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h -->
# sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h

## Purpose
Declares the visualization polling API and shared state used by OrangeFS visualization clients.

## Important APIs, Types, And Functions
Defines `struct pvfs2_vis_buffer` with I/O server count, history depth, performance matrix, and end-time array. Declares `pvfs2_vis_start(char *path, int update_interval)` and `pvfs2_vis_stop(void)`. Extern declarations expose `pint_vis_shared`, `pint_vis_error`, `pint_vis_mutex`, and `pint_vis_cond`.

## Control Flow
Consumers call `pvfs2_vis_start`, wait on `pint_vis_cond` while holding `pint_vis_mutex`, read `pint_vis_shared`, check `pint_vis_error`, and eventually call `pvfs2_vis_stop`.

## State And Persistence
The header itself stores no state but defines the process-global state contract exported by `pvfs2-vis.c`.

## Dependencies And Integration Points
Requires pthreads and `struct PVFS_mgmt_perf_stat`/`uint64_t` declarations from included OrangeFS headers in consumers. It is the common interface for SDL and simple text visualizers.

## Risks And Test Signals
Risks are exposing mutable globals directly, ABI drift in `PVFS_mgmt_perf_stat`, and consumers misusing the condition variable without a predicate. Test signals are compile coverage for all visualization clients and runtime wait/read cycles under concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/pvfs2-vis.h -->
