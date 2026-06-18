# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h

## Purpose
Defines DCN2 writeback controller register maps, field maps, concrete object layout, and exported helper prototypes.

## Important APIs, Types, And Functions
`DWBC_COMMON_REG_LIST_DCN2_0` lists CNV, WBSCL, debug, CRC, coefficient RAM, clamp, warmup, and soft-reset registers. `DWBC_COMMON_MASK_SH_LIST_DCN2_0` and `DWBC_REG_FIELD_LIST_DCN2_0` define fields used by DWB/CNV/WBSCL operations. Types include `dcn20_dwbc_registers`, `dcn20_dwbc_mask`, `dcn20_dwbc_shift`, and `dcn20_dwbc`. Prototypes expose constructor, DWB controls, CNV/scaler setup, and the horizontal/vertical scaler programming functions.

## Control Flow
No executable flow. The header creates the structural contract that `dcn20_dwb.c` and `dcn20_dwb_scl.c` use for register accesses.

## State And Persistence
`struct dcn20_dwbc` stores the base `dwbc` and constant register descriptor pointers. Runtime state is held in hardware registers defined by the macros.

## Dependencies And Integration Points
Relies on DWB-specific register-address macros such as `SRI2_DWB` and `SF_DWB`, plus common DWB parameter types. Used by DCN2 resource code and possibly later generations that reuse DCN20 writeback functions.

## Risks
Large macro lists make field drift likely when ASIC headers change. Optional coefficient-RAM fields are included in the field list and must be valid for callers that test/use them. Function prototypes expose scaler helpers that assume valid tap counts and dimensions.

## Test Signals
Compile coverage across ASIC register headers, writeback scaler programming tests, and register dumps confirming mask/shift alignment with hardware fields.
