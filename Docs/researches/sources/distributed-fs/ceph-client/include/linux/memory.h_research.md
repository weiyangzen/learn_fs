<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory.h -->
# sources/distributed-fs/ceph-client/include/linux/memory.h

## Purpose
This header defines generic memory-block and memory-group device model structures used for memory hotplug and sysfs topology.

## Important APIs, types, and functions
`struct memory_group` groups memory blocks for a memory device or NUMA node and tracks present kernel/movable pages. `enum memory_block_state` names sysfs-visible and internal online/offline transitions. `struct memory_block` represents a hotpluggable memory block with section number, state, online type, nid, zone, device, altmap, group linkage, and hwpoison counter. APIs include memory block sizing, notifier registration, memory notification, memory block device create/remove/find/walk, memory group register/unregister/find/walk, ID conversion helpers, `memory_block_advise_max_size`, and global `text_mutex`.

## Control flow
Hotplug code creates memory block devices for physical ranges, exposes state through sysfs, notifies registered callbacks during online/offline transitions, groups blocks by memory device, and removes block devices on hotremove. Disabled hotplug builds provide benign stubs.

## State and persistence
Runtime state is in memory block devices, group lists and counters, device locks, online state, zone association, and optional hwpoison counts. It reflects physical memory topology and sysfs state rather than persistent storage.

## Dependencies and integration points
It depends on node, mutex, memory hotplug, device model, sparsemem sections, altmaps, and notifier blocks. It integrates drivers/base memory sysfs, CXL/HMAT/memory tiers, KSM, cpusets, slab, and code-patching `text_mutex` users.

## Risks and test signals
Risks include state transition races, wrong block size/order, multi-zone blocks with NULL zone, group counter drift, notifier priority interactions, and hotplug-disabled call paths. Test online/offline sysfs transitions, notifier ordering, group registration, block walking, section-to-block conversions, hwpoison accounting, and advised max size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory.h -->
