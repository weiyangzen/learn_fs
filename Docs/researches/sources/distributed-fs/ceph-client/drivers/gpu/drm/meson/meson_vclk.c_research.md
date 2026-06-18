# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.c

Purpose: Implements Meson video clock programming for CVBS, HDMI CEA/VIC modes, and HDMI DMT modes. It configures HDMI PLL parameters, VID PLL fractional divider, VCLK/VCLK2 dividers and gates, ENCI/ENCP/VDAC/HDMI clock selection, and mode-frequency validation.

Important APIs, types, and functions: Exported APIs are `meson_vclk_dmt_supported_freq()`, `meson_vclk_vic_supported_freq()`, and `meson_vclk_setup()`. Important helpers include `meson_vid_pll_set()`, `meson_venci_cvbs_clock_config()`, `meson_hdmi_pll_set_params()`, `meson_hdmi_pll_find_params()`, `meson_hdmi_pll_generic_set()`, `meson_vclk_freqs_are_matching_param()`, and `meson_vclk_set()`. `params[]` is the table of supported HDMI clock topologies.

Control flow: CVBS setup programs a fixed 1.485 GHz HDMI PLL, VID PLL `/1`, VCLK2 divider for 27 MHz, VCLK2 gates, ENCI and VDAC clock selects. DMT validation/generation computes generic PLL parameters for pixel clock times ten. VIC validation compares requested PHY/VCLK frequencies against the supported table, including 1000/1001 variants and SoC package limits. HDMI setup selects a matching table row, derives HDMI-TX and VENC divisors, accounts for ENCI/DDR/YUV420 alternatives, sets HDMI system clock, HDMI PLL, VID PLL divider, VCLK divider, HDMI-TX pixel clock source, VENC source, and enables the relevant gates.

State and persistence: Programming persists in HHI PLL, divider, mux, reset, and gate registers. The function does not keep software state except through debug output and `priv->limits` checks. PLL lock polling waits until hardware reports lock, including an unbounded G12A retry loop.

Dependencies and integration points: Depends on `regmap`, `meson_vpu_is_compatible()`, SoC compatibility flags, DRM mode status values, and consumers in HDMI/CVBS encoders. HDMI encoder calculates `phy_freq`, `vclk_freq`, `venc_freq`, and HDMI pixel/dac frequencies, then calls this module.

Risks: Clock tables are finite and reject unsupported but potentially valid modes. PLL magic constants are SoC-specific and empirically bounded. G12A PLL lock loop can spin indefinitely if hardware never locks. DMT generic path logs fatal errors but cannot recover beyond returning from setup. 10-bit 2K/4K support is explicitly missing.

Test signals: `mode_valid` outcomes for CEA modes, DMT modelines, 1000/1001 refresh variants, SoC max PHY limits, CVBS 27 MHz output, HDMI 27/74.25/148.5/297/594 MHz paths, YUV420 4K modes, and PLL lock behavior on GXBB/GXL/GXM/G12A.
