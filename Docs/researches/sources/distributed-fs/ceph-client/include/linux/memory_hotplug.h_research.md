<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h

## Purpose
This header defines the core memory hotplug and hotremove interfaces for adding, onlining, offlining, and removing physical memory ranges and their metadata.

## Important APIs, types, and functions
`enum mmop` describes offline/default/kernel/movable online operations. Hotplug builds define `mhp_t` flags `MHP_MERGE_RESOURCE`, `MHP_MEMMAP_ON_MEMORY`, and `MHP_NID_IS_MGID`, plus `struct mhp_params` for altmap, pgprot, and dev_pagemap. APIs cover `pfn_to_online_page`, pluggable range queries, memmap-on-memory support, zone span locks, present page count adjustment, memmap init/deinit, online/offline pages, online page callbacks, node online/offline, architecture add/remove memory, adding pages/sections/memory/resources/driver-managed memory, online memory locking, hotplug begin/done, zone selection, linear mappings, and pgdat resizing. Disabled builds provide stubs.

## Control flow
Hotplug callers validate ranges, create mappings and memmap, add sparse sections, create memory block devices, then online pages into a selected zone. Hotremove offlines pages, isolates/removes sections, tears down linear mappings, and may offline nodes. Global hotplug locks serialize online memory operations and zone/pgdat span updates.

## State and persistence
Runtime state includes zone spans, pgdat node sizes, sparsemem sections, online page callbacks, default online type, movable-node setting, memory resources, and memmap-on-memory metadata. Physical memory presence persists in firmware/device state; kernel state is rebuilt on boot/hotplug.

## Dependencies and integration points
It depends on mm zones, spinlocks, notifiers, resources, altmaps, dev_pagemap, sparsemem, architecture mapping hooks, and memory block sysfs. It integrates CXL/NVDIMM/device memory, memory tiers, NUMA, reclaim, and platform hotplug.

## Risks and test signals
Risks include zone span lock misuse, invalid memmap-on-memory alignment, resource merge pointer invalidation, node/group ID confusion with `MHP_NID_IS_MGID`, offline failures due to pinned pages, and disabled-config stubs hiding unsupported operations. Test add/online/offline/remove, movable and kernel online types, memmap-on-memory, driver-managed memory, altmap ranges, resource merge, node on/offline, and concurrent hotplug serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory_hotplug.h -->
