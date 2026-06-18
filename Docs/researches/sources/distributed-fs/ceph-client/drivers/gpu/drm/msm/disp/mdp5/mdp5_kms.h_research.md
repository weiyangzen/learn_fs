# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_kms.h

Purpose: Central private header for MDP5 KMS. It defines the MDP5 device object, global atomic resource state, plane/CRTC/encoder private state, interface descriptors, register access helpers, IRQ mapping helpers, and cross-module prototypes.

Important APIs/types: `struct mdp5_kms` extends `struct mdp_kms` and stores DRM device, platform device, hardware pipe/mixer/interface arrays, config handler, caps, global private object, SMP and CTL managers, MMIO, clocks, resource lock, runtime PM flag, error handler, and enable count. `struct mdp5_global_state` aggregates `mdp5_hw_pipe_state`, `mdp5_hw_mixer_state`, and `mdp5_smp_state` under a DRM private state. `struct mdp5_plane_state` tracks assigned left/right pipes, blend stage, and dirtyfb needs. `struct mdp5_crtc_state` tracks CTL, pipeline, IRQ masks, command mode, and deferred start. `mdp5_write()`/`mdp5_read()` wrap MMIO with an enable-count warning.

Control flow/integration: Other MDP5 modules include this header to share resource ownership contracts. Plane check code writes pipe assignments into `mdp5_global_state`; CRTC code consumes mixer/interface pipeline state; KMS commit hooks prepare/complete SMP state. Inline `intf2vblank()`, `intf2err()`, and `lm2ppdone()` map logical interfaces/mixers to hardware IRQ bits used by CRTC and IRQ code.

State and persistence: The header describes volatile kernel objects only. Atomic state clones are the persistence boundary across check/commit phases. The `resource_lock` protects shared registers such as `REG_MDP5_DISP_INTF_SEL`.

Dependencies: Pulls in MSM DRM/KMS, generic MDP definitions, MDP5 cfg, generated `mdp5.xml.h`, pipe/mixer/ctl/smp headers, and optional DSI command encoder declarations gated by `CONFIG_DRM_MSM_DSI`.

Risks and test signals: Header-level risks are ABI coupling between modules and assumptions about array sizes such as `SSPP_MAX`, 8 mixers, and 5 interfaces. The register helpers warn but do not prevent unclocked access. Validate by building all MDP5 configurations, running atomic state debug printing, exercising DSI command mode vblank mapping, writeback mapping, and source split paths.
