<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile

## Purpose

`drivers/usb/phy/Makefile` maps USB PHY Kconfig symbols to object files. It controls which legacy PHY drivers and shared helpers are built into the kernel or emitted as modules.

## Important APIs, Types, and Functions

The important outputs are object mappings: `phy.o` for `CONFIG_USB_PHY`, `of.o` for `CONFIG_OF`, and driver objects for `CONFIG_AB8500_USB`, `CONFIG_FSL_USB2_OTG`, `CONFIG_NOP_USB_XCEIV`, `CONFIG_TAHVO_USB`, `CONFIG_AM335X_CONTROL_USB`, `CONFIG_AM335X_PHY_USB`, `CONFIG_OMAP_OTG`, `CONFIG_TWL6030_USB`, `CONFIG_USB_TEGRA_PHY`, `CONFIG_USB_GPIO_VBUS`, `CONFIG_USB_ISP1301`, `CONFIG_USB_MXS_PHY`, `CONFIG_USB_ULPI`, `CONFIG_USB_ULPI_VIEWPORT`, and `CONFIG_KEYSTONE_USB_PHY`.

## Control Flow

There is no runtime flow. Kbuild expands `obj-$(CONFIG_...)` entries according to configuration values and links the corresponding object into built-in archives or modules.

## State and Persistence Behavior

The Makefile persists build structure only. Runtime state is created by the drivers it includes.

## Dependencies and Integration Points

It integrates directly with `Kconfig` symbols and the Linux Kbuild system. It also reflects helper dependencies: OF helper code builds whenever `CONFIG_OF` is enabled, while `phy.o` builds only under `USB_PHY`.

## Risks and Test Signals

Risks are stale symbol/object names, missing objects for enabled symbols, and object ordering regressions if helper providers are needed by built-in consumers. Test signals are allmodconfig/allnoconfig/allyesconfig builds and targeted builds for each PHY symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile -->
