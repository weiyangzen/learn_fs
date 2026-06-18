# sources/distributed-fs/ceph-client/samples/kobject/kobject-example.c

Purpose: minimal kobject/sysfs example exposing three integer attributes under `/sys/kernel/kobject_example`.

Important APIs/functions: `kobject_create_and_add`, `sysfs_create_group`, `kobject_put`, `struct kobj_attribute`, `__ATTR`, `kstrtoint`, and show/store callbacks for `foo`, `baz`, and `bar`.

Control flow: init creates the kobject under `kernel_kobj`, creates one attribute group, and unwinds on failure. Attribute stores parse decimal integers into globals; show emits values. Exit puts the kobject.

State and persistence: global integers exist while module is loaded; sysfs files expose them. No persistence across unload.

Dependencies and integration: sysfs and kernel kobject infrastructure.

Risks: no locking around integer attributes, acceptable for sample but not robust shared state. Permissions allow writable attributes for root.

Test signals: load, read/write `/sys/kernel/kobject_example/{foo,baz,bar}`, check values, unload.
