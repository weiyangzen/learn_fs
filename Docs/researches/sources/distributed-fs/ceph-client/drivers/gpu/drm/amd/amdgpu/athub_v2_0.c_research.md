# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_0.c

## Purpose
This file implements ATHUB v2.0 clock-gating and light-sleep control for IP versions 1.3.1, 2.0.0, and 2.0.2.

## Important APIs, types, and functions
`athub_v2_0_set_clockgating()` toggles clock gating for supported versions and returns zero. `athub_v2_0_get_clockgating()` reports hardware state into AMDGPU clock-gating flags. Internal helpers update `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK`.

## Control flow
The setter skips SR-IOV VF. For supported IP versions, it calls medium-grain clock-gating and light-sleep helpers. Unlike v1.0, each helper returns early if the matching support flags are not present, which means unsupported features are left unchanged rather than force-cleared. If supported, the helper reads `ATHUB_MISC_CNTL`, sets or clears the bit based on `state`, and writes changed values.

## State and persistence behavior
Only the ATHUB hardware register is modified. No software cache is maintained. Getter output is caller-owned.

## Dependencies
It depends on AMDGPU core, generated ATHUB 2.0 offset/mask/default headers, SOC15 accessors, SR-IOV detection, and clock-gating flag definitions.

## Integration points
The AMDGPU IP block layer uses these functions as the v2.0 ATHUB clock-gating callbacks during power-management transitions and diagnostics.

## Risks and edge cases
Because unsupported features are left unchanged, stale firmware or bootloader register bits can remain set if support flags are absent. Getter does not special-case SR-IOV VF, unlike the setter. The supported IP-version switch must be updated when a new ASIC reuses the same register layout.

## Test signals
Hardware tests should verify the support-flag early returns, gate/ungate writes for each listed IP version, getter flag accuracy, and VF no-op setter behavior.
