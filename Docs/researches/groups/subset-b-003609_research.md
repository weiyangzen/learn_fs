# Research: subset-b-003609

Grouped source research for subset B work item `subset-b-003609`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_types.h

## Purpose
This header defines the core i915 GT engine data model. It names engine classes and physical engine IDs, describes the execlists hardware/software tracking block, and defines `struct intel_engine_cs`, the central object used by submission, reset, power management, PMU accounting, command parsing, workarounds, and user-visible engine enumeration.

## Important APIs, Types, and Functions
Important constants are engine classes (`RENDER_CLASS`, `COPY_ENGINE_CLASS`, `VIDEO_DECODE_CLASS`, `VIDEO_ENHANCEMENT_CLASS`, `COMPUTE_CLASS`, `OTHER_CLASS`), per-class maximums, `enum intel_engine_id`, `intel_engine_mask_t`, `ALL_ENGINES`, and `VIRTUAL_ENGINES`. `struct intel_hw_status_page` owns the engine HWSP VMA and CPU mapping. `struct intel_instdone` captures engine done/debug registers. `struct i915_ctx_workarounds` describes indirect/per-context workaround batches.

`struct intel_engine_execlists` carries execlists submission state: timers for timeslicing and preemption, context status buffer pointers, `active`, `inflight`, and `pending` ports, virtual-engine RB tree, context IDs, error bits, semaphore-yield state, and port count. `struct intel_engine_execlists_stats` and `struct intel_engine_guc_stats` provide alternate busyness accounting for execlists and GuC submission. `struct intel_engine_cs` ties everything together: GT/uncore pointers, IDs and UABI class/instance, logical masks, MMIO base, TLB invalidation registers, pinned contexts, sched engine, breadcrumbs, PMU samples, HWSP, workaround lists, IRQ callbacks, reset callbacks, emit/submit vfuncs, command-parser tables, statistics, sysfs-like scheduling properties, and OA/perf grouping.

The inline helpers expose engine capability bits such as command-parser use, stats support, preemption, semaphores, timeslices, virtual engine status, relative MMIO, and workaround hold-switchout usage.

## Control Flow
The header has no executable control flow beyond simple inline flag checks. Runtime flow is supplied by backends such as execlists or GuC, which fill `intel_engine_cs` callbacks during engine setup. Requests enter through `submit_request`, use emit helpers to build command buffers, update breadcrumb and active-request tracking, rely on IRQ callbacks for completion, and pass through reset hooks when recovery is required.

## State and Persistence Behavior
Most state is per-engine and persists for the engine lifetime: engine identity, UABI mapping fields, pinned kernel/bind contexts, scheduling defaults/properties, workaround lists, command-parser tables, PMU counters, status-page mappings, and reset/submission callbacks. Execlists arrays and timers are volatile submission state. `default_state`, workaround VMAs, context tags, and HWSP contents must survive normal operation but are sanitized after reset or resume.

## Dependencies and Integration Points
This header is consumed broadly by i915 GT code: engine discovery, UABI registration, execlists and GuC submission, logical-ring context setup, PMU, OA/perf, breadcrumbs, resets, workarounds, command parser, TLB invalidation, forcewake, and selftests. It depends on i915 GEM, scheduler priority lists, timelines, uncore access, wakeref handling, and platform workarounds.

## Risks
Changing engine IDs or class ordering can break legacy engine maps, UABI enumeration, GuC logical masks, and per-engine arrays. Incorrect flag semantics can enable preemption, semaphores, timeslicing, or command-parser behavior on unsupported hardware. `struct intel_engine_cs` is shared by many subsystems, so layout and lifetime changes can create subtle races around tasklets, timers, reset, PM, and request retirement.

## Test Signals
Useful signals include successful i915 build, engine discovery showing stable names and UABI classes, passing i915 selftests for engine setup, working execbuf submission on all engine classes, correct PMU busy counters, clean suspend/resume and reset, command-parser selftests, and no lockdep warnings around scheduler/tasklet/reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.c

## Purpose
This file builds the stable user-facing engine namespace from internal i915 engine objects. It sorts engines by UABI class and instance, assigns user-visible class/instance numbers and names, installs the lookup RB tree, derives scheduler capability bits, and reports which engine classes have default context isolation.

## Important APIs, Types, and Functions
`intel_engine_lookup_user()` searches `i915->uabi_engines` by class and instance. `intel_engine_add_user()` queues an engine onto `uabi_engines_llist` before final registration. `intel_engines_driver_register()` is the main registration pass: it drains the lockless list, sorts engines, filters incomplete GTs, assigns `uabi_class`, `uabi_instance`, final names, legacy indices, and RB-tree nodes, then validates debug mappings and sets scheduler caps. `intel_engines_has_context_isolation()` returns a bitmask of UABI classes with `default_state`. `intel_engine_class_repr()` maps internal classes to short names (`rcs`, `bcs`, `vcs`, `vecs`, `ccs`, `other`).

Internal helpers include `engine_cmp()`, `sort_engines()`, `set_scheduler_caps()`, `legacy_ring_idx()`, `add_legacy_ring()`, and `engine_rename()`. The `uabi_classes[]` table intentionally hides `OTHER_CLASS` from userspace by mapping it to `I915_NO_UABI_CLASS`.

## Control Flow
Engines are added during GT/engine initialization through `intel_engine_add_user()`. At driver registration, `intel_engines_driver_register()` drains the pending llist into a list, sorts it by UABI class then physical instance, and walks it once. Exposed engines are inserted into an RB tree in sorted order so later lookup is deterministic. Non-UABI engines are renamed but skipped for RB-tree exposure. The final pass computes global scheduler caps only for features available across all UABI engines.

## State and Persistence Behavior
The file mutates persistent driver state in `drm_i915_private`: `uabi_engines`, `engine_uabi_class_count`, and `caps.scheduler`. It also finalizes per-engine `uabi_class`, `uabi_instance`, `legacy_idx`, and `name`. Once registered, the mapping is expected to remain stable for the driver lifetime.

## Dependencies and Integration Points
It integrates with DRM UABI definitions (`I915_ENGINE_CLASS_*`, `I915_SCHEDULER_CAP_*`), execbuf legacy ring mapping, GuC submission capability reporting, GT unrecoverable-error state, and debug/selftest checks. Query ioctls and context engine selection depend on the RB tree created here.

## Risks
The UABI mapping must be deterministic; sorting or class-table mistakes can renumber engines and break userspace assumptions. Scheduler caps are deliberately intersection-style: if one engine lacks a feature, the global cap is disabled. Missing this can advertise unsupported scheduling behavior. Skipping engines from unrecoverable GTs prevents exposing half-initialized hardware, but also affects class counts and must match query expectations.

## Test Signals
Check `I915_QUERY_ENGINE_INFO` output for stable class/instance pairs, verify legacy execbuf rings map as expected, run debug selftests for UABI lookup/isolation, confirm scheduler caps match actual preemption/semaphore/stats behavior, and validate multi-GT failure paths do not expose incomplete engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.h

## Purpose
This header declares the engine UABI registration and lookup interface used by i915 driver setup, query paths, and context isolation reporting.

## Important APIs, Types, and Functions
The header forward-declares `struct drm_i915_private` and `struct intel_engine_cs`, then exports `intel_engine_lookup_user()`, `intel_engines_has_context_isolation()`, `intel_engine_add_user()`, `intel_engines_driver_register()`, and `intel_engine_class_repr()`.

## Control Flow
There is no internal control flow. Engine initialization code calls `intel_engine_add_user()` before final registration. Driver registration calls `intel_engines_driver_register()`. Later UABI/query code uses `intel_engine_lookup_user()` and `intel_engine_class_repr()`.

## State and Persistence Behavior
The header owns no state. Its functions manage persistent UABI engine state in `drm_i915_private` and per-engine UABI fields implemented in `intel_engine_user.c`.

## Dependencies and Integration Points
It is included by engine setup and userspace-facing engine query/registration code. It keeps the UABI mapping implementation private while exposing the minimal operations needed by the rest of i915.

## Risks
Prototype drift between this header and `intel_engine_user.c` would break engine registration or query builds. Because these calls define the user-visible engine namespace, any signature or semantic change must be coordinated with the UABI consumers.

## Test Signals
Build coverage is the main signal. Runtime signals are successful engine registration, working user-engine lookup, and correct scheduler/context-isolation reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.c

## Purpose
This file implements the legacy logical-ring/execlists submission backend for Gen8+ i915 engines. It creates and pins logical-ring contexts, queues requests by priority, submits context descriptors to ELSP/ELSQ ports, processes context status buffer events, supports preemption and timeslicing, handles virtual engines for load balancing, and participates in reset, capture, PM, IRQ, and busyness accounting.

## Important APIs, Types, and Functions
The public entry points are `intel_execlists_submission_setup()`, `intel_execlists_show_requests()`, and `intel_execlists_dump_active_requests()`. The key internal type is `struct virtual_engine`, which embeds an `intel_engine_cs`, an owning `intel_context`, a pending request, per-physical-engine RB nodes, and sibling engine pointers.

Core scheduling functions include `execlists_submit_request()`, `queue_request()`, `submit_queue()`, `kick_execlists()`, `execlists_dequeue()`, `execlists_submit_ports()`, `execlists_update_context()`, and `write_desc()`. CSB processing is handled by `process_csb()`, `csb_read()`, `gen8_csb_parse()`, `gen12_csb_parse()`, and `xehp_csb_parse()`. Context lifecycle and request allocation use `execlists_context_ops`, `execlists_context_pre_pin()`, `execlists_context_pin()`, `execlists_request_alloc()`, and `emit_pdps()`. Reset/capture paths include `execlists_reset_prepare()`, `execlists_reset_rewind()`, `execlists_reset_cancel()`, `execlists_reset_finish()`, `execlists_capture()`, and `execlists_hold()/unhold()`. Virtual submission uses `execlists_create_virtual()`, `virtual_submit_request()`, and `virtual_submission_tasklet()`.

## Control Flow
Setup installs vfuncs, IRQ masks, tasklet callbacks, timers, CSB pointers, submit registers, context tags, and engine cleanup hooks. A request submitted to an execlists engine is placed on a priority queue or hold list under the scheduler lock. If its priority exceeds the queue hint, the submission tasklet is kicked.

The tasklet first drains CSB events, promoting pending ports to inflight ports or scheduling out completed contexts. It handles preemption timeout and CS error interrupts, then dequeues new work if no submission is pending. `execlists_dequeue()` compares active contexts with queued and virtual work, may unwind incomplete requests for preemption or expired timeslice, merges adjacent same-context requests into one tail update, fills up to two ports, calls schedule-in accounting, sets preempt timers, and writes descriptors to ELSP/ELSQ. IRQ handling records CS errors, semaphore-yield requests, context-switch interrupts, and user interrupts for breadcrumbs.

Reset flow disables the tasklet, pauses the ring through the HWSP preempt semaphore, stops the command streamer, records the active CCID, drains CSB events, rewinds or cancels requests, resets CSB pointers, and re-enables the tasklet so queued work can replay.

## State and Persistence Behavior
Persistent engine state lives in `engine->execlists`: CSB head/write/status state, active/inflight/pending port arrays, virtual-engine RB tree, timers, error bits, context tag allocation, and preemption target. Request state moves between priority queues, executing request lists, hold lists, pending/inflight port references, and virtual-engine request slots. Runtime PM references and forcewake are taken on schedule-in and released on final schedule-out. Context image state is rewritten during submission, reset, and pre-pin.

## Dependencies and Integration Points
The backend integrates with logical-ring context code (`intel_lrc`), request/timeline/fence handling, `i915_sched_engine`, breadcrumbs, GT PM, uncore MMIO, MOCS, workarounds, reset machinery, i915 error capture, GVT notifiers, command emission helpers in `gen8_engine_cs`, virtual engine UABI, PMU stats, and selftests.

## Risks
The largest risks are concurrency and hardware ordering. CSB events can be stale or reordered, so reads use barriers, HWSP poisoning, MMIO fallback, and cacheline flushes. Port state is visible from tasklets, reset code, RCU readers, and retirement; reference handling mistakes can cause use-after-free or leaked requests. Preemption and timeslicing unwind requests while the GPU may still be executing them. Incorrect context-tail or force-restore handling can replay stale batches or skip dependencies. Virtual engines rely on stable sibling compatibility and careful request migration between physical engines.

## Test Signals
Signals include passing `selftest_execlists`, GPU hang/reset recovery tests, preemption and timeslice tests, semaphore wait/yield behavior, virtual-engine load balancing, request cancellation, suspend/resume, PMU busyness accuracy, no CSB invalid-event resets under load, stable breadcrumbs/user interrupts, and lockdep/KASAN-clean operation during reset and retirement stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.h

## Purpose
This header exposes the execlists submission backend interface for engine setup and debug reporting.

## Important APIs, Types, and Functions
It defines context-status notifier values `INTEL_CONTEXT_SCHEDULE_IN`, `INTEL_CONTEXT_SCHEDULE_OUT`, and `INTEL_CONTEXT_SCHEDULE_PREEMPTED`. It declares `intel_execlists_submission_setup()`, `intel_execlists_show_requests()`, `intel_execlists_dump_active_requests()`, and `intel_engine_in_execlists_submission_mode()`.

## Control Flow
There is no in-header flow. Engine initialization calls setup to install execlists callbacks. Debug/error reporting paths call the request display helpers. Backend checks can use `intel_engine_in_execlists_submission_mode()`.

## State and Persistence Behavior
The header owns no state. Its declarations operate on persistent `intel_engine_cs` and request state defined in other headers and implemented in `intel_execlists_submission.c`.

## Dependencies and Integration Points
It connects engine setup, debugfs/error-state dumping, GVT/context-status notifiers, and code that needs to distinguish execlists from other submission backends.

## Risks
The notifier enum values are consumed by context-status callbacks and must stay semantically stable. Exposing too much of the backend would make replacing execlists harder; the current header keeps the public surface narrow.

## Test Signals
Build coverage, successful engine setup, correct debug request dumps, and context-status notifier behavior under GVT/selftests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt.c

## Purpose
This file implements GGTT probing, initialization, PTE encoding, binding, invalidation, suspend/resume, aliasing PPGTT setup, GuC reservations, and cleanup for i915 GTs. It covers Gen6+ GMCH-backed GGTT and modern Gen8+ 64-bit PTE paths, while delegating older x86 GMCH handling to `intel_ggtt_gmch.c`.

## Important APIs, Types, and Functions
Public functions include `i915_ggtt_probe_hw()`, `i915_ggtt_create()`, `i915_ggtt_enable_hw()`, `i915_ggtt_init_hw()`, `i915_init_ggtt()`, `i915_ggtt_suspend_vm()`, `i915_ggtt_suspend()`, `i915_ggtt_resume_vm()`, `i915_ggtt_resume()`, `i915_ggtt_driver_release()`, `i915_ggtt_driver_late_release()`, `intel_ggtt_bind_vma()`, `intel_ggtt_unbind_vma()`, and `intel_ggtt_read_entry()`.

Important implementation groups are PTE encoders (`mtl_ggtt_pte_encode()`, `gen8_ggtt_pte_encode()`, `snb_pte_encode()`, `ivb_pte_encode()`, `byt_pte_encode()`, `hsw_pte_encode()`, `iris_pte_encode()`), insert/clear paths for Gen8 and Gen6, GGTT invalidation (`gen6_ggtt_invalidate()`, `gen8_ggtt_invalidate()`, `guc_ggtt_invalidate()`), binder updates through `MI_UPDATE_GTT`, and probe helpers for BAR/GSM mapping and scratch-page setup.

## Control Flow
Probe assigns each GT a GGTT, then chooses Gen8, Gen6, or legacy GMCH probe based on platform generation. Probe maps the GSM page-table aperture, creates scratch pages, selects PTE functions, sets VMA ops, and installs invalidation callbacks. Init reserves low/error-capture regions, GuC top address space, and guard/scratch pages, then optionally creates an aliasing PPGTT for platforms that need it.

Binding converts VMA resources into GGTT PTEs with guard pages and scratch fill. On platforms requiring GPU-side GGTT updates, it tries the BCS0 bind context and emits `MI_UPDATE_GTT`; otherwise it writes PTEs through CPU mappings. Suspend evicts or clears mappings while avoiding unnecessary PTE rewrites. Resume clears the address space, rebinds all bound VMAs, restores UC mappings, invalidates TLBs, optionally flushes CPU caches, and restores fences.

## State and Persistence Behavior
`struct i915_ggtt` persists BAR resources, GSM mapping, mappable aperture size, total GGTT size, scratch encoding, error-capture node, GuC firmware reservation, aliasing PPGTT, fence list, and invalidation/PTE callbacks. VMA `bound_flags` and `page_sizes_gtt` are updated during bind. Scratch PTEs fill unallocated or guard regions to keep speculative GPU accesses valid.

## Dependencies and Integration Points
This file integrates with PCI BAR/config probing, stolen memory, VGT ballooning, GuC submission/TLB invalidation, BCS0 bind context, GEM object/VMA binding, PPGTT code, runtime PM, fences, DPT/GGTT suspend paths, MOCS/PAT cache policy, VT-d workarounds, and error capture.

## Risks
PTE encoding is platform-sensitive; cache, local-memory, PAT, and address-mask mistakes can corrupt memory or break display/GPU access. GGTT invalidation must happen after all PTE writes are visible. Binder updates depend on the bind context being awake and not wedged; fallback paths must remain correct for reset/error capture. Aperture reservations and guard pages prevent GPU prefetch and GuC address issues, so changing them can cause hangs. Suspend/resume must not race pinned VMAs or leave stale mappings.

## Test Signals
Signals include successful GGTT probe/init on Gen6 through modern platforms, correct reported GGTT/GMADR sizes, working VMA bind/unbind and aperture mmap, GuC firmware loading with reserved top GGTT space, VT-d/BXT workaround stability, suspend/resume with display and GEM workloads, reset/error-capture success, PTE readback tests, and no GPU faults after GGTT invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.c

## Purpose
This file manages i915 GGTT fence registers, which are hardware detiler windows for tiled objects, not DMA/execution fences. It also detects and initializes memory swizzling behavior and preserves/fixes bit-17 swizzled object pages on older platforms.

## Important APIs, Types, and Functions
Public functions include `i915_vma_pin_fence()`, `i915_vma_revoke_fence()`, `i915_reserve_fence()`, `i915_unreserve_fence()`, `intel_ggtt_restore_fences()`, `intel_ggtt_init_fences()`, `intel_ggtt_fini_fences()`, `intel_gt_init_swizzling()`, `i915_gem_object_do_bit_17_swizzle()`, and `i915_gem_object_save_bit_17_swizzle()`.

Register writers are split by generation: `i830_write_fence_reg()`, `i915_write_fence_reg()`, and `i965_write_fence_reg()`, selected by `fence_write()`. `fence_update()` binds or clears a fence register for a VMA, waits for prior active users, revokes CPU mmaps when stealing a fence, and writes hardware if runtime PM says the device is active. `fence_find()` implements the LRU/active-fence selection policy.

## Control Flow
`intel_ggtt_init_fences()` detects bit-6 swizzling, determines the platform/vGPU fence count, allocates `i915_fence_reg` entries, initializes active trackers, and writes initial hardware state. A tiled VMA requiring CPU GTT detiling calls `i915_vma_pin_fence()`, which takes the GGTT mutex, finds or reuses a fence, increments its pin count, and updates hardware. Untiled access can revoke an existing fence. Reserved fences can be removed from the normal LRU for vGPU and later returned.

Swizzling detection runs once during fence init and programs i915 swizzle state. Bit-17 save/restore records page physical-address bit 17 before unpin and swaps 64-byte chunks after repin if the bit changes.

## State and Persistence Behavior
Persistent state is in `ggtt->fence_regs`, `ggtt->fence_list`, `ggtt->num_fences`, per-fence VMA/start/size/tiling/stride/dirty/pin-count fields, and `ggtt->bit_6_swizzle_x/y`. Per-object `obj->bit_17` persists the physical swizzle record across unpin/repin. Hardware fence registers are restored after resume/reset and may be skipped on runtime suspend when clearing only.

## Dependencies and Integration Points
The code integrates with GEM VMA binding and mmap revocation, frontbuffer/display fence users, vGPU fence reservation, runtime PM, uncore MMIO, MCHBAR/register swizzle detection, object page pinning, and GGTT resume/reset flows.

## Risks
Fence registers are scarce and visible to display, CPU GTT mappings, and old GPU blits. Stealing an active or pinned fence can corrupt tiled access, so waits and mmap revocation are mandatory. Generation-specific register layouts differ substantially. Swizzle detection mistakes can make tiled buffers appear corrupted to userspace. Skipping hardware clears when the device is not truly suspended can leave overlapping fence windows.

## Test Signals
Signals include tiled GEM mmap correctness, display scanout/FBC stability with tiled buffers, vGPU fence reservation behavior, suspend/resume fence restoration, bit-17 swizzle selftests on old platforms, no frontbuffer corruption after fence stealing, and lockdep-clean use of GGTT mutex/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.h

## Purpose
This header defines the software representation and public operations for GGTT fence registers and legacy swizzling support.

## Important APIs, Types, and Functions
`struct i915_fence_reg` records the list node, owning GGTT, current VMA, pin count, active tracker, register ID, dirty bit, start, size, tiling mode, and stride. The header exports fence reservation, unreservation, restoration, init/fini, VMA fence pin/revoke functionality through companion declarations, plus bit-17 swizzle save/restore helpers and `intel_gt_init_swizzling()`.

## Control Flow
The header contains declarations only. GGTT initialization calls `intel_ggtt_init_fences()`, tiled CPU/GTT access calls VMA pin/revoke helpers, resume/reset calls `intel_ggtt_restore_fences()`, and object backing-store migration paths call bit-17 swizzle helpers.

## State and Persistence Behavior
State is stored in `struct i915_fence_reg` instances allocated by `intel_ggtt_init_fences()` and in GEM object bitmaps for bit-17 tracking. The constant `I965_FENCE_PAGE` documents the page granularity used by newer fence registers.

## Dependencies and Integration Points
It depends on `i915_active` for active tracking and forward-declares GEM object, VMA, GGTT, GT, and scatterlist types. Consumers include GEM mmap/fence code, GGTT init/resume, display/frontbuffer users, and vGPU.

## Risks
Consumers must understand that these are detiling registers, not execution fences. Misusing `pin_count` or bypassing active tracking can cause tiled memory corruption. Any struct field semantic change must match `intel_ggtt_fencing.c`.

## Test Signals
Build coverage, tiled mmap/display correctness, fence init/fini leak checks, and vGPU fence reservation tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_fencing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.c

## Purpose
This file adapts pre-Gen6 x86 GMCH GTT support from the shared `intel-gtt`/AGP backend into the i915 GGTT address-space interface.

## Important APIs, Types, and Functions
The public functions are `intel_ggtt_gmch_probe()`, `intel_ggtt_gmch_enable_hw()`, and `intel_ggtt_gmch_flush()`. GGTT operations are implemented by `gmch_ggtt_insert_page()`, `gmch_ggtt_insert_entries()`, `gmch_ggtt_read_entry()`, `gmch_ggtt_clear_range()`, `gmch_ggtt_invalidate()`, and `gmch_ggtt_remove()`. `needs_idle_maps()` detects the Ironlake mobile VT-d workaround.

## Control Flow
Probe calls `intel_gmch_probe()`, retrieves total GTT size and GMADR base with `intel_gmch_gtt_get()`, sets GGTT resources and allocation callbacks, optionally enables `do_idle_maps` for Gen5 mobile VT-d systems, and installs GMCH-backed VMA operations. Enabling hardware delegates to `intel_gmch_enable_gtt()`. Insert/clear/invalidate operations directly call the GMCH GTT helpers.

## State and Persistence Behavior
The function initializes persistent GGTT fields: `vm.total`, `gmadr`, `mappable_end`, operation callbacks, invalidation callback, and `do_idle_maps`. It does not own separate PTE memory; the backend manages hardware state through `intel-gtt`.

## Dependencies and Integration Points
It depends on x86 `intel-gtt`, AGP memory-type flags, PCI devices, i915 VT-d detection, and the generic i915 GGTT VMA ops. It is selected by `intel_ggtt.c` for platforms older than Gen6 and is stubbed on non-x86 through the header.

## Risks
Legacy GMCH paths are platform- and architecture-specific. Cache flag mapping to AGP types must match expectations for uncached versus cached mappings. The Gen5 mobile VT-d idle-map workaround affects performance but avoids unsafe unmaps. Probe failure semantics are inverted by `intel_gmch_probe()` returning false on failure, so error handling must stay clear.

## Test Signals
Boot and GEM/display operation on pre-Gen6 x86 platforms, GMADR/GTT size reporting, aperture mmap correctness, VT-d active Gen5 mobile stability, and clean GMCH remove/flush paths are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.h

## Purpose
This header exposes the legacy GMCH GGTT hooks when building on x86 and provides safe `-ENODEV`/no-op stubs on non-x86 platforms.

## Important APIs, Types, and Functions
The x86 declarations are `intel_ggtt_gmch_flush()`, `intel_ggtt_gmch_enable_hw()`, and `intel_ggtt_gmch_probe()`. Non-x86 inline stubs keep callers buildable while preventing use of the x86-only backend.

## Control Flow
There is no internal flow. `intel_ggtt.c` calls these functions when the platform generation requires old GMCH support or when enabling hardware below Gen6.

## State and Persistence Behavior
The header owns no state. The implementation initializes and tears down GGTT state through `struct i915_ggtt`.

## Dependencies and Integration Points
It includes `intel_gtt.h` for GGTT types and integrates with the platform selection code in `intel_ggtt.c`. The conditional compilation boundary isolates x86 AGP/intel-gtt dependencies.

## Risks
Using the GMCH backend on non-x86 is intentionally blocked. Prototype or stub return-value changes can break probe fallback behavior in `intel_ggtt.c`.

## Test Signals
Cross-architecture builds and pre-Gen6 x86 probe/enable paths validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gpu_commands.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gpu_commands.h

## Purpose
This header centralizes i915 command-stream opcode and bit-field definitions used by kernel command emitters, the command parser, BLT helpers, pipe-control/cache flush code, media/GSC command paths, and address canonicalization helpers.

## Important APIs, Types, and Functions
The file defines instruction client fields (`INSTR_MI_CLIENT`, `INSTR_BC_CLIENT`, `INSTR_RC_CLIENT`, `INSTR_GSC_CLIENT`) and construction macros such as `MI_INSTR()`, `GFX_INSTR()`, `MEDIA_INSTR()`, and `GSC_INSTR()`. MI commands include no-op, interrupts, waits, flushes, arbitration control, context setup, semaphores, immediate/register stores, atomics, `MI_LOAD_REGISTER_IMM`, `MI_UPDATE_GTT`, register-memory commands, batch-buffer start, and math instructions.

3D and BLT definitions include pipe-control flags, render/cache invalidation bits, 3D state opcodes, color/source copy BLT commands, fast-copy tiling/MOCS fields, control-surface copy constants, and display flip encodings. GSC definitions include `GSC_FW_LOAD`, HECI limit flags, and `GSC_HECI_CMD_PKT`. Inline helpers are `gen8_canonical_addr()`, `gen8_noncanonical_addr()`, and `__gen6_emit_bb_start()`.

## Control Flow
The header has no runtime control flow except simple inline helpers. It is used by engine emit functions to compose command buffers and by parser code to recognize and validate command lengths, clients, and fields.

## State and Persistence Behavior
It stores no mutable state. Its macros encode the binary command ABI consumed by GPU command streamers across generations; those values persist as hardware contracts.

## Dependencies and Integration Points
Consumers include execlists request allocation (`MI_UPDATE_GTT`, arbitration control), engine emit helpers, command parser tables, BLT/copy paths, display flip paths, pipe-control/cache flush code, PXP/GSC HECI command submission, and GGTT binding through GPU commands.

## Risks
Opcode or bit-field mistakes can generate invalid command streams, hang the GPU, bypass command-parser restrictions, or perform cache/TLB operations incorrectly. Some bits have generation-specific meanings, such as GGTT/PPGTT addressing and GSC client aliasing with BLT client encoding. Pipe-control flags are restricted by engine/platform capabilities and must not be blindly reused on CCS or non-3D engines.

## Test Signals
Build coverage across i915, command-parser selftests, GPU hang-free batch submission, BLT copy and CCS control-surface tests, cache/TLB flush correctness, display flip tests, PXP/GSC HECI command operation, and validation of canonical address handling are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gpu_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.c

## Purpose
This file registers i915 Graphics Security Controller HECI interfaces as MEI auxiliary devices. It wires MMIO BAR resources, IRQ descriptors, optional extended operational memory, and HuC notifier integration for DG1/DG2-era GSC interfaces.

## Important APIs, Types, and Functions
Public entry points are `intel_gsc_init()`, `intel_gsc_fini()`, and `intel_gsc_irq_handler()`. Internal helpers include `gsc_init_one()`, `gsc_destroy_one()`, `gsc_irq_handler()`, `gsc_irq_init()`, `gsc_ext_om_alloc()`, `gsc_ext_om_destroy()`, and `gsc_release_dev()`.

`struct gsc_def` describes per-interface resources: MEI aux device name, HECI BAR offset, BAR size, polling mode, slow-firmware flag, and optional LMEM size. `gsc_def_dg1[]` exposes only HECI2 (`mei-gscfi`) while HECI1 is not implemented. `gsc_def_dg2[]` exposes HECI1 (`mei-gsc`) with a 4 MiB LMEM operational-memory object and HECI2 (`mei-gscfi`).

## Control Flow
`intel_gsc_init()` returns early when the device lacks HECI GSC support, then initializes both possible interfaces. `gsc_init_one()` skips non-primary tiles, skips HECI1 when PXP HECI is absent, selects a platform definition, allocates an IRQ descriptor unless polling is requested, allocates contiguous cleared LMEM for extended operational memory when required, fills `mei_aux_device` resources, initializes the auxiliary device, registers a HuC notifier for interface 0, and adds the device. Failures unwind through `gsc_destroy_one()`.

Interrupt handling receives GT IIR bits, maps bit 15 to interface 0 and bit 14 to interface 1, validates support/range, and forwards to the Linux generic IRQ layer for the per-interface IRQ descriptor.

## State and Persistence Behavior
Persistent state lives in `struct intel_gsc`: each interface records its `mei_aux_device`, optional LMEM GEM object, IRQ number, and ID. The LMEM object is pinned for the device lifetime and unpinned/dropped on teardown. Auxiliary devices persist until `intel_gsc_fini()` deletes and uninitializes them.

## Dependencies and Integration Points
The file integrates with Linux auxiliary bus and MEI aux devices, PCI resources, i915 platform feature flags (`HAS_HECI_GSC`, `HAS_HECI_PXP`), DG1/DG2 register offsets, local memory GEM allocation, HuC GSC notifier registration, GT IRQ dispatch, and PXP/GSC firmware consumers in other i915 modules.

## Risks
Resource description must match hardware exactly: wrong BAR offsets, sizes, or IRQ mapping prevent MEI communication. LMEM extended operational memory must be contiguous, pinned, and cleared. Multi-tile systems intentionally initialize only tile 0; changing that can expose nonfunctional devices. Failure unwind must avoid leaving auxiliary devices, notifiers, IRQ descriptors, or pinned GEM objects behind.

## Test Signals
Signals include MEI auxiliary devices appearing with expected names, successful GSC firmware/PXP/HuC flows, IRQ delivery on HECI events, clean init/fini unload cycles, no pinned-object leaks, correct behavior on DG1 versus DG2, and remote-tile systems skipping GSC initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.h

## Purpose
This header defines the i915 GT-side Graphics Security Controller interface state and public init/fini/IRQ entry points.

## Important APIs, Types, and Functions
`INTEL_GSC_NUM_INTERFACES` fixes the HECI interface count at two. `GSC_IRQ_INTF(_x)` maps interface IDs to GT interrupt bits, with HECI1 at bit 15 and HECI2 at bit 14. `struct intel_gsc` contains two `intel_gsc_intf` records, each holding a `mei_aux_device`, optional GEM object for scratch/operational memory, IRQ number, and interface ID. Public functions are `intel_gsc_init()`, `intel_gsc_fini()`, and `intel_gsc_irq_handler()`.

## Control Flow
The header has no executable control flow. GT initialization calls `intel_gsc_init()`, teardown calls `intel_gsc_fini()`, and GT interrupt handling calls `intel_gsc_irq_handler()` with the IIR bits.

## State and Persistence Behavior
The `intel_gsc` struct is embedded in `intel_gt` and persists for the GT lifetime. Interface fields are populated when auxiliary devices are registered and cleared during teardown.

## Dependencies and Integration Points
It forward-declares DRM/i915, GT, and MEI aux types and is included by GT type definitions and GSC implementation code. Its interrupt-bit mapping must match GT IRQ definitions and `intel_gsc.c`.

## Risks
Changing the interface count or IRQ bit mapping can break interrupt dispatch and MEI device setup. The header exposes lifetime-bearing pointers, so teardown must clear them consistently in the implementation.

## Test Signals
Build coverage, correct GT IRQ forwarding, auxiliary MEI device registration, and clean GSC teardown validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.h -->
