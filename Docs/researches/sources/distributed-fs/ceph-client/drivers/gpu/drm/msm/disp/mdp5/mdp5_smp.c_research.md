# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_smp.c

Purpose: Implements MDP5 Shared Memory Pool allocation and hardware programming for source pipe fetch buffering.

Important APIs/functions: `mdp5_smp_init()` creates the SMP handler from cfg block count/size and seeds reserved MMB state. `mdp5_smp_calculate()` computes per-plane block counts encoded into `blkcfg`. `mdp5_smp_assign()` allocates blocks per SMP client for a pipe. `mdp5_smp_release()` removes a pipe's client allocations from global state. `mdp5_smp_prepare_commit()` writes newly assigned blocks and FIFO thresholds before scanout uses them. `mdp5_smp_complete_commit()` clears FIFO thresholds for released pipes after scanout completion. `mdp5_smp_dump()` prints allocation state for atomic debug.

Control flow: Plane check computes `blkcfg` and pipe assignment calls `mdp5_smp_assign()`. Assign walks pipe clients, allocates blocks from the duplicated global state, and marks the pipe in `assigned`. Release clears per-client bitmaps and marks the pipe in `released`. KMS commit hooks call prepare before flush/wait and complete after commit completion to respect non-double-buffered SMP allocation registers.

State and persistence: `struct mdp5_smp` stores device lifetime config, reserved blocks, block geometry, and register-cache arrays for allocation/FIFO registers. `struct mdp5_smp_state` stores global and per-client bitmaps plus assigned/released masks in atomic private state.

Dependencies/integration: Depends on DRM formats for plane count/subsampling, MDP5 cfg client ids, KMS global state, pipe client counts, and MDP5 register macros.

Risks and test signals: SMP registers are not double buffered, so early release can corrupt active scanout. `smp_request_block()` assumes client bitmaps are empty on assign. Reserved blocks reduce requested count. Test format width changes, YUV plane counts, SMP exhaustion, atomic test-only rollback, plane disable/enable on separate CRTCs, and debug dump consistency.
