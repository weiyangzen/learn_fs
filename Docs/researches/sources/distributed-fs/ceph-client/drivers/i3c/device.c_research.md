# sources/distributed-fs/ceph-client/drivers/i3c/device.c

Purpose: Public I3C client-driver API layer. It validates client calls, handles runtime PM and bus locking, delegates to locked master-core helpers, manages IBI lifecycle wrappers, exposes device info and ID matching, and registers I3C drivers.

Important APIs/types/functions: Exports `i3c_device_do_xfers()`, `i3c_device_do_setdasa()`, `i3c_device_get_info()`, IBI request/enable/disable/free, `i3cdev_to_dev()`, `i3c_device_match_id()`, `i3c_device_get_supported_xfer_mode()`, `i3c_driver_register_with_owner()`, and `i3c_driver_unregister()`.

Control flow: Transfer and SETDASA APIs take runtime PM, acquire the bus normal-use read lock, call locked helpers, unlock, and release PM. IBI APIs lock the bus and `desc->ibi_lock` before delegating to master ops. Driver registration sets owner and bus type, requires a probe callback, and calls `driver_register()`.

State and persistence: This file observes descriptor state rather than owning it. IBI enable can hold a runtime PM reference until disable unless runtime IBI is allowed. Device info snapshots come from `dev->desc->info`.

Dependencies/integration: Internal helpers from `internals.h`, `i3c_bus_type` from `master.c`, runtime PM, mutex/rwsem locking, I3C ID tables, and controller implementations.

Risks: Transfer validation rejects missing buffers. IBI PM reference balancing is subtle. `i3c_device_get_supported_xfer_mode()` assumes a valid descriptor/master. Clients should disable IBI before freeing resources.

Test signals: Invalid transfer arrays, zero transfer count, ID matching with random PID, IBI request without handler/slots, enable/disable PM balance, and driver registration without probe.
