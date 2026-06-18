# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Makefile


Purpose: Builds the OMAP3 ISP driver as one composite media driver object.

Important APIs/types: Adds `-DDEBUG` to compiler flags when `CONFIG_VIDEO_OMAP3_DEBUG` is enabled. Defines `omap3-isp-objs` as the core `isp.o` and `ispvideo.o` plus CSIPHY, CCP2, CSI2, CCDC, preview, resizer, statistics, H3A AEWB/AF, and histogram objects. Links `omap3-isp.o` under `obj-$(CONFIG_VIDEO_OMAP3)`.

Control flow: The object list controls module link order and ensures all internal subdevice implementations are part of the same module.

State and persistence: Build metadata only.

Dependencies/integration: Mirrors the Kconfig symbol and the internal module graph used by `isp.c`, which initializes and registers each submodule.

Risks and test signals: Missing an object breaks symbols referenced by `isp.c` or media graph creation. Test with `CONFIG_VIDEO_OMAP3=m` and `=y`, debug enabled/disabled, and compile-test configurations where OMAP headers are available.
