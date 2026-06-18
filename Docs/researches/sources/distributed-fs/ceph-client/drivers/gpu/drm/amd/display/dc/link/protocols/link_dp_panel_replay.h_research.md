# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.h

## Purpose
`link_dp_panel_replay.h` declares Panel Replay setup and DMUB control APIs for DP links.

## Important APIs
- `dp_setup_replay()` configures VESA Panel Replay or FreeSync Replay for a link/stream.
- `dp_pr_get_panel_inst()` maps a link to a panel instance.
- `dp_pr_enable()` toggles Replay active state.
- `dp_pr_copy_settings()` sends Replay context to DMUB.
- `dp_pr_update_state()` and `dp_pr_set_general_cmd()` issue DMUB PR commands.
- `dp_pr_get_state()` queries current Replay firmware state.

## Control Flow And Integration
The header is used by commit/setup paths and HPD IRQ recovery. It exposes DMUB command data types through the function signatures, so callers must include compatible DMUB definitions via `link_service.h` and related includes.

## State, Risks, And Test Signals
Functions mutate `link->replay_settings` and DMUB/sink Replay state. Tests should compile call sites for VESA and FreeSync Replay, verify panel instance resolution, and exercise enable/update/general/state command wrappers.
