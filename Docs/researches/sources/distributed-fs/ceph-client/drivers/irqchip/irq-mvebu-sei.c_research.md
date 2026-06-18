<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c

### Purpose
`irq-mvebu-sei.c` implements the Marvell AP806 SEI controller. It creates a root SEI domain, a wired AP child domain, and a platform-MSI CP child domain over separate interrupt ranges.

### Important APIs, Types, And Functions
`struct mvebu_sei` stores MMIO, resource, domains, range capabilities, CP MSI bitmap/lock, and mask lock. `mvebu_sei_handle_cascade_irq()` reads SEI cause registers and dispatches root hwirqs. `mvebu_sei_ap_alloc()` maps wired AP interrupts. `mvebu_sei_cp_domain_alloc()` allocates CP MSI slots. `mvebu_sei_cp_compose_msi_msg()` builds SET_SEI MSI messages.

### Control Flow
Probe maps registers, loads AP/CP range capabilities, maps the top-level SPI parent, creates the root SEI nexus domain, creates a wired AP hierarchy domain, creates a CP MSI parent domain, resets cause/mask registers, and chains the parent IRQ. Root allocation only installs the low-level SEI chip. AP allocation offsets hwirqs by the AP range and uses level handling. CP allocation reserves one bitmap slot, offsets by the CP range, allocates the root parent, and uses edge handling. Cascade dispatch walks both 32-bit cause registers and reports unmapped hwirqs as spurious warnings.

### State, Persistence, And Dependencies
Persistent state includes root/AP/CP domains, CP allocation bitmap, MMIO cause/mask registers, and capability ranges. Dependencies include OF match data, platform MSI helpers, chained IRQ handling, irqdomain hierarchy, and `irq-msi-lib.c`.

### Integration Points
AP wired interrupts and CP platform MSI users share the same SEI hardware and root cascade. The CP MSI domain is selected by platform MSI clients.

### Risks
CP MSI allocation supports only single IRQ requests. AP type is restricted to level-high and CP type to edge-rising. The root domain has no translate callback and depends on child domains passing expected fwspecs. Affinity on the root chip returns `-EINVAL`.

### Test Signals
Validate AP and CP range mapping, CP bitmap exhaustion/free, MSI message data/address, cascade dispatch of mapped and unmapped bits, mask/unmask/ack register operations, parent SPI parse failure, and invalid type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c -->
