<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c

Purpose: Amlogic GXL MDIO mux/glue driver selecting between external MDIO and an internal Ethernet PHY.

Important APIs/types/functions: `struct gxl_mdio_mux` stores registers and mux handle. Core functions are `gxl_enable_internal_mdio`, `gxl_enable_external_mdio`, `gxl_mdio_switch_fn`, probe, and remove.

Control flow: probe maps registers, enables the `ref` clock, and calls `mdio_mux_init`. Switching internal programs PHY config, reset signal, PHY ID expected by the Meson GXL PHY driver, enables PHY, and delays for power-up. Switching external resets the mux/control register to external path.

State and persistence: state is hardware register selection, internal PHY enable/reset state, reference clock enable, and mdio-mux child state. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, COMMON_CLK, mdio-mux core, and the matching Meson GXL PHY driver identity. Compatible string is `amlogic,gxl-mdio-mux`.

Risks and test signals: risks include hard-coded internal PHY address/ID coupling, missing external cleanup beyond register zeroing, delay sensitivity, and invalid child IDs. Tests should cover child IDs 0/1, ref clock failures, repeated switching, and PHY driver match after internal enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c -->
