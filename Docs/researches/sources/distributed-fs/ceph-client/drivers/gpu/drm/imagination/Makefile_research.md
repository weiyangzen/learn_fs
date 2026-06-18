# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Makefile

Purpose: lists object composition for the PowerVR DRM module and its KUnit test object.

Important build rules: `powervr-y` includes CCB/CCCB, context, device, device info, driver, dump, free-list, firmware, firmware-processor, firmware trace/util, GEM, HWRT, job, MMU, power, queue, stream, sync, and VM objects. `powervr-$(CONFIG_DEBUG_FS)` adds `pvr_debugfs.o`. `obj-$(CONFIG_DRM_POWERVR)` builds `powervr.o`; `obj-$(CONFIG_DRM_POWERVR_KUNIT_TEST)` builds `pvr_test.o`.

Control flow and state: no runtime state; object order defines link membership for the kernel module.

Dependencies and integration: aligns with Kconfig symbols and the driver’s internal module layout. The files researched here are a subset of this larger module.

Risks: missing object entries cause unresolved symbols or dead features; adding debugfs-only code must remain conditional on `CONFIG_DEBUG_FS`.

Test signals: kernel build/link success for built-in and module configurations, plus debugfs and KUnit variants.
