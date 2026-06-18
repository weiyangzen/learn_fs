# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_crtc.h

Purpose: Defines Nouveau's CRTC wrapper and minimal helper API shared by display, connector, cursor, and legacy modeset code.

Important APIs/types: `struct nouveau_crtc` embeds `drm_crtc`, nvif head/event objects, CRTC index, saved flat-panel control and user state, procamp fields, last DPMS state, saved cursor position, current framebuffer metadata, cursor BO/VMA callbacks, LUT depth, and optional save/restore hooks. Inline helpers `nouveau_crtc()` and `to_drm_crtc()` convert between DRM and Nouveau types. `nv04_cursor_init()` is declared for legacy cursor setup.

Control flow/state contract: Display code uses `head` for scanout position and vblank control, connectors use CRTC linkage to find active connector, and cursor paths use the embedded callback table. The structure stores hardware restore state for legacy modesetting and suspend/resume.

Dependencies/integration: Includes DRM CRTC, nvif head, and nvif event headers. It is consumed by `nouveau_display.c`, `nouveau_connector.h`, and generation-specific display implementations.

Risks/test signals: Fields are shared across old and newer display paths, so changes can regress legacy NV04/NV50 behavior. Cursor callback pointers must be initialized before use. Test signals include vblank enable/disable, cursor movement/show/hide, suspend/resume restore, CRTC scanout position accuracy, and legacy DPMS behavior.
