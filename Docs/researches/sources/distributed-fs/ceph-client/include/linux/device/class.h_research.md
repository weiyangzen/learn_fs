# sources/distributed-fs/ceph-client/include/linux/device/class.h

Purpose: Defines the class-specific driver-model API for grouping devices by function rather than physical bus topology.

Important APIs, types, and functions: Defines `struct class`, `struct class_dev_iter`, `struct class_attribute`, `struct class_attribute_string`, and `struct class_interface`. APIs register/unregister/test classes, create class_compat links, iterate/find class devices, create/remove class files with optional namespace, show string attributes, register/unregister class interfaces, and create/destroy dynamically allocated classes.

Control flow: A subsystem registers a class with default attributes, devnode/uevent/release/shutdown/namespace/ownership/PM callbacks. Devices assigned to the class appear in the class hierarchy and can be found or iterated by helpers. Class interfaces receive add/remove callbacks for matching devices without exclusively binding them like drivers.

State and persistence: Class state is held by the driver core in private structures and kobjects; class devices and attributes exist in sysfs while registered. No persistent configuration is stored by the header.

Dependencies and integration points: Depends on kobjects, klists, PM, bus matching helpers, namespace operations, and devtmpfs node callbacks. Used by block, net, input, tty, DRM, and many other functional device groupings.

Risks and test signals: Risks include missing release callbacks for dynamic classes/devices, leaking references from `class_find_device()`, wrong namespace/ownership in sysfs, class interface callbacks racing with removal, and devnode mode mistakes. Test class register/unregister, device creation under classes, class attribute read/write, namespace-specific files, class interface add/remove, class_compat links, and dynamic `class_create()` cleanup.
