# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_device_driver.c

Purpose: `usbip_device_driver.c` implements the usbip generic-driver backend for virtual UDC (`usbip-vudc`) device-mode exports.

Important functions and data: `read_usb_vudc_device()` reads a vUDC parent platform device's binary `dev_desc`, copies descriptor fields into `struct usbip_usb_device`, maps `current_speed` strings to USB speed enums, and uses the platform device name as the busid. `is_my_device()` checks the `USB_UDC_NAME` property for `usbip-vudc`. `usbip_device_driver_open()` initializes the generic list and reports missing modules. The exported `device_driver` struct sets subsystem `udc` and provides generic open/close/refresh/get hooks plus vUDC-specific read/filter functions.

Control flow and integration: `usbipd --device` selects `device_driver` instead of `host_driver`, so daemon devlist/import requests enumerate vUDC gadgets instead of physical USB devices. Interface reading is intentionally omitted because vUDC does not support it here.

State and dependencies: state is in the generic exported-device list and libudev context. It depends on sysfs `dev_desc`, `current_speed`, UDC properties, and little-endian USB descriptors. Risks include failing if the descriptor file is absent or short, no interface data in devlist replies, assuming the parent relation and sysname are stable, and using string speed names that must match kernel output. Test signals are `usbipd --device`, `usbip list -r`, and successful attach of a ConfigFS gadget bound to `usbip-vudc`.
