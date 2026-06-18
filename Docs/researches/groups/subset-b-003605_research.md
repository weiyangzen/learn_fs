# Research: subset-b-003605

This grouped report covers the i915 GEM object, domain, mmap, local-memory, internal-object, frontbuffer, ioctl declaration, and execbuffer paths under `sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/`. Each section preserves the source path for reconciliation into the mirrored per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.c

## Purpose
`i915_gem_domain.c` implements cache-domain transitions for i915 GEM buffer objects. It coordinates CPU, WC, GTT, and render-domain access by waiting for outstanding work, pinning pages when direct CPU access requires stable backing storage, flushing write domains, updating `read_domains`/`write_domain`, and invalidating or flushing display frontbuffers. It also owns the legacy caching and set-domain ioctls and the display-plane pin path that forces scanout-safe cache policy.

## Important APIs and Functions
- `i915_gem_cpu_write_needs_clflush()` decides whether CPU writes must later be flushed, excluding dGPU and already-dirty objects and treating framebuffer/display use as a forced flush case.
- `flush_write_domain()` is the central write-domain drain helper. It flushes GGTT writes through all GGTT VMAs, emits WC barriers, synchronously clflushes CPU-domain writes, and marks render-domain writes as `cache_dirty` when GPU writes are not coherent.
- `i915_gem_object_flush_if_display()` and `_locked()` flush display-frontbuffer objects, using `I915_CLFLUSH_FORCE` if `cache_dirty` remains.
- `i915_gem_object_set_to_wc_domain()`, `_gtt_domain()`, and `_cpu_domain()` serialize access, wait for GPU fences, pin pages where needed, flush incompatible write domains, update domain fields, and mark `obj->mm.dirty` for writes.
- `i915_gem_object_set_cache_level()` changes the object PAT/cache coherency model, marks cached contents dirty, then unbinds VMAs so the new cache level is applied on rebind.
- `i915_gem_get_caching_ioctl()` and `i915_gem_set_caching_ioctl()` expose legacy caching controls except on dGPU, newer PAT-user-managed objects, and unsupported platforms.
- `i915_gem_set_domain_ioctl()` validates userspace CPU-domain requests, handles userptr validation, rejects proxy objects, pins pages, transitions to WC/GTT/CPU domain, and frontbuffer-invalidates writes.
- `i915_gem_object_prepare_read()` and `_prepare_write()` provide pread/pwrite setup: wait, pin pages, choose full CPU-domain transition or manual clflush flags, and return with pages pinned for the caller to finish.
- `i915_gem_object_pin_to_display_plane()` prepares scanout by forcing WT/NONE cache policy, optionally adding guard-page pin flags, preferring mappable GGTT placement, marking scanout, and flushing display data.

## Control Flow
Domain transitions all follow a common pattern: assert the object reservation is held, wait for relevant GPU activity, pin backing pages if direct memory-domain state must be stable, call `flush_write_domain()` for every incompatible write domain, then set `read_domains`, `write_domain`, and dirty/frontbuffer state for the requested access. Display pinning first enforces LMEM residency on LMEM platforms, changes cache level to WT when available or NONE otherwise, GGTT-pins with display constraints, then marks and flushes scanout.

The caching ioctls first gate unsupported device classes. `get_caching` uses an RCU object lookup and refuses `pat_set_by_user` objects. `set_caching` maps UAPI caching values to `enum i915_cache_level`, handles proxy/userptr exceptions, then locks the object and delegates to `i915_gem_object_set_cache_level()`.

## State and Persistence
The file mutates persistent object fields: `read_domains`, `write_domain`, `cache_dirty`, `cache_coherent` through object helpers, `mm.dirty`, GGTT VMA write tracking via `i915_vma_set_ggtt_write()`, and frontbuffer state through invalidate/flush calls. Cache-level changes persist in `pat_index`/coherency fields and force VMA unbind so future PTEs encode the new policy.

## Dependencies and Integration Points
This code depends on `i915_gem_clflush`, VMA/GGTT helpers, memory-region/LMEM helpers, display frontbuffer tracking, object wait/pin APIs, userptr validation, and UAPI structs from `i915_drm.h`. It is called by pread/pwrite, mmap fault/access paths, execbuffer relocation and GPU submission preparation, display modesetting, and GEM ioctl dispatch.

## Risks
- Incorrect domain transitions can expose stale data, especially on non-LLC platforms and objects whose GPU accesses bypass CPU cache.
- `pat_set_by_user` objects intentionally bypass kernel coherency assumptions; callers must not infer normal `cache_dirty` semantics for them.
- Display scanout requires extra cache conservatism; missing a flush can produce visible corruption.
- The set-domain ioctl deliberately rejects GPU domains and dGPU; changing these gates risks ABI or coherency regressions.
- Locking assumes the object reservation lock is held for most helpers; using them unlocked would race page migration, VMA state, or dirty accounting.

## Test Signals
Relevant signals include i915 selftests for GEM coherency/object behavior included from nearby object code, display scanout tests that catch stale framebuffer data, IGT pread/pwrite and set-domain tests, mmap coherency tests, and execbuffer relocation tests that exercise CPU/GTT write-domain transitions. Runtime `GEM_BUG_ON` assertions check impossible residual write domains after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.h

## Purpose
`i915_gem_domain.h` is the small public header for GEM domain/cache-level code. It forward-declares the GEM object and cache-level enum and exports the cache-level mutation API used by display, ioctl, and other GEM paths.

## Important APIs and Types
- `struct drm_i915_gem_object` and `enum i915_cache_level` are forward declarations, keeping the header lightweight.
- `i915_gem_object_set_cache_level(struct drm_i915_gem_object *obj, enum i915_cache_level cache_level)` changes object-wide cache policy and triggers VMA rebinding behavior in the implementation.

## Control Flow and Integration
The header has no runtime logic. Its single function is implemented in `i915_gem_domain.c` and is consumed by display pinning and caching ioctl paths, while broader domain helpers are declared in `i915_gem_object.h`.

## State and Persistence
No state is stored here. The declared function mutates object PAT/cache coherency and cache-dirty state in the implementation.

## Dependencies
The header intentionally avoids including heavy object headers. Consumers must include definitions for `enum i915_cache_level` from object types when they need concrete enum values.

## Risks and Test Signals
The risk is API misuse: callers must hold the object lock where required by the implementation and must understand that user-managed PAT objects may be treated as immutable. Build coverage is the primary signal for declaration consistency; behavior is covered through domain/cache tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_execbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_execbuffer.c

## Purpose
`i915_gem_execbuffer.c` implements the GEM execbuffer2 ioctl, the legacy userspace GPU submission path. It validates the exec object list and ioctl flags, resolves GEM handles to VMAs in a context VM, reserves GPU virtual address space, applies relocations, optionally command-parses batches into trusted shadow buffers, builds requests and sync fences, moves objects active on the GPU, and queues requests to the selected engine or parallel engine group.

## Important Types and Structures
- `struct eb_vma` wraps each `drm_i915_gem_exec_object2` with its resolved `i915_vma`, internal pin/fence/userptr flags, relocation and bind lists, and optional handle-hash node.
- `struct eb_fence` tracks syncobj and dma-fence inputs/outputs, including timeline syncobj points and preallocated `dma_fence_chain`.
- `struct i915_execbuffer` is the transaction object for one ioctl: device/file/args, exec array, VMA wrappers, selected context/GT, request array for parallel batches, relocation cache, object lookup table, unbound/reloc lists, external fences, command-parser capture lists, batch metadata, and runtime PM wakerefs.
- Internal flags such as `__EXEC_HAS_RELOC`, `__EXEC_ENGINE_PINNED`, `__EXEC_OBJECT_HAS_PIN`, and `UPDATE` track transient state not exposed through UAPI.

## Important APIs and Functions
- `i915_gem_execbuffer2_ioctl()` is the ioctl entry: validates buffer count and global flags, copies the user exec object array, calls `i915_gem_do_execbuffer()`, and writes back updated offsets when relocations moved buffers.
- `i915_gem_do_execbuffer()` orchestrates the full transaction: initialize `i915_execbuffer`, parse extensions/fences, get in/out fences, create lookup structures, select context and engine, look up VMAs, run relocation/parse, create requests, submit, signal fences, and unwind resources.
- `eb_select_context()` and `eb_select_engine()` resolve the GEM context, engine index, parallel context constraints, GT wakerefs, VM reference, context state allocation, and wedged-GT checks.
- `eb_lookup_vma()`, `__eb_add_lut()`, and `eb_lookup_vmas()` resolve handles through context fast LUT or file object IDR, check protected-content keys, create VMAs, validate exec-object flags, register relocation lists, and initialize userptr submit state.
- `eb_validate_vmas()`, `eb_pin_vma()`, `eb_reserve()`, and `eb_reserve_vma()` lock objects under ww context, pin VMAs, reserve dma-resv fence slots, and retry binding with progressively stronger unbind/evict passes.
- Relocation helpers `eb_relocate_vma()`, `eb_relocate_parse()`, `eb_relocate_parse_slow()`, `reloc_kmap()`, `reloc_iomap()`, and `relocate_entry()` patch GPU addresses in buffers using either atomic user-copy fast path or slow copied relocation arrays.
- `eb_parse()` invokes the command parser when required, creates read-only shadow batches from GT buffer pool, handles GGTT trampoline mode, and enforces secure-batch restrictions.
- `eb_move_to_gpu()`, `eb_requests_create()`, `eb_request_submit()`, `eb_submit()`, `eb_request_add()`, and `eb_requests_add()` build request DAGs, await object and external fences, move VMAs active, emit batch-start commands, queue requests, and retire older timeline entries.
- `add_fence_array()`, `add_timeline_fence_array()`, `await_fence_array()`, `signal_fence_array()`, and `eb_fences_add()` integrate legacy and timeline syncobj fences plus optional in/out sync files.

## Control Flow
The ioctl path starts by copying the user exec object list into one allocation that also reserves space for `eb_vma` entries and command-parser scratch entries. `i915_gem_do_execbuffer()` sets `__EXEC_HAS_RELOC` unless userspace requested `NO_RELOC`, parses extension chains and syncobj arrays, imports input fences, allocates an output fence fd if needed, initializes handle lookup, and selects the context/engine.

VMA lookup resolves each handle, validates flags/alignment/pinned offsets/cache-generation restrictions, records batch objects, rejects self-modifying batches, and starts userptr submit validation. A ww lock context is then used to pin the engine/timelines and all objects. Reservation first tries to reuse current VMA placements, then binds unbound objects, then retries with reordered constraints and VM eviction when `-ENOSPC` or lock contention prevents placement.

Relocations are attempted while page faults are disabled against stack relocation batches. If user memory faults or waiting is required, the slow path releases pins/locks, prefaults or copies relocation entries, revalidates userptrs and VMA placement, then repeats relocation. Relocation writes choose CPU kmap when coherent/dirty/LLC conditions favor it, or a temporary GGTT iomap when possible, and mark objects dirty and async synchronization unsafe as needed.

After relocation, the command parser may copy the batch into a protected shadow object and replace the batch VMA. Requests are allocated in parent-to-child order and added in reverse order for timeline lock ordering. External fences are awaited on the first relevant request, object dependencies are installed, VMAs are moved active for each batch, batch-start commands are emitted, and requests are queued. The unwind path drops VMA pins/references, engine pins, context/VM refs, buffer-pool refs, fences, and output fd reservations.

## State and Persistence Behavior
This file mutates per-context handle-to-VMA LUTs and object `lut_list` entries, VMA pin/fence/open state, exec-object offsets written back to userspace, object dirty/cache state through relocation mappings, dma-resv fence reservations, request timelines, syncobj fence values, GT runtime PM wakerefs, protected-content validation state, and command-parser buffer-pool ownership. It uses internal `args->flags` bits as transaction state and clears unknown UAPI bits before returning.

## Dependencies and Integration Points
Execbuffer integrates with almost every i915 GEM subsystem: GEM object lookup and locking, userptr validation, VMA/GGTT/PPGTT binding, eviction, command parser, GT buffer pool, engine/context/timeline/request code, syncobj and sync_file APIs, PXP protected content, cache-domain helpers, clflush helpers, runtime PM, and UAPI execbuffer structs. It is the main consumer of `i915_gem_object_types.h` fields such as cache coherency, placement, frontbuffer protection, and object flags.

## Risks
- This path is security-sensitive: malformed userspace pointers, relocation arrays, protected objects, secure batches, and command parser bypasses must be rejected without use-after-free or stale mapping.
- Lock ordering is fragile. The ww retry/backoff paths, timeline locks, VM mutex, and object reservation locks must be released in the intended order to avoid deadlock.
- Relocation slow-path state is explicitly lossy: partially patched objects can exist if userspace races relocation memory protections, so offset writeback and `__EXEC_HAS_RELOC` handling are critical.
- VMA placement and eviction retries must preserve pinned/fenceable/mappable/4G constraints; mistakes can cause GPU hangs or ABI-visible wrong addresses.
- Parallel contexts require matching batch count and no explicit batch length/start offsets; command parser and secure dispatch reject unsupported combinations.
- Syncobj timeline handling must avoid waiting and signaling the same nonzero point and must transfer `dma_fence_chain` ownership correctly.

## Test Signals
Signals include IGT execbuffer relocation, no-reloc, fence-array, timeline-syncobj, context-engine, userptr, protected-content, command-parser, and parallel-submit tests. Runtime `drm_dbg()` diagnostics identify invalid flags, bad rings, relocation bounds/alignment errors, and syncobj misuse. `trace_i915_request_add/queue` and object fault traces help validate submission order and active object movement. Debug GEM builds redefine `EINVAL` to log exact failure sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_execbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.c

## Purpose
`i915_gem_internal.c` implements volatile internal GEM objects backed by directly allocated pages rather than swappable shmem. These objects are intended for private driver hardware interfaces whose contents are valid only while pinned, such as ring-like structures, and may be discarded by the shrinker after unpin.

## Important APIs and Functions
- `internal_free_pages()` frees each scatterlist segment's allocated pages, then the sg table.
- `i915_gem_object_get_pages_internal()` allocates an sg table sized to the object, attempts high-order page allocation down to single pages, applies device DMA segment limits, handles i965 DMA32 restrictions, prepares pages for GTT DMA, and installs them with `__i915_gem_object_set_pages()`.
- `i915_gem_object_put_pages_internal()` finishes GTT page mappings, frees internal pages, clears `mm.dirty`, and resets CPU write-domain tracking via `__start_cpu_write()`.
- `i915_gem_object_internal_ops` supplies the backend ops: shrinkable, internal get/put pages, and debug name.
- `__i915_gem_object_create_internal()` allocates and initializes a private GEM object with struct-page backing, volatile allocation flag, CPU read/write domains, and default cache coherency.
- `i915_gem_object_create_internal()` is the public creator using the default internal ops.

## Control Flow
Creation validates nonzero page-aligned size, checks `base.size` overflow, allocates an i915 GEM object, initializes a private DRM GEM object, sets struct-page mem flag and volatile flag, and configures initial CPU domains/cache coherency. Page population happens lazily through the backend `get_pages`: allocate sg table, fill it with decreasing page orders until all pages are covered, retry with single-page segments if DMA mapping fails for high-order segments, then attach the pages. Release reverses GTT preparation and frees all pages.

## State and Persistence
Internal objects persist only as GEM object metadata until pages are pinned. Backing storage is volatile and can be reaped; contents are not cleared on allocation and are only valid while active/pinned. The object records struct-page backing, shrinkable ops, volatile flag, `read_domains`/`write_domain`, `cache_dirty`, and `mm.dirty`.

## Dependencies and Integration Points
This file depends on scatterlist allocation, page allocator flags, i915 GTT page preparation/finish helpers, sg segment sizing, object initialization APIs, and cache-domain helpers from `i915_gem_object.h`. It is used by driver-internal consumers needing temporary GPU-addressable storage.

## Risks
- Internal allocations are not zeroed; consumers must initialize contents before hardware can observe them.
- High-order allocation fallback and DMA segment restrictions must remain correct to avoid DMA mapping failures or oversized scatterlist segments.
- Volatile objects must not be exposed to userspace as durable GEM buffers because their backing can disappear.
- Page lifecycle depends on balanced pin/get and put/free paths.

## Test Signals
Object/shrinker selftests and internal consumers that pin, unpin, and repopulate volatile buffers exercise this backend. Allocation failure paths should be covered by fault injection or low-memory stress. Assertions validate size alignment and object-size overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.h

## Purpose
`i915_gem_internal.h` declares the constructors for driver-private internal GEM objects. It lets other i915 subsystems allocate volatile page-backed objects without exposing the backend implementation details.

## Important APIs and Types
- Forward declarations for `drm_i915_private`, `drm_i915_gem_object`, and `drm_i915_gem_object_ops`.
- `i915_gem_object_create_internal(i915, size)` creates an internal object with default internal ops.
- `__i915_gem_object_create_internal(i915, ops, size)` creates an internal object with caller-supplied object ops.

## Control Flow and State
The header has no logic or state. The implementation validates size, initializes private GEM metadata, sets volatile/struct-page state, and uses backend ops for page allocation.

## Dependencies and Integration
It includes only `<linux/types.h>` for `phys_addr_t`. Consumers supply the full i915 device and use returned objects through normal GEM object APIs.

## Risks and Test Signals
The leading-underscore constructor permits custom ops; callers must preserve internal-object invariants such as volatile page-backed storage and correct get/put pages. Build coverage and internal-object allocation tests cover the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ioctls.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ioctls.h

## Purpose
`i915_gem_ioctls.h` centralizes prototypes for i915 GEM ioctl handlers. It is a declaration-only integration header used by the DRM ioctl table and by implementation files that need cross-file ioctl entry points.

## Important APIs
Declared ioctl handlers include busy, create/create_ext, execbuffer2, aperture query, caching get/set, tiling get/set, madvise, mmap/mmap_offset, pread/pwrite, set_domain, sw_finish, throttle, userptr, and wait. All share the DRM ioctl shape `int handler(struct drm_device *dev, void *data, struct drm_file *file)`.

## Control Flow and Integration
The header contains no runtime control flow. It binds UAPI entry points to implementations spread across GEM files. In this subset, `i915_gem_execbuffer2_ioctl()` is implemented in `i915_gem_execbuffer.c`, caching and set-domain ioctls in `i915_gem_domain.c`, and mmap ioctls in `i915_gem_mman.c`.

## State and Persistence
No state is stored here. The declared handlers mutate GEM objects, file-private handle tables, VM mappings, request timelines, and object memory state in their respective implementations.

## Dependencies
Only `struct drm_device` and `struct drm_file` are forward-declared, keeping the header independent of full DRM/i915 definitions.

## Risks and Test Signals
The primary risk is declaration drift from implementations or ioctl table users. Build coverage catches signature mismatches; functional ioctl behavior is covered by IGT GEM tests and i915 selftests in the implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.c

## Purpose
`i915_gem_lmem.c` provides helpers for GEM objects resident in local memory (LMEM), including WC iomapping of contiguous LMEM pages and constructors for LMEM-backed objects.

## Important APIs and Functions
- `i915_gem_object_lmem_io_map(obj, n, size)` maps a contiguous LMEM object page range through the memory region's `io_mapping` using the object's DMA address adjusted by the region start.
- `i915_gem_object_is_lmem(obj)` reports whether an object is resident in a local-memory region, with lockdep asserting object lock for migratable/evictable objects where residency can change.
- `__i915_gem_object_create_lmem_with_ps(i915, size, page_size, flags)` creates an LMEM object with an explicit minimum page size via `i915_gem_object_create_region()`.
- `i915_gem_object_create_lmem(i915, size, flags)` creates an LMEM object in `INTEL_REGION_LMEM_0`.
- `i915_gem_object_create_lmem_from_data(i915, data, size)` creates a contiguous page-rounded LMEM object, maps it WC, copies initial data, flushes the mapping, releases the map, and returns the object.

## Control Flow
Creation helpers delegate to the region allocator for `i915->mm.regions[INTEL_REGION_LMEM_0]`. The data-loading helper creates a contiguous object, pins a WC kernel map without requiring the caller to hold the object lock, copies bytes, flushes the full map, releases the map, and drops the object on failure. The iomap helper requires contiguous backing and computes the region-relative offset from DMA address.

## State and Persistence
LMEM object residency is tracked in `obj->mm.region` and backing memory-region metadata. `create_lmem_from_data()` persists caller data into device-local memory and flushes CPU writes before returning. The explicit page-size variant affects the object's memory allocation granularity and final rounded GEM object size.

## Dependencies and Integration Points
This file depends on `intel_memory_region`, `i915_gem_region`, object DMA-address lookup, object map/flush APIs, and region indices. Display scanout preparation in `i915_gem_domain.c` relies on LMEM residency checks on LMEM-capable platforms.

## Risks
- `i915_gem_object_lmem_io_map()` assumes contiguous objects; violating that trips `GEM_BUG_ON` or maps wrong memory.
- Forcing a page size smaller than region minimum can make an object unusable for GTT insertion, as documented by the implementation.
- Data-copy construction must flush WC writes; missing this can leave device-visible stale data.
- Residency checks on migratable objects require object locking or pinning.

## Test Signals
LMEM allocation, migration, and object placement tests should exercise these helpers. Display/framebuffer tests catch LMEM residency requirements. Assertions cover contiguous iomap preconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.h

## Purpose
`i915_gem_lmem.h` declares public LMEM GEM helpers for residency checks, WC IO mapping, and LMEM object creation.

## Important APIs
- `i915_gem_object_lmem_io_map()` maps a contiguous LMEM object range.
- `i915_gem_object_is_lmem()` checks current or guaranteed local-memory residency.
- `i915_gem_object_create_lmem_from_data()` creates an LMEM object initialized from CPU data.
- `__i915_gem_object_create_lmem_with_ps()` creates LMEM with explicit page-size constraints.
- `i915_gem_object_create_lmem()` creates a normal LMEM object with flags.

## Control Flow and State
The header contains no logic. The implementation delegates object creation to memory-region allocation and records residency in object memory-region fields.

## Dependencies and Integration
It forward-declares the i915 device, GEM object, and memory region and includes `<linux/types.h>` for size/resource types. Users include it where they need LMEM-specific object behavior, notably display, region, and setup paths.

## Risks and Test Signals
The API exposes residency-sensitive helpers; callers must observe locking rules for migratable objects and contiguous requirements for IO maps. Build coverage catches declaration drift; LMEM/migration/display tests cover behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.c

## Purpose
`i915_gem_mman.c` implements i915 GEM mmap support: the legacy CPU mmap ioctl, modern fake-offset mmap-offset ioctl, GTT and CPU fault handlers, mmap-offset lifetime/revocation, dumb-buffer offsets, framebuffer mmap, and the DRM file mmap entry point.

## Important APIs and Functions
- `i915_gem_mmap_ioctl()` performs the legacy hidden `vm_mmap()` on the object's shmem file, optionally converting the VMA to write-combine, and is disabled on dGPU and graphics versions newer than 12.0.
- `i915_gem_mmap_gtt_version()` returns interface version 5, documenting partial mmap and multi-fault-handler support.
- `compute_partial_view()` computes tiled-aware partial GGTT views for faulting large objects through limited mappable aperture space.
- `vm_fault_cpu()` pins object pages and remaps struct-page or iomem scatterlist backing into the user VMA with `remap_io_sg()`.
- `vm_fault_gtt()` handles GTT mmap faults by taking runtime PM, ww-locking the object, pinning pages, binding a mappable GGTT VMA or partial view, pinning fences, remapping GGTT PFNs into userspace, marking userfault state, and recording writes.
- `vm_access()` implements debugger-style read/write access through a forced WC kernel map.
- `i915_gem_object_release_mmap_gtt()`, `__i915_gem_object_release_mmap_gtt()`, `i915_gem_object_runtime_pm_release_mmap_offset()`, and `i915_gem_object_release_mmap_offset()` revoke user mappings for GGTT, runtime PM suspend, and non-GTT mmap offsets.
- `lookup_mmo()`, `insert_mmo()`, `mmap_offset_attach()`, `__assign_mmap_offset()`, and `__assign_mmap_offset_handle()` manage one `i915_mmap_offset` per object and mmap type in an RB tree and DRM VMA offset manager.
- `i915_gem_mmap_offset_ioctl()` validates UAPI flags and returns fake mmap offsets for GTT/WC/WB/UC/FIXED modes.
- `i915_gem_mmap()` resolves a VMA offset to either an `i915_mmap_offset` or object-owned mmap node and installs i915 VMA operations.
- `i915_gem_fb_mmap()` maps framebuffer objects, handling TTM/fixed-offset objects and stolen/shmem objects differently.

## Control Flow
Modern mmap starts with `i915_gem_mmap_offset_ioctl()`, which validates extensions and flags, looks up and locks the object, creates or reuses an `i915_mmap_offset`, grants the calling DRM file one-shot access, and returns a fake offset. The actual `mmap()` enters `i915_gem_mmap()`, looks up the offset under the DRM VMA manager with RCU-safe object ref acquisition, then `i915_gem_object_mmap()` swaps in an anonymous singleton file, sets PFNMAP/IO flags, applies readonly restrictions, selects CPU or GTT vm_ops, and configures page protections.

CPU faults lock and pin pages, compute the object offset from the fake node start, and remap the scatterlist backing. GTT faults compute page offset, take runtime PM, ww-lock and pin pages, bind a mappable or partial GGTT VMA with eviction fallback, reject incoherent snoopable access, pin fence registers, calculate virtual address/PFN limits, remap the GGTT aperture, mark the VMA/object as userfault tracked, and set write/dirty state. Revocation paths remove CPU PTEs while holding the GGTT VM mutex and runtime PM wakeref so future user access faults back through the handler.

## State and Persistence
The file persists mmap offset nodes in `obj->mmo.offsets`, grants file-specific VMA-node access, uses `obj->userfault_count` and `userfault_link` to track active GGTT user mappings, records `vma->mmo`, marks `obj->mm.dirty` on writes, changes `vma->vm_page_prot`, and may hold an i915-wide mmap singleton file. Runtime suspend clears userfault state and unmaps TTM vma nodes.

## Dependencies and Integration Points
It integrates with DRM VMA offset manager, Linux mm fault APIs, anon inodes, runtime PM, GGTT/eviction/fence helpers, object pin/map APIs, TTM mmap hooks, user extensions, and framebuffer mmap users. It is tightly coupled to `i915_gem_object_types.h` fields `mmo`, `userfault_count`, `userfault_link`, `mem_flags`, and object ops `mmap_offset`/`mmap_ops`.

## Risks
- Incorrect fake-offset lookup or VMA-node lifetime can cause stale object access or missing access control.
- GTT mmap faults require runtime PM and GGTT mutex serialization; missing either can race suspend or GGTT PTE updates.
- GTT mappings of snoopable/non-LLC objects are rejected because they can corrupt or hang hardware.
- Userfault revocation must reliably zap CPU PTEs when fences are lost, objects are evicted, or runtime suspend occurs.
- Readonly objects must clear write permissions in the VMA and reject write faults/access.
- Partial view arithmetic for tiled objects must preserve tile-row alignment.

## Test Signals
The file includes `selftests/i915_gem_mman.c` under `CONFIG_DRM_I915_SELFTEST`. External signals include IGT mmap-offset, GTT mmap, WC/WB/UC mmap, suspend/resume mmap revocation, framebuffer mmap, and fault-injection tests. `trace_i915_gem_object_fault()` records fault behavior, while `GEM_BUG_ON` assertions cover userfault and mmap node invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.h

## Purpose
`i915_gem_mman.h` declares GEM mmap entry points and mmap-offset cleanup helpers used across i915 and DRM framebuffer paths.

## Important APIs
- `i915_gem_mmap_gtt_version()` reports GTT mmap ABI feature level.
- `i915_gem_mmap(struct file *filp, struct vm_area_struct *vma)` is the DRM file mmap hook.
- `i915_gem_dumb_mmap_offset()` supplies dumb-buffer mmap offsets.
- `__i915_gem_object_release_mmap_gtt()` and `i915_gem_object_release_mmap_gtt()` revoke GTT user mappings.
- `i915_gem_object_runtime_pm_release_mmap_offset()` and `i915_gem_object_release_mmap_offset()` revoke/clean mmap offsets during runtime PM or object teardown.
- `i915_gem_fb_mmap()` handles framebuffer object mmap setup.

## Control Flow and State
The header has no logic. The implementation manages object `mmo` RB trees, userfault accounting, DRM VMA offsets, VMA operations, and runtime-PM-safe revocation.

## Dependencies and Integration
It includes Linux `mm_types` and type definitions and forward-declares DRM/file/object structs. It is used by DRM driver mmap setup, framebuffer mapping code, object free paths, runtime suspend, and ioctl implementations.

## Risks and Test Signals
Callers must choose the right revocation helper based on lock/runtime-PM context. Misusing internal `__` revocation without required locks can race user faults. Build coverage and `i915_gem_mman.c` selftests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.c

## Purpose
`i915_gem_object.c` implements core i915 GEM object allocation, initialization, cache coherency setup, close/free behavior, mmap cleanup, page/VMA teardown, object read helpers, migration/placement predicates, DRM GEM callbacks, and module-level object slab setup.

## Important APIs and Functions
- `i915_gem_get_pat_index()` maps legacy cache-level enum values to platform PAT indices; `i915_gem_object_has_cache_level()` treats user-set PAT objects as kernel-immutable and otherwise compares PAT translation.
- `i915_gem_object_alloc()`/`free()` allocate from a dedicated slab and install `i915_gem_object_funcs`.
- `i915_gem_object_init()` initializes VMA lists/trees, LUT and mmap locks, RCU head, object ops, flags, madv state, and page-lookup radix caches.
- `__i915_gem_object_fini()` tears down page-iterator locks and reservation object.
- `i915_gem_object_set_cache_coherency()` and `_set_pat_index()` update PAT index, `cache_coherent`, and initial `cache_dirty` based on cache level/PAT and platform LLC/dGPU behavior.
- `i915_gem_object_can_bypass_llc()` identifies userspace objects that require heavy initial flushing because GPU MOCS can bypass LLC or userspace set PAT.
- `i915_gem_close_object()` removes per-context handle-to-VMA LUT entries and revokes mmap node access for a closing DRM file.
- `__i915_gem_object_pages_fini()` destroys all VMAs, frees mmap offsets, resets page pin count, and drops pages, with special handling for imported dma-bufs.
- `i915_gem_free_object()` is the DRM free callback; it removes client accounting and defers heavy free work through RCU and the driver workqueue.
- `i915_gem_object_read_from_page()` reads one page-bounded chunk from struct-page or mappable iomem backing.
- `i915_gem_object_evictable()`, `_migratable()`, `_can_migrate()`, `_migrate()`, `_placement_possible()`, and `_needs_ccs_pages()` answer placement and migration questions and delegate backend migration.
- DRM GEM funcs provide close, free, PRIME export, vmap, and vunmap behavior.
- Moving-fence helpers expose and wait for async migration/clear fences and unknown-state detection.

## Control Flow
Initialization builds the in-memory object scaffolding but leaves backend pages to object ops. Cache coherency helpers set PAT/cache flags before pages are used. On handle close, the object scans `lut_list` for entries owned by the closing file, carefully drops and reacquires the lock for long lists, revokes mmap access, removes context radix-tree mappings, closes VMAs, and drops object/LUT references.

Freeing is intentionally deferred. The DRM callback rejects freeing active frontbuffers, removes client accounting, increments a free counter, and queues the object on an llist for workqueue processing after RCU readers finish. The worker finalizes pages and VMAs, frees mmap offsets, calls backend release, drops shared VM reservations/import resources, then uses `call_rcu()` to free the slab object while preserving RCU-safe lookups.

Migration helpers require object lock and `I915_MADV_WILLNEED`, check region availability, alignment, evictability, backend support, and user placement constraints, then call backend `ops->migrate()`. Read helpers require pinned pages and choose kmap or WC iomap depending on backing type.

## State and Persistence
This file owns persistent object setup for `vma`, `lut_list`, `mmo`, `mm` page caches, flags, `pat_index`, `cache_coherent`, `cache_dirty`, placement arrays, free-list links, and DRM GEM callbacks. It mutates per-file/context LUTs, mmap offsets, VMA lists, page pin counts, object `mm.region`, dirty state, and moving-fence/unknown-state observation. Delayed free state is stored in `i915->mm.free_list`, `free_count`, and `free_work`.

## Dependencies and Integration Points
It integrates with DRM GEM core, PRIME dma-buf, i915 context LUTs, VMA management, mmap helpers, TTM object conversion, memory regions, PXP protected state, frontbuffer tracking, cache flushing, client accounting, RCU/workqueues, and selftests. Headers `i915_gem_object.h` and `i915_gem_object_types.h` expose much of this state to domain, mmap, execbuffer, and backend files.

## Risks
- RCU and deferred-free ordering is critical; object memory must remain alive for RCU handle/fdinfo readers while heavy teardown runs in process context.
- `lut_list` close handling must synchronize with context closure and handle reuse to avoid stale VMA fast-lookups.
- Cache coherency/PAT helpers interact with security guarantees around zeroed userspace memory and LLC bypass.
- Page/VMA teardown must not run while frontbuffer or pinned state remains active.
- Migration predicates are advisory when object is unlocked; callers relying on them must hold the object lock or pin pages.
- `i915_gem_object_wait_moving_fence()` contains a direct reservation wait and unknown-state check; callers must respect object lock and fence semantics.

## Test Signals
The file includes selftests for huge GEM objects, huge pages, migration, object behavior, and coherency under `CONFIG_DRM_I915_SELFTEST`. IGT object lifecycle, mmap, migration, PRIME import/export, and coherency suites exercise the external behavior. Tracepoints record object destruction, and many `GEM_BUG_ON` checks assert VMA/list/page invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.h

## Purpose
`i915_gem_object.h` is the main API surface for i915 GEM object users. It exposes object allocation/init, lookup/refcounting, reservation locking, tiling, page pinning and page lookup, kernel mapping, domain preparation, cache coherency, display flush, shrinker/madvise state, waits, migration, placement, shmem helpers, and userptr hooks.

## Important APIs and Types
- Object lookup/ref helpers: `i915_gem_object_lookup_rcu()`, `_get_rcu()`, `_lookup()`, `_get()`, and `_put()` wrap DRM IDR and refcount handling.
- Locking helpers: `i915_gem_object_lock()`, `_lock_interruptible()`, `_trylock()`, `_unlock()`, and assertion helpers use `dma_resv`/ww locking and track objects in `i915_gem_ww_ctx`.
- Flag/type helpers expose readonly, contiguous, volatile, protected, shrinkable, proxy, no-mmap, framebuffer, struct-page, and iomem predicates.
- Tiling helpers expose tiling mode, stride, tile height, tile-row size, and `i915_gem_object_set_tiling()`.
- Page-iterator APIs map page offsets to scatterlist entries, `struct page`, dirty pages, and DMA addresses with static type checks around `pgoff_t`.
- Page lifecycle APIs include `__i915_gem_object_set_pages()`, `i915_gem_object_pin_pages()`, `_pin_pages_unlocked()`, `_unpin_pages()`, `__i915_gem_object_put_pages()`, and `truncate()`.
- Kernel map APIs include `i915_gem_object_pin_map()`, `_pin_map_unlocked()`, `__i915_gem_object_flush_map()`, `i915_gem_object_unpin_map()`, and release-map.
- Domain/cache APIs include prepare read/write, finish access, cache coherency/PAT setters, display flush helpers, and domain transition helpers.
- Migration and placement APIs expose migrate, can-migrate, wait-migration, placement possible, and CCS aux-page requirements.
- Userptr APIs are real only under `CONFIG_MMU_NOTIFIER`; otherwise stubs assert and return `-ENODEV`.

## Control Flow
Most functions here are declarations or thin inline wrappers. The locking inline is important: it takes the object's dma-resv lock using an optional ww context, adds successfully locked objects to the ww object list, and records contended objects on `-EDEADLK`. Pinning increments `pages_pin_count` if pages are already present or calls `__i915_gem_object_get_pages()` to populate them. Unpinning decrements the pin count after invariant checks. `__start_cpu_write()` updates CPU domains and marks `cache_dirty` when CPU writes require clflush.

## State and Persistence
The header defines how callers mutate object persistent fields: `flags`, `tiling_and_stride`, `mm.pages_pin_count`, `read_domains`, `write_domain`, `cache_dirty`, `mm.dirty`, shrinker pins, and placement/migration state. It also documents caller responsibilities: many helpers require the object reservation lock or pinned pages.

## Dependencies and Integration Points
This header includes DRM GEM/file/device, i915 memory-region, GTT, ww locking, VMA types, and object type definitions. It is included by most GEM implementation files and by GT/display code that works with GEM objects.

## Risks
- The inline lock helpers hold object references while ww contexts track locked objects; misuse can leak references or deadlock.
- Page iterator macros enforce offset type safety; bypassing them risks truncation on large objects.
- `i915_gem_object_has_struct_page()`/`has_iomem()` require locking or pinned pages because backing can change through migration.
- Userptr stubs intentionally `GEM_BUG_ON` when CONFIG support is absent; callers must gate use correctly.
- Domain helpers return with pages pinned for prepare-read/write and require `i915_gem_object_finish_access()`.

## Test Signals
Build coverage is substantial because nearly every GEM file includes this header. Runtime behavior is covered by object, migration, mmap, domain, userptr, and execbuffer tests. Inline assertions catch missing pages, unbalanced unpins, bad tiling, and incorrect userptr configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.c

## Purpose
`i915_gem_object_frontbuffer.c` bridges GEM objects to display frontbuffer tracking. It creates and references `i915_frontbuffer` wrappers, attaches them to GEM objects via RCU, tracks GPU writes through `i915_active`, forwards invalidate/flush calls to display code, and exports the display frontbuffer interface.

## Important APIs and Functions
- `i915_gem_object_frontbuffer_get()` looks up or allocates a frontbuffer for an object, initializes `intel_frontbuffer` and `i915_active`, attaches it under `i915->frontbuffer_lock`, and handles racing creators.
- `i915_gem_object_frontbuffer_ref()` and `_put()` manage kref lifetime; final put clears scanout and the object RCU pointer, finalizes active/display state, drops the object ref, and frees via RCU.
- `frontbuffer_active()` and `frontbuffer_retire()` integrate `i915_active` with frontbuffer refs, flushing display state from GPU/CS origin when writes retire.
- `__i915_gem_object_frontbuffer_flush()` and `_invalidate()` perform RCU-safe lookup and call `intel_frontbuffer_flush()`/`invalidate()`.
- Display-interface callbacks `i915_frontbuffer_get/ref/put/flush_for_display()` adapt DRM/display calls to GEM-frontbuffer objects.
- `i915_display_frontbuffer_interface` is the exported callback table.

## Control Flow
Lookup first tries the RCU/kref-safe inline helper. If absent, allocation initializes the display base, object ref, kref, and active tracker. The global frontbuffer lock serializes installation; if another frontbuffer appeared, the new allocation is discarded and the existing one is returned with an added ref. Put uses `kref_put_lock()` so release runs with `frontbuffer_lock` held, clears the object's RCU pointer, unlocks, then finalizes active state and object/display references.

Flush and invalidate are fast-pathed by inline checks in the header; the out-of-line helpers only run when a frontbuffer pointer exists and then safely acquire a temporary kref.

## State and Persistence
The persistent state is `obj->frontbuffer`, an RCU pointer to `struct i915_frontbuffer`, plus `front->ref`, `front->write` active tracking, and display frontbuffer bits managed in display code. Creation pins the GEM object by reference until release. Release also calls `i915_ggtt_clear_scanout(obj)` to clear scanout markings.

## Dependencies and Integration Points
This file depends on display frontbuffer APIs, `intel_display_frontbuffer_interface`, `i915_active`, object refs, RCU, kref, the i915 global `frontbuffer_lock`, and display/domain flush helpers. Domain transitions and CPU writes call invalidate/flush helpers; display code calls through the exported interface.

## Risks
- RCU/kref lookup must avoid returning a frontbuffer after final release begins; the inline lookup loop handles this with `kref_get_unless_zero`.
- Release ordering must clear the object pointer under lock before freeing via RCU.
- Missing frontbuffer invalidation on CPU/GPU writes can break display coherency, FBC/PSR, or scanout updates.
- `i915_active` callbacks intentionally hold refs across active GPU writes; imbalance would leak frontbuffers or prematurely free them.

## Test Signals
Display frontbuffer, PSR/FBC, pageflip, and scanout coherency tests exercise this bridge. Object/domain tests that write framebuffer objects should trigger invalidate/flush. RCU/kref bugs would show as use-after-free or refcount leaks under concurrency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.h

## Purpose
`i915_gem_object_frontbuffer.h` defines the GEM-side frontbuffer wrapper and inline helpers for fast flush/invalidate and safe RCU lookup. It also declares the display frontbuffer interface exported by the implementation.

## Important APIs and Types
- `struct i915_frontbuffer` embeds `struct intel_frontbuffer`, points back to the GEM object, tracks GPU writes with `struct i915_active`, and uses RCU plus kref for lifetime.
- `i915_gem_object_frontbuffer_flush()` and `_invalidate()` inline-check `obj->frontbuffer` and call out-of-line helpers only when needed.
- `i915_gem_object_frontbuffer_get/ref/put()` manage frontbuffer lifetime.
- `i915_gem_object_frontbuffer_track()` adapts GEM frontbuffers to `intel_frontbuffer_track()`.
- `i915_gem_object_frontbuffer_lookup()` performs RCU-safe lookup with `kref_get_unless_zero()` and retries if the object pointer changes.
- `i915_display_frontbuffer_interface` exposes callbacks for display code.

## Control Flow
The lookup helper exits quickly when no frontbuffer is present. Otherwise it enters an RCU read-side critical section, dereferences the pointer, tries to take a kref, verifies the pointer still matches the object, and drops/retries on races. Inline flush/invalidate helpers avoid the overhead of this lookup for the common non-framebuffer object case.

## State and Persistence
The header defines the object-frontbuffer relation and lifetime fields but stores no global state. It documents that the object's `frontbuffer` pointer is RCU-protected and that refs must be taken before use outside the RCU section.

## Dependencies and Integration
It includes display frontbuffer definitions and object types, so it is a bridge header between GEM and display. Domain, object, and display files use it to coordinate scanout coherency.

## Risks and Test Signals
The main risks are RCU misuse and refcount imbalance. Tests that rapidly create/destroy framebuffers while CPU/GPU writes occur can expose races. Build coverage catches interface drift with display callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_frontbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_types.h

## Purpose
`i915_gem_object_types.h` defines the central data model for i915 GEM objects: backend operation hooks, cache-level and mmap enums, mmap offset nodes, page-iterator caches, the `drm_i915_gem_object` layout, allocation/placement flags, cache coherency state, tiling, page backing, migration placement, TTM/LMEM metadata, userptr/stolen/proxy unions, and helper conversion macros.

## Important Types and Fields
- `struct i915_lut_handle` links object handles to context VMA lookup tables for execbuffer fast lookup and close cleanup.
- `struct drm_i915_gem_object_ops` is the backend interface: get/put/truncate/shrink pages, pread/pwrite, mmap offset/ops, virtual unmap, dma-buf export, LRU adjustment, delayed free, migration, release, and debug name. Flags identify shrinkable, self-managed shrink list, proxy, and no-mmap objects.
- `enum i915_cache_level` describes legacy cache policy values: NONE, LLC, L3_LLC, WT, and max marker; these are translated to PAT indices.
- `enum i915_map_type` and `enum i915_mmap_type` define kernel map and userspace mmap cache modes.
- `struct i915_mmap_offset` stores a DRM VMA offset node, object pointer, mmap type, and RB-tree node.
- `struct i915_gem_object_page_iter` caches scatterlist lookup positions in a radix tree protected by a mutex.
- `struct drm_i915_gem_object` embeds/aliases DRM GEM and TTM BO storage, object ops, VMA list/tree, context LUT list, ww object-link, shared reservation VM, procfs client links, RCU/free nodes, userfault tracking, mmap-offset RB tree, allocation flags, memory flags, PAT/cache coherency fields, domain fields, frontbuffer pointer, tiling/stride, page/memory-region state, TTM metadata, PXP key instance, bit17 swizzle data, and backend-specific unions.

## Control Flow and Semantics
The file is declarative but heavily documents runtime contracts. Backend ops define how pages are acquired, released, shrunk, migrated, mapped, exported, and finally released. VMA lists are ordered with GGTT VMAs at the head and ppGTT VMAs at the tail while the RB tree supports exact lookup. Context LUT handles allow object close to remove fast VMA mappings from associated contexts.

Cache-state comments describe how `pat_index`, `pat_set_by_user`, `cache_coherent`, and `cache_dirty` interact. User PAT objects are managed by userspace, limiting kernel assumptions. Non-LLC platforms and LLC-bypass-capable platforms require careful initial flushing to avoid stale memory disclosure. `read_domains` and `write_domain` track cache/domain ownership for transitions in `i915_gem_domain.c`.

The `mm` substructure models page lifecycle and placement: pin counts, shrink pins, unknown migration/clear state, placement priority list, current region/resource, scatter-gather pages, page-size metadata, page iterators, shrinker links, madvise, dirty flag, and GT TLB generation. TTM state holds cached IO sg tables and backup objects.

## State and Persistence
This header defines nearly all persistent state carried by GEM objects across ioctls, mmap faults, execbuffer submissions, migration, suspend/resume, and display use. Fields such as `flags`, `mem_flags`, `pat_index`, `cache_dirty`, domain fields, `frontbuffer`, `tiling_and_stride`, `mm.pages`, `mm.region`, `mm.madv`, `mm.dirty`, `userfault_count`, and `mmo.offsets` are mutated by the implementation files in this subset.

## Dependencies and Integration Points
It depends on Linux mmu notifier types, DRM GEM/TTM types, i915 active/selftest/VMA resource definitions, UAPI `i915_drm.h`, and GT defines. It is included by core object, domain, mmap, execbuffer, LMEM, internal, frontbuffer, and many other i915 files.

## Risks
- The object embeds both DRM GEM and TTM BO representations; code must use accessors and preserve aliasing assumptions.
- Many fields are lock-protected by different locks: object reservation, `vma.lock`, `lut_lock`, `mmo.lock`, region locks, shrinker locks, RCU, and page-iterator mutexes. Misidentifying the lock leads to races.
- `cache_dirty` and coherency flags are security-sensitive for userspace memory zeroing and GPU cache bypass.
- `mem_flags` can change with migration; callers must hold object lock or pin pages before checking backing type.
- `unknown_state` indicates pages must not be exposed to CPU or GPU after failed async migration/clear.
- Allocation flags mix immutable object creation properties and later behavior such as PM volatility, GPU-only placement hints, CCS aux pages, readonly/protected state, and tiling quirks.

## Test Signals
Selftest-only fields (`st_link`, `page_mask`) and included object/migration/coherency selftests validate many invariants. IGT coverage for mmap, execbuffer, migration, userptr, PRIME, tiling, and display scanout exercises fields defined here. Static/build checks catch structure layout assumptions such as `to_intel_bo(NULL) == NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_types.h -->
