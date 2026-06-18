# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.c

Purpose: main Rocket DRM accel/platform driver. It registers a facade DRM platform device, probes individual RK3588 NPU core devices, manages per-file IOMMU domains and sched entities, exposes ioctls, and implements runtime PM for clocks.

Important APIs and types: module entry points are `rocket_register` and `rocket_unregister`; file callbacks are `rocket_open` and `rocket_postclose`; platform callbacks are `rocket_probe` and `rocket_remove`; PM callbacks are `rocket_device_runtime_resume/suspend`. It also implements `rocket_iommu_domain_get/put`.

Control flow: module init creates a simple `rknn` platform device and registers the real OF platform driver. First core probe creates the DRM facade; each core gets an index and runs `rocket_core_init`. Open creates a per-file IOMMU paging domain, initializes an aperture-wide `drm_mm`, and opens a sched entity over all cores. Close destroys scheduler, DRM MM, domain, and module ref. Runtime resume enables core clocks; suspend refuses if the scheduler reports non-idle.

State and persistence: global `drm_dev` and `rdev` represent the facade. Per-file state is `rocket_file_priv`: device pointer, IOMMU domain, virtual address allocator, mutex, and scheduler entity.

Dependencies and integration: uses DRM accel/GEM/ioctl helpers, IOMMU, OF platform matching, PM runtime, `rocket_device`, `rocket_core`, `rocket_gem`, and `rocket_job`.

Risks and test signals: test multi-core probe/remove, module ref balance, open before first core, IOMMU domain allocation failure, PM suspend with in-flight jobs, and ioctl dispatch for all UAPI commands.
