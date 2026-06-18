# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h

## Purpose
Defines the DCN IPP register-map macros and concrete IPP structure used by DCN1/DCN2/DCN201 resource code.

## Important APIs, Types, And Functions
Macros `IPP_REG_LIST_DCN`, `IPP_REG_LIST_DCN10`, `IPP_REG_LIST_DCN20`, and `IPP_REG_LIST_DCN201` enumerate CNVC format and cursor registers with generation-specific naming differences. Mask/shift macros define fields for surface format, bypass/alpha/format expansion, legacy cursor color/control, cursor address/size/control/position/hotspot, destination offsets, and optional `OUTPUT_FP`. Types include `dcn10_ipp_registers`, shift/mask structs, and `struct dcn10_ipp`. Constructors for DCN10 and DCN20 are declared.

## Control Flow
No runtime flow. Macro expansion creates register maps consumed by resource constructors and IPP functions.

## State And Persistence
`struct dcn10_ipp` stores a common `input_pixel_processor`, register descriptors, and cached cursor attributes. Hardware state is represented by the cursor and CNVC registers listed here.

## Dependencies And Integration Points
Includes `ipp.h` and relies on AMD-generated register macros like `SRI` and `IPP_SF`. It bridges resource-specific register tables to the common IPP interface.

## Risks
Generation-specific spelling differences matter: DCN10 uses `CURSOR_SETTINS` while DCN20 uses `CURSOR_SETTINGS`, and DCN201 drops HUBPREQ cursor settings. Incorrect macro selection causes wrong register addresses. Manually defined cursor magnify shift/mask must match ASIC headers.

## Test Signals
Cursor enable/move tests, format-control programming tests, and build coverage for all generation-specific register-list macros detect drift.
