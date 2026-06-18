<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c

## Purpose
Populates Linux cacheinfo data from OpenRISC cache configuration SPRs.

## Important APIs, Types, And Functions
`init_cache_level()` detects D-cache and I-cache presence, reads `SPR_DCCFGR`/`SPR_ICCFGR`, derives ways, sets, line size, and total size, and sets per-CPU leaf counts. `populate_cache_leaves()` fills `struct cacheinfo` leaves and D-cache write policy.

## Control Flow
Generic cacheinfo initialization calls level discovery first, then leaf population. Missing UPR or no caches returns `-ENOENT`.

## State And Persistence
Stores derived cache descriptors in `cpuinfo_or1k` and Linux per-CPU cacheinfo structures. Hardware cache configuration is read-only here.

## Dependencies And Integration Points
Depends on `SPR_UPR`, cache configuration masks, `cpu_cache_is_present()`, and generic cacheinfo sysfs.

## Risks
Uses `smp_processor_id()` for CPU info while accepting a `cpu` argument; unusual call contexts could describe the wrong CPU. Wrong bit decoding misreports cache geometry.

## Test Signals
`/sys/devices/system/cpu/cpu*/cache` contents, boot logs for cache geometry, and SMP systems with per-CPU cache data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/cacheinfo.c -->
