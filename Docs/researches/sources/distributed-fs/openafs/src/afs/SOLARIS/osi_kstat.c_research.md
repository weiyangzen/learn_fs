# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_kstat.c

## Purpose
Solaris kstat provider exposing OpenAFS cache-manager parameters, cache statistics, and Rx network statistics.

## Important APIs, Types, and Functions
Defines kstat data structs `afs_param_kstat`, `afs_cache_kstat`, `afs_rx_kstat`, update handlers `afs_param_ks_update`, `afs_cache_ks_update`, `afs_rx_ks_update`, and lifecycle functions `afs_kstat_init`/`afs_kstat_shutdown`.

## Control Flow
Initialization creates virtual named kstats `openafs:param`, `openafs:cache`, and `openafs:rx`, fills primary cell name, assigns update callbacks, adjusts string data size, and installs each kstat if creation succeeds. Update callbacks reject writes with `EACCES` and copy values from `cm_initParams`, `afs_stats_cmperf`, global cache counters, `AFSVersion`, and `rx_stats`. Shutdown deletes installed kstats and clears pointers.

## State and Persistence
Maintains static kstat handles and static `cellname`. Exposes live counters but does not persist them.

## Dependencies and Integration Points
Depends on Solaris kstat, OpenAFS cell/cache/stat structures, Rx atomic stats, and AFS global lock precondition noted for init.

## Risks
Virtual kstat structs must match named count and string sizing. Some Rx fields are atomic and some are not, so snapshots are approximate. Missing primary cell becomes `-UNKNOWN-`.

## Test Signals
After module init, `kstat` should list all three groups. Reads should update counters and reject writes. Shutdown should remove kstats. Validate cell/version strings and representative cache/Rx counters under activity.
