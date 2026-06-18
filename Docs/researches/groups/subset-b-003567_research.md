# Research: subset-b-003567

Grouped source research for subset B work item `subset-b-003567`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dsi.c

## Purpose
This file implements the DRM MIPI DSI bus core and a large set of MIPI DSI and MIPI DCS helper commands. It registers the `mipi-dsi` Linux bus, creates DSI peripheral devices from board data or Device Tree child nodes, tracks DSI hosts, wires DSI drivers into the driver core, and provides common packet/message wrappers used by panel, bridge, and host drivers.

## Important APIs, Types, and Functions
The bus-facing API is `mipi_dsi_bus_type`, `mipi_dsi_driver_register_full()`, and `mipi_dsi_driver_unregister()`. Device creation and lifetime APIs include `mipi_dsi_device_register_full()`, `devm_mipi_dsi_device_register_full()`, `mipi_dsi_device_unregister()`, and `of_find_mipi_dsi_device_by_node()`. Host APIs include `mipi_dsi_host_register()`, `mipi_dsi_host_unregister()`, and `of_find_mipi_dsi_host_by_node()`, with global `host_list` protected by `host_lock`.

Attachment and transport are centered on `mipi_dsi_attach()`, `mipi_dsi_detach()`, `devm_mipi_dsi_attach()`, and the internal `mipi_dsi_device_transfer()`, which calls the host `transfer` callback and adds `MIPI_DSI_MSG_USE_LPM` when the device mode flags request low-power mode. Packet helpers `mipi_dsi_packet_format_is_short()`, `mipi_dsi_packet_format_is_long()`, and `mipi_dsi_create_packet()` classify and encode DSI headers.

Protocol helpers cover generic writes/reads, DCS writes/reads, DSC enable and PPS transfer, peripheral shutdown/turn-on, maximum return packet size, input bus format mapping, DCS NOP/reset/sleep/display/tear/pixel-format/address/brightness commands, and "multi" wrappers around many commands using `struct mipi_dsi_multi_context`.

## Control Flow
At postcore init, `mipi_dsi_bus_init()` registers the bus. Device matching first tries OF matching and then compares the DSI device name with the driver name. Uevents prefer OF modaliases and fall back to `MIPI_DSI_MODULE_PREFIX` plus the device name.

Host registration scans available child nodes under the host's OF node; children with `reg` become DSI devices via `of_mipi_dsi_device_add()`, which derives the modalias, reads the virtual channel, grabs the node reference, and calls `mipi_dsi_device_register_full()`. The host is then linked into `host_list`. Unregistration iterates host children, detaches attached devices, unregisters them, and removes the host from the global list.

Transfers are simple wrappers: command helpers build a `struct mipi_dsi_msg`, choose the correct packet type from payload length or command kind, and call `mipi_dsi_device_transfer()`. Multi helpers short-circuit once `ctx->accum_err` is set, allowing panel init sequences to be written linearly while preserving the first error. Driver registration installs shim probe/remove/shutdown functions only when the `mipi_dsi_driver` provides those callbacks.

## State and Persistence Behavior
Persistent in-kernel state is the bus registration, each `struct mipi_dsi_device`, the host-owned child device tree, and the global host list. Device state includes host pointer, channel, name, fwnode/OF node reference, mode flags, and `attached`. Managed devm helpers persist cleanup actions until the owning device unbinds. The DSI command helpers do not cache display state; they transmit commands and rely on the panel/peripheral hardware and host driver to persist effects such as sleep state, pixel format, DSC mode, address window, and brightness.

## Dependencies and Integration Points
This code depends on the Linux device model, OF graph helpers, runtime PM generic callbacks, DRM display compression definitions, DRM MIPI DSI public headers, media bus formats, and `video/mipi_display.h` command constants. It is used by DSI host controller drivers, DSI panel drivers, bridge drivers, and OF helper code such as `drm_of_get_dsi_bus()`. The packet and command helpers are a shared protocol layer above host-specific transfer implementations.

## Risks
The virtual channel is limited to 0..3; bad `reg` properties or unchecked board data fail registration. `mipi_dsi_device_register_full()` frees the DSI object directly on `device_add()` failure after `device_initialize()`, which matches this implementation but is a lifetime area to treat carefully if changed. Host registration ignores errors from individual OF child device creation, so a malformed child can be logged and skipped while the host still registers. `mipi_dsi_detach()` clears `attached` before calling host detach, so detach failures leave software state saying detached. DCS brightness helpers differ in byte order between the legacy and large variants; mixing panel expectations can produce wrong brightness values. Multi helpers depend on callers checking `accum_err`.

## Test Signals
Useful signals include module/bus registration, OF-created DSI devices with correct modaliases and virtual channels, host lookup by OF node, successful attach/detach through host callbacks, correct low-power message flag propagation, packet creation for short and long packet types, panel init sequences stopping on the first multi-context error, successful generic and DCS reads/writes on real DSI hardware, DSC PPS/compression commands accepted by panels, and clean host unregistration without leaked child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mm.c

## Purpose
This file implements `drm_mm`, DRM's generic range allocator for GPU address spaces and similar driver-managed regions. It tracks allocated `drm_mm_node` ranges, free holes, interval overlap queries, range-restricted allocation, optional color-based placement adjustments, LRU-style eviction scanning, leak debugging, and allocator state dumping.

## Important APIs, Types, and Functions
The public lifecycle API is `drm_mm_init()`, `drm_mm_takedown()`, and `drm_mm_print()`. Allocation APIs are `drm_mm_reserve_node()` for caller-preselected ranges, `drm_mm_insert_node_in_range()` for searched allocations, and `drm_mm_remove_node()` for O(1) removal. Eviction scan APIs are `drm_mm_scan_init_with_range()`, `drm_mm_scan_add_block()`, `drm_mm_scan_remove_block()`, and `drm_mm_scan_color_evict()`. Overlap lookup is exposed through `__drm_mm_interval_first()`.

Internally, allocated nodes live in a linked list ordered by address and an interval tree keyed by `[start, last]`. Holes are represented as the gap following an allocated node or the synthetic `head_node`; the same hole is indexed in `hole_stack`, `holes_size`, and `holes_addr`. Helper paths include `add_hole()`, `rm_hole()`, `best_hole()`, `find_hole_addr()`, `first_hole()`, and `next_hole()`.

## Control Flow
Initialization creates a synthetic `head_node` with `start + size` and negative `size`, then adds one hole covering the managed range. Insert-by-search first rejects impossible sizes/ranges, checks the largest hole, normalizes alignment, selects an initial hole according to bottom-up, top-down, best, or eviction mode, applies optional `color_adjust`, intersects with the caller range, aligns the candidate start, and inserts the node into the list and interval tree. The source hole is removed and replaced with left and/or right residual holes.

Reservation follows a similar split path but starts from a caller-provided `node->start`, `node->size`, and `node->color`. Removal deletes any following hole, removes the node from the interval tree and node list, merges with the previous node's following hole, and clears the allocated bit. Scanning temporarily removes candidate nodes from the address list without poisoning their list pointers, computes whether the resulting enlarged hole can satisfy the requested allocation, and requires callers to restore candidates in exact reverse order.

## State and Persistence Behavior
All allocator state is in the caller-owned `struct drm_mm` and caller-owned `struct drm_mm_node`s; the allocator performs no allocation for normal operations. Persistent fields include list membership, RB nodes, interval tree augmentation, hole sizes, color tags, flags, and scan state. With `CONFIG_DRM_DEBUG_MM`, stack depot handles are saved on insertion to report leaked nodes at takedown. The implementation is explicitly not thread-safe; drivers must provide external locking around all mutations.

## Dependencies and Integration Points
The file depends on Linux interval tree/RB tree helpers, lists, stack traces, stack depot under debug config, and DRM printer/debug macros. GPU drivers use it for GTT/VRAM/aperture and other address-space allocation when Linux's resource allocator is not a good match. The `color_adjust` callback is the main integration hook for driver-specific placement constraints such as guard pages between incompatible cache domains.

## Risks
Incorrect external locking can corrupt multiple trees/lists at once. Range arithmetic is `u64`; callers must avoid overflow and zero-sized nodes. Alignment code handles power-of-two and arbitrary alignment differently, so edge cases need coverage. The scan API is fragile by design: removing scan blocks out of reverse order corrupts the allocator, and no unrelated operations are allowed while `scan_active` is nonzero. Color adjustment can shrink holes enough to require extra eviction via `drm_mm_scan_color_evict()`. Takedown only warns on leaks; callers remain responsible for removing all nodes.

## Test Signals
Signals include allocator selftests or KUnit-style insert/remove/reserve coverage, bottom-up/top-down/best/evict placement, alignment with power-of-two and non-power-of-two values, range restriction rejection, interval overlap lookup correctness, color adjustment guard behavior, scan add/remove reverse-order behavior, leak reporting under `CONFIG_DRM_DEBUG_MM`, and `drm_mm_print()` totals matching allocated plus free space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_config.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_config.c

## Purpose
This file owns DRM mode configuration setup, teardown, registration ordering, resource enumeration, standard property creation, global reset, cleanup, and structural validation. It initializes `dev->mode_config`, exposes the `GETRESOURCES` ioctl implementation, creates the shared atomic/legacy KMS properties, and warns about invalid encoder, CRTC, and plane topology.

## Important APIs, Types, and Functions
Registration helpers `drm_modeset_register_all()` and `drm_modeset_unregister_all()` register or unregister planes, CRTCs, encoders, and connectors in dependency order. `drm_mode_getresources()` implements user-facing resource enumeration. `drm_mode_config_reset()` calls object reset hooks for colorops, planes, CRTCs, encoders, and connectors. `drmm_mode_config_init()` initializes managed mode_config state and registers cleanup through `drmm_add_action_or_reset()`. `drm_mode_config_cleanup()` tears down KMS objects and ID allocators. `drm_mode_config_validate()` performs topology assertions.

The static `drm_mode_create_standard_properties()` builds common properties such as plane type, source and CRTC rectangles, FB/CRTC IDs, fences, damage clips, active/mode ID, VRR, color management LUTs, CTM, background color, format modifiers, async modifiers, and size hints.

## Control Flow
Registration proceeds from planes to CRTCs to encoders to connectors and unwinds in reverse on failure. `drm_mode_getresources()` first reports file-private framebuffers under `fbs_lock`, then reports min/max dimensions, leased CRTCs, all encoders, and leased connectors through the connector iterator while hiding writeback connectors from clients that did not opt in.

Initialization sets up mutexes, the modeset connection lock, object/tile IDRs, connector IDA, lists, connector free work, standard properties, and object counters. Under lockdep it also exercises modeset and DMA reservation lock acquisition to establish lock ordering. Cleanup destroys encoders, drops connector iterator references and flushes connector free work, destroys properties, colorops, planes, CRTCs, property blobs, leaked framebuffers, ID allocators, and the connection lock. Validation fixes default clone masks, checks clone symmetry and possible CRTC masks, ensures CRTCs have valid primary/cursor plane relationships, and checks the number of primary planes.

## State and Persistence Behavior
This file initializes persistent `drm_mode_config` state for a `drm_device`: object ID namespace, tile IDs, connector IDs, global properties, object lists, counters, locks, connector free queue, and optional suspend state owned by helper code elsewhere. It does not persist hardware state directly; reset and cleanup delegate to object callbacks. Resource enumeration exposes current registered KMS object IDs and file-private framebuffer IDs to userspace.

## Dependencies and Integration Points
It integrates with the DRM object model, property subsystem, framebuffer handling, connector iteration, leasing, managed resource cleanup, DMA reservation lockdep, color pipeline/colorop code, atomic properties, and every KMS object type. Userspace observes this file through `DRM_IOCTL_MODE_GETRESOURCES` and the global property IDs attached by plane/CRTC/connector setup paths.

## Risks
`drm_mode_getresources()` can race with incompletely initialized connectors if drivers register too early, as noted by the inline FIXME. Cleanup assumes single-threaded teardown; concurrent access could deadlock or use freed objects. Property creation failures during init require cleanup to tolerate partially initialized state. Topology validation uses warnings rather than hard failures, so bad possible masks can survive to runtime if drivers ignore logs. The lockdep-only acquisition sequence must stay aligned with real locking or it may miss ordering regressions.

## Test Signals
Signals include successful `drmm_mode_config_init()` followed by cleanup on failure paths, all standard properties present on `dev->mode_config`, `GETRESOURCES` returning correct counts and respecting leases/writeback capability, reset hooks firing in expected object order, teardown without leaked connectors/framebuffers, lockdep remaining quiet for modeset and reservation locks, and validation warnings for intentionally malformed encoder/plane topology in test drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_object.c

## Purpose
This file implements DRM modeset object ID management, lookup, optional object reference counting, property storage, property query ioctls, and property set ioctls for legacy and atomic drivers. It is the bridge between userspace object IDs/properties and in-kernel KMS objects such as connectors, CRTCs, planes, framebuffers, and blobs.

## Important APIs, Types, and Functions
Object ID APIs include `__drm_mode_object_add()`, `drm_mode_object_add()`, `drm_mode_object_register()`, `drm_mode_object_unregister()`, `drm_mode_object_find()`, `drm_mode_object_get()`, and `drm_mode_object_put()`. Leasing rules are centralized in `drm_mode_object_lease_required()`.

Property APIs include `drm_object_attach_property()`, `drm_object_property_set_value()`, `drm_object_property_get_value()`, `drm_object_property_get_default_value()`, `drm_object_immutable_property_get_value()`, `drm_mode_object_get_properties()`, `drm_mode_obj_get_properties_ioctl()`, `drm_mode_obj_find_prop_id()`, and `drm_mode_obj_set_property_ioctl()`. Set paths split into `set_property_legacy()` and `set_property_atomic()`.

## Control Flow
Object add allocates an ID from `dev->mode_config.object_idr` under `idr_mutex`, optionally places the object in the IDR immediately, sets object type/id, and initializes a kref when a free callback is supplied. Lookup locks the IDR, verifies type and ID consistency, enforces leases for CRTCs/connectors/planes, and takes a kref for refcounted objects if possible.

Properties are attached by appending to the object's fixed-size property array before userspace registration. Direct set/get functions update or read the stored software values, with atomic drivers routed to `drm_atomic_get_property()` for mutable properties. Property query ioctls take all modeset locks, find the object, filter atomic-only properties for non-atomic clients and plane color-pipeline compatibility properties based on file capability, and copy property IDs/values to userspace. Property set ioctls find the object and property, validate references, then either call legacy object-specific setters under all modeset locks or allocate an atomic state, set the property, and commit with deadlock backoff retry.

## State and Persistence Behavior
Persistent state is the mode_config IDR mapping IDs to objects, per-object ID/type/free callback/refcount, and per-object property/value arrays. Immutable/default values remain in the arrays; atomic mutable state lives in the atomic state objects and is queried through atomic callbacks. Reference counted objects can outlive lookup callers until `drm_mode_object_put()`. Non-refcounted static KMS objects rely on driver lifetime and registration ordering.

## Dependencies and Integration Points
This code depends on Linux IDR, kref, uaccess, DRM leasing, DRM atomic state/commit helpers, property validation, connector/CRTC/plane legacy setters, and modeset locks. It is exercised by `GETPROPERTIES` and `SETPROPERTY` ioctls and by all KMS object initialization paths that attach standard or driver-specific properties.

## Risks
The fixed `DRM_OBJECT_MAX_PROPERTY` array can overflow if drivers attach too many properties; the code warns and drops the attachment. Properties must be attached before userspace can see the object, otherwise userspace-visible state can change unsafely. Lease checks apply only to CRTC/connector/plane types; adding new lease-required object types requires updating `drm_mode_object_lease_required()`. Atomic and legacy property state differ; using direct stored-value getters for atomic mutable properties is wrong. Error paths in `drm_mode_obj_get_properties_ioctl()` rely on dropping references correctly when partially complete.

## Test Signals
Signals include unique ID allocation/removal under concurrent registration tests, lookup denying wrong types and unleased objects, refcounted lookup surviving object release races, property attach warnings at the max-property limit, `GETPROPERTIES` count-only and copy-out behavior, atomic-client filtering of atomic properties, plane color pipeline property filtering, legacy property setters reaching the right object callbacks, atomic set retries on `-EDEADLK`, and reference cleanup after ioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modes.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modes.c

## Purpose
This file implements DRM display-mode creation, destruction, timing generation, conversion, comparison, validation, list maintenance, command-line mode parsing, userspace modeinfo conversion, and HDMI YCbCr 4:2:0 capability helpers. It is the core shared modeline utility library for KMS drivers and connector probing.

## Important APIs, Types, and Functions
Allocation and list APIs include `drm_mode_create()`, `drm_mode_destroy()`, `drm_mode_duplicate()`, `drm_mode_copy()`, `drm_mode_init()`, `drm_mode_probed_add()`, `drm_connector_list_update()`, `drm_mode_sort()`, `drm_mode_prune_invalid()`, and `drm_set_preferred_mode()`.

Timing generation includes `drm_analog_tv_mode()` with `fill_analog_mode()`, `drm_cvt_mode()`, `drm_gtf_mode_complex()`, and `drm_gtf_mode()`. Conversion helpers include `drm_display_mode_from_videomode()`, `drm_display_mode_to_videomode()`, `drm_bus_flags_from_videomode()`, `of_get_drm_display_mode()`, `of_get_drm_panel_display_mode()`, `drm_mode_convert_to_umode()`, and `drm_mode_convert_umode()`.

Timing/query helpers include `drm_mode_set_name()`, `drm_mode_vrefresh()`, `drm_mode_get_hv_timing()`, and `drm_mode_set_crtcinfo()`. Matching and validation include `drm_mode_match()`, `drm_mode_equal()`, no-clock variants, `drm_mode_validate_driver()`, `drm_mode_validate_size()`, `drm_mode_validate_ycbcr420()`, and `drm_get_mode_status_name()`. Command-line parsing is exposed through `drm_mode_parse_command_line_for_connector()` and `drm_mode_create_from_cmdline_mode()`. HDMI 4:2:0 helpers are `drm_mode_is_420_only()`, `drm_mode_is_420_also()`, and `drm_mode_is_420()`.

## Control Flow
Mode generation allocates a cleared `drm_display_mode`, computes timing fields, sets flags/name, and returns the object or frees it on error. Analog TV generation chooses NTSC-like or PAL-like timing parameter tables, validates horizontal and vertical durations, and has a BT.601 exception for 13.5 MHz modes up to 720 active pixels. CVT and GTF paths implement integer versions of the VESA algorithms, including reduced blanking, margins, interlace, and sync polarity decisions.

Mode list update moves probed modes into the connector's active mode list under the mode_config mutex, merges duplicates, replaces stale modes, and prefers preferred-mode timings when duplicates differ slightly. Sorting ranks preferred modes first, then resolution, refresh rate, and clock. Pruning deletes non-OK modes and logs user-defined or verbose rejection details.

Command-line parsing splits a connector mode option into mode/name, bpp, refresh, extras, and comma options. It supports numeric modes with `M`/`R`, named analog modes such as NTSC/PAL, force flags, interlace, margins, rotation/reflection, TV margins, panel orientation, and TV mode. Conversion from parsed command-line mode chooses named analog, CVT, or GTF generation, marks the result user-defined, fixes 1366x768 where needed, and computes CRTC info.

## State and Persistence Behavior
The file mostly manipulates caller-owned `struct drm_display_mode` objects and connector mode lists. Modes persist until destroyed or moved between lists. Mode `status`, `type`, `flags`, aspect ratio, CRTC-adjusted fields, and name are cached in the mode object. Command-line parse output is stored in a caller-provided `struct drm_cmdline_mode`. No global mutable runtime state is kept beyond static timing and named-mode tables.

## Dependencies and Integration Points
Dependencies include Linux list sorting, OF/videomode helpers when enabled, framebuffer timing macros, DRM EDID/CEA mode matching, connector display info, mode_config driver `mode_valid` hooks, and uapi `drm_mode_modeinfo`. It integrates with connector probing, EDID processing, Device Tree panel timings, boot command-line connector forcing, HDMI sink capability parsing, and userspace mode ioctls.

## Risks
Timing math uses integer arithmetic and multiple unit conversions; overflow and rounding are handled in some paths but remain a risk when extending formulas. `drm_mode_vrefresh()` returns 0 on overflow or invalid totals, which can affect sorting. Command-line parsing is strict and order-sensitive; accepting new options can break syntax if delimiters are mishandled. Aspect ratio is stored differently in kernel modes and userspace flags, so conversion must clear and rebuild those bits. Connector list update assumes the mode_config mutex is held. 4:2:0 helpers depend on CEA VIC matching; non-CEA modes will not map to the HDMI bitmaps.

## Test Signals
Signals include generated CVT/GTF/analog modes matching known modelines, invalid analog timings returning NULL, videomode and OF timing round trips, correct mode names and vrefresh for interlace/doublescan/vscan/stereo cases, duplicate probed modes merging as expected, invalid modes pruned with correct status strings, command-line parser coverage for numeric, named, forced, rotated, and TV-margin options, userspace modeinfo conversion rejecting bad aspect flags and invalid driver modes, and YCbCr 4:2:0 filters matching EDID capability bitmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_helper.c

## Purpose
This file provides small auxiliary KMS helper functions that do not fit in the larger helper modules. It reorders built-in panel connectors, fills framebuffer metadata from userspace create requests, supports legacy CRTC initialization with a default primary plane, and wraps common atomic suspend/resume sequencing.

## Important APIs, Types, and Functions
The exported helpers are `drm_helper_move_panel_connectors_to_head()`, `drm_helper_mode_fill_fb_struct()`, `drm_crtc_init()`, `drm_mode_config_helper_suspend()`, and `drm_mode_config_helper_resume()`. Static support data includes `safe_modeset_formats` (`XRGB8888` and `ARGB8888`) and minimal `primary_plane_funcs` using non-atomic plane functions.

## Control Flow
`drm_helper_move_panel_connectors_to_head()` builds a temporary panel list, takes `connector_list_lock`, moves LVDS/eDP/DSI connectors into the temporary list, and splices them to the head of the connector list so userspace sees built-in panels first. `drm_helper_mode_fill_fb_struct()` copies width, height, format, pitches, offsets, modifier, and flags into a `drm_framebuffer`.

`drm_crtc_init()` allocates a simple primary plane with safe formats, marks `format_default`, and passes it to `drm_crtc_init_with_planes()`, cleaning up the plane on failure. Suspend disables polling if enabled, suspends DRM clients, calls `drm_atomic_helper_suspend()`, and rolls back clients/polling on failure. Resume requires a saved suspend state, calls `drm_atomic_helper_resume()`, clears suspend state, resumes clients, and re-enables polling if initialized.

## State and Persistence Behavior
Connector list order is persistently changed within `dev->mode_config.connector_list`. Framebuffer metadata is stored in the caller-provided framebuffer. Legacy CRTC init allocates and registers a primary plane whose lifetime becomes tied to normal plane/CRTC cleanup. Suspend stores the atomic state in `dev->mode_config.suspend_state` until resume consumes it.

## Dependencies and Integration Points
The file depends on DRM atomic helper suspend/resume, DRM client suspend/resume, probe helper polling, plane allocation, framebuffer formats, and CRTC initialization. It is used by older drivers that have not implemented explicit primary planes, by drivers wanting built-in panels to enumerate first, and by drivers using standard atomic KMS suspend/resume.

## Risks
Connector reordering changes userspace-visible connector order and must be done only when panel priority is desired. `drm_crtc_init()` encodes legacy assumptions: no primary plane scaling/repositioning/subpixel support and primary plane always covers the enabled CRTC; atomic drivers should not use it. Suspend rollback must keep polling/client state consistent if atomic suspend fails. Resume returns `-EINVAL` if suspend state is missing, which catches double-resume or unmatched paths.

## Test Signals
Signals include connector ordering with LVDS/eDP/DSI moved before external connectors, framebuffer fields matching `drm_mode_fb_cmd2`, legacy CRTC init creating a primary plane with safe formats and cleaning it on failure, suspend disabling polling and saving atomic state, failed suspend restoring clients/polling, resume restoring atomic state and clearing `suspend_state`, and no polling enable when polling was never initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_lock.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_lock.c

## Purpose
This file implements DRM KMS modeset locking on top of Linux wound/wait mutexes. It provides acquire contexts, deadlock backoff, lock tracking, all-lock helpers, debug diagnostics for improper backoff, and wrappers for single-lock modeset operations.

## Important APIs, Types, and Functions
Core APIs are `drm_modeset_lock_init()`, `drm_modeset_lock()`, `drm_modeset_lock_single_interruptible()`, and `drm_modeset_unlock()`. Acquire-context APIs are `drm_modeset_acquire_init()`, `drm_modeset_acquire_fini()`, `drm_modeset_drop_locks()`, and `drm_modeset_backoff()`. Broad locking helpers are deprecated `drm_modeset_lock_all()` / `drm_modeset_unlock_all()` and preferred `drm_modeset_lock_all_ctx()`. `drm_warn_on_modeset_not_all_locked()` is a debug assertion helper. The file uses a static `DEFINE_WW_CLASS(crtc_ww_class)`.

## Control Flow
Acquire initialization zeroes the context, initializes the WW acquire context, the locked-list head, and interruptible behavior. `drm_modeset_lock()` either behaves like a normal WW mutex when `ctx` is NULL or calls the internal `modeset_lock()` to acquire with the context, track successful locks in `ctx->locked`, tolerate `-EALREADY`, and record a contended lock on `-EDEADLK`. `drm_modeset_backoff()` clears the contended marker, drops all held locks, and takes the contended lock through the slow WW path before the caller retries.

`drm_modeset_lock_all_ctx()` acquires the connection mutex, all CRTC mutexes, all plane mutexes, and all private object locks. Deprecated `drm_modeset_lock_all()` additionally grabs `mode_config.mutex`, creates a global acquire context stored in `mode_config.acquire_ctx`, retries on deadlock, and requires `drm_modeset_unlock_all()` to drop and free that context. Debug-mode stack depot support records where a contended lock was encountered and prints if callers keep locking without backoff.

## State and Persistence Behavior
Each `struct drm_modeset_lock` owns a WW mutex and a list node used only while held by an acquire context. Each acquire context stores the WW context, list of held locks, interruptible/trylock flags, contended lock, and optional debug stack. Deprecated all-lock state persists temporarily in `dev->mode_config.acquire_ctx`. There is no hardware state; this is synchronization state guarding KMS object changes.

## Dependencies and Integration Points
The file depends on WW mutexes, stack depot/stack trace when debug config is enabled, DRM CRTC/plane/private object iteration, and mode_config locking. It is used by atomic commits, property ioctls, legacy KMS paths, connector probing, and helper macros such as `DRM_MODESET_LOCK_ALL_BEGIN()` / `END()`.

## Risks
Callers must handle `-EDEADLK` by invoking `drm_modeset_backoff()` before taking further locks; failing to do so risks deadlock and triggers debug warnings. Deprecated global all-lock helpers are brittle because the acquire context is stored globally and cannot be safely nested. Unlocking a lock not tracked in a context still calls `list_del_init()`, so initialization of the list head is mandatory. Mixing `mode_config.mutex` with WW locks requires consistent ordering outside this file. Interruptible contexts can return `-ERESTARTSYS` from slow paths.

## Test Signals
Signals include lockdep and WW mutex tests for random lock ordering, `-EDEADLK` retry paths through `drm_modeset_backoff()`, `-EALREADY` lock reentry tolerance with a context, interruptible single-lock interruption, all-lock acquisition covering connection, CRTC, plane, and private object locks, deprecated all-lock pairing without leaked `acquire_ctx`, and debug stack output when a caller ignores the backoff protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_of.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_of.c

## Purpose
This file contains DRM Device Tree helper functions for graph-based display pipelines. It maps OF graph ports to CRTCs, builds component framework matches, finds active encoder endpoints, locates connected panels or bridges, decodes dual-link LVDS metadata, counts DSI/eDP data lanes, and locates the DSI host for non-DSI-controlled display devices.

## Important APIs, Types, and Functions
CRTC/encoder graph helpers are `drm_of_crtc_port_mask()`, `drm_of_find_possible_crtcs()`, `drm_of_component_match_add()`, `drm_of_component_probe()`, and `drm_of_encoder_active_endpoint()`. Panel/bridge lookup is `drm_of_find_panel_or_bridge()`. LVDS helpers are `drm_of_lvds_get_dual_link_pixel_order()`, `drm_of_lvds_get_dual_link_pixel_order_sink()`, and `drm_of_lvds_get_data_mapping()`. Lane helpers are `drm_of_get_data_lanes_count()` and `drm_of_get_data_lanes_count_ep()`. When MIPI DSI support is enabled, `drm_of_get_dsi_bus()` returns a `mipi_dsi_host` for a device's input graph.

## Control Flow
`drm_of_find_possible_crtcs()` walks endpoints of an encoder port, follows each remote port, and ORs the matching CRTC bit from `drm_of_crtc_port_mask()`. `drm_of_component_probe()` first adds CRTC ports listed in the master's `ports` phandle property, then adds remote encoder-side components reachable from those ports, and finally calls `component_master_add_with_match()`. This ordering lets encoder bind callbacks query possible CRTCs.

Panel/bridge lookup first validates that a graph exists, obtains the requested remote node, tries panel lookup, then bridge lookup if no panel was found. LVDS source pixel order follows remote sink port properties and verifies both links form an even/odd pair; sink pixel order reads the sink ports directly. Data lane helpers count `data-lanes` elements and validate min/max bounds. `drm_of_get_dsi_bus()` follows device `port@0` to the remote DSI host node and returns `-EPROBE_DEFER` until the host is registered.

## State and Persistence Behavior
The helpers do not maintain global state. They acquire and release OF node references around graph traversal and component match setup. `drm_of_component_match_add()` intentionally takes an OF reference and registers `component_release_of` so the component framework owns release. Results are transient masks, pointers, or media bus format constants; persistent ownership remains with the DRM device, OF core, component framework, DSI host registry, panel subsystem, or bridge subsystem.

## Dependencies and Integration Points
The file depends on Linux OF graph APIs, component framework, media bus format constants, DRM CRTC/encoder/bridge/panel APIs, and MIPI DSI host lookup when enabled. It is used by Device Tree based display drivers to wire encoders to CRTCs, bind multi-component display devices, discover downstream panels/bridges, configure LVDS bus mapping, validate link lane count, and defer probing until DSI hosts are ready.

## Risks
Graph parsing is reference-sensitive; missing `of_node_put()` calls would leak nodes, while premature puts can invalidate comparisons. `drm_of_find_possible_crtcs()` returns 0 immediately if any endpoint lacks a remote port, which can hide other valid endpoints. `drm_of_component_probe()` requires a `ports` phandle property and available parent devices; malformed or disabled nodes fail binding. `drm_of_find_panel_or_bridge()` is deprecated for new drivers in favor of managed bridge lookup. LVDS helpers enforce all remote endpoints on a port having the same pixel type, which may reject more complex topologies. `drm_of_get_dsi_bus()` assumes `port@0` is the DSI input.

## Test Signals
Signals include DT graph unit tests or board boots where possible CRTC masks match expected ports, component master binding orders CRTCs before encoders, active encoder endpoint parsing matches the connected CRTC, panel/bridge lookup returns the expected downstream object or defers cleanly, LVDS even/odd ordering and data mapping strings produce correct media bus formats, invalid dual-link properties return `-EINVAL` or `-EPIPE`, data-lane counts enforce min/max bounds, and DSI bus lookup defers until host registration then succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_of.c -->
