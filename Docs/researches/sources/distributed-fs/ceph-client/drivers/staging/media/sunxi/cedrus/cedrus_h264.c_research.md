# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h264.c

Purpose: H.264 stateless decode backend for Cedrus. It programs H264 engine registers/SRAM from V4L2 stateless H264 controls, manages decoded picture buffer mappings, allocates per-session/per-buffer scratch DMA memory, handles IRQ status, and exports `cedrus_dec_ops_h264`.

Important APIs/functions: SRAM helpers write frame list, ref lists, scaling lists, and prediction weight tables. `cedrus_write_frame_list()` maps V4L2 DPB entries to Cedrus frame slots, allocates per-output MV column buffers, and writes `VE_H264_OUTPUT_FRAME_IDX`. `cedrus_set_params()` programs bitstream addresses, optional large-width deblock/intrapred DRAM buffers, software decode initialization, bit skipping, PPS/SPS/slice registers, QP registers, status clear, and IRQ enable. `cedrus_h264_start()` allocates pic-info, neighbor-info, and optional 4K scratch buffers. `cedrus_h264_stop()` frees per-capture-buffer MV columns and context scratch. `cedrus_h264_trigger()` starts slice decode.

Control flow: stream start allocates context scratch. Each decode job enables the engine, clears rotation, points extra buffers, writes scaling/frame/reference state, sets bitstream and slice parameters, then trigger writes `VE_H264_TRIGGER_TYPE_AVC_SLICE_DECODE`. IRQ status maps decode/VLD errors to `CEDRUS_IRQ_ERROR` and slice-complete to `CEDRUS_IRQ_OK`.

State and persistence: per-session scratch buffers live from OUTPUT streamon to streamoff. Per-capture-buffer MV-column buffers are allocated lazily and persist across jobs until stop. Buffer slot `position` and `pic_type` preserve DPB mapping across frames.

Dependencies/integration: consumes V4L2 H264 decode params, SPS, PPS, scaling matrix, slice params, pred weights, vb2 DMA addresses, and common Cedrus engine/format helpers. It uses `cedrus_regs.h` for all register fields.

Risks: comments document unreliable `VE_H264_VLD_OFFSET`, so bit skipping is done through repeated flush triggers. Several buffer-size formulas come from CedarX/BSP sources and include FIXMEs for frame-only streams and 4K H6 behavior. DPB timestamp misses silently skip refs. MV-column allocation failures abort setup mid-job. Large-width paths require extra buffers sized exactly for hardware expectations.

Test signals: H264 baseline/main/high streams, field/MBAFF streams, weighted prediction, scaling matrix present/absent, B-slices with both ref lists, dynamic resolution, 4K streams on H6-like hardware, invalid DPB timestamps, streamoff leak checks, and IRQ error injection.
