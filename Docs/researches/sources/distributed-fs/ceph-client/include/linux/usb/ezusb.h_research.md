<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h

Purpose: declares helper APIs for Cypress EZ-USB FX1 reset control and Intel HEX firmware download.

Important APIs and types: `ezusb_fx1_set_reset()` toggles the FX1 reset bit on a USB device. `ezusb_fx1_ihex_firmware_download()` downloads firmware from a named Intel HEX firmware file to the device.

Control flow: device drivers put the FX1 into reset, load firmware records, then release reset so the device can renumerate or start its programmed behavior.

State and persistence: state is hardware device reset state and volatile downloaded firmware. The firmware path references persistent firmware storage, but the header owns none.

Dependencies and integration points: forward-declared `struct usb_device` is expected from USB includes. It integrates USB device drivers with firmware-loading and vendor-control-transfer implementation code.

Risks and test signals: risks include leaving devices in reset, partial firmware downloads, firmware path errors, and renumeration timing races. Test successful and failed firmware load, reset release, disconnect during download, and device re-enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ezusb.h -->
