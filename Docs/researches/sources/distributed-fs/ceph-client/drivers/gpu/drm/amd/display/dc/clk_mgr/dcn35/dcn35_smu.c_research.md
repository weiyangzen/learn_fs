# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_smu.c

## Purpose
This file implements the DCN 3.5 DAL/VBIOS SMU mailbox wrapper. It converts display clock-manager requests into PMFW messages for clock programming, watermark and DPM table transfers, display idle optimizations, Z-state policy, DTB/DPREF queries, IPS support, and host-router bandwidth notification.

## Important APIs, Types, And Functions
The central helpers are `dcn35_smu_wait_for_response` and `dcn35_smu_send_msg_with_param`. They poll `MP1_SMN_C2PMSG_91`, write arguments to `MP1_SMN_C2PMSG_83`, and trigger messages through `MP1_SMN_C2PMSG_67`. Public wrappers include `dcn35_smu_set_dispclk`, `dcn35_smu_set_dppclk`, `dcn35_smu_set_hard_min_dcfclk`, `dcn35_smu_set_min_deep_sleep_dcfclk`, `dcn35_smu_set_dprefclk`, `dcn35_smu_get_dprefclk`, `dcn35_smu_get_dtbclk`, `dcn35_smu_set_dtbclk`, `dcn35_smu_set_zstate_support`, `dcn35_smu_transfer_dpm_table_smu_2_dram`, `dcn35_smu_transfer_wm_table_dram_2_smu`, `dcn35_smu_exit_low_power_state`, `dcn35_smu_get_ips_supported`, and `dcn35_smu_notify_host_router_bw`.

## Control Flow And Integration
Each exported function first checks `clk_mgr->smu_present` where firmware is required, then sends one message with an integer parameter. Clock requests are converted from kHz to MHz with ceiling semantics, and firmware return values are converted back to kHz. Table transfer wrappers rely on callers to program high and low DRAM address registers first. Z-state support maps Display Core enum values to bitfields for Z8, Z9, and Z10 support.

## State And Persistence
The file does not own long-lived heap state. Its persistent effects are PMFW state changes: hard minimum clocks, deep sleep DCFCLK, idle optimization flags, PME workaround state, DTB clock enablement, and SMU table contents. The wait loop honors `debug.disable_timeout` by extending retry count, which can intentionally make firmware waits unbounded for debug.

## Dependencies
It depends on register helpers, MP 14 register offsets and masks, `clk_mgr_internal`, Display Core logging, and the SMU table/message IDs from `dcn35_smu.h`. It integrates with `dcn35_clk_mgr.c`, which calls these wrappers during initialization, display commits, watermark notification, low-power transitions, and DPIA host-router bandwidth updates.

## Risks
Timeout and error handling is assert-heavy. A failed watermark transfer is downgraded to a warning, but many other failures assert and continue to read the argument register, so incorrect firmware behavior can propagate bogus clock values. Message IDs are locally defined with a TODO about real headers, creating interface drift risk. Unit conversion by ceiling avoids underclocking but can increase power.

## Test Signals
Look for `DC_LOG_SMU` traces showing requested and actual clock values, warnings on non-OK responses, successful IPS query/exit flows, and no display underflow during clock changes. Firmware interface tests should cover busy, failed, timeout, and successful response register sequences.
