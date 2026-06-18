<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c

## Purpose

`rv1_clk_mgr_vbios_smu.c` implements the Raven1 VBIOS-SMU mailbox used by the RV1 clock manager to request DISPCLK changes. It provides a thin register-level transport over MP1 SMN C2PMSG registers and updates DMCU PSR timing after the SMU returns the actual clock.

## Important APIs, Types, And Functions

The exported API is `rv1_vbios_smu_set_dispclk()`. Internal helpers are `rv1_smu_wait_for_response()` and `rv1_vbios_smu_send_msg_with_param()`. The file defines local MP1 base/address structures, C2PMSG register constants, `REG`/`FN` helpers, and VBIOSSMC message/result IDs for DISPCLK/DPREFCLK and response status.

## Control Flow

`rv1_vbios_smu_set_dispclk()` converts the requested kHz to MHz, calls the generic send helper with `VBIOSSMC_MSG_SetDispclkFreq`, and treats C2PMSG_83 as the returned actual MHz. The send helper clears C2PMSG_91 to BUSY, writes the parameter to C2PMSG_83, writes the message ID to C2PMSG_67, then polls C2PMSG_91 until it is no longer BUSY. An assertion expects `VBIOSSMC_Result_OK`. After a successful request, DMCU PSR wait-loop count is adjusted to `actual_mhz / 7` when DMCU is initialized and the returned clock differs from DFS bypass state.

## State And Persistence Behavior

The transport persists state only in MP1 mailbox registers and the returned clock in caller-managed `clk_mgr` state. DMCU wait-loop programming persists in DMCU firmware state until changed. The file keeps no heap or static mutable state.

## Dependencies And Integration Points

It depends on `reg_helper` register access, Linux sleep/delay functions through the included environment, DC/DMCU objects, `khz_to_mhz_ceil()`, and `dmcu->funcs`. It is installed as RV1's internal `.set_dispclk` callback.

## Risks

The polling helper stops on any non-BUSY response but only asserts OK; non-OK responses can still lead to reading C2PMSG_83 as a clock in non-assert builds. Register constants and MP1 base offsets are hard-coded locally. Timeout behavior is bounded by 1000 retries at 10 us but has no explicit error return from `rv1_vbios_smu_set_dispclk()` except whatever value remains in the parameter register.

## Test Signals

Trace SMU mailbox writes during DISPCLK changes, verify actual clock return values, exercise display resume and PSR panels, inject or simulate non-OK responses, and run mode changes that force repeated DISPCLK updates through the RV1 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c -->
