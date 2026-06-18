<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c

## Purpose
Implements DCN32-specific DALSMC mailbox helpers on top of DAL message, argument, and response registers.

## Important APIs, Types, And Functions
- `dcn32_smu_send_msg_with_param` sends ordinary DALSMC transactions and optionally returns the output argument.
- Delay-aware variants aggregate polling time for hard-min status diagnostics.
- `dcn32_smu_set_hard_min_by_freq` issues hard-min clock requests and, on supporting PMFW versions, polls `ReturnHardMinStatus`.
- Other public helpers send FCLK pstate support, CAB num-ways for UCLK pstate, watermark table transfer, PME workaround, and DMCUB MCLK ack wait policy.

## Control Flow
Transactions wait for a nonzero response, clear it, write the argument, write the message ID, trace the message, then wait for `DALSMC_Result_OK`. Hard-min status support is gated by ASIC revision and SMU version. When supported, the helper repeatedly queries hard-min status until the requested clock bit appears or a two-second total delay budget expires.

## State And Persistence
The file has no heap state. It mutates PMFW policy and uses static counters to track maximum hard-min wait time and timeout count for diagnostics. PMFW keeps the effective hard-min, FCLK switch, CAB, and DMCUB wait states.

## Dependencies And Integration Points
Uses DALSMC constants, DCN32 SMU13 table IDs, register helpers, SMU trace macros, and `clk_mgr_internal` context. It is called by `dcn32_clk_mgr.c` alongside common DCN30 SMU helpers.

## Risks And Edge Cases
The base send helper ignores the initial wait result and proceeds to clear/send, so a wedged response register can still lead to a failed transaction after the second wait. Hard-min status polling only works on specific PMFW versions. The DMCUB wait helper uses literal message ID `0x14`, matching `SetAlwaysWaitDmcubResp`; future constant changes would be easy to miss.

## Test Signals
Trace logs for SMU messages and delays, hard-min status success and timeout paths, FCLK pstate toggles, CAB changes, watermark transfer, PME workaround, and DMCUB MCLK ack toggles provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr_smu_msg.c -->
