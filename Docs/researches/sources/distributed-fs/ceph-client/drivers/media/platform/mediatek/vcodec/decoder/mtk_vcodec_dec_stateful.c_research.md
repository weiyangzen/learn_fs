# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateful.c

## Purpose
This file implements the stateful decoder behavior used by older MediaTek platforms such as MT8173. It manages stream-header parsing, DPB sizing, dynamic resolution change events, and reference/display buffer recycling.

## Important APIs, Types, And Functions
Static format table exposes H.264, VP8, VP9 coded formats and MT21C capture. `get_display_buffer()` returns decoded display frames to userspace. `get_free_buffer()` recycles capture buffers no longer referenced by firmware. `mtk_vdec_flush_decoder()` drains the decoder. `mtk_vdec_pic_info_update()` fetches picture info and DPB size. `mtk_vdec_worker()` performs normal frame decode or empty-flush handling. `vb2ops_vdec_stateful_buf_queue()` has special header-parse logic for early OUTPUT buffers and capture-buffer ownership flags. Controls expose `V4L2_CID_MIN_BUFFERS_FOR_CAPTURE` plus VP9/H.264 profile limits. `mtk_vdec_8173_pdata` wires these callbacks.

## Control Flow
After OUTPUT format setup initializes the codec, the first queued output buffers are decoded with no framebuffer to parse headers and detect resolution. Once header info is available, the driver updates capture sizes, DPB size, moves to `MTK_STATE_HEADER`, and emits `SOURCE_CHANGE`. During normal decode, a source and destination buffer are passed to `vdec_if_decode()`. Display buffers are completed, free reference buffers are requeued or released, and resolution changes trigger flush plus a source-change event. Decoder STOP queues an empty flush buffer that returns a LAST capture buffer.

## State, Persistence, And Dependencies
State includes context `picinfo`, `last_decoded_picinfo`, `dpb_size`, decoded frame count, capture-buffer flags (`used`, `queued_in_vb2`, `queued_in_v4l2`), and codec state. Dependencies include V4L2 events, vb2 DMA-contig, decoder PM via codec implementations, and `vdec_if_*`.

## Integration Points
Selected by OF pdata for MT8173. Shared decoder ioctls call these vb2 ops and worker through pdata.

## Risks
Capture-buffer ownership is complex and protected by `ctx->lock`; incorrect flags can leak buffers or return reference frames too early. Resolution-change condition uses width or height equality logic that may miss one-dimension changes. Empty flush consumes a destination buffer and must set LAST correctly.

## Test Signals
Stateful V4L2 compliance, header-only buffers, dynamic resolution streams, DPB minimum buffer control, flush/STOP/LAST semantics, reference-frame recycling, and error injection from `vdec_if_decode()`.
