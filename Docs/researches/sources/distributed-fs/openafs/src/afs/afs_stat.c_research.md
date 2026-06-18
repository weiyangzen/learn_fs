# sources/distributed-fs/openafs/src/afs/afs_stat.c

## Purpose

`afs_stat.c` defines and initializes the Cache Manager statistics globals. It is the concrete storage for the structures declared in `afs_stats.h`: `afs_cmstats`, `afs_stats_cmperf`, `afs_stats_cmfullperf`, and `afs_stats_XferSumBytes`. Its only function, `afs_InitStats`, prepares call counters, performance counters, timing minima, transfer minima, server bucket metadata, and cache-entry size fields during Cache Manager startup.

## Important APIs, Types, and Functions

The primary API is `afs_InitStats(void)`. It works with `struct afs_CMStats`, `struct afs_stats_CMPerf`, `struct afs_stats_CMFullPerf`, `struct afs_stats_opTimingData`, and `struct afs_stats_xferData`. It also records size information for `struct vcache` and platform vnode structures. On Darwin, `AFS_SIZEOF_VNODE` is pinned to a known vnode zone size because `struct vnode` is opaque to the shipped SDK headers; other platforms use `sizeof(struct vnode)`.

## Control Flow and State

Initialization zeroes the three global stats structures, sets `srvNumBuckets` to `NSERVERS`, initializes every file-server and cache-manager RPC timing `minTime.tv_sec` to `999999`, initializes file-server transfer `minTime.tv_sec` and `minBytes`, and then records cache/stat object size metadata. `stat_entry_size` is `sizeof(struct vcache)` plus `sizeof(struct vnode)` unless the build embeds the vnode in the vcache.

## Dependencies and Integration Points

The file depends on `afsincludes.h` for Cache Manager structures and `afs_stats.h` for stats layouts and constants. Runtime consumers include xstat callbacks, server/user stats code, RPC instrumentation macros, cache accounting, and call-counter macros across the AFS client. The initialization values in this file establish sentinel minima expected by `XSTATS_END_TIME` and transfer-stat update code elsewhere.

## Persistence and Side Effects

All state is in-memory and scoped to the current Cache Manager instance. The values become externally observable through xstat collection interfaces and debugging tools, but there is no direct disk persistence. Reinitializing after live use would destroy counters, so the function is intended to run once at startup.

## Risks and Test Signals

Risks include ABI drift in Darwin vnode sizing, missing initialization for new stats arrays added to `afs_stats.h`, and incorrect minima if new timing/transfer buckets are introduced without updating this loop. Test signals include xstat output immediately after startup, minimum RPC/transfer times remaining sane after first successful operation, and build checks for platforms with opaque vnode definitions or embedded vnode configurations.
