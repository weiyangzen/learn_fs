# File Research: sources/cow-pools/bcachefs-tools/include/linux/kobject.h

This header provides a compact kobject/sysfs compatibility layer. It defines `struct kobj_type`, `struct kobj_attribute`, `struct kobject`, and kobject event enums. The user-space `struct kobject` stores name, parent, type, refcount, state bits, and dynamic arrays of subdirectories/files/bin files.

It declares object lifecycle operations (`kobject_init`, `kobject_add`, `kobject_del`, `kobject_get`, `kobject_put`) and sysfs read/write helpers. `kobject_uevent_env()` is a no-op, and `fs_kobj` is null.
