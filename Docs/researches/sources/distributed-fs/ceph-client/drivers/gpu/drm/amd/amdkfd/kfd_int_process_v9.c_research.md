# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v9.c

Purpose: implements GFX9 and GFX9.4.3 KFD interrupt processing. It handles legacy GFX9 SQ packet layouts, PASID patching for no-HWS firmware behavior, CP bogus-context filtering, poison-consumption routing across GFX/MMHUB/SDMA, and node-aware filtering for multi-XCC GFX9.4.3.

Important APIs/types/functions: exports `event_interrupt_class_v9` and `event_interrupt_class_v9_4_3`. `event_interrupt_isr_v9` is the main ISR filter; `event_interrupt_isr_v9_4_3` wraps it with `kfd_irq_is_from_node`. `event_interrupt_wq_v9` performs deferred dispatch. `event_interrupt_poison_consumption_v9` maps interrupt client IDs to RAS blocks and reset modes, marks a process poisoned atomically, emits poison events, and invokes amdgpu RAS handling. `context_id_expected` gates a workaround for CP firmware that can send zero context IDs.

Control flow: ISR rejects non-KFD VMIDs except fences, filters supported clients, and patches missing PASIDs in no-HWS mode by copying the IH entry into `patched_ihre` and inserting `dev->dqm->vmid_pasid[vmid]`. It warns/drops zero PASID after patching and ignores zero-context CP end-of-pipe events on firmware expected to provide valid context IDs. Deferred handling signals CP and SDMA traps, decodes GFX9 SQ auto/wave/error fields through `KFD_CONTEXT_ID_GET_SQ_INT_DATA`, forwards debugger traps, handles CP bad opcodes, converts VMC/UTCL2 faults to memory-violation debug events plus SMI updates, and routes SDMA/VMC/SQ poison events to RAS handling.

State and persistence: local code persists no state, but it mutates patched interrupt payloads, process poison flags, RAS event state, event slots, debug queues, SMI counters, and prange/queue recovery via external subsystems.

Dependencies/integration: relies on SOC15 interrupt macros, amdgpu RAS/RAS manager, `kfd_smi_events`, DQM scheduling policy and VMID-to-PASID table, and KFD debug/event helpers. The GFX9.4.3 class is selected for partitioned multi-node devices.

Risks: no-HWS PASID patching is race-sensitive and depends on DQM VMID bookkeeping. Poison reset mode depends on IP and PM firmware versions. Zero-context filtering can drop legitimate events if firmware capability detection is wrong. Test signals include no-HWS PASID patch paths, CP end-of-pipe context filtering, GFX9 SQ debugger traps, SDMA ECC poison handling, VMC poison/fault events, and GFX9.4.3 node routing.
