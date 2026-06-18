# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.h

Purpose: Declares primary plane creation for the Meson DRM driver.

Important APIs, types, and functions: Exports `meson_plane_create(struct meson_drm *priv)`.

Control flow: The main DRM initialization path calls create to allocate and register the OSD1 primary plane, choose modifier list by SoC family, install plane helpers, and store the result in `priv->primary_plane`.

State and persistence: No header state. The implementation stores runtime plane state in DRM plane state, a private `enabled` flag, and staged `priv->viu`/`priv->afbcd` fields.

Dependencies and integration points: Includes `meson_drv.h`. Provides a small internal API between the main driver and the OSD primary-plane implementation.

Risks: The API assumes one primary plane. Future multi-OSD primary/overlay support would require expanding the function signature or creating additional constructors.

Test signals: Compile and runtime KMS plane enumeration with `"meson_primary_plane"`.
