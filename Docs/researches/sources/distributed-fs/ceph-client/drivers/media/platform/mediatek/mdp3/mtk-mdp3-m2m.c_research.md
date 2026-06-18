# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.c

## Purpose
This file implements the MDP3 V4L2 mem2mem video node. It exposes image processing operations to userspace, manages per-file contexts, negotiates formats/crop/compose controls, prepares vb2 buffers, invokes VPU path planning, and submits CMDQ work.

## Important APIs, Types, And Functions
`mdp_m2m_device_register()` creates the video device and `v4l2_m2m_dev`. `mdp_m2m_open()` allocates a context, controls, queues, and default formats. `mdp_m2m_device_run()` converts source/destination vb2 buffers into `img_ipi_frameparam`, calls `mdp_vpu_process()`, and sends an `mdp_cmdq_param` via `mdp_cmdq_send()`. `mdp_m2m_start_streaming()` checks scaling and initializes the VPU. Format and selection ioctls call `mdp_try_fmt_mplane()`, `mdp_try_crop()`, and V4L2 helpers. Controls map hflip, vflip, and rotation into the capture frame.

## Control Flow
Open creates an isolated context and default OUTPUT/CAPTURE formats. Userspace sets formats, selection, and controls, queues buffers, and starts both queues. The mem2mem scheduler calls `mdp_m2m_device_run()`, which populates input/output firmware descriptors, optionally switches to dual-bitblt for large work, asks the VPU for a pipeline config, waits for previous job drain, sends CMDQ, and later `mdp_m2m_job_finish()` completes both buffers.

## State, Persistence, And Dependencies
Per-context state includes `curr_param`, frame counters, controls, and queue state. `ctx_lock` serializes vb2 queues; device-level `m2m_lock` serializes open/release and video ioctls. There is no persistence. Dependencies include V4L2 mem2mem, vb2 DMA-contig, MDP regs helpers, VPU IPC, and CMDQ.

## Integration Points
Core probe calls `mdp_m2m_device_register()`. Register helpers convert V4L2 frames to firmware images. VPU returns `config` memory consumed by CMDQ. Job completion is called from the CMDQ callback path.

## Risks
VPU lifecycle depends on start/release state bits; missing `mdp_vpu_put_locked()` would leak firmware state. `device_run()` waits for outstanding `job_count`, serializing jobs and risking timeout. Selection type checks use single-planar type constants in places, so compliance coverage matters. Buffer errors complete both queues as error.

## Test Signals
V4L2 compliance for M2M MPLANE ioctls, format/crop/compose boundary tests, rotation/flip transformations, streamon/streamoff with queued buffers, VPU failure injection, CMDQ timeout handling, and suspend while jobs are active.
