# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_vidi.c

## Purpose
This file implements VIDI, a virtual Exynos display output used for testing and simulated hotplug. It creates a virtual CRTC, three virtual planes, a virtual connector with fake or user-supplied EDID, a simple encoder, and a timer-driven 50 Hz fake vblank source.

## Important APIs, Types, and Functions
The core type is `struct vidi_context`, holding the encoder, DRM device, CRTC, connector, three planes, optional raw EDID, connection state, suspend state, vblank timer, and mutex. The user-facing entry point is `vidi_connection_ioctl()`, also exposed through the sysfs `connection` attribute for the fake EDID path.

Important functions include `vidi_probe()`, `vidi_bind()`, `vidi_unbind()`, `vidi_remove()`, `vidi_enable_vblank()`, `vidi_fake_vblank_timer()`, `vidi_update_plane()`, `vidi_atomic_enable()`, `vidi_atomic_disable()`, `vidi_detect()`, `vidi_get_modes()`, and `vidi_create_connector()`.

## Control Flow
Probe allocates context, initializes the timer and mutex, stores driver data, and registers the component. Bind stores the DRM device, exposes the device through `priv->vidi_dev`, initializes three planes using the shared Exynos plane helper, creates an Exynos CRTC backed by the primary plane and `vidi_crtc_ops`, initializes a TMDS encoder, maps possible CRTCs, and creates a virtual connector. Connection can be changed either through sysfs using fake EDID or through `vidi_connection_ioctl()` with user-provided EDID. Both paths update `ctx->connected` and call `drm_helper_hpd_irq_event()`. Vblank is simulated by a periodic timer that calls `drm_crtc_handle_vblank()` and rearms itself while vblank remains enabled.

## State and Persistence Behavior
The driver persists connection state, optional EDID, suspend state, and plane/CRTC/connector objects for the lifetime of the component. `raw_edid` is dynamically replaced on connect IOCTL and freed on disconnect/remove. The vblank timer is active only when vblank is enabled and the CRTC is not suspended. Plane updates do not program hardware; they only log framebuffer DMA addresses.

## Dependencies and Integration Points
VIDI integrates with `EXYNOS_VIDI_CONNECTION` in `exynos_drm_drv.c`, `exynos_drm_private::vidi_dev`, the shared Exynos plane helper, Exynos CRTC creation, DRM EDID helpers, DRM hotplug helpers, DRM vblank core, and virtual connector mode probing. The header `exynos_drm_vidi.h` provides a NULL stub when the config option is disabled.

## Risks
`vidi_connection_ioctl()` trusts the EDID extension count enough to allocate `(extensions + 1) * EDID_LENGTH` after copying only the header, so malformed but accessible user memory can request a larger copy before `drm_edid_valid()` rejects it. The same-function duplicate unreachable `return -EINVAL;` is harmless but noisy. Connection and EDID state are mutex-protected, but `vidi_detect()` uses `READ_ONCE()` without locking and can observe connection changes independently of EDID replacement. The sysfs path refuses to operate when raw EDID is set, so tests must reset via IOCTL before using fake EDID again. Timer cleanup must occur before context removal to avoid use after free.

## Test Signals
Run modetest against the virtual connector, toggle sysfs `connection` with fake EDID, use the VIDI connection IOCTL with valid and invalid EDID blobs, verify hotplug events, confirm `get_modes()` returns fake/user modes, enable/disable vblank and observe 50 Hz events, perform atomic plane updates across all three formats, and test remove/unbind while vblank is active.
