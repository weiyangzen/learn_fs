# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-lynx.c

Purpose: Provides an NXP Lynx PCS phylink helper library for MDIO-backed PCS blocks in Layerscape/QorIQ Ethernet SerDes.

Important APIs, types, and functions: `struct lynx_pcs` wraps `phylink_pcs` and an `mdio_device`. `lynx_pcs_phylink_ops` implements in-band capabilities, state read, config, autoneg restart, and link-up. Exported constructors/destructor are `lynx_pcs_create_mdiodev()`, `lynx_pcs_create_fwnode()`, and `lynx_pcs_destroy()`.

Control flow: Consumers create a PCS from an MDIO bus/address or firmware node. Config chooses C22 helpers for SGMII/QSGMII/1000BASE-X/2500BASE-X, C45 helpers for 10GBASE-R state, and vendor MMD reads for USXGMII/10G-QXGMII. Link timers are programmed for gigabit modes. Non-inband SGMII link-up forces speed/duplex in `IF_MODE`.

State and persistence behavior: The object holds an MDIO device reference and marks supported interfaces. `pcs.poll = true`, so phylink polls state instead of relying on interrupts. No persistent hardware state beyond programmed PCS registers.

Dependencies and integration points: It depends on phylink MII PCS helpers, MDIO device management, firmware-node MDIO lookup, and `linux/pcs-lynx.h` consumer API.

Risks and edge cases: USXGMII currently requires in-band autoneg and returns `-EOPNOTSUPP` otherwise. Link timer programming must match interface mode. Constructor reference handling intentionally drops the caller-created MDIO reference after taking its own. Unsupported speeds in forced SGMII link-up are rejected.

Test signals: Test all supported interfaces, in-band and forced SGMII, USXGMII autoneg-only behavior, fwnode unavailable/defer paths, MDIO read/write failures, state decode for C22/C45/vendor paths, and create/destroy refcount balance.
