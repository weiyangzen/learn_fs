# sources/distributed-fs/ceph-client/drivers/i3c/master.c

Purpose: I3C core bus/master framework. It implements `i3c_bus_type`, bus IDs, sysfs/modalias handling, address-slot management, CCC helpers, DAA orchestration, I2C compatibility adapter, IBI dispatch and generic pools, master registration/unregistration, and locked operations used by `device.c`.

Important APIs/types/functions: Global state includes `i3c_bus_idr`, `i3c_core_lock`, dynamic bus numbering, and `i3c_bus_notifier`. Exports bus notifier/iterator APIs, hotjoin enable/disable, free-address lookup, locked CCC helpers, `i3c_master_do_daa*()`, DMA map/unmap helpers, `i3c_master_set_info()`, `i3c_master_add_i3c_dev_locked()`, generic IBI pool helpers, and `i3c_master_register/unregister()`.

Control flow: `i3c_init()` registers the I2C notifier and I3C bus. `i3c_master_register()` validates ops, initializes bus/device state, parses OF children, selects bus mode, allocates workqueue, initializes the bus, registers the master device, creates the I2C adapter facade, enables PM, and registers discovered I3C devices. Bus init attaches static I2C devices, runs controller `bus_init`, resets dynamic addresses, disables events, reserves requested addresses, handles SETDASA, and runs DAA.

State and persistence: `struct i3c_bus` tracks id, mode, SCL rates, current master, address slots, and device lists. Device descriptors persist PID/BCR/DCR/HDR/speed data, boardinfo, client device, master private data, and IBI state. Generic IBI pools persist slots and payload buffers.

Dependencies/integration: Linux driver core, OF, I2C core/notifier, runtime PM, DMA mapping, workqueues, IDR, rwsem locking, and controller `i3c_master_controller_ops`.

Risks: Address-slot bookkeeping and attach/reattach error paths are complex. Maintenance vs normal-use locking must remain correct. IBI teardown waits for pending work. Runtime PM spans core and controller code. The uevent path assumes descriptors are valid for registered devices.

Test signals: Master registration rollback, OF I2C/I3C parsing, mixed bus mode selection, RSTDAA/DAA, duplicate hotjoin rediscovery with IBI restoration, I2C adapter notifier attach/detach, sysfs, hotjoin APIs, IBI pool exhaustion/recycle, DMA bounce mapping, and PM paths.
