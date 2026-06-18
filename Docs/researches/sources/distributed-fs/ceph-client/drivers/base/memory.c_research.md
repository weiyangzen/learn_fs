# sources/distributed-fs/ceph-client/drivers/base/memory.c

## Purpose
Implements the driver-core sysfs representation of sparse physical memory as `/sys/devices/system/memory/memoryN`, plus memory hotplug control, memory-block lookup, memory-block-to-node linking support, memory groups, and optional memory-failure controls.

## Important APIs, Types, And Functions
Exports memory hotplug entry points such as `register_memory_notifier()`, `unregister_memory_notifier()`, `memory_notify()`, `memory_block_size_bytes()`, `create_memory_block_devices()`, `remove_memory_block_devices()`, `walk_memory_blocks()`, `for_each_memory_block()`, and memory group APIs `memory_group_register_static()`, `memory_group_register_dynamic()`, and `memory_group_unregister()`. Internal state is organized around `struct memory_block` devices stored in the `memory_blocks` xarray and `struct memory_group` objects stored in the marked `memory_groups` xarray. Sysfs attributes expose `phys_index`, `state`, `phys_device`, `removable`, optional `valid_zones`, root-level `block_size_bytes`, `auto_online_blocks`, hotplug `probe`, crash-hotplug support, and memory-failure page offlining.

## Control Flow
Boot initialization through `memory_dev_init()` validates the architecture block size, registers the `memory` subsystem bus, calculates `sections_per_block`, and creates one memory-block device per present sparsemem block. Hot-add flows call `create_memory_block_devices()`, which checks block alignment, creates offline blocks with `add_memory_block()`, registers devices, and rolls back created blocks on failure. Sysfs writes to `state` parse `online`, `online_kernel`, `online_movable`, or `offline`, take the device hotplug sysfs lock, and call `device_online()` or `device_offline()`. Bus `.online`/`.offline` callbacks serialize through the device lock, transition `mem->state`, and call `online_pages()` or `offline_pages()` under `mem_hotplug_begin()`/`mem_hotplug_done()`.

## State And Persistence
State persists in kernel objects and sysfs, not on disk. `mem->state`, `online_type`, `nid`, `zone`, `altmap`, `group`, and hardware-poison counters determine whether a block can be onlined/offlined and where it belongs. The `memory_blocks` xarray is the fast lookup index; `memory_groups` tracks static and dynamic hotplug grouping and uses `MEMORY_GROUP_MARK_DYNAMIC` for iteration. Memory block devices hold references via `get_device()` and are released by `memory_block_release()`, which warns if altmap cleanup was missed.

## Dependencies And Integration
Depends on SPARSEMEM, memory hotplug core (`online_pages()`, `offline_pages()`, `zone_for_pfn_range()`), NUMA node support, memblock boot discovery, sysfs, notifier chains, xarray, memory failure, kexec crash hotplug, and architecture hooks such as `memory_block_size_bytes()` and `arch_get_memory_phys_device()`. `node.c` calls `memory_block_add_nid_early()` and `unregister_memory_block_under_nodes()` to maintain memory-node links.

## Risks And Test Signals
Main risks are hotplug locking mistakes, reference leaks around xarray/device lookup, partial hot-add rollback failures, incorrect zone selection for blocks spanning zones or nodes, altmap accounting mismatches, and ABI regressions in long-lived sysfs files. Test signals include memory hotplug on/offline tests, NUMA sysfs link checks, memory-failure injection, `valid_zones` output, dynamic/static memory group lifecycle tests, and boot-time creation of all present memory blocks.
