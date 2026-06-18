<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c

## Purpose
`lproc_mdc.c` exposes MDC tunables and diagnostics through sysfs/lprocfs/debugfs. It lets operators inspect and change import activity, RPC concurrency, dirty/cache limits, checksums, DOM inline reply sizing, LSOM updates, grant shrink behavior, adaptive timeout parameters, and runtime statistics.

## Important APIs, Types, And Functions
Primary entry point is `mdc_tunables_init()`. Attribute handlers include `active_show/store`, `max_rpcs_in_flight_show/store`, `max_mod_rpcs_in_flight_show/store`, `max_dirty_mb_show/store`, `checksums_show/store`, `checksum_dump_show/store`, `dom_min_repsize_show/store`, `lsom_show/store`, grant shrink handlers, and grant byte readers. Seq/debugfs handlers include `mdc_cached_mb`, `mdc_unstable_stats`, `mdc_rpc_stats`, `mdc_batch_stats`, and `mdc_stats`.

## Control Flow
`mdc_tunables_init()` attaches the sysfs attribute group and debugfs variable table, sets up OBD lprocfs state, allocates metadata stats, attaches sptlrpc proc entries, and registers ptlrpc proc information. Store handlers parse booleans, integers, or memory sizes, then update `obd_import`, `client_obd`, OSC cache, or adaptive timeout fields under the appropriate locks. Seq write handlers clear histograms or shrink caches; seq show handlers print current counters and histograms.

## State And Persistence
State lives in `struct obd_device`, `struct client_obd`, `struct obd_import`, OSC stats, lprocfs histograms, and ptlrpc registration. Tunables persist for the lifetime of the MDC import/device and directly influence live RPC scheduling, dirty cache behavior, checksum use, grant shrinking, and debug counters.

## Dependencies And Integration Points
The file depends on `obd_class`, `lprocfs_status`, OSC cache/grant APIs, ptlrpc import state, sptlrpc proc attachment, cl environment allocation for LRU shrinking, and common Lustre attribute macros.

## Risks And Edge Cases
User input validation is critical because these knobs can throttle or disrupt metadata/data paths. Dirty limits are capped at one quarter RAM and maximum MB bounds. Import access must be protected by `with_imp_locked()` and reference helpers. Grant shrink toggling modifies import flags under spinlock.

## Test Signals
Test sysfs reads/writes for every attribute, invalid parse and range failures, active import toggling, RPC concurrency changes under load, dirty-cache shrink requests, checksum toggles, histogram reset/show, grant shrink interval updates, lprocfs setup failure unwinds, and concurrent reads while imports disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c -->
