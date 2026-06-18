# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/link_service_types.h

Purpose: Defines link-service types for DisplayPort/eDP link training, test patterns, LTTPR mode, DPCD lane-set bitfields, MST stream allocation, and link power/revision constants.

Important APIs and types: `enum dp_power_state`, `enum edp_revision`, DP data-efficiency constants, `enum lttpr_mode`, `struct link_training_settings`, `enum dp_test_pattern`, `IS_DP_PHY_SQUARE_PATTERN`, `IS_DP_PHY_PATTERN`, `enum dp_test_pattern_color_space`, `enum dp_panel_mode`, `enum dpcd_source_sequence`, `union dpcd_training_lane_set`, `struct dc_dp_mst_stream_allocation`, and `struct dc_dp_mst_stream_allocation_table`.

Control flow: Link training code consumes `link_training_settings` as both configured policy and mutable training state: link settings, lane voltage/pre-emphasis/post-cursor/FFE pointers, timing limits, training patterns, enhanced framing, LTTPR behavior, and lane settings arrays. Test-pattern code uses enums/macros to classify PHY/link/audio/video patterns. MST code receives a payload allocation table from DM.

State and persistence: The training structure contains mutable state (`hw_lane_settings`, `dpcd_lane_settings`) despite comments calling for a future separation from policy. MST allocation table is a snapshot passed from DRM/DM into DC and should not be used for atomic state calculations in DM.

Dependencies and integration points: Includes `grph_object_id.h`, `dal_types.h`, and `irq_types.h`; depends on DC link settings, lane settings, DPCD unions, and `MAX_CONTROLLER_NUM`. Integrated with DP AUX/DPCD programming, link encoder training, LTTPR handling, compliance tests, and MST payload programming.

Risks: Mixing policy and mutable training state can cause retries to accidentally change intended settings. Endian-specific bitfields require correct `LITTLEENDIAN_CPU` or `BIGENDIAN_CPU` definitions. MST table comments warn against misuse in atomic state calculations. Data efficiency constants affect bandwidth validation and must match DP encoding/FEC assumptions.

Test signals: DP link training retries across lane counts/rates, LTTPR transparent/non-transparent modes, DPCD lane-set packing on supported endian, test pattern classification, FEC efficiency calculations, and MST stream allocation propagation.
