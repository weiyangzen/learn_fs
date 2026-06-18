# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_encoder.c

Purpose: implements generic MDP5 DRM encoder logic for video-mode interfaces and dispatches to command-mode DSI helpers when needed.

Important APIs and functions: `mdp5_encoder_init()` allocates an encoder, stores its interface and CTL, initializes interface lock, and installs helpers. `mdp5_encoder_atomic_check()` connects CTL/interface into CRTC state and marks deferred start for modesets. `mdp5_encoder_enable()`, disable, and mode_set dispatch based on interface mode. Video-mode helpers program interface timing, panel format, frame/line counters, enable/disable timing engine, flush encoder bits, wait for disable latch, and update encoder state. Accessors return line count, frame count, and set DSI command/video mode.

Control flow: video mode_set derives sync/display windows and panel format from connector bpc, writes INTF registers under lock, and calls `mdp5_crtc_set_pipeline()`. Enable reprograms mode from current CRTC state, enables timing engine, commits encoder flush, and marks encoder state enabled. Disable clears timing engine, commits, waits for vblank, and marks disabled.

State and persistence: `struct mdp5_encoder` stores CTL, interface, enabled flag, and lock. Hardware timing register state is volatile.

Dependencies and integration: integrates with DRM encoder helpers, MDP5 CRTC pipeline, CTL commit/state, DSI command encoder helpers, interface IRQ helpers, and connector display info.

Risks: enable calls mode_set itself, so ordering with full modeset/deferred start is delicate. DSI cannot handle active-low sync, so polarity handling differs by interface. Connector bpc defaults to 8 when unknown.

Test signals: HDMI/eDP/DSI video modes, DSI command mode switch, full modeset versus plane-only commits, vblank latch wait, frame/line counters, and panel bpc variations.
