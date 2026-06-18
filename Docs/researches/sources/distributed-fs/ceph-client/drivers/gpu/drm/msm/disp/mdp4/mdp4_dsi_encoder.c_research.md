# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dsi_encoder.c

Purpose: implements the MDP4 encoder path for DSI video output when `CONFIG_DRM_MSM_DSI` is enabled.

Important APIs and functions: `mdp4_dsi_encoder_init()` allocates a DRM DSI encoder and installs helper callbacks. `mdp4_dsi_encoder_mode_set()` programs DSI timing registers from the adjusted mode. `mdp4_dsi_encoder_enable()` programs DMA packing/dither config, routes the CRTC to `INTF_DSI_VIDEO`, enables DSI output, and marks the encoder enabled. `mdp4_dsi_encoder_disable()` disables output and waits for primary vsync so the disable latches.

Control flow: modeset derives horizontal/vertical timing values, polarity, display start/end, and underflow recovery color. Enable uses CRTC helpers to program output format and interface selection before setting `REG_MDP4_DSI_ENABLE`. Disable is guarded by the local enabled flag and waits on `MDP4_IRQ_PRIMARY_VSYNC`.

State and persistence: state is a boolean `enabled` in the encoder plus programmed MDP4 DSI registers. No persistent storage.

Dependencies and integration: integrates with MDP4 KMS register helpers, MDP IRQ wait, DRM encoder helpers, and MSM DSI modeset attachment performed in `mdp4_kms.c`.

Risks: only video mode is used here; DSI command mode is not represented. Timing polarity and skew contain TODOs for panel-provided values. Disable depends on a functioning primary vblank source.

Test signals: DSI panel modeset, enable/disable cycles, suspend/resume, underflow behavior, and verifying timing registers against adjusted modes.
