# sources/distributed-fs/ceph-client/drivers/usb/misc/trancevibrator.c

## Purpose
`trancevibrator.c` is a minimal USB driver for the PlayStation 2 Trance Vibrator. It binds the ASCII Corporation vendor/product ID and exposes one sysfs attribute, `speed`, that sends a vendor control request to set vibration intensity.

## Important APIs, Types, and Functions
The only private state is `struct trancevibrator`, containing `struct usb_device *udev` and the last requested `speed`. `speed_show` reports the cached speed. `speed_store` parses decimal input with `kstrtoint`, clamps it to `[0, 255]`, updates the cached value, and sends `usb_control_msg` on endpoint zero using request `0x01`, `USB_DIR_OUT | USB_TYPE_VENDOR | USB_RECIP_OTHER`, `wValue = speed`, no data phase, and `USB_CTRL_SET_TIMEOUT`. On transfer failure it restores the old cached value.

`tv_probe` allocates state with `kzalloc_obj`, stores the USB device pointer, and attaches it with `usb_set_intfdata`. `tv_disconnect` clears interface data and frees the state. The `usb_driver` uses `dev_groups = tv_groups`, so the sysfs attribute is managed by the driver core.

## Control Flow
On probe, usbcore creates the device attribute group and the driver records interface state. User writes to `/sys/.../speed` synchronously send one vendor control transfer to the device. Reads return the cached speed, not a hardware query. Disconnect simply frees the private object after usbcore has detached the interface.

## State and Persistence
The driver keeps only an in-memory speed cache. The hardware vibration setting is changed by control transfer and may outlive the cached state until device reset or unplug. There is no locking around `speed`; concurrent sysfs writes can race, but the state is a single integer and failures roll back only relative to each writer's local `old` value.

## Dependencies and Integration Points
This file depends on Linux USB core, sysfs device attributes, allocation helpers, and vendor-specific endpoint-zero control transfers. Its integration surface is the USB ID table and the `speed` sysfs file.

## Risks and Edge Cases
The code does not take a reference to `udev`; it relies on interface lifetime during sysfs callbacks. Concurrent writes can reorder cached state and control messages. A failed control transfer restores the previous cached speed even if another writer has already succeeded. There is no suspend/resume handling, so the cached speed is not replayed after power management or reset. The request recipient is `USB_RECIP_OTHER`, which is device-specific and should not be generalized without hardware confirmation.

## Test Signals
Validation should cover sysfs reads/writes for negative, in-range, and greater-than-255 values, control-transfer failure injection to confirm rollback, disconnect while the sysfs attribute is active, and enumeration only for USB ID `0x0b49:0x064f`.
