# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_0.c

Purpose: implements the amdgpu IP block for JPEG v2.0, moving common lifecycle into `amdgpu_jpeg` helpers while providing v2 register programming, power/clock gating, doorbell-based ring operation, reset, IRQ, and reusable packet emission helpers.

Important APIs and functions: the exported `jpeg_v2_0_ip_block` uses `jpeg_v2_0_ip_funcs`. Public packet helpers include `jpeg_v2_0_dec_ring_emit_ib()`, `_emit_fence()`, `_emit_vm_flush()`, `_emit_wreg()`, `_emit_reg_wait()`, `_insert_start()`, `_insert_end()`, and `_nop()`, later reused by v2.5/v3/v4.0/v4.0.5. Lifecycle functions cover early/sw/hw init, fini, suspend/resume, idle wait, clockgating, powergating, and `jpeg_v2_0_ring_reset()`.

Control flow and state: sw init registers the JPEG decode IRQ, initializes shared JPEG firmware state, creates a doorbell-enabled `jpeg_dec` ring, initializes pitch register mappings, register-dump support, and reset-mask sysfs. Start enables DPM JPEG clocks, disables power gating, disables clock gating, sets tiling, JMI, interrupts, ring base/size, and `ring->wptr`. Stop reverses JMI, clock gating, power gating, and DPM. Power state is persisted in `adev->jpeg.cur_state`; ring state lives in `ring->wptr`, doorbell shadow memory, and JRBC registers.

Dependencies and integration: depends on `amdgpu_jpeg`, `amdgpu_pm`, SOC15 register helpers, VCN 2.0 offsets/masks, IRQ source `VCN_2_0__SRCID__JPEG_DECODE`, NBIO doorbell-range programming, reset mask sysfs, and amdgpu scheduler ring callbacks.

Risks and test signals: doorbell programming must match ring index `(vcn_ring0_1 << 1) + 1`; packet helper sizes in `emit_frame_size` and `emit_ib_size` must stay synchronized with emitted DW counts. Reset stops and restarts the whole block. Test signals include register dump init, sysfs reset mask, ring/IB tests, per-queue reset on bare metal, no per-queue reset on SR-IOV VF, powergating transitions, and trap interrupt fence processing.
