<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile

Purpose: maps the RZ/G2L CRU and CSI-2 Kconfig symbols to build objects.

Important APIs/types/functions: no runtime APIs. `obj-$(CONFIG_VIDEO_RZG2L_CSI2) += rzg2l-csi2.o` builds the standalone CSI-2 receiver. `rzg2l-cru-objs = rzg2l-core.o rzg2l-ip.o rzg2l-video.o` links the CRU composite module from core/media-graph, IP subdev, and video/DMA pieces. `obj-$(CONFIG_VIDEO_RZG2L_CRU) += rzg2l-cru.o` includes that composite.

Control flow and state: compile-time only; no runtime state or persistence.

Dependencies and integration points: relies on Kbuild composite object naming, so exported internal functions declared in `rzg2l-cru.h` are resolved inside `rzg2l-cru.o`. CSI-2 remains a separate module because it represents a separate platform device and OF compatible.

Risks: adding CRU files requires updating `rzg2l-cru-objs`; adding CSI-2 support files would require changing its object definition. Build failures can occur if function declarations in `rzg2l-cru.h` drift from composite member definitions.

Test signals: build `M=drivers/media/platform/renesas/rzg2l-cru` with both config symbols as modules and check that `rzg2l-cru.ko` contains `rzg2l-core.o`, `rzg2l-ip.o`, and `rzg2l-video.o` while `rzg2l-csi2.ko` is separate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile -->
