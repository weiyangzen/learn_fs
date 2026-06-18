# subset-b-001374 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c

## Purpose
Implements the VI/GFX8 memory queue descriptor manager for AMD KFD queues. It constructs, updates, checkpoints, restores, dumps, and loads CP, HIQ/DIQ, and SDMA MQDs used by the device queue manager to map user queues onto hardware queue descriptors.

## Important APIs, types, and functions
- `mqd_manager_init_vi` allocates a `struct mqd_manager` and fills its function table according to `enum KFD_MQD_TYPE`.
- CP/HIQ paths use `struct vi_mqd`; SDMA paths use `struct vi_sdma_mqd`.
- `allocate_mqd`, `init_mqd`, `load_mqd`, `update_mqd`, `checkpoint_mqd`, `restore_mqd`, and `get_wave_state` are the main CP queue hooks.
- `init_mqd_sdma`, `update_mqd_sdma`, `checkpoint_mqd_sdma`, and `restore_mqd_sdma` are the SDMA hooks.
- `update_cu_mask` maps a user CU mask through `mqd_symmetrically_map_cu_mask`.

## Control flow
The DQM asks this manager to allocate an MQD, initialize it with defaults, and then update it with queue properties. CP MQD initialization programs static defaults, persistence, base address, quantum, EOP fetcher, AQL read-pointer behavior, trap TBA/TMA, and CWSR fields. `load_mqd` delegates to `kfd2kgd->hqd_load` with an AQL-specific write-pointer shift. Updates fill PQ, EOP, IB, IQ, VMID, doorbell, ATC/MTYPE, CU mask, and active-state fields. HIQ/DIQ reuse CP initialization but set privileged/KMD queue bits. SDMA updates program ring base, read pointer writeback, doorbell, VM address, engine, and queue ID.

## State and persistence behavior
State persists in GTT-allocated `kfd_mem_obj` storage and in queue properties. Checkpoint/restore copies raw MQD bytes and rewrites doorbell fields from restored queue properties, then marks restored queues inactive until remapped. For VI CP, control stack data is reported as user-mode accessible, so checkpoint info returns zero control-stack bytes.

## Dependencies and integration points
Depends on `kfd_priv.h`, `kfd_mqd_manager.h`, VI hardware layout definitions, GFX8/OSS bit masks, GTT suballocation, DQM MQD callbacks, and `kfd2kgd` HQD operations. It integrates with CRIU through the PQM checkpoint hooks and with debugfs through `debugfs_show_mqd` callbacks.

## Risks
Bitfield shifts and memory type/ATC choices are hardware ABI sensitive. Queue-size calculations use `order_base_2`, so invalid or non-power-of-two sizes can produce wrong ring encodings if not validated earlier. Restored MQDs trust checkpointed raw data except for doorbell rewrites. CWSR and trap fields must match process-level TBA/TMA setup. The EOP size clamp is a specific hardware workaround and is easy to regress.

## Test signals
Exercise compute, AQL, PM4, HIQ/DIQ, and SDMA queue creation on VI ASICs; update CU masks and priority; suspend/preempt/restore queues; CRIU checkpoint/restore queues; inspect MQDs through debugfs; verify CWSR wave-state reporting and EOP-size boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager.c

## Purpose
Provides the generic packet-manager layer that sends scheduler PM4 commands through the HIQ kernel queue and builds runlist IBs from DQM process/queue lists. ASIC-specific packet layouts are supplied by `packet_manager_funcs`.

## Important APIs, types, and functions
- `pm_init` selects VI, v9, or Aldebaran packet builders and initializes the HIQ kernel queue.
- `pm_send_set_resources`, `pm_send_runlist`, `pm_send_query_status`, `pm_send_unmap_queue`, and `pm_config_dequeue_wait_counts` serialize scheduler commands.
- `pm_create_runlist_ib` emits map-process and map-queue packets into a GTT IB.
- `pm_calc_rlib_size` computes IB size and oversubscription flags.
- `pm_release_ib` frees the active runlist IB.

## Control flow
`pm_init` selects the function table from ASIC type or GC version, creates a HIQ kernel queue, and initializes `pm->lock`. Command senders acquire the lock, reserve packet space from the kernel queue, call the ASIC builder, and submit or roll back. Runlist submission first allocates a runlist IB, writes process and queue packets grouped by XNACK mode, optionally appends a chained runlist packet for oversubscription, then submits a top-level runlist packet through HIQ.

## State and persistence behavior
`struct packet_manager` holds the selected vtable, HIQ queue, active IB memory object, allocation state, IB size, oversubscription flag, and lock. The runlist IB remains allocated after successful submission until `pm_release_ib`, allowing debugfs inspection of the active runlist. The manager does not persist user queues itself; it reflects DQM lists and counters at build time.

## Dependencies and integration points
Depends on DQM counters and queue lists, `struct qcm_process_device`, kernel queue packet-buffer APIs, GTT suballocation, ASIC-specific packet managers, and `kfd_priv.h` PM declarations. Debugfs can dump the active runlist or intentionally submit malformed data to hang HWS in debug builds.

## Risks
Runlist size depends on DQM counters matching actual list contents; stale counts can lead to overflow, underallocation, or `-ENOMEM`. Mixed XNACK processes cause a two-pass runlist and chained mode on affected GPUs. All command senders require correct rollback on builder failure. `pm->allocated` is single-IB state, so missing `pm_release_ib` blocks future allocation.

## Test signals
Test runlist generation for no queues, multiple processes, SDMA/static/user queues, oversubscription, and mixed XNACK. Inject kernel-queue allocation failure and ASIC builder errors to validate rollback. Verify debugfs runlist dump, set-resources, query-status fence completion, unmap filters, and dequeue-wait configuration on supported GC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c

## Purpose
Builds PM4 MES packets for GFX9+ HWS scheduling, including generic v9 packets and the Aldebaran/GFX9.4.x per-debug-VMID map-process variant.

## Important APIs, types, and functions
- `kfd_v9_pm_funcs` and `kfd_aldebaran_pm_funcs` export packet-builder vtables.
- `pm_map_process_v9` and `pm_map_process_aldebaran` fill process context packets.
- `pm_runlist_v9`, `pm_set_resources_v9`, `pm_map_queues_v9`, `pm_unmap_queues_v9`, and `pm_query_status_v9` build scheduler control packets.
- `pm_config_dequeue_wait_counts_v9` emits a `WRITE_DATA` MMIO packet for dequeue wait-count tuning.

## Control flow
The generic packet manager passes pre-reserved packet buffers to these builders. Map-process packets encode PASID, DIQ/debug flags, process quantum, GDS/GWS/OAC, SDMA enable, queue count, trap handler addresses, GDS context, and page-table base. Aldebaran additionally writes SPI debug control, watch points, and single-mem-op debug mode. Map-queues selects compute or SDMA engines, including extended SDMA engine selectors for engines 8-15. Unmap-queues chooses preempt or reset and one of PASID/all/non-static filters. Query-status writes a fence-only-after-write-ack packet.

## State and persistence behavior
The file has no owned persistent state. It serializes data from `qcm_process_device`, `kfd_process_device`, `queue`, `device_queue_manager`, and device capabilities into binary PM4 packet buffers.

## Dependencies and integration points
Depends on `kfd_pm4_headers_ai.h`, `kfd_pm4_headers_aldebaran.h`, opcode definitions, DQM wait-time state, KFD debug flags, process runtime debug state, watch-point storage, isolation settings, XNACK chain flags, and `kfd2kgd->build_dequeue_wait_counts_packet_info`.

## Risks
This is a binary firmware contract: field widths, packet sizes, and enum values must match MES firmware expectations. SDMA engine selection differs across SDMA IP versions and high engine IDs. Debug and isolation fields can alter scheduling semantics. Dequeue-wait tuning is allowed only for specific GC ranges; returning `-EPERM` in the builder can roll back packet submission.

## Test signals
Validate packet dword dumps for GFX9, GFX9.4.3, GFX9.5, and Aldebaran paths. Cover debug trap enabled/disabled, watch points, SR-IOV XNACK support, isolation mode, SDMA engine IDs below and above 8, unmap filters, reset/preempt actions, and dequeue wait-count init/reset/set commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_vi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_vi.c

## Purpose
Builds VI/CIK-compatible PM4 MES packets and provides the shared `pm_build_pm4_header` helper used by VI and later packet managers.

## Important APIs, types, and functions
- `pm_build_pm4_header` creates type-3 PM4 headers from opcode and packet byte size.
- `kfd_vi_pm_funcs` exports the VI packet-manager vtable.
- Builders cover map-process, runlist, set-resources, map-queues, unmap-queues, query-status, and VI release-mem packets.

## Control flow
The generic packet manager calls these functions with packet-sized buffers. Map-process serializes PASID, DIQ flag, page-table base, SH memory registers, hidden private base, GDS context, GWS/OAC/GDS sizing, and queue count. Runlist encodes IB address, size, chain, valid bit, and concurrent process count. Map-queues chooses compute or SDMA engine and queue type, then writes doorbell, MQD address, and write-pointer address. Unmap-queues applies PASID/all/non-static filters. Query-status writes a completion fence command. Release-mem emits cache flush/invalidate with interrupt-after-write-confirm semantics.

## State and persistence behavior
No owned state. The output packet buffers are transient command payloads submitted by `kfd_packet_manager.c` through the HIQ.

## Dependencies and integration points
Depends on `kfd_pm4_headers_vi.h`, `kfd_pm4_opcodes.h`, queue and process-device state from `kfd_priv.h`, and DQM resource values. CIK chips reuse the VI packet structures through `pm_init`.

## Risks
Header `count` calculation and packet structure sizes must stay aligned. VI and CIK use narrower fields than AI/v9 headers, especially doorbell offsets, page-table base, GDS heap sizes, and runlist high-address encoding. Unsupported queue types are rejected with `WARN` and `-EINVAL`; callers must roll back.

## Test signals
Compare emitted packet dwords against firmware specs for CIK and VI chips. Exercise compute and SDMA map queues, runlist chaining, set resources, unmap filters, query-status fences, and release-mem completion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_vi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers.h

## Purpose
Defines a small legacy PM4 type-3 header and map-process packet layouts used by older KFD packet code, plus the cache-flush event constant shared by release-mem packets.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER` exposes opcode, count, and type fields.
- `struct pm4_map_process` and `struct pm4_map_process_scratch_kv` describe map-process packet payloads for legacy hardware variants.
- `CACHE_FLUSH_AND_INV_TS_EVENT` names the release-mem event type.

## Control flow
This header contains no executable control flow. Included C files cast dword buffers to these structures and write bitfields before submitting them to firmware.

## State and persistence behavior
No runtime state. The structs are binary packet contracts; their layout effectively persists as an ABI with command processor/MES firmware.

## Dependencies and integration points
Uses standard fixed-width integer types from including files. Protected with `PM4_MES_HEADER_DEFINED` and per-structure include guards so it can coexist with generation-specific PM4 headers.

## Risks
Compiler bitfield layout, field widths, and spelling differences (`u32all` versus `u32All` in other headers) are fragile. Layout changes break firmware command decoding. Legacy structs overlap conceptually with VI/AI headers, so accidental mixed inclusion can select the wrong packet shape.

## Test signals
Build all KFD packet-manager variants with this header included transitively; validate `sizeof` and emitted dwords for legacy MAP_PROCESS packets if the legacy path is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_ai.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_ai.h

## Purpose
Defines AI/GFX9-era MES PM4 packet layouts used by `kfd_packet_manager_v9.c`, including set-resources, runlist, map-process, map-queues, query-status, unmap-queues, release-mem, and write-data MMIO packets.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER` with `u32All` storage.
- Packet structs: `pm4_mes_set_resources`, `pm4_mes_runlist`, `pm4_mes_map_process`, `PM4_MES_MAP_PROCESS_VM`, `pm4_mes_map_queues`, `pm4_mes_query_status`, `pm4_mes_unmap_queues`, `pm4_mec_release_mem`, and `pm4_mec_write_data_mmio`.
- Enum groups define queue types, engine selectors, extended SDMA selectors, unmap actions, query commands, release-mem modes, and write-data MMIO controls.

## Control flow
No executable control flow. Packet-manager code zeroes one of these structs, writes header and bitfields, then submits the resulting dwords.

## State and persistence behavior
No local runtime state. These definitions are a hardware/firmware ABI and therefore persistent across command submissions and checkpoint compatibility expectations.

## Dependencies and integration points
Consumed primarily by v9 and Aldebaran packet builders. Includes extended engine selectors for SDMA0-7 and SDMA8-15 and a `WRITE_DATA` packet shape used to tune dequeue wait counts.

## Risks
Generated-style bitfields are sensitive to compiler and architecture assumptions used by the kernel. Small field-width differences from VI, especially doorbell offset width, GDS size high bits, XNACK retry disable check, and extended engine selector fields, can cause silent scheduler failure. Packet `sizeof` values are used directly for PM4 header counts and runlist sizing.

## Test signals
Compile-time checks through users of every packet struct; runtime packet dump comparison for set-resources, map-process, map-queues with high SDMA engines, unmap, query-status, release-mem, and dequeue wait-count write-data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_ai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_aldebaran.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_aldebaran.h

## Purpose
Adds the Aldebaran/GFX9.4.x `MAP_PROCESS` packet variant with per-debug-VMID fields used when KFD needs debug trap state, watch points, and SPI debug controls in process mapping.

## Important APIs, types, and functions
- `struct pm4_mes_map_process_aldebaran` extends the AI map-process layout.
- Extra fields include `single_memops`, `tmz`, `spi_gdbg_per_vmid_cntl`, and `tcp_watch_cntl[4]`.

## Control flow
No executable control flow. `pm_map_process_aldebaran` in `kfd_packet_manager_v9.c` writes this struct and advertises its `sizeof` through `kfd_aldebaran_pm_funcs`.

## State and persistence behavior
No owned runtime state. The packet layout persists as a firmware ABI for process-debug mapping.

## Dependencies and integration points
Requires `PM4_MES_TYPE_3_HEADER` from an already included generation header. Integrates with `kfd_process_device` debug fields (`spi_dbg_override`, `spi_dbg_launch_mode`, `watch_points`) and process debug flags.

## Risks
This header has no standalone include guard for the common PM4 header, so include order matters. Any size or bitfield mismatch breaks Aldebaran process mapping. Watch-point array size is fixed at four and must match device debug capability assumptions.

## Test signals
Build with `kfd_pm4_headers_ai.h` included first; inspect Aldebaran map-process dwords with debug trap enabled, watch points configured, and single-mem-op flag set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_aldebaran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_vi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_vi.h

## Purpose
Defines VI-generation MES PM4 packet layouts consumed by `kfd_packet_manager_vi.c`.

## Important APIs, types, and functions
- `union PM4_MES_TYPE_3_HEADER`.
- Packet structs: `pm4_mes_set_resources`, `pm4_mes_runlist`, `pm4_mes_map_process`, `pm4_mes_map_queues`, `pm4_mes_query_status`, `pm4_mes_unmap_queues`, and `pm4_mec_release_mem`.
- Enums define VI queue selectors, queue types, engine selectors, unmap actions, query commands, release-mem event/cache/destination/interrupt/data selections.

## Control flow
No executable code. The VI packet manager writes these structs into command buffers.

## State and persistence behavior
No local state. Struct layouts form the VI firmware command ABI and are reflected in runlist IBs and HIQ packets.

## Dependencies and integration points
Consumed by VI and CIK-compatible packet manager paths. Field widths match older hardware limits such as 21-bit doorbell offsets and 16-bit high runlist address field.

## Risks
Do not interchange with AI/v9 packet headers: fields such as `gds_heap_base`, `gds_heap_size`, doorbell offsets, and runlist high address differ. `sizeof` drives PM4 header counts, so padding changes would be hazardous.

## Test signals
Compile packet-manager VI path and compare emitted dwords for all packet structs. Include queue map/unmap for compute and SDMA, set-resources masks, runlist chaining, and release-mem cache flush events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_headers_vi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_opcodes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_opcodes.h

## Purpose
Defines PM4 IT opcode values and PM4 packet type constants used by KFD packet builders.

## Important APIs, types, and functions
- `enum it_opcode_type` includes general PM4 opcodes and KFD/MES-specific scheduler opcodes: `IT_SET_RESOURCES`, `IT_MAP_PROCESS`, `IT_MAP_QUEUES`, `IT_UNMAP_QUEUES`, `IT_QUERY_STATUS`, and `IT_RUN_LIST`.
- `PM4_TYPE_0`, `PM4_TYPE_2`, and `PM4_TYPE_3` constants identify packet formats.

## Control flow
No executable code. Packet builders pass opcode constants to `pm_build_pm4_header`.

## State and persistence behavior
No runtime state. Values are firmware ABI constants and must remain stable.

## Dependencies and integration points
Included by VI and v9 packet-manager implementations. The opcode constants are encoded into `PM4_MES_TYPE_3_HEADER`.

## Risks
Changing numeric values breaks command processor decoding. The enum mixes many graphics/compute PM4 commands with KFD scheduler commands, so accidental reuse or typo in packet builders can submit a valid but wrong opcode.

## Test signals
Packet-builder dword dumps should show expected opcodes for every PM4 packet. Build coverage should include both VI and v9 packet managers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_pm4_opcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_priv.h

## Purpose
Central private KFD header declaring process, device, queue, packet-manager, CRIU, doorbell, event, topology, interrupt, SVM, and debugfs contracts shared across the AMD KFD driver.

## Important APIs, types, and functions
- Core device types: `struct kfd_dev`, `struct kfd_node`, `struct kfd_device_info`, `struct kfd_mem_obj`.
- Queue types: `struct queue_properties`, `struct queue`, `struct process_queue_manager`, `struct qcm_process_device`, `struct process_queue_node`.
- Process types: `struct kfd_process_device`, `struct svm_range_list`, `struct kfd_process`.
- CRIU structs: process, device, BO, queue, event, and SVM private data.
- Packet-manager contracts: `struct packet_manager`, `struct packet_manager_funcs`, PM send APIs, and PM4 header helper.
- Function prototypes cover process lifecycle, queue management, MQD managers, DQM, kernel queues, doorbells, events, topology, interrupts, CWSR, and debugfs.

## Control flow
The header has inline helpers only. `kfd_flush_tlb` calls the amdgpu VM TLB flush for a PDD. `kfd_flush_tlb_after_unmap`, `kfd_devcgroup_check_permission`, `kfd_is_first_node`, `kfd_node_by_irq_ids`, and small GPU-ID/PDD lookup helpers encode common policy.

## State and persistence behavior
This file defines the persistent in-kernel state layout for KFD processes and queues: queue BO references, MQD pointers, PDD IDRs, doorbell bitmaps, eviction fences/work items, sysfs kobjects, SVM ranges, debug trap state, CRIU private data, and per-process context IDs. It also defines user-visible CRIU private structure versioning.

## Dependencies and integration points
Pulls in Linux MMU notifier, workqueue, mutex, spinlock, IDR, sysfs, DRM, amdgpu, kgd-kfd interface, and KFD UAPI headers. Nearly every file in this group depends on these definitions.

## Risks
Because this is the shared internal ABI, field ownership and locking comments are critical. Queue active/evicted/suspended/GWS state is DQM-lock protected but exposed through multiple call paths. CRIU private structure changes require `KFD_CRIU_PRIV_VERSION` updates. Doorbell and mmap offset bit encodings are user-visible. Inline permission and IRQ node matching must handle partitioned/multi-AID devices correctly.

## Test signals
Full KFD build coverage, queue lifecycle tests, CRIU checkpoint/restore compatibility tests, SVM page-fault tests, debug trap attach/detach, sysfs/procfs visibility, doorbell mmap, device-cgroup permission tests, and suspend/resume eviction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process.c

## Purpose
Owns KFD process lifecycle, lookup, sysfs/procfs exposure, process-device state, MMU-notifier teardown, CWSR setup, VM binding, eviction/restore work, interrupt drain, exception delivery, and process cleanup.

## Important APIs, types, and functions
- Global process table: `kfd_processes_table`, `kfd_processes_mutex`, and `kfd_processes_srcu`.
- Lifecycle: `kfd_create_process`, `create_process`, `kfd_unref_process`, `kfd_process_notifier_release_internal`, `kfd_cleanup_processes`.
- Process-device setup: `kfd_create_process_device_data`, `kfd_process_device_init_vm`, `kfd_bind_process_to_device`.
- Lookup: `kfd_lookup_process_by_pid`, `kfd_lookup_process_by_pasid`, `kfd_lookup_process_by_mm`, `kfd_lookup_process_by_id`.
- Eviction/restore: `kfd_process_evict_queues`, `kfd_process_restore_queues`, `evict_process_worker`, `restore_process_worker`, suspend/resume helpers.
- CWSR/trap: `kfd_process_init_cwsr_apu`, dGPU CWSR helpers, `kfd_process_set_trap_handler`, `kfd_process_set_trap_debug_flag`.
- Observability: procfs/sysfs queue, VRAM, SDMA, eviction, CU occupancy, SVM counters.

## Control flow
`kfd_create_process` pins the mm, flushes stale release work, locks process creation, finds an existing primary process or calls `create_process`, creates sysfs/debugfs entries, and returns a referenced process. `create_process` initializes process state, events, PQM, apertures/PDDs, SVM ranges, process hash entry, MMU notifier, and context ID. MMU notifier release removes the process from the hash table, cancels eviction/restore work, dequeues all devices, uninitializes queues, disables debug traps, and drops the notifier reference. Final kref release runs on `kfd_process_wq` to wait for GPU resets, signal eviction fences, free BOs/SVM/PDDs/events/sysfs, and free the process.

## State and persistence behavior
Persistent state includes per-mm process hash entries, krefs, lead-thread reference, PDD array, PQM queues, event IDR, eviction fence, delayed work, SVM range list, sysfs kobjects, debug state, runtime-enable state, exception masks/status, and context IDs. PDDs retain DRM VM ownership, PASID, BO IDRs, doorbells, CWSR/IB allocations, proc context memory, runtime-PM references, and per-device counters. Eviction is reference-counted by DQM and coordinated with dma fences and delayed restore retries.

## Dependencies and integration points
Integrates with amdgpu VM and reset domains, runtime PM, DQM, PQM, KFD events, SVM, SMI events, KFD debug trap code, sysfs/kobject infrastructure, mmu notifiers, workqueues, DRM file/private VM objects, and `kfd_priv.h` contracts.

## Risks
This file is concurrency heavy. Races exist around mmu-notifier release versus driver cleanup, process lookup under SRCU, delayed eviction/restore work, GPU reset completion, sysfs removal, and debug trap cleanup. Some comments document lock-order hazards, such as SDMA activity reads avoiding DQM lock while using `get_user`. The context-ID free helper appears sensitive to primary/secondary logic. CWSR mappings differ between APU and dGPU and must not outlive process memory. Exception delivery uses temporary work and `kthread_use_mm`.

## Test signals
Create/destroy processes across exec and mm teardown; open multiple contexts; bind DRM VMs and PASIDs; unload driver with live processes; run queue eviction/restore under memory pressure and suspend/resume; exercise runtime PM; validate sysfs/procfs entries and SDMA/CU counters; test CWSR mmap, trap handler chaining, interrupt drain, exception event delivery, debug attach/detach, and SVM cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process_queue_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process_queue_manager.c

## Purpose
Implements the per-process queue manager. It allocates queue IDs, creates/destroys user queues, updates queue properties and MQDs, manages GWS assignment, exposes queue snapshots/wave state, and checkpoints/restores queues for CRIU.

## Important APIs, types, and functions
- `pqm_init` and `pqm_uninit` manage `process_queue_manager` lists and qid bitmap.
- `pqm_create_queue`, `pqm_destroy_queue`, `pqm_update_queue_properties`, `pqm_update_mqd`, and `pqm_set_gws` are the core queue lifecycle/update APIs.
- `kfd_process_dequeue_from_device` and `kfd_process_dequeue_from_all_devices` terminate DQM process mappings.
- `kfd_process_get_queue_info`, `kfd_criu_checkpoint_queues`, `kfd_criu_restore_queue`, and checkpoint helpers pack/unpack queue private state.
- `pqm_debugfs_mqds` dumps MQDs through DQM MQD managers.

## Control flow
Queue creation finds or assigns a qid, registers the process with DQM if this is the first queue, optionally allocates MES process context, initializes a user queue, and calls `dqm->ops.create_queue` with optional restore MQD/control-stack data. On success it returns a relative doorbell offset and adds the queue to PQM/procfs. Destroy finds the queue, unrefs BO VAs, calls DQM destroy, removes procfs, releases BOs, frees GWS/MES resources, clears qid, and unregisters the process if it has no queues. Updates validate replacement ring mapping or CU mask constraints before calling DQM update.

## State and persistence behavior
PQM owns a linked list of `process_queue_node` and a bitmap of allocated queue IDs. Queue objects persist until destroy/uninit and carry BO references, MQD pointers, DQM placement, doorbell IDs, GWS state, and MES auxiliary BOs. CRIU persistence stores queue properties, doorbell IDs, GWS flag, SDMA ID, MQD bytes, and control-stack data in `kfd_criu_queue_priv_data` followed by variable data.

## Dependencies and integration points
Depends on DQM ops, kernel queue code, amdgpu GWS helpers, amdgpu reset/MES helpers, queue buffer pinning helpers from `kfd_queue.c`, CRIU structs from `kfd_priv.h`, procfs queue hooks, and MQD-manager checkpoint/debug callbacks.

## Risks
Error paths must clear qid bitmap bits and unregister first-queue process state. Some paths return `-1` instead of a specific errno. MES auxiliary allocations must be freed on every failure and destroy path. Queue BO reference/unreference order is important to keep GPUVM mappings alive while hardware can access them. CRIU restore trusts user-provided sizes after bounds checks and passes raw MQD data to DQM restore. CU masks on WGP ASICs must be pairwise enabled.

## Test signals
Create/destroy compute, SDMA, XGMI SDMA, and SDMA-by-engine queues; hit max queue limits; test first/last queue process register/unregister; update rings and CU masks; assign/remove GWS; exercise MES and non-MES paths; CRIU checkpoint/restore queues with MQD/control-stack data; debugfs MQD dump across XCCs; inject DQM failures to verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process_queue_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_queue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_queue.c

## Purpose
Provides basic queue object allocation/debug printing, user queue buffer validation/reference management, SVM fallback references for CWSR buffers, and topology-derived context save/restore sizing.

## Important APIs, types, and functions
- `init_queue`, `uninit_queue`, `print_queue_properties`, and `print_queue`.
- `kfd_queue_buffer_get`, `kfd_queue_buffer_put`, `kfd_queue_acquire_buffers`, `kfd_queue_release_buffers`, `kfd_queue_unref_bo_va`, and `kfd_queue_unref_bo_vas`.
- SVM helpers `kfd_queue_buffer_svm_get` and `kfd_queue_buffer_svm_put` when HSA SVM is enabled.
- `kfd_queue_ctx_save_restore_size` computes CWSR, control-stack, debugger, and EOP sizes for topology.

## Control flow
Queue creation copies caller-supplied properties into a zeroed `struct queue`. Buffer acquisition reserves the process VM root BO, validates and refs write/read pointer pages and ring BO, then for compute queues validates EOP and CWSR sizes against topology. CWSR first tries a normal GPUVM BO mapping; if that fails, it drops the VM reservation and tries SVM range references. Release drops BO refs and SVM queue refs. Unref helpers decrement GPUVM `queue_refcount` while the VM root is reserved.

## State and persistence behavior
The queue object owns a copy of `queue_properties`; those properties hold BO references for write pointer, read pointer, ring, EOP, and CWSR. GPUVM mappings track `queue_refcount`; SVM ranges track `queue_refcount` for queue-pinned ranges. Topology node properties persist computed sizes used by later queue validation and userspace ABI reporting.

## Dependencies and integration points
Depends on amdgpu VM mapping lookup/reference APIs, KFD topology, SVM range management, queue properties from `kfd_priv.h`, and device XCC/topology data. PQM calls these helpers during queue create/destroy/update.

## Risks
Expected-size checks must match userspace queue layout, including AQL half-size behavior on GFX7/GFX8. BO VA refcount decrement and BO unref must stay paired. SVM fallback only applies to CWSR and requires ranges to be GPU-accessible and always mapped. CWSR sizing is hardware-generation-specific and can underallocate debug or wave state if formulas are wrong.

## Test signals
Queue creation with valid and invalid write/read/ring/EOP/CWSR mappings; AQL queue size behavior on GFX7/GFX8; CWSR SVM fallback; queue destroy refcount cleanup; topology size outputs for GFX8, GFX9, GFX10, GFX11, and GFX12 variants; debug-memory and EOP buffer size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_queue.c -->
