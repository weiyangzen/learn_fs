# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.h

Purpose: conditional public header for pvrusb2 sysfs support. It exposes sysfs class and per-context creation hooks, or inline no-ops when the feature is disabled.

Important APIs, types, and functions: declares `pvr2_sysfs_class_create()`, `pvr2_sysfs_class_destroy()`, and `pvr2_sysfs_create(struct pvr2_context *mp)` under `CONFIG_VIDEO_PVRUSB2_SYSFS`; otherwise defines empty inline versions.

Control flow: module init calls class create, module exit calls class destroy, and per-device attach calls create. With sysfs disabled, the same call sites compile away.

State and persistence: no state in the header. Implementation state lives in `pvrusb2-sysfs.c` and in pvrusb2 context/channel objects.

Dependencies and integration points: includes Linux list/sysfs declarations and `pvrusb2-context.h`. It lets `pvrusb2-main.c` and attach code avoid preprocessor-heavy call sites.

Risks: callers should not assume sysfs exists unless the config is enabled. The no-op path means tests must cover both enabled and disabled builds.

Test signals: build with `CONFIG_VIDEO_PVRUSB2_SYSFS=y/m` and disabled; verify call sites need no extra ifdefs; class/device entries appear only in enabled builds.
