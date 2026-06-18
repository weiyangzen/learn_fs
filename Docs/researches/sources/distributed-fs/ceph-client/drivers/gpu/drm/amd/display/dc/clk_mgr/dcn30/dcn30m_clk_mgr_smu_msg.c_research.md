<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c

## Purpose

`dcn30m_clk_mgr_smu_msg.c` implements the mobile DCN30 SMU mailbox command used for SmartMux switching.

## Important APIs, Types, And Functions

The exported function is `dcn30m_smu_set_smart_mux_switch()`. Internal helpers mirror the DCN30 DALSMC transport: `dcn30m_smu_wait_for_response()` and `dcn30m_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for a response, clears response, writes argument and message ID, waits for completion, reports timeout through `dm_helpers_smu_timeout()`, and returns true only on `DALSMC_Result_OK`. The SmartMux wrapper sends `DALSMC_MSG_SmartAccess` with `pins_to_set` and returns the response argument.

## State And Persistence Behavior

Only mailbox registers are transiently modified. SmartMux routing state persists in PMFW/platform hardware. No local memory is allocated.

## Dependencies And Integration Points

It depends on `dalsmc.h`, DAL mailbox register offsets, `reg_helper`, DC logging, and timeout helpers. It is called by `dcn30m_clk_mgr.c`.

## Risks

The transport duplicates much of `dcn30_clk_mgr_smu_msg.c` but without message tracing and with the same unhandled busy-reject note. Unsupported firmware commands return false internally, but the wrapper returns a zero response without richer error detail.

## Test Signals

SmartAccess command response checks, timeout path testing, busy/rejected command behavior, and platform validation that the requested mux pins actually change routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c -->
