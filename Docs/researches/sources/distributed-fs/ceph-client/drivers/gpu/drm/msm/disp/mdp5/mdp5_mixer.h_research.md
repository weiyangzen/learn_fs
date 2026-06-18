# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_mixer.h

Purpose: Declares MDP5 layer mixer objects and their atomic allocation state.

Important APIs/types: `struct mdp5_hw_mixer` records array index, name, LM hardware id, capability bits, ping-pong id, DSPP id, and flush mask. `struct mdp5_hw_mixer_state` maps up to 8 mixer indices to owning DRM CRTCs. Public functions are `mdp5_mixer_init()`, `mdp5_mixer_assign()`, and `mdp5_mixer_release()`.

Control flow/state: The state struct is embedded in `mdp5_global_state`, so mixer allocation participates in DRM atomic duplicate/check/commit flow. Hardware mixer metadata is immutable once initialized from SoC config.

Dependencies/integration: Used by MDP5 KMS initialization and CRTC/pipeline allocation. The flush mask integrates with CTL commit programming.

Risks and test signals: The fixed 8-entry assignment array must cover all configured LMs. Tests should compile all cfg variants and exercise atomic debug state for mixer ownership during source split and CRTC disable.
