# subset-b-003765 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.c

## Purpose

`vkms_luts.c` provides built-in VKMS color lookup tables used by the virtual KMS color pipeline. It is data-only: 256-entry DRM LUT arrays encode linear, sRGB EOTF, and inverse sRGB transfer curves, and exported `vkms_color_lut` descriptors give other VKMS color code a uniform way to sample those arrays.

## Important APIs, Types, and Functions

- `linear_array`, `srgb_array`, and `srgb_inv_array`: static `struct drm_color_lut[LUT_SIZE]` tables with identical red/green/blue values and zero reserved fields.
- `linear_eotf`, `srgb_eotf`, and `srgb_inv_eotf`: exported `const struct vkms_color_lut` descriptors containing a table pointer, `lut_length = LUT_SIZE`, and `channel_value2index_ratio = 0xff00ffll`.
- `EXPORT_SYMBOL(...)`: makes the descriptors available to other VKMS compilation units or modules that implement color operations.
- The table-generation comment points to the external LUT generator and notes Skia transfer-function provenance.

## Control Flow

There is no executable control flow beyond module/link-time data initialization. Consumers choose one of the exported descriptors, convert a channel value to an index using the ratio, and read from the associated static array.

## State and Persistence Behavior

All state is static and immutable after load. The backing arrays are private to this translation unit; only descriptor addresses are exported. There is no allocation, locking, refcounting, or persistence outside the kernel image/module lifetime.

## Dependencies and Integration Points

- Depends on DRM `struct drm_color_lut` from `<drm/drm_mode.h>`.
- Depends on `struct vkms_color_lut` from `vkms_drv.h` and `LUT_SIZE` declarations from `vkms_luts.h`.
- Integrates with VKMS color pipeline code that implements EOTF/inverse EOTF transformations and expects 16-bit DRM LUT channel values.

## Risks and Edge Cases

- The descriptor ratio must stay synchronized with `LUT_SIZE` and the 16-bit input range. A mismatched ratio can clamp or skip entries.
- The table values are generated constants, so review should focus on monotonicity, endpoints, and curve identity rather than algorithmic behavior.
- All three channels are equal, making these grayscale transfer curves. Any future per-channel curve must update assumptions in consumers.
- External provenance means regeneration should be reproducible and documented when curves change.

## Test Signals

- Build/link checks should confirm the exported symbols resolve for VKMS color code.
- Unit or KUnit coverage should verify first/last entries are `0x0000`/`0xffff`, each table has exactly `LUT_SIZE` entries, and values are monotonic.
- Color-pipeline tests should compare selected sRGB and inverse-sRGB samples against expected transfer-function tolerances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.h

## Purpose

`vkms_luts.h` is the small public declaration header for VKMS built-in color lookup tables. It defines the shared LUT length and declares the exported linear, sRGB, and inverse-sRGB `vkms_color_lut` descriptors.

## Important APIs, Types, and Functions

- `LUT_SIZE`: fixed table size of 256 entries used by the static tables in `vkms_luts.c`.
- `linear_eotf`, `srgb_eotf`, `srgb_inv_eotf`: extern declarations for immutable `struct vkms_color_lut` descriptors.
- Include guard `_VKMS_LUTS_H_`: prevents duplicate declarations.

## Control Flow

The header has no runtime control flow. It provides compile-time constants and extern declarations for color code that samples LUTs.

## State and Persistence Behavior

The declarations refer to static module-lifetime data defined in `vkms_luts.c`. The header itself owns no storage and performs no initialization.

## Dependencies and Integration Points

- Assumes `struct vkms_color_lut` is visible before or through including VKMS driver headers in consumers.
- Couples `LUT_SIZE` to the generated table definitions and index-ratio math in `vkms_luts.c`.

## Risks and Edge Cases

- Changing `LUT_SIZE` requires regenerating all table initializers and revisiting index conversion logic.
- Because this header only forward-declares objects, consumers must include the right VKMS type definitions to avoid incomplete-type failures.

## Test Signals

- Compile coverage for all VKMS color consumers catches missing type declarations and symbol signature drift.
- Static assertions or table-size tests are useful if `LUT_SIZE` is ever changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_output.c

## Purpose

`vkms_output.c` wires a parsed VKMS configuration into DRM mode-setting objects. It creates planes, CRTCs, optional writeback connectors, encoders, and connectors; fills `possible_crtcs`/clone masks; attaches connectors to encoders; and resets mode configuration after the virtual display graph is constructed.

## Important APIs, Types, and Functions

- `vkms_output_init(struct vkms_device *vkmsdev)`: the only function in the file and the top-level output initialization path.
- `vkms_config_is_valid` and `vkms_config_for_each_*` helpers: validate and iterate the declarative VKMS topology.
- `vkms_plane_init`, `vkms_crtc_init`, `vkms_enable_writeback_connector`, and `vkms_connector_init`: delegated constructors for individual DRM object types.
- DRM managed allocation/init helpers: `drmm_kzalloc`, `drmm_encoder_init`, `drm_connector_attach_encoder`, `drm_crtc_mask`, `drm_encoder_mask`, and `drm_mode_config_reset`.

## Control Flow

Initialization first rejects invalid configuration with `-EINVAL`. It then initializes every configured plane and stores the resulting `vkms_plane` pointer in each plane config. Next it initializes every CRTC using its configured primary plane and optional cursor plane, and enables writeback if requested for that CRTC. After CRTCs exist, it walks plane possible-CRTC lists to populate each plane's `possible_crtcs` mask.

Encoder setup allocates a virtual encoder per encoder config, initializes it with `drmm_encoder_init`, marks it cloneable with itself, and fills its `possible_crtcs`. If one of those CRTCs has writeback, the normal encoder and writeback encoder are added to each other's `possible_clones`. Connector setup then initializes each connector and attaches all configured possible encoders. The final `drm_mode_config_reset` initializes DRM object states.

## State and Persistence Behavior

Objects allocated through DRM managed helpers persist until device teardown. Config structs are mutated to cache created plane, CRTC, encoder, and connector pointers. The file does not itself persist mode state; it builds object topology and leaves atomic state management to DRM helpers and other VKMS files.

## Dependencies and Integration Points

- Depends on VKMS configuration helpers from `vkms_config.h`, connector construction from `vkms_connector.h`, and plane/CRTC/writeback constructors declared through `vkms_drv.h`.
- Integrates with DRM managed object lifetimes and mode-config reset semantics.
- The writeback connector path integrates `vkms_writeback.c` and affects encoder clone masks for CRTC-compatible encoders.

## Risks and Edge Cases

- If writeback initialization fails, the code logs but does not return the failure. Later paths may see a CRTC marked for writeback without a fully initialized connector.
- Plane possible-CRTC masks are filled after all CRTCs are initialized; configuration helpers must not expose a CRTC without a valid `crtc` pointer.
- Clone-mask correctness matters for userspace topology probing. Missing reciprocal clone bits can make writeback or encoder combinations unavailable.
- Partial initialization errors rely on DRM managed cleanup. Any future non-managed allocation in this path must add explicit unwind behavior.

## Test Signals

- VKMS probe tests should cover valid and invalid configs, primary-only CRTCs, cursor planes, and writeback-enabled CRTCs.
- Mode enumeration should show expected plane/CRTC/encoder/connector masks and writeback clone relationships.
- Fault-injection tests for plane, CRTC, encoder, connector, and writeback allocation failures should verify error returns and no leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_plane.c

## Purpose

`vkms_plane.c` implements VKMS DRM plane support. It advertises supported framebuffer formats, owns VKMS plane state allocation/destruction/reset, prepares and unmaps shadow framebuffer memory, validates atomic plane updates, and snapshots framebuffer geometry/conversion data for the VKMS software composer.

## Important APIs, Types, and Functions

- `vkms_formats[]`: supported DRM pixel formats, including ARGB/XRGB variants, 16-bit/channel RGB, RGB565/BGR565, NV/YUV planar formats, P010/P012/P016, and low-bit-depth R formats.
- `vkms_plane_duplicate_state`, `vkms_plane_destroy_state`, `vkms_plane_reset`: plane state lifecycle callbacks backing `drm_plane_funcs`.
- `vkms_plane_atomic_update`: copies source/destination rects, framebuffer mapping, rotation, pixel-read function, and YUV-to-ARGB conversion matrix into `vkms_frame_info`/`vkms_plane_state`.
- `vkms_plane_atomic_check`: validates no scaling and obtains the matching CRTC state.
- `vkms_prepare_fb` and `vkms_cleanup_fb`: GEM shadow framebuffer prepare/vmap and vunmap helpers.
- `vkms_plane_init`: allocates a universal plane, attaches helpers, creates rotation and color properties, and optionally initializes default-pipeline color operations.

## Control Flow

Plane creation uses `drmm_universal_plane_alloc` with config-selected plane type and the static format list. Helper callbacks are attached immediately, then rotation and color-encoding/range properties are added. If the plane belongs to the default pipeline, color operation properties are initialized.

During atomic validation, disabled or framebuffer-less planes are accepted. Active planes fetch CRTC state and call `drm_atomic_helper_check_plane_state` with no scaling permitted. During framebuffer preparation, VKMS first delegates GEM plane preparation and then maps framebuffer planes into `iosys_map` storage in the shadow plane state. Atomic update is called after successful commit preparation and records all composer-facing metadata, including an extra framebuffer reference. Destroy-state later drops the saved framebuffer reference when appropriate, frees `frame_info`, destroys shadow state, and frees the VKMS state wrapper.

## State and Persistence Behavior

Each `vkms_plane_state` owns a dynamically allocated `vkms_frame_info` and embeds DRM shadow plane state. `frame_info` persists across commits while that plane state is alive and contains framebuffer pointer, rects, maps, and rotation. Framebuffer references are explicitly acquired in `vkms_plane_atomic_update` and released in state destruction when a CRTC and saved framebuffer are present. Mapping lifetime is controlled by DRM prepare/cleanup callbacks around atomic commits.

## Dependencies and Integration Points

- Uses DRM atomic, GEM framebuffer, GEM shadow-plane, blend/rotation/color-property, and FourCC helpers.
- Integrates with `vkms_formats.h` for pixel read functions and color conversion matrices.
- Feeds VKMS composer code through `vkms_frame_info`, `pixel_read_line`, and conversion matrix fields.
- Integrates with VKMS config through plane type and default-pipeline selection.

## Risks and Edge Cases

- The framebuffer refcount release is conditional on `crtc` and `frame_info->fb`; reference balancing should be checked carefully across disable commits and state duplication.
- `vkms_plane_atomic_update` assumes `prepare_fb` has populated shadow mappings before it copies them.
- No scaling is allowed. Userspace attempting scaled planes should reliably receive `-EINVAL` from helper validation.
- Format support must stay aligned with `get_pixel_read_line_function` and `get_conversion_matrix_to_argb_u16`; adding a format to one side only can fail at composition time.
- Reset allocation failure leaves the plane state unset after logging, which is consistent with kernel allocation failure behavior but can cascade into later setup failures.

## Test Signals

- Atomic commit tests should cover every advertised format, disable/enable transitions, framebuffer replacement, rotations/reflections, and color encoding/range combinations.
- Refcount and mapping tests should verify `drm_framebuffer_get/put` and `drm_gem_fb_vmap/vunmap` balance across duplicate, update, cleanup, and destroy paths.
- Negative tests should cover scaling rejection and missing CRTC/framebuffer edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_writeback.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_writeback.c

## Purpose

`vkms_writeback.c` implements VKMS writeback connector support. It exposes writeback formats, validates writeback framebuffer size against the active CRTC mode, maps writeback framebuffers for the software composer, queues writeback jobs, and initializes the writeback encoder/connector pair for an output.

## Important APIs, Types, and Functions

- `vkms_wb_formats[]`: supported writeback framebuffer formats.
- `vkms_wb_atomic_check`: validates writeback job framebuffer dimensions and delegates generic writeback state checks.
- `vkms_wb_connector_get_modes`: creates no-EDID modes up to device max width/height.
- `vkms_wb_prepare_job` and `vkms_wb_cleanup_job`: allocate/free `vkms_writeback_job`, vmap/vunmap the writeback framebuffer, and manage framebuffer refs.
- `vkms_wb_atomic_commit`: enables the composer, installs the active writeback job under `composer_lock`, queues the DRM writeback job, and initializes writeback frame info/pixel writer.
- `vkms_enable_writeback_connector`: creates the writeback encoder and calls `drmm_writeback_connector_init`.

## Control Flow

Atomic check returns early when there is no writeback job, no job framebuffer, or no associated CRTC. Otherwise it compares framebuffer dimensions to `crtc_state->mode` and rejects mismatches with `-EINVAL`, then calls DRM's writeback connector checker. Job preparation allocates a VKMS-private job wrapper, maps the framebuffer into `wb_frame_info.map`, takes a framebuffer reference, and stores the wrapper in `job->priv`.

At commit time, the connector state identifies the output CRTC and writeback connector. The composer is enabled, `active_writeback` and `wb_pending` are set while holding `composer_lock`, the job is queued to DRM, and the pixel write callback plus source/destination rectangles are initialized to the full CRTC mode size. Cleanup reverses mapping/refcount state, disables composer writeback participation, and frees the wrapper.

## State and Persistence Behavior

Writeback encoder and connector objects are DRM-managed and persist with the device. Individual writeback jobs allocate transient `vkms_writeback_job` objects stored in DRM job private data. Active job state is shared with the composer through `vkms_crtc_state` fields protected by the output's spinlock.

## Dependencies and Integration Points

- Uses DRM writeback, atomic helper, probe helper, EDID/no-EDID mode helper, and GEM framebuffer mapping APIs.
- Integrates with VKMS compositor state through `vkms_set_composer`, `active_writeback`, `wb_pending`, `wb_frame_info`, and `pixel_write`.
- Uses `get_pixel_write_function` from `vkms_formats.h`, so format lists and write callbacks must remain synchronized.

## Risks and Edge Cases

- `vkms_wb_atomic_commit` dereferences `connector_state->writeback_job->fb`; callers rely on DRM writeback semantics to only call this path for a valid job.
- The active job is published before `pixel_write` and rectangles are filled. The composer synchronization model must guarantee it cannot consume the job before those fields are initialized, or this ordering should be revisited.
- Cleanup returns early for jobs without framebuffer, so `job->priv` must only be set for framebuffer-backed jobs.
- Framebuffer size must exactly match the mode; no scaling or crop behavior is supported for writeback.

## Test Signals

- Writeback tests should cover valid commits, no-job commits, no-framebuffer jobs, framebuffer size mismatch, and each advertised writeback format.
- Race-oriented tests should verify composer state visibility around `active_writeback`, `wb_pending`, queueing, and cleanup.
- Mapping/refcount tests should ensure vmaps and framebuffer references are balanced on success and prepare failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Kconfig

## Purpose

`vmwgfx/Kconfig` declares build-time configuration for the VMware virtual GPU DRM driver and its optional mksGuestStats instrumentation default.

## Important APIs, Types, and Functions

- `CONFIG_DRM_VMWGFX`: tristate option for the VMware SVGA2/KMS DRM driver.
- Dependencies: `DRM`, `PCI`, and either `(X86 && HYPERVISOR_GUEST)` or `ARM64`.
- Selected subsystems: `DRM_CLIENT_SELECTION`, `DRM_TTM`, `DRM_TTM_HELPER`, `MAPPING_DIRTY_HELPERS`, and transitional `DRM_KMS_HELPER`.
- `CONFIG_DRM_VMWGFX_MKSSTATS`: optional boolean default for mksGuestStats instrumentation, dependent on `DRM_VMWGFX` and `X86`.

## Control Flow

Kconfig evaluation determines whether `vmwgfx.ko` can be built in, built as a module, or omitted. If selected, required DRM/TTM helper symbols are automatically enabled. The mksGuestStats option only appears when the base driver and X86 are enabled.

## State and Persistence Behavior

No runtime state is defined here. The selected symbols shape which objects are compiled and whether instrumentation defaults are enabled.

## Dependencies and Integration Points

- Integrates with the kernel DRM and PCI Kconfig menus.
- The `DRM_KMS_HELPER` select is documented as transitional until vmwgfx sets up the primary plane itself.
- `DRM_VMWGFX_MKSSTATS` ties into instrumentation types in `vm_basic_types.h` and driver-side stats code.

## Risks and Edge Cases

- Dependency changes can make the driver visible on unsupported architectures or hide it from supported virtualized environments.
- `select` bypasses dependencies of selected symbols, so selected helper symbols must remain safe to force-enable.
- Removing `DRM_KMS_HELPER` requires confirming all transitional CRTC setup code has been migrated.

## Test Signals

- Build matrix coverage should include `m`, `y`, and `n` for `DRM_VMWGFX` on supported arches and disabled visibility on unsupported combinations.
- X86 builds should cover mksGuestStats enabled/disabled; ARM64 should verify that option remains unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Makefile

## Purpose

`vmwgfx/Makefile` defines the object list that composes the VMware virtual GPU DRM driver module and wires it to `CONFIG_DRM_VMWGFX`.

## Important APIs, Types, and Functions

- `vmwgfx-y`: ordered list of object files for execbuf, GMR/MOB memory, KMS, ioctls, resources, TTM buffers, command/fence/IRQ handling, overlay, contexts, surfaces, PRIME, command buffers, cotables, stream output, dirty tracking, GEM, VKMS integration, and cursor plane support.
- `obj-$(CONFIG_DRM_VMWGFX) := vmwgfx.o`: builds the aggregate object when the Kconfig symbol is enabled.

## Control Flow

Kbuild compiles each listed `*.o` and links them into `vmwgfx.o`. The final object is included in the kernel or module build depending on the tristate value.

## State and Persistence Behavior

There is no runtime state in the Makefile. The object list controls which driver subsystems are present in the binary.

## Dependencies and Integration Points

- Must stay aligned with source files and declarations used across vmwgfx.
- The device include headers in this research item support many objects listed here, especially command, execbuf, surface, context, MOB, cotable, and devcap code.

## Risks and Edge Cases

- Omitting an object can cause link failures or subtler missing feature paths if references are conditionally compiled.
- Adding new objects in the wrong aggregate or order can expose unresolved symbols during incremental builds.
- Generated or shared ABI headers are not listed here directly; they are pulled through includes and must remain in include paths.

## Test Signals

- `allyesconfig`, `allmodconfig`, and targeted `CONFIG_DRM_VMWGFX=m/y` builds catch object-list drift.
- Link tests should cover both module and built-in forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_cmd.h

## Purpose

`svga3d_cmd.h` defines the VMware SVGA3D FIFO command ABI. It enumerates 3D command IDs and declares packed command payload structures for legacy fixed-function 3D, guest-backed resources, MOB/object-table operations, screen targets, logic operations, and command-era bridges into the DX command range.

## Important APIs, Types, and Functions

- `enum SVGAFifo3dCmdId`: command ID map from `SVGA_3D_CMD_BASE` through legacy commands, GB commands, DX commands, logicops, staging, and reserved/future ranges.
- `SVGA3dCmdHeader`: packed `{ id, size }` header used before command-specific payload bytes.
- Surface/context/shader commands: define/destroy/set/copy/present/clear payloads for `SVGA3dCmdDefineSurface`, `SVGA3dCmdDefineSurface_v2`, `SVGA3dCmdDefineGBSurface*`, `SVGA3dCmdDefineGBContext`, `SVGA3dCmdDefineGBShader`, and related bind/readback/invalidate commands.
- Draw-state commands: render state, render target, texture state, transform, viewport, scissor, clip plane, material, light, shader constants, vertex declarations/streams/divisors, and primitive draw payloads.
- MOB/object-table commands: `SVGAOTable*Entry`, `SVGA3dCmdSetOTableBase*`, `SVGA3dCmdGrowOTable`, `SVGA3dCmdDefineGBMob*`, and mapping/update commands.
- Screen and copy commands: GB screen target define/bind/update, GB screen DMA, screen copy status, zero-surface update/write, and logicops blit/fill/blend structures.

## Control Flow

The header has no executable code. Runtime control flow is implicit in FIFO submission: driver code writes `SVGA3dCmdHeader`, appends the matching packed structure and any variable-length tail data, and the virtual device interprets fields by command ID. Command families evolve from legacy host surfaces to guest-backed MOB/object-table resources and then to DX commands whose payload structures live in `svga3d_dx.h`.

## State and Persistence Behavior

The command structures describe state transitions in the virtual GPU: object creation/destruction, binding, readback/invalidation, draw state changes, query lifecycle, screen target updates, and synchronization/fence reporting. State itself persists in host/device resources, MOBs, object tables, and guest-visible buffers, not in this header.

## Dependencies and Integration Points

- Includes `svga3d_types.h`, `svga3d_limits.h`, and `svga_reg.h`.
- Used by vmwgfx command construction, execbuf validation, resource tracking, surface/context/shader/MOB managers, and virtual-device capability handling.
- Shares command IDs with the host hypervisor ABI; numeric values and packed layout are externally constrained.

## Risks and Edge Cases

- Packed structure sizes and command IDs are ABI. Any padding, type-width, or enum-number drift can break host parsing.
- Many commands use implicit variable-length payloads following a fixed header, so validators must compute sizes from command header length and count fields.
- Several names are reserved or dead; reusing them without host support can create compatibility failures.
- Surface flag versions split 32-bit and 64-bit flags. Validation must apply the right disallowed masks for command version and hardware capability.
- MOB offsets, pitches, array sizes, mip levels, and boxes are guest-controlled command data and require overflow and bounds checks before submission.

## Test Signals

- Compile-time `sizeof`/offset checks against known ABI sizes are valuable for packed command structs.
- Execbuf validation tests should cover command ID dispatch, payload length mismatch, variable-tail commands, invalid IDs, reserved/dead commands, and capability-gated commands.
- Integration tests should exercise surface/context/shader/MOB lifecycles, readback/invalidate ordering, screen target updates, and logicops commands under supported virtual hardware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_devcaps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_devcaps.h

## Purpose

`svga3d_devcaps.h` defines SVGA3D device capability indices and result types. The driver uses these constants to query and interpret host-advertised 3D, DX, shader-model, multisample, logic operation, format, and resource limits.

## Important APIs, Types, and Functions

- `SVGA3D_MAKE_HWVERSION`, `SVGA3D_MAJOR_HWVERSION`, `SVGA3D_MINOR_HWVERSION`: helpers for encoded hardware-version values.
- `SVGA3dHardwareVersion`: historical/current virtual hardware version constants.
- `SVGA3dDevCapIndex`: integer capability selector type.
- `SVGA3D_DEVCAP_*`: dense capability index list from core 3D support and fixed-function limits through DX format support, SM4.1/SM5, multisampling, logicops, GL43, and `SVGA3D_DEVCAP_MAX`.
- `SVGA3D_DXFMT_*`: bit flags describing DX format support properties such as shader sampling, render-target use, blending, mips, arrays, volume, vertex-buffer use, and multisampling.
- `SVGA3dDevCapResult`: union view of a capability result as bool, unsigned, signed, or float.

## Control Flow

There is no runtime control flow in the header. Driver code selects a capability index, reads the corresponding device result, and interprets the union member according to the documented capability.

## State and Persistence Behavior

Capability values are usually read during device initialization or feature probing and then cached in driver state. The header defines the index ABI but owns no storage.

## Dependencies and Integration Points

- Includes `svga3d_types.h` for VMware fixed-width and 3D types.
- Integrates with `vmwgfx_devcaps.o`, feature checks, format validation, shader-model gating, and command validation paths.
- Numeric indices must match host SVGA device firmware/hypervisor expectations.

## Risks and Edge Cases

- The capability table has missing/dead slots preserved for ABI numbering. Renumbering or compacting it would corrupt all later queries.
- `SVGA3dDevCapResult` is untagged; callers must know whether a specific index returns bool, integer, or float.
- Format capability flags are bitmasks, not enum values. Misinterpreting zero or unsupported flags can enable invalid render paths.
- `SVGA3D_DEVCAP_MAX` must stay consistent with host-provided capability table sizing.

## Test Signals

- Device-probe tests should verify queried caps are in range and cached values gate DX/SM/multisample/logicops paths correctly.
- ABI tests should detect changes to numeric capability indices and `SVGA3D_DEVCAP_MAX`.
- Format validation tests should cross-check `SVGA3D_DXFMT_*` flags against accepted surface/view/buffer uses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_devcaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_dx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_dx.h

## Purpose

`svga3d_dx.h` defines the VMware SVGA DX command and state ABI. It maps Direct3D 10/11-style resources, views, shaders, constant buffers, samplers, blend/depth/rasterizer state, queries, stream output, unordered-access views, staging copies, shader interfaces, and context MOB layouts into packed FIFO payload structures.

## Important APIs, Types, and Functions

- DX limits and IDs: vertex buffers, inputs, stream-output targets, shader-resource views, constant buffers, samplers, class instances, and object ID typedefs.
- Pipeline commands: `SVGA3dCmdDXSetSingleConstantBuffer`, shader resource/sampler/shader binds, draw/dispatch variants, input layout, vertex/index buffers, topology, render targets, blend/depth/rasterizer state, viewports, scissor rects, and clears.
- Query commands: define/destroy/bind/begin/end/readback/move/all-query/predication payloads and `SVGADXQueryDeviceState`.
- Copy/transfer commands: predicated copies, staging copies, buffer copies, convert/resolve transfers, surface copy/readback, transfer-to/from-buffer, and subresource update/readback/invalidate.
- View definitions: shader-resource, render-target, depth-stencil, unordered-access, and buffer-ex view descriptors.
- State-object definitions: input element layout, blend state, depth/stencil state, rasterizer state, sampler state, shader signatures, shader definitions, stream-output definitions, and COTable commands.
- Context MOB formats: `SVGADXInputAssemblyMobFormat`, `SVGADXContextMobFormat`, and `SVGADXShaderIfaceMobFormat` define host/guest shared backing layouts for DX context state.

## Control Flow

The file is declarative. Runtime flow is command submission: vmwgfx emits command IDs from `svga3d_cmd.h` and payloads from this header to mutate DX context state, bind resources, issue draws/dispatches, manage queries, and copy data. Context MOB structures provide a persistent snapshot format for binding, readback, invalidation, and recovery of complex DX pipeline state.

## State and Persistence Behavior

Most structures represent persistent virtual GPU state: context bindings, shader/interface state, cotables, view objects, state objects, query results, stream-output declarations, UAV bindings, and resource views. The header also defines transient operation payloads for draw, dispatch, clear, copy, update, and transfer commands. State lives in host resources and guest MOBs; packed structures are the serialized representation.

## Dependencies and Integration Points

- Includes `svga_reg.h`, `svga3d_limits.h`, and `svga3d_types.h`.
- Integrated by vmwgfx DX context, cotable, shader, surface/view, binding, stream-output, and execbuf validation code.
- Shares object type and command ID contracts with `svga3d_cmd.h`, `svga3d_types.h`, and host SVGA DX implementation.

## Risks and Edge Cases

- Many structures are packed ABI payloads with mixed 8/16/32-bit fields. Padding or signedness changes can break host compatibility.
- Several command families use implicit arrays following a fixed header, controlled by counts such as number of views, samplers, viewports, scissor rects, stream-output entries, or shader class instances.
- Context MOB formats contain large fixed arrays and reserved padding. Size drift or incomplete initialization can leak stale state to the host or corrupt context restore.
- Resource view descriptors are unions keyed by resource type/format. Validators must ensure the active union arm matches the surface/resource type.
- UAV and DX11.1 limits differ from earlier DX limits; capability gating must be precise.

## Test Signals

- ABI tests should check `sizeof` and offsets for packed command and MOB format structures.
- Execbuf validation should cover count-driven variable payloads, invalid object IDs, unsupported command IDs under lower caps, view/resource type mismatches, and copy/transfer bounds.
- Context save/restore and readback/invalidate tests should compare `SVGADXContextMobFormat` contents across bind/readback cycles.
- Rendering tests should cover draw/dispatch, queries, predication, stream output, UAVs, shader interfaces, and staging copies on supported virtual hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_dx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_limits.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_limits.h

## Purpose

`svga3d_limits.h` centralizes compile-time SVGA3D hardware and protocol limits for contexts, surfaces, render targets, UAVs, shaders, texture units, lights, surface sizes, arrays, samples, and sandbox data sizes.

## Important APIs, Types, and Functions

- Context/surface limits: `SVGA3D_HB_MAX_CONTEXT_IDS`, `SVGA3D_HB_MAX_SURFACE_IDS`, and `SVGA3D_HB_MAX_SURFACE_SIZE`.
- DX render/UAV limits: `SVGA3D_DX_MAX_RENDER_TARGETS`, DX11/DX11.1 UAV limits, and simultaneous RT/UAV aliases.
- Shader limits: maximum shader IDs, simultaneous shaders, shader memory bytes/words, and compute thread groups.
- Fixed-function/texture limits: texture units, lights, clip planes, texture coordinates, surface faces, vertex arrays, primitive ranges, and samples.
- Surface array limits: SM4 and SM5 array sizes with `SVGA3D_MAX_SURFACE_ARRAYSIZE`.
- Sandbox data-size constants for SBX/DVM paths.

## Control Flow

There is no runtime flow. Other headers and driver validators use these macros for array sizing, command validation, and capability clamping.

## State and Persistence Behavior

No state is owned here. The macros influence structure sizes and accepted resource dimensions throughout the driver.

## Dependencies and Integration Points

- Uses byte conversion macros from `vm_basic_types.h` indirectly in includers.
- Included by `svga3d_cmd.h`, `svga3d_dx.h`, and the aggregate `svga3d_reg.h`.
- Tightly coupled to fixed array lengths in command/context structures.

## Risks and Edge Cases

- Changing a limit can change packed ABI structure sizes when used in arrays, especially DX context MOB layouts.
- Some limits are aliases of the latest supported generation. Validators may need to use lower capability-specific limits on older virtual hardware.
- Large constants must be checked for overflow when multiplied by element sizes or page counts.

## Test Signals

- Compile-time checks should verify ABI structure sizes after any limit change.
- Runtime validation tests should cover boundary values at max, max plus one, and older-capability limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_reg.h

## Purpose

`svga3d_reg.h` is an aggregate include for SVGA3D virtual hardware definitions. It gathers base SVGA registers, 3D types, limits, command payloads, DX payloads, and device capabilities behind one guarded header.

## Important APIs, Types, and Functions

- Includes `svga_reg.h`, `svga3d_types.h`, `svga3d_limits.h`, `svga3d_cmd.h`, `svga3d_dx.h`, and `svga3d_devcaps.h`.
- Provides no independent structs, enums, macros, or functions beyond its include guard.

## Control Flow

There is no runtime or compile-time branching other than normal include expansion.

## State and Persistence Behavior

The header owns no state. It shapes compile dependencies by exposing the full SVGA3D ABI set to consumers.

## Dependencies and Integration Points

- Used by code that wants the complete SVGA3D ABI without including individual protocol headers.
- Because it includes command and DX headers, it can increase rebuild scope and namespace exposure.

## Risks and Edge Cases

- Include-order changes can expose circular dependency issues among low-level ABI headers.
- Aggregating many declarations can hide which smaller header a source actually depends on.
- Any conflicting macro/type in one included header becomes visible to all aggregate consumers.

## Test Signals

- Full vmwgfx builds are the main signal for aggregate include consistency.
- Header self-containment tests should compile a trivial source including only `svga3d_reg.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_surfacedefs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_surfacedefs.h

## Purpose

`svga3d_surfacedefs.h` describes SVGA3D surface formats in a static metadata table. It maps each `SVGA3dSurfaceFormat` to block/category flags, block dimensions, bytes per block, pitch granularity, and channel bit-depth/offset information.

## Important APIs, Types, and Functions

- `SVGA3dBlockDesc`: bitmask taxonomy for color, depth, stencil, compressed, planar YUV, typeless, integer, normalized, sRGB, floating point, bump, BCn, and compound channel descriptions.
- `SVGA3dChannelDef`: unioned channel byte fields for color, bump, YUV, luminance, depth, stencil, and exponent interpretations.
- `SVGA3dSurfaceDesc`: per-format descriptor containing format ID, block descriptor, block size, bytes per block, pitch bytes per block, bit depths, and bit offsets.
- `g_SVGA3dSurfaceDescs[]`: static const descriptor array indexed in the same order as `SVGA3dSurfaceFormat`.
- `STATIC_CONST`: platform-dependent storage-class macro, `static const` in the kernel/GNU path.

## Control Flow

There is no executable control flow. Runtime consumers index or search `g_SVGA3dSurfaceDescs` to validate formats, compute pitches/sizes, and understand channel layout.

## State and Persistence Behavior

The descriptor table is immutable static data. It does not allocate or mutate state; consumers derive transient validation and size calculations from it.

## Dependencies and Integration Points

- Includes `svga3d_types.h` for format IDs and size types.
- Integrates with surface creation validation, format capability checks, pitch/size calculations, and copy/transfer code.
- Must stay synchronized with `SVGA3dSurfaceFormat` enum values and devcap format constants.

## Risks and Edge Cases

- Table ordering must match enum numeric values. Missing or reordered entries can make every later format decode incorrectly.
- Compressed and planar formats use block and pitch units that differ from simple pixel formats; size calculations must use `blockSize`, `bytesPerBlock`, and `pitchBytesPerBlock` correctly.
- Unioned channel names make descriptor interpretation context-dependent.
- The `STATIC_CONST` macro has cross-platform baggage; in kernel builds it should remain static to avoid duplicate global definitions.

## Test Signals

- Static tests should verify `ARRAY_SIZE(g_SVGA3dSurfaceDescs) == SVGA3D_FORMAT_MAX` and descriptor `.format` matches its index where expected.
- Format-size tests should cover RGB, depth/stencil, compressed BC, NV12/YV12 planar, typeless, and buffer formats.
- Validation tests should compare descriptor properties against devcap-supported format flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_surfacedefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_types.h

## Purpose

`svga3d_types.h` is the foundational SVGA3D type and enum map. It defines IDs, geometry primitives, resource types, surface formats and flags, render and texture state enums, shader/query types, transfer/copy boxes, MOB/cotable identifiers, multisample settings, and query-result layouts used by the rest of the vmwgfx SVGA3D ABI.

## Important APIs, Types, and Functions

- Basic IDs and geometry: `SVGA3dSurfaceId`, `SVGA3dCopyRect`, `SVGA3dCopyBox`, `SVGA3dRect`, `SVGA3dBox`, `SVGA3dSignedBox`, `SVGA3dSize`, `SVGA3dSurfaceImageId`, and `SVGA3dSubSurfaceId`.
- `SVGA3dSurfaceFormat`: large format enum spanning legacy, DX, compressed, typeless, YUV, depth/stencil, integer, normalized, floating point, and buffer formats.
- Surface flags: 64-bit `SVGA3dSurfaceAllFlags` split into `Surface1`/`Surface2`, plus disallowed masks for host-backed, present, 2D, screen target, buffer, multisample, staging, logicops, DX-only, and SM5 cases.
- Render/texture/pipeline enums: render state names, blend/cull/fill/shade/compare/stencil/fog/primitive/transform/texture-stage enums, render targets, texture filters, addressing, and texture operations.
- Shader/query/cotable/MOB types: shader types and constants, query types/results, object-table types, cotable types, MOB formats, multisample pattern/quality, and frame update type.
- Logic operation and transfer definitions: logic op IDs, ROP3 values, transfer/copy types, and query result unions.

## Control Flow

The header has no executable control flow. Its enums and structs drive validation and serialization in command construction, resource creation, state tracking, and host capability interpretation.

## State and Persistence Behavior

The types model persistent virtual GPU objects and state but do not own storage. Persistent state appears in surfaces, contexts, shaders, queries, cotables, MOBs, and command buffers managed by vmwgfx and the host.

## Dependencies and Integration Points

- Includes `vm_basic_types.h` for VMware fixed-width integer aliases and constants.
- Included by command, DX, devcap, and surface-definition headers.
- Numeric values and bit masks are host ABI, so they must align with the VMware SVGA virtual device implementation.

## Risks and Edge Cases

- Enum values are serialized to the device. Renumbering or removing dead slots breaks ABI compatibility.
- Surface flags use 64-bit constants and masks; accidental 32-bit truncation can lose high feature bits such as multisample, UAV, raw views, structured buffers, or staging copy.
- Disallowed masks encode subtle capability rules. Validation must apply the mask appropriate to resource type and command generation.
- Geometry and size fields are unsigned in many places; arithmetic for boxes, pitches, mip levels, and array layers must guard overflow and underflow.
- Query-result unions are untagged and require the query type to choose the right interpretation.

## Test Signals

- ABI tests should check representative enum numeric values, surface flag width, and struct sizes.
- Resource validation tests should cover invalid formats, incompatible flag combinations, buffer stride limits, staging masks, multisample restrictions, and DX/SM feature gating.
- Query tests should cover each query type's result layout and state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_escape.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_escape.h

## Purpose

`svga_escape.h` defines VMware-specific SVGA escape command namespace values and the packed payload for fullscreen hint escape commands.

## Important APIs, Types, and Functions

- `SVGA_ESCAPE_NSID_VMWARE` and `SVGA_ESCAPE_NSID_DEVEL`: namespace identifiers for escape commands.
- `SVGA_ESCAPE_VMWARE_MAJOR_MASK`, `SVGA_ESCAPE_VMWARE_HINT`, and `SVGA_ESCAPE_VMWARE_HINT_FULLSCREEN`: VMware hint command IDs.
- `SVGAEscapeHintFullscreen`: packed payload with command ID, fullscreen flag, and monitor position `{ x, y }`.

## Control Flow

The header has no executable flow. Driver code emits an SVGA FIFO escape command with the VMware namespace, size, and this packed payload when it needs to send fullscreen hints to the host.

## State and Persistence Behavior

Fullscreen hint state is interpreted by the host. The header defines only the serialized message format and owns no persistent state.

## Dependencies and Integration Points

- Uses VMware fixed-width aliases from the broader include environment.
- Integrates with base FIFO `SVGA_CMD_ESCAPE` definitions in `svga_reg.h` and host UI/display hint handling.

## Risks and Edge Cases

- The struct is explicitly packed; any unpacked copy would change the host-visible wire layout.
- Namespace and command values must not collide with other escape families.
- Monitor coordinates are signed; callers should preserve negative positions for multi-monitor layouts.

## Test Signals

- Compile-time size checks for `SVGAEscapeHintFullscreen`.
- Escape construction tests should verify namespace, command, size, fullscreen flag, and signed coordinates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_escape.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_overlay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_overlay.h

## Purpose

`svga_overlay.h` defines legacy VMware SVGA video-overlay escape formats, FourCC identifiers, stream register update/flush payloads, and packed FIFO escape structures.

## Important APIs, Types, and Functions

- `VMWARE_FOURCC_YV12`, `VMWARE_FOURCC_YUY2`, `VMWARE_FOURCC_UYVY` and `SVGAOverlayFormat`: supported overlay video formats.
- `SVGA_VIDEO_COLORKEY_MASK`: color-key bit mask.
- `SVGA_ESCAPE_VMWARE_VIDEO`, `_SET_REGS`, and `_FLUSH`: overlay escape command IDs.
- `SVGAEscapeVideoSetRegs` and `SVGAEscapeVideoFlush`: non-packed logical payloads with stream ID and register/value items.
- `SVGAFifoEscapeCmdVideoBase`, `SVGAFifoEscapeCmdVideoFlush`, `SVGAFifoEscapeCmdVideoSetRegs`, and `SVGAFifoEscapeCmdVideoSetAllRegs`: packed FIFO escape payload layouts.

## Control Flow

There is no executable logic. Runtime overlay code constructs SET_REGS escapes with one or more register/value items to update stream state, then emits FLUSH escapes when needed. The all-register payload uses `SVGA_VIDEO_NUM_REGS` from `svga_reg.h`.

## State and Persistence Behavior

Overlay stream state persists in the virtual device/host overlay unit. The header defines message formats for mutating that state but stores none itself.

## Dependencies and Integration Points

- Includes `svga_reg.h` for video register IDs/counts and base types.
- Integrated by vmwgfx overlay support and the base SVGA escape FIFO command path.

## Risks and Edge Cases

- Several structs use one-element trailing arrays for variable numbers of register updates. Callers must allocate enough bytes for the actual item count.
- Packed FIFO structures must match host expectations exactly.
- Overlay support is legacy; modern display paths may not exercise it, increasing regression risk.
- Color-key values should be masked to 24 bits.

## Test Signals

- Overlay command construction tests should cover single-register, all-register, and flush payload sizes.
- Size/offset checks should cover packed FIFO escape structs.
- Functional tests should verify YV12/YUY2/UYVY stream setup, color keying, and destination screen selection where overlay support is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_reg.h

## Purpose

`svga_reg.h` defines the base VMware SVGA II virtual hardware register, FIFO, command-buffer, screen, cursor, GMR, overlay, capability, and memory-size ABI. It is the non-3D foundation used by vmwgfx before and alongside SVGA3D command submission.

## Important APIs, Types, and Functions

- Device IDs and ports: `SVGA_ID_*`, index/value/BIOS/IRQ ports, IRQ flags, cursor limits, and register enum from `SVGA_REG_ID` through extended cursor/dirty/fence registers.
- Guest memory types: `SVGAMobId`, `SVGAGuestMemDescriptor`, `SVGAGuestPtr`, `SVGAGuestImage`, GMR constants, and image format descriptors.
- Command buffer ABI: maximum sizes, contexts, statuses, flags, packed `SVGACBHeader`, and device-context control commands.
- Capabilities: `SVGA_CAP_*`, `SVGA_CAP2_*`, backdoor capability types, FIFO register enum, FIFO caps/flags, and FIFO capability record structures.
- Overlay/video and screen state: overlay unit registers, `SVGAOverlayUnit`, display topology, screen flags, `SVGAScreenObject`, and screen DMA status values.
- FIFO 2D commands: `SVGAFifoCmdId` and packed payloads for update, rect copy, cursor definitions, fence, escape, screen define/destroy, GMRFB blits, annotations, GMR2 define/remap, and memory sizing constants.

## Control Flow

The header is declarative. Driver runtime flow uses register indices to probe device version/capabilities and configure memory/FIFO state, then writes FIFO commands with the packed payloads defined here. Command buffer fields let the driver submit larger command streams and observe completion/error/preemption status through volatile header fields.

## State and Persistence Behavior

The virtual device persists register values, FIFO positions/status, guest memory regions, command-buffer status, screen objects, overlay unit state, cursor state, and fences. This header defines the serialized and MMIO/register-visible forms of that state but does not implement accessors.

## Dependencies and Integration Points

- Includes `vm_basic_types.h`.
- Used across vmwgfx driver initialization, FIFO management, IRQ/fence handling, GMR/MOB memory code, KMS screen target code, overlay code, command-buffer submission, and SVGA3D headers.
- Escape command structures in `svga_escape.h` and `svga_overlay.h` build on `SVGA_CMD_ESCAPE` and video register constants from this file.

## Risks and Edge Cases

- Packed structures and enum numbers are host ABI and must remain stable.
- `volatile` command-buffer status fields require correct memory ordering in runtime code outside this header.
- FIFO and command size constants cap untrusted command data; validators must enforce them before writing to shared FIFO memory.
- 32-bit and 64-bit guest physical/page fields coexist. Callers must select the right descriptor form for capabilities and avoid truncation.
- Screen, overlay, and cursor dimensions need bounds checks against max constants to avoid host rejection or memory overrun.

## Test Signals

- Probe tests should validate version negotiation, register availability, capability bits, FIFO register layout, and IRQ mask/status behavior.
- Command construction tests should check packed sizes and payloads for base 2D commands, escapes, GMR2 remaps, and screen objects.
- Command-buffer tests should cover status transitions, queue-full/error/preempted handling, context flags, MOB vs physical-address submissions, and max-size enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/vm_basic_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/vm_basic_types.h

## Purpose

`vm_basic_types.h` provides VMware fixed-width integer aliases, physical/page-number typedefs, common constants, byte conversion helpers, and mksGuestStats shared-memory descriptor types used by vmwgfx protocol headers.

## Important APIs, Types, and Functions

- Fixed-width aliases: `uint32`, `int32`, `uint64`, `uint16`, `int16`, `uint8`, `int8`, and `Bool`.
- Physical/page types: `PA`, `PPN`, `PPN32`, `PPN64`, and `INVALID_PPN64`.
- Limits and helpers: `MAX_UINT64`, `MAX_UINT32`, `MAX_UINT16`, `CONST64U`, `MBYTES_SHIFT`, and `MBYTES_2_BYTES`.
- mksGuestStats counters: `MKSGuestStatCounter`, `MKSGuestStatCounterTime`, flags, and aligned `MKSGuestStatInfoEntry`.
- `MKSGuestStatInstanceDescriptor`: page-based host-visible descriptor containing virtual-address starts, section lengths, arrays of pinned page numbers for stats/info/strings, and a description buffer.

## Control Flow

The header has no executable control flow. It standardizes type widths and data layout for other headers and for optional mksGuestStats communication.

## State and Persistence Behavior

The type aliases have no state. mksGuestStats descriptors and counters are persistent shared data allocated by runtime driver instrumentation code: counters are atomic64-backed, and the instance descriptor describes pinned pages that the host can walk. The comments note that the host does not acknowledge descriptor changes, so compatibility failures affect stats logging rather than core guest operation.

## Dependencies and Integration Points

- Includes Linux kernel, MM, and page headers for fixed-width kernel types, `PFN_UP`, atomics, and page sizing.
- Used by all SVGA/SVGA3D protocol headers for consistent ABI widths.
- Integrates with `CONFIG_DRM_VMWGFX_MKSSTATS` driver code that exposes guest stats to the host.

## Risks and Edge Cases

- VMware aliases must remain fixed-width; substituting C native types would make packed protocol structures architecture-dependent.
- `MBYTES_2_BYTES` name takes a count of megabytes despite the parameter name `_nbytes`; misuse can over/under-size resources.
- mksGuestStats structures contain guest virtual addresses and pinned page arrays. Runtime code must ensure pages remain pinned and lengths stay within the maximum page arrays.
- `MKSGuestStatInfoEntry` is explicitly 32-byte aligned; changing alignment affects host parsing.

## Test Signals

- Compile-time checks should verify alias sizes, `MKSGuestStatInfoEntry` alignment, and descriptor page-array capacity calculations.
- mksGuestStats tests should cover descriptor initialization, atomic counter updates, maximum stat counts, string/info section lengths, and disabled instrumentation builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/vm_basic_types.h -->
