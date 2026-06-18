# sources/distributed-fs/ceph-client/drivers/rapidio/devices/Makefile

Purpose: builds RapidIO device-level drivers, specifically the Tsi721 master-port driver and the generic mport character device.

Important entries: `obj-$(CONFIG_RAPIDIO_TSI721) += tsi721_mport.o` creates the Tsi721 module. `tsi721_mport-y := tsi721.o` always includes the PCI/mport driver body. `tsi721_mport-$(CONFIG_RAPIDIO_DMA_ENGINE) += tsi721_dma.o` conditionally links DMAengine support into the same module. `obj-$(CONFIG_RAPIDIO_MPORT_CDEV) += rio_mport_cdev.o` builds the user-space mport character device.

Control flow and integration: this file ties the Kconfig topology to concrete build artifacts. It keeps the Tsi721 DMA code in the Tsi721 module rather than as a separate object, which lets `tsi721.c` call `tsi721_register_dma()`, `tsi721_unregister_dma()`, and `tsi721_dma_stop_all()` when DMA support is compiled in.

State and persistence: no runtime state; output object composition depends on `.config`.

Dependencies: Linux kbuild, `RAPIDIO_TSI721`, `RAPIDIO_DMA_ENGINE`, and `RAPIDIO_MPORT_CDEV`.

Risks: conditional linking means code paths guarded by `CONFIG_RAPIDIO_DMA_ENGINE` must remain synchronized with stubs in `tsi721.h`; otherwise non-DMA builds can break. The cdev builds independently of Tsi721 and can attach to any registered RapidIO mport.

Test signals: build with all four combinations of Tsi721 and DMA enabled/disabled; run `nm` or module link checks to ensure DMA symbols are present only in DMA builds.
