# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v12_1.c

Purpose: implements the GFX12.1 KFD interrupt backend. It keeps the GFX11 event model but adds node-aware IH filtering for partitioned/multi-node devices and newer RAS event logging/poison APIs.

Important APIs/types/functions: `event_interrupt_class_v12_1` binds `event_interrupt_isr_v12_1` and `event_interrupt_wq_v12_1`. `event_interrupt_poison_consumption_v12_1` marks the PASID poisoned, attempts DQM queue reset for SQ poison, generates UniRAS event sequence numbers when enabled, logs the RAS event, and calls `amdgpu_amdkfd_ras_pasid_poison_consumption_handler`.

Control flow: ISR first extracts NodeID and VMID and calls `kfd_irq_is_from_node`; entries for other nodes are ignored with rate-limited debug logging. It then applies KFD VMID filtering, ignores MES queue fences embedded in CP end-of-pipe, warns once on PASID zero, and accepts CP, SQ, CP bad opcode, SOC21 SDMA trap, fence, VMC, and UTCL2 events. The workqueue callback handles VMC/UTCL2 memory violations with debug events plus SMI updates. GRBM/GFX handling covers CP event signaling, bad-op debugger events and MES bad-queue suspension, SDMA trap/ECC, and SQ auto/instruction/error decoding. GFX12.1 CP end-of-pipe uses `kfd_signal_event_interrupt(..., false)` for the last boolean argument, unlike earlier GFX10/11 CP signaling paths.

State and persistence: no private persistent state. It updates process poison state, queue reset/suspension state, debugger event state, SMI counters, and RAS logs through helpers. It depends on node partition metadata to avoid cross-node interrupt processing.

Dependencies/integration: integrates with the shared IH FIFO in `kfd_interrupt.c`, SOC15 field macros, GFX/VMC source IDs, DQM reset/suspend hooks, `amdgpu_ras_mgr`, and KFD SMI/debug/event layers.

Risks: node filtering must match hardware partitioning, or interrupts may be dropped or handled by the wrong KFD node. RAS behavior differs from v11 and must preserve PASID-specific handling. Test signals include multi-node interrupt routing, PASID-zero warning paths, CP/SQ/SDMA event signaling, VM-fault SMI updates, poison-consumption event IDs, and queue reset fallback paths.
