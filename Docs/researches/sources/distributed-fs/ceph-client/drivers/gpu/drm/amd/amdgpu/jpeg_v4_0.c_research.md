# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v4_0.c

Purpose: implements JPEG v4.0 for a single instance, including normal bare-metal startup, SR-IOV VF startup through MMSCH command tables, RAS poison interrupts/status, reset support, and reused v2 packet emission.

Important APIs and functions: exports `jpeg_v4_0_ip_block`; lifecycle functions cover early/sw/hw init, fini, suspend/resume, clock/power gating, idle/wait, and ring reset. `jpeg_v4_0_start_sriov()` builds an MMSCH v4 init table for VF mode. RAS helpers query JPEG0/JPEG1 poison status.

Control flow and state: sw init registers decode and poison IRQs, initializes shared JPEG state, sets the doorbell differently for SR-IOV VF, initializes the ring, RAS, register dump, and reset sysfs. HW init either sends the MMSCH init table and manually marks the scheduler ready in VF mode, or programs NBIO/VCN doorbells and runs the ring test. Power gating is bypassed for VFs by forcing `cur_state` to ungated. Bare-metal start programs static PG, CGC, tiling, JMI, JRBC interrupt enable, ring base/size, and `ring->wptr`.

Dependencies and integration: depends on VCN 4.0 offsets/masks, `mmsch_v4_0.h`, shared v2.0 packet helpers, amdgpu JPEG/RAS helpers, NBIO doorbell programming, SOC15 register access, and SR-IOV virtualization state.

Risks and test signals: MMSCH init has tight timeout/error handling and depends on the virtual MM table header layout. VF mode skips ring test and manually sets scheduler readiness, so VF coverage must include real command submission. Poison IRQ uses a separate `ras_poison_irq`. Test signals include bare-metal ring/IB tests, VF MMSCH mailbox success, powergating no-op on VF, RAS poison event processing, per-queue reset outside VF, and correct doorbell offset selection.
