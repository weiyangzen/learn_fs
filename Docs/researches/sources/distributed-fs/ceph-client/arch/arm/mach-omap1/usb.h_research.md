<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h

## Purpose
Provides OMAP1 USB declarations and constants for board code and USB platform initialization.

## Important APIs, Types, and Functions
Defines `is_usb0_device(config)` depending on `CONFIG_USB_OMAP`, declares or stubs `omap1_usb_init()`, and provides OHCI base constants with `OMAP_OHCI_BASE` set to the OMAP1 address.

## Control Flow
No runtime flow. Compile-time config chooses whether USB init is callable and whether USB0 should be treated as device-capable.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on OMAP1 USB platform-data headers and the USB support configuration.

## Risks
The comment notes `is_usb0_device()` is a simplification and the correct answer depends on HMC/OTG mode. This can affect transceiver pull-up/pull-down setup.

## Test Signals
Build with USB support enabled and disabled. Board tests should verify USB0 role handling for the configured HMC mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h -->
