# Research: subset-b-003770

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.h

Purpose: Declares the vmwgfx DX view/state-object classification interface used by command-buffer resource tracking. It maps SVGA3D create/destroy opcodes to compact driver enums so validation and binding code can manage shader-resource, render-target, depth-stencil, unordered-access views, and state objects consistently.

Important APIs/types: `enum vmw_view_type`, `enum vmw_so_type`, `union vmw_view_destroy`, the `vmw_view_destroy_cmds`, `vmw_view_cotables`, and `vmw_so_cotables` lookup tables, plus helpers `vmw_view_cmd_to_type()` and `vmw_so_cmd_to_type()`. Exported view APIs add/remove/lookup view resources, destroy surface or cotable view lists, recover the backing surface, and report dirtying behavior.

Control flow: This header has no runtime loop itself, but its inline command decoders are on the command-parse path. `vmw_view_cmd_to_type()` relies on the ordering of DX shader-resource/render-target/depth-stencil opcodes and special-cases UA and DSV v2. `vmw_so_cmd_to_type()` uses explicit switch cases for element layout, blend, depth-stencil, rasterizer, sampler, and stream-output objects.

State and persistence: It defines transient resource classifications and cotable mappings; persistent state lives in command-buffer resource managers, view lists, cotables, surfaces, and contexts owned elsewhere. The union layout assumes all destroy command payloads collapse to one `u32` view id.

Dependencies/integration: Depends on SVGA3D command and cotable definitions from vmwgfx device headers and is consumed by view/state-object implementation, binding cleanup, surface destruction, and command-buffer validation.

Risks: Opcode ordering assumptions are fragile when adding new SVGA commands. Any destroy payload that no longer fits a `u32` invalidates `union vmw_view_destroy`. Missing a new state-object opcode can make parser cleanup or cotable scrubbing incomplete.

Test signals: Header build tests, command-buffer tests that create and destroy every view/state-object type, surface destruction with attached views, and negative tests for unknown opcodes returning `*_max`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_so.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_stdu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_stdu.c

Purpose: Implements vmwgfx Screen Target Display Units, the KMS display path for guest-backed screen targets. It wires DRM CRTC/encoder/connector/primary/cursor objects to SVGA screen-target commands and updates screen contents from surface-backed or buffer-backed framebuffers.

Important APIs/types: `struct vmw_screen_target_display_unit`, `struct vmw_stdu_dirty`, `enum stdu_content_type`, command wrappers for define/bind/update/copy/update-image, DRM function tables, `vmw_kms_stdu_init_display()`, `vmw_kms_stdu_surface_dirty()`, and `vmw_kms_stdu_readback()`. Plane helpers prepare proxy display surfaces, pin resources, and update damage.

Control flow: Mode setup blanks and destroys any old target, then enables SVGA and defines a new target at connector GUI coordinates. Atomic disable blanks, updates, and usually destroys the target. Plane prepare chooses `SAME_AS_DISPLAY`, `SEPARATE_SURFACE`, or `SEPARATE_BO`; separate content gets a scanout GB surface sized to the CRTC. Atomic update binds the chosen display surface, then updates through CPU blit for BO content or SVGA surface copy for surface content. Dirty helpers reserve validation context, collect clips, emit copy/update commands, then fence resources.

State and persistence: Per-DU state tracks defined target, display surface, content type, dimensions, bytes-per-pixel, preferred mode, and GUI coordinates. Plane state tracks pinned user object and content type. Hardware state persists in SVGA screen-target definitions and bound surfaces until blanked/destroyed.

Dependencies/integration: Integrates DRM atomic helpers, damage clips, vblank/CRC hooks from `vmwgfx_vkms`, validation helpers, `vmw_gb_surface_define()`, BO CPU blit, cursor plane code, and SVGA FIFO command submission.

Risks: Mode memory validation depends on conservative tile alignment and memory caps. Proxy-surface lifetimes require correct pin/unpin balance. CPU blit paths can miss kernel-side dirty tracking without explicit damage propagation. VKMS callbacks need the surface set during atomic flush.

Test signals: KMS modeset/page-flip/damage tests, multi-monitor GUI-position changes, BO and surface framebuffer updates, dumb-buffer scanout, vkms CRC capture, hot unplug/disable paths, and low-memory failures during proxy surface creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_stdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_streamoutput.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_streamoutput.c

Purpose: Manages DX stream-output objects as command-buffer-managed vmwgfx resources backed by MOB memory and represented in context cotables. Stream-output hardware creation/destruction is owned by user command buffers, while this file handles resource lifetime, binding, scrubbing, and cotable list membership.

Important APIs/types: `struct vmw_dx_streamoutput`, `vmw_dx_streamoutput_add()`, `vmw_dx_streamoutput_remove()`, `vmw_dx_streamoutput_lookup()`, `vmw_dx_streamoutput_set_size()`, and `vmw_dx_streamoutput_cotable_list_scrub()`. Resource callbacks are collected in `vmw_dx_streamoutput_func`.

Control flow: Add allocates metadata, references the context stream-output cotable, initializes a guest-memory resource, stages it in the command-buffer manager, and sets `hw_destroy`. Commit notifications mark add/remove state and update cotable list membership under `binding_mutex`. Bind calls `unscrub()` to emit `DX_BIND_STREAMOUTPUT` with a MOB id, offset, and size. Unbind calls `scrub()` to bind `SVGA3D_INVALID_ID`, removes cotable linkage, fences the BO, and drops the hardware id.

State and persistence: The object stores a non-refcounted context pointer, refcounted cotable, user key/id, MOB size, cotable list node, and `committed` flag. Hardware-visible binding persists in the cotable until scrubbed or context teardown; `res->id` is used as live/stale state.

Dependencies/integration: Uses vmwgfx resource management, command-buffer resource manager, context cotables, binding mutex, MOB-backed TTM resources, and SVGA DX bind commands.

Risks: `ctx` is non-refcounted and relies on command-buffer/context lifetime ordering. `committed`, list membership, and `res->id` must remain synchronized across add/remove, bind/unbind, readback scrub, and context teardown. MOB mem_type assumptions are enforced with warnings and errors.

Test signals: DX stream-output create/remove command streams, eviction/unbind paths, context destruction with live stream outputs, MOB migration, and negative tests for non-MOB backing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_streamoutput.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_surface.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_surface.c

Purpose: Implements vmwgfx user and internal surface resources, covering legacy surfaces, guest-backed surfaces, PRIME/reference ioctls, coherent dirty tracking, surface backup handling, scanout surface creation, and DRM dumb-buffer integration.

Important APIs/types: `struct vmw_user_surface`, `struct vmw_surface_dirty`, legacy and GB `vmw_res_func` tables, `vmw_surface_define_ioctl()`, `vmw_surface_reference_ioctl()`, `vmw_gb_surface_define_ioctl()`, `vmw_gb_surface_define_ext_ioctl()`, `vmw_gb_surface_reference*_ioctl()`, `vmw_gb_surface_define()`, `vmw_dumb_create()`, and lookup helpers for BO-owned surfaces.

Control flow: Legacy define validates mip levels/formats, copies user sizes, computes per-face/mip offsets, creates cursor snooper state, initializes a resource, optionally creates a backup BO, and exposes a TTM prime object. Legacy validation allocates an SVGA surface id, emits `SURFACE_DEFINE`, and DMA uploads/downloads backup data during bind/unbind. GB surfaces choose v1-v4 define commands by SM level and array/stride features, bind/unbind MOBs, read back or invalidate, and destroy attached views/bindings. Extended GB define validates SM4/SM4.1/SM5 feature fields, creates or adopts backup buffers, enables coherent dirty tracking, and returns handles/map info.

State and persistence: Surface metadata stores format, flags, mip levels, base size, array/multisample fields, scanout, and serialized size. Resources track hardware id, backup BO, guest-memory size/offset, dirty/coherent flags, and view lists. User visibility is through TTM prime base objects and file references; dumb buffers transfer ownership to the GEM handle.

Dependencies/integration: Depends on SVGA3D surface definitions, vmwgfx resource core, BO/GEM/TTM, binding/view cleanup, cursor snooping, surface cache layout helpers, KMS scanout, and DRM dumb buffer callbacks.

Risks: User-provided sizes, formats, and flags are security-sensitive. Feature gates must match host capabilities. Dirty range translation for coherent surfaces can over/under-dirty subresources. Reference rules differ for primary/render clients and PRIME handles. Dumb-buffer surface ownership deliberately disables the user-surface refcount release hook.

Test signals: Surface ioctl ABI tests, PRIME import/reference paths, coherent mmap damage, legacy and GB eviction, scanout formats, SM4/SM5 feature rejection, cursor snoop cases, dumb-buffer creation, and fault injection on backup BO allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_surface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_system_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_system_manager.c

Purpose: Provides vmwgfx's TTM resource manager for the driver-specific system placement `VMW_PL_SYSTEM`. It wraps generic TTM resource allocation/free so vmwgfx can install a manager with `use_tt` semantics for system-backed buffer objects.

Important APIs/types: `vmw_sys_man_alloc()`, `vmw_sys_man_free()`, `vmw_sys_manager_func`, `vmw_sys_man_init()`, and `vmw_sys_man_fini()`.

Control flow: Init allocates a `ttm_resource_manager`, marks it `use_tt`, attaches vmwgfx alloc/free callbacks, initializes it with size 0, registers it for `VMW_PL_SYSTEM`, and marks it used. Fini retrieves the manager, evicts all resources, marks it unused, cleans it up, unregisters it from the TTM device, and frees the manager.

State and persistence: The manager persists in `dev_priv->bdev` as the placement manager for `VMW_PL_SYSTEM`. Each allocation creates one zeroed `ttm_resource` initialized from the requested place and BO.

Dependencies/integration: Uses DRM TTM device/resource-manager APIs and the vmwgfx private device's TTM backend. It is consumed indirectly by BO placement/move validation.

Risks: Fini assumes all users have quiesced enough for `ttm_resource_manager_evict_all()`. Incorrect `use_tt` semantics would affect vmwgfx's move/bind paths. The manager size is 0 because system memory is not limited here; other policy must enforce memory pressure.

Test signals: Driver load/unload, BO placement to `VMW_PL_SYSTEM`, eviction during teardown, suspend/resume, and TTM debug checks for leaked resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_system_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ttm_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ttm_buffer.c

Purpose: Implements vmwgfx's TTM backend: placements, DMA mapping, GMR/MOB binding, BO population, movement, fencing notifications, and helper creation of pinned populated BOs.

Important APIs/types: `vmw_vram_placement`, `vmw_sys_placement`, `vmw_tt_size`, `vmw_piter_start()`, `vmw_bo_sg_table()`, `vmw_bo_driver`, and `vmw_bo_create_and_populate()`. Internal callbacks include `vmw_ttm_map_dma()`, `vmw_ttm_bind()`, `vmw_ttm_unbind()`, `vmw_ttm_tt_create()`, `vmw_move()`, and `vmw_ttm_io_mem_reserve()`.

Control flow: TTM TT creation selects SG or normal TT based on external/imported buffers and DMA mode. Populate allocates pages or derives DMA addresses from imported SG tables. Map builds an SG table and maps it for DMA when required. Bind maps pages then binds them to GMR or MOB ids; unbind reverses device bindings and may unmap immediately in bind-mapping mode. Move binds new TT-backed non-system memory before moving, notifies vmwgfx resources/queries, uses null moves for TT-to-TT system transitions, or falls back to memcpy.

State and persistence: `struct vmw_ttm_tt` tracks dev_priv, SG table, vmw_sg_table view, MOB object, DMA mapping state, bound flag, memory type, and GMR id. BO resource placement and pin count drive whether validation moves or skips a BO.

Dependencies/integration: Integrates Linux DMA mapping, DRM TTM pool/placement/move helpers, vmwgfx GMR/MOB operations, BO/query move notifications, and PRIME external SG imports.

Risks: DMA API comments note assumptions about CPU synchronization; non-coherent platforms need scrutiny. Error paths after MOB allocation or SG mapping must not leak mappings. `vmw_ttm_bind()` sets `bound = true` after switch even if lower bind returns an error, which is a behavior worth testing. Move rollback relies on inverse notifications.

Test signals: PRIME import/export, map modes (`alloc_coherent`, `map_populate`, `map_bind`), GMR/MOB eviction, VRAM mmap offsets, suspend/unpopulate, BO move stress, and DMA debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ttm_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_va.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_va.c

Purpose: Implements overlay/video-acceleration stream handles as simple vmwgfx resources. It exposes ioctls to claim and unreference overlay streams and translates user handles to hardware stream ids.

Important APIs/types: `struct vmw_stream`, `va_stream_func`, `vmw_stream_claim_ioctl()`, `vmw_stream_unref_ioctl()`, and `vmw_user_stream_lookup()`.

Control flow: Claim delegates to `vmw_simple_resource_create_ioctl()`, whose init callback calls `vmw_overlay_claim()` and stores the resulting hardware `stream_id`. The set-argument callback returns the user-visible TTM handle through `drm_vmw_stream_arg`. Unref drops the file reference. Lookup resolves the simple resource from a TTM object file, rewrites the in/out id to the hardware stream id, and returns a refcounted resource pointer.

State and persistence: The resource stores a `vmw_simple_resource` and hardware overlay stream id. Hardware state is claimed until resource destruction, where `vmw_stream_hw_destroy()` calls `vmw_overlay_unref()`.

Dependencies/integration: Uses vmwgfx simple-resource helpers, TTM object files, overlay claim/unref functions, and DRM ioctl argument structures.

Risks: User handles and hardware stream ids are intentionally different, so lookup callers must respect the in/out rewrite. Overlay unref failures are only warned. The resource has no guest memory and is not evictable, so lifetime bugs show up as leaked or double-freed overlay ids.

Test signals: Stream claim/unref ioctl tests, lookup with invalid handles, multiple clients exhausting overlay ids, and teardown while streams remain referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_va.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.c

Purpose: Provides the shared vmwgfx validation transaction layer for command submission and KMS updates. It collects BOs/resources, merges duplicates, reserves and validates them in a safe order, tracks dirty/backup changes, and commits or reverts the batch.

Important APIs/types: Internal `vmw_validation_bo_node` and `vmw_validation_res_node`; exported `vmw_validation_add_bo()`, `vmw_validation_add_resource()`, `vmw_validation_res_switch_backup()`, `vmw_validation_res_set_dirty()`, `vmw_validation_prepare()`, `vmw_validation_done()`, `vmw_validation_revert()`, `vmw_validation_unref_lists()`, and preload helpers.

Control flow: Add operations allocate metadata from a page-backed context allocator and optionally insert hash items for duplicate detection. Resource reservation splices context-priority resources first, reserves each resource, adds its backup BO, and counts coherent backup switches. Prepare optionally locks a resource mutex, reserves resources, reserves BOs with TTM execbuf utilities, validates BO placement with retry/eviction, scans dirty BOs, and validates resources. Done fences BOs, unreserves resources while applying dirty/backup updates, unlocks, and unreferences lists. Revert backs off BO reservations, unreserves resources without committing changes, unlocks, and frees context memory.

State and persistence: Validation context owns temporary lists, hash links, allocator pages, ww ticket, and optional resource mutex. Persistent effects occur only at commit: BO fences, resource dirty flags, and backup BO/offset switches.

Dependencies/integration: Uses TTM execbuf reservation/fencing, vmwgfx BO placement/dirty tracking, resource reserve/validate/unreserve operations, command submission, KMS helpers, and context/cotable ordering.

Risks: Reservation ordering is central to deadlock avoidance. Hash entries must be dropped before cleanup when external locks might be held. Coherent dirty tracker accounting on backup switches must be balanced on backoff. CPU writers cause `-EBUSY` during BO validation.

Test signals: Execbuf validation with duplicate resources, interrupted reservations, coherent backup switches, dirty set/clear, BO validation failure retries, KMS update validation, and lockdep under context/cotable batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.h

Purpose: Declares the vmwgfx validation context ABI used internally by execbuf, KMS, and resource code. It defines dirty flags, context initialization, TTM reservation wrappers, and exported validation transaction functions.

Important APIs/types: `VMW_RES_DIRTY_NONE`, `VMW_RES_DIRTY_SET`, `VMW_RES_DIRTY_CLEAR`, `struct vmw_validation_context`, `DECLARE_VAL_CONTEXT`, `vmw_validation_has_bos()`, `vmw_validation_bo_reserve()`, `vmw_validation_bo_fence()`, `vmw_validation_align()`, and prototypes for add/prepare/done/revert/preload helpers.

Control flow: The macro initializes all lists and default fields for stack-allocated validation contexts. Inline BO reserve/fence delegates to TTM execbuf utilities using the context ww ticket. Callers typically declare a context, add resources/BOs, call `vmw_validation_prepare()`, submit commands, then call `vmw_validation_done()` or `vmw_validation_revert()`.

State and persistence: The context stores temporary lists, optional software hash context, allocator page list, ww acquire ticket, optional resource mutex, duplicate-merge flag, and allocator cursor. It should not persist past one validation transaction.

Dependencies/integration: Depends on Linux list/hashtable/ww mutex headers, TTM execbuf utilities, vmwgfx BO/resource/fence types, and the implementation in `vmwgfx_validation.c`.

Risks: `DECLARE_VAL_CONTEXT` must stay in sync with struct fields. Dirty flags are bit semantics, but implementation stores a single final dirty boolean. Callers must choose `merge_dups` carefully and must not reuse a context after cleanup.

Test signals: Compile coverage for all users, lockdep/ww mutex tests, validation transactions with no BOs, duplicate merge with and without hash context, and error paths that call revert/unref exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.c

Purpose: Adds optional virtual KMS-style vblank and CRC support to vmwgfx screen-target display. It simulates vblank with high-resolution timers and computes CRCs from the current scanout surface for DRM pipe CRC tests.

Important APIs/types: `vmw_vkms_init()`, cleanup, vblank enable/disable/timestamp callbacks, CRTC init/cleanup/atomic begin/flush/enable/disable hooks, CRC source functions, `vmw_vkms_set_crc_surface()`, and the lock helpers `vmw_vkms_modeset_lock*()`, `vmw_vkms_vblank_trylock()`, `vmw_vkms_unlock()`.

Control flow: Init reads `guestinfo.vmwgfx.vkms_enable`, initializes DRM vblank if enabled, and creates an ordered CRC workqueue. Enabling vblank computes timing constants and starts an hrtimer. The timer advances by frame period, handles DRM vblank, tries to lock against modeset, and queues CRC work when enabled. The worker references the current surface, cleans/synchronizes it with a fence, maps the backup BO, computes crc32 row-by-row, then emits CRC entries for every pending frame. Atomic begin/flush lock/unlock the VKMS state and deliver vblank events.

State and persistence: Each display unit holds timer period, current CRC surface reference, atomic lock state, CRC pending frame range, spinlock, and work item. Device state stores vkms enablement and CRC workqueue.

Dependencies/integration: Integrates DRM vblank/CRC APIs, vmwgfx KMS display units, surfaces/resources/BO mapping, host guestinfo, hrtimer, workqueues, dma fences, and crc32.

Risks: Locking bridges timer atomic context and non-atomic modeset code using an atomic state with bounded spin waits. CRC worker must unreference surfaces and not race disable/cleanup. `vmw_surface_sync()` assumes a backup BO exists. Falling behind batches identical CRC values over a frame range.

Test signals: IGT pipe CRC tests, vblank timestamp/event tests, enable/disable races, modeset while CRC enabled, cleanup with pending work, and guestinfo-disabled fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.h

Purpose: Declares the vmwgfx VKMS/vblank/CRC integration surface used by STDU and display-unit code. It keeps the optional vblank simulator interface separate from the main KMS implementation.

Important APIs/types: Init/cleanup, modeset/vblank lock helpers, vblank timestamp/enable/disable callbacks, CRTC lifecycle and atomic hooks, CRC source verification/setters, and `vmw_vkms_set_crc_surface()`.

Control flow: Callers initialize device-wide VKMS once, initialize each CRTC, then route DRM CRTC functions through these declarations. STDU atomic flush sets the CRC surface and calls VKMS flush; vblank callbacks use the lock helpers to coordinate with modesets.

State and persistence: The header declares no state directly; state is embedded in `struct vmw_private` and per-display-unit VKMS fields defined elsewhere.

Dependencies/integration: Forward-declares DRM CRTC/atomic state and vmwgfx private/surface types and depends on hrtimer and basic Linux types. Implemented by `vmwgfx_vkms.c`, consumed by `vmwgfx_stdu.c` and shared DU code.

Risks: Function signatures must match DRM callback expectations. Lock helpers are part of a cross-file concurrency protocol; misuse can expose incomplete modeset state to timer callbacks.

Test signals: Header compile tests, STDU builds with VKMS callbacks, DRM vblank/CRC callback registration, and lock/unlock pairing under atomic modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Kconfig

Purpose: Defines Kconfig options for the Intel xe DRM driver, including the main `DRM_XE` module, display support, DP tunnel support, GPU SVM, pagemap support, force-probe policy, and debug/profile menus.

Important APIs/types: `config DRM_XE`, `DRM_XE_DISPLAY`, `DRM_XE_DP_TUNNEL`, `DRM_XE_GPUSVM`, `DRM_XE_PAGEMAP`, `DRM_XE_FORCE_PROBE`, plus sourced `Kconfig.debug` and `Kconfig.profile`.

Control flow: Kconfig dependency resolution gates whether xe can be built, which subsystems are selected, and whether optional display/SVM/pagemap/tunnel functionality is compiled. The main driver depends on DRM/PCI and constrains page size unless compile-test/broken. Display support is only exposed for module builds with I/O port support.

State and persistence: Configuration choices persist in the kernel `.config` and alter object lists, module parameters, and compiled code. `DRM_XE_FORCE_PROBE` becomes the default value for the `xe.force_probe` module parameter.

Dependencies/integration: Selects DRM helpers, TTM, scheduler, GPUVM/GPUSVM, display helpers, ACPI/video dependencies, sound HDA integration, CEC, MMU notifier, auxiliary bus, and other kernel infrastructure.

Risks: `select` can force dependency stacks in surprising ways, especially ACPI video dependencies. Page-size gating limits architecture coverage. Display support depends on module build constraints. Force-probe strings can enable unsupported hardware or block supported devices.

Test signals: Kconfig allmodconfig/allyesconfig/randconfig, module and built-in builds, display-disabled builds, SVM-disabled UML builds, and force_probe parameter parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Makefile

Purpose: Defines the xe driver build graph: compiler flags, generated workaround sources, core object list, optional subsystem objects, shared i915 display object compilation, debug/test objects, header tests, and final `xe.o` module linkage.

Important APIs/types: `xe-y`, conditional `xe-$(CONFIG_...)` lists, generated `xe_wa_oob` and `xe_device_wa_oob` rules, `subdir-ccflags-*`, display shared-object rule, `hdrtest` machinery, and `obj-$(CONFIG_DRM_XE) += xe.o`.

Control flow: Kbuild first builds host generator `xe_gen_wa_oob`, produces generated workaround C/H files from rules, then compiles objects in sorted lists. Conditional blocks add I2C, SVM/userptr, hwmon, PMU, configfs, SR-IOV PF/VF, display, debugfs, fbdev, DP tunnel, tests, and VFIO support. Display objects are built partly from xe sources and partly from i915 display sources with compatibility include paths.

State and persistence: Generated workaround files live under `$(obj)/generated` for the build. Header test targets are only always-built under `CONFIG_DRM_XE_WERROR`.

Dependencies/integration: Integrates Kbuild, generated sources, i915 display source reuse, xe Kconfig symbols, debugfs, KUnit, PCI IOV, and many internal xe subsystems.

Risks: Object-list ordering and generated-header dependencies must remain correct. Shared i915 display compilation can break when include paths or source APIs change. Header tests intentionally compile each header twice and run kernel-doc with `-Werror`, exposing documentation or include self-containment problems.

Test signals: Incremental builds from clean tree, display enabled/disabled builds, `CONFIG_DRM_XE_WERROR` header tests, SR-IOV and debugfs configs, generated workaround regeneration, and module link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_command_header_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_command_header_abi.h

Purpose: Defines the packed Intel GSC MTL HECI command header used for xe kernel submissions to Graphics Security Controller firmware.

Important APIs/types: `struct intel_gsc_mtl_header`, `GSC_HECI_VALIDITY_MARKER`, `MTL_GSC_HEADER_VERSION`, `GSC_OUTFLAG_MSG_PENDING`, and `GSC_INFLAG_MSG_CLEANUP`.

Control flow: There is no executable flow. Producers fill the header before submitting a GSC packet; consumers validate marker, version, size, flags, status, and message handles on completion. Pending responses feed `gsc_message_handle` back into resubmissions.

State and persistence: The packed header is a firmware ABI layout containing session ids, firmware message handles, payload size, flags, and status. It persists only in command buffers shared with firmware.

Dependencies/integration: Consumed by `xe_gsc_submit.c` and other GSC code that writes/reads fields in mapped BO memory. Uses Linux integer types and bit macros from included contexts.

Risks: Packed layout, field widths, and the lower-20-bit `message_size` rule are firmware-contract sensitive. Confusing input vs output flags can cause leaks or missed pending-message continuation. Endianness and unaligned access assumptions must match xe map helpers.

Test signals: GSC submit unit tests or integration tests, firmware compatibility/version exchange, pending-message resubmission, malformed marker/status handling, and compile-time structure-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_command_header_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_mkhi_commands_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_mkhi_commands_abi.h

Purpose: Defines the MKHI GSC client ABI used by xe to query GSC host compatibility version information.

Important APIs/types: `HECI_MEADDRESS_MKHI`, `struct gsc_mkhi_header`, `MKHI_GROUP_ID_GFX_SRV`, `MKHI_GFX_SRV_GET_HOST_COMPATIBILITY_VERSION`, `gsc_get_compatibility_version_in`, and `gsc_get_compatibility_version_out`.

Control flow: The driver emits a generic MKHI header with the graphics-service group and compatibility-version command, submits it through the GSC transport, then reads project/compat major/minor fields from the output.

State and persistence: Packed request/response structures live in a transient GSC packet. The result may influence driver/GSC compatibility decisions elsewhere but this header itself stores no driver state.

Dependencies/integration: Included by `xe_gsc.c` compatibility-check code and wrapped by the generic GSC command header/submit path.

Risks: Header/result byte layout is a firmware ABI. Missing validation of `result` or reserved fields in consumers could hide firmware incompatibility. Version-field interpretation must remain aligned with firmware policy.

Test signals: GSC firmware version query during probe, simulated unsupported compatibility versions, packed-size checks, and error logging for nonzero MKHI results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_mkhi_commands_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_proxy_commands_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_proxy_commands_abi.h

Purpose: Defines the firmware proxy-message ABI for GSC-mediated communication among KMD, GSC, and CSME.

Important APIs/types: `HECI_MEADDRESS_PROXY`, `struct xe_gsc_proxy_header`, masks `GSC_PROXY_TYPE` and `GSC_PROXY_PAYLOAD_LENGTH`, addressing constants for KMD/GSC/CSME, and `enum xe_gsc_proxy_type`.

Control flow: Proxy handlers parse `hdr` into type and payload length, inspect source/destination, and process query/payload/end/notification messages. This header defines the wire format only.

State and persistence: Proxy packets are transient firmware messages. Status and addressing are stored in the packed header for each exchange.

Dependencies/integration: Used by xe GSC proxy code (`xe_gsc_proxy.*`) and transported through the generic GSC HECI submission path.

Risks: Payload length mask must be applied before buffer access. Invalid or unexpected proxy type/address combinations should be rejected to avoid confused routing. Packed ABI changes require synchronized firmware and driver updates.

Test signals: Proxy query/payload/end sequences, notification handling, invalid length/type fuzzing, and GSC proxy start/teardown during driver load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_proxy_commands_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_pxp_commands_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_pxp_commands_abi.h

Purpose: Defines xe's GSC PXP firmware command ABI for protected content operations, including HuC authentication, PXP session initialization, and stream-key invalidation.

Important APIs/types: `HECI_MEADDRESS_PXP`, `PXP_APIVER()`, `PXP_MAX_PACKET_SIZE`, `enum pxp_status`, `struct pxp_cmd_header`, command ids `PXP43_*`, and packed request/response structs for HuC auth, create ARB session, and invalidate stream key.

Control flow: Consumers build `pxp_cmd_header` with API version, command id, stream/session fields, and payload length; firmware returns status in the union. Init-session requests encode valid/app/session id bits and ARB protection mode; invalidate requests target an existing stream/session.

State and persistence: PXP session/stream identity is encoded in header bitfields. Persistent protected-session state lives in firmware and xe PXP management code, not this header.

Dependencies/integration: Used by xe PXP/HuC submit paths over the GSC HECI client. Relies on Linux sizes/types and GENMASK/BIT definitions available to consumers.

Risks: The command header union changes meaning by direction, so consumers must not read input bitfields as output status. Packet size excludes the top-level GSC header. Firmware status handling must distinguish retryable not-ready from fatal platform/configuration failures.

Test signals: HuC auth-only flow, PXP session create/destroy, stream-key invalidation, unsupported API version, platform configuration errors, and packed layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_pxp_commands_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_abi.h

Purpose: Defines GuC host-to-firmware action ids, HXG message field masks, legacy action enums, context registration parameter offsets, status enums, log controls, TLB invalidation modes, and GuC-to-GuC registration fields used by xe.

Important APIs/types: `GUC_ACTION_HOST2GUC_SELF_CFG`, `HOST2GUC_SELF_CFG_*`, `GUC_ACTION_HOST2GUC_CONTROL_CTB`, `enum xe_guc_action`, preemption options, context/multi-LRC offset enums, report/sleep/status enums, TLB invalidation type/mode definitions, and G2G field masks.

Control flow: There is no local execution; xe GuC CT/MMIO code builds action arrays using these ids and offsets. Self-config messages carry KLV key/length/value fields. CTB control enables/disables command transport buffers. TLB invalidation users select full/page/context/GUC invalidation and heavy/lite completion semantics.

State and persistence: These constants define firmware-visible protocol state and message array positions. Persistent state lives in GuC firmware, CT buffers, registered contexts, scheduling policies, and xe GuC data structures.

Dependencies/integration: Included by GuC submit, TLB invalidation, page reclaim, context registration, logging, SR-IOV relay/control, and firmware communication code. Depends on HXG message macros from other ABI headers.

Risks: Numeric action ids and parameter offsets are strict firmware ABI. Lite TLB invalidation requires software proof that stale translations are no longer in use. Context registration length/offset mismatches can hang scheduling. New firmware actions must not collide with legacy ids.

Test signals: GuC CT selftests, context registration/multi-LRC scheduling, TLB invalidation completion paths, page reclaim, logging controls, suspend S-state transitions, and firmware ABI compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_slpc_abi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_slpc_abi.h

Purpose: Defines the GuC SLPC power-control ABI: shared data layout, parameter ids, task/global states, event ids, task status/frequency masks, power profiles, and host-to-GuC PC/SLPC request actions.

Important APIs/types: shared-data size macros, `enum slpc_task_enable`, `enum slpc_global_state`, `enum slpc_param_id`, media ratio/GUCRC/event enums, `struct slpc_task_state_data`, `struct slpc_shared_data`, `enum slpc_power_profile`, `GUC_ACTION_HOST2GUC_PC_SLPC_REQUEST`, and `GUC_ACTION_HOST2GUC_SETUP_PC_GUCRC`.

Control flow: xe GuC PC code maps/fills `slpc_shared_data`, sets/unsets override parameters, sends SLPC events with event id/argc/data, and can switch GUCRC between host and firmware control. Firmware updates global/task state and interprets override bitfields and values.

State and persistence: The two-page packed shared buffer persists while SLPC is active. It contains header, global state, display data address, task state, override bitfields/values, reserved padding, and a legacy mode-definition page.

Dependencies/integration: Used by xe GuC power-control/frequency/sysfs paths. Relies on GuC HXG message macros and Linux integer types.

Risks: Shared-data padding and cacheline/page sizing are ABI-sensitive. `HOST2GUC_PC_SLPC_REQUEST_MSG_MAX_LEN` references `HOST2GUC_PC_SLPC_REQUEST_REQUEST_MSG_MIN_LEN`, which appears misspelled and should be build-covered. Parameter ids must match firmware expectations; wrong frequency masks can misreport or misconfigure power limits.

Test signals: GuC PC init/start/stop, min/max frequency sysfs, power profile changes, RC6/GUCRC mode transitions, SLPC reset/set/unset events, shared-structure size assertions, and builds that exercise the max-len macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/guc_actions_slpc_abi.h -->
