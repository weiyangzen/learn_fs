<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile

Purpose: Defines the object composition for the Cobalt driver module.

Important APIs/types: `cobalt-objs` links driver initialization, IRQ, V4L2, I2C, Omnitek DMA, flash, CPLD, and ALSA PCM implementation objects. `obj-$(CONFIG_VIDEO_COBALT) += cobalt.o` binds the aggregate module to Kconfig.

Control flow: Build system flow only; no runtime behavior.

State/persistence: No state. The object list controls which subsystems are linked into the single module.

Dependencies/integration: The file is the integration point between Kconfig and the C sources. It ensures ALSA support is built into the Cobalt module rather than as a separate module.

Risks: Missing any object from `cobalt-objs` would produce unresolved symbols or silently omit device functionality. Adding optional support here requires matching Kconfig dependencies.

Test signals: Module link success, modpost symbol checks, and load-time availability of V4L2, ALSA, MTD, I2C, DMA, and IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/Makefile -->
