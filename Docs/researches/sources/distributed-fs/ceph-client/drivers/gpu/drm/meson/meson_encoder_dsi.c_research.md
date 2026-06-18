# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.c

Purpose: Implements the Meson-side DSI encoder bridge. It connects the DRM encoder to the DW MIPI-DSI bridge/panel chain and programs the ENCL VENC path during atomic enable/disable.

Important APIs, types, and functions: `struct meson_encoder_dsi` wraps a `drm_encoder`, a Meson bridge, and `meson_drm *priv`. Bridge callbacks are `attach`, `atomic_enable`, and `atomic_disable`, with standard atomic state helpers. Public functions are `meson_encoder_dsi_probe()` and `meson_encoder_dsi_remove()`.

Control flow: probe allocates a bridge, finds graph port 2 remote DSI transceiver, resolves the downstream bridge, adds the Meson DSI bridge, initializes a simple DSI encoder, attaches the bridge chain, and stores it in `priv->encoders[MESON_ENC_DSI]`. Atomic enable obtains new connector and CRTC state, calls `meson_venc_mipi_dsi_mode_set()` for adjusted mode, loads ENCL gamma, disables ENCL video, enables ENCL FIFO mode, disables test output, disables OSD1 matrix wrapping, then enables ENCL video. Disable turns off ENCL and re-enables OSD1 matrix bit 0.

State and persistence: The driver persists only DRM object references; hardware state persists in ENCL registers and `VPP_WRAP_OSD1_MATRIX_EN_CTRL`. It relies on the clock framework and DSI bridge for DSI pixel/bit clock programming rather than direct VCLK setup.

Dependencies and integration points: Depends on DRM bridge/simple-KMS helpers, OF graph, `meson_venc`, `meson_vclk` includes, and register definitions. It is paired with `meson_dw_mipi_dsi.c`, which handles DW host/PHY details and panel attachment.

Risks: No explicit mode validation is implemented here; validation is delegated to bridge/panel and VENC helpers. Missing remote DSI bridge logs an error but returns 0, allowing systems without DSI. The matrix enable/disable side effect is specific and could interact with other output paths if multiple encoders were active.

Test signals: DT graph with DSI panel should produce bridge chain `encoder -> dsi encoder -> dw-mipi-dsi -> panel`. Atomic enable should program ENCL and show panel output. Disable should blank ENCL and restore matrix control.
