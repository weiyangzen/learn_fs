# Group Research: group_86_9front_sources_os_plan9_9front_sys_src_cmd_gs_jpeg_jdatasrc_c_sources_28785a4a332f

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front` under the bundled Ghostscript `gs/jpeg` IJG libjpeg source tree. I read all 17 listed files completely. This group covers decompression source input, coefficient buffering, color conversion, inverse DCT setup, Huffman/progressive Huffman entropy decoding, marker parsing, decompressor master control, upsampling, merged upsample/color conversion, transcoding coefficient reads, and the default error manager.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatasrc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatasrc.c

Standard stdio source manager for JPEG decompression input.

Key points:
- Defines a permanent `jpeg_source_mgr` wrapper around a caller-owned `FILE *`, a 4096-byte input buffer, and a `start_of_file` flag.
- `init_source` resets only the empty-file detection flag, deliberately preserving buffered bytes so multiple JPEG images can be read from one stream.
- `fill_input_buffer` reads via `JFREAD`, treats an empty file as fatal, but converts premature EOF after some data into a warning plus a synthetic EOI marker.
- `skip_input_data` consumes bytes from the current buffer and repeatedly refills as needed; it is simple stream-compatible skipping rather than `fseek`.
- `jpeg_stdio_src` allocates the source object and buffer in the permanent pool on first use, installs methods, and primes the manager with zero buffered bytes.

Dependencies and interactions:
- Used by applications before `jpeg_read_header`.
- Installs `jpeg_resync_to_restart` from `jdmarker.c` as the default restart resynchronizer.
- Not a core module; includes public headers plus `jerror.h`.

Risk notes:
- This source manager does not support input suspension because `fill_input_buffer` always returns `TRUE`.
- Mixing this source manager with a differently sized manager on the same decompression object is unsafe because its private object is permanent.
- Premature EOF recovery can produce partial image output with warnings rather than failing immediately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatasrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcoefct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcoefct.c

Decompression coefficient buffer controller between entropy decoding and inverse DCT output.

Key points:
- Tracks input-side MCU position, iMCU row position, optional full-image virtual coefficient arrays, and optional progressive block-smoothing latch state.
- In one-pass mode, allocates a single MCU buffer, decodes one iMCU row at a time, immediately applies per-component IDCT, skips unneeded components, and avoids right/bottom dummy blocks.
- In multi-scan or buffered-image mode, `consume_data` decodes MCUs into full-image virtual block arrays, while `decompress_data` later emits IDCT output from those arrays.
- Forces input consumption when output is about to overrun available coefficient data, allowing buffered progressive/multiscan output to proceed incrementally.
- Supports optional progressive block smoothing by estimating the first five AC coefficients from neighboring DC values when they are not yet fully known.
- `jinit_d_coef_controller` selects single-MCU or full-image buffering, requests padded virtual arrays, and adjusts access-window size for smoothing.

Dependencies and interactions:
- Calls entropy decoder `decode_mcu`, IDCT manager function pointers, input controller pass transitions, and memory manager virtual block APIs.
- Full-image coefficient arrays are also exposed to transcoding via `jpeg_read_coefficients`.

Risk notes:
- Single-pass suspension retries may leave partially assigned workspace coefficients, relying on caller zeroing before decode.
- Full buffering depends on `D_MULTISCAN_FILES_SUPPORTED`; otherwise multiscan/buffered operation fails at initialization.
- Block smoothing is progressive-only and requires available quant tables plus nonzero early quantizers to avoid invalid estimation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcoefct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcolor.c

Output colorspace conversion for decompression.

Key points:
- Builds fixed-point lookup tables for YCbCr/YCCK conversion to avoid inner-loop multiplications.
- Implements YCbCr-to-RGB, no-op planar-to-interleaved conversion, grayscale extraction, grayscale-to-RGB expansion, and Adobe YCCK-to-CMYK conversion.
- Uses `sample_range_limit` for RGB/YCCK outputs because DCT losses can push computed values outside sample range.
- Validates `jpeg_color_space` against `num_components` and selects conversion based on requested `out_color_space`.
- Marks chroma components unneeded when output is grayscale from grayscale or YCbCr, allowing earlier stages to avoid work.
- Sets `out_color_components` and final `output_components`, with color quantization reducing output to one colormapped component.

Dependencies and interactions:
- Called after upsampling unless merged upsample/color conversion is selected.
- Shares conversion constants and layout macros with `jdmerge.c` and public RGB configuration.

Risk notes:
- Unsupported conversions fail at initialization with `JERR_CONVERSION_NOTIMPL`.
- RGB no-op conversion is only used when `RGB_PIXELSIZE == 3`; other RGB layouts require explicit support.
- Color-space inference happens earlier in `jdapimin.c`, so this module depends on those defaults or application overrides being coherent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdct.h

Private shared declarations and arithmetic helpers for JPEG forward and inverse DCT modules.

Key points:
- Defines `DCTELEM` sizing for 8-bit versus wider sample builds and method pointer types for integer and floating FDCTs.
- Documents the FDCT convention: signed inputs, outputs scaled by 8, and quantization performed by the DCT manager.
- Defines multiplier-table element types for slow integer, fast integer, and floating IDCT implementations.
- Provides `IDCT_range_limit` and `RANGE_MASK` used by IDCT routines for fast safe sample limiting.
- Declares all compiled FDCT/IDCT variants, including reduced-size 4x4, 2x2, and 1x1 IDCTs.
- Supplies fixed-point helper macros: `FIX`, `DESCALE`, and portable 16x16 multiply variants.

Dependencies and interactions:
- Included by `jcdctmgr.c`, `jddctmgr.c`, and individual DCT/IDCT algorithm files.
- Assumes common integer-shift behavior supplied by `jmorecfg.h`/platform configuration.

Risk notes:
- This is private infrastructure; using it outside DCT managers couples code to IJG internals.
- Compile-time feature macros must match the functions linked into the build.
- Arithmetic macro tuning affects performance and portability but not the public API shape.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jddctmgr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jddctmgr.c

Inverse DCT manager for decompression output passes.

Key points:
- Allocates per-component multiplier tables large enough for any supported IDCT method and initializes them to zero.
- `start_pass` selects reduced-size IDCTs for scaled output or full-size IDCTs based on `cinfo->dct_method`.
- Builds method-specific dequantization multiplier tables from each component's latched quantization table.
- Skips rebuilding tables for unneeded components or when the existing table already matches the selected method.
- Leaves all-zero multiplier tables in buffered-image cases where output begins before a component's quant table has been seen.
- Supports slow integer, fast integer, and floating AA&N scaling when compiled.

Dependencies and interactions:
- Depends on quantization tables latched by `jdinput.c`.
- Supplies function pointers used by `jdcoefct.c` during coefficient-to-sample conversion.

Risk notes:
- Missing compiled DCT method support triggers `JERR_NOT_COMPILED`.
- Invalid per-component scaled sizes trigger `JERR_BAD_DCTSIZE`.
- Neutral gray fallback for unseen quant tables is intentional but can hide absent component data until later input arrives.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jddctmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.c

Sequential Huffman entropy decoder and shared Huffman table/bit-buffer routines.

Key points:
- Maintains bit-buffer state and DC prediction state so suspension can roll back to the start of the current MCU.
- `start_pass_huff_decoder` validates sequential scan parameters, derives active DC/AC Huffman tables, resets predictors, and precomputes per-block table and needed-coefficient flags.
- `jpeg_make_d_derived_tbl` validates Huffman code lengths, builds canonical decode tables, fills lookahead entries, and validates DC symbols.
- `jpeg_fill_bit_buffer` reads stuffed entropy bytes, detects markers, inserts zero bits after early segment termination, and preserves suspension state.
- `jpeg_huff_decode` handles slow-path over-lookahead Huffman decoding and returns a safe zero on corrupted overlong codes.
- `decode_mcu` decodes DC differences and AC run-length symbols into natural-order coefficients, or discards values for unneeded AC/DC paths.
- Restart processing discards unused bits, reads/recovers restart markers, resets DC predictors, and refreshes restart counters.

Dependencies and interactions:
- Shares `jdhuff.h` helpers with progressive Huffman decoding in `jdphuff.c`.
- Called by `jdcoefct.c` through the entropy decoder interface.
- Uses marker-reader restart handling from `jdmarker.c`.

Risk notes:
- Corrupt entropy data is often converted to warnings plus gray/zero-filled output rather than fatal errors.
- AC decoding relies on the padded `jpeg_natural_order` table to tolerate corrupted run lengths.
- Suspension correctness depends on only committing bit/source and predictor state after a complete MCU.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.h

Private shared declarations for sequential and progressive Huffman decompression.

Key points:
- Defines `d_derived_tbl`, containing max-code, value-offset, public table backlink, and 8-bit lookahead decode tables.
- Declares `jpeg_make_d_derived_tbl`, `jpeg_fill_bit_buffer`, and `jpeg_huff_decode`.
- Defines permanent and working bit-buffer state structures; working state copies source pointers to support suspension rollback.
- Provides `CHECK_BIT_BUFFER`, `GET_BITS`, `PEEK_BITS`, and `DROP_BITS` macros for hot entropy loops.
- Provides `HUFF_DECODE`, a fast lookahead-first symbol decoder with slow-path fallback for longer codes.
- Includes short external-name aliases for constrained linkers.

Dependencies and interactions:
- Included only by `jdhuff.c` and `jdphuff.c`.
- Assumes JPEG Huffman code requests never exceed 15 bits at once.

Risk notes:
- Macro arguments are evaluated in tightly constrained ways; callers must pass simple variables for bit counts.
- Bit-buffer type/size choices are fixed at 32-bit `INT32` here unless ported deliberately.
- This header exposes private entropy internals and should not become a general module dependency.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdinput.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdinput.c

Decompressor input controller for marker consumption, scan setup, and compressed-data pass transitions.

Key points:
- `initial_setup` validates dimensions, precision, component count, and sampling factors, then computes component block/sample dimensions and total iMCU rows.
- Detects whether the file has multiple scans based on first scan component count or progressive mode.
- `per_scan_setup` computes MCU geometry for interleaved and noninterleaved scans, including last-column/row dummy-block dimensions and MCU membership.
- `latch_quant_tables` copies each component's active quantization table at its first scan, protecting later output from table slot reuse between scans.
- `start_input_pass` prepares scan geometry, latches quant tables, starts entropy and coefficient input controllers, and switches `consume_input` to coefficient consumption.
- `consume_markers` drives marker reading until SOS/EOI, performs first-SOS setup, starts later scans, and handles tables-only datastreams.
- `reset_input_controller` resets error/marker/progression state for a new datastream.

Dependencies and interactions:
- Marker byte parsing is in `jdmarker.c`; entropy/coefficient scan consumers are initialized here.
- `jdtrans.c` relies on initial DCT sizing done here because it bypasses full `jdmaster.c`.

Risk notes:
- Precision must exactly match the compiled `BITS_IN_JSAMPLE`.
- Multiple scans are not expected unless detected up front; unexpected later SOS in single-scan mode is fatal.
- Quant table mutation after a component's first scan is ignored by design, matching JPEG scan semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdinput.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmainct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmainct.c

Main decompression buffer controller between coefficient output and postprocessing.

Key points:
- Holds downsampled component sample data in JPEG colorspace and feeds row groups to the postprocessor.
- Simple mode buffers one iMCU row, lets the coefficient controller fill it, and passes row groups through to upsampling/postprocessing.
- Context mode supports fancy vertical upsampling by creating two alternate "funny" pointer lists that preserve previous bottom row groups without copying data.
- Manufactures top and bottom context rows by pointer duplication, avoiding special cases in upsampling inner loops.
- Tracks context processing through `CTX_PREPARE_FOR_IMCU`, `CTX_PROCESS_IMCU`, and `CTX_POSTPONED_ROW`.
- Supports a crank-only path for the final pass of two-pass color quantization.
- Rejects full-image main buffering, since full buffering lives in coefficient or postprocessing controllers in this design.

Dependencies and interactions:
- Receives iMCU rows from `jdcoefct.c` and calls `jdpostct.c`.
- Context-row need is declared by `jdsample.c` when fancy 2h2v upsampling is selected.

Risk notes:
- Context rows are unsupported when `min_DCT_scaled_size < 2`.
- Bottom-of-image padding is delegated partly to the postprocessor/upsampler, so row counters must remain consistent.
- The pointer-list scheme is efficient but subtle; changes to row-group definitions can easily break it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmainct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmarker.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmarker.c

JPEG marker reader, marker parameter parser, restart resynchronizer, and APP/COM marker handling.

Key points:
- Defines JPEG marker codes and a permanent marker reader with overridable COM/APPn processors and optional marker-saving state.
- Byte-input macros preserve source restart points so marker parsing can suspend and reprocess safely.
- Parses SOI, SOF, SOS, DHT, DQT, DRI, optional DAC, APP0/JFIF, APP14/Adobe, COM, and unknown variable markers.
- SOI resets arithmetic tables, restart interval, colorspace assumptions, density defaults, and JFIF/Adobe flags.
- SOF validates image dimensions, component count, duplicate frame markers, component sampling, and quant-table selectors.
- SOS maps scan component IDs to SOF components, records entropy table selectors and spectral/progressive parameters, and increments scan count.
- DHT/DQT readers minimally validate lengths while converting quant tables from zigzag to natural order.
- APP0/APP14 are examined by default for JFIF/JFXX and Adobe transform metadata; other APP/COM markers are skipped unless saving or custom processors are installed.
- `next_marker` skips extraneous bytes and stuffed-zero sequences while warning about discarded data.
- `read_restart_marker` and `jpeg_resync_to_restart` implement stream-only restart recovery using discard, scan-forward, or leave-marker-unread strategies.
- `jpeg_save_markers` and `jpeg_set_marker_processor` expose application control over metadata retention and marker parsing.

Dependencies and interactions:
- Called by `jdinput.c` for header and inter-scan marker consumption.
- Entropy decoders call restart reading/resync methods at restart intervals.
- Source managers provide `fill_input_buffer`, `skip_input_data`, and optional custom restart resync.

Risk notes:
- Unsupported SOF types, reserved markers, arithmetic decoding in non-arithmetic builds, and malformed marker lengths are fatal.
- DNL is ignored, so files with initially unknown height are not supported.
- Saving very large APP/COM markers is bounded by the memory manager's max allocation chunk and can still consume image-pool memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmarker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmaster.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmaster.c

Master controller for decompression module selection, output dimensions, and pass orchestration.

Key points:
- `jpeg_calc_output_dimensions` computes 1/1, 1/2, 1/4, or 1/8 output scaling, chooses per-component IDCT scaled sizes, recomputes downsampled dimensions, and sets output component counts.
- `use_merged_upsample` gates the optimized merged path to non-fancy, non-CCIR, YCbCr-to-RGB, 2h1v/2h2v, unscaled component cases.
- `prepare_range_limit_table` builds the shared sample clamp/wrap table used by IDCT and color conversion.
- `master_selection` initializes color quantizers, color conversion/upsampling/postprocessing, inverse DCT, entropy decoder, coefficient controller, and main controller.
- Selects progressive versus sequential Huffman decoders; arithmetic coding is reported as not implemented.
- Chooses full coefficient buffering when input has multiple scans or buffered-image mode is enabled.
- Initializes virtual arrays, starts the first input pass, and sets progress accounting for multiscan input.
- `prepare_for_output_pass` chooses dummy versus real output passes, switches between one-pass/two-pass quantizers, and starts all active modules in pass order.
- `finish_output_pass` finishes quantizer work and advances pass count.
- `jpeg_new_colormap` supports switching external colormaps between buffered-image output passes when two-pass quantization is active.

Dependencies and interactions:
- Central integration point for `jdinput.c`, `jdcoefct.c`, `jddctmgr.c`, `jdhuff.c`/`jdphuff.c`, `jdcolor.c`, `jdsample.c`, `jdmerge.c`, `jdpostct.c`, and color quantizers.

Risk notes:
- Several options depend on compile-time feature macros; missing modules produce `JERR_NOT_COMPILED`.
- Quantization is incompatible with raw-data output.
- Merged upsampling constraints must remain synchronized with `jdmerge.c` capabilities.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmaster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmerge.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmerge.c

Optional merged upsampling and YCbCr-to-RGB color conversion for common decompression cases.

Key points:
- Compiled only when `UPSAMPLE_MERGING_SUPPORTED` is enabled.
- Combines simple chroma replication with color conversion, reducing repeated chroma contribution calculations.
- Supports only YCbCr-to-RGB with 2h1v or 2h2v sampling, no fancy upsampling, no CCIR601 alignment, and no upsample-time scaling.
- Builds the same fixed-point YCbCr-to-RGB tables as `jdcolor.c`.
- `merged_2v_upsample` emits two rows per row group when possible and uses a spare row if the client output buffer accepts only one row or the image has an odd final row.
- `merged_1v_upsample` handles the one-output-row case without spare buffering.
- `h2v1_merged_upsample` and `h2v2_merged_upsample` compute chroma-derived RGB offsets once per chroma sample and apply them to paired/four Y samples.

Dependencies and interactions:
- Selected only by `jdmaster.c` after capability checks.
- Replaces separate `jdcolor.c` and `jdsample.c` work for matching cases.

Risk notes:
- The initializer trusts `jdmaster.c`; it does not revalidate capabilities locally.
- Output width may be odd, so both merged kernels contain explicit final-column handling.
- This path implements box-filter upsampling only, so fancy upsampling must disable it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmerge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdphuff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdphuff.c

Progressive Huffman entropy decoder.

Key points:
- Compiled under `D_PROGRESSIVE_SUPPORTED`; otherwise the file contributes no decoder implementation.
- Extends savable entropy state with `EOBRUN` plus per-component DC predictors, preserving suspension rollback at MCU boundaries.
- `start_pass_phuff_decoder` validates progressive scan parameters, warns on suspect progression order, updates `coef_bits`, selects the scan-specific decode routine, and derives required Huffman tables.
- Supports four decode paths: DC first, AC first, DC refinement, and AC refinement.
- DC first decodes differences and writes coefficients shifted by `Al`; DC refinement ORs in the next approximation bit.
- AC first handles spectral bands, zero runs, and EOB runs, writing natural-order coefficients shifted by `Al`.
- AC refinement appends correction bits to existing coefficients and records newly nonzero coefficients so it can undo them if suspension occurs mid-MCU.
- Restart handling clears bit state, DC predictors, EOB runs, and restart counters.
- `jinit_phuff_decoder` allocates derived-table slots and initializes the per-component coefficient progression table to unknown.

Dependencies and interactions:
- Shares derived Huffman table and bit-buffer helpers with `jdhuff.c` through `jdhuff.h`.
- Requires full coefficient buffering in `jdcoefct.c` for progressive scans.

Risk notes:
- Bogus progression is mostly warned about rather than fatal, except invalid scan parameter structure.
- Large `Al` values are accepted liberally and may produce odd output rather than crashing.
- AC refinement is especially sensitive to suspension because newly nonzero coefficients alter later decoding semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdphuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdpostct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdpostct.c

Postprocessing controller for upsampling/color conversion and optional color quantization.

Key points:
- Directly delegates to the upsampler when no color quantization is requested.
- For one-pass color quantization or color precision reduction, uses a strip buffer between upsampling/color conversion and quantizer output.
- For two-pass quantization, can request a full-image virtual sample array, first saving upsampled color-converted rows for quantizer analysis, then replaying them through the quantizer.
- `start_pass_dpost` selects pass-through, save-and-pass, or crank-destination behavior based on buffer mode.
- `post_process_1pass` fills only as much strip data as can be emitted immediately, then quantizes it into the application output buffer.
- `post_process_prepass` scans new rows into the quantizer without emitting pixels and advances output counters for pass progress.
- `post_process_2pass` reads stored strips, clamps to bottom-of-image row count, and emits quantized pixels.

Dependencies and interactions:
- Receives row groups from `jdmainct.c` and invokes `jdsample.c`/`jdmerge.c` plus color quantizers.
- Full-image buffer allocation depends on `QUANT_2PASS_SUPPORTED`.

Risk notes:
- Two-pass paths fail if full-buffer support was not requested or not compiled.
- The one-pass path relies on the upsampler to detect bottom-of-image.
- Buffered-image output before two-pass quantization can reuse the virtual-array strip as temporary workspace.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdpostct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdsample.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdsample.c

Separate upsampling controller and per-component upsampling kernels.

Key points:
- Upsampling operates on row groups and then calls the color deconverter to emit interleaved output rows.
- `sep_upsample` fills a conversion buffer for one upsampled row group, color-converts available rows, and advances input row-group counters only after buffered rows are consumed.
- Full-size components avoid copying by pointing `color_buf` directly at input data.
- Unneeded components use a no-op method and are not allocated buffers.
- Generic integer-ratio upsampling replicates samples horizontally and vertically.
- Fast box-filter kernels handle common 2h1v and 2h2v cases.
- Fancy 2h1v and 2h2v kernels use triangle-filter interpolation; 2h2v requests context rows from `jdmainct.c`.
- `jinit_upsampler` validates sample ratios, rejects CCIR601 sampling and fractional ratios, selects methods, saves expansion factors, and allocates per-component color buffers only when needed.

Dependencies and interactions:
- Called by `jdpostct.c` unless `jdmerge.c` is selected.
- Depends on `jdmainct.c` to provide context rows for fancy 2h2v upsampling.
- Uses `jdcolor.c` for final colorspace conversion.

Risk notes:
- Fractional sampling ratios and CCIR601 alignment are not implemented.
- Fancy upsampling is disabled when `min_DCT_scaled_size == 1` because the main controller cannot provide context rows then.
- Generic integer upsampling uses simple replication, which is fast but visually weaker for uncommon high ratios.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdtrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdtrans.c

Transcoding decompression path for reading raw DCT coefficient arrays.

Key points:
- `jpeg_read_coefficients` initializes a reduced decompressor pipeline when called from `DSTATE_READY`, then consumes input until EOI into full-image coefficient arrays.
- Returns `NULL` on input suspension and otherwise returns the coefficient virtual-array descriptors.
- Can also expose coefficient arrays during buffered-image decompression after an output pass.
- Sets standalone coefficient-read state to `DSTATE_STOPPING` so `jpeg_finish_decompress` performs cleanup correctly.
- `transdecode_master_selection` marks `buffered_image`, selects progressive or sequential Huffman entropy decoding, always initializes full coefficient buffering, realizes virtual arrays, and starts the first input pass.
- Initializes progress estimates for progressive, multiscan, and single-scan inputs.

Dependencies and interactions:
- Requires `jpeg_read_header` from `jdapimin.c` before use.
- Bypasses normal `jdmaster.c` output modules and uses `jdinput.c`, entropy decoders, and `jdcoefct.c`.
- Coefficient arrays can be handed to compressor-side `jpeg_write_coefficients`.

Risk notes:
- Arithmetic-coded JPEG is not implemented.
- Progressive coefficient reads require `D_PROGRESSIVE_SUPPORTED`.
- Any later library call may reposition virtual-array backing storage, so callers cannot keep raw access pointers across calls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jerror.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jerror.c

Default IJG error, warning, trace, and message-formatting manager.

Key points:
- Builds `jpeg_std_message_table` by re-including `jerror.h` with `JMESSAGE` mapped to string entries.
- Default `error_exit` outputs the current message, destroys the JPEG object to clean temporary resources, and exits with failure.
- `output_message` formats the current message and writes it to stderr, or optionally to a Windows message box.
- `emit_message` prints the first warning by default, counts all warnings, and emits trace messages according to `trace_level`.
- `format_message` looks up standard or add-on message text, falls back on the generic bad-message string, and formats integer or string parameters.
- `reset_error_mgr` clears warning count and message code while preserving application method overrides and trace level.
- `jpeg_std_error` initializes all method pointers, message tables, trace/warning state, and add-on table bounds.

Dependencies and interactions:
- Used by both compressor and decompressor objects unless applications install custom handlers.
- Error macros throughout the library populate `err->msg_code` and `msg_parm` before calling these methods.

Risk notes:
- Default fatal handling exits the process; embedding applications usually need to override `error_exit` with `setjmp`/`longjmp` or equivalent recovery.
- Formatting uses `sprintf` into `JMSG_LENGTH_MAX`; message definitions must remain bounded.
- Warning policy suppresses repeated corrupt-data warnings unless high tracing is enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jerror.c -->