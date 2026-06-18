# sources/distributed-fs/ceph-client/include/linux/siox.h

## Purpose

`siox.h` defines the SIOX device and driver model interface. SIOX devices are attached to a SIOX master, expose status and watchdog statistics through kernfs nodes, and bind to `siox_driver` implementations that exchange cyclic input/output data.

## Important APIs, Types, And Functions

`struct siox_device` stores master membership, embedded device, type, input/output byte sizes, status type, last status values, connection state, watchdog and status error counters, and kernfs nodes for status exposure. `struct siox_driver` provides `probe`, `remove`, `shutdown`, `set_data`, `get_data`, and embedded `device_driver`.

Helpers and APIs include `to_siox_device()`, `siox_device_synced()`, `siox_device_connected()`, `to_siox_driver()`, `__siox_driver_register()`, `siox_driver_register()`, `siox_driver_unregister()`, and `module_siox_driver()`.

## Control Flow

A SIOX driver registers with `siox_driver_register()`. Matching devices call `probe()`. During master cycles, framework code calls `set_data()` with inbound status plus payload space excluding the status byte, and `get_data()` to retrieve outbound data excluding the status byte. Removal and shutdown callbacks handle teardown. Inline register/unregister helpers connect the driver to the generic device model.

## State And Persistence

`siox_device` persists while the physical or logical SIOX device exists. It tracks connection and synchronization status, status bytes across cycles, and cumulative error statistics. Driver-private state is expected to live through the embedded device model.

## Dependencies And Integration Points

Dependencies include the device model, module registration helpers, kernfs, list handling, and integer types. Integration points are SIOX master drivers, sysfs/kernfs status reporting, module loading, and cyclic industrial I/O device drivers.

## Risks And Test Signals

Risks include mismatched in/out byte sizes, drivers treating the framework-managed status byte as payload, stale connection status, and error counter lifetime issues. Test signals include driver probe/remove, cyclic data exchange, status/watchdog error increments, connected/synced reporting, shutdown behavior, and module register/unregister loops.
