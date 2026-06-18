# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.c

## Purpose
`i915_edram.c` detects platform eDRAM and records its size in `drm_i915_private`. That value drives feature predicates such as `HAS_EDRAM()` and write-through cache behavior.

## Important APIs, Types, and Functions
The public function is `i915_edram_detect()`. The helper `gen9_edram_size_mb()` decodes `HSW_EDRAM_CAP` bank, way, and set fields into megabytes using fixed tables.

## Control Flow
Detection returns early for platforms before Haswell/Broadwell/gen9+. It reads `HSW_EDRAM_CAP` with forcewake-safe uncore access, ignores disabled eDRAM, assigns a fixed 128 MB size for pre-gen9 capability formats, or calculates gen9+ size from register fields. It then logs the detected amount.

## State and Persistence Behavior
The only persistent state is `i915->edram_size_mb`, set during hardware probe and used as a device capability for the rest of the driver lifetime. The code does not program eDRAM registers; it only reads capability state.

## Dependencies and Integration Points
It depends on platform macros, uncore register reads, `HSW_EDRAM_CAP` bitfield macros, and DRM logging. `i915_driver_hw_probe()` calls it before DMA/GGTT setup. `i915_drv.h` exposes `HAS_EDRAM()` and `HAS_WT()` based on the stored size.

## Risks
Register format differences are handled coarsely: pre-gen9 always reports 128 MB when enabled. Reading too early without uncore access would fail, so probe ordering matters. Incorrect decode tables would affect cache policy and reported capabilities.

## Test Signals
Boot Haswell/Broadwell/gen9 eDRAM systems and confirm the `Found ...MB of eDRAM` log, `HAS_EDRAM()` behavior, WT cache paths, and no eDRAM report on unsupported or disabled platforms.
