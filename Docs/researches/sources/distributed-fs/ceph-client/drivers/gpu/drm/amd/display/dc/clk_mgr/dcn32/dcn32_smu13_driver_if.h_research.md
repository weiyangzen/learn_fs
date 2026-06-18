<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h

## Purpose
Defines the SMU13 driver-interface subset needed by the DCN32 clock manager: PPCLK identifiers, external watermark table layout, and PMFW table IDs.

## Important APIs, Types, And Functions
- `PPCLK_e` enumerates clock domains used by DPM and hard-min messages, including DISPCLK, DPPCLK, DPREFCLK, DCFCLK, DTBCLK, UCLK, FCLK, SOC, GFX, and media clocks.
- `WatermarkRowGeneric_t`, `Watermarks_t`, and `WatermarksExternal_t` describe the PMFW watermark upload format.
- `WATERMARKS_FLAGS_e` names watermark row meanings.
- `TABLE_*` constants identify SMU table types; DCN32 uses `TABLE_WATERMARKS`.

## Control Flow
This is a pure ABI header. Control flow appears in callers that use `PPCLK_e` values in SMU messages or fill `WatermarksExternal_t`.

## State And Persistence
Watermark tables are persisted in GPU memory before transfer to PMFW. PPCLK IDs and table IDs become encoded message arguments but allocate no state.

## Dependencies And Integration Points
Used by `dcn32_clk_mgr.c` and `dcn32_clk_mgr_smu_msg.c` to query DPM levels, set hard-min clocks, and transfer watermark tables.

## Risks And Edge Cases
ABI layout and enum ordering must match PMFW. `WatermarksExternal_t` includes spare and MMHUB padding fields that must be preserved even though the driver fills only a small row subset.

## Test Signals
Correct DPM responses per PPCLK, successful watermark table transfer, and PMFW driver interface version checks are the primary validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_smu13_driver_if.h -->
