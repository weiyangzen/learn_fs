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
