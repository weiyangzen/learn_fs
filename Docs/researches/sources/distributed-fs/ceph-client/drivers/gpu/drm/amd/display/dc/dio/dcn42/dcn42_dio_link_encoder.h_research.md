# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_link_encoder.h

## Purpose
Declares the DCN42 link encoder register field list and the DCN42 construction/HPD entry points. It adapts the DCN401 link encoder register model for DCN42 and exposes HPD callbacks implemented in the C file.

## Important APIs, Types, And Functions
`LINK_ENCODER_MASK_SH_LIST_DCN42(mask_sh)` enumerates DIG backend, DP DPHY, link framing, MST SAT, AUX, HPD, FEC, DIO clock-gating, and HDCP-related fields required by inherited link encoder helpers. The header declares `dcn42_link_encoder_construct()`, `dcn42_get_hpd_state()`, and `dcn42_program_hpd_filter()`.

## Control Flow
There is no runtime flow in the header. The macro expands during register table construction, and the declared constructor installs the function table that drives runtime behavior.

## State And Persistence
No state is stored in this file. It defines compile-time access to register fields; the C implementation persists state in `struct dcn10_link_encoder` and hardware registers.

## Dependencies And Integration Points
The header includes `dcn401/dcn401_dio_link_encoder.h`, inheriting base register and type definitions. DCN42 resource code uses the constructor declaration when creating link encoders. The macro must align with generated register headers for DIG, DP, AUX, HPD, FEC, and DIO clock registers.

## Risks
Register field drift is the main risk. A missing or incorrect field breaks compilation or misprograms inherited helper routines. The broad macro includes clock-gating and HDCP clock fields, so errors can cause subtle link bring-up, FEC, AUX, HPD, or power-gating regressions.

## Test Signals
Compilation with DCN42 enabled validates register names and function declarations. Runtime coverage should exercise HPD, AUX, DP training, MST allocation, FEC enable/ready/active paths, TMDS setup, DPIA output, and DIO clock-gating behavior.
