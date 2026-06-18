# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c

## Purpose

This file implements RAS support for UMC v6.1 hardware, including correctable and uncorrectable ECC counting, UE address conversion, error counter initialization, and channel indexing for Vega20/Arcturus-era layouts.

## Important APIs, Types, and Functions

Important symbols are `umc_v6_1_channel_idx_tbl`, `umc_v6_1_ras_hw_ops`, and `umc_v6_1_ras`. Key helpers manage RSMU UMC index mode, compute UMC register offsets, clear counters for lower and higher chips, query CE/UE counts, translate UE addresses to retired pages, and initialize interrupt/counter state.

## Control Flow

Count and address paths save the RSMU index-mode state, disable index mode when needed, optionally disallow DF C-state on Arcturus, loop `LOOP_UMC_INST_AND_CH`, read generation-specific UMC 6.1.1 or Arcturus 6.1.2 registers, update `ras_err_data`, restore DF C-state, restore index mode, and clear CE counters after count queries.

## State and Persistence Behavior

The implementation mutates RSMU index-mode state, DF C-state policy, ECC counter select registers, ECC counter registers, and MCA status registers. It stores no long-lived software error cache; reported retired pages are added directly to `ras_err_data`.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS/UMC helpers, RSMU register definitions, UMC 6.1 register headers, DPM DF C-state control, `amdgpu_umc_fill_error_record`, and channel-index data from `adev->umc.channel_idx_tbl`.

## Risks

Register selection depends on `adev->asic_type == CHIP_ARCTURUS`. Missed DF C-state protection can make UMC access unreliable. Address conversion assumes the 8KB/256B block mapping and channel table are correct.

## Test Signals

Signals include CE counter deltas on both chip selects, UE status detection, status clearing, stable DF C-state warnings, correct retired page addresses, and no regressions in RAS sysfs counters on Vega20/Arcturus systems.
