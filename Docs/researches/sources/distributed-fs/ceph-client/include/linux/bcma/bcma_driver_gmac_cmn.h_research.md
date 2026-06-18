# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_gmac_cmn.h

## Purpose
Defines BCMA GMAC common-core registers for switch tags, parser, PHY access/control, CFP/TCAM, and user-defined fields, plus the driver state used to serialize PHY register access.

## Important APIs, types, and functions
- Register constants cover `BCMA_GMAC_CMN_STAG*`, parser/MIB length, PHY access/control fields, RGMII control, CFP/TCAM data/mask/action/status, and UDF registers.
- `struct bcma_drv_gmac_cmn` stores the core pointer and `phy_mutex`.
- Access macros wrap 16/32-bit BCMA read/write operations.

## Control flow and state
Ethernet drivers use the common core to configure shared GMAC parsing and PHY operations. Access to `BCMA_GMAC_CMN_PHY_ACCESS` and `BCMA_GMAC_CMN_PHY_CTL` must take `phy_mutex` first, preventing concurrent MDIO-like transactions.

## State and persistence behavior
All state is live hardware register state; no persistence is defined here. The mutex is runtime serialization state.

## Dependencies and integration points
Depends on kernel types and BCMA core accessors. Integrated by Broadcom GMAC ethernet drivers sharing PHY and parser hardware.

## Risks
Ignoring `phy_mutex` can interleave PHY transactions. TCAM/UDF register programming is position-sensitive and may affect packet classification globally across ports.

## Test signals
Run concurrent PHY reads/writes, verify RGMII/PHY settings, exercise CFP/TCAM programming, and check packet classification after UDF/parser updates.
