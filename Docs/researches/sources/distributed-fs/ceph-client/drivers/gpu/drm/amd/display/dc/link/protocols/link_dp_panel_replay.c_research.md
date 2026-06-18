# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.c

## Purpose
`link_dp_panel_replay.c` implements VESA Panel Replay setup and DMUB command wrappers, with a selector that delegates AMD FreeSync Replay setup to eDP panel control code. It programs replay-related DPCD registers, configures ALPM and frame skipping, sends replay context/settings to DMUB, toggles Replay active state, updates DMUB Replay state, sends general Replay commands, and queries Replay state by GPINT.

## Important APIs And Functions
- `dp_setup_replay()` selects VESA Panel Replay (`dp_setup_panel_replay()`) or FreeSync Replay (`edp_setup_freesync_replay()`).
- `dp_pr_get_panel_inst()` maps a link to a panel/OTG instance using either legacy eDP panel instance lookup or current pipe context.
- `dp_pr_enable()` sends `DMUB_CMD__PR_ENABLE`, optionally sets static-screen params for external DP, and updates `replay_allow_active`.
- `dp_pr_copy_settings()` finds the link pipe, builds `DMUB_CMD__PR_COPY_SETTINGS`, and passes AUX/DIG/DPP/OTG/DPPHY, line time, FEC/DSC flags, debug flags, selective-update granularity, DSC slice height, and main-link activity option.
- `dp_pr_update_state()` and `dp_pr_set_general_cmd()` wrap DMUB update/general commands.
- `dp_pr_get_state()` polls `DMUB_GPINT__GET_REPLAY_STATE` until a non-invalid state or retry exhaustion.
- Internal helpers calculate static frame count and static-screen triggers, clear/configure DPCD Panel Replay enable/config registers, and set ALPM/frame skipping.

## Control Flow
VESA setup first clears Panel Replay enable/config DPCD registers and returns false if Replay is unsupported, no replay resource exists, or no panel instance can be found. It builds a `replay_context` from DDC AUX channel, link encoder transmitter/preferred engine, timing generator instance, and computed line time. It sends settings to DMUB through `dp_pr_copy_settings()`; on success it programs DPCD Panel Replay enable bits. Embedded links enable CRC/error IRQs, selective update, and early transport; external links only set basic enable. It then programs ALPM config based on replay settings and enables frame skipping when supported.

DMUB wrappers all resolve `panel_inst`, populate a `union dmub_rb_cmd`, set PR command type/subtype and payload size, and wake/execute DMUB synchronously. State query uses GPINT with reply and retries up to 1000 times if DMUB reports `PR_STATE_INVALID`.

## State And Persistence
The file writes `link->replay_settings.replay_feature_enabled`, `link->replay_settings.replay_allow_active`, sink DPCD Panel Replay configuration, receiver ALPM configuration, frame skipping mode, DMUB Replay firmware state, and stream static-screen parameters. It reads current pipe topology, link encoder instances, FEC state, DSC timing flags, selective update caps, and replay debug/config flags.

## Dependencies And Integration Points
It depends on eDP panel control for FreeSync Replay and static panel instance behavior, DPCD helpers, DM helpers, DMUB Replay command definitions, current `dc_state` pipe resources, link encoder state, and stream timing. HPD IRQ handling calls `dp_pr_enable()` to recover Replay after errors.

## Risks And Edge Cases
- The code assumes `link->ddc->ddc_pin` and `link->link_enc` are valid during setup; DPIA or unusual links could violate that if routed incorrectly.
- `lineTimeInNs` uses integer math and divides by `pix_clk_100hz / 10`; invalid timing could divide by zero.
- `dp_pr_get_state()` can spin 1001 GPINT attempts, assert on persistent invalid state, and still return true.
- DMUB command calls do not inspect command completion status beyond transport helper return in some paths.
- Only DP SST/eDP is supported for panel instance lookup; MST is explicitly not handled.

## Test Signals
Test VESA Replay setup on embedded and external DP SST, unsupported Replay early return, missing replay resource, frame update command version 1 vs 2 panel instance mapping, DMUB copy settings payload fields, Replay enable/disable idempotence, ALPM AUXLESS config, frame skipping DPCD bit, DSC/FEC flag propagation, state query timeout behavior, and HPD replay error recovery.
