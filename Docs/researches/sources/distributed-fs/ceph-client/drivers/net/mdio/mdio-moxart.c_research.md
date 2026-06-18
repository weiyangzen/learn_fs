<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c

Purpose: MOXA ART Ethernet MDIO controller driver for RTL8201CP-style PHY access.

Important APIs/types/functions: `struct moxart_mdio_data` stores MMIO base. Core routines are `moxart_mdio_read`, `moxart_mdio_write`, `moxart_mdio_reset`, probe, and remove.

Control flow: read/write callbacks encode PHY/register fields and MIIRD/MIIWR bits, poll auto-clearing control bits up to five 10 ms iterations, and return data/status. Reset scans all PHY addresses, reads BMCR, and writes BMCR_RESET for responsive devices. Probe allocates bus/private data, sets PHY_MAC_INTERRUPT placeholders for all addresses, maps registers, registers with OF MDIO, and stores bus.

State and persistence: volatile state is MMIO control/data registers and mii_bus data. Reset temporarily changes PHY BMCR reset bits. Remove unregisters and frees bus.

Dependencies/integration: depends on ARCH_MOXART or compile test, OF MDIO, platform MMIO, and phylib.

Risks and test signals: risks include broad reset scanning, fixed polling duration, PHY interrupt comments not matching OF behavior, and no Clause 45 support. Tests should include timeouts, BMCR reset behavior, OF child registration, and invalid MMIO resource errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c -->
