
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/Kconfig

## Purpose
This Kconfig entry enables the USB transport driver for Siano SMS1xxx mobile digital TV receivers.

## Important APIs, Types, and Functions
The symbol is `SMS_USB_DRV`, a `tristate` with prompt "Siano SMS1xxx based MDTV receiver". It depends on `DVB_CORE && HAS_DMA`, uses `depends on !RC_CORE || RC_CORE`, and selects `MEDIA_COMMON_OPTIONS` and `SMS_SIANO_MDTV`.

## Control Flow
Enabling this symbol builds the USB transport and pulls in the shared Siano MDTV core. The driver then binds USB IDs and hands data and request callbacks to the common smscore layer.

## State and Persistence
The file only controls build configuration. Runtime Siano device state is implemented in `smsusb.c` and the common Siano core.

## Dependencies and Integration Points
The entry connects USB Siano support to the DVB core, DMA-capable buffer usage, optional remote-control core availability, and shared media options.

## Risks and Edge Cases
The remote-control dependency expression allows builds both with and without `RC_CORE`; changes in common Siano code could require tightening that relationship. Missing `HAS_DMA` would break URB/buffer assumptions.

## Test Signals
Build with `CONFIG_SMS_USB_DRV=m`, verify `smsusb.o` links with common Siano objects, and check Kconfig dependency resolution for DVB-only and RC-core-enabled configurations.
