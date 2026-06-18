<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c

### Purpose
`irq-mvebu-gicp.c` implements the Marvell AP806 GICP platform-MSI parent. It allocates GIC SPIs from firmware-provided ranges and composes two-message set/clear MSI payloads for level-capable platform MSI users.

### Important APIs, Types, And Functions
`struct mvebu_gicp` stores SPI ranges, total SPI count, bitmap, resource, lock, and device. `gicp_idx_to_spi()` maps bitmap indices to real SPI numbers. `gicp_irq_domain_alloc()` reserves an SPI, allocates the parent GIC IRQ, and installs `gicp_irq_chip`. `gicp_compose_msi_msg()` emits SETSPI and CLRSPI messages. `gicp_msi_parent_ops` advertises platform MSI support.

### Control Flow
Probe reads `marvell,spi-ranges`, builds the range table and bitmap, finds the parent domain, clears pending interrupts by writing the CLRSPI register for entries 0-63, and creates an MSI parent domain. Allocation reserves the first free bitmap index, maps it to a GIC SPI, allocates a parent SPI as edge-rising initially, and installs the chip. Freeing tears down the parent IRQ and releases the bitmap bit.

### State, Persistence, And Dependencies
State is devm-managed GICP data, SPI bitmap, parent MSI domain, and MMIO resource used for MSI message addresses. Dependencies include OF properties, parent GIC domain, MSI parent helpers, and `irq-msi-lib.c`.

### Integration Points
Platform MSI devices select the GICP domain and receive MSI messages targeting the GICP set/clear registers, which in turn assert or clear parent GIC SPIs.

### Risks
Firmware range errors directly affect parent SPI allocation. Probe clears only 64 possible pending values even if ranges describe more. Allocation handles one IRQ at a time despite receiving `nr_irqs`. The parent type is initially edge-rising until the child sets type.

### Test Signals
Validate multi-range SPI mapping, bitmap exhaustion/free, MSI message set/clear addresses, level-capable MSI flags, pending clear on probe, parent-domain absence, and invalid `marvell,spi-ranges` lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c -->
