# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_1_2_sh_mask.h

## Purpose
This generated header defines Arcturus-named UMC 6.1.2 field shifts and masks for ECC counter and MCA status/address registers. It is the `_ARCT` counterpart to the UMC 6.1.1 sh/mask file.

## Important APIs, Types, and Functions
The macro families mirror UMC 6.1.1 with `_ARCT` register prefixes. `UMCCH0_0_EccErrCntSel_ARCT` fields include `EccErrCntCsSel`, `EccErrInt`, and `EccErrCntEn`. `UMCCH0_0_EccErrCnt_ARCT__EccErrCnt` exposes the 16-bit ECC counter. `MCA_UMC_UMC0_MCUMC_STATUST0_ARCT` exposes MCA status fields including `ErrorCode`, `ErrorCodeExt`, `ErrCoreId`, `Poison`, `Deferred`, `UECC`, `CECC`, `TCC`, `PCC`, `AddrV`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0_ARCT` exposes `ErrorAddr`, `LSB`, and reserved bits.

## Control Flow
The header itself has no control flow. In this tree, `amdgpu/umc_v6_1.c` includes the Arcturus offset header but not this sh/mask header, so current code relies on 6.1.1 field macros against Arcturus offsets. This file documents the equivalent `_ARCT` names that would be used if the C path were switched to fully Arcturus-prefixed field extraction.

## State and Persistence Behavior
The file stores no software state. Its fields describe persistent hardware selector, counter, status, and address state. The semantics match the RAS path: select chip side, read or initialize counters, classify MCA status, extract low-significant-bit information, and clear status after processing.

## Dependencies and Integration Points
It pairs with `umc_6_1_2_offset.h`. It is generated to fit AMD register helper conventions but is currently an integration reserve or documentation-equivalent surface because the C file uses 6.1.1 sh/mask names. Any future consumer would use `REG_GET_FIELD` and `REG_SET_FIELD` with the `_ARCT` register prefixes.

## Risks
Dead or unused generated headers can drift from real call sites. If a developer includes this file and mixes `_ARCT` and non-`_ARCT` field names, macro lookup or field interpretation can break. The risk is especially high around `LSB` and RAS classification bits because address retirement and error severity depend on exact positions.

## Test Signals
Compile a path that includes this header with `_ARCT` field names to ensure macro naming is complete. On Arcturus hardware, compare field positions against the 6.1.1 macros currently used by `umc_v6_1.c`, then validate CE/UE/deferred injection, address extraction, and status clearing.
