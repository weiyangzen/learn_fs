# Research: subset-b-003783

Work item `subset-b-003783` covers Xe DRM PXP, query, register save/restore, RTP, scheduling, allocator, shrinker, resource cursor, SoC remapper, and SR-IOV PF migration/control support under `sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.c

Purpose: implements Protected Xe Path (PXP) orchestration for integrated Xe devices, including feature detection, readiness reporting, KCR enablement, ARB session start/termination, protected exec queue tracking, protected BO key generation, and suspend/resume behavior. PXP is exposed to userspace through query status and protected queue/BO paths, but the implementation depends on HuC authentication via GSC and the GSC proxy.

Important APIs and control flow: `xe_pxp_is_supported()` gates on device capability plus `CONFIG_INTEL_MEI_GSC_PROXY`; `xe_pxp_init()` rejects unsupported topology, missing GSCCS, missing firmware, and too-old Panther Lake GSC firmware, then allocates `struct xe_pxp`, initializes completions, mutex/list state, ordered IRQ workqueue, KCR, and execution resources. `xe_pxp_get_readiness_status()` returns the uAPI status convention: negative errors, `0` for not ready, `1` for ready. `pxp_start()` serializes activation and termination through `pxp->mutex` and `pxp->activation`/`pxp->termination` completions, can run a termination before activation, and calls `__pxp_start_arb_session()` to submit the GSC session-init command and poll KCR session-in-play.

State and persistence: `pxp->status` moves through error, ready, start-in-progress, active, needs-termination, termination-in-progress, additional-termination, and suspended states. `key_instance` is incremented when an active session is terminated or suspended, invalidating protected BOs tagged with an older key. Active protected queues are held on `pxp->queues.list` and hold runtime PM references until removed.

Dependencies and integration: calls into `xe_pxp_submit.c` for VCS/GSC submissions, `xe_mmio`/KCR registers for session state, `xe_force_wake`, `xe_pm`, `xe_exec_queue_kill()`, BO helpers, HuC/GSC firmware state, and IRQ work from `xe_pxp_irq_handler()`. `xe_pxp_exec_queue_add()` starts PXP on demand and adds queues only when active; `pxp_invalidate_queues()` kills and removes all protected queues during termination or suspend.

Risks and test signals: the key-validity checks are intentionally racy and rely on repeated checks at submission/flip boundaries; tests should inject `xe_pxp_exec_queue_add()` failures, simulate termination IRQs, cover suspend/resume during activation/termination, and verify runtime PM refs are balanced for queue add/remove. Error paths around forcewake, firmware status, GSC pending responses, and completion timeouts should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h

Purpose: declares the public PXP interface used by query, exec queue, BO, IRQ, debugfs, and power-management code. It keeps PXP consumers insulated from `struct xe_pxp` internals.

Important APIs: feature/status helpers `xe_pxp_is_supported()`, `xe_pxp_is_enabled()`, and `xe_pxp_get_readiness_status()`; lifecycle hooks `xe_pxp_init()`, `xe_pxp_irq_handler()`, `xe_pxp_pm_suspend()`, and `xe_pxp_pm_resume()`; protected queue APIs `xe_pxp_exec_queue_set_type()`, `xe_pxp_exec_queue_add()`, and `xe_pxp_exec_queue_remove()`; BO/object key APIs `xe_pxp_key_assign()`, `xe_pxp_bo_key_check()`, and `xe_pxp_obj_key_check()`.

Dependencies and integration: forward declares DRM GEM, BO, device, exec queue, and PXP types. The header is included by PXP implementation, submit helpers, debugfs, query code, and users of protected object checks.

Risks and test signals: callers must handle `xe->pxp` being NULL, because `xe_pxp_is_enabled()` treats NULL as disabled. Tests should cover each public API with disabled PXP, not-ready PXP, and active PXP where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c

Purpose: creates debugfs entries under `pxp/` for observing PXP state and manually queuing a simulated termination interrupt.

Important APIs and control flow: `xe_pxp_debugfs_register()` copies a local `drm_info_list`, patches `data` to the target `struct xe_pxp`, creates the `pxp` directory, and registers `info` and `terminate`. `pxp_info()` locks `pxp->mutex` and prints status plus key instance. `pxp_terminate()` checks readiness, skips inactive PXP, and invokes `xe_pxp_irq_handler()` under `xe->irq.lock` with `KCR_PXP_STATE_TERMINATED_INTERRUPT`.

State and dependencies: uses PXP status enum from `xe_pxp_types.h`, `xe_pxp_get_readiness_status()`, `drm_debugfs_create_files()`, and KCR interrupt bit definitions. It does not own PXP lifetime; allocation is `drmm_kmalloc()` tied to DRM device lifetime.

Risks and test signals: debugfs terminate can race with normal PXP state transitions, so the IRQ lock and PXP state machine must remain robust. Manual testing should read `pxp/info`, trigger `pxp/terminate`, and observe queue invalidation and key instance changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h

Purpose: declares the PXP debugfs registration hook.

Important API: `xe_pxp_debugfs_register(struct xe_pxp *pxp)` is the single entry point and is expected to be called only when PXP support is being exposed through DRM debugfs.

Dependencies and risks: forward declares `struct xe_pxp`; there is no stub here, so build integration must only include/call it where the implementation is available. Test signal is the presence of `pxp/info` and `pxp/terminate` under the DRM minor debugfs root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c

Purpose: owns PXP command submission resources and packet emission. It allocates a VCS queue/batch for inline session termination and a GSCCS queue/VM/BO for HECI-style GSC firmware messages used by session init and stream-key invalidation.

Important APIs and control flow: `xe_pxp_allocate_execution_resources()` creates VCS and GSC resources; `xe_pxp_destroy_execution_resources()` frees them. `xe_pxp_submit_session_termination()` emits MFX wait, session selection, CRYPTO key exchange, and batch end into a GGTT batch, then creates/arms/pushes a `xe_sched_job` and waits up to one second. `xe_pxp_submit_session_init()` and `xe_pxp_submit_session_invalidation()` build PXP 4.3 firmware messages and submit via `gsccs_send_message()`.

State and persistence: `struct xe_pxp_gsc_client_resources` stores VM, BO, mapped batch/input/output iosys maps, queue, host-session handle, and in/out size. The GSC BO maps a batch page followed by input and output buffers. Headers are poisoned after use to avoid stale reply interpretation.

Dependencies and integration: uses `xe_vm_create()`, `xe_bo_create_pin_map()`, `xe_vm_bind_kernel_bo()`, `xe_exec_queue_create()`, `xe_sched_job`, GSC command helpers, PXP ABI structs, MI/MFX/GSC instruction definitions, and DMA fence waiting. `gsccs_send_message()` handles GSC pending responses by retrying for up to 40 times with 50 ms sleeps.

Risks and test signals: resource cleanup paths span VM, BO, and queue lifetimes; failure injection should cover bind timeout, queue creation failure, GSC invalid headers, message overflow, pending timeout, and firmware status errors. Command length assumptions are tight: PXP command size is currently small enough for a page, but new commands must revisit `inout_size` and batch layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h

Purpose: declares the internal PXP submission helper interface between the PXP state machine and command-emission implementation.

Important APIs: allocation/lifetime functions `xe_pxp_allocate_execution_resources()` and `xe_pxp_destroy_execution_resources()`; firmware/VCS submission functions `xe_pxp_submit_session_init()`, `xe_pxp_submit_session_termination()`, and `xe_pxp_submit_session_invalidation()`.

Dependencies and risks: forward declares `struct xe_pxp` and `struct xe_pxp_gsc_client_resources`; consumers must pass initialized resources from `xe_pxp_init()`. Tests should verify callers do not submit after destroy and handle negative errno returns from all command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h

Purpose: defines PXP state and resource structures shared by the PXP implementation, submit code, and debugfs.

Important types: `enum xe_pxp_status` models lifecycle and error states; `struct xe_pxp_gsc_client_resources` stores GSCCS VM/BO/queue and mapped batch/in/out buffers; `struct xe_pxp` stores device/GT pointers, VCS resources, GSC resources, protected queue list plus spinlock, status mutex, activation/termination completions, key-instance counters, and IRQ workqueue/event state.

State behavior: `key_instance` is the current protected-content generation and `last_suspend_key_instance` helps avoid redundant suspend cleanup. IRQ event flags `PXP_TERMINATION_REQUEST` and `PXP_TERMINATION_COMPLETE` are latched under the device IRQ lock and drained by ordered work.

Risks and test signals: locking rules are split between mutex state, queue spinlock, and IRQ spinlock. Tests should assert list initialization/removal, completion reinitialization, and event flag behavior across concurrent termination and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c

Purpose: implements `DRM_XE_DEVICE_QUERY` dispatch. It reports engines, memory regions, device config, GT list, GuC hardware config, topology masks, engine cycles, firmware versions, OA units, PXP status, and EU stall capabilities.

Important APIs and control flow: `xe_query_ioctl()` validates extensions/reserved fields, bounds-checks `query->query`, uses `array_index_nospec()`, and dispatches through `xe_query_funcs`. Most query handlers implement the two-call size-discovery ABI: if `query->size == 0`, set expected size and return; otherwise require exact size. `query_engine_cycles()` reads user input for clock ID and engine instance, obtains forcewake, reads upper/lower ring timestamp with CPU timestamp/delta, and writes only output fields back. `query_pxp_status()` directly forwards `xe_pxp_get_readiness_status()`.

State and dependencies: relies on device topology, GT/engine lists, TTM memory managers, VRAM accounting, GuC hwconfig, GT fuse topology, UC firmware structures, OA unit metadata, PXP state, and EU stall helpers. SR-IOV VF mode blocks engine-cycle queries with `-EOPNOTSUPP`.

Risks and test signals: exact-size uAPI checks can regress compatibility if struct sizes or ordering change. Tests should cover zero-size discovery, bad sizes, bad user pointers, invalid clock/engine class/GT IDs, SR-IOV VF denial, PXP disabled/error/not-ready/ready responses, and topology copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h

Purpose: declares the Xe query ioctl entry point.

Important API: `xe_query_ioctl(struct drm_device *dev, void *data, struct drm_file *file)` is wired into DRM ioctl handling and interprets `data` as `struct drm_xe_device_query`.

Dependencies and risks: forward declares DRM device/file types and keeps query implementation internal to `xe_query.c`. Tests should exercise the ioctl through DRM uAPI rather than this header directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c

Purpose: implements address-range conflict tracking backed by Linux interval trees and DMA fences. A range fence remains in the tree until its associated `dma_fence` signals, then cleanup removes it and frees storage.

Important APIs and control flow: `xe_range_fence_insert()` cleans pending signaled entries, ignores already-signaled fences, initializes the interval-tree node, gets the fence, registers `xe_range_fence_signal_notify()`, and inserts the node. The fence callback only adds the range fence to an `llist`, deferring removal/free until `__xe_range_fence_tree_cleanup()` runs in non-callback context. `xe_range_fence_tree_first()` and `_next()` wrap generated interval-tree iterators.

State and dependencies: `struct xe_range_fence_tree` owns a cached RB root and lockless list of pending frees. `xe_range_fence_tree_fini()` removes callbacks from all live fences and loops cleanup until empty.

Risks and test signals: callback/removal races are subtle; tests should cover insertion with pre-signaled fences, callback firing during fini, overlapping iterator queries, and custom `ops->free`. Callers must provide external synchronization around tree access because this file does not embed a lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h

Purpose: defines the range-fence data structures and public interval-tree API.

Important types and APIs: `struct xe_range_fence_ops` supplies an optional `free()` callback; `struct xe_range_fence` stores RB node, inclusive start/last, subtree metadata, fence reference, tree pointer, DMA fence callback, pending-free list node, and ops; `struct xe_range_fence_tree` stores root and pending list. Public functions initialize/finalize trees, insert fences, and iterate overlapping ranges. `xe_range_fence_kfree_ops` frees nodes with `kfree()`.

Risks and test signals: the header documents inclusive `last` semantics, while the insert argument is named `end` in the prototype. Callers should be tested for off-by-one range handling and external locking discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_range_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c

Purpose: manages register save/restore tables, including merging compatible register bit updates, applying them to MMIO, dumping them, and checking hardware or LRC readback.

Important APIs and control flow: `xe_reg_sr_init()` initializes an xarray and registers managed cleanup. `xe_reg_sr_add()` stores entries by register address, merging only compatible non-overlapping clear/set masks for the same raw register. `xe_reg_sr_apply_mmio()` forcewakes the GT, rejects VF processing by assertion, and writes each entry with `apply_one_mmio()`. Masked registers are written via upper mask bits; unmasked registers use RMW unless clearing all bits. MCR registers are accessed through `xe_gt_mcr_*`.

State and dependencies: `struct xe_reg_sr` owns an xarray of heap-allocated `xe_reg_sr_entry`. KUnit builds track `errors` on rejected entries. Integration points include RTP action processing, whitelist programming, GT reset/apply paths, default LRC lookup, and DRM printers.

Risks and test signals: conflicting entries are discarded, so table authors need tests for duplicate register actions. Readback checks should cover masked, unmasked, and MCR registers. Forcewake failure currently logs and returns without applying, which should be visible in GT logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h

Purpose: declares register save/restore lifecycle, mutation, apply, dump, and validation APIs.

Important APIs: `xe_reg_sr_init()`, `xe_reg_sr_add()`, `xe_reg_sr_apply_mmio()`, `xe_reg_sr_apply_whitelist()`, `xe_reg_sr_dump()`, `xe_reg_sr_readback_check()`, and `xe_reg_sr_lrc_check()`.

Dependencies and risks: forward declares GT, device, hardware engine, printer, and SR types. Callers must initialize `struct xe_reg_sr` before passing it to RTP or whitelist processing and must not assume rejected conflicting entries are retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h

Purpose: defines compact storage for register save/restore entries and tables.

Important types: `struct xe_reg_sr_entry` stores register descriptor, `clr_bits`, `set_bits`, and `read_mask`; `struct xe_reg_sr` stores an xarray keyed by register address plus a human-readable name and optional KUnit error counter.

State and integration: entries are built by RTP/whitelist code and consumed by MMIO apply/readback and LRC validation paths. The bit masks encode both RMW behavior and readback expectations.

Risks and test signals: table authors must keep `set_bits` within intended clear/read masks, especially for masked registers. KUnit should assert conflict handling and error counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_sr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c

Purpose: defines and processes engine register whitelist entries that allow or deny userspace non-privileged MMIO access to selected registers, mainly for workarounds and OA triggers.

Important APIs and control flow: `register_whitelist[]` is an RTP save/restore table with platform/version/engine rules and `WHITELIST()` actions. `xe_reg_whitelist_process_engine()` creates an RTP engine context, processes matching entries into `hwe->reg_whitelist`, then `whitelist_apply_to_hwe()` converts each logical whitelist target into `RING_FORCE_TO_NONPRIV` save/restore entries in `hwe->reg_sr` slot order. `xe_reg_whitelist_print_entry()` decodes access mode, deny bit, and range size for debug output.

State and dependencies: depends on RTP rule matching, `xe_reg_sr_add()`, engine MMIO base, OA register definitions, platform/version helpers, and `RING_MAX_NONPRIV_SLOTS`. The generated whitelist is stored in engine-local SR tables and later applied with other engine state.

Risks and test signals: slot exhaustion logs an error and stops adding entries; tests should cover platforms with many OA/MERT entries. Whitelist range decoding and deny/access flags should be verified for both debug dump accuracy and hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h

Purpose: exposes register whitelist processing and dump helpers.

Important APIs: `xe_reg_whitelist_process_engine()` fills per-engine whitelist/save-restore state; `xe_reg_whitelist_print_entry()` formats one whitelist entry; `xe_reg_whitelist_dump()` prints all entries in a save/restore table.

Dependencies and risks: depends on `struct xe_hw_engine`, `struct xe_reg_sr`, and DRM printers. Tests should compare dumped access/range strings with expected hardware flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h

Purpose: provides inline cursor utilities for walking TTM resources, scatter-gather tables, and `drm_pagemap_addr` arrays as contiguous DMA/resource segments.

Important APIs and control flow: `xe_res_first()` initializes from a TTM resource and handles VRAM/stolen gpu-buddy blocks or falls back to TT-style offsets. `xe_res_first_sg()` and `xe_res_first_dma()` initialize from SG and DMA page-map sources. `xe_res_next()` advances by bytes, moving across buddy blocks, SG elements, or coalesced DMA elements. `xe_res_dma()` returns the current DMA/resource address and `xe_res_is_vram()` identifies same-device VRAM segments.

State and dependencies: `struct xe_res_cursor` tracks segment start, size, remaining bytes, backing node, memory type, SG pointer, DMA page-map pointer, buddy allocator, and coalesced DMA metadata. It depends on TTM managers, Xe VRAM manager resources, DRM pagemap metadata, and interconnect protocol flags.

Risks and test signals: off-by-one and alignment bugs here affect BO copies and migrations. Tests should cover multi-block VRAM resources, TT fallback, SG advancement, DMA coalescing only when contiguous and same protocol, zero remaining behavior, and `xe_res_is_vram()` for VRAM versus system memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c

Purpose: emits Gen12-style ring commands around scheduled jobs for GSC, copy, video, render/compute, and migration queues. It handles timestamp copies, start seqno writes, TLB/cache invalidation, AuxCCS table invalidation, batch buffer starts, user fences, seqno signaling, and user interrupts.

Important APIs and control flow: `xe_ring_ops_get()` selects a `struct xe_ring_ops` by engine class and AuxCCS support. Internal emitters build bounded arrays of DWORD commands and write them to LRC rings. `__emit_job_gen12_simple()` serves copy/GSC-like engines, `__emit_job_gen12_video()` adds Aux table invalidation, `__emit_job_gen12_render_compute()` adds PIPE_CONTROL invalidation and render cache flushes, and `emit_migration_job_gen12()` emits two batch phases with migration flush flags. `emit_fake_watchdog()` supports forced engine reset tests.

State and dependencies: uses `xe_sched_job` fields such as `ptrs`, `user_fence`, `ring_ops_flush_tlb`, `ring_ops_force_reset`, `migrate_flush_flags`, and queue/LRC seqno addresses. It depends on MI/PIPE_CONTROL command definitions, engine registers, workarounds, VM/migration flags, SR-IOV VF timestamp sampling, and `MAX_JOB_SIZE_DW` assertions.

Risks and test signals: command streams must remain under `MAX_JOB_SIZE_DW`; tests should validate each engine class path, AuxCCS versus non-AuxCCS selection, VF duplicate timestamp storage, TLB invalidation flags, compute/no-render mask handling, user fence writes, and migration two-batch sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h

Purpose: declares ring operation selection for GT engine classes.

Important API: `xe_ring_ops_get(struct xe_gt *gt, enum xe_engine_class class)` returns the command-emission vtable appropriate to an engine class and platform compression mode.

Dependencies and risks: depends on engine class enum and `struct xe_ring_ops`. Callers must handle NULL for unsupported classes and must initialize GT platform/compression info before selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h

Purpose: defines the ring operations vtable and command-size bounds.

Important types and constants: `MAX_JOB_SIZE_DW` is 74 DWORDs and `MAX_JOB_SIZE_BYTES` is its byte size. `struct xe_ring_ops` contains `emit_job(struct xe_sched_job *)` and optional `emit_aux_table_inv(struct xe_gt *, u32 *)`.

Risks and test signals: every emitter in `xe_ring_ops.c` asserts it stays within `MAX_JOB_SIZE_DW`. Adding commands, workarounds, or user-fence features must update size proofs or risk ring overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c

Purpose: implements Register Table Processing (RTP), a rule/action engine used to apply platform, IP-version, stepping, GT, and engine-class specific register programming or active workaround tracking.

Important APIs and control flow: `rule_matches()` evaluates AND groups separated by `XE_RTP_MATCH_OR`, supports platform/subplatform, platform/graphics/media stepping, graphics/media version ranges, integrated/discrete, engine class/not-class, and callback rules. `xe_rtp_process_to_sr()` turns matching `xe_rtp_entry_sr` actions into `xe_reg_sr` entries, optionally iterating every engine and optionally skipping SR-IOV VF devices. `xe_rtp_process()` evaluates actionless entries for active tracking. `xe_rtp_process_ctx_enable_active_tracking()` registers a bitmap that matching entries set.

State and dependencies: context can be device, GT, or engine, selected by `XE_RTP_PROCESS_CTX_INITIALIZER`. Actions may be engine-base relative. Dependencies include register SR, GT topology, configfs PSMI, SR-IOV mode, and device platform metadata.

Risks and test signals: rule macros allow compound static tables, so KUnit should validate OR behavior, empty/invalid rule warnings, media-versus-graphics GT filtering on standalone media platforms, active bitmap bounds, engine-base offset application, and VF skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h

Purpose: provides the public macro DSL and function declarations for RTP tables.

Important APIs and macros: rule macros encode platform, subplatform, stepping, graphics/media version/range/any-GT, integrated/discrete, engine class, callback, and OR conditions. Action macros encode full writes, set/clear, field-set with or without read masks, and whitelist actions. `XE_RTP_RULES()` and `XE_RTP_ACTIONS()` build compound literal arrays, up to 12 items. `XE_RTP_PROCESS_CTX_INITIALIZER()` uses `_Generic` to infer device/GT/engine context.

Integration points: used by workaround and whitelist tables throughout Xe to populate `xe_reg_sr` tables or active workaround bitmaps. Declares match helpers for even engine instance, first render/compute, non-VF, PSMI enabled, discontiguous DSS groups, and FlatCCS.

Risks and test signals: macro expansion mistakes are compile-time hard to diagnose. Tests should compile representative tables for all rule/action forms and verify read masks, engine-base flags, and OR semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h

Purpose: contains private preprocessor helpers used only by `xe_rtp.h` to build the RTP macro DSL.

Important macros: `XE_RTP_PASTE_FOREACH()` pastes a prefix onto tuple elements and joins them with a configured separator for 1 to 12 arguments. `XE_RTP_DROP_CAST()` removes a cast wrapper from compound register macros so register initializers can be embedded in action literals.

Dependencies and risks: guarded by `_XE_RTP_INCLUDE_PRIVATE_HELPERS` so it is not included directly. Changes can silently alter many RTP tables, so tests should inspect preprocessed expansion for representative rule and action macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h

Purpose: defines RTP actions, rules, entries, match types, and processing context.

Important types: `struct xe_rtp_action` stores register, clear/set/read masks, and flags such as `XE_RTP_ACTION_FLAG_ENGINE_BASE`; `struct xe_rtp_rule` stores a match type and union payload for platform, version, stepping, engine class, or callback; `struct xe_rtp_entry_sr` combines named rules/actions and flags such as `FOREACH_ENGINE`; `struct xe_rtp_entry` is actionless; `struct xe_rtp_process_ctx` identifies device/GT/engine context and optional active-entry bitmap.

Risks and test signals: `u8` counters cap table size and rule/action counts. Tests should confirm entries with 12 macro arguments fit and that active bitmap sizes match `n_entries`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_rtp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c

Purpose: implements suballocated BO managers used for small GPU-visible allocations, with optional shadow BO support and CPU staging for iomem-backed VRAM.

Important APIs and control flow: `__xe_sa_bo_manager_init()` creates a managed pinned GGTT BO, optionally allocates CPU staging memory when the BO mapping is iomem, optionally creates a shadow BO and swap mutex, initializes the DRM suballocator excluding a guard region, and registers managed cleanup. `__xe_sa_bo_new()`, `xe_sa_bo_alloc()`, `xe_sa_bo_init()`, and `xe_sa_bo_free()` wrap DRM suballocation flows. `xe_sa_bo_flush_write()` and `xe_sa_bo_sync_read()` copy between CPU staging and GPU BO for iomem mappings; `xe_sa_bo_swap_shadow()` and `xe_sa_bo_sync_shadow()` manage shadow BO contents.

State and dependencies: `struct xe_sa_manager` stores DRM suballocator base, primary/shadow BOs, swap guard, CPU pointer, and iomem flag. Depends on managed BO creation, GGTT pinning, DRM managed cleanup, `xe_map_memcpy_*`, and DRM suballoc.

Risks and test signals: failures after creating BOs rely on DRM managed cleanup, and iomem staging must be flushed/synced explicitly. Tests should cover oversize allocation returning `-ENOBUFS`, guard-size exclusion, shadow swap under lockdep, iomem versus non-iomem CPU pointers, and fence-delayed free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h

Purpose: declares SA BO manager APIs and inline address/access helpers.

Important APIs: manager creation via `__xe_sa_bo_manager_init()` and inline `xe_sa_bo_manager_init()` with a 4 KiB guard; allocation/init/free helpers; flush/sync helpers; shadow swap/sync; `to_xe_sa_manager()`, `xe_sa_manager_gpu_addr()`, `xe_sa_bo_gpu_addr()`, `xe_sa_bo_cpu_addr()`, and `xe_sa_bo_swap_guard()`.

Risks and test signals: callers must use the correct CPU flush/sync helpers when `is_iomem` is true and hold the swap guard for shadow operations. Address helpers should be tested against suballocation offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h

Purpose: defines the SA manager storage structure.

Important type: `struct xe_sa_manager` embeds `drm_suballoc_manager`, tracks primary and optional shadow BOs, a mutex for shadow swapping, CPU pointer to either direct mapping or staging memory, and whether the BO mapping is iomem.

Risks and test signals: lifetime is tied to DRM managed cleanup in `xe_sa.c`. Tests should verify `cpu_ptr` updates when primary/shadow BOs swap and that shadow state is unavailable unless requested by flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c

Purpose: implements Xe scheduler job allocation, fence setup, runtime PM accounting, job push, error propagation, start/completion checks, user-fence metadata, snapshots, and dependency registration.

Important APIs and control flow: module init creates separate slabs for single and parallel/migration jobs. `xe_sched_job_create()` allocates a job, references the exec queue, initializes DRM scheduler job state, preallocates LRC seqno fences and chain fences, copies batch addresses, increments queue job count, and takes runtime PM. `xe_sched_job_arm()` asserts VM locking, determines whether TLB flush is needed, initializes LRC fences, chains parallel fences, stores the final fence, and arms DRM scheduler state. `xe_sched_job_push()` pushes to the DRM scheduler entity with a temporary ref. `xe_sched_job_set_error()` sets errors under fence locks and runs fence IRQ work.

State and dependencies: `struct xe_sched_job` owns refs to queue and fences, per-width `ptrs`, optional user fence data, ring-op flags, and DRM scheduler base. Dependencies include DRM scheduler, DMA fences/chains, LRC seqno fences, VM locking/TLB state, PM runtime, tracing, and exec queue lifecycle.

Risks and test signals: fence chain setup is sensitive to queue width and migration jobs use width 2 even if queue width differs. Tests should cover allocation failure cleanup, parallel fence chains, migration job slab choice, VM TLB invalidation flagging, error propagation to chain-contained fences, and runtime PM ref balance on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h

Purpose: declares scheduler job lifecycle, fence, query, snapshot, and dependency APIs plus small inline helpers.

Important APIs and constants: `XE_SCHED_HANG_LIMIT`, `XE_SCHED_JOB_TIMEOUT`, module init/exit, create/destroy/get/put, error setting, started/completed checks, arm/push, user-fence init, migration detection, snapshot capture/free/print, and `xe_sched_job_add_deps()`. Inlines expose job pointer from DRM scheduler job, job seqno, LRC seqno, and migration flush flag setter.

Dependencies and risks: callers must balance get/put and arm jobs before push. Tests should verify sequence number helpers after `xe_sched_job_arm()` and migration flush flags consumed by ring ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h

Purpose: defines scheduler job data structures and snapshots.

Important types: `struct xe_job_ptrs` stores each batch address, head offset, preallocated LRC fence, and chain fence. `struct xe_sched_job` embeds `drm_sched_job`, references queue/fence, stores refcount, LRC seqno, per-job user fence, timestamp sample, flags for TLB flush/forced reset/migration flush, and a flexible `ptrs[]`. `struct xe_sched_job_snapshot` records batch addresses for diagnostics.

State and risks: flexible array sizing must match slab selection in `xe_sched_job.c`. Tests should cover maximum queue width, migration two-batch jobs, and snapshot uncanonicalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c

Purpose: implements a per-device memory shrinker that frees purgeable/shrinkable Xe BO backing under kernel memory pressure while respecting reclaim, runtime PM, and TTM constraints.

Important APIs and control flow: `xe_shrinker_create()` allocates/registers a shrinker and stores it in `xe->mem.shrinker`; `xe_shrinker_mod_pages()` updates shrinkable/purgeable accounting under rwlock. `xe_shrinker_count()` reports purgeable pages plus shrinkable pages limited by backup capacity and `__GFP_FS`. `xe_shrinker_scan()` first tries purgeable objects, then backup/writeback paths if allowed, using `xe_shrinker_walk()` to prefer idle/no-writeback shrinking before potentially waiting on GPU or writing back.

State and dependencies: `struct xe_shrinker` stores device pointer, rwlock counters, kernel shrinker pointer, and PM wake worker. Depends on TTM LRU walking, `ttm_backup_bytes_avail()`, `xe_bo_shrink()`, runtime PM helpers, and a workqueue to wake the device outside reclaim when necessary.

Risks and test signals: reclaim context must not deadlock on runtime PM or fs reclaim; tests should cover `__GFP_FS`/`__GFP_IO` combinations, `ttm_bo_shrink_avoid_wait()`, flat-CCS runtime PM wakeups, purge-only behavior, accounting reaching zero before fini, and worker flush on cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h

Purpose: declares the per-device shrinker interface.

Important APIs: `xe_shrinker_mod_pages()` adjusts page accounting and `xe_shrinker_create()` registers the shrinker for a device.

Dependencies and risks: forward declares `struct xe_shrinker` and `struct xe_device`. Callers updating accounting must keep deltas balanced so final cleanup assertions do not fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h

Purpose: provides common sleep helpers with relaxed millisecond timing and exponential backoff.

Important APIs: `xe_sleep_relaxed_ms()` uses `msleep()` for delays over 20 ms and `usleep_range()` with 0.5 ms slack for shorter delays. `xe_sleep_exponential_ms()` sleeps for the current period, doubles it up to a maximum, and returns the actual requested delay.

Risks and test signals: callers must initialize `*sleep_period_ms` to a nonzero value or the first sleep is skipped and remains zero. Tests should cover zero, sub-20 ms, over-20 ms, and capped exponential growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c

Purpose: initializes optional SoC remapper hooks for telemetry and system-control regions and implements locked MMIO updates for remapper index fields.

Important APIs and control flow: `xe_soc_remapper_init()` checks device info flags, initializes `xe->soc_remapper.lock` when any remapper exists, and assigns function pointers for telemetry and sysctrl region setters. Setter helpers call `xe_soc_remapper_set_region()`, which takes `spinlock_irqsave` and performs `xe_mmio_rmw32()` on root tile MMIO register `SG_REMAP_INDEX1`.

State and dependencies: state lives in `xe->soc_remapper`, including function pointers and lock. Depends on remapper register definitions, root tile MMIO, and device capability flags.

Risks and test signals: function pointers remain NULL when the corresponding feature flag is absent; callers must check before invoking. Tests should validate masked RMW field encoding and concurrent setter serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h

Purpose: declares SoC remapper initialization.

Important API: `xe_soc_remapper_init(struct xe_device *xe)` populates remapper locks and function pointers based on device capabilities.

Dependencies and risks: includes `xe_device_types.h` because initialization writes into the device structure. Tests should verify initialization is harmless when no remapper capabilities are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c

Purpose: provides top-level SR-IOV mode detection, common initialization, workqueue lifetime, info printing, function-name formatting, and late init dispatch for PF or VF mode.

Important APIs and control flow: `xe_sriov_probe_early()` determines mode from device capability, VF MMIO register `VF_CAP_REG`, and PF readiness, or disables advertised VFs when platform SR-IOV support is not enabled. `xe_sriov_init()` calls PF or VF early init as appropriate, creates `xe-sriov-wq`, and registers managed cleanup. `xe_sriov_init_late()` dispatches to PF or VF late init.

State and dependencies: sets `xe->sriov.__mode`, `xe->sriov.wq`, and PF/VF-specific state. Depends on PCI SR-IOV APIs, MMIO, PF and VF modules, DRM managed cleanup, and fault-injection annotation.

Risks and test signals: mode is asserted nonzero after probing, so probe ordering is critical. Tests should cover PF readiness false, VF detection via MMIO, unsupported platform with total VFs advertised, workqueue allocation failure, and function-name formatting for PF/VF IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h

Purpose: declares top-level SR-IOV APIs and inline mode predicates.

Important APIs: `xe_sriov_mode_to_string()`, `xe_sriov_function_name()`, `xe_sriov_probe_early()`, `xe_sriov_print_info()`, `xe_sriov_init()`, and `xe_sriov_init_late()`. Inlines expose `xe_device_sriov_mode()`, `xe_device_is_sriov_pf()`, `xe_device_is_sriov_vf()`, and macros `IS_SRIOV_PF`, `IS_SRIOV_VF`, and `IS_SRIOV`.

Risks and test signals: `xe_device_sriov_mode()` asserts mode was initialized, so it must not be called before early probe. PF predicate depends on `CONFIG_PCI_IOV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c

Purpose: implements PF-side SR-IOV migration packet allocation, streaming read/write, descriptor/trailer creation, and descriptor compatibility validation.

Important APIs and control flow: `xe_sriov_packet_alloc()` creates an uninitialized packet with header bytes remaining. `xe_sriov_packet_init()` fills a header and allocates payload storage; VRAM packets allocate a pinned mapped BO, other packet types allocate `kvzalloc()` memory. `xe_sriov_packet_read_single()` selects descriptor, pending save data, or trailer and streams header then payload to userspace, freeing packets when complete. `xe_sriov_packet_write_single()` streams userspace header/payload into a pending packet and calls `xe_sriov_pf_migration_restore_produce()` when complete. `xe_sriov_packet_save_init()` prepares descriptor and zero-size trailer packets under the per-VF migration mutex.

State and dependencies: packet state tracks remaining header/payload bytes, typed header fields, and either BO or heap buffer storage. Descriptor KLVs include device ID and revision and are validated by `xe_sriov_packet_process_descriptor()`. Integration depends on PF migration state, GuC KLV helpers, per-VF locks, GT lookup, BO allocation, and userspace copy helpers.

Risks and test signals: partial reads/writes must preserve offsets correctly. Tests should cover short header writes, unsupported protocol version, invalid GT/tile, VRAM BO allocation failure, descriptor mismatches, truncated KLVs, unknown KLV skipping, trailer end-of-stream, and read ordering descriptor before data before trailer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h

Purpose: declares SR-IOV migration packet helpers.

Important APIs: allocation/free, header-backed initialization, read/write streaming, save initialization, and descriptor processing. These functions are used by PF migration read/write paths and migration control setup.

Risks and test signals: callers must hold the per-VF migration mutex where packet selection requires it. Tests should assert free handles NULL/ERR pointers and that descriptor processing rejects incompatible devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h

Purpose: defines the SR-IOV VF migration packet protocol structures.

Important types: `enum xe_sriov_packet_type` reserves zero and defines descriptor, trailer, GGTT, MMIO, GuC, and VRAM packet types. `struct xe_sriov_packet_hdr` is a packed protocol header with version, type, tile/GT IDs, flags, offset, and size. `struct xe_sriov_packet` stores runtime streaming state, CPU payload pointer, BO or heap buffer, and header.

Risks and test signals: packed header layout is ABI-like for debugfs migration streams. Tests should assert header size/layout, zero type rejection in restore, and correct allocation choice for VRAM versus non-VRAM packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_packet_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c

Purpose: implements PF readiness, early/late PF initialization, readiness waiting, exclusive/lockdown guards, VF enable lockdown, and VF summary printing.

Important APIs and control flow: `xe_sriov_pf_readiness()` verifies PCI PF, GuC submission, configured maximum VFs, reduces total VFs to driver limit, and records admin-only/device/driver VF counts. `xe_sriov_pf_init_early()` allocates per-VF state for VF0..N, initializes the master mutex, migration state, VFs-enabling guard, PF service, and MERT. `xe_sriov_pf_init_late()` initializes each GT PF side and PF sysfs. Guard wrappers add SR-IOV debug logging around `xe_guard_arm()`/`xe_guard_disarm()`.

State and dependencies: PF state includes `admin_only`, `device_total_vfs`, `driver_max_vfs`, `vfs[]`, `master_lock`, service state, migration state, and guard. Depends on configfs policy, PCI total VF APIs, GT PF modules, service/sysfs/provisioning, MERT, and DRM managed allocation.

Risks and test signals: when prerequisites fail, PF mode intentionally continues as native and sets total VFs to zero. Tests should cover configfs max VF reduction, admin-only propagation, guard denial while VFs are enabled, wedged-device readiness failure, and late init failure propagation across GTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h

Purpose: declares PF-specific SR-IOV lifecycle and reporting APIs, with no-op stubs when `CONFIG_PCI_IOV` is disabled.

Important APIs: PF readiness, early/late init, wait-ready, lockdown/end-lockdown, and VF summary printing. The disabled-config stubs keep non-IOV builds compiling.

Risks and test signals: callers should not assume `xe_sriov_pf_wait_ready()` has a stub in every disabled path unless build coverage confirms it. Tests should compile both PCI_IOV enabled and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c

Purpose: provides device-level PF control wrappers that fan out VF operations to every GT: pause, resume, stop, reset/FLR, save migration, and restore migration.

Important APIs and control flow: pause/resume/stop loop all GTs and log success; reset triggers FLR on all GTs then waits on all GTs. `xe_sriov_pf_control_sync_flr()` performs two sync phases across all GTs. Save starts by `xe_sriov_packet_save_init()`, initializes per-GT migration save rings, then triggers save on each GT; finish-save loops finish calls. Restore trigger/finish similarly fan out per GT.

State and dependencies: depends on `xe_gt_sriov_pf_control`, `xe_gt_sriov_pf_migration`, packet save initialization, and SR-IOV printk helpers. It treats any earlier error in multi-GT pause/resume/stop as `-EUCLEAN` to indicate partial failure.

Risks and test signals: multi-GT partial failures must not be hidden. Tests should simulate one GT failing in each operation, validate save descriptor/trailer initialization happens before GT save trigger, and verify reset waits after triggering all GTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h

Purpose: declares PF VF-control operations used by debugfs/sysfs/service callers.

Important APIs: pause, resume, stop, reset, prepare/wait/sync FLR, trigger/finish save, and trigger/finish restore for a VF ID.

Risks and test signals: callers must pass a valid nonzero VF ID where required. Tests should exercise APIs through debugfs wrappers and direct service paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c

Purpose: builds the PF SR-IOV debugfs tree under the DRM minor root, exposing root PF controls, PF info, per-VF controls, migration data streams, migration size, and tile-level debugfs children.

Important APIs and control flow: `xe_sriov_pf_debugfs_register()` creates `sriov/`, `sriov/pf/`, and `sriov/vfN/` directories, storing either `xe_device *` or VF IDs in inode private data. Root files include `restore_auto_provisioning` and `lockdown_vfs_enabling`; PF files include `vfs` and `versions`; VF files include `pause`, `resume`, `stop`, `reset`, `save`, `restore`, `migration_data`, and `migration_size`. Boolean writes trigger runtime-PM-protected calls; save/restore use read-to-finish and write-to-trigger semantics.

State and dependencies: uses dentry parent relationships to derive `xe` and VF ID, runtime PM guards, PF control APIs, migration read/write/size, provisioning, service printing, and tile debugfs population.

Risks and test signals: debugfs is a privileged control surface. Tests should cover offset rejection for command writes and migration data, lockdown open/release balancing, VF ID extraction for PF versus VF dirs, partial migration reads/writes, and runtime PM ref balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h

Purpose: declares PF SR-IOV debugfs registration with a stub for non-PCI_IOV builds.

Important API: `xe_sriov_pf_debugfs_register(struct xe_device *xe, struct dentry *root)` populates the PF debugfs tree when SR-IOV PF support is compiled in.

Risks and test signals: compile coverage should include PCI_IOV disabled builds to confirm the stub is used and no debugfs references leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h

Purpose: provides PF-only inline helpers and guard declarations for VF count, admin-only policy, master mutex access, and VF ID assertions.

Important APIs: `xe_sriov_pf_assert_vfid()` validates VF IDs in debug builds; `xe_sriov_pf_get_totalvfs()` returns driver-supported VFs; `xe_sriov_pf_num_vfs()` returns currently enabled VFs via PCI; `xe_sriov_pf_admin_only()` exposes configfs policy; `xe_sriov_pf_master_mutex()` returns the PF master lock; guard arm/disarm declarations are implemented in `xe_sriov_pf.c`.

Risks and test signals: helpers assert PF mode, so calling them in native/VF mode is a bug. Tests should cover VF0/PFID allowance where documented and nonzero VF requirements in higher-level callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c

Purpose: implements device-level PF migration state, support gating, per-VF locks/waitqueues, save-data consumption, restore-data production, debugfs read/write streaming, and total migration-size reporting.

Important APIs and control flow: `xe_sriov_pf_migration_init()` disables migration if memory-based IRQ support is missing, initializes per-VF mutexes/waitqueues, and registers cleanup for pending/descriptor/trailer packets. `xe_sriov_pf_migration_save_consume()` loops over GT migration queues, waiting on the per-VF waitqueue while data is pending but not yet ready. `xe_sriov_pf_migration_restore_produce()` handles descriptor/trailer packets at device level and dispatches other packet types to the target GT. `xe_sriov_pf_migration_read()` and `_write()` hold the per-VF lock and stream packets until the user buffer is consumed or data ends.

State and dependencies: `xe->sriov.pf.migration.disabled` gates support; each VF has `struct xe_sriov_migration_state` with waitqueue, lock, pending, descriptor, and trailer packets. Depends on per-GT control/migration APIs, packet helpers, runtime PM via debugfs callers, and SR-IOV logging.

Risks and test signals: save consumption can block interruptibly, restore must reject invalid tile/GT/type metadata, and trailer handling marks restore data done on all GTs. Tests should cover missing memirq gating, debug override behavior, wait interruption, empty save stream, descriptor/trailer validation, multi-GT size aggregation, and locked streaming partial transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h

Purpose: declares PF migration lifecycle, capability, packet flow, waitqueue, size, and user-buffer streaming APIs.

Important APIs: migration init/supported/disable, restore produce, save consume, size query, waitqueue access, debugfs-facing read, and debugfs-facing write.

Risks and test signals: callers must pass PF devices and valid VF IDs. Tests should verify `xe_sriov_pf_migration_supported()` behavior in debug and non-debug builds after `xe_sriov_pf_migration_disable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h

Purpose: defines PF migration state structures.

Important types: `struct xe_sriov_pf_migration` contains the device-level `disabled` flag. `struct xe_sriov_migration_state` contains per-VF waitqueue, mutex, currently processed pending packet, stream trailer packet, and descriptor packet.

State and risks: packet pointers are cleaned up by migration managed cleanup. Tests should verify cleanup frees partially consumed pending, descriptor, and trailer packets without double-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration_types.h -->
