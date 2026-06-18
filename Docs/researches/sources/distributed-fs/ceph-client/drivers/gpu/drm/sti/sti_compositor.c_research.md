# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.c

Purpose: Implements the `sti-compositor` component driver that maps the compositor register bank, obtains compositor and pixel clocks, deasserts main/aux reset controls, resolves VTG phandles, and builds the in-DRM topology for the STiH407 compositor.

Important APIs/functions: `sti_compositor_probe()` allocates `struct sti_compositor`, loads `stih407_compositor_data`, maps registers, gets `compo_main`, `compo_aux`, `pix_main`, and `pix_aux` clocks, acquires `compo-main`/`compo-aux` resets, and registers component ops. `sti_compositor_bind()` stores `dev_priv->compo`, creates VID and mixer subdevices first, then creates cursor/GDP planes and initializes CRTCs with the first GDP planes as primaries. `sti_compositor_debugfs_init()` delegates debugfs setup to VID and mixer subdevices.

Control flow: Binding is intentionally two-pass. The first pass constructs mixers and VID blocks because planes and CRTCs depend on them. The second pass creates cursor/GDP planes from descriptor offsets and calls `sti_crtc_init()` while primary plane slots are available. `drm_vblank_init()` is sized to the number of created CRTCs.

State/persistence: Runtime state is held in the devm-managed `struct sti_compositor`, including register base, descriptor copy, clock/reset handles, mixer/VID/VTG arrays, and VTG notifier blocks initialized to `sti_crtc_vblank_cb`.

Dependencies/integration: Uses Linux component framework, OF matching for `st,stih407-compositor`, DRM core, reset/clock APIs, and STI local modules (`sti_crtc`, `sti_cursor`, `sti_gdp`, `sti_mixer`, `sti_vid`, `sti_vtg`). The compositor is the anchor referenced by `sti_private`.

Risks/test signals: Error paths usually abort probe on missing mandatory clocks/registers but component bind logs and continues past failed plane creation, which can leave fewer CRTCs/planes than expected. Test with device-tree clock/reset/phandle coverage, KMS plane enumeration, vblank init count, and debugfs mixer/VID files after CRTC late registration.
