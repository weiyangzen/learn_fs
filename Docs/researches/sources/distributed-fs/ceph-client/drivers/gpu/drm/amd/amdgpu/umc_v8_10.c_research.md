# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c

## Purpose

This file implements UMC v8.10 RAS support, including multi-node register offsets, status-based CE/UE counting, swizzle-mode normalized-address to physical-address conversion, ECC-info table support, poison-mode reporting, and counter initialization.

## Important APIs, Types, and Functions

Important public data includes `umc_v8_10_channelnum_map_colbit_table`, `umc_v8_10_channel_idx_tbl_ext0`, `umc_v8_10_channel_idx_tbl`, `umc_v8_10_ras_hw_ops`, and `umc_v8_10_ras`. Key helpers include `get_umc_v8_10_reg_offset`, `umc_v8_10_get_col_bit`, `umc_v8_10_swizzle_mode_na_to_pa`, `umc_v8_10_convert_error_address`, direct count/address callbacks, ECC-info count/address callbacks, and `umc_v8_10_err_cnt_init`.

## Control Flow

Direct count flow loops all nodes, UMCs, and channels, reads `MCUMC_STATUS` for CE/UE signals, updates `ras_err_data`, and clears Gecc counts. Direct address flow requires `err_data->err_addr`, valid status, `AddrV`, and `UECC` before reading `ADDRT0`. Address conversion clears low bits using `AddrLsb`, enumerates possible C5/C6 normal-address values, maps each through swizzle mode, logs the PA, and fills RAS records.

## State and Persistence Behavior

The code mutates Gecc counter registers, MCA status registers, interrupt selection, and `ras_err_data`. It does not persist a local bad-page cache. Poison mode is forced true because the Gecc control register is not host accessible.

## Dependencies and Integration Points

Dependencies include UMC 8.10 register headers, AMDGPU RAS/UMC helpers, channel-index tables configured in `adev->umc`, `hweight32(adev->gmc.m_half_use)` in total-channel calculations, and common loop/channel callbacks.

## Risks

The swizzle mapping only supports channel counts present in the col-bit table; unsupported counts fail address conversion. Channel index selection across node/UMC/channel dimensions must match topology, including half-disabled memory.

## Test Signals

Signals include supported channel-count mapping, expected PA output for injected normalized addresses, CE count accumulation from ECC-info and direct paths, status clearing, correct behavior with disabled memory halves, and no failed PA mapping logs.
