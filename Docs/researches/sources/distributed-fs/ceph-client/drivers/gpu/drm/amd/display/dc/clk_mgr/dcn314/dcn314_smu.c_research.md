<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c

## Purpose
Implements the DCN314 VBIOS/PMFW SMU mailbox adapter. It translates display clock-manager requests into MP1 C2P message transactions for clock hard-mins, display idle optimization, table transfers, zstate policy, DTBCLK control, and PMFW version queries.

## Important APIs, Types, And Functions
- `dcn314_smu_send_msg_with_param` is the central transaction helper: wait for response ready, clear response, write parameter, write message ID, wait for completion, handle known failures, and return the SMU output parameter.
- `dcn314_smu_wait_for_response` polls `MP1_SMN_C2PMSG_91` until the response is no longer busy.
- Public wrappers include `dcn314_smu_set_dispclk`, `dcn314_smu_set_dppclk`, `dcn314_smu_set_hard_min_dcfclk`, `dcn314_smu_set_min_deep_sleep_dcfclk`, table DRAM address/transfer calls, `dcn314_smu_set_zstate_support`, and `dcn314_smu_set_dtbclk`.

## Control Flow
Every public call first checks `smu_present` where appropriate; DCFCLK and idle-optimization requests also honor `debug.pstate_enabled`. The mailbox sequence always waits for PMFW readiness before clearing the response and issuing a new message. On failed watermark-table transfers or disabled DCFCLK DPM, it logs nonfatal diagnostics; other failed messages assert. Zstate support maps DC policy enums to a bitmask sent through `VBIOSSMC_MSG_AllowZstatesEntry`.

## State And Persistence
The file does not own long-lived allocations. It mutates PMFW state through messages and relies on `clk_mgr_internal` for `smu_present`, context, and logging. Mailbox state persists in MP1 C2P registers across individual transactions until overwritten.

## Dependencies And Integration Points
Depends on MP1 register offsets, `reg_helper` accessors, DC logging, timeout reporting through `dm_helpers_smu_timeout`, and table IDs from `dcn314_smu.h`. It is called exclusively by the DCN314 clock manager and participates in PMFW's VBIOSSMC contract.

## Risks And Edge Cases
Timeouts can stall clock updates for up to the full polling budget. Some failures are tolerated, but unexpected failures assert and can expose PMFW/BIOS mismatches. All frequency parameters are rounded up from kHz to MHz; callers must account for returned values being MHz-derived. If `smu_present` is false, wrappers return requested values without programming hardware.

## Test Signals
Test with PMFW present/absent, forced SMU timeouts, disabled DCFCLK DPM, watermark table transfer failure, zstate enum variants, DTBCLK toggle, and returned actual clock values from DISPCLK/DPPCLK/DCFCLK messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn314/dcn314_smu.c -->
