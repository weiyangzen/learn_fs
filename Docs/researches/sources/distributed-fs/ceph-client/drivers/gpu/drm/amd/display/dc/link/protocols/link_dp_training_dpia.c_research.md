# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.c

Purpose: implements DisplayPort link training for USB4 DPIA display endpoints. It adapts standard DP training to tunneled links by coordinating DPCD operations with DMUB/DPIA `SET_CONFIG` messages.

Important APIs/functions: `dpia_perform_link_training`, `dpia_training_abort`, `dpia_get_eq_aux_rd_interval`, and `dpia_set_tps_notification` are exported. Internal helpers configure the link, send `SET_CONFIG`, build VS/PE and link-mode payloads, translate DP training patterns to DPIA training stages, set/clear DPCD training patterns, and run CR/EQ in transparent or non-transparent LTTPR mode.

Control flow: `dpia_perform_link_training` decides LTTPR mode, configures channel coding/LTTPR mode/link settings/FEC, then trains hops from the DPTX-to-DPIA hop down to DPRX when non-transparent LTTPR mode is used. Each hop runs CR, EQ, and end-training. Transparent or no-LTTPR mode trains only DPRX and leaves most USB4 tunneling control to DPIA firmware. Successful training waits briefly and optionally checks link-loss status; aborts perform cleanup writes and `SET_CONFIG(SET_LINK=0)` unless consolidated training is enabled.

State/persistence: mutates `link_training_settings`, reads `link->dpcd_caps.lttpr_caps`, `link->is_hpd_pending`, debug/config flags, and `link->skip_fallback_on_link_loss`. It sends synchronous DMUB commands through `dm_helpers_dmub_set_config_sync` and writes DPCD link, lane, and pattern registers.

Dependencies/integration: integrates with `link_dp_dpia`, `link_hwss`, `dm_helpers`, `dmub_cmd`, `link_dpcd`, `link_dp_phy`, `link_dp_training_8b_10b`, `link_dp_capability`, and `dc_dmub_srv`. It depends on firmware ACK behavior for `SET_CONFIG`.

Risks: timing is sensitive, especially the 16 ms clock-sync delay during final-hop EQ. Non-transparent mode assumes DPTX-to-DPIA CR/EQ success based on message ACKs. HPD pending changes abort semantics. A bad repeater count or hop index can address wrong DPCD repeater windows.

Test signals: USB4 DP tunnel training for transparent/non-transparent LTTPR, DMUB `SET_CONFIG` ACK/NACK, sink unplug during configure/training, fallback after link-loss check, debug extended AUX interval, and compliance corner case using `skip_fallback_on_link_loss`.
