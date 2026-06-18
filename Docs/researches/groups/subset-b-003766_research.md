# subset-b-003766 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.c

## Purpose
Implements the vmwgfx-local TTM object and reference-object layer used to expose kernel graphics resources as per-file user handles. It owns the per-device IDR namespace for `ttm_base_object` handles, per-open-file reference tracking, close-time cleanup, and the PRIME dma-buf export/import-by-fd path for shareable objects.

## Important APIs, Types, And Functions
- `struct ttm_object_file` stores the caller's `tdev`, a spinlock, a close-time `ref_list`, an RCU hash table keyed by base-object handle, and a kref.
- `struct ttm_object_device` stores the global object IDR and a wrapped copy of driver dma-buf ops.
- `struct ttm_ref_object` is a per-file counted reference to a `ttm_base_object`.
- `ttm_base_object_init()`, `ttm_base_object_lookup()`, `ttm_base_object_lookup_for_ref()`, and `ttm_base_object_unref()` manage global handles and object lifetime.
- `ttm_ref_object_add()` and `ttm_ref_object_base_unref()` create and drop per-file references.
- `ttm_prime_fd_to_handle()`, `ttm_prime_handle_to_fd()`, and `ttm_prime_object_init()` bridge TTM objects and dma-buf fds.

## Control Flow
Object creation initializes the base fields, allocates a global IDR handle above the MOB handle range, adds a per-file reference, then drops the creator's temporary base reference so lifetime is held by file references and dma-buf exports. Lookup from a file first checks the file hash, then uses `kref_get_unless_zero()` under the file lock. Lookup for fd import uses the device IDR under RCU and also uses `kref_get_unless_zero()`. File release repeatedly removes the first reference object because releasing one drops and reacquires the file lock.

PRIME export looks up a handle, verifies it is a shareable `ttm_prime_type`, serializes on `prime->mutex`, reuses an existing dma-buf when its file ref can be acquired, or exports a new dma-buf whose release wrapper clears `prime->dma_buf` and drops the base reference. PRIME fd-to-handle only supports dma-bufs exported by this exact `tdev->ops` instance.

## State, Persistence, And Dependencies
State is in-memory: per-device IDR, per-file hash/list, object krefs, and non-refcounted `prime->dma_buf` protected by a mutex. There is no persistent storage. The code depends on Linux IDR, RCU hash traversal, spinlocks, krefs, dma-buf, file refcounts, and vmwgfx constants such as `VMWGFX_NUM_MOB` and `VMW_RES_SURFACE`.

## Integration Points
Used by vmwgfx user resources such as contexts and surfaces that embed `ttm_base_object` or `ttm_prime_object`. File-private state comes from `vmw_fpriv(file)->tfile`. GEM handle code coexists with this object namespace by reserving object IDs above `VMWGFX_NUM_MOB`.

## Risks And Test Signals
Key risks are lifetime races between IDR lookup, file-close reference teardown, and dma-buf release; permission mistakes around non-shareable objects; and leaks if the driver's object-specific release does not RCU-free the embedding object. Test signals include repeated create/lookup/unref on one file, close-time cleanup with duplicate refs, cross-file access denial for non-shareable objects, PRIME fd round trips, dma-buf fd reuse after close, and module unload warning if the IDR is not empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.h

## Purpose
Declares the public object-management contract implemented by `ttm_object.c`. It defines the base object layout embedded by vmwgfx user-visible resources, the PRIME-aware wrapper object, and the APIs used by file open/release, resource creation/destruction, handle lookup, and dma-buf conversion.

## Important APIs, Types, And Functions
- `enum ttm_object_type` reserves generic TTM object kinds and driver-private ranges; vmwgfx uses driver type values such as `VMW_RES_CONTEXT` and `VMW_RES_SURFACE`.
- `struct ttm_base_object` contains RCU head, owner `ttm_object_file`, kref, release callback, numeric handle, object type, and shareability flag.
- `struct ttm_prime_object` embeds `ttm_base_object`, adds a mutex, exported size, real underlying type, cached dma-buf pointer, and underlying release callback.
- API declarations cover base initialization, lookup, unref, per-file reference add/drop, object-file/device init/release, and PRIME fd/handle conversion.
- Helper macros `ttm_base_object_kfree()` and `ttm_prime_object_kfree()` encode the expected RCU-free pattern.
- `ttm_base_object_type()` hides the internal `ttm_prime_type` wrapper and returns the real resource type.
- Inline `ttm_bo_wait()` adapts older call sites to `ttm_bo_wait_ctx()`.

## Control Flow
Callers allocate an embedding object, initialize resource-specific fields, then call `ttm_base_object_init()` or `ttm_prime_object_init()`. The release callback is called only after the object is removed from the device namespace and all file/dma-buf references are gone. Consumers must lookup with the correct file or device object and drop acquired refs with `ttm_base_object_unref()`.

## State, Persistence, And Dependencies
This header only describes in-memory state. It depends on `linux/dma-buf.h`, `kref`, `list`, `rcupdate`, and TTM buffer-object types. The comments document an RCU lifetime model: object release removes global visibility first, then embedding objects must be freed after an RCU grace period.

## Integration Points
Included by vmwgfx context, surface, and file-private code that needs handle-backed user resources. It also connects to TTM BO waiting and Linux dma-buf PRIME export support.

## Risks And Test Signals
The main risks are misuse of release callbacks, freeing without RCU, type confusion when `ttm_prime_type` wraps the real type, and incorrect shareability flags. Test signals should verify type reporting through `ttm_base_object_type()`, correct NULLing behavior of unref APIs, and resource-specific release callbacks under close, explicit destroy ioctl, and dma-buf export lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmw_surface_cache.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmw_surface_cache.h

## Purpose
Provides inline geometry, size, offset, and dirty-tracking helpers for SVGA3D surface formats. It converts user-visible surface dimensions into block-aligned byte layouts, mip-chain offsets, screen-target format predicates, and offset-to-subresource locations used by dirty tracking and CPU blit/update paths.

## Important APIs, Types, And Functions
- `clamped_umul32()` saturates 32-bit multiplication to avoid wraparound.
- `vmw_surface_get_desc()`, `vmw_surface_get_mip_size()`, and `vmw_surface_get_size_in_blocks()` derive descriptor and block dimensions.
- `vmw_surface_get_image_buffer_size()`, `vmw_surface_get_serialized_size()`, and `_extended()` compute backing-store sizes.
- `vmw_surface_get_pixel_offset()` and `vmw_surface_get_image_offset()` map coordinates, faces, and mips to byte offsets.
- `vmw_surface_is_*_screen_target_format()` gates legacy GB and DX screen target formats.
- `struct vmw_surface_cache`, `struct vmw_surface_mip`, and `struct vmw_surface_loc` cache per-mip layout and offset-derived locations.
- `vmw_surface_setup_cache()`, `vmw_surface_get_loc()`, `vmw_surface_inc_loc()`, `vmw_surface_min_loc()`, and `vmw_surface_max_loc()` support dirty-region computation.

## Control Flow
Callers set up a cache from base dimensions, format, mip levels, layers, and sample count. The cache precomputes mip sizes, bytes, row stride, image stride, total mip-chain bytes, and sheet bytes. Offset-to-location walks sheet, layer, mip, z, y, and x in that order. Increment/min/max helpers produce SVGA box-compatible ranges for touched subresources.

## State, Persistence, And Dependencies
All state is caller-owned stack or embedded cache data. There is no persistence or locking. The header depends on SVGA surface descriptors from `device_include/svga3d_surfacedefs.h` and DRM vmwgfx UAPI sizes.

## Integration Points
Used by surface validation, dirty tracking, and copy/update code that must reason about compressed, planar, multisample, mipmapped, cubemap, and array layouts. It also supplies format allow-lists for screen-target creation paths.

## Risks And Test Signals
Risks are arithmetic overflow, invalid zero strides, descriptor mismatch for planar/compressed formats, and off-by-one errors when translating byte ranges to SVGA boxes. Test signals include maximum dimension saturation, compressed block formats, planar YUV sizing, multisample size multiplication, all mip/layer offset boundaries, and dirty-range conversion at the first and last byte of each subresource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmw_surface_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.c

## Purpose
Implements the vmwgfx context binding manager. It tracks every resource bound into a context so bindings can be scrubbed before resources or contexts are swapped out, killed before resources are destroyed, and rebound after guest-backed contexts are restored.

## Important APIs, Types, And Functions
- `struct vmw_ctx_binding_state` stores fixed arrays for legacy textures/shaders and DX render targets, depth-stencil view, shader resources, constant buffers, stream-output targets, vertex/index buffers, UAVs, stream output, dirty bitmaps, and temporary command buffers.
- Static `vmw_binding_infos[]` maps binding type to storage size, per-shader offsets, and scrub function.
- `vmw_binding_add()`, `vmw_binding_state_commit()`, and `vmw_binding_transfer()` move staged execbuf binding data into persistent context state.
- `vmw_binding_state_scrub()`, `vmw_binding_res_list_scrub()`, `vmw_binding_state_kill()`, and `vmw_binding_res_list_kill()` remove device-visible references.
- `vmw_binding_rebind_all()` recreates scrubbed bindings when resources have valid IDs.
- Scrub functions emit immediate legacy/DX commands or mark dirty bitmaps for batched DX commands.
- `vmw_binding_dirtying()` identifies bindings that make the referenced resource GPU-writable.

## Control Flow
Execbuf validation builds temporary binding state. After commands are submitted, commit transfers entries into the context state and adds each to both the context list and resource binding list. Scrub walks either a context list or a resource list, emits unbind commands or dirty marks, sets `scrubbed`, then flushes batched commands. Rebind walks scrubbed entries with valid resources, emits bind commands through the same scrub functions with `rebind=true`, clears `scrubbed`, and emits dirty batches.

## State, Persistence, And Dependencies
State is entirely in memory and protected externally by `dev_priv->binding_mutex`, as described in the file comment. Binding entries intentionally hold non-refcounted context/resource pointers and rely on the resource subsystem and binding lists for ordering. Commands are emitted through `VMW_CMD_RESERVE`, `VMW_CMD_CTX_RESERVE`, and `vmw_cmd_commit()`.

## Integration Points
Called from context unbind/destroy, cotable scrub, resource eviction/destruction, execbuf validation, and dirty tracking. It integrates with `vmw_context_binding_state()`, resource `binding_head` lists, SVGA3D command definitions, and device capability helpers such as `vmw_max_num_uavs()`.

## Risks And Test Signals
Risks include stale non-refcounted pointers, missing dirty-bit emission, binding type array offset mistakes, batched command size overflows, and adding a new binding type without updating `BUILD_BUG_ON(vmw_ctx_binding_max != 14)` or `vmw_binding_dirtying()`. Test signals include context swapout with active bindings, resource eviction while bound in multiple contexts, DX SRV/UAV/RT/VB batch ranges, rebind after MOB restore, and destruction of bound views/shaders/stream-output objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.h

## Purpose
Declares the binding-manager data model shared by execbuf validation, context lifecycle, resource eviction, and cotable code. The header defines abstract binding types and per-binding metadata structs that store enough SVGA device data to reconstruct unbind and rebind commands.

## Important APIs, Types, And Functions
- `enum vmw_ctx_binding_type` covers legacy shader/render-target/texture bindings and DX shader, render target, shader resource, depth-stencil, stream-output, vertex/index buffer, UAV, compute UAV, and stream-output state bindings.
- `struct vmw_ctx_bindinfo` is the common list node with context/resource pointers, binding type, and scrubbed flag.
- Derived structs add device-specific fields such as shader slot, texture stage, view slot, constant-buffer offset/size, stream-output target range, vertex-buffer stride, index-buffer format, UAV splice index, and stream-output slot.
- `struct vmw_dx_shader_bindings` groups shader, constant-buffer, and shader-resource state per shader type.
- Public functions add/update bindings, commit staged state, scrub/kill resource or context lists, rebind all scrubbed state, allocate/free/reset binding state, expose the active list, and report whether a binding dirties its resource.

## Control Flow
Callers prepare a `vmw_ctx_bindinfo`-derived object from parsed command data, then call `vmw_binding_add()` with shader and slot indexes. Execbuf later commits staged state into persistent context state. Eviction/destruction callers scrub or kill by context or resource list. Restore callers rebind all scrubbed entries.

## State, Persistence, And Dependencies
The opaque `struct vmw_ctx_binding_state` is allocated in the implementation. The metadata structs store non-refcounted pointers, so callers must hold the global binding mutex and maintain resource lifetime ordering. The header depends on Linux lists and SVGA3D register definitions.

## Integration Points
Consumed by `vmwgfx_binding.c`, `vmwgfx_context.c`, resource validation/destruction code, and resources that maintain binding lists. It is part of the contract that guest-backed context swapout and resource swapout can happen independently.

## Risks And Test Signals
Risks include constructing the wrong derived bindinfo for a binding type, slot/shader indexes beyond fixed arrays, and using returned lists after dropping the binding mutex. Test signals include each binding type's add, commit, scrub, rebind, and kill path; constant-buffer offset updates; UAV splice index tracking; and dirty classification for render/depth/stream-output/UAV resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_blit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_blit.c

## Purpose
Provides CPU-side buffer-object copy helpers and a differential memcpy implementation that computes the bounding rectangle of modified pixels while copying. It is used where GPU blits are unavailable or inappropriate and where dirty tracking should avoid full-surface updates.

## Important APIs, Types, And Functions
- Generated `vmw_find_first_diff_*()` and `vmw_find_last_diff_*()` compare byte ranges using u8/u16/u32/u64 widths depending on alignment and architecture.
- `vmw_find_first_diff()` and `vmw_find_last_diff()` return granularity-aligned changed offsets.
- `vmw_memcpy()` is a plain copy callback for `struct vmw_diff_cpy`.
- `vmw_diff_memcpy()` copies only the changed span of a line and expands `diff->rect`.
- `struct vmw_bo_blit_line_data` caches mapped source/destination pages and copy metadata.
- `vmw_bo_cpu_blit_line()` copies one logical line across page boundaries using kmap.
- `vmw_bo_cpu_blit()` validates/populates TTM pages and copies a rectangle line-by-line.
- `vmw_external_bo_copy()` handles imported/external dma-buf backed BOs through vmap.

## Control Flow
The main blit path asserts source and destination differ and are pinned or reserved, populates TTs if needed, dispatches external objects to a vmap copy path, converts scatter-gather lists to page arrays when necessary, then loops over rows. Each row maps only the current source and destination pages, copies up to the next page boundary, and advances offsets. The diff callback updates line/offset state to track a destination dirty rectangle.

## State, Persistence, And Dependencies
State is transient per copy. It depends on TTM TT population, page arrays or SG tables, `kmap_atomic_prot()`, dma-buf vmap/vunmap for imported objects, `vmw_bo_map_and_cache()` for local external-style mapping, and DRM rectangles.

## Integration Points
Used by fb/surface update paths and dirty tracking code that provide `struct vmw_diff_cpy`. It integrates with vmwgfx BO mapping, PRIME SG helpers, and TTM memory protections.

## Risks And Test Signals
Risks are page-boundary off-by-one errors, unbalanced atomic maps, insufficient bounds validation by callers, dirty rectangles not matching copied bytes, and external-object full memcpy not using the diff callback. Test signals include unaligned source/destination offsets, strides different from width, copies spanning many pages, imported dma-buf BOs, identical source data producing empty dirty rects, and granularity equal to bytes-per-pixel for 16/32/64-bit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_blit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.c

## Purpose
Implements vmwgfx's TTM/GEM buffer-object wrapper. It handles allocation, placement, pinning, cached kernel mappings, CPU synchronization ioctls, move/swap notifications, resource detachment, dumb-surface cleanup, fencing, and helper lookup/reference operations for user BO handles.

## Important APIs, Types, And Functions
- `vmw_bo_create()` and internal `vmw_bo_init()` allocate a `struct vmw_bo`, initialize GEM private storage, set placement, and call `ttm_bo_init_reserved()`.
- `vmw_bo_pin_in_vram_or_gmr()`, `vmw_bo_pin_in_vram()`, `vmw_bo_pin_in_start_of_vram()`, `vmw_bo_unpin()`, and `vmw_bo_pin_reserved()` manage fixed placement.
- `vmw_bo_map_and_cache_size()`, `vmw_bo_map_and_cache()`, and `vmw_bo_unmap()` implement refcounted cached kernel maps.
- `vmw_user_bo_synccpu_ioctl()` implements CPU access grab/release and optional command-submission blocking.
- `vmw_bo_move_notify()` and `vmw_bo_swap_notify()` tear down mappings and detach resources before incompatible moves.
- `vmw_bo_fence_single()` adds a vmwgfx fence to one BO reservation object.
- `vmw_bo_surface()` discovers an attached or detached surface using dumb-surface, xarray, and rb-tree relationships.

## Control Flow
Creation aligns size, initializes GEM/TTM, sets placement from requested domains, optionally pins, and optionally leaves the BO reserved. Pinning reserves the BO, validates placement, and pins without changing placement afterward. Move notification unmaps VRAM transitions and unbinds resources when moving backup MOBs out of MOB placement. Destruction unmaps, tears down detached resources, detaches dumb-surface MOBs under command-buffer mutex, releases dirty/coherent tracking, releases GEM, and frees the wrapper.

## State, Persistence, And Dependencies
State is in the TTM BO plus vmwgfx fields: placement arrays, cached kmap, resource rb-tree, detached-resource xarray, eviction priority counters, map and CPU-writer atomics, DX query context pointer, dirty tracking pointer, and dumb-surface link. Dependencies include DRM GEM, TTM placement/reservation/fence APIs, vmwgfx resource binding, and dma-resv.

## Integration Points
Used by resource backing MOB management, command buffers, query MOBs, dumb buffers, PRIME/imported BOs, and user ioctls. Placement domains bridge vmwgfx `VMW_PL_*` managers with TTM system/VRAM memory.

## Risks And Test Signals
Risks include leaked cached maps, pin-count mismatches, invalid resource detachment ordering, CPU writer underflow, and BO destruction while dumb-surface/resource links remain. Test signals include placement fallback behavior, pin/unpin across VRAM/GMR/MOB/system, synccpu grab/release with busy fences and `allow_cs`, move-notify detaching MOB-backed resources, dumb BO teardown, and priority adjustment as resources attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.h

## Purpose
Declares the vmwgfx buffer-object abstraction built on top of TTM and GEM. It defines placement domains, creation parameters, the `struct vmw_bo` layout, and helper functions used throughout resource, command, framebuffer, and user-handle code.

## Important APIs, Types, And Functions
- `enum vmw_bo_domain` models system, waitable system, VRAM, GMR, and MOB placement preferences.
- `struct vmw_bo_params` supplies domain, busy-domain, TTM type, pin/keep-reservation flags, size, external reservation object, and scatter-gather table.
- `struct vmw_bo` embeds `ttm_buffer_object`, placement arrays, cached kmap state, resource rb-tree, eviction priority counters, detached-resource xarray, map/cpu-writer atomics, DX query context pointer, dirty tracking pointer, and dumb-surface association.
- Public functions cover placement, creation, user unref/synccpu ioctls, pin/unpin, guest pointer extraction, fencing, map/unmap, move/swap notify, detached-resource tracking, attached-surface discovery, user handle lookup, and MOB id extraction.
- Inline helpers adjust eviction priority and wrap GEM get/put for vmwgfx references.

## Control Flow
Callers construct `vmw_bo_params`, create a BO, then use placement helpers before TTM validation. Resource code attaches/detaches resources and updates priority counts. User code gets a ref via `vmw_user_bo_lookup()` and drops it with `vmw_user_bo_unref()`. Move/swap callbacks must be wired into TTM device functions to preserve mapping and resource invariants.

## State, Persistence, And Dependencies
The header describes in-memory BO state and depends on SVGA registers, DRM/TTM BO and placement APIs, Linux rb-tree types, xarray, and vmwgfx resource/fence forward declarations. There is no persistence.

## Integration Points
This is the common BO contract for command buffers, resources, dirty tracking, dumb surfaces, query MOBs, and CPU blits. It is also the bridge from DRM GEM handles to vmwgfx-specific BO behavior.

## Risks And Test Signals
Risks are incorrect domain combinations, priority counter imbalance, misuse of non-refcounted `dx_query_ctx`, stale `dumb_surface`, and forgetting that cached maps are protected by reservation/pinning. Test signals include reference get/put leak checks, priority add/del ordering, map/unmap counts, attached-surface lookup through all three paths, and MOB id use only when the resource is in MOB placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmd.c

## Purpose
Implements device command submission plumbing for legacy FIFO and newer command-buffer managers. It initializes and tears down FIFO state, reserves/commits command space, pings the host, emits fences and dummy queries, and reports whether 3D/command submission is supported by the virtual device.

## Important APIs, Types, And Functions
- `vmw_supports_3d()` checks SVGA capabilities, GBOBJECTS/MOB support, FIFO hardware version, and display-unit constraints.
- `vmw_fifo_create()` initializes FIFO registers, allocates static bounce storage, and records FIFO capabilities.
- `vmw_fifo_wait()`, `vmw_fifo_wait_noirq()`, and `vmw_fifo_is_full()` wait for FIFO space with IRQ or polling paths.
- `vmw_local_fifo_reserve()` reserves FIFO bytes in place or uses static/dynamic bounce buffers.
- `vmw_local_fifo_commit()` copies bounce data if needed, advances `NEXT_CMD`, clears `RESERVED`, and pings the host.
- `vmw_cmd_ctx_reserve()`, `vmw_cmd_commit()`, `vmw_cmd_commit_flush()`, and `vmw_cmd_flush()` abstract command-buffer versus FIFO submission.
- `vmw_cmd_send_fence()` emits SVGA fences or falls back to marker-based waiting.
- Dummy query helpers emit legacy or GB query waits for query barriers.

## Control Flow
Initialization writes FIFO min/max/next/stop/busy registers and enables `CONFIG_DONE`. Reserve chooses command buffers when `dev_priv->cman` exists; otherwise it only allows non-context FIFO commands. FIFO reserve serializes with `fifo_mutex`, verifies size, waits for space, and either returns FIFO memory or a bounce buffer. Commit finalizes reserved bytes, handles wraparound copying, updates FIFO registers under `rwsem`, pings the host, and unlocks.

## State, Persistence, And Dependencies
State is in `struct vmw_fifo_state`: static/dynamic buffers, reserved size, bounce flag, mutex/rwsem, and capability bits. Dependencies include SVGA registers/FIFO memory, wait queues, IRQ waiters, command-buffer manager APIs, TTM BO placement for dummy query memory, and vmwgfx fence/query code.

## Integration Points
All command emitters use these reserve/commit wrappers. The file integrates with `vmwgfx_cmdbuf.c` when command buffers are present and with legacy FIFO hardware otherwise. Fencing links command submission to `vmwgfx_irq.c` and fence manager state.

## Risks And Test Signals
Risks include FIFO wraparound errors, stuck FIFO timeouts, bounce-buffer leaks, issuing context commands without command buffers, and fence fallback sequencing bugs. Test signals include FIFO full waits with and without IRQMASK, reservations at end-of-ring, large dynamic bounce submissions, command-buffer and FIFO mode parity, fence seqno wrap avoidance, dummy query emission for legacy and MOB paths, and SVGA v3 command-buffer capability gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf.c

## Purpose
Implements the SVGA command-buffer manager used for asynchronous command submission. It allocates inline or pooled command-buffer space, submits buffers to hardware contexts, processes completion/preemption/error statuses, handles deferred error recovery, manages idle/allocation waiters, and owns command-buffer pool lifetime.

## Important APIs, Types, And Functions
- `struct vmw_cmdbuf_man` stores locks, work item, context queues, error list, DRM range manager, optional MOB/DMA pool backing, current small-command buffer, DMA pools for headers, wait queues, IRQ state, and hardware limits.
- `struct vmw_cmdbuf_context` has submitted, hardware-submitted, and preempted queues plus submission blocking state.
- `struct vmw_cmdbuf_header` describes one command buffer and its device header.
- `vmw_cmdbuf_alloc()`, `vmw_cmdbuf_reserve()`, and `vmw_cmdbuf_commit()` are the main allocation/submission APIs.
- `vmw_cmdbuf_cur_flush()` and `vmw_cmdbuf_idle()` flush and wait for completion.
- `vmw_cmdbuf_set_pool_size()`, `vmw_cmdbuf_remove_pool()`, `vmw_cmdbuf_man_create()`, and `vmw_cmdbuf_man_destroy()` manage bootstrap, pool, and teardown.

## Control Flow
Small submissions use a shared current command buffer protected by `cur_mutex`; larger ones allocate a dedicated header and space. Inline submissions use a DMA pool object containing header plus command bytes; pooled submissions allocate a range from `drm_mm` backed by coherent DMA memory or a pinned MOB. Commit flushes current work when requested, then queues the header to a context. Processing submits until the hardware queue limit, walks completed hardware buffers, frees successful ones, moves preempted ones, and defers command errors to workqueue context.

The error worker describes and skips the failing command when possible, blocks all contexts, preempts hardware, splices preempted buffers after the repaired buffer, restarts contexts, and emits a replacement fence if one was discarded.

## State, Persistence, And Dependencies
State is volatile queue, range-manager, DMA-pool, and wait-queue state. Dependencies include SVGA command-buffer registers, DMA pools, coherent DMA allocation, TTM BOs for MOB-backed pools, DRM MM, vmwgfx waiters, fences, and command-description helpers.

## Integration Points
Called by `vmwgfx_cmd.c` reserve/commit wrappers, resource/context/cotable binding paths, IRQ threaded handler, device initialization, and teardown paths before MOB memory management is removed.

## Risks And Test Signals
Risks include deadlocks between current-buffer and pool allocation, missed IRQ enabling/disabling, queue corruption during preemption/error recovery, freeing inline versus pooled headers incorrectly, and pool removal while work remains. Test signals include inline-only bootstrap, MOB-backed and DMA-backed pools, high-priority two-context devices, allocation wait under full pool, command error recovery with multiple queued buffers, preemption status handling, idle timeout, and destroy with `has_pool` already removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf_res.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf_res.c

## Purpose
Implements a per-context command-buffer resource manager. It tracks resources created or destroyed through command-buffer execution, stages additions/removals during execbuf validation, and commits or reverts those changes depending on whether command submission succeeds.

## Important APIs, Types, And Functions
- `struct vmw_cmdbuf_res_manager` owns a hash table of staged/committed resources and a list of committed resources.
- `struct vmw_cmdbuf_res` stores a refcounted `vmw_resource`, hash item, list node, staging state, and owning manager.
- `vmw_cmdbuf_res_lookup()` finds a resource by combined resource type and user key.
- `vmw_cmdbuf_res_add()` stages a new resource, inserts it in the hash immediately, refs the resource, and links it to the caller's staging list.
- `vmw_cmdbuf_res_remove()` stages removal or cancels an uncommitted add.
- `vmw_cmdbuf_res_commit()` finalizes staged additions/removals after commands are submitted.
- `vmw_cmdbuf_res_revert()` undoes staged additions/removals after validation/submission failure.
- `vmw_cmdbuf_res_man_create()` and `_destroy()` allocate and tear down the manager.

## Control Flow
Execbuf creates a staging list. Adds insert a hash-visible entry in `VMW_CMDBUF_RES_ADD` state. Removes find the hash entry; if the entry was only staged for add it is freed, otherwise it is removed from the committed hash/list and placed on the staging list as `VMW_CMDBUF_RES_DEL`. Commit calls resource `commit_notify()` and either moves adds to the committed list or drops deleted entries. Revert removes staged adds from the manager or restores staged deletes to the committed hash/list.

## State, Persistence, And Dependencies
State is in-memory and protected by `dev_priv->cmdbuf_mutex` according to the comments. Hash keys combine `user_key | (res_type << 24)`, so key-space assumptions are important. Dependencies include Linux hashtables, RCU hash deletion, vmwgfx resource references, and `enum vmw_cmdbuf_res_state`.

## Integration Points
Owned by guest-backed/DX contexts through `vmw_context_res_man()`. Used by execbuf resource commands that create/destroy command-buffer-managed views, shaders, stream-output objects, and related resources.

## Risks And Test Signals
Risks include key collisions if user keys exceed the assumed low bits, lookup during staged delete, missing commit/revert on an error path, and resource reference leaks. Test signals include add+commit, add+revert, committed remove+commit, committed remove+revert, remove of staged add, duplicate key rejection at higher layers, and manager destroy with live committed resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf_res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_context.c

## Purpose
Implements user-visible SVGA3D context resources for legacy, guest-backed, and DX contexts. It connects TTM handle lifetime, vmwgfx resource lifetime, context MOB binding/unbinding, binding state, command-buffer resource managers, DX cotables, and DX query MOB ownership.

## Important APIs, Types, And Functions
- `struct vmw_user_context` embeds `ttm_base_object`, `vmw_resource`, binding state, command-buffer resource manager, cotable array, cotable lock, and optional DX query MOB.
- Resource function tables define legacy, GB, and DX context capabilities, memory domains, and callbacks.
- `vmw_context_init()` chooses legacy FIFO context creation or guest-backed initialization depending on MOB support.
- `vmw_gb_context_create/bind/unbind/destroy()` and `vmw_dx_context_create/bind/unbind/destroy()` emit context commands.
- `vmw_dx_context_scrub_cotables()` scrubs bindings and all cotables in safe order.
- User ioctls `vmw_context_define_ioctl()`, `vmw_extended_context_define_ioctl()`, and `vmw_context_destroy_ioctl()` create/destroy handles.
- Accessors expose binding list/state, command-buffer resource manager, cotables, and DX query MOB binding.

## Control Flow
Context define allocates `vmw_user_context`, initializes a vmwgfx resource, optionally creates binding state, command-buffer resource manager, and DX cotables, then creates a TTM base handle. Legacy contexts emit `CONTEXT_DEFINE` immediately. Guest-backed and DX contexts allocate IDs on create, bind a MOB on validation, scrub bindings/cotables before unbind, optionally read back state, then bind invalid MOB and fence the backup BO. Destroy tears down resource-manager state, binding state, device context, pinned query BOs, cotable references, and TTM handle references.

## State, Persistence, And Dependencies
State is in memory: resource ID, guest-memory dirty flag, binding state, cotable resources, command-buffer managed resources, and DX query MOB pointer. It depends on TTM object handles, vmwgfx resource core, command submission, BO fencing, binding mutex, cmdbuf mutex, and SVGA context/cotable command definitions.

## Integration Points
The file is central to execbuf context lookup, resource validation, cotable allocation, query management, binding scrub/rebind, and user ioctls. DX cotables are allocated per context and accessed by cotable type through `vmw_context_cotable()`.

## Risks And Test Signals
Risks include lock-order violations during context/cotable scrub, leaked cotables or command-buffer resources on partial initialization, invalid query MOB association, and failing to scrub bindings before context swapout. Test signals include legacy and DX define/destroy ioctls, unsupported DX rejection, context MOB bind/unbind with readback, cotable scrub order, query MOB replacement denial, file-close cleanup, and context destruction while resources remain bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cotable.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cotable.c

## Purpose
Treats DX context object tables as vmwgfx resources with guest-memory backing so they participate in the same MOB validation, eviction, readback, fencing, and resize mechanisms as other resources. Cotables hold device-side records for views, shaders, stream output, queries, UAVs, and fixed-function DX state objects.

## Important APIs, Types, And Functions
- `struct vmw_cotable` embeds `vmw_resource`, stores owning context, readback size, highest seen entry, cotable type, scrubbed state, and active resource list.
- `co_info[]` defines initial entry counts, entry sizes, and optional unbind/scrub callbacks per cotable type.
- `vmw_cotable_scrub_order[]` enforces a safe scrub order for binding-bearing cotables.
- Resource callbacks `vmw_cotable_create()`, `vmw_cotable_bind()`, `vmw_cotable_unbind()`, and `vmw_cotable_destroy()` implement validation lifecycle.
- `vmw_cotable_scrub()` partially unbinds without requiring backup BO reservation.
- `vmw_cotable_unscrub()` rebinds the cotable MOB to the context.
- `vmw_cotable_resize()` allocates a larger MOB, reads back old contents, page-copies data, switches backing, and rebinds.
- `vmw_cotable_notify()` records highest used object-table ID and triggers resize on next validate.
- `vmw_cotable_add_resource()` links active resources into the cotable list.

## Control Flow
Allocation initializes a guest-backed resource with at least one page or type-specific minimum size, marks it scrubbed, and stores the owning context. Notify raises `seen_entries` and invalidates `res->id` so validation calls create. Create either unscrubs an attached MOB or doubles the backing size until it fits the highest seen entry. Scrub optionally calls type-specific list cleanup, emits readback plus `SET_COTABLE` with invalid MOB, marks scrubbed, and invalidates the resource. Full unbind delegates to context cotable scrub under binding mutex and fences the backup BO.

## State, Persistence, And Dependencies
Cotable contents live in guest-memory MOBs and are read back across eviction, but there is no disk persistence. Dependencies include vmwgfx resource core, BO creation/mapping/fencing, command submission, binding mutex, MKS statistics, and type-specific view/shader/stream-output cleanup helpers.

## Integration Points
Allocated by DX context initialization and accessed by `vmw_context_cotable()`. Cotable resource lists are maintained by view/shader/stream-output objects. Context unbind calls `vmw_dx_context_scrub_cotables()` using the exported scrub order.

## Risks And Test Signals
Risks include unrecoverable state if resize fails after device switch, incorrect readback size, scrub order regressions causing invalid context swapin, page-copy assumptions when old/new sizes differ, and missing type info when new cotables are added. Test signals include notify-triggered growth, resize after high object IDs, readback and unbind fencing, scrub/unscrub cycles, cotable destruction while resources are listed, SM4 versus SM5 cotable count, and callbacks for views/shaders/stream-output resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cotable.c -->
