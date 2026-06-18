# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-histb-combphy.c

## Purpose
HiSilicon STB COMBPHY provider that can be fixed-mode or selectable among SATA, PCIe, and USB3. It configures a parent syscon mode selector, deasserts POR, enables reference clock/EP clock, and writes vendor nano-register initialization.

## Important APIs, types, and functions
- `struct histb_combphy_priv` stores MMIO, syscon, reset, refclk, PHY, and mode metadata.
- `struct histb_combphy_mode` stores fixed/selectable mode and selector register fields.
- `histb_combphy_xlate()` validates phandle mode argument and fixed-mode compatibility.
- `histb_combphy_set_mode()` maps `PHY_TYPE_*` values to hardware selector values.
- `nano_register_write()` writes address/data through `COMBPHY_CFG_REG` strobe.

## Control flow
Probe maps MMIO, gets parent syscon, parses either `hisilicon,fixed-mode` or `hisilicon,mode-select-bits`, gets clk/reset, creates one PHY, and registers custom xlate. Xlate records selected mode. Init programs mode, clears bypass, enables clock/reset, enables EP clock, delays, and writes nano registers. Exit disables EP clock, asserts reset, and disables refclk.

## State and persistence
Selected mode is cached in `priv->mode.select`; hardware selector and PHY registers hold runtime state. No persistence.

## Dependencies and integration points
Uses generic PHY, syscon/regmap, reset, clk, `dt-bindings/phy/phy.h`, and platform OF. Consumers provide one mode argument in their PHY phandle.

## Risks and test signals
Risks include shared single PHY with mutable selected mode, fixed-mode/selector DT conflicts, and magic nano-register values. Test each mode, fixed-mode mismatch errors, missing selector bits, and clock/reset sequencing.
