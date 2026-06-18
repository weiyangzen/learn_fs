<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c

## Purpose

`phy-keystone.c` is a small TI Keystone USB PHY driver layered on the generic NOP PHY helper. Its Keystone-specific behavior is enabling or disabling the SuperSpeed PHY reference clock bit in a PHY control register.

## Important APIs, Types, and Functions

`struct keystone_usbphy` embeds `struct usb_phy_generic` and stores an MMIO `phy_ctrl` base. Important functions are `keystone_usbphy_init()`, `keystone_usbphy_shutdown()`, `keystone_usbphy_probe()`, and `keystone_usbphy_remove()`.

## Control Flow

Probe maps the first MMIO resource, creates a generic PHY, overrides init/shutdown callbacks, stores drvdata, and registers the PHY. Init sets `PHY_REF_SSP_EN` in `USB_PHY_CTL_CLOCK`; shutdown clears it. Remove unregisters the PHY.

## State and Persistence Behavior

Runtime state is per-device. Hardware state is the PHY clock control bit plus any generic PHY resources configured by `usb_phy_gen_create_phy()`.

## Dependencies and Integration Points

The driver depends on OF compatible `ti,keystone-usbphy`, MMIO, generic NOP PHY helpers, and the legacy USB PHY registry. Kconfig depends on `NOP_USB_XCEIV`.

## Risks and Test Signals

Risks include register bit assumptions and generic-resource lifecycle interactions. Tests should cover probe resource failure, generic helper failure, init/shutdown bit readback, remove after registration, and DWC3/Keystone controller integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c -->
