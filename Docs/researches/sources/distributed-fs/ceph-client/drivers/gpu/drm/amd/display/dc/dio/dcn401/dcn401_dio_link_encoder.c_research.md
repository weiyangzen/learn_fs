# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.c

## Purpose
This file implements the DCN401 link encoder. It resembles DCN32 capability and DMUB-alt-mode behavior while adopting a newer backend enable model like DCN35, including separate backend clock and enable bits.

## Important APIs and Functions
`enc401_hw_init` programs AUX DPHY constants, sets `TMDS_CTL0`, and initializes AUX. `dcn401_link_encoder_enable_dp_output` delegates to DCN10 VBIOS DP enable unless `debug.avoid_vbios_exec_table` is true; direct mode returns without programming. `dcn401_link_encoder_setup` writes `DIG_BE_MODE` for DP, DVI, HDMI, or MST, then sets both `DIG_BE_CLK_EN` and `DIG_BE_ENABLE`. `dcn401_is_dig_enabled` requires both bits. `dcn401_get_dig_mode` maps backend mode values back to signal types.

`dcn401_link_enc_funcs` uses DCN401 setup/state, DCN32 alt-mode and max-link-cap helpers, DCN31 DIO PHY mux, and common DCN10/DCN20 operations. `dcn401_link_encoder_construct` initializes object state, sets USB-C feature for USB-C connectors, maps transmitters A-E, queries connector speed capabilities, forces DP2 capable, imports HBR/UHBR/HDMI flags, and applies HDMI disable.

## Control Flow
Construction is connector-capability based. Setup is signal-driven and always enables backend clock and backend logic after mode selection. DP enable has the same VBIOS/direct split as DCN32. Alt-mode and max-link-cap behavior are delegated to DCN32 DMUB query helpers.

## State and Persistence
Persistent state includes backend mode, backend clock enable, backend enable, AUX DPHY registers, TMDS control, feature flags, preferred engine, connector speed capability bits, USB-C feature state, and common DP/HDMI link registers through delegated helpers.

## Dependencies and Integration Points
Dependencies include DCN31 DIO mux, DCN32 alt/max-cap helpers, DCN30 register contracts, VBIOS connector speed callback, GPIO, and common link encoder functions. It integrates into DCN401 resource construction and link programming paths.

## Risks and Test Signals
Risks include direct DP enable no-op under `avoid_vbios_exec_table`, mandatory DMUB availability through DCN32 alt helpers, duplicate `MIN` definition guards, USB-C feature copy ordering, and consistency between backend clock/enable state and disable paths delegated to older code. Tests should cover backend mode/setup for DP/DVI/HDMI/MST, `is_dig_enabled` with both bits, connector speed capability import, USB-C lane limiting, DP enable under both debug modes, HDMI disable override, and transmitter mapping.
