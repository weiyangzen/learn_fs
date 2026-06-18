# subset-b-004136 research

This grouped report covers the Chips&Media CODA V4L2 mem2mem codec driver files under `sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda`. Each section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-bit.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-bit.c

## Purpose
`coda-bit.c` implements the BIT-processor backed encode/decode engine for the CODA multi-standard VPU driver. It is the hardware command layer behind the generic V4L2 mem2mem plumbing in `coda-common.c`: it uploads per-context registers, manages firmware commands, queues compressed bitstreams, allocates internal frame/work/parameter buffers, starts sequence initialization, executes picture runs, handles sequence end, and services the BIT IRQ.

## Important APIs, Types, and Functions
The exported context operations are `coda_bit_encode_ops` and `coda_bit_decode_ops`. Encoder entry points include `coda_encoder_reqbufs()`, `coda_start_encoding()`, `coda_prepare_encode()`, `coda_finish_encode()`, and `coda_seq_end_work()`. Decoder entry points include `coda_decoder_reqbufs()`, `__coda_decoder_seq_init()`, `coda_dec_seq_init_work()`, `coda_start_decoding()`, `coda_prepare_decode()`, `coda_finish_decode()`, and `coda_decode_timeout()`.

Low-level command helpers are `coda_command_async()`, `coda_command_sync()`, `coda_wait_timeout()`, and `coda_hw_reset()`. The decoder bitstream ring is synchronized through `coda_kfifo_sync_from_device()`, `coda_kfifo_sync_to_device_full()`, `coda_kfifo_sync_to_device_write()`, `coda_bitstream_flush()`, `coda_fill_bitstream()`, `coda_bit_stream_end_flag()`, and `coda_bitstream_try_queue()`. Memory setup is handled by `coda_alloc_context_buffers()`, `coda_alloc_framebuffers()`, `coda_setup_iram()`, and `coda9_set_frame_cache()`. `coda_check_firmware()` validates firmware product/version, and `coda_irq_handler()` completes mem2mem jobs.

## Control Flow
Commands run under `dev->coda_mutex`. `coda_command_async()` restores per-context state for CODA7/CODA9 class devices, clears CODA960 write-protection state, marks the BIT engine busy, writes run index/codec mode/aux mode, traces the run, and writes `CODA_REG_BIT_RUN_COMMAND`. Synchronous callers then poll `CODA_REG_BIT_BUSY`; asynchronous picture runs complete through `coda_irq_handler()` and `ctx->completion`.

Encoding starts by validating firmware initialization, allocating JPEG quantization tables when needed, programming the stream buffer, frame memory layout, source size, framerate, codec-specific sequence parameters, rate-control state, slice/GOP settings, IRAM, and optional H.264 search RAM. After `CODA_COMMAND_SEQ_INIT`, it allocates internal reference buffers for non-JPEG codecs, registers them through the parameter buffer, issues `CODA_COMMAND_SET_FRAME_BUF`, and extracts stream headers. H.264 SPS/PPS headers are cached in `ctx->vpu_header`; non-CODA960 H.264 SPS may be rewritten by `coda_h264_sps_fixup()` to report visible cropping.

Each encode picture run applies pending rate-control parameter changes, picks source and destination buffers, assigns sequence numbers and key/P-frame flags, prepends cached headers for first/forced H.264 I-frames, writes source base addresses and destination bitstream address, and starts `CODA_COMMAND_PIC_RUN`. Completion reads the write pointer and picture type, computes payload bytes, copies metadata, marks EOS when the source was last, and returns both queues.

Decoding allocates a DMA write-combined bitstream ring and copies vb2 vmalloc source buffers into it. `coda_fill_bitstream()` validates JPEG SOI/EOI markers, drops empty buffers, stores timestamp metadata in `buffer_meta_list`, limits queue depth for JPEG and reordered streams, and tracks fetch safety with the 512-byte prefetch rule. Sequence initialization writes the ring pointers, stream options, codec aux state, H.264 PS/slice buffers, JPEG thumb settings, and `CODA_BIT_DEC_SEQ_INIT_ESCAPE`; it then reads stream dimensions, crop, required frame count, and parsed profile/level controls. Picture runs refill the ring, optionally use VDOA to copy a previous tiled display frame, program rotator/output addresses, pad terminal JPEG data, sync FIFO pointers to hardware, and start PIC_RUN. Finish updates FIFO read position, consumes metadata, reports macroblock errors, handles prescan/hold states, returns ready display frames in presentation order, and refills the ring.

## State and Persistence
State is per `struct coda_ctx`: initialization flag, sequence counters, bitstream FIFO, bitstream end flag in `bit_stream_param`, internal frame buffers and their metadata, IRAM allocation info, cached frame memory control, display/reorder indexes, VDOA use, and cached encoder headers. Device-level state includes firmware buffers and hardware registers but no filesystem persistence. Allocated DMA buffers are debugfs-visible through `coda_alloc_aux_buf()` callers.

## Dependencies and Integration Points
This file depends on V4L2 mem2mem/vb2, dma-contig/vmalloc memory models, firmware register definitions in `coda_regs.h`, codec helpers from `coda-h264.c`, `coda-mpeg2.c`, `coda-mpeg4.c`, JPEG helpers from `coda-jpeg.c`, VDOA support from `imx-vdoa.h`, tracepoints, clocks/reset control, and the IRQ/completion model wired by `coda-common.c`.

## Risks and Edge Cases
The command path is hardware-timing sensitive and uses several firmware workarounds: 512-byte initial bitstream padding, CODA960 reset after sequence end/JPEG runs, BWB avoidance elsewhere, fixed rotator index limits, and firmware-version-specific IRAM disables. `coda_job_ready()` assumes at least one metadata entry before `list_first_entry()` when decoder BIT mode is active, so readiness invariants matter. Sequence number reconstruction for reordered streams depends on metadata/FIFO synchronization and 16-bit hardware counter roll-over handling. JPEG padding and stream-end read-pointer overshoot can reset the FIFO if payload appears near full. `coda_hw_reset()` requires optional reset control and has CODA960 GDI bus quiesce timeout paths.

## Test Signals
Strong signals include firmware version logs matching product, successful `SEQ_INIT` and `SET_FRAME_BUF`, H.264/MPEG4 header extraction, correct SPS cropping on unaligned sizes, stable encode key/P-frame flags, decoder source-change event after sequence init, correct timestamp propagation through reordered decode, EOS event on LAST buffers, MB error-count control increments, timeout reset behavior, VDOA tiled-to-raster output, and clean release after abort/streamoff with no leaked internal buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-common.c

## Purpose
`coda-common.c` is the platform driver, V4L2 mem2mem interface, vb2 queue implementation, control setup, firmware loading, runtime PM glue, and video-device registration layer for the CODA VPU. It selects per-SoC codec capabilities, creates encoder/decoder video nodes, validates formats, manages queue lifecycle, and dispatches actual hardware work to `struct coda_context_ops`.

## Important APIs, Types, and Functions
Core exported helpers are `coda_write()`, `coda_read()`, `coda_write_base()`, `coda_alloc_aux_buf()`, `coda_free_aux_buf()`, `coda_encoder_queue_init()`, `coda_decoder_queue_init()`, `coda_m2m_buf_done()`, `coda_update_profile_level_ctrls()`, and `coda_product_name()`. Internal V4L2 ioctl handlers cover format enumeration/get/try/set, request buffers, qbuf/dqbuf, selection, encoder/decoder commands, frame sizes/intervals, stream parameters, and events. Mem2mem scheduling uses `coda_device_run()`, `coda_pic_run_work()`, `coda_job_ready()`, and `coda_job_abort()`. Device lifecycle is implemented by `coda_probe()`, `coda_fw_callback()`, `coda_hw_init()`, `coda_open()`, `coda_release()`, `coda_remove()`, and `coda_runtime_resume()`.

Important tables include per-product codec arrays (`codadx6_codecs`, `codahx4_codecs`, `coda7_codecs`, `coda9_codecs`), per-video-node descriptors (`coda_bit_encoder`, `coda_bit_decoder`, JPEG variants), and `coda_devdata[]` mapping OF compatibles to firmware names, product IDs, work/temp/IRAM sizes, and supported nodes.

## Control Flow
Probe gets clocks, MMIO, BIT IRQ, CODA960 JPEG IRQ, optional reset control, IRAM gen_pool, optional VDOA data, registers `v4l2_device`, initializes locks/IDA/debugfs, allocates per-device work/temp/IRAM buffers, creates an ordered workqueue, enables runtime PM, and starts asynchronous firmware request. The firmware callback tries fallback firmware names, allocates `codebuf`, copies/reorders firmware, initializes hardware, validates firmware, creates the mem2mem device, and registers each configured video node.

Open allocates a `coda_ctx`, assigns an ID, creates debugfs context state, selects the `coda_video_device`, sets default params, powers and clocks the device, creates a V4L2 mem2mem context, initializes controls, and sets vb2 queue state. Release tears down mem2mem, VDOA, pending sequence end, controls, clocks, runtime PM, debugfs, context buffers, and ID allocation.

Format flow normalizes all supported YUV variants for codec lookup, bounds image dimensions, estimates compressed `sizeimage`, enforces decoder capture dimensions once output is streaming, infers JPEG subsampling, and configures tiled vs linear frame maps plus VDOA use. Setting output format on a decoder or capture format on an encoder determines `ctx->codec`.

Streaming is split by queue. On decoder output stream-on, existing buffers are copied into the bitstream ring and sequence init may run immediately. JPEG decode inspects the first header to update capture dimensions and chroma subsampling. Once both queues stream, common code validates dimensions, enables buffered source mode for BIT decoders, resets counters/control state, and calls context `start_streaming`. Mem2mem work later locks buffer and hardware mutexes, calls `prepare_run`, waits for IRQ completion up to one second, runs timeout/reset handling if needed, calls `finish_run`, possibly queues sequence-end work, and finishes the mem2mem job.

## State and Persistence
Device state persists in `struct coda_dev`: V4L2/video devices, clocks, reset, MMIO, firmware index, firmware/code/temp/work/IRAM buffers, mutexes, workqueue, m2m device, ID allocator, debugfs root, and macroblock-error ratelimiter. Context state persists in `struct coda_ctx` defined in `coda.h`. External persistence is limited to firmware files requested by name and debugfs exposure of DMA buffers.

## Dependencies and Integration Points
The file integrates with OF compatibles `fsl,imx27-vpu`, `fsl,imx51-vpu`, `fsl,imx53-vpu`, `fsl,imx6q-vpu`, and `fsl,imx6dl-vpu`; Linux clocks, reset, genalloc IRAM, runtime PM, platform IRQs/resources, firmware loader, debugfs, V4L2 ioctl/event/control APIs, V4L2 mem2mem, vb2 dma-contig/vmalloc, and optional VDOA platform data.

## Risks and Edge Cases
Asynchronous firmware loading means video nodes appear only after callback success; failed fallback requests only surface in logs. `coda_approximate_timeperframe()` contains a continued-fraction update that is easy to regress because hardware stores numerator/denominator in 16-bit fields. Direct CODA960 JPEG decode uses `coda_encoder_queue_init()` intentionally because it is non-bitstream operation, which is non-obvious. Start/stop paths must preserve buffers in queued/done/error state correctly across partial stream-on failure. Runtime resume reinitializes hardware only when a PM domain is present and firmware was loaded. Module parameters (`disable_tiling`, `disable_vdoa`, `enable_bwb`) alter memory layout and stability.

## Test Signals
Useful validation includes OF probe and IRQ registration, fallback firmware discovery, video-node registration per SoC, v4l2-compliance for format/selection/cmd/event ioctls, correct VDOA/YUYV rejection when VDOA is unavailable, queue setup with dma-contig/vmalloc memory, zero-byte decoder EOS handling, source-change/EOS event delivery, runtime PM resume after domain power loss, and clean remove/release without leaked debugfs or DMA buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-gdi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-gdi.c

## Purpose
`coda-gdi.c` programs CODA960 GDI address translation registers for linear and macroblock-tiled frame maps. It is used by BIT and direct JPEG paths before encode/decode picture runs so the hardware interprets luma/chroma frame buffer addresses correctly.

## Important APIs, Types, and Functions
The only exported function is `coda_set_gdi_regs(struct coda_ctx *ctx)`. Static translation maps are `xy2ca_zero_map`, `xy2ca_tiled_map`, and `rbc2axi_tiled_map`. Helper macros `XY2()` and `RBC()` encode bit selectors for CODA9 `GDI_XY2_*`, `GDI_XY2_RBC_CONFIG`, and `GDI_RBC2_AXI_*` registers. Map selection depends on `ctx->tiled_map_type`, whose values are declared in `coda.h` as `GDI_LINEAR_FRAME_MAP` and `GDI_TILED_FRAME_MB_RASTER_MAP`.

## Control Flow
For linear mapping, `coda_set_gdi_regs()` writes zero maps and disables XY-to-RBC conversion. For tiled macroblock raster mapping, it selects `xy2ca_tiled_map`, enables tiled XY2RBC conversion, horizontal CA increment, and configures 16-by-8 chroma/luma block geometry. It then writes all XY-to-CA entries, clears BA and RA maps, writes the global config register, and, when tiled mode is enabled, writes the 32-entry RBC-to-AXI map.

## State and Persistence
The file stores only static lookup tables. Runtime state is CODA960 register state, refreshed on each caller path before the relevant JPEG or BIT picture run. There is no persistent storage.

## Dependencies and Integration Points
It depends on `struct coda_ctx`, `coda_write()`, GDI map constants from `coda.h`, and CODA9 register offsets from `coda_regs.h`. It is called from `coda_prepare_encode()`, `coda_prepare_decode()`, and CODA960 direct JPEG encode/decode preparation.

## Risks and Edge Cases
The map tables encode hardware address swizzling and are difficult to validate without frame corruption tests. Tiled mode assumes a single chroma plane, matching the comment in `set_default_params()` that macroblock tiling only works for NV12. Non-CODA960 callers should not use this function; current call sites guard by product or are direct CODA960 JPEG paths.

## Test Signals
Signals include correct NV12 tiled decode/encode output, no chroma swap or macroblock scrambling, YUYV output through VDOA, linear formats still decoding correctly after tiled contexts, and register traces showing `CODA9_GDI_XY2_RBC_CONFIG` disabled for linear and enabled with RBC2AXI entries for tiled mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-gdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-h264.c

## Purpose
`coda-h264.c` provides H.264 bitstream helper routines for the CODA driver. It parses SPS profile/level from queued decoder buffers, generates filler NAL units for hardware alignment/padding, maps H.264 profile and level IDC values to V4L2 menu constants, and rewrites encoder SPS cropping fields when older CODA firmware cannot emit correct visible-frame cropping.

## Important APIs, Types, and Functions
Public helpers are `coda_sps_parse_profile()`, `coda_h264_filler_nal()`, `coda_h264_padding()`, `coda_h264_profile()`, `coda_h264_level()`, and `coda_h264_sps_fixup()`. Static helpers include `coda_find_nal_header()` and a small RBSP bit reader/writer (`struct rbsp`, `rbsp_read_bit[s]()`, `rbsp_write_bit[s]()`, `rbsp_read_uev()`, `rbsp_write_uev()`, `rbsp_read_sev()`). `coda_filler_size[]` maps header alignment remainder to filler NAL size.

## Control Flow
Decoder output queuing calls `coda_sps_parse_profile()` before sequence initialization when no H.264 profile is cached. It scans for a four-byte start code and SPS NAL type 7, then stores `profile_idc` and `level_idc` into `ctx->params` for control updates and reorder decisions.

Encoder initialization calls `coda_h264_padding()` after SPS/PPS extraction to align the first encoded frame stream. If non-CODA960 firmware emits an SPS for a macroblock-rounded coded size while the visible width/height are not 16-aligned, `coda_h264_sps_fixup()` parses the SPS RBSP until the frame-cropping flag, rejects unsupported high-profile/VUI cases, computes right/bottom crop units from visible dimensions, rewrites cropping fields, clears VUI presence, writes an RBSP stop bit, and returns the new SPS size.

## State and Persistence
The helpers update only `ctx->params.h264_profile_idc` and `ctx->params.h264_level_idc` or mutate the in-memory SPS header buffer. There is no hardware or filesystem persistence in this file.

## Dependencies and Integration Points
It depends on vb2 buffer access, V4L2 H.264 control enums, and `struct coda_ctx`. It is consumed by decoder queuing/profile controls in `coda-common.c`, reorder decisions and bitstream padding in `coda-bit.c`, and SPS crop correction during H.264 encode startup.

## Risks and Edge Cases
The SPS parser assumes Annex B start codes and reads fixed offsets after the SPS NAL header. `coda_h264_sps_fixup()` does not support high-profile SPS extensions or VUI parameters, returning `-EINVAL` in those cases. It writes into the existing buffer and requires `*size < max_size`; incorrect RBSP parsing can corrupt the SPS. Filler NAL generation requires at least six bytes and silently relies on callers to allocate enough padding space.

## Test Signals
Tests should cover SPS profile/level extraction from buffers with leading non-SPS NALs, profile/level menu mapping, filler NAL byte pattern and alignment sizes for all remainders, successful SPS cropping for odd macroblock-aligned widths/heights, and expected failure for high-profile/VUI SPS inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-jpeg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-jpeg.c

## Purpose
`coda-jpeg.c` implements JPEG-specific support for both the older BIT JPEG paths and CODA960 direct JPEG processing unit. It supplies default JPEG Huffman/quantization tables, parses JPEG headers for decode setup, generates hardware Huffman tables, emits JPEG headers for encode, configures CODA960 JPEG BBC/GBU/GDI blocks, handles direct JPEG mem2mem encode/decode operations, and services the JPEG IRQ.

## Important APIs, Types, and Functions
Shared exported helpers are `coda_jpeg_write_tables()`, `coda_jpeg_check_buffer()`, `coda_jpeg_decode_header()`, and `coda_set_jpeg_compression_quality()`. Direct CODA960 ops are exported as `coda9_jpeg_encode_ops` and `coda9_jpeg_decode_ops`; their main methods are `coda9_jpeg_start_encoding()`, `coda9_jpeg_prepare_encode()`, `coda9_jpeg_finish_encode()`, `coda9_jpeg_encode_timeout()`, `coda9_jpeg_start_decoding()`, `coda9_jpeg_prepare_decode()`, `coda9_jpeg_finish_decode()`, `coda9_jpeg_release()`, and `coda9_jpeg_irq_handler()`.

Static support includes table data (`luma_dc`, `chroma_dc`, `luma_ac`, `chroma_ac`, `luma_q`, `chroma_q`), `struct coda_huff_tab`, JPEG marker constants, `coda9_jpeg_chroma_format()`, MCU alignment tables, Huffman generation for encode/decode, quantization table loading, `coda9_jpeg_encode_header()`, and `coda9_jpeg_dec_bbc_gbu_setup()`.

## Control Flow
Header parsing uses `v4l2_jpeg_parse_header()` to validate dimensions, component count, quantization table count/precision, Huffman table presence/length, scan component table selectors, entropy-coded segment offset, and supported 4:2:0/4:2:2 subsampling. Parsed quantization and Huffman tables are copied into `ctx->params` and transformed into hardware decode tables.

Older BIT JPEG encode uses `coda_jpeg_write_tables()` to copy default Huffman and active quantization tables into the CODA parameter buffer. `coda_jpeg_check_buffer()` filters decode input by SOI marker and an EOI marker within the final 32 bytes, trimming trailing data.

Direct CODA960 encode startup builds Huffman lookup data, allocates quantization tables, and scales them from the quality control. Prepare encode sets sequence numbers, marks keyframe, writes a JPEG header into the destination buffer, configures the bitstream buffer controller after the header, programs GBU/BBC, picture control, restart interval, Huffman and quantization tables, GDI source layout, MCU info, rotation, and starts the JPEG engine. Finish encode reads BBC write pointer to set payload, reports macroblock errors, flushes BBC, propagates metadata/LAST, returns buffers, and resets the VPU to avoid context-switch hangs.

Direct CODA960 decode startup seeds default quantization tables. Prepare decode parses the input header each frame, chooses scaling from requested capture size, configures picture/GDI/BBC/GBU state, installs user Huffman/quantization tables, sets restart state and DPCM diffs, points GDI at the destination buffer, and starts the JPEG engine. Finish decode reads error state, flushes BBC, returns source/destination buffers with metadata and full capture payload, and resets hardware.

## State and Persistence
JPEG state lives in `ctx->params`: quantization table pointers, quantization table indexes, Huffman table selectors, generated encode Huffman data, parsed decode Huffman tables, restart interval, quality, chroma subsampling, and `ctx->jpeg_ecs_offset`. Default static tables are shared read-only except `luma_q`/`chroma_q` are mutable arrays used as defaults. No filesystem persistence exists.

## Dependencies and Integration Points
This file depends on V4L2 JPEG parser helpers, V4L2 mem2mem/vb2, dma-contig addresses, unaligned big-endian writes, CODA register definitions, GDI programming from `coda-gdi.c`, base-address helper `coda_write_base()`, hardware reset from `coda-bit.c`, and common EOS handling through `coda_m2m_buf_done()`.

## Risks and Edge Cases
JPEG parser support is intentionally narrow: baseline three-component 4:2:0/4:2:2 input, 8-bit quantization tables, and four Huffman tables. `coda_jpeg_check_buffer()` assumes the source is CPU mapped and large enough to read marker bytes. Direct encode logs but does not fail on stride mismatch. Several busy loops wait on hardware without all having explicit timeouts; encode GDI wait has a 100 ms timeout, decode GDI wait does not. `coda9_jpeg_irq_handler()` unlocks `dev->coda_mutex` when no current context is found even though the threaded handler did not lock it, which is a notable risk.

## Test Signals
Useful signals include JPEG header parsing failures for malformed markers/tables, subsampling-driven capture format changes, quality control changing quant tables, valid SOI/EOI trimming, direct JPEG encode producing standards-compliant headers and EOI payloads, decode scaling by 1/2/4/8, overflow timeout reporting when capture buffers are too small, error macroblock handling, and repeated encode/decode context switches without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg2.c

## Purpose
`coda-mpeg2.c` provides small MPEG-2 helper functions for the CODA decoder. It maps firmware/header profile and level IDs to V4L2 controls and detects whether the first source buffer contains enough sequence/extension header bytes to be repeated as padding for CODA sequence initialization.

## Important APIs, Types, and Functions
Public functions are `coda_mpeg2_profile()`, `coda_mpeg2_level()`, and `coda_mpeg2_parse_headers()`. The profile mapper translates MPEG-2 profile IDs 5, 4, 3, 2, and 1 into simple, main, SNR scalable, spatially scalable, and high V4L2 enums. The level mapper translates IDs 10, 8, 6, and 4 into low, main, high-1440, and high. Unknown values return `-EINVAL`.

## Control Flow
`coda_update_profile_level_ctrls()` uses the mapping helpers after decoder sequence initialization reports parsed profile/level. `coda_bitstream_try_queue()` calls `coda_mpeg2_parse_headers()` when the first buffer is shorter than 512 bytes. The parser requires a sequence header start code at offset 0, then accepts either a 22-byte header with extension at offset 12 or an 86-byte form with quantization matrix and extension at offset 76, optionally followed by another start-code prefix.

## State and Persistence
This file has no persistent state. It only reads caller-provided buffers and returns enum values or detected header size.

## Dependencies and Integration Points
It depends on V4L2 MPEG-2 control enums and `struct coda_ctx` only for interface consistency. It integrates with `coda-bit.c` initial bitstream padding and `coda-common.c` read-only profile/level control updates.

## Risks and Edge Cases
Header detection is intentionally pattern-based rather than a full MPEG-2 parser. It only recognizes headers at the start of the buffer and fixed 22/86 byte variants; unusual valid headers may not be padded, causing sequence initialization to rely on userspace providing enough initial data. Unknown profile/level values expand/log through higher-level control code rather than being accepted silently.

## Test Signals
Tests should cover all profile/level mappings, 22-byte and 86-byte sequence-extension examples, buffers with following start-code prefixes, too-short or wrong-start-code buffers returning zero, and decoder startup with a first MPEG-2 buffer below 512 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg4.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg4.c

## Purpose
`coda-mpeg4.c` provides MPEG-4 Visual helper functions for the CODA decoder. It maps MPEG-4 profile/level IDs into V4L2 menu values and detects compact initial MPEG-4 headers for bitstream padding during decoder sequence initialization.

## Important APIs, Types, and Functions
Public functions are `coda_mpeg4_profile()`, `coda_mpeg4_level()`, and `coda_mpeg4_parse_headers()`. Profile mappings include simple, advanced simple, core, simple scalable, and advanced coding efficiency. Levels 0 through 5 map directly to V4L2 MPEG-4 level constants. Unknown values return `-EINVAL`.

## Control Flow
After sequence initialization, `coda_update_profile_level_ctrls()` uses these mappers to update read-only MPEG-4 controls from firmware header reports. During initial bitstream queuing, `coda_bitstream_try_queue()` calls `coda_mpeg4_parse_headers()` for short first buffers. The parser requires a visual object sequence start code at offset 0 and visual object start at offset 5, then accepts header lengths of 30, 31, or 32 bytes if the buffer ends there or the next bytes begin with a start-code prefix.

## State and Persistence
The file is stateless. It reads caller buffers and returns profile/level enums or header byte counts.

## Dependencies and Integration Points
It depends on V4L2 MPEG-4 control enums and the CODA private header for prototypes. It integrates with decoder bitstream padding in `coda-bit.c` and profile/level control updates in `coda-common.c`.

## Risks and Edge Cases
The header parser is a fixed-pattern recognizer, not a full MPEG-4 parser. Valid streams with different object/header arrangements may not be detected for padding, which can make firmware sequence initialization sensitive to first-buffer size. Profile mapping supports only the IDs the driver expects from CODA firmware or common streams.

## Test Signals
Tests should cover profile/level mapping success and `-EINVAL`, 30/31/32-byte header recognition, next-start-code recognition, rejection of too-short buffers and wrong start codes, and successful decoder startup with small initial MPEG-4 buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda.h

## Purpose
`coda.h` is the private driver contract for the Chips&Media CODA V4L2 mem2mem codec. It defines product IDs, device and context state, codec/queue/parameter structures, buffer metadata, context operation callbacks, helper prototypes, debug macros, and cross-file symbols shared by common, BIT, GDI, H.264, MPEG-2, MPEG-4, and JPEG implementation files.

## Important APIs, Types, and Functions
Key enums are `coda_inst_type` for encoder/decoder contexts and `coda_product` for CODA_DX6/HX4/7541/960 products. `struct coda_devtype` describes per-platform firmware names, codec tables, video nodes, and buffer sizes. `struct coda_dev` stores the V4L2 device, video nodes, clocks, reset, MMIO, firmware buffers, IRAM, workqueue, m2m device, locks, ID allocator, debugfs root, and MB-error ratelimiter.

`struct coda_params` stores codec controls and dynamic-change flags for H.264, MPEG-2, MPEG-4, JPEG, rate control, GOP, slice mode, framerate, VBV, rotation/mirroring, and force-keyframe state. `struct coda_q_data` stores per-queue format and crop/compose data. `struct coda_buffer_meta` carries source sequence/timecode/timestamp/ring positions/LAST across decoder reordering. `struct coda_iram_info` tracks per-context secondary AXI SRAM allocations. `struct coda_context_ops` is the polymorphic interface for BIT and direct JPEG contexts. `struct coda_ctx` is the large per-file-handle state object that ties all of this together.

Public prototypes expose register access, base-address writing, aux buffer allocation, queue initialization, hardware reset, bitstream fill/flush/end handling, GDI setup, firmware checking, H.264/MPEG/JPEG helper functions, profile-level control updates, mem2mem buffer completion, context ops, and IRQ handlers.

## Control Flow
The header shapes how `coda-common.c` dispatches operations. Each opened video node selects a `coda_video_device`, which points at one `coda_context_ops` table. Queue callbacks call the queue init functions declared here. The mem2mem work path invokes `prepare_run`, IRQ handlers complete `ctx->completion`, and common work then calls `finish_run` or `run_timeout`. Helper prototypes connect codec-specific parsing/generation functions into the generic queue and command flows.

## State and Persistence
All persistent runtime state is in `struct coda_dev` and `struct coda_ctx`; the header itself stores no runtime data. Driver persistence consists of allocated DMA/IRAM buffers, debugfs blobs, firmware image contents in `codebuf`, queued buffer metadata, and cached V4L2 control/format state. There is no filesystem data written by this driver.

## Dependencies and Integration Points
The header includes Linux debugfs, IDA, IRQ, mutex, kfifo, videodev2, ratelimit, V4L2 controls/device/file-handle, vb2-v4l2, and `coda_regs.h`. It integrates every source file in this directory and exposes the CODA-specific user control `V4L2_CID_CODA_MB_ERR_CNT`.

## Risks and Edge Cases
Because `struct coda_ctx` spans hardware state, vb2 queues, codec params, bitstream ring state, debugfs, VDOA, and synchronization primitives, layout/semantic changes have broad impact. Several fields are protected by different locks (`dev_mutex`, `coda_mutex`, `buffer_mutex`, `bitstream_mutex`, `wakeup_mutex`, `buffer_meta_lock`); callers must preserve those ownership rules. The inline `coda_bitstream_can_fetch_past()` is declared both inline and as a prototype, relying on the inline definition used by current code. `coda_params` mixes encoder controls and decoder parsed values, so control initialization must match context type.

## Test Signals
Header-level validation is compile/link coverage across all CODA objects, correct video-node context ops selection, no missing prototypes, controls wired to `struct coda_ctx` fields, lockdep coverage for command paths, decoder timestamp metadata integrity, and successful module load/open/stream/release for each supported product node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda.h -->
