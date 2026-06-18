# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v10.c

Purpose: implements the GFX10 KFD event interrupt backend. It supplies `event_interrupt_class_v10`, whose ISR-side callback cheaply filters IH entries and whose workqueue callback decodes CP, SQ, SDMA, VM fault, and fence-drain events for deferred processing.

Important APIs/types/functions: `event_interrupt_isr_v10` validates KFD VMID range, PASID presence, and supported SOC15 client/source combinations. `event_interrupt_wq_v10` dispatches decoded events to `kfd_signal_event_interrupt`, `kfd_set_dbg_ev_from_interrupt`, and `kfd_process_close_interrupt_drain`. The file defines GFX10 SQ interrupt encoding enums and bitfield macros for auto, wave, and error encodings, including debugger doorbell/trap extraction and CP bad-op error-code extraction.

Control flow: the shared interrupt layer calls `interrupt_isr` first. This function ignores non-KFD VMIDs except fence interrupts, rejects unsupported clients, logs the raw eight-dword IH packet, rejects PASID zero, then returns true only for end-of-pipe, SDMA trap, SQ message, CP bad opcode, VM fault clients, or fence events. Deferred work extracts `source_id`, `client_id`, `pasid`, `vmid`, `context_id0`, and `context_id1`. CP/SE clients either signal event slots, log and forward SQ messages, or create debugger events for bad opcodes. SDMA clients signal 28-bit trap payloads. VMC/VMC1/UTCL2 entries synthesize `kfd_hsa_memory_exception_data` for debugger memory-violation events. Fence-like interrupts close interrupt drain for the PASID.

State and persistence: no durable state is owned. Runtime state is the interrupt payload and per-process/event/debugger state updated through KFD helpers. The function relies on `dev->vm_info` and `dev->kfd->device_info` wiring selected at device bring-up.

Dependencies/integration: depends on `soc15_int.h` IH extraction macros, `kfd_events.h`, `kfd_debug.h`, and KFD DQM definitions. It plugs into `kfd_interrupt.c` through `struct kfd_event_interrupt_class`.

Risks: bitfield constants are ASIC-specific and regressions can silently misroute debugger trap codes or event IDs. VM fault permission fields are inferred from `ring_id`, so hardware format changes are high risk. PASID zero drops events. Test signals include GPU debug trap tests, CP end-of-pipe event signaling, SDMA trap signaling, VM fault eviction/debug events, and fence drain behavior on GFX10 hardware.
