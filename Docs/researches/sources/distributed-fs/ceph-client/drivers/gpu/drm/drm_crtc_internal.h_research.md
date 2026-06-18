# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_internal.h

Purpose: Private DRM KMS core header collecting internal prototypes for mode setting, ioctls, mode objects, connectors, CRTCs, encoders, planes, framebuffers, dumb buffers, properties, color management, EDID, atomic UAPI, bridge detachment, and optional DRM panic support. It is the internal linkage map for the DRM module, not a driver-facing API.

Important APIs/types/functions: Declares CRTC helpers (`drm_mode_crtc_set_obj_prop`, `drm_crtc_check_viewport`, register/unregister, force-disable, fence creation), mode-config lifecycle, resources ioctl, dumb-buffer ioctls, gamma ioctls, property/blob ioctls and validation, mode-object add/find/register/unregister/property enumeration, encoder/connector/plane ioctls and registration helpers, framebuffer creation/release/add/remove/dirty helpers, atomic debugfs and UAPI setters/getters, `__drm_atomic_helper_disable_plane`, `__drm_atomic_helper_set_config`, `drm_atomic_print_new_state`, EDID override and CTA SAD helpers, DisplayID/EDID extension lookup, firmware EDID loading stub, and DRM panic hooks.

Control flow: There is no executable flow. The header defines which symbols are callable across compilation units inside the DRM core and selects stubs for optional features with `#ifdef CONFIG_DEBUG_FS`, `CONFIG_DRM_LOAD_EDID_FIRMWARE`, and `CONFIG_DRM_PANIC`.

State and persistence behavior: No state is stored here. The prototypes expose operations over DRM device-owned state such as mode_config lists, object id registries, framebuffer lists, property blobs, connector/CRTC/plane atomic state, and optional panic registration.

Dependencies and integration points: Integrates nearly all core KMS implementation files and ioctl handlers. It forward-declares many DRM and kernel structs to avoid pulling large public headers into every implementation file. It also bridges optional subsystems: debugfs, firmware EDID, and panic display.

Risks: This file is a high-blast-radius contract: changing a prototype affects multiple core files and sometimes ioctl behavior. Because it is internal, there is less ABI stability pressure, but the functions it declares often back UAPI ioctls. Conditional stubs must match real implementations exactly enough that non-enabled builds compile and preserve expected no-op semantics.

Test signals: Full DRM build coverage across configs with and without `CONFIG_DEBUG_FS`, `CONFIG_DRM_LOAD_EDID_FIRMWARE`, and `CONFIG_DRM_PANIC`; ioctl smoke tests for mode resources, CRTC, connector, plane, framebuffer, property, dumb-buffer, gamma, and atomic paths; and sparse/build warnings for mismatched prototypes.
