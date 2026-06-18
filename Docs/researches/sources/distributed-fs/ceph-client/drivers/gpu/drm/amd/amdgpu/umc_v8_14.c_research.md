# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.c

## Purpose

This file implements a compact UMC v8.14 RAS backend focused on counter-based CE and UE reporting. It initializes Gecc counters, queries correctable and uncorrectable count fields, clears counters, and registers count-only RAS hardware operations.

## Important APIs, Types, and Functions

Important public symbols are `umc_v8_14_ras_hw_ops` and `umc_v8_14_ras`. Key helpers are `get_umc_v8_14_reg_offset`, `umc_v8_14_clear_error_count_per_channel`, `umc_v8_14_query_correctable_error_count`, `umc_v8_14_query_uncorrectable_error_count`, `umc_v8_14_query_error_count_per_channel`, and `umc_v8_14_err_cnt_init_per_channel`.

## Control Flow

The count path loops channels with `amdgpu_umc_loop_channels`, computes channel register offsets, reads `regUMCCH0_GeccErrCnt`, adds CE and uncorrectable counter deltas to `ras_err_data`, then clears the counter to `UMC_V8_14_CE_CNT_INIT`. Initialization sets the Gecc interrupt mode to APIC-based and seeds the counter.

## State and Persistence Behavior

The implementation only mutates hardware Gecc count/select registers and in-memory `ras_err_data` counters. It does not query MCA addresses, clear MCA status, or persist bad-page records.

## Dependencies and Integration Points

Dependencies include UMC 8.14 register headers, AMDGPU RAS/UMC helpers, `amdgpu_umc_loop_channels`, and SOC15 MMIO access macros. Integration is through `amdgpu_umc_ras` with `.err_cnt_init` and count-only `amdgpu_ras_block_hw_ops`.

## Risks

The UE query subtracts `UMC_V8_14_CE_CNT_INIT` from `GeccUnCorrErrCnt`; this assumes the uncorrectable field uses the same initialization baseline. No address callback means this backend cannot directly retire pages from queried errors.

## Test Signals

Signals include CE/UE count deltas, successful counter reset after queries, APIC interrupt setting, absence of invalid MMIO, and expected behavior when RAS frameworks request an address query that is not provided.
