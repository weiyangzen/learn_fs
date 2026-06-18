# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_1_sh_mask.h

## Purpose
This generated header defines shifts and masks for UMC 6.1.1 ECC counter and MCA status/address fields. It provides the field names used by `amdgpu/umc_v6_1.c` to configure ECC counting, accumulate correctable and uncorrectable error counts, and decode error addresses.

## Important APIs, Types, and Functions
`UMCCH0_0_EccErrCntSel__EccErrCntCsSel` selects lower or upper chip counter source, `EccErrInt` selects the interrupt type, and `EccErrCntEn` enables counting. `UMCCH0_0_EccErrCnt__EccErrCnt` exposes the 16-bit count. `MCA_UMC_UMC0_MCUMC_STATUST0` exposes MCA fields such as `ErrorCode`, `ErrorCodeExt`, `ErrCoreId`, `Poison`, `Deferred`, `UECC`, `CECC`, `TCC`, `PCC`, `AddrV`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes `ErrorAddr`, `LSB`, and reserved bits.

## Control Flow
The header has no runtime branches, but its fields drive `umc_v6_1.c`. Counter clear and initialization paths write `EccErrCntCsSel` for lower and higher chips and set `EccErrInt`. Correctable-error queries read `EccErrCnt`, subtract the initial count, and add one extra SRAM CE when `ErrorCodeExt == 6`, `Val == 1`, and `CECC == 1`. Uncorrectable-error queries check `Val` and any of `Deferred`, `UECC`, `PCC`, `UC`, or `TCC`. Address query checks `Val` and `UECC`, extracts `LSB` and `ErrorAddr`, masks low address bits, then builds a retired page address from channel and offset fields.

## State and Persistence Behavior
No software state lives here. Hardware counter and MCA status bits persist until the RAS path clears or reinitializes them. `EccErrCntCsSel` is a selector state, so reads of `EccErrCnt` depend on the last selected chip. MCA status is cleared by writing zero after address processing.

## Dependencies and Integration Points
It pairs with `umc_6_1_1_offset.h`. It is also used for field extraction in the Arcturus path because `umc_v6_1.c` includes `umc_6_1_2_offset.h` but not the `_ARCT` sh/mask header, relying on equivalent field layouts and non-ARCT field names for `REG_GET_FIELD` and `REG_SET_FIELD`.

## Risks
Correct RAS severity depends on these bit positions. Wrong `LSB` handling can retire the wrong page. Wrong `EccErrCntCsSel` fields can double count or miss one chip side. The shared use of 6.1.1 field names for 6.1.2-style offsets makes layout compatibility a critical assumption.

## Test Signals
Inject or simulate CE, UE, deferred, PCC, UC, and TCC conditions. Verify lower/higher chip counter accounting, SRAM CE detection, MCA status clearing, and error-address translation. Build tests should catch naming mismatches in `REG_GET_FIELD` and `REG_SET_FIELD`.
