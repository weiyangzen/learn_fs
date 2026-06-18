## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_vp8_if.c

Purpose: codec-specific VP8 encoder backend implementing `venc_common_if` for MediaTek VP8 hardware/firmware.

Important APIs/types/functions: exports `venc_vp8_if`. It defines VP8 work-buffer indexes, firmware config/buffer/VSI structs, and `struct venc_vp8_inst`. Important helpers allocate/free firmware-described work buffers, wait for frame IRQ, compose a final VP8 frame bitstream, initialize, encode, set params, and deinitialize.

Control flow: init allocates an instance, sets IPI ID to `IPI_VENC_VP8`, maps VP8 encoder register base, initializes firmware, and stores the mapped VSI. `VENC_SET_PARAM_ENC` writes input format, bitrate, visible/coded dimensions, GOP size, framerate, and temporal scalability mode into VSI, sends firmware set-param, then allocates AP work buffers and copies firmware-resident RC code buffers into DMA memory. Encode only supports normal frame encoding: enables IRQ, sends `vpu_enc_encode`, waits for `MTK_VENC_IRQ_STATUS_FRM`, then composes final VP8 output by prepending the uncompressed frame tag and firmware-generated header before the hardware payload.

State and persistence behavior: per-instance state tracks work buffers, allocation flag, frame count, temporal scalability mode, VPU instance, VSI pointer, and context. Work buffers persist until reconfiguration or deinit. `frm_cnt` increments after successful frame composition.

Dependencies and integration points: integrates with frontend `venc_if_*` dispatch, VPU IPI transport, hardware IRQ wait helpers, register reads for frame/header length, and firmware memory mapping for RC buffers.

Risks: `vp8_enc_compose_one_frame` moves data in-place inside the capture bitstream buffer; incorrect length registers or insufficient buffer size can corrupt output and is guarded only by size check. VP8 keyframe tag fields use visible dimensions from VSI and must be little-endian byte split. Temporal scalability mode must be set before encoder params to be included. Unlike H.264, no 34-bit IOVA path is present here.

Test signals: VP8 keyframe and inter-frame output inspection, small capture-buffer rejection, temporal scalability mode setup before stream start, RC_CODE buffer copy, frame IRQ timeout/error, repeated parameter reconfiguration, and deinit after partial allocation failure.
