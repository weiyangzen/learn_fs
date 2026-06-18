# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output_7a2000.c

Purpose: implements LS7A2000 HDMI/VGA-style output handling, HDMI PHY/PLL setup, AVI infoframes, HPD detection, connector mode probing, debugfs, and output initialization.

Important APIs/types/functions: `ls7a2000_output_init`, connector get_modes/detect helpers, HDMI encoder reset/enable/disable/mode_set, `ls7a2000_hdmi_phy_pll_config`, and `ls7a2000_hdmi_set_avi_infoframe`.

Control flow: output init creates per-pipe TMDS encoder and HDMI connector, attaches helper funcs, and enables polling. Encoder reset programs DVO clock/data and disables hardware I2C in favor of GPIO DDC, then releases HDMI PHY reset. Atomic mode set configures HDMI PHY PLL based on pixel clock bands and writes AVI infoframe content. Atomic enable programs zone, PHY control, and interface control; disable clears PHY/interface enable bits. Detection reads HPD bits and optionally probes DDC for pipe 0 fallback.

State and persistence: HDMI registers, PHY PLL, AVI packet registers, HPD status, and DVO config persist in hardware. Debugfs exposes HDMI register snapshots.

Dependencies and integration points: called by LS7A2000 descriptor, uses DRM EDID/HDMI helpers, DDC I2C, register access helpers, and CRTC mode state.

Risks and test signals: AVI content extraction casts unaligned bytes to `unsigned int *`; this may be risky on strict-alignment architectures. HDMI PLL wait has bounded polling but only logs failure. Test 25 MHz through 340 MHz modes, HPD and DDC fallback, both HDMI pipes, AVI infoframe correctness, and debugfs register reads.
