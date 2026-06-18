# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_sh_mask.h

## Purpose

`umc_8_14_0_sh_mask.h` defines field masks and shifts for the two UMC 8.14.0 GECC counter registers exported by the offset header. It is generated hardware ABI data, not executable driver logic.

## Important APIs, Types, And Macros

`UMCCH0_GeccErrCntSel` exposes `GeccErrInt`, `GeccErrCntEn`, and `PoisonCntEn` fields. `UMCCH0_GeccErrCnt` exposes a low 16-bit `GeccErrCnt` field and high 16-bit `GeccUnCorrErrCnt` field. There are no MCA status, MCA address, or GECC fatal-control fields in this file.

## Control Flow And Data Flow

Driver code writes selector fields to enable and choose GECC/poison counting, then reads the count register and masks/shifts the two 16-bit counters. The absence of MCA fields means detailed error classification and address decoding must come from another block, another header, firmware, or generation-specific code outside this file.

## State And Persistence Behavior

The macros are stateless. The hardware fields describe persistent counter-enable state and counter values. Counter state may accumulate across ordinary driver activity and should be reset, sampled, or latched according to UMC/RAS sequencing outside this header.

## Dependencies And Integration Points

It pairs with `umc_8_14_0_offset.h`. Consumers include AMDGPU RAS and UMC helpers that need GECC counter reporting on UMC 8.14.0 ASICs. The symbols intentionally differ from the `UMCCH0_0_*` names used by earlier versions.

## Risks And Test Signals

Risks include stale consumer code referencing older macro names, accidental use of UMC 8.10.0 masks against UMC 8.14.0 offsets, and misinterpreting the two adjacent 16-bit fields. Test signals are build coverage for UMC 8.14.0, GECC counter readback, poison-count enable checks where supported, and generated-header diffing.
