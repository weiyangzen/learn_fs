# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-main.c

Purpose: module and USB-driver entry point for pvrusb2. It registers the USB driver, creates/destroys global context/sysfs state, and wires each probed USB interface into the pvrusb2 context plus V4L2/DVB/sysfs attachment layers.

Important APIs, types, and functions: defines driver metadata, default debug mask, global `pvrusb2_debug`, and module parameter `debug`. `pvr_setup_attach()` creates V4L2, optional DVB, and sysfs interfaces for a context. `pvr_probe()` calls `pvr2_context_create()`, stores the context with `usb_set_intfdata()`, and returns probe status. `pvr_disconnect()` clears interface data and calls `pvr2_context_disconnect()`. `pvr_driver` provides USB name, ID table, probe, and disconnect callbacks. `pvr_init()` and `pvr_exit()` handle module load/unload.

Control flow: module init initializes global context state, registers the sysfs class, registers the USB driver, and logs version/debug state. USB core invokes probe for IDs in `pvr2_device_table`; probe creates context, which in turn creates hardware and eventually calls the attach callback to expose interfaces. Disconnect tears down the context. Module exit deregisters USB, releases global context state, and unregisters sysfs class.

State and persistence: global `pvrusb2_debug` controls trace output until module unload or parameter change. Per-device state is stored in `struct pvr2_context` via USB interface driver data. No persistent storage is used.

Dependencies and integration points: depends on USB core, pvrusb2 device attributes, context manager, hardware API, V4L2 layer, optional DVB layer, sysfs support, and debug tracing. It is the top-level integration point for kernel module lifecycle.

Risks: if `usb_register()` fails after `pvr2_sysfs_class_create()`, `pvr_init()` returns without destroying the class in this file, so init-failure cleanup depends on broader kernel/module behavior. Probe failure returns `-ENOMEM` for any context creation failure, even non-allocation errors hidden inside context creation. Attach ordering determines whether V4L2/DVB/sysfs see fully initialized hardware.

Test signals: module load/unload; USB probe/disconnect; sysfs class present only while loaded; V4L2/DVB nodes appear for supported devices; debug parameter changes trace output; failure injection around context creation and USB registration.
