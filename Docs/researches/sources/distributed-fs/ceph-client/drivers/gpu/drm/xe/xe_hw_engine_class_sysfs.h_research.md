# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.h

Purpose: declares engine-class sysfs initialization, timeout range validation, and the kobject wrapper used to map sysfs callbacks back to Xe device and engine class state.

Important APIs/types: `xe_hw_engine_class_sysfs_init`, `xe_hw_engine_timeout_in_range`, `struct kobj_eclass`, `kobj_to_eclass`, and `kobj_to_xe`.

Control flow/state: sysfs callbacks receive a `struct kobject` and recover the embedded `kobj_eclass` to access `xe` and `eclass` pointers.

Dependencies/integration: includes Linux kobject and references `struct xe_hw_engine_class_intf`; implicitly requires `struct xe_device` visibility in users.

Risks/test signals: the inline container conversions assume every callback kobject is a `struct kobj_eclass` except the defaults child uses parent conversion. Tests should cover default file callbacks and live file callbacks.
