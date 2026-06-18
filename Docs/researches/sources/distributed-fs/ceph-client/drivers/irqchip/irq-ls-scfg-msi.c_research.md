<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c

### Purpose
`irq-ls-scfg-msi.c` provides Freescale/NXP Layerscape SCFG MSI/MSI-X support. It creates an MSI parent domain backed by SCFG MSI interrupt registers and chains each MSIR parent interrupt to decode pending MSI bits.

### Important APIs, Types, And Functions
`struct ls_scfg_msi` stores registers, MSIIR address, SoC-specific config, MSIR descriptors, hwirq bitmap, and the MSI parent domain. `struct ls_scfg_msir` records each shared MSI register's parent GIC IRQ and bit range. `ls_scfg_msi_domain_irq_alloc()` allocates MSI hwirqs. `ls_scfg_msi_irq_handler()` decodes MSIR status. `ls_scfg_msi_compose_msg()` writes MSI address/data with optional CPU-affinity encoding.

### Control Flow
Probe selects SoC config, maps registers, reserves all possible hwirqs, counts parent IRQs, optionally limits MSIRs to CPU count for affinity mode, sets up chained handlers for each MSIR, releases bitmap bits covered by available MSIRs, creates an MSI parent domain, and stores drvdata. Allocation finds a free hwirq, prepares IOMMU MSI translation, and installs the parent chip. The chained handler reads an MSIR register big-endian, iterates set bits in its configured range, reconstructs hwirqs from bit position and SRS, and handles them in the MSI domain.

### State, Persistence, And Dependencies
Persistent state includes the used bitmap, chained parent handlers, SoC config table, global `msi_affinity_flag` from the `lsmsi=` early parameter, and the MSI domain. It depends on platform resources, OF IRQ counts, IOMMU MSI preparation, generic MSI parent ops, and `irq-msi-lib.c`.

### Integration Points
PCI MSI/MSI-X domains select this parent through the MSI bus token. It forwards device interrupts to the Linux MSI layer and parent GIC IRQs through chained handlers.

### Risks
`ls_scfg_msi_domain_irq_alloc()` leaks the allocated bitmap bit if `iommu_dma_prepare_msi()` fails. Affinity mode assumes MSIR index-to-CPU binding and disables itself if too few MSIRs exist. Status decoding uses big-endian reads regardless of CPU endianness as required by hardware.

### Test Signals
Exercise all compatibles including LS1043 v1.1 bit layout, `lsmsi=no-affinity`, MSI-X allocation/free, IOMMU MSI preparation failure, CPU affinity selection, chained MSIR dispatch, remove teardown, and vector exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c -->
