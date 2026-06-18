# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm.c

### Purpose
`intel_wm.c` is the generic dispatch and debugfs layer for display FIFO watermark management. It delegates platform-specific watermark computation/programming to `display->funcs.wm`, initializes the correct implementation family, defines common visibility policy, formats latency values, and exposes latency override files in debugfs.

### Important APIs, Types, And Functions
Public wrappers include `intel_update_watermarks()`, `intel_wm_compute()`, `intel_initial_watermarks()`, `intel_atomic_update_watermarks()`, `intel_optimize_watermarks()`, `intel_compute_global_watermarks()`, `intel_wm_get_hw_state()`, `intel_wm_sanitize()`, `intel_wm_plane_visible()`, `intel_print_wm_latency()`, `intel_wm_init()`, and `intel_wm_debugfs_register()`. Debugfs helpers show/write primary, sprite, and cursor latency arrays.

### Control Flow
Most functions check whether a function pointer exists and call it, returning success or false when unsupported. Initialization selects `skl_wm_init()` for display version 9+ and `i9xx_wm_init()` otherwise. `intel_wm_plane_visible()` treats inactive CRTCs as invisible and cursor planes with a framebuffer as visible regardless of `uapi.visible`. Debugfs open methods reject unsupported platform families; reads format units by generation, and writes parse exactly `num_levels` 16-bit latency values under the global modeset lock.

### State, Persistence, And Dependencies
Watermark state is stored in `display->wm`, platform watermark state, and hardware registers owned by implementation backends. Debugfs writes mutate latency arrays in memory and influence later computations. Dependencies include debugfs, DRM logging, i9xx and SKL watermark backends, display core/types, and modeset locking.

### Integration Points
Atomic check/commit paths use compute/update/optimize wrappers. Modeset setup reads/sanitizes hardware state. Display debugfs registration calls `intel_wm_debugfs_register()`, which also delegates to `skl_watermark_debugfs_register()`. VRR optimized guardband uses watermark max-latency data from the SKL backend.

### Risks
Function-pointer dispatch means missing backend hooks silently become no-ops, which is intentional but can hide incomplete platform enablement. Cursor visibility is conservative because frequent cursor updates can outrun watermark logic. Debugfs latency writes can destabilize watermark calculations and are protected only by modeset locking and input count validation.

### Test Signals
Signals include atomic watermark compute/update success on old and Gen9+ platforms, debugfs latency read/write with correct unit formatting, cursor plane update stress, modeset sanitize after firmware state, and underrun-free display operation after latency overrides.
