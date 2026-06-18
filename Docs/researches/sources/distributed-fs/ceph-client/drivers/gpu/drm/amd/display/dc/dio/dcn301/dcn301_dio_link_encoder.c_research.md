# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c

## Purpose
This file implements a DCN301 link encoder variant. It is structurally close to DCN30 but uses a distinct function table and a narrower VBIOS feature import path.

## Important APIs and Functions
`dcn301_link_enc_funcs` wires common DCN10/DCN20 operations, `enc3_hw_init`, FEC hooks, DCN20 alt-mode and max-link-cap helpers, HPD operations, and DPCD/PSR helpers. `dcn301_link_encoder_construct` initializes the base object, output signal mask, register pointers, transmitter-to-DIG preferred engine mapping, HDMI default capability, and VBIOS capability overrides.

## Control Flow
Construction copies init fields, sets `preferred_engine` for UNIPHY A-G, sets HDMI 6 Gb/s true by default, calls `get_encoder_cap_info`, then imports only HBR2, HBR3, HDMI 6 Gb/s, and USB-C capability bits. It does not import DP2/UHBR fields like DCN30. The debug `hdmi20_disable` flag clears HDMI 6 Gb/s after VBIOS parsing.

## State and Persistence
The persistent object state is the same base link encoder structure: context, encoder id, HPD/connector identities, feature flags, transmitter, preferred engine, and register/mask pointers. Hardware init is delegated to DCN30 `enc3_hw_init`.

## Dependencies and Integration Points
The implementation depends on DCN301 header definitions, DCN20/DCN10 link helpers, VBIOS functions, GPIO, and the shared `link_encoder_funcs` interface. It integrates into display resource construction for DCN301 ASICs.

## Risks and Test Signals
The main risk is capability skew from DCN30 because DP2/UHBR bits are intentionally absent in the VBIOS import. Tests should validate connector capability reporting, HDMI 6 Gb/s disable, AUX init through `enc3_hw_init`, DP SST/MST operation, FEC, HPD, and all expected DCN301 board transmitters.
