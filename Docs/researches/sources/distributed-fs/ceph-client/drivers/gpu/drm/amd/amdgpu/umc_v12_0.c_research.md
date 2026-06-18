# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.c

## Purpose

This file implements UMC v12.0 RAS support for AMDGPU memory controllers. It queries correctable, uncorrectable, and deferred ECC status, converts MCA error addresses to physical addresses, logs bad pages, integrates with ACA bank parsing, and registers the `amdgpu_umc_ras` callbacks for this hardware generation.

## Important APIs, Types, and Functions

Important exported or callback-facing symbols are `umc_v12_0_is_deferred_error`, `umc_v12_0_is_uncorrectable_error`, `umc_v12_0_is_correctable_error`, `umc_v12_0_ras_hw_ops`, `umc_v12_0_aca_info`, and `umc_v12_0_ras`. Core helpers include `get_umc_v12_0_reg_offset`, `umc_v12_0_query_error_count`, `umc_v12_0_query_error_address`, `umc_v12_0_convert_error_address`, `umc_v12_0_update_ecc_status`, and `umc_v12_0_query_ras_ecc_err_addr`.

## Control Flow

RAS count and address queries iterate channels via `amdgpu_umc_loop_channels`. Count flow reads `MCUMC_STATUS`, classifies it through the status predicates, accumulates socket/die-scoped statistics, then resets OdEcc counters. Address flow reads status and address registers, filters for UE or deferred errors, asks PSP RAS services to translate MCA addresses, expands retired-page candidates by flipping generation-specific PA bits, fills RAS error records, and clears status registers.

## State and Persistence Behavior

The driver mutates hardware ECC counters, MCA status registers, UMC flip-bit configuration, `adev->umc.retire_unit`, and the RAS context's ECC log radix tree. Deferred errors are cached as `ras_ecc_err` entries, tagged as newly detected, reserved through `amdgpu_ras_reserve_page`, and may be flushed to EEPROM by delayed page-retirement work after GPU reset recovery.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS, UMC helpers, PSP RAS address translation, SMUIO socket/die identity, ACA error cache logging, MCA register definitions, radix-tree locking, and GMC partition/VRAM metadata.

## Risks

Address conversion is sensitive to NPS mode, HBM/HBM3E type, UMC count, IP version, and flip-bit tables. Incorrect classification can undercount deferred poison events or misclassify replay-mode parity. Host-inaccessible poison mode is forced true.

## Test Signals

Useful signals are injected MCA status tests for CE/UE/DE classification, PSP address query success/failure logs, RAS sysfs/error counters, page retirement records and EEPROM persistence, ACA cache entries, no leaked ECC log entries, and no spurious reset loops after deferred-error recovery.
