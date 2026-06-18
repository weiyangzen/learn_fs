# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.c

## Purpose
Implements DCN42 link encoder construction and the small DCN42-specific HPD operations. It wires a DCN42 `link_encoder` to mostly inherited DCN35/DCN32/DCN31/DCN10 behavior while adding HPD sense/filter callbacks and DP2/UHBR capability setup from VBIOS connector speed caps.

## Important APIs, Types, And Functions
`dcn42_link_encoder_construct()` fills a `struct dcn20_link_encoder`/`struct dcn10_link_encoder` with context, ids, connector, HPD, transmitter, feature flags, register tables, and preferred DIG engine. `dcn42_get_hpd_state()` reads `DC_HPD_INT_STATUS.DC_HPD_SENSE`. `dcn42_program_hpd_filter()` writes connect/disconnect filter delays to `DC_HPD_TOGGLE_FILT_CNTL`. The static `dcn42_link_enc_funcs` table selects inherited functions for init, setup, TMDS/DP/MST/DPIA enablement, lane programming, FEC, PHY muxing, HPD enable/disable, validation, and destruction.

## Control Flow
Construction sets default feature data, marks USB-C connectors as DP over USB-C, maps `TRANSMITTER_UNIPHY_A` through `E` to preferred DIG engines, defaults HDMI 6 Gb/s support on, then optionally overrides link capability flags from VBIOS `get_connector_speed_cap_info()`. On success it sets HBR2/HBR3, HDMI 6Gb, DP2, and UHBR10/13.5/20 flags. On VBIOS failure it logs a warning and keeps defaults. A debug flag can force HDMI 2.0/6Gb support off.

## State And Persistence
The file stores persistent state only in the live link encoder object. HPD operations read/write hardware registers and return immediate results. Capability data persists in `enc10->base.features` for later validation and mode/link training decisions.

## Dependencies And Integration Points
The implementation depends on `reg_helper.h`, `core_types.h`, common link encoder interfaces, DCN35 inherited functions, DCN401 `get_dig_mode`, and VBIOS connector speed capability callbacks. It is constructed by DCN42 resource code and used by link detection, mode validation, link training, MST allocation, FEC, DPIA, and HPD paths.

## Risks
Capability correctness depends on VBIOS data; failure leaves DP2/UHBR flags at defaults except HDMI debug override. The transmitter-to-DIG mapping asserts on unexpected transmitters. HPD filter delay units must match register expectations. Since most behavior is inherited, signature or semantic changes in older DCN helper functions can affect DCN42 without changes in this file.

## Test Signals
Useful tests include build coverage of the function table, hotplug sense/filter behavior, connector capability reporting for HDMI/DP2/UHBR links, mode validation against VBIOS caps, successful link training across TMDS, DP SST/MST, and DPIA paths, and HDMI 2.0 disable debug behavior.
