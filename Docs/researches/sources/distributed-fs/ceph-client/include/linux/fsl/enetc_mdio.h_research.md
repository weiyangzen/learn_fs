# sources/distributed-fs/ceph-client/include/linux/fsl/enetc_mdio.h

Purpose: declares NXP ENETC MDIO/PCS helpers and register definitions for Clause 22/45 PHY access and SGMII PCS interface-mode programming.

Important APIs and types: PCS register constants define link timers and interface mode bits, including SGMII enable, autonegotiation, speed encoding, and half duplex. `enum enetc_pcs_speed` encodes 10/100/1000/2500 settings, with 2500 intentionally sharing the gigabit PCS encoding. `struct enetc_mdio_priv` stores ENETC hardware pointer and MDIO base. When `CONFIG_FSL_ENETC_MDIO` is reachable, read/write helpers for C22 and C45 and `enetc_hw_alloc()` are declared; otherwise stubs return `-EINVAL` or `ERR_PTR(-EINVAL)`.

Control flow: ENETC drivers allocate an `enetc_hw`, register an MDIO bus with the helper read/write callbacks, and configure PCS registers for the negotiated PHY/SerDes mode.

State and persistence: state is runtime MDIO bus and PCS register programming. No persistent storage is owned, but PHY/PCS configuration affects link behavior until reset.

Dependencies and integration points: depends on phylib `mii_bus`, ENETC hardware abstraction, device MMIO, and network driver link setup.

Risks and test signals: risks include Clause 22/45 address encoding bugs, 2.5G SGMII speed confusion, missing module dependency causing stub use, and PCS timer misprogramming. Tests should cover C22/C45 PHY reads/writes, autoneg on/off, 10/100/1000/2500 links, disabled-config stubs, and error injection for bus timeouts.
