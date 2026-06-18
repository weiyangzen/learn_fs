<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c

## Purpose

`dcn301_smu.c` implements the Van Gogh/DCN3.0.1 VBIOS-SMU mailbox. It wraps MP1 C2PMSG messages for clock setting, DCFCLK constraints, display idle optimization, PME, DRAM-address setup, and DPM/watermark table transfers.

## Important APIs, Types, And Functions

Exports include `dcn301_smu_get_smu_version()`, `dcn301_smu_set_dispclk()`, `dcn301_smu_set_dprefclk()`, `dcn301_smu_set_hard_min_dcfclk()`, `dcn301_smu_set_min_deep_sleep_dcfclk()`, `dcn301_smu_set_dppclk()`, `dcn301_smu_set_display_idle_optimization()`, `dcn301_smu_enable_phy_refclk_pwrdwn()`, `dcn301_smu_enable_pme_wa()`, DRAM address setters, and DPM/watermark table transfer helpers. Internal helpers are `dcn301_smu_wait_for_response()` and `dcn301_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for the previous response, logs non-OK responses, returns `-1` if still busy, clears response to BUSY, writes the argument and message, waits for completion, reports timeout, and returns C2PMSG_83. Clock setters convert kHz to MHz and return actual MHz as kHz. Table transfer functions assume the caller already set a GPU/MC address high and low. Display idle optimization sends a packed bitfield for DF request disable, PHY refclk off, and related idle flags.

## State And Persistence Behavior

State persists in PMFW clock/power policy, display idle optimization state, DPM/watermark table memory shared with SMU, and MP mailbox registers. No local dynamic state is held.

## Dependencies And Integration Points

It depends on Van Gogh MP register headers, `reg_helper`, `dm_helpers_smu_timeout()`, DC logging, and definitions from `dcn301_smu.h`. `vg_clk_mgr.c` uses it for all PMFW communication.

## Risks

Failure returns can become negative clocks when multiplied by 1000. Several command IDs are commented out or reused, so firmware ABI alignment is critical. `dcn301_smu_set_dprefclk()` notes DP DTO programming is handled elsewhere. Void helpers ignore send failure.

## Test Signals

SMU version detection, DISP/DPP/DCFCLK set responses, idle optimization transitions, DPM table transfer into framebuffer memory, watermark upload, PME workaround, timeout injection, and validation on Van Gogh firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c -->
