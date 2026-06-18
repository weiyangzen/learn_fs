# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.h

## Purpose

`soc_v1_0.h` declares the public SOC v1.0 common interfaces used by AMDGPU code outside `soc_v1_0.c`. It is focused on multi-XCC addressing, common IP block registration, SOC configuration initialization, GRBM selection, and register offset normalization.

## Important APIs, Types, And Functions

The header declares `soc_v1_0_common_ip_block`, `soc_v1_0_init_soc_config()`, `soc_v1_0_encode_ext_smn_addressing()`, `soc_v1_0_grbm_select()`, `soc_v1_0_normalize_xcc_reg_range()`, `soc_v1_0_normalize_xcc_reg_offset()`, `soc_v1_0_mid1_reg_range()`, and `soc_v1_0_normalize_reg_offset()`. It also exposes `AMDGPU_SOC_V1_0_DOORBELL_SIZE`, documenting the 2 MiB doorbell BAR contract.

## Control Flow And State

The header itself has no control flow. Callers use these declarations to initialize SoC-wide topology state, select GRBM context per XCC, encode extended SMN addresses for remote die/socket access, and normalize register offsets before lookup or access. The corresponding C implementation updates `adev` masks, XCP state, doorbell ranges, and hardware routing state.

## Dependencies, Risks, And Test Signals

The interfaces depend on AMDGPU core structures and the XCP/IP-map model. Risks are mostly contract mismatches: callers must understand whether a register is XCC-local, MID1, or globally addressed, and must pass correct XCC IDs to GRBM selection. Compile coverage plus multi-XCC register access, remote SMN access, XCP initialization, and KFD topology tests are the relevant signals.
