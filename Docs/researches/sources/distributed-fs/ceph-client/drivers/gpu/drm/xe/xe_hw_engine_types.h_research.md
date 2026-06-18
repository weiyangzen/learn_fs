# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_types.h

Purpose: declares engine class IDs, hardware engine IDs/masks, per-class scheduler property storage, hardware engine state, and hardware engine snapshot state.

Important types/constants: `enum xe_engine_class`, `enum xe_hw_engine_id`, class masks such as `XE_HW_ENGINE_BCS_MASK`, `XE_HW_ENGINE_MAX_INSTANCE`, `struct xe_hw_engine_class_intf`, `struct xe_hw_engine`, `enum xe_hw_engine_snapshot_source_id`, and `struct xe_hw_engine_snapshot`.

Control flow/state: hardware engine init populates `struct xe_hw_engine`; sysfs reads/writes `eclass`; exec queue creation and UAPI lookup use class/instance/logical instance; devcoredump/debug capture produces snapshots.

Dependencies/integration: includes forcewake, LRC, and register save/restore types and forward-declares BO, execlist port, GT, OA unit, and engine group.

Risks/test signals: enum ordering is ABI-sensitive inside the driver and maps to static tables. `XE_HW_ENGINE_MAX_INSTANCE` bounds parallel WQ arrays. Tests should verify masks cover intended IDs and engine info table stays aligned with enum values.
