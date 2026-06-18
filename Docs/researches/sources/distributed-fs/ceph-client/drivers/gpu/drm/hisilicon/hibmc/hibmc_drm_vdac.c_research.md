# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_vdac.c

Purpose: implements the HIBMC VGA-style DAC encoder and connector, including DDC-backed EDID mode enumeration and panel output enabling.

Important APIs/functions: `hibmc_vdac_init()` creates the DDC adapter, DAC encoder, VGA connector, helper functions, and encoder attachment. `hibmc_connector_get_modes()` reads EDID through DDC, falls back to no-EDID modes, and prefers 1024x768. `hibmc_encoder_mode_set()` sets panel/display control enable bits. `hibmc_connector_destroy()` unregisters the DDC adapter and cleans up the connector.

Control flow: called by HIBMC KMS init after DE and optional DP setup. Connector probing uses DDC detect helper and mode enumeration. Encoder mode set programs display control on modeset.

State and persistence: VDAC state is embedded in `priv->vdac`, with I2C adapter, connector, and encoder. Hardware output enable bits persist in `HIBMC_DISPLAY_CONTROL_HISILE`.

Dependencies and integration points: depends on DRM connector/encoder helpers, EDID helpers, HIBMC DDC implementation, and HIBMC register definitions. It shares the single HIBMC CRTC with optional DP output.

Risks: fallback mode list relies on global mode-config max dimensions. Error cleanup calls `hibmc_ddc_del()` for encoder or connector init failures. `hibmc_encoder_mode_set()` turns on panel-related bits but has no corresponding disable callback in this file.

Test signals: VGA connector detection via DDC, EDID and no-EDID fallback modes, encoder attach, mode set enabling output bits, connector destroy cleanup, and clone behavior with DP.
