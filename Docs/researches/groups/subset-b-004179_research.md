<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_h264_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_h264_dec.c

## Purpose
Programs the Rockchip VDPU2 H.264 stateless decoder run for the Hantro mem2mem driver. It translates the current V4L2 H.264 SPS/PPS/decode controls, decoded-picture-buffer metadata, and vb2 DMA buffers into VDPU software registers, then starts one decode job.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_h264_dec_run(struct hantro_ctx *ctx)`.
- Internal helpers `set_params()`, `set_ref()`, and `set_buffers()` write control registers, reference lists/reference numbers, DPB addresses, stream/output addresses, direct-motion-vector storage, and the auxiliary qtable buffer.
- Depends on `struct hantro_h264_dec_ctrls`, `struct v4l2_ctrl_h264_*`, `struct v4l2_h264_reference`, `hantro_h264_dec_prepare_run()`, `hantro_h264_get_ref_nbr()`, and `hantro_h264_get_ref_buf()`.

## Control Flow
`rockchip_vpu2_h264_dec_run()` prepares the H.264 context, fetches the source buffer, writes stream length/endian/AXI/mode/field/profile/PPS/SPS parameters, writes P and B reference-list packing registers, writes all DPB reference addresses, writes source/destination/DMV/qtable addresses, ends the prepare phase, and sets `VDPU_REG_DEC_E` in software register 57. Bottom-field decodes offset the output start by one aligned line, and high-profile reference pictures write a DMV buffer after the decoded frame storage.

## State And Persistence
No durable state is stored. The function consumes per-job control state cached in `ctx->h264_dec`, per-context auxiliary DMA from H.264 init, and vb2 buffer timestamps/addresses. Register writes are transient hardware state for a single decode job.

## Dependencies And Integration Points
Integrated through Rockchip codec ops in `rockchip_vpu_hw.c`, primarily RK3399/RK3328/RK3568 VDPU2 variants. It uses Hantro core run fencing via `hantro_start/end_prepare_run()` and completion through the shared VDPU2 IRQ path.

## Risks And Edge Cases
Correctness is sensitive to V4L2 control validation, DPB index ordering, interlaced field flags, monochrome high-profile DMV sizing, and destination layout assumptions in `hantro_get_dec_buf_addr()`. Missing or stale references can program wrong DPB addresses. Bottom-field offset and DMV offset arithmetic must match the backing buffer allocation.

## Test Signals
Useful signals are successful stateless H.264 decode for baseline/high profile, frame and field pictures, B slices, long-term references, monochrome streams, and no VDPU2 timeout/bus-error IRQs. Compare decoded CRCs against software decode and watch for corruption across reference-heavy streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_h264_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_jpeg_enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_jpeg_enc.c

## Purpose
Implements Rockchip VEPU2 JPEG baseline encode runs for the Hantro driver. It builds the JPEG header in the destination buffer, configures source crop/format/buffer registers, loads hardware-ordered quantization tables, starts encoding, and records encoded payload size on completion.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_jpeg_enc_run()` and `rockchip_vpu2_jpeg_enc_done()`.
- Helpers `rockchip_vpu2_set_src_img_ctrl()`, `rockchip_vpu2_jpeg_enc_set_buffers()`, and `rockchip_vpu2_jpeg_enc_set_qtable()` handle image geometry, DMA addresses, output limit, and luma/chroma quant tables.
- Uses `struct hantro_jpeg_ctx`, `hantro_jpeg_header_assemble()`, `get_unaligned_be32()`, VEPU register macros from `rockchip_vpu2_regs.h`, and vb2 contiguous DMA helpers.

## Control Flow
The run path obtains source/destination buffers, starts the Hantro prepare phase, maps the destination CPU address, assembles the JPEG header using current width/height/quality, switches hardware into JPEG mode, programs overfill crop values from aligned source dimensions to visible destination dimensions, writes output stream address after the header, writes input plane addresses for one to three planes, writes quantization tables in two contiguous blocks, programs endian and AXI settings, ends prepare, and sets encode enable. The done hook reads `VEPU_REG_STR_BUF_LIMIT`, divides by 8, and adds the header size to the output payload.

## State And Persistence
The only persistent software effect is the vb2 destination payload size. Header bytes are written into the destination buffer before hardware output. All other state is per-job register state.

## Dependencies And Integration Points
Selected by Rockchip VEPU2 variants in `rockchip_vpu_hw.c` for JPEG encoding. It depends on Hantro JPEG helpers, V4L2 JPEG quality state, supported Hantro source format descriptors, and the shared VEPU2 IRQ handler.

## Risks And Edge Cases
Destination buffers smaller than `header_size` are warned and get a zero stream limit. `vb2_plane_vaddr()` must be available for header assembly. Horizontal crop requires 4-pixel alignment. Quant-table register ordering is hardware-specific and the two loops must stay separate.

## Test Signals
Exercise JPEG encode across supported input layouts, cropped visible sizes, quality settings, minimal destination buffers, and large 4K/8K boundaries. Check JPEG parseability, payload size accounting, header correctness, and absence of VEPU buffer-full/bus-error IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_jpeg_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_mpeg2_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_mpeg2_dec.c

## Purpose
Programs one Rockchip VDPU2 stateless MPEG-2 decode job. It maps V4L2 MPEG-2 sequence, picture, and quantisation controls into VDPU registers and configures current, forward, and backward frame buffers.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_mpeg2_dec_run(struct hantro_ctx *ctx)`.
- `rockchip_vpu2_mpeg2_dec_set_quantisation()` copies quant matrices into the context qtable DMA buffer.
- `rockchip_vpu2_mpeg2_dec_set_buffers()` resolves reference timestamps with `hantro_get_ref()`, writes stream/output addresses, and programs field-aware reference base registers.

## Control Flow
The run path starts prepare, reads MPEG-2 controls, writes latency/stream length/mode/endian/AXI/interlace/picture-type registers, writes macroblock dimensions and scan/DCT/f-code flags, copies quantization data, writes bitstream and output addresses, maps forward/backward references based on I/P/B picture type, handles top/bottom-field current-reference substitution, ends prepare, and sets the VDPU decode enable bit.

## State And Persistence
No persistent storage is used. The MPEG-2 context owns a coherent qtable buffer initialized elsewhere and updated per job. Reference state comes from vb2 timestamps and Hantro decoded-buffer tracking.

## Dependencies And Integration Points
Used through Rockchip VDPU2 codec ops in `rockchip_vpu_hw.c`. It depends on V4L2 stateless MPEG-2 controls, Hantro core buffer/reference helpers, DMA-contig memory, and the common Rockchip VDPU2 interrupt/reset paths.

## Risks And Edge Cases
Field-coded pictures are the main risk: output start addresses and forward-reference top/bottom pairing depend on `picture_structure` and `TOP_FIELD` flags. Missing references intentionally fall back to the current frame, which avoids null DMA programming but may conceal userspace reference mistakes as visible decode corruption.

## Test Signals
Run I/P/B pictures, progressive and interlaced streams, top-first and bottom-field sequences, alternate scan, concealment motion vectors, and custom quant matrices. Validate output CRCs and check that missing-reference debug paths do not appear in normal playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_mpeg2_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_vp8_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_vp8_dec.c

## Purpose
Implements Rockchip VDPU2 VP8 stateless frame decode setup. It converts the V4L2 VP8 frame control into loop-filter, quantizer, partition, reference, probability-table, segment-map, and start registers.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_vp8_dec_run(struct hantro_ctx *ctx)`.
- Register descriptor tables (`vp8_dec_lf_level`, `vp8_dec_quant`, `vp8_dec_dct_base`, `vp8_dec_pred_bc_tap`, etc.) drive compact `hantro_reg_write()` programming.
- Helpers `cfg_lf()`, `cfg_qp()`, `cfg_parts()`, `cfg_tap()`, `cfg_ref()`, and `cfg_buffers()` split the hardware setup by VP8 syntax area.

## Control Flow
The run path starts prepare, fetches `V4L2_CID_STATELESS_VP8_FRAME`, clears the segment map on key frames, updates probability tables, soft-resets the codec to avoid multi-instance state leakage, writes core decode/endian/AXI/mode flags, programs skip/filter disable flags, writes macroblock dimensions and boolean decoder state, sets VP8 version filter flags, configures loop filters and quantizers with segmentation handling, computes control/DCT partition aligned base addresses and start bits from source DMA, writes normal 6-tap filters when needed, resolves last/golden/alt references, writes probability/segment/output buffers, ends prepare, and starts decode.

## State And Persistence
Per-context VP8 probability and segment-map DMA buffers persist across jobs. Key frames reset the segment map. Reference resolution is timestamp-based through the Hantro decoded-buffer pool. Hardware register state is per job.

## Dependencies And Integration Points
Integrated by `rk3399_vpu_codec_ops` and other VDPU2 Rockchip variants. It depends on V4L2 VP8 stateless controls, `hantro_vp8_prob_update()`, Hantro reference tracking, and the codec reset callback from the active variant.

## Risks And Edge Cases
Partition offset arithmetic is alignment-sensitive and depends on correct userspace control values. Missing golden/alt/last references fall back to the current destination while logging debug messages. The explicit soft reset is required for multi-instance corruption avoidance, so variant reset correctness matters.

## Test Signals
Test key/inter frames, segmentation modes, loop-filter deltas, all DCT partition counts, version-dependent bilinear/tap behavior, missing-reference handling, and multi-context concurrent decode. Good signals are stable CRCs and no cross-stream corruption after repeated soft resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_vp8_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_regs.h

## Purpose
Defines Rockchip VPU2 VEPU/VDPU register offsets and bitfield macros shared by Rockchip JPEG/VP8/H.264/MPEG-2 encoder and decoder code. It is a hardware map, not executable logic.

## Important APIs, Types, And Functions
- Provides VEPU encoder register macros for VP8 quantization/penalties, JPEG luma/chroma quant tables, input plane/output stream addresses, image stride/crop, H.264 controls, ROI, endian, interrupts, and encode start.
- Provides VDPU decoder register macros for common decode control, stream length, endian, interrupts, AXI, H.264 reference lists and controls, and VP8 partition/filter/segment/reference registers.
- Consumed by `rockchip_vpu2_hw_jpeg_enc.c`, `rockchip_vpu_hw.c`, and related Rockchip codec implementation files.

## Control Flow
There is no runtime control flow. Callers compose register values by ORing these macros and write them through `vepu_write*()`, `vdpu_write*()`, `hantro_reg_write()`, or `hantro_write_addr()`.

## State And Persistence
The header owns no state. Its definitions describe transient MMIO state in the VPU hardware blocks. Persistence and synchronization are handled by codec run functions and Hantro core locking/IRQ paths.

## Dependencies And Integration Points
Depends on Linux `BIT()` and bitfield conventions already visible through included compilation units. The register names align Rockchip-specific implementations with the generic Hantro codec-operation tables in `rockchip_vpu_hw.c`.

## Risks And Edge Cases
The file contains many overlapping offsets because different codecs reuse the same hardware register window; accidental cross-codec macro use can silently program the wrong field. A few macros reference `x` in the expansion while lacking an `(x)` parameter, which is a latent compile hazard if those macros are used. Hardware-specific ordering requirements, such as JPEG quant table block writes, are not enforceable by this header.

## Test Signals
Build all Rockchip Hantro variants with warnings enabled to catch bad macro use. Runtime validation comes from codec-level decode/encode tests and IRQ status checks on all supported VDPU2/VEPU2 SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_hw_av1_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_hw_av1_dec.c

## Purpose
Implements RK3588 VPU981 AV1 stateless decode support for the Hantro driver, including AV1 syntax-to-register programming, reference-frame bookkeeping, coherent side-buffer management, probability/CDF persistence, film grain generation, and optional postprocessing output.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu981_av1_dec_init()`, `rockchip_vpu981_av1_dec_exit()`, `rockchip_vpu981_av1_dec_run()`, `rockchip_vpu981_av1_dec_done()`, and `rockchip_vpu981_postproc_ops`.
- Maintains `struct hantro_av1_dec_hw_ctx` side buffers for global motion, tile info, film grain, input/output probability tables, sync tile buffer, and loop-filter/CDEF/superres/restoration column data.
- Major setup helpers cover tile layout, reference frames and sign bias, segmentation, loop filter, CDEF, loop restoration, superres, global motion shear parameters, probability tables, film grain synthesis, input/output buffer addresses, and postprocessor registers.

## Control Flow
Initialization allocates all fixed coherent buffers and seeds default AV1 CDFs. Each run starts prepare, loads required AV1 sequence/frame/tile-group controls, reallocates tile-column buffers if the frame needs more columns, cleans stale software references, stores the current destination buffer by source timestamp, writes core syntax parameters, global motion, tile descriptors, references, segmentation, loop filter, dimensions/superres, CDEF, loop restoration, film grain, CDF tables, decode mode, bus/timeouts, output tile addresses, and input stream base/length. It then ends prepare and sets `av1_dec_e`. Completion updates stored CDFs unless frame-end CDF update is disabled. Exit frees every coherent buffer.

## State And Persistence
The AV1 context is stateful across jobs: software reference slots retain timestamps, dimensions, order hints, frame types, and vb2 buffer references; CDF tables persist per refresh flags; coherent side buffers may be reused and grown. No on-disk persistence exists.

## Dependencies And Integration Points
Integrated by `rk3588_vpu981_codec_ops` and `rk3588_vpu981_variant` in `rockchip_vpu_hw.c`. Depends on V4L2 stateless AV1 controls, Rockchip AV1 helper functions for CDFs and film-grain block generation, Hantro buffer helpers, `rockchip_vpu981_regs.h`, DMA-coherent allocation, and the RK3588 AV1 IRQ handler.

## Risks And Edge Cases
Allocation failure paths during init return immediately without freeing earlier allocations until exit, so caller cleanup must run. Reference lookup is timestamp/index sensitive; several paths assume a valid index after distance tests and can be fragile if userspace supplies inconsistent references. Film grain allocates multiple temporary kernel buffers per frame. Tile counts, tile offsets, superres math, 10-bit layouts, and postprocessor format mappings are high-risk areas.

## Test Signals
Cover AV1 key/inter/intra-only frames, refresh flags, missing/invalid references, order-hint wrap, screen-content/intrabc, film grain, CDEF, loop restoration, superres, tiled streams, 8-bit and 10-bit outputs, postprocessed NV12/NV15/P010, and memory-allocation failure injection. Good signals are clean RK3588 decode-ready IRQs, stable CDF behavior over long GOPs, and no DMA leaks on stream close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_hw_av1_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_regs.h

## Purpose
Defines RK3588 VPU981 AV1 decoder register descriptors and address offsets used by `rockchip_vpu981_hw_av1_dec.c`. It is the typed bitfield map for AV1 syntax, bus, timeout, reference, side-buffer, and postprocessor programming.

## Important APIs, Types, And Functions
- Defines `AV1_SWREG()` and `AV1_DEC_REG()` to construct `struct hantro_reg` descriptors.
- Exposes descriptors such as `av1_dec_e`, `av1_dec_mode`, segmentation fields, loop-filter fields, reference scaling/sign-bias fields, CDEF/LR/superres fields, probability-table addresses, timeout/bus controls, and postprocessor output format/stride/size fields.
- Defines raw address offsets including `AV1_TILE_OUT_LU`, `AV1_REFERENCE_Y(i)`, `AV1_SEGMENTATION`, `AV1_GLOBAL_MODEL`, `AV1_CDEF_COL`, `AV1_FILM_GRAIN`, `AV1_INPUT_STREAM`, `AV1_PROP_TABLE`, and postprocessor output addresses.

## Control Flow
No runtime control flow exists. AV1 code passes these descriptors to `hantro_reg_write()` and raw offsets to `hantro_write_addr()` while programming a decode job.

## State And Persistence
The header owns no state. It describes the VPU981 MMIO state layout. Software persistence for references and probability tables lives in `struct hantro_av1_dec_hw_ctx`.

## Dependencies And Integration Points
Includes `hantro.h` for `struct hantro_reg`. It is tightly coupled to RK3588 AV1 decoder code and the RK3588 IRQ path in `rockchip_vpu_hw.c`.

## Risks And Edge Cases
Many descriptors encode signed AV1 syntax into unsigned masks, so callers must clamp/transform values before writing. Register numbers are sparse and hardware-specific; wrong offsets can corrupt unrelated decoder or postprocessor state. Because the file is declarative, it cannot enforce valid combinations such as superres, bit depth, or postprocessor formats.

## Test Signals
Build coverage catches descriptor type errors. Runtime signals come from AV1 conformance decode on RK3588, postprocessor format tests, interrupt status readback, and targeted tests for reference scaling, loop restoration, film grain, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu_hw.c

## Purpose
Declares Rockchip Hantro VPU variants and their supported formats, codec-operation tables, IRQ handlers, reset hooks, clock setup, and postprocessor capabilities. It is the integration layer between Rockchip SoC compatibles and generic Hantro core logic.

## Important APIs, Types, And Functions
- Exports `rk3036_vpu_variant`, `rk3066_vpu_variant`, `rk3288_vpu_variant`, `rk3328_vpu_variant`, `rk3399_vpu_variant`, `rk3568_vepu_variant`, `rk3568_vpu_variant`, `px30_vpu_variant`, and `rk3588_vpu981_variant`.
- Defines Rockchip encoder/decoder/postproc format tables, codec-op arrays for G1/H1/VDPU2/VEPU2/VPU981, IRQ handlers for VEPU/VDPU/VPU981, and reset helpers.
- Hardware init functions raise selected ACLKs to expected performance rates.

## Control Flow
During probe, the Hantro core selects one exported `struct hantro_variant`. The variant controls which formats appear to userspace, which clocks/IRQs are requested, which codec run/reset/init/exit/done hooks execute, and which postprocessor ops are available. IRQ handlers read hardware status, classify the vb2 result as done or error, clear interrupt/AXI state, and call `hantro_irq_done()`.

## State And Persistence
The file owns static const variant data only. Runtime state is in `struct hantro_dev` and `struct hantro_ctx`. Clock rate changes persist while the device is active, but no durable storage is used.

## Dependencies And Integration Points
Depends on Linux clocks, Hantro core structures, G1/H1/VPU2/VPU981 register headers, and codec-specific run functions. Device-tree compatible tables elsewhere point at these exported variants.

## Risks And Edge Cases
Format limits and codec masks decide userspace-visible ABI for each SoC. The RK3399 variant intentionally disables H.264 decode despite having ops to steer userspace to a better VDEC core. IRQ handlers use simple status-bit checks, so incomplete error decoding can hide timeout/bus/fuse causes. Clock index assumptions must match `clk_names`.

## Test Signals
Probe each compatible, verify advertised V4L2 formats and frame-size bounds, run JPEG/H.264/MPEG-2/VP8/AV1 where enabled, force error IRQs, test reset during streamoff, and confirm clock names/rates match device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sama5d4_vdec_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sama5d4_vdec_hw.c

## Purpose
Defines the Microchip/Atmel SAMA5D4 Hantro VDEC variant. It advertises G1 decoder formats, postprocessed YUYV output, codec operations, IRQ wiring, clock names, and codec capability bits.

## Important APIs, Types, And Functions
- Exports `sama5d4_vdec_variant`.
- Defines `sama5d4_vdec_fmts`, `sama5d4_vdec_postproc_fmts`, `sama5d4_vdec_codec_ops`, `sama5d4_irqs`, and `sama5d4_clk_names`.
- Uses generic G1 run/reset/init/exit functions for MPEG-2, VP8, and H.264.

## Control Flow
The Hantro core consumes the variant at probe. Userspace sees NV12 raw capture plus MPEG-2/VP8/H.264 stateless coded formats up to HD bounds. Codec jobs dispatch to generic G1 implementations, and interrupts use `hantro_g1_irq`.

## State And Persistence
Only static const tables are defined. Runtime state is owned by the Hantro core and codec-specific generic contexts. No persistent storage is touched.

## Dependencies And Integration Points
Depends on `hantro.h`, generic G1 decoder helpers, the G1 postprocessor, and a single `vdec_clk` clock resource from platform data/device tree.

## Risks And Edge Cases
The file assumes generic G1 behavior fully matches SAMA5D4 hardware. Format bounds are HD-limited; incorrect limits would affect userspace negotiation. Single-clock naming must match integration data.

## Test Signals
Probe with SAMA5D4 resources, verify `vdec_clk` acquisition, run MPEG-2/VP8/H.264 decode conformance streams, test YUYV postprocessed output, and confirm clean IRQ completion and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sama5d4_vdec_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/stm32mp25_vpu_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/stm32mp25_vpu_hw.c

## Purpose
Defines STM32MP25 Hantro decoder and encoder variants. The decoder exposes G1 VP8/H.264 decode, while the encoder exposes H1 JPEG encode with STM32-specific reset and IRQ handling.

## Important APIs, Types, And Functions
- Exports `stm32mp25_vdec_variant` and `stm32mp25_venc_variant`.
- Defines decoder and encoder format tables, `stm32mp25_vdec_codec_ops`, `stm32mp25_venc_codec_ops`, `stm32mp25_venc_irq()`, and `stm32mp25_venc_reset()`.
- Uses generic `hantro_g1_*` decoder operations and `hantro_h1_jpeg_enc_*` encoder operations.

## Control Flow
The decoder variant advertises NV12 output plus VP8 and H.264 coded formats up to FHD and dispatches to generic G1 run/reset/init/exit functions. The encoder variant advertises YUV input formats and JPEG output up to 4K, dispatches JPEG jobs to H1 helpers, resets with `reset_control_reset(vpu->resets)`, and marks job state from `H1_REG_INTERRUPT_FRAME_RDY`.

## State And Persistence
The file stores static variant data only. Runtime state lives in Hantro core, vb2 queues, and hardware registers. Reset changes transient hardware state but no durable storage.

## Dependencies And Integration Points
Depends on `hantro.h`, `hantro_jpeg.h`, `hantro_h1_regs.h`, reset-controller support through `vpu->resets`, and platform resources named `vdec-clk`, `venc-clk`, `vdec`, and `venc`.

## Risks And Edge Cases
The encoder IRQ clears only `H1_REG_INTERRUPT_BIT`, unlike some Rockchip handlers that clear broader state; error handling depends on the hardware status convention. Reset requires a valid reset control. Separate decoder/encoder variants must match platform compatible/resource wiring.

## Test Signals
Probe both VDEC and VENC instances, verify clock/reset/IRQ names, run VP8/H.264 decode and JPEG encode, force encoder error statuses, and confirm stream restart after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/stm32mp25_vpu_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sunxi_vpu_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sunxi_vpu_hw.c

## Purpose
Defines the Allwinner Hantro G2 VP9 decoder variant, including tiled raw formats, postprocessed formats, VP9 codec ops, clock setup, reset hook, IRQ wiring, and variant flags.

## Important APIs, Types, And Functions
- Exports `sunxi_vpu_variant`.
- Defines `sunxi_vpu_dec_fmts`, `sunxi_vpu_postproc_fmts`, `sunxi_vpu_hw_init()`, `sunxi_vpu_reset()`, `sunxi_vpu_codec_ops`, `sunxi_irqs`, and `sunxi_clk_names`.
- Uses generic G2 VP9 run/done/init/exit helpers and `hantro_g2_postproc_ops`.

## Control Flow
Probe selects the variant, sets the module clock to 300 MHz in init, exposes NV12_4L4/P010_4L4 tiled decode targets and VP9 coded input up to UHD, and dispatches jobs to G2 VP9 operations. Reset goes through the reset controller, and completion uses the generic G2 IRQ handler.

## State And Persistence
Only static tables are owned here. Runtime state is in Hantro core/G2 VP9 contexts. The module clock rate persists for the active device lifetime.

## Dependencies And Integration Points
Depends on two clocks named `mod` and `bus`, a reset controller, generic G2 VP9 decoder support, and postprocessing support. Variant flags `double_buffer`, `legacy_regs`, and `late_postproc` tune Hantro core behavior for this hardware.

## Risks And Edge Cases
Clock-rate programming assumes the first clock is the module clock. Format step size is 32 rather than the common macroblock step, so negotiation must match G2 tiling requirements. Variant flags are critical for register layout and postproc timing.

## Test Signals
Verify probe clock/reset resources, VP9 conformance decode on 8-bit and 10-bit streams, postprocessed NV12/P010 output, UHD boundary sizes, double-buffer behavior, and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sunxi_vpu_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/via/Kconfig

## Purpose
Adds Kconfig selection for the VIA Chrome9 framebuffer-backed camera controller driver.

## Important APIs, Types, And Functions
- Defines `VIDEO_VIA_CAMERA` as a tristate option named "VIAFB camera controller support".
- Depends on `V4L_PLATFORM_DRIVERS`, `FB_VIA`, and `VIDEO_DEV`.
- Selects `VIDEOBUF2_DMA_SG` and conditionally selects `VIDEO_OV7670` when `VIDEO_CAMERA_SENSOR` is enabled.

## Control Flow
There is no runtime control flow. Enabling this symbol builds the VIA camera platform driver and ensures its VB2 DMA-SG and OV7670 sensor dependencies are available.

## State And Persistence
No state is stored. The symbol controls build configuration.

## Dependencies And Integration Points
Integrated by the media platform drivers Kconfig hierarchy and paired with `drivers/media/platform/via/Makefile`. The help text documents the tested OLPC XO-1.5/OV7670 target.

## Risks And Edge Cases
The driver is tightly coupled to VIA framebuffer infrastructure, so missing `FB_VIA` blocks it. The conditional sensor selection may not cover non-OV7670 sensors if the driver were generalized.

## Test Signals
Configuration tests should verify module and built-in builds with `FB_VIA`, dependency rejection without framebuffer/V4L2 support, and expected autoselection of VB2 DMA-SG and OV7670 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/via/Makefile

## Purpose
Connects the VIA media platform Kconfig symbol to the camera driver object.

## Important APIs, Types, And Functions
- Adds `via-camera.o` to the build when `CONFIG_VIDEO_VIA_CAMERA` is enabled.

## Control Flow
No runtime control flow exists. Kbuild includes or omits the object based on the Kconfig symbol.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Integrated with `drivers/media/platform/via/Kconfig` and the kernel media platform build system.

## Risks And Edge Cases
The Makefile has a single object and no composite object list, so future multi-file VIA camera changes would need build updates.

## Test Signals
Build with `CONFIG_VIDEO_VIA_CAMERA=m` should produce `via-camera.ko`; built-in configuration should link the object into the kernel image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.c

## Purpose
Implements the VIA Chrome integrated camera controller V4L2 capture driver, originally for OLPC XO-1.5 systems with an OV7670 sensor. The controller captures into reserved framebuffer memory, then copies completed frames into userspace-provided VB2 DMA-SG buffers.

## Important APIs, Types, And Functions
- Module parameters `flip_image` and `override_serial` tune OV7670 vertical flip and OLPC serial-port conflict handling.
- Core state is `struct via_camera`; queued buffers use `struct via_buffer`.
- Major paths cover GPIO sensor power/reset, OV7670 subdev configuration, VIA register access, threaded IRQ handling, framebuffer capture-buffer setup, scaler/controller configuration, VB2 queue ops, V4L2 file/ioctl ops, PM hooks, serial-port guard, probe, and remove.

## Control Flow
Probe validates framebuffer memory/MMIO, checks the OLPC serial-port conflict, allocates the camera object, registers V4L2 state, sets DMA mask, enables capture-port pins, powers the sensor, creates an OV7670 I2C subdev on `VIA_PORT_31`, requests a shared threaded IRQ, initializes a VB2 DMA-SG queue, and registers a video device. Open requests the VIA framebuffer DMA engine, powers the sensor, and marks configuration needed. Stream-on configures the sensor and controller when needed, adds a CPU latency QoS request, enables capture and interrupts, and starts filling internal framebuffer buffers. IRQ top-half clears camera interrupt bits and wakes the thread; the thread copies the just-completed framebuffer capture buffer into the next queued SG buffer, timestamps it, increments sequence, and completes it. Stop disables interrupts/capture, removes QoS, and returns queued buffers with error.

## State And Persistence
All state is in memory: current format, sensor format, mbus code, capture-buffer offsets, queue list, sequence, opstate, flags, GPIO handles, MMIO mappings, and QoS request. No durable persistence exists. The global `via_cam_info` assumes one device.

## Dependencies And Integration Points
Depends on VIA framebuffer core (`viafb_dev`, IRQ, DMA copy, I2C adapter lookup, PM hooks), V4L2 core/subdev/ctrl/event APIs, OV7670 sensor support, VB2 DMA-SG memory ops, GPIO descriptors, PCI config access for OLPC serial-port arbitration, and platform data from `viafb-camera`.

## Risks And Edge Cases
The driver is hardware- and board-specific: one capture engine, one global camera, fixed OV7670 address/port, VGA sensor mode, and OLPC-specific GPIO/pin assumptions. Frame data is copied from framebuffer memory in IRQ thread context, so bandwidth and SG correctness matter. Queue insertion lacks explicit locking in `buf_queue` beyond VB2 queue serialization. Suspend/resume must preserve prior running state and sensor power. Serial override intentionally disables a conflicting serial-port bit.

## Test Signals
Probe on XO-1.5/VIA Chrome9 with reserved camera framebuffer memory, verify `/dev/video*` registration, enumerate YUYV/QCIF-VGA formats, stream with mmap/userptr/dmabuf/read, test open/close power cycling, flip control, suspend/resume while idle and streaming, serial-port refusal/override, CPU latency QoS add/remove balance, no underruns with two/three internal capture buffers, and correct frame sequence/timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.c -->
