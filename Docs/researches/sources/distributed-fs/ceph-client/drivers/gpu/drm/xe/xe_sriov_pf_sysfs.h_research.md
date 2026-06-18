<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h

## Purpose

`xe_sriov_pf_sysfs.h` declares the PF SR-IOV sysfs lifecycle and VF device-link helpers.

## Important APIs, Types, and Functions

`xe_sriov_pf_sysfs_init()` creates the `sriov_admin` tree. `xe_sriov_pf_sysfs_link_vfs()` creates `device` symlinks for enabled VFs. `xe_sriov_pf_sysfs_unlink_vfs()` removes those links.

## Control Flow

PF setup calls init once after PF metadata is available. VF enable paths call link for the enabled count; VF disable paths call unlink before or during teardown.

## State and Persistence Behavior

The functions update kobjects stored in PF metadata and create/remove sysfs links. The header owns no state.

## Dependencies and Integration Points

It forward-declares `struct xe_device` and is consumed by PF init and SR-IOV PCI enable/disable flows.

## Risks and Test Signals

The API assumes a PF device and valid VF counts. Tests should verify link removal matches link creation and that missing VF PCI devices are logged but do not corrupt the existing tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h -->
