# sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Kconfig

Purpose: declares `VIDEO_DT3155` for the DataTranslation DT3155 frame grabber.

Important APIs/types/functions: tristate option depends on `PCI` and `VIDEO_DEV`, and selects `VIDEOBUF2_DMA_CONTIG`.

Control flow: enables building `dt3155.o` and ensures contiguous DMA videobuf2 support is present.

State and persistence: no runtime state.

Dependencies/integration: matches `dt3155.c` use of PCI, V4L2, and vb2 DMA-contig.

Risks and test signals: missing dependencies would surface as build failures. Test with `CONFIG_VIDEO_DT3155=m/y` in media build configurations.
