# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.c

## Purpose
This file implements the baseline DCN3 DIO link encoder. It constructs a `dcn20_link_encoder`/`dcn10_link_encoder` object with DCN30 function pointers, initializes AUX/TMDS hardware, advertises output signal support, maps transmitters to preferred DIG engines, and imports link capabilities from VBIOS.

## Important APIs and Functions
`dcn30_link_encoder_validate_output_with_stream` delegates stream validation to the DCN10 implementation. `dcn30_link_enc_funcs` mostly reuses DCN10/DCN20 operations, with DCN30-specific `enc3_hw_init`, FEC hooks from DCN2, and DP/HDMI capability accessors. `dcn30_link_encoder_construct` fills the base object, register pointers, HPD/AUX register blocks, output signals, preferred engine, feature flags, and VBIOS-derived capability bits. `enc3_hw_init` writes hard-coded AUX DPHY RX/TX control values, sets legacy `TMDS_CTL0`, and calls `dcn10_aux_initialize`.

## Control Flow
Construction is linear: copy initialization data, choose `preferred_engine` from the UNIPHY transmitter, set HDMI 6 Gb/s default true, query `get_encoder_cap_info`, overwrite HBR2/HBR3/HDMI/DP2/UHBR/USB-C feature bits if the BIOS query succeeds, then respect `debug.hdmi20_disable`. Hardware init programs AUX electrical timing before enabling the common AUX machinery.

## State and Persistence
The object persists feature capability state in `enc10->base.features`, register table pointers, connector/HPD identities, and preferred DIG routing. Runtime hardware state persists in AUX DPHY registers and `TMDS_CTL_BITS`.

## Dependencies and Integration Points
It depends on `reg_helper.h`, `core_types.h`, `link_encoder.h`, `stream_encoder.h`, `dc_bios_types.h`, GPIO service interfaces, DCN20 helpers, and VBIOS callbacks. Display Core uses the function table through `struct link_encoder_funcs` during mode set, DP training, MST allocation, HPD handling, FEC, PSR packets, and link capability evaluation.

## Risks and Test Signals
Primary risks are wrong transmitter-to-DIG mapping, stale VBIOS capability fields, and hard-coded AUX DPHY values that may not fit all boards. Tests should cover HDMI 2.0 disable override, HBR2/HBR3/UHBR capability advertisement, USB-C capability propagation, AUX transactions after init, HPD filtering, DP SST/MST enable/disable, FEC state, and kernel build coverage for all referenced function pointers.
