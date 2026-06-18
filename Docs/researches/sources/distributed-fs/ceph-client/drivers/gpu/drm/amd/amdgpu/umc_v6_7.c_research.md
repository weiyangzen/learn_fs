# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c

## Purpose

This file implements UMC v6.7 RAS behavior. It supports direct register scans and firmware-provided ECC info tables, converts normalized UMC addresses into possible physical bad pages, queries poison mode, and exposes generation callbacks through `umc_v6_7_ras`.

## Important APIs, Types, and Functions

Public symbols include `umc_v6_7_channel_idx_tbl_first`, `umc_v6_7_channel_idx_tbl_second`, `umc_v6_7_convert_error_address`, and `umc_v6_7_ras`. Important helpers include `get_umc_v6_7_reg_offset`, ECC-info query functions, direct CE/UE count functions, reset-counter callbacks, UE address query callbacks, and `umc_v6_7_query_ras_poison_mode`.

## Control Flow

The direct path loops channels with `amdgpu_umc_loop_channels`, reads Gecc counters and MCA status, logs CE/UE counts, optionally prints diagnostic MCA IPID/SYND/MISC0 values, then resets lower and higher chip counters. Address queries read `MCUMC_STATUS` and `ADDRT0`, then call `umc_v6_7_convert_error_address` for valid UECC records.

## State and Persistence Behavior

The code mutates ECC counter select/count registers and MCA status registers. It reads cached ECC info from the RAS context but does not persist a separate software tree. Address conversion fills multiple `ras_err_data` records because one normalized address can map to eight column candidates and an additional R14-flipped set.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS/UMC helpers, UMC 6.7 register headers, `adev->umc.channel_idx_tbl`, DF hash status for channel hashing, and common RAS poison/error record APIs.

## Risks

The register address layout is non-linear and remapped in `get_umc_v6_7_reg_offset`. Physical address expansion depends on channel hash status and PA bit definitions. Diagnostic `dev_info` logging can be noisy during error storms.

## Test Signals

Signals include CE/UE counter deltas, correct reset of both chip-select counters, valid ECC-info table indexing, expected number of retired-page candidates, poison-mode reporting from `UCFatalEn`, and no false channel hashes in reported PA values.
