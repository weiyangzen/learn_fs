# sources/distributed-fs/ceph-client/drivers/dax/kmem.c

Purpose: DAX driver that converts dev_dax ranges into managed System RAM using memory hotplug.

Important APIs/types/functions: `dax_kmem_range()`, memory-tier helpers, `dev_dax_kmem_probe()`, CONFIG_MEMORY_HOTREMOVE-gated `dev_dax_kmem_remove()`, `device_dax_kmem_driver`, and module init/exit.

Control flow and state: probe validates target NUMA node, calculates abstract distance/memory type, aligns ranges to memory-block boundaries, warns about truncation, initializes node memory type, allocates driver data and static memory group, reserves each range as System RAM, and calls `add_memory_driver_managed()` with optional `MHP_MEMMAP_ON_MEMORY`. Remove attempts `remove_memory()` for each range; failures mark `any_hotremove_failed` and intentionally preserve resource/name state until reboot.

Dependencies and integration: depends on memory hotplug, memory tiers, memremap/pagemap, DAX bus, NUMA, resource reservation, and kmem DAX matching via `IORESOURCE_DAX_KMEM`.

Risks and test signals: irreversible hotremove failures, range truncation, invalid target node, memory type lifetime, request_mem_region conflicts, and memmap-on-memory support are high-risk. Test binding/unbinding with memory offline/online, mixed range alignment, target-node absence, memmap_on_memory true/false, resource conflicts, no CONFIG_MEMORY_HOTREMOVE behavior, and kexec resource naming.
