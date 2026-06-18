# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.c

## Purpose
Implements the DCN2.0.1 link encoder constructor and small USB-C/DP-alt-mode capability overrides on top of DCN10/DCN20 link-encoder behavior.

## Important APIs, Types, And Functions
`dcn201_link_encoder_get_max_link_cap()` calls the DCN10 max-cap helper, then limits lane count to two on USB-C combo PHY when DP alt-mode state indicates no DP4. `dcn201_link_encoder_is_in_alt_mode()` reads `RDPCS_PHY_DPALT_DISABLE` and returns true when alt mode is enabled. `dcn201_link_enc_funcs` mostly delegates to DCN10/DCN20 helpers, adding FEC support and DCN201 alt-mode/max-cap functions. `dcn201_link_encoder_construct()` initializes the encoder, reads VBIOS capability info, maps transmitters A/B to DIG engines, and applies debug HDMI 2.0 disable.

## Control Flow
Construction initializes base fields from `encoder_init_data`, assigns function table and register maps, sets supported output signals, maps only UNIPHY A/B to preferred DIG engines, defaults HDMI 6G on, queries VBIOS capabilities, copies HBR2/HBR3/HDMI/USB-C feature flags, logs on failure, then applies debug override. Capability query path reads DP alt-mode register fields after base capability calculation and clamps lanes when needed.

## State And Persistence
Persistent software state is the initialized `link_encoder` object fields and feature flags. Hardware state is read but not written by the DCN201-specific helpers in this file.

## Dependencies And Integration Points
Depends on DCN20 link-encoder structures, DCN10 link helpers, VBIOS capability callbacks, GPIO/HPD data, register helper macros, and stream encoder contracts. Integrated by DCN201 resource construction and link training paths.

## Risks
Only transmitters A and B are accepted; other transmitters assert and become unknown. Lane clamping depends on exact `RDPCSTX_PHY_CNTL2` bit semantics. VBIOS capability failure leaves defaults, which may overstate HDMI 6G until debug disables it.

## Test Signals
USB-C alt-mode lane-count tests, VBIOS capability read success/failure paths, HPD and link training on UNIPHY A/B, FEC readiness tests, and HDMI 2.0 debug override behavior.
