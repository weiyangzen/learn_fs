# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic.h

## Purpose
`arm-gic.h` defines ARM GICv1/v2 distributor, CPU interface, virtualization control, list-register, and VM control register constants, plus driver hooks for cascaded/child GICs, save/restore, SGIs, and CPU target migration.

## Important APIs, types, and functions
It defines `GIC_CPU_*`, `GIC_DIST_*`, `GICC_*`, `GICD_*`, `GICH_*`, `GICH_LR_*`, `GICH_VMCR_*`, `GICV_*` macros and functions such as `gic_cascade_irq`, `gic_cpu_if_down`, CPU/distributor save/restore, `gic_of_init`, `gic_of_init_child`, `gic_send_sgi`, `gic_get_cpu_id`, `gic_migrate_target`, and `gic_get_sgir_physaddr`.

## Control flow
Drivers program distributor enable/pending/active/priority/target/config registers, use CPU interface IAR/EOI/deactivate paths, optionally cascade child controllers, save/restore state over PM, and send SGIs for IPIs.

## State and persistence
State is mostly hardware register state; driver-owned `struct gic_chip_data` is forward-declared. Save/restore helpers preserve CPU and distributor state across suspend.

## Dependencies and integration points
It integrates with irqdomains, DT probing, ARM interrupt entry, KVM GICv2 emulation, CPU hotplug, and SMP IPI routing.

## Risks and test signals
Risks include register offset misuse, SGI target migration bugs, virtualization LR/VMCR bit errors, and suspend restore ordering. Tests should cover GICv2 boot, child GIC probing, SGI send, CPU hotplug, suspend/resume, and KVM maintenance interrupt paths.
