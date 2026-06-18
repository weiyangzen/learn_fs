<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h

## Purpose

`phy-am335x-control.h` declares the callback contract between the AM335x USB PHY driver and the AM335x control-module driver.

## Important APIs, Types, and Functions

`struct phy_control` contains two callbacks: `phy_power()` and `phy_wkup()`. Inline wrappers `phy_ctrl_power()` and `phy_ctrl_wkup()` invoke those callbacks. `am335x_get_phy_control()` returns a callback table for a device's `ti,ctrl_mod` phandle.

## Control Flow

The header has no independent execution. `phy-am335x.c` calls `am335x_get_phy_control()` during probe and later invokes the inline wrappers in init/shutdown and PM paths.

## State and Persistence Behavior

The header owns no state. The callback implementation changes AM335x control-module hardware state.

## Dependencies and Integration Points

It depends on `enum usb_dr_mode`, `struct device`, integer types, and bool definitions through includers. It is private to the AM335x PHY/control split.

## Risks and Test Signals

The wrappers assume a non-NULL `phy_control` and non-NULL callbacks. Compile coverage plus AM335x probe-defer and PM tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h -->
