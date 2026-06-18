<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_counter.h -->
# sources/distributed-fs/ceph-client/include/linux/page_counter.h

## Purpose
This header declares hierarchical page counters used by memory cgroups and device memory cgroups to track usage, limits, watermarks, and memory protection.

## Important APIs, types, and functions
`struct page_counter` contains hot `usage`, v1 `failcnt`, effective min/low and usage accounting fields, watermarks, protection support flags, limit fields (`min`, `low`, `high`, `max`), and parent pointer. Helpers include `page_counter_init()`, `page_counter_read()`, `page_counter_cancel()`, `page_counter_charge()`, `page_counter_try_charge()`, `page_counter_uncharge()`, min/low/high/max setters, `page_counter_memparse()`, `page_counter_reset_watermark()`, and `page_counter_calculate_protection()`.

## Control flow
Counters are initialized with parent linkage and max default. Charging walks/updates hierarchy and can fail with a pointer to the failing counter. Uncharge/cancel reverse charges. Limit setters update thresholds; protection calculation propagates effective min/low values from root to children. Watermark reset snapshots current usage.

## State and persistence
Persistent state includes atomic usage, fail counts, protection accounting, high/max/min/low limits, watermarks, and parent hierarchy. Cacheline padding isolates hot usage from colder fields.

## Dependencies and integration points
It depends on atomics, cacheline layout, page size, memcg/cgroup dmem configs, and memory control group reclaim/OOM logic.

## Risks and test signals
Risks include hierarchical charge leaks, limit races, watermark ordering, failcnt tracking differences between cgroup v1/v2, protection miscalculation, 32-bit maximum differences, and false sharing regressions. Test memcg charge/uncharge under hierarchy, max/high/min/low changes, watermark reset, recursive protection, memparse inputs, 32-bit builds, and concurrent charge stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_counter.h -->
