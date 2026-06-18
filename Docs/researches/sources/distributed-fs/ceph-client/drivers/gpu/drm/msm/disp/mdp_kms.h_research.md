# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_kms.h

Purpose: Defines the generic MDP KMS wrapper, IRQ helper structures, display capability bits, pipe/mixer capability bits, and CSC types used across MDP generations.

Important APIs/types: `struct mdp_kms_funcs` extends `msm_kms_funcs` with `set_irqmask`. `struct mdp_kms` embeds `msm_kms` and tracks IRQ handler list, vblank mask, current mask, and IRQ dispatch state. `struct mdp_irq` describes transient IRQ callbacks. Capability defines cover SMP, DSC, CDM, source split, pipe flip/scale/CSC/decimation/pixel-extension/cursor, and layer mixer display/writeback/pair support. `struct csc_cfg` stores matrix, bias, and clamp values.

Control flow/state: `mdp_kms_init()` initializes function pointers and the IRQ list, then delegates to `msm_kms_init()`. `mdp_kms_destroy()` delegates to `msm_kms_destroy()`. Other functions are implemented in `mdp_kms.c`.

Dependencies/integration: Includes Linux clock/platform/regulator headers, MDP format metadata, MSM driver/KMS headers, and generated common MDP enums. MDP5 cfg, pipe, mixer, and plane modules consume the capability bits.

Risks and test signals: This header is a cross-generation contract; changing capability bit values or CSC layout affects multiple drivers. Test by building MDP4, MDP5, and DPU users and by exercising YUV/CSC and IRQ paths.
