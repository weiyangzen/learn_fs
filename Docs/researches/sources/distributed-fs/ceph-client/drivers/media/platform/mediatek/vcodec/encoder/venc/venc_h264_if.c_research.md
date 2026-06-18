## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc/venc_h264_if.c

Purpose: codec-specific H.264 encoder backend for MediaTek hardware/firmware. It implements the `venc_common_if` contract, translates V4L2 H.264 parameters into firmware VSI configuration, manages firmware-described work buffers, emits SPS/PPS, encodes frames, and handles optional header prepending.

Important APIs/types/functions: exports `venc_h264_if`. Important types include H.264 frame/bitstream/work-buffer enums, standard and extended/34-bit VSI structs, and `struct venc_h264_inst`. Major functions include profile/level mapping, work-buffer alloc/free, SPS/PPS/header encode, frame encode, filler insertion, init, encode, set-param, and deinit.

Control flow: init allocates an instance, selects IPI ID based on extended firmware use, maps H.264 register base, calls `vpu_enc_init`, and stores the mapped VSI pointer as 32-bit or 34-bit layout. `VENC_SET_PARAM_ENC` populates VSI config, sends firmware set-param, reallocates all work buffers from firmware-provided sizes, maps/copies special RC_CODE and SKIP_FRAME buffers, and marks buffers allocated. Encode enables IRQ, handles sequence-header or frame options, sends VPU encode commands for SPS/PPS/frame, waits for expected IRQ status, reads bitstream byte count, and returns size/keyframe metadata. Prepend mode emits header, adds alignment filler if needed, then encodes the frame into the remaining bitstream buffer.

State and persistence behavior: per-instance state tracks work buffers, PPS scratch buffer, frame count, skipped frame count, prepend-header flag, VPU instance, VSI pointers, and context. Frame counters reset on force-intra/GOP/intra-period changes. Work buffers persist until reconfiguration or deinit.

Dependencies and integration points: depends on encoder VPU transport, hardware IRQ wait helpers, register base mapping, memory allocation helpers, frontend control translation, and SoC pdata flags for extended ABI and 34-bit IOVA.

Risks: firmware VSI layout and work-buffer semantics must match SoC firmware. 34-bit and 32-bit paths must stay behaviorally aligned. Prepend-header alignment/filler math can underflow available bitstream size if capture buffers are too small. Skip-frame handling copies firmware memory directly to userspace bitstream buffer. Unsupported profile/level values log and may map to defaults or zero.

Test signals: H.264 encode with separate and joined headers, IDR/I/P frame cadence, force-keyframe and GOP/intra-period changes, bitrate/framerate updates, skip-frame firmware state, 34-bit IOVA SoC, small capture buffers, expected IRQ statuses for SPS/PPS/frame, and work-buffer reallocation after format change.
