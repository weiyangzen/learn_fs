# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_sh_mask.h

## Purpose

`umc_8_7_0_sh_mask.h` is the generated UMC 8.7.0 bitfield header. It defines masks and shifts for GECC counter selection, GECC count values, MCA UMC status, and MCA UMC address reporting. It is hardware description data with no functions or mutable variables.

## Important APIs, Types, And Macros

The `UMCCH0_0_GeccErrCntSel` field set includes `GeccErrCntCsSel`, `GeccErrInt`, `GeccErrCntEn`, and `PoisonCntEn`; the chip-select selector is a notable difference from UMC 8.10.0. `UMCCH0_0_GeccErrCnt` again provides corrected and uncorrectable 16-bit counters. `MCA_UMC_UMC0_MCUMC_STATUST0` defines the 64-bit MCA status layout, including error code, address LSB, core ID, scrub, poison, deferred, UECC/CECC, syndrome-valid, TCC, PCC, address/misc valid, enable, uncorrected, overflow, and valid fields. `MCA_UMC_UMC0_MCUMC_ADDRT0` exposes a 56-bit error address plus a six-bit `LSB` field and two reserved high bits.

## Control Flow And Data Flow

Consumer control flow is external: configure the counter selector, read counts, then decode MCA status/address when an event is latched. Address reconstruction may require combining `ErrorAddr`, `LSB`, and status `AddrLsb`, depending on the consuming RAS path and hardware documentation.

## State And Persistence Behavior

The header is stateless, but the hardware fields represent persistent counters, status latches, validity flags, and address state. Overflow and valid bits are especially important because they determine whether the current report is complete or whether events were lost.

## Dependencies And Integration Points

It pairs with `umc_8_7_0_offset.h` and integrates with AMDGPU RAS, MCA decoding, UMC error count reporting, memory poison handling, and reset/recovery paths. Consumers need 64-bit-safe access for the MCA status/address masks.

## Risks And Test Signals

Risks include dropping the `GeccErrCntCsSel` dimension, ignoring the `LSB` address field, reading 64-bit MCA registers through 32-bit-only helpers, or writing reserved bits. Test signals include CE/UE injection on multiple chip-selects, address reconstruction checks, overflow handling, and register-generation diffs.
