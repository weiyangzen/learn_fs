<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h

## Purpose
`include/linux/pcs/pcs-xpcs.h` defines the public helper interface for Synopsys DesignWare XPCS, a phylink PCS used by several Ethernet MAC drivers. It declares supported autonegotiation mode constants, known PCS/PMA identity values, an identity structure, conversion and configuration helpers, MDIO/fwnode-based constructors, and destroy routines.

## Important APIs, Types, and Functions
Autonegotiation/interface mode constants include `DW_AN_C73`, `DW_AN_C37_SGMII`, `DW_2500BASEX`, `DW_AN_C37_1000BASEX`, and `DW_10GBASER`. `enum dw_xpcs_pcs_id` names native, NXP SJA1105/SJA1110, and generic DesignWare PCS IDs plus an ID mask. `enum dw_xpcs_pma_id` names native PMA, several DesignWare PMA generations and rates, Wangxun TXGBE 10G PMA, and Meta FBNIC 100G PMA. `struct dw_xpcs_info` pairs PCS and PMA IDs.

The opaque `struct dw_xpcs` is the implementation object. `xpcs_to_phylink_pcs()` exposes its phylink PCS facade. `xpcs_get_an_mode()` maps a `phy_interface_t` to an XPCS autonegotiation mode. `xpcs_config_eee_mult_fact()` configures EEE multiplier behavior. Constructors are `xpcs_create_mdiodev()` and `xpcs_create_fwnode()` for raw XPCS objects, plus `xpcs_create_pcs_mdiodev()` for callers that only need `struct phylink_pcs`. Destructors are `xpcs_destroy()` and `xpcs_destroy_pcs()`.

## Control Flow
A MAC driver discovers an XPCS instance through MDIO or firmware node, creates it, maps the requested PHY interface to an AN mode, optionally configures EEE behavior, passes the phylink PCS object to phylink, and destroys it on teardown. The implementation behind this header handles hardware ID probing, supported mode selection, link configuration, and phylink PCS callbacks.

## State and Persistence Behavior
The header defines no mutable state, but the opaque `dw_xpcs` instance created by the constructors persists across MAC/phylink lifetime. It likely holds MDIO/fwnode accessors, probed identity, supported mode tables, and PCS state. The caller must keep the underlying bus/fwnode resources alive for the lifetime of the XPCS object and avoid using the phylink PCS after destruction.

## Dependencies and Integration Points
The header includes clock, firmware node, MDIO, PHY, phylink, and type definitions. It integrates with DesignWare Ethernet controllers such as stmmac, switch drivers using NXP XPCS variants, Wangxun and Meta hardware IDs, MDIO bus infrastructure, phylink, PHY interface mode selection, and EEE configuration paths.

## Risks
Autonegotiation mode selection must match the requested `phy_interface_t`; a wrong mode can break link establishment or advertise invalid capabilities. Hardware ID matching must use masks and PMA/PCS pairing correctly because multiple vendors reuse or wrap XPCS blocks. Lifetime bugs can occur if MDIO devices, firmware nodes, or phylink callbacks outlive the XPCS object. EEE multiplier configuration is hardware-sensitive and can affect power/link stability.

## Test Signals
Build all XPCS consumers, probe known MDIO and firmware-node XPCS instances, verify `xpcs_get_an_mode()` across SGMII, 1000BASE-X, 2500BASE-X, 10GBASE-R, and Clause 73 modes, test link up/down and autonegotiation with phylink, validate identity matching on NXP/DesignWare/Wangxun/Meta devices, exercise EEE configuration, and run remove/error-path tests to catch lifetime leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h -->
