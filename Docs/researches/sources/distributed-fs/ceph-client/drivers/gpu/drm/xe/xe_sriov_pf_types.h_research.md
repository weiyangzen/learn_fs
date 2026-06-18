<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h

## Purpose

`xe_sriov_pf_types.h` defines the persistent per-PF and per-VF metadata embedded in `struct xe_device` when running as an SR-IOV Physical Function.

## Important APIs, Types, and Functions

`struct xe_sriov_metadata` stores a VF kobject, negotiated service version, and migration state. `struct xe_device_pf` stores PF mode flags, total/max VF counts, a guard for VF enabling, the PF master mutex, provisioning state, migration state, service version state, sysfs root, and the `vfs` metadata array.

## Control Flow

PF initialization allocates/fills this structure and its `vfs` array, initializes the master lock and service/provisioning state, then PF sysfs/debugfs/control/migration paths operate through these fields.

## State and Persistence Behavior

All fields persist for the PF device lifetime. `master_lock` serializes cross-GT VF configuration. `guard_vfs_enabling` protects enable flows. Per-VF kobjects and migration/service metadata remain indexed by VFID, with index zero representing PF metadata where used.

## Dependencies and Integration Points

The header includes guard, provisioning, service, and migration type headers and is included by Xe device SR-IOV mode-specific state. It is a central contract for PF provisioning, sysfs, VFIO migration, service negotiation, and control.

## Risks and Test Signals

Because many subsystems share this structure, layout or ownership changes can break teardown and reset paths. Tests should cover allocation/cleanup of `vfs`, master-lock use around provisioning, service reset on VF reset, and sysfs kobject lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h -->
