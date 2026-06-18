<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c

## Purpose
This file detects memory subsystem characteristics needed by display code: DRAM type, FSB and memory frequency on older platforms, channel count, QGV/PSF points, symmetry, 16Gb DIMM presence, and newer GDDR/ECC display-bandwidth effects. The results are cached in `display->dram.info`.

## Important APIs, Types, and Functions
Public functions include `intel_dram_type_str()`, `intel_mem_freq()`, `intel_fsb_freq()`, `intel_dram_detect()`, and `intel_dram_info()`. Internal helpers are grouped by generation: Pineview/i9xx/ILK frequency readers, SKL/ICL DIMM size/width/rank decoders, BXT DUNIT decoders, `icl_pcode_read_mem_global_info()`, `gen11_get_dram_info()`, `gen12_get_dram_info()`, and `xelpdp_get_dram_info()`.

Internal `struct dram_dimm_info` and `struct dram_channel_info` normalize DIMM dimensions before filling public `struct dram_info`. `intel_dram_type_str()` maps the enum values to readable debug strings and guards array size with `BUILD_BUG_ON`.

## Control Flow
`intel_dram_detect()` exits early for DG2 and no-display devices, allocates managed `dram_info`, then dispatches by display version and platform: Xe_LPD+ via `MTL_MEM_SS_INFO_GLOBAL`, Gen12 via pcode global memory info, Gen11 via SKL channel parsing plus pcode, BXT/GLK via DUNIT registers, Gen9 via SKL MCHBAR registers, and older platforms via strap/register frequency reads. Detection failures are logged but intentionally not probe-fatal.

## State and Persistence Behavior
The detected `dram_info` is device-managed memory with probe lifetime. It is a snapshot of platform memory topology and firmware-reported capabilities, not a dynamic telemetry stream. Older FSB/memory frequencies are strap-derived and may not reflect all BIOS-configured behavior. On Xe3p_LPD and later `ecc_impacting_de_bw` records whether ECC affects display engine bandwidth.

## Dependencies and Integration Points
The file depends on uncore MMIO, MCHBAR register definitions, pcode reads through `intel_parent_pcode_read()`, Valleyview IOSF sideband access, DRM managed allocation, and display platform/version helpers. Watermark, bandwidth, and display power-management code consumes `intel_dram_info()` to size memory-related limits.

## Risks
Register decoding is heavily platform-specific. Wrong display-version dispatch or field masks can misreport channel count or memory type, leading to incorrect watermark or bandwidth policy. SKL/ICL DIMM encoding differs by size units, and BXT values are per-device Gb rather than total DIMM Gb. Detection is non-fatal, so consumers must tolerate unknown or partially populated data. `intel_dram_info()` can return NULL on platforms that do not allocate DRAM info.

## Test Signals
Signals include boot logs showing expected DRAM type/channel counts on each generation, valid QGV/PSF counts from pcode, no MISSING_CASE warnings on supported hardware, watermark/bandwidth tests across memory configurations, suspend/resume without stale DRAM assumptions, and explicit coverage for NULL `intel_dram_info()` on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c -->
