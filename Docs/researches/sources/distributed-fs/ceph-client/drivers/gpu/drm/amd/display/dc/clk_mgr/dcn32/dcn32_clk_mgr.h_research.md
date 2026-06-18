<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h

## Purpose
Declares the DCN32 clock-manager lifecycle and the DPP DTO update helper shared with related code.

## Important APIs, Types, And Functions
- `dcn32_init_clocks` initializes SMU/DPM-derived clock tables and current clock state.
- `dcn32_clk_mgr_construct` and `dcn32_clk_mgr_destroy` allocate and release the DCN32 clock-manager backing state.
- `dcn32_update_clocks_update_dpp_dto` is exported so other DCN variants can reuse the per-DPP DTO update behavior.

## Control Flow
No executable flow is present. The prototypes define the integration boundary between ASIC construction, generic clock-manager function tables, and helper reuse.

## State And Persistence
State is owned by `struct clk_mgr_internal` in the implementation; this header does not declare a DCN32-specific wrapper.

## Dependencies And Integration Points
The prototypes reference `struct clk_mgr`, `struct clk_mgr_internal`, `struct dc_context`, `struct pp_smu_funcs`, `struct dccg`, and `struct dc_state` from broader display headers included by callers.

## Risks And Edge Cases
Because this header does not include the type definitions itself, include order matters for translation units using it. Exporting the DTO helper means callers must obey the same safe-to-lower semantics as DCN32.

## Test Signals
Build coverage and successful construction/init/update/destroy dispatch through the generic clock manager validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.h -->
