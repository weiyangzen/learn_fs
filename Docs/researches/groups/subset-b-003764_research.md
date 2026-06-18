# subset-b-003764 research

This grouped report covers the requested virtio-gpu queue/VRAM files and VKMS driver/config/composition/test files. Each file section preserves the original source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vq.c

## Purpose

`virtgpu_vq.c` is the virtio-gpu command transport layer. It allocates command buffers, submits scatter-gather descriptors to the control and cursor virtqueues, handles responses asynchronously from workqueue callbacks, emits fences, manages resource lifecycle commands, and exposes panic-path helpers for minimal framebuffer updates during `drm_panic`.

## Important APIs, types, and functions

The central local type is `struct virtio_gpu_vbuffer`, allocated from the `vgdev->vbufs` kmem cache by `virtio_gpu_alloc_vbufs()`, `virtio_gpu_get_vbuf()`, and panic-specific `virtio_gpu_panic_get_vbuf()`. Public command helpers include resource creation/destruction, scanout programming, 2D/3D transfers, context management, command submission, object attach/detach, cursor updates, UUID assignment, blob map/unmap, blob creation, and `SET_SCANOUT_BLOB`.

Queueing is handled by `virtio_gpu_queue_ctrl_sgs()`, `virtio_gpu_queue_fenced_ctrl_buffer()`, `virtio_gpu_queue_ctrl_buffer()`, `virtio_gpu_queue_cursor()`, and the panic variants. `virtio_gpu_dequeue_ctrl_func()` and `virtio_gpu_dequeue_cursor_func()` drain completed virtqueue buffers. Response callbacks update display modes, capset metadata/cache entries, EDID objects, object UUID state, and VRAM map state.

## Control flow and state

Command helpers allocate a vbuffer, fill little-endian virtio-gpu command structs, optionally attach outgoing data (`data_buf`, `data_size`) and object arrays, then submit descriptors. Control-queue submission waits for space under `ctrlq.qlock`, emits a fence only once the vbuffer position is known, adds fences to object reservations, records a sequence number, and increments `pending_commands`. `virtio_gpu_notify()` batches kicks by clearing `pending_commands` and calling `virtqueue_kick_prepare()`/`virtqueue_notify()`.

Completion flows from virtqueue callbacks `virtio_gpu_ctrl_ack()` and `virtio_gpu_cursor_ack()` into scheduled work. The control worker disables callbacks, reclaims all buffers, processes error/fence flags, invokes response callbacks, wakes queue waiters, frees object arrays later, and releases buffers. The cursor worker only traces and frees cursor vbuffers, then wakes waiters.

## Persistence and integration

The file mutates persistent in-memory driver state: scanout info, EDID pointers, capset cache entries, object `created`/`attached` flags, UUID states, VRAM `map_state`/`map_info`, queue sequence numbers, and wake queues. It integrates with virtio core, DRM EDID/KMS hotplug helpers, dma-mapping, GEM object arrays, virtio-gpu fences, blob resources, and tracepoints in `virtgpu_trace.h`.

## Risks and test signals

Key risks are queue-space deadlock, missed notifications, response callback races, stale object arrays, DMA sync errors for shmem transfers, scatterlist construction for vmalloc data, and panic-path GFP_ATOMIC assumptions. Error responses are ratelimited but many command helpers do not propagate queueing failures to callers. Test signals are mostly integration-level: boot/probe, resource creation, display hotplug/EDID, virgl/capset queries, PRIME UUID export, host-visible blob mmap, cursor movement, and panic display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vram.c

## Purpose

`virtgpu_vram.c` implements virtio-gpu GEM objects backed by host-visible blob VRAM. It creates private GEM objects, issues blob resource commands, maps them into the host-visible aperture, supports userspace mmap through PFN remapping, and exports DMA-BUF mappings for mappable and UUID-addressable resources.

## Important APIs, types, and functions

The object functions table `virtio_gpu_vram_funcs` wires GEM open/close, `virtio_gpu_vram_free()`, `virtio_gpu_vram_mmap()`, and PRIME export. `virtio_gpu_vram_create()` allocates `struct virtio_gpu_object_vram`, initializes GEM size and mmap offset, obtains a resource id, creates a blob resource, and optionally calls `virtio_gpu_vram_map()`. DMA-BUF helpers are `virtio_gpu_vram_map_dma_buf()` and `virtio_gpu_vram_unmap_dma_buf()`. `virtio_gpu_is_vram()` distinguishes this object class.

## Control flow and state

Creation aligns size, initializes a fake GEM mmap offset, creates a virtio blob resource, and if `VIRTGPU_BLOB_FLAG_USE_MAPPABLE` is set inserts a node in `vgdev->host_visible_mm`. The map command stores an aperture-relative offset and asynchronously updates `vram->map_state`/`map_info` through `virtgpu_vq.c`. mmap waits until the map leaves `STATE_INITIALIZING`, validates object flags and requested range, sets mixed-map/non-expand VMA flags, adjusts page protection based on virtio cache mode, and remaps the aperture PFN range.

Freeing checks whether the object was created, conditionally unmaps allocated host-visible aperture space, unrefs the host resource, and notifies the virtqueue. DMA-BUF export returns a real one-entry sg table for mappable resources and a stub sg table for non-mappable blob resources when a virtio peer can import by UUID.

## Dependencies and integration

The file depends on DRM GEM/VMA helpers, `drm_mm` host-visible allocation state, virtio blob commands from `virtgpu_vq.c`, DMA resource mapping, and UUID export capability for non-mappable sharing. It is a bridge between DRM userspace mmap, DMA-BUF import/export, and virtio host-visible memory.

## Risks and test signals

Risks include leaked `drm_mm` nodes on command failure, blocking waits if map completion never arrives, cache-mode mismatch, PFN overflow checks, and stub sg tables that only work for UUID-capable virtio devices. Test signals include blob creation with and without mappable flags, mmap range validation, PRIME export/import, and unmap/unref ordering during object teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Kconfig

## Purpose

This Kconfig file declares the VKMS driver and its KUnit test module options. VKMS is a software-only DRM/KMS implementation used for testing and headless display environments.

## Important symbols and dependencies

`DRM_VKMS` is a tristate option depending on `DRM && MMU`. It selects DRM client selection, KMS helper support, GEM shmem helpers, CRC32, and configfs support. `DRM_VKMS_KUNIT_TEST` is a tristate test option depending on `DRM_VKMS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is hidden behind the normal KUnit all-tests flow unless explicitly selected.

## Control flow and integration

The configuration controls compilation of the main `vkms` module and the `vkms-kunit-tests` object from the local Makefiles. Selecting configfs here is important because the driver always registers the VKMS configfs subsystem during module initialization.

## State, risks, and test signals

There is no runtime state in this file. Risks are build-configuration related: enabling VKMS pulls configfs and CRC support, while enabling KUnit tests requires exported-for-KUnit symbols in composer/config/format code. The test signal is successful kernel configuration and module build with `CONFIG_DRM_VKMS` and optionally `CONFIG_DRM_VKMS_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Makefile

## Purpose

This Makefile defines the compilation units for the VKMS module and conditionally descends into the KUnit tests directory.

## Important build entries

`vkms-y` links the core implementation objects: driver registration, plane/output/writeback/connector setup, format conversion, CRTC/composer logic, config/configfs support, color pipeline setup, and LUT tables. `obj-$(CONFIG_DRM_VKMS) += vkms.o` builds the module when VKMS is enabled. `obj-$(CONFIG_DRM_VKMS_KUNIT_TEST) += tests/` includes the test subdirectory for KUnit builds.

## Integration and risks

The object order makes all core VKMS helpers part of one module, so symbol visibility is mostly internal except KUnit-exported helpers. The Makefile must stay aligned with new source files; missing an object would surface as link errors or unregistered feature paths. Test signal is a successful module build with both normal and KUnit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/Makefile

## Purpose

This Makefile builds the VKMS KUnit aggregate test object.

## Important build entries

`vkms-kunit-tests-y` includes `vkms_config_test.o`, `vkms_format_test.o`, and `vkms_color_test.o`. `obj-$(CONFIG_DRM_VKMS_KUNIT_TEST) += vkms-kunit-tests.o` links them only when the KUnit test option is enabled.

## Integration and risks

The tests import symbols from the main VKMS module through the `EXPORTED_FOR_KUNIT_TESTING` namespace. Build failures indicate missing visibility annotations, missing source objects, or stale test object names. Runtime test signal is discovery of the `vkms-config`, `vkms-format`, and `vkms-color` suites by KUnit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_color_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_color_test.c

## Purpose

`vkms_color_test.c` is a KUnit suite for VKMS color math. It validates LUT indexing/interpolation, sRGB transfer LUT round-trips, and 3x4 color transformation matrices used by the composer and plane color pipeline.

## Important APIs and cases

The suite imports `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()` from `vkms_composer.c`, plus LUT tables from `vkms_luts.h`. `vkms_color_test_get_lut_index()` checks fixed-point LUT index calculations. `vkms_color_test_lerp()` covers boundary and half-step interpolation rounding. `vkms_color_test_linear()` verifies identity behavior through the linear EOTF table. `vkms_color_srgb_inv_srgb()` checks that sRGB EOTF followed by inverse EOTF returns approximately to the original 8-bit code value. Matrix tests validate a 50% desaturation matrix and a BT.709 encoding matrix.

## Control flow and state

The file is pure test code. It uses static reference LUT data, static parameter arrays, and KUnit expectations. No persistent kernel driver state is modified beyond loading the test module.

## Dependencies and integration

It depends on DRM fixed-point helpers, KUnit, VKMS composer exports, and the `EXPORTED_FOR_KUNIT_TESTING` namespace. These tests directly protect compositor color correctness because the same helpers are used during scanline blending.

## Risks and test signals

The strongest coverage is for rounding edges and standard transfer/matrix behavior. It does not exercise full plane atomic state, writeback output, or live DRM colorop property transitions. Passing `vkms-color` is a signal that color helper arithmetic and LUT table ratios remain compatible with expected 16-bit ARGB behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_color_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_config_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_config_test.c

## Purpose

`vkms_config_test.c` is the KUnit suite for the VKMS topology configuration model. It tests creation/destruction, default-device construction, validation rules, link attachment/detachment, object iteration, cross-config rejection, and connector status storage.

## Important APIs and cases

The suite exercises `vkms_config_create()`, `vkms_config_default_create()`, destroy helpers, list iteration macros, getters/setters, `vkms_config_is_valid()`, and xarray-backed link helpers for planes-to-CRTCs, encoders-to-CRTCs, and connectors-to-encoders. The parameterized default-config test covers all combinations of cursor, writeback, overlay, and plane pipeline flags.

Validation tests cover zero and excessive counts, missing primary planes, duplicate primary/cursor planes for one CRTC, missing possible CRTCs/encoders, invalid connector linkage, and attaching objects from different `vkms_config` owners. Link tests verify duplicate attach errors and correct iteration after detach and destroy.

## Control flow and state

Each test creates isolated heap-backed `struct vkms_config` objects, mutates their lists/xarrays, asserts validity or pointer identity, and destroys them before return. There is no DRM device registration in this suite; it targets the configuration data model before instantiation.

## Dependencies and integration

It depends on `vkms_config.h` and KUnit-exported config functions. It protects configfs and default module-parameter paths because both feed the same topology creation and validation helpers before `vkms_create()`.

## Risks and test signals

Coverage is strong for in-memory topology invariants, ownership boundaries, and default configuration variants. It does not cover configfs lifetime/reference interactions or live device enable/disable. Passing `vkms-config` signals that the config layer rejects invalid topologies and maintains list/xarray consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_config_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_format_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_format_test.c

## Purpose

`vkms_format_test.c` validates VKMS YUV-to-ARGB conversion math for multiple color encodings and ranges. It protects the conversion matrices and `argb_u16_from_yuv161616()` helper used by format read-line callbacks.

## Important APIs and cases

The suite imports `get_conversion_matrix_to_argb_u16()` and `argb_u16_from_yuv161616()`. The parameter table contains reference white, gray, black, red, green, and blue samples for BT.601, BT.709, and BT.2020 in both full and limited range. Reference values were generated with the `colour` Python framework and stored as 16-bit YUV/ARGB pairs.

## Control flow and state

For each parameter case, the test obtains a matrix using `DRM_FORMAT_NV12` plus the requested encoding/range, converts every reference YUV sample, and allows a bounded per-channel absolute difference of `0x1ff`. The file has no persistent state beyond static test vectors.

## Dependencies and integration

It depends on DRM color names, KUnit, and VKMS format exports. It covers the matrix-generation path used by planar and semiplanar YUV read-line functions for sampled framebuffer content.

## Risks and test signals

The suite focuses on numeric correctness for matrix conversion, not pointer stepping, subsampling offsets, packed pixel address calculation, or writeback encoding. Passing `vkms-format` is a strong signal that color encoding/range matrices and YUV channel conversion remain within expected tolerances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_format_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_colorop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_colorop.c

## Purpose

`vkms_colorop.c` creates the optional per-plane DRM color pipeline used by VKMS when the plane pipeline feature is enabled. It models a fixed chain of color operations that the composer later evaluates for each pixel.

## Important APIs and functions

`vkms_initialize_colorops()` creates and attaches a `COLOR_PIPELINE` property to a DRM plane. Internally, `vkms_initialize_color_pipeline()` allocates four `struct drm_colorop` objects: a 1D curve supporting sRGB EOTF and inverse EOTF, two 3x4 CTM operations, and a final 1D curve with the same supported transfer functions. Each operation allows bypass, and `drm_colorop_set_next_property()` links them in order. `vkms_colorop_funcs.destroy` delegates cleanup to DRM core.

## Control flow and state

The function allocates colorops, initializes each through DRM colorop helpers, records the first op id/name in a single enum list entry, then creates the plane property. On error it cleans already initialized ops and frees their memory. The persistent state lives in DRM plane/colorop objects and their property graph.

## Dependencies and integration

This file depends on DRM colorop, plane, property, and print helpers. It integrates with plane initialization and `vkms_composer.c`, where `pre_blend_color_transform()` traverses `plane_state->color_pipeline`, checks bypass state, and applies the corresponding LUT or matrix operation.

## Risks and test signals

Risks include partial allocation cleanup, leaked dynamically allocated pipeline names, mismatch between declared pipeline order and compositor evaluation, and unsupported colorop types. KUnit color tests cover the math helpers but not DRM property creation; integration tests should exercise plane initialization with `enable_plane_pipeline=1` and atomic commits that toggle colorop bypass/data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_colorop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.c

## Purpose

`vkms_composer.c` is VKMS's software composition engine. It blends active planes line by line into an internal 16-bit ARGB buffer, applies per-plane color operations and CRTC gamma LUTs, computes CRC entries for vblank frames, and writes composed pixels into writeback buffers.

## Important APIs and functions

Exported or externally used entry points are `vkms_composer_worker()`, `vkms_get_crc_sources()`, `vkms_verify_crc_source()`, `vkms_set_crc_source()`, and `vkms_set_composer()`. KUnit-visible helpers include `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()`. Internal helpers handle premultiplied alpha blending, background fill, gamma LUT application, colorop traversal, rotation-to-read-direction mapping, source/destination clamping, scanline blending, format/map validation, and active-plane composition.

## Control flow and state

The CRTC vblank path queues `vkms_composer_worker()` when CRC or writeback composition is enabled. The worker snapshots `frame_start`, `frame_end`, `crc_pending`, and `wb_pending` under `composer_lock`, prepares gamma LUT metadata from the live CRTC state, and composes only if CRC work is pending. Composition allocates one staging and one output line buffer, then for each CRTC scanline fills the background color, blends active planes in z-order, applies gamma, updates a CRC32 over the raw 16-bit ARGB line, and optionally writes a row to the writeback buffer. Once complete, writeback completion is signaled and CRC entries are emitted for every pending frame.

## Dependencies and integration

The composer consumes `vkms_crtc_state`, `vkms_plane_state`, pixel read/write functions from `vkms_formats.c`, LUT tables from `vkms_luts.h`, DRM rotation/rect/fixed-point helpers, DRM CRC APIs, and DRM writeback completion. It is synchronized with CRTC atomic commit via `vkms_crtc.c`, which flushes work before cleanup.

## Risks and test signals

High-risk areas are buffer bounds during rotated reads, subsampled format callback correctness, slow worker backpressure across vblank frames, lock ordering between `lock` and `composer_lock`, color pipeline state lifetime, and memory allocation during composition. KUnit tests cover LUT/matrix math; broader signals include IGT CRC/writeback/rotation/alpha/color-management tests and KMS atomic stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.h

## Purpose

`vkms_composer.h` declares KUnit-visible compositor helper APIs and the LUT channel enum used to index `struct drm_color_lut` fields.

## Important APIs and types

`enum lut_channel` maps red, green, blue, and reserved channels to the physical field order of `struct drm_color_lut`; the code relies on this ordering when treating LUT entries as `__u16` arrays. Under `CONFIG_KUNIT`, the header declares `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()`.

## Integration, state, and risks

The header has no runtime state. It depends on `kunit/visibility.h` and `vkms_drv.h`. Its primary integration point is between `vkms_composer.c` and the KUnit color suite. The risk is ABI/layout sensitivity: the compositor asserts `struct drm_color_lut` has no unexpected padding, and this enum must remain aligned with that struct layout.

## Test signals

The `vkms-color` KUnit suite uses these declarations to validate interpolation, LUT lookup, and matrix transformation behavior. Build failures under `CONFIG_DRM_VKMS_KUNIT_TEST` would flag missing or mismatched declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.c

## Purpose

`vkms_config.c` implements the in-memory VKMS topology configuration model. It creates/destroys device configs, builds default topologies from module parameters, validates plane/CRTC/encoder/connector relationships, exposes a debugfs summary, and manages xarray-backed possible-link relationships.

## Important APIs and functions

Public helpers include `vkms_config_create()`, `vkms_config_default_create()`, `vkms_config_destroy()`, `vkms_config_is_valid()`, `vkms_config_register_debugfs()`, create/destroy helpers for each topology object, attach/detach helpers for possible CRTCs/encoders, and lookup helpers for a CRTC primary or cursor plane. Many functions are exported for KUnit.

## Control flow and state

`vkms_config_create()` allocates a config, duplicates the device name, and initializes lists. The default constructor creates one primary plane, one CRTC, optional overlays/cursor, one encoder, and one connector, linking all possible paths. Destroy walks all lists safely; CRTC and encoder destruction also detaches reverse links from dependent objects.

Validation enforces 1 to 31 planes/CRTCs/encoders/connectors, at least one possible CRTC for every plane/encoder, at least one primary and no duplicate primary/cursor per CRTC, at least one encoder for every CRTC, and at least one possible encoder for every connector. Link attach helpers reject cross-config attachments and duplicates, then allocate xarray entries.

## Dependencies and integration

The file depends on Linux lists/xarrays, DRM plane/connector status types, debugfs helpers, and VKMS driver types. It feeds both `vkms_drv.c` default-device creation and `vkms_configfs.c` user-created devices. `vkms_output_init()` consumes the config object's runtime pointers during DRM object creation.

## Risks and test signals

Risks include reverse-link cleanup gaps, duplicate topology acceptance, xarray allocation errors, and using internal runtime pointers after device teardown. The `vkms-config` KUnit suite thoroughly covers default creation, validation rules, object iteration, link attach/detach, cross-config rejection, and connector status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.h

## Purpose

`vkms_config.h` defines the topology data model and helper API for configuring VKMS devices before they are instantiated as DRM devices.

## Important APIs and types

`struct vkms_config` owns device name, lists of planes/CRTCs/encoders/connectors, and the live `struct vkms_device *dev` when instantiated. Per-object structs store their owner config, link node, user-visible attributes, xarray possible-link sets, and temporary runtime DRM object pointers. Iteration macros wrap list and xarray traversal for all object/link classes. Inline accessors expose device name, CRTC count, plane type/default pipeline, CRTC writeback flag, and connector status.

The header declares all creation/destruction, validation, debugfs, attachment, detachment, and lookup functions implemented in `vkms_config.c`.

## State and integration

The state model is pre-device configuration plus runtime back-references populated during device creation. Configfs mutates this model under its device lock; the default module path creates it from module parameters; output/plane/connector initialization consumes it to build DRM objects.

## Risks and test signals

The main risks are lifetime confusion between persistent config objects and transient runtime pointers, xarray link ownership, and callers mutating configs while a device is enabled. The KUnit config suite exercises this API directly, including list iteration, link iteration, validation, and status setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.c

## Purpose

`vkms_configfs.c` exposes runtime creation and configuration of VKMS devices through configfs. It maps configfs directories, attributes, and symlinks to the `vkms_config` topology model, then creates or destroys DRM devices when the device `enabled` attribute changes.

## Important APIs and functions

The public entry points are `vkms_configfs_register()` and `vkms_configfs_unregister()`. Internal configfs item types model devices, planes, CRTCs, encoders, connectors, and possible-link groups. Attribute handlers expose CRTC `writeback`, plane `type`, connector `status`, and device `enabled`. `allow_link`/`drop_link` handlers connect planes to CRTCs, encoders to CRTCs, and connectors to encoders.

## Control flow and state

Creating a directory under `/config/vkms` allocates `struct vkms_configfs_device`, creates a `vkms_config`, initializes a mutex, and adds default child groups for planes, CRTCs, encoders, and connectors. Child directory creation allocates configfs wrappers and corresponding config objects. Symlinks in `possible_*` groups call the config attach helpers. Most structural mutations reject changes with `-EBUSY` once the device is enabled.

Writing `enabled=1` validates the config and calls `vkms_create()`. Writing `enabled=0` calls `vkms_destroy()`. Connector status can be changed while enabled and triggers `vkms_trigger_connector_hotplug()`. Release handlers destroy underlying config objects and wrapper allocations; device release also destroys a live device and the owned config.

## Dependencies and integration

The file depends on Linux configfs, cleanup scoped guards, mutexes, VKMS config helpers, `vkms_create()`/`vkms_destroy()`, and connector hotplug support. It is registered at module init and gives users a way to instantiate non-default VKMS topologies.

## Risks and test signals

Risks include configfs lifetime ordering, symlink targets from other devices, lock coverage around live enable/disable, ensuring all structural edits are blocked while enabled, and preventing the reserved default device name from colliding with module-created VKMS. KUnit does not cover configfs directly; useful signals are configfs integration tests creating devices, linking topology, toggling enabled, and changing connector status live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.h

## Purpose

`vkms_configfs.h` declares the VKMS configfs registration lifecycle.

## Important APIs

`vkms_configfs_register()` registers the `/config/vkms` subsystem and is called during module initialization. `vkms_configfs_unregister()` unregisters it during module exit.

## Integration, state, and risks

The header has no state. It is included by `vkms_drv.c` for module lifecycle and by `vkms_configfs.c` for self-declarations. Risk is minimal; registration state is implemented in the `.c` file through `is_configfs_registered`.

## Test signals

Build coverage verifies declaration/definition consistency. Runtime integration is successful module load/unload with configfs enabled and no double-register/unregister warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.c

## Purpose

`vkms_connector.c` implements VKMS virtual connector behavior: detection status, mode enumeration, encoder selection, connector initialization, and hotplug notification.

## Important APIs and functions

`vkms_connector_init()` allocates a managed `struct vkms_connector`, initializes a DRM virtual connector with atomic helper funcs, and attaches connector helper funcs. `vkms_connector_detect()` reads connector status from the live `vkms_config_connector` associated with the wrapper; if the config object has disappeared, it preserves the current connector status. `vkms_conn_get_modes()` publishes DRM no-EDID modes up to VKMS maximums and marks the default resolution preferred. `vkms_conn_best_encoder()` returns the first possible encoder. `vkms_trigger_connector_hotplug()` emits a KMS hotplug event.

## State and integration

The connector state comes from both DRM connector state and the configuration model. Configfs can change connector status and trigger hotplug while enabled. Output initialization links connectors to possible encoders according to the config.

## Risks and test signals

Risks include stale config pointers after configfs removal, missing possible encoders, and mode list assumptions without EDID. Tests should cover connector status transitions through configfs, hotplug event delivery, no-EDID mode enumeration, and atomic modesets through possible encoder paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.h

## Purpose

`vkms_connector.h` defines the VKMS connector wrapper and declares connector lifecycle/hotplug helpers.

## Important APIs and types

`struct vkms_connector` wraps `struct drm_connector`. `drm_connector_to_vkms_connector()` converts from DRM connector to wrapper. `vkms_connector_init()` creates the connector for a VKMS device, and `vkms_trigger_connector_hotplug()` emits a hotplug notification for connector status changes.

## Integration, state, and risks

The wrapper is used by output initialization and config connector runtime pointers. It has no standalone persistence beyond managed DRM allocation. The main risk is ensuring conversions are only applied to VKMS-owned connectors.

## Test signals

Build coverage verifies declarations. Runtime signals are successful connector initialization, status detection, and hotplug event behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_crtc.c

## Purpose

`vkms_crtc.c` implements VKMS CRTC state, vblank-driven composition scheduling, atomic CRTC hooks, CRC source plumbing, and CRTC initialization.

## Important APIs and functions

`vkms_crtc_init()` allocates a managed `struct vkms_output` with primary/cursor planes, installs helper funcs, enables gamma/color management/background color properties, initializes locks, and creates an ordered composer workqueue. Atomic hooks include duplicate/destroy/reset state, `vkms_crtc_atomic_check()`, `vkms_crtc_atomic_begin()`, and `vkms_crtc_atomic_flush()`. `vkms_crtc_handle_vblank_timeout()` is wired through DRM vblank timer funcs and queues composer work when enabled.

## Control flow and state

Atomic check adds affected planes, counts visible planes, allocates `active_planes`, and stores z-ordered `vkms_plane_state` pointers for composition. Atomic begin takes `vkms_output->lock` to prevent vblank scheduling while composer state is updated; atomic flush sends/arms page-flip events and stores the current `vkms_crtc_state` as `composer_state` before unlocking.

On vblank, the handler calls `drm_crtc_handle_vblank()`, snapshots the current composer state, updates frame range and pending flags under `composer_lock`, and queues `composer_work` on the ordered workqueue. State destruction warns if work is still pending and frees active-plane arrays.

## Dependencies and integration

The file depends on DRM atomic, vblank, blend/color management, probe, and managed allocation helpers. It is tightly integrated with `vkms_composer.c`, which consumes `vkms_crtc_state`, and with `vkms_drv.c` atomic commit tail, which flushes composer work before plane cleanup.

## Risks and test signals

Risks include lock ordering around commit/vblank, active-plane pointer lifetime, worker backlog if composition is slow, event delivery when vblank cannot be acquired, and gamma LUT size checks in driver atomic check. Signals include IGT atomic/CRC/vblank tests, KMS writeback tests, and warnings from pending work during state destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.c

## Purpose

`vkms_drv.c` is the VKMS module and DRM driver entry point. It declares module parameters, DRM driver/mode-config callbacks, device creation/destruction, module init/exit, and default-device setup.

## Important APIs and functions

Module parameters control default cursor, writeback, overlay, plane pipeline, and whether a default VKMS device is created. `vkms_atomic_commit_tail()` sequences DRM atomic helper operations, fake vblank, flip completion waits, composer work flushing, and plane cleanup. `vkms_atomic_check()` validates gamma LUT size before delegating to DRM atomic checks. `vkms_modeset_init()` initializes mode config bounds and output components. Public lifecycle APIs are `vkms_create()` and `vkms_destroy()`.

## Control flow and state

`vkms_init()` registers configfs, optionally creates a default config from module params, instantiates a device, and stores it in `default_config`. `vkms_create()` creates a faux device, opens a devres group, allocates a managed DRM device, stores config back-pointer, coerces DMA mask, initializes vblank count from config CRTCs, initializes modeset/output, registers debugfs, registers the DRM device, and starts client setup. Error paths release devres and destroy the faux device. `vkms_destroy()` unregisters DRM, shuts down atomic state, releases devres, destroys the faux device, and clears `config->dev`.

## Dependencies and integration

The file depends on faux devices, DRM managed allocation, GEM shmem helpers, fbdev shmem helpers, vblank, atomic helpers, config/configfs, and output initialization from other VKMS files. Configfs-created and default devices both converge on `vkms_create()`.

## Risks and test signals

Risks include init failure after configfs registration leaking registration when default-device creation fails, resource-group lifetime ordering, composer work flushing before cleanup, gamma LUT size calculation correctness, and module parameter interactions. Test signals include module load/unload, default device creation, configfs-created devices, fbdev client setup, atomic modesets, and KUnit suites for config/color/format helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.h

## Purpose

`vkms_drv.h` is the shared internal VKMS header. It defines constants, pixel/frame representations, plane/CRTC/output/device state structs, conversion callbacks, container helpers, and cross-file function declarations.

## Important APIs and types

Constants define default/min/max resolutions, overlay count, and LUT size. `struct vkms_frame_info` captures framebuffer, source/destination rects, iosys maps, and rotation. `struct pixel_argb_u16` is the internal 16-bit ARGB pixel format; `struct pixel_argb_s32` gives color pipeline headroom. `pixel_read_line_t` and `pixel_write_t` abstract format conversion. `struct conversion_matrix` stores YUV conversion coefficients. `struct vkms_plane_state`, `vkms_crtc_state`, `vkms_writeback_job`, `vkms_output`, and `vkms_device` are the main driver state types.

The header declares device creation/destruction, CRTC/output/plane initialization, CRC hooks, composer entry points, writeback row conversion, writeback connector enablement, and colorop initialization.

## State and integration

Most VKMS `.c` files share these structs. Composition, format conversion, writeback, plane atomic state, CRTC state, config-driven object creation, and DRM device lifecycle all meet here. State persistence is in DRM atomic state objects, managed DRM objects, workqueues, locks, and config back-pointers.

## Risks and test signals

Risks include layout assumptions for pixel structs used in CRC, callback pointers being unset for newly supported formats, and lifetime confusion among atomic state, frame info maps, and workqueue use. KUnit and IGT coverage should exercise format callbacks, composer math, CRC/writeback, and atomic state duplication/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.c

## Purpose

`vkms_formats.c` implements framebuffer pixel read and write conversion for VKMS. It converts many DRM formats into the compositor's internal 16-bit ARGB format, writes internal pixels back to supported writeback formats, and provides YUV colorimetry conversion matrices.

## Important APIs and functions

Public APIs are `get_pixel_read_line_function()`, `get_pixel_write_function()`, `get_conversion_matrix_to_argb_u16()`, and KUnit-visible `argb_u16_from_yuv161616()`. Internal helpers compute packed-pixel offsets/addresses, directional byte steps, subsampling offsets, RGB/gray/YUV conversion, generated read-line functions for RGB and grayscale formats, semiplanar/planar YUV readers, and ARGB-to-writeback writers.

## Control flow and state

Read-line callbacks start from a framebuffer coordinate, direction, and count, then walk the appropriate plane memory using pitches, offsets, block sizes, and rotation-derived direction. Packed RGB formats use generated tight loops. Low-bit R formats extract bitfields from blocks. YUV callbacks sample luma and chroma planes with hsub/vsub-aware stepping, then apply the plane's conversion matrix. Writeback row conversion obtains a destination row address and invokes the selected pixel writer for each output pixel.

Matrix selection chooses BT.601/BT.709/BT.2020 and full/limited range constants, copies them into the plane state, and swaps U/V columns for YVU or NV21/NV61/NV42 variants.

## Dependencies and integration

The file depends on DRM format metadata, fixed-point helpers, rect/blend definitions, and VKMS frame/plane/writeback state. Plane atomic setup selects read callbacks and conversion matrices; composer uses read callbacks; writeback uses pixel writers.

## Risks and test signals

Risks include pointer stepping bugs for rotated vertical reads, block-size assumptions, bit-order errors in R1/R2/R4 formats, chroma siting/subsampling mistakes, endian mistakes, unsupported format lists diverging from plane/writeback validation, and `BUG()` paths if validation misses an unsupported format. KUnit covers YUV matrix conversion; IGT should cover CRC/writeback for all advertised formats and rotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.h

## Purpose

`vkms_formats.h` declares VKMS format conversion entry points used by plane, composer, writeback, and KUnit code.

## Important APIs

`get_pixel_read_line_function()` maps a DRM fourcc to a scanline reader returning internal 16-bit ARGB pixels. `get_pixel_write_function()` maps a writeback fourcc to an encoder from internal pixels. `get_conversion_matrix_to_argb_u16()` selects the YUV-to-ARGB matrix for a format, encoding, and range. Under KUnit, `argb_u16_from_yuv161616()` is exposed for direct numeric testing.

## Integration, state, and risks

The header has no state, but it defines the callback boundary between VKMS atomic plane/writeback setup and compositor execution. Risks are declaration drift from implementation or format list drift from `vkms_plane.c`/`vkms_writeback.c` validation.

## Test signals

`vkms-format` KUnit validates the exposed YUV conversion helper. Build and IGT format coverage validate the read/write callback mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_formats.h -->
