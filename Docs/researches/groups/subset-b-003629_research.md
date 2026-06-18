# subset-b-003629 research

This grouped report covers the assigned i915 selftest/VLV support files and the Imagination PowerVR DRM driver files. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.h

Purpose: declares scheduler selftest helper APIs for temporarily changing `intel_engine_cs` scheduling policy and waiting for test requests. It is a small contract header shared by i915 scheduler selftests, with no implementation or persistent state.

Important APIs/types: `struct intel_selftest_saved_policy` captures `flags`, `reset`, `timeslice`, and `preempt_timeout` so a test can restore engine policy after mutation. `enum selftest_scheduler_modify` names supported mutations: disabling hangcheck and enabling a fast reset path. Exported prototypes are `intel_selftest_find_any_engine()`, `intel_selftest_modify_policy()`, `intel_selftest_restore_policy()`, and `intel_selftest_wait_for_rq()`.

Control flow and state: callers find a usable GT engine, save/modify policy through the modify API, run a scheduler scenario, then restore from the saved-policy snapshot. The header does not own memory; its state is caller-owned stack or local test data.

Dependencies and integration: depends only on `linux/types.h` plus forward declarations for i915 request, engine, and GT types. It integrates with scheduler selftests that need to alter engine policy without duplicating save/restore logic.

Risks: tests using this API must restore policy on all error paths or they can poison subsequent selftests. The enum is intentionally narrow; adding new policy modes requires matching implementation changes.

Test signals: success is indirect through scheduler selftests that compile against this header and verify request completion and policy restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_scheduler_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_uncore.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_uncore.c

Purpose: provides i915 uncore selftests for forcewake range tables, shadow-register ranges, and selected live forcewake behavior. It validates that static MMIO/forcewake metadata is ordered, valid, and watertight where newer platforms require contiguous coverage.

Important APIs/functions: `intel_fw_table_check()` checks `intel_forcewake_range` arrays for ascending order, positive length, and optional watertightness. `intel_shadow_table_check()` validates `i915_mmio_range` lists for Gen8, Gen11, Gen12, DG2, MTL, and XeLPM+ shadowed registers. `intel_uncore_mock_selftests()` runs pure table validation. `live_fw_table()` validates the runtime GT forcewake table. `live_forcewake_ops()` is a disabled-by-default broken selftest that probes forcewaked engine registers. `intel_uncore_live_selftests()` registers the live subtests.

Control flow and state: mock tests iterate over compile-time arrays and return immediately on the first malformed range. Live tests run through `intel_gt_live_subtests()`, take a runtime-PM wakeref, manually flush forcewake release timers, read a chosen engine register while forcewake is held, then expect the raw MMIO value to drop to zero once forcewake is released. The live forcewake test skips Valleyview/Cherryview and is gated behind `CONFIG_DRM_I915_SELFTEST_BROKEN`.

Dependencies and integration: depends on i915 selftest harness, `intel_gt`, uncore forcewake internals, runtime PM, engine iteration, hrtimer release, and MMIO helpers. It protects core uncore tables used by normal register access paths.

Risks: forcewake behavior is hardware- and platform-sensitive; the live test documents unreliability and external powerwell interference. Table validation can catch regressions early, but a false watertight flag or missing platform table will fail broad test runs.

Test signals: `intel_uncore_mock_selftests()` should pass without hardware. Live signals include nonzero register reads under forcewake, zero after forcewake release, and valid runtime forcewake table ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_uncore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.c

Purpose: implements small software-fence helpers used by i915 selftests to create on-stack, timer-backed, and heap-backed `i915_sw_fence` objects.

Important APIs/functions: `__onstack_fence_init()` initializes a stack fence waitqueue, pending count, error field, and no-op notify callback. `onstack_fence_fini()` commits and finalizes an initialized on-stack fence. `timed_fence_init()` creates an on-stack timer and either schedules a wake at `expires` or commits immediately. `timed_fence_fini()` cancels/destroys the timer and finalizes the fence. `heap_fence_create()` allocates a heap fence with a kref-backed lifetime and `heap_fence_put()` releases references through `heap_fence_release()`.

Control flow and state: on-stack fences are explicitly initialized and finalized by the caller. Timed fences transition to committed state from the timer callback `timed_fence_wake()` or synchronously if the expiration is in the past. Heap fences hold two references: one for the creator and one released when the fence free notification arrives. Final memory release uses `kfree_rcu()`.

Dependencies and integration: integrates with `../i915_sw_fence.h`, Linux timers, krefs, RCU freeing, and lockdep waitqueue classes through the header macro.

Risks: timer-backed fences require `timed_fence_fini()` to avoid on-stack timer lifetime bugs. Heap fences rely on the notify callback receiving `FENCE_FREE`; mismatched ref ownership can leak or prematurely free test fences.

Test signals: expected behavior is that selftests can create delayed dependencies, wait on them, and finalize without lockdep, timer, or refcount warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.h

Purpose: declares the selftest fence helper interface and lockdep-aware stack initialization macro.

Important APIs/types: `onstack_fence_init()` wraps `__onstack_fence_init()` with a static `lock_class_key` under `CONFIG_LOCKDEP`. `struct timed_fence` embeds an `i915_sw_fence` and `timer_list`. Public helpers are `__onstack_fence_init()`, `onstack_fence_fini()`, `timed_fence_init()`, `timed_fence_fini()`, `heap_fence_create()`, and `heap_fence_put()`.

Control flow and state: the header defines only caller-visible contracts. Stack fences are owned by the caller; timed fences own an on-stack timer; heap fences return an `i915_sw_fence *` whose allocation lifetime is managed by `heap_fence_put()` plus fence notifications.

Dependencies and integration: includes Linux timer support and i915 software fence internals. It is intended for selftest-only synchronization scenarios, not production driver paths.

Risks: callers must pair init/fini correctly and must not use a timed fence after the stack timer is destroyed. Lockdep naming is macro-based, so unusual call patterns can produce less useful diagnostics.

Test signals: compile coverage under lockdep and non-lockdep builds, plus downstream selftests that exercise delayed and heap fence dependency paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.c

Purpose: supplies RAPL energy helpers for i915 selftests that want approximate package/graphics energy readings on integrated GPUs.

Important APIs/functions: `librapl_supported()` rejects discrete GPUs and returns true only when `librapl_energy_uJ()` can read nonzero energy. `librapl_energy_uJ()` reads `MSR_RAPL_POWER_UNIT` to get the energy unit exponent, then reads `MSR_PP1_ENERGY_STATUS` and converts the raw value to microjoules.

Control flow and state: both functions are stateless. MSR reads use `rdmsrq_safe()` and return `0` on read failure, making unsupported hardware a soft no-op rather than a crash.

Dependencies and integration: depends on x86 MSR access and i915 platform predicates. It is used by performance/energy selftests that should skip where RAPL PP1 is unavailable or where discrete GPUs require hwmon integration instead.

Risks: RAPL counters can wrap and are platform-specific. Returning zero conflates unsupported hardware, read failure, and a true zero reading, which is acceptable for skip detection but not detailed diagnostics.

Test signals: selftests can call `librapl_supported()` before measuring and should observe increasing `librapl_energy_uJ()` values during workloads on supported integrated platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.h

Purpose: declares the RAPL selftest helper API.

Important APIs/types: forward declares `struct drm_i915_private` and exposes `librapl_supported(const struct drm_i915_private *i915)` plus `librapl_energy_uJ(void)`.

Control flow and state: no state is held by the header. Callers first check support, then sample energy values around a test workload.

Dependencies and integration: depends only on `linux/types.h`. The implementation integrates with MSR access and i915 platform detection.

Risks: header users must treat a zero energy value as unsupported or unavailable rather than as a precise power result.

Test signals: compile coverage and downstream energy-aware selftests that skip cleanly on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/librapl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_drm.h

Purpose: provides tiny DRM file helpers for i915 selftests using mock DRM/GEM devices.

Important APIs/functions: `mock_file(struct drm_i915_private *i915)` obtains a `struct file *` via `mock_drm_getfile(i915->drm.primary, O_RDWR)`. `to_drm_file(struct file *f)` returns `f->private_data` as a `struct drm_file *`.

Control flow and state: no local state; the helpers bridge Linux file objects to DRM file-private data for selftests that need per-file handles.

Dependencies and integration: includes `drm_file.h` and i915 driver definitions. Integrates with DRM mock file allocation and the `drm_file` handle namespace used by GEM tests.

Risks: callers must close/drop the returned file correctly. The cast in `to_drm_file()` assumes the file came from DRM mock infrastructure.

Test signals: selftests should be able to allocate mock file contexts and use DRM handle/object APIs without a real userspace open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.c

Purpose: constructs and tears down an in-kernel mock `drm_i915_private` suitable for GEM, GT, GTT, context, memory-region, and engine selftests without real hardware.

Important APIs/functions: `mock_gem_device()` allocates a fake PCI device, DRM device, display descriptor, runtime-PM state, mock uncore, GGTT, memory regions, workqueues, contexts, and a mock RCS engine. `mock_device_flush()` repeatedly flushes all mock engines and retires GT requests. `mock_destroy_device()` removes display data and releases devres/device references. `mock_device_release()` performs release-time cleanup when the DRM device is dropped.

Control flow and state: creation is staged with explicit unwind labels. The fake device disables IOMMU via a fake `dev_iommu` when Intel IOMMU support is enabled, initializes mock platform info, disables real wakeref hardware by incrementing GT wakeref count, assigns a GGTT, creates one mock engine, clears the wedged bit, and sets `i915->do_release`. Cleanup flushes requests, removes GT driver objects, drains GEM work, finalizes GGTT, destroys workqueues, releases TTM and memory-region state, and cleans mode config.

Dependencies and integration: integrates many i915 subsystems: display device probing, runtime PM, GT driver setup, mock engine/request/context helpers, memory regions, region TTM, GGTT, GEM MM, and DRM managed allocation.

Risks: partial initialization paths must exactly mirror successful initialization or leak workqueues, memory regions, devres, or fake devices. Because it fakes power/IOMMU/uncore behavior, it is good for unit-level GEM logic but not hardware timing.

Test signals: successful selftests should create/destroy mock devices repeatedly without leaks, workqueue leftovers, active requests, or WARNs from GT/memory-region teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.h

Purpose: declares the mock GEM device lifecycle functions used by i915 selftests.

Important APIs: `mock_gem_device()` returns a fully initialized mock `drm_i915_private *` or `NULL`; `mock_device_flush()` drains mock engine work and retires requests; `mock_destroy_device()` releases the mock device.

Control flow and state: the header does not own state but defines the expected lifecycle: create, run tests, flush if needed, destroy.

Dependencies and integration: forward declares `struct drm_i915_private`; implementation ties into DRM/i915 mock infrastructure.

Risks: tests must not use the pointer after `mock_destroy_device()`. Any new mock subsystem initialized in the `.c` file should be included in release cleanup.

Test signals: compile use by GEM and GT selftests plus leak-free create/destroy loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.c

Purpose: provides mock global and per-process GTT address-space operations for i915 selftests where page-table programming should be inert.

Important APIs/functions: `mock_ppgtt()` allocates a fake `i915_ppgtt` with a near-`U64_MAX` address-space size and no-op insert/clear/cleanup operations. `mock_init_ggtt()` populates a supplied GT GGTT with fake GMADR/mappable sizes, no-op bind/insert ops, and address-space initialization. `mock_fini_ggtt()` finalizes the GGTT address space. Internal no-op bind/unbind functions either do nothing or, for PPGTT, mark `vma_res->bound_flags`.

Control flow and state: PPGTT allocation initializes VM fields, DMA device, page-table allocation callbacks, and vma ops. GGTT initialization sets `is_ggtt`, resource bounds, total size, callbacks, and then calls `i915_address_space_init()`.

Dependencies and integration: depends on i915 VM/GTT abstractions, page-table DMA allocation helpers, and GT/GGTT structures. Used by mock GEM device construction and lower-level VM tests.

Risks: the mock implementation does not validate real PTE programming, aperture constraints, cache attributes, or hardware global binding. PPGTT `mock_bind_ppgtt()` asserts that global bind flags are not used.

Test signals: VM/GEM tests should observe address-space lifecycle and bound flag changes without hardware MMIO. Failures usually appear as `GEM_BUG_ON`, refcount, or address-space cleanup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.h

Purpose: declares mock GTT helpers for i915 selftests.

Important APIs: `mock_init_ggtt(struct intel_gt *gt)`, `mock_fini_ggtt(struct i915_ggtt *ggtt)`, and `mock_ppgtt(struct drm_i915_private *i915, const char *name)`.

Control flow and state: no state in the header. Callers initialize the GT GGTT during mock device setup, optionally create PPGTTs for tests, and finalize the GGTT during release.

Dependencies and integration: forward declares i915 private, GGTT, and GT structures. Implementation integrates with address-space and VM operations.

Risks: the `name` argument is currently unused by the implementation, so tests should not rely on named diagnostics from this helper.

Test signals: successful mock device creation and VM tests that can bind/unbind without touching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.c

Purpose: implements mock i915 memory regions backed by TTM resources for selftests.

Important APIs/functions: `mock_region_create()` allocates a mock memory-region instance ID and calls `intel_memory_region_create()` with `mock_region_ops`. `mock_object_init()` initializes GEM objects in the mock region, validates size, records `bo_offset`, sets CPU/GTT read domains, disables cache coherency, and attaches the memory region. `mock_region_get_pages()` allocates a TTM resource and converts it to an `i915_refct_sgt`; `mock_region_put_pages()` releases the refcounted sg table and TTM resource. `mock_region_fini()` finalizes TTM and frees the IDA instance.

Control flow and state: region instances are assigned from `i915->selftest.mock_region_instances`, limited by available TTM private memory types. GEM object page state flows through `obj->mm.res`, `obj->mm.rsgt`, and `__i915_gem_object_set_pages()`.

Dependencies and integration: depends on GEM memory-region object APIs, TTM placement/resource helpers, scatterlists, and the i915 memory-region core. It is used by selftests that need memory-region behavior without physical local memory.

Risks: object size is checked only against total region size; offset/size overlap policy depends on lower TTM allocation. Failure paths must free `obj->mm.res` if sg conversion fails.

Test signals: expected tests allocate mock regions, create GEM objects, get/put pages, and see resources released with no IDA leaks or stale `rsgt` pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.h

Purpose: declares mock memory-region creation for i915 selftests.

Important API: `mock_region_create(struct drm_i915_private *i915, resource_size_t start, resource_size_t size, resource_size_t min_page_size, resource_size_t io_start, resource_size_t io_size)` returns an `intel_memory_region *` or error pointer.

Control flow and state: the caller owns the returned memory region and must release it through the standard memory-region lifecycle.

Dependencies and integration: forward declares i915 private and memory-region structures and uses `linux/types.h` for `resource_size_t`.

Risks: callers need an initialized mock-region IDA in `i915->selftest.mock_region_instances`; mock GEM device setup performs this initialization.

Test signals: region tests should create mock regions of different sizes/page sizes and exercise GEM object allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.c

Purpose: creates and cancels mock i915 requests for GT scheduler/engine selftests.

Important APIs/functions: `mock_request(struct intel_context *ce, unsigned long delay)` creates a request through `intel_context_create_request()` and stores a mock delay. `mock_cancel_request(struct i915_request *request)` removes a queued request from the mock engine link list under `engine->hw_lock` and calls `i915_request_unsubmit()` when it had been queued.

Control flow and state: request creation relies on the enlarged i915 request slab to include mock request fields. Cancellation derives `struct mock_engine` from `request->engine`, removes `request->mock.link`, and returns whether the request was actually queued.

Dependencies and integration: depends on GT mock engine internals, GEM test utilities, and i915 request/context APIs. Used by selftests that model delayed execution or cancellation without real hardware.

Risks: cancellation assumes the request belongs to a mock engine. Using it on a real engine would make the `container_of()` invalid. Locking must match mock engine queue manipulation.

Test signals: scheduler tests can enqueue mock requests, cancel them, and observe unsubmit behavior and queue removal under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.h

Purpose: declares mock request creation and cancellation helpers.

Important APIs: `mock_request(struct intel_context *ce, unsigned long delay)` and `mock_cancel_request(struct i915_request *request)`.

Control flow and state: callers create a mock request tied to an Intel context and optional delay, then may cancel it if it remains queued.

Dependencies and integration: includes i915 request definitions and Linux list support. Implementation integrates with mock engine structures.

Risks: helpers are mock-only; tests must not pass requests from real engines to `mock_cancel_request()`.

Test signals: compile use by scheduler and mock engine tests, plus expected boolean return from cancellation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.c

Purpose: initializes an i915 uncore instance for mock devices with no-op MMIO read/write functions.

Important APIs/functions: macro-generated `nop_write8/16/32()` and `nop_read8/16/32/64()` implement raw MMIO accessors that ignore writes and return zero for reads. `mock_uncore_init()` calls `intel_uncore_init_early()` and assigns all raw read/write MMIO vfuncs to the no-op family.

Control flow and state: the uncore is initialized against `to_gt(i915)`, then its function pointers are replaced. No MMIO backing store is maintained, so register writes are not persistent.

Dependencies and integration: depends on `mock_uncore.h`, i915 uncore initialization, and `ASSIGN_RAW_*_MMIO_VFUNCS` macros. Used during mock GEM device creation before GT tests run.

Risks: tests that require register value persistence cannot use this uncore directly. Returning zero can hide missing setup unless tests explicitly assert behavior.

Test signals: mock-device tests should avoid real MMIO faults and should see deterministic zero reads from raw uncore access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.h

Purpose: declares mock uncore initialization.

Important API: `mock_uncore_init(struct intel_uncore *uncore, struct drm_i915_private *i915)`.

Control flow and state: no header state; caller supplies the uncore storage and owning i915 device.

Dependencies and integration: forward declares i915 private and uncore structures. Implementation integrates with early uncore setup and raw MMIO vfunc assignment.

Risks: the initialized uncore is intentionally non-persistent for MMIO values, so consumers must be mock-aware.

Test signals: mock GEM device creation can initialize uncore without hardware register mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/scatterlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/scatterlist.c

Purpose: selftests Linux/i915 scatter-gather table allocation, iteration, and trimming behavior over varied segment layouts.

Important APIs/functions: `alloc_table()` constructs an `sg_table` with synthetic contiguous PFNs and variable segment lengths. `expect_pfn_sg()`, `expect_pfn_sg_page_iter()`, and `expect_pfn_sgtiter()` verify order and lengths through `for_each_sg`, `for_each_sg_page`, and `for_each_sgt_page`. Segment generators include `one`, `grow`, `shrink`, `random`, and `random_page_size_pages`. `igt_sg_alloc()` validates `sg_alloc_table()`. `igt_sg_trim()` validates `i915_sg_trim()`. `scatterlist_mock_selftests()` registers both subtests.

Control flow and state: tests iterate over prime sizes and offsets to stress boundary behavior around continuation allocations. The PRNG is reseeded with `i915_selftest.random_seed` before allocation and verification so expected lengths match. Timeouts use `IGT_TIMEOUT` and `igt_timeout()` to avoid unbounded loops.

Dependencies and integration: depends on Linux scatterlist/page iteration APIs, prime-number iteration, pseudo-random state, and i915 selftest utilities. It specifically exercises `i915_sg_trim()` and generic scatterlist allocation limits.

Risks: relies on `pfn_to_page()` contiguity in sparse memory; if the synthetic PFN range is not contiguous, tests return `-ENOSPC` and stop that variant. Very large segment lengths are constrained to avoid overflowing `sg->length`.

Test signals: pass means all three iteration APIs traverse the expected PFN span and trimmed tables retain expected `nents/orig_nents` and page ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/scatterlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.c

Purpose: implements Valleyview/Cherryview IOSF sideband register access for BUNIT, CCK, CCU, DPIO, FLISDSI, NC, and PUNIT units.

Important APIs/functions: `vlv_iosf_sb_get()`/`vlv_iosf_sb_put()` acquire/release unit access and maintain `locked_unit_mask`. `vlv_iosf_sb_read()` and `vlv_iosf_sb_write()` translate unit to devfn/port/opcode and call `vlv_sideband_rw()`. `vlv_iosf_sb_init()` initializes the mutex and Valleyview CPU latency QoS request; `vlv_iosf_sb_fini()` removes them. Internal `__vlv_punit_get()` acquires the global IOSF MBI PUNIT lock and applies a CPU latency workaround for Valleyview.

Control flow and state: all sideband reads/writes require the caller to hold the appropriate unit via `get()`. `vlv_sideband_rw()` waits for the doorbell to become idle, disables preemption, writes address/data/doorbell fields, waits for completion, then reads data for reads. PUNIT access has extra locking and QoS state.

Dependencies and integration: depends on i915 uncore register access, `i915_iosf_mbi`, CPU latency QoS, DRM warnings, and platform predicates. Used by VLV/CHV display, power, and clock code that must access sideband registers.

Risks: invalid unit mapping returns zero or `-EINVAL`; callers that ignore `write()` return values can miss sideband timeouts. The lock mask warning in `put()` expects balanced unit masks. PUNIT access can hang hardware without the CPU latency workaround.

Test signals: platform tests should show no doorbell timeouts, no unbalanced lock-mask warnings, and correct sideband register effects on VLV/CHV hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.h

Purpose: declares the VLV/CHV IOSF sideband unit enumeration and access API.

Important APIs/types: `enum vlv_iosf_sb_unit` names BUNIT, CCK, CCU, DPIO, DPIO_2, FLISDSI, GPIO, NC, and PUNIT. Public functions are init/fini, get/put, and read/write.

Control flow and state: callers initialize per-device sideband state, acquire a unit mask, perform read/write operations, then release the same unit mask.

Dependencies and integration: includes `vlv_iosf_sb_reg.h` so consumers can use sideband register constants. Implementation relies on `drm_i915_private` sideband lock/QoS fields.

Risks: enum values are used as bit indices in `unit_mask`; reordering or inserting values affects mask users.

Test signals: compile coverage from platform-specific VLV/CHV code and runtime warnings for invalid or unbalanced unit access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb_reg.h

Purpose: defines IOSF sideband register addresses and bit fields used by Valleyview/Cherryview display, power, PLL, frequency, and power-gate control code.

Important definitions: BUNIT register `BUNIT_REG_BISOC`; PUNIT media/display/ISP power state registers and `_SSPM*` masks; power gate control/status macros and indices; GPU frequency/fuse/duty-cycle registers; DDR frequency force bits; NC fuse fields; turbo SoC override bits; CCK HPLL/DSI PLL/control divider/clock fields.

Control flow and state: the header is pure constants and macros. State is hardware-resident in sideband registers accessed via `vlv_iosf_sb_read()`/`write()`.

Dependencies and integration: included by `vlv_iosf_sb.h` and platform code that needs symbolic register fields for PUNIT, CCK, BUNIT, or NC sideband accesses.

Risks: bit encodings are hardware contracts. Incorrect shifts/masks can break power-gating, PLL programming, display clocks, or GPU frequency detection. Several comments mark Cherryview-specific fields, so cross-platform users must choose fields carefully.

Test signals: validated indirectly by VLV/CHV display bring-up, power management, frequency initialization, suspend/resume, and sideband access smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_iosf_sb_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.c

Purpose: preserves and restores Valleyview Gunit state across runtime/system suspend paths involving D3 and S0ix transitions.

Important APIs/functions: `vlv_suspend_init()` allocates `i915->vlv_s0ix_state` for Valleyview; `vlv_suspend_cleanup()` frees it. `vlv_suspend_complete()` waits for GT wells off, verifies context bits, disables GT wake, saves Gunit state, and releases forced clock. `vlv_resume_prepare()` forces the GFX clock, restores state, re-enables GT wake, clears force clock, checks access errors, and optionally reinitializes clock gating. Internal helpers save/restore many GAM, MBC, GCP, GPM, display CZ, GT SA, and Gunit-display registers.

Control flow and state: `struct vlv_s0ix_state` is the persistent suspend snapshot. Save reads a curated list of registers before the device enters deeper low-power states. Restore writes them back, preserving wake/force-clock bits controlled by the caller via masked RMW. Wake/clock helpers poll hardware status with short timeouts.

Dependencies and integration: depends on i915 uncore register access, GT register definitions, wait utilities, trace hooks, clock-gating init, and VLV/CHV platform checks. It integrates with suspend/resume and runtime-PM sequences.

Risks: register lists are hardware-specific and intentionally broad; missing a required register can cause resume failures, while restoring caller-controlled bits can disrupt the suspend sequence. Timeout handling tries to continue on resume but can leave runtime PM disabled by returning the first error.

Test signals: suspend/resume on VLV/CHV should complete without GT access errors, force-clock timeouts, wake-ack timeouts, or post-resume display/GT instability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.h

Purpose: declares VLV suspend/resume lifecycle hooks.

Important APIs: `vlv_suspend_init()`, `vlv_suspend_cleanup()`, `vlv_suspend_complete()`, and `vlv_resume_prepare(struct drm_i915_private *i915, bool rpm_resume)`.

Control flow and state: driver setup allocates suspend snapshot state, suspend calls complete after other GT quiesce work, resume calls prepare before normal operation, and cleanup frees state.

Dependencies and integration: forward declares `drm_i915_private` and uses `linux/types.h`. Implementation integrates with VLV/CHV power management and clock gating.

Risks: hooks are no-ops on non-VLV/CHV platforms in implementation, but callers should still preserve correct ordering around GT access disable/enable.

Test signals: VLV/CHV runtime/system suspend testing and compile coverage for platform PM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Kconfig

Purpose: defines Kconfig entries for the Imagination PowerVR DRM driver and its KUnit tests.

Important symbols: `DRM_POWERVR` is a tristate driver for PowerVR Series 6 and later / IMG Graphics. It depends on 64-bit ARM64 or 64-bit RISC-V, DRM, MMU, PM, and a tautological POWER_SEQUENCING expression allowing either configuration. It selects DRM execution, GEM shmem, DRM scheduler, GPUVM, and firmware loader support. `DRM_POWERVR_KUNIT_TEST` enables driver KUnit tests when `DRM_POWERVR && KUNIT`, defaulting under `KUNIT_ALL_TESTS`.

Control flow and state: no runtime logic; configuration controls whether `powervr` and `pvr_test` objects are built.

Dependencies and integration: integrates with the DRM subsystem, firmware loading, scheduler, GPUVM, and KUnit. Module name is documented as `powervr`.

Risks: architecture gating excludes 32-bit and non-ARM64/RISC-V builds. Adding source features may require additional selected dependencies here.

Test signals: `allyesconfig`/module builds with `DRM_POWERVR`, and KUnit builds when `DRM_POWERVR_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Makefile

Purpose: lists object composition for the PowerVR DRM module and its KUnit test object.

Important build rules: `powervr-y` includes CCB/CCCB, context, device, device info, driver, dump, free-list, firmware, firmware-processor, firmware trace/util, GEM, HWRT, job, MMU, power, queue, stream, sync, and VM objects. `powervr-$(CONFIG_DEBUG_FS)` adds `pvr_debugfs.o`. `obj-$(CONFIG_DRM_POWERVR)` builds `powervr.o`; `obj-$(CONFIG_DRM_POWERVR_KUNIT_TEST)` builds `pvr_test.o`.

Control flow and state: no runtime state; object order defines link membership for the kernel module.

Dependencies and integration: aligns with Kconfig symbols and the driver’s internal module layout. The files researched here are a subset of this larger module.

Risks: missing object entries cause unresolved symbols or dead features; adding debugfs-only code must remain conditional on `CONFIG_DEBUG_FS`.

Test signals: kernel build/link success for built-in and module configurations, plus debugfs and KUnit variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.c

Purpose: implements PowerVR firmware command-control buffers: KCCB for kernel-to-firmware commands and FWCCB for firmware-to-host events, including slot reservation, completion waiting, fences, and wakeup handling.

Important APIs/functions: `pvr_kccb_init()`/`pvr_kccb_fini()` initialize/cleanup the KCCB. `pvr_fwccb_init()` initializes the FWCCB. `pvr_fwccb_process()` consumes firmware commands and dispatches restart, free-list reconstruction/grow, stats, and context-reset notifications. `pvr_kccb_send_cmd()`, `_powered()`, and `_reserved_powered()` submit commands with appropriate PM/slot assumptions. `pvr_kccb_reserve_slot()`, `pvr_kccb_release_slot()`, and `pvr_kccb_wake_up_waiters()` manage async reservation fences. `pvr_kccb_wait_for_completion()` waits for return-slot execution.

Control flow and state: `pvr_ccb_init()` allocates uncached firmware objects for control and command rings, sets wrap masks and command sizes, and records firmware addresses. KCCB capacity is one less than slot count to distinguish full from empty. Reservation state combines firmware read/write offsets with `reserved_count`. Command send copies into the ring, clears return status if a slot is tracked, issues a memory barrier, updates write offset, decrements reservation count, and kicks MTS. FWCCB processing drops the FWCCB lock while handling each command.

Dependencies and integration: depends on firmware object mapping, PowerVR firmware ABI structs, runtime PM, free-list management, reset/power code, dump logging, dma_fence, waitqueues, and workqueue/IRQ paths.

Risks: ring offsets and `reserved_count` must remain consistent or KCCB can deadlock. Missing barriers could let firmware see incomplete commands. Waiter fences must be put exactly once. Unknown FWCCB commands are logged but ignored.

Test signals: interrupt processing should wake KCCB waiters, command return slots should transition from `NO_RESPONSE` to executed, and KCCB idle/reservation accounting should not warn under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.h

Purpose: declares the core PowerVR CCB data structure and KCCB/FWCCB public API.

Important APIs/types: `struct pvr_ccb` stores firmware objects, firmware addresses, ring sizing, a mutex, and CPU mappings for control and CCB memory. Public functions cover KCCB/FWCCB init/fini, FWCCB processing, KCCB fence allocation/freeing, slot reservation/release, command send variants, completion wait, idle check, and waiter wakeup.

Control flow and state: callers initialize device-level rings, reserve KCCB slots before queueing from scheduler paths, send commands with PM/reset assumptions satisfied, and wait for completion where required. Locking is centered on `pvr_ccb.lock`.

Dependencies and integration: includes PowerVR firmware interface definitions and Linux mutex/types. It forward declares `pvr_device` and firmware object types to avoid broader include coupling.

Risks: API naming separates powered/reserved variants; using the wrong variant can miss PM refs or corrupt reservation accounting.

Test signals: compile coverage from firmware, queue, job, and device code; runtime tests around command submission and interrupt completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.c

Purpose: implements PowerVR client CCBs used by per-context queues to write job commands for firmware consumption and kick firmware through KCCB.

Important APIs/functions: `pvr_cccb_init()`/`pvr_cccb_fini()` allocate/free uncached firmware objects for client CCB control and data. `pvr_cccb_cmdseq_fits()` checks available ring space while reserving end padding if wrapping is needed. `pvr_cccb_write_command_with_header()` writes command headers, optional padding, and payload bytes. `pvr_cccb_send_kccb_kick()` and `pvr_cccb_send_kccb_combined_kick()` send firmware kicks for single or combined geometry/fragment queues.

Control flow and state: the CCCB owns CPU-visible `write_offset`, firmware-visible read/dependency offsets in control memory, and a power-of-two `wrap_mask`. Command writes ensure a padding command fits at ring end, wrap to zero when needed, and use `wmb()` before KCCB kicks so firmware sees client commands before the kick. Combined kicks optionally omit fragment cleanup resources for partial-render jobs.

Dependencies and integration: depends on firmware object mapping, KCCB command APIs, HWRT cleanup state addresses, firmware ABI command headers, and queue/job scheduler serialization. The code relies on drm_sched serializing command writes rather than an internal mutex.

Risks: command sequences larger than the supported half-ring capacity complicate wrapping and should be rejected by callers using `pvr_cccb_cmdseq_can_fit()`. Incorrect write offsets or missing padding can make firmware parse garbage.

Test signals: job submission tests should see CCCB write offsets advance, KCCB kicks issued after writes, and no WARN from insufficient CCB space checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.h

Purpose: declares the client CCB structure and helper API for queue command submission.

Important APIs/types: `struct pvr_cccb` stores firmware objects, control/data CPU mappings, firmware addresses, ring size, local write offset, and wrap mask. `PADDING_COMMAND_SIZE` names the firmware padding header size. Helpers include init/fini, command write, single/combined KCCB kicks, `pvr_cccb_cmdseq_fits()`, `pvr_cccb_get_size_of_cmd_with_hdr()`, and `pvr_cccb_cmdseq_can_fit()`.

Control flow and state: queue code computes command sequence size, checks whether it can ever fit and currently fits, writes commands, then kicks firmware using reserved KCCB capacity.

Dependencies and integration: includes Rogue firmware ABI headers and forward declares PowerVR device, firmware object, and HWRT data structures.

Risks: `pvr_cccb_get_size_of_cmd_with_hdr()` warns on unaligned command sizes, so callers must pre-align firmware payload contracts. The half-capacity policy in `cmdseq_can_fit()` is a simplifying invariant used by fencing logic.

Test signals: compile/runtime coverage from job queue submission, especially ring wrap and combined geometry/fragment jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.c

Purpose: implements userspace-visible PowerVR context creation, destruction, queue setup, firmware-context allocation, and context lifetime management.

Important APIs/functions: `pvr_context_create()` validates UAPI args, maps priority, looks up VM context, creates job queues, initializes firmware data, creates a firmware object, allocates firmware/global and per-file IDs, and returns a handle. `pvr_context_destroy()` removes a file handle, kills queues, and drops the handle reference. `pvr_destroy_contexts_for_file()` cleans all contexts on file close and unmaps VM state for still-referenced contexts. `pvr_context_device_init()`/`fini()` manage device context xarray and lock. Internal helpers initialize render/compute/transfer firmware data from static context streams and create/destroy/kill queues by context type.

Control flow and state: `struct pvr_context` is kref-managed. Device-wide `ctx_ids` provides firmware IDs; file `ctx_handles` provides user handles; `file_link` is protected by `ctx_list_lock`. Render contexts own geometry and fragment queues, compute contexts own one compute queue, transfer-frag contexts own one transfer queue.

Dependencies and integration: depends on DRM auth for high priority, stream parsing, firmware objects, queue creation, VM contexts, xarrays, krefs, and UAPI context/job types.

Risks: `pvr_context_lookup_id()` assumes `xa_load()` returns non-NULL before `kref_get_unless_zero()`, so callers must pass valid IDs or this path is fragile. The error path after firmware object creation goes to `err_free_ctx_data` rather than `err_destroy_queues`, which is worth reviewing for queue leakage. Priority elevation is gated by `CAP_SYS_NICE` or DRM master.

Test signals: create/destroy ioctls for all context types, invalid static-state lengths, close-time cleanup, high-priority permission tests, and queue teardown under outstanding references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.h

Purpose: defines PowerVR context data structures, queue lookup helpers, reference helpers, and public context lifecycle APIs.

Important APIs/types: `enum pvr_context_priority` maps low/medium/high internal priorities. `struct pvr_context` includes kref, device, VM context, type/flags/priority, firmware object/data, firmware context ID, faulty flag, type-specific queues, and file-list linkage. Inline helpers map job type to queue, take/drop references, look up contexts by file handle or firmware ID, and fetch firmware address.

Control flow and state: contexts are reference-counted and registered in both per-file and per-device xarrays. Queue lookup is constrained by context type. `atomic_t faulty` marks contexts made unusable after reset with unfinished jobs.

Dependencies and integration: includes DRM scheduler, dma-fence, kref, xarray, UAPI types, CCCB, device, and queue headers.

Risks: inline lookup by firmware ID must handle concurrent destruction; the code attempts this with xarray locking and `kref_get_unless_zero()`. Queue union fields must be used consistently with `ctx->type`.

Test signals: compile coverage from job submission, context reset, close cleanup, and ioctl handling; runtime tests for invalid handles and stale references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.c

Purpose: creates PowerVR debugfs entries under the DRM minor debugfs root.

Important APIs/functions: static `pvr_debugfs_entries[]` currently contains one entry, `"pvr_fw"`, initialized by `pvr_fw_trace_debugfs_init`. `pvr_debugfs_init(struct drm_minor *minor)` creates a directory for each entry and calls its init callback with `pvr_dev` and the directory.

Control flow and state: called through the DRM driver debugfs callback. It relies on DRM to clean up all children under `minor->debugfs_root`, so no explicit fini exists.

Dependencies and integration: depends on DRM minor/device, debugfs, dentry, PowerVR device conversion, and firmware trace debugfs support.

Risks: debugfs directory creation failures are warnings only; the driver continues without that diagnostic tree. Additional entries should avoid requiring explicit teardown.

Test signals: with `CONFIG_DEBUG_FS`, `/sys/kernel/debug/dri/*/pvr_fw` should appear for registered devices and firmware trace files should initialize below it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.h

Purpose: declares debugfs entry plumbing for the PowerVR driver with a no-op fallback when debugfs is disabled.

Important APIs/types: under `CONFIG_DEBUG_FS`, `struct pvr_debugfs_entry` contains a directory name and init callback, and `pvr_debugfs_init()` is declared. Otherwise an inline no-op `pvr_debugfs_init()` is provided.

Control flow and state: debugfs initialization is optional and controlled entirely by configuration.

Dependencies and integration: forward declares DRM minor, PowerVR device, and dentry to keep includes light.

Risks: callers can invoke `pvr_debugfs_init()` unconditionally from driver setup because the no-op fallback exists.

Test signals: build coverage with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.c

Purpose: handles PowerVR device-level hardware initialization, register/clock setup, firmware loading, GPU ID validation, IRQ processing, feature exposure, and teardown.

Important APIs/functions: `pvr_device_init()` gets platform data, clocks, power ops, runtime PM, MMIO registers, GPU/firmware initialization, and IRQs. `pvr_device_fini()` tears down IRQ and GPU firmware state. `pvr_gpuid_decode_string()` parses a `B.V.N.C` override and is exported for KUnit. `pvr_device_has_uapi_quirk()`, `_enhancement()`, and `_feature()` expose filtered feature state. Internal helpers map registers, get clocks, process queue events, manage safety IRQs, request firmware, decode GPU ID registers, check supported BVNCs, set DMA mask, and initialize firmware/VM state.

Control flow and state: initialization powers the GPU before register access, loads firmware based on BVNC and major version, validates firmware-provided device info, chooses META/MIPS/RISC-V firmware processor, creates must-have stream masks, sets DMA info, creates kernel VM for non-MIPS firmware, initializes firmware, then requests threaded IRQ. IRQ handling clears firmware events, processes FWCCB, wakes KCCB waiters, processes active queues, marks runtime-PM activity, and handles RogueXE safety events.

Dependencies and integration: integrates platform devices, OF match data, clk, runtime PM, reset/power sequencing, firmware loader, pvr_fw, pvr_vm, pvr_queue, pvr_stream, DMA API, IRQs, and feature/quirk tables.

Risks: GPU support gating blocks unknown/experimental BVNCs unless `exp_hw_support` is set. Firmware filenames must match decoded BVNC. IRQ processing assumes firmware defs are initialized. Safety events are optional and feature-derived. Runtime PM ordering is critical around register access and firmware boot.

Test signals: probe/remove on supported DT compatibles, KUnit for GPU ID parsing, firmware load messages, IRQ-driven job completion, safety-event logs, and clean teardown without xarray/workqueue leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.h

Purpose: defines core PowerVR device/file structures, feature/quirk access macros, register accessors, UAPI padding validation, and device lifecycle declarations.

Important APIs/types: `struct pvr_gpu_id`, `struct pvr_fw_version`, `struct pvr_device_data`, and large `struct pvr_device` wrap DRM device state, hardware identity, firmware state, clocks, power domains, reset/pwrseq, IRQ, FWCCB/KCCB, kernel VM, queues, watchdog, context/free-list/job xarrays, reset semaphore, scheduler workqueue, and safety-event flag. `struct pvr_file` stores per-open xarrays and context list. Macros expose features/quirks/enhancements, convert between DRM/PVR types, pack BVNC, read/write/poll control registers, and validate union padding.

Control flow and state: this header defines the persistent state shared across the driver. `reset_sem` protects firmware command paths from reset/lost-device races. KCCB state includes return slots, reserved slots, waiters, and fence context. Per-file state owns user handles for contexts, free lists, HWRT datasets, and VM contexts.

Dependencies and integration: includes DRM device/file/mm headers, Linux IO/polling/locks/workqueue/xarray, CCB, firmware, stream, and device-info headers.

Risks: structure fields are cross-module contracts. Register accessors assume `pvr_dev->regs` is mapped and powered. `PVR_FEATURE_VALUE()` silently leaves output untouched when absent and returns `-EINVAL`; callers must initialize defaults.

Test signals: full-driver builds, probe/runtime paths using register access, UAPI validation tests for union padding, and reset/job tests exercising `reset_sem` semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.c

Purpose: maps firmware-provided feature, quirk, and enhancement bitmasks into fields inside `struct pvr_device`.

Important APIs/functions: `pvr_device_info_set_quirks()` maps `PVR_FW_HAS_BRN_*` bits to `pvr_dev->quirks.has_brn*`. `pvr_device_info_set_enhancements()` maps `PVR_FW_HAS_ERN_*` bits. `pvr_device_info_set_features()` maps `PVR_FW_HAS_FEATURE_*` bits to feature presence booleans and, where applicable, feature value fields. `pvr_device_info_set_common()` handles shared quirk/enhancement bitmask parsing and unsupported-bit warnings.

Control flow and state: mapping arrays store `offsetof()` values into `struct pvr_device`, allowing generic bit iteration to set booleans or values. Feature values are read sequentially from the parameter area after the feature bitmask; if a present valued feature lacks a parameter, `-EINVAL` is returned.

Dependencies and integration: depends on firmware device-info ABI constants, DRM warnings, `pvr_device` layout, and feature/quirk/enhancement structs.

Risks: offset mappings must stay synchronized with firmware enum maxima; `BUILD_BUG_ON` catches array-size drift. Unsupported bits warn but do not fail except malformed feature parameter streams. Reordering valued features changes parameter consumption semantics.

Test signals: firmware validation should populate expected feature fields; KUnit or firmware fixture tests should exercise unsupported bits and truncated feature-parameter streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.h

Purpose: defines PowerVR hardware feature, quirk, and enhancement state structures plus mapping APIs.

Important APIs/types: `struct pvr_device_features` contains `has_*` booleans and value fields for firmware-advertised capabilities. `struct pvr_device_quirks` and `struct pvr_device_enhancements` contain supported BRN/ERN booleans. Setters are `pvr_device_info_set_quirks()`, `pvr_device_info_set_enhancements()`, and `pvr_device_info_set_features()`. The header also defines META core constants and public `PVR_FEATURE_*` identifiers for UAPI/derived feature lookup.

Control flow and state: instances live inside `struct pvr_device` and are populated during firmware validation/device init.

Dependencies and integration: forward declares `pvr_device`; implementation depends on firmware ABI bit indices. Device, stream, query, and job code use the feature/quirk values.

Risks: adding a firmware feature requires updating the struct, mapping table, and any public derived feature IDs. Boolean presence and value fields must be interpreted together.

Test signals: firmware load on known GPUs should set expected fields; device-query ioctls should report filtered public features consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_device_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.c

Purpose: provides the main PowerVR DRM platform driver, file lifecycle, ioctl dispatch, device query helpers, user-object copy helpers, probe/remove paths, and module metadata.

Important APIs/functions: ioctl handlers cover BO creation/mmap-offset, device queries, VM context create/destroy, VM map/unmap, context create/destroy, free-list/HWRT dataset create/destroy, and job submission. `pvr_get_uobj()`, `pvr_set_uobj()`, `pvr_get_uobj_array()`, and `pvr_set_uobj_array()` implement size/stride-compatible UAPI copying. `pvr_drm_driver_open()` allocates `pvr_file` and xarrays; `pvr_drm_driver_postclose()` destroys contexts, free lists, HWRT datasets, and VM contexts. `pvr_probe()` allocates the DRM device, initializes power domains, reset semaphore, context/queue/runtime-PM/watchdog/device state, registers DRM, and initializes ID xarrays. `pvr_remove()` reverses that.

Control flow and state: most ioctls enter `drm_dev_enter()` and validate padding/flags before touching device state. Device queries support size-probe calls with null pointers and copy filtered GPU/runtime/quirk/enhancement/heap/static-area data. File state owns per-open handles. Probe sets autosuspend, watchdog, and runtime PM before `pvr_device_init()`.

Dependencies and integration: ties together DRM core, GEM shmem, PowerVR GEM/VM/context/free-list/HWRT/job/queue/power/device modules, OF platform matching, runtime PM, debugfs, and firmware declarations.

Risks: UAPI copy helpers must preserve forward/backward compatibility and zero extended output. `pvr_set_uobj_array()` appears to advance user/source pointers inconsistently in the strided branch, so array-output compatibility paths deserve focused testing. Probe initializes `free_list_ids`/`job_ids` after DRM registration, so early users must not access them before that point.

Test signals: ioctl validation tests for padding, flags, short structs, strided arrays, invalid handles, VM bounds, and job submission; probe/remove and file open/close leak tests; module firmware availability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.h

Purpose: declares driver identity/version constants and generic UAPI object copy helpers/macros for PowerVR ioctl compatibility.

Important APIs/types: constants define name `powervr`, description, and interface version `1.0.0`. Functions copy single user objects and arrays with stride/min-size handling. `PVR_UOBJ_MIN_SIZE()` uses `_Generic` mappings to derive minimum supported sizes for specific UAPI structs. Macros `PVR_UOBJ_GET`, `PVR_UOBJ_SET`, `PVR_UOBJ_GET_ARRAY`, and `PVR_UOBJ_SET_ARRAY` wrap helper calls with type-derived sizes.

Control flow and state: no persistent state. Ioctl handlers use these macros to accept older/larger user structs while enforcing required mandatory fields.

Dependencies and integration: includes UAPI `pvr_drm.h` and compiler attributes. The `_Generic` list is a central compatibility registry for query/job/sync/heap/static-data structures.

Risks: any UAPI struct used with the macros must be listed or compilation fails. Choosing the wrong last mandatory field changes ABI acceptance. Array copy helpers depend on correct stride semantics.

Test signals: compile coverage for every macro use and UAPI compatibility tests with minimum-size, exact-size, and extended-size structs/arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.c

Purpose: decodes firmware context reset notifications into readable DRM log messages.

Important APIs/functions: `pvr_dump_context_reset_notification()` prints whether all contexts or a specific context reset, reset reason, data master, job reference, and page-fault address when present. Internal `get_reset_reason_desc()` maps Rogue reset reason enums to strings; `get_dm_name()` maps firmware data-master IDs to names.

Control flow and state: stateless. It receives FWCCB context-reset data and logs through `drm_info()` using the owning `pvr_device`.

Dependencies and integration: called from `pvr_ccb.c` when processing `ROGUE_FWIF_FWCCB_CMD_CONTEXT_RESET_NOTIFICATION`. Depends on firmware ABI enums and PowerVR device conversion.

Risks: unknown reset reasons/data masters are logged as `Unknown`; future firmware enum additions should update the mapping tables. This file logs diagnostics only and does not modify context state.

Test signals: firmware reset notification injection or hardware reset events should produce clear reset reason/data-master/job/page-fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.h

Purpose: declares the firmware context-reset dump helper.

Important API: `pvr_dump_context_reset_notification(struct pvr_device *pvr_dev, struct rogue_fwif_fwccb_cmd_context_reset_data *data)`.

Control flow and state: no state in the header; FWCCB processing passes reset data to the implementation for diagnostic logging.

Dependencies and integration: forward declares `pvr_device` and the firmware context reset data struct, keeping callers decoupled from full dump implementation details.

Risks: purely diagnostic API; callers must not expect it to reset or mark contexts faulty.

Test signals: compile coverage from CCB processing and runtime reset-notification logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_dump.h -->
