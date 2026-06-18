# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Kconfig

Purpose: defines the build option for the Allwinner Cedrus VPU stateless decoder.

Important APIs/types: `config VIDEO_SUNXI_CEDRUS` is a tristate prompt depending on `VIDEO_DEV`, `RESET_CONTROLLER`, `HAS_DMA`, and `OF`; it selects `MEDIA_CONTROLLER`, `SUNXI_SRAM`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_MEM2MEM_DEV`.

Control flow: Kconfig-only; when built as a module, the module is named `sunxi-cedrus`.

State and persistence: build configuration only.

Dependencies/integration: declares mandatory framework dependencies used by the driver: V4L2/video device core, media controller, reset, DMA-contiguous vb2, memory-to-memory helpers, OF matching, and SRAM claiming.

Risks: missing `MEDIA_REQUEST_API` is not explicit here even though the driver requires requests on its output queue through vb2; this may be selected elsewhere by media controller/V4L2 configuration in this kernel version.

Test signals: randconfig and COMPILE_TEST builds should confirm all selected frameworks satisfy compile/link dependencies.
