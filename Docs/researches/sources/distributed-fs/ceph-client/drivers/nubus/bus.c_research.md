# sources/distributed-fs/ceph-client/drivers/nubus/bus.c

## Purpose
Implements the Linux driver-model bus layer for NuBus boards. It registers the `nubus` bus type, exposes driver register/unregister helpers, registers scanned board devices, releases associated resources, and provides a proc summary callback.

## Important APIs, Types, And Functions
- `nubus_bus_type` defines bus name, probe, and remove callbacks.
- `nubus_driver_register()` / `nubus_driver_unregister()` export driver-model registration for `struct nubus_driver`.
- `nubus_device_register()` initializes `struct nubus_board.dev`, names it `slot.X`, sets DMA mask, and registers it.
- `nubus_device_release()` frees functional resources associated with a board and then the board.
- `nubus_proc_show()` iterates devices and prints slot/name summaries.

## Control Flow
`postcore_initcall(nubus_bus_register)` registers the bus early. Scanning code later calls `nubus_device_register()` for each discovered board. Driver binding calls the optional NuBus driver `probe()` and `remove()` methods through bus callbacks.

## State And Persistence
Device-model state persists while board devices are registered. Functional resources are globally listed in `nubus_func_rsrcs` and removed when the board device is released.

## Dependencies And Integration Points
Depends on `linux/nubus.h`, driver core, DMA mask helpers, global NuBus resource list from `nubus.c`, and procfs sequence output.

## Risks And Edge Cases
- Release walks and mutates the global functional resource list without an explicit lock; this is acceptable for early/static NuBus lifecycle but would matter if hotplug existed.
- Device names are slot-based; duplicate registration for a slot would conflict.
- `dma_set_mask()` return value is ignored.

## Test Signals
On Macintosh NuBus systems, board devices should appear on the `nubus` bus as `slot.X`, drivers should bind via `nubus_driver_register()`, and `/proc/nubus` should list slot names when procfs is present.
