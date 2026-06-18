## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_sgmac.h

Purpose: defines SGMII/TBI MDIO field helpers, internal PHY addresses, link/autoneg bits, RX gate register, speed enum, and exported SGMAC operation tables.

Important APIs, types, and functions: macros pack PHY/register/control values, extract link speed, identify internal PHY and SGMII control/status/base-page registers, and define `AUTO_NEG_COMPLETE`, `LINK_STATUS`, `LINK_UP`, `MPA_IDLE_WITH_QMI_EMPTY`, and `SGMII_EN`. `enum xgene_phy_speed` represents 10/100/1000. Externs expose `xgene_sgmac_ops` and `xgene_sgport_ops`.

Control flow, state, and dependencies: included by SGMAC implementation and main setup. No live state is stored here.

Integration points: supports SGMII operation-table selection and internal PHY link polling.

Risks: incorrect field packing breaks internal PHY management and link speed interpretation. Changes need hardware validation.

Test signals: internal MDIO reads/writes, SGMII autoneg, link status extraction, and MAC speed programming.
