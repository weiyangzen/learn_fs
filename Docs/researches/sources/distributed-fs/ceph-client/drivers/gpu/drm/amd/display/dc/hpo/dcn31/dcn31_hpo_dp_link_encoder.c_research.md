# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.c

Purpose: Implements the DCN3.1 HPO DP link encoder for 128b/132b DisplayPort links. It controls link PHY enable/disable, test patterns, MST stream allocation table programming, VCP throttling, alt-mode detection, state readback, and VBIOS transmitter commands.

Important APIs and functions: `dcn31_hpo_dp_link_enc_enable` enables clocks, conditionally resets DPHY, enables precoder, and programs lane count. `dcn31_hpo_dp_link_enc_set_link_test_pattern` covers video, training, TPS, PRBS, custom 264-bit, and square patterns. `dcn31_hpo_dp_link_enc_update_stream_allocation_table` writes four SAT VC rows and triggers ACT/SAT update. `dcn31_hpo_dp_link_enc_set_throttled_vcp_size` converts fixed-point average slots to X/Y fields. `dcn31_hpo_dp_link_enc_enable_dp_output`, `disable_output`, and `set_ffe` call VBIOS transmitter control. `hpo_dp_link_encoder31_construct` binds the function table and register metadata.

Control flow: higher link code calls the `hpo_dp_link_encoder_funcs` vtable. PHY enable first uses BIOS to turn on transmitter output, then register programming enables link logic. MST allocation writes all four rows every update, zeroing unused entries, then waits for `SAT_UPDATE_PENDING` to clear. Disable uses BIOS transmitter disable and then shuts down encoder clocks.

State and persistence: object state includes instance, transmitter, HPD source, and register tables. Hardware state persists in DPHY, SAT, VC rate, and transmitter registers until changed. No heap allocation occurs.

Dependencies and integration: depends on `dc_bios_types.h`, `reg_helper.h`, `stream_encoder.h`, fixed-point helpers, MST allocation structs, and BIOS `transmitter_control`. Integrated with DP link training, MST payload manager, and HPO stream encoders.

Risks and test signals: invalid lane counts collapse to four-lane programming by ternary expression. Custom pattern code assumes at least 33 bytes. SAT wait timeout can leave MST allocation mismatched. Tests should cover each test pattern, lane-count encoding, VCP rounding carry, BIOS failure paths, MST table sizes 0-4, and alt-mode transmitter index bounds.
