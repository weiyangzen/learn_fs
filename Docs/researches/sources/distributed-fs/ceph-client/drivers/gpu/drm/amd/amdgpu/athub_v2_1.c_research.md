# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/athub_v2_1.c

## Purpose
This file provides ATHUB v2.1 clock-gating support for IP versions 2.1.0, 2.1.1, 2.1.2, and 2.4.0.

## Important APIs, types, and functions
`athub_v2_1_set_clockgating()` is the exported setter and `athub_v2_1_get_clockgating()` is the exported reporter. Internal helpers directly update `CG_ENABLE` and `CG_MEM_LS_ENABLE` in `ATHUB_MISC_CNTL` according to requested state and support flags.

## Control flow
The setter exits on SR-IOV VF. For supported versions it applies both helpers. Each helper reads `ATHUB_MISC_CNTL`, sets the relevant bit only if the requested state is gate and the relevant support flags are set, otherwise clears it, and writes only on change. The getter reads the same register and ORs ATHUB MGCG/LS support bits into the caller's flags when the hardware bits are set.

## State and persistence behavior
The only persistent state is the ATHUB hardware register. Caller-provided flags are updated in place.

## Dependencies
It depends on AMDGPU core, ATHUB 2.1 generated offset/mask headers, SOC15 accessors, SR-IOV detection, and common clock-gating flags.

## Integration points
The functions are selected by ATHUB v2.1/v2.4 IP block setup for runtime clock-gating transitions and diagnostics.

## Risks and edge cases
This version force-clears bits when support flags are absent, unlike v2.0's early-return behavior. Getter still reads on SR-IOV VF. Version coverage must stay synchronized with ASIC tables.

## Test signals
Test signals are register bit transitions under all four listed IP versions, support-flag gating behavior, VF setter no-op, and getter flag accuracy.
