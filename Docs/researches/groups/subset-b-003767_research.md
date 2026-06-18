# subset-b-003767 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.c

## Purpose
This file implements the vmwgfx DRM cursor plane. It bridges DRM atomic cursor state to VMware SVGA cursor mechanisms: legacy alpha-cursor FIFO commands backed by snooped legacy surfaces, guest-backed cursor updates from buffer objects, and the newer cursor MOB register path when `SVGA_CAP2_CURSOR_MOB` is available. It also owns cursor image snooping for old non-atomic userspace and the `DRM_VMW_CURSOR_BYPASS` ioctl hotspot override.

## Important APIs, types, and functions
- `vmw_send_define_cursor_cmd()` reserves FIFO command space and emits `SVGA_CMD_DEFINE_ALPHA_CURSOR` with an image payload. Reservation failure is deliberately swallowed because the FIFO reservation cannot be held while KMS atomic resource preparation waits.
- `vmw_cursor_update_type()` selects `VMW_CURSOR_UPDATE_LEGACY`, `VMW_CURSOR_UPDATE_MOB`, `VMW_CURSOR_UPDATE_GB_ONLY`, or `VMW_CURSOR_UPDATE_NONE` from the current user object, snooper state, `has_mob`, and `SVGA_CAP2_CURSOR_MOB`.
- `vmw_cursor_update_mob()` writes a `SVGAGBCursorHeader` plus ARGB image into a pinned cursor MOB, then writes `SVGA_REG_CURSOR_MOBID`.
- `vmw_cursor_mob_get()`, `vmw_cursor_mob_put()`, `vmw_cursor_mob_map()`, and `vmw_cursor_mob_unmap()` allocate, cache, pin, map, unmap, and destroy cursor MOB buffer objects. The plane keeps a small three-entry cache.
- `vmw_cursor_update_position()` programs cursor visibility and position through extra registers, FIFO cursor-bypass registers, or legacy cursor registers while holding `dev_priv->cursor_lock`.
- `vmw_kms_cursor_snoop()` copies a constrained surface DMA upload into `vmw_surface.snooper.image` and increments the snooper image id so legacy cursor updates can detect changes.
- `vmw_cursor_plane_prepare_fb()`, `vmw_cursor_plane_cleanup_fb()`, `vmw_cursor_plane_atomic_check()`, and `vmw_cursor_plane_atomic_update()` are the DRM plane helper lifecycle hooks.
- `vmw_kms_cursor_bypass_ioctl()` updates legacy hotspot offsets on one CRTC or all CRTCs under `mode_config.mutex`.
- `vmw_cursor_snooper_create()` allocates a 64x64 ARGB snooper buffer for legacy, non-atomic, scanout cursor surfaces.

## Control flow
The atomic cursor path starts in `vmw_cursor_plane_atomic_check()`, which delegates generic plane validation to `drm_atomic_helper_check_plane_state()`. Disabling the cursor exits early. Legacy snooped cursors are restricted to exactly 64x64 ARGB surfaces with a valid snooper image. `vmw_cursor_plane_prepare_fb()` then replaces the plane state's `vmw_user_object`, references the framebuffer backing surface or BO, selects an update type, validates and pins BOs for guest-backed paths, maps the image, detects unchanged buffers, and prepares/maps a cursor MOB when a real update is needed. On commit, `vmw_cursor_plane_atomic_update()` hides the cursor for null user objects, otherwise emits the selected image update, then computes global cursor coordinates from CRTC position plus display-unit GUI offsets and hotspot offsets before programming hardware position.

The legacy snoop path is separate. `vmw_cursor_snooper_create()` installs a snooper only for old non-atomic userspace creating a 64x64 ARGB scanout surface. Later execbuf validation calls `vmw_kms_cursor_snoop()` for surface DMA commands. The snooper accepts only face 0, mip 0, a single copy box starting at zero, page-aligned guest offsets, depth 1, and dimensions within 64x64. It maps the source BO, copies either a contiguous full cursor or per-row partial cursor data, increments `snooper.id`, and unmaps/unreserves the BO. `vmw_cursor_plane_update_legacy()` only sends a new define-cursor command when that id changes.

## State and persistence behavior
Persistent device state is minimal but timing-sensitive. Cursor visibility and coordinates live in SVGA registers or FIFO cursor fields. Legacy cursor image state is tracked in `vmw_surface.snooper.image` and `snooper.id`. Plane state tracks the current `vmw_user_object`, `cursor.update_type`, legacy hotspot/id, and a transient cursor MOB pointer. The plane object caches up to three MOBs across commits to reduce allocation churn; excess or undersized MOBs are unpinned and unreferenced. BO mapping state is cached through `vmw_bo_map_and_cache*()` and must be explicitly unmapped in cleanup.

## Dependencies and integration points
The file depends on DRM atomic helpers, `struct drm_plane`, vmwgfx KMS plane state, `vmw_user_object` conversion helpers, TTM BO reservation/pinning/mapping, vmwgfx FIFO command helpers, SVGA register definitions, dirty tracking, and `vmw_surface` metadata. It is called from KMS plane setup/teardown and from execbuf DMA validation for cursor snooping. It consumes capability bits initialized by `vmwgfx_drv.c` and shared state/types declared in `vmwgfx_cursor_plane.h` and `vmwgfx_drv.h`.

## Risks and edge cases
- Several resource preparation failures are collapsed to `-ENOMEM` or ignored. In particular `vmw_cursor_mob_get()` and `vmw_cursor_mob_map()` return values are not propagated from `prepare_fb()`, so MOB update failure can degrade into later no-op or stale cursor behavior.
- `vmw_cursor_update_mob()` assumes successful BO mappings and copies `crtc_w * crtc_h * 4` bytes; the preceding prepare/check paths must enforce size and mapping validity.
- The snooper supports only a narrow DMA shape and logs errors for partial offsets, multiple boxes, non-zero source/destination offsets, or larger dimensions. Legacy users outside that pattern will not update cursor images.
- `vmw_cursor_buffer_changed()` contains a currently unreachable memcmp branch because the function returns immediately when BO pointers differ. Dirty tracking is the active same-BO change detector.
- Cursor register programming is protected by `cursor_lock`, but image/MOB state is managed through atomic plane lifetime and BO reservations; regressions in cleanup ordering can leak pinned BOs or leave mappings behind.

## Test signals
Useful validation includes atomic cursor enable/disable, movement, hotspot changes, same-image commits, dirty BO updates, CRTC offset changes, legacy non-atomic 64x64 cursor surface updates through DMA, fallback behavior without `SVGA_CAP2_CURSOR_MOB`, and suspend/unload cleanup with no pinned cursor MOB leaks. Runtime signals include `drm_warn` for invalid legacy dimensions, `DRM_ERROR` from snooper rejection paths, absence of TTM reservation failures, and correct cursor visibility across multi-monitor display-unit offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.h

## Purpose
This header declares the vmwgfx cursor plane contract shared by KMS setup, atomic plane helpers, legacy cursor snooping, and cursor-specific plane state. It exposes the cursor plane's supported DRM format and the state needed to decide which SVGA cursor update path to use.

## Important APIs, types, and definitions
- `vmw_plane_to_vcp()` converts a `struct drm_plane` embedded object to `struct vmw_cursor_plane`.
- `vmw_cursor_plane_formats[]` advertises `DRM_FORMAT_ARGB8888`, matching the alpha cursor image format used by the C file.
- `enum vmw_cursor_update_type` names the four update modes: none, legacy snooped surface, guest-backed define-cursor command, and cursor MOB.
- `struct vmw_cursor_plane_state` augments common vmwgfx plane state with update type, change flags, a cursor MOB pointer, and legacy hotspot/id tracking.
- `struct vmw_cursor_plane` embeds `struct drm_plane` and keeps a three-entry cursor MOB reuse cache.
- Public functions include snooper creation, cursor plane destroy, atomic check/update, prepare/cleanup framebuffer hooks, and the snooping callback declaration.

## Control flow and integration
The KMS plane implementation includes this header to wire DRM plane callbacks to `vmw_cursor_plane_atomic_check()`, `vmw_cursor_plane_prepare_fb()`, `vmw_cursor_plane_atomic_update()`, `vmw_cursor_plane_cleanup_fb()`, and `vmw_cursor_plane_destroy()`. Surface creation code can call `vmw_cursor_snooper_create()` when a legacy cursor-sized surface is created. Execbuf/KMS code uses the snooping callback to keep legacy cursor image memory synchronized with surface DMA uploads.

## State and persistence behavior
The header defines the persistent cursor plane state that is cloned through DRM atomic state objects. `cursor.mob` is a referenced/pinned BO while active or cached by the plane after cleanup. `legacy.id` records the last snooped surface image id submitted to the device. `legacy.hotspot_x/y` stores driver-private hotspot offsets supplied through the cursor-bypass ioctl, separate from the DRM plane state's standard hotspot fields.

## Dependencies
It depends on SVGA3D command definitions, DRM file/format/plane declarations, and Linux integer types. It forward declares vmwgfx objects to avoid pulling in the full private driver header except where implementations need it.

## Risks and edge cases
- The header declares `vmw_cursor_cmd_dma_snoop()`, while the implementation and `vmwgfx_drv.h` expose `vmw_kms_cursor_snoop()`. If no other compatibility symbol exists, this stale declaration is misleading and should be checked before future users include it.
- `changed` and `surface_changed` fields are declared in `struct vmw_cursor_plane_state` but are not used in the inspected implementation, so new code should confirm whether they are legacy leftovers or planned state.
- The MOB cache size is fixed at three; changes to display topology or concurrent cursor plane assumptions should verify that this remains sufficient.

## Test signals
Compile-time coverage should catch prototype drift for callbacks actually wired by KMS. Runtime cursor tests should confirm that ARGB8888 framebuffers are accepted, non-ARGB cursor buffers are rejected elsewhere, and copied atomic state preserves `legacy` hotspot/id and MOB ownership correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cursor_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.c

## Purpose
This file snapshots VMware SVGA 3D device capability records and provides the data-copy path used by the GET_3D_CAP ioctl. It supports both guest-backed-object aware userspace, which can consume the raw devcap array, and older compatibility userspace, which expects FIFO-style capability records.

## Important APIs, types, and functions
- `struct svga_3d_compat_cap` wraps `SVGA3dFifoCapsRecordHeader` plus up to `SVGA3D_DEVCAP_MAX` `(cap, value)` pairs.
- `vmw_mask_legacy_multisample()` hides deprecated `SVGA3D_DEVCAP_DEAD5` multisample-maskable-samples data from legacy userspace by returning zero for that cap.
- `vmw_fill_compat_cap()` writes a bounded compatibility record into a caller-provided bounce buffer and sets header length/type.
- `vmw_devcaps_create()` allocates `vmw->devcaps` and reads each indexed `SVGA_REG_DEV_CAP` value when `SVGA_CAP_GBOBJECTS` is present.
- `vmw_devcaps_destroy()` frees and nulls the devcap array.
- `vmw_devcaps_size()` reports the byte count needed for raw guest-backed-aware caps, compatibility caps, legacy FIFO caps, or zero when no source exists.
- `vmw_devcaps_copy()` copies raw devcaps, fills compatibility records, or copies legacy FIFO cap words depending on device capabilities and userspace awareness.

## Control flow
Driver load calls `vmw_devcaps_create()` after SVGA capabilities and TTM managers are initialized. For guest-backed devices, the function writes each devcap index to `SVGA_REG_DEV_CAP` and reads back the value into a fixed-size array. Later ioctl handling asks `vmw_devcaps_size()` for the needed payload size and calls `vmw_devcaps_copy()` to populate the user response. On unload or probe error unwinding, `vmw_devcaps_destroy()` releases the vmalloc allocation.

## State and persistence behavior
The only persistent state is `vmw_private.devcaps`, a vmalloc array of `SVGA3D_DEVCAP_MAX` 32-bit values. It is a boot/probe-time snapshot; this file does not refresh it after device reset except through the broader driver restore/reinitialization path. Legacy FIFO caps are not cached here and are read directly from `vmw->fifo_mem` during copy.

## Dependencies and integration points
The implementation depends on `vmwgfx_drv.h` for `struct vmw_private`, register accessors, capability bits, and `vmw->fifo_mem`, plus SVGA register/development capability definitions. It integrates with `vmwgfx_drv.c` during probe/unload and with ioctl code that exposes 3D capability data to userspace.

## Risks and edge cases
- `vmw_devcaps_copy()` trusts `dst_size` from the caller for raw and FIFO `memcpy()` lengths; callers must obtain or clamp it through `vmw_devcaps_size()` to avoid overread.
- `vmw_devcap_get()` in the header indexes `vmw->devcaps` without bounds checks, so all callers must use valid `SVGA3D_DEVCAP_*` enum values and only after successful devcap creation.
- Non-guest-backed devices with no `fifo_mem` return size zero and copy failure; ioctl callers must surface that cleanly.
- The compatibility size calculation intentionally includes an extra `sizeof(uint32_t)` in `vmw_devcaps_size()` for guest-backed but not gb-aware clients, so consumers should avoid duplicating layout assumptions.

## Test signals
Probe on guest-backed SVGA should allocate a non-null devcap array and expose raw capabilities to gb-aware clients. Legacy clients should receive a caps record with type `SVGA3D_FIFO_CAPS_RECORD_DEVCAPS`, bounded pair count, and zero for the deprecated multisample cap. Non-GB or FIFO-only configurations should still return FIFO 3D caps when `fifo_mem` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.h

## Purpose
This header exposes the device-capability lifecycle and copy helpers used by vmwgfx probe and ioctl code. It also provides a small inline accessor for cached SVGA3D devcaps.

## Important APIs
- `vmw_devcaps_create()` initializes cached devcap storage for guest-backed devices.
- `vmw_devcaps_destroy()` frees cached devcap storage.
- `vmw_devcaps_size()` returns the capability payload size expected by a caller, taking guest-backed awareness into account.
- `vmw_devcaps_copy()` materializes capability data into a destination buffer.
- `vmw_devcap_get()` returns one cached devcap value when `SVGA_CAP_GBOBJECTS` is set, otherwise zero.

## Control flow and integration
`vmwgfx_drv.c` includes this header to initialize devcaps during driver load, query specific devcaps while deriving shader model support, and destroy the cache during unload/error paths. Ioctl code uses the size/copy API to answer user requests without knowing whether data comes from raw devcaps, compatibility records, or FIFO caps.

## State and persistence behavior
The header itself owns no storage, but all APIs operate on `struct vmw_private`. `vmw_devcap_get()` reads `vmw->capabilities` and `vmw->devcaps`, so its correctness depends on probe-time capability discovery and successful `vmw_devcaps_create()`.

## Dependencies
It includes `vmwgfx_drv.h` for `struct vmw_private` and `device_include/svga_reg.h` for `SVGA_CAP_GBOBJECTS`. That inclusion direction is heavier than a pure forward declaration but keeps the inline accessor available.

## Risks and edge cases
- `vmw_devcap_get()` has no `devcap < SVGA3D_DEVCAP_MAX` check and no null check for `vmw->devcaps`. It should only be called after successful devcap initialization and with constants from the SVGA3D devcap enum.
- Returning zero for non-GB devices conflates unsupported caps with valid zero-valued caps; callers use it only in guest-backed shader model detection, where that behavior is acceptable.

## Test signals
Compile tests should ensure the header does not create circular include failures. Runtime probe logs and shader model selection provide indirect checks that `vmw_devcap_get()` sees expected values for DX context, SM4.1, SM5, and GL43 capability bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.c

## Purpose
This is the vmwgfx DRM driver's module, PCI, device-lifecycle, ioctl-dispatch, power-management, and top-level initialization implementation. It binds VMware SVGA2/SVGA3 PCI devices to a DRM driver, discovers hardware capabilities, initializes memory/resource/fence/KMS subsystems, registers the DRM device, and tears everything down in reverse order.

## Important APIs, types, and functions
- The `DRM_IOCTL_VMW_*` macros and `vmw_ioctls[]` table define vmwgfx private ioctl encodings, handlers, and permissions.
- Module parameters `restrict_iommu`, `force_coherent`, `restrict_dma_mask`, and `assume_16bpp` alter DMA mapping, DMA mask, and mode-filter behavior.
- `vmw_probe()` is the PCI probe entry: removes conflicting apertures, enables PCI, allocates `struct vmw_private`, loads the driver, registers DRM, enables SVGA, starts generic clients, and initializes debugfs.
- `vmw_driver_load()` is the main initialization sequence for locks, PCI resources, SVGA version/caps, DMA mode, memory limits, TTM, devcaps, GMR/MOB managers, KMS, overlay, FIFO/device request, shader model, host reporting, and PM notifier.
- `vmw_driver_unload()` performs the reverse teardown: notifier removal, software context cleanup, FIFO resource accounting, SVGA disable, KMS/overlay cleanup, memory managers, devcaps, TTM, FIFO/device release, fence manager, IRQs, object device, IDRs, and mksstat cleanup.
- `vmw_request_device()`, `vmw_request_device_late()`, `vmw_release_device_early()`, and `vmw_release_device_late()` manage SVGA enable/config/FIFO, command buffer manager, MOB object tables, dummy query BO, and fence FIFO state.
- `vmw_svga_enable()` and `vmw_svga_disable()` expose top-level SVGA/VRAM manager state changes.
- `vmw_generic_ioctl()` wraps DRM ioctl dispatch to add vmwgfx-specific encoding checks and special permission handling for EXECBUF and UPDATE_LAYOUT.
- `vmw_pm_freeze()` and `vmw_pm_restore()` implement hibernation freeze/restore by suspending KMS, evicting resources, draining FIFO resources, disabling SVGA, then rebuilding the device.

## Control flow
PCI registration is installed by `drm_module_pci_driver(vmw_pci_driver)`. On probe, `vmw_setup_pci_resources()` maps either SVGA3 register MMIO plus VRAM BARs or SVGA2 I/O ports, VRAM, and FIFO memory. `vmw_detect_version()` writes and reads `SVGA_REG_ID` to confirm SVGA2/SVGA3 compatibility. `vmw_driver_load()` then initializes all per-device locks and resource IDR/LRU lists, reads capability bitmaps, warns on unsupported hypervisors, configures virtual KMS support, chooses DMA mapping mode, reads VRAM/FIFO/display/GMR/MOB limits, installs DMA masks and IRQs, initializes TTM and VRAM managers, snapshots devcaps, creates GMR/MOB/system managers when supported, derives shader model support from caps/devcaps, initializes KMS and overlay, requests the SVGA device/FIFO, and registers PM notifications.

After successful load, `vmw_probe()` registers the DRM device, increments FIFO resource use, enables SVGA/VRAM, starts DRM clients, and creates debugfs nodes. Remove unregisters DRM and calls `vmw_driver_unload()`. Error paths in `vmw_driver_load()` are carefully labeled to unwind only initialized subsystems.

Power management has two levels. Simple suspend/resume saves PCI state and toggles device power. Hibernation freeze suspends KMS, releases pinned execbuf BOs, evicts resources, tears down early device state, swaps out TTM BOs, refuses hibernation if FIFO resources remain, disables SVGA, and performs late device release. Restore re-detects SVGA, increments FIFO resource accounting, requests the device again, enables SVGA, restarts fencing, clears suspend state, and resumes KMS when needed.

## State and persistence behavior
`struct vmw_private` is allocated as the DRM device's private object and persists for the PCI device lifetime. This file initializes most global fields: PCI identity and BAR mappings, capability bitmaps, memory limits, display limits, shader model, feature booleans (`has_gmr`, `has_mob`), locks, wait queues, TTM device, object device, fence manager, command buffer manager, FIFO state, devcap cache, KMS/overlay state, PM notifier, and resource IDRs/LRUs. SVGA register state (`enable_state`, `config_done_state`, `traces_state`) is saved before device init and restored on final release.

## Dependencies and integration points
The file integrates Linux PCI, DMA, PM notifier, aperture, module parameter, and device power APIs with DRM core, DRM GEM/TTM helpers, TTM range/resource managers, vmwgfx BO/resource/fence/FIFO/KMS/overlay/devcaps/cmdbuf/mksstat subsystems, and generated kernel version metadata. User-visible integration comes through DRM driver features, file operations, private ioctls, PRIME import/export, fbdev client setup, debugfs, and module metadata.

## Risks and edge cases
- Initialization order is dense and error-path correctness is critical. A misplaced goto can leak IRQs, TTM managers, devcaps, IDRs, or leave FIFO/SVGA state enabled.
- `vmw_device_fini()` busy-waits on `SVGA_REG_BUSY` after writing `SVGA_REG_SYNC`; a stuck device would hang this path.
- `vmw_svga_disable()` intentionally documents a possible race with new modesets because KMS lost-device notification cannot be called under an SVGA lock without lock-order problems.
- DMA mode selection is policy-driven by module parameters and memory encryption. Misconfiguration can disable GMR/MOB/3D paths or force constrained DMA masks.
- Capability-derived shader model state depends on devcap availability. If `vmw_devcaps_create()` succeeds with unexpected zero values, higher shader models are silently disabled.
- `vmw_generic_ioctl()` bypasses extra checks for EXECBUF and overrides UPDATE_LAYOUT permission checks; ioctl table and UAPI encoding changes need regression coverage.

## Test signals
Key signals include successful probe/remove on SVGA2 and SVGA3, expected capability and memory-limit logs, TTM manager debugfs entries matching `has_gmr`/`has_mob`, private ioctl permission behavior for render/master/admin clients, working KMS/fbdev startup, 3D context creation at the selected shader model, hibernation refusal when FIFO resources remain active, hibernation restore with KMS resume, and clean unload with no pinned BO assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.h

## Purpose
This is the central private header for the vmwgfx driver. It defines driver identity/version constants, VMware SVGA resource limits, private TTM placement IDs, core per-file/per-device/resource structures, inline hardware accessors, shader model helpers, FIFO/register helpers, and cross-module function prototypes.

## Important APIs, types, and definitions
- Driver constants include `VMWGFX_DRIVER_NAME`, version `2.21.0`, static FIFO size, display-unit count, initial mode minimums, and SVGA2/SVGA3 PCI IDs.
- Resource and placement IDs define vmwgfx-specific TTM placements (`VMW_PL_GMR`, `VMW_PL_MOB`, `VMW_PL_SYSTEM`) and TTM object resource classes.
- `struct vmw_fpriv` stores per-open TTM object file state plus whether userspace is guest-backed aware.
- `struct vmw_resource` is the base hardware resource with kref, device id, guest memory attachment, dirty/coherency flags, pin count, MOB tree node, LRU/binding list nodes, and vtable/destructor callbacks.
- `struct vmw_surface_metadata` and `struct vmw_surface` describe legacy and guest-backed surfaces, including cursor snooper state.
- `struct vmw_fifo_state` tracks FIFO reservation buffers, capabilities, mutex, and rwsem.
- `struct vmw_dma_map_mode`, `struct vmw_sg_table`, `struct vmw_piter`, and `struct vmw_ttm_tt` describe DMA/TTM backing details for GMR/MOB bindings.
- `struct vmw_sw_context` carries execbuf validation state, resource caches, relocation lists, query state, staged bindings, command-managed resources, and validation context.
- `struct vmw_private` is the per-device root object embedding `struct drm_device` and holding PCI mappings, capability/state registers, memory limits, KMS/overlay pointers, locks, IDRs, wait queues, fence manager, FIFO/cmdbuf managers, devcaps, PM state, query BOs, resource LRUs, DMA mode, object tables, mksstat pages, and VKMS fields.
- Inline helpers include `vmw_priv()`, `vmw_fpriv()`, `vmw_is_svga_v3()`, `vmw_write()`, `vmw_read()`, shader-model predicates, `vmw_fifo_caps()`, `vmw_is_cursor_bypass3_enabled()`, FIFO memory read/write, fence read/write, IRQ status read/write, and shader type validation.
- The remainder of the header declares subsystem entry points for GMR, user objects, resources, GEM, ioctl, FIFO, execbuf, IRQ/waits, KMS, overlay, GMR ID/system managers, PRIME, MOB/object tables, contexts, surfaces, shaders, streamoutput, command-buffer resources, cotables, command buffer manager, CPU blits, host messaging/mksstat, dirty tracking, and BO VM faults.

## Control flow and integration
Most vmwgfx `.c` files include this header to share `struct vmw_private` and subsystem prototypes. Probe code initializes the fields defined here, ioctl/open paths allocate `vmw_fpriv`, execbuf code uses `vmw_sw_context`, resource-specific modules embed `vmw_resource`, KMS/surface code uses `vmw_surface` and snooper fields, and low-level register/FIFO users call the inline accessors. The header is therefore the compile-time integration point between Linux DRM/TTM frameworks and VMware SVGA device abstractions.

## State and persistence behavior
The structures defined here are the main persistence model for the driver. `vmw_private` lasts for the DRM device lifetime. `vmw_fpriv` lasts for each DRM file. `vmw_resource` derivatives are kref-counted and may be pinned, on LRU lists, dirty, or attached to guest memory. `vmw_sw_context` is reused around command submission and owns transient validation allocations. Inline accessors enforce serialized SVGA2 I/O-port register access with `hw_lock`, while SVGA3 uses MMIO directly. FIFO memory helpers use `READ_ONCE`/`WRITE_ONCE` and assert they are not used on SVGA3.

## Dependencies and integration points
The header depends on Linux suspend/sync/hashtable APIs, DRM auth/device/file/print/rect APIs, TTM execbuf/TT/placement/BO APIs, vmwgfx fence/register/validation headers, TTM object support, and the vmwgfx UAPI header. Because it declares nearly every internal subsystem boundary, changes here have broad rebuild and ABI-adjacent impact even when no UAPI structs change.

## Risks and edge cases
- `struct vmw_private` is large and shared widely; adding fields without clear ownership can create locking or lifetime ambiguity.
- Register helpers take `hw_lock` only for SVGA2 indexed I/O. Callers that need multi-register atomicity must provide higher-level locking, as cursor code does with `cursor_lock`.
- FIFO memory helpers `BUG_ON(vmw_is_svga_v3())`; any SVGA3 caller using legacy FIFO memory access will crash.
- `vmw_surface_unreference()` assumes the input pointer is non-null; callers must guard null pointers.
- Several inline helpers expose raw pointers or unchecked array indexes, such as `vmw_devcap_get()` in the companion header and resource conversion helpers. Callers must enforce capability and bounds invariants.
- Include order is delicate: the file notes that `vmwgfx_drm.h` must be last due to UAPI dependency issues.

## Test signals
Good coverage includes build tests across SVGA2/SVGA3 and CONFIG_COMPAT/MKSSTATS variants, sparse/lockdep checks around register and resource locks, runtime exercising of FIFO versus MMIO paths, resource create/destroy with dirty tracking, PRIME/GEM import-export, execbuf validation, KMS cursor/present paths, hibernation restore, and debugfs resource manager creation for all enabled memory domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.h -->
