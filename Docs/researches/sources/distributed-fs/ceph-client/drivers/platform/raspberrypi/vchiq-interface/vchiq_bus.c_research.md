# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_bus.c

Purpose: Generic VCHIQ bus implementation for non-discoverable VideoCore services. It lets the platform driver register named VCHIQ child devices and lets kernel VCHIQ clients bind as normal Linux drivers.

Important APIs, types, and functions: `vchiq_bus_type` defines `.name = "vchiq-bus"`, name-based `.match`, modalias `.uevent`, and probe/remove shims. `vchiq_device_register()` allocates a `struct vchiq_device`, initializes its embedded `struct device`, inherits DMA configuration from the parent, stores parent driver management data, and registers the device. `vchiq_device_unregister()` unregisters it. `vchiq_driver_register()` and `vchiq_driver_unregister()` export registration for `struct vchiq_driver`.

Control flow: `vchiq_arm.c` registers the bus at module init. Platform probe calls `vchiq_device_register(parent, "bcm2835-audio")`; matching is string equality between device name and driver name. Probe/remove callbacks cast from generic device/driver to VCHIQ-specific wrappers and call client hooks.

State and persistence: each registered VCHIQ device is heap allocated and freed by `vchiq_device_release()`. The device stores a pointer to the platform driver's management state. No persistent storage exists.

Dependencies and integration points: depends on Linux driver core, OF DMA configuration, and VCHIQ public bus headers. Integrates with kernel module autoload via `MODALIAS=vchiq:<name>`.

Risks: matching by exact `dev_name()` requires driver names to match registered service names precisely. `vchiq_device_unregister()` assumes a non-NULL pointer; callers should guard failed registrations. Device `init_name` and release semantics are simple but require no later renaming.

Test signals: register/unregister a dummy VCHIQ device and driver, check modalias emission, probe/remove call order, DMA mask configuration, and failure cleanup on `device_register()` errors.
