# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3.c

## Purpose

`irq-gic-v3.c` is the core ARM GICv3/GICv4 interrupt controller driver. It maps distributor and redistributor frames, configures SGIs, PPIs, SPIs, extended PPI/SPI ranges, interrupt priority and pseudo-NMI support, CPU interface system registers, irq domains, SMP IPIs, CPU hotplug, CPU power-management restore, KVM VGIC metadata, GIC errata, MBI, and ITS/LPI initialization.

## Important APIs, Types, And Functions

Core state is stored in `struct gic_chip_data gic_data`, which holds the fwnode, distributor base and physical address, redistributor regions, shared `struct rdists`, root irq domain, stride, flags, RSS support, PPI partition data, and counters. `struct redist_region` describes mapped redistributor MMIO regions. `struct partition_affinity` maps OF PPI partition fwnodes to CPU masks. Static keys control split EOI/deactivate support, pseudo-NMI support, and specific errata.

Key hardware helpers include `gic_dist_init()`, `gic_cpu_init()`, `gic_cpu_sys_reg_enable()`, `gic_cpu_sys_reg_init()`, `gic_enable_redist()`, `gic_populate_rdist()`, `gic_update_rdist_properties()`, and wait helpers for distributor/redistributor RWP. IRQ operations are provided by `gic_chip` and `gic_eoimode1_chip`, with handlers for mask/unmask, EOI, type, affinity, retrigger, irqchip state, vcpu affinity, and NMI setup/teardown. Domain operations are `gic_irq_domain_translate()`, `gic_irq_domain_alloc()`, `gic_irq_domain_free()`, `gic_irq_domain_select()`, and `gic_irq_get_fwspec_info()`.

## Control Flow

OF initialization maps the distributor and all redistributor regions, validates the distributor version, reads redistributor stride/region count, applies OF quirks, then calls `gic_init_bases()`. ACPI initialization maps the distributor from MADT, counts and maps redistributors from GICR or GICC subtables, creates a GSI fwnode, and also calls `gic_init_bases()`. `gic_init_bases()` chooses split EOI/deactivate mode, records global state, reads `GICD_TYPER`, applies IIDR quirks, creates the root irq domain, allocates per-CPU redistributor data, handles MBI if supported, installs the top-level IRQ handler, discovers redistributor features, enables CPU system-register access, initializes priorities, distributor, boot CPU redistributor, pseudo-NMI support, SMP hooks, PM notifier, and finally ITS or GICv2m MSI support.

The interrupt handling path reads `ICC_IAR1_EL1`, detects pseudo-NMI priority when enabled, performs priority drop and instruction synchronization, dispatches to `generic_handle_domain_irq()` or `generic_handle_domain_nmi()`, and deactivates unexpected interrupts. In EOI mode 1, EOI and deactivate are split and forwarded interrupts are not deactivated by the host. Masking and state operations select redistributor or distributor registers based on INTID range, with special register offsets for EPPI/ESPI. Affinity changes mask enabled SPIs, write `IROUTER`, then restore enablement.

CPU bring-up enables SRE, locates the CPU's redistributor by MPIDR affinity, wakes it, configures SGIs/PPIs, initializes system registers, checks RSS ability for SGIs, and calls `its_cpu_init()` when LPIs are available. SMP IPI setup allocates 8 SGIs from the GIC domain and sends SGIs by grouping targets by MPIDR cluster. CPU PM exit re-enables redistributor and CPU interface state; CPU PM enter can disable group 1 and put the redistributor to sleep when distributor security is disabled.

## State And Persistence Behavior

`gic_data` is global and `__read_mostly`, with per-CPU redistributor state allocated at init. Hardware state programmed by this file persists in the distributor, redistributors, and CPU interface registers. Per-CPU `has_rss` records local SGI routing support. `dist_prio_irq`, `dist_prio_nmi`, `cpus_have_group0`, `cpus_have_security_disabled`, and pseudo-NMI static keys encode boot-time priority model decisions. PPI partitions persist as allocated masks and fwnode pointers. ACPI setup uses init-only `acpi_data` and a persistent GSI domain fwnode.

## Dependencies And Integration Points

The driver depends on ARM GIC architecture headers, irqdomain core, generic irq-chip handlers, OF and ACPI MADT parsing, CPU hotplug, CPU PM, SMP, ARM SMCCC for NVIDIA T241 detection, KVM VGIC info, and optional ITS, MBI, and GICv2m code. It is the parent domain for LPIs and MBI SPIs and provides redistributor feature data consumed by the ITS driver. Firmware bindings include OF `arm,gic-v3`, `#redistributor-regions`, `redistributor-stride`, `ppi-partitions`, and ACPI GIC distributor/GICC/GICR subtables.

## Risks

The sensitive areas are priority/security configuration for pseudo-NMIs, split EOI/deactivate semantics, redistributor discovery, affinity routing, extended SPI/PPI offset translation, and errata-specific aliases. Incorrect priority translation when security is enabled can break interrupt masking or NMI behavior. Redistributor mismatch prevents CPUs from coming online. EOI/deactivate bugs can leave forwarded or unhandled interrupts stuck active. Errata such as T241 aliasing and GIC-700 deactivation workaround change register access paths and need hardware-specific validation.

## Test Signals

Boot logs should report SPIs, ESPIs, GICD_CTLR.DS/SCR_EL3.FIQ, redistributor discovery per CPU, feature strings, pseudo-NMI enablement, MBI/ITS handoff, and quirk activation. Functional tests should cover wired IRQ allocation from OF and ACPI fwspecs, SGI/IPI delivery, SPI/ESPI type and affinity changes, PPI/EPPI per-CPU handling, CPU hotplug, CPU PM suspend/resume, pseudo-NMI setup and teardown, KVM maintenance IRQ metadata, and boot with `irqchip.gicv3_nolpi`.
