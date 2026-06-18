# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Kconfig

Purpose: defines the build option for the Allwinner DE2 rotation V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_SUN8I_ROTATE` is a tristate depending on V4L mem2mem drivers, video, sunxi or compile-test, common clock, reset, OF, and PM. It selects videobuf2 DMA-contig and `V4L2_MEM2MEM_DEV`.

Control flow: selecting the symbol builds the composite `sun8i-rotate` module from core and format-table objects.

State and persistence: build configuration only.

Dependencies and integration points: exposes a standalone rotation/copy engine through V4L2 M2M.

Risks: runtime support depends on clocks, reset, IRQ, and compatible `allwinner,sun8i-a83t-de2-rotate`.

Test signals: Kconfig visibility, module build, and video-node registration on matching hardware.
