<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h

## Purpose
Declares the DCN314 clock-manager object shape and public lifecycle/update entry points used by the display core and ASIC construction code.

## Important APIs, Types, And Functions
- `struct clk_mgr_dcn314` embeds `struct clk_mgr_internal` and owns the DCN314 SMU watermark allocation descriptor.
- `struct dcn314_smu_watermark_set` pairs a CPU pointer to `struct dcn314_watermarks` with the GPU memory controller address passed to PMFW.
- `struct dcn314_ss_info_table` stores spread-spectrum percentages by clock source for local LUT-based DP reference adjustment.
- Public declarations expose clock-state comparison, SPLL SSC detection, clock initialization/update, construction, and destruction.

## Control Flow
The header itself has no executable control flow. Its declarations define the handoff between the DCN ASIC factory, the generic `clk_mgr` function table, and the DCN314 implementation file.

## State And Persistence
The persistent state introduced here is the `smu_wm_set` member. It persists from construction until destroy and determines whether watermark transfers use a GPU allocation or a dummy fallback.

## Dependencies And Integration Points
It depends on `clk_mgr_internal.h` for base clock-manager types, `union large_integer`, `struct dc_clocks`, `struct dc_state`, `struct dc_context`, `struct pp_smu_funcs`, and `struct dccg`. It is consumed by DCN314 construction and SMU code.

## Risks And Edge Cases
The forward declaration of `struct dcn314_watermarks` keeps the ABI opaque, so the `.c` file and SMU header must remain consistent about allocation size and table layout. Any mismatch between `DCN314_NUM_CLOCK_SOURCES` and the LUT in the `.c` file would affect spread-spectrum source indexing.

## Test Signals
Build coverage should catch type drift. Runtime coverage is visible through successful DCN314 construction, non-null watermark table allocation, clean destroy, and correct dispatch through `clk_mgr->funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_clk_mgr.h -->
