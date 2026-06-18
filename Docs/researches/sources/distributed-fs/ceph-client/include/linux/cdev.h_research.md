## sources/distributed-fs/ceph-client/include/linux/cdev.h

**Purpose:** This header defines the kernel character-device core object and registration helpers.

**Important APIs/types/functions:** `struct cdev` embeds a `kobject`, module owner, file operations pointer, list node, and device number/count. APIs include `cdev_init()`, `cdev_alloc()`, `cdev_put()`, `cdev_add()`, `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`, `cdev_del()`, and `cd_forget()`.

**Control flow, state, persistence:** Drivers initialize or allocate a `cdev`, bind file operations and device numbers, add it to the char-device map, optionally bind it to a device object, then delete/put during teardown. State persists in the VFS/device model while registered.

**Dependencies/integration:** Depends on kobjects, modules, file operations, inodes, and device numbers. Integrates with `device_create()`, sysfs, devtmpfs/udev, and VFS open path.

**Risks and test signals:** Risks include registering before file ops are ready, device-number collisions, parent lifetime bugs, deleting while open without correct refcounts, and mixing `cdev_add` with `cdev_device_add` incorrectly. Test signals include open/read/write/ioctl smoke tests, hot-unplug while open, sysfs/devnode checks, module unload, and refcount debug.
