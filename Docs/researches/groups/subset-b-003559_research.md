# Research: subset-b-003559

Grouped source research for subset B work item `subset-b-003559`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_helper.c

## Purpose
`drm_atomic_helper.c` is the central DRM/KMS helper implementation for atomic modeset checking, commit sequencing, plane updates, legacy API compatibility, suspend/resume state capture, and legacy page flips on top of the atomic core. It is a shared helper library for display drivers that implement the standard CRTC, encoder, connector, bridge, and plane helper callbacks but do not want to hand-roll the full atomic check and commit pipeline.

The file is not Ceph-specific despite the repository path. It is DRM core infrastructure in the vendored Linux source tree. Its responsibilities span two broad contracts: validating a staged `struct drm_atomic_state` before it can become visible, and committing that state to software and hardware in an order that preserves locking, vblank/event signaling, framebuffer lifetime, and nonblocking commit ordering.

## Important APIs, Types, and Functions
The modeset validation entry point is `drm_atomic_helper_check_modeset()`. It detects mode, enable, active, routing, and connector changes; resolves encoders with `atomic_best_encoder`, `best_encoder`, or `drm_connector_get_single_encoder()`; rejects incompatible encoder/CRTC combinations; adds affected connectors, planes, and bridges; validates clone masks; runs bridge and encoder `mode_valid` and `atomic_check`/`mode_fixup` paths; and finishes with CRTC `mode_fixup`. `handle_conflicting_encoders()`, `update_connector_routing()`, `set_best_encoder()`, `steal_encoder()`, `mode_valid()`, and `mode_fixup()` are the key internal helpers behind that API.

Plane validation is split into `drm_atomic_helper_check_plane_state()`, `drm_atomic_helper_check_crtc_primary_plane()`, and `drm_atomic_helper_check_planes()`. These helpers derive source/destination rectangles, apply rotation for scaling checks, clip visible regions, enforce full-CRTC primary coverage when requested, mark `planes_changed`, check damage clips, and dispatch driver plane/CRTC atomic checks. `drm_atomic_helper_check()` composes modeset checking, optional z-position normalization through `drm_atomic_normalize_zpos()`, plane checking, cursor async eligibility, and self-refresh state adjustment.

Commit helpers include disable-side functions (`drm_atomic_helper_commit_encoder_bridge_disable()`, `drm_atomic_helper_commit_crtc_disable()`, `drm_atomic_helper_commit_encoder_bridge_post_disable()`), state/legacy update functions (`drm_atomic_helper_update_legacy_modeset_state()`, `drm_atomic_helper_calc_timestamping_constants()`, `drm_atomic_helper_commit_crtc_set_mode()`), enable-side functions (`drm_atomic_helper_commit_encoder_bridge_pre_enable()`, `drm_atomic_helper_commit_crtc_enable()`, `drm_atomic_helper_commit_encoder_bridge_enable()`), and combined tails (`drm_atomic_helper_commit_tail()` and `drm_atomic_helper_commit_tail_rpm()`). `drm_atomic_helper_commit()` is the default atomic commit implementation used by drivers.

Synchronization and lifetime APIs are centered on `struct drm_crtc_commit`. `drm_atomic_helper_setup_commit()` allocates commit objects, reserves flip completions/events, enforces nonblocking backpressure, attaches commit references to CRTCs/connectors/planes, and optionally calls a driver `atomic_commit_setup` hook. `drm_atomic_helper_wait_for_dependencies()`, `drm_atomic_helper_fake_vblank()`, `drm_atomic_helper_commit_hw_done()`, and `drm_atomic_helper_commit_cleanup_done()` provide the state machine for waiting, signaling hardware completion, and signaling cleanup completion. `drm_atomic_helper_wait_for_fences()`, `drm_atomic_helper_wait_for_vblanks()`, and `drm_atomic_helper_wait_for_flip_done()` handle DMA fences and display completion.

Plane resource APIs include `drm_atomic_helper_prepare_planes()`, `drm_atomic_helper_unprepare_planes()`, `drm_atomic_helper_commit_planes()`, `drm_atomic_helper_commit_planes_on_crtc()`, `drm_atomic_helper_disable_planes_on_crtc()`, and `drm_atomic_helper_cleanup_planes()`. Legacy compatibility wrappers include `drm_atomic_helper_update_plane()`, `drm_atomic_helper_disable_plane()`, `drm_atomic_helper_set_config()`, `drm_atomic_helper_disable_all()`, `drm_atomic_helper_reset_crtc()`, `drm_atomic_helper_shutdown()`, `drm_atomic_helper_page_flip()`, and `drm_atomic_helper_page_flip_target()`. Power-management state APIs are `drm_atomic_helper_duplicate_state()`, `drm_atomic_helper_suspend()`, `drm_atomic_helper_commit_duplicated_state()`, and `drm_atomic_helper_resume()`. `drm_atomic_helper_bridge_propagate_bus_fmt()` is a small exported bridge format helper.

## Control Flow
The normal validation flow begins with a caller allocating and populating `struct drm_atomic_state`, then invoking `drm_atomic_helper_check()` through the device's `atomic_check` hook. `drm_atomic_helper_check_modeset()` first compares old/new CRTC state to set `mode_changed`, `active_changed`, `connectors_changed`, and `no_vblank`, then resolves connector routing and encoder assignment. If a full modeset is needed, it expands the state to include all affected connectors and planes before running connector checks, bridge inclusion, `mode_valid`, and fixup callbacks. After optional zpos normalization, `drm_atomic_helper_check_planes()` runs plane checks first and CRTC checks second.

The default commit path in `drm_atomic_helper_commit()` has a fail-capable phase and a point-of-no-return phase. Async updates use `drm_atomic_helper_prepare_planes()`, `drm_atomic_helper_async_commit()`, and `drm_atomic_helper_unprepare_planes()` without a full software-state swap. Normal commits call `drm_atomic_helper_setup_commit()`, initialize work, prepare framebuffer/writeback resources, optionally wait for incoming fences for blocking commits, then call `drm_atomic_helper_swap_state()`. After the swap, nonblocking commits queue `commit_work` on `system_dfl_wq`; blocking commits call `commit_tail()` inline.

`commit_tail()` waits for post-swap fences and prior commit dependencies, records self-refresh timing context, calls the driver `atomic_commit_tail` hook if present or `drm_atomic_helper_commit_tail()` otherwise, updates self-refresh timing averages, marks cleanup done, and drops the atomic state reference. The default tail disables old outputs, commits planes, enables new outputs, fakes vblank where necessary, marks hardware done, waits for vblanks, and cleans old plane resources. The runtime-PM variant enables modesets before committing planes with `DRM_PLANE_COMMIT_ACTIVE_ONLY`.

Suspend/resume flow duplicates all CRTC, plane, colorop, and connector states, disables all active outputs, and later resets mode config and commits the duplicated state with refreshed old-state pointers. Legacy set_config and page-flip flows allocate temporary atomic states and delegate to the normal atomic commit machinery, preserving older IOCTL behavior while using atomic checks and sequencing underneath.

## State and Persistence Behavior
The file operates on persistent DRM object state pointers: `crtc->state`, `plane->state`, `connector->state`, `colorop->state`, and private object states. `drm_atomic_helper_swap_state()` atomically replaces these pointers, moves old states into the atomic state for cleanup, and adds CRTC commit objects to `crtc->commit_list`. Plane pointer swaps are wrapped in `drm_panic_lock()`/`drm_panic_unlock()` so panic display paths see coherent plane state.

Commit state persists across asynchronous work through `struct drm_crtc_commit` completions: `flip_done`, `hw_done`, and `cleanup_done`. Old states keep commit references so later commits can wait on prior hardware completion and cleanup. Events are attached to `drm_crtc_state.event`, consumed by drivers or fake-vblank paths, and guarded by warnings if a backend fails to consume them by `commit_hw_done`.

Framebuffer and writeback resources are prepared before the software swap and cleaned after the old state is no longer displayed. Incoming plane fences are stored in `drm_plane_state.fence`, deadlines may be set to the next vblank for single-CRTC updates, and fence references are cleared after waits. Suspend state returned by `drm_atomic_helper_suspend()` is intentionally persistent until the driver passes it to resume and then releases it.

Legacy fields such as `connector->encoder`, `encoder->crtc`, `connector->dpms`, `crtc->mode`, `crtc->enabled`, `crtc->x`, and `crtc->y` are maintained for transition-era code but are only safe for code called from atomic commit-tail context.

## Dependencies and Integration Points
This file integrates with nearly every DRM KMS subsystem: atomic state management (`drm_atomic_*`), UAPI state setters from `drm_atomic_uapi.c`, blend/zpos normalization from `drm_blend.c`, bridges, connectors, encoders, CRTCs, planes, writeback connectors, framebuffer/GEM prepare helpers, DMA fences, vblank/event delivery, self-refresh helpers, damage helpers, panic display locking, and modeset lock acquire/backoff.

Drivers plug in through `drm_crtc_helper_funcs`, `drm_encoder_helper_funcs`, `drm_connector_helper_funcs`, `drm_plane_helper_funcs`, `drm_bridge_funcs`, and `drm_mode_config_helper_funcs`. Important hooks include `atomic_check`, `mode_fixup`, `mode_valid`, `atomic_mode_set`, `mode_set_nofb`, `atomic_begin`, `atomic_update`, `atomic_disable`, `atomic_enable`, `atomic_flush`, `prepare_fb`, `cleanup_fb`, `begin_fb_access`, `end_fb_access`, `atomic_commit_tail`, and `atomic_commit_setup`.

## Risks
The highest risk is sequencing. Moving waits, state swaps, event creation, or cleanup can cause use-after-free of framebuffer or state objects, missed vblank events, nonblocking commit reordering, visible tearing, or permanent stalls. The point-of-no-return comment in `drm_atomic_helper_commit()` is real: failures after software state is swapped are not recoverable through normal error returns.

Encoder routing is another fragile area. Incorrect `best_encoder`, clone-mask, or conflict handling can assign one encoder to multiple connectors or fail to disable legacy conflicting connectors. Connector unregister handling is intentionally racy but constrained; changing it can re-enable removed displays or reject valid resume paths.

Plane commits depend on driver callback contracts. Calling `atomic_update` or `atomic_disable` for inactive CRTCs, or suppressing those calls with the wrong flags, can break runtime PM or leave hardware planes active. Async commits intentionally support only narrow single-plane updates unless drivers opt into more checks; broadening this path without the same ordering guarantees risks overwriting synchronous state.

Commit completion tracking must remain balanced. Missing `commit_hw_done()` or `commit_cleanup_done()` calls cause later commits to hang or time out; early event frees can double-free reserved events; forgotten commit refs can leak. Suspend/resume assumes duplicated state is safe for the driver, which is not true for every private state extension.

## Test Signals
Build coverage should include DRM core and representative atomic drivers with `W=1`-style warning checks. Runtime signals include passing IGT atomic modeset, plane, cursor, async flip, writeback, suspend/resume, DPMS, page-flip, and event tests; no vblank or flip_done timeouts in logs; no `WARN_ON` from missing vblank-off, unconsumed events, or state pointer mismatches; and correct behavior under `DRM_MODE_ATOMIC_NONBLOCK`, `DRM_MODE_ATOMIC_TEST_ONLY`, and `DRM_MODE_PAGE_FLIP_ASYNC`.

Useful stress tests are repeated multi-CRTC nonblocking commits, hot-unplug during atomic checks, legacy `SETCRTC` and page-flip IOCTLs, framebuffer fence waits, writeback with out-fences, cursor-only updates, suspend/resume after active display use, and teardown through `drm_atomic_helper_shutdown()`. KASAN/KCSAN/KFENCE signals are particularly valuable because bugs often manifest as lifetime or ordering races rather than deterministic return-code failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_state_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_state_helper.c

## Purpose
`drm_atomic_state_helper.c` provides default reset, duplicate, destroy, and validation helpers for DRM atomic per-object state. It is the companion to the atomic commit helpers: drivers can use these functions as their CRTC, plane, connector, bridge, and private-object state hooks when they do not need fully custom state management, or call the underscored helpers when they subclass core DRM state structures.

The file's core job is reference and default-value correctness. Atomic commits duplicate current state, mutate the duplicates, swap them into live objects, and later destroy old state. These helpers ensure blobs, framebuffers, fences, commit objects, connector references, writeback jobs, TV defaults, bridge state, and color/blend defaults are initialized and released consistently.

## Important APIs, Types, and Functions
CRTC state helpers are `__drm_atomic_helper_crtc_state_reset()`, `__drm_atomic_helper_crtc_reset()`, `drm_atomic_helper_crtc_reset()`, `__drm_atomic_helper_crtc_duplicate_state()`, `drm_atomic_helper_crtc_duplicate_state()`, `__drm_atomic_helper_crtc_destroy_state()`, and `drm_atomic_helper_crtc_destroy_state()`. They set `crtc`, default `background_color`, reset vblank where available, refcount mode/color blobs on duplication, clear derived change flags and transient commit/event/async fields, cancel self-refresh on new updates, and release blobs plus commit resources on destruction.

Plane helpers are `__drm_atomic_helper_plane_state_reset()`, `__drm_atomic_helper_plane_reset()`, `drm_atomic_helper_plane_reset()`, `__drm_atomic_helper_plane_duplicate_state()`, `drm_atomic_helper_plane_duplicate_state()`, `__drm_atomic_helper_plane_destroy_state()`, and `drm_atomic_helper_plane_destroy_state()`. They initialize rotation, alpha, premultiplied blend mode, default color encoding/range, optional zpos, color pipeline, cursor hotspot defaults, and release framebuffer, fence, commit, and damage-clip blob references.

Connector helpers are `__drm_atomic_helper_connector_state_reset()`, `__drm_atomic_helper_connector_reset()`, `drm_atomic_helper_connector_reset()`, TV helpers (`drm_atomic_helper_connector_tv_margins_reset()`, `drm_atomic_helper_connector_tv_reset()`, `drm_atomic_helper_connector_tv_check()`), duplication/destruction helpers, and writeback cleanup. Connector duplication gets an extra connector reference if the state is linked to a CRTC, refs HDR metadata, clears commit, and intentionally drops one-shot writeback jobs.

Private object and bridge helpers are `__drm_atomic_helper_private_obj_create_state()`, `__drm_atomic_helper_private_obj_duplicate_state()`, `__drm_atomic_helper_bridge_duplicate_state()`, `drm_atomic_helper_bridge_duplicate_state()`, `drm_atomic_helper_bridge_destroy_state()`, `__drm_atomic_helper_bridge_reset()`, and `drm_atomic_helper_bridge_reset()`. They initialize `drm_private_obj` state ownership and provide a default `struct drm_bridge_state` lifecycle for bridge drivers.

## Control Flow
At driver load or after `drm_mode_config_reset()`, object reset hooks call these helpers to allocate or install zeroed state and seed defaults. CRTC reset also resets vblank accounting when the device has vblank support. Plane and connector resets free any prior state before installing new empty state.

During atomic state construction, DRM core calls duplicate hooks. The helper duplicate flow shallow-copies the current state and then fixes ownership: blob and framebuffer references are incremented, transient fields are cleared, and one-shot objects such as writeback jobs are not copied. The duplicated state can then be safely modified by UAPI property setters and driver atomic checks.

On state clear or object teardown, destroy helpers release resources acquired by reset/duplicate/property paths. CRTC destruction handles a subtle nonblocking commit case: if a commit object exists and an event was attached but abort completion is still set, it drops the extra completion reference and frees any stored event before putting the commit. Plane destruction puts framebuffers, fences, commits, and damage blobs. Connector destruction drops connector refs, commit refs, writeback jobs, and HDR metadata.

TV check flow compares old and new connector TV fields. Mode changes force `crtc_state->mode_changed`; margins and analog TV properties force `connectors_changed`, causing a full modeset path where needed.

## State and Persistence Behavior
The helpers manage the persistent `->state` pointer attached to each DRM object and the temporary duplicate states carried inside `struct drm_atomic_state`. They do not persist external configuration themselves, but they preserve references to persistent DRM resources while a staged or old state is alive.

Default state includes black opaque CRTC background, plane rotate-0, opaque alpha, premultiplied blending, property-defined color encoding/range, zpos, normalized_zpos, and cursor hotspot values. Connector TV defaults are taken from property defaults and command-line mode overrides. Self-refresh state is explicitly not preserved as active on duplicated CRTC state when a new update is available; effective active state is recomputed and `self_refresh_active` is cleared.

Writeback jobs are one-shot and are intentionally excluded from duplicated connector state. Commit pointers are transient synchronization state and are cleared in duplicates; old states keep commit references only through the commit helper flow in `drm_atomic_helper.c`.

## Dependencies and Integration Points
This file depends on core DRM types and helpers for atomic state, properties, connectors, CRTCs, planes, bridges, framebuffers, writeback, vblank, blend constants, DMA fences, and memory allocation. It is used directly by drivers that set their funcs to default atomic reset/duplicate/destroy hooks and indirectly by `drm_atomic_helper_duplicate_state()`, `drm_atomic_helper_swap_state()`, and normal atomic cleanup.

Integration with `drm_atomic_uapi.c` is through property blobs and state fields that UAPI setters later mutate, including color management blobs, HDR metadata, TV fields, zpos, alpha, rotation, color pipeline, and damage clips. Integration with `drm_atomic_helper.c` is through commit refs, self-refresh fields, vblank reset, and state destruction after commits.

## Risks
Most risks are lifetime bugs. Forgetting to get or put blobs, framebuffers, connector refs, fences, writeback jobs, or commit objects causes leaks, dangling pointers, or double frees. Because atomic state is copied with `memcpy()`, every newly added pointer field in a core state structure must be audited here for reference transfer, transient clearing, and destruction.

Default values are also ABI-visible. Changing reset defaults for alpha, blending, zpos, color range, TV fields, or background color can alter userspace-observed property state and driver assumptions. TV check must mark the right CRTC flags or analog connector changes can be accepted without the required modeset. Bridge/private object helpers are intentionally shallow; drivers with subclassed bridge/private state must not use them without extending copy/destroy behavior for their own allocations.

## Test Signals
Build-test drivers using default atomic state hooks and subclassed underscored helpers. Runtime signals include successful `drm_mode_config_reset()`, IGT atomic property tests, suspend/resume using duplicated state, connector TV property changes causing expected modesets, writeback jobs not being reused across commits, no framebuffer/blob/fence leaks under kmemleak, and no KASAN reports during repeated atomic commits and teardown. Adding any state pointer field should be accompanied by targeted duplicate/destroy tests or at least debug instrumentation that exercises commit abort and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_state_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_uapi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_uapi.c

## Purpose
`drm_atomic_uapi.c` is the marshalling layer between DRM atomic userspace APIs and kernel atomic state objects. It implements atomic GET/SET property behavior, the `DRM_IOCTL_MODE_ATOMIC` ioctl, explicit fence handling, DPMS compatibility, and helper setters used by legacy compatibility paths and drivers constructing atomic updates internally.

The file translates object IDs, property IDs, blob IDs, framebuffer IDs, fence FDs, and user pointers into typed `struct drm_atomic_state` mutations. It also validates UAPI restrictions such as the atomic client capability, supported ioctl flags, async-flip limits, immutable or enum/range property values, and event/out-fence signaling constraints.

## Important APIs, Types, and Functions
Exported helper setters include `drm_atomic_set_mode_for_crtc()`, `drm_atomic_set_mode_prop_for_crtc()`, `drm_atomic_set_crtc_for_plane()`, `drm_atomic_set_fb_for_plane()`, `drm_atomic_set_colorop_for_plane()`, and `drm_atomic_set_crtc_for_connector()`. These update CRTC mode blobs and enable flags, maintain CRTC plane/connector masks, manage framebuffer references, select plane color pipelines, and acquire required CRTC state under the atomic acquire context.

Property dispatch is split by object type. CRTC handling is in `drm_atomic_crtc_set_property()` and `drm_atomic_crtc_get_property()`, covering active, mode ID, VRR, degamma/CTM/gamma blobs, background color, CRTC out-fence pointer, scaling filter, sharpness, and driver-specific properties. Plane handling in `drm_atomic_plane_set_property()` and `drm_atomic_plane_get_property()` covers FB ID, IN_FENCE_FD, CRTC ID, source/destination rectangles, alpha, blend mode, rotation, zpos, color encoding/range, color pipeline, damage clips, scaling filter, cursor hotspots, and driver-specific properties. Color pipeline objects are handled by `drm_atomic_colorop_set_property()` and `drm_atomic_colorop_get_property()`, including LUT/CTM blob sizing through `drm_atomic_color_set_data_property()`. Connector handling covers CRTC ID, legacy DPMS rejection, TV properties, link status, HDR metadata, aspect/content type, content protection, HDCP type, colorspace, writeback FB/out-fence, max BPC, privacy screen, HDMI broadcast RGB, scaling mode, and driver properties.

`drm_atomic_get_property()` is the exported typed getter for current object state. `drm_atomic_set_property()` is the central setter used by the ioctl parser and by internal callers; it validates property values with `drm_property_change_valid_get()`, obtains the relevant object state, applies async-flip restrictions, and dispatches to the object-specific setter.

The ioctl implementation is `drm_mode_atomic_ioctl()`. Signaling support is provided by `create_vblank_event()`, `prepare_signaling()`, `setup_out_fence()`, `complete_signaling()`, CRTC/connector out-fence pointer helpers, and `struct drm_out_fence_state`. `drm_atomic_connector_commit_dpms()` implements legacy DPMS-on-atomic behavior for connector paths.

## Control Flow
For mode setting helpers, `drm_atomic_set_mode_for_crtc()` converts an internal `drm_display_mode` to a modeinfo blob, replaces the old blob, copies the mode, and toggles `state->enable`. `drm_atomic_set_mode_prop_for_crtc()` performs the reverse path from a userspace-provided blob ID, validating blob size and mode conversion before enabling the CRTC. Passing NULL clears the mode and disables the CRTC.

For object links, `drm_atomic_set_crtc_for_plane()` removes the plane from the old CRTC mask, assigns the new CRTC, obtains new CRTC state if needed, and adds the plane mask. `drm_atomic_set_crtc_for_connector()` similarly updates connector masks and connector references. These helpers may return `-EDEADLK` if modeset locking must be retried.

The atomic ioctl flow starts by rejecting devices without `DRIVER_ATOMIC`, clients without the atomic capability, unsupported flags, reserved fields, unsupported async page flips, and test-only plus event combinations. It allocates `struct drm_atomic_state`, initializes an interruptible acquire context, stores `allow_modeset` and the file's color pipeline capability, then parses user arrays of object IDs, property counts, property IDs, and values. Each property is looked up on the object and applied with `drm_atomic_set_property()`.

After property parsing, `prepare_signaling()` allocates vblank events for `DRM_MODE_PAGE_FLIP_EVENT` or CRTC out-fences, reserves events for file delivery, creates sync files for CRTC fences, and handles writeback out-fences. If async flip was requested, `set_async_flip()` marks all new CRTC states. The ioctl then chooses `drm_atomic_check_only()`, `drm_atomic_nonblocking_commit()`, or `drm_atomic_commit()` based on flags. Cleanup always goes through `complete_signaling()`, which either installs sync-file FDs on success or cancels events, drops files/FDs, and writes `-1` back to out-fence pointers on failure. `-EDEADLK` clears state, backs off locks, and retries parsing.

## State and Persistence Behavior
The file mutates staged atomic state rather than live DRM object state directly. Persistent live state is updated later by the atomic commit path. While staged, it owns references to looked-up framebuffers, mode/color/HDR/damage blobs, sync fences, writeback jobs, connectors, and color pipeline objects according to the state helper lifecycle.

Explicit input fences are stored in `drm_plane_state.fence` and consumed by commit helpers. Out-fence user pointers are first written with `-1` to communicate failure-by-default, then replaced with a real FD only after a sync file is created. On successful ioctl completion, FDs are installed into the process file table; on failure, unused FDs and sync files are dropped. CRTC out-fences are represented internally as vblank events with attached DMA fences. Writeback out-fences are stored in writeback jobs.

Some properties are intentionally one-shot or constrained. Writeback framebuffer getters return 0 after set. OUT_FENCE_PTR getters return 0. Userspace cannot set connector content protection to ENABLED; drivers must do that. Userspace cannot downgrade link-status from GOOD to BAD through atomic property set. DPMS cannot be written through the atomic property path and is handled by legacy compatibility.

## Dependencies and Integration Points
This file integrates the DRM ioctl layer, mode object/property framework, atomic state core, framebuffer lookup, sync_file and DMA fence frameworks, event reservation, vblank event delivery, writeback connectors, colorop/color pipeline infrastructure, property blob management, and modeset locking/backoff. It depends on `drm_atomic_helper.c` for the eventual check/commit behavior and on `drm_atomic_state_helper.c` for reference cleanup.

Drivers integrate by exposing standard properties and optional `atomic_set_property`/`atomic_get_property` hooks on CRTCs, planes, and connectors. Plane async behavior depends on `drm_plane_helper_funcs.atomic_async_check`. Color pipeline behavior depends on `struct drm_colorop` properties and the file-level `plane_color_pipeline` capability.

## Risks
This file sits directly on the userspace boundary, so pointer, FD, and reference handling are high risk. Incorrect `get_user()`/`copy_from_user()` handling, out-fence pointer writes, or FD installation ordering can leak FDs, return stale fences, or expose kernel errors incorrectly. `setup_out_fence()` currently allocates an FD before creating the sync file, so every error path must release the unused FD through `complete_signaling()`.

Property validation is security and ABI-sensitive. Bypassing `drm_property_change_valid_get()`, using the wrong object lookup function, or failing to check object visibility through `drm_mode_object_find()`/`drm_framebuffer_lookup()` can allow unauthorized object access. Async flips deliberately permit only no-op changes plus framebuffer/fence/damage updates and driver-approved non-primary behavior; relaxing this can let userspace change modes or plane geometry through an async path that commit helpers do not sequence as a normal modeset.

Blob size checks must match the exact object type. Color LUT, CTM, HDR metadata, damage clips, and colorop data all use different element and total-size constraints. A wrong size check can make drivers parse malformed data. Link-status, content protection, and DPMS have historical compatibility rules; changing them can break compositors and display managers.

## Test Signals
IGT atomic UAPI tests are the strongest signal: invalid flags, capability gating, property ranges/enums, blob sizes, object lookup permissions, test-only behavior, nonblocking commits, async flip restrictions, out-fence and in-fence behavior, writeback fences, event delivery, and `-EDEADLK` retry paths. Additional useful tests include KASAN/KMSAN runs against malformed user arrays, FD-leak checks around failing out-fence commits, compositor runs using atomic modesetting, Android-style explicit sync workloads, writeback connector tests, HDR/color-management blob tests, and content-protection/link-status property behavior checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic_uapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_auth.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_auth.c

## Purpose
`drm_auth.c` implements DRM primary-node master ownership and legacy authentication. A `struct drm_master` represents a group of clients associated with a primary DRM device node, and exactly one master, or lease owner of a master, may be the current device master at a time. The file supports old GETMAGIC/AUTHMAGIC authentication, SET_MASTER/DROP_MASTER ioctls, implicit master assignment on open, master release on close, lease cleanup, and internal master reservation by kernel DRM clients.

This code governs access to DRM_MASTER ioctls, especially modesetting operations where the current master is considered the owner of non-shareable display hardware.

## Important APIs, Types, and Functions
`drm_is_current_master()` and its locked helper test whether a `struct drm_file` is a master file and whether its lease owner matches `dev->master`. `drm_getmagic()` allocates a per-file authentication magic number in the current master's `magic_map`; `drm_authmagic()` finds that magic and marks the referenced file authenticated.

`drm_master_create()` allocates and initializes `struct drm_master`, including `refcount`, `magic_map`, lease lists, lease IDRs, and backpointer to the device. `drm_set_master()` installs the file's master as `dev->master`, invokes the driver's `master_set` hook, and records `was_master`. `drm_new_set_master()` creates a fresh master object for a file that has not previously been a master, switches the file to it, authenticates it, and installs it as current master.

`drm_master_check_perm()` encodes SET/DROP permission policy: a process that previously was master and still has the same thread-group ID can set/drop without `CAP_SYS_ADMIN`; otherwise admin capability is required. `drm_setmaster_ioctl()` and `drm_dropmaster_ioctl()` implement the public ioctls with permission checks, current-master checks, busy checks, and lessee rejection. `drm_master_open()` assigns first opener as master or attaches later openers to the current master. `drm_master_release()` removes magic IDs, drops current master if the closing file owns it, revokes leases for real masters on modeset devices, and releases the file's master reference.

Reference APIs are `drm_master_get()`, `drm_file_get_master()`, `drm_master_put()`, and the internal destroy callback `drm_master_destroy()`. Kernel clients use `drm_master_internal_acquire()` and `drm_master_internal_release()` to reserve the master mutex only when no userspace master is present.

## Control Flow
Open flow enters `drm_master_open()`. Under `dev->master_mutex`, if no current master exists the file gets a newly created master and becomes authenticated/current master. Otherwise the file takes a reference to the existing current master but is not itself current master.

GETMAGIC/AUTHMAGIC flow is protected by `dev->master_mutex`. A client without a magic gets an IDR slot in its associated master's `magic_map`; a master authenticates a peer by looking up the magic, setting `file->authenticated`, and replacing the IDR entry with NULL so the magic cannot be reused.

SET_MASTER flow locks `master_mutex`, checks permission, returns success if already current master, rejects if another current master exists, rejects missing master state, creates a new master for files that have never been master, rejects lessee masters, and otherwise installs the file's existing master as current. DROP_MASTER mirrors this: it checks permission/current-master state, rejects missing master and lessees, calls the driver's `master_drop` hook, and puts `dev->master`.

Release flow runs under `master_mutex`. It removes any outstanding magic, drops device master if the file is current, revokes leases if the file is a real modeset master, and drops the file-held master reference. Destroy flow releases lease resources, IDRs, unique string, and the master allocation when the kref reaches zero.

## State and Persistence Behavior
Persistent state includes `dev->master`, `drm_file.master`, `is_master`, `was_master`, `authenticated`, `magic`, `master_lookup_lock`, and the `drm_master` reference count, magic IDR, lease lists, and lease IDRs. Master state lives across file descriptors associated with the same master and is reference-counted until all users drop it.

The file uses `dev->master_mutex` for global master transitions and magic-map operations. `drm_file.master` lookups are protected by `master_lookup_lock` for lockless-ish readers that only need a stable reference. `was_master` persists after a file has been current master once and is part of the rootless SET/DROP policy. Lease owners affect current-master checks through `drm_lease_owner()`, and lessees are explicitly rejected from becoming or dropping the real device master via these ioctl paths.

## Dependencies and Integration Points
This file integrates with DRM file open/release paths, ioctl permission handling, leasing (`drm_lease_owner()`, `drm_lease_revoke()`, `drm_lease_destroy()`), driver `master_set` and `master_drop` callbacks, Linux capabilities, PID/TGID tracking, IDR allocation, krefs, and render/primary node distinctions. Modesetting drivers depend on this code to serialize display ownership between compositors, display managers, logind-style brokers, fbdev helpers, and legacy clients.

## Risks
Incorrect locking can corrupt master pointers or race master release with permission checks. `drm_is_current_master_locked()` asserts that either the per-file master lookup lock or device master mutex is held; new callers must respect that contract. Reference imbalance on `dev->master` or `file_priv->master` can leak master objects or free a master still reachable from open files.

Permission policy is compatibility-sensitive. Requiring `CAP_SYS_ADMIN` too often breaks rootless compositors and systems without logind-like brokers; allowing SET/DROP too broadly can let clients disrupt the display server. Magic authentication is legacy but still security-relevant for primary-node access; magic reuse or authenticating against the wrong master would violate client isolation. Lease handling must keep lessees from becoming full device masters and must revoke leases when a real master closes.

## Test Signals
Useful tests include opening primary nodes in different orders, verifying first opener becomes master, exercising SET_MASTER/DROP_MASTER with and without `CAP_SYS_ADMIN`, rootless compositor start/stop flows, logind FD-passing flows, GETMAGIC/AUTHMAGIC success and bad-magic failure, lease creation/revocation on master close, concurrent open/close/ioctl stress, and driver `master_set`/`master_drop` callback ordering. KASAN/KCSAN and lockdep are important signals for races around `master_mutex`, `master_lookup_lock`, and kref lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_blend.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_blend.c

## Purpose
`drm_blend.c` documents and implements generic DRM/KMS plane blending, transform, and ordering properties. It provides helpers for creating standard plane properties such as alpha, rotation, zpos, and pixel blend mode, normalizing plane z-order during atomic checks, and attaching the CRTC background color property.

The file defines userspace-visible semantics for source/destination rectangles, scaling, alpha blending, rotations/reflections, z-position ordering, blend mode formulas, and background color. Its executable code is shared by display drivers that expose these generic properties instead of defining driver-specific equivalents.

## Important APIs, Types, and Functions
`drm_plane_create_alpha_property()` creates a mutable range property named `alpha`, attaches it to a plane with default `DRM_BLEND_ALPHA_OPAQUE`, and seeds existing plane state. `drm_plane_create_rotation_property()` creates a bitmask `rotation` property with rotate-0/90/180/270 and reflect-x/y flags, validates the default and supported masks, attaches the property, and seeds plane state. `drm_rotation_simplify()` rewrites unsupported reflection combinations into equivalent rotation/reflection forms when possible.

`drm_plane_create_zpos_property()` and `drm_plane_create_zpos_immutable_property()` create mutable or immutable `zpos` range properties and initialize `zpos` plus `normalized_zpos` in current plane state. `drm_atomic_normalize_zpos()` is the exported atomic helper that detects zpos or plane-mask changes and recomputes per-CRTC normalized z-order. Its internal `drm_atomic_helper_crtc_normalize_zpos()` collects all planes in a CRTC's `plane_mask`, obtains their state, sorts by requested `zpos` and then plane object ID, assigns dense normalized values starting at zero, and marks `crtc_state->zpos_changed`.

`drm_plane_create_blend_mode_property()` creates the `pixel blend mode` enum property for supported modes: `None`, `Pre-multiplied`, and `Coverage`. It requires support for `DRM_MODE_BLEND_PREMULTI` because old userspace and DRM assumptions depend on that default. `drm_crtc_attach_background_color_property()` attaches the device-wide CRTC background color property with an opaque black ARGB64 default.

## Control Flow
Property creation functions are called by drivers during plane or CRTC initialization. They allocate DRM properties, attach them to mode objects, store property pointers on the object, and update existing state if reset already happened. Failures return `-ENOMEM` or `-EINVAL` for invalid blend-mode masks.

Z-position normalization runs during atomic check, commonly via `drm_atomic_helper_check()` when `dev->mode_config.normalize_zpos` is set or from a driver's custom check path. First, `drm_atomic_normalize_zpos()` scans old/new plane states and marks the target CRTC's `zpos_changed` if a plane's requested zpos changed. Then it scans old/new CRTC states and recomputes normalized order if the plane mask changed or zpos changed. Recalculation may pull additional plane states into the atomic transaction with `drm_atomic_get_plane_state()`, sorts them, assigns normalized positions, and returns any state acquisition error.

## State and Persistence Behavior
The file creates persistent DRM property objects stored on planes and CRTCs. User-selected values persist in `struct drm_plane_state` and `struct drm_crtc_state` across atomic commits. `zpos` is the requested property value; `normalized_zpos` is derived per CRTC for the current atomic state and gives drivers a dense hardware-friendly ordering. `zpos_changed` on CRTC state is a transient derived flag that forces recomputation and can be used by drivers to decide whether plane ordering changed.

Alpha defaults to fully opaque. Rotation defaults to the driver-supplied initial transform. Blend mode defaults to premultiplied. Background color defaults to opaque black in ARGB64 format. Immutable zpos communicates fixed hardware order to userspace while still letting userspace discover the order.

## Dependencies and Integration Points
This file depends on DRM atomic state, DRM property creation/attachment, plane and CRTC state structures, `drm_rect` semantics documented in the header comments, Linux sorting, and mode configuration fields such as `num_total_plane` and `background_color_property`. It integrates with `drm_atomic_helper_check()` through zpos normalization and with `drm_atomic_uapi.c` through property setters/getters for alpha, rotation, zpos, blend mode, and background color.

Drivers consume these helpers during initialization and atomic check/commit. Hardware-specific plane update code typically reads `alpha`, `pixel_blend_mode`, `rotation`, `zpos`, `normalized_zpos`, and CRTC `background_color` to program blending and composition registers.

## Risks
The userspace property ABI is stable. Renaming properties, changing defaults, or altering enum values breaks compositors and test suites. `drm_plane_create_blend_mode_property()` must keep premultiplied support mandatory because legacy userspace assumes that default. Rotation validation must ensure exactly one rotate bit is selected; otherwise downstream plane checks may receive impossible transforms.

Zpos normalization can expand atomic state by acquiring every plane on a CRTC. That affects locking, memory allocation, and nonblocking parallelism. Sorting ties by plane ID gives deterministic order; changing tie behavior can change visible composition for equal zpos values. Drivers that expose zpos on only some planes violate the documented expectation that all planes have zpos if any do. Incorrect min/max or immutable zpos assignment can make userspace choose orders the hardware cannot implement or hide fixed hardware constraints.

## Test Signals
Useful coverage includes property creation failure tests, modetest/IGT enumeration of alpha/rotation/zpos/blend/background properties, atomic property set/get tests, zpos sorting with equal zpos values, plane-mask changes that force normalization, mutable and immutable zpos combinations, rotation/reflection validation, alpha/blend visual tests, and compositor runs that rely on premultiplied alpha. Driver-specific tests should confirm `normalized_zpos` maps cleanly to hardware plane order and that all active planes receive expected values after atomic check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_blend.c -->
