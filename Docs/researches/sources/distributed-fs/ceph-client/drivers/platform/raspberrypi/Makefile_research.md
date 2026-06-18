# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Makefile

Purpose: kbuild rules for the Raspberry Pi VideoCore/VCHIQ driver group.

Important APIs, types, and functions: `obj-$(CONFIG_BCM2835_VCHIQ) += vchiq.o` builds a composite object from `vchiq_core.o`, `vchiq_arm.o`, `vchiq_bus.o`, and `vchiq_debugfs.o`; `vchiq_dev.o` is conditionally added when `CONFIG_VCHIQ_CDEV` is set. `obj-$(CONFIG_BCM2835_VCHIQ_MMAL) += vchiq-mmal/` descends into the MMAL service directory.

Control flow: kbuild links the composite VCHIQ module/built-in and optional child directory based on Kconfig.

State and persistence: no runtime state; build outputs track `.config`.

Dependencies and integration points: ties VCHIQ core, platform glue, bus registration, debugfs, optional miscdevice ABI, and MMAL service into one build product.

Risks: the composite object always includes debugfs stubs even when `CONFIG_DEBUG_FS` is disabled, which is intentional. If `CONFIG_VCHIQ_CDEV=n`, ioctl code is absent; callers must use kernel bus clients only. MMAL depends on VCHIQ symbols exported from the composite.

Test signals: build all combinations of `BCM2835_VCHIQ`, `VCHIQ_CDEV`, and `BCM2835_VCHIQ_MMAL`; inspect final object contents and module dependencies.
