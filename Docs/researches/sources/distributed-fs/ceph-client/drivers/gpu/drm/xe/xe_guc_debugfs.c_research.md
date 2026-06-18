# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.c

## Purpose
Registers GuC-specific debugfs files under a GT `uc` directory and adapts DRM debugfs callbacks to `struct xe_guc` printers.

## Important APIs, Types, And Functions
The exported entry point is `xe_guc_debugfs_register`. `guc_debugfs_show` resolves the `xe_gt` from the debugfs dentry hierarchy, takes a runtime PM guard, and calls the function stored in `drm_info_list.data`. Thin wrappers expose GuC log, LFD log, dmesg log dump, CTB, and PC printers.

## Control Flow
Registration always creates VF-safe files `guc_info` and `guc_ctb`. On non-VF devices it also creates PF-only log files. If GuC PC is not skipped, it adds `guc_pc`. File reads enter `guc_debugfs_show`, construct a `drm_printer`, resolve GT and GuC context, hold runtime PM, then invoke the selected print callback.

## State And Persistence
The file does not own persistent device state. It creates debugfs entries whose callbacks observe live GuC, CTB, log, and PC state. Runtime PM guarding is used so reads see accessible hardware-backed data.

## Dependencies And Integration Points
Depends on DRM debugfs helpers, `xe_pm`, `xe_guc_ct`, `xe_guc_log`, `xe_guc_pc`, and GuC info printing. It integrates with the GT debugfs tree layout by assuming `dent->d_parent->d_parent->d_inode->i_private` is the `xe_gt`.

## Risks And Test Signals
The dentry-parent assumption is fragile if debugfs layout changes. The PF/VF split avoids exposing PF-only or privileged paths on VFs. Tests are mainly debugfs smoke/runtime tests and manual reads of `guc_info`, `guc_ctb`, `guc_log*`, and `guc_pc`.
