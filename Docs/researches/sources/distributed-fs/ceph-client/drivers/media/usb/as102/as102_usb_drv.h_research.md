# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.h

## Purpose
Defines AS102 USB command constants, supported USB device IDs/names, and the USB token command container.

## Important APIs, types, and functions
Vendor control requests are `AS102_USB_DEVICE_TX_CTRL_CMD` (`0xf1`) and `AS102_USB_DEVICE_RX_CTRL_CMD` (`0xf2`). The header names supported products: Abilis reference design, PCTV picoStick 74e, Elgato EyeTV DTT Deluxe, nBox DVB-T Dongle, and Sky Italia Digital Key, with their VID/PID constants. `struct as10x_usb_token_cmd_t` stores one AS10x command and one AS10x response. `as102_urb_stream_irq()` is declared for URB completion.

## Control flow and state
No executable flow exists. Constants here drive USB matching and request dispatch in `as102_usb_drv.c`, and the token type supplies persistent command/rsp storage inside `struct as10x_bus_adapter_t`.

## Dependencies and integration points
Includes `as10x_cmd_t` through use in the token struct. Integrated by `as102_drv.h` and USB transport code.

## Risks and test signals
Risks are incorrect VID/PID constants or mismatch between ID table, device-name array, and eLNA config arrays. Test signals are all supported devices binding to the expected product name and the command buffers remaining large enough for all AS10x command unions.
