<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memory_hotplug.c -->
# sources/distributed-fs/ceph-client/mm/memory_hotplug.c

## Purpose

`memory_hotplug.c` implements the core Linux memory hotplug and hotremove paths for adding, onlining, offlining, and removing physical memory ranges. It coordinates resource reservation, sparsemem section creation/removal, node and zone span updates, memory block device registration, page onlining callbacks, memmap-on-memory altmaps, automatic `ZONE_MOVABLE` policy, and memory removal migration/isolation. The complete 2432-line file was read.

## Important APIs, Types, and Functions

Exported and externally consumed APIs include `get_online_mems()`, `put_online_mems()`, `mem_hotplug_begin()`, `mem_hotplug_done()`, `mhp_get_default_online_type()`, `mhp_set_default_online_type()`, `pfn_to_online_page()`, `__add_pages()`, `__remove_pages()`, `set_online_page_callback()`, `restore_online_page_callback()`, `generic_online_page()`, `move_pfn_range_to_zone()`, `adjust_present_page_count()`, `mhp_supports_memmap_on_memory()`, `add_memory_resource()`, `__add_memory()`, `add_memory()`, `add_memory_driver_managed()`, `mhp_get_pluggable_range()`, `mhp_range_allowed()`, `try_online_node()`, `try_offline_node()`, `remove_memory()`, and `offline_and_remove_memory()`. Internal state and helper types include `memmap_mode`, `online_policy`, `auto_movable_ratio`, `auto_movable_numa_aware`, `online_page_callback`, the static percpu `mem_hotplug_lock`, `movable_node_enabled`, `mhp_default_online_type`, `auto_movable_stats`, and `auto_movable_group_stats`.

## Control Flow

Adding normal memory starts by reserving an `iomem_resource` child in `register_memory_resource()`, then `add_memory_resource()` validates memory-block alignment, resolves memory-group IDs, serializes with `mem_hotplug_begin()`, optionally updates memblock metadata, initializes/registers a previously offline node, calls either `arch_add_memory()` or per-memory-block `create_altmaps_and_memory_blocks()` for memmap-on-memory, creates memory block devices, links them under the node, adds firmware-map entries for ordinary `System RAM`, releases the hotplug write lock, optionally merges the resource, and auto-onlines memory blocks according to `mhp_get_default_online_type()`.

Onlining a memory block calls `online_pages()` under the hotplug write lock. It moves the PFN range into the selected zone with `move_pfn_range_to_zone()`, notifies node and memory hotplug listeners, adjusts isolated pageblock accounting, initializes zone pagesets if this is the first population of a zone, frees pages through `online_pages_range()` and the registered `online_page_callback`, updates present-page accounting and node states, rebuilds zonelists when needed, undoes page isolation, shuffles the zone, recalculates watermarks, starts `kswapd`/`kcompactd`, updates writeback limits, and emits `MEM_ONLINE`.

Offlining under `CONFIG_MEMORY_HOTREMOVE` is the inverse but more complex. `offline_pages()` rejects holes and multizone ranges, disables per-cpu page lists and LRU cache draining, isolates the range, sends last-memory and going-offline notifications, repeatedly scans for movable pages with `scan_movable_pages()`, migrates them with `do_migrate_range()`, dissolves free hugetlb folios, verifies isolation, removes isolated free pages from the buddy with `__offline_isolated_pages()`, updates managed/present counts and node states, stops reclaim/compaction threads for memoryless nodes, sends `MEM_OFFLINE`, and shrinks zone/node spans with `remove_pfn_range_from_zone()`. Removing memory requires all memory block devices to be offline, removes firmware-map entries, tears down memory block devices, removes arch memory or per-block altmaps, removes memblock and resource state, and may unregister an empty node.

## State and Persistence Behavior

Persistent runtime state spans kernel parameters, node/zone metadata, memory block devices, `/proc/iomem` resources, firmware-map entries, memblock metadata on architectures that keep it, and memory-group present-page counters. `memmap_on_memory`, `online_policy`, `auto_movable_ratio`, and `auto_movable_numa_aware` are module parameters. The hotplug lock serializes structural changes against users that call `get_online_mems()`. Zone and pgdat spans persist after onlining and are shrunk during removal when possible. Memmap-on-memory stores altmap pointers in each `memory_block` and must free all altmap allocations during remove.

## Dependencies and Integration Points

This file integrates with sparsemem (`sparse_add_section()`, `sparse_remove_section()`), architecture hotplug hooks (`arch_add_memory()`, `arch_remove_memory()`, `arch_get_mappable_range()`), memory block sysfs devices, node registration, memblock, firmware maps, resource management, page allocator zones, page isolation and migration, hugetlb, KASAN zero shadow setup, kswapd/kcompactd, writeback throttling, memory notifiers, node notifiers, device hotplug locking, memory groups such as virtio-mem style dynamic groups, and `memremap.c` through `ZONE_DEVICE` and `get_dev_pagemap()`.

## Risks and Edge Cases

Alignment is critical: hotplug operations generally require memory-block or section granularity, while memmap-on-memory introduces pageblock-aligned exceptions. Incorrect zone selection can break kernel/movable memory ratios or create overlapping zone spans. Offlining can fail because of signals, holes, pages with unmovable references, migration failures, hugetlb dissolution failure, notifier vetoes, CPUs still associated with a node, or racing sysfs online attempts. Altmap accounting is fragile because every per-block vmemmap allocation must be undone. `pfn_to_online_page()` has a special slow path for sections tainted by `ZONE_DEVICE` subsection collisions. Resource names control whether memory is considered driver-managed, so malformed names or wrong flags affect kexec and firmware-map behavior.

## Test Signals

Useful tests include memory hotplug selftests for add/online/offline/remove, sysfs memory block onlining across `online_kernel`, `online_movable`, and automatic policies, NUMA node first/last memory notifier coverage, failure-injection of memory and node notifiers, hotremove with busy/unmovable/hugetlb/DMA-pinned pages, altmap and memmap-on-memory add/remove with leak checks, dynamic memory group ratio tests, resource conflict and out-of-mappable-range tests, `movable_node` boot-parameter behavior, and stress tests racing onlining/offlining with allocation, migration, and cpuset changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memory_hotplug.c -->
