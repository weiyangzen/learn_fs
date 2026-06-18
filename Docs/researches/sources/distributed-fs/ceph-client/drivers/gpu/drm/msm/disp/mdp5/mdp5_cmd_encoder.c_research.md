# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cmd_encoder.c

Purpose: implements MDP5 DSI command-mode encoder support, centered on pingpong tearcheck and CTL start signaling.

Important APIs and functions: `mdp5_cmd_encoder_mode_set()` programs tearcheck for the adjusted mode and sets the CRTC pipeline. `mdp5_cmd_encoder_enable()` enables tearcheck, flushes encoder timing bits through CTL, marks encoder state enabled, and sets the local enabled flag. `mdp5_cmd_encoder_disable()` disables tearcheck, marks encoder state disabled, commits encoder flush, and clears enabled. Internal helpers set up, enable, and disable pingpong tearcheck using `vsync_clk`.

Control flow: tearcheck setup gets the active mixer pingpong id, rounds `vsync_clk` to 19.2 MHz, computes clocks per line from vtotal and refresh, writes sync config, height, init, read pointer IRQ, start position, thresholds, and disables autorefresh. Enable sets/enables the clock and asserts `PP_TEAR_CHECK_EN`.

State and persistence: state is the shared `struct mdp5_encoder` enabled flag and hardware pingpong/clock registers. No file-local persistent state.

Dependencies and integration: only compiled with DSI support. Depends on MDP5 CRTC pipeline/mixer helpers, CTL commit/state APIs, clock framework, and pingpong registers.

Risks: if `vsync_clk` is missing or cannot round/enable, command-mode enable fails. The fallback tearcheck cadence is approximate and documented as a stability fallback because panel interrupts are not wired.

Test signals: DSI command-mode panel commits, pp_done completion, vsync clock error paths, enable/disable cycles, and tearcheck register programming against mode refresh.
