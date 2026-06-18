# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-omap-control.c

## Purpose
OMAP/TI control-module PHY helper driver. It maps shared control registers and exports APIs used by USB2, PIPE3, PCIe, and OTGHS PHY drivers for power control, PCIe PCS delay, and OTG mailbox mode state.

## APIs, Flow, And State
Exports `omap_control_pcie_pcs()`, `omap_control_phy_power()`, and `omap_control_usb_set_mode()`. Probe selects an `omap_control_phy_type` from match data, maps `otghs_control` or `power`, obtains `sys_clkin` for PIPE3/PCIe, maps `pcie_pcs` for PCIe, and stores `struct omap_control_phy` as driver data. Power writes are type-specific: USB2 and DRA7/AM437 USB2 powerdown bits, PIPE3/PCIe command/frequency fields, and OTGHS host/device/disconnect mailbox bits.

## Dependencies And Integration
Loaded with `subsys_initcall()` for early availability. Integrates with `phy-omap-usb2.c` and `phy-ti-pipe3.c` through exported symbols and `ctrl-module` phandles. Uses named platform resources and clocks.

## Risks And Tests
Exported helpers are void and cannot return write failures to callers. Raw register access is unlocked, so shared control updates depend on external serialization. Probe maps missing `sys_clkin` to `-EINVAL`, not defer. Test all compatibles, helper/type mismatch logging, PCS delay writes, OTG modes, and dependent driver probe ordering.
