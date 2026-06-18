# subset-b-003785 Research

Grouped research for the Xe DRM driver files listed in work item `subset-b-003785`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.h

Purpose: Defines the main Xe Linux tracepoint surface for TLB invalidation fences, execution queues, scheduler jobs/messages, hardware fences, MMIO register reads/writes, runtime/system PM transitions, EU stall reads, and max-job-count throttling. This header is consumed through the tracepoint framework and instantiated by the corresponding `CREATE_TRACE_POINTS` translation unit elsewhere in the Xe driver.

Important APIs/types/functions: It declares event classes `xe_tlb_inval_fence`, `xe_exec_queue`, `xe_exec_queue_multi_queue`, `xe_sched_job`, `xe_sched_msg`, `xe_hw_fence`, and `xe_pm_runtime`, then binds concrete events such as `xe_tlb_inval_fence_send/recv/signal/timeout`, `xe_exec_queue_create/submit/reset/kill/stop/resubmit`, `xe_sched_job_create/exec/run/free/timedout/set_error/ban`, `xe_sched_msg_add/recv`, `xe_hw_fence_create/signal/try_signal`, and PM get/put/resume/suspend variants. Standalone `TRACE_EVENT`s include `xe_reg_rw`, `xe_eu_stall_data_read`, and `xe_exec_queue_reach_max_job_count`.

Control flow: Trace calls made by other Xe subsystems expand into `TP_fast_assign` blocks that snapshot device names and selected fields from live structures, followed by `TP_printk` formatting for ftrace/perf consumers. The header ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` outside the include guard, matching Linux tracepoint generation rules.

State and persistence behavior: This file does not mutate persistent driver state. It records transient snapshots of object pointers, fence sequence numbers, GuC IDs/states, job fence errors, batch addresses, MMIO values, and caller symbols. Because events snapshot fields from live objects, call sites must pass valid objects with stable lifetime for the duration of the tracepoint.

Dependencies and integration points: Depends on Linux tracepoint macros plus Xe execution queue, scheduler job, GPU scheduler, GT, GuC execution queue, TLB invalidation, and VM headers. It integrates with call sites across queue scheduling, GuC submission, fence signaling, MMIO, and PM code. Device-name helpers use `dev_name()` through Xe device/tile/GT conversion helpers.

Risks: Tracepoint ABI changes can break userspace tooling that depends on field names or print formats. The event payloads dereference nested pointers such as `q->guc`, `job->q`, `job->fence`, and `mmio->tile`; unsafe or premature tracing around initialization/teardown could crash. Pointer logging is diagnostic-only and subject to kernel pointer formatting policy.

Test signals: Enable ftrace/perf tracepoints under `events/xe/*` and exercise queue creation/submission/reset, TLB invalidation, MMIO access, and runtime PM. KUnit or fault-injection tests around scheduler and GuC paths can assert tracepoints compile and remain available, but functional validation is primarily runtime tracing under real workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.c

Purpose: Instantiates the BO/VM/VMA tracepoints declared in `xe_trace_bo.h` by defining `CREATE_TRACE_POINTS` and including the trace header.

Important APIs/types/functions: It has no callable functions of its own. Its key interface is the generated tracepoint objects for `xe_trace_bo.h`.

Control flow: When built by the kernel tracepoint machinery, this translation unit expands the declarations in the header into definitions. The `#ifndef __CHECKER__` guard avoids confusing sparse/static checker runs with tracepoint definition expansion.

State and persistence behavior: No runtime state is stored here. Persistence is limited to generated tracepoint symbols in the module/kernel image.

Dependencies and integration points: Depends only on `xe_trace_bo.h` and the kernel trace subsystem. Linkage must remain one-definition-only; no other C file should define `CREATE_TRACE_POINTS` for this header.

Risks: If the file is omitted from the build, tracepoint declarations may compile but fail to link. If another unit also instantiates these tracepoints, duplicate-symbol build failures result.

Test signals: A kernel build with sparse and normal compiler paths validates the checker guard. Runtime evidence is the presence of BO/VMA/VM events under the Xe trace event directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.h

Purpose: Defines tracepoints for buffer object creation/validation/fault/migration, VMA bind/rebind/invalidation/eviction activity, and VM lifecycle/rebind/failure events.

Important APIs/types/functions: Event class `xe_bo` backs `xe_bo_cpu_fault`, `xe_bo_validate`, and `xe_bo_create`. `xe_bo_move` records old/new TTM placement names and `move_lacks_source`. Event class `xe_vma` backs pagefault, access-counter, bind, pagefault-bind, unbind, userptr/non-userptr rebind, invalidation, eviction, and invalidate-complete events. Event class `xe_vm` backs VM create/free/kill/cpu-bind/restart/rebind-worker events and operation failures.

Control flow: Call sites pass `struct xe_bo`, `struct xe_vma`, or `struct xe_vm`; the trace macros snapshot size, flags, VM pointer, ASID, virtual address bounds, userptr address, and placement strings. The trace include section generates declarations/definitions depending on whether a C unit defines `CREATE_TRACE_POINTS`.

State and persistence behavior: No driver state is mutated. Tracepoint state consists of per-event snapshots of memory-management state at the time of the trace.

Dependencies and integration points: Includes `xe_bo.h`, `xe_bo_types.h`, and `xe_vm.h`. It integrates with BO allocation/migration, page fault handling, VM bind/unbind, rebind workers, and userptr invalidation code. Placement names come from `xe_mem_type_to_name`, so placement indexes must be valid.

Risks: The VMA trace class dereferences `xe_vma_vm(vma)` and computes `xe_vma_end(vma) - 1`; malformed or half-initialized VMAs could produce invalid data. `xe_bo_move` indexes placement names by `new_placement` and `old_placement`; invalid memory type values would risk out-of-bounds access. Trace formats are diagnostic ABI for tooling.

Test signals: Exercise GEM object creation, CPU faults, BO migration between system/VRAM/stolen placements, VM creation/destruction, page-fault binds, and userptr invalidation while observing `events/xe/xe_bo_*`, `xe_vma_*`, and `xe_vm_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.c

Purpose: Instantiates GuC communication and engine activity tracepoints declared in `xe_trace_guc.h`.

Important APIs/types/functions: Contains no exported functions; it creates generated tracepoint definitions for GuC CT flow-control, CTB H2G/G2H messages, and GuC engine activity events.

Control flow: Defines `CREATE_TRACE_POINTS` before including `xe_trace_guc.h`, except for sparse checker builds. The Linux tracepoint machinery turns the header macros into concrete trace event definitions.

State and persistence behavior: No independent runtime state. Generated tracepoint symbols persist as part of the built driver.

Dependencies and integration points: Depends on `xe_trace_guc.h`; call sites in GuC CT and engine activity code use the generated events.

Risks: Duplicate instantiation or missing build inclusion causes tracepoint linkage issues. The checker guard must be preserved to keep static analysis clean.

Test signals: Build validation plus runtime visibility of `xe_guc_ct_*`, `xe_guc_ctb_*`, and `xe_guc_engine_activity` events under the Xe trace subsystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.h

Purpose: Provides tracepoints for GuC CT buffer flow control, H2G/G2H CTB messages, and GuC engine activity accounting snapshots.

Important APIs/types/functions: Event class `xe_guc_ct_flow_control` underlies `xe_guc_ct_h2g_flow_control` and `xe_guc_ct_g2h_flow_control`, recording head, tail, size, space, and message length. Event class `xe_guc_ctb` underlies `xe_guc_ctb_h2g` and `xe_guc_ctb_g2h`, recording GT id, action, length, tail, and head. `xe_guc_engine_activity` records metadata and activity counters from `struct engine_activity`.

Control flow: GuC communication paths emit the CT flow/CTB tracepoints around ring-buffer operations. Engine-activity sampling emits a snapshot including global/change counters, GuC TSC frequency, latency, quanta ratio, active ticks, accumulated active/total/quanta counters, and CPU timestamp.

State and persistence behavior: This header only observes GuC communication/accounting state. It snapshots values without changing queue pointers or activity counters.

Dependencies and integration points: Includes Xe device, GuC exec queue, and GuC engine activity type headers. It is consumed by GuC CT and engine utilization/statistics paths.

Risks: Ring-buffer diagnostics are only as accurate as call-site ordering; tracing before head/tail updates versus after updates changes interpretation. `xe_guc_engine_activity` assumes `struct engine_activity` is populated and stable. New GuC actions or metadata layouts may require trace format updates.

Test signals: Enable tracepoints during GuC submission, CT send/receive stress, and engine activity collection. Verify H2G and G2H events distinguish direction and that activity counters update plausibly under busy/idle engine workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.c

Purpose: Instantiates the logical-ring-context timestamp tracepoint declared in `xe_trace_lrc.h`.

Important APIs/types/functions: No direct APIs; it emits generated tracepoint definitions for `xe_lrc_update_timestamp`.

Control flow: Defines `CREATE_TRACE_POINTS` then includes the LRC trace header, guarded away from sparse checker runs.

State and persistence behavior: No mutable driver state. Only generated tracepoint metadata and symbols are produced.

Dependencies and integration points: Depends on `xe_trace_lrc.h`; LRC code calls the generated tracepoint when context timestamp changes.

Risks: Standard tracepoint instantiation risks: duplicate definitions, missing build entry, or checker incompatibility if the guard is removed.

Test signals: Build the driver and confirm `xe_lrc_update_timestamp` appears in the Xe trace event namespace when LRC timestamp updates are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.h

Purpose: Defines a focused tracepoint for logical ring context timestamp updates.

Important APIs/types/functions: `TRACE_EVENT(xe_lrc_update_timestamp)` records the `struct xe_lrc *`, old timestamp, new `lrc->ctx_timestamp`, LRC fence-context name, and device id.

Control flow: LRC update paths call the tracepoint after updating or while comparing timestamp state, passing the old timestamp so the trace entry can show old/new values.

State and persistence behavior: The tracepoint is observational only. It snapshots LRC timestamp values and string data from the fence context.

Dependencies and integration points: Includes GT and LRC headers and uses `gt_to_xe((lrc)->fence_ctx.gt)` to derive the device name. Integrated with LRC/context restore or accounting paths that maintain `ctx_timestamp`.

Risks: Callers must pass an initialized LRC with a valid `fence_ctx.gt` and name. Timestamp trace interpretation depends on call-site semantics, especially whether `old` is pre-update or last-observed state.

Test signals: Run workloads that update LRC timestamps and inspect trace output for monotonic or expected old/new transitions per context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.c

Purpose: Implements a TTM resource manager for stolen memory by extending the VRAM manager, detecting stolen-memory size/base for integrated and discrete platforms, and providing CPU/GPU offset and TTM bus mapping helpers.

Important APIs/types/functions: Internal `struct xe_ttm_stolen_mgr` embeds `struct xe_ttm_vram_mgr` and stores `io_base`, `stolen_base`, and optional WC mapping. Public functions are `xe_ttm_stolen_mgr_init`, `xe_ttm_stolen_io_mem_reserve`, `xe_ttm_stolen_cpu_access_needs_ggtt`, `xe_ttm_stolen_io_offset`, and `xe_ttm_stolen_gpu_offset`. Detection helpers include `get_wopcm_size`, `detect_bar2_dgfx`, `detect_bar2_integrated`, and `detect_stolen`.

Control flow: Initialization allocates the stolen manager with DRM-managed memory, skips SR-IOV VFs, selects a detection path for DGFX, newer integrated platforms, or legacy x86 stolen memory, then initializes the embedded VRAM manager with `XE_PL_STOLEN`. If direct CPU access is available, it maps `io_base` with `devm_ioremap_wc`. CPU bus reservation chooses between BAR2-style direct offsets and legacy GGTT-mediated stolen access.

State and persistence behavior: The manager persists as a TTM memory type manager for `XE_PL_STOLEN`. It tracks immutable base addresses and an optional CPU mapping. Allocation accounting is inherited from `xe_ttm_vram_mgr`. `xe_ttm_stolen_io_mem_reserve` mutates the passed TTM resource bus fields (`offset`, `addr`, `is_iomem`, `caching`) for CPU mapping.

Dependencies and integration points: Uses PCI BAR resources, MMIO registers (`DSMBASE`, `GGC`, `STOLEN_RESERVED`, `GSCPSMI_BASE`), WOPCM sizing, platform checks, SR-IOV checks, workarounds, Xe BO/GGTT helpers, resource cursors, and `__xe_ttm_vram_mgr_init`. Legacy x86 path relies on external `intel_graphics_stolen_res`.

Risks: Platform register interpretation is sensitive: wrong stolen base/size can overlap WOPCM, GSC PSMI reserved regions, or normal VRAM. Legacy platforms requiring GGTT CPU access need BOs with `XE_BO_FLAG_GGTT`; otherwise CPU mapping fails. `to_stolen_mgr(ttm_manager_type(...))` assumes the manager exists for offset helpers. Direct BAR mapping is intentionally disabled when CPU access must go through GGTT.

Test signals: Boot on DGFX, Xe2 integrated, pre-1270 integrated x86, and SR-IOV VF configurations; validate reported stolen size, WOPCM carveout, debug logs, BO allocation in `XE_PL_STOLEN`, CPU mmap paths, and GPU offsets. Fault paths should cover missing WOPCM size, invalid GMS/GGMS, no `io_base`, and missing GGTT flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.h

Purpose: Declares the stolen-memory manager interface used by Xe memory-management and BO mapping code.

Important APIs/types/functions: Declares `xe_ttm_stolen_mgr_init`, `xe_ttm_stolen_io_mem_reserve`, `xe_ttm_stolen_cpu_access_needs_ggtt`, `xe_ttm_stolen_io_offset`, and `xe_ttm_stolen_gpu_offset`, with forward declarations for `ttm_resource`, `xe_bo`, and `xe_device`.

Control flow: Consumers initialize stolen memory during device memory-manager setup, ask whether CPU access must be GGTT-mediated, reserve TTM bus mappings for stolen resources, and convert BO/resource offsets into CPU or GPU-visible addresses.

State and persistence behavior: The header owns no state. Its API exposes access to the hidden manager state initialized in the C file.

Dependencies and integration points: Included by BO mapping, TTM manager setup, and stolen-memory placement paths. It intentionally hides `struct xe_ttm_stolen_mgr` internals.

Risks: Callers must only use offset/reserve helpers after successful manager initialization and for `XE_PL_STOLEN` resources. Incorrect use on non-stolen BOs would produce meaningless offsets.

Test signals: Compile coverage of all callers and runtime stolen-memory allocation/mapping tests on platforms with and without stolen support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_stolen_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.c

Purpose: Implements Xe's TTM system-memory manager for TT placement (`XE_PL_TT`), providing simple resource allocation objects for system-backed buffer objects.

Important APIs/types/functions: Internal `struct xe_ttm_sys_node` wraps a `ttm_range_mgr_node` and tracks the TTM BO. Manager callbacks are `xe_ttm_sys_mgr_new`, `xe_ttm_sys_mgr_del`, and `xe_ttm_sys_mgr_debug`, collected in `xe_ttm_sys_mgr_func`. Public API is `xe_ttm_sys_mgr_init`; managed cleanup is `xe_ttm_sys_mgr_fini`.

Control flow: Init computes total RAM via `si_meminfo`, initializes `xe->mem.sys_mgr` with `use_tt = true`, registers it as `XE_PL_TT`, marks it used, and registers a DRM managed cleanup action. Allocation creates a flexible node with one range, initializes the TTM resource, refuses non-temporary allocations when manager usage exceeds size, sets `start` to `XE_BO_INVALID_OFFSET`, and returns the resource. Free finalizes and frees the node. Fini disables the manager, evicts all resources, cleans up, and unregisters the driver manager.

State and persistence behavior: Persistent state lives in `xe->mem.sys_mgr` and TTM accounting. Per-resource state is dynamically allocated and freed with BO resource lifetime. No debug state is emitted because runtime-PM wrapping would be required.

Dependencies and integration points: Depends on TTM placement/range/TT APIs, DRM managed cleanup, system memory info, and Xe BO definitions. Integrated with TTM memory placement and eviction as the system memory backend.

Risks: Usage check compares TTM usage against `man->size << PAGE_SHIFT`; unit consistency depends on TTM manager accounting. Cleanup returns early on eviction failure, which leaves manager cleanup deferred/unfinished. Debug hook is intentionally empty to avoid PM issues.

Test signals: Allocate/free TT-backed BOs, trigger temporary and non-temporary placement paths, force memory pressure/eviction, and unload/remove the driver to verify managed cleanup and no leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.h

Purpose: Declares the system-memory TTM manager initialization entry point.

Important APIs/types/functions: Forward declares `struct xe_device` and declares `int xe_ttm_sys_mgr_init(struct xe_device *xe)`.

Control flow: Memory-manager setup code calls this once during device initialization to register `XE_PL_TT`.

State and persistence behavior: No state in the header; initialized manager state lives in `xe->mem.sys_mgr`.

Dependencies and integration points: Included by device/TTM setup code that needs to register system placement.

Risks: Minimal API surface. Call ordering matters: it should occur before BOs can request TT placement and before teardown actions are needed.

Test signals: Build coverage and successful TT BO allocation after device initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.c

Purpose: Implements Xe's TTM VRAM resource manager using the DRM GPU buddy allocator, including allocation/free, placement compatibility checks, debug reporting, initialization/finalization, and DMA scatter-gather export for CPU-visible VRAM.

Important APIs/types/functions: Internal helpers `xe_ttm_vram_mgr_first_block` and `xe_is_vram_mgr_blocks_contiguous`. TTM callbacks are `xe_ttm_vram_mgr_new`, `xe_ttm_vram_mgr_del`, `xe_ttm_vram_mgr_intersects`, `xe_ttm_vram_mgr_compatible`, and `xe_ttm_vram_mgr_debug`, collected in `xe_ttm_vram_mgr_func`. Public APIs include `__xe_ttm_vram_mgr_init`, `xe_ttm_vram_mgr_init`, `xe_ttm_vram_mgr_alloc_sgt`, `xe_ttm_vram_mgr_free_sgt`, `xe_ttm_vram_get_cpu_visible_size`, `xe_ttm_vram_get_used`, and `xe_ttm_vram_get_avail`.

Control flow: Allocation clamps `lpfn`, rejects impossible sizes, allocates a `xe_ttm_vram_mgr_resource`, sets buddy flags from TTM placement flags, checks size/page alignment, locks the manager, enforces visible-memory availability for visible-only placements, allocates buddy blocks, computes visible usage, updates `visible_avail`, and records contiguous start when possible. Free returns buddy blocks and visible accounting under the same lock. Init optionally registers a DRM cgroup region, initializes the TTM manager and buddy allocator, registers the memory type, marks it used, and adds managed cleanup. SG export walks resource cursors over buddy blocks, limits SG segment size to 2 GiB, maps physical VRAM resources with `dma_map_resource`, and unwinds on errors.

State and persistence behavior: Persistent manager state includes buddy allocator state, visible-size/available counters, default page size, mutex, memory type, and TTM manager registration. Per-resource state includes the allocated buddy block list, visible bytes used, and flags. `visible_avail` is protected by `mgr->lock` and must return to `visible_size` at teardown.

Dependencies and integration points: Depends on DRM buddy, TTM resource manager, DRM managed cleanup, cgroup registration, Xe VRAM region descriptors, Xe resource cursors, DMA mapping APIs, and tile-to-VRAM IO start mapping. Used by normal VRAM placements and by stolen manager via `__xe_ttm_vram_mgr_init`.

Risks: Visible-memory accounting is a central correctness constraint; missed updates can overcommit CPU-visible BAR space or trip teardown warnings. Alignment checks rely on `default_page_size`, buddy chunk size, and BO page alignment. SG export only supports fully visible resources (`used_visible_size >= res->size`) and must unmap partially-built tables correctly. The tile calculation assumes `res->mem_type - XE_PL_VRAM0` indexes the right tile.

Test signals: Allocate/free VRAM BOs with topdown, contiguous, range-limited, and visible-only placements; verify fragmentation handling, contiguous flag inference, placement compatibility/intersection behavior, debugfs manager output, SG export/import under DMA mapping, and teardown after eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.h

Purpose: Declares the VRAM manager API and inline converters between TTM base structures and Xe VRAM manager/resource structures.

Important APIs/types/functions: Declares initialization, SG allocation/free, visible/used/available query functions, and inline `to_xe_ttm_vram_mgr_resource` plus `to_xe_ttm_vram_mgr`.

Control flow: Setup code calls init functions; memory accounting/debug code calls query functions; DMA-buf or external mapping paths call SG helpers; TTM callbacks and consumers use inline converters for container access.

State and persistence behavior: Header has no storage but exposes access to manager/resource state defined in `xe_ttm_vram_mgr_types.h`.

Dependencies and integration points: Includes `xe_ttm_vram_mgr_types.h`; forward-declares DMA direction, device, tile, and VRAM region types. Shared by regular VRAM and stolen-memory manager code.

Risks: Container helpers assume the passed base pointer really belongs to Xe VRAM manager/resource types. Misuse with non-VRAM TTM resources will corrupt interpretation.

Test signals: Compile coverage for all consumers, SG export tests, and memory-manager init paths for both `XE_PL_VRAM*` and `XE_PL_STOLEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr_types.h

Purpose: Defines the data structures backing Xe's VRAM TTM manager and its allocated resources.

Important APIs/types/functions: `struct xe_ttm_vram_mgr` contains a `ttm_resource_manager`, DRM `gpu_buddy`, CPU-visible size/accounting, default page size, allocation mutex, and TTM memory type. `struct xe_ttm_vram_mgr_resource` contains the base TTM resource, buddy block list, visible bytes consumed, and buddy allocation flags.

Control flow: These structures are initialized by `__xe_ttm_vram_mgr_init`, mutated by allocation/free callbacks, queried by debug/accounting helpers, and embedded by the stolen-memory manager.

State and persistence behavior: Manager fields persist for device lifetime. Resource fields persist for each BO's residency in VRAM/stolen placement. The mutex protects buddy allocation and visible accounting.

Dependencies and integration points: Includes Linux GPU buddy and TTM device APIs. Used by `xe_ttm_vram_mgr.c`, `xe_ttm_vram_mgr.h`, and `xe_ttm_stolen_mgr.c`.

Risks: The comment typo "Proped" is harmless, but the semantics are important: `visible_size` is the CPU-visible aperture, not total VRAM. Incorrect lock discipline around `visible_avail` or `blocks` would corrupt allocations.

Test signals: Structural validation comes from allocation/free stress, lockdep, and teardown accounting assertions that `visible_avail` returns to `visible_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.c

Purpose: Defines platform/engine/LRC tuning tables and processes them through the Xe RTP rules engine into saved-register state for GT, hardware engine, and logical-ring-context programming.

Important APIs/types/functions: Static tables `gt_tunings`, `engine_tunings`, and `lrc_tunings` contain `xe_rtp_entry_sr` entries with names, match rules, and register actions. Public functions are `xe_tuning_init`, `xe_tuning_process_gt`, `xe_tuning_process_engine`, `xe_tuning_process_lrc`, and `xe_tuning_dump`. KUnit visibility exports are provided for GT and engine processing.

Control flow: Init allocates one DRM-managed bitmap block for active tuning tracking and partitions it among GT, engine, and LRC arrays. Processing functions create an RTP context for the target object, enable active tracking against the matching bitmap, and call `xe_rtp_process_to_sr` to append register actions to `gt->reg_sr`, `hwe->reg_sr`, or `hwe->reg_lrc`. LRC processing marks actions as context-image actions. Dump walks active bitmaps and prints applied tuning names.

State and persistence behavior: Persistent state is the active tuning bitmaps stored under `gt->tuning_active.*` and saved-register lists in GT/HWE objects. The table data is static const. DRM-managed allocation ties lifetime to the Xe device.

Dependencies and integration points: Depends on RTP rule/action macros, platform version checks, engine class matching, SR-IOV header availability, register definitions, and DRM printer/debug support. Integrated with GT/engine initialization and debugfs or diagnostics that dump active tunings.

Risks: Tuning tables encode hardware-specific register workarounds/performance settings; wrong platform ranges, media/graphics version rules, or engine-class filters can program invalid registers or omit required tuning. Bitmap allocation must match table sizes. LRC tunings must only target registers present in context images.

Test signals: KUnit tests can call exported processing functions against synthetic platform/engine contexts. Hardware bring-up should compare active dump output to expected tuning sets per platform/engine, and register state tests should validate saved-register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.h

Purpose: Declares the Xe tuning subsystem API for initializing, processing, and dumping GT/engine/LRC tuning state.

Important APIs/types/functions: Declares `xe_tuning_init`, `xe_tuning_process_gt`, `xe_tuning_process_engine`, `xe_tuning_process_lrc`, and `xe_tuning_dump`, with forward declarations for `drm_printer`, `xe_gt`, and `xe_hw_engine`.

Control flow: GT setup calls init and GT processing; engine setup calls engine and LRC processing; diagnostics call dump.

State and persistence behavior: No state in the header. API consumers operate on tuning state stored in GT/HWE structures.

Dependencies and integration points: Included by GT and engine initialization code and any debugfs/diagnostic printer that exposes tuning decisions.

Risks: Callers must initialize tuning bookkeeping before processing tables or dumping active bits. Missing process calls will leave saved-register tuning absent.

Test signals: Build coverage plus platform initialization tests showing tuning dump output after processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.c

Purpose: Coordinates Xe microcontroller lifecycle across GuC, HuC, GSC, and WOPCM: initialization, post-hwconfig setup, firmware load, reset/sanitize, start/stop, suspend/resume, and wedging.

Important APIs/types/functions: Public lifecycle functions are `xe_uc_init_noalloc`, `xe_uc_init`, `xe_uc_init_post_hwconfig`, `xe_uc_load_hw`, `xe_uc_reset_prepare`, `xe_uc_stop_prepare`, `xe_uc_stop`, `xe_uc_start`, `xe_uc_suspend_prepare`, `xe_uc_suspend`, `xe_uc_runtime_suspend`, `xe_uc_runtime_resume`, `xe_uc_sanitize_reset`, and `xe_uc_declare_wedged`. Internal helpers map `xe_uc` to GT/device, reset GuC, sanitize HuC/GuC, wait for reset, and handle SR-IOV VF hardware load.

Control flow: Early init initializes GuC noalloc state. Full init initializes GuC/HuC/GSC even when uC is disabled so firmware status moves to disabled, then initializes WOPCM and performs a minimal GuC load for hwconfig on enabled non-VF devices. Post-hwconfig sanitizes/resets uC, then initializes GuC/HuC/GSC post-hwconfig. Hardware load for PF uploads HuC and GuC, enables GuC communication, records default LRCs, does GuC post-load init, starts power/RC features, enables engine activity stats, attempts HuC auth without failing driver load, and starts async GSC load. VF load resets, enables communication, connects to PF, marks submission enabled, enables opt-in features, and records LRCs.

State and persistence behavior: Mutates firmware/submission/power-management state inside `uc->guc`, `uc->huc`, `uc->gsc`, and `uc->wopcm`. Most operations are no-ops when `xe_device_uc_enabled()` is false. Suspend waits for reset completion, stops GuC, and calls GuC suspend. Runtime suspend/resume delegate to GuC runtime PM.

Dependencies and integration points: Integrates with GuC, HuC, GSC, WOPCM, GT, SR-IOV VF, power control, render C-state, engine activity, default LRC recording, and wedge handling. Uses GT logging and assertions.

Risks: Lifecycle ordering is critical: communication must be enabled after firmware upload, WOPCM must exist before loading, reset/sanitize must clear stale states, and GSC async load must be stopped/waited during suspend/stop prepare. HuC auth failures are logged but non-fatal by design. VF path diverges significantly and relies on PF-preloaded firmware.

Test signals: Boot/load, GT reset, suspend/resume, runtime PM, SR-IOV VF startup, GuC disabled mode, HuC auth failure, and wedge tests. Trace/log evidence should show firmware upload, GuC communication, RC/PC startup, and non-fatal HuC handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.h

Purpose: Declares the public uC lifecycle interface for Xe GT code.

Important APIs/types/functions: Exposes initialization, post-hwconfig setup, hardware load, reset prepare, runtime suspend/resume, stop prepare/stop/start, suspend prepare/suspend, sanitize reset, and wedge declaration functions for `struct xe_uc`.

Control flow: Device/GT probe and reset paths call init/load/start; suspend/runtime PM paths call suspend/resume helpers; error paths call reset prepare or wedge declaration.

State and persistence behavior: Header has no state; functions mutate the `xe_uc` aggregate declared in `xe_uc_types.h`.

Dependencies and integration points: Forward-declares `struct xe_uc` to keep compile dependencies small. Included by GT lifecycle, reset, PM, and wedge handling code.

Risks: API call order matters. Calling start/stop/load before init or when firmware state is invalid can produce delegated GuC/HuC/GSC errors.

Test signals: Compile coverage and lifecycle integration tests across probe, reset, suspend/resume, and GuC-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.c

Purpose: Registers the debugfs subtree for Xe microcontroller diagnostics.

Important APIs/types/functions: Public function `xe_uc_debugfs_register(struct xe_uc *uc, struct dentry *parent)` creates a `uc` debugfs directory and delegates registration to GSC, GuC, and HuC debugfs helpers.

Control flow: Debugfs setup calls this with the parent GT/device debugfs dentry. The function creates `uc`; if creation fails, it warns and returns. Otherwise it calls `xe_gsc_debugfs_register`, `xe_guc_debugfs_register`, and `xe_huc_debugfs_register`.

State and persistence behavior: Persists debugfs dentries/files until debugfs teardown. Does not mutate firmware state, only exposes diagnostics/control surfaces supplied by child subsystems.

Dependencies and integration points: Depends on Linux debugfs, DRM debugfs, Xe GSC/GuC/HuC debugfs helpers, macros, and `xe_uc_types.h`.

Risks: `debugfs_create_dir` failures are non-fatal. Child registration assumes `uc` substructures are initialized enough for their debugfs callbacks. Debugfs callbacks may need PM/runtime locking in child code.

Test signals: Mount debugfs and verify `uc` directory plus GSC/GuC/HuC entries appear for a GT. Inject debugfs creation failure or run with debugfs disabled to confirm graceful behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.h

Purpose: Declares uC debugfs registration.

Important APIs/types/functions: Forward declares `struct dentry` and `struct xe_uc`, and declares `xe_uc_debugfs_register`.

Control flow: Debugfs setup code uses this to attach the uC diagnostics subtree under a parent dentry.

State and persistence behavior: No state in the header.

Dependencies and integration points: Included by higher-level debugfs setup code and implemented by `xe_uc_debugfs.c`.

Risks: Minimal. Callers must pass a valid parent dentry and initialized `xe_uc`.

Test signals: Build coverage and presence of the `uc` debugfs directory at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.c

Purpose: Implements firmware selection, request, parsing, validation, copying, upload, and printing for GuC, HuC, and GSC microcontroller firmware.

Important APIs/types/functions: Public APIs are `xe_uc_fw_init`, `xe_uc_fw_copy_rsa`, `xe_uc_fw_upload`, `xe_uc_fw_check_version_requirements`, and `xe_uc_fw_print`. Key internal pieces include firmware definition macros/tables, `uc_fw_auto_select`, `uc_fw_override`, `uc_fw_vf_override`, `uc_fw_request`, CSS/GSC parsing helpers (`parse_css_header`, `parse_cpd_header`, `parse_gsc_layout`, `parse_headers`), `uc_fw_copy`, `uc_fw_xfer`, and `uc_fw_fini`.

Control flow: Firmware init starts with autoselection by platform/GT type, applies user module-parameter overrides, handles SR-IOV VF preloaded firmware, marks unsupported/disabled states, requests the blob, parses CSS or GSC headers, checks versions, copies the firmware into a managed GGTT BO, and registers cleanup that reverts status to selected. Upload asserts the firmware is not already loaded, validates loadability, DMA-transfers the CSS header plus uCode from GGTT to WOPCM, marks `TRANSFERRED`, or marks `LOAD_FAIL` on error. Printing emits path, status, wanted/found versions, and component sizes.

State and persistence behavior: Mutates `struct xe_uc_fw`: path, user override flag, wanted/found versions, version type, full-version requirement, `has_gsc_headers`, size, BO pointer, RSA/uCode/CSS offsets, private data size, build type, and firmware status. Firmware blobs are released after copying. BO lifetime is DRM-managed. VF mode marks GuC/HuC as preloaded and suppresses local paths.

Dependencies and integration points: Uses Linux firmware loader, DRM managed actions, Xe module params, platform metadata, GT/device helpers, SR-IOV VF queries, Xe BO creation, GGTT addresses, force-wake/MMIO DMA registers, GSC/HuC/GuC ABI structures, and `linux-firmware` filenames declared with `MODULE_FIRMWARE`.

Risks: Firmware filename tables must stay ordered newest-to-oldest and platform-correct. Header parsing must validate all sizes before dereferencing untrusted firmware data. Version policy differs for force-probed/full-version-required platforms, major-only supported platforms, HuC no-version filenames, and GSC compatibility versions. DMA upload requires force-wake and correct GGTT/WOPCM offsets. User overrides bypass version failure in `xe_uc_fw_check_version_requirements`, increasing diagnostic importance.

Test signals: Boot each supported platform with matching, missing, old-minor, wrong-major, malformed CSS, malformed GSC CPD/BPDT, user override, disabled uC, and SR-IOV VF configurations. Validate status transitions, logs, BO creation, RSA copy size, DMA register programming, timeout handling, and debugfs/print output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.h

Purpose: Declares uC firmware operations and inline status/type/version helper predicates.

Important APIs/types/functions: Declares init, RSA copy, upload, version check, and print functions. Inline helpers compute RSA offset, change status, stringify status/type, map status to errno, query supported/enabled/available/loadable/loaded/running/overridden/error states, sanitize loadable firmware, compute upload size, and expose the firmware download URL.

Control flow: Firmware code and uC subcomponents use status predicates to gate operations. Upload size and RSA offset helpers are consumed by firmware transfer/authentication paths. `xe_uc_fw_sanitize` resets loadable-or-later firmware back to `LOADABLE` across reset cycles.

State and persistence behavior: `xe_uc_fw_change_status` mutates the private `__status` field. Other helpers are read-only except sanitize. Status ordering is semantically significant because predicates compare enum values.

Dependencies and integration points: Includes errno, Xe macros, firmware ABI, and firmware types. Integrated across GuC/HuC/GSC firmware loaders and diagnostics.

Risks: Enum ordering underpins helper logic; inserting statuses in the wrong location can break `>=` predicates. `__xe_uc_fw_status` warns on uninitialized checks, so callers must follow init ordering. `xe_uc_fw_is_loadable` excludes `PRELOADED` despite its high enum value.

Test signals: Unit tests for each status-to-string/error/predicate combination, reset sanitize behavior, upload-size calculation, and RSA offset calculation for CSS-at-zero and GSC-contained CSS offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_abi.h

Purpose: Documents and defines packed ABI structures and bit fields for CSS-based, GSC-based, and late-binding firmware layouts used by Xe microcontroller firmware parsing.

Important APIs/types/functions: CSS definitions include `uc_css_rsa_info`, `uc_css_guc_info`, bit masks for time/version/build/header fields, and `uc_css_header` with a `static_assert` size of 128 bytes. GSC definitions include `gsc_version`, `gsc_partition`, `gsc_layout_pointers`, `gsc_bpdt_header`, `gsc_bpdt_entry`, `gsc_cpd_header_v2`, `gsc_cpd_entry`, and `gsc_manifest_header`. Late-binding definitions include `csc_fpt_header` and `csc_fpt_entry`.

Control flow: `xe_uc_fw.c` uses these structures to validate firmware blobs, locate manifests/CSS entries, extract versions/security version, and compute uCode/RSA offsets. The header itself has no executable control flow.

State and persistence behavior: Defines on-disk/in-blob layout interpretation only. Packed structs map directly onto firmware bytes; no kernel-owned state is stored here.

Dependencies and integration points: Includes build-bug and Linux types. It is part of the ABI contract between the kernel driver and GuC/HuC/GSC firmware image formats.

Risks: Packed layout, field widths, masks, and documented entry names must match firmware producer output exactly. Any structure change without firmware-format change coordination can break parsing. Parser code must continue to bounds-check before casting to these structs.

Test signals: Firmware parser tests using known-good and malformed CSS/GSC/late-binding blobs; static size/layout assertions; cross-check extracted versions against firmware release metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_types.h

Purpose: Defines the uC firmware state machine enums, firmware type/version enums, version struct, and `struct xe_uc_fw` storage.

Important APIs/types/functions: `enum xe_uc_fw_status` models states from `NOT_SUPPORTED` and `UNINITIALIZED` through `SELECTED`, `MISSING`, `ERROR`, `AVAILABLE`, `LOADABLE`, `LOAD_FAIL`, `TRANSFERRED`, `RUNNING`, and `PRELOADED`. `enum xe_uc_fw_type` distinguishes GuC, HuC, and GSC. `enum xe_uc_fw_version_types` distinguishes release versus compatibility versions. `struct xe_uc_fw` stores type/status, path, override/full-version flags, size, BO, GSC-header flag, wanted/found versions, RSA/uCode/CSS offsets, private data size, and build type.

Control flow: The comments document expected phase transitions used by `xe_uc_fw.c` and uC subcomponents. Code elsewhere tests status ordering and type fields to decide whether firmware is supported, enabled, loadable, loaded, or PF-preloaded.

State and persistence behavior: `struct xe_uc_fw` persists inside GuC/HuC/GSC objects. The `status` field is exposed as const through a union while firmware loader internals mutate `__status`, discouraging arbitrary writes outside the loader.

Dependencies and integration points: Forward-declares `struct xe_bo`; used by firmware loader headers and GuC/HuC/GSC type definitions.

Risks: The state machine is explicitly noted as complicated. Status enum ordering affects inline predicates, and `PRELOADED` is a special high-valued state that is not locally loadable. Version arrays must be indexed by `xe_uc_fw_version_types`.

Test signals: Status transition tests across init/fetch/copy/upload/auth/reset and VF preloaded flows; compile-time coverage of all firmware types and version-type indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_types.h

Purpose: Defines the aggregate Xe microcontroller container embedded in each GT.

Important APIs/types/functions: `struct xe_uc` contains `struct xe_guc guc`, `struct xe_huc huc`, `struct xe_gsc gsc`, and `struct xe_wopcm wopcm`.

Control flow: No executable flow. Lifecycle code in `xe_uc.c` initializes and operates these members in a defined order.

State and persistence behavior: The aggregate persists for GT lifetime and owns all uC subcomponent state. WOPCM state is present even though VF paths skip WOPCM initialization.

Dependencies and integration points: Includes GuC, HuC, GSC, and WOPCM type headers. Used by GT structures, uC lifecycle, debugfs, firmware code, and subcomponent helpers.

Risks: Struct layout couples `container_of` helpers in `xe_uc.c` and `xe_uc_fw.c` to member placement in surrounding GT/subcomponent structs. Adding new uC components requires lifecycle/debugfs updates.

Test signals: Compile coverage and GT initialization tests that validate all subcomponents are initialized, exposed, and torn down appropriately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.c

Purpose: Implements userptr VMA setup, MMU interval notifier invalidation, page pinning through DRM GPUSVM, repin/rebind list management, and test-only forced invalidation.

Important APIs/types/functions: Public APIs include `xe_vma_userptr_check_repin`, `__xe_vm_userptr_needs_repin`, `xe_vma_userptr_pin_pages`, `xe_vm_userptr_pin`, `xe_vm_userptr_check_repin`, `xe_userptr_setup`, `xe_userptr_remove`, `xe_userptr_destroy`, and optional `xe_vma_userptr_force_invalidate`. Notifier callbacks are `xe_vma_userptr_invalidate_start` and `xe_vma_userptr_invalidate_finish`; internal helpers include `xe_vma_userptr_invalidate_pass1`, `xe_vma_userptr_do_inval`, and `xe_vma_userptr_complete_tlb_inval`.

Control flow: Setup initializes list links and inserts an MMU interval notifier for the current process range. Pinning uses `drm_gpusvm_get_pages` under VM lock with read-only/device-private context. On MMU invalidation, start callback rejects non-blockable ranges, takes the GPUSVM notifier write lock, advances the notifier sequence, moves non-fault-mode VMAs to `invalidated`, enables/waits for reservation fences as needed, optionally defers via embedded `finish`, invalidates TLBs for fault-mode initially-bound VMAs, and unmaps GPUSVM pages. Finish callback completes deferred TLB wait or invalidation. VM repin moves invalidated entries into `repin_list`, pins pages, and schedules VMA rebinds; on error it restores pending entries.

State and persistence behavior: Per-VM state includes `invalidated` and `repin_list`. Per-userptr state includes notifier, GPUSVM pages, embedded finish object, TLB invalidation batch, `finish_inuse`, `tlb_inval_submitted`, and `initial_bind`. Invalidations mutate lists and page mappings under combinations of VM lock, notifier lock, invalidated spinlock, and reservation locks. Removal frees pages then removes notifier only after GPU access is safe.

Dependencies and integration points: Depends on DRM GPUSVM, Linux MMU interval notifiers, DMA reservation fences, Xe SVM/private-page ownership, VM/VMA helpers, TLB invalidation batching, VM invalidate/rebind paths, and BO tracepoints (`trace_xe_vma_userptr_invalidate*`).

Risks: Lock ordering is subtle and enforced with lockdep assertions. Non-blockable invalidations return false, forcing notifier core behavior. Deferred invalidation uses one embedded finish per userptr; concurrent use falls back to synchronous invalidation. `-EFAULT` during repin requires unbinding/invalidation cleanup to avoid stale GPU access. Fault-mode and non-fault-mode paths differ significantly.

Test signals: MMU notifier stress with mmap/munmap/mprotect while GPU binds are active, non-fault and fault-mode VMs, concurrent exec/rebind workers, forced invalidation with `CONFIG_DRM_XE_USERPTR_INVAL_INJECT`, page fault injection, `-EFAULT` repin handling, lockdep, and tracepoint observation for invalidate/invalidate-complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.h

Purpose: Defines VM-level and VMA-level userptr state and declares userptr APIs, with stubs when DRM GPUSVM is disabled.

Important APIs/types/functions: `struct xe_userptr_vm` stores `repin_list`, `invalidated_lock`, and `invalidated`. `struct xe_userptr` stores invalidation/repin links, `drm_gpusvm_pages`, MMU interval notifier, embedded notifier finish, TLB invalidation batch, flags for finish/TLB state, `initial_bind`, and optional injection divisor. Declares setup/remove/destroy, VM pin/check, VMA pin/check, and optional force-invalidate functions.

Control flow: VM and VMA code use the structs for invalidation-to-repin-to-rebind flow. When `CONFIG_DRM_GPUSVM` is disabled, setup and pinning return errors/no-ops so callers can compile without userptr support. Force invalidation compiles only under its injection option.

State and persistence behavior: The structs are embedded in VM/VMA objects and persist for their lifetimes. Comments document lock ownership for list manipulation, finish state, TLB batch state, and `initial_bind`.

Dependencies and integration points: Includes list/mutex/notifier/scatterlist/spinlock, DRM GPUSVM, and Xe TLB invalidation types. Consumed by VM/VMA binding, SVM, and notifier code.

Risks: The lock contract in comments is part of correctness; violating it risks list corruption, stale GPU mappings, or notifier races. Stubbed functions must match real-function semantics closely enough for disabled-GPUSVM builds.

Test signals: Compile both GPUSVM enabled/disabled configurations, run userptr bind/rebind/invalidation tests, and lockdep tests for invalidated and repin list manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.c

Purpose: Implements an Xe validation transaction wrapper around `drm_exec`/`drm_gpuvm_exec_lock` with an rwsem-based validation domain that can retry allocation/locking after OOM by excluding competing validators for exhaustive eviction.

Important APIs/types/functions: Debug-only `xe_validation_assert_exec` validates special exec sentinel pointers. Internal helpers are `xe_validation_lock`, `xe_validation_trylock`, `xe_validation_unlock`, `xe_validation_contention_injected`, and `__xe_validation_should_retry`. Public APIs are `xe_validation_ctx_init`, `xe_validation_exec_lock`, `xe_validation_ctx_fini`, and `xe_validation_should_retry`.

Control flow: Context init stores flags, acquires the validation domain in read or write mode (blocking, interruptible, or trylock), and initializes `drm_exec` if supplied. `xe_validation_exec_lock` wraps `drm_gpuvm_exec_lock`, unlocking and retrying exclusive on qualifying `-ENOMEM`. `xe_validation_should_retry` is intended inside `drm_exec_until_all_locked`; it finalizes/reinitializes `drm_exec`, upgrades to exclusive locking when needed, clears the return value, and tells the macro loop to retry. Fini finalizes `drm_exec` and releases the domain lock.

State and persistence behavior: `struct xe_validation_device` owns an rwsem. `struct xe_validation_ctx` tracks whether the lock is held and whether it is exclusive, requested exclusive mode, flags copied from caller, exec flags, and `nr` for reinitialization. No persistent allocations are made.

Dependencies and integration points: Depends on DRM exec, GEM, GPUVM exec, Xe assertions, and the validation header. Integrated with BO/VM validation paths that need `drm_exec` locking and TTM exhaustive eviction behavior.

Risks: Retry behavior currently treats some WW contention as `-ENOMEM` due to TTM behavior, with a debug slowpath workaround inspecting drm_exec internals. Incorrect use outside `drm_exec_until_all_locked` can break retry control flow. Exclusive upgrade must release read lock before taking write lock to avoid deadlock. Sentinel exec values require careful debug assertions.

Test signals: KUnit or integration tests covering normal shared validation, exclusive validation, no-block failure, interruptible signal interruption, OOM retry upgrade, `drm_gpuvm_exec_lock` retry, debug sentinel assertions, and `CONFIG_DEBUG_WW_MUTEX_SLOWPATH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.h

Purpose: Defines the validation transaction API, special drm_exec sentinels, flags/state structures, retry macro, and scoped cleanup helper for Xe validation.

Important APIs/types/functions: Provides `XE_VALIDATION_UNIMPLEMENTED`, `XE_VALIDATION_UNSUPPORTED`, and `XE_VALIDATION_OPT_OUT` sentinel exec pointers; `xe_validation_lockdep`; optional `xe_validation_assert_exec`; `struct xe_validation_device`; `struct xe_val_flags`; `struct xe_validation_ctx`; function declarations; `xe_validation_retry_on_oom`; `xe_validation_device_init`; and `xe_validation_guard` based on `DEFINE_CLASS`/`scoped_guard`.

Control flow: Callers initialize a validation device rwsem, create a context with flags, enter `drm_exec_until_all_locked` loops, and use `xe_validation_retry_on_oom` or the scoped guard to handle cleanup and retry. Sentinel exec pointers mark call paths that cannot yet provide a real `drm_exec`.

State and persistence behavior: `xe_validation_device` rwsem persists per validation domain. `xe_validation_ctx` persists for one transaction and records lock/exec state required for retry and cleanup.

Dependencies and integration points: Depends on DMA reservation WW locking, Linux rwsem/types, DRM exec/GEM/GPUVM forward declarations, and C cleanup-class macros. Integrated with memory allocation, eviction, VM validation, and tests that opt out of full validation.

Risks: Sentinel values are encoded as `ERR_PTR` with negative constants; they must not be passed to normal `drm_exec` operations. The retry macro uses `goto *__drm_exec_retry_ptr`, so it must be used only in the expected DRM exec macro context. Comments contain typos but the API contract is clear.

Test signals: Compile with and without debug/prove-locking, exercise scoped guard cleanup, sentinel assertion paths, retry macro behavior under OOM, and lockdep validation that transactions can be initialized at sentinel use sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.h -->
