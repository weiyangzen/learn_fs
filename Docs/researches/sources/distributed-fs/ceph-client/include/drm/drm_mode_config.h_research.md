# sources/distributed-fs/ceph-client/include/drm/drm_mode_config.h

Purpose: declares the central KMS mode-configuration object and global driver callbacks for framebuffer creation, mode validation, atomic checking/commit, and optional atomic state subclassing.

Important APIs and types: `struct drm_mode_config_funcs` contains `fb_create`, `get_format_info`, device-wide `mode_valid`, `atomic_check`, `atomic_commit`, and optional `atomic_state_alloc/clear/free`. `struct drm_mode_config` owns the global modeset mutex, connection lock, legacy acquire context, IDR locks and ID spaces, framebuffer list, connector list/free work, encoder/plane/colorop/CRTC/property/private-object lists, display size limits, output polling state, blob property lock/list, standard property pointers, dumb-buffer preferences, quirk flags, async flip and modifier flags, cursor limits, suspend atomic state, and helper-private callbacks. Initialization/cleanup APIs are `drmm_mode_config_init()`, deprecated wrapper `drm_mode_config_init()`, `drm_mode_config_reset()`, and `drm_mode_config_cleanup()`.

Control flow: drivers initialize mode config during probe, fill limits and callback pointers, create KMS objects and properties under this global registry, then expose ioctls. Userspace framebuffer creation calls `fb_create`; mode enumeration and atomic commits consult validation callbacks; atomic commits run `atomic_check` then `atomic_commit`; suspend/resume helpers stash state in `suspend_state`.

State and persistence behavior: `drm_mode_config` persists for the DRM device lifetime. It tracks global object IDs, object lists, property objects, blob properties, framebuffer objects, output polling work, and suspend state. Some lists are immutable after init, while connectors and framebuffers have dedicated locks/free work.

Dependencies and integration points: integrates with modeset locks, IDR/IDA, workqueues, framebuffer and format info, atomic state, connector polling, writeback, color management, TV/HDMI/HDCP/HDR properties, and managed cleanup via `drmm_mode_config_init()`.

Risks: lock layering is complex: global mutex, `connection_mutex`, IDR mutex, framebuffer lock, blob lock, connector spinlock, and panic raw spinlock protect different subsets. Atomic callbacks have strict error-code contracts; `atomic_commit` must not return validation-only errors such as `-EINVAL` or acquire new modeset locks. Modifier and legacy AddFB quirks affect userspace ABI.

Test signals: mode-config init/cleanup, framebuffer creation with modifiers and legacy quirks, atomic check/commit success and failure codes, connector hotplug polling, property/blob lifetime, suspend/resume state restore, connector free work, object ID allocation, and lockdep coverage for modeset locks.
