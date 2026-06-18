# sources/distributed-fs/ceph-client/drivers/misc/rpmb-core.c

Purpose: implements the kernel RPMB class, allowing storage providers to register Replay Protected Memory Block devices and clients to find devices, hold references, and route RPMB request/response frames.

Important APIs and types: global `rpmb_ida` allocates class device IDs. Exported APIs are `rpmb_dev_get()`, `rpmb_dev_put()`, `rpmb_route_frames()`, `rpmb_dev_find_device()`, `rpmb_interface_register()`, `rpmb_interface_unregister()`, `rpmb_dev_register()`, and `rpmb_dev_unregister()`. `rpmb_class` defines class name and release callback.

Control flow: `rpmb_dev_register()` validates descriptor, copies the device ID, allocates an ID, initializes device name/class/parent, and registers the device. Release frees ID, copied dev_id, and object. Frame routing validates non-null request/response buffers and delegates to provider `descr.route_frames()` with the parent device. Unregister deletes the device and drops its reference. `subsys_initcall()` registers the class early; module exit destroys IDA and unregisters class.

State and persistence: class devices and IDA allocations are in kernel memory. The RPMB storage itself is external persistent secure storage; this file only routes frames.

Dependencies and integration points: depends on `<linux/rpmb.h>`, device class infrastructure, class interfaces, and provider drivers that supply `struct rpmb_descr`.

Risks and test signals: descriptor ownership is mixed: the struct is copied, but `dev_id` is deep-copied. Providers must unregister at the correct parent lifetime. Tests should cover invalid descriptors, allocation failure unwind, class interface notifications, find-device reference handling, route callback error propagation, and unregister/release sequencing.
