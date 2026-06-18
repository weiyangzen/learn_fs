# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_ioc32.c

## Purpose

`drm_ioc32.c` implements the 32-bit userspace compatibility ioctl layer for DRM core ioctls on 64-bit kernels. It translates legacy pointer-sized structures to native structures for the subset of DRM core ioctls that need explicit marshalling, then forwards handling to `drm_ioctl_kernel()` or `drm_ioctl()`.

## Important APIs, Types, And Functions

The exported entry point is `drm_compat_ioctl()`. Explicit compat handlers include `compat_drm_version()`, `compat_drm_getunique()`, `compat_drm_setunique()`, `compat_drm_getclient()`, `compat_drm_getstats()`, `compat_drm_wait_vblank()`, and x86-only `compat_drm_update_draw()` and `compat_drm_mode_addfb2()`. The file defines 32-bit variants of `drm_version`, `drm_unique`, `drm_client`, `drm_stats`, `drm_wait_vblank`, and x86 packed `drm_update_draw`/`drm_mode_fb_cmd2` structures.

`drm_compat_ioctls[]` maps core ioctl numbers to handlers with `DRM_IOCTL32_DEF()`. Missing entries intentionally fall back to `drm_ioctl()` on the assumption that the ioctl layout is compat-safe.

## Control Flow

`drm_compat_ioctl()` extracts `DRM_IOCTL_NR(cmd)`, bounds-checks against `drm_compat_ioctls[]`, applies `array_index_nospec()`, and either dispatches an explicit compat function or falls back to the normal DRM ioctl path. Handlers copy compact 32-bit structures from userspace, populate native kernel structures with `compat_ptr()` pointer expansion, call the corresponding native DRM core handler through `drm_ioctl_kernel()`, then copy result fields back.

`compat_drm_wait_vblank()` converts request fields into native `union drm_wait_vblank`, calls `drm_wait_vblank_ioctl()`, and copies reply sequence/time fields back even when the native ioctl returns an error. `compat_drm_mode_addfb2()` handles an x86 packed layout by copying fields up to `modifier`, then separately copying the modifier array into the native request before invoking `drm_mode_addfb2()`.

## State And Persistence

This file does not own persistent state. It temporarily stores marshalled ioctl arguments on the kernel stack. Persistent effects are delegated to the native DRM ioctl handlers: version strings, bus IDs, client authentication reporting, vblank waits, and framebuffer creation. The compat dispatch table is static read-only after initialization.

## Dependencies And Integration Points

The file depends on Linux compat pointer helpers, nospec array-index hardening, usercopy helpers, DRM file/device/print headers, `drm_crtc_internal.h`, and `drm_internal.h`. It integrates directly with `drm_ioctl_kernel()` for permission-checked native calls and with the normal `drm_ioctl()` fallback for compatible layouts. Driver-private ioctls are not translated here unless they share normal layouts; drivers with incompatible private ioctls must wrap this path themselves.

## Risks And Edge Cases

The fallback assumption can be wrong for ioctl structs with embedded pointers or different packing, especially driver-private commands. `compat_drm_setunique()` is intentionally dead and returns `-EINVAL`, preserving modern DRM behavior. `compat_drm_getstats()` clears the defunct stats structure instead of querying real stats. Type width truncation is deliberate for old ABI fields such as pid/uid/iocs. The x86-only packed ADD_FB2 handling is architecture-specific; other architectures rely on native compatibility.

## Test Signals

Test with 32-bit userspace on a 64-bit kernel using `DRM_IOCTL_VERSION`, `GET_UNIQUE`, `GET_CLIENT`, `GET_STATS`, `WAIT_VBLANK`, and x86 `MODE_ADDFB2`. Useful negative tests include unsupported SET_UNIQUE, invalid user pointers, short buffers, no explicit compat-table entry fallback, and render-node permission propagation through `drm_ioctl_kernel()`.
