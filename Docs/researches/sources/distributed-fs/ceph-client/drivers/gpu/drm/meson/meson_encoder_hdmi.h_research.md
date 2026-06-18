# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.h

Purpose: Declares the HDMI encoder probe/remove functions used by the Meson DRM device setup and teardown paths.

Important APIs, types, and functions: Exports `meson_encoder_hdmi_probe(struct meson_drm *priv)` and `meson_encoder_hdmi_remove(struct meson_drm *priv)`.

Control flow: No local execution. It is a private module boundary between the main Meson DRM driver and the HDMI encoder implementation.

State and persistence: No state is declared here. The implementation stores the encoder object in `priv->encoders[MESON_ENC_HDMI]` and maintains connector/CEC state privately.

Dependencies and integration points: Like the DSI header, it assumes `struct meson_drm` is declared by including context. It keeps HDMI internals opaque to the rest of the driver.

Risks: Standalone inclusion without a prior `struct meson_drm` declaration would fail. Any future consumer outside the current Meson DRM include order should add a forward declaration or include `meson_drv.h`.

Test signals: Build coverage and successful main-driver invocation of probe/remove are the relevant signals.
