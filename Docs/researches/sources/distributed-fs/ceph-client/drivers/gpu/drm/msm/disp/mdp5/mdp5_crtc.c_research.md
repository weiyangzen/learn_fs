# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_crtc.c

Purpose: implements MDP5 DRM CRTCs, including dynamic mixer assignment, stage/zpos validation, blending, flush/start sequencing, command-mode pp_done waits, vblank/event handling, scanout position, vblank counter, and legacy LM cursor support.

Important APIs and functions: `mdp5_crtc_init()` constructs CRTCs. Atomic helpers include custom state reset/duplicate/destroy/print, mode_set, check, flush, enable, and disable. Public helpers expose vblank mask, pipeline setup, CTL/mixer/pipeline access, and commit wait. Cursor functions support legacy LM cursors when no cursor plane is provided.

Control flow: atomic check collects visible planes, marks command-mode dirtyfb needs, decides whether a right mixer is needed for source split or wide modes, assigns/release mixers, computes IRQ masks, sorts planes by zpos, and assigns mixer stages. Atomic flush stores page-flip event, programs blend state through LM registers and CTL layer regs, arms pp_done for command mode, commits all flush bits, updates IRQ masks, and requests one-shot vblank completion. Commit wait uses pp_done for command mode and flush register drain for video mode.

State and persistence: `struct mdp5_crtc` stores enabled state, event, flush mask, pending flags, IRQ descriptors, pp completion, cursor BO/iova/dimensions/position, and LM lock. `mdp5_crtc_state` stores CTL and pipeline.

Dependencies and integration: depends on MDP5 CTL, mixer assignment, plane flush/pipe helpers, encoder line/frame counters, DRM vblank/event core, MSM GEM, runtime PM, and MDP IRQ dispatch.

Risks: legacy LM cursor is unsupported with source split and deprecated when cursor planes exist. Mixer assignment and release happen during atomic check and must stay consistent with DRM atomic state rollback. Stage count and fullscreen assumptions determine whether border color is required.

Test signals: multi-plane zpos, cursor plane versus LM cursor, source split, command-mode pp_done waits, video flush waits, vblank timestamp/counter, suspend/resume cursor restore, and invalid too-many-plane commits.
