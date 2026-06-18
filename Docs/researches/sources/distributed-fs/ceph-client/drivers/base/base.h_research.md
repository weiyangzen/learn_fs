# sources/distributed-fs/ceph-client/drivers/base/base.h

## Purpose
Defines private driver-core structures, helpers, and internal function declarations used only within `drivers/base`. It is the shared internal contract for bus/class/device private state, initialization ordering, probing, devres, device links, devtmpfs, module sysfs, and optional subsystems.

## Important APIs, Types, And Functions
- `struct subsys_private` backs `bus_type` and `class` objects with ksets, klists, notifier heads, autoprobe flags, glue dirs, and lock keys.
- `struct driver_private` stores a driver kobject, device list, bus node, module kobject, and public driver pointer.
- `struct device_private` stores child/parent/driver/bus/class list nodes, deferred probe state, async driver, optional Rust driver type, and dead flag.
- Declarations cover init functions, bus/driver/device probe helpers, devres internals, deferred probing, device links, devtmpfs, software nodes, pinctrl binding, and auxiliary bus init.

## Control Flow
Driver-core C files include this header to share private layout and call internal helpers. Startup uses declared init functions such as `devices_init()`, `buses_init()`, `classes_init()`, `firmware_init()`, `platform_bus_init()`, `faux_bus_init()`, `cpu_dev_init()`, and optional `auxiliary_bus_init()`. Probe/bind paths use internal bus, driver, deferred-probe, and device-link helpers.

## State And Persistence
The structs define persistent private state attached to public bus/class/device/driver objects. Inline get/put wrappers manage subsystem kset references. `device_set_driver()` writes `dev->driver` with `WRITE_ONCE()` to support lockless readers such as uevent paths.

## Dependencies And Integration Points
Used broadly across `drivers/base`. Conditional blocks integrate modules+sysfs, devtmpfs, block class, pinctrl, auxiliary bus, hypervisor, Rust driver type metadata, and device links.

## Risks And Edge Cases
Because this is private layout, changes can silently affect many driver-core files. Locking and lifetime semantics are central: wrong kset/klist reference handling can produce leaks or use-after-free. `device_set_driver()` documents lockless-read concerns and must preserve atomic pointer update semantics.

## Test Signals
All driver-core build configurations, driver bind/unbind/probe defer paths, class/bus registration, devres release ordering, device-link supplier/consumer operations, devtmpfs node creation/removal, and lockdep coverage for subsystem private locks are useful validation.
