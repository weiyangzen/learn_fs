# sources/distributed-fs/ceph-client/include/linux/device/faux.h

Purpose: Declares a simple faux-bus device abstraction for drivers that need a `struct device` anchor without real bus resources or binding complexity.

Important APIs, types, and functions: Defines `struct faux_device`, `to_faux_device()`, `struct faux_device_ops`, `faux_device_create()`, `faux_device_create_with_groups()`, `faux_device_destroy()`, `faux_device_get_drvdata()`, and `faux_device_set_drvdata()`.

Control flow: A caller creates a named faux device with optional parent, callbacks, and attribute groups. The faux bus probes it, optionally invoking `probe`; later destruction removes it and invokes optional remove handling. Driver data helpers forward to the embedded `struct device`.

State and persistence: State is the embedded `struct device`, optional sysfs groups, driver data, and faux bus binding state. It is in-memory and visible through the driver model while alive.

Dependencies and integration points: Depends on container helpers and device core. Intended for firmware loading or other tasks that need device-scoped APIs, devres, logging, or sysfs without platform resources.

Risks and test signals: Risks include using faux devices where real hardware resources need bus semantics, missing destroy calls, callback lifetime bugs, and sysfs group cleanup mistakes. Test create/destroy, parent reference handling, probe failure, remove callback, drvdata helpers, and attribute group visibility.
