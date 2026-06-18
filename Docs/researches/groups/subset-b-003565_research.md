# Research: subset-b-003565

Grouped research for DRM GEM, GEM helper, VRAM, TTM, shmem, DMA, framebuffer, atomic-shadow, and GPU SVM files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/`. Each section preserves the source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem.c

## Purpose
`drm_gem.c` is the DRM core implementation for Graphics Execution Manager objects. It owns device-level GEM setup, object initialization and teardown, userspace handle tables, flink names, fake mmap offsets, shmem page extraction, VMA mapping setup, common vmap wrappers, reservation locking helpers, and LRU/shrinker support. It deliberately leaves synchronization policy, migration policy, and backing-store details to object-specific `drm_gem_object_funcs`, while providing the shared contracts that all GEM helpers and drivers rely on.

## Important APIs, Types, And Functions
Important exported APIs include `drm_gem_init()`, `drm_gem_object_init()`, `drm_gem_private_object_init()`, `drm_gem_object_release()`, `drm_gem_handle_create()`, `drm_gem_handle_delete()`, `drm_gem_object_lookup()`, `drm_gem_objects_lookup()`, `drm_gem_dumb_map_offset()`, `drm_gem_create_mmap_offset()`, `drm_gem_get_pages()`, `drm_gem_put_pages()`, `drm_gem_mmap_obj()`, `drm_gem_mmap()`, `drm_gem_get_unmapped_area()`, `drm_gem_vmap[_locked]()`, `drm_gem_vunmap[_locked]()`, `drm_gem_lock_reservations()`, `drm_gem_lru_*()`, and `drm_gem_evict_locked()`. The central state is `struct drm_gem_object`: `refcount`, `handle_count`, `name`, `filp`, `resv`, `vma_node`, `lru_node`, `funcs`, and optional GPUVA state.

## Control Flow
Device initialization creates `object_name_lock`, `object_name_idr`, and a VMA offset manager. Object initialization first sets up private GEM fields, initializes reservation and optional GPUVA state, then optionally allocates a shmem file as backing store. Handle creation increments `handle_count`, allocates an IDR entry under the file table lock, allows VMA access for the file, calls the object's `open` hook, and finally publishes the object pointer into the handle table. Handle deletion removes the table pointer first, calls the object's `close` hook, removes PRIME handle bookkeeping, revokes mmap permission, decrements the handle reference, and then frees the IDR slot. Mmap flows through fake offsets: `drm_gem_mmap()` looks up an exact `vma_node`, checks file permission, then `drm_gem_mmap_obj()` pins a GEM reference into the VMA and either calls the object's `mmap` hook or installs generic PFNMAP/write-combined vm flags and vm ops.

## State And Persistence Behavior
GEM objects are kernel-lifetime objects with kref ownership and per-open userspace handles. `handle_count` owns one object reference while at least one userspace handle exists. Global flink names live in `dev->object_name_idr` and are removed when the last handle goes away. Fake mmap offsets live in the device VMA manager and are released by `drm_gem_object_release()`. Shmem-backed objects persist pages in the anonymous file until `drm_gem_put_pages()` or object release, with `mapping_set_unevictable()` used while page arrays are held. LRU membership tracks page counts and is explicitly updated by users of the LRU helpers.

## Dependencies And Integration Points
This file integrates with Linux shmem/tmpfs, folios, IDR, kref, dma-resv, dma-buf/PRIME bookkeeping, VMA offset management, DRM file lifecycle, DRM ioctl dispatch, managed DRM cleanup (`drmm_add_action`), and optional Transparent Hugepage tmpfs mounts. Object-specific behavior is supplied through `drm_gem_object_funcs` hooks such as `free`, `open`, `close`, `mmap`, `vmap`, `vunmap`, `print_info`, and `evict`. Higher-level helpers in this subset build on these APIs for DMA, shmem, TTM, VRAM, framebuffer, and atomic plane use cases.

## Risks
The most sensitive areas are reference ownership around handles, mmap VMAs, exported dma-bufs, and IDR replacement. Wrong ordering can expose freed objects or leak handle references. Mmap lookup must continue to reject zero-refcount objects and unauthorized VMA nodes. Shmem page pinning must preserve GFP zone constraints and release folios in batches. `drm_gem_get_unmapped_area()` currently calls `drm_gem_object_put(obj)` even when lookup failed and `obj` was set to NULL, so any change to the null tolerance of `drm_gem_object_put()` would matter. LRU shrink callbacks must remove successfully shrunk objects from the LRU and avoid blocking on already-held reservation locks.

## Test Signals
Useful signals include DRM core build coverage, GEM ioctl tests for create/open/close/flink/change-handle paths, PRIME import/export handle tests, mmap permission tests using stale and unauthorized offsets, shmem page pin/unpin stress, reservation deadlock tests for multi-object locking, and shrinker/LRU tests that exercise active, idle, and refcount-zero objects. Runtime debugfs output from `drm_gem_print_info()` and lockdep coverage for dma-resv and LRU locks are also important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_atomic_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_atomic_helper.c

## Purpose
`drm_gem_atomic_helper.c` provides generic atomic modeset helpers for GEM-backed framebuffers. It primarily solves two problems: implicit synchronization for GEM framebuffer planes and safe kernel mappings for shadow-buffered planes whose commit-tail update functions need CPU access to framebuffer data.

## Important APIs, Types, And Functions
The main synchronization entry point is `drm_gem_plane_helper_prepare_fb()`, which extracts reservation fences from every GEM object backing a framebuffer plane. Shadow-plane state helpers include `__drm_gem_duplicate_shadow_plane_state()`, `drm_gem_duplicate_shadow_plane_state()`, `__drm_gem_destroy_shadow_plane_state()`, `drm_gem_destroy_shadow_plane_state()`, `__drm_gem_reset_shadow_plane()`, and `drm_gem_reset_shadow_plane()`. Mapping helpers are `drm_gem_begin_shadow_fb_access()` and `drm_gem_end_shadow_fb_access()`, with `drm_gem_simple_kms_*` wrappers for `struct drm_simple_display_pipe`.

## Control Flow
`prepare_fb` starts with any explicit fence already attached to the plane state. If an explicit fence exists, it requests kernel fences from each GEM reservation object; otherwise it requests write fences. For each framebuffer plane, it obtains the GEM object through `drm_gem_fb_get_obj()`, calls `dma_resv_get_singleton()`, and either installs that fence directly or chains it with the existing fence using `dma_fence_chain`. Shadow state reset allocates a `drm_shadow_plane_state`, initializes base atomic state and format-conversion state, and attaches it to the plane. Duplication copies the base atomic state and format conversion state but intentionally does not copy mappings. `begin_shadow_fb_access` maps all framebuffer BOs through `drm_gem_fb_vmap()` and records both base mappings and offset-adjusted data pointers; `end_shadow_fb_access` unmaps in reverse through `drm_gem_fb_vunmap()`.

## State And Persistence Behavior
The helper stores per-commit shadow mappings in `struct drm_shadow_plane_state`, not in the plane or framebuffer itself. Mapping lifetime is bounded by atomic access callbacks and must not leak into duplicated state. Fence state is persisted in `state->fence` for the atomic helper machinery to wait on. Format conversion state is copied and released with the shadow plane state.

## Dependencies And Integration Points
This file depends on dma-resv and dma-fence-chain for implicit synchronization, DRM atomic state helpers for plane-state lifecycle, `drm_gem_framebuffer_helper.c` for framebuffer BO lookup and vmap/vunmap, and `drm_simple_kms_helper` for simple display pipe wrappers. Drivers commonly wire these helpers through `DRM_GEM_SHADOW_PLANE_FUNCS`, `DRM_GEM_SHADOW_PLANE_HELPER_FUNCS`, or plane helper `prepare_fb`.

## Risks
Fence merging is subtle: explicit fences are intentionally allowed to override normal implicit write-fence behavior, and adding both in the wrong way would regress explicit synchronization use cases such as different refresh rates sharing one buffer. Shadow mappings must be created outside commit-tail paths that cannot legally call `dma_buf_vmap()`. State duplication must not retain stale `iosys_map` pointers. Error paths in `prepare_fb` must drop the currently accumulated fence chain.

## Test Signals
Coverage should include atomic plane updates with imported dma-buf framebuffers, explicit fence versus implicit fence behavior, multi-plane framebuffer fence chaining, shadow-plane reset/duplicate/destroy cycles, begin/end mapping balance under failure injection, and simple-KMS users of the wrapper callbacks. Lockdep and dma-fence selftests are relevant supporting signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_atomic_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_dma_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_dma_helper.c

## Purpose
`drm_gem_dma_helper.c` implements GEM objects backed by DMA-addressable memory that is contiguous from the device perspective. It targets simple display and accelerator devices that either require physically contiguous CMA memory or see contiguous IOVA through an IOMMU. It supplies default GEM object callbacks, dumb-buffer creation, mmap, vmap, debug printing, and PRIME import/export helpers.

## Important APIs, Types, And Functions
The key type is `struct drm_gem_dma_object`, wrapping `struct drm_gem_object` with `vaddr`, `dma_addr`, `sgt`, and noncoherent mapping state. Public functions include `drm_gem_dma_create()`, `drm_gem_dma_free()`, `drm_gem_dma_dumb_create[_internal]()`, `drm_gem_dma_get_sg_table()`, `drm_gem_dma_prime_import_sg_table()`, `drm_gem_dma_prime_import_sg_table_vmap()`, `drm_gem_dma_vmap()`, `drm_gem_dma_mmap()`, `drm_gem_dma_print_info()`, and no-MMU `drm_gem_dma_get_unmapped_area()`. `drm_gem_dma_default_funcs` wires these into GEM callbacks.

## Control Flow
Creation rounds size to pages, allocates or driver-creates a GEM object, installs default funcs when missing, initializes either shmem-backed public GEM state or private imported state, creates a fake mmap offset, then allocates backing memory with `dma_alloc_wc()` or `dma_alloc_noncoherent()`. Dumb creation computes pitch and size, creates the DMA object, publishes a GEM handle, and drops the allocation reference. Freeing distinguishes imported buffers from native allocations: imported objects unmap any vmap and call `drm_prime_gem_destroy()`, while native objects free DMA memory through the matching coherent/write-combined API. Mmap adjusts the fake offset to object-relative offset, clears PFNMAP from the generic GEM setup, sets DONTDUMP/DONTEXPAND, and maps the whole DMA allocation with `dma_mmap_wc()` or `dma_mmap_pages()`.

## State And Persistence Behavior
Native DMA GEM objects keep a stable kernel virtual address and bus address for their lifetime. Imported objects may only have `dma_addr`, `sgt`, and optional vmap state derived from the dma-buf exporter. GEM handle state and mmap offsets are owned by the core GEM code. The `map_noncoherent` flag selects allocation and mmap/free symmetry.

## Dependencies And Integration Points
This helper depends on the DMA mapping API, CMA or IOMMU behavior behind `drm_dev_dma_dev()`, drm dumb-buffer sizing, GEM VMA management, dma-buf PRIME attachment/import paths, and optional no-MMU file operation integration. Drivers typically use the macros in the corresponding header to populate `drm_driver` and `drm_gem_object_funcs`.

## Risks
The largest risk is assuming physical contiguity for imported buffers: `drm_gem_dma_prime_import_sg_table()` rejects imports whose contiguous size is smaller than the dma-buf size, and relaxing that would break devices without scatter-gather. Allocation/free APIs must match `map_noncoherent`. Mmap must preserve VMA flags so core GEM references are released if mapping fails. Imported vmap paths must unmap with `dma_buf_vunmap_unlocked()` during free. Dumb-buffer size multiplication should remain guarded by `drm_mode_size_dumb()` where possible.

## Test Signals
Useful tests include dumb-buffer creation and mmap on CMA and IOMMU-backed devices, PRIME import of contiguous and non-contiguous sg tables, dma-buf vmap import and free, no-MMU get-unmapped-area lookup and permission checks, debugfs print verification, and failure injection for DMA allocation, mmap, and handle publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_dma_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_framebuffer_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_framebuffer_helper.c

## Purpose
`drm_gem_framebuffer_helper.c` provides framebuffer helpers for drivers that use plain `struct drm_framebuffer` backed directly by GEM objects. It validates framebuffer BO sizes, initializes framebuffer objects, manages GEM references, exposes BO handle creation for GETFB, maps/unmaps framebuffer BOs for CPU access, synchronizes imported dma-bufs for CPU access, and validates AFBC layout size requirements.

## Important APIs, Types, And Functions
Core exports are `drm_gem_fb_get_obj()`, `drm_gem_fb_destroy()`, `drm_gem_fb_create_handle()`, `drm_gem_fb_init_with_funcs()`, `drm_gem_fb_create_with_funcs()`, `drm_gem_fb_create()`, `drm_gem_fb_create_with_dirty()`, `drm_gem_fb_vmap()`, `drm_gem_fb_vunmap()`, `drm_gem_fb_begin_cpu_access()`, `drm_gem_fb_end_cpu_access()`, and `drm_gem_fb_afbc_init()`. It also defines standard framebuffer funcs with optional dirty callback via `drm_atomic_helper_dirtyfb`.

## Control Flow
Framebuffer creation first checks atomic-driver format/modifier support, then looks up each GEM handle from the creating DRM file. For each format plane it computes plane-adjusted width and height, calculates the minimum byte size from pitch, min pitch, and offset, and rejects undersized GEM objects. Successful validation stores object references in `fb->obj[]` and calls `drm_framebuffer_init()`. Destruction drops each GEM reference, cleans up the framebuffer, and frees the struct. Vmap maps every backing object through `drm_gem_vmap()` and unwinds already mapped planes on failure; optional data pointers are derived by adding each plane offset. CPU access begin/end only calls dma-buf CPU access hooks for imported GEM objects. AFBC initialization decodes block size and tiled-header modifier bits, computes aligned dimensions, header size, body size, and rejects too-small backing objects.

## State And Persistence Behavior
The framebuffer holds one GEM reference per backing plane for its lifetime. `fb->obj[]`, pitches, offsets, modifiers, and format metadata form the persistent state consumed by atomic helpers and drivers. Vmap state is caller-owned through arrays of `struct iosys_map` and must be explicitly released. Dirty framebuffer support persists through the selected framebuffer funcs.

## Dependencies And Integration Points
This helper integrates with DRM format metadata, mode config `fb_create`, GEM handle lookup, GEM vmap/vunmap, dma-buf CPU access synchronization, atomic damage helper dirty handling, and AFBC modifier definitions. It is commonly paired with `drm_gem_atomic_helper.c` shadow-plane helpers and simple display drivers.

## Risks
Generic size validation may be insufficient for hardware-specific pitch, alignment, tiling, compression, or modifier constraints; drivers must validate those before or around these helpers. Integer overflow in size calculations would be high impact, so callers rely on prior mode validation and small typed fields. CPU access calls only cover imported BOs; native cache management remains object/driver-specific. AFBC bpp handling includes format-specific special cases and a TODO to replace it once format block info is complete.

## Test Signals
ADDFB2/GETFB tests should cover multi-plane formats, offsets, undersized BO rejection, unsupported format/modifier rejection, dirtyfb paths, vmap unwind on partial failure, imported dma-buf begin/end CPU access, and AFBC modifiers including invalid block sizes, tiled headers, and too-small buffers. IGT framebuffer and kms tests are the most relevant runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_framebuffer_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_shmem_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_shmem_helper.c

## Purpose
`drm_gem_shmem_helper.c` implements GEM objects backed by anonymous shmem pages. It is the standard helper for pageable system-memory GEM buffers, with support for page pinning, vmap/vunmap, dumb-buffer creation, mmap faults, madvise/purge, sg table creation, DMA mapping for device access, PRIME import variants, debug printing, and KUnit-only convenience wrappers.

## Important APIs, Types, And Functions
The key type is `struct drm_gem_shmem_object`, which extends GEM with `pages`, `pages_use_count`, `pages_pin_count`, `vmap_use_count`, `vaddr`, `sgt`, `madv`, purge list state, and write-combine flags. Important exports include `drm_gem_shmem_init()`, `drm_gem_shmem_create()`, `drm_gem_shmem_release()`, `drm_gem_shmem_free()`, `drm_gem_shmem_pin[_locked]()`, `drm_gem_shmem_unpin[_locked]()`, `drm_gem_shmem_put_pages_locked()`, `drm_gem_shmem_vmap_locked()`, `drm_gem_shmem_vunmap_locked()`, `drm_gem_shmem_madvise_locked()`, `drm_gem_shmem_purge_locked()`, `drm_gem_shmem_mmap()`, `drm_gem_shmem_get_sg_table()`, `drm_gem_shmem_get_pages_sgt()`, `drm_gem_shmem_prime_import_sg_table()`, and `drm_gem_shmem_prime_import_no_map()`.

## Control Flow
Initialization installs default GEM funcs, uses either regular `drm_gem_object_init()` or private object init for imported buffers, creates a fake mmap offset, initializes purge-list state, and sets a non-movable-friendly GFP mask for native shmem mappings. Page acquisition calls core `drm_gem_get_pages()`, optionally marks pages write-combined on x86, stores the page array, and sets use counts. Pinning increments the pin count or acquires pages under the reservation lock. Vmap either delegates imported objects to `dma_buf_vmap()` or pins native pages, vmaps them with write-combined protection when requested, and marks pages dirty/accessed on put. Mmap rejects COW mappings for native objects, pins pages, installs PFNMAP/DONTEXPAND/DONTDUMP flags, and uses custom fault handlers to insert PFNs. sg-table acquisition pins pages, builds an sg table, DMA maps it, caches it in `shmem->sgt`, and unwinds on failure. Purge unmaps DMA, frees the sg table, drops pages, marks `madv = -1`, removes mmap offsets, truncates shmem, and invalidates mapping pages.

## State And Persistence Behavior
The helper tracks separate page use, pin, and vmap reference counts. Native page arrays and cached sg tables persist until unpinned, purged, or object release. Imported objects preserve exporter-owned state through `import_attach`, external `resv`, and optionally an unmapped dma-buf attachment when `prime_import_no_map` is used. `madv` acts as purgeability state: non-negative means retained, negative means purged. VMAs hold GEM references via core vm open/close while shmem VM open/close adjusts page use counts.

## Dependencies And Integration Points
This file integrates with shmem-backed core GEM pages, dma-resv locking, dma-buf PRIME, Linux vm fault insertion including optional PMD PFNMAP huge faults, x86 page cacheability helpers, DMA sg mapping, DRM dumb-buffer sizing, and KUnit visibility. Drivers consume it through `drm_gem_object_funcs`, driver PRIME callbacks, dumb-create callbacks, and shrinker/purge code.

## Risks
Reference-count symmetry is the main risk: page use, pin, vmap, mmap, and sg-table lifetimes overlap. Purge is only valid for purgeable objects and must not race active mappings or DMA use. Imported objects bypass native page pinning and must keep dma-buf attachment/reservation ownership correct. Fault insertion must reject purged objects and out-of-range offsets. Write-combined page attribute changes are x86-specific and must be reverted before pages are returned. The KUnit helper `drm_gem_shmem_vunmap()` ignores the return from `dma_resv_lock_interruptible()`, which is acceptable for test-only visibility but should not be copied into production paths.

## Test Signals
Coverage should include shmem dumb create, mmap faults and write faults, forked VMA open/close accounting, vmap/vunmap reference counts, sg-table caching and DMA unmap on release, madvise/purge behavior under shrinker pressure, imported dma-buf mapping and no-map import, x86 write-combine attribute transitions, PMD fault fallback, and KUnit tests for vmap, madvise, and purge helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_shmem_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_ttm_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_ttm_helper.c

## Purpose
`drm_gem_ttm_helper.c` is a small adapter layer between GEM objects and TTM buffer objects. It supplies reusable GEM callback implementations for TTM-backed drivers: debug printing, vmap/vunmap, mmap, and dumb-buffer mmap-offset retrieval.

## Important APIs, Types, And Functions
Public APIs are `drm_gem_ttm_print_info()`, `drm_gem_ttm_vmap()`, `drm_gem_ttm_vunmap()`, `drm_gem_ttm_mmap()`, and `drm_gem_ttm_dumb_map_offset()`. The helper relies on `drm_gem_ttm_of_gem()` to convert a GEM object to `struct ttm_buffer_object`, and on TTM APIs including `ttm_bo_vmap()`, `ttm_bo_vunmap()`, and `ttm_bo_mmap_obj()`.

## Control Flow
Debug printing reads the TTM resource placement bitmask, formats known placement and caching bits, and prints bus offsets when the current resource is I/O memory. Vmap and vunmap are direct wrappers around TTM BO vmap APIs. Mmap delegates to `ttm_bo_mmap_obj()` and then drops the GEM reference acquired by `drm_gem_mmap_obj()` because TTM has taken over object VMA lifetime accounting. Dumb map offset looks up the GEM handle, returns the already allocated `vma_node` offset address, and releases the lookup reference.

## State And Persistence Behavior
This file does not own backing memory state. TTM owns placement, resources, mmap behavior, and BO refcounting after handoff. GEM owns handle lookup and fake offset storage. `drm_gem_ttm_mmap()` is notable because it intentionally transfers lifetime responsibility away from the GEM mmap reference to TTM.

## Dependencies And Integration Points
It depends on DRM printer helpers, GEM object lookup, VMA offset storage, and TTM placement/resource/mmap APIs. It is used by TTM-backed GEM helpers such as VRAM and by drivers that expose TTM BOs through GEM interfaces.

## Risks
The key correctness point is the extra `drm_gem_object_put()` after successful TTM mmap; removing it would double-account references, while doing it on failed mmap would underflow ownership. Debug printing assumes `bo->resource` is valid. Dumb-map offset assumes the TTM/GEM object already has an initialized `vma_node`.

## Test Signals
Build coverage with TTM drivers, mmap tests for TTM GEM BOs, dumb map offset ioctl tests, vmap/vunmap tests across system and VRAM placements, and debugfs inspection of placement/bus offset output provide the main signals. Refcount leak checks around mmap are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_ttm_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_vram_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_vram_helper.c

## Purpose
`drm_gem_vram_helper.c` implements GEM objects backed by a TTM-managed VRAM aperture for simple devices with dedicated video memory. It provides VRAM BO creation, pin/unpin, vmap/vunmap, dumb-buffer creation, plane prepare/cleanup helpers that pin scanout buffers to VRAM, a TTM device implementation for VRAM placement/moves, debugfs, managed VRAM MM initialization, and mode validation based on available VRAM.

## Important APIs, Types, And Functions
The main types are `struct drm_gem_vram_object` and `struct drm_vram_mm`. Public functions include `drm_gem_vram_create()`, `drm_gem_vram_put()`, `drm_gem_vram_offset()`, `drm_gem_vram_vmap()`, `drm_gem_vram_vunmap()`, `drm_gem_vram_fill_create_dumb()`, `drm_gem_vram_driver_dumb_create()`, `drm_gem_vram_plane_helper_prepare_fb()`, `drm_gem_vram_plane_helper_cleanup_fb()`, `drm_vram_mm_debugfs_init()`, `drmm_vram_helper_init()`, and `drm_vram_helper_mode_valid()`. It also defines TTM device funcs and default GEM object funcs using TTM mmap/print helpers.

## Control Flow
VRAM object creation requires `dev->vram_mm`, allocates or driver-creates a GEM/TTM object, initializes GEM shmem metadata, assigns the TTM device, starts placement in system memory, and calls `ttm_bo_init_validate()`. Pinning reserves the TTM BO, selects requested placement flags, validates placement, and increments the TTM pin count. Vmap requires the caller to hold the reservation lock, lazily calls `ttm_bo_vmap()` only when no cached map exists, increments `vmap_use_count`, and returns the cached map. Vunmap only decrements the use count; the actual unmap is delayed until move/delete notification. Plane prepare pins every framebuffer GEM object into VRAM, then calls GEM atomic `prepare_fb` for fencing; cleanup unpins all planes. TTM move callbacks unmap cached mappings before memcpy moves, choose system placement for eviction, reserve VRAM bus addresses, and initialize a range manager for the VRAM aperture.

## State And Persistence Behavior
`drm_vram_mm` persists on `drm_device.vram_mm` and is managed by `drmm_add_action_or_reset()`. Each VRAM BO persists current TTM resource placement, pin count, cached map, vmap use count, and placement arrays. Pinned scanout buffers have stable VRAM offsets returned by `drm_gem_vram_offset()`. Cached vmaps persist across vunmap calls until the BO moves or is deleted, reducing page-table churn.

## Dependencies And Integration Points
The helper integrates GEM with TTM resource managers, TTM TT, TTM move/mmap/vmap APIs, GEM framebuffer helpers, GEM atomic fence helpers, DRM managed cleanup, DRM debugfs, DRM mode validation, and PRIME/GEM object callback infrastructure. Drivers use it through `DRM_GEM_VRAM_DRIVER`, `DEFINE_DRM_GEM_FOPS`, dumb-create callbacks, and plane helper callbacks.

## Risks
VRAM helpers assume `dev->vram_mm` is initialized and warn otherwise. Pin/unpin must be balanced or scanout BOs will remain immovable. `drm_gem_vram_offset()` only makes sense for pinned non-system resources. Cached mappings must be unmapped before TTM moves; moving while `vmap_use_count` is nonzero is warned and unsafe. Plane prepare must unwind partial pins on failure. Mode validation uses a conservative half-VRAM and 32-bit-depth assumption, so it is a general admission check rather than a guarantee under heavy pinning.

## Test Signals
Relevant tests include VRAM MM initialization and cleanup, dumb-buffer create/map, pin/unpin balance through atomic plane updates, scanout offset correctness, TTM eviction from VRAM to system, vmap caching across moves, debugfs `vram-mm`, mode validation for large modes, and memory pressure scenarios where inactive BOs are evicted while active scanout remains pinned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_vram_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpusvm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpusvm.c

## Purpose
`drm_gpusvm.c` implements the DRM GPU Shared Virtual Memory helper layer. It lets GPU drivers mirror CPU virtual address ranges into GPU page tables by managing MMU interval notifiers, dynamically sized SVM ranges, HMM page collection, DMA mappings for system and device-private memory, advisory migration-state scans, range invalidation state, and range teardown. It is infrastructure for drivers that implement GPU page fault handling, invalidation callbacks, and garbage collection.

## Important APIs, Types, And Functions
Central types are `struct drm_gpusvm`, `struct drm_gpusvm_notifier`, `struct drm_gpusvm_range`, `struct drm_gpusvm_pages`, `struct drm_gpusvm_ctx`, and driver callbacks in `struct drm_gpusvm_ops`. Key exports include `drm_gpusvm_init()`, `drm_gpusvm_fini()`, `drm_gpusvm_notifier_find()`, `drm_gpusvm_range_find()`, `drm_gpusvm_range_find_or_insert()`, `drm_gpusvm_range_remove()`, `drm_gpusvm_range_get()/put()`, `drm_gpusvm_scan_mm()`, `drm_gpusvm_find_vma_start()`, `drm_gpusvm_get_pages()`, `drm_gpusvm_range_get_pages()`, `drm_gpusvm_unmap_pages()`, `drm_gpusvm_range_unmap_pages()`, `drm_gpusvm_range_evict()`, `drm_gpusvm_has_mapping()`, `drm_gpusvm_range_pages_valid()`, and `drm_gpusvm_range_set_unmapped()`.

## Control Flow
Initialization records the target `mm`, address window, notifier size, chunk sizes, DRM device, and ops; full SVM mode requires an invalidate callback and chunk sizes, while page-only API mode allows a minimal setup. On GPU fault, drivers call `drm_gpusvm_range_find_or_insert()` while holding their own SVM lock. The helper validates the fault address, finds or allocates an interval notifier, inserts it into the mm, locates the CPU VMA, checks write permission for writable faults, chooses the largest aligned chunk that fits the CPU VMA, notifier, and GPUVA bounds, optionally verifies CPU pages are already present for larger chunks, allocates a range, inserts it into the notifier range tree/list, and inserts the notifier into the global tree/list. Invalidation is delivered through `mmu_interval_notifier`: the helper takes `notifier_lock`, updates the notifier sequence, and calls the driver's invalidate op. Page collection uses HMM faults with requested read/write permissions, retries on notifier sequence changes, allocates `drm_pagemap_addr` arrays, maps system pages with `dma_map_page()`, maps DRM device-private pages through `drm_pagemap` callbacks, stores flags, and records the notifier sequence. Removal unmaps DMA/device mappings, frees address arrays, removes the range, releases it, and removes/free the notifier when empty.

## State And Persistence Behavior
`drm_gpusvm` owns a global interval tree and ordered list of notifiers plus a global `notifier_lock`. Each notifier owns its MMU interval notifier and an interval tree/list of ranges. Each range owns refcounted lifetime, interval bounds, a parent notifier pointer, and `drm_gpusvm_pages` state. `drm_gpusvm_pages` persists DMA/device mappings, a notifier sequence, a device pagemap reference, and flags such as `has_dma_mapping`, `has_devmem_pages`, `unmapped`, `partial_unmap`, and `migrate_devmem`. Partial unmap is not split; drivers are expected to invalidate the whole range and migrate remaining device memory back as needed.

## Dependencies And Integration Points
This file is tightly coupled to Linux HMM (`hmm_range_fault`, HMM PFN flags), MMU interval notifiers, mmap locking, zone-device/device-private pages, DMA mapping, DRM pagemap callbacks for device memory, interval trees, kref, lockdep annotations, and DRM driver-provided invalidation/range allocation hooks. It is expected to be called from GPU page fault handlers, driver invalidation callbacks, GPU binding commit paths, and driver garbage collectors.

## Risks
This is high-concurrency memory-management code. Drivers must hold their own SVM lock around range insertion/removal and must recheck `drm_gpusvm_range_pages_valid()` under `notifier_lock` immediately before committing GPU bindings. Missing invalidation or DMA unmap in a notifier callback can violate the IOMMU security model. Mixed system/device/private pages are rejected unless allowed by context; incorrect `allow_mixed`, `devmem_only`, or `device_private_page_owner` policy can cause faults, retries, or unsupported mappings. Timeout/retry behavior around HMM faults must avoid livelock. Partial unmaps intentionally destroy whole ranges, so driver garbage collectors must handle `partial_unmap` and migrate surviving device-memory pages. The documented examples contain illustrative pseudo-code and should not be treated as complete driver locking or migration policy.

## Test Signals
Strong signals include GPU fault tests that create ranges at every chunk size and boundary, VMA permission rejection tests, notifier invalidation and UNMAP races, retry tests where CPU mappings change during HMM collection, system-page DMA mapping and device-private mapping paths, mixed-page rejection/allowance, `drm_gpusvm_scan_mm()` state classification, partial-unmap garbage collection, range eviction back to system memory, teardown with live notifiers/ranges, and lockdep validation for driver SVM lock plus `notifier_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpusvm.c -->
