# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.h

## Purpose
This header centralizes MDP3 driver-wide platform data and runtime device state. It describes supported infrastructure blocks, multimedia subsystems, buffer usage classes, platform quirks, mutex pipe mappings, and the primary `struct mdp_dev`.

## Important APIs, Types, And Functions
`struct mdp_platform_config` records per-SoC feature quirks for RDMA, RSZ, WROT, and TDSHP behavior. `struct mtk_mdp_driver_data` is the full platform-data contract: infra compatibles, component data, format tables, default limits, pipe info, parallel-processing criteria, and component DT IDs. `struct mdp_mm_subsys` stores MMSYS/mutex devices plus `mtk_mutex` handles. `struct mdp_dev` holds all live driver state, including workqueues, VPU/SCP handles, CMDQ clients, V4L2 objects, suspend/job counters, and locks. Exported declarations include VPU reference helpers and `mdp_video_device_release()`.

## Control Flow
No direct control flow is implemented. The declarations define how probe code initializes the device, how M2M contexts access the shared device, and how VPU lifetime is reference-counted.

## State, Persistence, And Dependencies
State is in-memory kernel device state. `vpu_lock` protects working buffer metadata and VPU count operations; `m2m_lock` serializes V4L2 mem2mem device operations; `job_count` and `callback_wq` synchronize suspend with CMDQ completion. Dependencies include V4L2, mem2mem, MediaTek MMSYS/mutex, MDP components, and MDP VPU definitions.

## Integration Points
Used by all MDP3 implementation files: core probe, M2M ioctls, register conversion, VPU IPC, component setup, CMDQ submission, and platform config tables.

## Risks
Many fields are platform-data indexed, so mismatched table lengths or enum values can corrupt pipe/component selection. Locking expectations are implicit in comments and call sites. The `pp_used` value controls CMDQ client array bounds.

## Test Signals
Compile coverage across all supported SoCs, lockdep during concurrent opens/streaming/suspend, and probe coverage with one and two multimedia subsystems exercise this header's contracts.
