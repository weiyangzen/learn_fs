# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.c

Purpose: creates and unregisters the single DRM accel facade device used by all Rocket NPU cores.

Important APIs and types: exports `rocket_device_init` and `rocket_device_fini`.

Control flow: init allocates a managed DRM device embedding `struct rocket_device`, stores it as drvdata on the facade platform device, counts available `rockchip,rk3588-rknn-core` DT nodes, allocates the core array, configures 40-bit DMA and max segment size, initializes `sched_lock`, and registers the DRM device. Fini warns if cores remain and unregisters DRM.

State and persistence: persistent state is the `rocket_device` with DRM device, scheduler lock, core array, and core count. It lasts from first core probe until last core removal.

Dependencies and integration: called from `rocket_drv.c` when the first core probes; uses OF node scanning, DRM managed allocation, DMA API, and platform device drvdata.

Risks and test signals: test zero available cores, partial core probe failure, DRM registration failure, core hot-unplug ordering, and consistency between counted DT nodes and actual probes.
