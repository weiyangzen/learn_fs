# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.c

## Purpose
Implements the Amlogic Meson video encoder programming layer for CVBS, HDMI/TMDS, and MIPI DSI/LCD-style output paths. It translates DRM display modes and HDMI VICs into ENCI, ENCP, and ENCL hardware register programming and maintains the active VENC mode state used by interrupt and encoder code.

## Important APIs, types, and functions
- Global CVBS tables `meson_cvbs_enci_pal` and `meson_cvbs_enci_ntsc` provide PAL/NTSC ENCI timing and analog adjustment parameters.
- `union meson_hdmi_venc_mode` holds either ENCI interlace timing fields or ENCP progressive/interlace timing fields for HDMI.
- Static `meson_hdmi_venc_vic_modes[]` maps CEA VICs to precomputed ENCI/ENCP timing tables for 480i/576i, 480p/576p, 720p, 1080i/p, and 2160p modes.
- Exported HDMI helpers: `meson_venc_hdmi_supported_mode()`, `meson_venc_hdmi_supported_vic()`, `meson_venc_hdmi_venc_repeat()`, and `meson_venc_hdmi_mode_set()`.
- LCD/DSI helpers: `meson_encl_load_gamma()` and `meson_venc_mipi_dsi_mode_set()`.
- CVBS helpers: `meson_venci_cvbs_mode_set()` and `meson_venci_get_field()`.
- Lifecycle/IRQ helpers: `meson_venc_enable_vsync()`, `meson_venc_disable_vsync()`, and `meson_venc_init()`.

## Control flow
HDMI mode setup first decides whether to use ENCI or ENCP. Double-clocked interlaced modes use ENCI and HDMI read-rate repetition; known VICs use static timing tables; unknown but otherwise valid DMT modes synthesize a simple ENCP timing block from `struct drm_display_mode`. Pixel counts, active region, porch, sync width, and field-line counts are adjusted for HDMI repeat, VENC repeat, YUV420, and interlace. The function disables VDAC and both ENCI/ENCP, programs the selected encoder, computes DE/HSYNC/VSYNC windows, selects the VIU/VPP mux, writes `VPU_HDMI_SETTING`, records repeat/use-ENCI flags, and marks `priv->venc.current_mode` as HDMI.

The ENCI path programs CVBS-like timing, ENCI FIFO-to-video settings, top/bottom field windows, DVI sync windows, and interlaced field-specific VSYNC registers. The ENCP path writes the table or synthesized ENCP mode fields, enables ENCP, programs DE and DVI sync timing for even and optionally odd fields, then selects ENCP in the VPP mux.

MIPI DSI mode setup selects ENCL, disables ENCL, derives all horizontal and vertical timing from the DRM mode, configures ENCL video, test pattern, dithering, TTL/TCON DE/HSYNC/VSYNC outputs, gamma coefficient base registers, and sets the current mode to MIPI DSI. CVBS setup skips reprogramming when the requested PAL/NTSC tag is already active, then programs ENCI, VDAC, upsamplers, DAC selections, saturation/contrast/brightness/hue, and analog sync adjustment.

Initialization powers down VDAC and HDMI PHY registers via HHI regmap, disables HDMI routing and all encoders, disables VSync IRQ generation, and resets the current mode to none. VSync enable chooses ENCP line-reset interrupt only for MIPI DSI and ENCI line-reset for the other modes.

## State and persistence
The durable runtime state lives in `priv->venc`: `current_mode`, `hdmi_repeat`, `venc_repeat`, and `hdmi_use_enci`. The file also leaves persistent hardware state in VPU/VENC MMIO registers and HHI regmap registers until another modeset or `meson_venc_init()` rewrites them. Gamma loading writes 256-entry linear LUT data separately for R, G, and B and enables the ENCL gamma control port.

## Dependencies and integration points
Depends on Linux MMIO helpers, regmap for HHI, DRM display mode flags, Meson register definitions, `meson_vpu_is_compatible()`, and `meson_vpp_setup_mux()`. It is called by Meson HDMI, CVBS, and DSI encoder implementations and by the CRTC/IRQ path that needs VSync control and field polarity.

## Risks
The HDMI timing tables are hardware-specific magic values; small changes can break sync on specific TVs or CEA modes. ENCI/ENCP repeat handling is subtle because HDMI FIFO read/write rates, VENC pixel doubling, interlace field math, and YUV420 all interact. DMT fallback accepts a broad mode range but uses a minimal synthesized ENCP timing path that may not match all monitor expectations. Gamma programming uses polling with warning-only timeout handling, so display output may continue with stale gamma if the hardware is not ready. `meson_venci_cvbs_mode_set()` is idempotent by mode tag, which can skip reprogramming after external register corruption.

## Test signals
Useful validation includes HDMI mode coverage for each mapped VIC, DMT fallback modes, 480i/576i double-clocked ENCI output, YUV420 FIFO rate handling, PAL/NTSC CVBS output, MIPI DSI panel timings, VSync IRQ selection, suspend/resume reinitialization, and `priv->venc` repeat/use-ENCI state observed by HDMI clock/encoder code. Register dumps around `VPU_HDMI_SETTING`, ENCI/ENCP DE/VSYNC registers, and HHI VDAC/PHY controls are high-value debugging signals.
