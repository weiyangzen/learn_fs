<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile

Purpose: Defines cx18 module object composition and include paths.

Important APIs/types: `cx18-objs` links the main driver, board tables, I2C, firmware, GPIO, queues, streams, fileops, ioctl, controls, mailbox, VBI, audio/video, IRQ, AV core/audio/firmware/VBI, SCB, DVB, and IO objects. `cx18-alsa-objs` links ALSA main and PCM objects. `obj-$(CONFIG_VIDEO_CX18)` and `obj-$(CONFIG_VIDEO_CX18_ALSA)` bind modules to Kconfig. Include paths expose DVB frontend and tuner headers.

Control flow: Build-system only.

State/persistence: No state.

Dependencies/integration: Separates core capture driver from optional ALSA module, matching runtime extension callback behavior.

Risks: Missing object entries break symbol resolution or leave driver features unavailable. Include-path reliance can hide header movement issues.

Test signals: Module link success for both configs, modpost checks, and successful load of `cx18` and `cx18-alsa`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/Makefile -->
