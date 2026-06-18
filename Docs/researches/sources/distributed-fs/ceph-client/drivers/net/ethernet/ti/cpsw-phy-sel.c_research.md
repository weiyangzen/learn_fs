# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw-phy-sel.c

## Purpose
Implements the built-in TI CPSW PHY interface selection helper for AM335x/AM43xx/DRA7-style control-module `gmii-sel` registers. It lets CPSW Ethernet drivers program MII/RMII/RGMII mode bits for each slave port based on the requested PHY interface.

## Important APIs, Types, and Functions
The exported API is `cpsw_phy_sel(struct device *dev, phy_interface_t phy_mode, int slave)`. The private state is `struct cpsw_phy_sel_priv`, containing the device, mapped `gmii_sel` register, `rmii_clock_external`, and SoC-specific selector callback. Implementation callbacks are `cpsw_gmii_sel_am3352` and `cpsw_gmii_sel_dra7xx`; platform probing is in `cpsw_phy_sel_probe`.

## Control Flow
Probe matches one of `ti,am3352-cpsw-phy-sel`, `ti,dra7xx-cpsw-phy-sel`, or `ti,am43xx-cpsw-phy-sel`, allocates private state, maps the `gmii-sel` resource, records the optional `rmii-clock-ext` flag, and stores the SoC-specific callback. `cpsw_phy_sel` finds the selector node either through a `cpsw-phy-sel` phandle or child node, locates the bound platform device on the platform bus, retrieves private state, invokes the selector callback, releases the device, and drops the node reference.

The AM335x/AM43xx selector maps RMII/RGMII/RGMII-ID/MII into two-bit mode fields, handles per-slave RMII external clock enable bits, and RGMII internal-delay bits. The DRA7 selector supports slaves 0 and 1 with different bit positions, rejects invalid slave numbers, warns that external RMII clock is unsupported, and otherwise writes the selected mode.

## State and Persistence
Software state is static after probe: register mapping, external clock flag, and callback. Persistent hardware state is the `gmii-sel` register bitfield controlling port interface mode and optional clock/delay bits. No restore logic is present in this file; callers or system PM must ensure control-module state is valid after resets if needed.

## Dependencies and Integration Points
Depends on platform bus/device lookup, OF phandles/child nodes, PHY interface enums, MMIO accessors, and `cpsw.h`. It is built in with `builtin_platform_driver`, and legacy CPSW drivers call the exported `cpsw_phy_sel` during interface setup.

## Risks and Test Signals
Risks include a likely confusing error path where `dev_err(dev, ...)` is used after `bus_find_device` returns NULL, unsupported PHY modes silently defaulting to MII after warning, invalid slave indexes on AM335x not explicitly bounded, missing PM restore, and DTs that use neither phandle nor child node. Test signals include mode register reads for MII/RMII/RGMII/RGMII-ID on each compatible, RMII external-clock behavior, invalid slave tests, probe deferral/order tests where Ethernet calls before selector device exists, and link-up verification after mode selection.
