# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.h

Purpose: declares GT sysfs initialization and provides a helper to recover `struct xe_gt` from a GT kobject.

Important APIs: `xe_gt_sysfs_init` and inline `kobj_to_gt`, which uses `container_of(kobj, struct kobj_gt, base)->gt`.

Control flow: sysfs attribute handlers use `kobj_to_gt` to map from their kobject context back to the GT.

State and persistence: no state beyond the `kobj_gt` wrapper defined in the types header.

Dependencies and integration: includes `xe_gt_sysfs_types.h`; used by throttling and frequency sysfs code.

Risks: `kobj_to_gt` assumes the kobject is a `struct kobj_gt`, so it must not be used on child group kobjects unless their parent is first resolved appropriately.

Test signals: sysfs attribute handlers on GT kobjects and type-safety review of call sites.
