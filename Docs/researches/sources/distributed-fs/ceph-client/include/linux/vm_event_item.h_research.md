# sources/distributed-fs/ceph-client/include/linux/vm_event_item.h

## Purpose
`vm_event_item.h` defines the enumeration of VM event counters used by Linux memory-management statistics. It is the shared item list consumed by `vmstat.h`, `/proc/vmstat`, tracing, reclaim, migration, THP, NUMA balancing, swap, and debug accounting code.

## Important APIs, Types, and Functions
The file defines zone-expansion helper macros `DMA_ZONE()`, `DMA32_ZONE()`, `HIGHMEM_ZONE()`, `DEVICE_ZONE()`, and `FOR_ALL_ZONES()`. The main API is `enum vm_event_item`, starting with IO and swap counters (`PGPGIN`, `PGPGOUT`, `PSWPIN`, `PSWPOUT`), zone-expanded allocation/reclaim counters, page lifecycle counters, reclaim/kswapd counters, OOM, NUMA balancing, migration, compaction, hugetlb, CMA, unevictable list activity, THP, ballooning, TLB flush debug, swap zero-page/zswap/KSM events, x86 direct-map split/collapse, per-VMA lock stats, and stack-usage buckets. `NR_VM_EVENT_ITEMS` terminates the enum. When transparent huge pages are disabled, selected THP file counters are replaced with `BUILD_BUG()` expressions to catch accidental use.

## Control Flow
The header itself has no runtime control flow. Its enum values become indexes into per-CPU `vm_event_state.event[]` arrays and into the `vmstat_text[]` name table. Conditional compilation controls which counters exist for a given kernel build; callers must only reference counters enabled by the same config.

## State and Persistence
No state is stored here. Persistence-like behavior comes from the stable ordering expected between this enum and generated/user-visible vmstat names. The counters using these items are in-memory and accumulate until boot reset or per-CPU folding, not durable storage.

## Dependencies and Integration Points
The header depends on `linux/thread_info.h` for `THREAD_SIZE` stack buckets and on many `CONFIG_*` symbols. It integrates directly with `vmstat.h`, memory reclaim, page allocator, migration, compaction, THP, swap, balloon, zswap, x86 page-table mapping, and debug accounting call sites.

## Risks
Changing enum order or config guards can break `/proc/vmstat` interpretation and userspace tooling. Referencing disabled counters either fails compilation through `BUILD_BUG()` or silently disappears behind config-specific accounting wrappers. Zone-expanded counter counts must stay aligned with zone definitions. Adding counters requires matching text names and audit of all build configurations.

## Test Signals
Build coverage across NUMA, THP, swap, migration, compaction, highmem, device-zone, and debug configs is the primary signal. Runtime signals include expected `/proc/vmstat` names and monotonic changes during allocation, reclaim, compaction, swap, THP fault/split, and OOM stress tests.
