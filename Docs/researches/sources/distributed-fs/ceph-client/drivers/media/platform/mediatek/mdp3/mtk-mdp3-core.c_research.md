# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.c

## Purpose
This is the MDP3 platform driver. It binds supported MediaTek MDP3 device tree compatibles, discovers shared MMSYS/mutex/SCP infrastructure, configures components, initializes workqueues/CMDQ/V4L2 mem2mem state, and handles suspend cleanup.

## Important APIs, Types, And Functions
`mdp_probe()` is the main setup path. `__get_pdev_by_id()` finds infrastructure platform devices by platform data compatibles. `mdp_mm_subsys_deploy()` stores MMSYS and mutex devices for each multimedia subsystem. `mdp_vpu_get_locked()` boots the remote processor, registers IPI handlers, and initializes VPU shared buffers on first use; `mdp_vpu_put_locked()` deinitializes on last release. `mdp_video_device_release()` performs deferred global teardown when the video device is released. `mdp_suspend()` waits for outstanding CMDQ jobs before system suspend.

## Control Flow
Probe allocates `struct mdp_dev`, checks whether the node is the controlling MDP instance, deploys infra devices, obtains mutexes from platform pipe info, configures components, creates job and clock workqueues, obtains SCP/rproc handles, creates CMDQ clients, registers V4L2 and the mem2mem video device, then returns. Error labels unwind in reverse order. Remove unregisters V4L2; final resource destruction is delegated to the video-device release callback.

## State, Persistence, And Dependencies
Persistent driver state lives in `struct mdp_dev`: platform data, component array, mutex handles, workqueues, VPU reference count, CMDQ clients, V4L2 devices, and suspend/job counters. There is no filesystem persistence. Dependencies include OF platform discovery, runtime PM, SCP/remoteproc, CMDQ mailbox, mtk-mutex, V4L2, and videobuf2 DMA-contig.

## Integration Points
The file connects `mtk-mdp3-cfg.h` platform data to `mdp_comp_config()`, `mdp_m2m_device_register()`, VPU helpers in `mtk-mdp3-vpu.c`, and CMDQ execution code.

## Risks
Resource lifetime is split between probe/remove and video-device release, so failure paths and late users must keep ordering correct. `res->start` selects the controlling node; incorrect resource data can silently skip full setup. Suspend can fail if `job_count` never drains. VPU refcount calls are expected to be protected by `vpu_lock`.

## Test Signals
Probe/unprobe on each compatible, runtime V4L2 device creation, suspend during active jobs, SCP/VPU boot errors, CMDQ client creation across `pp_used`, and fault injection along probe unwind are the strongest signals.
