# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Kconfig

Purpose: declares build-time configuration symbols for the SAA7146 common PCI/media support.

Important APIs/types: `VIDEO_SAA7146` is a hidden tristate depending on `I2C && PCI`. `VIDEO_SAA7146_VV` is a hidden tristate depending on `VIDEO_DEV`, selecting `VIDEOBUF2_DMA_SG` and the base `VIDEO_SAA7146` module.

Control flow: Kconfig dependency resolution determines whether base PCI/I2C support and optional V4L2 video/VBI support are built.

State/persistence: no runtime state; affects kernel configuration and module composition.

Dependencies/integration: selected by board drivers using SAA7146 hardware. The split lets DVB-only or non-video users depend on the base module while video/VBI users pull in VB2 DMA scatter-gather support.

Risks/test signals: incorrect dependencies cause link failures or missing symbols (`vb2_dma_sg_memops`, V4L2 ops, I2C/PCI APIs). Config tests should build base-only and video-enabled combinations.
