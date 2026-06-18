# Group Research: group_1524_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_jpeg_jdcolor_c_sources__256c38828980

Scope: `Docs/research_subset_a.md`; source tree is `sources/os/plan9/plan9`. Files are part of the Plan 9 Ghostscript vendored Independent JPEG Group decoder/encoder support code, centered on JPEG decompression color conversion, marker/input control, Huffman entropy decoding, IDCT/DCT plumbing, upsampling, postprocessing, and error reporting.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcolor.c

Purpose: output colorspace conversion for JPEG decompression.

Key structures and routines:
- `my_color_deconverter` extends `jpeg_color_deconverter` with cached YCbCr conversion tables.
- `build_ycc_rgb_table()` precomputes fixed-point Cb/Cr contribution tables for YCbCr to RGB/YCCK conversion.
- `ycc_rgb_convert()` converts planar YCbCr rows to interleaved RGB using `sample_range_limit`.
- `null_convert()` interleaves component planes without changing colorspace.
- `grayscale_convert()` copies luminance-only output, including YCbCr to grayscale by ignoring chroma.
- `gray_rgb_convert()` expands grayscale samples into RGB triples.
- `ycck_cmyk_convert()` handles Adobe-style YCCK to CMYK by converting YCbCr to inverted RGB-style CMY and passing K through.
- `jinit_color_deconverter()` validates component counts, selects conversion method, sets `out_color_components`, and clears `component_needed` for unused chroma in grayscale output.

Important behavior:
- Uses fixed-point scale `SCALEBITS = 16` to avoid floating point in hot loops.
- Range limiting is mandatory after lossy DCT reconstruction and color math.
- Supports grayscale, RGB, CMYK, YCbCr, YCCK, and null same-colorspace conversion; unsupported conversions call `JERR_CONVERSION_NOTIMPL`.
- If `quantize_colors` is enabled, final `output_components` is one colormapped component.

Dependencies:
- Requires `jinclude.h`, `jpeglib.h`, JPEG memory manager allocation, error macros, and RGB layout macros such as `RGB_RED`, `RGB_GREEN`, `RGB_BLUE`, `RGB_PIXELSIZE`.

Notes:
- This is image-decoder infrastructure embedded in the Plan 9 source tree via Ghostscript, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdct.h

Purpose: private shared declarations for forward and inverse DCT modules.

Key definitions:
- `DCTELEM` is `int` for 8-bit samples and `INT32` for wider sample builds.
- Function pointer types: `forward_DCT_method_ptr`, `float_DCT_method_ptr`.
- IDCT multiplier table element types: `ISLOW_MULT_TYPE`, `IFAST_MULT_TYPE`, `FLOAT_MULT_TYPE`.
- `IDCT_range_limit(cinfo)` and `RANGE_MASK` define the bulletproof post-IDCT range-limiting convention.
- External declarations for forward DCTs: `jpeg_fdct_islow`, `jpeg_fdct_ifast`, `jpeg_fdct_float`.
- External declarations for inverse DCTs: `jpeg_idct_islow`, `jpeg_idct_ifast`, `jpeg_idct_float`, reduced-size IDCTs `4x4`, `2x2`, `1x1`.
- Fixed-point arithmetic helpers: `ONE`, `CONST_SCALE`, `FIX`, `DESCALE`, `MULTIPLY16C16`, `MULTIPLY16V16`.

Important behavior:
- Documents the convention that forward DCT output is scaled up by 8.
- IDCT routines are expected to perform dequantization and range limiting themselves.
- Supports old toolchains with optional short external names and multiply-cast tuning macros.

Dependencies:
- Consumed by DCT manager and individual DCT/IDCT implementations.
- Depends on JPEG scalar types, `DCTSIZE`, `DCTSIZE2`, `BITS_IN_JSAMPLE`, and right-shift macros from the JPEG portability layer.

Notes:
- This header is central to the decoder/encoder DCT ABI inside the vendored IJG code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jddctmgr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jddctmgr.c

Purpose: inverse-DCT manager for decompression.

Key structures and routines:
- `my_idct_controller` extends `jpeg_inverse_dct` and tracks the current IDCT method per component.
- `multiplier_table` union reserves enough storage for slow integer, fast integer, and float multiplier tables.
- `start_pass()` chooses the IDCT implementation per component and builds the dequantization multiplier table.
- `jinit_inverse_dct()` allocates the controller and per-component multiplier tables.

Important behavior:
- Handles reduced-size IDCTs when `IDCT_SCALING_SUPPORTED` is compiled in: 1x1, 2x2, and 4x4 use ISLOW-style multiplier tables.
- Full-size IDCT selection follows `cinfo->dct_method`: `JDCT_ISLOW`, `JDCT_IFAST`, or `JDCT_FLOAT`, depending on compile-time support.
- Skips table rebuilds when the component is not needed or the table already matches the active method.
- If a component has not yet latched a quantization table in buffered-image mode, its multiplier table remains zeroed, producing neutral output.

Dependencies:
- Uses quant tables saved in `jpeg_component_info.quant_table`.
- Calls IDCT routines declared in `jdct.h`.
- Relies on JPEG memory manager and compile-time feature macros.

Notes:
- No per-block IDCT work happens here; this file only performs pass setup and table preparation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jddctmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.c

Purpose: sequential Huffman entropy decoder for JPEG decompression.

Key structures and routines:
- `savable_state` stores per-component DC predictors.
- `huff_entropy_decoder` stores bitreader state, restart countdown, derived DC/AC tables, per-MCU table pointers, and per-block needed flags.
- `start_pass_huff_decoder()` validates sequential scan parameters, derives Huffman tables, initializes predictors and restart state, and precomputes block-level table/need metadata.
- `jpeg_make_d_derived_tbl()` expands a public JPEG Huffman table into fast decode tables and validates table shape.
- `jpeg_fill_bit_buffer()` loads entropy-coded bytes, handles stuffed `FF/00`, detects markers, supports suspension, and pads missing data with zero bits after warning.
- `jpeg_huff_decode()` handles slow-path Huffman symbol decoding beyond the lookahead table.
- `process_restart()` consumes restart markers, resets bit state and DC predictors.
- `decode_mcu()` decodes one MCU’s DC and AC coefficients into dezigzagged natural order.
- `jinit_huff_decoder()` allocates and wires the entropy decoder.

Important behavior:
- Supports input suspension by copying permanent state into local working variables and committing only after a full MCU succeeds.
- Uses `HUFF_LOOKAHEAD` acceleration from `jdhuff.h`.
- AC values can be discarded for components or scaled outputs that do not need them.
- Corrupt/truncated entropy data degrades to warnings and zero-filled coefficients where possible.
- Restart markers reset DC predictors and bit-buffer state.

Dependencies:
- Shares bitreader and Huffman derived table declarations with `jdphuff.c` through `jdhuff.h`.
- Uses `jpeg_natural_order[]`, marker reader restart handling, source manager callbacks, and JPEG error macros.

Notes:
- This is the baseline/sequential counterpart to `jdphuff.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.h

Purpose: private shared declarations and hot-path macros for sequential and progressive Huffman decoders.

Key definitions:
- `HUFF_LOOKAHEAD = 8`.
- `d_derived_tbl` stores `maxcode`, `valoffset`, public table backlink, and lookahead decode tables.
- `bit_buf_type`, `BIT_BUF_SIZE`, `bitread_perm_state`, and `bitread_working_state` define entropy bit-buffer state.
- `BITREAD_STATE_VARS`, `BITREAD_LOAD_STATE`, and `BITREAD_SAVE_STATE` manage suspension-safe local/permanent state transfer.
- `CHECK_BIT_BUFFER`, `GET_BITS`, `PEEK_BITS`, `DROP_BITS` implement inline bit access.
- `HUFF_DECODE` implements the fast lookahead path with fallback to `jpeg_huff_decode()`.

Important behavior:
- The macros assume `get_buffer` and `bits_left` are local variables, which is why decode functions have a specific shape.
- `jpeg_fill_bit_buffer()` may return false for source suspension; callers provide an action.
- `HUFF_DECODE` returns symbols directly for common short codes and jumps to a caller-provided slow label otherwise.

Dependencies:
- Implementations live in `jdhuff.c`; progressive decoder reuses them.
- Depends on source-manager buffer state and JPEG scalar types.

Notes:
- This header is performance-critical and intentionally macro-heavy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdhuff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdinput.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdinput.c

Purpose: input controller for decompression, coordinating marker parsing and compressed scan consumption.

Key structures and routines:
- `my_input_controller` extends `jpeg_input_controller` with `inheaders`.
- `initial_setup()` validates dimensions, precision, component count, sampling factors, initializes component block/sample dimensions, and determines multi-scan status.
- `per_scan_setup()` computes MCU geometry for single-component and interleaved scans.
- `latch_quant_tables()` saves the quant table actually used by each component’s first scan.
- `start_input_pass()` sets up per-scan MCU geometry, latches quant tables, starts entropy and coefficient controllers, and switches `consume_input` to coefficient consumption.
- `finish_input_pass()` switches `consume_input` back to marker consumption.
- `consume_markers()` reads markers until SOS/EOI/suspension and coordinates first versus later scans.
- `reset_input_controller()` resets stream state and related marker/error/progression state.
- `jinit_input_controller()` allocates and initializes the controller.

Important behavior:
- Separates header/marker consumption from compressed coefficient consumption by swapping the `consume_input` method pointer.
- Supports multi-scan and progressive files by allowing later SOS markers only when expected.
- Quant tables are copied per component so later table-slot reuse does not corrupt final dequantization.
- Initializes transcoder-relevant dimensions even when full decompression master setup is not used.

Dependencies:
- Marker reader, entropy decoder, coefficient controller, JPEG memory manager, and error manager.

Notes:
- This is the central bridge between `jdmarker.c` and entropy/coefficient decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdinput.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmainct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmainct.c

Purpose: main decompression buffer controller between coefficient decoding and postprocessing.

Key structures and routines:
- `my_main_controller` extends `jpeg_d_main_controller` with per-component work buffers and optional context-row pointer machinery.
- `alloc_funny_pointers()`, `make_funny_pointers()`, `set_wraparound_pointers()`, and `set_bottom_pointers()` build pointer lists that provide above/below context rows without copying sample rows.
- `start_pass_main()` selects simple, context-row, or post-crank processing mode.
- `process_data_simple_main()` handles the normal no-context path, fetching one iMCU row and feeding row groups to postprocessing.
- `process_data_context_main()` handles fancy upsamplers that require vertical context rows.
- `process_data_crank_post()` runs the postprocessor alone for the final two-pass quantization pass.
- `jinit_d_main_controller()` allocates row-group buffers and optional context pointer lists.

Important behavior:
- Raw-data output bypasses this controller.
- Context mode needs `min_DCT_scaled_size >= 2`; otherwise it errors with `JERR_NOTIMPL`.
- Uses row groups as the unit passed to postprocessing.
- Bottom edge handling duplicates the last real sample row by pointer aliasing.
- Does not support full-image main buffers; those live in coefficient or post controllers.

Dependencies:
- Coefficient controller `decompress_data`, postprocessor `post_process_data`, upsampler `need_context_rows`, JPEG memory manager.

Notes:
- The “funny pointer” design is an optimization to avoid copying retained context rows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmainct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmarker.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmarker.c

Purpose: JPEG marker parser and restart-marker recovery logic.

Key structures and routines:
- `JPEG_MARKER` enum defines SOF/SOS/DQT/DHT/DRI/APP/COM/RST marker codes.
- `my_marker_reader` extends `jpeg_marker_reader` with overridable COM/APPn processors and marker-saving state.
- Input macros `INPUT_VARS`, `INPUT_SYNC`, `INPUT_BYTE`, `INPUT_2BYTES` support suspension-safe parsing.
- `get_soi()`, `get_sof()`, `get_sos()`, `get_dac()`, `get_dht()`, `get_dqt()`, `get_dri()` parse core marker types.
- `examine_app0()` recognizes JFIF/JFXX APP0 metadata.
- `examine_app14()` recognizes Adobe APP14 metadata and transform flag.
- `get_interesting_appn()` inspects APP0/APP14 without saving the full marker.
- `save_marker()` optionally stores COM/APPn payloads in `marker_list`.
- `skip_variable()` skips unneeded variable-length markers.
- `next_marker()` finds the next marker after entropy data, warning about extraneous bytes.
- `first_marker()` enforces initial SOI.
- `read_markers()` dispatches marker handling until SOS, EOI, or suspension.
- `read_restart_marker()` verifies expected RSTn markers.
- `jpeg_resync_to_restart()` implements default recovery from missing/wrong restart markers.
- `reset_marker_reader()` and `jinit_marker_reader()` initialize parser state.
- `jpeg_save_markers()` and `jpeg_set_marker_processor()` expose marker customization hooks.

Important behavior:
- Designed for suspending data sources; marker parameters are reprocessed after suspension unless saving-marker state has advanced the restart point.
- Rejects unsupported SOF types such as lossless/differential modes.
- Parses DQT values from zigzag order into natural order.
- Minimal DHT validation occurs here; deeper Huffman validation occurs in `jdhuff.c`.
- Ignores DNL by skipping it, while zero image dimensions are rejected at SOF.
- APP0 and APP14 are interpreted even when not saved, because they affect density/colorspace transform assumptions.

Dependencies:
- Source manager callbacks `fill_input_buffer`, `skip_input_data`, `resync_to_restart`.
- JPEG memory manager, quant/Huffman table allocation, error/trace macros.

Notes:
- This is one of the main robustness boundaries for malformed JPEG streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmarker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmaster.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmaster.c

Purpose: master decompression controller that selects modules and coordinates output passes.

Key structures and routines:
- `my_decomp_master` extends `jpeg_decomp_master` with pass count, merged-upsample flag, and saved quantizer pointers.
- `use_merged_upsample()` determines whether `jdmerge.c` can replace separate upsampling and color conversion.
- `jpeg_calc_output_dimensions()` computes output dimensions, IDCT scaling choices, component downsampled dimensions, output component count, and recommended output buffer height.
- `prepare_range_limit_table()` builds the shared table used for clamping and post-IDCT signed-to-unsigned conversion.
- `master_selection()` initializes all selected decompression modules.
- `prepare_for_output_pass()` starts the modules needed for each output pass and handles two-pass quantization dummy/final passes.
- `finish_output_pass()` completes quantization and increments pass count.
- `jpeg_new_colormap()` switches external colormaps in buffered-image mode.
- `jinit_master_decompress()` allocates the master controller and performs module selection.

Important behavior:
- Supports IDCT scaling to 1/8, 1/4, 1/2, or full output where compiled.
- Chooses merged upsampling only for YCbCr to RGB, 2h1v/2h2v sampling, no fancy upsampling, no CCIR601, and compatible scaling.
- Arithmetic-coded JPEG is explicitly rejected as not implemented.
- Initializes full coefficient buffering when needed for multiple scans or buffered-image mode.
- Range-limit table includes a masked region to keep corrupt IDCT output from indexing out of bounds.

Dependencies:
- Initializes color converter, upsampler/merged upsampler, post controller, IDCT manager, entropy decoder, coefficient controller, main controller, and memory virtual arrays.

Notes:
- This file is the decompression pipeline assembly point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmaster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmerge.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmerge.c

Purpose: optimized merged upsampling and YCbCr-to-RGB conversion.

Key structures and routines:
- `my_upsampler` extends `jpeg_upsampler` with an `upmethod`, YCbCr conversion tables, spare row buffer, row width, and rows remaining.
- `build_ycc_rgb_table()` duplicates the fixed-point table logic from `jdcolor.c`.
- `start_pass_merged_upsample()` resets spare-row and row-count state.
- `merged_2v_upsample()` handles 2:1 vertical sampling, including spare-row buffering when caller provides only one output row.
- `merged_1v_upsample()` handles 1:1 vertical sampling.
- `h2v1_merged_upsample()` converts one row group for 2h1v sampling.
- `h2v2_merged_upsample()` converts two output rows for 2h2v sampling.
- `jinit_merged_upsampler()` allocates state, selects 1v/2v method, allocates spare row if needed, and builds conversion tables.

Important behavior:
- Only supports YCbCr to RGB.
- Only supports 2:1 horizontal chroma expansion with 1:1 or 2:1 vertical expansion.
- Assumes `jdmaster.c` has already verified all preconditions.
- Computes chroma contribution once per pair or quartet of output pixels, reducing conversion work.
- Handles odd output widths with a separate final-column path.

Dependencies:
- Depends on `jdmaster.c` capability selection, RGB layout macros, sample range-limit table, JPEG memory manager.

Notes:
- This is a fast path; unsupported cases fall back to `jdsample.c` plus `jdcolor.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmerge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdphuff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdphuff.c

Purpose: progressive JPEG Huffman entropy decoder.

Key structures and routines:
- `savable_state` stores `EOBRUN` plus DC predictors.
- `phuff_entropy_decoder` stores bitreader state, restart countdown, derived tables, and active AC table.
- `start_pass_phuff_decoder()` validates progressive scan parameters, updates coefficient progression status, selects the MCU decode routine, derives tables, and initializes restart/bit state.
- `process_restart()` handles RST markers, resets DC predictors and EOB run count.
- `decode_mcu_DC_first()` decodes initial DC scans.
- `decode_mcu_AC_first()` decodes initial AC spectral scans with EOB run handling.
- `decode_mcu_DC_refine()` appends one refinement bit to DC coefficients.
- `decode_mcu_AC_refine()` handles AC successive approximation, including correction bits, new nonzero coefficients, EOB runs, and rollback on suspension.
- `jinit_phuff_decoder()` allocates the decoder and progression-status table `coef_bits`.

Important behavior:
- Compiled only under `D_PROGRESSIVE_SUPPORTED`.
- AC scans must contain exactly one component; DC scans may be multi-component.
- Scan order inconsistencies are warnings, while invalid scan parameters are fatal.
- AC refinement must undo newly nonzero coefficients if input suspension occurs mid-MCU, because future decoding depends on zero/nonzero state.
- Reuses Huffman bitreader and derived table machinery from `jdhuff.c`/`jdhuff.h`.

Dependencies:
- Requires coefficient buffers from the progressive coefficient controller path.
- Uses `jpeg_natural_order[]`, marker restart handling, error macros, and source-manager suspension semantics.

Notes:
- This is the progressive counterpart to `jdhuff.c`, with additional complexity for spectral selection and successive approximation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdphuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdpostct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdpostct.c

Purpose: decompression postprocessing controller for upsampling/color conversion and color quantization buffering.

Key structures and routines:
- `my_post_controller` extends `jpeg_d_post_controller` with an optional full-image virtual array, strip buffer, strip height, and strip row state.
- `start_pass_dpost()` selects one-pass, first-pass quantization, second-pass quantization, or pass-through behavior.
- `post_process_1pass()` runs upsampling into a strip buffer and then quantizes/emits rows.
- `post_process_prepass()` runs first pass of two-pass quantization, saving converted rows to a virtual full-image buffer and feeding the quantizer statistics.
- `post_process_2pass()` reads saved rows from the virtual buffer and emits quantized output.
- `jinit_d_post_controller()` allocates strip or full-image quantization buffers when needed.

Important behavior:
- If no color quantization is required, this controller delegates directly to the upsampler.
- Two-pass quantization requires a virtual full-image buffer rounded to the strip height.
- Strip height is `max_v_samp_factor`, matching efficient upsampler output granularity.
- In prepass, `out_row_ctr` is advanced even though no output is emitted so the caller can track completion.

Dependencies:
- Upsampler, color quantizer, JPEG memory manager virtual arrays, buffer-mode enum.

Notes:
- This controller is mostly bypassed for simple non-quantized output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdpostct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdsample.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdsample.c

Purpose: separate upsampling routines for decompression.

Key structures and routines:
- `my_upsampler` extends `jpeg_upsampler` with per-component color buffers, method pointers, row counters, rowgroup heights, and integer expansion factors.
- `start_pass_upsample()` resets row buffer and image-height state.
- `sep_upsample()` fills per-component upsampled buffers and calls color conversion.
- `fullsize_upsample()` aliases input data for full-size components.
- `noop_upsample()` handles components not needed downstream.
- `int_upsample()` implements generic integral-ratio replication.
- `h2v1_upsample()` and `h2v2_upsample()` implement fast box-filter replication for common 2:1 ratios.
- `h2v1_fancy_upsample()` and `h2v2_fancy_upsample()` implement triangle-filter interpolation for better visual quality.
- `jinit_upsampler()` validates sampling ratios, selects per-component methods, requests context rows where needed, and allocates buffers.

Important behavior:
- Upsampling input is counted in row groups.
- CCIR601 sampling is rejected as not implemented.
- Fancy 2h2v upsampling needs context rows from `jdmainct.c`.
- Fancy upsampling is disabled when `min_DCT_scaled_size == 1` because main controller cannot provide context rows there.
- Fractional sampling ratios are rejected with `JERR_FRACT_SAMPLE_NOTIMPL`.

Dependencies:
- Color converter, main controller context-row support, JPEG memory manager, component sampling geometry.

Notes:
- Merged fast-path cases may use `jdmerge.c` instead of this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdtrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdtrans.c

Purpose: transcoding decompression support for reading raw DCT coefficient arrays.

Key routines:
- `jpeg_read_coefficients()` reads the whole JPEG image into virtual coefficient-block arrays and returns them.
- `transdecode_master_selection()` initializes only the decompression modules required for coefficient extraction.

Important behavior:
- On first call from `DSTATE_READY`, initializes transcoding mode and enters `DSTATE_RDCOEFS`.
- Consumes input until EOI, returning `NULL` on suspension.
- Sets `buffered_image = TRUE` and always uses a full-image coefficient buffer.
- Selects progressive Huffman or sequential Huffman entropy decoder; arithmetic coding is rejected.
- Initializes progress estimates based on progressive/multiscan/single-scan assumptions.
- After coefficient read completion, state becomes `DSTATE_STOPPING`; coefficient arrays remain available until `jpeg_finish_decompress()`.

Dependencies:
- Input controller, entropy decoder, coefficient controller, memory manager virtual arrays, progress manager.

Notes:
- This is for lossless JPEG transformations/transcoding workflows rather than pixel output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.c

Purpose: default JPEG library error, warning, trace, and message formatting implementation.

Key routines:
- Builds `jpeg_std_message_table[]` by reincluding `jerror.h` with `JMESSAGE` defined.
- `error_exit()` outputs the message, destroys the JPEG object, and exits with failure.
- `output_message()` formats and prints to stderr, or to a Windows message box if configured.
- `emit_message()` applies warning/trace policy.
- `format_message()` looks up the message template and formats string or integer parameters.
- `reset_error_mgr()` clears warning count and message code for a new image.
- `jpeg_std_error()` fills a `jpeg_error_mgr` with default methods and message tables.

Important behavior:
- Default fatal errors do not return; applications can override `error_exit` for `setjmp`/`longjmp` recovery.
- Only the first warning is printed unless trace level is at least 3, but all warnings are counted.
- Add-on message tables are supported.
- Uses `sprintf` into a buffer expected to be at least `JMSG_LENGTH_MAX`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jversion.h`, `jerror.h`, C stdio/stdlib behavior.

Notes:
- This is general IJG support used by both compression and decompression.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.h

Purpose: JPEG library message-code catalog and convenience macros for fatal errors, warnings, and trace output.

Key contents:
- `J_MESSAGE_CODE` enum is generated by `JMESSAGE` entries when first included normally.
- Message strings cover JPEG structure errors, unsupported features, memory/backing-store failures, marker parsing traces, quantization traces, and warnings.
- Fatal macros: `ERREXIT`, `ERREXIT1`, `ERREXIT2`, `ERREXIT3`, `ERREXIT4`, `ERREXITS`.
- Warning macros: `WARNMS`, `WARNMS1`, `WARNMS2`.
- Trace macros: `TRACEMS`, `TRACEMS1`, `TRACEMS2`, `TRACEMS3`, `TRACEMS4`, `TRACEMS5`, `TRACEMS8`, `TRACEMSS`.
- `MAKESTMT` wraps multi-statement macros safely.

Important behavior:
- Designed for reinclusion: without `JMESSAGE`, it declares the enum once; with `JMESSAGE`, it emits table entries.
- Error macros set `msg_code` and message parameters before dispatching through the installed error manager.
- String-parameter macros use `strncpy` into `msg_parm.s`.

Dependencies:
- Expects `jpeg_error_mgr` fields and constants like `JMSG_STR_PARM_MAX` from `jpeglib.h`.

Notes:
- This header is the message ABI for the JPEG library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jerror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctflt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctflt.c

Purpose: floating-point forward DCT implementation.

Key routine:
- `jpeg_fdct_float(FAST_FLOAT *data)` performs an in-place 8x8 forward DCT using two 1-D passes.

Important behavior:
- Compiled only when `DCT_FLOAT_SUPPORTED` is enabled.
- Enforces `DCTSIZE == 8` with a deliberate syntax error otherwise.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Processes rows first, then columns, with five key multiplies per 1-D DCT and constants such as `0.707106781`, `0.382683433`, `0.541196100`, and `1.306562965`.
- Produces scaled DCT coefficients for later quantization by the compression DCT manager.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, `FAST_FLOAT`.

Notes:
- Although grouped with decompression files, this is compression-side forward DCT code in the same JPEG module directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctflt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctfst.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctfst.c

Purpose: fast, lower-accuracy integer forward DCT implementation.

Key definitions and routine:
- `CONST_BITS = 8`.
- Precomputed AA&N constants: `FIX_0_382683433`, `FIX_0_541196100`, `FIX_0_707106781`, `FIX_1_306562965`.
- Optional inaccurate rounding override for speed when `USE_ACCURATE_ROUNDING` is not defined.
- `MULTIPLY(var,const)` multiplies and descales immediately.
- `jpeg_fdct_ifast(DCTELEM *data)` performs an in-place 8x8 two-pass forward DCT.

Important behavior:
- Compiled only when `DCT_IFAST_SUPPORTED` is enabled.
- Enforces `DCTSIZE == 8` with a deliberate syntax error otherwise.
- Uses the Arai, Agui, and Nakajima scaled DCT algorithm.
- Trades precision for fewer shifts, smaller fixed-point constants, and faster 16-bit-friendly intermediates.
- Intended to pair with quantization tables adjusted for the scaled DCT convention.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jdct.h`, fixed-point macros and `DCTELEM`.

Notes:
- This is compression-side DCT support included in the same vendored JPEG code batch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctfst.c -->