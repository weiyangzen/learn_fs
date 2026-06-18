# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn35/dcn35_dio_link_encoder.h

## Purpose
This header defines the DCN35 link encoder mask/shift surface and public API for new DIG backend clock/mode control, FGC gating, DP enable/disable, and DPIA output.

## Important APIs, Types, and Macros
`LINK_ENCODER_MASK_SH_LIST_DCN35(mask_sh)` maps DIG backend enable/control/clock fields, DP DPHY PRBS/symbol/scrambler/training fields, DP link/framing/stream/MST fields, AUX/HPD fields, FEC fields, DIO link HPO selection, and DIO clock gating fields. It is a large replacement-style mask list for the newer DCN35 backend register model.

Public APIs include constructor, init, `dcn35_link_encoder_set_fgcg`, `dcn35_is_dig_enabled`, `dcn35_get_dig_mode`, setup, DP SST/MST enable, output disable, and DPIA enable/disable.

## Control Flow and State
No executable flow is in the header. Declared functions modify DIG backend mode/clock, DP output state, DPIA state through DMUB, DIO clock gating, and link encoder object capabilities.

## Dependencies and Integration Points
The header includes DCN32, DCN30, and DCN31 link encoder headers, reflecting that DCN35 composes behavior from all three generations.

## Risks and Test Signals
Risk is high for mask drift because this header touches backend clocking, FEC, MST, AUX, HPD, HPO selection, and clock gating. Test signals include build coverage, DP/HDMI/DVI mode setup, HPD/AUX operation, FEC ready/active status, MST SAT programming, DIO FGC gating, and DPIA enable/disable through function-table hooks.
