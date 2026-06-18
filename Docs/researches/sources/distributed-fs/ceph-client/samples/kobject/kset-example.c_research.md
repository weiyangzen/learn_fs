# sources/distributed-fs/ceph-client/samples/kobject/kset-example.c

Purpose: demonstrates custom kobject type, attributes, release method, default groups, visibility callback, and kset membership.

Important APIs/functions: `struct foo_obj`, `struct foo_attribute`, `sysfs_ops`, `kobj_type`, `kset_create_and_add`, `kobject_init_and_add`, `kobject_uevent`, `kobject_put`, `__ATTR`, `ATTRIBUTE_GROUPS`, and per-object show/store callbacks.

Control flow: init creates a kset and three objects (`foo`, `bar`, `baz`). Each object has default attributes and sends an add uevent. Attribute callbacks access per-object integers. Exit puts each object and unregisters the kset; release callbacks free object memory.

State and persistence: per-object integer fields under sysfs while loaded.

Dependencies and integration: sysfs, kobjects, ksets, and uevent infrastructure.

Risks: attributes are sample-level and unlocked. Visibility callback changes mode for one attribute and must stay consistent with default groups. Correct release callback is critical for memory lifetime.

Test signals: load and inspect `/sys/kernel/kset_example/`, read/write object attributes, observe uevents, unload and verify release logs.
