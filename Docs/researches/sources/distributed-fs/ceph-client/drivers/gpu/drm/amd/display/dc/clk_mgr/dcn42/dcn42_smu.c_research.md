# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_smu.c

## Purpose
This file implements the DCN 4.2 PMFW/DAL mailbox wrapper. It programs PMFW display clocks, hard minimum DCFCLK, deep-sleep DCFCLK, DPPCLK, display idle policy, PME workaround, DRAM table addresses, DPM/watermark table transfers, Z-state support, DTB enablement, and DPREF/DTB clock queries.

## Important APIs, Types, And Functions
The low-level helpers are `dcn42_smu_wait_for_response` and `dcn42_smu_send_msg_with_param`. They use MP 15 registers `MP1_SMN_C2PMSG_71`, `72`, and `73` via `DAL_MSG_REG`, `DAL_RESP_REG`, and `DAL_ARG_REG`. Public wrappers include `dcn42_smu_get_pmfw_version`, `dcn42_smu_set_dispclk`, `dcn42_smu_set_dppclk`, `dcn42_smu_set_hard_min_dcfclk`, `dcn42_smu_set_min_deep_sleep_dcfclk`, `dcn42_smu_set_display_idle_optimization`, `dcn42_smu_enable_phy_refclk_pwrdwn`, `dcn42_smu_enable_pme_wa`, `dcn42_smu_transfer_dpm_table_smu_2_dram`, `dcn42_smu_transfer_wm_table_dram_2_smu`, `dcn42_smu_set_zstate_support`, `dcn42_smu_get_dprefclk`, `dcn42_smu_get_dtbclk`, and `dcn42_smu_set_dtbclk`.

## Control Flow And Integration
Before sending, the wrapper waits until the response register is not `CmdRejectedBusy`, writes busy to clear it, writes the parameter, triggers the message, and waits for a non-busy result. Clock setters convert kHz requests to MHz and return firmware response values in kHz. Table transfers assume the high and low DRAM address messages have already been sent. Z-state support uses the same Z8/Z9/Z10 bit encoding as DCN 3.5.

## State And Persistence
The file owns no heap state. Its effects persist in PMFW until changed: clock hardmins, idle optimization flags, PME restore, table contents, Z-state policy, and DTB state. Debug `disable_timeout` can extend the wait loop indefinitely.

## Dependencies
It depends on MP 15 register headers, register helpers, `dcn42_smu.h`, Display Core logging, and `clk_mgr_internal`. `dcn42_clk_mgr.c` is the main caller.

## Risks
The response model differs from DCN 3.5: busy is `CmdRejectedBusy`, and any other value exits the wait loop. If firmware returns a prereq or unknown-command code before send, the code logs a warning but still sends. Failed watermark transfer is warned and reset to OK, while other failed commands rely on warnings/asserts rather than structured recovery. There is an unused `dcn42_dpia_host_router_bw` union, suggesting copied or incomplete functionality.

## Test Signals
Check PMFW version detection, busy retry behavior, failed watermark transfer warning, correct clock unit conversions, DTB on/off transitions, Z-state bit parameters, and logs showing requested versus actual clock values.
