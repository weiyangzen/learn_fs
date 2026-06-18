# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.c

Purpose: Implements the OMAP DRM encoder object that bridges DRM mode setting to OMAP DSS output timing configuration.

Important APIs/functions: `omap_encoder_init()` allocates `struct omap_encoder`, initializes a DRM encoder of type TMDS, stores the target `omap_dss_device`, and installs helper callbacks. `omap_encoder_mode_set()` converts the adjusted DRM mode to `videomode`, restores missing sync/data-enable/pixel-edge flags from bridge timings and connector display info bus flags, and calls `dss_mgr_set_timings()`. `omap_encoder_destroy()` cleans up and frees the encoder.

Control flow: Modeset setup creates an encoder for each connected output and attaches the output bridge chain. During modeset, DRM helper calls `mode_set`, which writes upstream manager timings through DSS manager wrappers before bridge/output enable.

State and persistence: `struct omap_encoder` only stores the DRM encoder and output pointer. No persistent storage exists.

Dependencies/integration: Depends on DRM encoder/bridge/connector helpers, videomode conversion, OMAP DSS manager timing API, and bridge timing/display info bus flags.

Risks and test signals: The mode flag restoration is a documented hack because DRM display modes lose some videomode flags. The connector search assumes the matching connector is present in the mode config list. Test panels/bridges with DE and pixel/sync edge flags, chained bridges, and modeset ordering with each DSS output type.
