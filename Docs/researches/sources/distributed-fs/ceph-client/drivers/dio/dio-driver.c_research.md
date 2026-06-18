# sources/distributed-fs/ceph-client/drivers/dio/dio-driver.c

Purpose: connects DIO devices to the Linux driver core by registering the `dio` bus, matching DIO ids, and exposing registration helpers for DIO drivers.

Important APIs/types/functions: exports `dio_register_driver()`, `dio_unregister_driver()`, and `dio_bus_type`. Internal helpers are `dio_match_device()`, `dio_device_probe()`, and `dio_bus_match()`.

Control flow: `postcore_initcall(dio_driver_init)` registers `dio_bus_type`. Driver registration fills common `struct device_driver` fields and calls `driver_register()`. Bus matching checks a driver's id table against a DIO device. Matching treats `DIO_WILDCARD` as universal, compares full encoded ids when the primary id needs a secondary id, and otherwise compares only the primary byte. Probe re-runs the match, calls the driver's `probe()` callback, and records the driver on success.

State and persistence behavior: bus type registration persists for the kernel lifetime. Each successful probe stores the owning `struct dio_driver *` in the `struct dio_dev`; unregister relies on the driver core to unwind device bindings.

Dependencies and integration points: depends on `linux/dio.h` conversion macros and driver/device types. It is used by DIO bus enumeration in `dio.c` and any DIO device drivers.

Risks and test signals: probe treats any nonnegative driver `probe()` result as success and normalizes it to zero, so drivers must return negative values on failure. Matching depends on correct secondary-id encoding. Test signals include bus registration before DIO device enumeration, wildcard and secondary-id match behavior, driver bind/unbind callbacks, and exported symbol availability to DIO drivers.
