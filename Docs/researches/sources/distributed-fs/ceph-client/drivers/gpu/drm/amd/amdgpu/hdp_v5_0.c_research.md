# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.c

## Purpose
`hdp_v5_0.c` provides HDP 5.0 cache invalidation, memory power gating, medium-grain clock gating, clock-gating state reporting, and basic register initialization.

## Important APIs, Types, And Functions
The exported `hdp_v5_0_funcs` table wires `amdgpu_hdp_generic_flush`, `hdp_v5_0_invalidate_hdp`, `hdp_v5_0_update_clock_gating`, `hdp_v5_0_get_clockgating_state`, and `hdp_v5_0_init_registers`.

## Control Flow
Invalidate uses direct MMIO when no ring write function is available and ring-emitted register writes otherwise. Memory power gating first forces IPH and RC memory clocks on, disables all LS/DS/SD controls because HDP 5.0 cannot switch dynamically, then enables exactly one supported memory power mode according to `adev->cg_flags`, and finally releases clock overrides. Medium-grain clock gating toggles soft override masks in `mmHDP_CLK_CNTL`: clearing overrides enables gating, setting overrides disables it. Init sets `HDP_MISC_CNTL.FLUSH_INVALIDATE_CACHE`.

## State, Dependencies, And Integration
State lives in HDP 5.0 registers (`mmHDP_READ_CACHE_INVALIDATE`, `mmHDP_CLK_CNTL`, `mmHDP_MEM_POWER_CTRL`, `mmHDP_MISC_CNTL`) and in `adev->cg_flags`. The file depends on SOC15 register access, HDP 5.0 headers, AMDGPU ring helpers, and generic HDP flush.

## Risks And Test Signals
Risks include enabling multiple SRAM power modes, failing to force clocks before mode changes, not posting invalidation writes, and stale clock-gating state reporting. Test signals are host/GPU coherency tests, ring and direct invalidation paths, clock-gating flag validation, and suspend/resume with HDP gating enabled.
