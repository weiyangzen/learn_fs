# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lcdc_encoder.c

Purpose: implements the MDP4 LVDS/LCDC encoder path, including LCDC timing, LVDS PHY mux programming, clock/regulator control, and mode validation.

Important APIs and functions: `mdp4_lcdc_encoder_init()` allocates an LVDS encoder, obtains the LCDC clock through `mdp4_get_lcdc_clock()`, and gets LVDS regulators. `mdp4_lcdc_encoder_mode_set()` programs LCDC timing registers and stores pixel clock. `mdp4_lcdc_encoder_enable()` programs DMA output format, routes the CRTC, enables regulators and LCDC clock, configures the LVDS PHY, enables LCDC, and marks enabled. `mdp4_lcdc_encoder_disable()` disables LCDC, waits for primary vsync, disables clock/regulators, and clears enabled. `mdp4_lcdc_encoder_mode_valid()` requires exact clock rounding.

Control flow: `setup_phy()` derives bits per pixel from connector display info, falls back to 18 bpp, writes 18/24-bit LVDS mux tables, lane enables, PHY config, and serialization enable after a short delay.

State and persistence: stores LCDC clock, pixel clock, regulator handles, and enabled flag. Register and regulator states are volatile.

Dependencies and integration: depends on DRM connector display info, MDP4 CRTC routing, LVDS PLL helper, regulator framework, and clock framework.

Risks: LVDS channel count, swap, and some data-enable polarity are hard-coded/TODO. Unsupported bpp aborts PHY setup after earlier enable work. Exact clock validation can reject modes a panel might tolerate.

Test signals: LVDS panel modes, 18/24 bpp paths, regulator failures, exact clock validation, enable/disable latch wait, and suspend/resume.
