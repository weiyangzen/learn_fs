# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.h

Purpose: this header defines the DPU core performance data structures and function prototypes shared between CRTC, KMS initialization, and debugfs/performance code.

Important types: `struct dpu_core_perf_params` stores per-CRTC requested performance: maximum per-pipe instantaneous bandwidth, arbitrated bandwidth, and core clock rate. `struct dpu_core_perf_tune` stores the debug performance mode. `struct dpu_core_perf` holds the SoC-specific `dpu_perf_cfg`, current and maximum core clock, tuning state, bandwidth-release control, and fixed-mode clock/IB/AB overrides.

Important APIs: `dpu_core_perf_adjusted_mode_clk()` applies catalog clock scaling and is used by both performance checking and mode validation. `dpu_core_perf_crtc_check()` validates a proposed CRTC state. `dpu_core_perf_crtc_update()` applies bandwidth/clock changes. `dpu_core_perf_crtc_release_bw()` drops bandwidth when frame work drains. `dpu_core_perf_init()` binds catalog config and maximum clock during KMS setup. `dpu_core_perf_debugfs_init()` exposes tuning/debug entries when debugfs is enabled.

Dependencies and integration: includes Linux types, dcache, mutex, DRM CRTC definitions, and `dpu_hw_catalog.h`. `dpu_crtc.h` embeds `dpu_core_perf_params` in both live and atomic CRTC state. Catalog headers provide `dpu_perf_cfg` values used through this interface.

State and persistence: the structures persist inside `struct dpu_kms` and `struct dpu_crtc` for the lifetime of the device/CRTC. Atomic state copies carry proposed values across check/commit.

Risks: the header exposes debug writable fields indirectly through debugfs, so production behavior can be altered at runtime on debug builds. Type widths mix `u32` KBps votes with `u64` clocks/bandwidth; overflow and unit mismatches are key review points.

Test signals: compile coverage for all users, debugfs creation, KMS init using every catalog perf block, CRTC check/update/release call paths, and mode validation using adjusted clock rates.
