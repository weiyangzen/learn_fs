# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c

## Purpose
This file implements the DCN32 link encoder. It keeps most DCN30/DCN31 behavior but uses connector speed capability data, forces DP2 capability, queries USB-C alt-mode state through DMUB, and changes direct DP enable behavior when VBIOS execution is avoided.

## Important APIs and Functions
`enc32_hw_init` programs AUX DPHY RX/TX constants, sets `TMDS_CTL0`, and initializes AUX. `dcn32_link_encoder_enable_dp_output` delegates to the DCN10 VBIOS path unless `debug.avoid_vbios_exec_table` is true; in that direct-programming case the function intentionally does nothing. `query_dp_alt_from_dmub`, `dcn32_link_encoder_is_in_alt_mode`, and `dcn32_link_encoder_get_max_link_cap` use DMUB VBIOS transmitter query commands to derive DP Alt Mode and cap lanes to two when USB is active without DP4.

`dcn32_link_enc_funcs` reuses many DCN10/DCN20 operations, DCN31 DIO PHY mux, DCN32 alt/max-cap helpers, and `enc32_hw_init`. `dcn32_link_encoder_construct` initializes object state, maps transmitters A-E to DIG engines, queries `get_connector_speed_cap_info`, imports HBR/UHBR/HDMI capability bits, and sets `IS_DP2_CAPABLE = 1`.

## Control Flow
Construction is similar to DCN30 but capability data is connector-based instead of encoder-based. Alt-mode and max-link-cap queries always use DMUB; there is no non-DMUB legacy path in this file. DP enable returns early through VBIOS path unless direct programming is requested.

## State and Persistence
Persistent object state includes feature flags, connector identity, register pointers, preferred engine, and VBIOS-derived connector speed capabilities. Hardware state includes AUX DPHY registers, TMDS control, and any common link encoder state reached through delegated functions.

## Dependencies and Integration Points
The file depends on DCN31 DIO mux APIs, DMUB services, connector speed VBIOS callbacks, GPIO, link encoder base helpers, and debug flags. It is reused by DCN321 and DCN401 for selected behavior.

## Risks and Test Signals
Risks include direct DP enable becoming a no-op when VBIOS execution is avoided, mandatory DMUB availability for alt-mode queries, and connector-speed-cap callback absence or failure. Tests should cover VBIOS and direct DP enable modes, connector speed table parsing, USB-C lane limiting, DMUB query failure fallback, HBR/UHBR capability advertisement, and transmitter mapping for A-E.
