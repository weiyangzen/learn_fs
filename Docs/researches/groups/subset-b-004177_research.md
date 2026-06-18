# subset-b-004177 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro.h

## Purpose
Defines the central private interfaces for the Verisilicon Hantro VPU driver: hardware variants, V4L2/media-device function objects, per-device state, per-filehandle codec context, format descriptors, register helpers, decoded-buffer metadata, and exported helpers used by codec backends.

## Important APIs, Types, And Functions
Key types are `struct hantro_variant`, `struct hantro_dev`, `struct hantro_ctx`, `struct hantro_fmt`, `struct hantro_reg`, `struct hantro_decoded_buffer`, and `struct hantro_postproc_regs`. Inline helpers map V4L2/video objects to driver contexts, read/write encoder and decoder register windows, update masked register fields, fetch queued buffers, and select the decoder buffer address with or without postprocessing.

## Control Flow And State
`hantro_ctx` is the per-open state owner. It tracks encoder/decoder mode, sequence counters, negotiated source/destination/reference formats, controls, JPEG quality, bit depth, postprocessor need, selected codec ops, and a union of codec-specific hardware contexts. `hantro_dev` owns persistent device-wide resources: clocks, resets, mapped registers, V4L2/m2m/media devices, variant data, mutexes, IRQ lock, and watchdog work.

## Dependencies And Integration Points
The header binds Linux platform, V4L2, videobuf2 DMA-contig, media-controller, runtime codec headers from `hantro_hw.h`, and register IO primitives. Backend files include this header to share register helpers and buffer conventions.

## Risks And Test Signals
DMA addresses are truncated to 32 bits in `hantro_write_addr`, matching the driver mask; any future 64-bit DMA support must audit every caller. Postprocessor address selection changes decoded-buffer ownership, so regression tests should cover raw decode, postprocessed decode, and reference reuse. Compile coverage across enabled SoC variants is important because variant fields gate many optional paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_drv.c

## Purpose
Implements the platform driver, V4L2 mem2mem device lifecycle, queue initialization, control registration, codec job scheduling, IRQ completion handoff, watchdog timeout handling, media-controller topology, runtime PM, and device-tree matching for Hantro encoder/decoder instances.

## Important APIs, Types, And Functions
Public helpers include `hantro_get_ctrl`, `hantro_get_ref`, `hantro_irq_done`, `hantro_watchdog`, `hantro_start_prepare_run`, and `hantro_end_prepare_run`. Internal anchors include `device_run`, `queue_init`, `hantro_ctrls_setup`, `hantro_open`, `hantro_release`, `hantro_probe`, `hantro_remove`, and media entity helpers. The `controls[]` table declares JPEG, MPEG2, VP8, H264, HEVC, VP9, and AV1 stateless controls.

## Control Flow And State
Open allocates `hantro_ctx`, initializes V4L2 m2m queues, resets formats, and installs controls matching encoder or decoder capability bits from the variant. Job execution resumes runtime PM, enables clocks, copies source metadata to destination, and calls `ctx->codec_ops->run`. Codec runs call start/end prepare helpers to bind request controls and enable/disable postproc. Completion comes from IRQ or watchdog; it cancels work, invokes codec `done` on success, disables clocks, updates buffer sequences, handles EOS draining, and finishes the m2m job.

## Dependencies And Integration Points
The file integrates with platform DT compatibles, media controller links, V4L2 requests, videobuf2 DMA-contig queues, pm_runtime, clk/reset frameworks, and variant tables defined by SoC-specific files outside this work item.

## Risks And Test Signals
`device_run` uses `hantro_job_finish_no_pm` for all error exits, including after runtime PM or clocks may already be active; PM/clock error-path tests are useful. Control validation rejects unsupported H264 chroma/bit depth, HEVC bit depths outside 8/10, VP9 non-profile-0, and AV1 non-8/10. Important tests include request API decode, EOS draining, timeout reset, shared-device scheduling, media graph enumeration, and probe/remove under missing clocks/IRQs/register resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1.c

## Purpose
Provides common G1 decoder interrupt and reset handling used by G1 codec backends.

## Important APIs, Types, And Functions
`hantro_g1_irq` reads `G1_REG_INTERRUPT`, classifies completion as `VB2_BUF_STATE_DONE` when `DEC_RDY_INT` is set and error otherwise, clears the interrupt register, gates the decoder clock, and calls `hantro_irq_done`. `hantro_g1_reset` disables decoder IRQs, gates the clock, and writes the soft-reset register.

## Control Flow And State
The file has no persistent state of its own. It operates on `struct hantro_dev` register state and delegates job state transitions to the core driver. Reset is intended for watchdog or backend recovery paths via `ctx->codec_ops->reset`.

## Dependencies And Integration Points
Depends on `hantro.h` for register access and driver types and on `hantro_g1_regs.h` for bit definitions. Variants bind this IRQ handler through `struct hantro_irq`.

## Risks And Test Signals
All non-ready interrupts are collapsed to buffer error; this is simple but loses hardware status detail. Test signals include successful IRQ completion, error IRQ completion, watchdog-triggered reset, and ensuring clock gate writes do not race with the core completion path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_h264_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_h264_dec.c

## Purpose
Programs G1 decoder registers for stateless H.264 frame or field decode.

## Important APIs, Types, And Functions
The exported entry point is `hantro_g1_h264_dec_run`. Internal helpers `set_params`, `set_ref`, and `set_buffers` map V4L2 H.264 SPS/PPS/decode controls, prepared DPB state, reference lists, bitstream DMA, destination DMA, DMV buffer offset, and auxiliary table DMA into the G1 register file.

## Control Flow And State
`hantro_g1_h264_dec_run` first calls `hantro_h264_dec_prepare_run`, which latches request controls and builds DPB/reference-list state in `ctx->h264_dec`. It then writes decoder control registers for profile, interlace/field mode, picture size, QP offsets, stream length, CABAC/scaling flags, reference counts, reference picture numbers, list indexes, and DPB DMA addresses. After `hantro_end_prepare_run`, it programs common config and enables decode interrupt/start.

## Dependencies And Integration Points
Depends on the shared H.264 helper in `hantro_h264.c`, G1 register macros, V4L2 H.264 stateless controls, VB2 DMA addresses, and core postproc-aware `hantro_get_dec_buf_addr`.

## Risks And Test Signals
Reference-list packing assumes 16 entries and directly indexes arrays in fixed groups. Field decoding adjusts destination and DMV offsets; conformance tests should include MBAFF, bottom fields, long-term refs, monochrome high profile, scaling matrices, and missing/inactive DPB entries. Buffer sizing must account for appended motion-vector data for high-profile reference frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_h264_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_mpeg2_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_mpeg2_dec.c

## Purpose
Programs G1 decoder registers for stateless MPEG-2 decode.

## Important APIs, Types, And Functions
`hantro_g1_mpeg2_dec_run` is the backend entry point. `hantro_g1_mpeg2_dec_set_quantisation` copies the V4L2 quantisation control into the coherent hardware qtable buffer. `hantro_g1_mpeg2_dec_set_buffers` chooses forward/backward/current reference addresses and writes stream, output, reference, and qtable base registers.

## Control Flow And State
The run path applies request controls, fetches sequence and picture controls, writes G1 decode config, picture type/interlace/field flags, macroblock dimensions, MPEG-2 syntax options, stream length, f-code values, error-concealment start MB, APF threshold, quant table DMA, and buffer addresses. Missing forward/backward references fall back to the current destination buffer to keep hardware inputs valid.

## Dependencies And Integration Points
Integrates with `hantro_mpeg2_dec_copy_qtable` and `ctx->mpeg2_dec.qtable` allocation from `hantro_mpeg2.c`, plus core timestamp reference lookup through `hantro_get_ref`.

## Risks And Test Signals
Field-picture reference selection is branchy and depends on `TOP_FIELD_FIRST`; tests should cover I/P/B frames, top/bottom fields, progressive/interlaced sequences, alternate scan, concealment motion vectors, and absent reference timestamps. Stream payload length is masked to 24 bits by macros, so oversized inputs rely on higher-level format constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_mpeg2_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_regs.h

## Purpose
Defines G1 decoder and postprocessor register offsets and bitfield macros.

## Important APIs, Types, And Functions
The header is declarative. It provides `G1_SWREG`, interrupt/config/control register offsets, bitfield construction macros for H.264/MPEG2/VP8/JPEG-era decode features, reference address registers, qtable and motion-vector bases, soft reset, and G1 postprocessor register definitions.

## Control Flow And State
No runtime state lives here. The macros encode the contract between codec runners and hardware registers. Several register fields are reused by different codecs, so the same register offsets carry codec-specific meanings.

## Dependencies And Integration Points
Used by `hantro_g1.c`, G1 H.264/MPEG2/VP8 runners, and G1 postprocessor code. The macros assume Linux `BIT`, `GENMASK`, and standard integer types are available through includers.

## Risks And Test Signals
Because masks and shifts are hand-coded, a single off-by-one can silently corrupt decode. The reused fields increase maintenance risk when adding codecs or variants. Useful signals are hardware conformance suites per codec, register trace comparison against vendor BSPs, and build coverage for every includer using overlapping macro names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_vp8_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_vp8_dec.c

## Purpose
Programs G1 decoder registers and auxiliary buffers for stateless VP8 decode.

## Important APIs, Types, And Functions
`hantro_g1_vp8_dec_run` is the entry point. Helpers configure loop filter levels and deltas (`cfg_lf`), quantizer and segment deltas (`cfg_qp`), control/DCT partition addresses and start bits (`cfg_parts`), interpolation taps (`cfg_tap`), reference buffers (`cfg_ref`), segment/probability/output buffers (`cfg_buffers`).

## Control Flow And State
The run path applies request controls, clears the segment map on keyframes, updates VP8 probability tables through `hantro_vp8_prob_update`, writes common config and VP8 mode registers, configures dimensions and boolean decoder state, then derives aligned macroblock and DCT partition locations from userspace-provided frame control fields. It writes last/golden/alt reference addresses by timestamp, with fallback to destination when references are absent.

## Dependencies And Integration Points
Depends on V4L2 VP8 stateless frame controls, `ctx->vp8_dec.segment_map`, `ctx->vp8_dec.prob_tbl`, G1 register maps, shared MC filter table `hantro_vp8_dec_mc_filter`, and VB2 DMA-contig buffers.

## Risks And Test Signals
Partition arithmetic is sensitive to byte/bit alignment, keyframe header length, number of DCT partitions, and buffer payload correctness. Segmentation and loop-filter delta paths need regression coverage. Test vectors should include keyframes, interframes with missing refs, 1/2/4/8 DCT partitions, segmentation map updates, simple vs normal loop filters, and all interpolation versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g1_vp8_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2.c

## Purpose
Provides common G2 decoder interrupt/reset behavior and shared decoded-buffer layout calculations for G2 codecs.

## Important APIs, Types, And Functions
Exports `hantro_g2_irq`, `hantro_g2_reset`, `hantro_g2_check_idle`-adjacent reset behavior through active polling, and offset helpers `hantro_g2_chroma_offset`, `hantro_g2_motion_vectors_offset`, `hantro_g2_luma_compress_offset`, and `hantro_g2_chroma_compress_offset`.

## Control Flow And State
`hantro_g2_irq` validates the IRQ bit, clears interrupt status via masked register writes, gates clock, finishes success on `DEC_RDY_INT`, logs recoverable/error status bits, and only reports buffer error once the hardware is no longer running. `hantro_g2_reset` uses hardware abort and waits until decode enable clears to avoid programming a running block.

## Dependencies And Integration Points
Used by G2 HEVC and VP9 backends and variants. Offset helpers depend on negotiated `ref_fmt`, HEVC SPS-derived MV sizing, and compressed reference-size helpers from `hantro_hw.h`.

## Risks And Test Signals
The reset path busy-waits with `mdelay(1)` until inactive and warns that programming a running IP can hang the CPU. Tests should cover successful IRQ, bus/error/timeout IRQ status, abort handling, watchdog reset, and buffer-size calculations for 8-bit/10-bit HEVC with and without compression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_hevc_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_hevc_dec.c

## Purpose
Programs G2 decoder registers, reference address tables, tile metadata, scaling lists, stream buffer, and postprocessed/compressed output settings for stateless HEVC decode.

## Important APIs, Types, And Functions
The exported entry is `hantro_g2_hevc_dec_run`. Helpers include `prepare_tile_info_buffer`, `compute_header_skip_length`, `set_params`, `set_ref_pic_list`, `set_ref`, `set_buffers`, and `prepare_scaling_list_buffer`.

## Control Flow And State
The run path calls `hantro_hevc_dec_prepare_run`, writes SPS/PPS/decode-derived bit depths, coding-block sizes, picture dimensions, transform hierarchy, deblocking/SAO/PCM/tiles/list flags, reference list indexes, POC deltas, long-term bitmaps, current and reference luma/chroma/MV/compression addresses, stream length and tile buffer addresses, tile-size memory, and scaling lists. It then enables HEVC mode, clock gating, output, optional reference compression, bus width, swaps, and decode start.

## Dependencies And Integration Points
Relies on `hantro_hevc.c` for control latching, tile buffer allocation, reference POC-to-DMA tracking, and compression policy. Uses G2 register descriptors from `hantro_g2_regs.h`, VB2 DMA buffers, and V4L2 HEVC stateless controls.

## Risks And Test Signals
`set_ref` returns errors if referenced POCs are not known, so DPB control correctness is critical. Tile memory layout and scaling-list ordering are hardware-specific. Tests should cover IDR and non-IDR frames, long-term refs, missing refs, tiles with uniform and explicit spacing, PCM, SAO/deblock flags, 8/10-bit streams, NV12_4L4 validation, and compression enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_hevc_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_regs.h

## Purpose
Defines G2 register descriptors, mode constants, interrupt bits, codec-specific fields for HEVC and VP9, address registers, postprocessor/downscale fields, and stream-buffer extension registers.

## Important APIs, Types, And Functions
The key macro is `G2_DEC_REG`, which constructs `struct hantro_reg` descriptors for masked read-modify-write helpers. It declares descriptors such as `g2_mode`, `g2_stream_len`, HEVC reference-list fields, VP9 segmentation/filter/reference-scale fields, output/RS/downscale fields, and address offsets like `G2_OUT_LUMA_ADDR`, `G2_REF_LUMA_ADDR(i)`, and `G2_VP9_PROBS_ADDR`.

## Control Flow And State
No runtime state is stored. The header centralizes the G2 hardware ABI. Some descriptors have legacy and non-legacy variants, and some register numbers are reused by HEVC POC fields and VP9 filter-delta fields depending on decode mode.

## Dependencies And Integration Points
Included by `hantro_g2.c`, G2 HEVC/VP9 runners, and postprocessor code. It depends on `hantro.h` for `struct hantro_reg`.

## Risks And Test Signals
Register descriptor reuse makes accidental cross-codec changes risky. Legacy vs new register fields need SoC-specific test coverage. Useful signals include register dumps from G2 HEVC/VP9 runs, conformance suites on legacy and non-legacy variants, and tests for downscale/postprocessor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_vp9_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_vp9_dec.c

## Purpose
Implements G2 VP9 stateless decode, including register programming, probability-table upload, segmentation state, tile metadata, reference scaling, source alignment, and post-decode probability adaptation from hardware counters.

## Important APIs, Types, And Functions
Exports `hantro_g2_vp9_dec_run` and `hantro_g2_vp9_dec_done`. Major helpers include `start_prepare_run`, `get_ref_buf`, `config_output`, `config_ref_registers`, `config_tiles`, `config_segment`, `config_loop_filter`, `config_picture_dimensions`, `config_bit_depth`, `config_quant`, `config_others`, `config_compound_reference`, `config_probs`, `config_counts`, `config_seg_map`, and `config_source`.

## Control Flow And State
Preparation latches VP9 frame and compressed-header controls, resets/loads frame context state, and applies firmware-style probability updates. Register config updates the destination metadata, chooses a motion-vector reference, writes G2 VP9 mode/swap/burst settings, output and reference addresses/scales/sign biases, tile info, segmentation features, loop filter, dimensions, bit depth, quant deltas, temporal MVP/write-MV flags, compound reference registers, probability table DMA, counter DMA, segment map ping-pong addresses, and aligned stream start/length. Completion optionally adapts coefficient and non-coefficient probabilities from hardware counters and stores the refreshed frame context, then updates `last`.

## Dependencies And Integration Points
Uses V4L2 VP9 helpers, `hantro_vp9.h` probability layouts, G2 register descriptors, VB2 timestamp lookup, per-buffer `hantro_decoded_buffer.vp9` metadata, and core codec `done` callback dispatch.

## Risks And Test Signals
Stateful VP9 behavior is complex: frame contexts, segmentation feature data, active segment map, tile geometry caches, reference dimensions, and last-frame state must survive across jobs. Test signals include keyframe reset, intra-only, error-resilient, parallel decode, frame-context refresh, resolution change, segmentation update/no-update, missing refs, legacy/non-legacy registers, tiled frames, and probability adaptation conformance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_vp9_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_jpeg_enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_jpeg_enc.c

## Purpose
Programs H1 encoder registers for JPEG encode and updates capture-buffer payload after hardware completion.

## Important APIs, Types, And Functions
Exports `hantro_h1_jpeg_enc_run` and `hantro_h1_jpeg_enc_done`. Helpers configure source image format/overfill (`hantro_h1_set_src_img_ctrl`), output/input DMA buffers (`hantro_h1_jpeg_enc_set_buffers`), and luma/chroma quantization table registers (`hantro_h1_jpeg_enc_set_qtable`).

## Control Flow And State
The run path applies request controls, assembles a JPEG header directly into the destination buffer via `hantro_jpeg_header_assemble`, switches the encoder to JPEG mode, writes source format, stream output address after the header, remaining output capacity, source plane addresses, quant tables, AXI swap/burst settings, and finally starts JPEG intra encode. The done callback reads the hardware stream-limit register, converts bits to bytes, and sets capture payload to header size plus encoded bytes.

## Dependencies And Integration Points
Uses H1 register macros, VB2 DMA addresses and CPU mapping for the JPEG destination header, negotiated V4L2 formats from `hantro_v4l2`, and the JPEG helper context from `hantro_jpeg.h`.

## Risks And Test Signals
The destination queue must be CPU-mapped for header writes, unlike decoder queues. Header size is subtracted from output capacity; undersized buffers trigger warnings and zero capacity. Tests should cover one-, two-, and three-plane source formats, crop/overfill dimensions, different JPEG quality values, exact/too-small output buffers, and payload accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_jpeg_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_regs.h

## Purpose
Defines H1 encoder register offsets and bitfield macros, including common AXI/interrupt fields, JPEG mode controls, input image controls, stream limits, quantization table addresses, and additional H264/VP8-era encoder fields.

## Important APIs, Types, And Functions
This header is declarative. JPEG code uses `H1_REG_INTERRUPT`, `H1_REG_AXI_CTRL`, `H1_REG_ADDR_OUTPUT_STREAM`, `H1_REG_STR_BUF_LIMIT`, `H1_REG_ADDR_IN_PLANE_*`, `H1_REG_ENC_CTRL`, `H1_REG_IN_IMG_CTRL`, `H1_REG_JPEG_LUMA_QUAT(i)`, and `H1_REG_JPEG_CHROMA_QUAT(i)`.

## Control Flow And State
No runtime state is stored. The macros define how encoder backends compose register values and address offsets. Several definitions support codecs not in this work item, so changes affect a wider encoder surface.

## Dependencies And Integration Points
Included by H1 JPEG encode code and other H1 encoder paths. It assumes standard `BIT` style macros through includers.

## Risks And Test Signals
Contiguous quant-table register ordering is required by hardware and called out by the JPEG encoder. Regression signals include JPEG register traces, payload-size correctness, and compile coverage for other H1 encoder code that shares these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h264.c

## Purpose
Maintains H.264 decoder auxiliary memory and per-context DPB/reference-list state shared by H.264 hardware backends.

## Important APIs, Types, And Functions
Exports `hantro_h264_dec_init`, `hantro_h264_dec_exit`, `hantro_h264_dec_prepare_run`, `hantro_h264_get_ref_buf`, and `hantro_h264_get_ref_nbr`. Internal helpers assemble scaling lists, prepare CABAC/POC/scaling auxiliary table data, update the persistent DPB, and deduplicate field reference lists.

## Control Flow And State
Initialization allocates a coherent private table and copies the static CABAC initialization table. Each prepare run applies request controls, validates required controls are present, updates the context DPB by matching V4L2 DPB entries by `reference_ts`, computes valid and long-term bitmaps, stores current POC fields, copies scaling matrices if present, builds P and B reference lists with V4L2 helpers, and deduplicates field references to hardware-sized lists.

## Dependencies And Integration Points
Uses V4L2 H.264 stateless controls and reflist builder helpers, VB2 timestamp-based reference lookup through `hantro_get_ref`, postprocessor-aware decoded-buffer addresses, and the G1 H.264 runner that consumes prepared fields and auxiliary DMA.

## Risks And Test Signals
DPB matching by timestamp is central; bad timestamps produce fallback current-buffer references. Field deduplication is explicitly trial-and-error based and should be guarded by conformance tests. Test vectors should include frame/field pictures, MBAFF, long-term refs, reordered refs, scaling matrices, CABAC/CAVLC, missing refs, and stream sequences that reuse DPB slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hevc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hevc.c

## Purpose
Manages HEVC decoder per-context auxiliary buffers, tile-buffer reallocation, control latching, SPS validation, reference-buffer tracking by POC, and reference-compression policy.

## Important APIs, Types, And Functions
Exports `hantro_hevc_dec_init`, `hantro_hevc_dec_exit`, `hantro_hevc_dec_prepare_run`, `hantro_hevc_ref_init`, `hantro_hevc_get_ref_buf`, and `hantro_hevc_add_ref_buf`. Internal helpers include `tile_buffer_reallocate` and `hantro_hevc_validate_sps`.

## Control Flow And State
Initialization zeroes the HEVC context, allocates tile-size and scaling-list buffers, resets reference tracking, and sets `use_compression` from the module parameter and postproc need. Prepare run applies request controls, fetches decode/scaling/SPS/PPS controls, validates tiled output format dimensions, and reallocates tile edge/filter/SAO/BSD buffers when PPS tile columns exceed prior allocation. Reference tracking uses `ref_bufs_poc`, `ref_bufs`, and `ref_bufs_used` to map POC values to DMA addresses across frames.

## Dependencies And Integration Points
Consumed by `hantro_g2_hevc_dec.c`, relies on V4L2 HEVC stateless controls, DMA coherent allocation, negotiated `ctx->bit_depth`, postprocessor decisions, and the optional `CONFIG_VIDEO_HANTRO_HEVC_RFC`.

## Risks And Test Signals
On init failure after tile-size allocation, scaling-list allocation failure currently returns without freeing the first buffer until context cleanup paths run. Tile reallocation frees old buffers before fully allocating replacements, so allocation failure can degrade later decode until retried. Tests should cover changing tile column counts, NV12_4L4 dimension validation, compression on/off, ref POC reuse/eviction, and 8/10-bit streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hevc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hw.h

## Purpose
Declares codec-specific hardware contexts, auxiliary DMA buffer type, codec/postproc operation tables, exported backend symbols, dimension constants, and helper functions for buffer-size/layout calculations.

## Important APIs, Types, And Functions
Important structs include `hantro_aux_buf`, `hantro_h264_dec_hw_ctx`, `hantro_hevc_dec_hw_ctx`, `hantro_mpeg2_dec_hw_ctx`, `hantro_vp8_dec_hw_ctx`, `hantro_vp9_dec_hw_ctx`, `hantro_av1_dec_hw_ctx`, `hantro_postproc_ctx`, `hantro_postproc_ops`, and `hantro_codec_ops`. Inline helpers compute macroblock/superblock counts, VP9/H264/HEVC/AV1 motion-vector sizes, and HEVC compressed luma/chroma sizes.

## Control Flow And State
The header defines the persistent per-codec state embedded in `hantro_ctx`: DPB/reference lists, coherent aux buffers, VP9 frame contexts and segmentation state, HEVC tile/reference/compression state, and AV1 reference/probability state. `hantro_codec_ops` establishes the core lifecycle: optional init/exit, per-job run, optional done, and timeout reset.

## Dependencies And Integration Points
Integrates Linux interrupts, V4L2 controls, VP9 helpers, VB2, AV1 probability headers, variant declarations, and all codec backend prototypes. It is the main compile-time contract between platform variants, core driver, postprocessor, and codec files.

## Risks And Test Signals
Size helpers drive buffer allocation; wrong formulas can cause DMA overruns or hardware faults. `hantro_h264_mv_size` uses macroblock width twice, which should be reviewed against expected width-by-height sizing and test coverage. ABI-like struct fields are private but broadly shared, so changes need full codec build and conformance coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.c

## Purpose
Builds a baseline JPEG header and hardware-ordered quantization tables for Hantro JPEG encode.

## Important APIs, Types, And Functions
Exports `hantro_jpeg_header_assemble`. Internal pieces include the fixed padded `hantro_jpeg_header`, `hw_reorder`, `jpeg_scale_qp`, `jpeg_scale_quant_table`, and `jpeg_set_quality`. Fixed offsets patch luma/chroma quant tables, height, width, and Huffman tables in the header template.

## Control Flow And State
The assembler copies the template into the caller-provided destination buffer, writes image height/width, copies V4L2 reference Huffman tables, and computes quality-scaled quantization tables. It stores file-order quant tables into the JPEG header and hardware-order quant tables into `ctx->hw_luma_qtable` and `ctx->hw_chroma_qtable` for register programming by H1 JPEG code.

## Dependencies And Integration Points
Uses `media/v4l2-jpeg.h` reference quant/Huffman tables, `hantro_jpeg.h` context definitions, and H1 encoder code that guarantees the destination buffer is CPU-accessible and reserves `JPEG_HEADER_SIZE` bytes before hardware output.

## Risks And Test Signals
The implementation depends on fixed offsets into a static header; static assertions guard only total size and alignment. Any header-template edit must update offsets. Tests should verify generated JPEG headers parse, width/height bytes are correct, quant tables match quality scaling, SOS payload remains 8-byte aligned, and hardware quant register order matches expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.h

## Purpose
Declares the small JPEG helper contract used by Hantro JPEG encoder backends.

## Important APIs, Types, And Functions
Defines `JPEG_HEADER_SIZE`, `JPEG_QUANT_SIZE`, `struct hantro_jpeg_ctx`, and `hantro_jpeg_header_assemble`. The context carries width, height, quality, output buffer pointer, and hardware-ordered luma/chroma quantization tables.

## Control Flow And State
No persistent state is stored here. A caller fills a stack or transient `hantro_jpeg_ctx`, points `buffer` at the capture buffer, and calls the assembler. The helper writes the software JPEG header and populates quant tables for subsequent register writes.

## Dependencies And Integration Points
Used directly by `hantro_jpeg.c` and `hantro_h1_jpeg_enc.c`. `JPEG_HEADER_SIZE` must match the static header size in the C file and the V4L2 format `header_size` used by the encoder path.

## Risks And Test Signals
The API trusts the caller to provide a buffer at least `JPEG_HEADER_SIZE` bytes. Tests should cover format negotiation exposing the same header size, encoder handling of undersized buffers, and quality/path values that fill both hardware quant table arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_mpeg2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_mpeg2.c

## Purpose
Provides shared MPEG-2 decoder auxiliary quantization-table handling.

## Important APIs, Types, And Functions
Exports `hantro_mpeg2_dec_copy_qtable`, `hantro_mpeg2_dec_init`, and `hantro_mpeg2_dec_exit`. The file includes a MPEG-style zigzag permutation table used to place four 64-entry quantizer matrices into hardware memory.

## Control Flow And State
Initialization allocates a coherent 256-byte qtable buffer in `ctx->mpeg2_dec.qtable`. Each run-side caller copies intra, non-intra, chroma-intra, and chroma-non-intra matrices from the V4L2 quantisation control into zigzag-addressed regions. Exit frees the coherent buffer.

## Dependencies And Integration Points
Used by G1 and Rockchip VPU2 MPEG-2 runners. Depends on V4L2 MPEG-2 stateless quantisation controls and DMA coherent allocation through `ctx->dev`.

## Risks And Test Signals
`hantro_mpeg2_dec_copy_qtable` silently returns if buffer or control is null, so caller-side control validation is important. Tests should cover default and custom quant matrices, all four matrix regions, init allocation failure, and decode conformance with alternate scan streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_mpeg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_postproc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_postproc.c

## Purpose
Implements Hantro G1/G2 postprocessor enable/disable, downscale frame-size enumeration, intermediate decode-buffer allocation, and postproc-aware decoded-buffer address selection.

## Important APIs, Types, And Functions
Exports `hantro_needs_postproc`, `hantro_postproc_init`, `hantro_postproc_free`, `hantro_postproc_get_dec_buf_addr`, `hantro_postproc_enable`, `hantro_postproc_disable`, `hanto_postproc_enum_framesizes`, `hantro_g1_postproc_ops`, and `hantro_g2_postproc_ops`. Internal helpers configure G1 pipeline registers, G2 raster/downscale output, buffer sizing, and DMA allocation.

## Control Flow And State
Postproc need is true for decoder contexts when forced by bitstream/controls or destination format metadata. Init allocates intermediate decoder buffers per capture buffer. Address selection reallocates per-index buffers if size requirements grow, otherwise returns the intermediate DMA address. G1 enable programs pipeline mode and YUYV output. G2 enable either writes downscale destinations or raster-scan output addresses, then configures output bit depth/format and enables RS output.

## Dependencies And Integration Points
Uses G1/G2 register descriptors, `hantro_v4l2` format-depth helpers, VB2 capture queues, codec motion-vector size helpers from `hantro_hw.h`, and variant `postproc_ops`.

## Risks And Test Signals
Intermediate buffer sizing must include codec-specific MV and optional HEVC compression data. G1 has a suspicious `input_height_ext` expression using `MB_HEIGHT(ctx->dst_fmt.height >> 8)` rather than shifting the macroblock height result; this deserves review. Tests should cover postprocessed YUYV, G2 downscale indices 0-3, 10-bit output, HEVC compression, buffer growth reallocation, and disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_postproc.c -->
