# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn31/dcn31_optc.h

## Purpose
Defines the DCN 3.1 OPTC register list, field shift/mask list, and public entry points consumed by DCN31 resource construction and later generation OPTC implementations. It is a hardware contract header rather than an algorithmic module.

## Important APIs, Types, and Macros
`OPTC_COMMON_REG_LIST_DCN3_1(inst)` maps the OTG, ODM, VTG, GSL, CRC, DSC, DWB, DRR, and interrupt registers for one OPTC instance. `OPTC_COMMON_MASK_SH_LIST_DCN3_1(mask_sh)` enumerates field masks and shifts needed by `reg_helper` calls, including update locks, timing registers, CRC windows, GSL, DSC format, ODM segment source fields, memory selection, DRR trigger windows, and update-pending fields. Public prototypes export `dcn31_timing_generator_init()`, `optc31_immediate_disable_crtc()`, `optc31_set_drr()`, `optc3_init_odm()`, `optc31_read_otg_state()`, and `optc31_read_reg_state()`.

## Control Flow and State
The header has no runtime control flow. Its state significance is the fixed mapping between generated ASIC register names and the `struct optc` register/shift/mask tables. Consumers rely on these macro expansions to populate static register tables; if a field is missing here, code paths reading or writing it will either fail to compile or silently use an incompatible generation-specific table.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h` for base OPTC types, register-table structures, and shared function prototypes. DCN314, DCN32, DCN35, DCN401, and DCN42 implementation files reuse functions declared here, especially DRR and readback helpers. Resource generation code pairs this header's lists with ASIC-specific register definitions.

## Risks and Test Signals
Primary risk is register drift: wrong field names, duplicate register entries, or omitted masks can corrupt timing, CRC, ODM, or update-lock behavior. Build coverage catches many issues through macro expansion. Runtime signals include successful mode-set, CRC capture, DRR, GSL, DSC, and interrupt programming on DCN31 hardware.
