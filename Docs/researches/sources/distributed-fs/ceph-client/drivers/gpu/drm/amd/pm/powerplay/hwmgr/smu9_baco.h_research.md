# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.h

Purpose: declares SMU9 BACO support and state query functions.

Important APIs/types: includes `hwmgr.h` and `common_baco.h`, then exports `smu9_get_bamaco_support(struct pp_hwmgr *hwmgr)` and `smu9_baco_get_state(struct pp_hwmgr *hwmgr, enum BACO_STATE *state)`.

Control flow and state: callers use this header to determine BACO availability and observe whether the GPU is in BACO. Entry/exit sequencing lives elsewhere. No state is declared here.

Dependencies and integration: depends on `pp_hwmgr`, `enum BACO_STATE`, and common BACO constants. Used by SMU9 power-management paths.

Risks and test signals: callers must pass a valid `state` pointer. The function name uses `bamaco`, which can be missed by searches for BACO. Compile SMU9 BACO users and validate on SOC15 NBIF BACO-capable hardware.
