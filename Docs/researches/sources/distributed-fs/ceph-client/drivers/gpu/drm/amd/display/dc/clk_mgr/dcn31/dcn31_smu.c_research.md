<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c

## Purpose

`dcn31_smu.c` implements the DCN31/Yellow Carp VBIOS-SMU mailbox. It wraps clock, DCFCLK, DPPCLK, idle optimization, PME, table transfer, Z-state, and DTBCLK messages with SMU-presence and pstate-debug guards.

## Important APIs, Types, And Functions

Exports include `dcn31_smu_get_smu_version()`, `dcn31_smu_set_dispclk()`, `dcn31_smu_set_dprefclk()`, `dcn31_smu_set_hard_min_dcfclk()`, `dcn31_smu_set_min_deep_sleep_dcfclk()`, `dcn31_smu_set_dppclk()`, `dcn31_smu_set_display_idle_optimization()`, `dcn31_smu_enable_phy_refclk_pwrdwn()`, `dcn31_smu_enable_pme_wa()`, DRAM address setters, DPM/watermark table transfers, `dcn31_smu_set_zstate_support()`, and `dcn31_smu_set_dtbclk()`. Internal transport helpers are `dcn31_smu_wait_for_response()` and `dcn31_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for prior response, logs non-OK status, returns `-1` if busy, clears response, writes argument and message, waits for completion, handles explicit failure specially for watermark table transfer by logging and resetting the response to OK, reports timeouts, and returns C2PMSG_83. Most setters return requested clocks if SMU is absent; DCFCLK/deep-sleep and idle optimization also honor debug `pstate_enabled`. Z-state support maps DC enum values to Allow/Disallow message IDs and a parameter indicating Z10-capable states, with a debug gate that can downgrade Z10-only support to disallow.

## State And Persistence Behavior

Effects persist in PMFW clock constraints, idle optimization, Z-state permission, DTBCLK state, shared DPM/watermark table transfers, and MP mailbox registers. No dynamic state is allocated here.

## Dependencies And Integration Points

It depends on Yellow Carp MP register headers, `reg_helper`, DC logging, `dm_helpers_smu_timeout()`, debug flags in `dc`, and types/table IDs from `dcn31_smu.h`. `dcn31_clk_mgr.c` calls it during construction and updates.

## Risks

Returning requested clocks when SMU is absent can hide missing firmware interaction from higher layers. Pstate-disabled debug mode makes DCFCLK/idle calls no-ops returning `-1`. Watermark transfer failure is intentionally non-fatal, which can leave stale PMFW watermarks. Z-state downgrade behavior depends on `enable_z9_disable_interface`.

## Test Signals

SMU present/absent paths, pstate-disabled paths, clock set responses, table-transfer failure logging, timeout handling, Z-state allow/disallow with debug gate, DTBCLK toggles, idle optimization messages, and PME workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c -->
