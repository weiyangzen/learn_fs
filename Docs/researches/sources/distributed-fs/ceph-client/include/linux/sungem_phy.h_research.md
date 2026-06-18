# sources/distributed-fs/ceph-client/include/linux/sungem_phy.h

Purpose: declares the PHY abstraction used by the Sun GEM Ethernet driver family, including MDIO callbacks, PHY operation tables, probed PHY instance state, and model-specific MII register constants.

Important APIs and types: `struct mii_phy_ops` defines init, suspend, autonegotiation, forced setup, link polling, link readout, and fiber enable hooks. `struct mii_phy_def` describes supported PHY IDs, masks, ethtool feature bits, autonegotiation behavior, name, and ops. `struct mii_phy` stores current advertising/autoneg/speed/duplex/pause state plus host `net_device`, MDIO read/write callbacks, and platform data. `sungem_phy_probe()` fills a caller-provided instance. Register constants cover Broadcom BCM5201/5221/5241/5400 and Marvell 88E1011 details.

Control flow: the network driver initializes MDIO access in `struct mii_phy`, calls `sungem_phy_probe()`, then invokes ops to configure autonegotiation or forced speed and poll/read link state.

State and persistence: runtime link configuration is stored in `struct mii_phy`; persistent hardware state lives in PHY registers and is rewritten by driver operations.

Dependencies and integration points: integrates with `net_device`, ethtool feature definitions, MDIO register access, and legacy Sun GEM hardware support.

Risks and test signals: risks include stale register bit definitions, wrong PHY ID masks, MDIO callback lifetime, and mismatched pause/duplex reporting. Test with supported PHY models, autoneg and forced modes, suspend/resume, link flap handling, and ethtool reporting.
