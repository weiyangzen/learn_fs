# Grouped Research: subset-b-003611

Grouped research for i915 GT GTT, LRC, migration, cacheability, RC6, LMEM, renderstate, reset, and ring infrastructure. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.c

Purpose: implements common i915 graphics translation table helpers for GGTT/PPGTT address spaces: page-table GEM object allocation, page-table CPU mapping, VM lifecycle teardown, scratch pages, GTT workarounds, private PAT programming, and read-scratch VMA construction.

Important APIs and functions: `i915_ggtt_require_binder()` selects the media 13.0 binder workaround; `intel_vm_no_concurrent_access_wa()` centralizes CHV/BXT VTD concurrent-access restrictions; `alloc_pt_lmem()` and `alloc_pt_dma()` allocate page-table or scratch GEM objects and attach them to the VM-wide dma-resv; `map_pt_dma()` and `map_pt_dma_locked()` pin CPU mappings for paging structures, with Meteor Lake forced WC mapping; `i915_vm_lock_objects()` locks the shared VM reservation object via scratch or top-level PD; `i915_address_space_init()` and `i915_address_space_fini()` initialize/take down krefs, locks, drm_mm, lists, minimum alignments, and reservation state; `i915_vm_release()` queues asynchronous PPGTT release; `setup_scratch_page()` creates aligned 4K or 64K scratch backing; `free_scratch()` drops scratch levels; `gtt_write_workarounds()` restores generation-specific GTT MMIO workarounds after load/reset; `setup_private_pat()` dispatches private PAT programming across BDW/CHV/ICL/TGL/XeHP/XeLP media; `__vm_create_scratch_for_read()` and `_pinned()` create optional read scratch VMAs.

Control flow: allocation paths create an internal or LMEM object, override its reservation object with `i915_vm_resv_get(vm)`, and optionally account it to a DRM client. CPU mapping selects the coherent map type, overrides MTL to WC because of suspected ATS/CAT errors, pins the object map, and marks the object unshrinkable. VM release is kref-driven: `i915_vm_put()` reaches `i915_vm_release()`, which queues `__i915_vm_release()` on the i915 workqueue; release closes all bound/unbound VMAs, synchronizes async unbind dependencies, invokes the VM-specific cleanup callback, tears down the drm_mm, and finally drops the shared reservation kref. Scratch setup tries a 64K scratch for 48-bit PPGTT huge-page cases, falls back to 4K on allocation/alignment failure, poisons it for debug, and records `scratch_order`. Workaround/PAT setup writes MMIO registers based on graphics IP and GT type.

State and persistence: persistent VM state includes the `drm_mm`, `bound_list`, `unbound_list`, scratch object array, top/pd shift, alignment table, pending unbind tree, dma-resv kref, and function-pointer backend hooks. Page-table objects persist with shared reservation locking until both VM and object users release references. Private PAT/GTT workaround state lives in hardware registers and must be restored after GPU reset. Scratch contents are a reserved safe target for invalid/unmapped PTEs.

Dependencies and integration points: depends on GEM internal/LMEM object creation, i915 VMA bind/unbind/destruction, `drm_mm`, dma-resv, intel uncore MMIO, GT MCR multicast writes, runtime graphics feature macros, and GTT/PPGTT backend callbacks declared in `intel_gtt.h`. Reset, PPGTT, GGTT, migration, renderstate, and ring code all consume these VM/page-table helpers.

Risks: shared dma-resv ownership is lifetime-sensitive because paging objects outlive VM teardown in some destruction races. `clear_vm_list()` handles dying objects by deferring VM mutex/resv freeing; a missed ref or list delete can leak VM state or UAF. Scratch page alignment and size are correctness-critical for 64K PTE mode. PAT table selection is ABI- and platform-sensitive; wrong entries produce coherency, scanout, or LMEM caching bugs. Meteor Lake WC fallback is a temporary workaround and may hide ATS ordering assumptions. Reset workarounds must be re-applied consistently after GPU reset.

Test signals: i915 selftests under `mock_gtt.c`, PPGTT/GGTT bind-unbind stress, shrinker/reclaim lockdep, suspend/resume with `skip_pte_rewrite`, reset recovery checking GTT workarounds, huge-GTT-page 64K scratch tests, MTL ATS/CAT workloads, PAT/cache-coherency validation, and fault-injection of page-table allocation/mapping paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.h

Purpose: declares the core i915 GTT address-space contract, page-table types, PTE/PDE encoding constants, VM lifetime helpers, GGTT/PPGTT structs, and backend operation hooks used by the GT memory-management code.

Important APIs and types: `struct i915_page_table`, `struct i915_page_directory`, and `struct i915_vm_pt_stash` model paging structure allocation and preallocation; `struct i915_vma_ops` defines VM-specific bind/unbind callbacks; `struct i915_address_space` is the central VM abstraction with drm_mm allocator, scratch levels, callbacks for inserting/clearing entries, and VM lists; `struct i915_ggtt` extends the VM with GMADR/GSM mappings, aperture, fences, userfault list, and global resources; `struct i915_ppgtt` wraps a private VM and root page directory. Inline helpers include `i915_vm_is_4lvl()`, `i915_vm_min_alignment()`, `i915_vm_to_ggtt()`, `i915_vm_to_ppgtt()`, `i915_vm_get/tryget/put()`, `i915_vm_resv_get/put()`, PTE/PDE index/count helpers, and DMA/vaddr page-table accessors. Prototypes cover GGTT init/suspend/resume, PPGTT creation/init, scratch setup, page-table allocation/free/stash, VMA bind/unbind, workarounds, PAT setup, and read-scratch VMAs.

Control flow: code using this header allocates an address space, fills generation-specific callbacks, calls `i915_address_space_init()`, then uses `vm->vma_ops` to bind/unbind VMA resources. Page-table stashes are preallocated and mapped before taking paths that cannot fail. PTE/PDE indexing helpers keep binding code from crossing page-table boundaries. VM references and reservation references are separate krefs: `i915_vm_put()` releases the logical VM, while `i915_vm_resv_put()` releases the lock object after all shared page-table objects stop using it.

State and persistence: the header defines persistent address-space state rather than implementing it: GTT total/reserved range, allocation color, scratch pages, bound/unbound VMA lists, pending unbind interval tree, per-memory-type alignment requirements, and function pointers for hardware-specific page insertion. GGTT persistent state includes aperture IO mapping, fence registers, error capture allocations, and optional aliasing PPGTT. PPGTT persistent state is the root page directory.

Dependencies and integration points: integrates Linux `kref`, `drm_mm`, `io_mapping`, scatterlists, dma-resv, i915 VMA/resource types, reset locking, intel memory region types, and backend implementations in `gen6_ppgtt`, `gen8_ppgtt`, GGTT files, and migration/ring/LRC users.

Risks: struct layout assumptions are enforced with `BUILD_BUG_ON` in container helpers; incompatible changes can break casts between `i915_ppgtt`/`i915_ggtt` and `i915_address_space`. PTE flag definitions are reused across backend encoders and must match hardware. `i915_pte_count()` assumes nonzero page-aligned ranges and panics on invalid input. VM callback fields must be fully initialized before binding. Reservation kref misuse can destroy locks while page-table objects still share them.

Test signals: compile-time assertions, PPGTT creation/bind/unbind selftests, VM kref leak checks, huge-page and 64K page coverage, GGTT aperture/fence tests, suspend/resume, and lockdep validation of VM mutex/reservation locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h

Purpose: declares the GT hardware-configuration blob container and init/fini entry points.

Important APIs and types: `struct intel_hwconfig` holds a byte size and pointer to parsed/raw hardware configuration data. `intel_gt_init_hwconfig(struct intel_gt *gt)` is the setup hook and `intel_gt_fini_hwconfig(struct intel_gt *gt)` releases the blob.

Control flow: GT initialization is expected to populate `gt->hwconfig` through the init function, and GT teardown releases any allocated memory through fini. This header does not define parsing semantics; it is a small contract between GT setup and hardware-config users.

State and persistence: the persistent state is a pointer/size pair attached to the GT for the lifetime between init and fini. It may represent firmware-provided or hardware-discovered capability data.

Dependencies and integration points: forward-declares `struct intel_gt` and includes only Linux integer types. Integrates with GT initialization and any downstream code that interprets hardware configuration keys.

Risks: consumers must validate `ptr` and `size` before parsing. Ownership is implicit from the init/fini pairing, so double-free or stale-pointer bugs are possible if callers bypass fini or copy the struct blindly.

Test signals: GT probe/fini tests, missing/empty hwconfig cases, malformed blob parsing in implementation files, and memory leak checks during driver unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c

Purpose: programs LLC-related IA/ring frequency tables so integrated GPUs with shared LLC can request memory-ring or CPU-reference frequencies appropriate to GT frequency.

Important APIs and functions: `intel_llc_enable()` calls `gen6_update_ring_freq()`; `intel_llc_disable()` is currently a no-op. Internal helpers include `llc_to_gt()`, `cpu_max_MHz()`, `get_ia_constants()`, `calc_ia_freq()`, and `gen6_update_ring_freq()`.

Control flow: enable reads CPU maximum frequency from cpufreq or TSC fallback, reads DCLK-derived minimum ring frequency, obtains RPS min/max raw GPU frequencies, and iterates from max to min GPU frequency. For each GPU frequency, `calc_ia_freq()` derives IA and ring ratios differently for Gen9+, Gen8, Haswell, and older shared-clock platforms, then writes the PCODE min-frequency table with `snb_pcode_write()`.

State and persistence: no software state is stored in `struct intel_llc`; the effective state is the PCU frequency table programmed into hardware. The table persists until power/reset/firmware changes require reprogramming.

Dependencies and integration points: depends on cpufreq, TSC frequency, PCODE register interface, intel RPS min/max frequency state, DCLK register, and GT uncore. It is part of GT power/frequency setup and only applies when `HAS_LLC(i915)` and not discrete graphics.

Risks: bad frequency conversion can overconstrain IA/ring frequencies or reduce memory bandwidth. `max_gpu_freq <= min_gpu_freq` is guarded to avoid an unsigned loop underflow. cpufreq absence falls back to measured TSC and relies on PCU clamping. PCODE write failures are not surfaced by `intel_llc_enable()`.

Test signals: `selftest_llc.c`, boot on Gen6-HSW/BDW/SKL class hardware, RPS min/max variation, cpufreq unavailable cases, PCODE trace/debug logging, and memory-bandwidth/power telemetry when GT frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h

Purpose: exposes the minimal LLC programming interface to GT initialization and teardown code.

Important APIs: `intel_llc_enable(struct intel_llc *llc)` programs the hardware ring/IA frequency table; `intel_llc_disable(struct intel_llc *llc)` is the matching shutdown hook and currently has no hardware work.

Control flow: callers include this header, pass the `intel_gt.llc` member, and rely on `intel_llc.c` to recover the containing GT.

State and persistence: no state is defined here; state lives in hardware PCU tables and the empty `struct intel_llc` declared in `intel_llc_types.h`.

Dependencies and integration points: forward-declares `struct intel_llc` to avoid leaking GT internals. Used by GT power-management setup.

Risks: the API assumes `intel_llc` is embedded in `struct intel_gt`; standalone allocation would break `container_of()` in the implementation.

Test signals: compile coverage of GT setup and selftest coverage from `intel_llc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h

Purpose: defines the `struct intel_llc` storage type used as an embedded marker inside `struct intel_gt`.

Important type: `struct intel_llc` is currently empty; it exists to provide a typed subobject for LLC enable/disable APIs and future state.

Control flow: implementation functions use `container_of(llc, struct intel_gt, llc)` to reach the GT.

State and persistence: no fields are stored today. Hardware-side LLC/ring-frequency state is programmed by `intel_llc.c`.

Dependencies and integration points: no includes beyond guards; included by GT type declarations and `intel_llc.h`.

Risks: because the struct is empty, its only semantic value is its embedding location. Moving or duplicating it without updating `llc_to_gt()` assumptions would break runtime behavior.

Test signals: build coverage and LLC enable selftests on platforms with shared LLC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.c

Purpose: implements i915 logical-ring-context allocation, initialization, register-state layout, descriptor construction, per-context workaround batches, pin/unpin lifecycle, reset refresh, and runtime accounting for execlists/GuC-capable engine contexts.

Important APIs and functions: exported functions include `lrc_alloc()`, `lrc_reset()`, `lrc_pre_pin()`, `lrc_pin()`, `lrc_unpin()`, `lrc_post_unpin()`, `lrc_fini()`, `lrc_destroy()`, `lrc_init_state()`, `lrc_init_regs()`, `lrc_reset_regs()`, `lrc_update_regs()`, `lrc_update_offsets()`, `lrc_check_regs()`, `lrc_indirect_bb()`, `lrc_init_wa_ctx()`, `lrc_fini_wa_ctx()`, and `lrc_update_runtime()`. Internal critical helpers include `set_offsets()`, `reg_offsets()`, per-generation context offset arrays, `init_common_regs()`, `init_ppgtt_regs()`, `__lrc_init_regs()`, `lrc_descriptor()`, Gen12/DG2 workaround batch emitters, and Gen8/Gen9 global WA batch constructors.

Control flow: allocation creates a context-state GEM object in LMEM when possible with shmem fallback, adds redzone/WA pages/parallel GuC parent scratch as needed, allocates a ring, and creates or adopts a timeline. Pinning maps the context object, sets `ce->lrc_reg_state`, initializes state once, and updates register state and LRCA descriptor using current ring tail. The context image is treated as a batch buffer of `MI_LOAD_REGISTER_IMM` commands: compact encoded offset tables are decoded into engine-relative MMIO slots, common registers and PDP/PML4 pointers are filled, WA batch pointers are installed, and STOP_RING is cleared. `lrc_update_regs()` refreshes ring start/head/tail/ctl, render RPCS/OA state, and Gen12 per-context indirect/per-context WA batches, then returns a force-restore descriptor. Reset scrubs the ring and context state, then rebuilds LRCA. WA context initialization allocates and pins a shared GGTT batch object for Gen8/9 render engines and emits indirect/per-context workaround command sequences.

State and persistence: persistent per-context state includes the context VMA, mapped register-state pointer, ring, timeline, default golden context state, WA page offsets, LRCA descriptor, runtime counters, and optional GuC parallel scratch. Per-engine persistent state includes `engine->wa_ctx` VMA and recorded indirect/per-context batch offsets and sizes. Hardware-visible state is stored in the context image and saved/restored by the GPU across context switches.

Dependencies and integration points: depends on GEM LMEM/shmem, GGTT VMA pinning, intel ring allocation, intel context/timeline lifetime, engine register definitions, OA/perf RPCS setup, PPGTT root DMA addresses, GT scratch offsets, engine workaround data, and platform feature macros. Reset code calls LRC reset paths; request submission consumes descriptors/register state; renderstate and migration rely on rings/contexts created through the same engine infrastructure.

Risks: context offset tables are platform-specific and must match hardware context image layouts; an incorrect offset corrupts register restore. WA batches are constrained to page/cacheline boundaries and missing MI_BATCH_BUFFER_END semantics differ for indirect versus per-context batches. Descriptor bit allocation changes across Gen8, Gen11, XeHP, and GuC contexts. `lrc_check_regs()` can repair some corrupt ring fields but indicates a serious submission risk. Redzone checks only exist under debug. Protected-content run-alone and DG2 predicate workarounds are subtle and platform-gated.

Test signals: `selftest_lrc.c`, live context-switch tests, execlists/GuC submission tests, reset recovery with LRC rebuild, render and compute workload switching across Gen8-Gen12/XeHP, OA state validation, context redzone debug failures, WA batch disassembly, and runtime accounting underflow selftest counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h

Purpose: declares the logical-ring-context API, context-image layout constants, descriptor bit definitions, runtime helpers, and DG2 predicate workaround offsets.

Important APIs and types: `LRC_PPHWSP_*`, `LRC_STATE_OFFSET`, and scratch offsets define context image layout. Lifecycle functions include `lrc_alloc`, `lrc_pre_pin`, `lrc_pin`, `lrc_unpin`, `lrc_post_unpin`, `lrc_fini`, and `lrc_destroy`. State programming functions include `lrc_init_state`, `lrc_init_regs`, `lrc_reset_regs`, `lrc_update_regs`, `lrc_update_offsets`, and `lrc_check_regs`. Runtime helpers `lrc_runtime_start()` and `lrc_runtime_stop()` update `intel_context_stats`. Enums and defines encode context addressing modes, fault behaviors, descriptor validity/privilege/priority bits, SW context ID fields, and DG2 predicate workaround slots.

Control flow: engine context code calls the allocation/pin/update functions during context creation and submission. Runtime start/stop guard barrier contexts, avoid nested activation, sample context timestamps, and clear the active marker.

State and persistence: constants describe persistent hardware context image offsets. The inline runtime helpers update per-context software runtime totals, active timestamp, and EWMA through `lrc_update_runtime()`.

Dependencies and integration points: includes `intel_context.h`, priority list types, bitfield helpers, and Linux integer types. Integrated by engine context ops, request submission, reset, and runtime accounting.

Risks: descriptor bit constants are hardware ABI. `LRC_STATE_OFFSET` assumes the PPHWSP is exactly one page; changing it breaks context image access. Runtime helpers rely on callers pairing start/stop around actual execution.

Test signals: build coverage, LRC selftests, runtime accounting tests, context descriptor validation, and Gen12 priority/fault-mode submission tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h

Purpose: provides register-state array indices and context-status-buffer constants for Gen8+ logical ring contexts.

Important definitions: `CTX_DESC_FORCE_RESTORE`; `CTX_CONTEXT_CONTROL`, `CTX_RING_HEAD`, `CTX_RING_TAIL`, `CTX_RING_START`, `CTX_RING_CTL`, `CTX_TIMESTAMP`, PDP/PML4 descriptor slots, and `CTX_R_PWR_CLK_STATE`; `ASSIGN_CTX_PDP()` and `ASSIGN_CTX_PML4()` macros; indirect-context default offsets for Gen8-Gen12; execlists status buffer offsets and CSB pointer masks; maximum hardware context ID values for Gen8, Gen11, Gen12, and XeHP.

Control flow: LRC initialization uses these indices to write into the context image array, and submission uses descriptor/CSB constants to force restore and parse status buffers.

State and persistence: this header defines offsets into persistent hardware-saved context images and status buffers. The macros write DMA addresses of PPGTT roots into the register-state image.

Dependencies and integration points: uses Linux types and helper functions/macros supplied by `intel_gtt.h` users, including `i915_page_dir_dma_addr()` and `px_dma()`. Consumed by `intel_lrc.c` and execlists scheduling code.

Risks: array indices include `+ 1` offsets because the context image stores `(register,value)` pairs after command words; off-by-one edits corrupt context state. Context ID maxima reserve special hardware values on Gen12/XeHP and must not be exceeded.

Test signals: LRC layout selftests, live execlists CSB parsing, context ID allocator tests, PPGTT root restore tests, and platform bring-up on each context-layout generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.c

Purpose: implements GPU-assisted memory migration and clearing for i915 GEM objects, using copy engines, a special pinned migration PPGTT, inline PTE rewriting, BLT commands, and Flat CCS auxiliary-state handling.

Important APIs and functions: `intel_migrate_init()` creates the pinned migration context; `intel_migrate_create_context()` creates per-operation contexts sharing the migration VM; `intel_migrate_copy()` and `intel_context_migrate_copy()` copy scatterlist-backed memory between system and local memory; `intel_migrate_clear()` and `intel_context_migrate_clear()` clear scatterlist ranges with a value; `intel_migrate_fini()` destroys the pinned context. Key internals include `migrate_vm()`, `xehp_insert_pte()`, `xehp_toggle_pdes()`, `insert_pte()`, `emit_no_arbitration()`, `emit_pte()`, `emit_copy()`, `emit_copy_ccs()`, `emit_clear()`, and CCS scatterlist helpers.

Control flow: initialization finds a copy engine, builds a special PPGTT with fixed 8 MiB windows per copy engine instance, preallocates page tables, maps page-table pages into the PPGTT so GPU commands can rewrite PTEs, and creates a pinned context. Copy/clear operations create or fallback to a migration context, pin it, build one or more requests, disable arbitration/preemption, emit inline PTE writes for source/destination windows, invalidate, emit BLT copy or color-fill commands, handle Flat CCS copy/overwrite when LMEM compression metadata is present, flush again, add the request, and loop over chunks until the scatterlists are consumed. On 64K-page platforms the windows are split into system-memory and LMEM regions and compact page-table layout is toggled through dummy LMEM PTE/PDE programming.

State and persistence: `struct intel_migrate` stores the pinned base context. The pinned context owns the migration PPGTT and ring state. The migration VM persists fixed virtual windows and page-table mappings for each copy-engine instance. Requests update transient PTE entries inline but rely on non-preemptible windows to keep PTE updates and BLTs atomic with respect to other migration contexts.

Dependencies and integration points: depends on copy-engine availability, `intel_context`, `i915_request`, `intel_ring_begin()`, PPGTT allocation/stash APIs, GEM LMEM/Flat CCS feature macros, scatterlist DMA addresses, BLT command definitions, MOCS indices, and request dependency handling. Integrated with GEM memory eviction/migration and LMEM clearing.

Risks: the PTE update plus BLT sequence must not be preempted; otherwise another migration context can rewrite the shared fixed windows. Engine instance address partitioning uses high 32-bit offsets, so incorrect instance handling causes overlap. 64K compact PT layout and dummy PDE toggles are fragile. Scatterlist length mismatches, CCS sideband size calculation, or missing flushes can corrupt data or leak compression metadata. The code assumes copy engines support MI_ARB_ON_OFF, MI_STORE_DATA_IMM, and BLT operations. DGFX asserts that at least one side is LMEM.

Test signals: `selftest_migrate.c`, LMEM eviction/restore, smem-to-lmem and lmem-to-smem copy tests, lmem-to-lmem copies, clear-to-zero with Flat CCS, nonzero clear, multi-copy-engine concurrency, 64K page DGFX tests, request dependency propagation, and fault injection in PPGTT/page-table setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h

Purpose: declares the public migration/clear APIs for GPU-assisted i915 memory movement.

Important APIs: `intel_migrate_init()` and `intel_migrate_fini()` manage the GT migration context. `intel_migrate_create_context()` creates a shared-VM migration context. `intel_migrate_copy()` and `intel_context_migrate_copy()` copy scatterlist memory between source and destination placements with PAT and LMEM flags. `intel_migrate_clear()` and `intel_context_migrate_clear()` clear scatterlist memory to a value. All copy/clear APIs return the last emitted `i915_request` through `out`.

Control flow: higher-level GEM migration code calls the `intel_migrate_*` wrappers with a ww context; lower-level users that already hold a pinned migration context can call `intel_context_migrate_*` directly.

State and persistence: the only declared state is `struct intel_migrate`, whose implementation stores the pinned base context. Requests returned in `out` carry asynchronous completion state for the migration work.

Dependencies and integration points: forward-declares fences/dependencies/requests/GT/scatterlists and includes `intel_migrate_types.h`. Integrated with GEM TTM/LMEM migration paths.

Risks: callers must pass DMA-mapped scatterlists and correct PAT/LMEM flags; wrong flags program wrong PTE cacheability/local-memory bits. `out` ownership must be released by callers. Wrappers may return errors after submitting a partially completed last request.

Test signals: GEM migration tests, request/fence dependency tests, API misuse checks for null migration context, and scatterlist boundary coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h

Purpose: defines the migration subsystem state embedded in `struct intel_gt`.

Important type: `struct intel_migrate` contains `struct intel_context *context`, the pinned base migration context and owner of the special migration PPGTT.

Control flow: `intel_migrate_init()` populates `context`; copy/clear operations create or borrow contexts from it; `intel_migrate_fini()` destroys and clears it.

State and persistence: the context pointer persists while migration is available for the GT. A null context means migration operations should fail with `-ENODEV`.

Dependencies and integration points: forward-declares `struct intel_context`; included by `intel_migrate.h` and GT type definitions.

Risks: lifetime is single-pointer based, so double-finalization and operations racing with teardown must be prevented by GT lifecycle ordering.

Test signals: init/fini leak checks, migration API behavior when context allocation fails, and driver unload/reload with pending migration requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c

Purpose: defines and programs Memory Object Control State tables for i915 GTs, selecting platform-specific cacheability/L3/L4 settings and installing them into global, per-engine, and L3CC registers.

Important APIs and functions: public functions are `intel_mocs_init()`, `intel_mocs_init_engine()`, and `intel_set_mocs_index()`. Internal types `drm_i915_mocs_entry` and `drm_i915_mocs_table` carry table entries, sizes, and well-known UC/WB/unused indices. Platform tables include SKL/Broxton, ICL/TGL/Gen12, DG1/DG2, and MTL variants. Helpers include `get_mocs_settings()`, `get_entry_control()`, `__init_mocs_table()`, `mocs_offset()`, `init_mocs_table()`, `get_entry_l3cc()`, `l3cc_combine()`, and `init_l3cc_table()`.

Control flow: table selection zeroes a table descriptor, chooses entries and indices based on graphics IP/platform, validates size and Gen9 skip-caching workaround restrictions, and returns flags indicating global MOCS, engine MOCS, and render L3CC programming. GT init programs global MOCS registers when supported and always programs L3CC when flagged. Engine init, called under forcewake, skips global-MOCS platforms, otherwise writes each engine's MOCS table and programs render L3CC for render engines. `intel_set_mocs_index()` caches UC and optional WB indices into `gt->mocs` for command emitters such as migration and LRC workarounds.

State and persistence: software persists selected indices in `gt->mocs`. Hardware persists MOCS and LNCFCMOCS register tables until reset or power loss, so init paths must run at GT/engine initialization and after reset as appropriate. Undefined entries are filled from `unused_entries_index` to discourage accidental reserved-index use.

Dependencies and integration points: depends on platform/IP feature macros, intel uncore forcewake MMIO, MCR multicast writes for XeHP+ L3CC, engine IDs/classes, GT MOCS storage, and command emitters that encode MOCS indices into BLTs. User-space ABI relies on stable MOCS indices for older platforms and bspec-published tables for ICL+.

Risks: MOCS indices are ABI-sensitive; changing existing entries can break userspace/GmmLib assumptions. Reserved hardware entries must be programmed but not used on ICL+. DGFX/global-MOCS handling differs from integrated platforms. `mocs_offset()` only lists known engine IDs and asserts on unsupported IDs. Wrong UC/WB indices can cause coherency or Flat CCS copy bugs.

Test signals: `selftest_mocs.c`, register readback after GT/engine init and reset, platform table selection tests across Gen9-Gen12/DG1/DG2/MTL, BLT migration coherency tests, userspace MOCS ABI tests, and forcewake/MCR validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h

Purpose: documents the MOCS programming model and declares GT/engine initialization entry points.

Important APIs: `intel_mocs_init(struct intel_gt *gt)` initializes GT-global MOCS and L3CC state; `intel_mocs_init_engine(struct intel_engine_cs *engine)` initializes per-engine MOCS state where needed; `intel_set_mocs_index(struct intel_gt *gt)` caches selected MOCS indices into GT state.

Control flow: GT setup calls global init and index selection; engine setup or reset calls per-engine init under forcewake. The header comment explains that batches reference table indices rather than direct cacheability values.

State and persistence: the header itself stores no state; hardware MOCS tables and `gt->mocs` selected indices are the persistent effects.

Dependencies and integration points: forward-declares GT and engine structures. Integrated with context workaround batches, BLT/migration command emission, and platform cacheability ABI.

Risks: callers must ensure forcewake is active for engine initialization as required by implementation. Missing init after reset can leave stale cacheability registers.

Test signals: MOCS selftests, reset register reprogramming checks, and command streams using UC/WB indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c

Purpose: implements shared PPGTT page-table allocation/free helpers, page-directory entry updates, PPGTT creation dispatch, VMA bind/unbind wrappers, page-table stash preallocation/mapping, and base PPGTT initialization.

Important APIs and functions: `alloc_pt()`, `__alloc_pd()`, `alloc_pd()`, and `free_px()` manage page-table/page-directory structures and backing GEM objects. `__set_pd_entry()`, `clear_pd_entry()`, and `release_pd_entry()` write DMA PDE entries and manage use counts. `i915_ppgtt_init_hw()` programs GTT workarounds and enables Gen6/Gen7 PPGTT hardware. `i915_ppgtt_create()` dispatches to Gen6 or Gen8 implementations. `ppgtt_bind_vma()` and `ppgtt_unbind_vma()` implement generic VMA operations using VM callbacks. `i915_vm_alloc_pt_stash()`, `i915_vm_map_pt_stash()`, and `i915_vm_free_pt_stash()` prepare fail-safe page-table allocations. `ppgtt_init()` initializes the common VM fields.

Control flow: page-table allocation creates a wrapper, allocates a VM-specific DMA object, and initializes use counts. Binding ensures the VMA range is allocated once via `vm->allocate_va_range()`, derives PTE flags from read-only and LMEM backing, inserts entries, and issues a write memory barrier. Unbind clears the range only if allocated and invalidates TLB state. Stash allocation computes how many PT/PD objects a range may need at each level, allocates them into two linked lists, maps them under object locks, and frees unused/failed stash entries.

State and persistence: page tables keep an atomic `used` count and a `base` GEM object. Page directories own an entry pointer array and spinlock. VMA resources remember whether page tables have been allocated. The PPGTT VM persists total size, DMA device, LMEM page-table flags, and bind/unbind function pointers.

Dependencies and integration points: depends on GEM LMEM/internal object allocation through VM callbacks, Gen6/Gen8 PPGTT backends, `intel_gtt.h` helper types, tracepoints, and GT hardware init. Used by normal PPGTTs and the migration PPGTT.

Risks: PDE updates must flush CPU cache lines for GPU page walkers. `release_pd_entry()` has a concurrent use-count path protected by spinlock only at the final drop; incorrect atomic ordering can double-free or leak page tables. Stash sizing intentionally overestimates for later misalignment; underestimation would introduce allocation failures in non-failing bind sections. `ppgtt_unbind_vma()` does not clear `allocated`, so page-table allocation state remains for reuse.

Test signals: PPGTT selftests, bind/unbind under memory pressure, page-table stash fault injection, Gen6/Gen8 backend creation tests, TLB invalidation validation, migration VM setup, and concurrent bind/unbind stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ppgtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.c

Purpose: manages RC6 low-power GPU states: platform setup, enable/disable, park/unpark behavior, BIOS validation, power-context allocation, runtime-PM gating, and residency counter accounting.

Important APIs and functions: public APIs are `intel_rc6_init()`, `intel_rc6_sanitize()`, `intel_rc6_enable()`, `intel_rc6_unpark()`, `intel_rc6_park()`, `intel_rc6_disable()`, `intel_rc6_fini()`, `intel_rc6_residency_ns()`, `intel_rc6_residency_us()`, `intel_rc6_print_residency()`, and `intel_check_bios_c6_setup()`. Platform helpers include `gen11_rc6_enable()`, `gen9_rc6_enable()`, `gen8_rc6_enable()`, `gen6_rc6_enable()`, `vlv_rc6_init()`, `chv_rc6_init()`, `vlv_rc6_enable()`, `chv_rc6_enable()`, `bxt_check_bios_rc6_setup()`, `rc6_supported()`, `pctx_corrupted()`, and `rc6_res_reg_init()`.

Control flow: init takes a runtime-PM wakeref to keep the GPU awake until RC6 is ready, validates support/BIOS/platform exclusions, initializes residency registers, allocates or validates VLV/CHV power context, disables RC6 for sanitization, and marks support on success. Enable forcewakes all domains, dispatches platform-specific threshold/power-gating register programming, records whether manual RC6 entry is possible, handles context-corruption workarounds, drops the runtime-PM wakeref, and marks enabled. Unpark restores automatic RC control; park optionally forces a target RC state when idle; disable reacquires the runtime-PM wakeref and clears RC registers. Fini disables, restores Meteor Lake BIOS C6 state when captured, releases power-context objects, and balances wakerefs. Residency reads forcewake-protected counters, handles VLV/CHV 40-bit high/low windows, accounts wraparound into software-extended counters, and converts hardware units to ns/us.

State and persistence: `struct intel_rc6` stores support/enabled/manual/wakeref flags, control value, BIOS RC state, power-context GEM object, residency register IDs, previous raw counters, and accumulated extended residency. Hardware state includes RC threshold registers, power-gating enables, PCBR/RC6 context base, RC_CONTROL/RC_STATE, and residency counters.

Dependencies and integration points: depends on runtime PM, uncore forcewake/MMIO, PCODE, stolen memory/GEM region allocation, GT engine enumeration, GuC RC ownership, BIOS/firmware setup, vGPU detection, clock helpers, and debugfs/seq output. Integrated with GT parking/unparking, initialization, reset/sanitize, and power-management flows.

Risks: wakeref balancing is critical: init intentionally holds runtime PM disabled until RC6 enable succeeds or fini releases it. BIOS setup checks can disable power saving on BXT/MTL. RC6 context corruption workaround can disable runtime PM to protect state. Residency wrap handling depends on sufficiently frequent reads. Wrong thresholds can increase latency or power draw. GuC RC ownership changes which RC_CTL bits the driver programs.

Test signals: `selftest_rc6.c`, runtime-PM suspend/resume, park/unpark idle tests, residency debugfs monotonicity and wrap tests, BIOS-disabled BXT/MTL paths, VLV/CHV stolen power-context allocation, GuC RC mode, and pctx corruption fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h

Purpose: declares RC6 lifecycle, parking, residency, and BIOS-state query functions.

Important APIs: `intel_rc6_init/fini`, `intel_rc6_sanitize`, `intel_rc6_enable/disable`, `intel_rc6_unpark/park`, `intel_rc6_residency_ns/us`, `intel_rc6_print_residency`, and `intel_check_bios_c6_setup`.

Control flow: GT power-management code initializes RC6, enables it when hardware state is ready, calls unpark/park as GT busy-idle state changes, sanitizes after resume/reset, queries residency for telemetry, and finalizes during teardown.

State and persistence: state is carried by `struct intel_rc6` from `intel_rc6_types.h`; this header does not define fields.

Dependencies and integration points: uses Linux integer types and forward declarations for `seq_file` and RC6 types. Integrated with GT PM, debugfs, runtime PM, and platform BIOS validation.

Risks: callers must pair init/fini and enable/disable to keep runtime-PM references balanced. Residency queries return zero when unsupported.

Test signals: GT PM tests, residency debugfs tests, suspend/resume sanitize, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h

Purpose: defines the RC6 residency enum and persistent RC6 software state for each GT.

Important types: `enum intel_rc6_res_type` identifies locked RC6, RC6, RC6p, RC6pp, and VLV media alias counters. `struct intel_rc6` stores residency register IDs, previous hardware counters, accumulated software-extended residency, enable control value, captured BIOS state, optional power-context GEM object, and boolean flags for supported/enabled/manual/wakeref/bios capture.

Control flow: `intel_rc6.c` initializes register IDs and flags, updates counters during residency reads, and uses flags to gate enable/disable/park behavior.

State and persistence: all fields persist for the GT lifetime. `prev_hw_residency` and `cur_residency` implement wrap-tolerant counter extension. `pctx` owns VLV/CHV stolen power-context backing while RC6 support is active.

Dependencies and integration points: includes spinlock/types and `intel_engine_types.h` for `i915_reg_t`; forward-declares GEM object. Embedded in GT type definitions.

Risks: counter arrays must stay indexed consistently with `enum intel_rc6_res_type`. Bitfields must be updated under lifecycle ordering that protects runtime PM and hardware access.

Test signals: residency wrap tests, init/fini leak checks for `pctx`, and platform register ID validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c

Purpose: discovers, sizes, maps, and creates the local-memory (`LMEM`) memory region for discrete Intel GPUs, including optional Resizable BAR adjustment, Flat CCS stolen-area exclusion, low-memory reservation, and TTM region initialization.

Important APIs and functions: public `intel_gt_setup_lmem()` delegates to `setup_lmem()`. Internal helpers include `_resize_bar()`, `i915_resize_lmem_bar()`, `region_lmem_init()`, `region_lmem_release()`, `get_legacy_lowmem_region()`, and `reserve_lowmem_region()`. The region ops use `intel_region_ttm_init/fini()` and `__i915_gem_ttm_object_init`.

Control flow: setup rejects non-DGFX or invalid LMEM BAR. For Flat CCS platforms it reads tile address range and CCS base MCR registers, computes usable LMEM before tile-stolen CCS memory, and warns if CCS base is missing; otherwise it reads GSMBASE. It may resize the LMEM PCI BAR on 64-bit systems, honoring `i915->params.lmem_bar_size` when supported. It applies optional module-parameter size limiting, computes IO aperture size, chooses minimum page size based on 64K-page support, creates an `INTEL_MEMORY_LOCAL` region with WC IO mapping and TTM backing, reserves DG1 legacy low 1 MiB when required, and reports reduced BAR aperture.

State and persistence: the returned `intel_memory_region` persists as GT local-memory allocator state. It owns a WC `io_mapping`, TTM region state, physical LMEM size, CPU-visible IO aperture, minimum page size, and reserved low-memory ranges.

Dependencies and integration points: depends on PCI BAR/rebar APIs, runtime PM/forcewake during BAR resize, uncore/MCR register reads, Flat CCS definitions, i915 memory region and TTM helpers, GEM LMEM object allocation, module parameters, and DGFX platform detection.

Risks: BAR resizing disables PCI memory decoding and must hold forcewake to avoid later forcewake ack timeouts. Incorrect Flat CCS subtraction can expose stolen CCS memory to normal allocations. Reduced BAR means CPU mapping covers less than total LMEM and callers must respect `io_size`. DG1 low-memory reservation prevents legacy conflicts. 32-bit builds cannot resize BAR. Invalid module parameter handling falls back to full LMEM if unsupported.

Test signals: DGFX probe on DG1/DG2/MTL, Flat CCS base/range validation, reduced/rebar BAR boot tests, module `lmem_size` and `lmem_bar_size` coverage, TTM allocation/free stress, IO mapping tests, and driver unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h

Purpose: declares the GT local-memory setup entry point.

Important API: `intel_gt_setup_lmem(struct intel_gt *gt)` returns an `intel_memory_region` for DGFX local memory or an error pointer when unavailable.

Control flow: GT probe calls this after GT/uncore PCI resources are ready and stores the returned memory region for GEM/TTM allocation.

State and persistence: the returned region owns LMEM allocator and IO mapping state until destroyed by the memory-region core.

Dependencies and integration points: forward-declares `struct intel_gt`; the return type is `struct intel_memory_region` from the wider i915 memory subsystem.

Risks: callers must handle `ERR_PTR(-ENODEV/-ENXIO/-EIO)` on platforms without valid LMEM.

Test signals: DGFX and integrated-platform probe coverage and LMEM allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_region_lmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.c

Purpose: prepares and emits generation-specific render null-state batches used to initialize render engine state before user workloads on Gen6-Gen9 render engines.

Important APIs and functions: `intel_renderstate_init()`, `intel_renderstate_emit()`, and `intel_renderstate_fini()` are public. Internal helpers include `render_state_get_rodata()` and `render_state_setup()`. `OUT_BATCH` appends auxiliary batch commands with page-bound checking.

Control flow: init chooses rodata by render engine graphics generation, allocates a one-page internal GEM object if a null state exists, creates a GGTT VMA, initializes a ww context, pins the intel context, locks and pins the VMA high/global, and calls `render_state_setup()`. Setup maps the object WB, copies the generated batch, applies relocations to the VMA GGTT offset with optional 64-bit relocation dwords, records batch offset/size, pads to cacheline, appends pooled-EU media pool state commands when needed, appends `MI_BATCH_BUFFER_END`, aligns auxiliary size, flushes and releases the map. Emit marks the VMA active and submits the main batch and optional auxiliary batch securely. Fini unpins/closes/releases VMA and context and tears down the ww context.

State and persistence: `struct intel_renderstate` stores the ww context, selected rodata, VMA, main batch offset/size, auxiliary offset/size. The batch object persists only for the init/emit/fini scope around a request.

Dependencies and integration points: depends on generated `gen6_null_state` through `gen9_null_state` rodata, GEM internal objects, GGTT VMA pinning, intel context pinning, engine `emit_bb_start`, request activity tracking, and render/media pool hardware commands.

Risks: relocation offsets must exactly match generated batch content; unresolved or malformed 64-bit relocations fail init. Batch and auxiliary data must fit in one page. Secure dispatch is used, so command validity matters. Context pinning and VMA locking use ww backoff and must clean up correctly on `-EDEADLK`. Non-render or unsupported Gen returns no-op state.

Test signals: renderstate init/emit on Gen6-Gen9 render engines, generated null-state relocation validation, pooled-EU platforms, request execution smoke tests before userspace batches, ww-deadlock retry tests, and object/VMA leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h

Purpose: declares render null-state rodata and runtime renderstate object APIs.

Important APIs and types: `struct intel_renderstate_rodata` holds relocation offsets, batch dwords, and batch item count. `RO_RENDERSTATE(_g)` builds extern rodata definitions for generated Gen-specific null-state files. `struct intel_renderstate` stores ww context, rodata, VMA, and batch/aux offsets and sizes. Functions are `intel_renderstate_init()`, `intel_renderstate_emit()`, and `intel_renderstate_fini()`.

Control flow: callers initialize a renderstate for a pinned context, emit it into an `i915_request`, then finalize to unpin and release resources.

State and persistence: renderstate state is temporary per initialization/emission sequence; rodata objects are static build-time constants.

Dependencies and integration points: includes GEM ww support and forward-declares request/context/VMA types. Integrated with generated renderstate sources and render engine initialization paths.

Risks: the `RO_RENDERSTATE` macro assumes generated symbol naming conventions. Callers must call fini after successful init, including no-rodata cases where only context/ww state may be held.

Test signals: compile/link coverage for generated rodata, renderstate emit tests, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.c

Purpose: implements GT and engine reset handling for i915, including guilty request accounting, generation-specific hardware reset sequences, GuC/GSC/display coordination, wedge/unwedge state, reset locking, user notifications, and reset timeout watchdogs.

Important APIs and functions: public functions include `__i915_request_reset()`, `intel_has_gpu_reset()`, `intel_has_reset_engine()`, `intel_reset_guc()`, `intel_gt_reset()`, `intel_gt_reset_all_engines()`, `intel_gt_reset_engine()`, `__intel_engine_reset_bh()`, `intel_engine_reset()`, `intel_gt_handle_error()`, reset lock/unlock helpers, `intel_gt_set_wedged()`, `intel_gt_unset_wedged()`, `intel_gt_terminally_wedged()`, init/fini wedge markers, `intel_gt_init_reset()`, `intel_gt_fini_reset()`, wedge watchdog init/fini, and `intel_engine_reset_needs_wa_22011802037()`. Internal reset implementations cover legacy PCI reset, G33/G4X/ILK, Gen6 domain reset, Gen8+ engine reset prepare/cancel, Gen11 SFC locks, DG2 full-reset workaround, GuC reset, and GSC WA 14015076503.

Control flow: hang handling first optionally captures error state, tries per-engine reset when supported and GuC submission is not owning resets, then escalates to global reset under `I915_RESET_BACKOFF`. Global reset serializes with reset-engine flags and SRCU readers, emits uevents, arms a wedge watchdog, optionally prepares display reset, calls `intel_gt_reset()`, and finishes display/reset notifications. `intel_gt_reset()` revokes fenced user mmaps, unwedges if possible, increments reset counters, prepares engines/GuC and forcewake, performs hardware reset with retries, restores interrupts/display overlay/uC, reinitializes GT hardware, resumes engines, and either finishes or wedges/taints on failure. Wedging stops submission, optionally resets engines, replaces submit hooks with EIO no-op submission, cancels inflight requests, and prevents new execbuf. Unwedging waits for outstanding timeline fences, resets engines, restores default submission, and clears the wedge bit when recoverable.

State and persistence: persistent reset state is `gt->reset.flags`, reset mutex, waitqueue, SRCU, and wedge work. Request/context/client state is updated through guilty/innocent counters, ban scores, request errors, skipped requests, and context bans. Hardware reset state includes forcewake-held reset domains, RC6 prevention, SFC forced locks, GGTT fences, GuC/uC state, display IRQ/reset state, and engine register defaults. Wedge-on-init/fini bits are terminal lifecycle markers.

Dependencies and integration points: depends on i915 request/context, engine PM and reset hooks, breadcrumbs, GuC/GSC firmware, display reset/overlay/IRQ code, GGTT/fence restore, error capture, runtime PM, PCI config/MMIO uncore, SRCU/RCU/wait queues, stop-machine-related VMA mmap revocation constraints, and CI taint reporting.

Risks: reset runs in delicate contexts with bottom halves disabled for engine reset. Global resources such as fence registers and GGTT are clobbered, requiring SRCU backoff and mmap revocation. Gen11 SFC lock handling must unlock even on timeout and includes paired VCS/VECS cases. Reset retry choices trade corruption risk against wedging. Wedge/unwedge swaps submit hooks and relies on synchronization to prevent requests slipping through. Display-clobbering resets require IRQ/display coordination. GSC WA introduces 200 ms delays or skips GSC reset only under specific idle conditions.

Test signals: `selftest_reset.c`, `selftest_hangcheck.c`, simulated debugfs resets, per-engine hang recovery, global reset fallback, GuC submission reset paths, display-clobber platforms, SFC video reset tests, wedged/unwedged debugfs recovery, request guilty/ban accounting tests, reset lock contention, suspend/resume after reset, and CI taint/uevent observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h

Purpose: declares the GT/engine reset, wedge, error handling, and reset-lock APIs used across i915.

Important APIs: `intel_gt_init_reset/fini_reset`, `intel_gt_handle_error()`, `intel_gt_reset()`, `intel_engine_reset()`, `__intel_engine_reset_bh()`, `__i915_request_reset()`, reset trylock/interruptible lock/unlock, `intel_gt_set_wedged()`, `intel_gt_unset_wedged()`, `intel_gt_terminally_wedged()`, wedge-on-init/fini markers, `intel_gt_reset_engine()`, `intel_gt_reset_all_engines()`, `intel_reset_guc()`, `intel_wedge_on_timeout()` helper macro, `intel_has_gpu_reset()`, `intel_has_reset_engine()`, and `intel_engine_reset_needs_wa_22011802037()`. `I915_ERROR_CAPTURE` controls error-state capture.

Control flow: users report hangs through `intel_gt_handle_error()` or direct engine/global reset APIs; code needing protection from reset uses the SRCU reset lock helpers; long reset sections can use `intel_wedge_on_timeout()` to schedule automatic wedging.

State and persistence: declarations operate on `struct intel_reset` embedded in the GT, request error state, and engine reset flags.

Dependencies and integration points: includes compiler/types/SRCU, engine types, and reset types. Used by request allocation/submission, hangcheck, display reset, GuC code, and GEM error paths.

Risks: reset lock users must always release the SRCU tag. `__intel_engine_reset_bh()` is bottom-half-oriented and has stricter context expectations than `intel_engine_reset()`. Wedge-on-init/fini are intentionally irreversible.

Test signals: reset API build coverage, lock/unlock pairing tests, hangcheck selftests, and wedge timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h

Purpose: defines the persistent reset coordination state and reset flag bit layout for each GT.

Important type and constants: `struct intel_reset` contains `flags`, `mutex`, `queue`, and `backoff_srcu`. Flag bits include `I915_RESET_BACKOFF`, engine-specific bits starting at `I915_RESET_ENGINE`, and high bits `I915_WEDGED_ON_INIT`, `I915_WEDGED_ON_FINI`, and `I915_WEDGED`.

Control flow: global reset sets `I915_RESET_BACKOFF` to block reset-sensitive users and reset-engine attempts; per-engine reset uses `I915_RESET_ENGINE + engine->id`; wedging sets `I915_WEDGED`; init/fini failures add terminal wedge bits. The waitqueue wakes clients when reset backoff ends, and SRCU protects code sections that cannot race with global reset resource clobbering.

State and persistence: all fields persist for the GT lifetime. The mutex serializes wedging/unwedging. The waitqueue and SRCU manage concurrent users around reset.

Dependencies and integration points: includes mutex, waitqueue, and SRCU headers. Embedded in `struct intel_gt` and consumed by `intel_reset.c` plus callers using reset locks.

Risks: flag bit allocation must leave enough room for all engine reset bits before high wedge bits. Incorrect memory ordering around flag updates can allow execbuf or reset users through at unsafe times.

Test signals: reset flag contention tests, SRCU lock coverage, wedge/unwedge races, and build-time assertions in reset code for engine-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c

Purpose: implements intel ring-buffer allocation, pinning, mapping, space accounting, reset/unpin/free, and command reservation for i915 engine requests.

Important APIs and functions: `intel_ring_update_space()`, `__intel_ring_pin()`, `intel_ring_pin()`, `intel_ring_reset()`, `intel_ring_unpin()`, `intel_engine_create_ring()`, `intel_ring_free()`, and `intel_ring_begin()`. Internal helpers include `create_ring_vma()` and `wait_for_space()`.

Control flow: ring creation allocates an `intel_ring`, validates power-of-two size and `RING_CTL_SIZE`, sets wrap/effective size, creates a GGTT VMA backed by LMEM, stolen memory, or internal shmem fallback, marks it read-only on GPUs with GGTT read-only support, and initializes space. Pinning increments `pin_count`; the first pin GGTT-pins the VMA with an offset bias to avoid offset-zero wrap hangs, maps it through iomap on non-LLC mappable objects or coherent GEM map otherwise, marks it unshrinkable, resets pointers, and stores `vaddr`. `intel_ring_begin()` reserves qword-aligned command space plus request finalization space, decides whether wrapping is needed, waits for earlier requests if the ring lacks space, fills wrap tail with MI_NOOPs, poisons debug memory, advances `emit`, and returns a CPU pointer for command emission.

State and persistence: `intel_ring` stores kref, VMA, size/effective size, wrap shift, head/tail/emit offsets, free space, pin count, and mapped CPU address. VMA backing persists until ring kref free; mapping and unshrinkable status persist while pinned.

Dependencies and integration points: depends on GEM object creation in LMEM/stolen/internal memory, GGTT pinning, VMA iomap/fenceability, coherent map type selection, i915 requests/timelines for space waits, engine registers/commands, and request reserved-space conventions. Used by LRC contexts, migration command emission, renderstate emission, and general engine request construction.

Risks: ring wrap logic is safety-critical; `need_wrap` writes MI_NOOPs to avoid executing stale commands. Packets must be qword aligned. `reserved_space` is assumed sufficient for request finalization and cannot fail late. Waiting for space relies on timeline request ordering and target postfix offsets. Non-LLC iomap versus GEM map selection must match cache coherency. Read-only ring buffers protect against stray GPU writes only where GGTT supports it.

Test signals: `selftest_ring.c`, request submission stress with small rings, wraparound at end-of-ring, interruptible wait behavior, timeline retire freeing space, non-LLC/stolen/iomap platforms, LMEM ring allocation, reset pointer rebuild, and debug poison checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c -->
