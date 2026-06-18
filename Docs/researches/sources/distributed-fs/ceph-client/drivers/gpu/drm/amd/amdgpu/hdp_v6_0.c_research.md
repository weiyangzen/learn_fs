# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c

## Purpose
`hdp_v6_0.c` supplies HDP 6.0 clock and memory power-gating callbacks plus generic HDP flush support.

## Important APIs, Types, And Functions
The exported `hdp_v6_0_funcs` table contains `amdgpu_hdp_generic_flush`, `hdp_v6_0_update_clock_gating`, and `hdp_v6_0_get_clockgating_state`.

## Control Flow
`hdp_v6_0_update_clock_gating` returns early unless LS/DS/SD HDP gating is supported. It selects `regHDP_CLK_CNTL_V6_1` for HDP IP 6.1.0 and `regHDP_CLK_CNTL` otherwise, forces RC memory clock on, clears all ATOMIC/RC power mode bits, enables exactly one mode in priority order SD, LS, then DS, sets ATOMIC/RC power-control enable bits, and releases the RC clock override. `hdp_v6_0_get_clockgating_state` reads `regHDP_MEM_POWER_CTRL` and maps ATOMIC LS/DS/SD bits to AMDGPU clock-gating flags.

## State, Dependencies, And Integration
State is fully hardware-resident in HDP clock and memory-power registers, with policy gated by `adev->cg_flags` and HDP IP version. Dependencies include HDP 6 register headers, SOC15 macros, KFD ioctl constants, and generic HDP flush. Integration occurs through `adev->hdp.funcs`.

## Risks And Test Signals
Risks include using the wrong clock-control register for 6.1.0, mode-priority regressions, and failing to release clock overrides after power-mode changes. Test signals are HDP flush coherency, clock-gating state reporting on 6.0 and 6.1 hardware, and suspend/resume with clock gating enabled.
