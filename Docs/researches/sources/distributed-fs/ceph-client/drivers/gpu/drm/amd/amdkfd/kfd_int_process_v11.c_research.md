# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v11.c

Purpose: implements the GFX11 event interrupt class. It extends the GFX10-style CP/SQ/SDMA/VM-fault path with GFX11 packet layouts, MES-fence filtering, SMI VM-fault notification, queue suspension after debugger bad-op events, and poison-consumption/RAS handling.

Important APIs/types/functions: `event_interrupt_class_v11` exposes `event_interrupt_isr_v11` and `event_interrupt_wq_v11`. Helper printers decode auto, instruction, and error SQ packets using GFX11 field positions. `event_interrupt_poison_consumption_v11` marks a process as poison-consumed, optionally resets its queues, signals poison events, and invokes the amdgpu RAS poison handler.

Control flow: ISR filtering checks VMID ownership unless the entry is a fence, obtains PASID and `context_id0`, and suppresses MES queue fences marked by `AMDGPU_FENCE_MES_QUEUE_FLAG`. It accepts CP end-of-pipe, SQ message, CP bad opcode, SOC21 SDMA trap, KFD fences, and VMC/GFX UTCL2 faults when queue eviction on VM fault is enabled. The workqueue path first handles VMC/GFX UTCL2 faults by building memory exception data and updating SMI VM fault counters. For GRBM/GFX clients, CP end-of-pipe signals a 32-bit event, CP bad opcode generates debugger events and suspends the bad MES queue, SDMA trap signals 28 bits, SDMA ECC triggers poison flow, and SQ messages are decoded by encoding. SQ error types other than illegal instruction and memory violation are treated as poison consumption.

State and persistence: this file persists no local state. It mutates process poison state (`p->poison`), process debug/event queues, SMI counters, DQM queue state, and RAS state through external helpers.

Dependencies/integration: relies on SOC15/SOC21 interrupt IDs, VMC irq source definitions, `kfd_smi_events`, `kfd_debug`, DQM reset/suspend operations, and amdgpu RAS helpers. Selected through device information for GFX11 nodes.

Risks: poison handling uses a simple atomic flag plus queue reset fallback; incorrect source classification can unnecessarily reset queues or GPU. Bad-op suspension is MES-specific. Fault handling is gated by `amdgpu_no_queue_eviction_on_vm_fault`. Test signals include MES queue fence filtering, debugger bad-op queue suspension, SMI VM fault event emission, poison-consumption recovery, and SQ packet decoding coverage.
