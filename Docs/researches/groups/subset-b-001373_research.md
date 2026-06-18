# Research: subset-b-001373

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v10.c

Purpose: implements the GFX10 KFD event interrupt backend. It supplies `event_interrupt_class_v10`, whose ISR-side callback cheaply filters IH entries and whose workqueue callback decodes CP, SQ, SDMA, VM fault, and fence-drain events for deferred processing.

Important APIs/types/functions: `event_interrupt_isr_v10` validates KFD VMID range, PASID presence, and supported SOC15 client/source combinations. `event_interrupt_wq_v10` dispatches decoded events to `kfd_signal_event_interrupt`, `kfd_set_dbg_ev_from_interrupt`, and `kfd_process_close_interrupt_drain`. The file defines GFX10 SQ interrupt encoding enums and bitfield macros for auto, wave, and error encodings, including debugger doorbell/trap extraction and CP bad-op error-code extraction.

Control flow: the shared interrupt layer calls `interrupt_isr` first. This function ignores non-KFD VMIDs except fence interrupts, rejects unsupported clients, logs the raw eight-dword IH packet, rejects PASID zero, then returns true only for end-of-pipe, SDMA trap, SQ message, CP bad opcode, VM fault clients, or fence events. Deferred work extracts `source_id`, `client_id`, `pasid`, `vmid`, `context_id0`, and `context_id1`. CP/SE clients either signal event slots, log and forward SQ messages, or create debugger events for bad opcodes. SDMA clients signal 28-bit trap payloads. VMC/VMC1/UTCL2 entries synthesize `kfd_hsa_memory_exception_data` for debugger memory-violation events. Fence-like interrupts close interrupt drain for the PASID.

State and persistence: no durable state is owned. Runtime state is the interrupt payload and per-process/event/debugger state updated through KFD helpers. The function relies on `dev->vm_info` and `dev->kfd->device_info` wiring selected at device bring-up.

Dependencies/integration: depends on `soc15_int.h` IH extraction macros, `kfd_events.h`, `kfd_debug.h`, and KFD DQM definitions. It plugs into `kfd_interrupt.c` through `struct kfd_event_interrupt_class`.

Risks: bitfield constants are ASIC-specific and regressions can silently misroute debugger trap codes or event IDs. VM fault permission fields are inferred from `ring_id`, so hardware format changes are high risk. PASID zero drops events. Test signals include GPU debug trap tests, CP end-of-pipe event signaling, SDMA trap signaling, VM fault eviction/debug events, and fence drain behavior on GFX10 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v11.c

Purpose: implements the GFX11 event interrupt class. It extends the GFX10-style CP/SQ/SDMA/VM-fault path with GFX11 packet layouts, MES-fence filtering, SMI VM-fault notification, queue suspension after debugger bad-op events, and poison-consumption/RAS handling.

Important APIs/types/functions: `event_interrupt_class_v11` exposes `event_interrupt_isr_v11` and `event_interrupt_wq_v11`. Helper printers decode auto, instruction, and error SQ packets using GFX11 field positions. `event_interrupt_poison_consumption_v11` marks a process as poison-consumed, optionally resets its queues, signals poison events, and invokes the amdgpu RAS poison handler.

Control flow: ISR filtering checks VMID ownership unless the entry is a fence, obtains PASID and `context_id0`, and suppresses MES queue fences marked by `AMDGPU_FENCE_MES_QUEUE_FLAG`. It accepts CP end-of-pipe, SQ message, CP bad opcode, SOC21 SDMA trap, KFD fences, and VMC/GFX UTCL2 faults when queue eviction on VM fault is enabled. The workqueue path first handles VMC/GFX UTCL2 faults by building memory exception data and updating SMI VM fault counters. For GRBM/GFX clients, CP end-of-pipe signals a 32-bit event, CP bad opcode generates debugger events and suspends the bad MES queue, SDMA trap signals 28 bits, SDMA ECC triggers poison flow, and SQ messages are decoded by encoding. SQ error types other than illegal instruction and memory violation are treated as poison consumption.

State and persistence: this file persists no local state. It mutates process poison state (`p->poison`), process debug/event queues, SMI counters, DQM queue state, and RAS state through external helpers.

Dependencies/integration: relies on SOC15/SOC21 interrupt IDs, VMC irq source definitions, `kfd_smi_events`, `kfd_debug`, DQM reset/suspend operations, and amdgpu RAS helpers. Selected through device information for GFX11 nodes.

Risks: poison handling uses a simple atomic flag plus queue reset fallback; incorrect source classification can unnecessarily reset queues or GPU. Bad-op suspension is MES-specific. Fault handling is gated by `amdgpu_no_queue_eviction_on_vm_fault`. Test signals include MES queue fence filtering, debugger bad-op queue suspension, SMI VM fault event emission, poison-consumption recovery, and SQ packet decoding coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v12_1.c

Purpose: implements the GFX12.1 KFD interrupt backend. It keeps the GFX11 event model but adds node-aware IH filtering for partitioned/multi-node devices and newer RAS event logging/poison APIs.

Important APIs/types/functions: `event_interrupt_class_v12_1` binds `event_interrupt_isr_v12_1` and `event_interrupt_wq_v12_1`. `event_interrupt_poison_consumption_v12_1` marks the PASID poisoned, attempts DQM queue reset for SQ poison, generates UniRAS event sequence numbers when enabled, logs the RAS event, and calls `amdgpu_amdkfd_ras_pasid_poison_consumption_handler`.

Control flow: ISR first extracts NodeID and VMID and calls `kfd_irq_is_from_node`; entries for other nodes are ignored with rate-limited debug logging. It then applies KFD VMID filtering, ignores MES queue fences embedded in CP end-of-pipe, warns once on PASID zero, and accepts CP, SQ, CP bad opcode, SOC21 SDMA trap, fence, VMC, and UTCL2 events. The workqueue callback handles VMC/UTCL2 memory violations with debug events plus SMI updates. GRBM/GFX handling covers CP event signaling, bad-op debugger events and MES bad-queue suspension, SDMA trap/ECC, and SQ auto/instruction/error decoding. GFX12.1 CP end-of-pipe uses `kfd_signal_event_interrupt(..., false)` for the last boolean argument, unlike earlier GFX10/11 CP signaling paths.

State and persistence: no private persistent state. It updates process poison state, queue reset/suspension state, debugger event state, SMI counters, and RAS logs through helpers. It depends on node partition metadata to avoid cross-node interrupt processing.

Dependencies/integration: integrates with the shared IH FIFO in `kfd_interrupt.c`, SOC15 field macros, GFX/VMC source IDs, DQM reset/suspend hooks, `amdgpu_ras_mgr`, and KFD SMI/debug/event layers.

Risks: node filtering must match hardware partitioning, or interrupts may be dropped or handled by the wrong KFD node. RAS behavior differs from v11 and must preserve PASID-specific handling. Test signals include multi-node interrupt routing, PASID-zero warning paths, CP/SQ/SDMA event signaling, VM-fault SMI updates, poison-consumption event IDs, and queue reset fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v9.c

Purpose: implements GFX9 and GFX9.4.3 KFD interrupt processing. It handles legacy GFX9 SQ packet layouts, PASID patching for no-HWS firmware behavior, CP bogus-context filtering, poison-consumption routing across GFX/MMHUB/SDMA, and node-aware filtering for multi-XCC GFX9.4.3.

Important APIs/types/functions: exports `event_interrupt_class_v9` and `event_interrupt_class_v9_4_3`. `event_interrupt_isr_v9` is the main ISR filter; `event_interrupt_isr_v9_4_3` wraps it with `kfd_irq_is_from_node`. `event_interrupt_wq_v9` performs deferred dispatch. `event_interrupt_poison_consumption_v9` maps interrupt client IDs to RAS blocks and reset modes, marks a process poisoned atomically, emits poison events, and invokes amdgpu RAS handling. `context_id_expected` gates a workaround for CP firmware that can send zero context IDs.

Control flow: ISR rejects non-KFD VMIDs except fences, filters supported clients, and patches missing PASIDs in no-HWS mode by copying the IH entry into `patched_ihre` and inserting `dev->dqm->vmid_pasid[vmid]`. It warns/drops zero PASID after patching and ignores zero-context CP end-of-pipe events on firmware expected to provide valid context IDs. Deferred handling signals CP and SDMA traps, decodes GFX9 SQ auto/wave/error fields through `KFD_CONTEXT_ID_GET_SQ_INT_DATA`, forwards debugger traps, handles CP bad opcodes, converts VMC/UTCL2 faults to memory-violation debug events plus SMI updates, and routes SDMA/VMC/SQ poison events to RAS handling.

State and persistence: local code persists no state, but it mutates patched interrupt payloads, process poison flags, RAS event state, event slots, debug queues, SMI counters, and prange/queue recovery via external subsystems.

Dependencies/integration: relies on SOC15 interrupt macros, amdgpu RAS/RAS manager, `kfd_smi_events`, DQM scheduling policy and VMID-to-PASID table, and KFD debug/event helpers. The GFX9.4.3 class is selected for partitioned multi-node devices.

Risks: no-HWS PASID patching is race-sensitive and depends on DQM VMID bookkeeping. Poison reset mode depends on IP and PM firmware versions. Zero-context filtering can drop legitimate events if firmware capability detection is wrong. Test signals include no-HWS PASID patch paths, CP end-of-pipe context filtering, GFX9 SQ debugger traps, SDMA ECC poison handling, VMC poison/fault events, and GFX9.4.3 node routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_int_process_v9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_interrupt.c

Purpose: provides the shared KFD interrupt buffering and deferred-processing framework. KGD/amdgpu ISR code asks KFD whether an IH entry is wanted; wanted entries are copied into a per-node FIFO and processed later on a high-priority workqueue.

Important APIs/types/functions: `kfd_interrupt_init` allocates `node->ih_fifo`, creates a shared `KFD IH` workqueue if necessary, initializes `node->interrupt_lock`, sets up `node->interrupt_work`, and publishes `interrupts_active`. `kfd_interrupt_exit` stops new interrupt work and frees the FIFO. `enqueue_ih_ring_entry` copies entries into the FIFO with overflow warning. `interrupt_wq` drains entries and invokes the generation-specific `event_interrupt_class->interrupt_wq`. `interrupt_is_wanted` calls the generation-specific ISR filter.

Control flow: device init calls `kfd_interrupt_init`; it allocates a fixed FIFO sized for 16,384 IH entries times the hardware entry size and uses `smp_wmb` before interrupts become visible. ISR-side code calls `interrupt_is_wanted`, then `enqueue_ih_ring_entry` and schedules `node->interrupt_work` elsewhere in the driver. The worker repeatedly obtains a linear FIFO pointer, passes it to the ASIC-specific workqueue decoder, then skips the consumed bytes. If it spends more than one second in one run, it requeues itself to avoid soft-lockup warnings.

State and persistence: owns per-node FIFO memory, `interrupts_active`, spinlock initialization, and work item registration. There is no persistent disk state; loss is possible when the FIFO overflows because hardware provides no back-pressure or acknowledgment.

Dependencies/integration: depends on Linux `kfifo`, workqueues, spinlocks, and `struct kfd_event_interrupt_class` installed in `node->kfd->device_info`. It is the bridge between amdgpu ISR context and KFD scheduler/event/debug processing.

Risks: comments assume single reader/writer and non-reentrant enqueue/dequeue. FIFO overflow loses events. `kfd_interrupt_exit` frees the FIFO after disabling interrupts but does not itself flush queued work, so teardown ordering elsewhere must guarantee no use-after-free. Test signals include FIFO overflow warnings, worker rescheduling under interrupt storms, init/exit race tests, and generation-specific interrupt callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.c

Purpose: implements KFD kernel-owned queues, especially HIQ, used to submit PM4/MES packets from the driver to hardware. It allocates queue memory, doorbells, MQDs, and pointer buffers, exposes packet acquire/submit/rollback, and tears queues down safely.

Important APIs/types/functions: `kernel_queue_init`/`kernel_queue_uninit` are public constructors/destructors. `kq_acquire_packet_buffer` reserves dwords in the ring and handles wrap with NOP padding. `kq_submit_packet` publishes the write pointer and rings the kernel doorbell, supporting 32-bit and 64-bit doorbells. `kq_rollback_packet` discards pending write-pointer reservations. Internal `kq_initialize` and `kq_uninitialize` allocate/free GTT suballocations, initialize `struct queue`, allocate/init MQDs, and load HIQ MQDs.

Control flow: initialization obtains a kernel doorbell, allocates packet queue, EOP memory on newer ASICs, read-pointer and write-pointer buffers, zeros them, initializes queue properties, creates a `struct queue`, allocates and initializes an MQD via the HIQ MQD manager, and loads it into the fixed HIQ pipe/queue for HIQ type. Packet acquisition reads hardware rptr and pending wptr, computes modulo free space with one dword left empty, NOP-fills to the ring end if wrapping, and advances pending pointers. Submission checks fatal-error detection, orders ring writes with barriers, updates wptr memory, and writes the doorbell. Uninit destroys loaded HIQ MQDs under reset-domain read lock when possible, then frees MQD, GTT allocations, doorbell, and queue.

State and persistence: `struct kernel_queue` persists pending pointers, GPU/CPU addresses for PQ/EOP/rptr/wptr, doorbell, queue object, MQD manager, and NOP packet. Hardware-visible state is in GTT allocations and doorbell writes; it is not durable across device reset.

Dependencies/integration: depends on KFD GTT suballocator, kernel doorbell allocator, queue initialization helpers, DQM MQD managers, amdgpu reset domain, and PM4 packet definitions. Consumers build packets using `kq_acquire_packet_buffer` then call submit or rollback.

Risks: ring arithmetic assumes power-of-two queue size and one unused slot. Failed EOP allocation on CIK path relies on NULL-safe free. Destroying HIQ is skipped if reset-domain read lock is unavailable, leaving teardown to reset handling. Test signals include wraparound/NOP padding, rollback, 32/64-bit doorbell submission, FED `-EIO` path, allocation unwinding, and reset/uninit races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.h

Purpose: declares the KFD kernel queue interface and the `struct kernel_queue` state shared with queue users.

Important APIs/types/functions: declares `kq_acquire_packet_buffer`, `kq_submit_packet`, and `kq_rollback_packet`. `struct kernel_queue` contains the owning `kfd_node`, MQD manager, `struct queue`, pending 32/64-bit write pointers, NOP packet, GTT memory objects and CPU/GPU addresses for rptr/wptr/PQ/EOP/fence, and a list node.

Control flow: callers reserve packet space through `kq_acquire_packet_buffer`, write packet dwords into the returned buffer, then call `kq_submit_packet`; on construction failure after reservation they call `kq_rollback_packet`. The struct fields are filled by `kfd_kernel_queue.c` initialization and consumed by packet builders and teardown paths.

State and persistence: the header defines all persistent in-memory queue state. The union of `wptr64_kernel` and `wptr_kernel` mirrors hardware doorbell-size differences. GPU addresses are persisted while the kernel queue lives and are embedded into MQDs and hardware registers.

Dependencies/integration: includes `kfd_priv.h` for KFD core types and Linux list/types headers. It is used by DQM/HIQ code that submits commands through kernel queues.

Risks: external users can access fields directly, so layout changes have broad impact. The union demands correct doorbell-size checks before dereference. Test signals are mostly exercised through `kfd_kernel_queue.c`: packet reservation/submit, queue creation/destruction, and doorbell-size variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_kernel_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.c

Purpose: implements SVM/HMM page migration between system RAM and GPU VRAM for AMD KFD. It copies pages with SDMA through temporary GART mappings, creates device-private/coherent `dev_pagemap` memory for VRAM, handles CPU faults on device pages, and updates SMI/per-process migration counters.

Important APIs/types/functions: public exports include `svm_migrate_to_vram`, `svm_migrate_vram_to_ram`, `svm_migrate_addr_to_pfn`, and `kgd2kfd_init_zone_device`. Internal copy helpers include `svm_migrate_gart_map`, `svm_migrate_copy_memory_gart`, and `svm_migrate_copy_done`. Migration helpers include `svm_migrate_vma_to_vram`, `svm_migrate_copy_to_vram`, `svm_migrate_vma_to_ram`, `svm_migrate_copy_to_ram`, and CPU fault callback `svm_migrate_to_ram`. `svm_migrate_pgmap_ops` wires folio free and migrate-to-RAM callbacks.

Control flow: RAM-to-VRAM validates the requested subrange, resolves the destination KFD node, reserves VRAM accounting, allocates/attaches an SVM BO, then iterates VMAs. For each VMA it calls `migrate_vma_setup`, maps source system pages for DMA, creates VRAM zone-device destination pages, batches contiguous copy ranges through GART windows and `amdgpu_copy_buffer`, completes `migrate_vma_pages`, waits on the final fence, finalizes migration, unmaps DMA, emits SMI events, updates `actual_loc`, `vram_pages`, and page-in counters. VRAM-to-RAM selects device-private/coherent pages, allocates locked system pages, batches contiguous VRAM copies back to DMA-mapped system pages, finalizes migration, decrements `vram_pages`, frees the SVM BO when no VRAM pages remain, and updates page-out counters. VRAM-to-VRAM migrates all current VRAM pages to RAM, retrying up to three times, then migrates the requested range to the new GPU. CPU faults call `svm_migrate_to_ram`, locate the owning process/range, avoid recursive faulting-task migration, align to range granularity, and migrate the fault region back to RAM.

State and persistence: mutates `svm_range` fields (`actual_loc`, `vram_pages`, `ttm_res`/SVM BO references), per-process-device page-in/page-out counters, zone-device page `zone_device_data`, SMI event streams, migration fences, and amdgpu memory reservations. No on-disk persistence exists.

Dependencies/integration: tightly integrates Linux HMM `migrate_vma`, `dev_pagemap`, DMA mapping, amdgpu TTM/GART/copy-buffer infrastructure, KFD SVM range locking, amdgpu memory accounting, SMI events, and process lookup by `mm`.

Risks: this file is concurrency- and lifetime-sensitive. Error cleanup must unlock/put allocated pages, drop VRAM page references, unmap DMA, and finalize migration consistently. `svm_migrate_copy_to_ram` cleanup calls `svm_migrate_put_sys_page(dst[i])` with DMA-address-derived values, so mapping/cleanup assumptions need careful review against callers and DMA-unmap helpers. VRAM-to-VRAM currently stages through RAM and can fail with `-EDEADLK` if pages do not leave VRAM. Device pgmap registration reserves system memory for `struct page`s over all VRAM and disables SVM support on remap failure. Test signals include migrate_vma partial migration, DMA mapping failures, copy fence errors, CPU page faults on device pages, XGMI coherent vs private pgmap, VRAM accounting exhaustion, SMI migration events, and mixed-domain debug forcing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.h

Purpose: declares the SVM migration interface for KFD code when `CONFIG_HSA_AMD_SVM` is enabled.

Important APIs/types/functions: defines `enum MIGRATION_COPY_DIR` with `FROM_RAM_TO_VRAM` and `FROM_VRAM_TO_RAM`. Declares `svm_migrate_to_vram`, `svm_migrate_vram_to_ram`, and `svm_migrate_addr_to_pfn`.

Control flow: SVM policy code calls `svm_migrate_to_vram` to move a range or subrange to a selected GPU node and calls `svm_migrate_vram_to_ram` to evict/fault pages back to system memory. Address translation helpers convert VRAM offsets into device-page PFNs using the amdgpu KFD pgmap.

State and persistence: the header owns no state. It exposes functions that mutate `svm_range`, process-device counters, and HMM page state in the implementation.

Dependencies/integration: guarded by `IS_ENABLED(CONFIG_HSA_AMD_SVM)` and includes KFD SVM/private headers plus Linux MM locking definitions. It is the compile-time bridge between SVM range management and migration implementation.

Risks: callers must hold the locks documented in the implementation: mmap read lock, SVM/prange locks, and `prange->migrate_mutex` as applicable. Test signals are compile coverage with SVM enabled/disabled and migration callers honoring lock/context requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_module.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_module.c

Purpose: owns KFD module-level initialization and shutdown sequencing and exposes `kgd2kfd_init`/`kgd2kfd_exit` for amdgpu-to-KFD integration.

Important APIs/types/functions: `kfd_init` validates module parameters, initializes char device, topology, process workqueue, procfs, and debugfs. `kfd_exit` tears them down. `kgd2kfd_init` and `kgd2kfd_exit` are the external wrappers.

Control flow: init first validates `sched_policy` bounds and `max_num_of_queues_per_device`. It then calls `kfd_chardev_init`, `kfd_topology_init`, and `kfd_process_create_wq` with reverse-order cleanup on failure. `kfd_procfs_init` failure is intentionally ignored, while debugfs init is attempted unconditionally after procfs. Exit cleans up processes, destroys process workqueue, finalizes debugfs/procfs, shuts topology down, and exits char device.

State and persistence: module state includes char device registration, topology data, process workqueue, procfs/debugfs entries, and live KFD process state. No local static mutable state is declared here beyond module parameters defined elsewhere.

Dependencies/integration: depends on KFD core subsystems and amdgpu calling the `kgd2kfd_*` wrappers during driver init/exit.

Risks: init ordering is a contract; adding subsystems must include correct unwind. Procfs failures are non-fatal by design. Exit assumes process cleanup precedes workqueue destruction. Test signals include invalid module parameter rejection, failure injection for char/topology/workqueue init, unload with live processes, and debugfs/procfs optional availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.c

Purpose: provides generation-independent MQD manager helpers used by per-ASIC MQD manager implementations. It centralizes priority mapping, shared HIQ/SDMA MQD allocation, CU-mask mapping, HQD load/destroy/free helpers, stride helpers, and preemption-failure reporting.

Important APIs/types/functions: `pipe_priority_map` maps KFD queue priorities to CP pipe priorities. `allocate_hiq_mqd`, `allocate_sdma_mqd`, and `free_mqd_hiq_sdma` manage MQDs inside the preallocated HIQ/SDMA MQD region. `mqd_symmetrically_map_cu_mask` maps user CU masks across SE/SH/XCC topology. `kfd_hiq_load_mqd_kiq`, `kfd_destroy_mqd_cp`, `kfd_free_mqd_cp`, `kfd_is_occupied_cp`, `kfd_load_mqd_sdma`, `kfd_destroy_mqd_sdma`, and `kfd_is_occupied_sdma` call the `kfd2kgd` hardware callbacks. `kfd_hiq_mqd_stride`, `kfd_get_hiq_xcc_mqd`, `kfd_mqd_stride`, and `kfd_check_hiq_mqd_doorbell_id` support multi-XCC and diagnostics.

Control flow: generation-specific initializers install these helpers into `struct mqd_manager` vtables. HIQ and SDMA allocations carve offsets from `dev->dqm->hiq_sdma_mqd`; CP MQDs may be freed either through amdgpu kernel memory free or GTT suballocation free based on the backing object. CU mask mapping bounds-checks shader-engine/shader-array dimensions, counts active CUs from amdgpu topology, and symmetrically spreads selected CUs across available SE/SH and XCC instances, using WGP pairs on GFX10+.

State and persistence: mutates `kfd_mem_obj` descriptors, queue properties via vtable users, and hardware HQD state through `kfd2kgd`. It owns no global mutable state except `pipe_priority_map`.

Dependencies/integration: depends on amdgpu topology (`gfx.cu_info`, `gfx.config`), DQM MQD manager arrays, KFD/XCC masks, and `kfd2kgd` hardware callbacks.

Risks: CU-mask mapping has explicit stack-corruption guardrails for unsupported topology sizes; exceeding them leaves no CUs enabled and can hang queues. Shared HIQ/SDMA allocation uses pointer arithmetic on a common BO and must stay aligned with manager sizes and XCC counts. Test signals include CU-mask topology variants, HIQ/SDMA offset calculations, CP/SDMA HQD load/destroy/is_occupied callbacks, and preemption-failure doorbell diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.h

Purpose: defines the MQD manager abstraction used by KFD queue management and declares common helpers implemented in `kfd_mqd_manager.c`.

Important APIs/types/functions: `struct mqd_manager` is a vtable plus device context and `mqd_size`. It covers MQD allocation/init/load/update/destroy/free, occupancy checks, wave-state extraction, checkpoint/restore, debugfs dumping, preemption-failure checks, and stride calculation. `struct mqd_user_context_save_area_header` defines the user-visible compact header for control-stack and wave-state offsets/sizes. The header declares HIQ/SDMA allocation helpers, CP/SDMA load/destroy/free helpers, CU-mask mapping, stride helpers, and HIQ XCC accessors.

Control flow: DQM selects a per-generation `mqd_manager_init_*` function and stores manager instances by `KFD_MQD_TYPE`. Queue creation and scheduling then call through the vtable for CP, HIQ, DIQ, and SDMA queues without knowing the underlying MQD layout.

State and persistence: the abstraction persists function pointers, a mutex, device pointer, and MQD size. Queue state is persisted in hardware-visible MQD memory allocated/managed by implementations.

Dependencies/integration: includes `kfd_priv.h` for queue/device/process types and is included by all ASIC-specific MQD manager files plus kernel queue/DQM code.

Risks: vtable omissions are runtime failures; each queue type must install a coherent set of callbacks. The checkpoint/restore ABI must match user-space expectations for debugger/process checkpointing. Test signals include manager initialization for every queue type and ASIC, debugfs dumps, checkpoint/restore round trips, and wave-state extraction ABI validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c

Purpose: implements MQD manager operations for CIK-era ASICs. It programs `struct cik_mqd` compute descriptors and `struct cik_sdma_rlc_registers` SDMA descriptors, including HIQ/DIQ variants and checkpoint/restore support.

Important APIs/types/functions: `mqd_manager_init_cik` constructs per-type managers. `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, and `destroy`/`free` helpers cover CP queues. SDMA uses `init_mqd_sdma` and `update_mqd_sdma`. HIQ uses `init_mqd_hiq` and `update_mqd_hiq`. `update_cu_mask`, `set_priority`, `checkpoint_mqd`, `restore_mqd`, `checkpoint_mqd_sdma`, and `restore_mqd_sdma` manage optional state transitions.

Control flow: CP MQDs are GTT suballocated, zeroed/aligned, initialized with header, persistent state, quantum, static thread masks, base address, and AQL enable when needed. Update fills PQ base, rptr report address, doorbell offset, VMID, queue size, optional ATC bits, NO_UPDATE_RPTR for AQL, CU mask, and pipe priority. SDMA update fills ring control, RB base, rptr writeback, doorbell, virtual address, engine/queue ID. HIQ update marks the queue as privileged KMD. Manager init wires different allocation/free/load callbacks for CP, HIQ, DIQ, and SDMA.

State and persistence: queue state persists in MQD memory and SDMA register snapshots. Restore copies checkpointed MQDs back and rewrites doorbell offsets from current queue properties before marking queues inactive.

Dependencies/integration: depends on CIK register/struct headers, shared MQD helpers, KFD GTT suballocation, KFD2KGD HQD callbacks, and debugfs `seq_hex_dump`.

Risks: CIK-specific field encodings differ from SOC15 generations. `se_mask[4]` assumes max four shader engines. Restore must rewrite doorbell offsets to avoid stale process mappings. Test signals include CIK CP/HIQ/DIQ/SDMA queue creation, AQL vs PM4 loading, CU-mask update, checkpoint/restore, debugfs MQD dumps, and HIQ preemption-failure detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c

Purpose: implements MQD manager operations for GFX10 compute and SDMA queues using `v10_compute_mqd` and `v10_sdma_mqd` layouts.

Important APIs/types/functions: `mqd_manager_init_v10` wires CP, HIQ, DIQ, and SDMA vtables. Core helpers include `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `checkpoint_mqd`, `restore_mqd`, `init_mqd_hiq`, `destroy_hiq_mqd`, `init_mqd_sdma`, and `update_mqd_sdma`.

Control flow: compute MQD init zeros the descriptor, writes header/static thread masks/persistent state/PQ defaults/base address/quantum/debug scheduler bit, enables AQL if requested, and configures CWSR fields when enabled. Update programs PQ size/base/rptr/wptr polling/doorbell, IB/EOP controls, VMID, AQL no-update/slot-based/full/drop bits, CWSR control, CU mask, and priority. Load calls `hqd_load` with AQL write-pointer shift. HIQ init marks privileged KMD and destroy unmaps HIQ by doorbell offset. SDMA update programs RB control/base/rptr/doorbell, engine/queue IDs, and dummy register.

State and persistence: MQD memory captures queue state and CWSR metadata. Checkpoint copies compute or SDMA MQDs; GFX10 control stack remains in the user-accessible context save area, so `get_wave_state` only copies a header to userspace.

Dependencies/integration: relies on GFX10 register masks, shared MQD helpers, amdgpu HQD/HIQ callbacks, KFD CWSR/debugger queue properties, and debugfs dumping.

Risks: GFX10 removed WPP clamp bits used by earlier generations, so AQL field programming must stay generation-correct. EOP size calculation uses `ffs` and assumes nonzero EOP size. Test signals include CWSR wave-state header reporting, AQL/PM4 queues, HIQ unmap, SDMA MQD load, CU-mask updates, checkpoint/restore, and debugfs dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c

Purpose: implements GFX11 MQD managers, adding aligned MQD allocation, debugger workaround CU-mask modes, PCIe atomic acknowledgement bits, SDMA write-pointer polling, and MES-specific SDMA allocation behavior.

Important APIs/types/functions: `mqd_manager_init_v11` wires CP/HIQ/DIQ/SDMA managers. `update_cu_mask` supports `UPDATE_FLAG_DBG_WA_ENABLE`/`DISABLE` by forcing static thread masks. `init_mqd`, `update_mqd`, `get_wave_state`, `checkpoint_mqd`, `restore_mqd`, `init_mqd_hiq`, `destroy_hiq_mqd`, `init_mqd_sdma`, and `update_mqd_sdma` implement queue operations.

Control flow: compute allocation uses `AMDGPU_MQD_SIZE_ALIGN`. Init programs full or workaround static masks, persistent preload size 0x55, base address, quantum, dispatch-pointer debug status, optional atomics support acknowledgement, AQL control, and CWSR fields. Update fills PQ/EOP/IB/VMID/doorbell fields and AQL flags, then applies CU-mask/WA updates and priority. SDMA init zeros a page when MES is enabled, otherwise the SDMA MQD size. SDMA update enables rptr writeback, 32-bit wptr polling, schedule quantum, and doorbell offset. Manager init switches SDMA allocation/free to generic CP allocation/free under MES.

State and persistence: queue state is persisted in aligned MQD memory. Debug workaround state is encoded as static thread masks. Checkpoint/restore copy MQDs and rewrite doorbell offset; wave-state retrieval copies only the context-save header because control stack is user-visible elsewhere.

Dependencies/integration: depends on GFX11 structs/masks, amdgpu atomics support detection, global `amdgpu_sdma_phase_quantum`, shared MQD helpers, MES shared-resource flag, and debugfs.

Risks: WA flag handling can override user CU masks. MES SDMA uses different backing allocation size and free path. Atomics acknowledgement is firmware-dependent. Test signals include CU debug WA toggles, MES and non-MES SDMA queue creation, atomics-capable devices, AQL flag programming, CWSR wave-state reads, and HIQ preemption-failure reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c

Purpose: implements GFX12.0 MQD manager operations for compute, HIQ/DIQ, and SDMA queues. It closely follows GFX11 but uses GFX12 structures, masks, context-save user header, and SDMA MCU write-pointer polling.

Important APIs/types/functions: `mqd_manager_init_v12` is the public initializer. Helpers include `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `init_mqd_hiq`, `init_mqd_sdma`, `update_mqd_sdma`, and debugfs dump callbacks.

Control flow: compute init uses aligned MQD size, sets static thread masks for eight SE fields, persistent preload 0x55, MQD base, quantum, debug status, optional atomics support bit, AQL control, and CWSR fields. Update programs PQ size/base/rptr/wptr polling/doorbell, IB/EOP controls, VMID, AQL no-update/slot/full/drop fields, CWSR control, CU mask, and priority. `get_wave_state` fills `mqd_user_context_save_area_header`, not the older nested KFD context-save header. SDMA update programs queue RB control with MCU write-pointer polling, schedule quantum, dummy register, and switch-inside-IB for fairness.

State and persistence: MQD memory stores queue and CWSR state. The file does not implement checkpoint/restore callbacks for v12 CP/SDMA in this snapshot, unlike v10/v11; consumers must tolerate missing callbacks or use higher-level alternatives.

Dependencies/integration: depends on GFX12 struct/mask headers, shared MQD helpers, amdgpu atomics detection, `amdgpu_sdma_phase_quantum`, KFD2KGD HQD callbacks, and debugfs.

Risks: absence of checkpoint/restore callbacks is an ABI/feature difference to verify against checkpointing consumers. EOP size programming assumes valid nonzero sizes. SDMA allocation uses generic CP allocation/free for page-aligned MQDs. Test signals include GFX12 queue creation for CP/HIQ/DIQ/SDMA, CWSR header ABI, AQL/PM4 operation, SDMA fairness switch, and checkpointing feature probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12_1.c

Purpose: implements GFX12.1 MQD management, including multi-XCC compute MQD replication, a GFX12.1-specific CU-mask mapper, metadata queue programming, and updated SDMA register fields.

Important APIs/types/functions: `mqd_manager_init_v12_1` wires queue-type vtables. `mqd_symmetrically_map_cu_mask_v12_1` maps CU masks across the smaller GFX12.1 SE/SH layout and XCC subsets. Core helpers include `allocate_mqd`, base `init_mqd`/`update_mqd`, multi-XCC `init_mqd_v12_1`/`update_mqd_v12_1`/`load_mqd_v12_1`/`destroy_mqd_v12_1`, `get_wave_state_v12_1`, `init_mqd_sdma`, and `update_mqd_sdma`.

Control flow: compute allocation multiplies aligned MQD size by `NUM_XCC` for compute queues. Base init programs GFX12.1 descriptor defaults, preload size 0x63, static masks including `se8`, atomics bit, AQL control, and CWSR fields. Base update rebuilds PQ control, programs queue base, optional metadata queue base/control when metadata size equals four times main queue size, rptr/wptr polling, doorbell, IB/EOP controls, VMID, AQL flags, priority, and active state. Multi-XCC init/update iterates each XCC MQD at `mqd_stride`, adjusts per-XCC CWSR base, sets `compute_current_logical_xcc_id` and `compute_tg_chunk_size` for AQL, and handles PM4 target XCC. Load/destroy iterate `for_each_inst` over `xcc_mask`, passing XCC IDs to KGD. Wave-state retrieval iterates per-XCC context-save areas and reports XCC0 sizes to callers.

State and persistence: per-compute queue state is persisted as one MQD per XCC in a single allocation. `current_logical_xcc_start` is advanced to distribute AQL logical XCC assignment. Metadata queue settings are persisted in MQD KD fields when valid.

Dependencies/integration: depends on GFX12.1 masks, DQM `current_logical_xcc_start`, `NUM_XCC`, XCC masks, KFD2KGD per-XCC load/destroy callbacks, shared MQD helpers, amdgpu SDMA quantum, and debugfs.

Risks: `err` in `destroy_mqd_v12_1` and `load_mqd_v12_1` is not initialized before the XCC loop; if `xcc_mask` were empty, return would be undefined, though normal devices should have at least one XCC. Metadata queue size validation is strict and silently ignores invalid metadata after a warning. CU mapper assumes GFX12.1 topology dimensions fitting `[2][2]`. Test signals include multi-XCC compute creation/load/destroy, metadata queue valid/invalid sizes, CWSR per-XCC addresses, CU-mask mapping, PM4 target XCC, and SDMA queue programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c

Purpose: implements MQD management for GFX9, including special CWSR control-stack allocation, VRAM-backed MQDs for selected IPs, SDMA descriptors, HIQ handling, and multi-XCC variants for GFX9.4.3/9.4.4/9.5.0.

Important APIs/types/functions: `mqd_manager_init_v9` builds managers for CP, HIQ, DIQ, and SDMA. Key helpers include `mqd_stride_v9`, `mqd_on_vram`, `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `get_wave_state`, `get_checkpoint_info`, checkpoint/restore helpers, SDMA init/update/checkpoint/restore, HIQ init/destroy, and GFX9.4.3 multi-XCC init/update/load/destroy/wave-state/checkpoint/restore helpers.

Control flow: for compute queues with CWSR, allocation creates an enlarged buffer with MQD in the first GPU page and the control stack after it, using special amdgpu kernel memory allocation and VRAM/GTT domain selection. Init programs GFX9 MQD defaults, queue size/base/rptr/wptr/EOP/VMID, AQL flags, CWSR save area fields, trap-present bit, CU masks, priority, and optional GWS SIMD distribution. Wave-state reads copy a header plus control-stack bytes from the MQD-adjacent stack. GFX9.4.3-style devices replicate MQDs per XCC, update per-XCC CWSR base addresses, assign logical XCC IDs, flush HDP if MQDs are in VRAM, and load/destroy each XCC through KGD. HIQ multi-XCC paths use shared HIQ MQD slices and unmap each XCC. SDMA paths program RB control/base/rptr/doorbell, dummy register, engine/queue IDs, and switch-inside-IB.

State and persistence: MQD memory stores queue state, CWSR fields, control-stack contents, doorbell IDs, and per-XCC stride metadata. `current_logical_xcc_start` advances on multi-XCC init/restore. `queue_doorbell_id0` is cleared after preemption-failure checks.

Dependencies/integration: depends on v9 structs/masks, amdgpu kernel memory allocation/free, HDP flush, DQM XCC masks/logical counters, shared MQD helpers, KFD2KGD HQD callbacks, user copy APIs, and debugfs.

Risks: this is one of the most delicate MQD files. The enlarged MQD/control-stack allocation must preserve 4K boundaries and memory attributes. Multi-XCC stride and checkpoint buffer math must match user ABI and allocation size. VRAM-backed MQDs require HDP flushes for CPU writes to become visible. Test signals include CWSR allocation and wave-state copying, checkpoint/restore with multiple XCCs, HIQ per-XCC load/unmap, GWS update flag behavior, VRAM MQD paths on 9.4.3/9.5.0, SDMA restore, and preemption-failure doorbell clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c -->
