# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.h

Purpose: Declares the DSI encoder lifecycle hooks used by the main Meson DRM driver.

Important APIs, types, and functions: Exports `meson_encoder_dsi_probe(struct meson_drm *priv)` and `meson_encoder_dsi_remove(struct meson_drm *priv)`. It relies on `struct meson_drm` being visible before or through included driver context.

Control flow: No direct control flow exists. The main driver calls probe during DRM device setup and remove during teardown.

State and persistence: The header defines no state. State is held privately in `meson_encoder_dsi.c` and in `priv->encoders[MESON_ENC_DSI]`.

Dependencies and integration points: Minimal internal header for the Meson DRM encoder registry. It intentionally hides `struct meson_encoder_dsi` internals.

Risks: Because the header does not include `meson_drv.h` or forward declare `struct meson_drm`, callers must already have the type declared. That is acceptable in current local include order but can be fragile if reused standalone.

Test signals: Compile coverage from main driver inclusion is the main signal; runtime signals live in `meson_encoder_dsi.c`.
