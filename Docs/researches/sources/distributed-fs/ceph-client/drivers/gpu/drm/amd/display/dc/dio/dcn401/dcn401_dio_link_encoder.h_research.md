# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_link_encoder.h

## Purpose
This header defines the DCN401 link encoder mask/shift surface and public constructor/setup/state APIs. It is a newer-generation backend register contract similar to DCN35 but with a smaller exported API.

## Important APIs, Types, and Macros
`LINK_ENCODER_MASK_SH_LIST_DCN401(mask_sh)` maps DIG backend enable/control/clock fields, DP DPHY PRBS/symbol/scrambler/training fields, DP link/framing/stream/MST fields, AUX and HPD fields, and FEC state. It provides the fields used by DCN401 setup, state readback, AUX init, and inherited link operations.

The header declares `dcn401_link_encoder_construct`, `enc401_hw_init`, `dcn401_link_encoder_enable_dp_output`, `dcn401_link_encoder_setup`, `dcn401_get_dig_mode`, and `dcn401_is_dig_enabled`. `dcn401_get_dig_mode` is declared twice, which is harmless in C but noisy.

## Control Flow and State
No executable flow is present. Declared functions program backend clock/enable/mode, AUX DPHY, DP output, and object feature state in the C implementation.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h` and the C implementation composes DCN31 and DCN32 behavior. Resource construction and link function-table setup depend on this signature.

## Risks and Test Signals
Risks include mask drift for backend enable/clock fields, duplicate prototype maintenance, and missing fields compared with DCN35 if shared code expands. Test signals include compile coverage, backend mode setup, DP/HDMI/DVI/MST operation, FEC status, HPD/AUX operation, and DCN32 USB-C alt-mode integration.
