# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.c

Purpose: Provides shared SPARC Open Firmware platform-device helpers for IRQ/resource lookup, MMIO mapping, archdata propagation, default bus translation, and SBUS matching.

Important APIs/types/functions: `irq_of_parse_and_map()` returns precomputed platform-device IRQs. `of_address_to_resource()` copies prebuilt resources. `of_iomap()` maps a resource through `of_ioremap()`. `of_propagate_archdata()` recursively copies IOMMU, streaming cache, host controller, NUMA node, and DMA ops from a bus device to descendants. Translation helpers include `of_bus_default_count_cells()`, `of_out_of_range()`, `of_bus_default_map()`, `of_bus_default_get_flags()`, `of_bus_sbus_match()`, and `of_bus_sbus_count_cells()`.

Control flow: Architecture-specific OF scanners build platform devices and resources first. Generic users later call these helpers to retrieve IRQs, resources, and mapped MMIO from the existing platform device associated with a node. Address translation verifies a child address lies in a parent range, adds the child offset to the parent base, and returns new parent cells.

State and persistence: The file owns no persistent global state. It reads and writes already-created `platform_device` archdata and resources.

Dependencies and integration points: It depends on Linux OF/platform APIs, SPARC archdata fields, common header `of_device_common.h`, resource APIs, and architecture-specific `of_ioremap()`.

Risks and test signals: Callers get `0`, `NULL`, or `-EINVAL` when no platform device exists or the index is out of range, so probe ordering matters. Translation handles only up to two size cells. Tests include `of_iomap()` for every resource type, archdata propagation through nested buses, SBUS hierarchy matching, out-of-range ranges, and invalid indexes.
