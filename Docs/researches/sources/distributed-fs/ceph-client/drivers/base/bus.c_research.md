# sources/distributed-fs/ceph-client/drivers/base/bus.c

### Purpose
`bus.c` implements Linux driver-core bus and subsystem registration for the Ceph client source tree. It owns `/sys/bus`, `/sys/devices/system`, bus-level sysfs attributes, bus device/driver lists, driver bind/unbind controls, subsystem interfaces, bus notifiers, and helper registration for system and virtual subsystems.

### Important APIs, Types, And Functions
The file centers on `struct subsys_private`, `struct bus_type`, `struct device_driver`, and kobject/kset/klist glue. Exported entry points include `bus_register()`, `bus_unregister()`, `bus_add_device()`, `bus_remove_device()`, `bus_add_driver()`, `bus_remove_driver()`, `bus_for_each_dev()`, `bus_find_device()`, `bus_for_each_drv()`, `bus_rescan_devices()`, `device_reprobe()`, `subsys_interface_register()`, `subsys_interface_unregister()`, `subsys_system_register()`, `subsys_virtual_register()`, `driver_find()`, `bus_get_dev_root()`, and `buses_init()`. Sysfs helpers include `bus_create_file()`, `bus_remove_file()`, driver `bind`, `unbind`, `uevent`, and bus `drivers_probe`, `drivers_autoprobe`, and `uevent`.

### Control Flow
`buses_init()` creates the global `/sys/bus` and `/sys/devices/system` ksets. `bus_register()` allocates a `subsys_private`, registers the bus kset, creates `devices` and `drivers` child ksets, initializes interface lists and klist iterators, adds probe control files, and installs bus attribute groups. `bus_add_device()` attaches bus attributes and sysfs links, then adds the device to the bus klist; `bus_probe_device()` performs initial probing and notifies registered `subsys_interface` callbacks. `bus_add_driver()` creates driver kobjects, adds the driver to the bus driver klist, optionally probes existing devices, adds module links and bind/unbind files, and leaves cleanup to error labels on early failures. Removal mirrors this order, detaching drivers and dropping the bus reference taken at add time.

### State, Persistence, And Dependencies
Persistent runtime state is held in global `bus_kset`, `system_kset`, and each bus's `subsys_private` ksets, klists, mutex, lockdep key, notifier chain, root device, and autoprobe flag. The persistent external surface is sysfs. Dependencies include kobject/kset/klist, sysfs, driver probing (`driver_attach()`, `device_attach()`), module links, driver core PM hooks, and `base.h` internals.

### Integration Points
This file is a foundation for all devices and drivers in the tree, including block, network, platform, CPU, and container/system subsystems. `subsys_system_register()` and `subsys_virtual_register()` are used by compatibility-style subsystems that want a root device under `/sys/devices/system` or `/sys/devices/virtual`. `bus_notify()` feeds bus notifier users, while `drivers_probe` and driver `bind`/`unbind` expose manual reprobe controls to userspace.

### Risks
Reference counting is subtle: `bus_to_subsys()` returns an incremented reference, and add paths intentionally retain an extra reference until the corresponding remove path, causing several valid double-`subsys_put()` sequences. Bind/unbind sysfs paths must cope with devices disappearing between lookup and attach. Probe controls require parent locking for buses with `need_parent_lock`. `bus_add_driver()` logs and continues after some sysfs group failures, so partial optional files can exist. `driver_find()` deliberately returns a raw driver pointer without preventing concurrent unregister; callers must provide exclusion.

### Test Signals
Useful signals include bus register/unregister leak checks, sysfs layout under `/sys/bus/<name>`, manual bind/unbind/probe behavior, `drivers_autoprobe=0` versus `1`, notifier ordering, subsystem interface add/remove callbacks for already-present devices, reprobe with parent locking, and fault injection through kset/sysfs allocation failures.
