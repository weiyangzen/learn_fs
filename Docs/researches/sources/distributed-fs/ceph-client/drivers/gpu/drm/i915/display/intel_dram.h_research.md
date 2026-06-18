<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h

## Purpose
This header exposes the display driver's normalized DRAM information structure and DRAM detection/query helpers.

## Important APIs, Types, and Functions
`struct dram_info` contains `enum intel_dram_type`, `fsb_freq`, `mem_freq`, `num_channels`, `num_qgv_points`, `num_psf_gv_points`, `ecc_impacting_de_bw`, `symmetric_memory`, and `has_16gb_dimms`. Exported helpers are `intel_dram_detect()`, `intel_fsb_freq()`, `intel_mem_freq()`, `intel_dram_info()`, and `intel_dram_type_str()`.

## Control Flow
There is no executable flow in the header. The shape of `struct dram_info` drives downstream branches in display bandwidth and watermark code after `intel_dram_detect()` populates `display->dram.info`.

## State and Persistence Behavior
The header defines persistent probe-time state rather than runtime counters. Comments clarify that `ecc_impacting_de_bw` is only valid from Xe3p_LPD onward, so consumers must gate usage by platform capability.

## Dependencies and Integration Points
It forward declares `struct intel_display` and uses Linux fixed-width types. It integrates with `intel_dram.c`, display bandwidth code, and debug logging.

## Risks
Consumers can overinterpret fields on unsupported platforms. `intel_dram_info()` may be NULL, and some fields are only populated for selected generations. Adding enum values requires updating `intel_dram_type_str()`.

## Test Signals
Compile checks for all users, enum/string array size assertions, NULL-safe consumers, and platform-specific tests that verify the valid subset of fields per generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h -->
