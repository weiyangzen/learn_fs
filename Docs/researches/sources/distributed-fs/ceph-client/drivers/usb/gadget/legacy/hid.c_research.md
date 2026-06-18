# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/hid.c

## Purpose

`hid.c` implements the legacy `g_hid` composite gadget. Unlike configfs HID gadgets, this driver discovers HID function descriptors from platform data registered through a `hidg` platform device and builds a composite configuration containing one function per descriptor.

## Important APIs, Types, and Functions

`struct hidg_func_node` stores a HID function instance, concrete function, list node, and platform-provided `hidg_func_descriptor`. Core functions are `hidg_plat_driver_probe()`, `hidg_plat_driver_remove()`, `hid_bind()`, `do_config()`, `hid_unbind()`, `hidg_init()`, and `hidg_cleanup()`. It uses `usb_get_function_instance("hid")`, fills `struct f_hid_opts`, and adds each HID function to one configuration.

## Control Flow

Module init first probes the platform driver to collect HID descriptors, then registers the composite driver. Platform probe adds descriptors to `hidg_func_list`. Composite bind requires at least one descriptor, obtains a HID function instance for each node, copies subclass/protocol/report length/report descriptor into options, assigns strings, optionally creates an OTG descriptor, and registers one configuration. The configuration callback instantiates and adds every HID function, unwinding already added functions on failure. Cleanup unregisters composite and platform drivers.

## State and Persistence Behavior

The global `hidg_func_list` is populated from platform data and holds descriptor pointers, function instances, and concrete functions. USB string and OTG descriptor state are static globals. HID report descriptors come from platform data and must remain valid for the function lifetime. No persistent storage is used.

## Dependencies and Integration Points

It depends on libcomposite, platform-device infrastructure, `linux/usb/g_hid.h`, and `u_hid.h`. It integrates board/platform code that supplies HID descriptors with the USB HID function implementation and host HID class drivers.

## Risks and Test Signals

Risks include platform descriptor lifetime, no HID descriptors resulting in `-ENODEV`, global list cleanup removing all nodes on any platform remove, partial bind cleanup for multiple functions, and report descriptor validity. Tests should provide one and multiple platform HID descriptors, enumerate keyboard/mouse/vendor reports, validate report length, exercise read/write on `/dev/hidg*`, test OTG controllers, and remove platform devices or unload after enumeration.
