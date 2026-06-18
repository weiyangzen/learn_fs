# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.c

## Purpose

This file implements UMC v8.7 RAS support for Sienna-style memory controllers. It handles direct register CE/UE scans, ECC-info table scans, UE address conversion, counter initialization, and RAS callback registration.

## Important APIs, Types, and Functions

Important public symbols are `umc_v8_7_channel_idx_tbl`, `umc_v8_7_ras_hw_ops`, and `umc_v8_7_ras`. Important helpers include `get_umc_v8_7_reg_offset`, ECC-info count/address functions, `umc_v8_7_convert_error_address`, direct Gecc count functions, direct address query functions, and `umc_v8_7_err_cnt_init`.

## Control Flow

Direct count flow loops UMC instances and channels, reads lower and higher chip Gecc counters, checks MCA status for SRAM CE and UE-like conditions, updates `ras_err_data`, then clears counters. Direct address flow reads status and address registers, masks low address bits according to `LSB`, converts valid UECC errors to retired pages, fills error records, and clears status.

## State and Persistence Behavior

The code mutates Gecc counter select/count registers, MCA status registers, and `ras_err_data`. It does not persist a separate ECC tree. Address conversion maps one UMC address to one retired page using a 4KB block plus channel and 256B offset fields.

## Dependencies and Integration Points

Dependencies include RSMU headers, UMC 8.7 register headers, AMDGPU RAS/UMC helpers, `adev->umc.channel_idx_tbl`, and RAS ECC-info storage.

## Risks

DF C-state protection is marked TODO for ECC-info paths, so safe access depends on firmware/interface readiness. Direct and ECC-info paths use different sources and must agree. Address conversion depends heavily on channel table correctness.

## Test Signals

Signals include direct and ECC-info CE/UE counter agreement, correct lower/higher chip counter reset, valid retired page output for injected UECC, status clearing, and no access instability around DF C-state transitions.
