<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c

### Purpose
`dns323-setup.c` initializes the D-Link DNS-323 NAS across hardware revisions A1, B1, and C1.

### Important APIs, Types, And Functions
Important functions include `dns323_init()`, `dns323_identify_rev()`, `dns323_read_mac_addr()`, revision-specific power-off callbacks, `dns323_pci_init()`, and `dns323c_phy_fixup()`. It defines NOR partitions, Ethernet/SATA data, LED/button platform devices, I2C devices, and MPP mode arrays.

### Control Flow
PCI init only runs for revision A1. Main init calls common Orion setup, identifies revision from SoC ID and PHY ID, applies revision-specific MPP modes, maps/registers NOR flash, installs revision-specific LED/button/I2C data, reads MAC from flash, initializes USB/Ethernet/I2C/UART and SATA for B1/C1, configures power-off GPIOs, and registers a PHY LED fixup for C1 when PHYLIB is built in.

### State, Persistence, And Dependencies
State persists in `system_rev`, platform devices, GPIO directions, flash resource mappings, Ethernet MAC platform data, and registered power-off callbacks. Dependencies include Orion GPIO/MPP, physmap flash, mv643xx Ethernet, SATA, I2C board info, PHYLIB, and flash-stored configuration.

### Integration Points
The `MACHINE_START(DNS323, ...)` descriptor wires this setup into legacy ATAGS boot. Common Orion PCI, IRQ, timer, restart, and memory fixup hooks are used.

### Risks
Revision detection pokes Ethernet SMI registers directly and defaults to B1 on timeouts. MAC parsing assumes a string at a fixed flash offset. Several GPIO setup failures log but do not stop boot. Bootloader mach-type quirks are noted.

### Test Signals
Each revision should boot with correct LED polarity, buttons, I2C devices, MAC address, SATA availability, and power-off behavior; C1 should apply the Marvell PHY LED fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/dns323-setup.c -->
