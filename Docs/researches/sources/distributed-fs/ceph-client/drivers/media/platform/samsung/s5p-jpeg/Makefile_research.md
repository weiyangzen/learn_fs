# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Makefile

Purpose: Kbuild recipe for the Samsung JPEG codec driver.

Important declarations: `s5p-jpeg-objs := jpeg-core.o jpeg-hw-exynos3250.o jpeg-hw-exynos4.o jpeg-hw-s5p.o` links the common V4L2/mem2mem core with all supported hardware register backends. `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_JPEG) += s5p-jpeg.o` ties the aggregate object to Kconfig.

Control flow and integration: regardless of selected runtime variant, all helper backends are compiled into the driver object so OF/platform matching can choose behavior at probe time.

State and persistence: no runtime state.

Risks: new JPEG backend files or symbol renames must be reflected here. Because all backends are linked, compile errors in any variant break the whole driver.

Test signals: module and built-in builds with the Kconfig symbol enabled; disabled-symbol build should omit the aggregate object.
