# sources/distributed-fs/ceph-client/include/drm/drm_panic.h

## Purpose
`drm_panic.h` exposes the minimal DRM interfaces needed to draw a panic screen into a scanout buffer from panic context. It describes the scanout buffer layout and locking rules for state that panic printing may safely touch.

## Important APIs, types, and functions
`struct drm_scanout_buffer` carries format, `iosys_map` mappings, optional page array, dimensions, per-plane pitch, optional `set_pixel` callback for special layouts, and private callback data. With `CONFIG_DRM_PANIC`, `drm_panic_trylock`, `drm_panic_lock`, and `drm_panic_unlock` map to raw spinlock irqsave operations on `drm_device.mode_config.panic_lock`. Optional QR helpers are declared under `CONFIG_DRM_PANIC_SCREEN_QR_CODE`.

## Control flow
Panic code tries to acquire the panic lock and aborts drawing if it cannot. While held, it may access software state protected by the lock and invariant state between DRM device register/unregister boundaries. Pixel writing uses either the driver `set_pixel` hook, linear mappings, or per-page panic-safe kmap. Unlock restores IRQ flags.

## State and persistence
The header itself stores no state beyond the scanout buffer descriptor supplied by a driver. Persistent assumptions are deliberately narrow: plane lists and invariant plane state are considered stable only within device registration, while dynamic hardware access must be explicitly protected.

## Dependencies and integration points
It depends on DRM device/mode config locking, fourcc format metadata, `iosys_map`, kmsg/panic infrastructure, and optional QR code panic-screen code. It integrates with atomic helper state swapping, framebuffer pinning from plane helper callbacks, and drivers that can expose a linear panic scanout path.

## Risks and test signals
Risks include taking non-panic-safe locks, assuming hardware state without panic-lock protection, dereferencing state set up only by begin/end framebuffer access, invalid linear pitch/format metadata, and fallback stubs that silently disable real locking when panic support is off. Test signals include CONFIG_DRM_PANIC on/off builds, forced panic screen rendering, non-linear `set_pixel` paths, page-array scanout without preallocated maps, QR-code builds, and lockdep or panic-notifier review for atomic-context safety.
