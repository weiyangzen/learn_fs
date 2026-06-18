# sources/distributed-fs/ceph-client/include/uapi/drm/drm_mode.h

## Purpose

`drm_mode.h` is the central DRM/KMS UAPI model for display mode setting. It defines display mode timings, CRTC/encoder/connector/plane discovery, framebuffer creation and dirty tracking, cursor operations, gamma and color-management data, HDR metadata, page flips, dumb buffers, atomic commits, format modifier blobs, blob properties, leasing, damage rectangles, and ARGB packing helpers.

## Important APIs, Types, And Constants

Core mode data is represented by `struct drm_mode_modeinfo` and flags such as `DRM_MODE_TYPE_*`, sync/scan/stereo/aspect flags, content type, DPMS, scaling, dithering, dirty, link status, panel type, rotation/reflection, and content-protection values. Resource and object discovery uses `drm_mode_card_res`, `drm_mode_get_connector`, `drm_mode_get_encoder`, `drm_mode_get_plane`, and `drm_mode_get_plane_res`.

Properties use `DRM_MODE_PROP_*`, `drm_mode_get_property`, `drm_mode_obj_get_properties`, `drm_mode_obj_set_property`, object type IDs, and `drm_mode_property_enum`. Framebuffer and plane paths use legacy `drm_mode_fb_cmd`, modern `drm_mode_fb_cmd2`, dirty clips, `drm_format_modifier_blob`, and `drm_format_modifier`. CRTC operations include `drm_mode_crtc`, `drm_mode_set_plane`, cursor structs, LUT structs, and page-flip structs. Atomic and leasing APIs are `drm_mode_atomic`, `DRM_MODE_ATOMIC_*`, and the create/list/get/revoke lease structs. Color and HDR APIs include CTM, LUT, colorop, HDR infoframe, and output metadata structures.

## Control Flow

Most discovery is count-first: userspace calls an ioctl with zero or temporary counts, allocates arrays, then retries until counts stabilize. Legacy modesetting creates or imports a GEM object, creates a framebuffer, sets a CRTC or plane, then page-flips. Atomic modesetting packs object IDs, property counts, property IDs, and values into `drm_mode_atomic`, optionally validates with `TEST_ONLY`, and commits blocking or nonblocking with optional events. Connector force-probing is triggered by `count_modes == 0` for DRM master clients and can be slow.

## State And Persistence

The header defines handles for kernel-managed objects: framebuffer IDs, blob IDs, object/property IDs, GEM handles, and lessee IDs. User-created blobs persist until destroyed or FD cleanup. Framebuffers and dumb buffers persist until closed/destroyed; asynchronous commits require userspace to track completion events and object lifetimes.

## Dependencies And Integration Points

It includes Linux bit/constant helpers and `drm.h`, and relies on `drm_fourcc.h` format/modifier values by contract. It is consumed by all KMS drivers, display servers, compositors, libdrm, Mesa GBM, IGT, and driver-specific APIs that reuse DRM format, rotation, event, and framebuffer semantics.

## Risks

Races around hotplug require retry loops. Forced connector probing can block or flicker. `drm_mode_fb_cmd2` has subtle rules: up to four planes, identical modifiers across planes, and zero can mean both unused and valid offset/linear modifier depending on context. Atomic commits are sensitive to array packing, `ALLOW_MODESET`, event CRTC inclusion, and blob lifetime. Fixed-point source coordinates, sign-magnitude CTMs, HDR unit scaling, and ARGB bit-depth conversion are common bug surfaces.

## Test Signals

Relevant tests include IGT KMS discovery and hotplug retry, connector force-probe behavior, legacy and atomic page flips, atomic `TEST_ONLY`, dumb-buffer lifecycle, framebuffer modifier validation, `IN_FORMATS` blob parsing, property enumeration and setting, color/HDR blob validation, lease create/revoke/list behavior, damage clips, and 32/64-bit ABI layout checks.
