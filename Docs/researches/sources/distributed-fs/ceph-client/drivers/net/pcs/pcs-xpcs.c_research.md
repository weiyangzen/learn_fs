# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.c

Purpose: Implements the generic Synopsys DesignWare XPCS phylink library, including identification, supported interface validation, autonegotiation setup/status, link state resolution, EEE control, clock handling, and public constructors/destructors.

Important APIs, types, and functions: Public APIs include `xpcs_to_phylink_pcs()`, `xpcs_get_an_mode()`, `xpcs_config_eee_mult_fact()`, `xpcs_create_mdiodev()`, `xpcs_create_pcs_mdiodev()`, `xpcs_create_fwnode()`, `xpcs_destroy()`, and `xpcs_destroy_pcs()`. MDIO accessors are `xpcs_read()`, `xpcs_write()`, `xpcs_modify()`, `xpcs_read_vpcs()`, and `xpcs_write_vpcs()`. `xpcs_phylink_ops` provides validate, in-band caps, pre-config, config, get-state, AN restart, link-up, and EEE hooks. Compatibility tables map PCS IDs/interfaces to supported link modes, AN modes, and PMA callbacks.

Control flow: Creation allocates `dw_xpcs`, gets optional clocks, reads or accepts platform-provided PCS/PMA IDs, selects a descriptor, populates supported interfaces, and sets polling/reset behavior. Phylink validation intersects supported link modes with the selected interface. Pre-config switches interface mode, possibly soft-resets. Config dispatches to Clause 73, Clause 37 SGMII, Clause 37 1000BASE-X, 2500BASE-X, 10GBASE-R no-op, and optional vendor PMA callbacks. State reading decodes C73/C37/2500/10G paths, handles faults and resets, and resolves speed/duplex/pause.

State and persistence behavior: `struct dw_xpcs` caches descriptor, IDs, interface, reset need, clocks, phylink PCS, and EEE multiplier. Hardware autoneg/PCS/PMA registers persist until reset/reconfiguration. Some PMA IDs disable polling and reset behavior for interrupt-driven or special hardware.

Dependencies and integration points: It depends on MDIO C45/C22 helpers, phylink, ethtool link modes, clocks, firmware MDIO lookup, and vendor helper files for NXP and WangXun. Platform and MAC drivers use its constructors to obtain `phylink_pcs`.

Risks and edge cases: Link-status bits can be latching-low, so unnecessary rereads can miss down events. Fault handling resets and reconfigures C73 links. SGMII MAC-side/PHY-side differences and TXGBE quirks affect register programming. Autoneg advertisement support is per-compat table, and unsupported interfaces return `-ENODEV`/`-EINVAL`. Clock preparation must unwind on ID failure. EEE multiplier must be configured appropriately by consumers.

Test signals: Probe all descriptor IDs, validate supported interfaces/link modes, C73 advertisement/LPA resolution, C37 SGMII and 1000BASE-X forced/in-band paths, 2500BASE-X fixed link, USXGMII speed programming, fault/reset recovery, PMA-specific TXGBE and NXP callbacks, EEE enable/disable, clock failure unwind, fwnode and MDIO constructors, and destroy after partial create failures.
