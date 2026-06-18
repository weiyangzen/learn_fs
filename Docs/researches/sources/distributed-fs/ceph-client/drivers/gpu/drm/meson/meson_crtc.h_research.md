# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_crtc.h

## Purpose
Declares the Meson CRTC creation and IRQ entry points for the DRM driver.

## Important APIs, types, and functions
- `int meson_crtc_create(struct meson_drm *priv);`
- `void meson_crtc_irq(struct meson_drm *priv);`

## Control flow
No complex control flow exists in the header. It includes `meson_drv.h` so callers share the `struct meson_drm` definition.

## State and persistence
No state is stored. The declared functions create the CRTC object and consume persistent `meson_drm` private state in IRQ context.

## Dependencies and integration points
Used by `meson_drv.c` for CRTC creation and top-level IRQ dispatch. It is intentionally narrow, keeping `struct meson_crtc` private to the implementation.

## Risks
Signature changes affect top-level driver build. The header exposes no way to query CRTC internals, so all cross-file state must flow through `struct meson_drm`.

## Test signals
Build coverage catches declaration drift. Runtime validation is CRTC creation and IRQ handling through `meson_drv.c`.
