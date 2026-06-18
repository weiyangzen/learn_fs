<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h

## Purpose
Declares DCN32-specific SMU message helpers and small protocol constants not fully covered by common DCN30 headers.

## Important APIs, Types, And Functions
- `FCLK_PSTATE_NOTSUPPORTED` and `FCLK_PSTATE_SUPPORTED` encode the PMFW argument for FCLK switch allowance.
- `dcn32_smu_send_fclk_pstate_message`, `dcn32_smu_send_cab_for_uclk_message`, `dcn32_smu_transfer_wm_table_dram_2_smu`, `dcn32_smu_set_pme_workaround`, `dcn32_smu_set_hard_min_by_freq`, and `dcn32_smu_wait_for_dmub_ack_mclk` are the exported helpers.
- The header temporarily defines `DALSMC_MSG_SetCabForUclkPstate` and `DALSMC_Result_OK` for local availability.

## Control Flow
No executable flow. The prototypes define which DCN32-only mailbox operations are available to the clock manager.

## State And Persistence
No state is declared. Callers change PMFW state through the declared functions.

## Dependencies And Integration Points
Includes `core_types.h` and `dcn30/dcn30_clk_mgr_smu_msg.h` so DCN32 helpers can coexist with common SMU helpers.

## Risks And Edge Cases
Duplicate local definitions can drift from `dalsmc.h`; this is explicitly marked as temporary. Consumers need to pass PPCLK IDs and MHz frequencies consistent with the PMFW hard-min contract.

## Test Signals
Build coverage, successful hard-min programming, FCLK pstate messaging, CAB messaging, and watermark transfer validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.h -->
