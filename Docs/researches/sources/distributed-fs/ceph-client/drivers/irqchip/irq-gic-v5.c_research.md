<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c

## Purpose
Provides the core ARM GICv5 irqchip. It creates separate irqdomains for PPIs, SPIs, LPIs, and IPIs, implements system-instruction based mask/unmask/EOI/state operations, initializes CPU interfaces, registers CPUs with IRS, and supports OF/ACPI initialization.

## Important APIs, Types, And Functions
Global state lives in `struct gicv5_chip_data gicv5_global_data`, plus `lpi_ida`, `num_lpis`, `pri_bits`, and `base_ipi_virq`. Important irq chips are `gicv5_ppi_irq_chip`, `gicv5_spi_irq_chip`, `gicv5_lpi_irq_chip`, and `gicv5_ipi_irq_chip`. Key functions are `gicv5_init_common()`, `gicv5_init_domains()`, `gicv5_handle_irq()`, `handle_irq_per_domain()`, `gicv5_starting_cpu()`, `gicv5_hwirq_init()`, PPI sysreg state helpers, SPI/LPI affinity callbacks, and LPI allocation/free domain operations.

## Control Flow
OF or ACPI first probes the IRS layer, initializes the LPI domain, then `gicv5_init_common()` creates PPI/SPI/IPI domains, reads CPU interface priority and ID bit capacities, initializes the boot CPU interface, installs `gicv5_handle_irq`, enables IRS, registers CPU hotplug state, allocates per-CPU IPIs from the IPI hierarchy, and probes ITS nodes. Interrupt handling issues `CDIA`, validates the returned interrupt, applies GSB/ISB ordering, extracts type and ID, and dispatches into the matching irqdomain.

## State And Persistence
Static global data holds irqdomain pointers, CPU interface capabilities, SPI counts, IRS capability state, and fwnode. LPI IDs are allocated from an IDA and released on domain free. CPU-local PPI enable, priority, PCR, and CR0 registers are programmed on each CPU start. Hardware affinity, priority, pending, and active state are stored in GICv5 system-instruction-visible state rather than memory-mapped distributor registers.

## Dependencies And Integration Points
The core depends on ARM64 FEAT_GCIE CPU capability checks, GICv5 IRS helpers, ITS probing, KVM VGIC info, cpuhotplug, hierarchical irqdomains, SMP IPI setup, OF `arm,gic-v5`, ACPI MADT GICv5 IRS records, and IORT IWB token lookup for GSI routing. The LPI domain is the parent for ITS and IWB interrupt delivery.

## Risks
Ordering is critical around system instructions: masking uses GSB/ISB to satisfy lazy-disable and acknowledge rules. Domain `select()` paths assume firmware fwspec formats are consistent. LPI allocation must free IRS ISTE state and IDA IDs on partial failures. CPU interface capability mismatches produce hard boot failures on affected CPUs.

## Test Signals
Boot on GICv5 hardware or emulation with FEAT_GCIE, validate PPI/SPI/LPI/IPI delivery, CPU hotplug registration, SMP IPIs, MSI via ITS/IWB, KVM maintenance IRQ setup when virtualization is available, irqchip pending/active state operations, affinity changes, and ACPI GSI routing for regular GSI and IWB encoded GSI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5.c -->
