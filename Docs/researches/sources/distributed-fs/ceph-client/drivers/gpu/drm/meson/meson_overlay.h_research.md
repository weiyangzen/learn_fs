# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.h

Purpose: Declares overlay plane creation for the Meson DRM driver.

Important APIs, types, and functions: Exports `meson_overlay_create(struct meson_drm *priv)`.

Control flow: The main driver calls create during DRM device initialization. The implementation allocates and registers a DRM universal overlay plane, assigns helper callbacks, sets immutable zpos, and stores it in `priv->overlay_plane`.

State and persistence: No state is declared in the header. Plane state lives in `meson_overlay.c`, DRM plane state, and staged `priv->viu` fields.

Dependencies and integration points: Includes `meson_drv.h` for private driver structures. The function integrates the VD1 overlay into the KMS plane list.

Risks: Minimal header risk. Any future multiple-overlay support would require changing the single create API and `priv->overlay_plane` assumption.

Test signals: Successful DRM plane enumeration with `"meson_overlay_plane"` after `meson_overlay_create()` returns 0.
