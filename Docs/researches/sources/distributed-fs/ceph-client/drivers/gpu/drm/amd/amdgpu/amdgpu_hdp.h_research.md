# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.h

## Purpose
`amdgpu_hdp.h` defines the common HDP state, HDP RAS wrapper, and function-table contract used by common and ASIC-specific HDP code.

## Important APIs, types, and functions
It defines `struct amdgpu_hdp_ras`, `struct amdgpu_hdp_funcs`, and `struct amdgpu_hdp`. Function pointers cover HDP flush, invalidate, clock-gating update/query, and register initialization. It declares the common RAS and flush/invalidate helper functions.

## Control flow
The header itself has no control flow. ASIC code installs `amdgpu_hdp_funcs`; common paths call through `amdgpu_hdp_flush()` and `amdgpu_hdp_invalidate()`.

## State and persistence behavior
`struct amdgpu_hdp` holds runtime RAS and function-table pointers. HDP register state is hardware state and is not persistent in this header.

## Dependencies and integration points
The header depends on AMDGPU RAS types and forward-declared device/ring types. It integrates with GMC RAS initialization, memory coherency paths, and IP-specific clock-gating/register initialization.

## Risks and edge cases
Null function tables must be handled by callers. Clock-gating and register-init hooks are hardware-specific and can affect coherency if installed incorrectly.

## Test signals
Build tests, HDP RAS init, flush/invalidate behavior across ASIC generations, and clock-gating state tests validate this contract.
