# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.c

## Purpose

`link_detection.c` owns link and receiver detection state for AMD Display Core links. It classifies connected sink signal types, probes HPD/DDC/AUX/DPCD/EDID, manages local and remote sink objects, queries HDCP and dongle capabilities, verifies DP link capability, starts/stops MST topology management, and handles DPIA/USB4 detection quirks.

## Important APIs, Types, And Functions

- `link_detect()` is the public detection entry. It detects the local sink, verifies link capability, delegates MST topology discovery when needed, and resets MST topology on disconnect.
- `link_detect_connection_type()` determines physical, analog, eDP, DPIA, and HPD-based connection type without downstream MST enumeration.
- `detect_link_and_local_sink()` is the central local-sink state machine. It disconnects old sinks, detects signal/caps, creates `dc_sink`, reads EDID/MCCS/SCDC, applies panel patches, queries HDCP, initializes DP trace, and handles eDP panel config.
- `detect_dp()` handles native DP versus passive dongle detection, active branch classification, DPCD capability retrieval, and external bridge quirks.
- `verify_link_capability()` chooses destructive training-based verification or non-destructive reported/max capability assignment.
- `discover_dp_mst_topology()` and `link_reset_cur_dp_mst_topology()` start/stop DRM MST topology helpers and maintain DPIA DSC workaround flags.
- `link_add_remote_sink()` and `link_remove_remote_sink()` manage MST remote sink references and EDID parsing.
- `link_is_hdcp14()`, `link_is_hdcp22()`, `link_get_status()`, and `link_clear_dprx_states()` expose state managed here.

## Control Flow

Detection begins with connection type. Analog links ignore HPD and use an EDID-header DDC probe, falling back to DAC load detection. eDP powers the panel and waits for HPD readiness unless power sequencing is disabled. DPIA links query tunneled HPD state and pending HPD flags. Physical digital links use HPD state.

When a connection exists, the function chooses signal/transaction type by connector. HDMI/DVI/LVDS/RGB are I2C. eDP reads eDP caps and current link settings. DP waits for USB-C alt mode if needed, detects DPCD caps through AUX or passive dongle identity through I2C, applies external bridge and DPIA tunnel rules, and may enable USB4 bandwidth allocation mode. It then creates a local sink, reads EDID, handles no-EDID analog/DP failure modes, reads MCCS/SCDC, adjusts HDMI/DVI/RGB sink signal interpretation, queries HDCP, and initializes panel config for eDP.

After local sink detection, DP capability verification may destructively turn streams off and train at known limits, or non-destructively use reported/max caps for eDP, DPIA, MST, unavailable encoders, or debug skip modes. MST-capable DP sinks are delegated to the MST topology manager, causing `link_detect()` to return false for upper-layer local handling while the MST manager owns downstream enumeration.

## State And Persistence Behavior

The file mutates many in-memory link fields: `local_sink`, `remote_sinks[]`, `sink_count`, `type`, `dpcd_caps`, `dpcd_sink_count`, `cur_link_settings`, `reported_link_cap`, `verified_link_cap`, `hdcp_caps`, `aux_mode`, `link_state_valid`, `wa_flags`, `panel_config`, `psr_settings`, `replay_settings`, `dongle_max_pix_clk`, and `dprx_states`. It manages sink reference counts with `dc_sink_retain()` and `dc_sink_release()`. It does not write on-disk state.

## Dependencies And Integration Points

It integrates with DDC/AUX helpers, DPCD/capability parsers, HPD helpers, DP training, DP PHY, DPIA bandwidth, eDP panel control, DP trace, DM EDID/MCCS/MST helpers, clock manager power-state hooks, and hardware sequencing callbacks for eDP power and analog load detect. `link_factory.c` installs these functions into `link_service`.

## Risks And Edge Cases

- Sink reference handling is delicate when replacing a same-EDID sink, aborting EDID reads, or downstream SST branch unplug occurs.
- Destructive verification turns streams off and trains; it is gated by several debug/config/resource checks but can still be disruptive.
- Passive dongle detection relies on retrying I2C signatures and inferred max pixel clocks.
- USB-C alt-mode polling has a 200 ms timeout and may fail early HPD events.
- DP no-EDID behavior intentionally keeps fail-safe DP connected, while HDMI/DVI no-EDID aborts.
- DPIA MST DSC always-on workaround is vendor/device-specific and must be cleared on topology reset.

## Test Signals

Coverage should include HDMI/DVI/LVDS/RGB, analog with DDC and load detect, DP native SST, DP passive HDMI/DVI dongles, active dongles, SST branch unplug, MST branch connect/disconnect, eDP resume and OLED AUX settings, USB-C alt-mode delay, DPIA HPD and bandwidth allocation mode, EDID same/change, bad/no EDID, HDCP 1.4/2.2 capability queries, and destructive/non-destructive link verification. Logs under hotplug, EDID parser, DP trace, and MST topology are primary runtime signals.
