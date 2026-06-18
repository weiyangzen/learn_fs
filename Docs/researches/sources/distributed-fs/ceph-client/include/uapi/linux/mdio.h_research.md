# sources/distributed-fs/ceph-client/include/uapi/linux/mdio.h

Purpose: defines Clause 45 MDIO manageable-device IDs, register numbers, bit masks, Ethernet PHY ability/status constants, EEE constants, BASE-T1/USXGMII support bits, and a helper for encoding Clause 45 PHY IDs in ioctl data.

Important APIs and types: constants cover MMDs such as PMA/PMD, WIS, PCS, PHYXS, AN, C22 extension, and vendor devices; generic registers like `MDIO_CTRL1`, `MDIO_STAT1`, `MDIO_DEVS*`, EEE registers, AN registers, 10GBASE-T, BASE-T1, LASI, and USXGMII fields. Bit masks describe speeds, loopback, low power, reset, autonegotiation, device presence, media types, link faults, FEC, EEE, pause, master/slave, polarity, transmit disable, and link state. `mdio_phy_id_c45()` encodes PRTAD/DEVAD using `MDIO_PHY_ID_C45`, `MDIO_PHY_ID_PRTAD`, and `MDIO_PHY_ID_DEVAD`.

Control flow: PHY drivers, ethtool paths, and ioctl users read/write MDIO registers using these addresses and masks, decode advertised/link-partner capabilities, configure speed/EEE/autoneg/FEC/low-power behavior, and map Clause 45 addresses through legacy MII ioctl structures.

State and persistence: hardware PHY registers hold link/autoneg/power state; kernel PHY state machines cache and act on it. This header defines constants only.

Dependencies and integration points: depends on `linux/types.h` and `linux/mii.h`; integrates phylib, ethtool, netdevice drivers, SFP/PHY modules, copper/fiber Ethernet standards, BASE-T1 automotive PHYs, and user ioctl tools.

Risks and test signals: risks include overlapping PMA/PCS speed encodings, deprecated aliases, GENMASK/BIT macro availability, Clause 45 address packing errors, and wrong interpretation of hardware-specific register pages. Test phylib compile/use, ethtool advertise/link-mode conversion, C45 ioctl encoding, EEE negotiation, BASE-T1 autoneg, USXGMII in-band status, and register decode against known PHYs.
