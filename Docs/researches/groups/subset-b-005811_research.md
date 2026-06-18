# subset-b-005811 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_crtc.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_crtc.h

Purpose: Defines the DRM CRTC core interface for KMS display pipelines: mutable atomic CRTC state, legacy CRTC fields, CRTC callback contracts, CRTC registration/cleanup helpers, lookup helpers, and iteration/mask utilities. It is the central contract for scanout timing, mode transitions, vblank/page-flip events, color management, cursor/primary plane compatibility, and per-CRTC debug/CRC state.

Important APIs, types, and functions: Key types are `struct drm_crtc_state`, `struct drm_crtc_funcs`, `struct drm_crtc`, and `struct drm_mode_set`. Important state fields include `enable`, `active`, `planes_changed`, `mode_changed`, `active_changed`, `connectors_changed`, `zpos_changed`, `color_mgmt_changed`, `no_vblank`, `plane_mask`, `connector_mask`, `encoder_mask`, `mode`, `adjusted_mode`, color blobs, background color, target vblank, VRR/self-refresh flags, flip event, and commit pointer. Important callbacks cover reset, legacy cursor/gamma/config/page-flip/property operations, atomic duplicate/destroy/get/set property, debugfs registration, CRC source management, atomic state printing, and vblank counter/interrupt/timestamp hooks. Exported helpers include `drm_crtc_init_with_planes()`, `drmm_crtc_init_with_planes()`, `drm_crtc_cleanup()`, `drmm_crtc_alloc_with_planes()`, `drm_crtc_index()`, `drm_crtc_mask()`, `drm_mode_set_config_internal()`, `drm_crtc_from_index()`, `drm_crtc_find()`, CRTC list iteration macros, `drm_crtc_create_scaling_filter_property()`, `drm_crtc_in_clone_mode()`, and `drm_crtc_create_sharpness_strength_property()`.

Control flow: Atomic commits assemble a `drm_crtc_state`, set change flags during checking, then commit hardware changes and eventually signal `event` through vblank or fake-vblank paths. Legacy modesets use `struct drm_mode_set` and `set_config`, while atomic drivers normally route legacy paths through atomic helpers. Page flips may use immediate vblank-targeted callbacks, with the core acquiring vblank references around target flips and the driver releasing them when completion is signalled. Registration attaches a CRTC to `drm_mode_config.crtc_list`, assigns an index/mask, binds primary and cursor planes for legacy IOCTL compatibility, and installs callback tables. Managed allocation variants tie cleanup to DRM managed resources.

State and persistence: This header declares runtime-only state, not persistent storage. CRTC state is protected by the CRTC modeset lock; pending commits are tracked on `commit_list` under `commit_lock`; event delivery is coordinated with the device event lock; CRC capture state is embedded in the CRTC; legacy fields mirror atomic state for non-atomic users. Persistent user-visible ABI appears through object IDs, properties, event semantics, and mode/blob exposure rather than disk state.

Dependencies and integration points: Depends on DRM mode objects, modes, planes, mode config, modeset locks, device state, debugfs CRC, vblank core, atomic helpers, bridge/connector/encoder routing, property blobs, self-refresh helpers, and optional device tree port matching. Drivers integrate by embedding or allocating `struct drm_crtc`, supplying `drm_crtc_funcs`, optionally subclassing `drm_crtc_state`, wiring primary/cursor planes, and using helper callbacks for legacy-to-atomic compatibility.

Risks and test signals: Risks include confusing `enable` versus `active`, missing change flags that should trigger a modeset, signalling flip events with wrong vblank timestamps, leaking or double-freeing state blob references in custom duplicate/destroy hooks, lock-order mistakes around CRTC and connection locks, incorrect plane/connector/encoder masks, broken no-vblank fake-event behavior, and stale legacy fields in atomic drivers. Test with atomic check-only and commit paths, DPMS active toggles, full modesets, page flips with and without target vblank, disabled-CRTC events, CRC debugfs open/source changes, color management properties, VRR/self-refresh toggles, cursor legacy IOCTLs, hot-unregister debugfs hooks, and multi-CRTC clone routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_crtc_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_crtc_helper.h

Purpose: Declares the legacy DRM modesetting helper entry points used by drivers that rely on shared CRTC/encoder/connector helper code instead of hand-implementing all KMS transitions.

Important APIs, types, and functions: Exposes `drm_helper_disable_unused_functions()`, `drm_crtc_helper_set_config()`, `drm_crtc_helper_set_mode()`, `drm_crtc_helper_atomic_check()`, `drm_helper_crtc_in_use()`, `drm_helper_encoder_in_use()`, `drm_helper_connector_dpms()`, `drm_helper_resume_force_mode()`, and `drm_helper_force_disable_all()`. It forward-declares the KMS objects used by these helpers.

Control flow: Drivers route legacy `set_config` and DPMS paths into these helpers. The helpers evaluate whether CRTCs and encoders are in use, apply modes or disable unused functions, and provide resume/force-disable paths that restore or shut down display pipelines after suspend or error handling. Atomic-capable users can call the atomic check helper to validate a CRTC contribution in a shared path.

State and persistence: No state is stored in the header. Runtime effects occur in CRTC/encoder/connector state and hardware programmed by helper implementations.

Dependencies and integration points: Integrates with CRTC, encoder, connector, framebuffer, display mode, atomic state, and modeset acquire contexts. It exists for helper-based KMS drivers and legacy compatibility paths, often alongside `drm_crtc_funcs.set_config`.

Risks and test signals: Risks include mixing helper and driver-private modeset sequencing inconsistently, missing modeset acquire contexts, leaving unused encoders enabled, and resume paths restoring stale modes. Test legacy SETCRTC, connector DPMS, suspend/resume, forced global disable, and helper paths in drivers that also expose atomic APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_crtc_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_damage_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_damage_helper.h

Purpose: Provides helper declarations and iterator state for using framebuffer damage clips in atomic plane updates and dirty framebuffer handling.

Important APIs, types, and functions: Defines `struct drm_atomic_helper_damage_iter`, the iterator macro `drm_atomic_for_each_plane_damage()`, and declares `drm_atomic_helper_check_plane_damage()`, `drm_atomic_helper_dirtyfb()`, `drm_atomic_helper_damage_iter_init()`, `drm_atomic_helper_damage_iter_next()`, and `drm_atomic_helper_damage_merged()`. The iterator tracks the plane source rectangle, damage clip array, clip count, current index, and whether a full update is required.

Control flow: Atomic plane checking records whether damage information is usable. Drivers initialize an iterator from old/new plane state and call `drm_atomic_for_each_plane_damage()` to receive clipped rectangles in framebuffer coordinates. If userspace provided no damage, helpers fall back to the full plane source. Dirty framebuffer IOCTL handling can be routed through `drm_atomic_helper_dirtyfb()` to trigger the same update logic.

State and persistence: Damage is transient commit state. The iterator holds temporary traversal state only; persistent state remains in plane state, framebuffer objects, and userspace-provided damage blobs.

Dependencies and integration points: Depends on atomic helpers, plane state, framebuffers, DRM rectangles, clip rectangles, and drivers with partial update or shadow-buffer upload paths. It integrates with framebuffer `dirty` callbacks and atomic plane commit helpers.

Risks and test signals: Risks include failing to clip damage to the plane source, skipping a required full update, mishandling empty damage lists, coordinate-space confusion between framebuffer and CRTC rectangles, and stale damage across plane changes. Test no-damage updates, multiple clips, clips outside the source, scaling/rotation cases where full updates are needed, dirtyfb IOCTLs, and partial-update hardware upload regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_damage_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_debugfs.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_debugfs.h

Purpose: Declares the DRM debugfs interface for per-minor and per-device diagnostic files, including driver-supplied show callbacks, GPU virtual-address dumps, and per-client debugfs directories.

Important APIs, types, and functions: Defines `DRM_DEBUGFS_GPUVA_INFO()`, `struct drm_info_list`, `struct drm_info_node`, `struct drm_debugfs_info`, and `struct drm_debugfs_entry`. With `CONFIG_DEBUG_FS`, declares `drm_debugfs_create_files()`, `drm_debugfs_remove_files()`, `drm_debugfs_add_file()`, `drm_debugfs_add_files()`, `drm_debugfs_gpuva_info()`, `drm_debugfs_clients_add()`, and `drm_debugfs_clients_remove()`. Without debugfs, all helpers become no-op stubs returning success or zero.

Control flow: Drivers describe debugfs files with static info arrays or add files dynamically on a `drm_device`. The core instantiates these entries under DRM debugfs roots and passes a `seq_file` whose private data identifies the minor or device entry. GPUVA dump entries use the macro and call `drm_debugfs_gpuva_info()` from their show callback. Client add/remove hooks maintain per-file debugfs directories when debugfs is enabled.

State and persistence: State is runtime-only debugfs directory/file metadata linked from minors or devices. No information persists after unregister or unmounting debugfs. Stub builds intentionally drop debugfs behavior while preserving call-site compilation.

Dependencies and integration points: Depends on Linux debugfs, `seq_file`, DRM minors, DRM devices, DRM files, and `drm_gpuvm`. It integrates with `drm_driver.debugfs_init`, CRTC/encoder late debugfs hooks, GPUVA-enabled GEM drivers, and per-client accounting/debug views.

Risks and test signals: Risks include show callbacks dereferencing torn-down device state, registering duplicate names, assuming debugfs exists in non-debugfs builds, leaking entries on unregister, and exposing device-private data on render nodes where policy discourages it. Test with `CONFIG_DEBUG_FS=y/n`, primary and render minors, device unregister while files are open, GPUVA dump output, and client debugfs creation/removal on open/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_debugfs_crc.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_debugfs_crc.h

Purpose: Defines per-CRTC CRC capture state and the debugfs-gated API for adding frame CRC entries used by display validation tests.

Important APIs, types, and functions: Defines `DRM_MAX_CRC_NR`, `DRM_CRC_ENTRIES_NR`, `struct drm_crtc_crc_entry`, `struct drm_crtc_crc`, and `drm_crtc_add_crc_entry()`. CRC entries can carry an optional frame counter and up to ten CRC values; per-CRTC state includes a spinlock, source name, opened/overflow flags, a 128-entry circular buffer, head/tail indexes, value count, and waitqueue.

Control flow: Userspace opens CRC debugfs files and selects a source through CRTC funcs. During scanout, drivers call `drm_crtc_add_crc_entry()` with the current frame and CRC values. The core queues entries in the circular buffer, wakes readers, and reports overflow when producers outrun readers. Without debugfs, the add helper returns `-EINVAL`.

State and persistence: CRC state is transient per CRTC and is reset as debugfs source/open state changes or the CRTC is destroyed. There is no durable persistence; only queued entries in memory are retained until read or overwritten.

Dependencies and integration points: Depends on debugfs, CRTC callbacks `set_crc_source`, `verify_crc_source`, and `get_crc_sources`, waitqueues, and spinlocks. It is used by IGT-style display tests and driver CRC sampling hardware.

Risks and test signals: Risks include value-count mismatches, buffer overflow handling, races between source changes and producer interrupts, stale source pointers, debugfs-disabled builds, and frame counter/timestamp mismatches with vblank. Test CRC open/close, source enable/disable, auto source, reader blocking/wakeup, overflow reporting, invalid value counts, and interrupt-driven CRC generation during modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_debugfs_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_device.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_device.h

Purpose: Defines `struct drm_device`, the central per-GPU/display-device object that ties together driver identity, lifetime management, minors, open files, clients, vblank/event handling, KMS mode configuration, GEM namespaces, VRAM management, fbdev emulation, debugfs roots, DMA device selection, and hot-unplug state.

Important APIs, types, and functions: Defines wedge recovery flags, `struct drm_wedge_task_info`, `enum switch_power_state`, `struct drm_device`, `drm_dev_set_dma_dev()`, and `drm_dev_dma_dev()`. Important fields include `ref`, parent `dev`, optional `dma_dev`, managed-resource list, `driver`, primary/render/accel minors, `registered`, `master`, `driver_features`, `unplugged`, file/client lists, vblank locks/state, `max_vblank_count`, `event_lock`, `mode_config`, GEM object-name IDR, VMA offset manager, VRAM manager, switcheroo power state, fb helper pointer, and debugfs root.

Control flow: Drivers allocate a DRM device, initialize subsystems, and only then register it. Open files are tracked in file lists; KMS objects live under `mode_config`; vblank code uses per-CRTC state plus locks; events are queued under `event_lock`; GEM handles and mmap offsets use the object IDR and VMA manager. Hot-unplug sets `unplugged` and drivers should bracket hardware access with `drm_dev_enter()`/`drm_dev_exit()`. DMA import/export paths use `drm_dev_dma_dev()` so virtual or bus-attached devices can name the actual DMA-capable device.

State and persistence: This is runtime kernel state scoped to the DRM device reference lifetime. It persists across client opens and closes until unregister and final put, but it has no on-disk persistence. Some fields expose stable userspace ABI state such as node existence, object IDs, event behavior, mode objects, and debugfs/sysfs visibility.

Dependencies and integration points: Depends on Linux devices, krefs, mutexes, spinlocks, IDR, optional transparent hugepage mounts, DRM driver structs, minors, masters, vblank, VMA managers, VRAM MM, fb helper, and mode config. It is the anchor for almost every DRM subsystem.

Risks and test signals: Risks include registering before initialization is complete, DMA device mismatch for imported buffers, hot-unplug races, stale file/client list entries, vblank counter wrap mistakes, event lock misuse, master lock ordering bugs, managed-resource lifetime surprises, and per-device feature masking diverging from driver expectations. Test probe/register/unregister ordering, render/primary/accel node creation, hot-unplug under active IOCTLs, vblank enable/disable, event delivery, PRIME import on non-DMA-capable devices, fbdev teardown, debugfs cleanup, and per-device feature disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_drv.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_drv.h

Purpose: Defines the DRM driver-level contract: feature flags, driver callback table, device allocation/registration lifetime APIs, hot-unplug helpers, wedged-device notification, feature checks, firmware-driver policy, and debugfs root initialization hooks.

Important APIs, types, and functions: Defines `enum drm_driver_feature` with modern flags such as `DRIVER_GEM`, `DRIVER_MODESET`, `DRIVER_RENDER`, `DRIVER_ATOMIC`, syncobj support, compute accel, GPUVA, and cursor hotspot, plus legacy AGP/DMA/IRQ flags. `struct drm_driver` contains lifecycle callbacks, open/postclose, master hooks, debugfs init, GEM creation/PRIME import hooks, dumb buffer callbacks, fbdev probe, fdinfo printing, version/name metadata, feature mask, private IOCTL table, and file operations. Allocation/lifetime APIs include `devm_drm_dev_alloc()`, `drm_dev_alloc()`, `__drm_dev_alloc()`, `drm_dev_register()`, `drm_dev_unregister()`, `drm_dev_get()`, `drm_dev_put()`, `drm_put_dev()`, `drm_dev_enter()`, `drm_dev_exit()`, `drm_dev_unplug()`, and `drm_dev_wedged_event()`.

Control flow: Drivers allocate and initialize `struct drm_device`, configure KMS/GEM resources, then call `drm_dev_register()` last so userspace cannot access partially initialized state. Opens call core file setup and optional driver `open`; closes eventually call `postclose`. Feature checks intersect driver-level and per-device feature masks. Hot-unplug uses `drm_dev_unplug()` plus `drm_dev_enter()`/`exit()` gates around hardware access. Wedged-device events advertise recovery expectations to userspace. Debugfs root hooks are compiled out when debugfs is disabled.

State and persistence: Driver structs are usually static; device state is runtime and reference-counted. Public ABI persistence is through the advertised feature flags, device nodes, IOCTL table, file operations, and version metadata. Deprecated `load`, `unload`, and `release` callbacks remain for old drivers but are not preferred lifetime state mechanisms.

Dependencies and integration points: Integrates with Linux file operations, DRM devices, minors, masters, GEM/PRIME, fbdev helpers, dma-buf, sg tables, mode config, syncobj features, dmem cgroup region registration, video firmware-driver-only policy, and debugfs initialization.

Risks and test signals: Risks include setting mutually incompatible feature flags, exposing userspace nodes before initialization completes, using deprecated load/unload paths with races, incorrect fops ownership, dumb-buffer callbacks that violate pitch/size ABI, PRIME import hooks that misuse DMA devices, hot-unplug checks that race hardware removal, and mismatched `DRIVER_ATOMIC` advertising. Test registration failure unwind, open/close callbacks, feature-gated IOCTLs, render/accel node creation, dumb buffer create/map, PRIME import/export, fbdev probe, debugfs init, wedged event reporting, and hot-unplug under concurrent IOCTLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_dumb_buffers.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_dumb_buffers.h

Purpose: Declares the helper for calculating legacy dumb-buffer pitch and size according to hardware pitch and allocation alignment requirements.

Important APIs, types, and functions: Exposes `drm_mode_size_dumb(struct drm_device *dev, struct drm_mode_create_dumb *args, unsigned long hw_pitch_align, unsigned long hw_size_align)`.

Control flow: A driver's `dumb_create` path can call this helper to validate and fill `pitch` and `size` in the userspace `drm_mode_create_dumb` request before allocating backing memory with GEM, TTM, DMA, VRAM, or another allocator.

State and persistence: No state is stored here. The helper contributes to userspace-visible buffer metadata returned by dumb-buffer IOCTLs.

Dependencies and integration points: Integrates with `struct drm_driver.dumb_create`, `struct drm_mode_create_dumb`, and the DRM device. It is typically used by simple display drivers or storage-specific dumb create helpers.

Risks and test signals: Risks include overflow in width/height/bpp multiplication, insufficient alignment for hardware scanout, and ABI-visible pitch/size mismatches. Test minimum and maximum dimensions, unusual depths/bpps, alignment boundaries, overflow rejection, and framebuffer creation from returned dumb buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_dumb_buffers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_edid.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_edid.h

Purpose: Defines EDID and CTA/CEA display-identification data structures, bitfields, constants, quirks, and helper APIs for reading, validating, duplicating, parsing, matching, and applying monitor EDID data to DRM connectors and display modes.

Important APIs, types, and functions: Defines EDID block lengths, DDC I2C addresses, extension tags, timing structures (`struct est_timings`, `struct std_timing`, `struct detailed_timing`, detailed monitor-range/string/color/CVT structures), input/feature/deep-color/VRR/DSC bit masks, `struct drm_edid_product_id`, packed `struct edid`, `struct drm_edid_ident`, `DRM_EDID_IDENT_INIT()`, `struct cea_sad`, and `enum drm_edid_quirk`. APIs include SAD and speaker allocation parsing, HDMI AVI/vendor infoframe construction, quantization range setup, manufacturer and panel ID encode/decode helpers, DDC probing, legacy `struct edid` reads, mode addition, override update, CEA/DMT mode matching, monitor audio/HDMI detection, EDID validity/header checks, monitor-name extraction, and newer opaque `struct drm_edid` allocation/read/update/match/quirk helpers.

Control flow: Connector probe paths read EDID over DDC, switcheroo, custom block readers, or overrides. The EDID is validated, parsed into connector display info, used to add modes, checked for quirks, and queried for audio, HDMI, quantization, panel ID, and infoframe metadata. Legacy callers operate directly on `struct edid`; newer paths use opaque `struct drm_edid` ownership and connector update helpers before adding modes.

State and persistence: EDID bytes are monitor-provided runtime data cached or owned by connector state outside this header. The packed structs define wire/on-device ABI layouts and must remain layout-stable. Connector properties and display modes derived from EDID become userspace-visible until the next hotplug/probe update.

Dependencies and integration points: Depends on I2C/DDC, DRM connectors, display modes, HDMI infoframes, display-info population, audio ELD generation, quirks tables, panel matching, override firmware/debug mechanisms, and userspace mode enumeration.

Risks and test signals: Risks include accepting malformed EDIDs, packed-layout or endian mistakes, checksum/extension handling errors, DDC failures, wrong mode derivation for detailed/standard/CEA timings, incorrect YCbCr/deep-color/VRR/DSC capability parsing, stale override data, and broken panel quirk matching. Test valid and corrupt base blocks, multiple extensions, DDC NACKs, DisplayID at alternate address, monitor audio SADs, HDMI/DP classification, panel ID matching, EDID override, hotplug re-read, CEA VIC matching, and malformed range/timing descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_eld.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_eld.h

Purpose: Defines HDMI/DisplayPort ELD byte offsets, masks, and helpers for extracting or updating monitor audio capability information derived from EDID.

Important APIs, types, and functions: Defines ELD header and baseline block offsets/masks for version, baseline length, CEA EDID version, monitor name length, SAD count, connector type, AI/HDCP support, audio sync delay, speaker allocation, port ID, manufacturer/product IDs, monitor name, and SAD array offsets. Helpers include `drm_eld_mnl()`, `drm_eld_sad_get()`, `drm_eld_sad_set()`, `drm_eld_sad()`, `drm_eld_sad_count()`, `drm_eld_calc_baseline_block_size()`, `drm_eld_size()`, `drm_eld_get_spk_alloc()`, and `drm_eld_get_conn_type()`.

Control flow: Connector/audio code builds or reads an ELD buffer, sets monitor name and SAD data, computes the baseline length, and exposes the buffer to audio drivers. Consumers validate version and monitor-name length before returning the SAD pointer, then use count and size helpers to traverse the audio descriptors.

State and persistence: ELD is an in-memory byte buffer associated with connector/audio state. It persists only while connector state is cached; no on-disk storage exists. The byte layout is ABI-like because audio drivers and userspace diagnostics expect exact offsets.

Dependencies and integration points: Depends on `struct cea_sad` from EDID parsing and integrates with HDMI/DP audio, DRM connector EDID parsing, speaker allocation reporting, and codec/ALSA handoff paths.

Risks and test signals: Risks include out-of-bounds SAD access when monitor-name length or SAD count is corrupt, wrong baseline length units, connector-type bit misinterpretation, and accepting unsupported ELD versions. Test ELD buffers with HDMI and DP types, zero and maximum monitor-name lengths, multiple SADs, malformed version fields, speaker allocation masks, audio delay limits, and round-trip SAD get/set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_eld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_encoder.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_encoder.h

Purpose: Defines DRM encoder objects and callbacks, representing the routing stage between CRTCs and connectors/bridges in a KMS display pipeline.

Important APIs, types, and functions: Defines `struct drm_encoder_funcs` and `struct drm_encoder`. Encoder state includes parent device, list node, mode object base, name, user-visible encoder type, stable index, `possible_crtcs`, `possible_clones`, legacy current CRTC pointer, bridge chain, function/helper tables, and debugfs entry. Exported helpers include `drm_encoder_init()`, `drmm_encoder_init()`, `drmm_encoder_alloc()`, `drmm_plain_encoder_alloc()`, `drm_encoder_index()`, `drm_encoder_mask()`, `drm_encoder_crtc_ok()`, `drm_encoder_find()`, `drm_encoder_cleanup()`, and encoder iteration macros.

Control flow: Drivers initialize encoders during mode-config setup, set possible CRTC and clone masks before registration, attach bridges/connectors, and optionally supply reset/destroy/late-register/early-unregister/debugfs callbacks. KMS routing checks masks to decide whether a CRTC can drive an encoder and whether clone configurations are legal. Managed allocation variants register cleanup with DRM managed resources.

State and persistence: Encoder objects are runtime KMS mode objects with stable indices and userspace IDs for the device lifetime. They are not hotplugged in DRM core assumptions, though connectors and bridges may be dynamic around them. No disk persistence exists.

Dependencies and integration points: Depends on CRTC masks, mode objects, connector routing, bridges, debugfs, and helper private callbacks. Integrates with atomic connector state, legacy encoder `crtc` state, bridge chains, and object lookup under lease checks.

Risks and test signals: Risks include incorrect `possible_crtcs` or `possible_clones` masks, forgetting self-clone bits where required, stale legacy `crtc` use in atomic drivers, cleanup lifetime mismatches with managed allocation, and debugfs hooks surviving unregister. Test encoder registration warnings, multi-CRTC routing, clone modes, leased-object lookup, bridge attach order, debugfs init/removal, and driver unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_exec.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_exec.h

Purpose: Declares the DRM execution locking helper used to acquire multiple GEM object reservation locks with wound/wait deadlock avoidance and retry-on-contention control flow.

Important APIs, types, and functions: Defines flags `DRM_EXEC_INTERRUPTIBLE_WAIT` and `DRM_EXEC_IGNORE_DUPLICATES`, `struct drm_exec`, object iteration macros, `drm_exec_until_all_locked()`, `drm_exec_retry_on_contention()`, `drm_exec_is_contended()`, and APIs `drm_exec_init()`, `drm_exec_fini()`, `drm_exec_cleanup()`, `drm_exec_lock_obj()`, `drm_exec_unlock_obj()`, `drm_exec_prepare_obj()`, and `drm_exec_prepare_array()`. State includes a `ww_acquire_ctx`, locked-object array, contended/prelocked objects, and capacity counts.

Control flow: Callers initialize an exec context and enter `drm_exec_until_all_locked()`, which cleans up at loop entry and sets a local retry label. Inside the loop, callers prepare or lock each GEM object; if contention is recorded, `drm_exec_retry_on_contention()` jumps back, releases locks, and retries with ww-mutex ordering. Once all locks are acquired, the caller submits or validates work, then finalizes and unlocks via cleanup/fini.

State and persistence: State is transient per submission or validation path. It stores references to currently locked GEM objects and ww acquisition state only for the duration of the operation.

Dependencies and integration points: Depends on GEM objects and Linux ww-mutexes. Integrates with command submission, eviction, validation, GPUVM updates, and any path that needs multiple reservation locks while handling duplicate objects and interruptible waits.

Risks and test signals: Risks include using the retry macro outside its loop body, unsigned reverse-iteration surprises, leaked locks on error paths, duplicate object handling mistakes, sleeping behavior when interruptible waits are requested, and failure to reserve fence slots before submission. Test locking arrays with duplicates, contention against another thread, signal interruption, reverse unlock order, fence reservation counts, and error unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fb_dma_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fb_dma_helper.h

Purpose: Declares helpers for using DMA-backed GEM objects as framebuffer scanout buffers, including address lookup, non-coherent synchronization, and scanout-buffer export.

Important APIs, types, and functions: Declares `drm_fb_dma_get_gem_obj()`, `drm_fb_dma_get_gem_addr()`, `drm_fb_dma_sync_non_coherent()`, and `drm_fb_dma_get_scanout_buffer()`. The helpers operate on DRM framebuffers, plane state, planes, DRM devices, DMA GEM objects, and scanout-buffer descriptors.

Control flow: Plane update paths retrieve the DMA GEM object for a framebuffer plane, compute the DMA address adjusted for framebuffer offsets and plane source state, optionally synchronize non-coherent mappings between old and new plane states, and provide scanout-buffer metadata to display helpers or bridges.

State and persistence: No independent state is stored. Helpers derive runtime DMA addresses and synchronization operations from framebuffer GEM objects and plane state.

Dependencies and integration points: Integrates with `drm_gem_dma_helper`, framebuffer objects, plane state, non-coherent DMA memory, and scanout helpers used by simple display drivers.

Risks and test signals: Risks include wrong plane index handling, offset/source coordinate miscalculation, cache coherency bugs on non-coherent platforms, and exporting scanout buffers unsupported by hardware. Test multi-plane framebuffers, nonzero offsets, panning/source rectangles, imported DMA buffers, non-coherent CPU writes, and scanout-buffer handoff to display pipelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fb_dma_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fb_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fb_helper.h

Purpose: Defines the DRM fbdev emulation helper interface that maps KMS devices onto Linux fbdev/fbcon, including surface sizing, helper state, callback hooks, default fb_ops, mode restoration, damage flushing, hotplug handling, and suspend support.

Important APIs, types, and functions: Defines `struct drm_fb_helper_surface_size`, `struct drm_fb_helper_funcs`, `struct drm_fb_helper`, `drm_fb_helper_from_client()`, and `DRM_FB_HELPER_DEFAULT_OPS`. With `CONFIG_DRM_FBDEV_EMULATION`, declares prepare/init/fini/unprepare, fb_ops implementations, mode restore, unregister/fill info, damage range/area, deferred IO, suspend, cmap/ioctl, hotplug, initial config, and `drm_fb_helper_gem_is_fb()`. Without fbdev emulation, only a false `drm_fb_helper_gem_is_fb()` stub remains.

Control flow: Drivers prepare and initialize a helper, then probe fbdev through `drm_driver.fbdev_probe`. The helper chooses an initial KMS configuration, allocates or references a scanout framebuffer, fills `fb_info`, and services fbdev operations. Writes through fbdev accumulate damage and schedule work to flush. Hotplug may defer setup when no outputs exist or when another KMS master owns the device; mode restore reacquires fbdev control when appropriate. Suspend paths call driver-specific or generic fb suspend handling.

State and persistence: State is runtime: embedded DRM client, client buffer, framebuffer, `fb_info`, pseudo palette, damage clip/work, resume work, helper mutex, delayed hotplug/deferred setup flags, preferred bpp, and optional deferred IO state. It persists while fbdev emulation is registered and is torn down during driver unload or fbdev disable.

Dependencies and integration points: Depends on Linux fbdev, DRM client helpers, DRM framebuffers, fbcon, KMS mode setting, workqueues, deferred IO, GEM framebuffer detection, and driver `fbdev_probe`. It integrates with generic fbdev DMA/shmem/TTM wrappers and KMS hotplug/suspend paths.

Risks and test signals: Risks include console lock deadlocks on resume, damage coalescing races, stale fbdev modes after hotplug, deferred setup never retrying, mismatch between fbdev dimensions and scanout surface, incorrect pseudo-palette/cmap handling, and fbdev enabled when another master controls KMS. Test boot fbcon, no-monitor deferred setup, hotplug after boot, multi-display min/max sizing, fbdev writes and deferred IO, suspend/resume, KMS master handoff, cmap/ioctl paths, and teardown with fbcon active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fb_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_dma.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_dma.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers whose framebuffer memory is backed by DMA GEM helpers.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_dma_driver_fbdev_probe()` and defines `DRM_FBDEV_DMA_DRIVER_OPS` to set `.fbdev_probe` to that helper. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: DMA GEM drivers include the macro in `struct drm_driver` initialization. When fbdev emulation starts, the DRM core calls the probe helper to allocate and initialize fbdev state using DMA-backed scanout storage.

State and persistence: The header stores no state. Runtime fbdev state is held in `struct drm_fb_helper` and the allocated DMA GEM framebuffer.

Dependencies and integration points: Integrates with `drm_fb_helper`, `drm_gem_dma_helper`, `struct drm_driver.fbdev_probe`, and Kconfig-controlled fbdev emulation.

Risks and test signals: Risks include silently disabling fbdev when Kconfig is off, using the macro in a driver that does not use DMA-compatible GEM objects, and mismatched surface sizing. Test builds with fbdev emulation on and off, boot console creation, DMA dumb-buffer allocation, and fbdev teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_shmem.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_shmem.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers using shmem GEM backing storage.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_shmem_driver_fbdev_probe()` and defines `DRM_FBDEV_SHMEM_DRIVER_OPS` to install it as `.fbdev_probe`. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: Shmem GEM drivers compose this macro into `struct drm_driver`. The fbdev helper calls the probe callback to create the fbdev surface and DRM framebuffer backed by shmem GEM objects.

State and persistence: No state is stored in the header. Runtime state lives in fb helper structures and shmem GEM objects.

Dependencies and integration points: Integrates with DRM fb helper, shmem GEM helpers, driver fbdev callbacks, and Kconfig.

Risks and test signals: Risks include fbdev being unavailable in no-emulation builds, using shmem fbdev paths without CPU mapping support, and damage flushing assumptions for shadow-backed buffers. Test fbdev emulation enabled/disabled builds, fbcon output, mmap/write behavior, hotplug reconfiguration, and shmem object cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_shmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_ttm.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_ttm.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers using TTM-managed backing storage.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_ttm_driver_fbdev_probe()` and defines `DRM_FBDEV_TTM_DRIVER_OPS` to set `.fbdev_probe` accordingly. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: TTM-based drivers add this macro to the DRM driver ops. The fbdev helper invokes the probe callback to allocate a fbdev framebuffer through TTM-capable GEM/BO paths.

State and persistence: No header-owned state exists. Runtime state is in fb helper structures and TTM/GEM buffer objects.

Dependencies and integration points: Depends on fb helper surface sizing and TTM-backed framebuffer allocation. It integrates with `struct drm_driver.fbdev_probe`, Kconfig, and TTM GEM helpers.

Risks and test signals: Risks include missing fbdev support in Kconfig-off builds, BO placement/mapping failures during console setup, and eviction/pinning conflicts while fbdev is scanning out. Test fbcon boot, suspend/resume, memory pressure eviction behavior, hotplug resize, and fbdev teardown in TTM drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fbdev_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_file.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_file.h

Purpose: Defines DRM minor node identity, per-open file/client state, pending event delivery structures, file operation entry points, memory accounting structs, and fdinfo reporting helpers.

Important APIs, types, and functions: Defines global `drm_minors_xa`, `enum drm_minor_type`, `struct drm_minor`, `struct drm_pending_event`, `struct drm_file`, `struct drm_memory_stats`, node-type predicates `drm_is_primary_client()`, `drm_is_render_client()`, `drm_is_accel_client()`, and APIs for file errors, PID updates, minor acquire/release, open/read/release/poll, event reserve/cancel/send, memory-stat printing, fdinfo display, and mock file creation. `struct drm_file` tracks client capability flags, master/auth state, PID/client ID, GEM handle IDR, syncobj xarray, driver private data, framebuffer list, blob list, event queues/space, PRIME caches, client name, and debugfs client directory.

Control flow: Opening a DRM node creates a `drm_file`, assigns its minor, sets client capabilities through IOCTLs, optionally authenticates primary clients, and adds it to device file lists. GEM handles, framebuffers, blobs, syncobjs, and PRIME caches are scoped to the file. Event producers reserve event space, add pending events, and later send or cancel them; `drm_read()` drains ready events, while `drm_poll()` waits for them. Release unwinds pending events, handles, per-file framebuffers, driver private data, debugfs client entries, and master/auth references.

State and persistence: State is per open file descriptor and lasts until release. Event queues are transient but userspace-visible through `read()`/`poll()`. GEM handles and framebuffer references are per-file namespaces; global object references can outlive a file only through other refs such as dma-buf or other handles.

Dependencies and integration points: Depends on Linux files, devices, completions, waitqueues, IDR, xarray, PRIME, dma fences, DRM events/uapi, masters, GEM, syncobjs, debugfs clients, and fdinfo memory accounting. Integrates with all DRM file operations and driver `open`/`postclose` callbacks.

Risks and test signals: Risks include event-space leaks, pending event use-after-close, master pointer lifetime races, RCU PID misuse, per-file GEM handle races, framebuffer list locking errors, syncobj namespace leaks, incorrect primary/render/accel permission checks, and fdinfo stats double-counting shared objects. Test open/close storms, auth/master handoff, render-node access without auth, event reserve/send/cancel under close, read/poll behavior, GEM handle create/delete, PRIME import cache cleanup, fdinfo with shared/private buffers, and debugfs client removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fixed.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fixed.h

Purpose: Provides fixed-point arithmetic helpers used by DRM display code for ratios, timing math, color calculations, and formatted small fixed-point values without floating point.

Important APIs, types, and functions: Defines `fixed20_12` and `dfixed_*` macros/helpers for 20.12 arithmetic; defines 32.32 constants such as `DRM_FIXED_POINT`, `DRM_FIXED_ONE`, masks, epsilon, and almost-one; implements `drm_sm2fixp()`, integer/fixed conversions, rounding/ceil helpers, `drm_fixp_msbset()`, `drm_fixp_mul()`, `drm_fixp_div()`, `drm_fixp_from_fraction()`, and `drm_fixp_exp()`. Also defines Q4 helpers `fxp_q4_from_int()`, `fxp_q4_to_int()`, `fxp_q4_to_int_roundup()`, `fxp_q4_to_frac()`, `FXP_Q4_FMT`, and `FXP_Q4_ARGS()`.

Control flow: Callers convert integer or fractional values into fixed point, perform multiplication/division with overflow-reducing shifts, and convert results back to integers or formatted Q4 output. The exponential helper iteratively sums terms until a fixed tolerance and handles negative exponents by reciprocal division.

State and persistence: Stateless inline arithmetic only. Results may become ABI-visible if used to derive mode timings or property values, but the header itself stores nothing.

Dependencies and integration points: Depends on kernel 64-bit division/math helpers and wordpart extraction. Integrated by DRM drivers and helpers that cannot use floating point in kernel code.

Risks and test signals: Risks include overflow, precision loss from shifting, division by zero, negative rounding surprises, `INT_MIN` absolute-value overflow in fraction conversion, and convergence/runtime issues in `drm_fixp_exp()`. Test positive and negative values, large operands near overflow, small fractions, rounding/ceil boundaries, zero denominators rejected by callers, and Q4 formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_flip_work.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_flip_work.h

Purpose: Declares a thread-safe utility for deferring work until after a page flip or vblank, commonly to release framebuffers or cursor buffer objects after scanout no longer uses them.

Important APIs, types, and functions: Defines callback type `drm_flip_func_t`, `struct drm_flip_work`, and functions `drm_flip_work_queue()`, `drm_flip_work_commit()`, `drm_flip_work_init()`, and `drm_flip_work_cleanup()`. State includes a debug name, callback, work item, queued list, committed list, and spinlock.

Control flow: Producers queue values into `queued`. When the flip/vblank boundary is reached, `drm_flip_work_commit()` moves queued items to committed under the spinlock and schedules worker execution on the supplied workqueue; the worker calls the callback for each committed item in process context. Commit is safe from atomic context.

State and persistence: State is runtime queue contents and pending work. It persists only for the lifetime of the initialized `drm_flip_work` instance and has no disk persistence.

Dependencies and integration points: Depends on workqueues, spinlocks, lists, and driver page-flip/vblank completion paths. It integrates with legacy display drivers that need delayed unref/free operations outside interrupt context.

Risks and test signals: Risks include cleanup while work is pending, queueing values with insufficient lifetime, calling callbacks in unexpected order, committing to a destroyed workqueue, and leaking queued items on error paths. Test queue/commit from interrupt and process context, cleanup after pending work, multiple commits, empty commits, and framebuffer unref after vblank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_flip_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_format_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_format_helper.h

Purpose: Declares framebuffer memory-copy, byte-swap, and pixel-format conversion helpers plus reusable temporary conversion state for drivers that need CPU-side scanout conversion.

Important APIs, types, and functions: Defines `struct drm_format_conv_state`, initializers `DRM_FORMAT_CONV_STATE_INIT` and `DRM_FORMAT_CONV_STATE_INIT_PREALLOCATED()`, state management functions, `drm_fb_clip_offset()`, `drm_fb_memcpy()`, `drm_fb_swab()`, and many XRGB8888/ARGB8888 conversion routines to RGB332, RGB565, RGB565BE, XRGB1555, ARGB1555, RGBA5551, RGB888, BGR888, ARGB8888, ABGR8888, XBGR8888, BGRX8888, XRGB2101010, ARGB2101010, GRAY8, MONO, GRAY2, and ARGB4444.

Control flow: Drivers initialize or reuse a conversion state, reserve temporary storage as needed, compute source offsets from clips and format info, then copy or convert the clipped framebuffer region from `iosys_map` source maps to destination maps using destination pitches. Preallocated state lets callers avoid allocation in sensitive paths.

State and persistence: Conversion state only caches temporary memory and whether it is caller-owned. Converted pixels are written to destination backing storage; no other persistent state exists.

Dependencies and integration points: Depends on DRM framebuffers, format info, rectangles, `iosys_map`, and GFP allocation flags. Integrates with fbdev emulation, shadow-plane helpers, simple display pipes, and drivers whose hardware accepts fewer formats than userspace can provide.

Risks and test signals: Risks include incorrect clip offset for multi-plane/block formats, temporary buffer lifetime mistakes, endian/byte-swap errors, alpha handling differences, pitch overruns, allocation failures in commit paths, and cached versus non-cached memory handling. Test every conversion format, odd widths/heights, unaligned clips, large pitch padding, preallocated state reuse, allocation failure, and visual CRC comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_format_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fourcc.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_fourcc.h

Purpose: Defines DRM pixel-format metadata and helper APIs for interpreting FourCC formats, host-endian aliases, plane counts, bytes-per-block, block geometry, chroma subsampling, alpha/YUV/indexed flags, bpp, pitch, and legacy format mapping.

Important APIs, types, and functions: Defines `DRM_FORMAT_MAX_PLANES`, host-endian aliases for common formats, `struct drm_format_info`, inline predicates for YUV packed/semiplanar/planar layouts and 4:1:0, 4:1:1, 4:2:0, 4:2:2, and 4:4:4 sampling, plane width/height helpers, and APIs `__drm_format_info()`, `drm_format_info()`, `drm_get_format_info()`, `drm_mode_legacy_fb_format()`, `drm_driver_legacy_fb_format()`, `drm_driver_color_mode_format()`, `drm_format_info_block_width()`, `drm_format_info_block_height()`, `drm_format_info_bpp()`, and `drm_format_info_min_pitch()`.

Control flow: Framebuffer creation and plane validation look up a format through static tables or the driver's `get_format_info` hook, then use plane/block/subsampling helpers to validate dimensions, pitches, offsets, and minimum memory requirements. Legacy bpp/depth and driver color modes are translated to FourCC values for old IOCTLs and fbdev paths.

State and persistence: Format info is static metadata and has no mutable state. It defines userspace ABI interpretation of FourCC/modifier combinations and must remain stable.

Dependencies and integration points: Depends on UAPI `drm_fourcc.h`, DRM devices, and kernel math helpers. Integrated by framebuffer creation, planes, format conversion helpers, dumb-buffer sizing, modifiers, fbdev, and display drivers.

Risks and test signals: Risks include wrong block dimensions for packed or tiled formats, pitch underestimation, YUV subsampling dimension rounding errors, endian alias mistakes, legacy bpp/depth mismatches, and driver hook divergence from core format tables. Test RGB/YUV/indexed formats, multi-plane pitches, odd chroma dimensions, modifier-specific format info, legacy fb format mapping, and minimum-pitch calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_fourcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_framebuffer.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_framebuffer.h

Purpose: Defines DRM framebuffer objects, framebuffer callbacks, refcount helpers, list iteration, and AFBC framebuffer specialization used by KMS planes and userspace framebuffer IOCTLs.

Important APIs, types, and functions: Defines `struct drm_framebuffer_funcs`, `DRM_FRAMEBUFFER_HAS_HANDLE_REF()`, `struct drm_framebuffer`, `obj_to_fb()`, init/lookup/remove/cleanup/unregister APIs, `drm_framebuffer_get()`, `drm_framebuffer_put()`, `drm_framebuffer_read_refcount()`, `drm_framebuffer_assign()`, `drm_for_each_fb()`, `struct drm_afbc_framebuffer`, and `fb_to_afbc_fb()`. Framebuffer fields include device, mode object base/refcount, allocating process name, format, callbacks, per-plane pitches/offsets, modifier, dimensions, flags, internal flags, per-file list entry, and optional GEM backing objects.

Control flow: A driver's `fb_create` path validates a mode command, initializes a framebuffer, attaches backing storage, and registers it on the mode-config framebuffer list. Userspace and planes look up framebuffers by object ID; asynchronous scanout paths take references until hardware is done; removal unregisters userspace visibility before final put; destroy callbacks release backing objects and call core cleanup. Dirty callbacks allow userspace to signal changed regions.

State and persistence: Framebuffers are runtime KMS objects. They persist while referenced by userspace files, planes, commits, or drivers, and are released through refcounting. No disk persistence exists, but object IDs, format/modifier/pitch/offset metadata, and dirty semantics are userspace ABI state.

Dependencies and integration points: Depends on DRM FourCC format info, mode objects, files, GEM objects, clip rects, mode config framebuffer locks, plane state, and framebuffer creation callbacks. AFBC specialization integrates with ARM AFBC modifiers and GEM framebuffer helpers.

Risks and test signals: Risks include backing-object lifetime leaks, refcount imbalance during async flips, pitch/offset/modifier validation gaps, exposing handles through GETFB incorrectly, dirty callback coordinate errors, list iteration without `fb_lock`, and AFBC alignment/size mistakes. Test addfb/addfb2, framebuffer lookup after file close, page flip lifetime, remove while scanning out, dirtyfb IOCTL, multi-plane and modifier formats, AFBC metadata, and driver unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_framebuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem.h

Purpose: Defines the DRM GEM base object model for graphics buffer objects: object callbacks, refcounting, handle namespaces, mmap offsets, dma-buf/PRIME integration, reservation locks, GPUVA tracking, LRU shrinker support, default GEM file operations, and helper APIs.

Important APIs, types, and functions: Defines `enum drm_gem_object_status`, `struct drm_gem_object_funcs`, `struct drm_gem_lru`, `struct drm_gem_object`, `DRM_GEM_FOPS`, `DEFINE_DRM_GEM_FOPS()`, huge tmpfs helpers, object init/release/free functions, mmap helpers, get/put helpers, handle create/delete, mmap offset allocation/free, page get/put, GEM lock/unlock, vmap/vunmap, object lookup helpers, DMA reservation wait, multi-object reservation lock/unlock, dumb map offset, LRU helpers, eviction helper, shared/imported predicates, GPUVA lock assertion/init, and GPUVM BO iteration macros.

Control flow: Drivers initialize GEM objects with either shmem-backed or private storage, install object funcs, expose per-file handles, optionally allocate mmap offsets, and use reservation locks for CPU/GPU synchronization. When handles are closed and references drop, the object free callback releases backing storage and dma-buf attachment/export state. PRIME paths export/import dma-bufs through object funcs and driver hooks. LRU helpers allow shrinkers to scan reclaimable objects. GPUVA-aware drivers maintain per-object mapping lists under the proper lock mode.

State and persistence: GEM objects are runtime memory objects with refcounts, handle counts, global flink names, optional shmem file backing, mmap node, dma-buf export/import references, reservation object, GPUVA list, object funcs, and LRU placement. State persists while any handle, dma-buf, framebuffer, GPU mapping, or driver reference exists.

Dependencies and integration points: Depends on krefs, dma-buf, dma-resv, VMA manager, Linux mm, file operations, DRM file handle IDRs, PRIME helpers, sync/fence infrastructure, fdinfo memory stats, transparent hugepage tmpfs support, and GPUVM. It is the base for DMA, shmem, TTM, VRAM, and driver-private BO implementations.

Risks and test signals: Risks include refcount/handle-count imbalance, global-name lifetime bugs, mmap offset exposure after free, reservation deadlocks, dma-buf reference loops, incorrect imported-object cleanup, shrinker eviction while pinned/active, GPUVA list locking mismatches, and fdinfo stats races. Test handle create/delete across files, flink/open legacy paths, mmap and munmap, PRIME export/import, vmap/vunmap, reservation contention, shrinker/LRU eviction, hot-unplug cleanup, fdinfo memory stats, and GPUVA map/unmap under both immediate and reservation-lock modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_atomic_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_atomic_helper.h

Purpose: Declares GEM-aware atomic plane helpers, especially for preparing framebuffers and managing shadow-buffered plane state with CPU mappings and format-conversion state.

Important APIs, types, and functions: Declares `drm_gem_plane_helper_prepare_fb()`, shadow plane maximum size constants, `struct drm_shadow_plane_state`, `to_drm_shadow_plane_state()`, low-level and public reset/duplicate/destroy helpers, `DRM_GEM_SHADOW_PLANE_FUNCS`, begin/end framebuffer access helpers, `DRM_GEM_SHADOW_PLANE_HELPER_FUNCS`, simple-display-pipe shadow helpers, and `DRM_GEM_SIMPLE_DISPLAY_PIPE_SHADOW_PLANE_FUNCS`.

Control flow: Atomic plane `prepare_fb` pins or prepares GEM-backed framebuffers. Shadow-buffered planes use a subclassed plane state that stores mappings for framebuffer BOs and data pointers adjusted for offsets. Reset, duplicate, and destroy hooks initialize/copy/release conversion state. Begin/end access hooks establish and release CPU access/mappings around shadow updates, and simple display pipe macros wire the same flow into simple KMS drivers.

State and persistence: Shadow plane state is per-plane atomic state and persists across commits until replaced. Its mappings are transitional and should be established in prepare/begin paths and removed in cleanup/end paths. Format-conversion temporary storage is copied or destroyed with plane state.

Dependencies and integration points: Depends on GEM objects, plane state, `iosys_map`, DRM format conversion, FourCC info, and simple display pipes. Integrates with atomic plane funcs/helper funcs and drivers that upload from shadow buffers to hardware memory.

Risks and test signals: Risks include leaking CPU mappings, duplicating transitional map state incorrectly, stale data pointers after framebuffer offsets change, prepare/cleanup imbalance, shadow buffer size limits inconsistent with mode config, and missing CPU access synchronization for imported dma-bufs. Test atomic plane enable/disable, framebuffer replacement, duplicate/destroy under check-only commits, mmap/vmap failures, imported buffers, format conversion reuse, and simple-pipe helper macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_atomic_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_dma_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_dma_helper.h

Purpose: Defines the DMA-backed GEM object subtype and helper APIs/macros for simple drivers that allocate contiguous or DMA-address-contiguous scanout buffers.

Important APIs, types, and functions: Defines `struct drm_gem_dma_object`, `to_drm_gem_dma_obj()`, create/free/print/sg-table/vmap/mmap helpers, `drm_gem_dma_vm_ops`, object-func wrapper inlines for free/print/get_sg_table/vmap/mmap, dumb-create helpers, PRIME import helpers, driver-op macros `DRM_GEM_DMA_DRIVER_OPS*`, no-MMU `drm_gem_dma_get_unmapped_area()`, and `DEFINE_DRM_GEM_DMA_FOPS()`.

Control flow: Drivers create DMA GEM objects for dumb buffers or internal framebuffers. The object stores CPU virtual address, DMA address, optional imported sg table, and non-coherent flag. Object funcs wrap the DMA helpers for free, mmap, vmap, and PRIME export. Driver op macros install default dumb-create and PRIME import behavior, with variants that ensure imported buffers are virtually mapped. File-op macros install DRM open/release/ioctl/poll/read/mmap behavior plus no-MMU get-unmapped-area support.

State and persistence: State is per GEM DMA object: base GEM object, DMA address, sg table, CPU virtual address, and coherency flag. It persists until the GEM refcount reaches zero and the DMA allocation/import attachment is freed.

Dependencies and integration points: Depends on DRM file/ioctl/GEM infrastructure, DMA allocation/mapping, PRIME dma-buf imports, sg tables, VM operations, dumb-buffer IOCTLs, and no-MMU mapping support. It integrates with framebuffer DMA helpers and fbdev DMA helpers.

Risks and test signals: Risks include assuming physical contiguity for multi-entry sg imports, cache maintenance omissions for non-coherent buffers, mmap attributes mismatching allocation attributes, imported-buffer vmap availability, no-MMU mapping errors, and dumb-buffer size overflow. Test native allocation, imported sg tables, vmap-required imports, mmap from userspace, PRIME export/import, non-coherent CPU writes, no-MMU builds, and dumb framebuffer creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_dma_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_framebuffer_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_framebuffer_helper.h

Purpose: Declares helper functions for creating and managing DRM framebuffers backed by GEM objects, including handle creation, destruction, CPU access, vmap/vunmap, dirty-enabled creation, and AFBC metadata initialization.

Important APIs, types, and functions: Defines `AFBC_VENDOR_AND_TYPE_MASK`, `drm_gem_fb_get_obj()`, `drm_gem_fb_destroy()`, `drm_gem_fb_create_handle()`, `drm_gem_fb_init_with_funcs()`, `drm_gem_fb_create_with_funcs()`, `drm_gem_fb_create()`, `drm_gem_fb_create_with_dirty()`, `drm_gem_fb_vmap()`, `drm_gem_fb_vunmap()`, `drm_gem_fb_begin_cpu_access()`, `drm_gem_fb_end_cpu_access()`, `drm_is_afbc()`, and `drm_gem_fb_afbc_init()`.

Control flow: Framebuffer creation looks up GEM handles from a mode command, validates format and plane metadata, stores object references in the framebuffer, and installs framebuffer funcs. Handle creation exports a GEM handle for GETFB-like paths. Vmap and CPU access helpers iterate backing objects for all planes. AFBC initialization validates modifier-derived block geometry, alignment, offsets, and minimum buffer size for AFBC framebuffers.

State and persistence: The helper manages framebuffer references to GEM backing objects and temporary CPU mappings. State persists as long as the framebuffer object exists; mappings persist only between vmap/vunmap calls.

Dependencies and integration points: Depends on GEM, DRM framebuffer core, FourCC/modifier metadata, dma-buf CPU access directions, `iosys_map`, mode commands, and AFBC modifiers. Integrated by most GEM-based KMS drivers' `fb_create` callbacks.

Risks and test signals: Risks include plane handle/object mismatch, missing references on shared objects, invalid offsets/pitches accepted, vmap partial failure unwinds, CPU access not propagated to all planes, dirty callback mismatch, and AFBC size/alignment underestimation. Test addfb2 with one and multi-plane formats, duplicate handles, invalid pitches/offsets, vmap failure injection, CPU begin/end on imported buffers, dirtyfb helper creation, and AFBC modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_framebuffer_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_shmem_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_shmem_helper.h

Purpose: Defines the shmem-backed GEM object subtype and helper APIs/macros for drivers whose buffer objects are pageable shmem files with optional pinning, vmap, madvise/purge, PRIME import, and dumb-buffer creation.

Important APIs, types, and functions: Defines `struct drm_gem_shmem_object`, `to_drm_gem_shmem_obj()`, init/create/release/free helpers, page put/pin/unpin/vmap/vunmap/mmap helpers, locked pin/unpin and madvise helpers, `drm_gem_shmem_is_purgeable()`, purge, sg-table helpers, print-info helper, `drm_gem_shmem_vm_ops`, object-func wrapper inlines, PRIME import helpers, `drm_gem_shmem_dumb_create()`, `DRM_GEM_SHMEM_DRIVER_OPS`, and KUnit-only direct wrappers.

Control flow: Drivers create shmem GEM objects, pin pages for scanout or dma-buf access, optionally vmap them for CPU access, and unpin/unmap when no longer needed. Madvise marks objects as purgeable or active; purge can drop unpinned, non-imported, non-exported backing pages with positive madv and an sg table. Object funcs wrap the helpers under GEM reservation locking. Driver op macros install shmem PRIME and dumb-create defaults.

State and persistence: Per-object state includes the base GEM object, page array, page use and pin counts, madv state/list, imported sg table, virtual address and vmap count, dirty/accessed-on-put flags, and write-combine mapping policy. The shmem file backing persists while the GEM object exists, but pages can be evicted or purged if unpinned and marked purgeable.

Dependencies and integration points: Depends on Linux shmem/mm, GEM, PRIME, dma-buf attachments, sg tables, VM operations, DRM file/ioctl, shrinker/madvise patterns, and KUnit test hooks. Used by many virtual/simple GPU and display drivers.

Risks and test signals: Risks include page pin/use count imbalance, purging exported or imported buffers, stale sg tables after purge, vmap count leaks, dirty/accessed flags not applied on put, mmap attribute mismatch, and madvise races under reservation locks. Test create/free, pin/unpin nesting, vmap/vunmap nesting, mmap faults, PRIME import/export, madvise active/purge transitions, shrinker purge under memory pressure, KUnit helper paths, and write-combined mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_shmem_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_ttm_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_ttm_helper.h

Purpose: Declares adapter helpers that let TTM buffer objects participate in GEM object callbacks for printing, vmap/vunmap, mmap, and dumb-buffer map-offset handling.

Important APIs, types, and functions: Defines `drm_gem_ttm_of_gem()` and declares `drm_gem_ttm_print_info()`, `drm_gem_ttm_vmap()`, `drm_gem_ttm_vunmap()`, `drm_gem_ttm_mmap()`, and `drm_gem_ttm_dumb_map_offset()`.

Control flow: TTM-backed drivers use the container macro to recover `struct ttm_buffer_object` from the embedded GEM base, install helper callbacks in GEM object funcs or driver dumb-map ops, and route userspace mmap/map-offset requests through TTM's BO mapping logic.

State and persistence: No independent state is stored. Helpers operate on TTM BO state embedded around the GEM base and on transient virtual mappings.

Dependencies and integration points: Depends on DRM device/GEM and TTM BO headers. Integrated by VRAM helpers and TTM-based drivers that expose GEM APIs.

Risks and test signals: Risks include wrong container assumptions for non-TTM GEM objects, BO reservation/pinning mistakes during vmap/mmap, and offset exposure for evictable BOs. Test TTM GEM mmap, vmap/vunmap, dumb map offset, eviction around mappings, and debug info printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_ttm_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_vram_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_gem_vram_helper.h

Purpose: Defines GEM/TTM helper types and APIs for devices with dedicated VRAM, including VRAM-backed GEM objects, default driver and plane helper macros, VRAM memory-manager integration, and mode validation against VRAM capacity.

Important APIs, types, and functions: Defines placement flags, `struct drm_gem_vram_object`, container helpers `drm_gem_vram_of_bo()` and `drm_gem_vram_of_gem()`, object creation/put/offset/vmap/vunmap helpers, dumb create sizing/fill helpers, `drm_gem_vram_driver_dumb_create()`, plane prepare/cleanup helpers, `DRM_GEM_VRAM_PLANE_HELPER_FUNCS`, `DRM_GEM_VRAM_DRIVER`, `struct drm_vram_mm`, `drm_vram_mm_of_bdev()`, `drm_vram_mm_debugfs_init()`, `drmm_vram_helper_init()`, and `drm_vram_helper_mode_valid()`.

Control flow: Drivers initialize a managed VRAM MM with base and size, create VRAM GEM objects backed by TTM BOs, use dumb-create helpers for scanout buffers, and wire plane helper funcs so framebuffer BOs are pinned/prepared for scanout and unpinned on cleanup. Objects can be placed in VRAM or system memory and evicted when VRAM is scarce; vmap helpers manage reference-counted CPU mappings. Mode validation rejects display modes whose framebuffer requirements exceed available VRAM.

State and persistence: Runtime state includes each VRAM object's TTM BO, cached map, vmap use count, placement policy, and the device's `drm_vram_mm` with VRAM base/size and TTM device. It persists for the DRM device and object lifetimes but has no disk persistence.

Dependencies and integration points: Depends on DRM GEM/file/ioctl/modes, TTM BO and placement APIs, TTM-backed GEM helpers, plane helper callbacks, VRAM debugfs, and mode validation. Integrated by simple PCI/display drivers with fixed aperture VRAM.

Risks and test signals: Risks include incorrect VRAM base/size setup, placement flags that allow scanout from evicted system memory, vmap count imbalance, BO pin/unpin leaks in plane helpers, dumb pitch/size overflow, mode validation not accounting for bpp/pitch, and debugfs lifetime issues. Test VRAM MM init failure, dumb create/map, page flips under VRAM pressure, eviction to system memory, plane prepare/cleanup balance, vmap/vunmap nesting, mode validation near memory limits, and debugfs VRAM reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_gem_vram_helper.h -->
