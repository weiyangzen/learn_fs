# sources/distributed-fs/ceph-client/drivers/base/container.c

### Purpose
`container.c` defines the small system bus used for container devices under the driver core. It provides a bus type named `container` and registers it as a system subsystem.

### Important APIs, Types, And Functions
The main exported object is `container_subsys`, a `struct bus_type` with `.name`, `.dev_name`, `.online`, and `.offline`. `trivial_online()` always succeeds. `container_offline()` converts `struct device` to `struct container_dev` and delegates to the optional `container_dev.offline` callback. `container_dev_init()` registers the subsystem with `subsys_system_register()`.

### Control Flow
At init time, `container_dev_init()` calls `subsys_system_register(&container_subsys, NULL)`. That creates the bus and root system device through `bus.c` helpers. Online requests succeed unconditionally. Offline requests only do work if the concrete container device supplies an `.offline` method; otherwise they succeed.

### State, Persistence, And Dependencies
The file has no private mutable state. Persistent state is created by the driver core when registering `container_subsys`, including sysfs directories and the root device. Dependencies are `linux/container.h`, `base.h`, and the bus/subsystem registration path in `bus.c`.

### Integration Points
Container device providers use the `container_subsys` bus and `struct container_dev` callbacks to expose devices under the system-device hierarchy. The generic `online` and `offline` sysfs attribute handling comes from `core.c` when the bus supports these callbacks.

### Risks
The online path is intentionally a no-op, so any device-specific reactivation work must live elsewhere or be unnecessary. Offline behavior depends entirely on the optional container callback and returns success when none is provided. Registration failure is logged but not recovered in this file.

### Test Signals
Signals include successful `/sys/devices/system/container` registration, offline callback invocation and return propagation, no-op online success, behavior without an offline callback, and init-time error logging if subsystem registration fails.
