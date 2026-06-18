<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c

## Purpose

`rn_clk_mgr_vbios_smu.c` implements Renoir's VBIOS-SMU mailbox for display clock, DCFCLK, DPPCLK, PHYCLK, display-count/low-power, 48 MHz refclk power-down, PME workaround, SMU version, and periodic retraining queries.

## Important APIs, Types, And Functions

Exports include `rn_vbios_smu_get_smu_version()`, `rn_vbios_smu_set_dispclk()`, `rn_vbios_smu_set_hard_min_dcfclk()`, `rn_vbios_smu_set_min_deep_sleep_dcfclk()`, `rn_vbios_smu_set_phyclk()`, `rn_vbios_smu_set_dppclk()`, `rn_vbios_smu_set_dcn_low_power_state()`, `rn_vbios_smu_enable_48mhz_tmdp_refclk_pwrdwn()`, `rn_vbios_smu_enable_pme_wa()`, and `rn_vbios_smu_is_periodic_retraining_disabled()`. Internal transport helpers are `rn_smu_wait_for_response()` and `rn_vbios_smu_send_msg_with_param()`.

## Control Flow

The generic send helper waits for a non-BUSY response before sending, logs if the prior response was not OK, returns `-1` if still BUSY, clears the response register, writes the argument and message ID, waits again, reports SMU timeout through `dm_helpers_smu_timeout()`, and returns the argument register. Clock setters convert kHz to MHz and multiply returned MHz back to kHz. DCFCLK hard-min and deep-sleep setters are gated on SMU version `0x370c00`. Display low-power is encoded as display count 0 or 1.

## State And Persistence Behavior

State persists in MP1 C2PMSG registers and PMFW-controlled clock/power policy. DISPCLK updates also adjust DMCU PSR wait-loop state. The implementation holds no allocated or static mutable state.

## Dependencies And Integration Points

It depends on Renoir MP register headers, `reg_helper`, `dm_helpers_smu_timeout()`, DC logging, DMCU, `khz_to_mhz_ceil()`, and `enum dcn_pwr_state`. `rn_clk_mgr.c` calls these helpers for all runtime SMU interactions.

## Risks

The transport returns the argument register for all messages, even commands whose response semantics are not frequencies. Failed commands may propagate `-1` through kHz conversions. Assertions assume PMFW returns actual DISP/DPP clocks at least as high as requested. Periodic retraining query passes default parameter 1 so unsupported messages are treated conservatively as disabled.

## Test Signals

Mailbox timeout injection, SMU version-gated DCFCLK messages, display low-power display-count messages, DPP/DISP actual clock validation, 48 MHz power-down toggling, PME workaround calls, periodic retraining query behavior, and PSR wait-loop updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c -->
