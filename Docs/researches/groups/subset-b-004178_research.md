# subset-b-004178 research

This grouped report covers the requested Hantro VPU V4L2, VP8, VP9, i.MX8M variant, and Rockchip AV1 helper files. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.c

## Purpose
`hantro_v4l2.c` implements the V4L2 mem2mem ioctl and vb2 queue-facing contract for the Hantro VPU driver. It mediates format enumeration, try/set/get format operations, crop/selection, encoder stop/start commands, buffer setup, buffer validation, queueing, and stream lifecycle initialization for encoder and stateless decoder contexts.

## Important APIs, Types, And Functions
The file exports `hantro_ioctl_ops`, `hantro_queue_ops`, `hantro_reset_raw_fmt`, `hantro_reset_fmts`, `hantro_get_format_depth`, and `hantro_get_default_fmt`. Format selection is centered on `hantro_get_formats`, `hantro_get_postproc_formats`, `hantro_find_format`, `hantro_check_depth_match`, `hantro_try_fmt`, `hantro_set_fmt_out`, and `hantro_set_fmt_cap`. Queue lifecycle is handled by `hantro_queue_setup`, `hantro_buf_prepare`, `hantro_buf_queue`, `hantro_start_streaming`, `hantro_stop_streaming`, and request completion helpers.

## Control Flow
Applications enter through V4L2 ioctl callbacks. Enumeration filters formats by encoder/decoder direction, coded/raw side, bit depth, and optional postprocessor formats. `TRY_FMT` normalizes unsupported fourcc values to defaults, applies frame-size constraints, fills raw multi-plane layout, and adds codec-specific motion-vector side data to capture buffers when no postprocessor is used. `S_FMT` validates busy/streaming restrictions, commits source or destination format state, propagates colorimetry, resets the peer raw format when codec/depth changes, and updates request/hold-capture-buffer flags. Streaming start selects codec ops from the hardware variant based on the coded queue, runs codec init, and optionally initializes postprocessing; streaming stop tears down postprocessing and codec state and returns queued buffers with error status.

## State And Persistence
State is per `struct hantro_ctx`: source, destination, reference, VPU source/destination format pointers, bit depth, postprocessing need, codec ops pointer, and capture/output sequence counters. vb2 queue flags are updated to express request requirements and H264 hold-capture-buffer support. No state is persistent across device close; DMA and codec-private state are initialized and released through codec ops during streaming.

## Dependencies And Integration Points
The file integrates Linux V4L2, v4l2-ctrls, v4l2-event, v4l2-mem2mem, and videobuf2 APIs. It depends on Hantro core definitions from `hantro.h`, hardware sizing helpers from `hantro_hw.h`, postprocessor helpers such as `hantro_needs_postproc`, and codec motion-vector size helpers for H264, VP9, HEVC, and AV1. Hardware variants provide format tables, postprocessor format tables, and `codec_ops` arrays.

## Risks
Format state is highly order-sensitive: changing coded formats resets raw formats, and decoder dynamic resolution changes only allow pixelformat stability while streaming. Incorrect `sizeimage` calculation can underallocate buffers, especially for non-postprocessed capture formats carrying motion-vector data. Bit-depth filtering must stay aligned with variant format tables, because postprocessed formats currently allow only downconversion unless `match_depth` is set. Request and hold-capture-buffer flags are codec-specific and can break stateless decoding if updated incompletely for new formats.

## Test Signals
Useful signals include V4L2 compliance on mem2mem devices, format enumeration and `TRY_FMT`/`S_FMT` tests for encoder and decoder directions, streaming tests for EOS behavior, dynamic resolution change tests on decoder OUTPUT, and codec decode/encode tests that verify capture buffer sizing for H264, VP9, HEVC, and AV1 with and without postprocessing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.h

## Purpose
`hantro_v4l2.h` declares the public V4L2-facing helpers and operation tables implemented by `hantro_v4l2.c`. It is the small interface used by the Hantro core and codec setup code to reset default formats, query bit depth, and bind ioctl/vb2 operations to video devices.

## Important APIs, Types, And Functions
The header defines `HANTRO_FORCE_POSTPROC` and `HANTRO_AUTO_POSTPROC` as boolean policy values passed into raw-format selection. It declares `hantro_ioctl_ops`, `hantro_queue_ops`, `hantro_reset_raw_fmt`, `hantro_reset_fmts`, `hantro_get_format_depth`, and `hantro_get_default_fmt`.

## Control Flow
Driver initialization uses the exported operation tables when registering the V4L2 mem2mem video device. Context setup and format reset paths call `hantro_reset_fmts` or `hantro_reset_raw_fmt`; codec-specific or postprocessor-aware paths use `hantro_get_default_fmt` and `hantro_get_format_depth` to select compatible raw formats.

## State And Persistence
The header defines no storage. It exposes functions that mutate per-context format state in `struct hantro_ctx`, including source/destination formats, bit depth, and postprocessing flags.

## Dependencies And Integration Points
It includes `hantro.h` for `struct hantro_ctx` and `struct hantro_fmt`, and relies on V4L2/vb2 operation types made visible through that driver context. It is included by Hantro core files that need to wire device operations or reset format state.

## Risks
Because the postprocessor policy macros are plain booleans, callers must pass them in the intended semantic position; swapping them with unrelated boolean arguments would be easy during refactors. Any signature change here affects multiple driver registration and context setup paths.

## Test Signals
Build coverage is the main direct signal. Runtime validation comes from successful V4L2 device registration and format reset behavior on open, `S_FMT`, and codec changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp8.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp8.c

## Purpose
`hantro_vp8.c` provides VP8 decoder support data and context allocation for the Hantro G1 path. It packs V4L2 VP8 entropy probabilities into the hardware layout, exposes the VP8 motion compensation filter taps, and allocates/frees per-context DMA buffers for the segment map and probability table.

## Important APIs, Types, And Functions
`struct vp8_prob_tbl_packed` describes the hardware probability table layout. `hantro_vp8_dec_mc_filter` exports the 8-by-6 interpolation filter coefficients. `hantro_vp8_prob_update` copies fields from `struct v4l2_ctrl_vp8_frame` into the packed probability DMA buffer. `hantro_vp8_dec_init` allocates the segment map and probability table buffers, and `hantro_vp8_dec_exit` releases them.

## Control Flow
Codec init computes macroblock dimensions from `ctx->dst_fmt`, rounds the segment map size to hardware alignment, allocates coherent DMA for the segment map, then allocates coherent DMA for the packed probability table. On allocation failure it unwinds the already allocated segment map. Before a frame is run, `hantro_vp8_prob_update` writes skip, intra, reference, segment, luma/chroma mode, motion-vector, and coefficient probabilities into fixed byte offsets in `ctx->vp8_dec.prob_tbl.cpu`.

## State And Persistence
State is per decoder context in `ctx->vp8_dec.segment_map` and `ctx->vp8_dec.prob_tbl`. Both are coherent DMA buffers used by hardware and are valid only between codec init and exit. Probability contents are refreshed from frame controls; segment map contents are initialized by coherent allocation and used across VP8 frame processing as hardware scratch/reference state.

## Dependencies And Integration Points
The file depends on `hantro.h`, V4L2 VP8 frame control definitions, Linux DMA coherent allocation, and constants such as `V4L2_VP8_MV_PROB_CNT` and `V4L2_VP8_COEFF_PROB_CNT`. It is referenced by variant codec ops, including i.MX8M G1 VP8 decode entries, and by G1 VP8 register programming code that consumes the DMA addresses.

## Risks
The packed probability layout is offset-sensitive and has explicit padding; any mismatch with hardware register expectations will produce decode corruption rather than obvious build failures. The segment map sizing depends on macroblock dimensions and 64-byte alignment. Exit assumes buffers were allocated by init; changes to partial-init behavior must preserve safe unwind and free semantics.

## Test Signals
Signals include VP8 decode conformance streams with segmentation enabled, streams that update entropy probabilities, DMA mapping diagnostics, and memory-leak/error-unwind tests around codec init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.c

## Purpose
`hantro_vp9.c` initializes and releases the VP9 decoder hardware context for Hantro G2, including tile-edge scratch space, BSD control storage, double-buffered segment maps, probability tables, symbol-count tables, and tile information. It also maps the hardware symbol-count memory into the V4L2 VP9 count table pointer structure used by shared VP9 probability update logic.

## Important APIs, Types, And Functions
Size helpers include `hantro_vp9_tile_filter_size`, `hantro_vp9_bsd_control_size`, `hantro_vp9_segment_map_size`, `hantro_vp9_prob_tab_size`, `hantro_vp9_count_tab_size`, and `hantro_vp9_tile_info_size`. `init_v4l2_vp9_count_tbl` initializes pointer fields in `ctx->vp9_dec.cnts`. `hantro_vp9_dec_init` allocates and zeros the coherent DMA buffers, while `hantro_vp9_dec_exit` frees them. Internal helpers `get_coeffs_arr` and `get_eobs1` select coefficient/eob count arrays for transform sizes.

## Control Flow
Initialization first verifies the hardware variant advertises `V4L2_PIX_FMT_VP9_FRAME`, then derives maximum VP9 frame dimensions from the variant format table rather than the current stream. It allocates tile-edge plus BSD control memory as one block with `bsd_ctrl_offset`, allocates two segment-map areas in one block for alternating use, and allocates a misc block containing probabilities, counters, and tile info with recorded offsets. After zeroing all buffers, it binds V4L2 count pointers into the counter region inside `misc`. Failure paths free earlier allocations in reverse order.

## State And Persistence
Per-context state lives in `ctx->vp9_dec`: coherent DMA buffers, offsets into those buffers, segment map size, and pointer aliases into the count table. Segment maps are double-buffered across frames. Probability and counter memory is transient hardware state for the active context and is released at stream stop through codec exit.

## Dependencies And Integration Points
The file includes `hantro.h`, `hantro_hw.h`, and `hantro_vp9.h`. It depends on G2 VP9 hardware register programming and completion paths, variant format tables, Linux DMA coherent allocation, and the V4L2 mem2mem stateless VP9 controls that consume the initialized `cnts` structure.

## Risks
Buffer sizes are derived from maximum variant dimensions and hard-coded tile limits, so format table changes can alter DMA footprint. The count table pointer setup is sensitive to `struct symbol_counts` layout; a mismatch with hardware output or the V4L2 VP9 library's expected pointer shape would break adaptive probability updates. `tx16x16_count` has a documented shape mismatch with the API, requiring special handling elsewhere.

## Test Signals
VP9 conformance streams with many tiles, segmentation, adaptive probability updates, and maximum-resolution frames are important. Fault-injection around coherent allocation should verify unwind paths. Debugging should inspect tile/BSD offsets, segment-map toggling, and symbol-count propagation after decode completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.h

## Purpose
`hantro_vp9.h` defines the hardware memory layouts used by the Hantro G2 VP9 decoder for probabilities and symbol counts. It is consumed by VP9 context initialization and register/probability programming paths that exchange probability tables and count tables with the hardware.

## Important APIs, Types, And Functions
`struct hantro_g2_mv_probs` models motion-vector probability storage. `struct hantro_g2_probs` contains inter/intra mode, transform, partition, interpolation, reference, skip, MV, and coefficient probability arrays. `struct hantro_g2_all_probs` wraps keyframe-specific probability tables plus `hantro_g2_probs`. `struct mv_counts` and `struct symbol_counts` define the hardware-written count tables for probability adaptation.

## Control Flow
The header contains no executable code. `hantro_vp9_dec_init` uses `sizeof(struct hantro_g2_all_probs)` and `sizeof(struct symbol_counts)` to size the misc DMA area, then pointer-maps fields in `struct symbol_counts` into the V4L2 VP9 count abstraction. G2 VP9 run/done paths use the same structures when programming and reading hardware probability/count state.

## State And Persistence
These structures describe in-memory coherent DMA contents, not persistent storage. Their binary layout is effectively an ABI between the driver and hardware, so field order, padding, and dimensions are part of the state contract.

## Dependencies And Integration Points
The header relies on fixed-width integer types being available from includers. It is included by `hantro_vp9.c` and G2 VP9 hardware code. It bridges Hantro hardware memory format with V4L2 stateless VP9 probability/count update logic.

## Risks
Changing dimensions, field order, or implicit padding can silently corrupt hardware programming. The count arrays for different transform sizes must remain synchronized with `init_v4l2_vp9_count_tbl` and any VP9 library expectations. There are no compile-time layout assertions in this header.

## Test Signals
Build coverage catches type visibility issues, but functional signals require VP9 decode tests with adaptive entropy updates, motion-vector-heavy inter frames, and coefficient count readback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/imx8m_vpu_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/imx8m_vpu_hw.c

## Purpose
`imx8m_vpu_hw.c` describes the NXP i.MX8M Hantro VPU hardware variants. It provides SoC control-register reset/clock helpers, supported G1/G2 format tables, codec operation tables, IRQ/clock/register resource names, shared-device matching, and exported `hantro_variant` definitions for i.MX8MQ and i.MX8MM VPU instances.

## Important APIs, Types, And Functions
Low-level helpers are `imx8m_soft_reset`, `imx8m_clk_enable`, `imx8mq_runtime_resume`, `imx8mq_vpu_hw_init`, and `imx8m_vpu_g1_reset`. Format tables include `imx8m_vpu_dec_fmts`, `imx8m_vpu_postproc_fmts`, `imx8m_vpu_g2_dec_fmts`, and `imx8m_vpu_g2_postproc_fmts`. Codec op arrays map Hantro modes to G1/G2 run/init/exit/reset/done functions. Exported variants are `imx8mq_vpu_variant`, `imx8mq_vpu_g1_variant`, `imx8mq_vpu_g2_variant`, and `imx8mm_vpu_g1_variant`.

## Control Flow
For the combined i.MX8MQ variant, hardware init records the control register base as the last mapped register range. Runtime resume enables all clocks, soft-resets G1 and G2, enables both block clocks in the control register, writes fuse registers to expose decoder/postprocessor capabilities, then disables clocks again. During V4L2 context setup, the core uses the selected variant's format tables and codec ops; stream start later invokes the run/init/exit callbacks selected by codec mode.

## State And Persistence
Persistent driver configuration is static const variant data. Runtime mutable state is limited to MMIO writes under `vpu->ctrl_base` and clock state during resume/reset. Format and codec capability state is not dynamically discovered; it is encoded in these tables.

## Dependencies And Integration Points
The file depends on Linux clock and delay APIs, Hantro core definitions, JPEG/G1/G2 register headers, postprocessor ops, G1 MPEG2/VP8/H264 decode paths, and G2 HEVC/VP9 decode paths. Device-tree compatible matching elsewhere selects these exported variants and resource-name arrays.

## Risks
Resource array ordering matters: the combined variant assumes the control range is the last register base. Fuse register writes are hard-coded to all ones, so changes to control register semantics could advertise unsupported blocks. Split G1/G2 variants use shared device matching, making device-tree binding and clock/resource naming regressions likely if names drift. Format max dimensions and bit-depth/match-depth flags directly affect V4L2 negotiation.

## Test Signals
Probe/runtime-PM tests on i.MX8MQ and i.MX8MM are key. Decode smoke tests should cover MPEG2, VP8, H264 on G1 and HEVC/VP9 on G2, plus postprocessed NV12/YUYV/P010 negotiation where supported. Device-tree resource-name and clock-name validation should accompany binding changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/imx8m_vpu_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.c

## Purpose
`rockchip_av1_entropymode.c` supplies Rockchip/Hantro AV1 default entropy CDF tables and helper functions for initializing, selecting, and storing AV1 CDF state. Most of the file is static default probability data derived from AOM AV1 tables; the executable surface copies those defaults into hardware-facing CDF structures and manages per-reference-frame CDF snapshots.

## Important APIs, Types, And Functions
The file defines `AOM_CDF*` conversion macros around `ICDF`, many `static const u16` default CDF arrays for AV1 intra/inter modes, transforms, palette, skip, references, motion vectors, coefficient bases, eob flags, and quantizer-context coefficient probabilities. `rockchip_av1_get_q_ctx` maps base quantizer values to one of four coefficient table contexts. Exported functions are `rockchip_av1_default_coeff_probs`, `rockchip_av1_set_default_cdfs`, `rockchip_av1_get_cdfs`, and `rockchip_av1_store_cdfs`.

## Control Flow
Default initialization begins with callers providing `struct av1cdfs` and non-DV motion-vector CDF storage. `rockchip_av1_set_default_cdfs` bulk-copies every non-quantizer-selected default table into the target structures, including regular MV CDFs and intrabc/non-DV MV CDFs. `rockchip_av1_default_coeff_probs` chooses a quantizer context using thresholds 20, 60, and 120, then copies coefficient, txb-skip, eob, dc-sign, and br/base tables for that context. During decode, `rockchip_av1_get_cdfs` points the active AV1 context at a reference frame's saved CDFs. After decode, `rockchip_av1_store_cdfs` copies the active CDFs into every reference slot selected by `refresh_frame_flags`, skipping self-copy when the active pointer already targets that slot.

## State And Persistence
Static default tables are read-only kernel data. Runtime CDF state lives in `ctx->av1_dec`: active CDF pointers, arrays of last CDFs per reference frame, and non-DV motion-vector CDF snapshots. This state persists only across frames within an open decode context and models AV1 reference-frame entropy adaptation.

## Dependencies And Integration Points
The file includes `hantro.h` and `rockchip_av1_entropymode.h`. It depends on the header's AV1 constants and `struct av1cdfs`/`struct mvcdfs` layout. AV1 hardware setup code calls these helpers while preparing default state for sequence/frame parameters and while updating reference slots according to V4L2 AV1 frame controls.

## Risks
The dominant risk is layout drift: every `memcpy` assumes source table dimensions exactly match destination fields in `struct av1cdfs` and `struct mvcdfs`. CDF table values are specification-derived and hard to review manually; accidental edits can create subtle decode mismatches. Quantizer thresholds in `rockchip_av1_get_q_ctx` must stay aligned with the table grouping. `refresh_frame_flags` is trusted as an 8-bit reference mask; incorrect flag handling can poison future reference-frame entropy state.

## Test Signals
AV1 conformance streams should cover keyframes, inter frames, reference refresh combinations, intrabc, palette, transform/eob variants, and multiple quantizer ranges. Differential decode against software AV1 output is the strongest signal. Static checks comparing table sizes against destination fields would reduce risk but are not present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.h

## Purpose
`rockchip_av1_entropymode.h` defines the AV1 entropy-mode constants, enums, and CDF structures used by Rockchip/Hantro AV1 decode support. It is the layout contract between AV1 entropy default generation, AV1 hardware programming, and per-context reference CDF state.

## Important APIs, Types, And Functions
The header defines many AV1 dimension constants such as `AV1_INTRA_MODES`, `NUM_REF_FRAMES`, `TX_SIZES`, `TOKEN_CDF_Q_CTXS`, and `SIG_COEF_CONTEXTS`. Enums cover block sizes, filter intra modes, frame type, transform size, prediction mode, and partition type. `struct mvcdfs` contains motion-vector CDF groups. `struct av1cdfs` contains the full hardware-facing AV1 entropy state, including partition, mode, segment, reference, transform, palette, CFL, motion, eob, coefficient, and padding fields. Declared functions are `rockchip_av1_store_cdfs`, `rockchip_av1_get_cdfs`, `rockchip_av1_set_default_cdfs`, and `rockchip_av1_default_coeff_probs`.

## Control Flow
The header has no executable control flow. AV1 decode setup allocates or embeds `struct av1cdfs`/`struct mvcdfs`, initializes defaults through the declared functions, selects reference CDF state for each frame, then stores updated state into refreshed reference slots after decode.

## State And Persistence
The structures represent per-context, per-reference entropy state that persists across frames in a decode session. Padding fields are explicit because hardware layout and DMA/register programming expect stable offsets.

## Dependencies And Integration Points
It includes Linux integer types and forward-declares `struct hantro_ctx`. It is included by `rockchip_av1_entropymode.c` and AV1 decoder hardware code. The V4L2 AV1 frame controls and Hantro AV1 context structures depend on these constants matching AV1 specification dimensions and hardware expectations.

## Risks
This is a high-coupling layout header: changing constants, enum order, array dimensions, or padding affects table copies and hardware interpretation. Some enum aliases preserve AV1 naming relationships, so cleanup refactors can accidentally alter semantic values. The large `struct av1cdfs` would benefit from layout assertions against hardware documentation.

## Test Signals
Build coverage catches missing declarations, but functional coverage requires AV1 decode tests across prediction modes, transform sizes, palette/CFL/intrabc features, and reference refresh behavior. Size/layout checks would be useful additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_entropymode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.c

## Purpose
`rockchip_av1_filmgrain.c` implements AV1 film grain synthesis helpers for Rockchip/Hantro AV1 decode support. It generates deterministic luma and chroma grain blocks from the AV1 Gaussian sequence, pseudo-random LFSR state, autoregressive coefficients, bit depth, scaling shifts, and grain limits.

## Important APIs, Types, And Functions
The file contains the static `gaussian_sequence[2048]` table, helper functions `clamp`, `round_power_of_two`, `rockchip_av1_init_random_generator`, `rockchip_av1_update_random_register`, and `rockchip_av1_get_random_number`, plus exported generators `rockchip_av1_generate_luma_grain_block` and `rockchip_av1_generate_chroma_grain_block`.

## Control Flow
Luma generation initializes a random register from the frame seed, fills a 73-by-82 block with Gaussian samples when luma scaling points are present, then applies an autoregressive filter over the interior area using `ar_coeff_lag`, 24 luma coefficients, `ar_coeff_shift`, and min/max clamps. Chroma generation separately initializes random sequences for Cb and Cr, fills 38-by-44 chroma blocks when chroma points or luma-derived scaling are enabled, then applies chroma autoregressive filtering. If luma points exist, chroma filtering also averages the corresponding 2-by-2 luma grain samples and applies the final chroma coefficient.

## State And Persistence
The file has only read-only static Gaussian data. Generated grain blocks are caller-provided stack or context memory and are deterministic for the same seed and frame parameters. There is no cross-frame persistence inside this file.

## Dependencies And Integration Points
It includes `rockchip_av1_filmgrain.h` for prototypes and Linux integer types. AV1 decode hardware code calls these helpers when film grain parameters are enabled and then uses the generated blocks to program hardware or prepare grain synthesis state.

## Risks
Array dimensions and loop bounds are fixed to AV1 film grain block geometry; off-by-one changes can corrupt caller memory. `ar_coeff_lag` and coefficient array sizes must match the AV1 limits expected by callers. The helper `round_power_of_two` assumes positive shift counts in current use, so caller validation of bit depth and grain scale shift matters. Chroma luma-coordinate calculations depend on the luma block's 73-by-82 padding.

## Test Signals
Film grain conformance vectors with known seeds are the best signal. Tests should cover no-grain paths, luma-only, chroma-only, chroma-from-luma, different bit depths, multiple autoregressive lags, and clamp boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.h

## Purpose
`rockchip_av1_filmgrain.h` declares the AV1 film grain block generation helpers used by Rockchip/Hantro AV1 decode support. It exposes the exact block dimensions and parameter contracts needed by the implementation and callers.

## Important APIs, Types, And Functions
The header declares `rockchip_av1_generate_luma_grain_block` for 73-by-82 luma grain blocks and `rockchip_av1_generate_chroma_grain_block` for 38-by-44 Cb/Cr grain blocks. Parameters include bit depth, point counts, grain scale shift, autoregressive lag and coefficients, coefficient shift, min/max clamps, chroma scaling mode, and random seed.

## Control Flow
There is no executable control flow in the header. Callers allocate correctly shaped grain arrays, pass parsed AV1 film grain parameters, call luma generation first when chroma may depend on luma, and then call chroma generation.

## State And Persistence
The header defines no storage. It declares pure generation-style routines that fill caller-owned buffers deterministically from frame parameters.

## Dependencies And Integration Points
It includes Linux integer types. AV1 hardware setup code and `rockchip_av1_filmgrain.c` share this interface. The array pointer dimensions are part of the compile-time safety contract between caller buffers and implementation loops.

## Risks
Because dimensions are encoded in function parameter types, any caller-side buffer mismatch becomes a compile-time issue, but changing those dimensions is an ABI-level driver change. The header does not document valid ranges for shifts, lags, or point counts, so validation must remain in the AV1 frame-parameter parsing path.

## Test Signals
Build coverage validates array type compatibility. Runtime AV1 film grain tests should verify deterministic output for known seeds and parameter combinations, especially chroma-from-luma cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_av1_filmgrain.h -->
