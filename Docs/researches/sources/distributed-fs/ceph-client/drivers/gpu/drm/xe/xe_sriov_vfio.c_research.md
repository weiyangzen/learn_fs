<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c

## Purpose

`xe_sriov_vfio.c` exports the narrow PF-facing API used by the external `xe-vfio-pci` module for VF migration and lifecycle control.

## Important APIs, Types, and Functions

`xe_sriov_vfio_get_pf()` maps a VF PCI device to the PF `xe_device`. `xe_sriov_vfio_migration_supported()` gates migration on PF mode and PF migration support. Macro-generated wrappers export wait-FLR, prepare-FLR, suspend/resume, stop-copy enter/exit, resume-data enter/exit, error/stop, and stop-copy-size functions. `xe_sriov_vfio_data_read()` and `xe_sriov_vfio_data_write()` transfer migration data through PF migration helpers.

## Control Flow

Every wrapper rejects non-PF devices with `-EPERM`, rejects `PFID` or VF IDs beyond currently enabled VFs with `-EINVAL`, takes a no-resume runtime PM guard, then calls the corresponding PF control or migration function.

## State and Persistence Behavior

The file owns no state. It orchestrates persistent PF migration/control state and migration data streams managed by the PF migration subsystem.

## Dependencies and Integration Points

It depends on the public DRM Intel Xe SR-IOV VFIO header, PCI PF lookup, runtime PM guards, PF control helpers, PF migration helpers, and module-scoped symbol exports for `xe-vfio-pci`.

## Risks and Test Signals

Risks include VF ID validation tied to currently enabled VF count, no-resume PM usage requiring callers to ensure power state expectations, and cross-module ABI drift. Tests should cover non-PF rejection, PFID rejection, out-of-range VF rejection, each wrapper mapping to the intended PF helper, and data read/write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c -->
