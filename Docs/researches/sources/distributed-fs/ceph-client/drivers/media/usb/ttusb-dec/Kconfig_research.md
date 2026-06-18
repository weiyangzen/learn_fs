
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/Kconfig

## Purpose
This Kconfig entry enables support for Technotrend/Hauppauge DEC USB DVB devices.

## Important APIs, Types, and Functions
The symbol is `DVB_TTUSB_DEC`, a `tristate` depending on `DVB_CORE && USB && INPUT && PCI`, and selecting `CRC32`.

## Control Flow
When enabled, the companion Makefile builds both the DEC USB transport and its small frontend module. `CRC32` is required for firmware validation in the driver.

## State and Persistence
The file controls compile-time configuration only. Runtime firmware and DVB state are implemented in `ttusb_dec.c` and `ttusbdecfe.c`.

## Dependencies and Integration Points
It integrates DVB, USB, input subsystem support for the optional IR remote, and CRC32 firmware checks.

## Risks and Edge Cases
The help text documents required firmware files and paths; without them probe can fail or leave the device uninitialized. The PCI dependency is inherited from the DVB stack rather than the USB hardware itself.

## Test Signals
Build with `CONFIG_DVB_TTUSB_DEC=m`, verify `CRC32` selection, and test module loading with and without the expected firmware files.
