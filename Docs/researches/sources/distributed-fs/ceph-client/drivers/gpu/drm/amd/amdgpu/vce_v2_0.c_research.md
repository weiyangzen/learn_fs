# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v2_0.c

Purpose: Implements VCE 2.0 encode support for CIK-era hardware. It manages two physical VCE rings, firmware memory layout, ECPU boot/stop, dynamic or software clock gating, SMC-style power-gating reinitialization, soft reset, and trap interrupt fence processing.

Important APIs and functions: `vce_v2_0_ip_block` is the descriptor. Hardware helpers include `vce_v2_0_mc_resume`, `start`, `stop`, `firmware_loaded`, `lmi_clean`, `disable_cg`, `init_cg`, `set_sw_cg`, `set_dyn_cg`, and `enable_mgcg`. Lifecycle hooks cover early/sw/hw init/fini, suspend/resume, idle/wait, soft reset, clock/power gating. Ring callbacks use generic VCE emit/parse/test helpers with generation-specific pointer accessors.

Control flow: early init runs shared VCE setup, sets two rings, and installs ring/IRQ functions. SW init registers legacy IRQ 167, allocates VCE memory sized for firmware/stack/data, resumes the firmware BO, and initializes both rings. HW init sets clocks, enables dynamic MGCG, and ring-tests both rings. Start marks VCE busy, initializes and disables CG for boot, programs MC windows and both ring buffers, enables ECPU clock, releases reset, waits for firmware loaded, and clears busy. Power gate stops the block; ungate starts it.

State and persistence: Uses `adev->vce.gpu_addr`, `ring[0..1]`, IRQ, idle work, firmware version/state from shared helpers, DPM/CG flags, and PM structures. Hardware state includes 40-bit VCPU cache BAR, cache offsets/sizes, VCE LMI controls, ring base/pointers, CGTT override, clock gating registers, VCPU control, soft reset, and VCE status.

Dependencies and integration points: Depends on `amdgpu_vce` shared code, CIK/VCE 2.0/SMU/OSS register definitions, DPM/ASIC clock hooks, ring/fence core, and legacy interrupt source 167. It processes `entry->src_data[0]` as the ring index.

Risks: `hw_fini` only cancels idle work and does not call `vce_v2_0_stop`; stop is reached through suspend/power-gating paths. Some stop failures log and return 0 when LMI is not idle or VCE busy, which may leave hardware running. Soft reset asserts SRBM VCE reset and immediately calls start, so correctness depends on prior state. Clock-gating mode selection differs between HW init and set_clockgating_state.

Test signals: Ring tests for both rings, firmware loaded status bit, successful trap IRQ processing, clock-gating transitions, and init success log. Failure signals include firmware loaded timeouts, VCE busy/not-idle logs, unhandled interrupt ring indices, and soft reset/start errors.
