# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.c

## Purpose
`link_dp_phy.c` is the DP PHY state bridge. It enables/disables main-link output, updates current link and lane settings, controls sink RX power state, programs hardware drive settings, mirrors lane settings to DPCD, and manages FEC ready/enable state around training.

## Important APIs
- `dpcd_write_rx_power_ctrl()` writes `DP_SET_POWER` D0/D3 unless synchronous link training is in progress.
- `dp_enable_link_phy()` stores `cur_link_settings`, enables DP link output through HWSS, then powers the sink receiver D0.
- `dp_disable_link_phy()` optionally powers the receiver D3, disables link output, clears `cur_link_settings`, and notifies clock manager of link-rate changes.
- `dp_set_hw_lane_settings()` programs HW lane settings through link HWSS, with LTTPR non-transparent skip logic for non-immediate downstream repeaters and fixed-VS exceptions.
- `dp_set_drive_settings()` programs HW settings, converts them to DPCD lane settings, and writes DPCD lane settings.
- `dp_set_fec_ready()` writes `DP_FEC_CONFIGURATION`, calls encoder `fec_set_ready`, and moves `link->fec_state` between not-ready and ready.
- `dp_set_fec_enable()` waits at least 7 us after training before enabling FEC in the encoder and updates `fec_state`.

## Control Flow
Training and verification call `dp_enable_link_phy()` before DPCD training operations. Lane setting updates flow from training decisions into `dp_set_hw_lane_settings()` and then to sink-visible DPCD through `dp_set_drive_settings()`. On disable, receiver power-down is skipped when a dongle workaround requires it, implicit eDP power control is skipped, or the link is disconnected. FEC is set ready before training when policy allows and enabled after successful training.

## State And Persistence
The file mutates `link->cur_link_settings`, `link->cur_lane_setting`, `link->fec_state`, sink `DP_SET_POWER`, sink `DP_FEC_CONFIGURATION`, hardware link output, hardware PHY lane drive, and clock-manager notification state.

## Dependencies And Integration Points
It depends on link HWSS, DPCD helpers, generic training helpers for DPCD lane conversion, capability FEC policy, clock manager, resource/link encoder selection, and Atom firmware chip caps. Training, verification, DPMS, and capability code all call into this file.

## Risks And Edge Cases
- `dpcd_write_rx_power_ctrl()` skips writes during sync link training; callers must account for receiver power state.
- Non-transparent LTTPR lane programming deliberately skips non-immediate downstream repeaters except fixed-VS/128b cases.
- FEC state transitions assume encoder callbacks exist and that DPCD writes succeed before hardware state changes.
- `dp_disable_link_phy()` clears `cur_link_settings`, which affects later HPD IRQ allow/link-loss logic.

## Test Signals
Test PHY enable/disable with receiver power D0/D3, keep-receiver-powered dongles, eDP implicit power skip, LTTPR non-transparent lane programming offsets, fixed-VS exceptions, FEC ready/enable/disable transitions, and clock-manager notification after disable.
