# sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi.h

Purpose: public platform interface for the Synopsys DesignWare HDMI bridge core, covering SoC glue data, PHY selection, bus formats, audio callbacks, CEC policy, HPD/rx-sense, and bind/probe lifecycle.

Important APIs/types/functions: `enum dw_hdmi_phy_type`, `struct dw_hdmi_mpll_config`, `struct dw_hdmi_curr_ctrl`, `struct dw_hdmi_phy_config`, `struct dw_hdmi_phy_ops`, `struct dw_hdmi_plat_data`, `dw_hdmi_probe`, `dw_hdmi_bind`, `dw_hdmi_unbind`, `dw_hdmi_remove`, `dw_hdmi_resume`, audio setter/enabler helpers, PHY I2C/reset helpers, `dw_hdmi_bus_fmt_is_420`, and `dw_hdmi_to_plat_data`.

Control flow: glue drivers populate `dw_hdmi_plat_data` and bind/probe the opaque `struct dw_hdmi`; the common implementation calls optional mode validation, PHY, HPD, and audio callbacks while the DRM bridge is attached, modes are selected, audio is configured, and HPD/rx-sense changes are handled.

State and persistence: this header owns no storage. Runtime state lives in `struct dw_hdmi`, hardware registers, and platform-owned private pointers; no on-disk persistence exists.

Dependencies and integration points: DRM display modes/info, encoders, platform devices, regmap, HDMI codec, CEC, bridge chains, SoC PHY glue, and media bus format conventions.

Risks and test signals: watch for wrong PHY tables by pixel clock/bpc, callback lifetime bugs, invalid input bus encoding, YCbCr 4:2:0 policy mistakes, audio parameter drift, and HPD races. Test bind/unbind/resume, RGB/YUV/bpc modes, audio plug/sample changes, CEC disable, vendor and Synopsys PHYs, and HPD/rx-sense transitions.
