<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c

### Purpose
`irq-mvebu-odmi.c` implements the Marvell ODMI platform-MSI parent. Each ODMI frame provides eight interrupt slots mapped to parent GIC SPIs and exposed through a generic MSI parent domain.

### Important APIs, Types, And Functions
`struct odmi_data` stores each frame's resource, base, and SPI base. Global `odmis`, `odmis_bm`, and `odmis_count` manage slot allocation. `odmi_irq_domain_alloc()` reserves a slot and allocates a parent SPI. `odmi_compose_msi_msg()` builds the ODMI doorbell address/data. `odmi_msi_parent_ops` declares platform MSI support.

### Control Flow
OF init reads `marvell,odmi-frames`, allocates frame state and a bitmap, maps each frame resource, reads its `marvell,spi-base`, and creates an MSI parent domain sized at `frames * 8`. Allocation reserves the first free hwirq, computes frame and slot, allocates the parent GIC SPI as edge-rising, explicitly sets parent type to edge-rising, and installs `odmi_irq_chip`. Freeing releases the parent IRQ and bitmap slot.

### State, Persistence, And Dependencies
State is global frame arrays, bitmap, mapped MMIO frames, and the MSI parent domain. Dependencies include OF resources/properties, GIC three-cell specs, MSI parent helpers, and `irq-msi-lib.c`.

### Integration Points
Platform MSI clients use ODMI as a generic MSI parent; ODMI turns MSI writes into GIC SPI assertions.

### Risks
On parent allocation failure the error path clears `odmin` rather than full `hwirq`, which can release the wrong bitmap bit for frames beyond zero. Global state allows one ODMI controller set. Group events are not supported; only eight interrupts per frame are exposed.

### Test Signals
Validate multiple frames, per-frame SPI base mapping, bitmap allocation/free beyond frame zero, MSI message data/address, parent edge type setup, malformed properties, and ENOSPC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c -->
