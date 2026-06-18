<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs

Purpose: Implements Tyr's Rust platform and DRM driver glue for Mali Valhall CSF devices. It probes clocks/regulators/MMIO, performs early GPU reset and L2 power-on, reads GPU identity, creates a DRM device, and exposes a Panthor-compatible DRM driver name and ioctl.

Important APIs/types/functions: `TyrPlatformDriverData` owns a foreign-owned DRM device reference. `TyrDrmDeviceData` stores the platform device, clock/regulator mutexes, and `GpuInfo`. `issue_soft_reset()` writes `GPU_CMD_SOFT_RESET` and polls reset completion. The OF table matches `rockchip,rk3588-mali` and `arm,mali-valhall-csf`. `impl platform::Driver` performs probe. `impl drm::Driver` declares driver data/file/object types and the `PANTHOR_DEV_QUERY` ioctl.

Control flow: Probe gets and enables core/stacks/coregroup clocks, obtains enabled `mali` and `sram` regulators, maps 2 MiB MMIO, issues a soft reset, powers on L2, reads/logs GPU info, initializes DRM device data, creates the DRM device, and registers it. `PinnedDrop` for device data disables clocks.

State and persistence: State is in Rust-owned `ARef`s, pinned mutex-protected clock/regulator holders, devres MMIO, and immutable GPU info read at probe. No durable persistence exists.

Dependencies and integration points: Uses kernel Rust abstractions for platform devices, DRM, ioctls, clocks, regulators, devres IO memory, polling, `Arc`, and mutexes. User-space compatibility intentionally uses the `panthor` driver name and Panthor UAPI query.

Risks and test signals: The driver is incomplete and may leak semantic references to Panthor. Risks include probe unwind after partial clock enable, regulator requirements on boards without supplies, reset timeout, and lack of runtime PM/scheduler/MMU. Test signals are Rust build, probe on matching DT, successful `PANTHOR_DEV_QUERY`, reset/L2 poll success, and clock disable on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/driver.rs -->
