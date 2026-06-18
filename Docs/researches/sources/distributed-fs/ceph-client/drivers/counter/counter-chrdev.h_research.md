# sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.h

Purpose: internal header for the Generic Counter character-device layer.

Important APIs/types/functions: declares `counter_chrdev_add(struct counter_device *counter)` and `counter_chrdev_remove(struct counter_device *counter)`. It includes `linux/counter.h` for `struct counter_device`.

Control flow: `counter-core.c` calls `counter_chrdev_add()` during `counter_alloc()` before `device_initialize()` and calls `counter_chrdev_remove()` from the device release path and allocation error cleanup.

State and persistence: the header has no state; it exposes lifecycle hooks for initializing and freeing cdev/kfifo/list state embedded in `struct counter_device`.

Dependencies and integration: private to `drivers/counter`; it couples the core registration layer to `counter-chrdev.c` without exposing implementation details to hardware drivers.

Risks: any signature changes require coordinated updates to `counter-core.c`; the header intentionally does not expose `counter_push_event()` because that is declared by the public counter API.

Test signals: successful allocation/registration of any counter device proves `counter_chrdev_add()` is callable; unregister/free paths and allocation-error injection prove `counter_chrdev_remove()` cleanup is balanced.
