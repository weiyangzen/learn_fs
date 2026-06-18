# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.c

Purpose: Implements the Meson DRM CVBS encoder bridge and simple DRM encoder for composite analog output. It exposes PAL and NTSC modes, validates them, configures ENCI timings and VCLK2, powers the VDAC, and attaches a downstream connector bridge.

Important APIs, types, and functions: `struct meson_encoder_cvbs` owns a `drm_encoder`, a Meson bridge, and `meson_drm *priv`. `meson_cvbs_modes[]` defines PAL `720x576i` and NTSC `720x480i` modes with ENCI mode descriptors. Bridge callbacks include `attach`, `get_modes`, `mode_valid`, `atomic_check`, `atomic_enable`, and `atomic_disable`. Public entry points are `meson_encoder_cvbs_probe()` and `meson_encoder_cvbs_remove()`.

Control flow: probe finds graph port 0 remote connector bridge, creates a DRM bridge of type Composite, initializes a TVDAC encoder, attaches bridge and bridge-connector, and stores the encoder in `priv->encoders[MESON_ENC_CVBS]`. Atomic enable finds the active connector/CRTC state, maps adjusted mode to one of the two CVBS definitions, programs ENCI via `meson_venci_cvbs_mode_set()`, sets VCLK2 to 27 MHz through `meson_vclk_setup()`, selects VDAC0 source, then writes SoC-specific VDAC HHI registers. Atomic disable powers down VDAC.

State and persistence: The file does not maintain mode state beyond DRM object lifetime. Hardware state persists in ENCI, VCLK2, VDAC selection, and HHI VDAC control registers until disabled or overwritten. The bridge is removed on `remove`; devm allocation handles memory lifetime.

Dependencies and integration points: Depends on DRM bridge/connector helpers, OF graph, `meson_venc` ENCI mode data, `meson_vclk`, and `meson_registers.h`. It shares the same CRTC/VIU pipeline as HDMI/DSI but targets analog ENCI/VDAC output.

Risks: Only two fixed modes are supported. Mode matching is strict on timings, clock, flags, and 3D flags, so userspace modelines must match exactly. VDAC register constants are SoC-specific and differ on G12A. Missing connector bridge returns success with no CVBS output, which is expected for disabled hardware but can hide DT issues.

Test signals: `modetest` should list only PAL/NTSC composite modes. Atomic commits for both modes should enable ENCI and VDAC. Disable should zero the G12A VDAC controls or set legacy `HHI_VDAC_CNTL1` to 8. Probe deferral should occur if the connector bridge is unavailable.
