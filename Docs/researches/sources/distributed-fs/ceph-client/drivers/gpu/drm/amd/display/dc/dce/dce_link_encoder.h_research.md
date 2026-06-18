# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_link_encoder.h

## Purpose
This header declares the DCE110 link encoder object, its register table schemas, generation-specific register-list macros, and all public link encoder operations implemented in `dce_link_encoder.c`. It is the contract between resource construction code and the DCE link encoder backend.

## Important APIs, Types, and Macros
`TO_DCE110_LINK_ENC()` casts from abstract `struct link_encoder`. Register list macros split AUX, HPD, and link/DIG/DP/DMCU/DAC blocks: `AUX_REG_LIST()`, `HPD_REG_LIST()`, `LE_COMMON_REG_LIST_BASE()`, `LE_COMMON_REG_LIST()`, `LE_DCE60_REG_LIST()`, `LE_DCE80_REG_LIST()`, `LE_DCE100_REG_LIST()`, `LE_DCE110_REG_LIST()`, and `LE_DCE120_REG_LIST()`. `struct dce110_link_enc_registers` includes DMCU, DIG, DP, MST, security packet, DPHY, and DAC registers; separate structs describe AUX and HPD register subsets. Public APIs cover construct/destroy, output validation, hardware init, setup, enable/disable for TMDS/DP/MST/LVDS/analog, DP lane settings, DP PHY patterns, MST SAT updates, DIG FE/BE connection, HPD, PSR helpers, max link caps, and HPD filtering.

## Control Flow and State
This header does not execute code. It shapes runtime by deciding which registers are present for each DCE generation and by exposing operations used by the common DC link layer. The concrete object stores pointers to static register tables while the base object stores connector, transmitter, engine, feature, and GPIO state.

## Dependencies and Integration Points
It depends on `link_encoder.h` for base types and signal/link settings, on generated register macros supplied by including compilation units, and on DC BIOS/link infrastructure. Consumers include resource pool builders and DCE generation files that instantiate register tables and call the constructors.

## Risks and Test Signals
Risk centers on register-list correctness. DCE120 omits `DP_DPHY_INTERNAL_CTRL`, while older generations include DAC or HBR2 pattern registers selectively; mismatches cause build errors or runtime writes to invalid addresses. API-level tests are compile coverage for all generation macros, construction smoke tests for HPD and no-HPD instances, and link bring-up validation across connector types.
