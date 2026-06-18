# sources/distributed-fs/ceph-client/drivers/base/faux.c

## Purpose
`faux.c` implements a minimal fake bus for devices that need sysfs lifecycle callbacks but no real hardware resources or bus-specific matching. It provides create/destroy helpers and a single always-matching synchronous driver.

## Important APIs, Types, And Functions
`struct faux_object` embeds `struct faux_device` and stores caller ops and sysfs groups. Public APIs are `faux_device_create_with_groups()`, `faux_device_create()`, `faux_device_destroy()`, and init-only `faux_bus_init()`. Internal bus callbacks are `faux_match()`, `faux_probe()`, `faux_remove()`, and `faux_device_release()`.

## Control Flow, State, And Persistence
Initialization allocates and registers a root `faux` device, registers the `faux` bus, then registers `faux_driver`. Creating a device allocates a wrapper, records ops/groups, initializes the embedded device, assigns parent or root, bus, name, release callback, and no-PM flag, then calls `device_add()`. Probe invokes caller `probe`, then adds groups only after successful initialization; group-add failure calls caller remove.

## Dependencies, Integration Points, Risks, And Test Signals
The faux bus depends on the driver core, sysfs groups, `linux/device/faux.h`, and init ordering from `driver_init()`. Risks include unique name requirements, callbacks running before create returns, group creation rollback, root-device lifetime on init failure, and synchronous binding assumptions. Test signals include successful create/destroy, probe failure returning NULL, sysfs group visibility after probe, remove callback ordering, parented and root devices, and init failure unwind.
