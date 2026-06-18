# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs_types.h

Purpose: defines the wrapper type connecting a sysfs kobject to an Xe GT.

Important type: `struct kobj_gt` contains the base `struct kobject` and a `struct xe_gt *gt`.

Control flow: `xe_gt_sysfs_init` allocates and registers this wrapper; `kobj_to_gt` retrieves the GT for sysfs handlers.

State and persistence: wrapper lifetime is owned by kobject reference counting and device-managed cleanup.

Dependencies and integration: includes Linux kobject and forward-declares `struct xe_gt`.

Risks: release must free the wrapper allocation, and users must not keep `gt` references past GT teardown.

Test signals: kobject lifetime tests during driver bind/unbind and sysfs access races.
