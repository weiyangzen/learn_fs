# subset-b-005810 DRM atomic, bridge, connector, and client header research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_atomic.h

## Purpose
This header defines the core DRM atomic state model: reference-counted commit objects, the aggregate `drm_atomic_state`, per-object old/new state slots for CRTCs, planes, connectors, colorops, private objects, and bridge bus state. It is the central contract between userspace atomic IOCTL assembly, driver atomic check hooks, helper commit sequencing, and nonblocking commit lifetime management.

## Important APIs, types, and functions
Key types are `struct drm_crtc_commit`, `struct drm_atomic_state`, `struct drm_private_obj`, `struct drm_private_state`, `struct drm_private_state_funcs`, `struct drm_bus_cfg`, and `struct drm_bridge_state`. Important APIs allocate, initialize, clear, refcount, and free atomic states; get CRTC, plane, connector, colorop, private-object, and bridge states; add affected objects; run `drm_atomic_check_only`, `drm_atomic_commit`, and `drm_atomic_nonblocking_commit`; and dump state. Iterator macros expose old, new, and old/new state traversal for connectors, CRTCs, planes, colorops, and private objects.

## Control Flow
Atomic users gather mutable state with `drm_atomic_get_*_state`, run checks, then commit either synchronously or through `commit_work`. Helper-backed commits use `drm_crtc_commit` completions to separate hardware programming (`hw_done`), flip/event delivery (`flip_done`), and old-buffer cleanup (`cleanup_done`). After `drm_atomic_helper_swap_state`, object current-state pointers hold the new state while the atomic state retains the old state for disable, cleanup, and destruction paths.

## State and Persistence
The header defines in-memory KMS state only, but that state represents persistent hardware configuration and userspace-visible properties. `state_to_destroy` fields prevent old/new ownership confusion across swap and teardown. Private objects are tied to the DRM device lifetime and carry a modeset lock; shared private state in nonblocking commits must preserve commit ordering to avoid use-after-free.

## Dependencies and Integration Points
It depends on CRTC, plane, connector, encoder, colorop, property, modeset-lock, kref, completion, and bridge concepts. It integrates with `drm_atomic_helper.h`, bridge atomic state, connector writeback fences, userspace out-fences, `drm_mode_config_funcs`, and driver-private atomic extensions.

## Risks and Test Signals
Risk concentrates around state lifetime, stale old/new assumptions after swap, adding unrelated objects without `allow_modeset`, unsafe peeks via `__drm_atomic_get_current_plane_state`, private-object nonblocking ordering, and missed completion signaling. Tests should cover refcounted commit waits, nonblocking commits sharing private state, connector array bounds, old/new iterator behavior, bridge state retrieval, out-fence pointer handling, and modeset-needed calculation for mode, active, connector, and self-refresh transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_atomic_helper.h

## Purpose
This header declares the standard helper layer for atomic KMS validation, commit sequencing, legacy ioctl emulation, suspend/resume duplication, nonblocking commit synchronization, plane iteration, and plane enable/disable predicates. It is the common path for drivers that rely on DRM core helpers instead of implementing the full atomic sequence manually.

## Important APIs, types, and functions
Important declarations include `drm_atomic_helper_check_modeset`, `drm_atomic_helper_check_plane_state`, `drm_atomic_helper_check_planes`, `drm_atomic_helper_check`, `drm_atomic_helper_commit`, `drm_atomic_helper_commit_tail`, `drm_atomic_helper_commit_tail_rpm`, async check/commit helpers, fence/vblank/flip waits, modeset disable/enable helpers, plane prepare/commit/cleanup helpers, `drm_atomic_helper_swap_state`, and nonblocking helpers `drm_atomic_helper_setup_commit`, `drm_atomic_helper_wait_for_dependencies`, `drm_atomic_helper_commit_hw_done`, and `drm_atomic_helper_commit_cleanup_done`. Macros include `DRM_PLANE_NO_SCALING`, plane commit flags, and CRTC plane iterators.

## Control Flow
A helper commit normally checks modesets and planes, prepares plane resources, swaps state, disables old modesets, programs modes and planes, enables new modesets, waits for fences/vblanks/flips, and cleans old planes. Nonblocking commits first set up `drm_crtc_commit` dependencies, run the tail in work context, and signal the hardware and cleanup completion points.

## State and Persistence
The helpers mutate atomic state ownership and current object state through `swap_state`, but this header itself only declares the flow. Legacy helpers translate `set_config`, update-plane, disable-plane, and page-flip requests into atomic transactions. Suspend/resume helpers duplicate and restore display state.

## Dependencies and Integration Points
It integrates with mode config helper vtables, CRTC/plane/connector state, fences, bridge chaining, writeback connectors, runtime PM variants, and legacy IOCTL entry points. `drm_atomic_helper_bridge_propagate_bus_fmt` ties bridge bus-format negotiation into the atomic helper path.

## Risks and Test Signals
Risk areas are incorrect commit-stage ordering, missing cleanup signaling, plane enable/disable states where CRTC and framebuffer are inconsistent, failures after plane preparation, async update checks bypassing full validation, and legacy entry points producing incomplete atomic state. Tests should exercise blocking and nonblocking commits, dependency waits across multiple CRTCs, vblank/flip waits, plane scaling limits, active-only plane commit flags, suspend/resume duplicated-state commits, and legacy page-flip target paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_state_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_atomic_state_helper.h

## Purpose
This header declares default reset, duplicate, and destroy helpers for atomic CRTC, plane, connector, private-object, and bridge state. It lets drivers subclass state structures while reusing the core copy/reset/destruction semantics for common fields.

## Important APIs, types, and functions
The CRTC APIs are `__drm_atomic_helper_crtc_state_reset`, `__drm_atomic_helper_crtc_reset`, `drm_atomic_helper_crtc_reset`, duplicate helpers, and destroy helpers. Plane and connector sections mirror this pattern, with TV-specific connector reset/check/margin helpers. Private object helpers initialize and duplicate base private state. Bridge helpers duplicate, destroy, and reset `drm_bridge_state`.

## Control Flow
Drivers call the double-underscore helpers when they allocate a subclassed state and need the base portion initialized or copied. Non-underscored helpers are suitable as direct vtable hooks for drivers that do not add private fields. Destroy helpers release common references held by state before driver-specific cleanup completes.

## State and Persistence
The state is transient atomic KMS state, but it owns references to persistent objects such as framebuffers, property blobs, writeback jobs, and connector/bridge state. Correct duplication and destruction determine whether aborted atomic checks, failed commits, and hot-unplug paths leak or use freed resources.

## Dependencies and Integration Points
It connects the object vtables in CRTC, plane, connector, private-object, and bridge definitions to the atomic core declared in `drm_atomic.h`. It is used by drivers implementing `atomic_duplicate_state`, `atomic_destroy_state`, and reset callbacks.

## Risks and Test Signals
Main risks are subclass drivers forgetting to call base duplicate/destroy helpers, copying stale pointers without taking references, TV connector defaults not being reset, and bridge atomic hooks lacking a valid reset state. Tests should force allocation failure during duplicate, abort atomic checks, reset objects during mode-config reset, exercise TV margin/property validation, and hot-unplug connectors or bridges with pending duplicated states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_state_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_uapi.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_atomic_uapi.h

## Purpose
This header declares the small API used to mutate atomic state in ways that mirror userspace-visible KMS relationships: CRTC mode, plane CRTC/framebuffer/color pipeline attachment, and connector CRTC routing.

## Important APIs, types, and functions
The exported functions are `drm_atomic_set_mode_for_crtc`, `drm_atomic_set_mode_prop_for_crtc`, `drm_atomic_set_crtc_for_plane`, `drm_atomic_set_fb_for_plane`, `drm_atomic_set_colorop_for_plane`, and `drm_atomic_set_crtc_for_connector`. They update object state while maintaining references and derived fields expected by the atomic core.

## Control Flow
Users of this API first acquire the relevant object state through `drm_atomic_get_*_state`, then call setters to change relationships. The full transaction is later validated by atomic check hooks and committed or rolled back by the atomic core.

## State and Persistence
The setters modify only the pending atomic state. Effects become persistent hardware and userspace-visible state only if the containing `drm_atomic_state` commits successfully. Framebuffer and mode property setters must manage object references correctly across replacement and abort paths.

## Dependencies and Integration Points
It integrates with CRTC mode blobs, display modes, plane framebuffers, colorop pipelines, connector routing, and the atomic IOCTL/property decoding layer.

## Risks and Test Signals
Risks include direct field mutation by drivers bypassing reference management, mode-blob lifetime mistakes, connector/plane CRTC mismatches, and colorop assignment without adding affected colorops. Tests should cover replacing modes and framebuffers repeatedly, disabling planes and connectors by setting NULL, aborting after setters, and validating that getters/reporting reflect the pending state only after commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_atomic_uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_audio_component.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_audio_component.h

## Purpose
This header defines the component interface used for direct cooperation between DRM display drivers and HDA audio drivers, especially for HDMI/DisplayPort audio power, ELD reporting, clock/rate synchronization, and hotplug notification.

## Important APIs, types, and functions
`struct drm_audio_component_ops` is implemented by the DRM side and exposes module ownership, audio power well get/put, codec wake override, CDCLK query, audio rate synchronization, and ELD retrieval. `struct drm_audio_component_audio_ops` is implemented by the audio side and exposes ELD notification, pin-to-port mapping, and optional component master bind/unbind callbacks. `struct drm_audio_component` binds the DRM device, both ops tables, and a `master_bind_complete` completion.

## Control Flow
The HDA driver calls DRM ops when it needs display power, current clocking, sample-rate programming, or ELD bytes. The DRM driver calls audio ops when display hotplug or pipeline setup/teardown changes pin sense or ELD. Component binding uses the completion to coordinate master availability.

## State and Persistence
Persistent state lives in the participating DRM and audio drivers; this header stores only cross-driver pointers and a binding completion. ELD bytes and enabled state are snapshots supplied on demand.

## Dependencies and Integration Points
It depends on Linux component binding, completion, module pinning, and HDMI/DP audio conventions. It integrates display hotplug, audio codec power management, and audio stream setup across independent drivers.

## Risks and Test Signals
Risks include dangling ops during module unload, unbalanced power-well wakerefs, stale ELD after hotplug, mismatched pin-to-port mapping, and races while binding or unbinding the component master. Tests should cover hotplug while HDA is power-saving, partial ELD buffer copies, invalid ELD return paths, rate changes during modeset, and driver unload with active audio clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_audio_component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_auth.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_auth.h

## Purpose
This internal DRM header defines master ownership, authentication token storage, and leasing metadata for legacy/primary DRM nodes. It captures who is current master, which files can access privileged operations, and how display-resource leases relate lessors and lessees.

## Important APIs, types, and functions
`struct drm_master` contains a kref, parent device, bus-unique string, magic-token IDR, driver-private data, lessor pointer, lessee id, lessee lists, leased-object IDR, and owner lessee IDR. Public functions are `drm_master_get`, `drm_file_get_master`, `drm_master_put`, `drm_is_current_master`, and `drm_master_create`.

## Control Flow
DRM file open/master transitions create or reference master objects. Authentication tokens are tracked in `magic_map`. Lease creation links a lessee master to a lessor and populates lease IDRs. Current-master checks gate privileged IOCTL behavior.

## State and Persistence
Master state is in-memory and scoped to a DRM device, open files, and lease lifetime. It persists across individual IOCTL calls until master drop, device close, lease revocation, or device teardown. Locking is split between `master_mutex` for unique/auth data and `mode_config.idr_mutex` for lease IDRs/lists.

## Dependencies and Integration Points
It depends on `idr`, `kref`, DRM file objects, device master locking, and mode-config object ID management. It integrates with DRM authentication, primary node semantics, and display-resource leasing.

## Risks and Test Signals
Risks include refcount leaks, use-after-free across file close, lock-order mistakes between master and mode-config mutexes, stale magic tokens, and lease revocation leaving object IDs accessible. Tests should cover master create/drop, file master reference acquisition, current-master changes, nested lessee teardown, lessor lifetime while lessees exist, and authenticated versus unauthenticated IOCTL access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_blend.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_blend.h

## Purpose
This header declares helpers for standard plane blending, alpha, rotation/reflection, z-position, normalized z-ordering, blend mode, and CRTC background color properties.

## Important APIs, types, and functions
It defines blend mode values `DRM_MODE_BLEND_PREMULTI`, `DRM_MODE_BLEND_COVERAGE`, `DRM_MODE_BLEND_PIXEL_NONE`, `DRM_BLEND_ALPHA_OPAQUE`, and the inline `drm_rotation_90_or_270`. Property helpers include `drm_plane_create_alpha_property`, `drm_plane_create_rotation_property`, `drm_rotation_simplify`, `drm_plane_create_zpos_property`, `drm_plane_create_zpos_immutable_property`, `drm_atomic_normalize_zpos`, `drm_plane_create_blend_mode_property`, and `drm_crtc_attach_background_color_property`.

## Control Flow
Drivers attach supported properties during plane or CRTC initialization. Atomic property decoding stores requested values in plane/CRTC state, then `drm_atomic_normalize_zpos` computes a consistent normalized z-order across planes in a transaction before driver check/commit.

## State and Persistence
Properties are persistent KMS object properties exposed to userspace; their requested values live in atomic state and commit to current plane/CRTC state. Immutable zpos is fixed after property creation.

## Dependencies and Integration Points
It depends on DRM mode flags, plane/CRTC objects, and atomic state. It integrates with compositor plane assignment, hardware composition ordering, rotation support, and background fill behavior.

## Risks and Test Signals
Risks include unsupported rotation bits surviving simplification, alpha default mismatches, zpos ties or normalization instability, and blend mode exposure not matching hardware. Tests should cover all rotation/reflection combinations, immutable and mutable zpos ordering, disabling/enabling planes while normalizing, alpha extremes, unsupported blend mode rejection, and background color property propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_blend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_bridge.h

## Purpose
This header defines DRM bridge objects and bridge-chain operations for display pipeline components between encoders and connectors/panels. It covers attach/detach, mode validation, atomic enable/disable ordering, bus-format negotiation, HPD, EDID/mode discovery, HDMI infoframes, HDMI/DP audio hooks, CEC hooks, panel bridge helpers, reference management, and debugfs support.

## Important APIs, types, and functions
Key types are `enum drm_bridge_attach_flags`, `struct drm_bridge_funcs`, `struct drm_bridge_timings`, `enum drm_bridge_ops`, and `struct drm_bridge`. Important APIs allocate/add/remove/attach bridges, find OF bridges, get/put bridge refs, walk bridge chains, get current atomic bridge state, validate and mode-set chains, run atomic bridge check/disable/post-disable/pre-enable/enable, propagate bus formats, detect, read EDID, get modes, enable HPD, notify HPD, wrap panels as bridges, and expose debugfs parameters.

## Control Flow
Bridge chains attach to an encoder in order. During atomic check, the chain validates modes and usually checks bridges from sink toward source while negotiating output and input bus formats. During commit, disable/post-disable and pre-enable/enable callbacks run in direction-sensitive order, with `pre_enable_prev_first` allowing DSI-style ordering where upstream initialization precedes peripheral initialization. HPD callbacks are registered through bridge HPD helpers and later notify connectors.

## State and Persistence
`struct drm_bridge` is refcounted, globally listed, optionally backed by device-managed allocation, and may hold a next-bridge reference for safe hot-unplug behavior. Atomic bridges embed a `drm_private_obj` and own `drm_bridge_state` with input/output bus configuration. Persistent bridge metadata includes supported ops, connector type, interlace/YUV420 support, HDCP support, DDC adapter, HDMI vendor/product, audio/CEC devices, and HPD callback data protected by `hpd_mutex`.

## Dependencies and Integration Points
It depends on DRM atomic/private objects, encoders, connectors, modes, EDID, panels, OF graph discovery, I2C DDC, HDMI codec parameters, CEC, and debugfs. It integrates with `drm_bridge_connector`, panel bridge support, connector HDMI/audio infrastructure, and atomic helper commit sequencing.

## Risks and Test Signals
Risks include incorrect callback ordering, mixing deprecated and atomic hooks, missing mandatory callbacks for advertised ops, bus-format negotiation failure or leaked kmalloc arrays, HPD callback races, bridge hot-unplug use-after-free, and only-one-bridge assumptions for HDMI/audio ops. Tests should cover multi-bridge chains, atomic and legacy callback mixtures, DSI `pre_enable_prev_first`, EDID versus fixed-mode bridges, HPD enable/disable/notify races, panel bridge teardown, OF lookup failures, HDMI infoframe/audio/CEC ops validation, and bridge-state locking assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge_connector.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_bridge_connector.h

## Purpose
This small header declares the helper that creates a `drm_connector` from an encoder's bridge chain. It supports bridge-based display pipelines where the connector behavior is aggregated from bridge operations rather than implemented directly by the encoder driver.

## Important APIs, types, and functions
The only API is `drm_bridge_connector_init(struct drm_device *drm, struct drm_encoder *encoder)`, returning a connector or an error pointer/NULL depending on implementation failure mode.

## Control Flow
Drivers build and attach a bridge chain to an encoder, then call this initializer to create a connector backed by the chain's detect, modes/EDID, HPD, and HDMI/audio capabilities. The resulting connector participates in normal registration and atomic modesets.

## State and Persistence
State is owned by the connector created by the implementation. This header defines no storage, but the created connector persists until normal DRM connector cleanup and must track bridge-chain lifetime.

## Dependencies and Integration Points
It depends on `drm_bridge.h`, encoder objects, connector registration, and bridge ops. It integrates bridge-only drivers with userspace-visible connector enumeration.

## Risks and Test Signals
Risks include initializing before the bridge chain is complete, missing final bridge connector type, HPD or EDID ops not propagating, and cleanup order between connector and bridges. Tests should create fixed-panel, EDID-capable, HPD-capable, and HDMI bridge chains and verify connector properties, modes, detect status, and hot-unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge_connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_bridge_helper.h

## Purpose
This header declares a bridge helper for resetting the CRTC associated with a bridge pipeline. It provides a narrow bridge-to-modeset utility for recovery or disable paths.

## Important APIs, types, and functions
The only function is `drm_bridge_helper_reset_crtc(struct drm_bridge *bridge, struct drm_modeset_acquire_ctx *ctx)`.

## Control Flow
Callers pass a bridge and modeset acquire context; the implementation locates the related pipeline/CRTC and performs a reset through normal modeset locking rules.

## State and Persistence
No state is declared here. Any persistent effect is a CRTC state/hardware reset performed by the implementation through KMS helpers.

## Dependencies and Integration Points
It depends on bridge objects and modeset acquire contexts. It integrates bridge drivers with core CRTC reset behavior while respecting modeset lock acquisition.

## Risks and Test Signals
Risks include deadlocks from incorrect acquire context use, resets on detached bridges, and failure to handle bridges without an active CRTC. Tests should cover reset on active and inactive pipelines, bridge detach during reset, ww-mutex retry paths, and error propagation when the CRTC cannot be acquired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_bridge_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_buddy.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_buddy.h

## Purpose
This header exposes DRM printer helpers for the generic GPU buddy allocator. It is diagnostic glue between `linux/gpu_buddy.h` memory-management state and DRM debug output.

## Important APIs, types, and functions
It declares `drm_buddy_print(struct gpu_buddy *mm, struct drm_printer *p)` for whole allocator dumps and `drm_buddy_block_print(struct gpu_buddy *mm, struct gpu_buddy_block *block, struct drm_printer *p)` for individual block dumps.

## Control Flow
Drivers or debugfs callbacks call the print helpers with an allocator or block and a DRM printer. The helpers format allocator state into the selected print sink.

## State and Persistence
The header owns no state. It observes in-memory GPU buddy allocator state and emits diagnostics without changing allocation metadata.

## Dependencies and Integration Points
It depends on the generic `gpu_buddy` allocator and `drm_printer`. It integrates with DRM memory manager debugfs and driver diagnostics.

## Risks and Test Signals
Risks are mostly diagnostic: racing allocator mutation while printing, incomplete block context, or output that becomes misleading for corrupted allocator state. Tests should cover empty, fragmented, fully allocated, and partially freed allocators, block-level printing for root and leaf blocks, and debugfs invocation under allocator locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_buddy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_cache.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_cache.h

## Purpose
This header declares DRM cache-management and write-combined memory copy helpers used by graphics drivers for CPU/GPU buffer coherency and efficient reads from WC mappings.

## Important APIs, types, and functions
APIs include `drm_clflush_pages`, `drm_clflush_sg`, `drm_clflush_virt_range`, `drm_need_swiotlb`, `drm_arch_can_wc_memory`, `drm_memcpy_init_early`, and `drm_memcpy_from_wc`. The inline `drm_arch_can_wc_memory` disables WC optimizations on architectures where uncached/no-snoop behavior is unsafe or outside coherent cache mechanisms.

## Control Flow
Drivers flush page arrays, scatter-gather tables, or virtual ranges before or after CPU access as required by buffer placement. Early initialization selects an optimized memcpy-from-WC implementation, then callers copy from WC `iosys_map` sources into destination maps.

## State and Persistence
The header manages no persistent state except implementation selection performed by `drm_memcpy_init_early`. Cache flushes affect CPU cache state and DMA coherency for buffer contents.

## Dependencies and Integration Points
It depends on Linux pages, scatterlists, architecture config symbols, SWIOTLB decisions, and `iosys_map`. It integrates with GEM/TTM buffer access, framebuffer readback, and DMA mapping constraints.

## Risks and Test Signals
Risks include assuming WC memory is safe on ARM/arm64/LoongArch/PPC/MIPS exceptions, missing flushes around noncoherent mappings, incorrect SWIOTLB decisions for DMA masks, and overlapping or unmapped `iosys_map` copies. Tests should cover architecture-specific return values, clflush on multi-page and SG buffers, WC copy length boundaries, and DMA-mask cases requiring SWIOTLB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_client.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_client.h

## Purpose
This header defines the in-kernel DRM client abstraction used by fbdev emulation and similar internal clients. It covers client lifecycle, hotplug/restore/suspend/resume callbacks, client-owned framebuffers, dumb-buffer creation/mapping/flushing, and helper modeset probing/commit.

## Important APIs, types, and functions
Key types are `struct drm_client_funcs`, `struct drm_client_dev`, and `struct drm_client_buffer`. APIs initialize, register, and release clients; create/delete/flush/vmap/vunmap client buffers; create/free/probe/check/commit client modesets; set DPMS; wait for vblank; and iterate client modesets/connectors. Client state tracks device, name, list entry, callback table, DRM file, modeset mutex, modeset array, suspend state, hotplug pending, and hotplug failure.

## Control Flow
An internal client initializes against a DRM device, registers for callbacks, probes connector/CRTC modesets, allocates buffers, commits modesets under the modeset mutex, responds to hotplug, restores display state on lastclose, and suspends/resumes with the device. Buffer helpers create GEM-backed framebuffers and map them for CPU drawing.

## State and Persistence
Client objects persist on `drm_device.clientlist` until unregister/release. Modesets and buffers persist across hotplug and restore operations until explicitly freed. `suspended`, `hotplug_pending`, and `hotplug_failed` control deferred hotplug behavior.

## Dependencies and Integration Points
It depends on connectors, CRTCs, mode sets, GEM objects, framebuffers, DRM files, `iosys_map`, and module ownership. It integrates internal clients with DRM device unregister, lastclose restore, hotplug events, and framebuffer console support.

## Risks and Test Signals
Risks include hotplug during suspend, modeset mutex misuse, stale connector references, GEM field misuse despite the FIXME, buffer vmap lifetime bugs, restore racing with userspace master acquisition, and writeback connectors being incorrectly used by clients. Tests should cover suspend-hotplug-resume, client unregister while buffers are mapped, lastclose restore with and without force, connector iteration excluding writeback, dumb-buffer creation failure, and vblank waits for each CRTC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_client_event.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_client_event.h

## Purpose
This header declares event fan-out helpers that notify registered DRM clients about device unregister, hotplug, restore, suspend, and resume. It also provides no-op stubs when `CONFIG_DRM_CLIENT` is disabled.

## Important APIs, types, and functions
The API surface is `drm_client_dev_unregister`, `drm_client_dev_hotplug`, `drm_client_dev_restore`, `drm_client_dev_suspend`, and `drm_client_dev_resume`.

## Control Flow
Core DRM and helper paths call these functions at lifecycle and display events. With client support enabled, implementations iterate registered clients and invoke relevant callbacks; with support disabled, static inline stubs discard the event.

## State and Persistence
This header owns no state. It operates on the device's registered client list and client suspend/hotplug bookkeeping declared in `drm_client.h`.

## Dependencies and Integration Points
It depends on `CONFIG_DRM_CLIENT` and `struct drm_device`. It integrates DRM device lifecycle, hotplug helpers, fbdev/client restore, and power management paths.

## Risks and Test Signals
Risks include missing events when the config is disabled, callbacks after unregister, restore semantics when multiple clients exist, and hotplug deferral across suspend. Tests should cover enabled and disabled builds, unregister followed by hotplug, forced restore, suspend/resume ordering, and clients that return errors from hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_client_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_color_mgmt.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_color_mgmt.h

## Purpose
This header declares DRM color management helpers for CRTC gamma/degamma/CTM properties, plane YCbCr encoding/range properties, LUT size and validation helpers, fixed-point conversion, and legacy palette/gamma loading utilities.

## Important APIs, types, and functions
Inline helpers `drm_color_lut_extract` and `drm_color_lut32_extract` round userspace LUT values to hardware precision. Other APIs include `drm_color_ctm_s31_32_to_qm_n`, `drm_crtc_enable_color_mgmt`, `drm_mode_crtc_set_gamma_size`, LUT size helpers, `drm_plane_create_color_properties`, `drm_color_lut_check`, gamma/palette load and fill helpers, and `drm_color_lut32_check`. Enums define YCbCr encodings, ranges, and LUT validation tests.

## Control Flow
Drivers expose color properties during initialization, atomic property setting installs blobs or enum values into state, check paths validate LUT blobs for channel equality or monotonicity as needed, and commit paths convert/load LUT entries into hardware-specific precision.

## State and Persistence
CRTC and plane color properties are persistent KMS properties. LUT blobs are refcounted DRM property blobs referenced by atomic state. Hardware tables are updated during commit from validated blob contents.

## Dependencies and Integration Points
It depends on DRM property blobs, UAPI LUT structures, math64 helpers, CRTC and plane objects, and legacy palette/gamma code. It integrates with atomic color management, legacy gamma IOCTLs, and plane YCbCr conversion controls.

## Risks and Test Signals
Risks include precision overflow for large bit depths, accepting malformed blob lengths, non-monotonic LUTs on hardware that requires monotonic tables, CTM fixed-point conversion mistakes, and mismatched default encoding/range. Tests should cover 16-bit and >16-bit LUT extraction, 32-bit LUT extraction at high precision, invalid blob sizes, equal-channel and non-decreasing checks, gamma size setup, and legacy 888/565/555/palette loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_color_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_colorop.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_colorop.h

## Purpose
This header defines DRM color operation objects used to model per-plane color pipelines. A colorop is a mode object chained through a read-only next pointer and configured through atomic state/properties for curves, LUTs, matrices, multipliers, bypass, and interpolation.

## Important APIs, types, and functions
Important definitions include `DRM_COLOROP_FLAG_ALLOW_BYPASS`, `enum drm_colorop_curve_1d_type`, `struct drm_colorop_state`, `struct drm_colorop_funcs`, and `struct drm_colorop`. Initialization helpers create curve, 1D LUT, 3x4 CTM, multiplier, and 3D LUT operations. Other APIs find, clean up, destroy, duplicate/destroy/reset atomic state, destroy whole pipelines, set next-property links, iterate colorops, and return stable names for types, transfer functions, and interpolation modes.

## Control Flow
Drivers create colorops for a plane, set their supported type/properties, chain them with `drm_colorop_set_next_property`, and expose the pipeline to userspace. Atomic property decoding updates `drm_colorop_state`; plane state can reference a colorop pipeline; check/commit code applies or bypasses operations depending on state and hardware limits.

## State and Persistence
Colorops are persistent DRM mode objects listed in `mode_config.colorop_list`, with invariant indexes and per-plane ownership. Mutable state contains bypass, curve type, multiplier, data blob, and atomic backpointer. Blob data interpretation is type-specific and must survive until state destruction.

## Dependencies and Integration Points
It depends on DRM mode objects, properties, UAPI colorop type enums, planes, atomic state, and property blobs. It integrates with `drm_atomic.h` colorop arrays and the plane color pipeline client capability.

## Risks and Test Signals
Risks include exposing a bypass property that cannot reliably bypass, invalid next-chain topology, blob size/type mismatches, stale blob references after duplicate/destroy, and nonblocking commits reading colorop state without locks. Tests should cover each initializer, state duplicate/destroy with blobs, bypass true fallback, chain ordering and next property IDs, lookup by leased/unleased file, pipeline destruction, and unsupported transfer/interpolation names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_colorop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_connector.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_connector.h

## Purpose
This header defines DRM connector types, sink capability structures, mutable connector atomic state, connector callback tables, HDMI/audio/CEC helpers, command-line mode representation, the central `drm_connector` object, connector property APIs, tile groups, and safe connector-list iteration. It is the main contract for display outputs exposed to userspace.

## Important APIs, types, and functions
Important enums include connector force/status/registration state, TV modes, link status, panel orientation, HDMI broadcast RGB, privacy-screen status, colorspace, output color format, and bus flags. Key structs include `drm_display_info`, HDMI/SCDC/DSC capability structs, TV and HDMI connector state, `drm_connector_state`, HDMI audio/infoframe/CEC function tables, `drm_connector_funcs`, `drm_cmdline_mode`, `drm_connector_hdmi_audio`, `drm_connector_hdmi`, `drm_connector_cec`, `drm_connector`, `drm_tile_group`, and `drm_connector_list_iter`. APIs initialize/register/unregister/cleanup connectors, attach encoders and properties, update EDID/link/VRR/tile/path/privacy/orientation state, create tile groups, iterate connectors safely, and map enum values to names.

## Control Flow
Drivers initialize connectors with function tables and optional DDC/HDMI metadata, attach possible encoders, register connectors to userspace, probe modes through `fill_modes`/detect/EDID helpers, and update properties as hotplug or EDID data changes. Atomic transactions duplicate connector state, set standardized or private properties, select best encoders, route connectors to CRTCs, validate HDMI infoframes/audio/HDR, and commit state. Safe iteration uses `drm_connector_list_iter` because connectors may be hot-added or removed.

## State and Persistence
`struct drm_connector` persists as a refcounted mode object with sysfs/debugfs presence, registration state, mode lists, EDID blob, properties, display info, possible encoders, current legacy encoder, ELD/audio latency, DDC adapter, EDID error counters, tile data, HDMI audio/infoframe state, and CEC data. `drm_connector_state` is mutable atomic state containing CRTC routing, best encoder, link status, TV settings, content/scaling/protection/color/HDR/privacy/max-bpc/writeback/HDMI state. Locks include connector mutex, mode-config mutexes, ELD mutex, EDID override mutex, HDMI infoframe/audio mutexes, and CEC mutex.

## Dependencies and Integration Points
It depends on DRM mode objects, properties, UAPI modes, EDID parsing, HDMI infoframes, I2C DDC, panels, privacy screens, writeback jobs, CEC, platform devices, fwnode, notifier blocks, and encoders/CRTCs. It integrates userspace GETCONNECTOR/atomic properties, hotplug polling, fb helpers, bridge connectors, HDMI codec framework, DP MST tiling, panel orientation quirks, and content protection.

## Risks and Test Signals
Risks include using unregistered connectors in modesets, stale connector references outside list iteration, inconsistent EDID/display_info updates, property creation not matching state fields, HDMI infoframe/audio races with ALSA, privacy-screen notifier races, tile/path blob lifetime bugs, bad max-bpc/colorspace validation, and legacy versus atomic DPMS confusion. Tests should cover hotplug add/remove, registration-state restrictions, connector lookup refcounts and leases, EDID update and corrupt/null counters, command-line forced modes, property attach/set/get paths, HDMI init/infoframe/audio callbacks, CEC physical address updates, tile group refcounts, privacy-screen provider updates, connector-list iteration during removal, and atomic state duplicate/destroy with HDR/writeback blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_connector.h -->
