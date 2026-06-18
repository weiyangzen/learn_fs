# subset-b-003626 i915 VMA, device, GVT, memory, and pcode research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.c

Purpose: implements the core i915 virtual memory area lifecycle for GEM objects bound into GGTT, DPT, or per-process GPU address spaces. It creates per-object/per-VM/per-view singleton VMAs, pins and binds them into `drm_mm`, builds special scatter-gather views, tracks GPU activity, and unbinds or destroys VMAs safely.

Important APIs/functions: exports `i915_vma_instance`, `i915_vma_bind`, `i915_vma_pin_ww`, `i915_vma_pin`, `i915_ggtt_pin`, `i915_vma_unbind`, `i915_vma_unbind_async`, `__i915_vma_evict`, `i915_vma_wait_for_bind`, `i915_vma_pin_iomap`, `i915_vma_revoke_mmap`, `i915_vma_parked`, and shrinkability helpers. Internal helpers cover allocation from `slab_vmas`, VMA lookup/creation in the object rb-tree, `i915_vma_insert`, rotated/remapped/partial page-table construction, active callbacks, GGTT fencing, scanout flag cleanup, and forced destruction.

Control flow: `i915_vma_instance()` first looks up a matching VMA under `obj->vma.lock`; `vma_create()` resolves races while inserting into the object tree and VM unbound list. Pinning gets pages, optionally prepares async bind work and page-table stash, locks `vm->mutex`, inserts a `drm_mm_node` when needed, binds missing global/local PTEs, records active page counts, and increments the pin count. Unbind waits for active/async bind completion, revokes mmap/fences/iomap, snapshots resource state into `i915_vma_resource_unbind()`, clears bind flags, detaches the node, invalidates TLBs for synchronous unbind, and drops page pins. Closed VMAs are deferred to `i915_vma_parked()` for idle-time destruction.

State and persistence: state is in `struct i915_vma`: `node`, `vm`, `obj`, `pages`, `iomap`, `fence`, `guard`, pin/bind/error flags, `active`, `pages_count`, `gtt_view`, object/vm/closed list links, and current `resource`. It is in-memory only and lifetime is bounded by the GEM object or VM close. Async bind/unbind fences can outlive the live VMA through refcounted `i915_vma_resource` snapshots.

Dependencies and integration: depends on GEM object locking and page pinning, `drm_mm`, `i915_active`, dma fences, `i915_vma_resource`, GGTT fencing, GT runtime PM, TLB invalidation, display frontbuffer and scanout code, TTM/lmem object helpers, and selftests. Display exports use `i915_display_vma_interface`.

Risks: lock ordering is delicate across object reservation locks, `vm->mutex`, runtime PM, async fence work, and shrinkers. Incorrect page-view SG construction can corrupt display mappings. Failing to flush GGTT writes, revoke userfault mmap, or invalidate TLBs before page release risks stale CPU/GPU access. Pin-count overflow, stale closed-list entries, and async bind/unbind races are guarded mostly by assertions and fence ordering.

Test signals: `CONFIG_DRM_I915_SELFTEST` includes `selftests/i915_vma.c`; runtime signals include GEM debug assertions, tracepoints `trace_i915_vma_bind/unbind`, error logging of allocator stacks, eviction/execbuf tests, display scanout paths, and suspend/resume or VM teardown exercising async unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.h

Purpose: declares the public/internal VMA API used by GEM, execbuf, GGTT display paths, eviction, and VM teardown code.

Important APIs/functions: exposes VMA lookup/creation, pin/unpin, bind/unbind, async unbind, active tracking, mmap revoke, TLB invalidation, GGTT iomap, fence pinning, scanout markers, shrinkability helpers, current-resource access, module init/exit, and selftest-only page helpers. Inline helpers provide flag tests (`i915_vma_is_ggtt`, `i915_vma_is_bound`, `i915_vma_is_pinned`), effective offset/size with guard subtraction, object-backed refcount wrappers, view comparison, pin count updates, GGTT offset narrowing, and iteration over object GGTT VMAs.

Control flow: callers include this header to move from high-level object operations into VMA lifecycle operations. The inline pin/unpin and flag helpers are intentionally tiny and assume callers satisfy locking documented by exported functions and `assert_vma_held`.

State and persistence: no storage beyond inline access to `struct i915_vma`; it defines flag interpretation and lock expectations. Effective state remains in the VMA object and object reservation lock.

Dependencies and integration: includes GEM object, GTT, active, request, GGTT fencing, and resource headers. It links VMA code to display through `intel_display_vma_interface`, to execbuf through `_i915_vma_move_to_active`, and to eviction through unbind APIs.

Risks: many helpers assume allocated `drm_mm_node`, GGTT-only state, or nonzero pin counts and use `GEM_BUG_ON` rather than recoverable errors. Misusing raw `__i915_vma_pin/unpin` or `i915_vma_get_current_resource()` without a bound VMA can break lifetime rules.

Test signals: compile-time coverage comes from many i915 translation units, selftest declarations, lockdep through `assert_vma_held`, and runtime GEM assertions when helpers are called in invalid states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.c

Purpose: implements refcounted snapshots of VMA binding data so unbind operations can be fenced, deferred, and ordered independently from the live `struct i915_vma`.

Important APIs/functions: exports `i915_vma_resource_alloc/free`, `i915_vma_resource_hold/unhold`, `i915_vma_resource_unbind`, `__i915_vma_resource_init`, `i915_vma_resource_bind_dep_sync`, `i915_vma_resource_bind_dep_await`, `i915_vma_resource_bind_dep_sync_all`, and module init/exit. Internal pieces include `unbind_fence_ops`, `i915_vma_resource_unbind_work`, the software-fence notifier, and an interval tree keyed by unbind range including guard pages.

Control flow: binding initializes a resource snapshot. Unbind publishes `unbind_fence`, optionally takes a wakeref, inserts delayed work into the VM pending-unbind interval tree when dependencies remain, and commits the software fence. When dependencies complete, work rewrites PTEs unless skipped, signals the unbind fence after hold count reaches zero, removes the interval-tree node under `vm->mutex`, releases wakeref and refcounted SG tables, and frees via RCU.

State and persistence: state is volatile kernel memory in a slab cache. The important persistent-in-flight state is `hold_count`, `chain`, `unbind_fence`, `rb`, `vm`, `wakeref`, `bi.pages_rsgt`, range fields, `skip_pte_rewrite`, `immediate_unbind`, and optional TLB pointer.

Dependencies and integration: depends on `i915_sw_fence`, dma fences, interval trees, runtime PM, `i915_vma_ops`, VM `pending_unbind`, and memory-region SG table references. VMA bind paths call the dependency helpers to avoid rebinding over ranges whose PTE teardown is still pending.

Risks: waiting on pending unbinds while holding `vm->mutex` can deadlock worker removal paths, hence `sync_all` deliberately releases the mutex. Interval bounds include cache-color guard expansion; errors there can allow overlapping bind/unbind. Signaling occurs in dma-fence critical paths, so allocations and wakeref acquisition are constrained.

Test signals: exercised by VMA async unbind tests, VM destruction, bind-after-evict workloads, lockdep/prove-locking checks in hold/unhold, and slab module init/exit failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.h

Purpose: defines the VMA resource snapshot ABI shared by VMA bind/unbind code and GTT backend operations.

Important APIs/types: defines `struct i915_page_sizes`, `struct i915_vma_bindinfo`, and `struct i915_vma_resource`; declares allocation, refcount, hold/unhold, unbind, dependency sync/await, and module lifecycle functions. Inline helpers wrap dma-fence references and initialize/finalize resource snapshots.

Control flow: callers allocate first, initialize under the VM lock with immutable bind data, pass to backend `bind_vma`, and later publish unbind. `i915_vma_resource_init()` copies pages, page-size metadata, readonly/lmem bits, region, ops, private data, address range, and guard size; it also optionally takes a reference on `pages_rsgt` for async-capable backing storage.

State and persistence: all fields represent in-flight kernel state, not disk state. `bi` can be discarded after bind, while range, ops, fence, and TLB fields persist until unbind completion. Under error-capture builds it also records the memory region.

Dependencies and integration: integrates with dma-fence, `i915_sw_fence`, runtime PM, i915 scatterlist reference counting, VM address spaces, and backend `i915_vma_ops`. The header is included by both VMA implementation and page-table backends.

Risks: `vm` is explicitly non-refcounted and cleared after unbind, so users must respect fence/resource lifetime. `i915_vma_resource_fini()` assumes a single hold remains. Missing `pages_rsgt` disables safe async object-destruction support.

Test signals: compile-time users validate structure layout. Runtime coverage comes from async unbind, capture-error, and selftest paths that initialize resources from live VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_types.h

Purpose: defines `struct i915_vma` and documents GGTT view semantics for normal, partial, rotated, and remapped object mappings.

Important APIs/types: `assert_i915_gem_gtt_types()` enforces view union layout assumptions. `struct i915_vma` contains address-space node state, object/VM pointers, backend ops, SG pages, iomap, fencing, page sizes, guard and display alignment, open/pin/bind flags, active tracking, page binding counts, view metadata, object/VM/eviction/closed list links, and current async resource. It also defines VMA flag bits and `I915_VMA_PAGES_ACTIVE`.

Control flow: this header is consumed by the implementation and callers that need direct state. The documentation describes adding new GGTT views: extend view type/metadata and implement SG-table construction in VMA page acquisition.

State and persistence: the VMA is an in-memory object whose lifetime is bounded by its GEM object. It persists while present in object rb-tree/list or VM lists, then is destroyed after unbind/close. It is not serialized across driver reloads.

Dependencies and integration: depends on GEM object types, GTT view types, rb-trees, `drm_mm`, and active/resource subsystems. Display, execbuf, eviction, and mmap code all interpret the flag bits defined here.

Risks: flags multiplex pin counts and state bits into one atomic, so masks must remain non-overlapping. Page-count high bits encode active binds; incorrect arithmetic can leak or prematurely release pages. View layout assertions are essential because `i915_vma_compare()` uses compact `memcmp` over union branches.

Test signals: build-time `BUILD_BUG_ON` assertions, i915 VMA selftests, and broad compile coverage through most GEM and GTT paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_wait_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_wait_util.h

Purpose: provides i915-specific polling macros for sleepable and atomic wait loops with timeout handling.

Important APIs/macros: `__wait_for`, `_wait_for`, `wait_for`, `_wait_for_atomic`, `wait_for_us`, `wait_for_atomic_us`, and `wait_for_atomic`. Debug builds define `_WAIT_FOR_ATOMIC_CHECK` to catch atomic-context misuse when preempt count is meaningful.

Control flow: sleepable waits calculate a raw-ktime deadline, repeatedly execute optional operation code, evaluate the condition before declaring timeout, sleep with bounded exponential backoff, and return `0` or `-ETIMEDOUT`. Atomic waits use `local_clock()`, optional preempt disable/enable to keep CPU-local time coherent, `cpu_relax()`, and timeout accounting across CPU migration.

State and persistence: stateless macros; all variables are block-local temporaries. The only side effects come from the caller-supplied condition and optional operation.

Dependencies and integration: used by pcode and register-poll paths. Depends on kernel delay, ktime, scheduler clock, SMP, preemption, and compiler barrier APIs.

Risks: conditions may be evaluated many times and must be side-effect safe. `wait_for_us` and atomic waits require compile-time constant timeouts, and `wait_for_atomic_us` rejects waits above 50 ms. Atomic mode can burn CPU and should be reserved for contexts that cannot sleep.

Test signals: compile-time `BUILD_BUG_ON` checks, debug atomic-context warnings, and runtime users such as `skl_pcode_request()` timeout/retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_wait_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.c

Purpose: selects and applies platform-specific clock-gating and display/GT workaround register programming during i915 initialization.

Important APIs/functions: exports `intel_clock_gating_hooks_init()` and `intel_clock_gating_init()`. Internal init functions cover DG2, CFL/CML, SKL, KBL, BXT, GLK, BDW, CHV, HSW, IVB, VLV, gen6, ILK, G4X, i965, gen3, i85x, i830, and a no-op fallback. Helpers include `gen9_init_clock_gating`, `g4x_disable_trickle_feed`, `gen6_check_mch_setup`, and `gen8_set_l3sqc_credits`.

Control flow: hook initialization picks a static function table based on platform/version macros. Later `intel_clock_gating_init()` calls the selected function, which writes or read-modify-writes uncore/display/GT registers for known workarounds, often calling PCH clock-gating setup or shared gen helpers.

State and persistence: persistent driver state is the `i915->clock_gating_funcs` pointer. Hardware-visible state is MMIO register programming that lasts until reset/suspend or reinitialization.

Dependencies and integration: depends on uncore MMIO helpers, display register headers, PCH setup, GT MCR access, platform stepping macros, and MCHBAR definitions. It is part of hardware init rather than runtime policy.

Risks: workarounds are platform and stepping sensitive; writing the wrong register or missing a posting read can cause hangs, underruns, flicker, or power issues. Some comments identify historical hardware errata whose requirements are not obvious from code.

Test signals: platform boot on affected hardware, display underrun/flicker checks, runtime PM and suspend/resume, debug messages from no-op or MCH setup validation, and regression coverage for hardware workaround tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.h

Purpose: declares the clock-gating setup entry points used by i915 device initialization.

Important APIs/functions: `intel_clock_gating_hooks_init(struct drm_device *drm)` selects the platform hook table; `intel_clock_gating_init(struct drm_device *drm)` applies the selected clock-gating/workaround programming.

Control flow: this header is included by initialization code and by the implementation. It keeps the concrete platform dispatch private to `intel_clock_gating.c`.

State and persistence: no state in the header; state lives in `drm_i915_private->clock_gating_funcs` and hardware registers.

Dependencies and integration: only forward-declares `struct drm_device`, minimizing include coupling.

Risks: callers must run hook selection before applying clock gating. Missing this ordering would dereference an uninitialized function table.

Test signals: compile/link coverage from driver init, plus boot-time hardware init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.c

Purpose: isolates CPU-family matching used by i915 workarounds so x86 family names do not collide with i915 platform names.

Important APIs/functions: `intel_match_g8_cpu()` checks the running CPU against `g8_cpu_ids`, covering Alder Lake, Comet Lake, Kaby Lake, Raptor Lake, and Rocket Lake families when `CONFIG_X86` is enabled. Non-x86 builds return false.

Control flow: on x86, the function delegates to `x86_match_cpu()` with a sentinel-terminated static match table. On other architectures, the stub avoids pulling in x86 headers.

State and persistence: stateless; it reads current CPU identity through kernel CPU matching infrastructure and stores no driver state.

Dependencies and integration: depends on `asm/cpu_device_id.h` and `asm/intel-family.h` under x86, and is consumed by workaround logic needing host CPU generation information.

Risks: incomplete CPU tables can disable a workaround on a matching system. Overmatching can enable a workaround unnecessarily. Architecture guards must remain correct for allmodconfig builds.

Test signals: x86 and non-x86 compile coverage, plus targeted workaround tests or boot logs on listed CPU families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.h

Purpose: declares the CPU matching helper used by i915 workaround code.

Important APIs/functions: exposes `bool intel_match_g8_cpu(void)`.

Control flow: callers treat the helper as a simple predicate and remain independent from x86 CPU header naming.

State and persistence: none.

Dependencies and integration: includes only `linux/types.h`, making it safe for broad driver inclusion. The implementation handles architecture-specific details.

Risks: the minimal API is easy to use, but its meaning is tied to the implementation's CPU table; callers should document the specific workaround context.

Test signals: compile coverage and whichever platform workaround path consumes the predicate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.c

Purpose: initializes, refines, and prints static and runtime Intel GPU device information.

Important APIs/functions: exports `intel_platform_name`, `intel_device_info_print`, `intel_device_info_runtime_init_early`, `intel_device_info_runtime_init`, `intel_device_info_driver_create`, and `intel_driver_caps_print`. Internal helpers map PCI IDs to subplatform bits, read GMD IP version registers before normal MMIO setup, and validate reported IP versions.

Control flow: driver creation stores matched static info and copies initial runtime info. Early runtime init reads GMD graphics/media IP versions through PCI BAR mapping when available and marks platform/subplatform masks from PCI IDs. Later runtime init adjusts fields requiring MMIO/PCH state, currently disabling ppGTT on gen6 with VT-d.

State and persistence: updates `i915->__info` and `RUNTIME_INFO(i915)` in memory, including device ID, platform mask, IP versions, ppgtt type/size, page sizes, and stepping. The data persists for the driver lifetime.

Dependencies and integration: depends on PCI IDs, GMD registers, i915 platform macros, VT-d detection, DRM printers, and runtime info consumed throughout the driver.

Risks: incorrect subplatform classification changes feature/workaround selection globally. GMD direct BAR reads happen before regular MMIO and must use always-on registers. Static platform name array size is enforced but missing names return `<unknown>`.

Test signals: boot logs, debugfs/info dumps, force-probe/device matching tests, GMD platforms, VT-d gen6 systems, and compile-time `BUILD_BUG_ON` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.h

Purpose: defines the core static and runtime hardware capability model for i915.

Important APIs/types: declares `enum intel_platform`, subplatform bit assignments, `enum intel_ppgtt_type`, `DEV_INFO_FOR_EACH_FLAG`, `struct intel_ip_version`, `struct intel_runtime_info`, `struct intel_device_info`, and `struct intel_driver_caps`, plus initialization and print functions.

Control flow: static PCI match tables populate `struct intel_device_info`; driver creation copies `__runtime`; early and normal runtime init mutate fields that require PCI ID or MMIO knowledge. Other i915 code reads the resulting flags and version fields through macros.

State and persistence: structures persist inside `drm_i915_private` for the driver lifetime. They model platform, engines, memory regions, PAT mapping, feature flags, page sizes, ppgtt capability, IP versions, and scheduler caps.

Dependencies and integration: includes i915 UAPI memory classes, stepping, engine/context/SSEU types, and GEM object cache constants. It is foundational for feature gates across display, GT, memory, and virtualization paths.

Risks: flag additions must update the print macro list and initialization data. Subplatform bits share namespaces per parent platform, so callers must combine them with platform checks. Wrong capabilities can misprogram hardware or expose unsupported UAPI behavior.

Test signals: compile-time coverage across the driver, device-info debug output, PCI ID table tests, platform-specific CI, and feature/workaround branch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.c

Purpose: provides i915 host-side integration with Intel GVT-g graphics virtualization when `CONFIG_DRM_I915_GVT` is enabled.

Important APIs/functions: exports `intel_gvt_init`, `intel_gvt_driver_remove`, `intel_gvt_resume`, `intel_gvt_set_ops`, and `intel_gvt_clear_ops`, plus many i915 symbols under namespace `I915_GVT` for the external GVT module. Internal helpers test supported platforms, snapshot initial PCI/MMIO state, and initialize/clean devices.

Control flow: i915 devices register on a global list. When GVT ops are registered, existing devices are initialized if module parameters, guest status, platform support, and GuC submission restrictions allow it. Initial state capture saves PCI config space and MMIO ranges from `intel_gvt_iterate_mmio_table()`. Clear/remove paths call backend cleanup and free snapshots under a global mutex.

State and persistence: global state includes `intel_gvt_devices`, `intel_gvt_ops`, and `intel_gvt_mutex`. Per-device state lives in `dev_priv->vgpu.initial_cfg_space`, `initial_mmio`, list entry, and `dev_priv->gvt`. State is volatile and rebuilt on driver/module load.

Dependencies and integration: depends on GEM, context, ring, runtime PM, uncore forcewake, GVT MMIO table iteration, vGPU detection, kernel module symbol namespaces, and hypervisor-facing GVT backend ops.

Risks: GVT must not initialize on guests, unsupported devices, or GuC submission. Snapshot allocation failures disable GVT without failing i915. Exported symbols expand coupling to GEM internals, so API changes can break the GVT module.

Test signals: GVT module load/unload, device probe/remove, suspend/resume with `pm_resume`, supported BDW/SKL/KBL/BXT/CFL/CML hosts, and failure logs for unsupported or GuC-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.h

Purpose: declares the GVT integration interface and provides no-op stubs when GVT is disabled.

Important APIs/types: under `CONFIG_DRM_I915_GVT`, defines `struct intel_gvt_mmio_table_iter`, `struct intel_vgpu_ops`, and declarations for init/remove/resume, host init, MMIO table iteration, and ops registration. Without GVT, inline stubs make init/remove/resume harmless and MMIO iteration return success.

Control flow: i915 core code can call GVT hooks unconditionally; compile-time configuration decides whether real backend integration or stubs are used.

State and persistence: no state in the header. Real state is in `intel_gvt.c` globals and `drm_i915_private` vGPU fields.

Dependencies and integration: includes only `linux/types.h` and forward-declares `drm_i915_private`, keeping the boundary narrow between i915 core and optional virtualization.

Risks: stubbed `intel_gvt_iterate_mmio_table()` returns success despite doing nothing, which is correct only when callers are also conditional on GVT context. Interface changes must keep disabled builds compiling.

Test signals: build coverage with GVT enabled and disabled, module namespace export tests, and virtualization init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt_mmio_table.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt_mmio_table.c

Purpose: defines the MMIO register ranges that GVT must snapshot or track for virtual GPU emulation.

Important APIs/functions: exports `intel_gvt_iterate_mmio_table()`. Internal iterator functions cover generic registers, BDW-only registers, BDW-plus gen8 registers, pre-SKL PCH/AUX ranges, SKL-plus display/GT/power registers, and BXT-specific DPIO/PHY/PLL/ring ranges. Macros `MMIO_F`, `MMIO_D`, and `MMIO_RING_*` centralize callback invocation by register offset and size.

Control flow: the exported function always iterates the generic table, then dispatches by platform: Broadwell gets BDW-only, BDW-plus, and pre-SKL ranges; Skylake/Kaby/Coffee/Comet get BDW-plus and SKL-plus; Broxton gets BDW-plus, SKL-plus, and BXT ranges. Any callback error aborts iteration and propagates.

State and persistence: this file stores no runtime state. It drives caller-owned state through `iter->handle_mmio_cb`, commonly a snapshot buffer or GVT tracking table.

Dependencies and integration: includes many display, GT, pcode, MCHBAR, PV info, and GVT register headers. `intel_gvt.c` uses it to capture initial hardware state; the GVT module can use the same iterator for MMIO emulation metadata.

Risks: this is a large hand-maintained register inventory; omissions or wrong sizes can produce incomplete virtual device state. Platform guards must match GVT-supported hardware. Callback alignment assumptions are enforced only through the callback used by snapshot code.

Test signals: GVT host initialization, vGPU boot/display workloads, suspend/resume state restoration, and platform-specific register access fault testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt_mmio_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_mchbar_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_mchbar_regs.h

Purpose: centralizes MCHBAR mirror register offsets and bit fields used by i915 for memory controller, power, frequency, DRAM, and legacy chipset information.

Important APIs/macros: defines mirror bases `MCHBAR_MIRROR_BASE` and `_SNB`, stolen memory and DRAM configuration registers, clock/thermal/frequency registers, package power SKU fields, memory self-refresh watermark masks, reset-domain fields, Broxton/DG1/SKL/ICL DIMM layout masks, and display compensation register bits.

Control flow: no executable control flow; consumers use `_MMIO(...)` definitions with uncore read/write helpers. Comments note that Haswell and later mirror access has write restrictions for some registers.

State and persistence: no software state. The macros describe hardware state stored in chipset/MCHBAR registers.

Dependencies and integration: includes `i915_reg_defs.h`. Used by clock gating, GVT MMIO table, memory bandwidth/watermark, RPS/power, and chipset detection code.

Risks: bitfield definitions vary by generation; reusing a mask on the wrong platform can misinterpret DRAM layout or power data. The mirror is not accessible from command parser register reads, and Haswell write behavior is special.

Test signals: build coverage from users, platform boot on affected generations, memory bandwidth/watermark correctness, GVT snapshot coverage, and debug logs that read MCH_SSKPD or package power registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_mchbar_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.c

Purpose: creates, probes, validates, looks up, reports, and destroys i915 memory regions such as system, local, and stolen memory.

Important APIs/functions: exports `intel_memory_region_lookup`, `intel_memory_region_by_type`, `intel_memory_type_is_local`, `intel_memory_region_reserve`, `intel_memory_region_debug`, `intel_memory_type_str`, `intel_memory_region_create`, `intel_memory_region_set_name`, `intel_memory_region_avail`, `intel_memory_region_destroy`, `intel_memory_regions_hw_probe`, and `intel_memory_regions_driver_release`. Internal helpers perform optional IO memory tests.

Control flow: hardware probe walks `i915->mm.regions` capability bits, maps region IDs to UAPI classes/instances, creates the correct backend (`ttm_system`, shmem, stolen local/system), stores successful regions, and logs sizes. Creation initializes resources, object lists, backend ops, optional backend init, and memtest. Release fetches and destroys all registered regions.

State and persistence: each `struct intel_memory_region` stores resource ranges, IO aperture, min page size, total size, type/instance/id, names, object list lock, range-manager flag, and backend-private pointer. It is runtime-only and tied to driver lifetime.

Dependencies and integration: depends on GEM backends, stolen memory setup, TTM buddy manager, DRM printers, i915 parameters, IO mapping, and UAPI memory classes. Object allocation and migration code query these regions.

Risks: memtest writes to IO memory and is gated by debug or module params; failures abort region creation. Destroy refuses to free leaked regions if backend release reports busy, preventing use-after-free but leaking intentionally. Wrong capability maps can expose missing or invalid memory regions.

Test signals: `CONFIG_DRM_I915_SELFTEST` includes memory-region and mock-region tests; runtime debug output, memtest failures, local-memory availability queries, and probe/remove paths provide additional signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.h

Purpose: declares the memory-region abstraction used by i915 GEM allocation, local memory, stolen memory, and TTM-backed managers.

Important APIs/types: defines `enum intel_memory_type`, `enum intel_region_id`, `I915_ALLOC_CONTIGUOUS`, `for_each_memory_region`, `struct intel_memory_region_ops`, and `struct intel_memory_region`. Declares lookup, create/destroy, hardware probe/release, type string, reserve, debug, availability, and system/shmem setup functions.

Control flow: backend implementations provide ops for init/release/object initialization. Probe code creates regions and stores them in `i915->mm.regions`; users iterate with `for_each_memory_region` or look up by class/instance/type.

State and persistence: `struct intel_memory_region` holds the authoritative in-driver state for a region: resources, iomap, type, instance, UAPI name, object list, range-manager flag, and backend-private pointer.

Dependencies and integration: includes IO resources, mutex, IO mapping, `drm_mm`, and i915 UAPI memory classes. It bridges user-visible memory classes with internal GEM/TTM allocation backends.

Risks: object list locking is local to each region and must be honored by alloc/free paths. `private` hides regions from userspace but does not prevent internal misuse. Region IDs must stay aligned with capability bits and `intel_region_map`.

Test signals: compile coverage, memory-region selftests, object allocation tests by memory class, and debug/availability output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pci_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pci_config.h

Purpose: defines legacy Intel graphics PCI configuration offsets, BAR indices, and bit fields used by i915 setup and chipset control paths.

Important APIs/macros: provides BAR constants for gen2/gen3/gen4+ and gen12 LMEM, `intel_mmio_bar(graphics_ver)`, MCHBAR offsets and enable bits, reset-domain fields, legacy clock-control fields, display/render clock masks, OpRegion ASLE/ASLS, SWSCI bits, and backlight mode register `LBPC`.

Control flow: the only executable helper maps graphics version to the MMIO BAR: gen2 uses `GEN2_MMADR_BAR`, gen3 uses `GEN3_MMADR_BAR`, and later versions use `GEN4_GTTMMADR_BAR`.

State and persistence: no software state; macros describe PCI config space fields that persist in hardware/firmware configuration until changed by driver/platform.

Dependencies and integration: consumed by PCI probe, MMIO mapping, reset, clock, OpRegion, and legacy platform setup code.

Risks: generation-specific BAR indices are critical; using the wrong BAR maps the wrong resource. Several fields are legacy or empirically documented, so platform guards matter.

Test signals: device probe on gen2/3/4+ platforms, PCI resource mapping logs, reset-domain tests, and legacy display/backlight behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pci_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.c

Purpose: implements i915 PCODE mailbox access for power/firmware commands and exposes a display-facing pcode interface.

Important APIs/functions: exports `snb_pcode_read`, `snb_pcode_write_timeout`, `skl_pcode_request`, `intel_pcode_init`, `snb_pcode_read_p`, `snb_pcode_write_p`, and `i915_display_pcode_interface`. Internal helpers decode gen6/gen7 mailbox status, perform locked mailbox read/write, retry SKL-style requests, and wait for dGPU pcode initialization.

Control flow: mailbox operations serialize on `i915->sb_lock`, check readiness, write data/data1 and mailbox command, wait for ready to clear, optionally read results, and translate status bits. `skl_pcode_request()` sends a request until the reply matches or timeout occurs, first sleep-polling then retrying with preemption disabled. dGPU init waits up to 10 seconds, then extends to 180 seconds with a notice.

State and persistence: no long-lived software state besides lock serialization. Hardware state is in PCODE mailbox/data registers and firmware initialization status.

Dependencies and integration: depends on uncore forcewake-aware register helpers, pcode register definitions, wait macros, runtime PM wrappers for parameterized commands, and display parent interface callbacks.

Risks: mailbox access is timeout-sensitive and firmware-dependent. Busy/locked/rejected statuses must be interpreted correctly. Atomic retry can stall CPUs briefly, so timeout limits are guarded. Missing runtime PM around parameterized commands can access powered-down hardware.

Test signals: pcode read/write users, display pcode interface consumers, dGPU initialization logs, timeout/retry debug messages, and error-code propagation in power/frequency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.h

Purpose: declares PCODE mailbox helpers and the display pcode callback interface exported by i915.

Important APIs/functions: exposes `snb_pcode_read`, `snb_pcode_write_timeout`, convenience macro `snb_pcode_write`, `skl_pcode_request`, `intel_pcode_init`, parameterized dGPU helpers `snb_pcode_read_p/write_p`, and `i915_display_pcode_interface`.

Control flow: callers choose direct mailbox read/write, request-with-ack polling, or command/parameter helpers. The implementation handles locking, wait policy, and runtime PM where needed.

State and persistence: no header state; all state is hardware mailbox registers and implementation-local locks.

Dependencies and integration: includes `linux/types.h`, forward-declares `drm_device` and `intel_uncore`, and bridges display code to i915 pcode operations.

Risks: the one-millisecond `snb_pcode_write` default may be too short for long-running commands; callers needing longer waits must use `snb_pcode_write_timeout`.

Test signals: compile/link coverage from pcode clients, display pcode callbacks, and platform power-management tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.c

Purpose: connects i915 memory regions to DRM TTM device/resource-manager infrastructure and converts TTM allocations to i915 scatter-gather tables.

Important APIs/functions: exports `intel_region_ttm_device_init/fini`, `intel_region_to_ttm_type`, `intel_region_ttm_init/fini`, `intel_region_ttm_resource_to_rsgt`, and `intel_region_ttm_resource_free`; selftest builds also expose `intel_region_ttm_resource_alloc`.

Control flow: device init creates `dev_priv->bdev` with i915 TTM funcs. Region init maps i915 memory type/instance to TTM placement type and initializes a buddy manager sized by region and IO aperture. Fini cleans manager move fences, repeatedly flushes free objects and drains workqueues until the region object list empties, then tears down the buddy manager. Resource conversion chooses range-manager or buddy-resource SG table construction.

State and persistence: TTM state lives in `dev_priv->bdev` and `mem->region_private` as a `ttm_resource_manager`. Allocated resources remain until explicitly freed or manager teardown.

Dependencies and integration: depends on TTM device/range manager, i915 TTM buddy manager, GEM TTM driver funcs, memory-region abstraction, and i915 refcounted SG table helpers.

Risks: teardown can return `-EBUSY` and intentionally leave region memory allocated if objects leaked. Mapping instance to `TTM_PL_PRIV + instance` must stay below `TTM_NUM_MEM_TYPES`. Selftest allocation deliberately detaches `res->bo` to expose misuse.

Test signals: TTM-backed local memory tests, mock-region selftests, object leak detection during region fini, SG-table conversion validation, and eviction/migration workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.h

Purpose: declares the TTM integration surface for i915 memory regions.

Important APIs/functions: exposes TTM device init/fini, region init/fini, TTM type mapping, resource-to-refcounted-SG conversion, resource free, `i915_ttm_driver()`, and selftest-only resource allocation.

Control flow: memory-region setup calls `intel_region_ttm_init()` for suitable regions after the global TTM device exists; teardown calls fini/free functions in reverse. GEM backends call conversion helpers after TTM allocation.

State and persistence: no state in the header; state resides in the TTM device and each region's `region_private`.

Dependencies and integration: includes i915 selftest declarations, forward-declares TTM and i915 types, and provides the boundary between memory-region code and TTM allocation internals.

Risks: selftest-only declarations are hidden behind `CONFIG_DRM_I915_SELFTEST`; production code must not depend on them. Callers must pass resources from the matching region manager to avoid freeing through the wrong manager.

Test signals: build coverage with and without selftests, local-memory allocation tests, and TTM teardown checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.h -->
