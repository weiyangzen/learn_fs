# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c

## Purpose

`link_dpms.c` owns link-associated stream DPMS programming and link enable/disable sequencing. It bridges stream power state changes to signal-specific link protocols: DP/eDP training, MST/SST payload allocation, DSC programming, HDMI SCDC/retimer setup, LVDS/analog/virtual link output, audio, infoframes, USB4 bandwidth allocation, PSP stream config, and blank/unblank ordering.

## Important APIs, Types, And Functions

- Public blanking and state helpers: `link_blank_all_dp_displays()`, `link_blank_all_edp_displays()`, `link_blank_dp_stream()`, `link_set_all_streams_dpms_off_for_link()`, `link_resume()`, and `link_get_master_pipes_with_dpms_on()`.
- DSC APIs: `link_set_dsc_on_stream()`, `link_set_dsc_pps_packet()`, `link_set_dsc_enable()`, and `link_update_dsc_config()`.
- Payload APIs: `link_reduce_mst_payload()`, `link_increase_mst_payload()`, `allocate_mst_payload()`, `deallocate_mst_payload()`, `update_sst_payload()`, and `link_calculate_sst_avg_time_slots_per_mtp()`.
- Link enable/disable paths: `enable_link_dp()`, `enable_link_dp_mst()`, `enable_link_hdmi()`, `enable_link_lvds()`, `enable_link_analog()`, `enable_link_virtual()`, `enable_link()`, `disable_link_dp()`, and `disable_link()`.
- DPMS entries: `link_set_dpms_on()` and `link_set_dpms_off()`.
- Board support helpers program HDMI retimer/redriver I2C settings from VBIOS integrated info or defaults.

## Control Flow

`link_set_dpms_on()` validates it is called on the master pipe, resolves link encoder/HWSS, sets OTG mux, programs stream attributes, powers VPG, builds infoframes, handles seamless/eDP fast boot early returns, sets up DSC before link training, optionally sets panel replay, enables the signal-specific link, enables the stream, enables DSC on the sink and sends PPS, allocates USB4 bandwidth and DP payloads, unblanks, enables stream features, updates PSP, and enables audio.

`link_set_dpms_off()` performs the reverse at stream level: AV mute, audio disable, PSP update, blanking, USB4 deallocation, MST/SST payload deallocation, HDMI SCDC/retimer legacy setup, signal-specific stream/link disable ordering, ASSR disable, DSC disable, HPO mux reset, VPG powerdown, and eDP panel-mode state workaround.

DP link enable powers eDP when needed, optionally toggles MST mode, updates clocks for DP1.x, writes source OUI/cable ID, trains with retries and optional fallback, enables FEC for 8b/10b, and restores eDP AUX brightness/backlight settings. MST allocation uses DM helpers to update sideband payloads and local link encoder allocation tables. DP2 SST payload allocation writes DPCD VC payload registers and updates HPO allocation hardware.

## State And Persistence Behavior

The file mutates hardware state extensively and updates in-memory link/stream state: `link_status.link_active`, `cur_link_settings`, `mst_stream_alloc_table`, `dpia_bw_alloc_config`, `stream->dsc_packed_pps`, `stream->dpms_off`, panel mode, PSP stream config, audio state, AV mute, DPCD power/MST/FEC/DSC/hblank states, HDMI SCDC state, retimer/redriver I2C state, DCCG DSC clocks, VPG power, and OTG output mux. No on-disk persistence is used.

## Dependencies And Integration Points

It depends on HWSS selection, DPCD/DDC/HPD helpers, DP PHY/training/capability, eDP panel control, panel replay, DPIA bandwidth, DM MST helpers, resource and infoframe builders, DSC blocks, DCCG/clock manager, VPG, link validation bandwidth formulas, and PSP content-protection stream config. `link_factory.c` installs its public functions into `link_service`.

## Risks And Edge Cases

- The file acknowledges a boundary issue: DSC programming is done in link DPMS sequencing despite depending on front-end locks and OPTC state.
- MST allocation has many ordering requirements: source allocation table, sideband messages, ACT polling, and throttled VCP size must stay consistent.
- DP2 SST payload update returns `DC_OK` after logging some failures, so black-screen symptoms may be the only runtime signal.
- USB4 bandwidth allocation stores per-remote-sink requested bandwidth and adds overhead; stale remote sink indexes can misallocate.
- HDMI retimer/redriver programming depends on VBIOS tables and fixed default I2C addresses.
- DP link training failure is tolerated for SST in some cases but not MST.
- DPMS-on returns early if `stream->dpms_off` is true, so caller state must be coherent.

## Test Signals

Exercise DP/eDP SST, DP MST, DP2 128b/132b SST/MST, USB4 DPIA bandwidth allocation, DSC enable/disable and dynamic PPS update, FEC, hblank reduction, HDMI >340 MHz SCDC/retimer/redriver, DVI/LVDS/RGB/virtual paths, seamless boot, eDP fast boot, OLED/backlight AUX restore, link-training fallback/failure, MST payload increase/reduce, and DPMS off/on ordering. Logs under DP2 payload, MST, DSC, retimer/redriver, hotplug, and PSP update are important.
