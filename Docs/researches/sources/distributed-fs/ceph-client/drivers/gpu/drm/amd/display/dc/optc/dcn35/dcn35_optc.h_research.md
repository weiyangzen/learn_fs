# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h

## Purpose
Defines DCN3.5 and DCN3.6 OPTC field extensions over the DCN3.2 baseline and declares DCN35 public timing-generator helpers.

## Important APIs, Types, and Macros
`OPTC_COMMON_MASK_SH_LIST_DCN3_5(mask_sh)` composes `OPTC_COMMON_MASK_SH_LIST_DCN3_2()` and adds CRC window double-buffering, CRC engine 1-3 legacy result fields, CRC window readback fields, `OPTC_FGCG_REP_DIS`, long-vtotal stop-control fields, and additional pipe update status fields. `OPTC_COMMON_MASK_SH_LIST_DCN3_6(mask_sh)` further adds CRC polynomial selection and 32-bit CRC result fields. Prototypes expose init, fine-grain clock gating, DRR, long-vtotal, CRC configuration, and OTG-disable wait helpers.

## Control Flow and State
The header has no runtime flow. It defines the hardware state surface that DCN35 code can access: CRC windows/results, clock gating, and long vertical-total counters. These fields directly affect display validation and debug behavior because the implementation checks mask presence before enabling newer CRC paths.

## Dependencies and Integration Points
Includes `dcn10/dcn10_optc.h` and `dcn32/dcn32_optc.h`. DCN42 reuses `optc35_configure_crc()`, `optc35_set_long_vtotal()`, and `dcn35_timing_generator_set_fgcg()` while supplying a different field list.

## Risks and Test Signals
Risk is mainly feature-flag drift: fields added to the macro imply hardware support that implementation paths may use. Tests should compile DCN35/DCN36 style tables and run CRC window, CRC32, long-vtotal, and FGC clock-gating scenarios.
