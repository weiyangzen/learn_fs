# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_main.c

Purpose: module entry and exit for the USB/IP virtual USB device controller. It registers a `platform_driver` named by `GADGET_NAME`, creates `num` emulated controller platform devices, and tears them down on init failure or module exit.

Important APIs/types/functions: `module_param_named(num, vudc_number, uint, S_IRUGO)` exposes the controller count. `vudc_driver` binds `.probe = vudc_probe`, `.remove = vudc_remove`, and `vudc_groups` sysfs attributes. `vudc_init()` checks `usb_disabled()`, validates at least one device, registers the driver, then calls `alloc_vudc_device()`, `platform_device_add()`, and `platform_get_drvdata()`. `vudc_cleanup()` reverses the global `vudc_devices` list with `platform_device_del()` and `put_vudc_device()`.

Control flow: successful init is driver registration followed by per-index device allocation/addition/listing. Any device allocation, add, or failed probe jumps to cleanup that removes already-added devices and unregisters the driver. Exit always walks the same list and unregisters after deleting all devices.

State and persistence: persistent kernel state is the module parameter and static `vudc_devices` list. Device lifetime is reference-counted through platform device put paths. There is no disk persistence.

Dependencies and integration: depends on platform bus, USB core availability, and helpers from `vudc.h`. Sysfs integration is delegated through `vudc_groups`, and all network/transfer behavior lives in the other vudc files.

Risks: partial init cleanup relies on list membership only after successful `platform_device_add()`, so earlier failures are handled separately. The `platform_get_drvdata()` post-add check treats a probe failure after platform add as `-EINVAL`; diagnostics depend on probe-side logs.

Test signals: load with default and multiple `num=` values, reject `num=0`, verify created platform devices expose sysfs attributes, and inject probe/allocation failures to confirm cleanup leaves no devices or registered driver.
