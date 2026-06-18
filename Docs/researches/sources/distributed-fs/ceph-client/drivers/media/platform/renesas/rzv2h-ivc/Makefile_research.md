<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile

Purpose: defines the composite object layout for the RZ/V2H(P) IVC driver.

Important APIs/types/functions: no runtime APIs. `rzv2h-ivc-y` links `rzv2h-ivc-dev.o`, `rzv2h-ivc-subdev.o`, and `rzv2h-ivc-video.o` into one module. `obj-$(CONFIG_VIDEO_RZV2H_IVC) += rzv2h-ivc.o` includes it when configured.

Control flow and state: compile-time only. Cross-file functions declared in `rzv2h-ivc.h` resolve inside the composite module.

Dependencies and integration points: separates platform/runtime resource management (`*-dev.c`), subdevice/media graph (`*-subdev.c`), and video/vb2 transfer logic (`*-video.c`) while publishing one module for the platform device compatible.

Risks: adding new source files requires updating `rzv2h-ivc-y`. Removing or renaming helper functions in one object breaks the composite link.

Test signals: module build with `CONFIG_VIDEO_RZV2H_IVC=m`; inspect that all three objects are linked into `rzv2h-ivc.ko`; compile-test after any file split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile -->
