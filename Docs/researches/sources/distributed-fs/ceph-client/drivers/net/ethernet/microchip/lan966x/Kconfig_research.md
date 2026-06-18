# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/Kconfig

Purpose: defines build options for the Microchip LAN966x switch driver and optional DCB support.

Important behavior: `CONFIG_LAN966X_SWITCH` is a tristate depending on optional PTP clock support, MMIO, device tree, switchdev, and bridge availability; it selects `PHYLINK`, `PAGE_POOL`, `VCAP`, and `FDMA`. `CONFIG_LAN966X_DCB` is a bool depending on `LAN966X_SWITCH && DCB`, defaults to yes, and enables DCB apptrust/app/rewrite operations.

Control flow and state: no runtime control flow. Build-time state determines whether the main switch object is compiled and whether `lan966x_dcb.o` is included.

Dependencies and integration points: ties the driver into switchdev/bridge, phylink, PTP, page_pool, VCAP, and the shared Microchip FDMA helper. The DCB symbol controls whether `lan966x_dcb_init` is a real initializer or an inline no-op from the main header.

Risks and test signals: dependency mistakes can produce link or compile failures in bridge-disabled, PTP-disabled, DCB-disabled, or modular configurations. Test `LAN966X_SWITCH=m/y`, `BRIDGE=n`, `DCB=n`, and debugfs combinations.
