# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dalsmc.h

## Purpose
This header defines the DCN 4.01 DAL-to-SMC message namespace used by the clock-manager SMU message wrapper. It is a compact contract for response codes, message IDs, and FCLK switch policy values.

## Important APIs, Types, And Functions
`DALSMC_VERSION` is defined as `0x1` and is checked at runtime by `dcn401_smu_check_msg_header_version`. Response constants include OK, Failed, UnknownCmd, CmdRejectedPrereq, and CmdRejectedBusy. Message IDs cover version checks, DRAM address setup, table transfer, hard minimum clock programming, DPM queries, display count, FCLK/UCLK p-state allow, CAB/UCLK policy, DMCUB wait behavior, DRR status, active/idle/SubVP UCLK/FCLK hardmins, and UMC channel query. `FclkSwitchAllow_e` names allow/disallow values.

## Control Flow And Integration
`dcn401_clk_mgr_smu_msg.c` includes this file and passes these IDs to `dcn401_smu_send_msg_with_param`. During `dcn401_init_clocks`, version messages validate that firmware and driver agree. During updates, the clock manager uses the hardmin, p-state, DMCUB wait, DRR, and display-count messages to synchronize PMFW with the Display Core mode state.

## State And Persistence
The header declares no state. Its constants control persistent firmware-side settings after messages are sent, such as p-state allow policy, hardmins, and watermark table ownership.

## Dependencies
It has no included dependencies and is consumed by the DCN 4.01 SMU message wrapper plus `dcn401_smu14_driver_if.h` table definitions.

## Risks
Message ID drift is the main risk. Since callers use numeric IDs directly, any mismatch between this header and PMFW can silently send a valid command with the wrong meaning. The version check catches only header version agreement, not semantic changes behind reused IDs.

## Test Signals
Firmware bring-up should assert that `DALSMC_MSG_GetMsgHeaderVersion` returns `DALSMC_VERSION`, every required message returns OK on supported ASIC revisions, and unsupported messages fail gracefully without corrupting clock-manager cached state.
