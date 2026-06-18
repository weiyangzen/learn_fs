
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
