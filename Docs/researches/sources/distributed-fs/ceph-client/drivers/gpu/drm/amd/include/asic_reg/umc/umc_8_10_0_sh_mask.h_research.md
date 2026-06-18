# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_10_0_sh_mask.h

## Purpose

`umc_8_10_0_sh_mask.h` is the generated field-layout companion for UMC 8.10.0 offsets. It defines bit masks and shifts used to encode or decode GECC counter control, GECC counter values, MCA UMC status, MCA error address, and GECC fatal-error control. It has no functions, structs, or runtime data.

## Important APIs, Types, And Macros

For `UMCCH0_0_GeccErrCntSel`, the header exposes interrupt selection, GECC counter enable, and poison counter enable fields. `UMCCH0_0_GeccErrCnt` splits the register into 16-bit corrected and uncorrectable GECC counts. `MCA_UMC_UMC0_MCUMC_STATUST0` is a 64-bit status map with error code, extended code, address LSB, error core ID, scrub/poison/deferred flags, UECC/CECC classification, syndrome-valid, TCC, PCC, address/misc valid, enabled, uncorrected, overflow, and valid bits. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit error address. `UMCCH0_0_GeccCtrl__UCFatalEn` controls fatal treatment for uncorrectable errors.

## Control Flow And Data Flow

Consumers typically write `GeccErrCntSel` fields to select and enable an error counter, read `GeccErrCnt`, then read `STATUST0` and `ADDRT0` when a memory error is reported. Data flows from hardware MCA latches into driver RAS decoding. Status bits gate interpretation: the driver should treat address and misc fields as meaningful only when validity fields are set and should handle overflow as evidence of lost events.

## State And Persistence Behavior

The header itself is stateless. The described hardware state is persistent until cleared or reset: counters accumulate, MCA status latches error classification, address registers retain the reported physical address, and `UCFatalEn` changes future fault handling. Incorrect writes can persist until driver recovery or GPU reset.

## Dependencies And Integration Points

It is paired with `umc_8_10_0_offset.h`; offsets without these masks cannot be decoded safely. Integration points include AMDGPU RAS interrupt/report paths, sysfs/debugfs error count reporting, memory poison handling, GPU reset decision logic, and ASIC-specific UMC helpers.

## Risks And Test Signals

The main risks are 64-bit field truncation, using 32-bit helpers for MCA status, treating reserved fields as writable, and assuming address validity without checking `AddrV`. Test signals include ECC injection, poison event handling, CE/UE classification checks, validation that 16-bit counter fields do not bleed into each other, and register-generation diffs against AMD's canonical UMC 8.10.0 data.
