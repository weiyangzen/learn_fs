# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_plane.c

Purpose: implements MDP4 DRM planes, framebuffer preparation/cleanup, scanout programming, scaling checks, format setup, CSC setup for YUV, and plane creation.

Important APIs and functions: `mdp4_plane_init()` creates primary or overlay planes with RGB or RGB+YUV formats based on pipe caps. `mdp4_plane_atomic_update()` calls `mdp4_plane_mode_set()`. `mdp4_plane_prepare_fb()` and cleanup pin/unpin framebuffer backing through MSM helpers. `mdp4_plane_set_scanout()` writes per-plane strides and IOVA bases. `mdp4_write_csc_config()` writes CSC matrix/bias/clamp registers.

Control flow: mode_set ignores disabled plane states, converts source rectangles from Q16 to integer pixels, checks up/down scaling limits, sets scaling op bits and phase steps, writes source/destination geometry, framebuffer addresses, source format/unpack fields, optional YUV CSC state, op mode, phase steps, and tiled frame size when needed.

State and persistence: each plane stores pipe id and name. Framebuffer pinning state is managed by MSM framebuffer helpers. Hardware register state is volatile and latched by CRTC flush.

Dependencies and integration: integrates with DRM atomic helpers, damage clips, MSM format descriptors, MDP4 register helpers, and CRTC flush/mixer configuration.

Risks: `atomic_check()` is empty, so invalid scaling or format combinations fail late in atomic update with `WARN_ON`. Property helpers are placeholders. Tiled support is narrow and tied to Samsung 64x32 NV12.

Test signals: RGB and YUV scanout, NV12 tiled modifier, scaling limit failures, framebuffer pin cleanup, damage clip support, and blend interactions with CRTC mixer setup.
