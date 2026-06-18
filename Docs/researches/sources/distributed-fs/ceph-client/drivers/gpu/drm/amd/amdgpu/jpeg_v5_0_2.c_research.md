<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c

Purpose: implements AMDGPU JPEG IP block version 5.0.2. It is a close variant of v5.0.1 for ten-ring JPEG decode support, but without active RAS registration and without the SR-IOV MMSCH startup path in this file.

Important APIs and functions: `jpeg_v5_0_2_early_init()` validates the JPEG instance count, sets ten rings, and installs ring and IRQ functions. `jpeg_v5_0_2_sw_init()` registers ten JPEG trap source IDs, initializes common JPEG software/firmware state, creates ring objects, records internal and external pitch-register addresses, initializes register-dump support, and publishes reset masks. `jpeg_v5_0_2_hw_init()` checks RRMT capability, disables the JPEG tile anti-hang bit, optionally configures doorbells, and runs ring tests. `jpeg_v5_0_2_ip_block` exports the AMD IP callbacks.

Control flow: the ungate path uses `jpeg_v5_0_2_start()` to initialize each hardware instance and JRBC ring. Ring initialization enables the appropriate JRBC interrupt bit, programs VMID zero, ring BAR low/high, rptr/wptr zero, RB control, and RB size. Gate/fini calls reset JMI, re-enable anti-hang, and cancel idle work. Interrupt handling maps an IH node to a physical JPEG AID and dispatches each VCN JPEG source ID to the corresponding decode ring fence driver.

State and persistence behavior: runtime state is in `adev->jpeg`, ring objects, doorbell or MMIO write pointers, JPEG current PG state, and programmed JRBC/JMI registers. Unlike v5.0.1, `ring->use_doorbell` is set false in software init despite doorbell indexes being calculated, so MMIO write-pointer commits are expected. `adev->jpeg.supported_reset` always includes per-queue reset after the soft/full reset mask is computed.

Dependencies and integration points: uses common AMDGPU JPEG helpers, SOC15/VCN register macros, `jpeg_v4_0_3` ring packet emitters, AMDGPU ring/fence/IRQ infrastructure, `node_id_to_phys_map`, and register dump support. The ring funcs omit `.parse_cs`, unlike v5.0.1 and v5.3.0, which is a visible integration difference.

Risks and edge cases: idle and wait helpers share the same false/zero initial aggregate issue as v5.0.1. The `hw_fini()` body has odd indentation but functionally gates when `cur_state` is not gate. Disabled `#if 0` ACA/RAS code suggests poison handling is not wired despite similar hardware error-code knowledge. Reset helper does not take the VCN reset mutex used in v5.0.1. Always advertising per-queue reset may be wrong if firmware or platform support is incomplete.

Test signals: probe should create ten rings per JPEG instance, register all ten trap IRQ IDs, pass ring tests, and expose reset masks. Exercise MMIO write-pointer mode, interrupt-to-ring mapping for each source ID, per-ring stall/drop/core reset, suspend/resume, register dump output, RRMT capability flagging, and reset recovery after a timed-out fence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v5_0_2.c -->
