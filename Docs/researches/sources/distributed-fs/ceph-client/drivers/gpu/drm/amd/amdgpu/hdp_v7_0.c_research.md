# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.c

## Purpose
`hdp_v7_0.c` provides HDP 7.0 clock and memory power-gating callbacks and uses generic HDP flushing.

## Important APIs, Types, And Functions
The exported `hdp_v7_0_funcs` table contains `amdgpu_hdp_generic_flush`, `hdp_v7_0_update_clock_gating`, and `hdp_v7_0_get_clockgating_state`.

## Control Flow
`hdp_v7_0_update_clock_gating` exits unless HDP LS/DS/SD support is advertised. It reads `regHDP_CLK_CNTL` and `regHDP_MEM_POWER_CTRL`, forces RC memory clocks on, clears ATOMIC and RC LS/DS/SD enable bits, then enables one mode with SD preferred over LS and DS. It sets ATOMIC/RC power-control enable bits when any supported mode exists and finally clears the RC clock override. `hdp_v7_0_get_clockgating_state` reports LS/DS/SD based on ATOMIC memory power bits.

## State, Dependencies, And Integration
The state model is hardware register state plus `adev->cg_flags`. Dependencies include HDP 7.0 register headers, SOC15 access macros, KFD ioctl constants, and generic HDP flush. Integration is via the device HDP function table.

## Risks And Test Signals
Risks are the same class as v6 but without the v6.1 alternate register path: incorrect power-mode priority, stale overrides, or inaccurate state reporting. Test signals include HDP cache coherency, clock-gating state readback, and suspend/resume on HDP 7 hardware.
