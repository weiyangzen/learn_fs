# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_pipe.h

Purpose: Declares MDP5 source pipe descriptors and global pipe assignment state.

Important APIs/types: `SSPP_MAX` is defined as `SSPP_CURSOR1 + 1`. `struct mdp5_hw_pipe` stores index, name, enum pipe id, register offset, capability bits, CTL flush mask, and SMP block configuration. `struct mdp5_hw_pipe_state` maps pipe indices to owning DRM planes. Public functions are `mdp5_pipe_assign()`, `mdp5_pipe_release()`, and `mdp5_pipe_init()`.

Control flow/state: The state struct is part of `mdp5_global_state`, letting pipe ownership be changed transactionally in atomic check and committed only after the DRM atomic swap succeeds.

Dependencies/integration: Used by MDP5 KMS construction, plane atomic check/update, SMP state, and CTL flush programming.

Risks and test signals: The `SSPP_MAX` dependency on generated enum ordering must remain valid. `blkcfg` is cached in the pipe object and must track the active allocation. Compile all MDP5 cfgs and test plane allocation for each pipe class.
