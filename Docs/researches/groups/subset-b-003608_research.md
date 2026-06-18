# subset-b-003608 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.c

## Purpose
`gen8_engine_cs.c` emits low-level command-stream sequences for Gen8+ i915 engines. It covers render and non-render cache flushes, TLB invalidation, batch-buffer starts, initial and final request breadcrumbs, user interrupts, preemption points, and several platform workarounds for Gen8 through Xe HP style hardware.

## Important APIs, Types, and Functions
Important exported functions include `gen8_emit_flush_rcs()`, `gen8_emit_flush_xcs()`, `gen11_emit_flush_rcs()`, `gen12_emit_flush_rcs()`, `gen12_emit_flush_xcs()`, `gen8_emit_init_breadcrumb()`, `gen8_emit_bb_start()`, `gen8_emit_bb_start_noarb()`, `xehp_emit_bb_start()`, `xehp_emit_bb_start_noarb()`, `gen8_emit_fini_breadcrumb_xcs()`, `gen8_emit_fini_breadcrumb_rcs()`, `gen11_emit_fini_breadcrumb_rcs()`, `gen12_emit_fini_breadcrumb_xcs()`, `gen12_emit_fini_breadcrumb_rcs()`, and `gen12_emit_aux_table_inv()`. Internal helpers include `preparser_disable()`, `gen12_get_aux_inv_reg()`, `gen12_needs_ccs_aux_inv()`, `mtl_dummy_pipe_control()`, `preempt_address()`, `hwsp_offset()`, `emit_preempt_busywait()`, `gen8_emit_fini_breadcrumb_tail()`, `gen12_emit_preempt_busywait()`, and the DG2/MTL hold-switchout semaphore helpers.

## Control Flow
Flush paths reserve ring space with `intel_ring_begin()`, assemble PIPE_CONTROL or MI_FLUSH_DW packets based on `EMIT_FLUSH` and `EMIT_INVALIDATE`, then commit with `intel_ring_advance()`. Gen8 render invalidation may prepend VF/DC workaround pipe controls; Gen11 splits flush and invalidate into separate PIPE_CONTROL packets; Gen12 may emit dummy depth flushes, HDC/CCS flushes, parser disable/enable commands, and AUX table invalidation waits. Batch-buffer start paths either disable arbitration around the batch for no-preempt/noarb cases or enable it before the user batch and disable it afterwards. Final breadcrumb paths write the request seqno to HWSP/GGTT, emit a user interrupt, optionally busy-wait for preemption or switchout workaround semaphores, set `rq->tail`, and append two workaround dwords to avoid lite restore with `HEAD == TAIL`.

## State and Persistence
Persistent effects are GPU-visible command dwords written into the request ring and seqno writes to the timeline HWSP. `rq->infix`, `rq->tail`, and `rq->wa_tail` are updated so request accounting, preemption, and unwind logic know the command boundaries. The file does not own durable objects; it mutates ring contents and request metadata for later submission and retirement.

## Dependencies and Integration Points
The file depends on `intel_ring` space management, `intel_gpu_commands.h` packet definitions, engine/register definitions, request/timeline state, platform predicates such as `GRAPHICS_VER_FULL()`, `IS_DG2()`, `HAS_FLAT_CCS()`, and GuC submission state. Engine setup assigns these emitters into engine function tables, and request construction uses them when flushing caches, starting user batches, and completing breadcrumbs.

## Risks and Edge Cases
The main risks are incorrect dword counts, missing parser disable around TLB invalidations, invalid GGTT/HWSP alignment, and platform workaround predicates that are too broad or too narrow. Gen12 AUX invalidation has tight ordering requirements: memory traffic must be quiesced, the AUX invalidation register must be written, and a semaphore wait must observe completion. Breadcrumb emission also depends on qword-aligned tail and seqno writes; mistakes can break fence signaling, preemption, or hang attribution.

## Test Signals
Useful signals include gem/i915 request completion tests, cache/TLB invalidation tests after PPGTT updates, self-modifying batch relocation paths, preemption and no-preempt workloads, DG2/MTL workaround coverage, GuC versus execlists submission, and ring-tail alignment assertions from debug kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h

## Purpose
`gen8_engine_cs.h` declares the Gen8+ command emission API and provides small inline helpers for building PIPE_CONTROL, PIPE_CONTROL post-sync writes, and MI_FLUSH_DW GGTT writes.

## Important APIs, Types, and Functions
The header exposes generation-specific flush, batch start, init breadcrumb, final breadcrumb, and AUX table invalidation functions used by engine backends. Inline helpers include `__gen8_emit_pipe_control()`, `gen8_emit_pipe_control()`, `gen12_emit_pipe_control()`, `__gen8_emit_write_rcs()`, `gen8_emit_ggtt_write_rcs()`, `gen12_emit_ggtt_write_rcs()`, `__gen8_emit_flush_dw()`, and `gen8_emit_ggtt_write()`.

## Control Flow
Inline helpers advance a caller-provided dword pointer while writing fixed command packet layouts. PIPE_CONTROL helpers clear six dwords, set opcode and flag groups, and write the post-sync offset. RCS GGTT write helpers emit a qword PIPE_CONTROL write with global GTT selection. XCS GGTT write uses MI_FLUSH_DW with `MI_FLUSH_DW_USE_GTT` and stored-dword operation.

## State and Persistence
There is no owned state. The helpers persist GPU command state only by writing into the caller's ring or batch buffer. `GEM_BUG_ON()` guards enforce qword alignment and the MI_FLUSH_DW bit-5 workaround for GGTT addresses.

## Dependencies and Integration Points
The header depends on `intel_gpu_commands.h`, `intel_gt_regs.h`, and GEM debug assertions. It is included by Gen8+ engine emission code and by paths that need to assemble breadcrumb or flush packets without duplicating packet layout details.

## Risks and Edge Cases
Because these helpers encode hardware packet formats, any off-by-one in packet length, flag grouping, or address alignment can corrupt the ring stream. The Gen12 PIPE_CONTROL helper accepts two flag groups, so callers must keep generation-specific flags in the correct dword.

## Test Signals
Compile-time users catch signature drift. Runtime signals include ring parser validation, breadcrumb completion, cache flush correctness, and debug assertions on misaligned HWSP/GGTT addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_engine_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c

## Purpose
`gen8_ppgtt.c` implements Gen8+ per-process graphics translation table management. It allocates and tears down multi-level page-table trees, encodes PTEs/PDEs, inserts normal and huge-page mappings, clears ranges back to scratch entries, initializes scratch tables, handles vGPU page-table notifications, and constructs `i915_ppgtt` address spaces.

## Important APIs, Types, and Functions
The exported entry point is `gen8_ppgtt_create()`. PTE/PDE encoding helpers include `gen8_pde_encode()`, `gen8_pte_encode()`, and `gen12_pte_encode()`. Tree helpers include `gen8_pd_range()`, `gen8_pd_contains()`, `gen8_pt_count()`, `gen8_pd_top_count()`, `gen8_pdp_for_page_index()`, and `gen8_pdp_for_page_address()`. Lifecycle functions include `gen8_ppgtt_cleanup()`, `gen8_ppgtt_alloc()`, `gen8_ppgtt_clear()`, `gen8_ppgtt_foreach()`, `gen8_init_scratch()`, `gen8_alloc_top_pd()`, `gen8_preallocate_top_level_pdp()`, and `gen8_init_rsvd()`. Mapping functions include `gen8_ppgtt_insert()`, `gen8_ppgtt_insert_pte()`, `gen8_ppgtt_insert_huge()`, `xehp_ppgtt_insert_huge()`, `gen8_ppgtt_insert_entry()`, and `xehp_ppgtt_insert_entry()`.

## Control Flow
Creation initializes the `i915_ppgtt`, chooses 3- or 4-level topology, selects read-only support and LMEM/SMEM page-table allocators, installs PTE insertion/clear/foreach callbacks, initializes scratch objects, allocates the top page directory, preallocates 3-level PDP entries when needed, notifies vGPU if active, and reserves a workaround VMA if required. Range allocation walks page-directory levels, pulls tables from the stash, fills them with scratch encodings, installs them under `pd->lock`, and updates `used` counters. Range clearing recursively replaces PTEs/PDEs with scratch entries and frees empty page-table pages. Insert paths walk scatter-gather DMA segments, encode PTEs with PAT/cache/read-only/LMEM bits, support 2M and 64K layouts, flush CPU caches for written page-table pages, and record actual GTT page sizes.

## State and Persistence
Persistent state lives in `ppgtt->pd`, `vm->scratch[]`, page-table objects, `px_used()` counters, `pt->is_compact`, `vma_res->page_sizes_gtt`, and optional `vm->rsvd` workaround objects. vGPU creation/destruction writes PDP addresses and notifications through the vgt interface. Page-table memory is GPU-visible and remains active until VM cleanup or range clear frees unused subtrees.

## Dependencies and Integration Points
This file depends on GEM internal/LMEM allocation, scatterlist DMA iteration, `intel_gtt` page-table helpers, PAT/cache helpers, vGPU PV info, and GT platform feature predicates. Its callbacks are consumed by VMA bind/unbind paths, context VM setup, GGTT/PPGTT invalidation flows, and selftests that validate huge-page behavior.

## Risks and Edge Cases
Risks center on concurrency and page-table accounting: `used` counters must prevent freeing tables still being walked, locks must be dropped around allocation safely, and scratch entries must match page size/layout. Huge-page insertion is subtle for mixed SG alignment, compact 64K LMEM layout, and scratch padding. Gen11/Gen12 read-only disablement is a hardware workaround. vGPU notification increments top PD use so virtualized page tables are never removed prematurely.

## Test Signals
Strong tests include bind/unbind range stress, random VM allocation/clear, 4K/64K/2M page-size combinations, LMEM versus system memory mappings, read-only PTE faults on supported gens, vGPU create/destroy paths, reserved-wa VMA placement, and debug assertions under concurrent VM teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h

## Purpose
`gen8_ppgtt.h` is the public header for Gen8+ PPGTT creation and GGTT PTE encoding.

## Important APIs, Types, and Functions
It declares `gen8_ppgtt_create(struct intel_gt *gt, unsigned long lmem_pt_obj_flags)` and `gen8_ggtt_pte_encode(dma_addr_t addr, unsigned int pat_index, u32 flags)`. The source file in this subset implements PPGTT creation; GGTT PTE encoding is declared here for users outside this file.

## Control Flow
The header contains declarations only. Callers request a new `i915_ppgtt` from GT setup or GEM context/VM code and use the GGTT encoder when producing platform-compatible GGTT PTE values.

## State and Persistence
No state is owned by the header. `gen8_ppgtt_create()` returns an address-space object with persistent page-table and scratch state managed by the VM lifecycle.

## Dependencies and Integration Points
The header forward-declares `i915_address_space` and `intel_gt` and depends on Linux kernel integer/DMA types. It is the integration point between GT initialization, VM binding code, and the Gen8+ page-table implementation.

## Risks and Edge Cases
Prototype drift would break VM setup across the driver. Callers must pass the correct GT and LMEM page-table allocation flags for the target platform because those choices shape later page-table allocation behavior.

## Test Signals
Build coverage catches declaration mismatches. Runtime coverage comes from PPGTT VM creation, context creation, page-table binding, and GGTT PTE encoding tests on Gen8+ and LMEM-capable platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_renderstate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_renderstate.c

## Purpose
`gen8_renderstate.c` embeds a generated Gen8 null render-state batch and its relocation offsets. The renderstate layer uses it to initialize predictable render pipeline state without constructing the packet stream at runtime.

## Important APIs, Types, and Functions
The file defines `gen8_null_state_relocs[]` and `gen8_null_state_batch[]`, then invokes `RO_RENDERSTATE(8)` to generate the exported renderstate descriptor/accessors expected by `intel_renderstate.h`.

## Control Flow
There is no procedural control flow beyond static initialization. At runtime the renderstate framework selects this Gen8 descriptor, applies relocation offsets from `gen8_null_state_relocs[]` into the generated batch payload, and submits/copies the command stream as part of render-state setup.

## State and Persistence
All data in this file is immutable static command/state payload. Persistent GPU effects occur only when the renderstate framework submits the batch and the hardware consumes the state commands. The `cmds end`, `state start`, and `state end` comments mark regions inside the generated array.

## Dependencies and Integration Points
The file depends on `intel_renderstate.h` and the `RO_RENDERSTATE()` macro convention. It integrates with render engine initialization and any path that needs the Gen8 null render state before user workloads execute.

## Risks and Edge Cases
Because the payload is generated hardware command data, manual edits are risky. Incorrect relocation offsets or stale generated data can program invalid surface/state addresses or leave render units in an unexpected state. Compatibility is tied to Gen8 command encoding, not to later Gen9+ packet variants.

## Test Signals
Relevant signals include GPU boot/render initialization tests, render pipeline sanity tests that run before userspace batches, relocation validation in the renderstate loader, and comparison against regenerated intel-gpu-tools output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_renderstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen9_renderstate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen9_renderstate.c

## Purpose
`gen9_renderstate.c` embeds the generated Gen9 null render-state batch and relocation table used to program known render pipeline state on Gen9 hardware.

## Important APIs, Types, and Functions
The file defines `gen9_null_state_relocs[]` and `gen9_null_state_batch[]`, then invokes `RO_RENDERSTATE(9)` to create the Gen9 renderstate descriptor consumed by the shared renderstate framework.

## Control Flow
The source has static data only. Runtime behavior is driven by `intel_renderstate`: select the Gen9 descriptor, patch the four relocation sites in the batch, and submit the generated command/state stream to initialize render state.

## State and Persistence
State is an immutable static array in the driver image. Persistent GPU state changes occur only after the batch is emitted to the render engine. Array markers identify command and state sections, and the `-1` relocation terminator ends relocation scanning.

## Dependencies and Integration Points
The file depends on `intel_renderstate.h` and generated payload compatibility with Gen9 command encodings. It is used by render engine setup paths that need null state for Gen9 platforms.

## Risks and Edge Cases
Gen9 differs slightly from Gen8 in generated packet contents and relocation offsets, so sharing or misselecting payloads would be unsafe. Since this is generated code, review should focus on provenance, array boundaries, relocation values, and whether the generator version matches the target hardware documentation.

## Test Signals
Signals include render engine initialization, null-state submission success, GPU hangs during early render workloads, relocation patch coverage, and comparing the embedded payload with regenerated intel-gpu-tools output for the intended Gen9 platform set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen9_renderstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c

## Purpose
`hsw_clear_kernel.c` embeds a generated Haswell GPU kernel used by i915 render clear paths. It is data-only code containing precompiled EU instructions.

## Important APIs, Types, and Functions
The only symbol is `static const u32 hsw_clear_kernel[]`, a generated instruction stream. There are no C functions or exported types in this file.

## Control Flow
Control flow is encoded inside the GPU instruction words, not in C. The including/consumer code supplies this array as a shader/kernel payload for clear operations on Haswell-generation render hardware.

## State and Persistence
The array is immutable driver data. GPU-visible persistence happens when consumers copy or reference the kernel in a batch/state object. The file itself owns no locks, allocations, or runtime state.

## Dependencies and Integration Points
The file intentionally has no includes in the snippet and is normally consumed by a render clear implementation that includes or references the array. Its generated provenance comes from IGT GPU Tools and must match Haswell EU ISA expectations.

## Risks and Edge Cases
Manual modification is high risk because the words are opaque hardware instructions. Incorrect instruction data can cause GPU hangs, bad clears, or memory corruption. The symbol is `static`, so integration depends on inclusion or same-translation-unit use rather than external linkage.

## Test Signals
Signals include Haswell render clear selftests, framebuffer/buffer clear correctness, GPU hangcheck during clear batches, and binary comparison against the known generated kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/hsw_clear_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c

## Purpose
`intel_breadcrumbs.c` implements i915 request completion notification. It tracks contexts with requests waiting for breadcrumb signaling, lazily arms engine interrupts, runs bottom-half work through `irq_work`, signals dma fences, and removes completed/canceled waiters.

## Important APIs, Types, and Functions
Public functions include `intel_breadcrumbs_create()`, `intel_breadcrumbs_reset()`, `__intel_breadcrumbs_park()`, `intel_breadcrumbs_free()`, `i915_request_enable_breadcrumb()`, `i915_request_cancel_breadcrumb()`, `intel_context_remove_breadcrumbs()`, and `intel_engine_print_breadcrumbs()`. Important internals include `__intel_breadcrumbs_arm_irq()`, `intel_breadcrumbs_disarm_irq()`, `add_signaling_context()`, `remove_signaling_context()`, `signal_irq_work()`, `irq_signal_request()`, and `insert_breadcrumb()`.

## Control Flow
When a waiter enables a breadcrumb, active incomplete requests are inserted into the context's ordered `signals` list under `ce->signal_lock`; the context is added to the breadcrumb `signalers` RCU list when the first request appears. IRQ work drains already-signaled requests from an llist, walks signaling contexts in RCU read-side critical sections, stops at the first incomplete request per context, removes completed requests, and then signals dma fences outside the context signal lock. Interrupts are armed lazily when signalers exist and disarmed after an interrupt interval with no listeners or when the engine parks.

## State and Persistence
State is stored in `struct intel_breadcrumbs`: reference count, active count, `signalers`, `signaled_requests`, IRQ lock/work state, interrupt enable count, wakeref token, and engine hooks. Requests persist list membership through `rq->signal_link`, `rq->signal_node`, and `I915_FENCE_FLAG_SIGNAL`; contexts are held by reference while they appear in `signalers`.

## Dependencies and Integration Points
The file depends on dma-fence internals, request completion helpers, timeline retirement, engine IRQ enable/disable hooks, GT PM wakerefs, RCU lists, spinlocks, and irq_work. It integrates with request wait paths, engine interrupt handlers via `intel_engine_signal_breadcrumbs()`, context teardown, request retirement, and debug dumping.

## Risks and Edge Cases
Concurrency is the primary risk. The code must avoid signaling callbacks while holding `ce->signal_lock`, keep RCU list removal safe, balance request/context references, and avoid disabling interrupts while a waiter can still appear. Already-completed requests are fast-pathed into `signaled_requests`. Park/free paths must ensure IRQ work is drained and no signalers remain.

## Test Signals
Useful tests cover many waiters on one context, waiters across contexts, request completion racing with enable/cancel, engine park/unpark, interrupt storms, fence callback reentrancy, context removal with completed signals, and debug assertions for empty signaler lists at free time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h

## Purpose
`intel_breadcrumbs.h` declares the breadcrumb signaling API and small lifecycle helpers for engine request-completion notifications.

## Important APIs, Types, and Functions
It declares creation/free/reset/park functions, request enable/cancel functions, context cleanup, and debug printing. Inline helpers are `intel_breadcrumbs_unpark()`, `intel_breadcrumbs_park()`, `intel_engine_signal_breadcrumbs()`, `intel_breadcrumbs_get()`, and `intel_breadcrumbs_put()`.

## Control Flow
Callers create breadcrumbs for an IRQ-capable engine, unpark/park them with engine PM, queue irq work from interrupt context through `intel_engine_signal_breadcrumbs()`, and enable/cancel request-specific breadcrumbs around waits. Reference management uses `kref`.

## State and Persistence
The header does not own state, but its inlines mutate `b->active`, queue `engine->breadcrumbs->irq_work`, and adjust `b->ref`. The persistent fields are defined in `intel_breadcrumbs_types.h`.

## Dependencies and Integration Points
It depends on Linux atomics and irq_work plus the breadcrumb type definition. It is included by engine PM, request wait, interrupt, and debug code.

## Risks and Edge Cases
`intel_breadcrumbs_park()` calls the heavy park path only when the active count reaches zero, so active reference imbalance can leave IRQs armed or prematurely disarm them. `intel_engine_signal_breadcrumbs()` assumes `engine->breadcrumbs` is initialized and safe for IRQ work queueing.

## Test Signals
Build coverage validates prototypes. Runtime signals include balanced park/unpark counts, IRQ work firing from interrupts, reference-counted free after engine cleanup, and request wait wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h

## Purpose
`intel_breadcrumbs_types.h` defines `struct intel_breadcrumbs`, the shared state container for i915 request breadcrumb signaling and IRQ management.

## Important APIs, Types, and Functions
The central type is `struct intel_breadcrumbs`. Important fields are `ref`, `active`, `signalers_lock`, `signalers`, `signaled_requests`, `signaler_active`, `irq_lock`, `irq_work`, `irq_enabled`, `irq_armed`, `engine_mask`, `irq_engine`, and IRQ enable/disable function pointers.

## Control Flow
The comments document the design: instead of waking every waiter on every interrupt, the implementation wakes/uses a first client to perform coherent seqno checks, then cascades wakeups for completed clients and transfers bottom-half responsibility through the signaler queue.

## State and Persistence
All fields are runtime state. Lists persist request/context wait state until completion/cancel, `irq_armed` persists a GT PM wakeref while interrupts are expected, and `irq_enabled` tracks hardware interrupt enable nesting.

## Dependencies and Integration Points
The type depends on irq_work, kref, list/llist, spinlocks, engine type definitions, engine masks, and wakeref tokens. It is consumed by `intel_breadcrumbs.c`, engine PM, engine interrupt signaling, and debug paths.

## Risks and Edge Cases
The lock partition is important: `signalers_lock` protects signaler list modifications, `irq_lock` protects hardirq-sensitive interrupt state, and `signaler_active` gates context teardown waiting for RCU walkers. Misusing these fields can race interrupt disarm with waiter insertion or free a context while it is being walked.

## Test Signals
Test signals include lockdep, RCU debug, request wait stress, park/free assertions, interrupt enable/disable balance, and contexts with ordered signal lists under heavy completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c

## Purpose
`intel_context.c` implements the core i915 hardware context lifecycle: allocation, initialization, state allocation, pin/unpin, active tracking, request creation, parent/child binding for parallel submission, runtime statistics, and ban/revoke behavior.

## Important APIs, Types, and Functions
Public functions include `intel_context_create()`, `intel_context_alloc_state()`, `intel_context_free()`, `__intel_context_do_pin_ww()`, `__intel_context_do_pin()`, `__intel_context_do_unpin()`, `intel_context_init()`, `intel_context_fini()`, `i915_context_module_init()`, `i915_context_module_exit()`, `intel_context_enter_engine()`, `intel_context_exit_engine()`, `intel_context_prepare_remote_request()`, `intel_context_create_request()`, `intel_context_get_active_request()`, `intel_context_bind_parent_child()`, `intel_context_get_total_runtime_ns()`, `intel_context_get_avg_runtime_ns()`, `intel_context_ban()`, and `intel_context_revoke()`.

## Control Flow
Creation allocates from a slab and initializes fields from the engine. State allocation runs under `pin_mutex`, rejects banned contexts, calls `ce->ops->alloc()`, sets `CONTEXT_ALLOC_BIT`, and accounts objects to DRM clients. Pinning ensures state is allocated, locks HWSP/ring/state objects through the ww context, pins ring/timeline/state, calls backend `pre_pin`, acquires active tracking, serializes on `pin_mutex`, rejects closed contexts, performs first-pin backend setup, and publishes `pin_count`. Unpin decrements `pin_count`, calls backend unpin/post-unpin at zero, releases active tracking, and preserves a temporary context reference across asynchronous active release. Request creation pins the context, creates an i915 request, unpins, and adjusts lockdep nesting for timeline mutex use.

## State and Persistence
Persistent state includes the context reference, VM reference, timeline, ring, state VMA, `pin_count`, `active_count`, `i915_active`, flags, GuC state, parallel relationship fields, runtime EWMA/total counters, and slab allocation. Pinned state prevents shrinker reclamation of ring/context/timeline objects while GPU-visible. RCU delayed free protects readers of context fields.

## Dependencies and Integration Points
The file depends on GEM object/VMA locking and pinning, timelines, rings, `i915_active`, request creation, scheduler/GuC state, DRM client accounting, tracepoints, and engine PM. It is used by engine setup, userspace context creation, kernel contexts, request submission, hang recovery, and context reconfiguration paths.

## Risks and Edge Cases
The pin path has multiple nested resources and must unwind in exact reverse order. `pin_count` publication uses memory barriers so other CPUs do not see a pinned context before backend state is valid. Closed/banned contexts reject new pin/allocation. Remote requests must not target their own context and must keep the target context image/timeline pinned until the modifying request retires. Parallel parent/child pointers rely on immutability after binding and parent pinning for safe child access.

## Test Signals
Signals include context creation/destruction stress, ww deadlock retry coverage, pin/unpin reference balance, shrinker interaction, request creation under memory pressure, banned/revoked context behavior, GuC active request lookup, runtime accounting, parallel context binding, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h

## Purpose
`intel_context.h` declares the core context API and defines inline helpers for context references, pinning, timeline locking, activity entry/exit, scheduling flags, ban/revoke state, and runtime clocks.

## Important APIs, Types, and Functions
The header exposes creation/lifecycle functions, pin/unpin functions, request helpers, remote request preparation, active request lookup, SSEU reconfiguration, and runtime statistic readers. Important inlines include `intel_context_is_child()`, `intel_context_is_parent()`, `intel_context_to_parent()`, `intel_context_is_parallel()`, `intel_context_lock_pinned()`, `intel_context_is_pinned()`, `intel_context_pin()`, `intel_context_pin_ww()`, `intel_context_unpin()`, `intel_context_enter()`, `intel_context_exit()`, `intel_context_get()`, `intel_context_put()`, `intel_context_timeline_lock()`, `intel_context_close()`, flag getters/setters for semaphores/banned/exiting/nopreempt/own-state, and `intel_context_clock()`.

## Control Flow
Most helpers are small state transitions. Pinning first tries to increment a nonzero `pin_count`, falling back to the full pin path. Unpin either directly decrements or hands the final pin to an asynchronous `sched_disable()` operation. Enter/exit update `active_count`, call backend `enter`/`exit`, and hold/release GT PM wakerefs while active. Timeline locking uses nested lock classes for parent and child parallel contexts.

## State and Persistence
The header manipulates persistent `struct intel_context` fields defined in `intel_context_types.h`: flags, pin count, active count, timeline, wakeref, ops, and parallel metadata. It also defines constants such as `PARENT_SCRATCH_SIZE` and `INTEL_CONTEXT_BANNED_PREEMPT_TIMEOUT_MS`.

## Dependencies and Integration Points
It depends on active tracking, driver types, engine types, ring/timeline types, GT PM, and trace helpers. It is included by nearly every GT component that creates requests, submits work, waits on contexts, or manages context power state.

## Risks and Edge Cases
Inline state changes are widely used and must preserve locking expectations. `intel_context_to_parent()` asserts parent pinning before child access. The asynchronous sched-disable unpin path can leave `pin_count == 2` while scheduling disable owns a pin. `intel_context_close()` does not itself wait for users; backend `close` behavior matters.

## Test Signals
Build coverage catches API drift. Runtime signals include lockdep for timeline nesting, pin/unpin balance, context active PM reference balance, nopreempt/banned/exiting flag semantics, and parallel submission selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h

## Purpose
`intel_context_param.h` provides a tiny context-parameter helper for setting the per-context watchdog timeout.

## Important APIs, Types, and Functions
The only helper is `intel_context_set_watchdog_us(struct intel_context *ce, u64 timeout_us)`, which stores the timeout in `ce->watchdog.timeout_us`.

## Control Flow
There is no branching. Callers include this header when translating a user or internal context parameter into the context watchdog field.

## State and Persistence
The helper persists the timeout in the context object. Enforcement is elsewhere; this header only sets the stored value.

## Dependencies and Integration Points
It depends on `intel_context.h` and Linux integer types. It integrates with context parameter plumbing and watchdog/hang detection code that later reads `ce->watchdog.timeout_us`.

## Risks and Edge Cases
There is no validation in this helper, so callers must clamp or reject invalid timeout values before calling it. Concurrent updates require external serialization if the field is visible to submission or watchdog code.

## Test Signals
Tests should cover context parameter setting, boundary timeout values, and watchdog behavior that consumes the stored microsecond timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c

## Purpose
`intel_context_sseu.c` reconfigures a Gen8+ context's slice/subslice/EU partitioning by updating the context RPCS register state, including active contexts that need an ordered GPU-side modification.

## Important APIs, Types, and Functions
The public API is `intel_context_reconfigure_sseu()`. Internal helpers are `gen8_emit_rpcs_config()` and `gen8_modify_rpcs()`.

## Control Flow
`intel_context_reconfigure_sseu()` locks the context pin state, compares the requested `intel_sseu` with `ce->sseu`, and if changed asks `gen8_modify_rpcs()` to update active hardware state. If the context is idle/unpinned, the new SSEU is simply stored and will be programmed on next pin. If active, a kernel request is created on the same engine, serialized with the remote context through `intel_context_prepare_remote_request()`, emits a `MI_STORE_DWORD_IMM` to the context image's `CTX_R_PWR_CLK_STATE`, and submits the request. On success, `ce->sseu` is updated.

## State and Persistence
Persistent state is `ce->sseu` and the RPCS dword in the logical render context image. Active updates temporarily pin the target context and add a request that keeps the context image/timeline alive until retirement.

## Dependencies and Integration Points
The file depends on context pinning, engine kernel request creation, ring emission, LRC state offsets, SSEU RPCS encoding, and remote request serialization. It integrates with userspace context parameter changes or internal code that needs per-context EU partitioning.

## Risks and Edge Cases
The path is Gen8+ only and asserts that with `GEM_BUG_ON()`. Updating an active context by CPU writes is not enough, so the GPU-side ordered request is required. Failure after creating the request must still submit/add the request and unpin the context. Callers rely on `pin_mutex` to keep pinned/idle state stable while deciding update mode.

## Test Signals
Tests include SSEU reconfiguration on idle and busy contexts, invalid/unsupported SSEU masks before entry, request ordering relative to work on the target context, and checking that RPCS state changes survive context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h

## Purpose
`intel_context_types.h` defines the core `struct intel_context` data model and backend `struct intel_context_ops` used by i915 submission engines.

## Important APIs, Types, and Functions
`struct intel_context_ops` defines backend hooks for allocation, pinning, unpinning, request cancellation, enter/exit, stats update, reset, destroy, virtual engine creation, parallel context creation, and sibling lookup. `struct intel_context` contains references, engine/inflight pointers, VM, GEM context pointer, breadcrumb signal lists, context state VMA, ring, timeline, wakeref, flags, LRC state/descriptor/tag, stats, active/pin tracking, ops pointer, SSEU, pinned context list link, workaround batch page, GuC state, GuC ID, destroyed link, parallel submission metadata, and selftest fault-injection flags.

## Control Flow
This header has no runtime control flow, but its fields drive the lifecycle implemented in `intel_context.c`, breadcrumb signaling in `intel_breadcrumbs.c`, GuC submission, LRC setup, and parallel submission. Bit definitions under `flags` encode context state transitions such as allocated, valid, closed, banned, nopreempt, GuC initialized, perma-pinned, parking, exiting, low-latency, and own-state.

## State and Persistence
The structure is the persistent in-memory representation of a GPU context. It owns/holds references to GPU-visible state objects, scheduling state, active and pin counters, runtime accounting, and submission metadata for both execlists and GuC paths.

## Dependencies and Integration Points
The header depends on active tracking, software fences, engine types, SSEU, wakerefs, and GuC firmware ABI definitions. It is the shared contract between engine setup, context lifecycle code, scheduler backends, breadcrumbs, PM, hang recovery, and selftests.

## Risks and Edge Cases
Several fields are accessed under RCU or special locks, so readers must honor the documented protection. `inflight` encodes a pointer plus low-bit count, making alignment assumptions important. Parent/child parallel pointers are immutable after creation but not fully refcounted in both directions. GuC state has its own lock and must not be mixed with timeline or pin locks incorrectly.

## Test Signals
Signals include lockdep/RCU debug, context lifecycle selftests, GuC scheduling tests, parallel submission tests, breadcrumb wait tests, runtime stats validation, and fault-injection paths for dropped GuC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h

## Purpose
`intel_engine.h` is the main public façade for i915 engine objects. It defines engine MMIO access macros, engine masks, status-page layout, execlist helpers, and prototypes/inlines for engine initialization, cleanup, IRQ, reset, idle, diagnostics, virtual engines, heartbeat/property clamping, and pinned contexts.

## Important APIs, Types, and Functions
Important macros include `ENGINE_READ*`, `ENGINE_WRITE*`, engine class masks, `I915_GEM_HWS_*` status-page offsets, `execlists_num_ports()`, `execlists_active()`, `intel_read_status_page()`, and `intel_write_status_page()`. Declared functions include engine init/free/release, common setup/cleanup, resume, ring submission setup, stop/cancel CS, pending MI forcewake wait, active head/batch head reads, instdone capture, IRQ enable/disable, idle checks, dump helpers, busy-time retrieval, hung-entity lookup, context-size calculation, pinned context creation/destruction, CCS enablement, property clamping, and virtual/parallel engine creation.

## Control Flow
The header provides fast-path inlines for reading/writing engine-relative registers through `intel_uncore`, checking GuC/virtual/heartbeat capabilities, getting virtual siblings, and setting/clearing hung context pointers. `execlists_active()` uses repeated READ_ONCE and memory barriers to read a stable active request pointer.

## State and Persistence
No state is owned by the header, but it defines persistent hardware status-page offsets used for preemption, seqno, migration, GGTT bind, PXP, GSC, and scratch values. The write helper flushes status-page cachelines before and after stores to make HW-visible writes robust.

## Dependencies and Integration Points
The header depends on PMU/request/selftest, engine/GT/timeline/workaround types, uncore register helpers, and GuC virtual-engine helpers. It is included across GT code and is the API boundary for engine lifecycle, command submission, debugging, PM, heartbeat, and reset flows.

## Risks and Edge Cases
Register macros assume register definitions accept an engine base parameter. Status-page offsets are ABI-like within the driver and must remain aligned with command emission code. Virtual engine heartbeat is only valid with GuC submission. Inline state helpers such as hung context pointer setters have no locking, so callers must provide the correct synchronization.

## Test Signals
Build coverage catches macro/prototype drift. Runtime signals include engine init on all platform engine masks, MMIO register dump correctness, HWSP seqno/preempt paths, virtual engine creation, heartbeat capability checks, and reset/hung-context capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c

## Purpose
`intel_engine_cs.c` implements i915 engine discovery, setup, common initialization, teardown, idle/reset helpers, diagnostics, hung request discovery, busy-time access, and pinned kernel/bind context creation. It is the central implementation behind the `intel_engine.h` API.

## Important APIs, Types, and Functions
Important public functions include `intel_engine_context_size()`, `intel_engine_set_hwsp_writemask()`, `intel_engines_init_mmio()`, `intel_engine_init_execlists()`, `intel_engine_create_pinned_context()`, `intel_engine_destroy_pinned_context()`, `intel_engines_init()`, `intel_engine_cleanup_common()`, `intel_engine_resume()`, `intel_engine_get_active_head()`, `intel_engine_get_last_batch_head()`, `intel_engine_stop_cs()`, `intel_engine_cancel_stop_cs()`, `intel_engine_wait_for_pending_mi_fw()`, `intel_engine_get_instdone()`, `__intel_engine_flush_submission()`, `intel_engine_is_idle()`, `intel_engines_are_idle()`, `intel_engine_irq_enable()`, `intel_engine_irq_disable()`, `intel_engines_reset_default_submission()`, `intel_engine_can_store_dword()`, `intel_engine_dump_active_requests()`, `intel_engine_dump()`, `intel_engine_get_busy_time()`, `intel_engine_create_virtual()`, `intel_engine_get_hung_entity()`, and `xehp_enable_ccs_engines()`. Major internals include the `intel_engines[]` metadata table, fuse-pruning helpers, `intel_engine_setup()`, `init_status_page()`, `intel_engine_init_tlb_invalidation()`, `engine_setup_common()`, `measure_breadcrumb_dw()`, `engine_init_common()`, and diagnostic dump helpers.

## Control Flow
MMIO initialization starts with the platform engine mask, applies media/compute/GSC/DG2 fuses, assigns logical IDs, allocates each engine, computes reset domains/MMIO bases/GuC IDs/default properties/context size, sanitizes HWSP writes, and records engines in GT arrays. Full engine initialization chooses GuC, execlists, or ring submission setup, runs common setup, calls the backend setup, creates pinned kernel and optional GGTT bind contexts, measures final breadcrumb dword size, and registers the engine for userspace. Cleanup unwinds scheduler, breadcrumbs, retire/cmd parser, default state, pinned contexts, status page, and workaround lists. Idle/reset helpers flush submission tasklets, inspect scheduler queues and ring head/tail/mode, stop the command streamer with `STOP_RING`, wait for forcewake completion, and read instdone registers. Dump paths capture requests, ring buffers, LRC state, registers, HWSP, breadcrumbs, heartbeat, and properties.

## State and Persistence
Persistent engine state includes allocated `intel_engine_cs` objects in `gt->engine[]`, `gt->engine_class[][]`, engine masks/counts, status-page VMA and CPU map, scheduler engine, breadcrumbs, workarounds, TLB invalidation register metadata, pinned kernel/bind contexts, properties/defaults, latency stats, reset domains, and uABI registration. The status page and pinned contexts remain GPU-visible until cleanup.

## Dependencies and Integration Points
The file depends on GEM object/VMA allocation, GGTT pinning, GT/uncore/register helpers, GuC and execlists submission backends, command parser, workarounds, breadcrumbs, PM/retire/heartbeat, reset, MCR reads, scheduler engine, request dumping, and platform fuse registers. It is the integration hub for engine setup at driver load/resume and for error capture/hang recovery.

## Risks and Edge Cases
Engine masks must reflect fused-off hardware before forcewake pruning and engine allocation. TLB invalidation register selection intentionally avoids catch-all future platform matching; unsupported platforms return errors/warnings. Status pages must avoid unsafe high GGTT placement on non-LLC platforms. Cleanup assumes GPU access has stopped. Diagnostics read live hardware snapshots and may race with execution, so they use references/RCU where needed but are best-effort. Pinned context creation relies on perma-pinning and special lockdep classes to be safe inside engine PM barriers.

## Test Signals
High-value tests include engine discovery across platform masks/fuses, GuC/execlists/ring backend selection, status-page allocation and cleanup, command parser init failure unwinds, TLB invalidation on each engine class, heartbeat/breadcrumb measurement, idle checks after submission/reset, stop-ring timeout handling, error-state dumps, virtual engine creation, and selftests included at the bottom of the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c

## Purpose
`intel_engine_heartbeat.c` implements periodic engine liveness checks. While an engine is awake, it submits low-priority kernel-context pulse requests, escalates priority if a heartbeat stalls, and triggers engine/GT error handling when progress cannot be restored.

## Important APIs, Types, and Functions
Public functions include `intel_engine_init_heartbeat()`, `intel_engine_unpark_heartbeat()`, `intel_engine_park_heartbeat()`, `intel_gt_unpark_heartbeats()`, `intel_gt_park_heartbeats()`, `intel_engine_set_heartbeat()`, `intel_engine_pulse()`, and `intel_engine_flush_barriers()`. Key internals include `next_heartbeat()`, `heartbeat_create()`, `idle_pulse()`, `heartbeat_commit()`, `show_heartbeat()`, `reset_engine()`, `heartbeat()`, `__intel_engine_pulse()`, and `set_heartbeat()`.

## Control Flow
Unpark schedules delayed heartbeat work when the interval is nonzero. The worker flushes submission, checks any previous systole request, obtains an engine PM wakeref if awake, skips wedged GTs, detects disabled schedulers, escalates a stuck heartbeat through normal, heartbeat, and barrier priorities if scheduling supports it, or calls reset handling. If no heartbeat is outstanding and the engine serial changed, it tries to lock the kernel timeline, creates a kernel request, attaches idle barriers, queues it, and schedules the next heartbeat. Setting heartbeat changes the interval under engine PM and kernel timeline lock and optionally sends a barrier pulse to recheck execution.

## State and Persistence
Persistent heartbeat state lives in `engine->heartbeat.work`, `engine->heartbeat.systole`, `engine->heartbeat.blocked`, `engine->props.heartbeat_interval_ms`, `engine->wakeref_serial`, and request `emitted_jiffies`/priority fields. Outstanding systole requests hold references until completed or parked.

## Dependencies and Integration Points
The file depends on kernel workqueues, engine PM, kernel contexts, request creation/commit/queue internals, scheduler priority updates, barrier task handling, GT reset/error capture, GuC hung-context discovery, and engine dump diagnostics. PM unpark/park paths start and stop heartbeats.

## Risks and Edge Cases
Too-short custom heartbeat intervals can preempt innocent work or downgrade reset precision, so warnings are emitted when the interval is below twice preempt timeout. The worker must avoid blocking allocations and timeline locks in some paths. A stuck kernel timeline lock is itself treated as a possible liveness failure. GuC mode requires manual hung-context discovery if GuC hang detection is unavailable.

## Test Signals
Signals include heartbeat selftests, forced pulse behavior, priority escalation, disabled scheduler reset paths, hangcheck on/off behavior, engine park/unpark cancellation, barrier flush requests, and custom interval warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h

## Purpose
`intel_engine_heartbeat.h` declares heartbeat and barrier-flush APIs for engine liveness management.

## Important APIs, Types, and Functions
The header declares `intel_engine_init_heartbeat()`, `intel_engine_set_heartbeat()`, `intel_engine_park_heartbeat()`, `intel_engine_unpark_heartbeat()`, `intel_gt_park_heartbeats()`, `intel_gt_unpark_heartbeats()`, `intel_engine_pulse()`, and `intel_engine_flush_barriers()`.

## Control Flow
Callers initialize heartbeat work during engine PM setup, unpark/park heartbeats as engines or GTs wake/sleep, adjust intervals through the property setter, force an immediate pulse for liveness checking, and flush idle barriers by submitting a kernel request.

## State and Persistence
The header owns no state. Implementations mutate `engine->heartbeat`, engine properties, and kernel-context request state.

## Dependencies and Integration Points
Only `intel_engine_cs` and `intel_gt` are forward-declared here. The API is consumed by engine PM, sysfs/property code, hangcheck paths, and barrier management.

## Risks and Edge Cases
Callers must only pulse engines that support preemption/reset semantics, and must coordinate with engine PM so heartbeat work does not outlive initialized engine state.

## Test Signals
Build coverage for prototypes plus runtime tests for init, park/unpark, interval changes, forced pulse, and barrier flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c

## Purpose
`intel_engine_pm.c` implements engine wakeref get/put callbacks. It resets/scrubs pinned contexts on unpark, starts breadcrumbs and heartbeats, parks engines by switching to a safe kernel context when needed, drains idle barriers, and initializes engine PM state.

## Important APIs, Types, and Functions
Public functions are `intel_engine_init__pm()` and `intel_engine_reset_pinned_contexts()`. Important internals include `intel_gsc_idle_msg_enable()`, `dbg_poison_ce()`, `__engine_unpark()`, `duration()`, `__queue_and_release_pm()`, `switch_to_kernel_context()`, `call_idle_barriers()`, and `__engine_park()`. `wf_ops` connects these callbacks to `intel_wakeref`.

## Control Flow
On unpark, the engine obtains a GT PM wakeref, waits for the kernel context to leave inflight state, optionally poisons the context image in debug builds, resets the kernel context image, calls backend unpark, unparks breadcrumbs, and starts heartbeat. On park, it clears saturation, attempts to switch to the perma-pinned kernel context for execlists-style safe suspend, returning `-EBUSY` if that request must first run. Once safe, it calls idle barrier callbacks, parks heartbeat and breadcrumbs, calls backend park, and asynchronously releases the GT wakeref. `switch_to_kernel_context()` constructs a barrier-priority request without the usual timeline mutex assumptions because engine PM park has exclusive submission ownership.

## State and Persistence
Persistent state includes `engine->wakeref`, `engine->wakeref_track`, `engine->wakeref_serial`, kernel context state, pinned context list, heartbeat/breadcrumb activity, and barrier task llist. Debug poisoning writes `CONTEXT_REDZONE` into context images to catch stale trust in suspend-corrupted state.

## Dependencies and Integration Points
The file depends on breadcrumbs, contexts, heartbeat, GT PM, RC6/GSC registers, ring/request internals, shmem utilities, and engine backend park/unpark/reset hooks. It is called from engine initialization and runtime PM wakeref transitions.

## Risks and Edge Cases
The park path is lock-order sensitive because it can run while retiring requests. It open-codes part of context enter and carefully orders timeline active-list insertion, request queueing, and wakeref deferred park to avoid underflow. GuC submission skips kernel-context switching because scheduling disable provides the idle guarantee. Pinned LMEM context images may be corrupted across suspend and must be reset.

## Test Signals
Signals include engine PM selftests, runtime suspend/resume with active and idle engines, kernel context switch-on-park, barrier callback flushing, breadcrumb/heartbeat active counts, GSC idle message setup on media v13, and pinned context reset after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h

## Purpose
`intel_engine_pm.h` provides inline engine PM wakeref helpers and declares engine PM initialization/reset functions.

## Important APIs, Types, and Functions
Important helpers include `intel_engine_pm_is_awake()`, `__intel_engine_pm_get()`, `intel_engine_pm_get()`, `intel_engine_pm_get_if_awake()`, `intel_engine_pm_might_get()`, `intel_engine_pm_put()`, `intel_engine_pm_put_async()`, `intel_engine_pm_put_delay()`, `intel_engine_pm_flush()`, `intel_engine_pm_might_put()`, and `intel_engine_create_kernel_request()`. Declarations include `intel_engine_init__pm()` and `intel_engine_reset_pinned_contexts()`.

## Control Flow
The inlines delegate to `intel_wakeref` and GT PM helpers. Virtual engines fan out `might_get`/`might_put` to physical sibling wakerefs. `intel_engine_create_kernel_request()` wraps `i915_request_create(engine->kernel_context)` with an explicit engine PM get/put because the kernel context is also used inside the engine-PM barrier.

## State and Persistence
The helpers mutate `engine->wakeref` counts and, for virtual engines, physical sibling wakeref expectations plus GT PM expectations. Kernel request creation persists a request on the engine's perma-pinned kernel context.

## Dependencies and Integration Points
The header depends on driver/request/engine/GT PM and wakeref types. It is used by context code, heartbeat, breadcrumbs, SSEU reconfiguration, request creation, and engine PM implementation.

## Risks and Edge Cases
Kernel context requests outside the PM barrier must take a PM reference or race with park/unpark. Virtual engines require special handling because their PM state maps to several physical engines. `get_if_awake()` callers must tolerate a false result without forcing wake.

## Test Signals
Signals include PM reference balance, virtual-engine wakeref propagation, kernel request creation while engines park/unpark, and flush waiting for delayed wakeref puts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h

## Purpose
`intel_engine_regs.h` defines engine-relative MMIO register offsets and bitfields used by i915 command streamer, execlist, context, power, predicate, nonprivileged access, SFC, and media clock-gating code.

## Important APIs, Types, and Functions
The header is macro-only. Major register groups include ring head/tail/start/control, sync registers, PSMI/max-idle, ACTHD/DMA_FADD/IPEIR/IPEHR/INSTDONE, HW status page, HWSTAM, MI_MODE, interrupt mask/error/status registers, RPCS fields, reset control, batch-buffer state/address, context control, PDP registers, execlist status/control, timestamps, force-to-nonprivileged slots, CS GPRs, SFC lock/status registers, and VDBOX clock-gating controls.

## Control Flow
There is no C control flow. Other code passes these macros to engine-relative accessors such as `ENGINE_READ(engine, RING_HEAD)` or `ENGINE_WRITE(engine, RING_MI_MODE, value)`, where the engine MMIO base is supplied at call time.

## State and Persistence
The header owns no runtime state. It defines the address/bit layout for persistent hardware registers. Writes to these registers configure engine execution, context save/restore, reset, interrupts, PPGTT, scheduling, MOCS overrides, and media units.

## Dependencies and Integration Points
It depends on `i915_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is included by engine setup, command emission, reset, PM, workarounds, context SSEU, diagnostics, and media/video code.

## Risks and Edge Cases
Incorrect offsets or bit masks can program the wrong hardware register. Several offsets alias across generations, such as `ACTHD`/`GEN8_R_PWR_CLK_STATE`, so callers must select by platform. Engine-relative macros require a base-aware register accessor; direct uncore use without supplying the correct base would be wrong.

## Test Signals
Signals include register dump sanity, engine bring-up on every class, reset and stop-ring behavior, context switch and PPGTT enablement, SFC lock tests, workarounds using force-to-nonprivileged slots, and platform-specific MMIO validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h

## Purpose
`intel_engine_stats.h` provides inline execlists engine busyness accounting helpers for context-in/context-out transitions.

## Important APIs, Types, and Functions
The two helpers are `intel_engine_context_in(struct intel_engine_cs *engine)` and `intel_engine_context_out(struct intel_engine_cs *engine)`. Both operate on `engine->stats.execlists`.

## Control Flow
`intel_engine_context_in()` increments nested active count if already active; otherwise it disables local IRQs, begins a seqcount write, records `ktime_get()` as the start time, increments active, ends the seqcount, restores IRQs, and asserts active is nonzero. `intel_engine_context_out()` decrements nested active count if more than one context is active; otherwise it disables local IRQs, begins a seqcount write, decrements active, adds elapsed time since `start` to `total`, ends the seqcount, and restores IRQs.

## State and Persistence
Persistent state is `engine->stats.execlists.active`, `start`, `total`, and the seqcount lock. The total accumulated busy time feeds PMU/stat readers and engine diagnostics.

## Dependencies and Integration Points
The header depends on atomics, ktime, seqlock, GEM assertions, and `intel_engine.h`. It is used by execlists context switch paths and read by PMU or busy-time helpers that need consistent snapshots from hardirq-capable readers.

## Risks and Edge Cases
The writer is serialized by the submission backend, but readers may run in hardirq, so seqcount and local IRQ disabling are required. Active underflow is fatal. Nested active counts must match context in/out events or total busy time will be inflated or lost.

## Test Signals
Signals include PMU busy-time tests, nested context switch accounting, active underflow debug assertions, hardirq reader consistency, and engine dump runtime values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_stats.h -->
