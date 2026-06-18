# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn314/dcn314_optc.h

## Purpose
Provides DCN 3.14 OPTC register and field metadata plus the timing-generator init prototype. It adapts the DCN31 register model to DCN314 by defining the exact register list and mask/shift expansion needed by the DCN314 resource tables.

## Important APIs, Types, and Macros
`OPTC_COMMON_REG_LIST_DCN3_14(inst)` lists OTG timing/update-lock/status, ODM input/memory/format, VTG, GSL, CRC, DSC, DRR, pipe update, and interrupt destination registers. `OPTC_COMMON_MASK_SH_LIST_DCN3_14(mask_sh)` supplies the field names used by `REG_GET/SET/UPDATE`, including `OTG_CURRENT_MASTER_EN_STATE` absence compared with some newer headers, ODM segment fields, `OTG_H_TIMING_DIV_MODE_MANUAL`, and pipe update status fields. The only prototype is `dcn314_timing_generator_init()`.

## Control Flow and State
The header only defines compile-time register tables. Its state behavior is indirect: it controls which fields the DCN314 implementation can persist into hardware registers and which readback/update paths can be wired into the vtable.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h`. The DCN314 implementation relies on this header, while resource construction supplies generated arrays using these macro expansions. Shared helper functions from DCN10/DCN20/DCN30/DCN31 assume these masks are consistent with the fields they access.

## Risks and Test Signals
The main risk is mismatch between this register contract and the ASIC register headers. Build failures catch missing symbols, but incorrect field selection can surface only as timing, ODM, CRC, DRR, or interrupt malfunction. Regression signals include successful compilation for DCN314 configs and hardware mode-set/VRR/CRC tests.
