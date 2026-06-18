# sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun50i-usb3.c

Purpose: Allwinner H6 USB3 PHY driver for a single USB 2+3 host PHY combo. It performs clock/reset sequencing and writes vendor PHY tuning registers.

Important APIs, types, and functions: `struct sun50i_usb3_phy` stores the generic PHY, MMIO base, reset, and clock. `sun50i_usb3_phy_open` programs external VBUS, spread-spectrum/reference enables, PIPE clock, forced VBUS, and low/high PHY tune values. PHY ops are init and exit.

Control flow: probe gets the unnamed clock and reset, maps resource 0, creates a PHY with `sun50i_usb3_phy_ops`, stores driver data, and registers a simple OF PHY provider. Init enables the clock, deasserts reset, then calls `sun50i_usb3_phy_open`. Exit asserts reset and disables the clock.

State and persistence: state is only the current clock/reset state and MMIO programming. The BSP-derived tuning values are reapplied on every init.

Dependencies and integration: generic PHY, OF compatible `allwinner,sun50i-h6-usb3-phy`, platform MMIO, common clock framework, reset controller, and xHCI/DWC consumers through the PHY provider.

Risks: register magic values are undocumented BSP imports; changes need board-level signal validation. There is no regulator or runtime PM handling in this file. Init failure unwinds clock if reset deassert fails. Test signals include probe deferral for clock/reset, successful SuperSpeed link training, repeated init/exit cycles, and PHY provider phandle resolution.
