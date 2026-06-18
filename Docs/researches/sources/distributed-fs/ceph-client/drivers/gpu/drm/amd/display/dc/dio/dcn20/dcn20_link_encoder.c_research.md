# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c

Purpose: Extends the DCN10 link encoder for DCN20 with FEC control, DCN2 AUX initialization, USB-C alt-mode awareness, and an optional VBIOS-avoidance DP path.

Important APIs/types/functions: `dcn20_link_encoder_construct()` installs `dcn20_link_enc_funcs`. `enc2_fec_set_enable()`, `enc2_fec_set_ready()`, and `enc2_fec_is_active()` manage FEC bits. `link_enc2_read_state()` captures FEC/training state. `dcn20_link_encoder_enable_dp_output()` optionally uses `dcn10_link_encoder_enable_dp_output()` or updates local `dpcssys_phy_seq_cfg`. `enc2_hw_init()` programs AUX DPHY from a golden table or defaults.

Control flow: FEC APIs are direct register updates/readback. DP enable delegates to DCN10 unless `debug.avoid_vbios_exec_table` is set; in that mode it selects an MPLL config by link rate, marks lanes enabled, configures DIG lanes, and sets DP mode without running VBIOS. Max link capability starts from DCN10 and clamps lane count to two when USB-C alt mode is not four-lane. Hardware init writes AUX DPHY controls, sets legacy `TMDS_CTL0`, and initializes AUX HPD selection.

State/persistence: Adds `phy_seq_cfg` under `struct dcn20_link_encoder`; most persistent base state remains in embedded `dcn10_link_encoder`. Hardware state includes FEC bits, AUX DPHY settings, USB-C alt-mode fields, and inherited DIG/DP/HPD state.

Dependencies/integration: Reuses DCN10 helpers heavily, depends on VBIOS golden table values, DC debug flags, and DCN20 DPCS/UNIPHY register fields.

Risks: The VBIOS-avoidance path is partial: it prepares config and mode but does not perform the full transmitter table sequence. Unsupported link rates log and abort. Alt-mode lane limiting depends on `DP_IS_USB_C` and register state.

Test signals: FEC enable/ready/active readback, AUX golden-table/default writes, USB-C DP2 lane clamp, DP output with and without `avoid_vbios_exec_table`, and state capture for diagnostics.
