# sources/distributed-fs/ceph-client/include/linux/device/driver.h

Purpose: Defines the driver-specific portion of the Linux driver model, including `struct device_driver`, probe strategy, driver registration, driver attributes, device iteration, deferred probe, and module/builtin driver boilerplate macros.

Important APIs, types, and functions: Defines `enum probe_type`, `struct device_driver`, and `struct driver_attribute`. APIs include `driver_register()`, `driver_unregister()`, `driver_find()`, probe-completion waits, driver sysfs file creation/removal, `driver_set_override()`, `driver_for_each_device()`, `driver_find_device()` plus name/OF/fwnode/devt/ACPI/next wrappers, deferred probe helpers, `driver_init()`, `module_driver()`, and `builtin_driver()`.

Control flow: A subsystem-specific driver registration macro eventually registers a `device_driver` with a bus. The driver core matches devices, chooses synchronous/asynchronous probe behavior from `probe_type`, calls probe/sync_state/remove/shutdown/PM callbacks, attaches default attribute groups, and exposes optional bind/unbind unless suppressed. Iteration helpers walk bound devices and return referenced matches.

State and persistence: Driver state includes name, bus, owner, built-in module name, match tables, callbacks, sysfs groups, PM ops, coredump hook, and private driver-core structures. It lives in memory while registered and is represented in sysfs.

Dependencies and integration points: Depends on kobjects, klists, PM, bus APIs, modules, OF/ACPI match tables, sysfs attributes, devcoredump, and Rust post-unbind integration.

Risks and test signals: Risks include unregister while devices are bound, missing module owner, unsafe asynchronous probe assumptions, deferred-probe stalls, reference leaks from find helpers, and incorrect driver override parsing. Test registration/unregistration, bind/unbind sysfs, async and forced-sync probe paths, deferred probe completion, driver attributes, coredump callback, and module_driver/builtin_driver expansion.
