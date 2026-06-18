# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_titan.c

## Purpose
Titan/Privateer/Falcon/Granite EV6+Titan platform support with SMP-aware IRQ routing, legacy IRQ setup, Titan dispatch helpers, and family machine vectors. The source was read as part of `subset-b-000628` and contains 423 lines.

## Important APIs, Types, and Functions
Defines `titan_mv` and `privateer_mv`. Important routines are `titan_update_irq_hw`, `titan_enable_irq`, `titan_disable_irq`, `titan_cpu_set_irq_affinity`, `titan_set_irq_affinity`, `titan_device_interrupt`, `titan_srm_device_interrupt`, `init_titan_irqs`, `titan_init_irq`, `titan_legacy_init_irq`, `titan_dispatch_irqs`, `titan_request_irq`, `titan_late_init`, `titan_map_irq`, and `titan_init_pci`.

## Control Flow
IRQ init selects SRM or placeholder interrupt dispatch, clears Titan Cchip DIM masks, and registers Titan level IRQs. Legacy init additionally resets DMA/PIC state. Affinity updates rebuild per-CPU DIM masks with ISA routed to the boot CPU. `titan_dispatch_irqs` receives a hardware mask, filters it for the current CPU, converts highest-priority bits to SRM-like vectors, and re-enters `alpha_mv.device_interrupt`.

## State and Persistence Behavior
`titan_cpu_irq_affinity[4]` and `titan_cached_irq_mask` are protected by `titan_irq_lock`. Hardware state lives in Titan Cchip DIM CSRs, legacy PIC/DMA registers, requested IRQ descriptors for event-counting no-op handlers, and PCI hose resources.

## Dependencies
Depends on `core_titan.h`, Titan error handling, Alpha SMP masks, i8259/DMA helpers, common PCI setup, and machine-vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
`titan_device_interrupt` is a placeholder unless SRM or another dispatch path is installed. Affinity and dispatch priority conversions can misroute or starve IRQs. Legacy vs non-legacy initialization must match the selected board vector.

## Test Signals
Build Titan and Privateer vectors, boot with SRM dispatch, exercise SMP IRQ affinity, inspect `/proc/interrupts` event counts, test PCI devices across hoses, and confirm legacy ISA interrupts only when using the legacy path.
