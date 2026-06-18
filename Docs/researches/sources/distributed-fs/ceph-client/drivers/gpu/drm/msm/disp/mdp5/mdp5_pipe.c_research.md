# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.c

Purpose: Provides atomic allocation/release of MDP5 source pipes (SSPPs) to DRM planes and constructs pipe descriptors from SoC config.

Important APIs/functions: `mdp5_pipe_assign()` selects a pipe matching required caps and optional right-pipe source-split needs. It checks both new and old global pipe state to avoid immediate reuse of pipes still scanning out or still owning non-double-buffered SMP allocations. It also handles SMP block assignment through `mdp5_smp_assign()`. `mdp5_pipe_release()` releases global pipe ownership and SMP blocks. `mdp5_pipe_init()` creates immutable pipe metadata and CTL flush mask.

Control flow: Plane atomic check computes required caps from format, scale, rotation, cursor type, and source split. If reallocation is needed, it asks `mdp5_pipe_assign()` for a left pipe and optionally a right pipe. Candidate selection rejects pipes already in old/new state, caps mismatches, cursor-pipe misuse, and for source split, mismatched right-pipe type/order. After successful assignment, old pipes are released in the same duplicated atomic state.

State and persistence: Ownership lives in `global_state->hwpipe.hwpipe_to_plane[]`; per-pipe immutable metadata includes `pipe`, `reg_offset`, `caps`, `flush_mask`, and the last SMP `blkcfg`. No disk persistence exists.

Dependencies/integration: Tied to MDP5 KMS global atomic state, plane check/update, SMP allocator, DRM plane types, and CTL flush masks.

Risks and test signals: Reuse avoidance can transiently consume more pipes and cause `-ENOMEM` during complex updates. Right-pipe selection does not explicitly check old/new ownership for the right candidate in the visible loop, so source-split behavior needs careful regression coverage. Test cursor versus overlay pipe selection, YUV/scale caps, SMP allocation changes, disabling planes, and wide source split.
