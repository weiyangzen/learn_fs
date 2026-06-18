# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_sh_mask.h

## Purpose
This generated header defines field shifts and masks for UMC 12.0.0 ECC counter and MCA registers. It lets AMDGPU RAS code select ECC counter behavior, extract counter overflow state, classify MCA status, and read error addresses without hard-coded bit arithmetic in C files.

## Important APIs, Types, and Functions
The interface is macro-only. `UMCCH0_OdEccCntSel__OdEccCntSel` selects the ECC counter source and `UMCCH0_OdEccCntSel__OdEccErrInt` selects the error interrupt type. `UMCCH0_OdEccErrCnt__Cnt`, `CntOvr`, and `OvrClr` describe the counter value, overflow flag, and overflow clear bit. `MCA_UMC_UMC0_MCUMC_STATUST0` exposes 64-bit MCA fields such as `ErrorCode`, `ErrorCodeExt`, `AddrLsb`, `ErrCoreId`, `Scrub`, `Poison`, `Deferred`, `UECC`, `CECC`, `TCC`, `PCC`, `AddrV`, `UC`, `Overflow`, and `Val`. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit `ErrorAddr`.

## Control Flow
The header has no control flow. `amdgpu/umc_v12_0.c` uses the masks in classification helpers. `umc_v12_0_is_deferred_error()` checks `Val`, `Poison`, and `Deferred`; `umc_v12_0_is_uncorrectable_error()` checks `PCC`, `UC`, and `TCC`; `umc_v12_0_is_correctable_error()` checks `CECC`, selected `UECC` cases, and replay-mode `ErrorCodeExt` values. Address query code extracts `MCUMC_ADDRT0.ErrorAddr` before platform-specific address translation.

## State and Persistence Behavior
No state is stored by the header. The bitfields describe hardware state that persists until firmware or the driver clears it. MCA `Val`, `Overflow`, and error-type bits act as latches for RAS handling. `OdEccErrCnt` accumulates correctable-event count state and can signal overflow.

## Dependencies and Integration Points
It pairs with `umc_12_0_0_offset.h` and is consumed by `amdgpu/umc_v12_0.c`, AMDGPU RAS helpers, SMUIO topology helpers, and register helper macros `REG_GET_FIELD` and `REG_SET_FIELD`. The field naming must match those helper conventions exactly.

## Risks
These fields drive RAS severity decisions. A wrong status mask can misclassify deferred poison as uncorrectable, treat uncorrectable memory faults as correctable, or skip address translation. The address mask intentionally covers only low 56 bits; consumers must not infer high reserved bits as address bits. Counter overflow handling depends on the `CntOvr` and `OvrClr` positions matching hardware.

## Test Signals
Unit-style compile coverage comes from building UMC v12.0 RAS code. Hardware or emulation tests should inject correctable, uncorrectable, deferred, poison, replay-mode parity, and overflow cases, then confirm `ce_count`, `ue_count`, `de_count`, error-address records, and register clearing match expectations.
