# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/uvd_v4_2.c

Purpose: Implements the UVD 4.2 decode IP block for CIK-era hardware. It provides a single UVD ring, start/stop/reset sequencing, DCM/MGCG programming, SMC-backed power-gating transitions, and trap-to-fence interrupt handling.

Important APIs and functions: `uvd_v4_2_ip_block` exports the block. Lifecycle hooks are `uvd_v4_2_early_init`, `sw_init`, `hw_init`, `hw_fini`, `prepare_suspend`, `suspend`, `resume`, `is_idle`, `wait_for_idle`, `soft_reset`, and gating hooks. Ring callbacks mirror UVD 3.1: read/write pointers, IB emission, fence emission, NOP insertion, and ring tests. `uvd_v4_2_set_powergating_state` is a notable generation-specific hook that programs `mmUVD_PGFSM_CONFIG` when DPM is not active.

Control flow: early init refuses to enable the block when global `amdgpu_dpm` is disabled because this generation needs DPM to ungate UVD. SW init registers legacy IRQ 124, initializes shared UVD state, creates the `uvd` ring, and resumes UVD memory. HW init enables MGCG, sets UVD clocks, tests the ring, and configures semaphore timeouts. Power-on from `set_powergating_state(UNGATE)` powers through SMC PG status checks and then runs `uvd_v4_2_start`; gate stops UVD and can request PG FSM power down. Start programs LMI, cache, MPC mux, VCPU reset release, interrupt enable, and RBC ring registers.

State and persistence: Uses `adev->uvd.inst->ring`, `adev->uvd.inst->irq`, `adev->uvd.max_handles`, firmware/heap/stack offsets, `adev->gfx.config.gb_addr_config`, DPM/PG flags, and SMC current PG status. Hardware state persists in UVD cache windows, LMI extension registers, RBC pointers/base/size, CGC memory control, and PG FSM registers.

Dependencies and integration points: Includes `cikd`, UVD 4.2, OSS 2.0, BIF 4.1, and SMU 7.0.1 register definitions. Uses shared UVD helpers for firmware BO management, parser/test helpers, idle work, and DPM clock hooks. IRQ registration uses `AMDGPU_IRQ_CLIENTID_LEGACY` source 124.

Risks: Early init failure when DPM is disabled is intentional but can surprise board bring-up. Power-gating comments state the hook only reinitializes the block while actual gating belongs to SMC/DPM. Interrupt set is a TODO stub. Fixed VCPU polling can fail under slow firmware start. Ring and fence formats remain 32-bit-address constrained for command payloads.

Test signals: Ring test helper, local context-register ring test, shared UVD IB test, semaphore programming, and the init success log validate the path. Timeout/error logs around VCPU reset attempts, ring allocation failures, and `-ENOENT` from early init are useful failure signals.
