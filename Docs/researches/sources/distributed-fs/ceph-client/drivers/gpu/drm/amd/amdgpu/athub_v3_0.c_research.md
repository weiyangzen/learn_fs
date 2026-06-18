# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v3_0.c

## Purpose
This file implements ATHUB v3.0 clock-gating control, including per-IP-version register address quirks for ATHUB 3.0.1 and 3.3.0.

## Important APIs, types, and functions
`athub_v3_0_set_clockgating()` supports IP versions 3.0.0, 3.0.1, 3.0.2, and 3.3.0. `athub_v3_0_get_clockgating()` reports register state. `athub_v3_0_get_cg_cntl()` and `athub_v3_0_set_cg_cntl()` abstract the `ATHUB_MISC_CNTL` address difference: 3.0.1 uses `0x00d7`, 3.3.0 uses `0x00d8`, and other supported versions use the generated `regATHUB_MISC_CNTL`.

## Control flow
The setter skips SR-IOV VF. For supported IP versions, it reads the proper control register, toggles `CG_ENABLE` if `AMD_CG_SUPPORT_ATHUB_MGCG` allows it, toggles `CG_MEM_LS_ENABLE` if `AMD_CG_SUPPORT_ATHUB_LS` allows it, and writes changed values through the version-aware setter. The getter reads through the version-aware helper and maps bits to AMDGPU flags.

## State and persistence behavior
State is entirely in the version-specific ATHUB control register. No software cache is kept.

## Dependencies
It depends on AMDGPU core, ATHUB 3.0 generated headers, Navi enum definitions, SOC15 accessors, and clock-gating flags.

## Integration points
AMDGPU ATHUB v3.x IP block callbacks use this during power-management and reporting. The register quirk helpers isolate callers from per-revision address differences.

## Risks and edge cases
Using the wrong register address for 3.0.1 or 3.3.0 would silently report or modify the wrong register. Getter has no SR-IOV VF guard. The setter ignores unsupported versions without warning, so misclassified ASICs may leave clock gating unchanged.

## Test signals
Hardware validation should cover each supported IP version's register address, gate/ungate transitions, getter flag reporting, and no-op behavior on unsupported revisions and SR-IOV VF setters.
