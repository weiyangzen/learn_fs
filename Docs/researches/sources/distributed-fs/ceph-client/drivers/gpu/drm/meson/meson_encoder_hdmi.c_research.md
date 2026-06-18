# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.c

Purpose: Implements the Meson HDMI encoder bridge that sits before the DW-HDMI transceiver bridge. It validates HDMI modes against VENC and VCLK capabilities, selects output bus format, programs VENC/VCLK/format muxing on atomic enable, creates the HDMI bridge connector, and manages CEC notifier physical address updates.

Important APIs, types, and functions: `struct meson_encoder_hdmi` stores encoder, bridge, connector, `meson_drm *priv`, selected `output_bus_fmt`, and CEC notifier. Bridge callbacks include `attach`, `detach`, `mode_valid`, `hpd_notify`, `atomic_enable`, `atomic_disable`, `atomic_get_input_bus_fmts`, and `atomic_check`. Public hooks are `meson_encoder_hdmi_probe()` and `remove()`.

Control flow: probe finds graph port 1 remote DW-HDMI bridge, adds a Meson HDMI bridge, initializes a TMDS encoder, attaches the bridge without creating a connector, creates a bridge connector, resets connector state, attaches HDR metadata when supported, attaches max-bpc 8..8, enables 4:2:0, and registers a CEC notifier against the remote platform device. Atomic check records negotiated output bus format and marks mode changed on HDR metadata changes. Mode validation rejects unsupported TMDS/sink combinations, checks CEA VIC modes with `meson_venc_hdmi_supported_vic()` and `meson_vclk_vic_supported_freq()`, or DMT modes with `meson_venc_hdmi_supported_mode()` and `meson_vclk_dmt_supported_freq()`. Enable programs VENC HDMI mode, VCLK, VPU HDMI format control, and ENCI/ENCP enable.

State and persistence: `output_bus_fmt` persists between atomic check and enable. Connector state carries HDR metadata and 4:2:0 allowance. Hardware state persists in VENC, VCLK, `VPU_HDMI_FMT_CTRL`, `VPU_HDMI_SETTING`, and ENCI/ENCP enable bits. CEC notifier persists until detach.

Dependencies and integration points: Depends on DRM bridge connector, media bus formats, CEC notifier, OF graph/platform lookup, `meson_venc`, `meson_vclk`, and DW-HDMI bridge HPD/EDID callbacks.

Risks: 4:2:0 selection is split between display capability, negotiated bus format, and DW-HDMI PHY setup. CEC physical address is currently set by reading EDID in HPD notify, with an inline FIXME about better use of connector display info. Max bpc is constrained to 8. Probe error paths release the DT node but CEC `put_device()` is only called on notifier allocation failure.

Test signals: HDMI mode lists for CEA and DMT modes, 4:2:0-only sink validation, HDR metadata property causing mode_changed, HPD notifications updating CEC physical address, ENCI path for 480i/576i, ENCP path for progressive/HD interlace, and disable clearing HDMI routing plus ENCI/ENCP enables.
