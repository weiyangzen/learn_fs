# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.h

Purpose: declares the MDP5 CTL manager and CTL programming API used by MDP5 CRTCs, encoders, and pipeline setup code.

Important APIs and types: opaque `struct mdp5_ctl_manager` and `struct mdp5_ctl` enforce encapsulation. Manager functions initialize the pool, reset hardware, and request a CTL for an interface. CTL functions get CTL id, set pipeline, set encoder state, route cursor, program blend layers, compute flush masks for LM/pipe/cursor/encoder, commit flush/start, and read commit status. `MAX_PIPE_STAGE` defines left/right pipe slots per stage, and `MDP5_CTL_BLEND_OP_FLAG_BORDER_OUT` requests border color base output.

Control flow and integration: atomic encoder check places a CTL into CRTC state; CRTC blend and flush code then calls the functions declared here. Encoder enable/disable uses encoder flush masks and encoder state updates.

State and persistence: no state in the header; opaque objects are allocated in `mdp5_ctl.c`.

Dependencies: includes MSM driver definitions and relies on MDP5 enum types for pipes and interfaces.

Risks: API callers must provide a valid pipeline with mixer/interface and stage arrays sized to `STAGE_MAX + 1` by `MAX_PIPE_STAGE`. No release prototype appears here, so CTL ownership semantics are not obvious from this file alone.

Test signals: compile coverage, CTL allocation and pipeline setup during modesets, flush mask correctness for every pipe/interface, and debug state showing expected CTL ids.
