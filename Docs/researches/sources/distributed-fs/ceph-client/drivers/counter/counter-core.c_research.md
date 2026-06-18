# sources/distributed-fs/ceph-client/drivers/counter/counter-core.c

Purpose: provides the Generic Counter bus, device allocation, registration, managed helpers, and module initialization. It is the central lifetime owner for `struct counter_device` and the bridge between hardware drivers, sysfs, and the character-device event interface.

Important APIs/types/functions: defines `counter_device_allochelper` to co-allocate `struct counter_device` with aligned driver private data. Exports `counter_priv()`, `counter_alloc()`, `counter_put()`, `counter_add()`, `counter_unregister()`, `devm_counter_alloc()`, and `devm_counter_add()` in namespace `COUNTER`. Internal objects include `counter_ida`, `counter_bus_type`, `counter_device_type`, and `counter_devt`.

Control flow: `counter_init()` registers the `counter` bus and reserves 256 character-device minors. `counter_alloc()` allocates storage, assigns an ID with IDA, initializes lifetime locks and dev fields, initializes the character device with `counter_chrdev_add()`, initializes the embedded device, and names it `counter%d`. Hardware drivers then fill in name, parent, ops, counts, signals, and extensions before calling `counter_add()`. `counter_add()` mirrors the parent/of_node, builds sysfs groups with `counter_sysfs_add()`, and publishes both cdev and device through `cdev_device_add()`. `counter_unregister()` removes the cdev/device pair, clears `ops` under `ops_exist_lock`, and wakes event readers.

State and persistence: persists only kernel objects and ID allocations for registered devices. Per-device private data lives adjacent to the counter object and is freed by `counter_device_release()`. The IDA ID and cdev FIFO are released when the final device reference drops.

Dependencies and integration: uses Linux bus/device/cdev/IDA/devres APIs. Integrates with `counter-sysfs.c` for attribute construction and `counter-chrdev.c` for event cdev lifetime. Hardware drivers use managed helpers heavily, with `ti-eqep.c` being a non-devm registration example that calls `counter_add()`/`counter_unregister()` directly.

Risks: `counter_alloc()` performs `counter_chrdev_add()` before `device_initialize()`, so all error paths must remain balanced. Clearing `ops` is the unregister sentinel used by cdev reads/ioctls, so hardware drivers must not free callback backing state before unregister completes. The fixed `COUNTER_DEV_MAX` of 256 bounds minors. `counter_priv()` depends on the co-allocation layout.

Test signals: register/unregister a simple counter driver, devm unwind on probe failure, ID reuse after release, sysfs and cdev presence after `counter_add()`, readers receiving `-ENODEV` after unregister, and module init/exit bus and chrdev region cleanup.
