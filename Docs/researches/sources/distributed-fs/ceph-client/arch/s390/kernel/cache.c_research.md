# sources/distributed-fs/ceph-client/arch/s390/kernel/cache.c

## Purpose
Extracts s390 cache topology and attributes through ECAG and exposes them through generic Linux cacheinfo/sysfs and `/proc/cpuinfo` style output.

## Important APIs, Types, And Functions
`show_cacheinfo()` prints cache leaves. `init_cache_level()` determines level and leaf count. `populate_cache_leaves()` fills `struct cacheinfo` entries. Internal helpers include `get_cache_type()`, `ecag()`, and `ci_leaf_init()`. `union cache_topology` decodes per-level scope/type fields.

## Control Flow
Initialization reads ECAG topology once per CPU, counts cache levels until no valid cache appears, then populates each leaf with line size, associativity, size, set count, type, level, and shared/private state. Separate instruction/data cache levels produce two leaves.

## State And Persistence
State is stored in generic per-CPU `cpu_cacheinfo` structures. No persistent storage is used. Shared caches are marked with `disable_sysfs`, reflecting limited per-CPU ownership.

## Dependencies And Integration Points
Depends on `linux/cacheinfo.h`, CPU masks, seq files, and s390 facility ECAG. It integrates with generic cache sysfs and CPU reporting.

## Risks And Edge Cases
ECAG values must be nonzero and internally consistent or set-count division can misbehave. Cache levels above `CACHE_MAX_LEVEL` are ignored. Private/shared mapping affects sysfs visibility.

## Test Signals
Signals include cacheinfo sysfs inspection on multiple machine generations, CPU hotplug cache population, ECAG emulation tests, and sanity checks for line size, associativity, and number of sets.
