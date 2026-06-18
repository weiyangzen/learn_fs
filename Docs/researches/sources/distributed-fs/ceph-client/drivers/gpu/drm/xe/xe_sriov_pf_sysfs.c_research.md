<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c

## Purpose

`xe_sriov_pf_sysfs.c` builds the PF-admin sysfs tree under a PCI device for SR-IOV administration. It exposes bulk provisioning attributes, per-PF/per-VF profile attributes, VF control operations, and symlinks to PF/VF PCI devices.

## Important APIs, Types, and Functions

Internal wrappers `xe_sriov_kobj`, `xe_sriov_dev_attr`, and `xe_sriov_vf_attr` connect kobjects to `xe_device` and VF IDs. Bulk write-only attributes are `.bulk_profile/exec_quantum_ms`, `preempt_timeout_us`, `sched_priority`, and `vram_quota`. Per-function `profile/` attributes expose exec quantum, preempt timeout, scheduling priority, and VF VRAM quota. The VF control attribute `stop` maps to `xe_sriov_pf_control_stop_vf()`. Public functions are `xe_sriov_pf_sysfs_init()`, `xe_sriov_pf_sysfs_link_vfs()`, and `xe_sriov_pf_sysfs_unlink_vfs()`.

## Control Flow

Initialization creates `sriov_admin`, then child `pf` and `vfN` kobjects for every total VF, registers devm cleanup actions, and links `pf/device` to the PF device. Store paths acquire runtime PM, wait for PF readiness, parse the input, and call provisioning/control APIs. Visibility callbacks hide VRAM quota when LMTT is unavailable, hide or downgrade scheduling-priority write access for VFs, and hide control files for PF. VF link/unlink functions add or remove `device` symlinks only for enabled VFs.

## State and Persistence Behavior

The root kobject is stored in `xe->sriov.pf.sysfs.root`; per-function kobjects are stored in `xe->sriov.pf.vfs[n].kobj`. The sysfs files mutate persistent PF provisioning state and GT/tile resource assignments via the provisioning APIs. Kobjects are devm-managed with `kobject_put` cleanup.

## Dependencies and Integration Points

The file integrates Linux kobject/sysfs, DRM managed actions, Xe runtime PM, PCI SR-IOV VF lookup, PF readiness, PF control, PF provisioning, and SR-IOV logging. It is the user-visible administrative surface for PF resource shaping.

## Risks and Test Signals

Risks include partial VF symlink setup if PCI VF lookup fails mid-loop, user-visible permission mismatches for priority/VRAM on unsupported platforms, and race sensitivity around VF enable/disable versus sysfs writes. Tests should cover kobject tree creation, attribute visibility by platform/LMTT/VFID, parse failures, runtime-PM guarded writes, successful bulk/per-VF provisioning, and link/unlink idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c -->
