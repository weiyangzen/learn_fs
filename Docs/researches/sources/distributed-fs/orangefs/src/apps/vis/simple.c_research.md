<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/simple.c -->
# sources/distributed-fs/orangefs/src/apps/vis/simple.c

## Purpose
Minimal text-mode visualization smoke test. It starts the shared visualization poller and prints the latest read counter from server 0 for five updates.

## Important APIs, Types, And Functions
`options` stores only the mount point. `main` parses `-m`, calls `pvfs2_vis_start`, waits on `pint_vis_cond`, prints `pint_vis_shared.io_perf_matrix[0][depth-1].read`, checks `pint_vis_error`, then stops the poller. `parse_args` and `usage` handle the mount argument and version flag.

## Control Flow
After startup the program performs exactly five blocking waits. Each wake prints one sample and unlocks the mutex. It then calls `pvfs2_vis_stop` and exits.

## State And Persistence
No persistent state. Runtime state is the shared visualization globals managed by `pvfs2-vis.c` and the parsed mount string.

## Dependencies And Integration Points
Depends on pthreads, OrangeFS management headers, and the visualization backend. Useful as a non-SDL smoke consumer of `pvfs2_vis_start`.

## Risks And Test Signals
Risks include assuming at least one I/O server, waiting without a predicate loop, memory leak for parsed mount path, and returning without unlocking if `pint_vis_error` is seen. Test signals are five printed samples on an active mount, invalid mount failure, and error propagation from the polling thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/vis/simple.c -->
