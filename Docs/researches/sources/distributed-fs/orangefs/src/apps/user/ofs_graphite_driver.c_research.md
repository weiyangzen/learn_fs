<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c

## Purpose
Continuously polls OrangeFS server performance counters or timers and emits metrics to stdout and/or a Graphite plaintext endpoint.

## Important APIs, Types, And Functions
`options` captures mount point, Graphite host, name prefix, single-server selection, counter/timer type, key/history/frequency settings, raw/print/debug flags. `GRAPHITE_CNT` computes raw or delta counter samples and writes/prints them. `GRAPHITE_TIMER` emits sum/average/count/min/max timer values. `main` initializes OrangeFS, resolves the mount, discovers I/O servers, allocates performance matrices, calls `PVFS_mgmt_perf_mon_list` in an infinite loop, formats metric names, and tracks last samples. `parse_args`, `usage`, `graphite_connect`, and `print_sample` support setup.

## Control Flow
After defaults are filled, the tool optionally connects to Graphite, initializes PVFS, resolves the mount point, gets I/O server addresses, and enters a polling loop. Each loop refreshes credentials, fetches up to `history` samples, skips the very first sample to avoid counter discontinuity, emits selected counter/timer names, saves the last sample per server, and sleeps.

## State And Persistence
Runtime state includes dynamically allocated matrices, per-server last samples, next sample IDs, server names, and the Graphite socket. It writes no local files but publishes external metrics.

## Dependencies And Integration Points
Depends on `pvfs2.h`, `pvfs2-mgmt.h`, `pvfs2-internal.h`, POSIX sockets, DNS, and Graphite port 2003. It is an operational monitoring integration for OrangeFS performance monitor APIs.

## Risks And Test Signals
Risks include DEBUG always enabled, infinite loop with limited cleanup, sending NUL bytes with metrics, possible server-index mismatch when single-server mode narrows arrays, unchecked `strcat` into metric name buffers, and dependence on internal counter enum ordering. Test signals are counter and timer polling against a test cluster, single-server selection, Graphite listener output validation, raw versus delta output, credential refresh, and handling of unreachable Graphite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_graphite_driver.c -->
