# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c

## Purpose
This file implements the DCN321 link encoder variant. It combines DCN32 AUX/DP enable behavior with older DCN20 USB-C alt-mode/max-link helpers and connector-speed capability import.

## Important APIs and Functions
`dcn321_link_enc_funcs` uses `enc32_hw_init`, `dcn32_link_encoder_enable_dp_output`, DCN31 DIO PHY mux, common DCN10/DCN20 link operations, FEC hooks, and DCN20 alt-mode/max-link-cap functions. `dcn321_link_encoder_construct` initializes the base link encoder object and imports connector speed capability data from VBIOS.

## Control Flow
Construction sets USB-C feature state when the connector id is USB-C before copying `*enc_features`, then copies init fields, selects preferred engine for transmitters A-E, sets HDMI 6 Gb/s default true, queries `get_connector_speed_cap_info`, imports HBR2/HBR3/HDMI/UHBR flags, forces `IS_DP2_CAPABLE = 1`, and applies `debug.hdmi20_disable`.

## State and Persistence
Persistent state includes feature flags, connector and HPD metadata, transmitter/preferred DIG mapping, register and mask tables, and connector-speed capability bits. Runtime hardware state is handled by delegated DCN32/DCN20/DCN10 functions.

## Dependencies and Integration Points
It depends on DCN321 header, DCN31/32 link helpers, common link encoder contracts, VBIOS connector speed callbacks, and GPIO types. It integrates into resource construction for DCN321 ASICs.

## Risks and Test Signals
A notable risk is ordering: the USB-C `DP_IS_USB_C` bit is set before `enc10->base.features = *enc_features`, so the assignment may overwrite it unless `enc_features` already carries the bit. Tests should check USB-C feature propagation, DP Alt Mode behavior using DCN20 helpers, connector speed capability import, DP2/UHBR flags, HDMI disable override, and A-E transmitter mapping.
