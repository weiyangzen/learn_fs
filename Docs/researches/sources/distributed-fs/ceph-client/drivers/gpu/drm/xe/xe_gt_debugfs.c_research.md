# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.c

## Purpose
Creates per-GT debugfs directories and diagnostic/control files for topology, workarounds, register save/restore, engines, MOCS, PAT, powergating, stats, default LRCs, force reset, uC, and SR-IOV-specific views.

## Important APIs and Functions
- `xe_gt_debugfs_register` creates `tile#/gt#` debugfs directories and a legacy symlink, then registers safe and PF-only files.
- Shared show callbacks: `xe_gt_debugfs_simple_show` and `xe_gt_debugfs_show_with_rpm`.
- Diagnostic printers include `hw_engines`, `steering`, `register_save_restore`, `register_save_restore_check`, default LRC dumpers, and `hwconfig`.
- Writable controls: `stats` clears GT stats; `force_reset` queues async reset; `force_reset_sync` performs synchronous reset.

## Control Flow
The GT dentry stores `struct xe_gt *` in `i_private`; `node_to_gt` recovers it from the parent dentry for DRM info callbacks. Registration always creates VF-safe files and only adds privileged PF-only MMIO views when not an SR-IOV VF. uC and SR-IOV PF/VF debugfs registration is delegated after base GT files are installed.

## State and Persistence
No core GT state is owned here, but debugfs write paths mutate GT stats or trigger reset. Runtime PM guards are used for files that read live hardware state.

## Dependencies and Integration Points
Integrates DRM debugfs, runtime PM, forcewake, GT MCR, idle, SR-IOV PF/VF debugfs, stats, topology, GuC hwconfig, LRC, MOCS, PAT, register SR, tuning, uC debugfs, and workaround dumping.

## Risks and Test Signals
- Debugfs read paths that access privileged registers must remain VF-gated to avoid invalid VF MMIO access.
- Force-reset debugfs reads trigger reset for backward compatibility; tests should prefer write path but retain legacy behavior awareness.
- `register-save-restore-check` should be useful after init/resume/reset to catch missing register programming.
