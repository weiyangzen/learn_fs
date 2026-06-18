# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.h

Purpose: Declares the CVBS mode descriptor, fixed supported-mode count, global mode table, and probe/remove hooks for the Meson composite encoder.

Important APIs, types, and functions: `struct meson_cvbs_mode` pairs an ENCI hardware mode descriptor with a DRM display mode. `MESON_CVBS_MODES_COUNT` is fixed at 2. The header exports `meson_cvbs_modes[]`, `meson_encoder_cvbs_probe()`, and `meson_encoder_cvbs_remove()`.

Control flow: No runtime control flow exists in the header. Consumers call probe/remove from the main Meson DRM driver and inspect `meson_cvbs_modes[]` for supported composite modes.

State and persistence: The table declared here is defined in `meson_encoder_cvbs.c` and represents static driver-supported state, not dynamically learned hardware state.

Dependencies and integration points: Includes `meson_drv.h` and `meson_venc.h` so the descriptor can reference `struct meson_drm`, `struct drm_display_mode`, and `struct meson_cvbs_enci_mode`.

Risks: The fixed count must stay synchronized with the array definition. The include guard name references VENC/CVBS rather than encoder/CVBS, so future renames should avoid duplicate guards.

Test signals: Build coverage should catch mismatched table count and missing `struct meson_cvbs_enci_mode`. Runtime output should expose exactly `MESON_CVBS_MODES_COUNT` modes.
