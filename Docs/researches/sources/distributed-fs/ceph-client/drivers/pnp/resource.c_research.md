# sources/distributed-fs/ceph-client/drivers/pnp/resource.c

## Purpose
`resource.c` is the core PnP resource-registration and resource-conflict helper for the Linux PnP bus in this source tree. It lets protocol parsers record possible IRQ, DMA, I/O, memory, and bus resources on a `struct pnp_dev`; validates proposed current resources against kernel resource ownership, user-reserved ranges, PCI legacy IRQ use, and other PnP devices; and exports lookup/add/possible-config helpers used by PnP protocol and driver code.

## Important APIs, Types, and Functions
Key APIs are `pnp_register_irq_resource()`, `pnp_register_dma_resource()`, `pnp_register_port_resource()`, `pnp_register_mem_resource()`, `pnp_free_options()`, `pnp_check_port()`, `pnp_check_mem()`, `pnp_check_irq()`, `pnp_check_dma()` when ISA DMA is enabled, `pnp_resource_type()`, `pnp_get_resource()`, `pnp_add_resource()` and typed add helpers, `pnp_possible_config()`, and `pnp_range_reserved()`. Static boot parameter arrays `pnp_reserve_irq`, `pnp_reserve_dma`, `pnp_reserve_io`, and `pnp_reserve_mem` feed `__setup()` parsers.

## Control Flow
Protocol code first registers option descriptors through `pnp_build_option()` and typed wrappers, then assignment paths add current resources to `dev->resources`. Checkers short-circuit disabled resources, probe global kernel reservations with `request_region()`, `request_mem_region()`, `request_irq()`, or `request_dma()`, compare against boot-reserved ranges, check intra-device duplicates, and walk all PnP devices for conflicts. IRQ checking additionally rejects IRQs above 15, consults PCI devices including legacy IDE compatibility IRQs, and then tests requestability.

## State and Persistence Behavior
Software state lives in the `dev->options` and `dev->resources` lists and in static boot-parameter reservation arrays initialized to `-1`. Resource additions copy a `struct resource` and set names to the PnP device name. Hardware/resource-manager state is not permanently claimed by the check paths except for transient request/release probes; actual ownership is represented by resources and later driver activation.

## Dependencies and Integration Points
It depends on PnP core list helpers, Linux resource management, IRQ and ISA DMA APIs, PCI iteration when configured, libata legacy IRQ helpers, boot-parameter parsing through `get_option()`, and debug helpers from `base.h`. Exported symbols integrate with PnP protocol drivers, PnP client drivers, and system-resource reservation logic.

## Risks and Edge Cases
The range macros take pointers and assume `end >= start`; malformed resources can underflow length calculations. Boot-reserved I/O and memory ranges are stored as `int`, which is narrower than `resource_size_t` on wide-address systems. Conflict checks walk global PnP device lists without local locking in this file, relying on PnP core serialization. PCI legacy IRQ handling is x86/ISA-centric and intentionally conservative. `pnp_possible_config()` only matches exact `min` and `size` for I/O and memory, not all possible aligned alternatives.

## Test Signals
Build with PnP, PCI on/off, and ISA DMA on/off. Exercise resource parsing, disabled resources, overlapping same-device resources, cross-device overlaps, boot parameters `pnp_reserve_irq/dma/io/mem`, PCI IDE legacy IRQ conflicts, and exported helper lookups. Fault-inject allocation failure for option/resource additions and verify no leaked list entries.
