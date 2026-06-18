<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile

Purpose: Builds the TVE200 DRM module from its two source objects.

Important APIs/types/functions: `tve200_drm-y` includes `tve200_display.o` and `tve200_drv.o`; `obj-$(CONFIG_DRM_TVE200)` emits `tve200_drm.o`.

Control flow: Kernel kbuild aggregates display-pipe code and platform-driver code into one driver object when `DRM_TVE200` is enabled.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Kconfig selecting the required DRM helper libraries. The build list reflects the split between hardware display programming and probe/lifecycle logic.

Risks and test signals: Build tests should catch missing object additions if new TVE200 source files are introduced, and module naming must match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tve200/Makefile -->
