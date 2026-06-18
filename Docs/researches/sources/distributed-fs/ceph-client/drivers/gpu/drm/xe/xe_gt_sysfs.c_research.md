# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.c

Purpose: creates the per-GT sysfs kobject under a tile sysfs node.

Important APIs and functions: `xe_gt_sysfs_init` allocates `struct kobj_gt`, initializes its kobject type, adds it as `gt%d` under `tile->sysfs`, stores `gt->sysfs`, and registers a managed cleanup action. `xe_gt_sysfs_kobj_release` frees the wrapper object; `gt_sysfs_fini` drops the kobject reference.

Control flow: initialization is called during GT setup after tile sysfs exists. On kobject add failure, the initialized kobject is put, invoking release.

State and persistence: `gt->sysfs` points to the kobject for the GT lifetime. Sysfs entries are kernel object lifetime state, not persistent storage.

Dependencies and integration: depends on Linux kobject/sysfs, DRM managed device actions, and GT/tile/device types. Other GT sysfs feature groups attach under this kobject.

Risks: kobject lifetime correctness depends on exactly one `kobject_put` through managed cleanup after successful add. `kzalloc_obj` allocation failure or `kobject_add` failure must not leak.

Test signals: GT sysfs directory creation/removal for multi-tile/multi-GT devices, failure injection on allocation/add, and use-after-free checks during device removal.
