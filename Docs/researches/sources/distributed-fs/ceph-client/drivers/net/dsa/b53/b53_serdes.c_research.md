# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.c

Purpose: Northstar Plus B53 SerDes/SGMII PHY logic and phylink PCS integration.

Important APIs/types/functions: lane/block access helpers, `b53_pcs_ops`, `b53_serdes_link_set()`, `b53_serdes_phylink_get_caps()`, `b53_serdes_phylink_mac_select_pcs()`, and `b53_serdes_init()`.

Control flow: transport maps port to lane, init validates SerDes IDs and initializes `dev->pcs[lane]`; phylink config toggles 1000BASE-X fiber mode, restart sets BMCR autoneg restart, state reads digital/BMSR status, and link set powers BMCR up/down.

State and persistence behavior: `dev->serdes_lane` caches selected lane; `dev->pcs[]` stores initialized PCS objects; hardware state is volatile across reset.

Dependencies and integration points: B53 register wrappers, `b53_serdes.h`, PHY constants, phylink PCS APIs, and SRAB transport ops.

Risks: only two lanes supported; interface configuration is minimal; capability assumptions are SoC-specific; missing initialized ID disables PCS.

Test signals: SGMII/1000BASE-X/2500BASE-X phylink tests, autoneg restart/state reporting, SerDes init failure, and reset/reprobe.
