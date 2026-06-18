## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_smuio.h

Purpose: defines the SMUIO abstraction for ROM register access, clock-gating state, package/topology identity, XGMI/ethernet-switch capabilities, custom HBM detection, and GPU clock counter retrieval.

Important APIs and types: `enum amdgpu_pkg_type` identifies APU, CEM, OAM, BB, and unknown packages. `struct amdgpu_smuio_mcm_config_info` stores socket and die IDs. `struct amdgpu_smuio_funcs` supplies callbacks for ROM index/data offsets, ROM clock gating, clock-gating flags, die/socket ID, package type, host GPU XGMI support, ethernet switch connectivity, custom HBM support, and GPU clock counter. `struct amdgpu_smuio` stores the callback table.

Control flow: no logic; ASIC-specific SMUIO modules populate `funcs`, and common code calls through it to query platform/topology and ROM clocking information.

State and persistence: runtime callback pointer only. Returned topology/package data reflects hardware registers.

Dependencies and integration points: references `struct amdgpu_device` and is embedded under AMDGPU device state. Integrates with SMU/SMUIO IP blocks, topology discovery, clock gating, ROM access, and clock counter users.

Risks: optional callbacks require NULL checks by callers. Package enum numeric values likely match firmware/register encodings and should not be changed casually.

Test signals: ASIC-specific SMUIO init, ROM access, clock-gating state reporting, topology ID queries, XGMI support detection, and clock counter reads.
