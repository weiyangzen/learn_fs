## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.h

Purpose: declares encoder dispatch APIs and shared parameter/result structures used between the V4L2 encoder frontend, dispatch layer, VPU transport, and codec backends.

Important APIs/types/functions: defines firmware-sensitive enums `venc_yuv_fmt`, `venc_start_opt`, and `venc_set_param_type`; structs `venc_enc_param`, `venc_frame_info`, `venc_frm_buf`, and `venc_done_result`; backend symbols `venc_h264_if` and `venc_vp8_if`; and dispatcher functions.

Control flow: the frontend converts V4L2 formats/controls into `venc_enc_param`, calls `venc_if_set_param`, then encodes sequence headers or frames through `venc_if_encode`. Codec backends pass `venc_frame_info` through the VPU transport for extended firmware paths.

State and persistence behavior: most structures are transient per configuration or per frame, but enum numeric ordering is persistent ABI with firmware. `venc_done_result` carries output bitstream size and keyframe flag back to the V4L2 worker.

Dependencies and integration points: includes encoder context definitions. The comments explicitly warn that YUV format and parameter enum ordering must match VPU code.

Risks: renumbering enums or inserting values breaks firmware. `frm_rate` is an integer FPS derived by callers, losing fractional frame-rate precision. `venc_frm_buf` assumes at most `MTK_VCODEC_MAX_PLANES`.

Test signals: ABI review for enum changes, encode tests for every supported input YUV format, dynamic parameter command tests, and validation that output `bs_size`/keyframe flags match produced bitstreams.
