# sources/distributed-fs/ceph-client/drivers/rapidio/rio-driver.c

Purpose: implements RapidIO bus driver-model glue: device/driver matching, probe/remove/shutdown dispatch, driver registration helpers, mport class registration, bus registration, uevent modalias generation, and reference helpers for `struct rio_dev`.

Important APIs, types, and functions: `rio_match_device()` compares `struct rio_device_id` tables with `struct rio_dev` IDs. `rio_dev_get()` and `rio_dev_put()` wrap device references and are exported. `rio_device_probe()`, `rio_device_remove()`, and `rio_device_shutdown()` are bus callbacks. `rio_register_driver()` and `rio_unregister_driver()` wrap `driver_register()`/`driver_unregister()` for `struct rio_driver`. `rio_attach_device()` assigns `rio_bus_type` to a `rio_dev`. Exported globals include `rio_mport_class` and `rio_bus_type`.

Control flow: at `postcore_initcall`, `rio_bus_init()` registers the `rapidio_port` class and the `rapidio` bus, unwinding the class if bus registration fails. When a driver is registered, its embedded `device_driver` name and bus are initialized. Bus matching uses the ID table, accepting wildcard vendor/device/assembly IDs. Probe obtains a device reference before invoking the driver probe and stores `rdev->driver` only on success; failure drops the reference. Remove invokes the bound driver's remove callback, clears the driver pointer, and drops the reference acquired at probe. Shutdown delegates to the driver if present. Uevents emit `MODALIAS=rapidio:v...` for module autoloading.

State and persistence: persistent state is held in the Linux device model: registered class, registered bus type, bound driver pointer on each `rio_dev`, and device reference counts. The file itself keeps no mutable global list beyond the class/bus objects.

Dependencies and integration: depends on Linux device model, RapidIO sysfs groups (`rio_mport_groups`, `rio_dev_groups`, `rio_bus_groups`), and RapidIO headers. Device creation code, including `rio_mport_cdev` dynamic add/remove, calls `rio_attach_device()` and `rio_add_device()` elsewhere to put devices onto this bus.

Risks: probe assumes `rdrv->id_table` is present; drivers without ID tables will not bind. Reference handling is simple but must be paired with device creation/removal paths outside this file. `rio_match_bus()` has compact formatting around the `out` label but functional behavior is straightforward.

Test signals: register a test RapidIO driver with exact and wildcard IDs, verify probe/remove reference transitions, check shutdown callback dispatch, inspect uevent modalias strings, test bus/class registration failure unwinding, and ensure `rio_mport_class` consumers see add/remove callbacks.
