# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_7_0_offset.h

## Purpose

`umc_8_7_0_offset.h` is the generated UMC 8.7.0 register-offset header for GECC counters and MCA UMC error-reporting registers. It uses the `mm*` address macro style rather than the `reg*` style used by the later UMC 8.10.0 and 8.14.0 headers in this work item.

## Important APIs, Types, And Macros

The header exports `mmUMCCH0_0_GeccErrCntSel`, `mmUMCCH0_0_GeccErrCnt`, `mmMCA_UMC_UMC0_MCUMC_STATUST0`, and `mmMCA_UMC_UMC0_MCUMC_ADDRT0`, with `_BASE_IDX` values of `0`. There is no `GeccCtrl` offset in this version-specific file.

## Control Flow And Data Flow

No code executes here. Consumers use these addresses with `umc_8_7_0_sh_mask.h` to select GECC counter sources, sample corrected/uncorrected counts, decode MCA status, and read the MCA error address when RAS or machine-check reporting indicates a UMC error.

## State And Persistence Behavior

The macros do not store software state. They name hardware latches and counters that persist until cleared, reset, or overwritten by new hardware events. The base-index value is part of the access path and is therefore important state-routing metadata for register helpers.

## Dependencies And Integration Points

This file integrates with AMDGPU UMC 8.7.0 RAS handling, memory error interrupt/reporting code, and MMIO helpers that understand `mm*` offsets and base indexes. It should be paired with `umc_8_7_0_sh_mask.h`.

## Risks And Test Signals

Risks include confusing `mm*` and `reg*` naming families, using the wrong base index, and assuming the later `GeccCtrl` fatal-enable field exists. Tests should include build coverage for UMC 8.7.0, ECC injection/readout, MCA address decode validation, and generated-offset comparison.
