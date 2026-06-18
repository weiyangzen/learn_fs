# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_ras_if.h

## Purpose

`ta_ras_if.h` defines the shared-memory ABI between AMDGPU and the RAS trusted application. It lets the host enable/disable RAS features, trigger error injection, query block/sub-block information, and translate between MCA and physical addresses through PSP/TEE firmware.

## Important APIs, Types, And Functions

The ABI version is `RAS_TA_HOST_IF_VER`. `enum ras_command` covers enable, disable, trigger error, query block/sub-block info, query address. `enum ta_ras_status` includes success, reset-needed, invalid parameters, unavailable RAS, duplicate commands, injection failure, ASD/TEE/register access errors, unsupported device/IP/function/error injection, timeout, and PCS state failures. `enum ta_ras_block` enumerates UMC, SDMA, GFX, MMHUB, ATHUB, PCIE/BIF, HDP, XGMI/WAFL, DF, SMN, SEM, MP0/MP1, FUSE, MCA, VCN, JPEG, IH, MPIO, and MMSCH. Input/output unions reserve 256 dwords for ABI headroom and include init flags, feature toggles, error injection, and address translation payloads.

## Control Flow, State, And Dependencies

The driver writes `cmd_id`, `if_version`, and `ras_in_message`, invokes the TA, then checks `resp_id`, `ras_status`, and `ras_out_message`. State persists in TA initialization, enabled RAS features, injection switches, output flags, and queried address data. The header integrates with AMDGPU RAS, PSP TA loading, MCA/UMC address reporting, and NPS/memory partition handling.

## Risks And Test Signals

Risks include firmware/driver layout drift, enum value mismatches, oversized assumptions hidden by reserved padding, invalid node sentinel handling, and dangerous error-injection commands reaching production hardware. Tests should cover TA init flags, feature enable/disable by block/error type, injection failure and reset-needed statuses, MCA-to-PA and PA-to-MCA translation, unsupported IP/device statuses, and version mismatch handling.
