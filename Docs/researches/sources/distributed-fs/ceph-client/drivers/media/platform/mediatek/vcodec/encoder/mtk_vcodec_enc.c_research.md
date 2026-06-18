## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.c

Purpose: implements the V4L2 mem2mem encoder frontend: controls, format negotiation, VB2 queue operations, encoder command/flush handling, workqueue-driven encode jobs, and default per-context parameters.

Important APIs/types/functions: exports `mtk_venc_ioctl_ops`, `mtk_venc_m2m_ops`, `mtk_vcodec_enc_queue_init`, `mtk_vcodec_enc_ctrls_setup`, `mtk_vcodec_enc_set_default_params`, `mtk_venc_lock`, `mtk_venc_unlock`, and `mtk_vcodec_enc_release`. Core internal paths include control setter `vidioc_venc_s_ctrl`, format helpers, queue setup/prepare/start/stop, `mtk_venc_encode_header`, `mtk_venc_param_change`, and `mtk_venc_worker`.

Control flow: userspace sets formats and controls through V4L2 ioctls. Capture format selection initializes the codec backend with `venc_if_init`. Start-streaming waits until both output and capture queues are active, translates V4L2 params into `venc_enc_param`, sends `VENC_SET_PARAM_ENC`, and for H.264 joined-header mode requests header prepending. The m2m scheduler calls `device_run`; H.264 may first emit SPS/PPS into a capture buffer, then queue encode work. The worker removes source/destination buffers, handles the synthetic flush source buffer, maps DMA addresses into `venc_frm_buf`/`mtk_vcodec_mem`, calls `venc_if_encode`, propagates timestamps/keyframe flags, completes buffers, and finishes the m2m job.

State and persistence behavior: per-context state includes source/capture `q_data`, colorspace fields, encoder params, state machine (`FREE`, `INIT`, `HEADER`, `ABORT`), latched `param_change`, an ordered `encode_work`, and a synthetic `empty_flush_buf`. Parameter changes are copied into `mtk_video_enc_buf` at source-buffer queue time so changes apply to a specific frame. `is_flushing` persists until the zero-payload LAST capture buffer is dequeued or streamoff clears it.

Dependencies and integration points: integrates with V4L2 controls/ioctls/events, v4l2-mem2mem scheduling, videobuf2 DMA-contig, codec dispatch in `venc_drv_if.c`, and platform capabilities from `mtk_vcodec_enc_drv.c`.

Risks: `mtk_venc_worker` intentionally avoids `dev_mutex`, so it races with ioctls and must only touch state protected by queue/m2m semantics. Format size calculations must match hardware alignment and userspace buffer sizes. Flush handling depends on recognizing the synthetic source buffer and zero-payload LAST capture buffer. Some controls are accepted but not fully enforced by firmware paths, such as B-frame count.

Test signals: v4l2-compliance for mem2mem encoders, H.264 header separate/joined modes, STOP/START encoder commands, streamoff during flush, dynamic bitrate/framerate/GOP/force-keyframe changes, unsupported bitrate mode, buffer too small, 4K capability frame sizes, and abort-state behavior after backend errors.
