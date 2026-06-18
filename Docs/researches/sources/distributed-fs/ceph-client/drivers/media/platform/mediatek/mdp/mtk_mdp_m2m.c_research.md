# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.c

## Purpose
This file implements the legacy MDP V4L2 mem2mem frontend. It exposes formats, controls, crop/compose selection, vb2 queue operations, per-file context setup, VPU firmware initialization, and the job worker that fills the VPU shared configuration and runs processing.

## Important APIs, Types, and Functions
Format/limit data include `mtk_mdp_formats[]`, size alignments, and the default variant. Key helpers are format lookup/try/set, crop validation, scaler-ratio checking, queue setup/prepare/streaming, address preparation, `mtk_mdp_m2m_worker()`, `mtk_mdp_process_done()`, control creation and `mtk_mdp_s_ctrl()`. Public registration APIs are `mtk_mdp_register_m2m_device()` and `mtk_mdp_unregister_m2m_device()`.

## Control Flow
Open allocates a context, initializes controls and V4L2 file handle, creates a mem2mem context, loads/registers VPU firmware on the first active context, adds the context to `ctx_list`, and sets default formats. Streaming initializes the VPU instance on first use. The mem2mem scheduler queues `ctx->work`; the worker checks error state, maps current source/destination vb2 buffers to DMA addresses, fills source/destination size/format/address and misc controls into the VPU shared structure, sends `AP_MDP_PROCESS`, and completes both buffers with DONE or ERROR. Stop streaming drains queued buffers as errors and drops runtime PM.

## State and Persistence
Per-context state includes source/destination frame formats/crops/payloads, controls, colorimetry, VPU instance and shared memory pointer, mem2mem queues, and error flags. Device state tracks active context count and the job workqueue. No user configuration persists across close.

## Dependencies and Integration Points
The frontend depends on V4L2 ioctl/mem2mem, vb2 DMA-contig, runtime PM, the VPU firmware loader/IPI path, and helper functions from `mtk_mdp_regs.c` that populate `ctx->vpu.vsi`. It registers a `/dev/video*` M2M node named `mtk-mdp:m2m`.

## Risks and Edge Cases
`mtk_mdp_check_scaler_ratio()` uses integer division, so ratios below 1 truncate and boundary cases need testing. Format defaults and payload calculations must match multi-plane and single-plane YUV addressing, especially `YVU420` synthetic plane offsets. `mtk_mdp_s_ctrl()` checks rotation using the current control value rather than the incoming value in a subtle way. Release always calls VPU deinit even if init failed or streaming never started. Workqueue flushing on release serializes all jobs, so long VPU operations can delay close.

## Test Signals
Use v4l2-compliance, all advertised formats, single-plane and multi-plane YUV buffers, crop/compose with rotation, scaler-ratio limits, runtime PM start/stop balance, multiple contexts, VPU process failures, watchdog error state, and streamoff with queued buffers.
