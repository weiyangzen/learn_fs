# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.h

Purpose: Documents and declares the MDP5 Shared Memory Pool API and its atomic state model.

Important APIs/types: `struct mdp5_smp_state` contains a global block bitmap, per-client bitmaps, and bitmasks of assigned and released pipes. Public functions initialize the SMP, calculate required blocks, assign/release blocks, dump state, and prepare/complete commit hardware updates.

Control flow/state: The header explicitly describes the two-step update contract: prepare commit writes new assignments before pipes use them; complete commit clears released clients after old scanout is done. The state is embedded in `mdp5_global_state`.

Dependencies/integration: Depends on DRM printing and MSM/MDP5 generated SMP types. Plane allocation and KMS commit hooks are the primary callers.

Risks and test signals: The API relies on callers respecting the prepare/complete split. Tests should check atomic rollback, debug printing, and plane reallocation where old and new SMP allocations overlap in time.
