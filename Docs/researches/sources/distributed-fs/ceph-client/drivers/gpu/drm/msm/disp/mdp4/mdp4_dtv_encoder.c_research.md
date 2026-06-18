# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dtv_encoder.c

Purpose: implements the MDP4 TMDS/DTV encoder used for HDMI-style external output.

Important APIs and functions: `mdp4_dtv_encoder_init()` allocates the encoder and obtains `hdmi_clk` and `tv_clk`. `mdp4_dtv_encoder_mode_set()` stores pixel clock and programs DTV timing/polarity registers. `mdp4_dtv_encoder_enable()` routes the CRTC to external mixer/interface, sets and enables clocks, enables DTV output, and flips the enabled flag. `mdp4_dtv_encoder_disable()` disables DTV output, waits for external vsync, disables clocks, and clears state. `mdp4_dtv_round_pixclk()` delegates clock rounding to `tv_clk`.

Control flow: enable first configures the DMA pack format and CRTC routing, then applies pixel clock rate and enables both MDP TV and HDMI clocks before asserting `REG_MDP4_DTV_ENABLE`.

State and persistence: stores pixel clock, clock handles, and `enabled`; hardware register state is volatile.

Dependencies and integration: used by `mdp4_kms.c` for TMDS interface setup and HDMI bridge/connector init. Depends on clock framework, DRM encoder helpers, MDP IRQ waits, and MDP4 register helpers.

Risks: clock enable failures are logged but do not unwind earlier clock actions or abort enable. Disable warns if called while not enabled. Polarity/skew are mode-derived with TODOs for panel/connector data.

Test signals: HDMI hotplug/modeset, pixel clock rounding, repeated enable/disable, external vblank wait, and underrun clear behavior.
