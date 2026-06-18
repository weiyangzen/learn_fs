# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioctl.c

## Purpose

`drm_ioctl.c` is the DRM core ioctl dispatcher and implementation home for several legacy and generic core ioctls. It exposes version/bus-id/client/capability operations, client capability negotiation, no-op/invalid-op helpers for deprecated ioctls, core ioctl permission checks, core ioctl descriptor table, driver-private ioctl dispatch, userspace argument marshalling, and permission flag lookup.

## Important APIs, Types, And Functions

Important exported functions are `drm_getunique()`, `drm_getclient()`, `drm_noop()`, `drm_invalid_op()`, `drm_version()`, `drm_ioctl_kernel()`, `drm_ioctl()`, and `drm_ioctl_flags()`. Important internal helpers are `drm_unset_busid()`, `drm_set_busid()`, `drm_getstats()`, `drm_getcap()`, `drm_setclientcap()`, `drm_setversion()`, `drm_copy_field()`, `drm_validate_value_string()`, `drm_set_client_name()`, and `drm_ioctl_permit()`.

The central table is `drm_ioctls[]`, built with `DRM_IOCTL_DEF()`. It maps core ioctl command numbers to functions and access flags such as `DRM_RENDER_ALLOW`, `DRM_AUTH`, `DRM_MASTER`, and `DRM_ROOT_ONLY`. The table covers version/auth, master, vblank, GEM, PRIME, KMS resource/property/framebuffer/atomic/dumb-buffer operations, syncobj operations, CRTC sequence operations, and DRM lease ioctls.

## Control Flow

Simple core ioctls first marshal user buffers through `drm_ioctl()` and then operate on DRM state. `drm_getunique()` returns the current master's bus ID under `dev->master_mutex`. `drm_setversion()` validates the requested DRM interface and driver versions, updates `dev->if_version`, and for interface minor >= 1 populates the master's bus ID through PCI or `dev->unique`. `drm_getclient()` is hollowed out to report only the current client's authentication state for index zero. `drm_getcap()` and `drm_setclientcap()` implement feature negotiation, with render-safe caps handled before KMS-only caps.

`drm_ioctl()` validates the ioctl type, chooses either a driver-private descriptor from `dev->driver->ioctls` or a core descriptor from `drm_ioctls[]`, hardens the index with `array_index_nospec()`, computes input/output/kernel buffer sizes from the userspace command and the trusted descriptor command, copies input from userspace, zero-extends to the kernel struct size, calls `drm_ioctl_kernel()`, and copies output back. `drm_ioctl_kernel()` updates file ownership for passed file descriptors, rejects unplugged devices, applies `drm_ioctl_permit()`, and invokes the handler.

## State And Persistence

Persistent state touched here includes `drm_master.unique`, `drm_master.unique_len`, `dev->if_version`, per-file capability booleans (`stereo_allowed`, `universal_planes`, `atomic`, `aspect_ratio_allowed`, `writeback_connectors`, `supports_virtualized_cursor_plane`, `plane_color_pipeline`), and `file_priv->client_name`. The ioctl dispatcher itself keeps only stack or temporary heap buffers for ioctl arguments. Capabilities returned from `drm_getcap()` reflect driver feature flags and `mode_config` fields.

## Dependencies And Integration Points

The file depends on Linux usercopy, nospec, PCI device checks, capabilities, and DRM auth, CRTC/KMS, driver, file, print, PRIME, GEM, syncobj, lease, and vblank internals. It is the normal `file_operations.unlocked_ioctl` path for DRM drivers. Driver-private ioctls integrate by publishing `drm_driver.ioctls` and `num_ioctls`; core permission and marshalling behavior applies to both core and private commands.

## Risks And Edge Cases

The GET_UNIQUE/SET_VERSION behavior is constrained by old libdrm open-by-name and open-by-busid semantics; returning a bus ID too early can break old userspace. `drm_set_busid()` does not return `-ENOMEM` if `kstrdup(dev->unique)` fails for non-PCI devices, leaving `unique_len` zero. `drm_ioctl()` copies output even if the handler failed, then reports `-EFAULT` if output copy fails, which can mask the original handler error. Permission flags are central security boundaries: render nodes require `DRM_RENDER_ALLOW`, master ioctls require current master, and root-only ioctls require `CAP_SYS_ADMIN`. The atomic client cap has a special Xorg process-name compatibility rejection. `drm_set_client_name()` rejects non-graphical ASCII and embedded NUL by comparing `strlen()` to the requested length.

## Test Signals

Important tests include ioctl type rejection, invalid core and driver ioctl numbers, stack versus heap argument buffers, zero-extension of shorter user structs, permission failures for render/auth/master/root-only calls, unplugged-device `-ENODEV`, SET_VERSION bus-id behavior on PCI and platform devices, GET_UNIQUE compatibility, GET_CAP values for render-only and KMS drivers, client cap negotiation, SET_CLIENT_NAME validation, syncobj/GEM/PRIME dispatch, lease ioctl dispatch, and driver-private ioctl bounds hardening.
