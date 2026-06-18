# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/gp8psk.h

## Purpose
This header supplies the Genpix driver's logging prefix, debug masks, and a few common vendor request constants shared with the implementation and related frontend code.

## Important APIs, types, and functions
It declares `dvb_usb_gp8psk_debug`, defines `deb_info()`, `deb_xfer()`, and `deb_rc()`, and names vendor commands such as `GET_USB_SPEED`, `RESET_FX2`, `FW_VERSION_READ`, `VENDOR_STRING_READ`, `PRODUCT_STRING_READ`, and `FW_BCD_VERSION_READ`.

## Control flow and state
The header contains no mutable state beyond using the externally declared debug module parameter. Its constants are used to form USB control requests and to make logs consistent.

## Dependencies and integration
It includes `dvb-usb.h`, thereby binding the driver to DVB USB structures, IDs, debug support, and rc-core integration.

## Risks and test signals
Risk is low, but command-value changes would break firmware/device protocol compatibility. Compile with debug enabled and exercise version/vendor/product read commands to confirm constants still match firmware behavior.
