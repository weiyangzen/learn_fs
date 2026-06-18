<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_interrupts.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_interrupts.h

## Purpose
`sdca_interrupts.h` defines the SDCA interrupt allocation and dispatch contract. It maps up to 31 SDCA control interrupt positions onto regmap IRQ infrastructure and records enough context for per-control handlers.

## Important APIs, types, and functions
`SDCA_MAX_INTERRUPTS` reserves 31 usable interrupt bits. `struct sdca_interrupt` stores the IRQ name, owning device, device and function regmaps, ASoC component, function/entity/control pointers, private handler data, and assigned IRQ number. `struct sdca_interrupt_info` owns the `regmap_irq_chip`, `regmap_irq_chip_data`, fixed interrupt array, and `irq_lock`. APIs include `sdca_irq_allocate()`, `sdca_irq_request()`, `sdca_irq_free()`, `sdca_irq_data_populate()`, `sdca_irq_populate_early()`, `sdca_irq_populate()`, `sdca_irq_cleanup()`, and early/normal enable and disable helpers.

## Control flow
SDCA code allocates an interrupt container against a device regmap and parent IRQ, populates early function-level data, later binds component/control context after the ASoC component exists, requests handlers per SDCA interrupt position, and enables or disables interrupt bits around function initialization and runtime operation.

## State and persistence behavior
Interrupt state is runtime-only and protected by `irq_lock`. The fixed interrupt array carries control-specific handler context across IRQ callbacks until cleanup. No persistent state exists beyond hardware interrupt masks and regmap state.

## Dependencies and integration points
It depends on Linux IRQs, mutexes, regmap IRQ chips, ASoC components, and parsed SDCA function/entity/control metadata. It is the integration point for jack, HID, control-change, and component-specific SDCA event handlers.

## Risks and test signals
Risks include off-by-one use of the reserved interrupt bit, stale control pointers after function cleanup, enable-order races between early and full population, handler/private-data mismatches in `sdca_irq_free()`, and regmap IRQ masking bugs. Test signals include multi-function interrupt sharing, every valid interrupt position, controls with no interrupt, early status clearing, concurrent request/free, suspend/resume disable/enable, and jack/HID report delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_interrupts.h -->
