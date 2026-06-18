# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.c

Purpose: `usbip_host_driver.c` implements the daemon backend for physical USB devices bound to the `usbip-host` kernel driver.

Important functions and data: `is_my_device()` accepts libudev USB devices whose current driver is `usbip-host`. `usbip_host_driver_open()` initializes list state, calls the generic open/enumeration path, and logs module-loading guidance when no devices are found. The exported `host_driver` struct sets subsystem `usb` and callbacks for common open/close/refresh/get, `read_usb_device()`, `read_usb_interface()`, and the filter.

Control flow and integration: this is the default backend selected by `usbipd`. It only exports devices already rebound by `usbip bind`, so binding and daemon export are separate steps.

State and dependencies: runtime state is the generic exported-device list. It depends on libudev driver names, `usbip-core.ko`, `usbip-host.ko`, and sysfs attributes created by the kernel driver. Risks include driver-name matching failures, stale enumeration under hotplug races, and no direct binding fallback inside the daemon. Test signals are `usbip bind -b BUSID`, `usbipd`, and `usbip list -r HOST` showing the bound device.
