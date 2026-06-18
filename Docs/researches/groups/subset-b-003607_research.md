# subset-b-003607 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_pages.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_pages.c

### Purpose
`huge_pages.c` is the i915 GEM huge-page selftest suite. It validates page-size selection, scatterlist construction, PPGTT mappings, 64K scratch behavior, compact/mixed page-table layouts, transparent huge-page fallback, shrink behavior, and GPU/CPU visibility for objects backed by 4K, 64K, and 2M pages.

### Important APIs, Types, And Functions
Core helpers include `hugepage_ctx()`, `get_largest_page_size()`, `get_huge_pages()`, `huge_pages_object()`, fake huge-page object constructors, `igt_check_page_sizes()`, `gpu_write()`, `cpu_check()`, and the `igt_create_*` allocation wrappers. Mock tests are registered through `i915_gem_huge_page_mock_selftests()`, and live tests through `i915_gem_huge_page_live_selftests()`.

### Control Flow
Mock tests create synthetic PPGTT/device-region objects and verify advertised page-size masks, misaligned DMA handling, and 64K scratch support. Live tests allocate large or awkwardly sized objects, bind them into full PPGTTs, force writes through GPU batches, read back through CPU mappings, exercise compact/mixed page-table paths, and run smoke/randomized allocation loops until the selftest timeout.

### State, Persistence, And Dependencies
State is transient in GEM objects, scatter-gather tables, VM page tables, scratch pages, request fences, and object shrinker state. The file depends on GEM region/internal/lmem APIs, PPGTT VM helpers, mock DRM/device/region helpers, random test utilities, and `igt_gem_utils` GPU store helpers.

### Integration Points
The suite plugs into i915 selftest registration and covers the huge-page behavior consumed by GEM object creation, VM binding, GPU execution, memory-region placement, and shrink/fallback logic.

### Risks
Large allocations can be skipped or fail under memory pressure, so tests must distinguish real correctness failures from resource exhaustion. Page-size mask accounting, 64K scratch scrubbing, mixed compact mappings, and CPU cache flushing are easy to regress because the same object can be visible through several page-table granularities.

### Test Signals
Signals are subtest failures, page-size mismatch logs, GPU write/readback mismatches, missing 64K scratch pages, THP fallback/shrink failures, and skipped live tests when PPGTT is unavailable or the GT is wedged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_client_blt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_client_blt.c

### Purpose
`i915_gem_client_blt.c` validates client-visible BLT copies between linear, X-tiled, and Y-major/Tile4 surfaces. It checks that the copy engine preserves software-visible tiling layouts across object placement changes and GGTT eviction-like rebinding.

### Important APIs, Types, And Functions
Important types are `enum client_tiling`, `struct blit_buffer`, and `struct tiled_blits`. Key helpers include `linear_x_y_to_ftiled_pos()`, `fastblit_supports_x_tiling()`, `prepare_blit()`, `tiled_blits_create_buffers()`, `fill_scratch()`, `tiled_offset()`, `verify_buffer()`, `tiled_blit()`, and `igt_client_tiled_blits()`.

### Control Flow
The test allocates source, destination, scratch, and batch VMAs for each copy engine. It fills scratch data in CPU-visible order, emits either `XY_FAST_COPY_BLT` on capable platforms or legacy XY source-copy commands with BCS tiling controls, then relocates buffers into selected holes to simulate rebinding. Final verification walks the expected tiled offsets and checks the copied values.

### State, Persistence, And Dependencies
State lives in transient GEM objects, VMAs, batch buffers, and per-run random placement state. Dependencies include copy-engine lookup, BLT command definitions, GGTT/PPGTT VMA pinning, memory-region allocation, display capability checks for modern X tiling, and i915 random utilities.

### Integration Points
The live selftest enters through `i915_gem_client_blt_live_selftests()` and runs only when the GT is not wedged. It validates the BLT command emission paths used by userspace clients that copy tiled buffers.

### Risks
Platform-specific tiling encodings are brittle, especially F-tile subtile remapping, Tile4 flags, X-tile fastblit restrictions, and bit-17 swizzle quirks. Incorrect pitch units or relocation offsets can silently copy into the wrong tile position.

### Test Signals
Failures report buffer creation, BLT submission, or verification errors. Skips are expected on pre-gen4, bad swizzle configurations, missing copy engines, and unsupported fastblit/tile combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_client_blt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_coherency.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_coherency.c

### Purpose
`i915_gem_coherency.c` stress-tests GEM cache-domain transitions by writing, overwriting, and reading the same cachelines through CPU, GGTT, write-combined CPU maps, and GPU store-dword commands.

### Important APIs, Types, And Functions
`struct context` carries the test object and selected engine. Access modes are described by `struct igt_coherency_mode`. The implementation centers on `cpu_set/get()`, `gtt_set/get()`, `wc_set/get()`, `gpu_set()`, validity filters for fences and store-dword support, `random_engine()`, and `igt_gem_coherency()`.

### Control Flow
The test chooses a random engine, iterates all valid overwrite/write/read mode triples, creates a one-page internal object, shuffles cacheline offsets, writes stale inverse values, overwrites them with new random values, then reads through each valid getter. Prime-number iteration varies the count of touched cachelines to expose partial-flush errors.

### State, Persistence, And Dependencies
State is limited to one transient GEM object per iteration, cache-domain metadata, GGTT mappings, request fences, and CPU/WC maps. Dependencies include object prepare/finish access, clflush helpers, GGTT iomap pinning, engine PM references, `MI_STORE_DWORD_IMM`, random helpers, and request submission.

### Integration Points
The live test is registered by `i915_gem_coherency_live_selftests()` and validates the cache-domain API used by GEM mmap, exec, and CPU access paths.

### Risks
The main risks are missing clflush-before/after handling, incorrect domain transitions around GGTT/WC maps, GPU writes not being waited on through active tracking, and false skips when hardware lacks fences or store-dword commands.

### Test Signals
The strongest signal is a value mismatch naming overwrite, write, and read modes plus offset. Setup failures identify invalid domain transitions, GGTT pinning, or GPU request construction problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_coherency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_context.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_context.c

### Purpose
`i915_gem_context.c` is the live context-management selftest suite. It tests request submission across many logical contexts, parallel switching, per-context VM isolation, shared-VM execution, readonly object enforcement, and context-specific SSEU reconfiguration.

### Important APIs, Types, And Functions
Major tests are `live_nop_switch()`, `live_parallel_switch()`, `igt_ctx_exec()`, `igt_shared_ctx_exec()`, `igt_ctx_readonly()`, `igt_ctx_sseu()`, and `igt_vm_isolation()`. Helpers include `gpu_fill()`, `cpu_fill/check()`, `create_test_object()`, `throttle()`, `emit_rpcs_query()`, SSEU spinner helpers, and scratch read/write batches.

### Control Flow
The suite creates mock files and live/kernel contexts, submits ordered no-op or store-dword requests across engines, throttles outstanding requests, and checks CPU-visible object contents. SSEU tests pin render contexts, reconfigure slice/subslice masks during idle, busy, reset, and idle-after-reset phases, then query RPCS registers. VM isolation writes through one context into scratch-space offsets and verifies a second VM still reads its own scratch page.

### State, Persistence, And Dependencies
All state is transient in i915 contexts, per-context VMs, huge fake GEM objects, active requests, engine power refs, spinner fences, and scratch pages. Dependencies include context creation/registration, VM binding, render register commands, reset helpers, live-test guards, and `igt_gem_utils` batch helpers.

### Integration Points
`i915_gem_context_live_selftests()` registers these tests for the live GT path and skips when the GT is wedged. Results validate the context ABI and internal scheduling behavior used by execbuffer and engine backends.

### Risks
High request counts can expose timing-dependent failures. The most fragile areas are ordered fence chaining, request throttling, context VM lifetime, readonly VMA enforcement, SSEU state restore after reset/idle, and scratch offsets accidentally overlapping real nodes.

### Test Signals
Signals include timeout while switching contexts, CPU readback mismatches in huge objects, SSEU RPCS slice-count mismatches, failed kernel-context restore, and VM-isolation reads returning another context's scratch write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_dmabuf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_dmabuf.c

### Purpose
`i915_gem_dmabuf.c` verifies i915 PRIME dma-buf export/import behavior, including self-import reuse, importing external mock buffers, same-driver import through forced different devices, LMEM limitations, ownership transfer, and exported object vmap behavior.

### Important APIs, Types, And Functions
The suite includes `igt_dmabuf_export()`, `igt_dmabuf_import_self()`, `igt_dmabuf_import_same_driver_lmem()`, `verify_access()`, `igt_dmabuf_import_same_driver()`, `igt_dmabuf_import()`, `igt_dmabuf_import_ownership()`, and `igt_dmabuf_export_vmap()`.

### Control Flow
Mock tests create shmem objects, export them, import them back, import synthetic `mock_dmabuf()` buffers, pin pages, and vmap exported memory. Live tests force same-driver imports to look like external devices, verify LMEM-only exports fail when migration to system memory is impossible, and use GPU writes through imported objects to verify visibility from the native object.

### State, Persistence, And Dependencies
State is held in transient GEM objects, dma-buf refs, reservations/fences, attachments, sg tables, and maps. The file depends on PRIME import/export hooks, memory-region placement, mock context/dmabuf helpers, `igt_gpu_fill_dw()`, dma-resv waits, and `force_different_devices`.

### Integration Points
`i915_gem_dmabuf_mock_selftests()` runs on a mock device, while `i915_gem_dmabuf_live_selftests()` exercises real memory regions. The tested paths are the same PRIME interfaces used for cross-driver buffer sharing.

### Risks
Refcounting and ownership transfer are subtle around import-after-`dma_buf_put()`. LMEM migration policy can change expected errors. External attachment waits must observe exclusive fences, or importers may see stale GPU writes.

### Test Signals
Signals include self-import creating a duplicate object, wrong LMEM import error, exported object not moving to SMEM, GPU write visibility mismatches, dma-resv wait timeouts, and nonzero data in freshly exported vmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_migrate.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_migrate.c

### Purpose
`i915_gem_migrate.c` tests GEM object migration between system memory and local memory, including content preservation, failure fallback, asynchronous unbind behavior, and reset behavior under simulated GPU/memcpy allocation failures.

### Important APIs, Types, And Functions
Important routines are `igt_fill_check_buffer()`, `igt_create_migrate()`, `lmem_pages_migrate_one()`, `__igt_lmem_pages_migrate()`, `igt_lmem_pages_failsafe_migrate()`, `igt_async_migrate()`, and `igt_lmem_async_migrate()`.

### Control Flow
Basic tests allocate objects in one region, fill predictable dword patterns, migrate to a target region, pin pages, confirm the old placement is no longer valid, wait for migration, and verify contents. Failsafe tests toggle TTM migration failure modes and memcpy bans. Async tests bind VMAs behind spinner dependencies and ensure migration schedules async unbinds without blocking on the spinner.

### State, Persistence, And Dependencies
State is transient in GEM objects, LMEM/SMEM region placement, moving fences, VMAs, dependency sets, spinners, and GT wedge/reset flags. Dependencies include `intel_migrate_clear()`, `i915_gem_object_migrate()`, TTM move failure injection, reset helpers, and spinner infrastructure.

### Integration Points
`i915_gem_migrate_live_selftests()` runs only when LMEM exists and dispatches through `intel_gt_live_subtests()`. It validates migration semantics used by TTM-backed memory management and mmap fault migration.

### Risks
Failure injection can wedge the GT by design and must reset all GTs cleanly. Async migration is vulnerable to deadlocks if unbinds become synchronous. Content validation depends on correct map type for coherent CPU access.

### Test Signals
Expected signals include region mismatch, data mismatch, unexpected migration success/failure, wrong wedge state after failure injection, spinner termination by hangcheck, and stale moving fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_mman.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_mman.c

### Purpose
`i915_gem_mman.c` validates i915 GEM mmap behavior across GGTT, WC/WB/UC, and fixed mmap offsets. It covers partial tiled GGTT views, mmap offset exhaustion, LMEM fault migration, userspace access helpers, GPU execution from mmap-written batches, and PTE revocation after unbind or page release.

### Important APIs, Types, And Functions
Important helpers include `tiled_offset()`, `check_partial_mapping(s)()`, `igt_partial_tiling()`, `igt_smoke_tiling()`, `igt_mmap_offset_exhaustion()`, `__igt_mmap()`, `igt_mmap_migrate()`, `__igt_mmap_access()`, `__igt_mmap_gpu()`, and `__igt_mmap_revoke()`.

### Control Flow
Tiling tests create huge fake objects and map partial GGTT views over prime/random page offsets, manually computing swizzled tiled locations. Generic mmap tests assign offsets, map into the current process, read poison-initialized backing store, write replacement poison, and check through WC or GGTT. Migration tests force small BAR-like visible sizes, fill mappable memory, fault non-visible LMEM through fixed mmap, and verify expected placement or SIGBUS-like failure. Revoke tests prefault PTEs, unbind or drop pages, then require absent PTEs.

### State, Persistence, And Dependencies
State lives in GEM objects, memory-region visible ranges, VMA offset manager nodes, current process VMAs/PTEs, GGTT fences, TTM buddy manager visible-size state, and active requests. Dependencies include `igt_mmap`, memory-region/TTM migration APIs, GGTT iomap, clflush/flush helpers, page-table walkers, and reset helpers.

### Integration Points
`i915_gem_mman_live_selftests()` temporarily borrows an mm for kthreads and runs the live suite. These tests cover user mmap ABI behavior and the memory-manager paths used by page faults and eviction.

### Risks
The suite manipulates global offset-manager holes and memory-region visible sizes, so cleanup must restore state. Tiling math, swizzle handling, PTE revocation, and migration failure injection are platform-sensitive. Missing `current->mm` handling would break kthread execution.

### Test Signals
Signals include partial-view misalignment logs, wrong mmap poison values, unexpected mmap allocation success, failed LMEM migration/fault behavior, absent/present PTE check failures, and GPU batch execution timeouts from mmap-written memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_mman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_object.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_object.c

### Purpose
`i915_gem_object.c` provides basic GEM object selftests: mock creation of a shmem object and live sanity checking of the selftest-only huge fake object.

### Important APIs, Types, And Functions
The file defines `igt_gem_object()`, `igt_gem_huge()`, `i915_gem_object_mock_selftests()`, and `i915_gem_object_live_selftests()`.

### Control Flow
The mock test creates a one-page shmem object and releases it. The live test creates a huge fake object whose DMA-visible size exceeds its real page count, pins pages, and verifies `i915_gem_object_get_page()` wraps each virtual page to the expected real page modulo the chosen awkward page count.

### State, Persistence, And Dependencies
State is transient in a mock device, live i915 device, and GEM object page arrays. Dependencies include `huge_gem_object`, mock GEM device setup, GT GGTT size, and flush-test infrastructure.

### Integration Points
These tests are small entry points in the broader GEM selftest suite and provide quick coverage for object allocation and huge-object page lookup helpers used by other selftests.

### Risks
The live test depends on GGTT size and fake huge-object semantics; a change in page lookup wrapping or pin-page handling can fail it even if normal shmem objects still work.

### Test Signals
Failures are object creation errors, pin-pages errors, or page lookup mismatches with the expected modulo real-page index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_phys.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_phys.c

### Purpose
`i915_gem_phys.c` tests conversion of a shmem GEM object into physically contiguous pages through the i915 physical-object path.

### Important APIs, Types, And Functions
The file defines `mock_phys_object()` and registers it through `i915_gem_phys_mock_selftests()`.

### Control Flow
The test creates a one-page shmem object, verifies it initially has struct pages, attaches physical backing with `i915_gem_object_attach_phys()`, checks that the object is no longer represented as normal struct-page backing, verifies pages are pinned, then marks the object dirty through the GTT domain so release must copy data back.

### State, Persistence, And Dependencies
State is transient in the mock GEM device and object page state. Dependencies include shmem object creation, object locking, physical attach logic, page pin-count tracking, GTT domain transition, and mock device lifecycle.

### Integration Points
This is a mock-only selftest for the physical backing path used by legacy or special GEM object handling. It validates assumptions other code makes after `attach_phys()`.

### Risks
Incorrect page-type transitions can leave the object both struct-page and physical-backed, leak pin counts, or skip dirty copyback on release.

### Test Signals
Failures report missing initial struct pages, failed physical attach, still-struct-page backing after attach, missing page pins, or failed GTT-domain dirtying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_phys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.c

### Purpose
`igt_gem_utils.c` provides reusable GEM selftest helpers for request allocation and simple GPU dword-fill batches.

### Important APIs, Types, And Functions
Exports are `igt_request_alloc()`, `igt_emit_store_dw()`, and `igt_gpu_fill_dw()`.

### Control Flow
`igt_request_alloc()` resolves and temporarily references the engine-specific `intel_context` before creating a request. `igt_emit_store_dw()` allocates an internal batch object, writes generation-specific `MI_STORE_DWORD_IMM` commands for each page-spaced target dword, pins the batch VMA, and returns it. `igt_gpu_fill_dw()` creates a request, marks batch and destination VMAs active, emits a batch-buffer start, submits the request, and releases the batch VMA.

### State, Persistence, And Dependencies
State is transient in internal batch objects, VMAs, request fences, and target object active tracking. Dependencies include GEM context lookup, request creation, generation-specific GPU command encodings, chipset flush, VMA pinning, and engine `emit_bb_start`.

### Integration Points
Many selftests call `igt_gpu_fill_dw()` to validate GPU visibility and cache/domain behavior without open-coding batch construction.

### Risks
Address encoding differs across gen2/4/8+ hardware. Missing VMA active tracking or secure dispatch on older platforms can make later CPU checks race or fail.

### Test Signals
Indirect signals appear in callers as failed request creation, batch pinning errors, GPU fill failures, or readback mismatches after store-dword batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.h

### Purpose
`igt_gem_utils.h` declares shared GEM selftest helpers for request allocation, GPU dword-store batch creation, and unlocked VMA active tracking.

### Important APIs, Types, And Functions
It forward-declares i915 request/context/VMA and intel context/engine types, declares `igt_request_alloc()`, `igt_emit_store_dw()`, `igt_gpu_fill_dw()`, and defines inline `igt_vma_move_to_active_unlocked()`.

### Control Flow
The inline helper locks a VMA, calls `i915_vma_move_to_active()`, unlocks the VMA, and returns the result, allowing selftests to use active tracking from call sites that do not already hold the VMA lock.

### State, Persistence, And Dependencies
The header stores no state. It depends on `i915_vma.h`, Linux integer types, and the request/VMA APIs provided by the i915 driver.

### Integration Points
Included by context, dma-buf, huge-page, and other GEM selftests that need a small GPU store workload or a context-bound request.

### Risks
The unlocked wrapper must only be used where taking the VMA lock locally is correct; callers that already hold conflicting locks could deadlock.

### Test Signals
Compilation catches interface drift; runtime signals occur in callers when VMA active tracking, request allocation, or GPU fill helpers fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.c

### Purpose
`mock_context.c` creates lightweight mock, live, and kernel i915 GEM contexts for selftests without requiring normal userspace ioctl setup.

### Important APIs, Types, And Functions
The file provides `mock_context()`, `mock_context_close()`, `mock_init_contexts()`, `live_context()`, `kernel_context()`, and `kernel_context_close()`.

### Control Flow
`mock_context()` allocates and initializes an `i915_gem_context`, optionally creates a mock PPGTT, sets persistence, default engines, handle/VMA lookup structures, and engine mutexes. `live_context()` creates a proto-context for a mock file, converts it to a real context, disables error capture, allocates an id in the file-private xarray, and registers it. `kernel_context()` creates a non-bannable persistent context, optionally binding a supplied VM.

### State, Persistence, And Dependencies
State persists only for the lifetime of returned contexts and their referenced VMs/engine sets. Dependencies include file private data, mock DRM/GTT helpers, proto-context creation, default engine setup, xarray registration, and common context close paths.

### Integration Points
These helpers are used by many live and mock GEM selftests to get contexts suitable for request submission, VM isolation, or fake-device tests.

### Risks
Partially initialized contexts must release VMs and engine structures correctly on failure. Live context registration must match real context lifetime rules or tests can leak file-private IDs.

### Test Signals
Signals are context creation errors, failed engine setup, failed xarray allocation, and downstream request allocation failures against returned contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.h

### Purpose
`mock_context.h` declares context construction and destruction helpers used by i915 GEM selftests.

### Important APIs, Types, And Functions
It declares `mock_init_contexts()`, `mock_context()`, `mock_context_close()`, `live_context()`, `kernel_context()`, and `kernel_context_close()`, plus forward declarations for file, i915 device, engine, and address-space types.

### Control Flow
The header has no executable flow beyond making the helper interfaces available to mock and live tests.

### State, Persistence, And Dependencies
It stores no state. Dependencies are intentionally light and limited to forward declarations so selftests can include it without pulling in full context internals.

### Integration Points
Used by huge-page, dma-buf, context, client BLT, and other selftests that need mock-file or kernel contexts.

### Risks
Signature drift between this header and `mock_context.c` would break builds. The header also exposes helpers that return contexts with different lifetime expectations, so callers must use the matching close path.

### Test Signals
Compilation is the primary signal; runtime validation happens in tests using the declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.c

### Purpose
`mock_dmabuf.c` implements an in-memory dma-buf exporter for selftests so i915 PRIME import paths can be exercised without another real driver.

### Important APIs, Types, And Functions
The file defines dma-buf ops `mock_map_dma_buf()`, `mock_unmap_dma_buf()`, `mock_dmabuf_release()`, `mock_dmabuf_vmap()`, `mock_dmabuf_vunmap()`, `mock_dmabuf_mmap()`, and factory `mock_dmabuf()`.

### Control Flow
The factory allocates a flexible `mock_dmabuf`, allocates pages, fills `DEFINE_DMA_BUF_EXPORT_INFO`, and exports a dma-buf. Attachment mapping builds an sg table over the pages and calls `dma_map_sgtable()`. Vmap uses `vm_map_ram()`, vunmap reverses it, mmap is intentionally unsupported, and release drops all pages.

### State, Persistence, And Dependencies
State persists in the dma-buf private `struct mock_dmabuf` until release. Dependencies include Linux dma-buf ops, scatterlist allocation, DMA mapping, page allocation, and vmalloc mapping helpers.

### Integration Points
`i915_gem_dmabuf.c` uses this mock exporter to validate import, vmap, ownership, and page pinning behavior for external dma-bufs.

### Risks
Error paths must drop partially allocated pages and sg tables. The ops intentionally do not implement mmap, so tests relying on mmap must expect `-ENODEV`.

### Test Signals
Signals are dma-buf export/map/vmap failures, import failures in i915, and memory-pattern mismatches in PRIME tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.h

### Purpose
`mock_dmabuf.h` defines the private container and conversion helper for the mock dma-buf exporter used in selftests.

### Important APIs, Types, And Functions
It defines `struct mock_dmabuf` with `npages` and a flexible page array, and inline `to_mock()` to retrieve it from `dma_buf->priv`.

### Control Flow
There is no runtime flow beyond the inline cast helper.

### State, Persistence, And Dependencies
The header stores no state itself. The described state is owned by `mock_dmabuf.c` and attached to the exported dma-buf. It depends only on `<linux/dma-buf.h>`.

### Integration Points
Used by the mock dma-buf ops and included by dma-buf selftests that call `mock_dmabuf()`.

### Risks
The conversion assumes every dma-buf passed to `to_mock()` was exported by the mock exporter; using it on another dma-buf would interpret unrelated private data.

### Test Signals
Compilation and PRIME mock tests validate the struct layout and helper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_dmabuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_gem_object.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_gem_object.h

### Purpose
`mock_gem_object.h` provides a minimal mock GEM object wrapper type for selftests.

### Important APIs, Types, And Functions
It defines `struct mock_object` containing a single `struct drm_i915_gem_object base`.

### Control Flow
The header has no executable control flow.

### State, Persistence, And Dependencies
State is only the embedded GEM object when a selftest allocates this type. It depends on `gem/i915_gem_object_types.h`.

### Integration Points
The type is a simple building block for mock GEM tests that need a concrete container around the base i915 GEM object.

### Risks
Because the wrapper adds no fields, any test needing extra ownership metadata must provide it elsewhere. Layout assumptions are straightforward but still tied to i915 GEM object internals.

### Test Signals
Build coverage and mock object tests are the practical signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_gem_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.c

### Purpose
`gen2_engine_cs.c` implements command streamer helpers for gen2 through gen5 era engines: cache flush emission, breadcrumb writes, batch-buffer starts, i830 TLB workaround copying, and interrupt mask control.

### Important APIs, Types, And Functions
Exports include `gen2_emit_flush()`, `gen4_emit_flush_rcs()`, `gen4_emit_flush_vcs()`, `gen2_emit_breadcrumb()`, `gen5_emit_breadcrumb()`, `i830_emit_bb_start()`, `gen2_emit_bb_start()`, `gen4_emit_bb_start()`, `gen2_irq_enable/disable()`, and `gen5_irq_enable/disable()`.

### Control Flow
Flush paths reserve ring space and emit MI flush or pipe-control sequences with extra delay/store commands for old cache invalidation behavior. Breadcrumb helpers write request seqnos into the hardware status page and raise `MI_USER_INTERRUPT`. Batch starts encode secure/non-secure bits; i830 additionally blits unpinned batches into scratch to avoid stale TLB bugs before execution.

### State, Persistence, And Dependencies
State changes are ring buffer contents, request tail offsets, hardware status page seqnos, GT scratch contents, and IRQ mask registers. Dependencies include ring reservation, GPU command definitions, GT scratch offsets, uncore register access, and gen5 GT IRQ helpers.

### Integration Points
These functions are wired into engine ops for older platforms and are used by request submission, retirement signaling, and interrupt enable/disable paths.

### Risks
Old hardware workarounds rely on precise command ordering and scratch sizes. Wrong secure bits or insufficient i830 workaround space can execute the wrong batch address or expose privileged commands.

### Test Signals
Signals include request timeouts, missing breadcrumbs/interrupts, relocation visibility failures after invalidation, and ring-tail assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.h

### Purpose
`gen2_engine_cs.h` declares gen2/gen4/gen5 engine command-streamer operations for flushes, breadcrumbs, batch starts, and IRQ control.

### Important APIs, Types, And Functions
Declarations cover `gen2_emit_flush()`, `gen4_emit_flush_rcs()`, `gen4_emit_flush_vcs()`, `gen2_emit_breadcrumb()`, `gen5_emit_breadcrumb()`, `i830_emit_bb_start()`, `gen2_emit_bb_start()`, `gen4_emit_bb_start()`, and gen2/gen5 IRQ enable/disable functions.

### Control Flow
The header has no executable flow; it exposes implementations from `gen2_engine_cs.c` to engine setup code.

### State, Persistence, And Dependencies
It stores no state and depends only on Linux integer types plus forward declarations for `i915_request` and `intel_engine_cs`.

### Integration Points
Included by engine initialization code that assigns function pointers for legacy platforms.

### Risks
Prototype drift would break engine op binding at compile time. Incorrect use of generation-specific functions on the wrong platform would cause command encoding bugs.

### Test Signals
Build coverage and legacy-platform request submission tests validate this header's declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.c

### Purpose
`gen6_engine_cs.c` implements gen6/gen7/Haswell command streamer helpers for render and non-render engines: PIPE_CONTROL flushes, MI_FLUSH_DW flushes, breadcrumbs, batch-buffer starts, and IRQ masking.

### Important APIs, Types, And Functions
Key exports are `gen6_emit_flush_rcs()`, `gen6_emit_flush_xcs()`, `gen6_emit_flush_vcs()`, `gen6_emit_bb_start()`, `hsw_emit_bb_start()`, `gen7_emit_flush_rcs()`, breadcrumb emitters for RCS/XCS, and gen6/HSW IRQ enable/disable helpers. Internal helpers include `gen6_emit_post_sync_nonzero_flush()`, `mi_flush_dw()`, and `gen7_stall_cs()`.

### Control Flow
Gen6 render flushes first emit Sandy Bridge PIPE_CONTROL workarounds, then combine render/depth flushes and invalidate bits based on mode. XCS/VCS paths use `MI_FLUSH_DW` with TLB/BSD invalidation flags. Gen7 render flushes force CS stall and post-sync writes, adding a separate stall before state-cache invalidation. Breadcrumb paths write seqnos through pipe-control or MI flush commands and trigger user interrupts.

### State, Persistence, And Dependencies
State changes are command ring contents, hardware status page seqnos, scratch writes, request tail updates, and engine/GT interrupt masks. Dependencies include GPU command encodings, ring helpers, GT scratch offsets, gen5/gen6 IRQ infrastructure, and batch-start helpers from command definitions.

### Integration Points
The functions populate engine ops for SNB/IVB/HSW-era hardware and directly affect request ordering, cache coherency, and interrupt delivery.

### Risks
PIPE_CONTROL workarounds are ordering-sensitive. Missing CS stalls or post-sync writes can produce stale seqnos or cache incoherency. Breadcrumb sizes must match reserved ring space in engine setup.

### Test Signals
Signals include request hangs, stale CPU readback after GPU writes, missing interrupts, invalid ring tails, and platform-specific failures around render-cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.h

### Purpose
`gen6_engine_cs.h` declares gen6/gen7/Haswell engine command-streamer operations used by i915 engine setup.

### Important APIs, Types, And Functions
It declares render and XCS/VCS flush functions, breadcrumb emitters, batch-buffer start functions, and IRQ helpers: `gen6_emit_flush_rcs/xcs/vcs()`, `gen7_emit_flush_rcs()`, `gen6/gen7_emit_breadcrumb_*()`, `gen6_emit_bb_start()`, `hsw_emit_bb_start()`, `gen6_irq_enable/disable()`, and `hsw_irq_enable/disable_vecs()`.

### Control Flow
No runtime flow exists in the header; it exposes the generation-specific implementations.

### State, Persistence, And Dependencies
It stores no state and depends on Linux integer types, `intel_gpu_commands.h`, and forward declarations for request and engine objects.

### Integration Points
Engine initialization includes this header to bind command emission hooks for gen6/gen7-era platforms.

### Risks
The declarations are hardware-generation-specific; misbinding them to unsupported engines would emit invalid command sequences.

### Test Signals
Build coverage plus engine submission, flush, and interrupt tests validate correct declaration and binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.c

### Purpose
`gen6_ppgtt.c` implements Sandy Bridge/Ivy Bridge/Haswell-era per-process GTT support, including page-directory allocation, scratch setup, PDE flushing through GGTT, PTE insertion/clearing, pin/unpin, and platform enable programming.

### Important APIs, Types, And Functions
Important exports are `gen6_ppgtt_enable()`, `gen7_ppgtt_enable()`, `gen6_ppgtt_pin()`, `gen6_ppgtt_unpin()`, and `gen6_ppgtt_create()`. Core internals include `gen6_write_pde()`, `gen6_ppgtt_clear_range()`, `gen6_ppgtt_insert_entries()`, `gen6_flush_pd()`, `gen6_alloc_va_range()`, scratch setup, PD VMA bind/unbind ops, and dummy PD object ops.

### Control Flow
Creation allocates the PPGTT, initializes VM callbacks, builds scratch page/table state, and creates a top page-directory VMA in the GGTT. VA allocation stashes and installs page tables, fills them with scratch PTEs, increments used counts, and flushes PDEs if the PD VMA is globally bound. Insert writes DMA-backed PTEs from an sg iterator; clear resets PTEs to scratch and marks unused PTs for later cleanup. Pinning places the PD object high in GGTT and binds PDEs.

### State, Persistence, And Dependencies
Persistent driver state includes `struct gen6_ppgtt`, its page directory, scratch objects, PD GGTT VMA, `pd_addr`, `pp_dir`, pin count, PT used counts, and `scan_for_unused_pt`. Dependencies include GGTT allocation, page-table DMA helpers, runtime PM, uncore registers, vGPU/trace support, and VM reservation locking.

### Integration Points
The VM callbacks integrate with i915 address-space binding. Enable functions program platform registers for PPGTT cache behavior and pagefault continuation.

### Risks
Gen6 hardware cannot remove cached PDEs on the fly, so clear only resets PTEs. PDE flush ordering needs barriers, posting reads, and GGTT invalidation. Pin-count races or stale unused page tables can corrupt VM mappings.

### Test Signals
Signals include PPGTT creation failures, page-table leaks, stale mappings after clear, GPU page faults, binding failures, and generation-specific register misconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.h

### Purpose
`gen6_ppgtt.h` defines the gen6 PPGTT container, page-table index helpers, PDE iteration macros, and public PPGTT lifecycle functions.

### Important APIs, Types, And Functions
The central type is `struct gen6_ppgtt`, embedding `struct i915_ppgtt` plus a flush mutex, PD VMA, MMIO PD address, `pp_dir`, atomic pin count, and unused-PT scan flag. It provides `gen6_pte_index/count()`, `gen6_pde_index()`, `to_gen6_ppgtt()`, `gen6_for_each_pde()`, `gen6_for_all_pdes()`, and declarations for pin/unpin/enable/create functions.

### Control Flow
The macros iterate page-directory entries across rounded ranges or all PDEs. Inline conversion verifies the embedded base offset at build time.

### State, Persistence, And Dependencies
The header stores no state but defines the persistent state shape used by `gen6_ppgtt.c`. It depends on `intel_gtt.h` and the GEM ww-context forward declaration.

### Integration Points
Used by gen6 PPGTT implementation and engine/context code that needs to pin, unpin, enable, or create PPGTTs.

### Risks
The iteration macro mutates start/length arguments, so callers must pass simple variables. Incorrect container assumptions would break downcasts from `i915_ppgtt`.

### Test Signals
Build-time `BUILD_BUG_ON`, PPGTT selftests, and live VM binding failures are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_renderstate.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_renderstate.c

### Purpose
`gen6_renderstate.c` contains a generated gen6 null render-state batch used to initialize/reset render pipeline state for command submission.

### Important APIs, Types, And Functions
The file defines `gen6_null_state_relocs[]`, `gen6_null_state_batch[]`, and invokes `RO_RENDERSTATE(6)` to instantiate the renderstate object/accessors expected by the i915 renderstate framework.

### Control Flow
There is no normal C control flow; the static arrays encode GPU commands, relocation slots, and embedded state data. The `RO_RENDERSTATE` macro packages those arrays for runtime use by the renderstate loader.

### State, Persistence, And Dependencies
State is static read-only data in the driver image. Runtime persistence is the render-state batch copied/bound by the renderstate infrastructure. Dependencies are `intel_renderstate.h` and the generated batch format from intel-gpu-tools.

### Integration Points
Used when gen6 render engines need a known null state before executing user or kernel batches.

### Risks
Generated command words are opaque and hardware-specific. A wrong relocation offset or stale generated sequence can program invalid render state and cause GPU hangs.

### Test Signals
Signals are render engine hangs, failed renderstate load, relocation processing errors, and regressions on gen6 render submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_renderstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.c

### Purpose
`gen7_renderclear.c` builds a gen7/Haswell media-pipeline batch that clears residual general-purpose registers by dispatching a small kernel across all hardware threads.

### Important APIs, Types, And Functions
Main public API is `gen7_setup_clear_gpr_bb()`. Supporting types include `struct cb_kernel`, `struct batch_chunk`, and `struct batch_vals`. Helpers fill surface state, binding tables, kernel data, interface descriptors, state base addresses, VFE state, descriptor load, media objects, and pipeline flush/invalidate commands.

### Control Flow
`batch_get_defaults()` derives thread count and surface dimensions from platform/GT. If called with no VMA, `gen7_setup_clear_gpr_bb()` returns required batch size. Otherwise it maps the object WC, zeroes it, partitions command and state chunks, copies the IVB or HSW clear kernel, emits flush/invalidate and cache-mode setup, switches to media pipeline, emits state base and VFE/interface descriptors, dispatches one media object per hardware thread, and ends the batch.

### State, Persistence, And Dependencies
State is the generated batch contents inside the supplied VMA object. Dependencies include embedded `ivb_clear_kernel.c`/`hsw_clear_kernel.c`, GPU command definitions, platform GT sizing, cache-mode registers, and GEM object mapping/flush.

### Integration Points
Used by engine setup or workarounds that need to sanitize residual registers before user workloads on gen7-class render engines.

### Risks
Batch layout is alignment-sensitive. Incorrect thread counts can leave registers uncleared. Platform-specific cache-mode workarounds and IVB/HSW kernel selection must match hardware.

### Test Signals
Signals include returned size too small for allocated object, batch construction errors, GPU hangs while executing the clear batch, and security/selftest failures that detect uncleared residual state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.h

### Purpose
`gen7_renderclear.h` declares the gen7 render GPR clear-batch setup helper.

### Important APIs, Types, And Functions
It forward-declares `struct intel_engine_cs` and `struct i915_vma`, and declares `gen7_setup_clear_gpr_bb()`.

### Control Flow
The header has no executable flow. The declared function returns the required batch size when passed a null VMA or fills the supplied VMA when present.

### State, Persistence, And Dependencies
It stores no state and has only forward-declaration dependencies.

### Integration Points
Included by gen7 render engine setup code that allocates and populates the clear-GPR batch buffer.

### Risks
Callers must respect the two-mode API and allocate at least the size returned by a null-VMA call before asking the implementation to fill a VMA.

### Test Signals
Build coverage and render-clear execution tests validate the declaration and call contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderclear.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderstate.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderstate.c

### Purpose
`gen7_renderstate.c` contains a generated gen7 null render-state batch for initializing the render pipeline to a known state.

### Important APIs, Types, And Functions
The file defines `gen7_null_state_relocs[]`, `gen7_null_state_batch[]`, and invokes `RO_RENDERSTATE(7)`.

### Control Flow
Like the gen6 file, control flow is encoded as static GPU command/data arrays. Relocation offsets identify command words that the renderstate loader patches before submission.

### State, Persistence, And Dependencies
State is static read-only generated batch data plus runtime copies managed by the renderstate framework. The file depends on `intel_renderstate.h`.

### Integration Points
Used by gen7 render-engine initialization paths to emit a known null state before workloads.

### Risks
The generated data is hardware-specific and not self-describing. Incorrect relocation offsets, command words, or state layout can hang the render engine or leave stale state.

### Test Signals
Signals include renderstate load failures, GPU hangs on gen7 render workloads, and regressions in tests that require clean render pipeline state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen7_renderstate.c -->
