# sources/distributed-fs/ceph-client/scripts/gdb/linux/device.py

Purpose: Adds GDB commands/functions for traversing Linux driver-core buses, classes, devices, and child device trees.

Important APIs/classes: `dev_name()`, `for_each_bus()`, `for_each_class()`, `get_bus_by_name()`, `get_class_by_name()`, `klist_for_each()`, `bus_for_each_device()`, `class_for_each_device()`, `device_for_each_child()`, commands `lx-device-list-bus`, `lx-device-list-class`, `lx-device-list-tree`, and functions `$lx_device_find_by_bus_name`, `$lx_device_find_by_class_name`.

Control flow: Bus/class iteration walks global `bus_kset` and `class_kset` kobject lists, converts containers to `subsys_private`, then traverses klist device nodes. Commands list all buses/classes or a named one; tree command validates a `struct device *` expression and recursively prints children. Finder functions return the first matching device by name.

State/persistence: Registers commands/functions at import. Uses cached GDB types.

Dependencies/integration: GDB Python API, `linux.utils.container_of`, `linux.lists.list_for_each_entry`, and driver-core struct layouts.

Risks: Strongly tied to kernel internals such as `struct subsys_private` and `struct device_private`. Invalid pointers or corrupted lists can make traversal fail. Finder functions return `None` silently when not found.

Test signals: List all buses/classes, query known bus/class and device names, recursive child tree traversal, invalid pointer argument, and kernels with changed driver-core layouts.
