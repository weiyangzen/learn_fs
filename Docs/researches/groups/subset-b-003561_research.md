# subset-b-003561 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_connector.c

Purpose: Implements the DRM KMS connector core: connector object initialization, registration, cleanup, connector list iteration, standard connector properties, connector ioctls, firmware-node lookup, out-of-band hotplug routing, privacy-screen integration, HDMI metadata helpers, and tiled-monitor group management. Connectors model display sinks and are the user-visible endpoint for modes, EDID, hotplug status, link state, color metadata, DPMS, and routing to encoders.

Important APIs/types/functions: Public exports include `drm_get_connector_type_name`, `drm_connector_init`, `drm_connector_dynamic_init`, `drm_connector_init_with_ddc`, `drmm_connector_init`, `drmm_connector_hdmi_init`, `drm_connector_attach_edid_property`, `drm_connector_attach_encoder`, `drm_connector_has_possible_encoder`, `drm_connector_cleanup`, register/unregister helpers, connector-list iterator helpers, property creation/attachment helpers for DVI-I, TV, scaling, aspect ratio, colorspace, content type, VRR, max bpc, HDR metadata, Broadcast RGB, panel orientation, privacy screen, path, tile, and panel type, `drm_connector_atomic_hdr_metadata_equal`, `drm_connector_property_set_ioctl`, `drm_mode_getconnector`, `drm_connector_find_by_fwnode`, `drm_connector_oob_hotplug_event`, and tile-group refcount helpers. Internal state centers on `struct drm_connector`, `struct drm_display_info`, `struct drm_mode_config`, `connector_list`, per-type `ida`s, mode lists, property blobs, CEC/privacy/HDMI substructures, and `struct drm_tile_group`.

Control flow: Initialization registers a mode object, allocates a 32-bit connector index and per-type ID, names the connector, initializes lists and mutexes, reads `video=` command-line mode overrides, attaches baseline properties, and optionally adds the connector to `mode_config.connector_list`. DRM-managed init registers a cleanup action. HDMI init validates vendor/product strings, connector type, supported output formats, YCbCr420 consistency, max bpc, and infoframe callbacks before attaching max-bpc/HDR state. Registration only proceeds after the DRM device is registered, creates sysfs/debugfs entries, runs late hooks, exposes the mode object, sends hotplug events, registers privacy notifiers, and appends to the global fwnode lookup list. Unregister reverses this sequence, including early sysfs removal, driver hooks, debugfs cleanup, privacy notifier removal, and global-list removal. Cleanup frees modes, IDs, blobs, bus formats, tile/privacy resources, state, locks, fwnodes, and finally zeroes the structure, emitting a hotplug event if the device remains registered.

Control flow continued: `drm_mode_getconnector` resolves the connector, copies possible encoder IDs, optionally forces a probe only for the current DRM master, exposes filtered modes with stereo/aspect-ratio policy, copies mode data to userspace, reads the current encoder under `connection_mutex`, and returns object properties after probing so EDID-derived properties are current. Property helpers create shared properties lazily on `mode_config` or per connector, attach defaults to connector mode objects, and update blobs through `drm_property_replace_global_blob`. Privacy provider attachment creates both software and hardware state properties, snapshots provider state, and later notifiers update state under `connection_mutex` and emit sysfs property events. Tile groups are looked up and allocated through `mode_config.tile_idr` with kref lifetime management.

State and persistence behavior: Connector lifetime is refcounted through `drm_mode_object` and krefs; connector list iteration takes transient refs and defers final freeing through `connector_free_work` if the final put happens while holding the list spinlock. User-visible state is stored in connector mode-object properties, `connector->state` for atomic properties, EDID/path/tile property blobs, persistent display-info arrays, and connector/encoder routing bitmasks. There is no disk persistence, but sysfs/debugfs property exposure and hotplug events are external state surfaces. Locking spans `connector->mutex`, global `connector_list_lock`, `mode_config.connector_list_lock`, `connection_mutex`, and per-feature mutexes for CEC, ELD, EDID override, HDMI infoframes, and HDMI audio.

Dependencies and integration points: Integrates with DRM mode objects, properties, atomic state, framebuffer/modeset ioctls, sysfs/debugfs, EDID parsing and overrides, panel orientation quirks, privacy-screen providers, CEC callbacks, HDMI audio/infoframe support, platform devices, fwnode lookup for Type-C/out-of-band HPD, `video=` command-line parsing, idr/ida allocators, and KMS helper paths that consume connector routing and DPMS state. Driver callbacks in `drm_connector_funcs`, `drm_connector_hdmi_funcs`, and connector helper functions are policy boundaries.

Risks: Connector index allocation is capped at 31 because bitmasks are 32-bit. Many property helpers assume required mode_config properties or atomic state already exist, such as max-bpc needing a connector state. Registration and cleanup ordering is subtle because sysfs/debugfs, global lookup, privacy notifiers, and object registration must be torn down in reverse enough to avoid dangling userspace references. `drm_connector_set_obj_prop` calls legacy `dpms` or driver `set_property` callbacks directly and then updates cached property values, so callback failures and stale legacy state matter. Mode probing in `GETCONNECTOR` mutates connector mode lists only for DRM master; non-master callers see read-only results. Tile/path blobs and privacy-screen state updates can race with hotplug-style userspace polling if locks are not observed by callers.

Test signals: Exercise static and dynamic connector init/register/unregister/cleanup, DRM-managed cleanup, error unwinds for ID/name allocation, HDMI init validation failures, possible-encoder attachment and duplicate-encoder warnings, forced command-line modes and panel orientation, GETCONNECTOR two-pass mode/property copying, non-master probe demotion, stereo/aspect-ratio filtering, EDID/path/tile blob replacement, link-status and VRR updates, privacy-screen notifier behavior, fwnode lookup including secondary fwnode, out-of-band HPD callback dispatch, tile-group refcount/idr lifetime, and hotplug/sysfs/debugfs removal while references are held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc.c

Purpose: Implements core DRM CRTC object support: CRTC lookup, registration hooks, CRC state initialization, out-fence creation, CRTC allocation/init/cleanup helpers, legacy GETCRTC/SETCRTC ioctls, viewport validation, legacy property setting, scaling/sharpness property helpers, and clone-mode detection. A CRTC represents the display pipeline that blends planes and feeds encoders/connectors.

Important APIs/types/functions: Exports include `drm_crtc_from_index`, `drm_mode_set_config_internal`, `drm_crtc_init_with_planes`, `drmm_crtc_init_with_planes`, `__drmm_crtc_alloc_with_planes`, `drm_crtc_cleanup`, `drm_crtc_create_scaling_filter_property`, `drm_crtc_create_sharpness_strength_property`, and `drm_crtc_in_clone_mode`. Internal entry points declared through `drm_crtc_internal.h` include `drm_crtc_force_disable`, `drm_crtc_register_all`, `drm_crtc_unregister_all`, `drm_crtc_create_fence`, `drm_mode_getcrtc`, `drm_mode_setcrtc`, `drm_mode_crtc_set_obj_prop`, and `drm_crtc_check_viewport`.

Control flow: CRTC initialization validates primary/cursor plane types, rejects more than 32 CRTCs, warns about missing atomic state callbacks for atomic drivers, initializes commit tracking, modeset lock, mode object, name, fence context/timeline, object properties, list linkage, index, primary/cursor plane back-links, CRC state, and atomic properties (`ACTIVE`, `MODE_ID`, out-fence pointer, VRR). DRM-managed helpers register cleanup actions or allocate the containing object. Cleanup frees CRC source state, gamma storage, modeset lock, mode object/list membership, atomic state, and name before zeroing the structure.

Control flow continued: `drm_mode_getcrtc` finds the CRTC, locks the primary plane to return current framebuffer and source offsets, then locks the CRTC to return atomic or legacy mode/enabled state and applies aspect-ratio filtering. `drm_mode_setcrtc` validates modeset support, source coordinate range, CRTC and framebuffer IDs, leasing of the primary plane for enable, mode conversion, aspect-ratio permissions, primary-plane format/modifier support, viewport bounds, connector count consistency, connector lookup, and then dispatches to atomic `set_config` or legacy `__drm_mode_set_config_internal` under the all-modeset lock retry macro. The legacy internal set_config wrapper snapshots old primary framebuffers for every CRTC, invokes the driver/helper callback, updates primary plane crtc/fb on success, and performs framebuffer get/put refcount balancing.

State and persistence behavior: Persistent kernel state includes CRTC index/name/list membership, primary/cursor plane pointers, `crtc->state` for atomic drivers, legacy `enabled/mode/hwmode/x/y`, fence timeline seqno/context, CRC debugfs source/ring state initialized here and consumed by `drm_debugfs_crc.c`, and object properties. There is no disk persistence. Locking uses per-CRTC and per-plane modeset locks plus global lock-all acquisition for SETCRTC.

Dependencies and integration points: Integrates with DRM planes, framebuffers, mode conversion, properties, dma-fence, debugfs CRC, atomic UAPI, legacy helper `set_config`, driver CRTC callbacks, mode_config object registration, leasing/auth, and KMS ioctl dispatch. Atomic drivers still pass through this file for object creation and legacy ioctl translation to atomic set_config.

Risks: CRTC indices cannot exceed 31 because CRTC masks are 32-bit. Cleanup comments assume CRTC lists are mostly static; runtime removal would disturb indices. Legacy SETCRTC has complex unwind paths over framebuffer, connector, and mode references. `__drm_mode_set_config_internal` must preserve old framebuffers across all CRTCs because one legacy set_config may steal connectors and disable other CRTCs. Viewport checks depend on current primary-plane rotation state. `drm_crtc_create_fence` allocates fences with CRTC-owned lock and timeline, so callers must signal/drop fences correctly elsewhere.

Test signals: Cover init with invalid plane types, too many CRTCs, missing callbacks, name allocation failure, CRC source allocation failure, DRM-managed cleanup, GETCRTC for atomic and legacy state, SETCRTC disable and enable paths, framebuffer `-1` reuse, unknown framebuffer/connector IDs, lease denial, invalid aspect-ratio bits, format/modifier rejection, rotated viewport bounds, connector count mismatch, atomic vs legacy set_config dispatch, framebuffer refcount preservation when set_config steals outputs, scaling/sharpness property creation, and clone-mode encoder mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper.c

Purpose: Provides the deprecated legacy CRTC modeset helper implementation used by non-atomic drivers. It supplies encoder/CRTC in-use checks, unused-output disable, full mode programming sequencing, a default atomic CRTC check for simple primary-plane CRTCs, legacy `set_config`, connector DPMS handling, resume mode restoration, and force-disable-all behavior.

Important APIs/types/functions: Exports include `drm_helper_encoder_in_use`, `drm_helper_crtc_in_use`, `drm_helper_disable_unused_functions`, `drm_crtc_helper_set_mode`, `drm_crtc_helper_atomic_check`, `drm_connector_get_single_encoder`, `drm_crtc_helper_set_config`, `drm_helper_connector_dpms`, `drm_helper_resume_force_mode`, and `drm_helper_force_disable_all`. Important callback dependencies are `drm_crtc_helper_funcs` (`mode_fixup`, `prepare`, `mode_set`, `commit`, `disable`, `dpms`, `mode_set_base`), `drm_encoder_helper_funcs` (`mode_fixup`, `prepare`, `mode_set`, `commit`, `disable`, `dpms`), and `drm_connector_helper_funcs.best_encoder`.

Control flow: In-use helpers walk connector/encoder routing under mode_config and connection locks and warn if used with atomic modeset. Unused disable first disables unreferenced encoders and clears their CRTC pointers, then disables CRTCs without in-use encoders and clears primary framebuffer pointers. `drm_crtc_helper_set_mode` saves current CRTC state, updates desired mode/x/y, lets encoders and CRTC run `mode_fixup`, copies adjusted mode to `hwmode`, prepares encoders and CRTC, calls CRTC `mode_set`, calls encoder `mode_set`, commits CRTC then encoders, calculates timestamping constants, and rolls back saved software state if any step fails.

Control flow continued: `drm_crtc_helper_set_config` validates the legacy interface, handles disable when no framebuffer is requested, snapshots all encoder and connector routing, determines whether a full modeset or base update is needed from framebuffer, coordinates, mode, encoder, CRTC, and DPMS changes, gets refs on newly bound connectors, chooses best encoders, validates encoder-to-CRTC routing, executes either full `drm_crtc_helper_set_mode` plus DPMS-on or `mode_set_base`, disables unused functions, and restores saved routing plus tries to restore the old mode on failure. DPMS helper computes aggregate encoder and CRTC DPMS from all attached connectors and orders callbacks CRTC-before-encoder for power-up and encoder-before-CRTC for power-down.

State and persistence behavior: This file mutates legacy in-memory fields directly: `connector->encoder`, `connector->dpms`, `encoder->crtc`, `crtc->enabled`, `crtc->mode`, `crtc->hwmode`, `crtc->x/y`, and `crtc->primary->fb`. It does not persist state outside RAM. Rollback is limited to core routing and CRTC fields; comments explicitly note driver-private bookkeeping is not restored.

Dependencies and integration points: Integrates with DRM connector list iterators, CRTC/encoder/connector helper callback tables, vblank timestamping, framebuffer state, mode comparison/copy/duplication, modeset locks, atomic helper check for primary-plane presence, and legacy CRTC funcs `set_config`. The file is explicitly not suitable for atomic modeset drivers except the small CRTC atomic-check helper.

Risks: The helper is deprecated because it calls disable/dpms hooks without the stronger state guarantees atomic helpers provide. Failure rollback may leave driver-private hardware or bookkeeping partially changed. `drm_crtc_helper_disable` drops connector references for connectors previously held while encoder-bound, so reference ownership must match legacy expectations. `mode_set_base` fallback to full modeset is based on helper callback presence and framebuffer format equality, not full hardware capability. DPMS aggregation uses numeric DPMS ordering, so connector state must be canonical. Many functions WARN but still proceed if called in unsuitable atomic contexts.

Test signals: Legacy-driver tests should cover no-op set_config, framebuffer-only flips, coordinate-only base updates, full mode changes, encoder reassignment, CRTC stealing, DPMS-off connector re-enable, best_encoder failure, encoder/CRTC compatibility rejection, mode_fixup and mode_set failure rollback, failed restore logging, disable path with bound connectors, resume-force-mode preserving powered-off outputs, force-disable-all iterating enabled CRTCs, and lockdep expectations for mode_config and connection locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper_internal.h

Purpose: Private header for the DRM KMS helper module. It exposes only internal helper-layer prototypes shared between legacy CRTC helpers and probe helpers; these interfaces are not exported to drivers.

Important APIs/types/functions: Declares opaque structs and `drm_crtc_mode_valid`, `drm_encoder_mode_valid`, `drm_connector_mode_valid`, and `drm_connector_get_single_encoder`. The mode-validation functions are implemented in probe-helper code, while `drm_connector_get_single_encoder` is implemented in `drm_crtc_helper.c`.

Control flow: There is no runtime control flow in the header. It defines the compile-time coupling that lets helper code validate a mode against CRTC, encoder, and connector callbacks and lets probe/configuration code fetch the sole possible encoder when a connector does not need a `best_encoder` policy.

State and persistence behavior: No state is stored here. The declarations operate on caller-owned DRM connector, encoder, CRTC, display mode, and modeset acquire context objects.

Dependencies and integration points: Integrates the legacy/helper KMS module with `drm_probe_helper.c` and `drm_crtc_helper.c`. It forward-declares only the types required by these internal prototypes, keeping the include boundary small.

Risks: Because this is an internal header, signature drift must be kept synchronized across helper C files. `drm_connector_get_single_encoder` is only correct for connectors with one possible encoder and warns when that assumption is violated.

Test signals: Build coverage is the main signal. Functional coverage comes from mode-probe validation tests and legacy set_config paths that use connector mode validation and single-encoder fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_internal.h

Purpose: Private DRM KMS core header collecting internal prototypes for mode setting, ioctls, mode objects, connectors, CRTCs, encoders, planes, framebuffers, dumb buffers, properties, color management, EDID, atomic UAPI, bridge detachment, and optional DRM panic support. It is the internal linkage map for the DRM module, not a driver-facing API.

Important APIs/types/functions: Declares CRTC helpers (`drm_mode_crtc_set_obj_prop`, `drm_crtc_check_viewport`, register/unregister, force-disable, fence creation), mode-config lifecycle, resources ioctl, dumb-buffer ioctls, gamma ioctls, property/blob ioctls and validation, mode-object add/find/register/unregister/property enumeration, encoder/connector/plane ioctls and registration helpers, framebuffer creation/release/add/remove/dirty helpers, atomic debugfs and UAPI setters/getters, `__drm_atomic_helper_disable_plane`, `__drm_atomic_helper_set_config`, `drm_atomic_print_new_state`, EDID override and CTA SAD helpers, DisplayID/EDID extension lookup, firmware EDID loading stub, and DRM panic hooks.

Control flow: There is no executable flow. The header defines which symbols are callable across compilation units inside the DRM core and selects stubs for optional features with `#ifdef CONFIG_DEBUG_FS`, `CONFIG_DRM_LOAD_EDID_FIRMWARE`, and `CONFIG_DRM_PANIC`.

State and persistence behavior: No state is stored here. The prototypes expose operations over DRM device-owned state such as mode_config lists, object id registries, framebuffer lists, property blobs, connector/CRTC/plane atomic state, and optional panic registration.

Dependencies and integration points: Integrates nearly all core KMS implementation files and ioctl handlers. It forward-declares many DRM and kernel structs to avoid pulling large public headers into every implementation file. It also bridges optional subsystems: debugfs, firmware EDID, and panic display.

Risks: This file is a high-blast-radius contract: changing a prototype affects multiple core files and sometimes ioctl behavior. Because it is internal, there is less ABI stability pressure, but the functions it declares often back UAPI ioctls. Conditional stubs must match real implementations exactly enough that non-enabled builds compile and preserve expected no-op semantics.

Test signals: Full DRM build coverage across configs with and without `CONFIG_DEBUG_FS`, `CONFIG_DRM_LOAD_EDID_FIRMWARE`, and `CONFIG_DRM_PANIC`; ioctl smoke tests for mode resources, CRTC, connector, plane, framebuffer, property, dumb-buffer, gamma, and atomic paths; and sparse/build warnings for mismatched prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_damage_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_damage_helper.c

Purpose: Implements DRM atomic damage helpers for partial framebuffer updates. It converts legacy DIRTYFB clip rectangles into atomic plane damage blobs, discards damage when a full modeset is needed, iterates damage clipped to the plane source rectangle, and merges damage into one bounding rectangle.

Important APIs/types/functions: Exports `drm_atomic_helper_check_plane_damage`, `drm_atomic_helper_dirtyfb`, `drm_atomic_helper_damage_iter_init`, `drm_atomic_helper_damage_iter_next`, and `drm_atomic_helper_damage_merged`. Internal helper `convert_clip_rect_to_rect` translates `struct drm_clip_rect` arrays to `struct drm_mode_rect` arrays. Main types are `struct drm_atomic_state`, `struct drm_plane_state`, `struct drm_property_blob`, `struct drm_atomic_helper_damage_iter`, and `struct drm_rect`.

Control flow: Atomic check inspects the new CRTC state for a plane and drops `fb_damage_clips` if the CRTC needs a modeset so drivers perform full plane updates. `drm_atomic_helper_dirtyfb` allocates an atomic state and optional damage blob, handles annotated-copy clip pairs by using every other clip, locks each plane using the framebuffer, replaces that plane state's damage blob, commits the atomic state, and handles `-EDEADLK` by clearing state, backing off, and retrying. Damage iterator init exits early for invisible/unbound planes, loads damage clips and count, computes integer source bounds from 16.16 fixed-point source coordinates with outward rounding, and switches to full update when clips are absent, ignored, or the source rectangle changed. Iterator next returns full source once or walks clips until one intersects the plane source. Merge uses the iterator to accumulate min/max bounds.

State and persistence behavior: Damage is transient atomic state stored in `plane_state->fb_damage_clips` as a property blob. DIRTYFB commits are blocking and use modeset acquire context and atomic state lifetime rules. No disk persistence exists. The helper owns temporary clip arrays and damage blobs only until commit and state cleanup.

Dependencies and integration points: Integrates legacy framebuffer dirty callbacks with atomic plane commits, DRM property blobs, modeset locking/backoff, plane source clipping, framebuffer ownership, and driver atomic plane update paths that consume damage through the iterator macros.

Risks: Large clip counts can allocate sizable arrays/blobs. Annotated-copy mode halves `num_clips`, so odd inputs rely on legacy semantics and may discard the last clip. Full modesets and source-rectangle changes intentionally discard fine-grained damage, which can surprise performance tests but is necessary for correctness. Drivers must call `drm_atomic_helper_check_plane_damage` and `drm_atomic_helper_check_plane_state` at the expected times for iterator assumptions to hold. `dirtyfb` commits all planes currently scanning out the framebuffer, so multi-plane use of the same fb can fan out work.

Test signals: DIRTYFB with no clips, normal clips, annotated-copy clips, framebuffer used by zero/one/multiple planes, interruptible vs internal caller locking, `-EDEADLK` retry, allocation failures, full modeset damage discard, source-rect changes forcing full update, invisible/unbound planes producing no damage, fixed-point rounding at fractional source bounds, clips outside source being skipped, and merged damage bounding-box correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_damage_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs.c

Purpose: Implements DRM debugfs infrastructure: global roots, per-device/minor symlinks, default debug files, per-client debug directories, driver-added debugfs entries, connector/CRTC/encoder debugfs trees, EDID override and force controls, connector display diagnostics, HDMI infoframe dumps, GPU VA dumps, and cleanup.

Important APIs/types/functions: Public/internal functions include `drm_debugfs_gpuva_info`, `drm_debugfs_create_files`, `drm_debugfs_remove_files`, `drm_debugfs_bridge_params`, `drm_debugfs_init_root`, `drm_debugfs_remove_root`, `drm_debugfs_clients_add`, `drm_debugfs_clients_remove`, `drm_debugfs_dev_init`, `drm_debugfs_dev_fini`, `drm_debugfs_dev_register`, `drm_debugfs_register`, `drm_debugfs_unregister`, `drm_debugfs_add_file`, `drm_debugfs_add_files`, `drm_debugfs_connector_add/remove`, `drm_debugfs_crtc_add/remove`, and `drm_debugfs_encoder_add/remove`. Static show/write paths cover `name`, `clients`, `gem_names`, client `proc_info`, connector `force`, `edid_override`, `vrr_range`, `output_bpc`, audio/AVI/HDMI/HDR/SPD infoframes, and bridge/encoder params.

Control flow: Root init creates `/sys/kernel/debug/dri` and optionally `/sys/kernel/debug/accel`. Device init creates a unique device directory under the appropriate root. Device registration adds default files and modeset/atomic debugfs support. Minor registration adds numeric symlinks to the device directory and invokes legacy driver debugfs init for non-render minors. The default file-open helpers reject access if the underlying device node is no longer registered, then bind a seq_file to either `drm_info_node` or `drm_debugfs_entry`. Driver file addition allocates entries with DRM-managed memory and creates read-only debugfs files.

Control flow continued: Connector debugfs creation builds a connector-named directory with writable `force` and `edid_override`, read-only VRR/output-bpc diagnostics, HDMI infoframe files when supported callbacks exist, and driver connector debugfs hooks. The force writer parses fixed strings into `connector->force`; EDID writer either resets or installs an override buffer. HDMI audio infoframes are read under the connector HDMI infoframe mutex, while AVI/HDMI/HDR/SPD state infoframes are read under `connection_mutex` from connector atomic state. CRTC debugfs creates `crtc-N`, then adds CRC files through `drm_debugfs_crtc_crc_add`. Encoder debugfs creates `encoder-N`, bridge params, and optional driver hooks.

State and persistence behavior: Debugfs dentries are stored in device, connector, CRTC, encoder, minor, and drm_file fields. Per-client directories are named by `client_id` and link to the owning DRM device. Writes mutate in-memory connector force state and EDID override state. No persistent storage is used; debugfs contents disappear on cleanup or reboot. Locking uses master/filelist/client-name mutexes, RCU for process identity, object-name mutex, HDMI infoframe mutex, and `connection_mutex` for connector state infoframes.

Dependencies and integration points: Integrates with Linux debugfs/seq_file, DRM minors, masters, GEM names, file/client tracking, GPUVM, EDID override internals, connector/CRTC/encoder objects, HDMI infoframe packing, bridge debugfs, framebuffer/client/atomic debugfs initializers, and driver-specific debugfs callbacks.

Risks: Debugfs is diagnostic but can mutate connector force and EDID override, so tests must treat it as a control surface. Several creation paths ignore allocation/debugfs failures by design, so missing files may not fail device registration. `drm_debugfs_remove_files` uses lookup and DRM-managed free of inode private data, so stale open files and lifetime ordering need care. The client symlink target uses `dev->unique`; unexpected unique strings can affect link readability. HDMI infoframe reads depend on state/callback support and return empty data when infoframes are unset.

Test signals: Root/device/minor creation and removal, default file contents for name/clients/gem names, client add/remove with proc_info and device symlink, GPUVM dump with initialized and uninitialized managers, connector force string parsing and invalid length/input, EDID override set/reset, VRR/output_bpc returning `-ENODEV` when disconnected, HDMI infoframe files only for supported callbacks and correct packed bytes, CRTC CRC debugfs creation, encoder bridge params, driver debugfs hooks, and access after device unregister returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs_crc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs_crc.c

Purpose: Implements the DRM debugfs CRTC CRC ABI. It lets userspace inspect/select a CRTC CRC source and read per-frame CRC samples from a debugfs ring buffer populated by drivers.

Important APIs/types/functions: Exports `drm_crtc_add_crc_entry`; internal debugfs setup is `drm_debugfs_crtc_crc_add`. File operations are implemented by `crc_control_show/open/write`, `crtc_crc_open/release/read/poll`, and helpers `crtc_crc_data_count` and `crtc_crc_cleanup`. Main state is `struct drm_crtc_crc` inside `struct drm_crtc`: `source`, `opened`, `entries`, `head`, `tail`, `values_cnt`, `overflow`, `lock`, and waitqueue.

Control flow: CRC debugfs files are created only when the CRTC supplies both `set_crc_source` and `verify_crc_source`. The control file lists valid sources from optional `get_crc_sources` and marks the active one, or prints the active source alone. Writing a source copies and NUL-terminates user input, strips a trailing newline, validates it through the driver, refuses changes while the data file is open, and swaps `crc->source` under the spinlock. Opening `crc/data` optionally checks active atomic CRTCs, validates source and value count, allocates the fixed ring buffer, marks it opened under the spinlock, and asks the driver to enable the source. Release clears `opened`, disables the driver source with `NULL`, and frees/reset ring state.

Control flow continued: Reads wait for ring data unless opened nonblocking, validate the user buffer can hold one formatted line, pop one ring entry, release the lock, format the frame counter or `XXXXXXXXXX` plus each CRC as hex fields, and copy to userspace. Poll watches the waitqueue and reports readable when a source and buffered data exist. `drm_crtc_add_crc_entry` is called by drivers, rejects calls when no entries are allocated, drops samples with `-ENOBUFS` on ring overflow while logging the first overflow, writes frame/CRC values into the head entry, advances the power-of-two circular index, and wakes readers.

State and persistence behavior: State is volatile per CRTC and debugfs session. The active source string persists in memory across control reads/writes until CRTC cleanup, with default allocation in `drm_crtc.c`. The data ring exists only while `crc/data` is open. Spinlocks protect ring and source/opened fields; waitqueues coordinate blocking readers.

Dependencies and integration points: Integrates with CRTC driver callbacks `verify_crc_source`, `set_crc_source`, and optional `get_crc_sources`; atomic CRTC active state; Linux debugfs, poll, waitqueue, circular buffer helpers, and userspace copy helpers. CRTC debugfs directories are created by `drm_debugfs.c`.

Risks: Only one reader can open `crc/data`; control source changes are blocked while opened. Drivers must supply stable `values_cnt` and exactly that many CRC values for each entry. Ring overflow indicates userspace reads too slowly and drops samples. Atomic active-state check prevents opening CRC capture on inactive CRTCs, but legacy behavior depends on driver callbacks. Read formatting consumes a whole entry per read and requires user buffer large enough for the configured CRC count.

Test signals: Source listing with and without `get_crc_sources`, selecting valid/invalid sources, newline stripping, refusing oversized writes, refusing source changes while data is open, open failure for inactive atomic CRTC, invalid zero/too-large value counts, driver enable failure cleanup, blocking and nonblocking reads, poll readiness, formatting with and without frame counters, ring overflow path and one-time log, release disabling source, and driver calls to `drm_crtc_add_crc_entry` before/after open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_debugfs_crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid.c

Purpose: Implements iteration over DisplayID data blocks embedded in EDID extension blocks. It validates DisplayID section headers/checksums, applies monitor-specific quirks, walks all DisplayID extensions, and exposes base-section version and primary-use/product-type values.

Important APIs/types/functions: Internal/public-to-DRM functions include `displayid_iter_edid_begin`, `__displayid_iter_next`, `displayid_iter_end`, `displayid_version`, and `displayid_primary_use`. Static helpers are `get_quirks`, `displayid_get_header`, `validate_displayid`, `find_next_displayid_extension`, and `displayid_iter_block`. Main types are `struct displayid_iter`, `struct displayid_header`, `struct displayid_block`, and quirk descriptors keyed by `struct drm_edid_ident`.

Control flow: Iterator begin clears the iterator, stores the DRM EDID pointer, and records quirks. `__displayid_iter_next` first advances within the current section by the previous block header plus payload length; if no next block is valid, it searches for the next EDID extension with `DISPLAYID_EXT`, validates section length and checksum, records base-section version and primary-use from the first section, skips the DisplayID header, and returns the first valid data block. On exhaustion or invalid extension, it clears `drm_edid` so further calls return NULL. `displayid_iter_end` zeros the iterator.

State and persistence behavior: Iteration state is fully contained in caller-provided `struct displayid_iter`: current EDID, section pointer, section length, byte index, extension index, base version, primary-use/product-type, and quirks. No allocations or persistent state are used. Returned block pointers reference the original EDID data.

Dependencies and integration points: Integrates with DRM EDID helpers `drm_edid_find_extension` and `drm_edid_match`, DisplayID structures/constants from `drm_displayid_internal.h`, and DRM logging for checksum notes. EDID parsers use this iterator to find detailed timing, tiled display, vendor-specific, CTA, and other DisplayID blocks.

Risks: Invalid checksum causes the whole extension to be skipped unless a quirk says to ignore it. `find_next_displayid_extension` sets length to `EDID_LENGTH - 1` because the EDID extension checksum is outside DisplayID payload, so off-by-one mistakes would truncate or overrun parsing. The iterator stops on malformed current-block state with `WARN_ON`, which prevents continuing into later extensions. Base-section version/primary-use come from the first DisplayID section encountered.

Test signals: EDIDs with no DisplayID extension, one valid extension with multiple blocks, multiple DisplayID extensions, truncated headers, blocks whose payload exceeds section length, invalid checksums with and without the CSO quirk, base-section version/primary-use capture, iterator end/reset behavior, and consumers using `displayid_iter_for_each` over all block types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid_internal.h

Purpose: Defines DRM-internal DisplayID constants, packed wire-format structures, and iterator declarations used by EDID/DisplayID parsing code.

Important APIs/types/functions: Defines VESA OUI, DisplayID 2.0 version, DisplayID 1.x and 2.0 data-block tags, product type and primary-use constants, packed structs `displayid_header`, `displayid_block`, `displayid_tiled_block`, `displayid_detailed_timings_1`, `displayid_detailed_timing_block`, `displayid_formula_timings_9`, `displayid_formula_timing_block`, and `displayid_vesa_vendor_specific_block`, bitfield masks `DISPLAYID_VESA_MSO_OVERLAP` and `DISPLAYID_VESA_MSO_MODE`, private iterator struct `displayid_iter`, iterator declarations, `displayid_iter_for_each`, `displayid_version`, and `displayid_primary_use`.

Control flow: There is no executable flow. The header maps DisplayID byte layouts into packed C structures and provides declarations for the iterator implemented in `drm_displayid.c`.

State and persistence behavior: No global state is stored. `struct displayid_iter` carries transient parse state over EDID memory supplied by callers. Packed structs are views over EDID/DisplayID binary data and should not be treated as independently owned storage.

Dependencies and integration points: Used by `drm_displayid.c` and EDID parsing paths that decode tiled display topology, detailed timings, formula timings, VESA vendor-specific MSO data, and CTA/vendor blocks. It depends only on Linux integer/bit headers and a forward declaration of `struct drm_edid`.

Risks: Packed struct definitions must exactly match the DisplayID specification; field-size mistakes propagate into EDID parsing and mode discovery. Multibyte fields are little-endian where declared and require correct conversion by consumers. The iterator is marked private and should not be accessed directly outside its helper API.

Test signals: Compile-time layout checks where available, parser tests using known DisplayID fixtures for each block type, tiled-topology EDIDs, detailed/formula timing EDIDs, VESA vendor-specific MSO data, DisplayID 1.x vs 2.0 tag handling, and endian-sensitive multibyte timing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_displayid_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw.c

Purpose: Provides low-level DRM drawing helpers for converting XRGB8888 colors and drawing monochrome bitmap glyphs or solid fills into mapped framebuffer memory for common 16-, 24-, and 32-bit pixel layouts.

Important APIs/types/functions: Exports `drm_draw_can_convert_from_xrgb8888`, `drm_draw_color_from_xrgb8888`, `drm_draw_blit16`, `drm_draw_blit24`, `drm_draw_blit32`, `drm_draw_fill16`, `drm_draw_fill24`, and `drm_draw_fill32`. It uses conversion helpers from `drm_format_internal.h`, pixel formats from `drm_fourcc.h`, foreground-bit helpers from `drm_draw_internal.h`, and `iosys_map_wr` for memory or I/O mapped destinations.

Control flow: Format support is a switch over specific RGB565, RGB/X/ARGB 1555, RGB888, X/ARGB/XBGR/ABGR8888, and 2101010 variants. Color conversion dispatches to per-format helpers and warns once for unsupported formats. Blit helpers iterate destination pixels, sample a monochrome source bitmap at `x / scale, y / scale`, and write only foreground pixels in the requested output width. The 24-bit path writes three bytes explicitly in little-endian blue/green/red order. Fill helpers iterate every destination pixel and write the supplied converted color, also using explicit byte writes for 24-bit pixels.

State and persistence behavior: No state is retained. All writes go directly to the caller-provided `struct iosys_map` at offsets computed from pitch, coordinates, and bytes per pixel. Source bitmap data is read-only and caller-owned.

Dependencies and integration points: Used by DRM panic/console or simple drawing paths that need to render glyphs or fills into framebuffers without a full acceleration stack. Integrates with Linux `iosys-map`, DRM fourcc formats, and internal pixel conversion helpers.

Risks: Callers must ensure destination dimensions, pitch, scale, and mapping are valid; the helpers do no bounds checking. Unsupported formats return false/0 and conversion emits a WARN_ONCE. The 24-bit write order assumes the expected little-endian byte layout. Blit only paints foreground pixels and leaves background untouched, so callers must pre-fill if they need a background color.

Test signals: Color conversion tests for every supported format, unsupported format warning/zero return, 16/24/32 blit output for representative glyph bitmaps and scale factors, fill output and pitch handling, 24-bit byte order verification, iosys_map I/O and system-memory destinations, and bounds tests in callers that clip draw rectangles before invoking these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw_internal.h

Purpose: Private DRM drawing header that declares color conversion, blit, and fill helpers and defines inline bitmap helpers for glyph drawing.

Important APIs/types/functions: Inline helpers are `drm_draw_is_pixel_fg`, which tests a bit in a 1-bpp source bitmap, and `drm_draw_get_char_bitmap`, which returns the bitmap start for a character in a `struct font_desc`. It declares all drawing functions implemented in `drm_draw.c`: format support, XRGB8888 color conversion, 16/24/32-bit blits, and 16/24/32-bit fills.

Control flow: The foreground test computes `sbuf8[(y * spitch) + x / 8] & (0x80 >> (x % 8))`, matching MSB-first glyph bitmap storage. Character lookup advances by `c * font->height * font_pitch`.

State and persistence behavior: No state is stored. The helpers operate on caller-owned font/bitmap memory and destination maps.

Dependencies and integration points: Includes Linux font and integer types and forward-declares `struct iosys_map`. It is consumed by DRM drawing users and `drm_draw.c`, providing a compact internal contract without exposing these helpers as public UAPI.

Risks: Callers must pass a character index valid for the font data and a pitch matching the font bitmap layout. Negative or out-of-range x/y values in `drm_draw_is_pixel_fg` would index invalid memory; callers and blit loops are responsible for sane coordinates.

Test signals: Unit-style checks for MSB-first bit extraction, glyph pointer offsets for known font dimensions and pitch, declarations matching `drm_draw.c`, and draw callers clipping source coordinates before invoking inline helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw_internal.h -->
