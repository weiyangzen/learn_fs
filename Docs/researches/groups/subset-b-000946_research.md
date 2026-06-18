# subset-b-000946 Research

Grouped research for HabanaLabs common driver sources under `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_submission.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_submission.c

## Purpose
Implements the core HabanaLabs command-submission and wait paths. The file accepts userspace CS ioctls, validates command chunks, creates `hl_cs` and `hl_cs_job` objects, parses user command buffers through ASIC-specific parsers, schedules work on hardware queues, manages fences and command sequence numbers, handles staged submissions, implements signal/wait synchronization streams with SOB accounting, and exposes wait ioctls for single CS, multi-CS, and user interrupt completion.

## Important APIs, Types, And Functions
Primary entry points are `hl_cs_ioctl()` and `hl_wait_ioctl()`. `hl_cs_ioctl()` dispatches normal execution, signal/wait, collective wait, encapsulated signal reserve/unreserve, engine control, and PCI HBW flush commands. `hl_wait_ioctl()` dispatches single CS waits, multi-CS waits, and interrupt waits.

Important lifecycle helpers include `allocate_cs()`, `cs_do_release()`, `cs_rollback()`, `hl_cs_rollback_all()`, `hl_complete_job()`, `cs_timedout()`, `cs_parser()`, `hl_cs_allocate_job()`, `hl_cs_sanity_checks()`, `hl_cs_copy_chunk_array()`, and `validate_queue_index()`. Fence helpers are `hl_fence_init()`, `hl_fence_get()`, `hl_fence_put()`, `hl_ctx_get_fence()`, `hl_wait_for_fence()`, and `_hl_cs_wait_ioctl()`.

Sync-stream and signal APIs include `hl_gen_sob_mask()`, `hl_cs_signal_sob_wraparound_handler()`, `cs_ioctl_reserve_signals()`, `cs_ioctl_unreserve_signals()`, `cs_ioctl_signal_wait()`, `cs_ioctl_extract_signal_seq()`, and `cs_ioctl_signal_wait_create_jobs()`. Multi-CS waits are handled by `hl_multi_cs_completion_init()`, `hl_wait_multi_cs_completion_init()`, `hl_cs_poll_fences()`, and `hl_multi_cs_wait_ioctl()`. Interrupt waits are handled by `_hl_interrupt_wait_ioctl()`, `_hl_interrupt_wait_ioctl_user_addr()`, `_hl_interrupt_ts_reg_ioctl()`, `unregister_timestamp_node()`, and `hl_release_pending_user_interrupts()`.

## Control Flow
Normal execution starts in `hl_cs_ioctl()`, which validates padding, device status, CS type exclusivity, staged-submission support, and sync-stream support via `hl_cs_sanity_checks()`. It then optionally runs the context-switch restore phase through `hl_cs_ctx_switch()`. Default submissions copy the user chunk array, allocate a CS, register it in debugfs, set staged-submission metadata, validate every queue, acquire or interpret command buffers, allocate one job per chunk, increment CS references for completion-producing queues, parse external queue jobs via the ASIC parser, reject internal-only CSs that would need completion, and call `hl_hw_queue_schedule_cs()`.

Signal, wait, and collective-wait submissions use the same CS lifetime model but synthesize kernel command buffers rather than parsing user CBs. Wait CSs first resolve the referenced signal CS fence, validate that it is a signal or encapsulated-signal producer, and treat already completed or gone signal fences as no-op success. Encapsulated signal waits also resolve the reservation handle from the context signal manager and hold a kref across scheduling.

Completion flows are reference-count driven. Queue completions call `hl_complete_job()`, which releases patched CBs/userptrs, removes debugfs job state, updates timestamps for job-based completion mode, and drops the CS reference taken at scheduling time. When the CS refcount reaches zero, `cs_do_release()` completes any internal jobs, updates hardware queue CI, removes mirror/staged-list nodes, schedules the next TDR, releases staged and encapsulated-signal references, records fence error/timestamp state, pushes recent outcomes into the per-context outcome store, completes the fence, wakes multi-CS waiters, releases SOB references, and frees the CS.

Timeout handling is driven by `cs_timedout()` delayed work. It obtains a live CS reference, marks the CS timed out unless reset is skipped, captures first-time timeout error information, emits logs by CS type, requests a state dump, and either conditionally resets the device or sends notifier events. Rollback paths flush completion workqueues, iterate `hdev->cs_mirror_list`, mark CSs aborted, complete their jobs, force multi-CS completions, and release dangling encapsulated signal reservations.

Wait ioctls either look up a single fence and wait on its completion, poll/wait a bounded list of fences until one completes, or add a pending interrupt node that an interrupt handler will complete. For old sequences whose fence slot has been reused, the single-CS wait path can recover recent timestamp/error results from `ctx->outcome_store`; otherwise it reports the CS as gone.

## State And Persistence
Per-CS state lives in `struct hl_cs`: sequence, type, context, fence, jobs, queue counts, staged-submission flags, timestamp fields, timeout work, SOB metadata, and completion/abort flags. Per-job state lives in `struct hl_cs_job`: queue type/id, command buffer references, patched CB data, userptr list, work item, and debugfs list node. Per-context state is consumed through `ctx->cs_sequence`, `ctx->cs_pending`, `ctx->outcome_store`, `ctx->sig_mgr`, and `ctx->ts_reg_lock`.

The file persists recent completed outcomes in a fixed-size `hl_cs_outcome_store` using a free list, used list, and hash map. If the store is full, the oldest outcome is evicted. Hardware SOB state is reference-counted through `struct hl_hw_sob`; signal reservations and signal/wait CSs hold references until the first relevant completion releases and optionally resets the SOB. Multi-CS waits use a fixed `hdev->multi_cs_completion[]` pool. User interrupt waits temporarily link `hl_user_pending_interrupt` nodes into interrupt wait/timestamp lists and hold CB or mmap buffer references until completion or unregister.

## Dependencies And Integration Points
This file is tightly integrated with ASIC callbacks in `hdev->asic_funcs`, especially `cs_parser`, queue locks, context switch, sync-stream CB sizing, collective wait job creation, SOB reset/group reset, engine control, and queue testing. It depends on queue code (`hl_hw_queue_schedule_cs()`, `hl_hw_queue_update_ci()`), context/fence lookup from `context.c`, command-buffer and memory-manager helpers, VM/userptr pinning, debugfs registration, event notifier/reset handling in `device.c`, and UAPI structs/flags from `habanalabs_accel.h`.

It also coordinates with completion queues through `hdev->cq_wq[]`, CS completion workqueue `cs_cmplt_wq`, timestamp cleanup workqueue `ts_free_obj_wq`, common user CQ interrupts, decoder interrupts, and per-context notifier/eventfd state indirectly through reset and abort paths.

## Risks
The highest risk areas are reference ownership and race ordering. CS, fence, CB, context, SOB, encapsulated-signal handle, and pending-interrupt lifetimes overlap across user ioctl threads, completion workqueues, timeout work, reset rollback, and interrupt handlers. Missing a kref get/put or deleting a list node without the expected lock can produce use-after-free, leaked waits, or double SOB reset.

Staged submissions are sensitive because only selected CSs receive timeouts or completions; a partially submitted staged sequence can deadlock if the pending fence ring lacks room for the remaining stages. The code explicitly logs this condition in `allocate_cs()`. Multi-CS wait correctness depends on setting stream-master maps before polling fence completion and on `mcs_handling_done` preventing userspace from seeing a completion before multi-CS bookkeeping has run.

Signal/wait SOB wraparound and encapsulated-signal unreserve must stay synchronized with `prop->next_sob_val`, current SOB offset, and reservation handle state. Interrupt wait paths that read userspace completion values can race with interrupts and reset aborts; the code uses completion reinitialization and list locks, but the behavior remains concurrency-heavy. Debug/error semantics also matter: not-submitted CSs use `-EBUSY`, reset aborts use `-EIO`, TDR uses `-ETIMEDOUT`, and callers depend on these distinctions in UAPI status.

## Test Signals
Useful test coverage includes CS ioctl validation for bad padding, queue ids, invalid CB sizes, internal-only completion CSs, too many chunks, and unsupported flags; parser failure rollback; normal completion on external/HW queues; job-based vs CS-based timestamp modes; staged submissions with first/middle/last combinations; staged sequence pending-ring exhaustion; TDR with and without reset; reset rollback with active CSs; signal, wait, and collective wait success/failure; SOB wraparound; encapsulated signal reserve/unreserve and wait offsets; multi-CS waits with completed, busy, gone, and shared-stream cases; interrupt wait on kernel CQ and userspace address modes; interrupt timestamp registration reuse; and reset-induced abort of waiters.

Runtime signals include `validation_drop_cnt`, `parsing_drop_cnt`, `out_of_mem_drop_cnt`, `max_cs_in_flight_drop_cnt`, TDR logs, state dumps, `HL_NOTIFIER_EVENT_CS_TIMEOUT`, `HL_NOTIFIER_EVENT_DEVICE_RESET`, debugfs CS/job lists, and fence wait statuses returned through the UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/command_submission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/context.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/context.c

## Purpose
Owns HabanaLabs context lifetime. It creates per-file user contexts, initializes kernel and user context state, manages ASIDs, VM/CB VA resources, pending CS fence rings, recent outcome storage, timestamp-registration locking, and encapsulated-signal reservation handles. It also provides the fence lookup APIs used by command submission and wait ioctls.

## Important APIs, Types, And Functions
Context lifecycle entry points are `hl_ctx_create()`, `hl_ctx_init()`, `hl_ctx_do_release()`, `hl_ctx_put()`, `hl_ctx_get()`, `hl_get_compute_ctx()`, `hl_ctx_mgr_init()`, and `hl_ctx_mgr_fini()`. Fence lookup APIs are `hl_ctx_get_fence()` and `hl_ctx_get_fences()`, both built on `hl_ctx_get_fence_locked()`.

Encapsulated signal cleanup is implemented by `encaps_handle_do_release()`, `hl_encaps_release_handle_and_put_ctx()`, `hl_encaps_release_handle_and_put_sob()`, and `hl_encaps_release_handle_and_put_sob_ctx()`. The per-context signal manager is initialized and finalized by `hl_encaps_sig_mgr_init()` and `hl_encaps_sig_mgr_fini()`.

## Control Flow
`hl_ctx_create()` allocates a context, inserts it into the file-private context IDR, initializes it as a user context, takes a reference on the owning `hl_fpriv`, and stores it as the active compute context. `hl_ctx_init()` initializes common state first: refcount, sequence number, CS lock, context-switch tokens, pending fence array, outcome-store free list/hash, and hardware-block memory tracking. Kernel contexts receive ASID 0 and initialize VM/MMU plus ASIC context state. User contexts allocate a free ASID, initialize VM, CB VA pool, ASIC context state, encapsulated signal manager, and timestamp-registration mutex.

Release flows are reference-counted. `hl_ctx_do_release()` calls `hl_ctx_fini()`, clears `hpriv->ctx` under `ctx_lock`, drops the `hpriv` reference, and frees the context. `hl_ctx_fini()` releases all pending fences in the ring, finalizes debug/coresight state for user contexts, calls ASIC context cleanup, finalizes decoder context state, CB VA pool, VM, ASID, encapsulated signal manager, and timestamp mutex. Kernel context cleanup instead finalizes ASIC context, VM, and MMU state.

Fence lookup is ring-based. A sequence greater than or equal to `ctx->cs_sequence` is invalid, a sequence older than `max_pending_cs` is considered gone, and an in-window sequence returns the fence in `ctx->cs_pending[seq & (max_pending_cs - 1)]` with an added fence reference. `hl_ctx_get_fences()` performs multiple lookups under a single `cs_lock` and releases already acquired fences on error.

## State And Persistence
Persistent context state includes `asid`, `handle`, `cs_sequence`, `cs_pending[]`, `outcome_store`, context-switch tokens, VM mappings, CB VA pools, hardware-block mappings, encapsulated signal IDR, and timestamp registration lock. The context manager state is an IDR protected by a mutex inside `hl_fpriv`. The compute context is also visible through `hdev->fpriv_list` and `hpriv->ctx`.

Encapsulated signal handles persist in `ctx->sig_mgr.handles` until unreserved, consumed by CS completion, or cleaned during context/device release. Cleanup may optionally put the hardware SOB reference and/or the context reference depending on which release callback is used.

## Dependencies And Integration Points
The file integrates with ASID allocation, VM/MMU initialization, CB VA pool management, decoder context cleanup, Coresight debug mode, hardware-block memory tracking, command-submission fence waits, and file-private lifetime in `device.c`. It calls ASIC-specific `ctx_init()` and `ctx_fini()` hooks. `hl_get_compute_ctx()` coordinates with `hdev->fpriv_list_lock` and `hpriv->ctx_lock`, which makes it an important bridge between device-level reset paths and per-context resources.

## Risks
The fence ring intentionally reuses slots, so callers must correctly distinguish invalid, gone, and live fences. A caller that assumes `NULL` means error could mis-handle old completed CSs. Context release relies on every active CS and pending interrupt holding references; missing references elsewhere can allow `hl_ctx_fini()` to run while asynchronous work still dereferences the context.

Encapsulated signal finalization is subtle because different paths own different combinations of SOB and context references. `hl_encaps_sig_mgr_fini()` expects rollback to have emptied the IDR and logs a warning if handles remain, then puts SOB references without putting context references. Ordering with `idr_for_each_entry()` plus kref callbacks that remove from the same IDR should remain carefully reviewed.

## Test Signals
Coverage should include user context create/destroy, kernel context init/fini, ASID exhaustion, ASIC `ctx_init()` failure unwinding, pending fence lookup for live/future/gone sequences, multi-fence lookup error unwind, release with outstanding CS fences, release while debug mode is active, encapsulated signal handle leak cleanup, and reset paths that call `hl_get_compute_ctx()`. Debug logs for user/kernel context close, warnings about leftover encapsulated signal handles, and fence wait behavior on gone sequences are useful runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/debugfs.c

## Purpose
Implements debugfs support for HabanaLabs devices. It creates diagnostic and control nodes, reports live command buffers, command submissions, jobs, userptrs, VM mappings, MMU translations, engine-idle state, state dumps, and optional Direct I/O statistics. It also provides privileged debugfs paths for direct device memory access, DMA memory dump, monitor dump, I2C, LEDs, power state changes, timeout/debug toggles, memory scrub, and error acknowledgement.

## Important APIs, Types, And Functions
Device-level lifecycle APIs are `hl_debugfs_device_init()`, `hl_debugfs_device_fini()`, and `hl_debugfs_add_device()`. Object tracking APIs are `hl_debugfs_add_file()`, `hl_debugfs_remove_file()`, `hl_debugfs_add_cb()`, `hl_debugfs_remove_cb()`, `hl_debugfs_add_cs()`, `hl_debugfs_remove_cs()`, `hl_debugfs_add_job()`, `hl_debugfs_remove_job()`, `hl_debugfs_add_userptr()`, `hl_debugfs_remove_userptr()`, `hl_debugfs_add_ctx_mem_hash()`, and `hl_debugfs_remove_ctx_mem_hash()`. State dump ingestion is handled by `hl_debugfs_set_state_dump()`.

Read/show handlers include `command_buffers_show()`, `command_submission_show()`, `command_submission_jobs_show()`, `userptr_show()`, `vm_show()`, `userptr_lookup_show()`, `mmu_show()`, `mmu_ack_error()`, `engines_show()`, and optional `dio_*_show()` handlers. Memory and control handlers include `hl_access_mem()`, `device_va_to_pa()`, `hl_data_read32()`, `hl_data_write32()`, `hl_data_read64()`, `hl_data_write64()`, `hl_dma_size_write()`, `hl_monitor_dump_trigger()`, `hl_memory_scrub()`, `hl_device_write()`, `hl_stop_on_err_write()`, `hl_timeout_locked_write()`, I2C handlers, LED handlers, and power-state handlers.

## Control Flow
`hl_debugfs_device_init()` initializes the in-memory debugfs bookkeeping object, allocates the table of `hl_debugfs_entry` records, initializes lists/locks/semaphores/blob descriptors, and initializes config-access history state. `hl_debugfs_add_device()` binds the device debugfs root from DRM accel debugfs, creates common nodes through `add_files_to_device()`, and adds I2C/LED secured nodes only when firmware security is disabled.

The seq-file based nodes are driven by `hl_debugfs_list[]`, `hl_debugfs_open()`, and `hl_debugfs_write()`. Each table entry wires a show callback and optional write callback to a `hl_debugfs_entry`. The object-tracking add/remove functions maintain debugfs lists under spinlocks or mutexes, and show handlers walk those lists to render live state.

Direct memory access flows through `hl_access_mem()`. Device virtual addresses are translated through the active compute context and MMU when they fall in device VA ranges. Physical addresses are matched against configured PCI memory regions and dispatched to ASIC `access_dev_mem()`; non-IOMMU host-memory access can fall back to `phys_to_virt()` for mapped host ranges. Config-region accesses are logged in a fixed history ring for later dump by `hl_debugfs_cfg_access_history_dump()`.

## State And Persistence
Debugfs state lives primarily in `hdev->hl_debugfs`: root dentry, entry array, tracked file/CB/CS/job/userptr/context lists, locks, lookup settings, MMU address/ASID fields, DMA and monitor blob descriptors, state-dump ring, and optional DIO statistics. `hdev->debugfs_cfg_accesses` stores a bounded ring of recent config accesses with timestamps and access type. Device flags such as `memory_scrub_val`, `disabled`, `stop_on_err`, `timeout_jiffies`, `skip_reset_on_timeout`, `device_release_watchdog_timeout_sec`, and power state are directly exposed or mutated by debugfs nodes.

Blob data allocated by DMA and monitor dump nodes persists until overwritten or device debugfs finalization. State dumps are retained in a ring under `state_dump_sem` and can be discarded by writing a skip count to the `state_dump` node.

## Dependencies And Integration Points
The file depends on DRM accel debugfs roots, Linux debugfs/seq-file helpers, PCI, IOMMU detection, VM/MMU helpers, command-buffer and memory-manager objects, ASIC callbacks for CPU messages, memory access, DMA dump, monitor dump, idle checks, MMU error ack, protection-bit ack, power/debug operations, and optional `CONFIG_HL_HLDIO` Direct I/O helpers. It is fed by command submission, memory management, context management, and device error paths through the add/remove and state dump APIs.

## Risks
Many debugfs nodes deliberately perform privileged destructive actions: direct MMIO/memory writes, PCI power changes, suspend/resume, stop-on-error reset, device disable, memory scrub, and timeout changes. These are acceptable debugfs capabilities but need strict assumptions about debugfs access control. The direct host-memory fallback uses `phys_to_virt()` and is invalid when IOMMU mapping is present; address validation must remain conservative.

Concurrency risks include list traversal while tracked objects are removed, active compute context lookup during VM/MMU dumps, state dump ring updates while userspace reads, and config-access history dumping that unlocks while iterating copied entries. The `mmu_asid_va_write()` parser appears to require `0x` but parses from `c+3`, so input parsing deserves scrutiny because the expected offset after the space and `0x` prefix is easy to get wrong. Optional DIO debugfs paths parse file descriptors and device VAs from strings and depend on page alignment and kernel context use.

## Test Signals
Useful checks include debugfs creation/removal across successful init, failed init with exposed interfaces, and device fini; show handlers with empty and populated lists; concurrent add/remove stress for CB/CS/job/userptr tracking; MMU lookup for kernel and user ASIDs; invalid direct memory addresses; config-region access logging and dump expiry; memory scrub blocked by active compute context; DMA dump size/address validation; state dump ring read/write; stop-on-error reset trigger; I2C length validation; firmware-security gating of secured nodes; and optional DIO success/failure/stat reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/decoder.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/decoder.c

## Purpose
Provides common decoder-core support for HabanaLabs devices. It initializes per-decoder bookkeeping, handles abnormal decoder interrupts in workqueue context, converts decoder interrupt status bits into driver notifier events and reset decisions, and stops enabled decoder cores when a user context is finalized.

## Important APIs, Types, And Functions
Public APIs are `hl_dec_init()`, `hl_dec_fini()`, and `hl_dec_ctx_fini()`. Internal helpers are `dec_abnrm_intr_work()` and `dec_print_abnrm_intr_source()`. The file defines VCMD register offsets for control and IRQ status plus bit masks for ENDCMD, BUSERR, TIMEOUT, CMDERR, ABORT, and RESET abnormal interrupt sources.

## Control Flow
`hl_dec_init()` checks `hdev->asic_prop.max_dec`; if no decoder cores exist, it is a no-op. Otherwise it allocates `hdev->dec`, initializes each `struct hl_dec` with the device pointer, core id, abnormal interrupt work item, and ASIC-provided decoder base address. Missing base addresses fail initialization and free the decoder array.

When hardware schedules `dec_abnrm_intr_work()`, the worker reads the decoder VCMD IRQ status register, logs the core and decoded source bits, writes the status back to clear the interrupt, and reads it again to flush the clear. TIMEOUT marks a general hardware error and requires device reset. CMDERR maps to undefined opcode. ENDCMD, BUSERR, and ABORT map to user engine error. If reset is required, the worker adds a device reset notifier bit and calls `hl_device_cond_reset()`; otherwise it sends notifier events directly.

`hl_dec_ctx_fini()` iterates enabled decoders from `decoder_enabled_mask` and writes zero to each VCMD control register to stop decoder activity during context teardown.

## State And Persistence
Persistent state is the `hdev->dec` array. Each element stores the owning device, decoder core id, VCMD base address, and abnormal interrupt work item. No per-context decoder state is allocated in this file; context finalization performs direct register writes based on enabled-core mask.

## Dependencies And Integration Points
The file depends on `hdev->asic_prop.max_dec`, `decoder_enabled_mask`, ASIC `get_dec_base_addr()`, MMIO `RREG32/WREG32`, notifier event masks, and reset/event helpers from `device.c`. It is initialized from `hl_device_init()`, finalized from `hl_device_fini()`, and called from context teardown in `context.c`.

## Risks
The abnormal interrupt worker reads and writes device registers asynchronously, so reset/fini ordering must ensure work cannot access freed `hdev->dec` or inaccessible MMIO. Event classification is simple bitmask mapping; missing a status bit can under-report errors. TIMEOUT triggers reset, while other errors only notify userspace, so hardware behavior must match that policy. `hl_dec_ctx_fini()` assumes decoder base addresses remain valid and that stopping enabled decoders is safe during context release.

## Test Signals
Coverage should include devices with zero decoders, valid multi-decoder init, invalid base-address failure unwind, synthetic abnormal interrupt statuses for each bit, timeout-triggered conditional reset, non-timeout notifier delivery, and context finalization stopping only enabled decoder cores. Runtime signals are decoder abnormal interrupt logs, decoded source strings, notifier masks, and reset scheduling after TIMEOUT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/device.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/device.c

## Purpose
Implements the common HabanaLabs device lifecycle and device-wide services. It covers ASIC function selection, DMA allocation/mapping wrappers, direct PCI-region access, device status checks, file-private release, mmap routing, control-device creation, early/late initialization, heartbeat monitoring, suspend/resume, reset orchestration, process kill/disable during reset or removal, notifier event delivery, full device init/fini, MMIO trace helpers, captured error information, IRQ affinity, heartbeat event handling, clock throttling events, and CPLD shutdown handling.

## Important APIs, Types, And Functions
Lifecycle entry points are `hl_device_init()`, `hl_device_fini()`, `hl_device_reset()`, `hl_device_cond_reset()`, `hl_device_suspend()`, `hl_device_resume()`, `hl_device_release()`, `hl_mmap()`, `hl_device_status()`, `hl_device_operational()`, and `hl_ctrl_device_operational()`.

Initialization helpers include `device_early_init()`, `device_early_fini()`, `device_late_init()`, `device_late_fini()`, `cdev_sysfs_debugfs_add()`, `cdev_sysfs_debugfs_remove()`, and `device_init_cdev()`. Reset helpers include `cleanup_resources()`, `take_release_locks()`, `device_hard_reset_pending()`, `device_release_watchdog_func()`, `device_kill_open_processes()`, `device_disable_open_processes()`, `send_disable_pci_access()`, `handle_reset_trigger()`, and `device_heartbeat_schedule()`.

Device service APIs include DMA wrappers (`hl_asic_dma_alloc_coherent_caller()`, `hl_asic_dma_free_coherent_caller()`, `hl_asic_dma_pool_zalloc_caller()`, `hl_asic_dma_pool_free_caller()`, `hl_dma_map_sgtable_caller()`, `hl_dma_unmap_sgtable_caller()`, `hl_asic_dma_map_sgtable()`, `hl_asic_dma_unmap_sgtable()`), memory access (`hl_access_sram_dram_region()`, `hl_access_cfg_region()`, `hl_access_dev_mem()`), utilization/debug (`hl_engine_data_sprintf()`, `hl_device_utilization()`, `hl_device_set_debug_mode()`), notifier (`hl_notifier_event_send_all()`), MMIO (`hl_rreg()`, `hl_wreg()`), error capture (`hl_capture_razwi()`, `hl_handle_razwi()`, `hl_capture_page_fault()`, `hl_handle_page_fault()`, `hl_handle_critical_hw_err()`, `hl_handle_fw_err()`, `hl_capture_engine_err()`, `hl_enable_err_info_capture()`), and event handlers (`hl_eq_heartbeat_event_handle()`, `hl_handle_clk_change_event()`, `hl_eq_cpld_shutdown_event_handle()`).

## Control Flow
`hl_device_init()` performs staged bring-up. It first selects ASIC callbacks by ASIC type and runs early ASIC init, ASID init, workqueue creation, MMU interface setup, kernel memory manager setup, reset/heartbeat work initialization, locks, and device lists. It allocates user interrupt timestamp pools and common CQ interrupt resources, runs ASIC software init, initializes multi-CS completion state, hardware queues, completion queues, shadow CS queue, event queue, MMU, kernel context, state dump, debugfs bookkeeping, command-buffer pool, and decoder support. It then enables the device for firmware communication, runs hardware init and queue tests, performs late init and VM init, registers the DRM accel device, adds control/sysfs/debugfs files, initializes hwmon, schedules heartbeat, enables firmware events, and marks init done.

`hl_device_reset()` serializes reset through `reset_info.in_reset`, distinguishes hard reset, compute reset, firmware-bypass reset, delayed reset, device-release reset, and watchdog/reset-thread origins. It can schedule hard reset work instead of doing it inline. The reset path blocks new work, optionally disables firmware PCI access, marks the device disabled, flushes queue/message/open critical sections, rolls back CS resources and waiters, kills open processes for hard reset, calls ASIC `hw_fini()`, releases/recreates kernel context and MMU state for hard reset, resets queues/CQs, reruns `hw_init()`, checks idle state, tests queues, runs late init or compute-reset late init, scrubs memory, clears reset state, schedules heartbeat, and enables firmware events. Failed compute resets escalate to hard reset; failed hard resets leave the device disabled and unusable.

`hl_device_cond_reset()` either resets immediately or, when a user context exists and has event notification, schedules a device-release watchdog and notifies userspace first. This gives userspace a bounded chance to release the device before a hard reset. `hl_device_fini()` competes with reset by acquiring the reset state, disables firmware PCI access, blocks new operations, finalizes hwmon, rolls back resources, kills compute and control users, finalizes hardware/software queues, contexts, decoder, VM/MMU, interrupts, ASIC software, early resources, cdev/sysfs/debugfs, and DRM registration.

File release flows through `hl_device_release()` and `hpriv_release()`. They finalize contexts and memory managers, check whether the device is idle, reset or scrub memory as required, remove file-private entries from device lists, clear compute context active state, release notifier eventfd, and free `hl_fpriv`.

## State And Persistence
Device-wide persistent state is extensive: ASIC identity and function table, PCI regions/BAR mappings, workqueues, reset state, heartbeat state, event/completion queues, hardware queues, shadow CS queue, kernel context, memory managers, VM/MMU state, debugfs/sysfs/control device state, hwmon state, open file-private lists, notifier masks, captured error info, clock throttling state, IRQ affinity masks, and flags such as `disabled`, `init_done`, `late_init_done`, `device_fini_pending`, `device_cpu_disabled`, `is_compute_ctx_active`, `compute_ctx_in_release`, `cpld_shutdown`, and `pldm`.

Reset state persists counters and causes (`hard_reset_cnt`, `compute_reset_cnt`, `curr_reset_cause`, `prev_reset_trigger`, `reset_trigger_repeated`, `needs_reset`, `hard_reset_pending`, `watchdog_active`, `hard_reset_schedule_flags`). Captured error information stores only first occurrences for RAZWI, page fault, critical hardware error, firmware error, engine error, and CS timeout until `hl_enable_err_info_capture()` clears it.

## Dependencies And Integration Points
This file is the central integration point for the common driver. It calls ASIC-specific hooks for early/software/hardware/late init/fini, DMA, MMU, queues, reset, suspend/resume, idle checks, firmware CPU messages, queue tests, Coresight, power, memory scrub, and event enabling. It integrates with DRM accel registration, Linux cdev/device/sysfs/debugfs/hwmon, PCI power management, eventfd notifications, process/task signaling, workqueues, tracepoints, command submission rollback, context management, VM/MMU, CB pool, decoder init/fini, EQ/CQ/HW queue code, firmware loader/status, and UAPI event masks.

## Risks
Reset orchestration is the highest-risk area. It spans asynchronous heartbeat work, watchdog work, reset workqueue, user release, process killing, CS rollback, interrupt abort, hardware fini/init, and user notifications. Incorrect state transitions around `in_reset`, `in_compute_reset`, `disabled`, or `hard_reset_pending` can allow new MMIO/CS work during teardown or leave the device permanently blocked. The path deliberately escalates compute reset failures to hard reset, so error unwinding must avoid double-freeing kernel context, MMU, queues, or work items.

Device initialization has many staged allocations with labels; failure unwinding must match the successful prefix exactly. The code also intentionally exposes interfaces on some hardware-init failures for debugging, returning success-like `rc = 0` while marking the device disabled, which consumers must understand. File release can reset the device if resources remain busy, and hard reset can kill processes; these behaviors are operationally significant.

DMA address offset handling and trace wrappers must preserve scatterlist addresses correctly across map/unmap. Direct PCI-region access must restore DRAM BAR base after temporary remap. Error capture stores only the first event, so later potentially more informative events are suppressed until capture is re-enabled. IRQ affinity code depends on NUMA topology and masks out hyperthread siblings.

## Test Signals
Important tests include successful init/fini for each ASIC type, all failure-unwind labels, exposing disabled debug interfaces after hardware init failures, suspend/resume with reset on resume, heartbeat success/failure and broken PCI link reporting, immediate conditional reset vs watchdog-delayed reset, hard reset scheduling from non-reset context, reentry from reset work, compute reset escalation, process-kill retries/timeouts, device release with active CS/CB/dmabuf resources, memory scrub after release/reset, cdev/sysfs/debugfs add/remove, DMA map/unmap with device host offset, MMIO trace helpers, direct SRAM/DRAM/config access including DRAM BAR restore, captured RAZWI/page-fault/FW/HW/engine error first-event behavior, notifier eventfd delivery, clock throttling events, and CPLD shutdown blocking further resets/access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/device.c -->
