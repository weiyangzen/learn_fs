# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.h

Purpose: Defines the internal AFBCD operation interface and G12A decoded-output address used by Meson OSD AFBC support.

Important APIs, types, and functions: `MESON_G12A_AFBCD_OUT_ADDR` is the hardware-internal buffer address used to transfer decoded pixels from the ARM AFBC decoder to VIU/OSD. `struct meson_afbcd_ops` contains callbacks for `init`, `exit`, `reset`, `enable`, `disable`, `setup`, optional `fmt_to_blk_mode`, and `supported_fmt`. It exports `meson_afbcd_gxm_ops` and `meson_afbcd_g12a_ops`.

Control flow: The main driver selects one ops table by SoC family, planes call support functions during format/modifier validation, and commit/disable paths call setup/enable/reset/disable through this vtable.

State and persistence: The header defines interface shape only. Callback implementations use `struct meson_drm` to read staged plane state and write persistent decoder hardware registers.

Dependencies and integration points: Includes `meson_drv.h` for `struct meson_drm`. Integrated by `meson_plane.c`, `meson_osd_afbcd.c`, and likely the main VIU commit code.

Risks: The fixed G12A output address is not memory allocated by this driver; misuse outside the intended hardware path would be dangerous. `fmt_to_blk_mode` is optional and must be NULL-checked or used only with ops that provide it.

Test signals: Compile-time conformance of both ops tables and runtime primary-plane AFBC enable/disable on GXM/G12A.
