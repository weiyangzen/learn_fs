# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_vp8.c

Purpose: VP8 stateless decode backend for Cedrus. It uses the H264 hardware engine mode for VP8, builds/updates the hardware probability table, performs necessary hardware bitstream parsing side effects, programs VP8 registers, and exports `cedrus_dec_ops_vp8`.

Important APIs/functions: static `prob_table_init[]` seeds hardware entropy/probability tables; `k_mv_entropy_update_probs` mirrors VP8 spec probabilities. `read_bits()` drives the hardware bit reader through H264 trigger/status registers. Header-processing helpers parse segmentation, loop filter deltas, quant deltas, reference refresh, and MV probability updates for hardware state. `cedrus_vp8_update_probs()` copies V4L2 VP8 frame entropy fields into the coherent probability buffer. `cedrus_vp8_setup()` enables H264/VP8 engine mode, programs source partition sizes, VLD offsets/address/length, entropy-probability buffer, PPS/filter/segmentation/reference flags, invokes header parsing, resets modified registers, writes quant/size/segment/filter/ref/destination registers, and enables IRQs. `cedrus_vp8_start()` allocates the coherent probability buffer and seeds it; `cedrus_vp8_stop()` disables engine and frees it.

Control flow: stream start allocates and initializes probability memory. Each job updates probabilities from controls, initializes hardware bitstream reader, runs header parsing to mutate internal hardware state, then trigger writes `VE_H264_TRIGGER_TYPE_VP8_SLICE_DECODE`. Completion uses H264-like IRQ bits.

State and persistence: per-session coherent entropy probability buffer persists while streaming. `last_frame_p_type`, `last_filter_type`, and `last_sharpness_level` persist across frames when loop filter level is nonzero and are folded into the next PPS register.

Dependencies/integration: consumes `V4L2_CID_STATELESS_VP8_FRAME`, V4L2 VP8 helpers/macros, vb2 DMA-contig buffers, and common Cedrus reference-address helpers.

Risks: comments explicitly note the driver must parse frame headers with hardware despite userspace parsing; bypassing this produces bad images. Probability buffer offsets were reverse-engineered, including an unknown 2048-byte seed offset. Header size handling differs for key/inter frames. `VE_H264_VLD_LEN` uses full plane size rather than payload for one register, while end address uses payload. Persistent last-filter fields update only when filter level is nonzero.

Test signals: VP8 key/inter frames, segmentation on/off, loop filter delta updates, token partitions, golden/alt reference frames, probability update cases, corrupted headers, stream restart state reset, and comparison against software decode output.
