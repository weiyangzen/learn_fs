# sources/distributed-fs/ceph-client/include/linux/phy/omap_control_phy.h

## Purpose
TI OMAP control-module PHY interface for USB, PIPE3, PCIe, and related PHY power/mode controls. It exposes register bit definitions and optional helper calls used by OMAP PHY drivers and consumers.

## Important APIs, Types, and Functions
Defines `enum omap_control_phy_type`, `struct omap_control_phy`, `enum omap_control_usb_mode`, register bit masks for OTG validity, PHY power down, PIPE3 clock/power fields, PCIe PCS delay, and AM437x USB2 control. Exports `omap_control_phy_power()`, `omap_control_usb_set_mode()`, and `omap_control_pcie_pcs()` when `CONFIG_OMAP_CONTROL_PHY` is enabled, with no-op stubs otherwise.

## Control Flow
Consumers call mode or power helpers; implementation code writes the mapped control-module registers selected by `type`. When disabled at build time, helpers compile away.

## State and Persistence
`struct omap_control_phy` holds persistent device, MMIO register pointers, system clock, and PHY type. Hardware register state persists outside the header and affects power, VBUS/session flags, PIPE3 power, and PCIe PCS delay.

## Dependencies and Integration Points
Integrates with OMAP control-module drivers, USB2/OTG/PIPE3 PHY drivers, PCIe PHY setup, `struct device`, MMIO, and clocks.

## Risks
Incorrect bit programming can power down links, misreport USB role/session state, or mis-tune PCIe delay. Stubs can hide missing functionality if a consumer treats no-op behavior as success.

## Test Signals
Board boot tests on OMAP/DRA7/AM437x, USB host/device role switching, PIPE3 power-cycle tests, PCIe bring-up, and build tests with `CONFIG_OMAP_CONTROL_PHY` enabled and disabled.
