<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c

## Purpose

`xe_sriov_pf_provision.c` implements Physical Function provisioning policy for Xe SR-IOV resources. It switches between automatic and custom provisioning and applies per-VF or bulk configuration for execution quantum, preemption timeout, scheduling priority, and VRAM/LMEM quota across all GTs or tiles.

## Important APIs, Types, and Functions

The public API is the `xe_sriov_pf_provision_*` family declared in the paired header. Auto provisioning flows through `xe_sriov_pf_provision_vfs()` and `xe_sriov_pf_unprovision_vfs()`, using `xe_gt_sriov_pf_config_set_fair()` and `xe_gt_sriov_pf_config_release()`. Scheduler tunables are handled by `*_apply_vf_eq`, `*_query_vf_eq`, `*_apply_vf_pt`, `*_query_vf_pt`, `*_apply_vf_priority`, and bulk equivalents. VRAM quota is handled by `*_apply_vf_vram`, `*_bulk_apply_vram`, and `*_query_vf_vram`. `xe_sriov_pf_provision_set_mode()` is the mode transition gate.

## Control Flow

Auto mode provisions VFs by iterating every GT and assigning a fair split from `VFID(1)` through `num_vfs`. Unprovisioning releases each VF on each GT. Most EQ/PT/VRAM operations take `xe_sriov_pf_master_mutex(xe)` and then iterate GTs or tiles, preserving the first error while attempting all backends. Query operations compare every GT's value and return `-EUCLEAN` through `pf_report_unclean()` if per-GT state diverges. VRAM quota rounds the requested device-wide size up to tile count times LMTT page alignment, then divides it per tile.

## State and Persistence Behavior

The persistent device-level state is `xe->sriov.pf.provision.mode`. Resource assignments themselves persist in GT PF configuration objects and tile LMTT-backed LMEM provisioning, not in this file. Switching from auto to custom preserves existing allocations; switching back to auto is refused while VFs are enabled and otherwise releases all VF resources.

## Dependencies and Integration Points

This file depends on SR-IOV helpers for VF counts and PF assertions, GT PF config/policy code for actual GuC-facing provisioning, LMTT page size for VRAM alignment, and `xe_sriov_printk.h` for diagnostics. It is called from PF enable/disable flows, sysfs bulk/per-VF attributes, and SR-IOV debugfs quota controls.

## Risks and Test Signals

Risks include partial success across GTs because the first error is returned after later GTs may already have changed, stale custom allocations when changing modes intentionally preserves resources, and inconsistent query state on multi-GT devices. Tests should cover mode transitions with VFs enabled/disabled, multi-GT inconsistency returning `-EUCLEAN`, VRAM rounding on multi-tile devices, and sysfs/debugfs paths forcing custom mode after manual quota changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c -->
