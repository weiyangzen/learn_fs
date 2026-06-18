# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.h

Purpose: central private header for MDP4 KMS structures, register accessors, bit translation helpers, and cross-file prototypes.

Important APIs and types: `struct mdp4_kms` embeds `mdp_kms` and stores DRM device, revision, MMIO, regulator, clocks, error handler, runtime PM flag, and blank cursor BO/iova. Inline helpers wrap MMIO reads/writes and translate pipes, overlays, DMAs, and mixer stage selections into hardware bit masks. `mdp4_pipe_caps()` exposes plane feature caps by pipe class.

Control flow and integration: CRTC, plane, encoder, IRQ, PLL, and KMS files include this header to share MDP4 register layout helpers and function prototypes. Encoders call CRTC config/routing helpers declared here.

State and persistence: declares in-memory KMS state only. Hardware register state is managed by users of `mdp4_write()` and `mdp4_read()`.

Dependencies: includes DRM panel, MSM driver/KMS, shared `mdp_kms`, and generated `mdp4.xml.h` register definitions.

Risks: helper mappings must match hardware bit definitions; invalid enum values generally map to zero, which can silently skip flush or IRQ bits. `mixercfg()` warns for invalid pipes but still returns current config.

Test signals: build coverage after generated register updates, per-pipe flush/IRQ validation, and modeset tests proving expected pipe-to-mixer routing.
