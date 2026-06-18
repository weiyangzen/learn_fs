<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h

## Purpose
Defines the DALSMC message IDs, response codes, hard-min status bits, and FCLK switch enum used by DCN32 display-to-SMU mailbox calls.

## Important APIs, Types, And Functions
- `DALSMC_Result_*` constants define PMFW response values.
- `DALSMC_MSG_*` constants enumerate the DAL message contract, including SMU version queries, DRAM table address/transfer, hard min/max clock requests, DPM frequency queries, display count, FCLK switch allowance, CAB for UCLK pstate, DMCUB wait policy, and hard-min status.
- `CHECK_HARD_MIN_CLK_*` bit masks describe which clocks PMFW reports as having fulfilled DAL hard-min arbitration.
- `FclkSwitchAllow_e` names allow/disallow states.

## Control Flow
This header has no executable control flow. It is consumed by mailbox helpers that write these IDs to DAL message registers and interpret response/status bits.

## State And Persistence
The constants map to PMFW state transitions; no C state is allocated. Hard-min status bits reflect PMFW's persisted arbiter state after clock requests.

## Dependencies And Integration Points
Used by `dcn32_clk_mgr_smu_msg.c` and shared conceptually with DCN30 SMU message helpers. It defines the PMFW protocol surface for DCN32 clock management.

## Risks And Edge Cases
Message ID drift between driver and PMFW would send the wrong command. Hard-min status polling depends on version gating in the caller because older PMFW may not support `ReturnHardMinStatus`.

## Test Signals
Successful version negotiation, table transfer, DPM queries, hard-min requests, FCLK switch allow/disallow, CAB messages, and hard-min status polling validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dalsmc.h -->
