<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h

## Purpose

`xe_sriov_vf.h` declares the VF SR-IOV lifecycle, migration capability, and debugfs API.

## Important APIs, Types, and Functions

The header exposes `xe_sriov_vf_init_early()`, `xe_sriov_vf_init_late()`, `xe_sriov_vf_migration_supported()`, `xe_sriov_vf_migration_disable()`, and `xe_sriov_vf_debugfs_register()`.

## Control Flow

VF device initialization calls early then late init. Migration-capable code checks the supported helper before registering CCS or migration paths. Debugfs setup calls the registration function with the VF root dentry.

## State and Persistence Behavior

The APIs mutate or read `xe->sriov.vf` state, especially the migration disabled flag and CCS state initialized later.

## Dependencies and Integration Points

It depends on Linux types and forward declarations for `dentry` and `xe_device`. Consumers include VF probe/init, debugfs setup, and VF migration support code.

## Risks and Test Signals

Callers must only use these functions in VF mode. Build tests should catch signature drift and VF init tests should confirm early disable prevents late CCS setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h -->
