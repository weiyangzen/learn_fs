# Group Research: group_1523_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_jpeg_jccolor_c_sources__4de118820bf0

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely. This group is vendored Independent JPEG Group code inside Plan 9's Ghostscript tree, so its relevance is as image codec support for a Plan 9 user-space program rather than kernel/VFS code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccolor.c

Input color conversion module for JPEG compression.

Key behavior:
- Allocates and fills fixed-point RGB-to-YCbCr lookup tables for fast per-sample conversion.
- Converts interleaved application RGB rows into planar JPEG component buffers for YCbCr output.
- Reuses the Y portion of the RGB-to-YCbCr tables for RGB-to-grayscale conversion.
- Converts Adobe-style CMYK to YCCK by inverting C/M/Y into R/G/B, converting to YCbCr, and passing K through.
- Provides grayscale pass-through and generic null conversion for already matching color spaces.
- `jinit_color_converter` validates `input_components` against `in_color_space`, validates `num_components` against `jpeg_color_space`, and installs the appropriate `start_pass` and `color_convert` callbacks.

Dependencies:
- Uses IJG compressor state (`j_compress_ptr`), memory manager image pool allocation, `jpeg_color_converter`, `J_COLOR_SPACE`, `RGB_*` macros, and error macros from `jpeglib.h`.

Notable risks:
- Only a limited set of conversions is implemented; unsupported color-space pairs fail with `JERR_CONVERSION_NOTIMPL`.
- RGB pass-through is only allowed when `RGB_PIXELSIZE == 3`.
- The conversion tables are per-image allocations and are initialized only for conversions that set `rgb_ycc_start`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcdctmgr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcdctmgr.c

Forward-DCT manager for JPEG compression.

Key behavior:
- Selects the configured FDCT implementation: slow integer, fast integer, or floating point when compiled in.
- Verifies each component's referenced quantization table exists before a pass.
- Builds per-quant-table divisor arrays adjusted for DCT scaling, including AA&N scale factors for fast integer/float DCTs.
- Converts unsigned samples to centered DCT input, calls the selected FDCT routine, then quantizes coefficients into JPEG coefficient blocks.
- Uses a fast zero-result path for division unless `FAST_DIVIDE` is defined.

Dependencies:
- Depends on `jdct.h` FDCT implementations (`jpeg_fdct_islow`, `jpeg_fdct_ifast`, `jpeg_fdct_float`) and IJG quantization/component state.
- Uses image-pool allocations for divisor tables.

Notable risks:
- The selected `dct_method` must match compile-time feature macros or initialization errors with `JERR_NOT_COMPILED`.
- Quantization table presence is enforced at pass start, not when parameters are initially set.
- The integer path has careful sign handling because C division rounding for negatives is not portable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcdctmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.c

Sequential Huffman entropy encoder for JPEG compression.

Key behavior:
- Maintains MCU-local savable state for bit buffering and DC predictions so output suspension can back up to an MCU boundary.
- Expands JPEG Huffman table definitions into fast symbol-to-code/length tables via `jpeg_make_c_derived_tbl`.
- Emits bits with byte stuffing after `0xFF` bytes and supports restart markers.
- Encodes DC coefficient differences and AC run-length/value symbols in JPEG natural-order traversal.
- Provides optional entropy-optimization support by gathering symbol frequencies and building optimal Huffman tables with `jpeg_gen_optimal_table`.
- `jinit_huff_encoder` installs the entropy encoder and initializes derived/statistics table pointers.

Dependencies:
- Shares declarations with `jcphuff.c` through `jchuff.h`.
- Uses destination-manager callbacks, JPEG coefficient ordering, Huffman table arrays, restart state, and memory-manager allocation.

Notable risks:
- Actual output suspension is supported, but marker writing elsewhere is not suspendable.
- Coefficient range checks depend on `MAX_COEF_BITS` from sample precision.
- The optimal-table generator mutates frequency arrays, so callers avoid running it more than once per table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.h

Private Huffman encoder declarations shared by sequential and progressive compressor modules.

Key contents:
- Defines `MAX_COEF_BITS` as 10 for 8-bit samples and 14 otherwise.
- Defines `c_derived_tbl`, the encoder-side expanded Huffman table containing code and code-length entries for every possible symbol.
- Provides short external-name aliases when `NEED_SHORT_EXTERNAL_NAMES` is enabled.
- Declares `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table`.

Dependencies:
- Requires IJG compressor types, Boolean type, and Huffman table definitions from the surrounding JPEG headers.

Notable risks:
- This is not a public application header; comments explicitly limit it to `jchuff.c` and `jcphuff.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcinit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcinit.c

Compression pipeline initializer.

Key behavior:
- Initializes compression master control, which validates parameters and derives image/scan geometry.
- For normal input, initializes color conversion, downsampling, and preprocessing; raw downsampled input bypasses those modules.
- Initializes FDCT, entropy encoder, coefficient controller, main controller, and marker writer.
- Chooses progressive Huffman encoder when progressive mode is active and compiled in; arithmetic coding is rejected as not implemented.
- Requests realization of virtual arrays after all modules have declared their needs.
- Writes SOI and optional early file header markers immediately, while frame/scan headers are deferred.

Dependencies:
- Coordinates the compression-side IJG module init functions and relies on the memory manager's virtual-array realization hook.

Notable risks:
- Arithmetic coding is explicitly unavailable in this build path.
- Progressive compression requires `C_PROGRESSIVE_SUPPORTED`; otherwise initialization fails.
- Linking this file pulls in the full compression library, which is why transcoding uses a separate path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcinit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmainct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmainct.c

Compression main buffer controller between preprocessing and coefficient compression.

Key behavior:
- Maintains per-component downsampled strip buffers for one iMCU row.
- In pass-through mode, repeatedly asks the preprocessor to fill row groups, then hands complete iMCU rows to the coefficient controller.
- Tracks suspension and adjusts the caller's input-row counter so a suspended final input row is not incorrectly treated as consumed.
- Contains dormant full-image buffering code under `FULL_MAIN_BUFFER_SUPPORTED`, but that macro is undefined in this file.
- `jinit_c_main_controller` allocates strip buffers unless raw-data mode bypasses the module.

Dependencies:
- Calls `cinfo->prep->pre_process_data` and `cinfo->coef->compress_data`.
- Uses component dimensions computed by `jcmaster.c`.

Notable risks:
- Full-buffer mode is compiled out, so any request for a full main buffer errors.
- The suspension row-counter adjustment is intentionally subtle and coupled to caller expectations in the public compression API.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmainct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmarker.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmarker.c

JPEG marker writer for compression output.

Key behavior:
- Emits low-level marker bytes and big-endian 16-bit marker fields through the destination manager.
- Writes DQT, DHT, optional DAC, DRI, SOF, SOS, JFIF APP0, Adobe APP14, SOI, EOI, and abbreviated table-only streams.
- Suppresses duplicate quantization and Huffman table emission using each table's `sent_table` flag.
- Chooses SOF0, SOF1, SOF2, or SOF9 based on baseline/progressive/arithmetic/precision state.
- Emits scan-specific Huffman tables, respecting progressive scans where only DC or AC tables are used.
- Exposes application marker insertion through `write_marker_header` and `write_marker_byte`.

Dependencies:
- Uses `jpeg_marker_writer`, destination manager callbacks, component tables, scan parameters, and IJG marker/table structures.

Notable risks:
- Marker writing does not support suspension; callers must ensure enough destination buffer space around header/trailer marker emission.
- Images wider or taller than 65535 are rejected at SOF emission.
- Arithmetic marker support is conditionally compiled, but compressor initialization elsewhere rejects arithmetic coding in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmarker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmaster.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmaster.c

Master control logic for JPEG compression.

Key behavior:
- Validates image dimensions, component counts, sample precision, sampling factors, and scanline width overflow.
- Computes per-component block/sample dimensions and total iMCU rows.
- Validates optional scan scripts, including sequential/progressive consistency, component ordering, DC-before-AC requirements, and successive approximation ordering.
- Selects current scan parameters and computes MCU layout for interleaved and noninterleaved scans.
- Converts restart rows into restart MCU intervals with 16-bit limiting.
- Schedules pass types: main pass, optional Huffman optimization pass, and output pass.
- Coordinates per-pass startup across color conversion, downsampling, preprocessing, FDCT, entropy, coefficient, main, and marker modules.
- Initializes different first-pass behavior for full compression versus coefficient transcoding.

Dependencies:
- Relies on component tables populated by `jcparam.c`, marker writing from `jcmarker.c`, entropy encoders, coefficient controller, and preprocessing/FDCT modules.

Notable risks:
- Progressive mode forces Huffman optimization by default because standard tables are assumed inadequate.
- Compile-time feature macros gate multiscan/progressive/entropy optimization paths.
- Scan-script validation is central; invalid scripts fail before data output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmaster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcomapi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcomapi.c

Common public API helpers shared by compression and decompression.

Key behavior:
- `jpeg_abort` frees all nonpermanent memory pools, resets compressor/decompressor state for reuse, and clears decompressor marker lists.
- `jpeg_destroy` delegates full cleanup to the memory manager and marks the object destroyed.
- Provides permanent-pool allocation helpers for quantization and Huffman table structs, clearing `sent_table` so new tables will be emitted.

Dependencies:
- Uses the common JPEG memory manager interface and state constants for compressor/decompressor objects.

Notable risks:
- Application-owned source/destination streams and top-level structs are not closed or freed here.
- `jpeg_abort` assumes temporary virtual arrays never live in the permanent pool, matching IJG memory-manager design.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcomapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jconfig.cfg -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jconfig.cfg

Template configuration file for IJG `jconfig.h` generation.

Key behavior:
- Undefines portability and compiler feature macros that a configure step may set, such as prototypes, unsigned char/short support, standard headers, BSD strings, far pointers, and short external names.
- Under `JPEG_INTERNALS`, provides internal configuration placeholders for unsigned right shift behavior, `INLINE`, default memory limits, and `mktemp` availability.
- Under `JPEG_CJPEG_DJPEG`, enables BMP, GIF, PPM, and Targa support while disabling Utah RLE, two-file command line mode, signal catching, binary-mode avoidance, and progress reports.

Dependencies:
- Intended to be edited or transformed by IJG configuration tooling and included indirectly as generated JPEG build configuration.

Notable risks:
- This is not runtime code; actual behavior depends on the generated/selected `jconfig.h` used by the build.
- The file reflects conservative defaults and may be superseded by Ghostscript/Plan 9 build glue elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jconfig.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcparam.c

Default parameter and table setup for JPEG compression.

Key behavior:
- Builds scaled luminance/chrominance quantization tables from JPEG spec defaults.
- Converts user quality 0..100 into IJG's nonlinear quantization scaling curve.
- Installs standard 8-bit Huffman tables for luminance and chrominance DC/AC coding.
- `jpeg_set_defaults` allocates component info, initializes precision, quality, Huffman/arithmetic defaults, restart defaults, density/JFIF defaults, smoothing, DCT choice, and color-space-dependent component layout.
- Chooses default JPEG colorspace from input colorspace, commonly RGB to YCbCr.
- Sets component IDs, sampling factors, quant tables, and Huffman table selectors for grayscale, RGB, YCbCr, CMYK, YCCK, and unknown color spaces.
- When progressive support is compiled in, `jpeg_simple_progression` builds recommended scan scripts, with a custom 10-scan YCbCr script.

Dependencies:
- Uses permanent memory pool allocation through `jpeg_alloc_quant_table` and `jpeg_alloc_huff_table`.
- Feeds component/table state consumed by master control, FDCT, entropy, and marker writer modules.

Notable risks:
- Most setters are only valid in `CSTATE_START`.
- Standard Huffman tables are marked valid only for 8-bit data; higher precision forces optimized coding.
- Progressive script allocation is retained in the permanent pool and reused when possible.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcphuff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcphuff.c

Progressive JPEG Huffman entropy encoder.

Key behavior:
- Compiled only under `C_PROGRESSIVE_SUPPORTED`.
- Selects separate MCU encoders for DC first scans, AC first scans, DC refinement scans, and AC refinement scans.
- Supports statistics-gathering mode for optimized Huffman table generation.
- Emits progressive AC EOBRUN symbols and buffers AC refinement correction bits.
- Handles restart markers by flushing pending EOB runs, resetting DC predictions or AC state, and emitting RST markers in output mode.
- Uses `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table` shared with the sequential Huffman encoder.
- `jinit_phuff_encoder` installs progressive entropy callbacks and initializes table/correction-bit buffers.

Dependencies:
- Depends on validated progressive scan parameters from `jcmaster.c`.
- Uses destination manager fields directly but does not support output suspension.

Notable risks:
- Multiple-scan progressive output is incompatible with output suspension in this implementation.
- AC refinement correction buffer has a fixed `MAX_CORR_BITS` size and forces EOB emission to avoid overflow.
- DC refinement scans intentionally need no Huffman table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcphuff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcprepct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcprepct.c

Compression preprocessing controller for color conversion, buffering, downsampling, and edge padding.

Key behavior:
- Buffers color-converted rows until enough rows exist for one downsampling row group.
- Pads the bottom of the image by replicating the final converted row.
- Pads the final output iMCU row vertically to the caller's expected full iMCU height.
- Supports optional context-row mode when input smoothing is compiled in and requested by the downsampler.
- Context mode allocates wrapped row-pointer arrays around three physical row groups so the downsampler can address rows above and below the current group.
- `jinit_c_prep_controller` selects simple or context preprocessing and allocates per-component conversion buffers sized for horizontal edge expansion.

Dependencies:
- Calls color converter and downsampler method pointers.
- Uses component geometry from master setup and row-copy helpers from IJG utilities.

Notable risks:
- Full-buffer preprocessing is not supported and errors if requested.
- Context-row support depends on `INPUT_SMOOTHING_SUPPORTED`; otherwise a downsampler request for context rows fails.
- The code intentionally allows row pointers before the nominal buffer start in context mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcprepct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcsample.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcsample.c

Compression downsampling module.

Key behavior:
- Defines row-group semantics: `max_v_samp_factor` input rows produce each component's `v_samp_factor` output sample rows.
- Provides per-component downsampling methods: full-size copy, arbitrary integral box filtering, h2v1 averaging, h2v2 averaging, and optional smoothing variants.
- Performs horizontal edge expansion by duplicating rightmost samples.
- Uses alternating rounding bias in h2v1/h2v2 cases to reduce systematic rounding bias.
- Optional smoothing uses neighboring context rows and integer-scaled weights based on `smoothing_factor`.
- `jinit_downsampler` validates sampling ratios, rejects unsupported fractional sampling and CCIR601 sampling, assigns component-specific method pointers, and advertises whether context rows are needed.

Dependencies:
- Uses component sampling factors and image geometry from compressor setup.
- Cooperates with `jcprepct.c`, which supplies context rows and vertical padding.

Notable risks:
- CCIR601 sampling is explicitly not implemented.
- Smoothing is only available for full-size and h2v2 paths; unsupported smoothing combinations produce a trace warning and fall back without smoothing.
- Arbitrary integral downsampling exists but comments note it is not optimized for uncommon ratios.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jctrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jctrans.c

Compression support for coefficient-level JPEG transcoding.

Key behavior:
- `jpeg_write_coefficients` starts a compression object that writes preexisting virtual DCT coefficient arrays instead of accepting sample rows.
- Marks all tables for output, initializes the destination, selects transcoding modules, writes SOI, and enters `CSTATE_WRCOEFS` pending `jpeg_finish_compress`.
- `jpeg_copy_critical_parameters` copies dimensions, colorspace, precision, sampling, quantization tables, component IDs/factors/table selectors, and JFIF density/version from a decompressor to a compressor.
- Verifies saved per-component quantization tables match the source table slots, rejecting cases this encoder cannot duplicate.
- Provides a special coefficient controller that reads supplied coefficient virtual arrays and generates dummy padding blocks at image edges on the fly.

Dependencies:
- Uses decompressor-side parsed metadata, compressor parameter defaults, marker writer, Huffman/progressive entropy encoders, and virtual block arrays.

Notable risks:
- Arithmetic transcoding output is rejected as not implemented.
- Huffman table assignments are not copied from the source; defaults or later caller changes are used.
- Dummy block generation assumes prior block DC values are available when padding at right/bottom edges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jctrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapimin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapimin.c

Minimum decompression API needed for full decompression and transcoding.

Key behavior:
- `jpeg_CreateDecompress` validates ABI version/struct size, preserves application error/client fields, zeros the decompressor struct, initializes memory management, marker reader, input controller, and start state.
- Provides destroy/abort wrappers over common API routines.
- Guesses JPEG input colorspace and default output colorspace from component count, JFIF marker, Adobe marker, Adobe transform, and component IDs.
- Initializes decompression defaults: scaling, gamma, buffered/raw modes, DCT method, fancy upsampling, block smoothing, and color quantization options.
- `jpeg_read_header` drives input consumption until SOS or EOI and returns header status codes.
- `jpeg_consume_input` is the central decompressor input state machine.
- Provides helpers for input completion, multiple-scan detection, and final decompression cleanup.

Dependencies:
- Uses decompressor memory manager, marker reader, input controller, source manager, master controller, and common abort/destroy routines.

Notable risks:
- Color-space inference is heuristic because JPEG lacks a complete standard colorspace declaration.
- Empty input is fatal in the stdio source manager; truncated nonempty input may be converted to a fake EOI.
- `jpeg_finish_decompress` errors if the caller has not consumed all output scanlines in non-buffered mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapimin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapistd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapistd.c

Standard full-decompression public API.

Key behavior:
- `jpeg_start_decompress` initializes master decompression, optionally preloads multiple scans into the coefficient buffer, and prepares output passes.
- `output_pass_setup` handles dummy output passes needed for two-pass color quantization, then enters either scanline or raw-output state.
- `jpeg_read_scanlines` runs the main decompression pipeline into caller scanline buffers and advances `output_scanline`.
- `jpeg_read_raw_data` returns one raw iMCU row through the coefficient controller and requires caller capacity for a full iMCU row.
- Buffered-image mode APIs `jpeg_start_output` and `jpeg_finish_output` allow selecting and finishing output passes by scan number when multiscan support is compiled in.

Dependencies:
- Calls master decompression, input controller, main controller, coefficient controller, and optional progress monitor hooks.

Notable risks:
- Linking this file intentionally pulls in the full decompressor, unlike `jdapimin.c`.
- Multipass/multiscan and two-pass quantization paths are compile-time gated.
- Excess read calls after output completion warn and return zero rather than silently proceeding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapistd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatadst.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatadst.c

Stdio destination manager for JPEG compression.

Key behavior:
- Wraps an application-provided `FILE *` with a `jpeg_destination_mgr`.
- Allocates a 4096-byte output buffer in the image pool at compression start.
- Writes full buffers with `JFWRITE`, resets destination pointers, and always reports successful buffer emptying unless a file error occurs.
- Flushes the partial final buffer in `term_destination`, calls `fflush`, and checks `ferror`.
- `jpeg_stdio_dest` allocates the destination manager in the permanent pool so one JPEG object can write multiple images to the same stream.

Dependencies:
- Uses C stdio through IJG `JFWRITE` and JPEG memory/error manager interfaces.

Notable risks:
- This manager does not implement suspension; file-write failures raise fatal JPEG errors.
- The caller remains responsible for opening and closing the stream.
- Reusing a JPEG object with a different destination manager can be unsafe because the permanent private object size may differ.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatadst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatasrc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatasrc.c

Stdio source manager for JPEG decompression.

Key behavior:
- Wraps an application-provided `FILE *` with a `jpeg_source_mgr`.
- Allocates a permanent 4096-byte input buffer so image sequences can be read from the same stream without losing buffered bytes.
- `fill_input_buffer` reads with `JFREAD`, treats an empty file as fatal, and injects a fake EOI marker with warning on later EOF/truncation.
- `skip_input_data` skips buffered bytes and refills as needed, using a simple stream-friendly implementation rather than `fseek`.
- Uses the library's default restart resynchronization method.
- `term_source` is a no-op; stream cleanup remains the caller's responsibility.

Dependencies:
- Uses C stdio through IJG `JFREAD`, decompressor source manager callbacks, error handling, and default restart resync.

Notable risks:
- This source manager is non-suspending; `skip_input_data` assumes `fill_input_buffer` never returns `FALSE`.
- Truncated nonempty files may produce partial output after fake EOI insertion.
- Reusing one JPEG object with a different source manager is unsafe for the same private-object-size reason as the destination manager.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatasrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcoefct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcoefct.c

Decompression coefficient buffer controller.

Key behavior:
- Sits between entropy decoding and inverse DCT, and also forms the buffered-image/transcoding coefficient-array interface.
- In single-pass mode, allocates one MCU workspace, decodes each MCU, immediately applies IDCT for needed components, and emits one iMCU row.
- In multiscan/buffered mode, consumes entropy-decoded coefficients into full-image virtual block arrays and later decompresses output rows from those arrays.
- Maintains input-side MCU counters and output-side iMCU row progress separately.
- Supports suspension by saving MCU column and vertical offsets before returning `JPEG_SUSPENDED`.
- Optional progressive block smoothing estimates early AC coefficients from neighboring DC values when coefficients are not yet fully known.
- `jinit_d_coef_controller` allocates either full-image virtual coefficient arrays or a single-MCU buffer and installs consume/decompress callbacks.

Dependencies:
- Calls entropy decoder `decode_mcu`, inverse DCT methods, input controller pass finishing, memory manager virtual block arrays, and IJG block-copy/zero helpers.

Notable risks:
- Full-buffer mode requires `D_MULTISCAN_FILES_SUPPORTED`; otherwise a request for full buffering fails.
- Block smoothing depends on progressive support, quantization table availability, nonzero quantizers, and coefficient-bit tracking.
- The single-pass path requires entropy decoding and output IDCT to proceed in lockstep.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcoefct.c -->