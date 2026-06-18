<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h

## Purpose
Declares the DCN315 clock-manager wrapper type and constructor/destructor entry points.

## Important APIs, Types, And Functions
- `struct clk_mgr_dcn315` embeds the generic internal clock manager and a DCN315 SMU watermark set.
- `struct dcn315_smu_watermark_set` stores the CPU pointer and GPU address for PMFW watermark upload.
- `dcn315_clk_mgr_construct` and `dcn315_clk_mgr_destroy` are the externally visible lifecycle functions.

## Control Flow
There is no executable control flow. The header defines the type boundary consumed by ASIC initialization and implemented in `dcn315_clk_mgr.c`.

## State And Persistence
The watermark allocation descriptor persists for the clock manager lifetime. All other clock state lives in the embedded `clk_mgr_internal`.

## Dependencies And Integration Points
Depends on `clk_mgr_internal.h` for generic clock manager infrastructure and GPU address types. The opaque `struct dcn315_watermarks` comes from the SMU ABI header at implementation time.

## Risks And Edge Cases
Because the watermark type is opaque here, allocation and free code must use the matching DCN315 SMU header layout. Constructor/destructor callers must pass the concrete `struct clk_mgr_dcn315`, not just the embedded base.

## Test Signals
Build-time type checks, successful clock manager allocation, and clean destruction of the watermark GPU buffer validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_clk_mgr.h -->
