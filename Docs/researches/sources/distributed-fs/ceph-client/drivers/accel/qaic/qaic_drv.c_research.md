# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_drv.c

Purpose: main Qualcomm QAIC PCI/DRM accel driver. It creates the device model, registers DRM ioctls, manages users, probes PCI resources and MSI vectors, registers the MHI controller and MHI service drivers, handles reset/remove/power-management, and coordinates online/offline state.

Important APIs and types: module entry points are `qaic_init` and `qaic_exit`; major callbacks include `qaic_open`, `qaic_postclose`, `qaic_pci_probe/remove/shutdown`, PCI error reset hooks, PM suspend/resume, and `qaic_mhi_probe`. It defines `qaic_device_config`, `qaic_accel_driver`, the QAIC ioctl table, and PCI IDs for AIC080/AIC100/AIC200.

Control flow: PCI probe allocates `qaic_device`/`qaic_drm_device`, initializes locks/workqueues/DBCs/SSR, maps MHI and DBC BARs, sets DMA masks, configures per-DBC IRQs or single-MSI fallback, registers the DRM accel node, and registers an MHI controller. When `QAIC_CONTROL` appears, `qaic_mhi_probe` opens the control channel, negotiates protocol version, marks the device online, and emits a uevent. Removal/reset notifies users, wakes control and DBC waiters, cleans SSR and DBC state, frees MHI, and unregisters DRM.

State and persistence: central state is `qaic_device`: PCI BARs, MHI controller/channels, DBC array, workqueues, bootlog/RAS/SSR/timesync channels, SRCU locks, and `dev_state`. User state is per DRM fd with an IDA handle and SRCU-protected pointer to the DRM device.

Dependencies and integration: integrates DRM accel/GEM, PCI, MHI controller support, sysfs/debugfs, RAS, SSR, Sahara firmware loader, timesync, and datapath/control files. The global `datapath_polling` module parameter changes IRQ behavior.

Risks and test signals: cover probe unwind, protocol-version mismatch, single-MSI fallback, open/close while device goes offline, PCI reset during in-flight DMA, suspend refusal when datapath busy, module exit with link-up cleanup, and optional service registration failures.
