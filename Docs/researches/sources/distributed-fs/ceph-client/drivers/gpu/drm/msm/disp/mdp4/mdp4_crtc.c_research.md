# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_crtc.c

Purpose: implements MDP4 DRM CRTC objects, including mixer setup, overlay flush, vblank event completion, legacy hardware cursor handling, and CRTC IRQ callbacks.

Important APIs and functions: `mdp4_crtc_init()` constructs a CRTC for a DMA/overlay pair. Atomic helpers include mode set, enable, disable, check, begin, and flush. Public helpers `mdp4_crtc_set_config()`, `mdp4_crtc_set_intf()`, and `mdp4_crtc_wait_for_commit_done()` are used by encoders and KMS commit flow. Cursor entry points are `mdp4_crtc_cursor_set()` and `mdp4_crtc_cursor_move()`.

Control flow: atomic flush stores any DRM event, programs blend/mixer state, writes overlay flush bits, and requests a vblank IRQ. The vblank callback unregisters its one-shot IRQ, atomically consumes pending cursor/flip flags, sends flip events, updates cursor registers, and schedules old cursor GEM unpin on a workqueue.

State and persistence: `struct mdp4_crtc` tracks enabled state, DMA/overlay routing, pending event, last flush mask, cursor BOs/iovas, and IRQ descriptors. State is volatile hardware and in-memory DRM state.

Dependencies and integration: uses MDP IRQ helpers, DRM vblank/event locks, MSM GEM IOVA pinning, MDP4 register helpers, and plane pipe ids. Encoders call into CRTC config/intf functions to route output.

Risks: cursor register updates are intentionally vblank-only to avoid underflow, so missed vblank can delay cursor changes. `atomic_check()` is minimal, leaving validation to planes/encoders. Mixer setup scans all CRTCs without explicit extra locking.

Test signals: page flip event timing, cursor set/move/disable, vblank enable/disable, underrun recovery, and flush wait timeout logs.
