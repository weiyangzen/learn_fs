# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v5_0.c

Purpose: Implements UVD 5.0 decode support for VI-era hardware. Compared with UVD 4.2, it uses 64-bit BAR registers for VCPU and ring buffers, has broader clock-gating programming, exposes clock-gating state, and keeps one decode ring.

Important APIs and functions: `uvd_v5_0_ip_block` is the exported descriptor. Lifecycle hooks include `uvd_v5_0_early_init`, `sw_init`, `hw_init`, suspend/resume/fini, `soft_reset`, gating setters, and `get_clockgating_state`. Ring callbacks are `uvd_v5_0_ring_*` helpers. Core hardware helpers are `uvd_v5_0_mc_resume`, `start`, `stop`, `enable_clock_gating`, `set_sw_clock_gating`, and `enable_mgcg`.

Control flow: SW init registers the VISLANDS30 UVD system-message interrupt, initializes shared UVD state, creates the `uvd` ring, and resumes firmware state. HW init sets UVD clocks, ungates clocking, enables MGCG, tests the ring, and writes semaphore timeouts. Start disables dynamic power gating, programs VCPU cache BAR low/high registers and cache offsets, resets UVD subblocks, boots VCPU, enables interrupts, programs RBC ring base/size/read-write pointers, then clears `RB_NO_FETCH`. Stop idles RBC, stalls LMI, resets VCPU, disables VCPU clock, unstalls LMI, and clears status.

State and persistence: Persistent driver state is held in `adev->uvd.inst->ring`, IRQ, firmware BO address, `max_handles`, PM mutex, DPM/PG/CG flags, and GFX tiling address config. Hardware state includes `mmUVD_LMI_VCPU_CACHE_64BIT_BAR_*`, `mmUVD_LMI_RBC_RB_64BIT_BAR_*`, RBC control, UVD power status, semaphore registers, and CGC gate/control registers.

Dependencies and integration points: Uses `vid`, UVD 5.0, OSS/BIF 5.0, VI, SMU 7.1.2, and VISLANDS interrupt definitions. Integrates with shared UVD parser/test/begin/end helpers, DPM clock control, ring/fence core, and SMC PG status for clock-gating queries.

Risks: Interrupt set remains a TODO stub. `get_clockgating_state` refuses to inspect when UVD is powergated and depends on SMC status accuracy. Fixed polling and reset delays remain sensitive to firmware/hardware timing. `set_powergating_state` states it does not own actual SMC power gating. The `#if 0` hardware clock-gating path documents dormant code that may diverge from real hardware expectations.

Test signals: Ring helper test, local register write test, shared UVD IB test, semaphore timeout writes, clock-gating state readback, and init success logs. Failure signals include ring alloc/test errors, VCPU timeout logs, `-EBUSY` when gating while non-idle, and powergated-state messages from clock-gating queries.
