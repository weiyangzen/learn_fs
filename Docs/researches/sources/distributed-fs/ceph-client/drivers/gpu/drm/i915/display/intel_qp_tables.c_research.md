<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c

## Purpose
`intel_qp_tables.c` provides static Display Stream Compression rate-control quantization parameter lookup tables for i915. The tables map bits-per-component, buffer range index, target bits-per-pixel index, and 4:4:4 versus 4:2:0 format to DSC range min/max QP values.

## Important APIs, Types, And Functions
The only exported functions are `intel_lookup_range_min_qp()` and `intel_lookup_range_max_qp()`. They use `PARAM_TABLE()` to select one of twelve static `u8` tables: min/max QP for 4:4:4 at 8/10/12 bpc and min/max QP for 4:2:0 at 8/10/12 bpc. Table dimensions are based on `DSC_NUM_BUF_RANGES` and per-format BPP-count constants.

## Control Flow
Callers pass `bpc`, `buf_i`, `bpp_i`, and `is_420`. The lookup macro checks the requested bpc, chooses the 4:2:0 or 4:4:4 table, and returns `table[buf_i][bpp_i]`. Unknown bpc values hit `MISSING_CASE(bpc)` and return 0.

## State And Persistence Behavior
All table data is compile-time constant and read-only. There is no dynamic state, locking, allocation, or persistence beyond the binary image.

## Dependencies And Integration Points
The file includes DRM DSC definitions for `DSC_NUM_BUF_RANGES`, i915 display utility macros for `MISSING_CASE`, and its own header. It is used by DSC parameter calculation code that needs C-model-aligned QP range values for PPS/rate-control programming.

## Risks
The functions do not bounds-check `buf_i` or `bpp_i`; callers must ensure indices match the selected table width and `DSC_NUM_BUF_RANGES`. Incorrect table values or index calculation errors can degrade DSC visual quality or violate sink expectations. Unsupported bpc silently returns 0 after `MISSING_CASE`, which is safe for build coverage but likely wrong for a real mode.

## Test Signals
Useful signals include DSC conformance tests, PPS programming inspection, mode validation across 8/10/12 bpc and RGB/YCbCr420 formats, fuzz or KUnit-style index-bound tests around caller calculations, and visual corruption checks on compressed links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.c -->
