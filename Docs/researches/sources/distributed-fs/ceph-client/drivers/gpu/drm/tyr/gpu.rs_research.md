<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs

Purpose: Reads and exposes Mali GPU identity/features for Tyr, logs a human-readable model summary, decodes GPU IDs, and powers on the L2 block.

Important APIs/types/functions: `GpuInfo` transparently wraps `uapi::drm_panthor_gpu_info` and implements `AsBytes` for copyout. `GpuInfo::new()` reads identity, feature, thread, coherency, present-mask, and address-space registers. `GpuInfo::log()` prints model/features/presence masks. `va_bits()` and `pa_bits()` decode MMU feature widths. `GpuId::from(u32)` extracts architecture/product/version fields. `l2_power_on()` writes `L2_PWRON_LO` and polls `L2_READY_LO`.

Control flow: Probe calls `l2_power_on()` after reset and then `GpuInfo::new()`. GPU info is copied to userspace by `file.rs`. Logging maps known arch/product to `g610`, otherwise `unknown`.

State and persistence: GPU info is a snapshot captured at probe and stored in the DRM device data. No ongoing state is updated here.

Dependencies and integration points: Uses register constants from `regs.rs`, Rust devres IO access, polling, Panthor UAPI layout, and bitfield helpers.

Risks and test signals: Risks include stale or incomplete texture feature reporting, only one known model, assuming low/high present registers, and L2 poll timeout. Test signals include register-read fault propagation, correct UAPI byte layout, known GPU ID decoding, and behavior on unknown model IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/gpu.rs -->
