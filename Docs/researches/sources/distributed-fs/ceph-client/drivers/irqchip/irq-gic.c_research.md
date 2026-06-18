<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c

## Purpose
Implements the classic ARM GICv1/GICv2 interrupt controller, including distributor and CPU interface setup, irqdomain mapping for SGI/PPI/SPI interrupts, SMP IPI delivery, CPU PM save/restore, KVM VGIC information, cascaded secondary GICs, OF probing, and ACPI MADT probing.

## Important APIs, Types, And Functions
`struct gic_chip_data` stores distributor/CPU base addresses, raw mappings, non-banked per-CPU aliases, saved PM state, irqdomain, and interrupt count. Important chip callbacks include `gic_mask_irq()`, `gic_unmask_irq()`, `gic_eoi_irq()`, `gic_eoimode1_*()`, `gic_set_type()`, `gic_set_affinity()`, `gic_ipi_send_mask()`, and irqchip state get/set. Initialization is centered on `gic_of_init()`, `gic_v2_acpi_init()`, `gic_of_setup()`, `gic_init_bases()`, `__gic_init_bases()`, `gic_dist_init()`, and `gic_cpu_init()`.

## Control Flow
Probe maps distributor and CPU interface registers, handles quirks, decides whether split EOI/deactivate can be used, creates a linear irqdomain, initializes distributor targets/configuration, initializes the boot CPU interface, installs `gic_handle_irq`, sets up SMP IPIs, and optionally initializes GICv2m MSI frames. Runtime interrupt handling reads `GIC_CPU_INTACK`, filters spurious IDs, performs EOI early in split mode, stores SGI source encodings, and dispatches through the domain. Cascaded GICs use a chained handler that reads their CPU interface and dispatches to a secondary domain.

## State And Persistence
The driver keeps static `gic_data[]`, per-CPU SGI source state, CPU target maps, and static keys for deactivate and read-modify-write access. PM support saves SPI enable/active/config/target and per-CPU PPI enable/active/config registers, then restores them before re-enabling the distributor and CPU interface. No on-disk state exists; persistence is MMIO register programming across boot, suspend, and CPU hotplug.

## Dependencies And Integration Points
It depends on `irq-gic-common`, ARM/ARM64 exception hooks, cpuhotplug, CPU PM notifiers, OF and ACPI IRQ initialization, KVM VGIC info, GICv2m MSI support, and optional non-banked GIC handling. It integrates with device tree compatibles such as `arm,gic-400`, `arm,cortex-a9-gic`, and `qcom,msm-qgic2`, and with ACPI `GENERIC_DISTRIBUTOR`/`GENERIC_INTERRUPT` records.

## Risks
Register ordering and EOI/deactivate mode are high risk, especially for forwarded interrupts. Broken firmware ranges may hide GICv2 deactivate registers unless `irqchip.gicv2_force_probe` is used. CPU target mapping must match hardware CPU interface IDs. PM save/restore can lose edge interrupts while powered down, as noted by the source comments. Non-banked and byte-access quirks are platform specific.

## Test Signals
Build on ARM and ARM64 with OF and ACPI variants. Runtime coverage should include boot IRQ delivery, SGI/IPI operation, CPU hotplug, suspend/resume, cascaded child GICs, GICv2m MSI users, KVM VGIC initialization, `irqchip.gicv2_force_probe` behavior on broken ranges, and spurious IRQ handling under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic.c -->
