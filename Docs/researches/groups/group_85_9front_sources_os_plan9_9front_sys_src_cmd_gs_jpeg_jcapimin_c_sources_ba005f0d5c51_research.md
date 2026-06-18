# Group Research: group_85_9front_sources_os_plan9_9front_sys_src_cmd_gs_jpeg_jcapimin_c_sources_ba005f0d5c51

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front` under the bundled Ghostscript `gs/jpeg` IJG libjpeg source tree. I read all 21 listed files completely. This group covers compressor public APIs, compressor pipeline modules, Huffman entropy encoders, transcoding helpers, decompressor public APIs, stdio output destination, and the autoconf `jconfig.h` template.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapimin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapimin.c

Minimum public API for the JPEG compression object, shared by normal compression and coefficient transcoding.

Key points:
- `jpeg_CreateCompress` validates caller/library version and struct size, preserves the application-provided error manager/client data, zeroes the compressor struct, initializes the memory manager, clears permanent table/module pointers, sets default `input_gamma`, and enters `CSTATE_START`.
- `jpeg_destroy_compress` and `jpeg_abort_compress` are thin wrappers over common `jpeg_destroy`/`jpeg_abort`.
- `jpeg_suppress_tables` toggles every allocated quantization and Huffman table `sent_table` flag, supporting abbreviated datastream workflows.
- `jpeg_finish_compress` completes the active scan/raw/coefficient-writing state, drives remaining multipass output from buffered coefficients, writes EOI, terminates the destination, and aborts the object back to reusable start state.
- `jpeg_write_marker`, `jpeg_write_m_header`, and `jpeg_write_m_byte` allow COM/APP marker emission after compression start and before image data output, with state checks for scan/raw/coefficient modes.
- `jpeg_write_tables` writes a tables-only abbreviated JPEG datastream from `CSTATE_START`, initializes destination and marker writer, emits unsent tables, then deliberately does not abort so application-owned memory pool allocations are not unexpectedly freed.

Dependencies and interactions:
- Depends on `jinclude.h`, `jpeglib.h`, the memory manager, marker writer, destination manager, master controller, and coefficient controller.
- Normal applications also use `jcapistd.c` for `jpeg_start_compress` and scanline/raw write loops; transcoders combine this file with `jctrans.c`.

Risk notes:
- Marker-writing APIs require precise call timing; calling after scanline output begins is rejected.
- `jpeg_finish_compress` cannot tolerate suspension during post-first-pass buffered output and reports `JERR_CANT_SUSPEND`.
- Repeated `jpeg_write_tables` calls may leak image-pool marker/destination workspaces unless the application explicitly calls `jpeg_abort`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapimin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapistd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapistd.c

Standard public compression API for full pixel-to-JPEG compression.

Key points:
- `jpeg_start_compress` requires `CSTATE_START`, optionally unsuppresses all tables, resets error/destination managers, initializes the full compressor module graph via `jinit_compress_master`, prepares the first pass, sets `next_scanline = 0`, and enters either `CSTATE_RAW_OK` or `CSTATE_SCANNING`.
- `jpeg_write_scanlines` validates scanning state, warns on excess calls, updates progress, triggers delayed frame/scan marker output on the first call, caps input at remaining image height, and delegates to the main controller.
- `jpeg_write_raw_data` is the raw-downsampled-data entry point; it validates raw state, requires at least one iMCU row, triggers delayed headers, calls the coefficient controller directly, and advances `next_scanline` by one iMCU row.

Dependencies and interactions:
- Pulling in this file intentionally links the full compressor, unlike the smaller transcoding API path.
- Uses master, main, coefficient, progress, and destination module contracts initialized by `jcinit.c`.

Risk notes:
- Raw data writes must provide exactly compressor-shaped component planes with at least one full iMCU row.
- Extra scanlines in the final valid call are silently ignored, but calls after the image is complete only warn and return no useful progress.
- Suspension is handled by returning fewer rows, so callers must honor returned row counts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapistd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccoefct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccoefct.c

Compressor coefficient buffer controller between forward DCT/quantization and entropy encoding.

Key points:
- Defines `my_coef_controller`, tracking iMCU row state, MCU position within row, a per-MCU block pointer buffer, and optional full-image virtual coefficient arrays.
- Supports pass-through single-pass mode and, when enabled, full coefficient buffering for Huffman optimization or multiscans.
- `start_iMCU_row` computes how many MCU rows belong to the current iMCU row, including partial bottom rows for noninterleaved scans.
- `compress_data` performs forward DCT for one iMCU row in single-pass mode, fills right/bottom dummy blocks with zero AC coefficients and repeated DC coefficients, and sends each MCU to entropy encoding.
- `compress_first_pass` DCTs all image components into virtual block arrays, pads right/bottom dummy blocks in the arrays, then calls `compress_output` to emit the current scan.
- `compress_output` reads DCT block pointers from virtual arrays for the active scan and sends MCUs to the entropy encoder.
- `jinit_c_coef_controller` allocates either a single MCU workspace or padded full-image virtual arrays per component.

Dependencies and interactions:
- Calls `fdct->forward_DCT`, `entropy->encode_mcu`, and memory-manager virtual block array APIs.
- Used by `jcmainct.c` in normal compression, directly by raw-data input, and by master-driven additional passes.

Risk notes:
- Suspension in single-pass mode causes the current MCU to be re-DCTed on retry.
- Full coefficient buffering only exists when entropy optimization or multiscans are compiled in.
- Dummy block generation assumes `blkn-1` is valid when copying DC values at bottom/right edges; this follows established MCU ordering assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccoefct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccolor.c

Input color conversion module for compression.

Key points:
- Allocates a color converter with optional precomputed RGB-to-YCbCr tables.
- `rgb_ycc_start` builds fixed-point tables for CCIR 601-derived RGB to YCbCr conversion, including chroma offsets and rounding.
- Implements `rgb_ycc_convert`, `rgb_gray_convert`, `cmyk_ycck_convert`, `grayscale_convert`, and `null_convert`.
- Converts application interleaved input rows into libjpeg’s internal planar component buffers.
- `jinit_color_converter` validates `input_components` against `in_color_space`, validates `num_components` against `jpeg_color_space`, selects a conversion function, and installs `rgb_ycc_start` only when table-backed conversion is needed.

Dependencies and interactions:
- Called by `jcprepct.c` before downsampling.
- Relies on `RGB_RED`, `RGB_GREEN`, `RGB_BLUE`, and `RGB_PIXELSIZE` configuration from the public headers.

Risk notes:
- Only selected conversions are implemented: RGB to YCbCr/grayscale, CMYK to YCCK, direct pass-through, and grayscale extraction.
- Unsupported colorspace combinations fail at initialization.
- Conversion math assumes samples are in the configured `0..MAXJSAMPLE` range.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcdctmgr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcdctmgr.c

Forward DCT manager and coefficient quantizer for compression.

Key points:
- Selects the active DCT implementation (`JDCT_ISLOW`, `JDCT_IFAST`, or `JDCT_FLOAT`) based on compile-time support and `cinfo->dct_method`.
- `start_pass_fdctmgr` verifies each component’s quantization table and builds scaled divisor tables for the chosen DCT method.
- Integer DCT path copies input samples into a centered workspace, runs the selected integer FDCT, then quantizes each coefficient with portable rounding for negative values.
- Floating DCT path uses reciprocal floating divisors and rounds via a bias technique.
- Initializes divisor arrays lazily per quant table and marks unused slots `NULL`.

Dependencies and interactions:
- Includes `jdct.h` for private DCT routine declarations.
- Called by the coefficient controller for block-row FDCT/quantization.
- Depends on quant tables prepared by `jcparam.c` or application-supplied table setup.

Risk notes:
- If a requested DCT method was not compiled, initialization errors with `JERR_NOT_COMPILED`.
- Quantization table absence is detected at pass start, not when parameters are set.
- The integer path’s division macro can trade correctness-preserving speed behavior via `FAST_DIVIDE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcdctmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.c

Sequential Huffman entropy encoder plus optimal Huffman table generator.

Key points:
- Maintains savable bit/DC predictor state so output suspension can roll back to the start of an MCU.
- `start_pass_huff` selects real encoding or statistics-gathering mode, prepares derived tables or count arrays, resets DC predictors, bit buffer, and restart state.
- `jpeg_make_c_derived_tbl` validates a `JHUFF_TBL`, derives canonical Huffman codes and sizes, rejects illegal/duplicate symbols, and fills `c_derived_tbl`.
- `encode_one_block` emits DC difference category/value bits and AC run-length/category/value symbols, including ZRL and EOB handling.
- `encode_mcu_huff` handles restart markers, encodes each block in the MCU, commits destination and predictor state only after the MCU succeeds, and updates restart counters.
- `finish_pass_huff` flushes pending bits.
- With `ENTROPY_OPT_SUPPORTED`, gather mode counts symbols and `jpeg_gen_optimal_table` builds length-limited canonical Huffman tables using JPEG section K.2-style adjustment.
- `finish_pass_gather` generates updated DC/AC tables once per used table.

Dependencies and interactions:
- Includes `jchuff.h`, sharing derived-table declarations and `MAX_COEF_BITS` with progressive Huffman.
- Called by `jccoefct.c`/`jctrans.c` through the entropy encoder interface.
- Marker emission uses restart marker constants and byte-stuffing rules.

Risk notes:
- Negative coefficient coding assumes two’s complement behavior, as comments state.
- Optimization mutates frequency arrays while generating tables; callers prevent multiple generation passes per table.
- Suspension support depends on destination managers respecting `next_output_byte`/`free_in_buffer` rollback semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.h

Private shared declarations for sequential and progressive Huffman compression.

Key points:
- Defines `MAX_COEF_BITS` as 10 for 8-bit samples and 14 otherwise, matching expected DCT coefficient magnitude ranges.
- Defines `c_derived_tbl`, holding encoder-side Huffman code and code-length lookup arrays for all possible byte-sized symbols.
- Declares `jpeg_make_c_derived_tbl` for expanding a public `JHUFF_TBL` into encoder lookup form.
- Declares `jpeg_gen_optimal_table` for building an optimal/length-limited public Huffman table from symbol frequencies.
- Provides short external-name aliases for constrained linkers.

Dependencies and interactions:
- Included by `jchuff.c` and `jcphuff.c` only.
- Depends on public compressor types from `jpeglib.h`.

Risk notes:
- This is private compressor infrastructure; other modules should not depend on it.
- Coefficient magnitude assumptions are tied to IJG’s supported 8-bit/12-bit sample modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcinit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcinit.c

Full-compressor module selection and initialization.

Key points:
- `jinit_compress_master` initializes master control for full compression.
- If not using raw data input, initializes color conversion, downsampling, and preprocessing controllers.
- Always initializes forward DCT.
- Selects entropy encoder: arithmetic coding is unimplemented; progressive mode uses progressive Huffman when compiled; otherwise sequential Huffman.
- Initializes coefficient controller with full buffering when multiscans or optimized Huffman coding require it.
- Initializes main controller, marker writer, realizes virtual arrays, and writes SOI immediately while delaying frame/scan headers.

Dependencies and interactions:
- Split from `jcmaster.c` so transcoders can use master logic without linking the full pixel pipeline.
- Calls almost every compressor module initializer in the normal path.

Risk notes:
- Arithmetic coding is a hard error.
- Progressive compression requires `C_PROGRESSIVE_SUPPORTED`.
- Marker header design intentionally permits application APP/COM marker insertion after SOI and before first scan data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmainct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmainct.c

Main buffer controller between preprocessing/downsampling and coefficient compression.

Key points:
- Defines a controller that tracks current iMCU row, row groups received, suspension state, pass mode, and component strip buffers.
- Full-image main buffering is present but disabled with `#undef FULL_MAIN_BUFFER_SUPPORTED`; normal operation uses strip buffers.
- `start_pass_main` installs the simple pass-through processor for non-raw input and returns immediately for raw-data mode.
- `process_data_simple_main` fills one iMCU row via `prep->pre_process_data`, returns for more input when incomplete, sends full rows to `coef->compress_data`, and uses an input-row-counter adjustment to handle output suspension without signaling false image completion.
- `jinit_c_main_controller` skips buffers for raw-data input or allocates per-component strip buffers sized to downsampled DCT block width and iMCU height.

Dependencies and interactions:
- Receives application scanlines from `jpeg_write_scanlines`.
- Drives `jcprepct.c` and `jccoefct.c`.

Risk notes:
- The suspension workaround manipulates `in_row_ctr`; callers must use returned counts exactly.
- Full-buffer modes are not available in this build path despite retained code.
- Raw-data input bypasses this module entirely.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmainct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmarker.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmarker.c

JPEG marker writer for compression.

Key points:
- Defines JPEG marker codes and a marker writer with `last_restart_interval` tracking.
- Low-level emitters write bytes, markers, and big-endian 16-bit values through the destination manager; marker-writing suspension is not supported.
- Emits DQT, DHT, optional DAC, DRI, SOF, SOS, JFIF APP0, Adobe APP14, arbitrary marker headers/bytes, SOI, EOI, and tables-only datastreams.
- `write_frame_header` emits needed DQT tables before SOF, determines baseline vs extended/progressive/arithmetic SOF marker, and warns on 16-bit quant tables in otherwise baseline files.
- `write_scan_header` emits needed entropy tables/conditioning, DRI if changed, then SOS.
- `write_file_header` emits SOI plus configured APP0/APP14; `write_tables_only` emits SOI, all unsent tables, and EOI.
- `jinit_marker_writer` installs all marker writer methods.

Dependencies and interactions:
- Used by `jcapimin.c`, `jcapistd.c`, `jcmaster.c`, and `jctrans.c`.
- Table `sent_table` flags from quant/Huffman table objects prevent duplicate marker output.

Risk notes:
- Applications using suspension must ensure buffer space for markers; this module errors if marker output cannot complete.
- Arbitrary marker APIs trust the caller to provide correct payload length and safe marker choice.
- SOF dimension fields cap emitted JPEG dimensions at 65535.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmarker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmaster.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmaster.c

Compressor master control: validation, scan setup, and pass scheduling.

Key points:
- `initial_setup` validates image dimensions, component counts, sample precision, sampling factors, scanline width overflow, component block/sample dimensions, and total iMCU rows.
- `validate_script` checks multscan/progressive scan scripts for component order, valid progression parameters, DC-before-AC rules, refinement sequence consistency, and complete data coverage.
- `select_scan_parameters` chooses current scan component list and spectral/successive approximation parameters from `scan_info` or creates a single sequential scan.
- `per_scan_setup` computes MCU geometry for interleaved and noninterleaved scans, MCU membership arrays, last-column/last-row widths, and restart interval derived from rows.
- `prepare_for_pass` orchestrates main input, Huffman optimization, and output passes, starting only the modules needed for the pass and controlling delayed marker output.
- `pass_startup` emits frame and scan headers on first scanline/raw-data call for single-pass compression.
- `finish_pass_master` advances pass type, scan number, and pass number.
- `jinit_c_master_control` allocates master state, validates parameters, determines progressive mode, forces optimized coding for progressive output, and computes total pass count.

Dependencies and interactions:
- Central coordinator for color conversion, downsampling, preprocessing, FDCT, entropy, coefficient, main, and marker modules.
- Used by normal compression and transcoding; `transcode_only` changes the initial pass type.

Risk notes:
- Progressive mode forces Huffman optimization as a compatibility/default-quality choice.
- Many optional modes depend on compile-time gates (`C_MULTISCAN_FILES_SUPPORTED`, `C_PROGRESSIVE_SUPPORTED`, `ENTROPY_OPT_SUPPORTED`).
- Scan script validation is strict; malformed or incomplete scripts fail before output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmaster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcomapi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcomapi.c

Common public API shared by compression and decompression objects.

Key points:
- `jpeg_abort` releases all nonpermanent memory pools, closes temporary virtual-array storage via the memory manager, resets compressor/decompressor global state, and clears decompressor marker lists.
- `jpeg_destroy` invokes the memory manager self-destruct method, nulls the memory manager pointer, and marks the object destroyed.
- `jpeg_alloc_quant_table` and `jpeg_alloc_huff_table` allocate permanent table structs and initialize `sent_table = FALSE`.

Dependencies and interactions:
- Called by compressor/decompressor-specific abort/destroy wrappers.
- Table allocation helpers are used by parameter setup, transcoding copy, and entropy optimization.

Risk notes:
- Closing application data source/destination streams is explicitly outside these routines.
- `jpeg_abort` keeps permanent allocations for reuse; callers expecting full cleanup must call `jpeg_destroy`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcomapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jconfig.cfg -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jconfig.cfg

Autoconf template for generated `jconfig.h`.

Key points:
- Contains `#undef` placeholders for compiler/platform capabilities: prototypes, unsigned char/short, `void`, `const`, char signedness, standard headers, BSD strings, `sys/types.h`, far pointers, short external names, and incomplete-type behavior.
- Under `JPEG_INTERNALS`, configures right-shift behavior, `INLINE`, default memory limits, and `NO_MKTEMP`.
- Under `JPEG_CJPEG_DJPEG`, enables BMP/GIF/PPM/Targa sample-app support by default, leaves Utah RLE disabled, and controls two-file command line, signal catcher, binary-mode handling, and progress reports.

Dependencies and interactions:
- Consumed by the old `configure` script to produce `jconfig.h`.
- The resulting macros affect public headers, core library internals, memory managers, and command-line utilities.

Risk notes:
- This is a template, not a usable configuration header until processed.
- Feature defaults are command-line app defaults and may differ from the Plan 9/Ghostscript build’s effective configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jconfig.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcparam.c

Optional compressor parameter-default and helper routines.

Key points:
- `jpeg_add_quant_table` scales caller-provided base quantization tables, clamps values, optionally enforces baseline range, and marks tables unsent.
- `jpeg_set_linear_quality`, `jpeg_quality_scaling`, and `jpeg_set_quality` implement IJG’s default luminance/chrominance quant tables and 0-100 quality curve.
- `add_huff_table` copies and lightly validates Huffman table counts/symbols.
- `std_huff_tables` installs JPEG standard 8-bit luminance/chrominance DC/AC tables.
- `jpeg_set_defaults` allocates permanent `comp_info`, sets default precision, quality, Huffman tables, arithmetic conditioning, scan/raw/entropy/DCT/restart/JFIF defaults, and then selects a default JPEG colorspace.
- `jpeg_default_colorspace` maps input colorspaces to preferred JPEG colorspaces.
- `jpeg_set_colorspace` sets component count, IDs, sampling factors, quant/Huffman table assignments, and JFIF/Adobe marker flags for grayscale, RGB, YCbCr, CMYK, YCCK, or unknown data.
- With progressive support, `jpeg_simple_progression` allocates/reuses permanent scan-script storage and fills a recommended progressive scan sequence.

Dependencies and interactions:
- Public setup layer used by `cjpeg`, normal applications, and transcoding parameter copying.
- Feeds tables and component metadata consumed by `jcmaster.c`, `jcmarker.c`, `jcdctmgr.c`, and entropy encoders.

Risk notes:
- All mutating helpers require `CSTATE_START`.
- Standard Huffman tables are explicitly only valid for 8-bit precision; higher precision forces optimization.
- `jpeg_set_colorspace` overwrites component assignments, so custom sampling/table choices must be applied after it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcphuff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcphuff.c

Progressive JPEG Huffman entropy encoder.

Key points:
- Compiled only under `C_PROGRESSIVE_SUPPORTED`.
- Maintains progressive-specific state: gather/output mode, bit buffer, DC predictors, AC table number, EOB run, buffered correction bits, restart state, derived tables, and optimization counts.
- `start_pass_phuff` selects one of four MCU encoders: DC first, AC first, DC refinement, or AC refinement; allocates correction-bit buffer for AC refinement; prepares derived tables or statistics counts.
- Output functions emit bytes with byte stuffing but do not support suspension.
- `emit_symbol`, `emit_eobrun`, and `emit_buffered_bits` abstract output vs statistics gathering.
- DC first scans encode point-transformed DC differences; AC first scans encode spectral bands with EOB run aggregation.
- DC refinement emits one refinement bit per block; AC refinement manages newly nonzero coefficients, correction bits, ZRLs, EOB runs, and buffer overflow limits.
- Finish routines flush pending EOB/bit data or generate optimized tables from gathered counts.
- `jinit_phuff_encoder` allocates encoder state and marks tables/buffers unallocated.

Dependencies and interactions:
- Shares `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table` from `jchuff.c` via `jchuff.h`.
- Scan validity is assumed to have been checked by `jcmaster.c`.
- Used for both normal progressive compression and progressive transcoding.

Risk notes:
- Output suspension is explicitly unsupported for progressive Huffman output.
- AC refinement relies on a fixed `MAX_CORR_BITS` buffer and flush thresholds to avoid overflow.
- Right-shift handling includes portability logic for signed shifts, but coefficient coding still assumes IJG’s supported numeric ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcphuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcprepct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcprepct.c

Compression preprocessing controller for color conversion, downsampling input buffering, and vertical edge padding.

Key points:
- Buffers color-converted rows until enough rows are available for the downsampler’s row-group contract.
- Simple mode buffers one row group and pads the bottom of the image by replicating the last row.
- Context-row mode, enabled only when input smoothing support needs it, uses wrapped row-pointer arrays around three real row groups so downsamplers can inspect rows above and below.
- `start_pass_prep` resets rows remaining and buffer position.
- `pre_process_data` converts input rows, pads bottom rows, invokes the downsampler, and pads final output rows to full iMCU height.
- `pre_process_context` fills and rotates context buffers, creates top/bottom dummy context rows, and downscales row groups when enough input is available.
- `jinit_c_prep_controller` rejects full-buffer requests, allocates the prep controller, chooses simple vs context processing, and allocates per-component color buffers wide enough for horizontal edge expansion.

Dependencies and interactions:
- Calls `cconvert->color_convert` from `jccolor.c` and `downsample->downsample` from `jcsample.c`.
- Feeds the main controller’s component strip buffers.

Risk notes:
- Context mode is available only if `INPUT_SMOOTHING_SUPPORTED` compiled it in.
- Assumes the caller supplies one-iMCU-height output buffers.
- Buffer dimensions are tied to component sampling factors computed by master setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcprepct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcsample.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcsample.c

Compression downsampler module.

Key points:
- Defines row groups as `max_v_samp_factor` input rows producing `v_samp_factor` output rows per component.
- `expand_right_edge` pads rows horizontally by duplicating rightmost samples to DCT-block width.
- `sep_downsample` applies one selected per-component downsample method to each component independently.
- Implements arbitrary integral-ratio box-filter downsampling, full-size copy/pad, common h2v1 and h2v2 downsampling with alternating rounding bias, and optional smoothed h2v2/full-size downsampling.
- Smoothing uses context rows and fixed-point weighted sums intended for dither cleanup.
- `jinit_downsampler` allocates the downsampler, rejects unsupported CCIR601 sampling, selects a per-component method from sampling-factor ratios, requests context rows when smoothing requires them, and warns when smoothing cannot apply to all components.

Dependencies and interactions:
- Called by `jcprepct.c`.
- Uses sampling factors and component dimensions established by `jcmaster.c`.

Risk notes:
- Fractional sampling ratios and CCIR601 sampling are not implemented.
- Arbitrary integral-ratio path is generic but not optimized for uncommon factors.
- Smoothing is limited to full-size and h2v2 cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jctrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jctrans.c

Compression-side support for coefficient transcoding.

Key points:
- `jpeg_write_coefficients` starts a compression object for writing preexisting virtual DCT coefficient arrays, unsuppresses tables, initializes destination/error managers, selects transcoding modules, and enters `CSTATE_WRCOEFS`.
- `jpeg_copy_critical_parameters` copies image dimensions, color space, precision, CCIR601 flag, quantization tables, component IDs/sampling/quant table assignments, and JFIF density/version data from a decompressor to a compressor for lossless transcoding.
- It verifies that component-private quantization tables match their referenced quant table slots, rejecting files that reuse a slot incompatibly.
- `transencode_master_selection` initializes master control in transcode-only mode, selects Huffman/progressive Huffman entropy encoder, installs a special coefficient controller, initializes marker writer, realizes arrays, and writes SOI/APP markers.
- Special coefficient controller reads caller-supplied virtual block arrays and creates dummy padding blocks on the fly for right/bottom edges.
- `compress_output` walks active scan MCUs from virtual arrays and feeds entropy encoding.

Dependencies and interactions:
- Paired with decompression-side coefficient readers in `jdtrans.c` outside this group.
- Uses `jcmaster.c`, entropy encoders, marker writer, and memory manager virtual block arrays.

Risk notes:
- Arithmetic transcoding is unimplemented.
- Cannot represent source JPEGs whose components have saved quant tables that differ from their referenced quant table slots.
- Caller must supply coefficient arrays matching component block dimensions and virtual-array unit-height requirements.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jctrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapimin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapimin.c

Minimum public API for JPEG decompression and transcoding header consumption.

Key points:
- `jpeg_CreateDecompress` validates version/struct size, preserves error manager/client data, zeroes the decompressor struct, initializes memory manager, clears table pointers, initializes marker reader and input controller, and enters `DSTATE_START`.
- Destroy/abort wrappers delegate to common routines.
- `default_decompress_parms` guesses JPEG and output colorspaces from component count, JFIF/Adobe markers, transform code, and component IDs; then sets scale, gamma, buffering, raw output, DCT, upsampling, block smoothing, and color quantization defaults.
- `jpeg_read_header` drives input consumption to SOS or EOI, maps return codes to public header results, supports tables-only streams, and handles suspension.
- `jpeg_consume_input` is the decompressor input state machine, initializing source/input controller at start, consuming headers, installing defaults on SOS, and delegating later states to the input controller.
- `jpeg_input_complete` and `jpeg_has_multiple_scans` expose input-controller state.
- `jpeg_finish_decompress` verifies final output completion, finishes the output pass, consumes input to EOI, terminates the source, and aborts back to reusable start state.

Dependencies and interactions:
- Depends on decompressor marker reader/input controller/master modules outside this group.
- Shared cleanup is in `jcomapi.c`; standard scanline APIs are in `jdapistd.c`.

Risk notes:
- Colorspace detection is heuristic because JPEG streams often lack definitive colorspace metadata.
- `jpeg_finish_decompress` requires all output scanlines/raw rows to be consumed unless buffered-image mode is active.
- Suspension-aware callers must inspect `FALSE`/`JPEG_SUSPENDED` returns and retry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapimin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapistd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapistd.c

Standard decompression API for full pixel output.

Key points:
- `jpeg_start_decompress` requires header-ready state, initializes decompressor master modules, handles buffered-image mode, preloads all scans for multscan files when needed, and performs dummy output passes before entering scanning/raw-output state.
- `output_pass_setup` prepares an output pass, runs any two-pass color-quantization dummy passes, and transitions to `DSTATE_SCANNING` or `DSTATE_RAW_OK`.
- `jpeg_read_scanlines` validates state, warns on excess calls, updates progress, invokes the main decompressor controller, and advances `output_scanline`.
- `jpeg_read_raw_data` validates raw-output state, requires one full iMCU row of caller buffer space, invokes coefficient decompression directly, and advances `output_scanline`.
- Buffered-image APIs `jpeg_start_output` and `jpeg_finish_output` select output scan numbers, run output pass setup/finish, and consume input until enough scans are available.

Dependencies and interactions:
- Pulling this file into an application links the full decompressor.
- Uses decompressor master, input controller, coefficient controller, and main controller modules outside this group.

Risk notes:
- Multiscan input preload and buffered-image APIs require `D_MULTISCAN_FILES_SUPPORTED`.
- Dummy passes require `QUANT_2PASS_SUPPORTED`.
- Raw-data output buffer height must match the computed iMCU row height.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdapistd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatadst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatadst.c

Standard stdio destination manager for JPEG compression output.

Key points:
- Defines a permanent destination manager wrapping a caller-owned `FILE *` and an image-pool 4096-byte output buffer.
- `init_destination` allocates the buffer and initializes `next_output_byte`/`free_in_buffer`.
- `empty_output_buffer` writes the full buffer with `JFWRITE`, resets pointers, and always returns `TRUE`.
- `term_destination` writes remaining buffered bytes, flushes the stream, and checks `ferror`.
- `jpeg_stdio_dest` allocates the destination manager on first use, installs method pointers, and records the output stream.

Dependencies and interactions:
- Used by applications before `jpeg_start_compress` or `jpeg_write_tables`.
- Not a core internal module; includes `jinclude.h`, `jpeglib.h`, and `jerror.h` without defining `JPEG_INTERNALS`.

Risk notes:
- This destination manager does not support output suspension.
- The application remains responsible for opening and closing the `FILE *`.
- Reusing the same compression object with a different destination manager type can be unsafe because the permanent private object size may differ.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatadst.c -->