# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.h

## Purpose
This compact header declares the DCN32 link encoder public API. Unlike earlier generation headers, it does not add a large register-list macro; it reuses DCN30/DCN31 register contracts.

## Important APIs
The header declares `dcn32_link_encoder_construct`, `enc32_hw_init`, `dcn32_link_encoder_enable_dp_output`, `dcn32_link_encoder_is_in_alt_mode`, and `dcn32_link_encoder_get_max_link_cap`.

## Control Flow and State
Control flow is implemented in the C file. The APIs affect AUX init, DP output enable, object construction, and USB-C lane capability state. Persistent state is the underlying `dcn20_link_encoder`/`dcn10_link_encoder` object and hardware registers.

## Dependencies and Integration Points
It includes `dcn30/dcn30_dio_link_encoder.h` and is included by DCN321, DCN35, and DCN401 code that reuse DCN32 behavior or type declarations.

## Risks and Test Signals
The header risk is API drift: DCN321/DCN401 depend on these prototypes. Test signals include all dependent ASIC builds, DMUB alt-mode query linkage, DP output function-table binding, and constructor signature consistency with resource code.
