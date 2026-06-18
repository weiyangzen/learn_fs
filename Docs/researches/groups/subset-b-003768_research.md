# subset-b-003768 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_execbuf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_execbuf.c

## Purpose
`vmwgfx_execbuf.c` is the vmwgfx command-submission verifier and submitter. It accepts userspace SVGA3D command streams through `DRM_VMW_EXECBUF`, validates every command against the caller's objects and the virtual device capability set, builds resource and buffer validation lists, patches userspace handles into hardware ids, submits through either the legacy FIFO or command-buffer manager, and returns/imports/exports synchronization fences.

## Important APIs, Types, and Functions
- `struct vmw_relocation`, `struct vmw_resource_relocation`, and `enum vmw_resource_relocation_type` hold delayed BO/MOB/GMR and resource-id fixups. Resource relocations can rewrite ids, unconditional NOP a command, or conditionally NOP it if an evicted resource has no host id.
- `struct vmw_ctx_validation_info` tracks a context resource plus its current and staged binding state for this execbuf.
- `struct vmw_cmd_entry` and `vmw_cmd_entries[]` are the verifier dispatch table. Entries encode callback, userspace permission, and guest-backed object capability requirements.
- `vmw_execbuf_res_val_add()`, `vmw_cmd_res_check()`, `vmw_view_res_val_add()`, and `vmw_view_id_val_add()` are the main resource lookup/validation helpers.
- Command-specific validators such as `vmw_cmd_dma()`, `vmw_cmd_draw()`, `vmw_cmd_set_shader()`, `vmw_cmd_dx_view_define()`, `vmw_cmd_dx_set_vertex_buffers()`, and SM5 UAV/indirect validators check embedded ids, dimensions, capability gates, dirty flags, and binding side effects.
- `vmw_cmd_check_all()` walks the submitted byte stream, using `vmw_cmd_check()` for each command and rejecting size drift.
- `vmw_execbuf_process()` is the central orchestration path; `vmw_execbuf_ioctl()` is the DRM ioctl entry point.
- `vmw_execbuf_fence_commands()` and `vmw_execbuf_copy_fence_user()` integrate with `vmwgfx_fence.c` and sync-file fd export.
- `__vmw_execbuf_release_pinned_bo()` and `vmw_execbuf_release_pinned_bo()` flush and unpin the global query BO.

## Control Flow
`vmw_execbuf_ioctl()` checks ABI version, optionally waits on an imported sync-file fence, and calls `vmw_execbuf_process()`. Processing optionally allocates an output fence fd, copies userspace commands into a command-buffer allocation or a vmalloc bounce buffer, takes `cmdbuf_mutex`, initializes the shared `vmw_sw_context`, optionally ties a DX context, validates all commands, reserves resources and BOs, validates memory placement, rebinds context state under `binding_mutex`, submits through FIFO or cmdbuf, emits a fence marker, commits staged context bindings and staged command resources, fences validated BOs, copies fence information to userspace, installs exported fence fds, and finally drops references outside the command mutex.

Error flow backs off BO validation, reverts staged command resources, commits no binding changes, frees relocation lists, releases invalid pinned query state if needed, frees command-buffer headers, and returns the negative errno. The code explicitly treats fence-submit failure as mostly harmless because the fence send path synchronizes before reporting failure to userspace.

## State and Persistence Behavior
The file mutates long-lived driver state: context binding state, cotables, staged view/shader/stream-output resources, `dev_priv->pinned_bo`, `dummy_query_bo_pinned`, `query_cid`, `query_cid_valid`, command-buffer manager state, last known query MOB binding, and BO/resource dirty tracking. Userspace handles are not submitted directly; they are translated only after validation has established stable TTM resources and resource ids. No filesystem persistence exists, but command submissions persist in host-visible SVGA device state and vmwgfx resource managers.

## Dependencies and Integration Points
This file depends on TTM validation, vmwgfx resource managers, BO placement helpers, binding/cotable/view/shader/stream-output code, KMS cursor snooping, FIFO and command-buffer reservation helpers, `vmwgfx_fence.c`, Linux `dma_fence`/`sync_file`, and DRM file-private TTM object tables. It is a high-risk integration layer between untrusted DRM ioctls and the virtual SVGA hardware command processor.

## Risks
The verifier must stay byte-for-byte synchronized with the device parser; any size miscalculation, unchecked command body, or stale relocation can become a device error or privilege boundary issue. Lock ordering between `cmdbuf_mutex`, validation reservations, and `binding_mutex` is delicate. Query BO pinning has recovery paths but can stall while waiting for device idle. Capability gates for guest-backed, DX, SM4/SM5, and GL43 commands must match host behavior. Usercopy failures after fence creation require forced waits and handle cleanup to avoid leaving userspace unable to synchronize.

## Test Signals
Good tests exercise valid and invalid execbuf streams, command-size truncation, privileged command rejection, guest-backed versus legacy capability paths, DX context requirements, view/shader/resource lifetime across eviction, BO relocation into VRAM/GMR/MOB, imported and exported fence fds, fence copyout failure handling, query BO switching, and suspend/reset paths that release pinned query state. Kernel signals include `VMW_DEBUG_USER` messages, `MKSSTAT_KERN_EXECBUF`, absence of `WARN_ON` in context-cache paths, and no lockdep or dma_fence warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_execbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.c

## Purpose
`vmwgfx_fence.c` implements vmwgfx synchronization objects on top of Linux `dma_fence`. It maps SVGA fence sequence numbers into kernel fences, exposes optional userspace TTM base-object handles, supports wait/signaled/unref/event ioctls, and coordinates interrupt waiter programming through `vmwgfx_irq.c`.

## Important APIs, Types, and Functions
- `struct vmw_fence_manager` owns the fence list, spinlock, fifo-down state, device pointer, and dma-fence context id.
- `struct vmw_user_fence` wraps a TTM base object plus `struct vmw_fence_obj` for userspace-visible fences.
- `struct vmw_event_fence_action` stores a dma-fence callback that sends a DRM event, optionally timestamped from the fence signal timestamp.
- `vmw_fence_manager_init()` and `vmw_fence_manager_takedown()` allocate and destroy the manager.
- `vmw_fence_obj_init()`, `vmw_fence_create()`, and `vmw_user_fence_create()` initialize kernel-only or userspace fences.
- `vmw_fences_update()` reads the hardware fence register, signals passed fences in list order, removes interrupt waiters, and publishes `last_read_seqno`.
- `vmw_fence_obj_wait_ioctl()`, `vmw_fence_obj_signaled_ioctl()`, `vmw_fence_obj_unref_ioctl()`, and `vmw_fence_event_ioctl()` are the DRM ABI handlers.
- `vmw_fence_fifo_down()` marks the FIFO down and drains/signals all live fences during teardown/reset.

## Control Flow
Fence creation initializes a `dma_fence` with the manager lock and appends it to the ordered fence list unless the FIFO is down. Signaling paths call `vmw_fences_update()`, which reads the current SVGA seqno and signals each list head that has passed according to wrap-aware arithmetic. `enable_signaling` programs a seqno interrupt waiter and rereads the seqno to close the race between checking the fence and enabling interrupts. Userspace wait ioctl converts microsecond timeout into a jiffies cookie for repeated waits, looks up the TTM object, waits on the dma fence, and can unref the handle on success.

## State and Persistence Behavior
The persistent runtime state is in `vmw_fence_manager::fence_list`, `fifo_down`, fence `waiter_added` bits, TTM object references, and pending DRM events. The manager holds an implicit reference while a fence remains on its list. Event callbacks own a fence reference until the callback sends or synthesizes the event. There is no disk persistence.

## Dependencies and Integration Points
This file integrates with `vmw_execbuf_fence_commands()` for fence emission, `vmwgfx_irq.c` for `vmw_seqno_waiter_add/remove()` and wakeups, TTM object-file lookup/refcounting for userspace handles, DRM event reservation/delivery, and Linux `dma_fence` callback semantics.

## Risks
The most important risks are missed interrupts around `enable_signaling`, unsignaled fence destruction with callbacks, wraparound comparisons, userspace handle type confusion, and event lifetime on already-signaled fences. FIFO-down handling deliberately forces completion after timeout, so lockup recovery can hide the original stalled command but prevents indefinite waits.

## Test Signals
Exercise fence create/wait/signaled/unref ioctls, timeout-cookie reuse, interruptible waits, event delivery with and without requested timestamps, already-signaled event callbacks, FIFO-down teardown, and sync with execbuf fence copyout. Watch for dma_fence warnings, leaked TTM base objects, and stalled `fence_queue` waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.h

## Purpose
`vmwgfx_fence.h` declares the vmwgfx fence abstraction used by execbuf, KMS, IRQ, and ioctl paths. It exposes `struct vmw_fence_obj`, manager lifecycle APIs, reference helpers, wait/signaled/create routines, FIFO up/down hooks, and userspace fence/event ioctls.

## Important APIs, Types, and Functions
- `VMW_FENCE_WAIT_TIMEOUT` is the common five-second wait used by recovery paths.
- `struct vmw_fence_obj` embeds `struct dma_fence base`, tracks whether a seqno interrupt waiter was added, links into the manager list, and stores a type-specific destroy callback.
- `vmw_fence_obj_reference()` and `vmw_fence_obj_unreference()` are thin `dma_fence_get/put` wrappers that NULL caller pointers on put.
- Declared creation paths are `vmw_fence_create()` for kernel fences and `vmw_user_fence_create()` for userspace handles.
- Declared ABI handlers cover wait, signaled, unref, fence event, and explicit event callback queueing.

## Control Flow
Consumers include the header to create fences after command submission, fence BO validation lists, expose handles to userspace, wait during cleanup, and attach DRM events. The header itself has no complex control flow, but its inline reference helpers define the ownership convention used throughout the driver.

## State and Persistence Behavior
The header defines in-memory fence state only. The `dma_fence` base owns refcount, signal state, callbacks, and timestamps; vmwgfx-specific fields connect that base object to SVGA seqno waiter management and manager list lifetime.

## Dependencies and Integration Points
It depends on Linux `dma-fence` and `dma-fence-array` headers and forward-declares DRM and vmwgfx private types. It is included by driver components that need synchronization without exposing `struct vmw_fence_manager` internals.

## Risks
Because this header exposes only an opaque manager and inline reference operations, misuse risks are mostly ownership-related: double put, forgetting to clear a handed-off pointer, or treating a `vmw_fence_obj` as signaled without calling update/wait helpers. The lack of a conventional include-guard `#define` after `#ifndef _VMWGFX_FENCE_H_` is unusual, though the file terminates with the matching `#endif`.

## Test Signals
Compile coverage should catch prototype drift against `vmwgfx_fence.c`. Runtime validation comes from execbuf/KMS fence creation, userspace fence ioctls, and teardown paths that call FIFO up/down and manager takedown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gem.c

## Purpose
`vmwgfx_gem.c` adapts vmwgfx TTM buffer objects to the DRM GEM and PRIME interfaces. It supplies GEM object callbacks, creates GEM handles for vmwgfx BOs, imports dma-buf scatter-gather tables, handles mmap/vmap differences for imported objects, and exposes a debugfs view of per-file GEM objects.

## Important APIs, Types, and Functions
- `vmw_gem_object_funcs` provides GEM operations: free, open/close, info printing, pin/unpin, sg-table export, vmap/vunmap, mmap, and vm ops.
- `vmw_vm_ops` routes GEM faults and write faults through vmwgfx BO VM handlers plus TTM open/close hooks.
- `vmw_gem_object_create_with_handle()` creates a vmwgfx BO with default domain based on MOB support and publishes a GEM handle.
- `vmw_prime_import_sg_table()` creates a `ttm_bo_type_sg` BO backed by an imported dma-buf reservation object and sg table.
- `vmw_gem_object_create_ioctl()` implements dmabuf allocation ABI response fields including map handle and current GMR id.
- `vmw_debugfs_gem_init()` registers `vmwgfx_gem_info`; debugfs helpers walk DRM files and object idrs.

## Control Flow
Object creation builds `vmw_bo_params`, calls `vmw_bo_create()`, then creates a GEM handle that owns the user reference. PRIME import locks the dma-buf reservation, creates an SG-type BO using the imported reservation and sg table, assigns vmwgfx GEM funcs, and unlocks. Mapping imported objects delegates to dma-buf operations and rejects iomem vmaps; local BO mappings use TTM helpers. mmap for imported objects resets VMA hooks before calling dma-buf mmap and drops the `drm_gem_mmap_obj()` reference on success.

## State and Persistence Behavior
Runtime state lives in GEM handle tables, BO refcounts, BO pin counts, TTM resources, imported dma-buf reservation objects, and optional debugfs output. No disk persistence exists. The debugfs walk observes open DRM files under `filelist_mutex` and object idrs under `table_lock`.

## Dependencies and Integration Points
The file depends on `vmwgfx_bo.h`, TTM GEM helpers, DRM PRIME helpers, dma-buf APIs, Linux debugfs, and vmwgfx BO VM fault handlers. KMS framebuffer creation and execbuf BO lookup rely on the GEM handles created here.

## Risks
Imported dma-buf paths have distinct ownership and mapping semantics; failure to reset VMA fields or drop references would cause stale vm_ops or leaks. `vmw_gem_object_get_sg_table()` assumes `bo->ttm` is a `vmw_ttm_tt`. Debugfs walks task names under RCU because stored pids may outlive tasks. Pin/unpin callbacks assume callers already hold the appropriate reservation context.

## Test Signals
Cover dmabuf allocation ioctl, GEM mmap/vmap/vunmap for local and imported objects, PRIME import/export, pin/unpin through framebuffer scanout, debugfs `vmwgfx_gem_info` under multiple DRM clients, and refcount/pin-count stability after handle close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmr.c

## Purpose
`vmwgfx_gmr.c` emits SVGA FIFO commands to bind and unbind Guest Memory Regions using the GMR2 command set. It translates vmwgfx scatter-gather page iterators into PPN remap payloads understood by the virtual SVGA device.

## Important APIs, Types, and Functions
- `VMW_PPN_SIZE` selects 32-bit or 64-bit page-number payload width from `sizeof(unsigned long)`.
- `VMW_PPN_PER_REMAP` caps each remap command to a future-safe payload size.
- `vmw_gmr2_bind()` reserves FIFO space, emits `SVGA_CMD_DEFINE_GMR2`, then one or more `SVGA_CMD_REMAP_GMR2` commands containing DMA page numbers.
- `vmw_gmr2_unbind()` emits a zero-page `DEFINE_GMR2` to release a GMR id.
- `vmw_gmr_bind()` and `vmw_gmr_unbind()` are the exported capability-gated wrappers.

## Control Flow
Binding starts a `vmw_piter` over a vmwgfx sg table, returns success for empty mappings, rejects devices without `SVGA_CAP_GMR2`, and reserves a single FIFO region sized for the define command plus all remap chunks. Each remap chunk fills offset, count, 32/64-bit flags, and sequential PPNs from the DMA iterator before committing the FIFO reservation. Unbind reserves and commits a small define command with `numPages = 0`.

## State and Persistence Behavior
The file does not allocate ids or maintain state; it programs host-visible SVGA GMR mappings for ids allocated elsewhere. Binding persists in the virtual device until unbound or reset. The source sg table and iterator state are consumed only during command construction.

## Dependencies and Integration Points
It depends on vmwgfx FIFO reservation/commit helpers, `struct vmw_sg_table`, `struct vmw_piter`, DMA addresses, and SVGA register command definitions. TTM placement and execbuf relocation ultimately depend on these mappings when BOs reside in GMR space.

## Risks
The command size calculation must match the exact emitted payload, and the `BUG_ON` asserts that the buffer cursor ends where expected. Large mappings are split to avoid oversized remaps, but the total FIFO reservation can still fail. Page-number width must match host/device expectations. Devices without GMR2 support intentionally reject binds.

## Test Signals
Test empty sg tables, single-page and multi-chunk mappings, 32-bit and 64-bit PPN builds, FIFO reserve failure, GMR2 capability absence, and unbind during BO eviction. Device-side display or DMA failures after relocation are likely signals of malformed GMR binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmrid_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmrid_manager.c

## Purpose
`vmwgfx_gmrid_manager.c` implements a TTM resource manager for vmwgfx GMR and MOB id spaces. It allocates numeric ids using `ida`, tracks page consumption, applies soft graphics-memory limits, and installs/removes the manager for TTM placement types.

## Important APIs, Types, and Functions
- `struct vmwgfx_gmrid_man` embeds `ttm_resource_manager` and stores a spinlock, `ida`, max id count, max page budget, used pages, and placement type.
- `vmw_gmrid_man_get_node()` allocates a TTM resource, assigns a GMR/MOB id, increments used pages, and expands soft limits when possible.
- `vmw_gmrid_man_put_node()` frees the id, decrements used pages, finalizes the TTM resource, and frees memory.
- `vmw_gmrid_man_debug()` reports usage to DRM printers.
- `vmw_gmrid_man_init()` and `vmw_gmrid_man_fini()` register and unregister the manager with the vmwgfx TTM device.

## Control Flow
Initialization selects limits from `dev_priv` based on `VMW_PL_GMR` or `VMW_PL_MOB`, initializes the resource manager and ida, registers it with TTM, and marks it used. Allocation initializes a resource from the requested TTM place, allocates an id up to the configured maximum, then updates page accounting under the manager lock. If usage exceeds the current soft page budget, the manager warns the guest/host and attempts to double the budget up to half of RAM; if it cannot cover current usage, allocation fails with `-ENOSPC` and fully unwinds. Finalization marks the manager unused, evicts all resources, cleans up TTM state, unregisters it, destroys the ida, and frees the manager.

## State and Persistence Behavior
Persistent runtime state is the id allocator and page counters for the registered TTM placement. Allocated TTM resources store the id in `res->start`, which later becomes the hardware GMR/MOB id used by relocation and binding. No disk persistence exists.

## Dependencies and Integration Points
This file depends on Linux `ida`, TTM resource-manager APIs, vmwgfx device limits, `totalram_pages()`, DRM warning/printer helpers, and `vmw_host_printf()` for guest-visible warnings. BO placement into `VMW_PL_GMR` and `VMW_PL_MOB` depends on this manager.

## Risks
Accounting must remain balanced across all allocation failures and frees. The soft-limit expansion policy allows graphics memory growth up to half of RAM, so memory pressure behavior is intentionally permissive but potentially surprising. Locking only protects accounting, while id allocation happens outside the spinlock. Finalization assumes eviction drains all resources before cleanup.

## Test Signals
Cover GMR and MOB initialization, id exhaustion, page-budget overflow with successful expansion, page-budget overflow with `-ENOSPC`, balanced `used_gmr_pages` after eviction, debug output, and module unload/reset paths that call `vmw_gmrid_man_fini()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmrid_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ioctl.c

## Purpose
`vmwgfx_ioctl.c` implements several vmwgfx DRM ioctls that are not the main execbuf path: parameter queries, 3D capability blob copyout, surface present, and present readback. It translates userspace ABI structs into driver capability values and KMS helper calls.

## Important APIs, Types, and Functions
- `vmw_getparam_ioctl()` returns scalar capabilities such as streams, 3D support, hardware caps, FIFO caps, max framebuffer/MOB memory, screen target support, shader model support, GL43 support, and PCI device id.
- `vmw_get_cap_3d_ioctl()` copies the vmwgfx 3D capability blob into a userspace buffer, respecting GB-awareness.
- `vmw_present_ioctl()` validates clips, looks up a framebuffer and surface, then calls `vmw_kms_present()`.
- `vmw_present_readback_ioctl()` validates clips and framebuffer backing, then calls `vmw_kms_readback()` with an optional fence reply pointer.

## Control Flow
Getparam switches on the requested enum and may set file-private `gb_aware` when userspace asks for max MOB memory. 3D caps ioctl validates padding and size, allocates a vmalloc bounce buffer, copies devcaps into it, and then copies to userspace. Present and readback ioctls copy clip rectangles from userspace, lock all modesets, look up the framebuffer, validate surface or BO backing, call KMS, drop references, unlock, and free clips.

## State and Persistence Behavior
The file mutates only small runtime state: `vmw_fpriv::gb_aware` and normal object references during ioctl handling. KMS calls can submit device commands and produce fences, but that state is owned by KMS/execbuf/fence layers. No disk persistence exists.

## Dependencies and Integration Points
It depends on vmwgfx device caps helpers, overlay status, FIFO caps, PCI ids, KMS framebuffer/present/readback functions, TTM object files, user resource lookup, DRM framebuffer lookup, modeset locking, and usercopy APIs.

## Risks
Usercopy validation is central: clip pointer NULL, clip count zero, padding, and max-size handling determine ABI behavior. The `gb_aware` side effect changes later capability sizes and memory reporting for the file. Present requires a valid framebuffer and surface pairing; readback only accepts BO-backed framebuffers. Modeset locking is coarse (`drm_modeset_lock_all`) and can serialize display operations.

## Test Signals
Exercise every getparam enum, GB-aware transitions, invalid getparam ids, 3D caps truncation and copy faults, present with zero clips/null clips/invalid fb/invalid surface, readback with surface-backed fb rejection, and successful present/readback on both screen object and screen target display units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_irq.c

## Purpose
`vmwgfx_irq.c` installs and handles SVGA device interrupts. It acknowledges hardware status bits, wakes FIFO/fence waiters, defers fence and command-buffer work to a threaded IRQ handler, provides fallback wait logic when interrupts or fences are unavailable, and manages IRQ mask waiter reference counts.

## Important APIs, Types, and Functions
- `vmw_irq_handler()` is the fast hardirq handler that reads/acks status, wakes FIFO waiters, and schedules threaded fence/cmdbuf work.
- `vmw_thread_fn()` runs deferred fence updates and command-buffer IRQ processing.
- `vmw_seqno_passed()` checks fence progress using cached seqno, fresh fence update, FIFO-idle fallback, and stale-seqno detection.
- `vmw_fallback_wait()` implements a wait loop on `fence_queue` with timeout, optional FIFO-idle semantics, interruptibility, and low-CPU lazy scheduling.
- `vmw_generic_waiter_add/remove()`, `vmw_seqno_waiter_add/remove()`, and `vmw_goal_waiter_add/remove()` update `irq_mask` and hardware `SVGA_REG_IRQMASK`.
- `vmw_irq_install()` and `vmw_irq_uninstall()` allocate PCI IRQ vectors, request/free threaded IRQs, and clear device status/masks.

## Control Flow
Install allocates between one and `VMWGFX_MAX_NUM_IRQS` vectors, pre-clears pending status, requests each threaded IRQ, and records the number installed. The hardirq reads device status and masks it with the current software IRQ mask. FIFO-progress bits wake the FIFO queue immediately. Fence-goal/any-fence and command-buffer/error bits set pending thread bits and return `IRQ_WAKE_THREAD` if newly scheduled. The thread clears pending bits, updates fences and wakes `fence_queue`, or calls into the command-buffer manager. Uninstall disables the hardware mask, clears status, frees installed IRQs, and releases PCI vectors.

## State and Persistence Behavior
Runtime state includes `dev_priv->irq_mask`, waiter counters, pending thread bits, IRQ vector array/count, `last_read_seqno`, `marker_seq`, and wait queues. No disk persistence exists. IRQ mask bits remain programmed in the virtual hardware until changed or uninstalled.

## Dependencies and Integration Points
This file integrates with `vmwgfx_fence.c` for fence updates, `vmw_cmdbuf_irqthread()` for command buffers, `vmw_cmd_send_fence()`/marker sequence users through wait helpers, PCI IRQ vector APIs, Linux wait queues, and SVGA irq status/mask registers.

## Risks
Interrupt race handling is shared with fence `enable_signaling`; waiter counts must remain balanced or interrupts stay disabled/enabled incorrectly. `vmw_fallback_wait()` reports lockups after timeout but returns success unless interrupted, so callers rely on side effects and logs. FIFO-idle waits temporarily block command submission via command-buffer idle or FIFO rwsem. Install error paths record partial vector count but rely on caller cleanup for already requested IRQs.

## Test Signals
Test IRQ install/uninstall on devices with and without `SVGA_CAP_IRQMASK`, fence interrupt wakeups, FIFO-progress wakeups, command-buffer/error threaded handling, waiter add/remove balance, fallback wait timeout/interruption, and no lost wakeups under concurrent fence creation and signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.c

## Purpose
`vmwgfx_kms.c` provides the common KMS/display-mode infrastructure for vmwgfx display units. It implements atomic state helpers, framebuffer creation for BO-backed and surface-backed scanout, topology validation and layout updates, present/readback dispatch, dirty/plane update helpers, suspend/resume, mode enumeration, and `vmw_user_object` utilities shared by display paths.

## Important APIs, Types, and Functions
- Display-unit helpers include `vmw_du_init()`, `vmw_du_cleanup()`, plane/crtc/connector duplicate/reset/destroy functions, `vmw_du_primary_plane_atomic_check()`, and `vmw_du_crtc_atomic_check()`.
- Framebuffer paths are `vmw_kms_new_framebuffer_surface()`, `vmw_kms_new_framebuffer_bo()`, `vmw_kms_new_framebuffer()`, and `vmw_kms_fb_create()`.
- Mode/configuration paths include `vmw_kms_check_display_memory()`, `vmw_kms_check_implicit()`, `vmw_kms_check_topology()`, `vmw_kms_atomic_check_modeset()`, `vmw_kms_init()`, and `vmw_kms_close()`.
- Present/readback helpers are `vmw_kms_present()`, `vmw_kms_readback()`, `vmw_kms_helper_dirty()`, `vmw_kms_helper_validation_finish()`, and `vmw_du_helper_plane_update()`.
- Layout and connector helpers include `vmw_du_update_layout()`, `vmw_kms_update_layout_ioctl()`, `vmw_du_connector_detect()`, `vmw_connector_mode_valid()`, and `vmw_connector_get_modes()`.
- `vmw_user_object_*()` helpers abstract whether a display object is a raw BO or a surface with guest-memory backing.

## Control Flow
KMS init configures DRM mode limits, framebuffer creation, atomic check/commit callbacks, suggested-offset and hotplug properties, then tries screen-target, screen-object, and legacy display init in order. Framebuffer creation looks up a userspace object, validates dimensions/format/modifier, creates either a surface or BO framebuffer, attaches dirty tracking, and drops lookup references. Atomic checking validates plane scaling, primary presence, connector masks, implicit display-unit constraints, topology memory, screen-target per-output limits, and bounding-box memory. Present/readback dispatch by active display unit to STDU or SOU helpers and flushes SVGA commands after present.

## State and Persistence Behavior
The file manages in-memory DRM mode_config state, display-unit preferred layout (`pref_width`, `pref_height`, `pref_active`, `gui_x`, `gui_y`), connector properties/status, framebuffer references, BO dirty trackers, surface dirty/coherent flags, suspend atomic state, and temporary validation contexts/fences for dirty updates. Layout changes are runtime state announced through DRM hotplug events; no filesystem persistence exists.

## Dependencies and Integration Points
It depends on DRM atomic/modeset helpers, damage helpers, framebuffer helpers, vmwgfx STDU/SOU/LDU backends, BO/resource validation, surface dirty tracking, `vmwgfx_execbuf.c` fence helpers, SVGA registers, `vmwgfx_vkms` CRC work, and user object lookup from vmwgfx resource/BO layers.

## Risks
Topology validation must prevent integer overflow and memory overcommit while still matching virtual hardware limits. Surface framebuffers require scanout metadata and one-level 2D dimensions. Dirty tracking coherence between BOs and surfaces is subtle. Plane update FIFO-size callbacks must not under-reserve; the helper commits zero bytes if calculated submit size exceeds reservation. Suspend/resume depends on a saved atomic state and warns if resume is called without suspend. User-object helpers must maintain correct references across BO-backed dumb surfaces and surface-backed framebuffers.

## Test Signals
Exercise KMS init fallback order, framebuffer creation with invalid handles/formats/modifiers/sizes, surface scanout metadata rejection, atomic modesets with implicit units and topology bounds, layout ioctl overflow and memory-limit failures, STDU/SOU present/readback, dirtyfb damage clipping, plane update command-size accounting, suspend/resume/lost-device paths, and connector mode enumeration under different max width/height limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_kms.c -->
