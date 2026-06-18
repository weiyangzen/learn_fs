<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c

Purpose: Amlogic G12A MDIO mux/glue driver selecting external MDIO or an internal Ethernet PHY and registering the internal EPHY PLL with the common clock framework.

Important APIs/types/functions: `struct g12a_mdio_mux` stores registers, mux handle, and PLL clock. `struct g12a_ephy_pll` implements `clk_hw`. Key functions are PLL ops, `g12a_enable_internal_mdio`, `g12a_enable_external_mdio`, `g12a_mdio_switch_fn`, `g12a_ephy_glue_clk_register`, probe, and remove.

Control flow: probe maps registers, enables peripheral clock, registers input mux and EPHY PLL clocks, and initializes mdio-mux children. Switching to internal enables/locks PLL, programs PHY identity/control/source registers, and waits for power-up. Switching external clears mux/source and disables PLL when enabled.

State and persistence: runtime state is register programming for PLL and PHY control, clock enable state, and mdio-mux child selection. No persistent storage exists.

Dependencies/integration: depends on COMMON_CLK, OF MDIO, HAS_IOMEM, mdio-mux core, and platform bus. Compatible string is `amlogic,g12a-mdio-mux`.

Risks and test signals: risks include PLL lock timeout, `__clk_is_enabled` usage, hard-coded PLL/PHY magic values, child ID assumptions 0/1, and cleanup with PLL enabled. Tests should cover clock registration, internal/external switching, invalid child IDs, and remove after internal selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c -->
