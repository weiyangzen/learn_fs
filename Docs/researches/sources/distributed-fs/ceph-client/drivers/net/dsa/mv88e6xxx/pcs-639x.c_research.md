# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-639x.c

Purpose: implements Clause 45 PCS support for 88E6390/6393x SerDes lanes, covering SGMII/1000BASE-X/2500BASE-X and high-speed 5G/10G/RXAUI/XAUI/USXGMII modes with phylink integration and hardware errata workarounds.

Important APIs/types/functions: `struct mv88e639x_pcs` owns one MDIO C45 endpoint plus separate SGMII and XG `phylink_pcs` objects. Shared helpers wrap C45 read/write/modify, IRQ dispatch, SGMII power/config/state, XG state, and PCS selection. Exported ops are `mv88e6390_pcs_ops` and `mv88e6393x_pcs_ops`.

Control flow: init maps a SerDes lane from port, allocates PCS, assigns family-specific phylink ops, applies required errata, requests optional IRQ, and stores private state. PCS selection returns SGMII or XG PCS by interface. Enable paths set active IRQ handler, unmask interrupts, power lanes, and post-config applies family errata before enabling links.

State and persistence: runtime state includes selected interface, `handle_irq`, IRQ number, erratum flags, 5G support, and PCS objects. Hardware state spans C45 PHYXS/VEND1 registers, power-down bits, advertisement, link status, and interrupt masks.

Dependencies/integration: depends on default MDIO bus, phylink, SerDes lane mapping, `phy.h`, port/serdes register constants, and family/product IDs.

Risks: complex errata sequences must be applied in the right power/config order. `handle_irq` is shared between SGMII and XG PCS, so active PCS transitions must disable the previous handler cleanly. 2500BASE-X AN workaround intentionally rewrites nonstandard vendor registers.

Test signals: phylink mode switches among SGMII/1000BASE-X/2500BASE-X/10G/USXGMII, link IRQs and polling fallback, erratum 3.14/4.6/4.8/5.2 register writes, 5G support gating, and teardown after IRQ setup failures.
