# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c

## Purpose
Implements the DCN2.1 link encoder, including Renoir-style PHY acquisition/release, MPLL configuration for DP rates when avoiding VBIOS execution tables, and construction of a DCN2.1-specific link function table.

## Important APIs, Types, And Functions
`dcn21_mpll_cfg_ref[]` stores reference MPLL settings for RBR, HBR, HBR2, and HBR3. `update_cfg_data()` selects the MPLL config for a requested link rate and enables all four lanes. `dcn21_link_encoder_acquire_phy()` handles USB-C DP-alt-mode acknowledgement and enables the DP reference clock. `dcn21_link_encoder_release_phy()` releases alt-mode ack and disables ref clock. `dcn21_link_encoder_enable_dp_output()` and MST variant wrap PHY acquisition around inherited enable paths. `dcn21_link_encoder_disable_output()` releases PHY for DP signals. The constructor initializes fields, transmitter-to-DIG mapping A through G, and VBIOS feature flags.

## Control Flow
DP output enable first acquires PHY. If VBIOS exec tables are allowed, it delegates to DCN10 enable. If debug avoids VBIOS exec tables, it fills local PHY sequence config, calls `enc1_configure_encoder()`, and sets up DP output. MST enable delegates after PHY acquisition. Disable delegates to DCN10 and releases PHY for DP signals. Construction populates base identity, output signal mask, register maps, preferred engine by transmitter, default HDMI 6G, VBIOS caps, and debug overrides.

## State And Persistence
Software state includes the base link encoder and `phy_seq_cfg`. Hardware state includes DP-alt disable acknowledgement, DP reference clock enable, and inherited link/PHY programming. Feature flags persist in the encoder object.

## Dependencies And Integration Points
Depends on DCN20 link encoder headers, DCN10 link helpers, VBIOS callbacks, GPIO/HPD data, Linux delay, stream encoder functions, and debug flags. Used by DCN2.1 resource/link-training paths.

## Risks
PHY acquisition can return without release if `update_cfg_data()` fails after reference clock enable in the avoid-VBIOS path. Lane mapping is marked TODO and currently enables all lanes. USB-C alt-mode handshake depends on `RDPCS_PHY_DPALT_DISABLE` semantics and fixed 40 microsecond delay. Unsupported link rates return false and abort enable.

## Test Signals
DP SST/MST link training at RBR/HBR/HBR2/HBR3, USB-C alt-mode plug/unplug, avoid-VBIOS-exec-table debug mode, reference-clock enable/disable readback, and failure-path cleanup tests are important.
