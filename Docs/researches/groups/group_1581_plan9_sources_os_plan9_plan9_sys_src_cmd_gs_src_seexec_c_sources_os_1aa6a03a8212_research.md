# Group Research: group_1581_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_seexec_c_sources_os_1aa6a03a8212

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/seexec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/seexec.c

Ghostscript eexec encryption/decryption stream filters for Type 1 font data.

Key behavior:
- `s_exE_process` implements `eexecEncode` by applying `gs_type1_encrypt` over the caller-provided bytes with the stream crypt state.
- `s_exD_set_defaults` initializes decode mode as unknown, sets default `lenIV = 4`, and clears optional PFB state.
- `s_exD_process` skips Adobe-compatible leading whitespace, detects binary vs ASCII-hex eexec input from the first bytes, optionally honors enclosing PFB record boundaries, decodes hex with `s_hex_process`, decrypts with `gs_type1_decrypt`, and discards the initial `lenIV` random bytes.
- The decode template deliberately limits output buffer size to keep eexec read-ahead under the PostScript 512-source-byte requirement.

Notable dependencies:
- Type 1 crypt helpers: `gscrypt1.h`.
- Hex/scanner helpers: `sfilter.h`, `scanchar.h`, `s_hex_process`.
- Optional coordination with `PFBDecode` state through `stream_PFBD_state`.

Research notes:
- The binary/hex auto-detection includes practical compatibility behavior for malformed PostScript, including ignoring leading whitespace and sometimes `%`.
- PFB handling tries not to read beyond encrypted record boundaries by pausing at record ends or converting prematurely decoded hex sections back to binary mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/seexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter.h

Header defining stream states for simple Ghostscript filters: eexec encode/decode, PFB decode, and SubFileDecode.

Key contents:
- `stream_exE_state` stores the Type 1 encryption state for eexec encoding.
- `stream_exD_state` stores eexec decode parameters and dynamic state: crypt state, binary/hex detection, `lenIV`, optional underlying PFB state pointer, odd hex digit, remaining PFB record/hex counts, and skip count.
- `stream_PFBD_state` stores PFB record decode mode, record type, and record bytes left.
- `stream_SFD_state` stores SubFileDecode limits, EOD pattern, skip count, match state, and delayed-copy state.

Notable dependencies:
- Uses Ghostscript stream and GC declaration macros.
- Requires `gstypes.h`; comments note historical compiler issues around `strimpl.h`.

Research notes:
- This is a state-contract header; implementations are split across `seexec.c` and `sfilter1.c`.
- The state layouts expose client-set parameters separately from initialization-derived and dynamic values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter1.c

Level 1 simple Ghostscript filters: `PFBDecode` and `SubFileDecode`.

Key behavior:
- `PFBDecode` parses binary Type 1 PFB records beginning with `0x80`, accepts text, binary, and EOF record types, converts text record CR to LF, and can convert binary records to hex when `binary_to_hex` is set.
- PFB record lengths are read as little-endian 32-bit values; invalid record markers return `ERRC`, EOF record returns `EOFC`.
- `SubFileDecode` can either copy a fixed number of bytes without an EOD pattern or scan for an EOD byte pattern.
- SubFileDecode supports `skip_count`, repeated EOD counting, partial EOD matches across buffer boundaries, and delayed copying of bytes that looked like a partial EOD but did not complete.

Notable dependencies:
- `sfilter.h` for state definitions.
- `strimpl.h` stream cursor/template machinery.

Research notes:
- SubFileDecode’s pattern fallback can be quadratic in EOD length, explicitly accepted because EOD strings are expected to be small.
- PFBDecode returns partial progress cleanly when headers or records span buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter2.c

Simple Level 2 stream filters: ASCII85 encode and byte-translation encode/decode.

Key behavior:
- `ASCII85Encode` initializes inline state, emits 4-byte groups as 5 ASCII85 bytes, uses `z` for all-zero words, emits `~>` on final data, and wraps output at 79 columns.
- It contains compatibility guards to avoid producing line starts that confuse document managers, specifically `%!` or `%%`.
- Final partial words are padded internally and emitted with the required shortened ASCII85 output.
- `ByteTranslateEncode` and `ByteTranslateDecode` share `s_BT_process`, mapping every input byte through a 256-entry translation table.

Notable dependencies:
- ASCII85 state from `sa85x.h`.
- Byte-translate state from `sbtx.h`.
- Debug tracing through `gdebug.h`.

Research notes:
- The ASCII85 loop is careful about buffer limits and line wrapping; status `1` indicates output buffer exhaustion.
- ByteTranslate is deliberately symmetric: encode and decode differ only by the caller-supplied table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxboth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxboth.c

Build-composition source file that includes both stdio-backed and file-descriptor-backed stream implementations.

Key behavior:
- Includes `sfxstdio.c` first, providing normal public `sread_file`, `swrite_file`, `sappend_file`, and `sread_subfile`.
- Defines `KEEP_FILENO_API`, then includes `sfxfd.c`, causing its public entry points to be exposed as `sread_fileno`, `swrite_fileno`, and `sappend_fileno` instead of clashing with stdio names.

Notable dependencies:
- Directly depends on source inclusion rather than separate object linkage.

Research notes:
- This is a legacy compile-time composition technique, not a standalone implementation.
- The resulting build offers both backends in the same executable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxboth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxfd.c

Alternative file stream backend using direct OS file-descriptor calls while retaining a `FILE *` interface.

Key behavior:
- `sread_fileno`, `swrite_fileno`, and `sappend_fileno` initialize Ghostscript streams backed by `read`, `write`, `lseek`, and `fsync`.
- Read support detects seekability by probing `lseek`, supports subfile limits, implements `available`, seeks within the current buffer when possible, and retries interrupted/nonblocking reads for `EINTR`, `EAGAIN`, and `EWOULDBLOCK`.
- Write support flushes with `s_process_write_buf`, calls `fsync` on flush, handles zero-length writes specially, retries transient write errors, and supports append positioning.
- `s_fileno_switch` switches an update-mode stream between reading and writing while preserving current logical position and append mode.

Notable dependencies:
- Platform wrappers: `unistd_.h`, `errno_.h`.
- Ghostscript stream internals: `stream.h`, `strimpl.h`, `gpcheck.h`.

Research notes:
- Comments warn this may not compile unchanged on non-Unix platforms.
- With `KEEP_FILENO_API`, public names are renamed so this can coexist with `sfxstdio.c`.
- The backend aggressively syncs on flush, which is stronger and more expensive than the stdio backend.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxstdio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxstdio.c

Default Ghostscript file stream backend using ANSI stdio.

Key behavior:
- `sread_file`, `swrite_file`, and `sappend_file` initialize streams around `FILE *`.
- Read initialization probes seekability with `ftell`/`fseek` and clears probe-induced error state when appropriate.
- `sread_subfile` confines an existing seekable read stream to a logical byte range.
- Read processing uses `fread`, honors `file_limit`, returns `EOFC` on EOF, and processes Ghostscript interrupts.
- Write processing uses `fwrite`, flush uses `fflush`, and close flushes pending stream data before closing the file.
- `s_file_switch` switches a bidirectional stream between read/write modes while preserving logical position.

Notable dependencies:
- `stream.h`, `strimpl.h`, `gpcheck.h`.
- C stdio wrappers via `stdio_.h`.

Research notes:
- This is the portable baseline compared with the direct-file-descriptor variant.
- The stream mode/procedure setup mirrors `sfxfd.c`, making the two backends interchangeable at the higher stream layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxstdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.c

Support routines for Huffman-coded stream helpers declared in `shc.h`.

Key behavior:
- `hc_put_code_proc` writes a full buffered Huffman code word to output, optionally reversing bits per byte for low-order-first encodings.
- `hc_put_last_bits_proc` flushes final partial bits one byte at a time, applying bit reversal when needed, and stores updated bit-buffer state back into the stream state.

Notable dependencies:
- `shc.h` for state and bit-size definitions.
- `gsbittab.h` through `shc.h` for `byte_reverse_bits`.

Research notes:
- Most Huffman work is macro-based in `shc.h`; this file contains the out-of-line routines used when buffered output crosses word boundaries or needs final flushing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.h

Common Huffman coding definitions, state, tables, and bit-buffer macros.

Key contents:
- Defines `hc_definition`: canonical Huffman code counts by length plus decoded values in lexicographic code order.
- Defines `stream_hc_state_common` with `FirstBitLowOrder`, `bits`, and `bits_left`.
- Defines encode table structures `hce_code` and `hce_table`.
- Provides encoder macros for loading/storing state and emitting code values into an output bit buffer.
- Defines decode table structures `hcd_code` and `hcd_table`.
- Provides decoder macros for loading/storing state, ensuring bits, reading more input bytes, peeking bits, and skipping bits.

Notable dependencies:
- `gsbittab.h` for bit reversal and masks.
- `scommon.h` stream-state common definitions.

Research notes:
- The header supports code lengths up to 16 bits and decoded values up to 15 bits.
- Decoding is designed as a two-level table lookup: fixed initial bits and optional auxiliary subtables.
- The macros depend on Ghostscript’s one-byte-before-cursor stream cursor convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.c

Huffman utility implementation for generating bounded canonical code definitions and encode/decode tables.

Key behavior:
- `hc_compute` builds a Huffman tree from value frequencies, computes code lengths, bounds lengths to `def->num_counts`, sorts values into canonical order, and fills `counts` and `values`.
- `hc_limit_code_lengths` adjusts too-long code lengths while maintaining a full prefix code.
- `hc_bytes_from_definition` compresses a well-behaved Huffman definition into run-length bytes of value-count/code-length pairs.
- `hc_sizes_from_bytes` computes definition array sizes from that compressed representation.
- `hc_definition_from_bytes` expands compressed bytes back into canonical counts and value order.
- `hc_make_encoding` builds canonical code/code-length entries by decoded value.
- `hc_sizeof_decoding` computes storage required for two-level decode tables.
- `hc_make_decoding` fills first-level and auxiliary decode table entries.

Notable dependencies:
- Memory and error APIs: `gsmemory.h`, `gserror.h`, `gserrors.h`.
- Huffman definitions from `shc.h`.

Research notes:
- `hc_definition_from_bytes` appears to contain a loop typo: `for (j = 0; j < n; n++)` increments `n` instead of `j`, which would not terminate normally for positive `n` and would corrupt expansion if used.
- Allocation failure in `hc_compute` correctly returns `gs_error_VMerror`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.h

Public interface for Huffman generation and table-construction utilities.

Key contents:
- Declares `hc_compute` for deriving a bounded canonical code from frequencies.
- Declares byte-string compression/expansion helpers for Huffman definitions.
- Declares encoding table and decoding table creation helpers.

Notable dependencies:
- Requires `shc.h` types such as `hc_definition`, `hce_code`, and `hcd_code`.
- Uses `gs_memory_t` for allocation in `hc_compute`.

Research notes:
- This header is consumed by filters that need dynamic Huffman tables rather than fixed tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.c

Image interpolation encode filter using DDA stepping and component scaling.

Key behavior:
- Defines `stream_IIEncode_state` with image scale parameters, input/output pixel sizes, row sizes, current row buffers, selected conversion case, and DDA state for X/Y mapping.
- `s_IIEncode_init` computes pixel sizes, initializes DDAs, allocates two row buffers, and selects an optimized scale/conversion case based on input/output bit depth, max values, and color count.
- `s_IIEncode_process` reads complete input rows into `cur`, maps output pixels to source X positions with DDA, converts component values between 8-bit and 16-bit representations, and writes output rows until the destination height is complete.
- `s_IIEncode_release` frees allocated row buffers.

Notable dependencies:
- DDA helpers: `gxdda.h`, `gxfixed.h`.
- Fraction conversion: `gxfrac.h`.
- Shared image scale params from `siinterp.h`/`sisparam.h`.

Research notes:
- The source allocates `prev` but the processing path only uses `cur`, so despite the filter name it behaves as a row/nearest mapping plus value conversion rather than full bilinear interpolation in this file.
- Comments mark allocation error returns as “WRONG” because they return `ERRC` instead of a VM error.
- A comment flags output-buffer handling as requiring an entire output pixel, so partial-pixel buffer edges are a known concern.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.h

Header for the image interpolation stream filter.

Key contents:
- Includes shared image scaling parameter definitions from `sisparam.h`.
- Exports `s_IIEncode_template`.

Notable dependencies:
- Requires `strimpl.h` when stream templates are referenced by the including compilation unit.

Research notes:
- This header exposes only the stream template; concrete state is private to `siinterp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.c

Smoothed image scaling stream filter based on a Mitchell filter and Graphics Gems III scaling code.

Key behavior:
- Supports fixed-point accumulation when `USE_FPU <= 0`, otherwise floating-point accumulation.
- Defines `stream_IScale_state` with source/destination row buffers, intermediate horizontally scaled rows, contribution lists, filter weights, and row offsets.
- `Mitchell_filter` supplies the reconstruction filter with support 2.0.
- `calculate_contrib` precomputes source pixel contributors and weights for a scaling dimension, including downscale widening and edge reflection/clamping.
- `zoom_x` applies horizontal filtering into a temporary row ring.
- `zoom_y` applies vertical filtering from temporary rows into destination output.
- `s_IScale_init` computes scale factors, row sizes, allocates working buffers, precomputes X contributions, and prepares the first Y contribution list.
- `s_IScale_process` streams input rows, horizontally scales each row, and emits output rows once enough temporary rows are available.
- `s_IScale_release` frees all working storage.

Notable dependencies:
- Math and config wrappers: `math_.h`, `gconfigv.h`.
- Shared parameters from `siscale.h`/`sisparam.h`.

Research notes:
- The scaler supports both encode/decode templates identically via `s_IScale_template`.
- Allocation failure is marked with the historical “WRONG” comment because it returns `ERRC` rather than VM-specific errors.
- The temporary ring is bounded by `MAX_ISCALE_SUPPORT`, limiting memory and filter support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.h

Header for the smoothed image scaling stream filter.

Key contents:
- Includes shared image scaling parameter definitions from `sisparam.h`.
- Exports `s_IScale_template`.

Notable dependencies:
- Requires stream template context from `strimpl.h` in users.

Research notes:
- Concrete scaler state and implementation are private to `siscale.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sisparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sisparam.h

Shared parameter definitions for Ghostscript image scaling streams.

Key contents:
- Defines maximum digital-filter support as `MAX_ISCALE_SUPPORT = 8`.
- Defines `stream_image_scale_params_t` with color count, input/output component bit depths, max component values, and input/output dimensions.
- Defines `stream_image_scale_state_common` and `stream_image_scale_state`.

Notable dependencies:
- Intended for stream filter implementations using `strimpl.h`.

Research notes:
- Supports 8- or 16-bit input/output components.
- The support cap bounds both runtime and temporary storage for scaling filters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sisparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.c

JBIG2Decode stream filter adapter around the external `jbig2dec` library.

Key behavior:
- `s_jbig2decode_error` maps jbig2dec messages to Ghostscript logging and records fatal decode errors as `gs_error_ioerror`.
- `s_jbig2decode_make_global_ctx` parses a `/JBIG2Globals` byte string into a `Jbig2GlobalCtx`.
- `s_jbig2decode_set_global_ctx` attaches an externally owned global context to a stream state.
- `s_jbig2decode_init` creates an embedded-mode jbig2 decoder context using optional globals.
- `s_jbig2decode_process` feeds compressed input to jbig2dec, completes the page on final input, retrieves a page image, copies bitmap bytes out, and inverts bits to match PostScript black/white polarity.
- `s_jbig2decode_release` frees the page image and decoder context.
- Defaults clear external-library pointers for GC safety.

Notable dependencies:
- External `jbig2.h`.
- Ghostscript stream and error infrastructure.

Research notes:
- Comments explicitly bypass normal Ghostscript memory discipline for the external library and rely on `release` for cleanup.
- Several allocation paths are noted as TODO/not checked for allocation failure.
- The filter assumes a single page image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.h

Header for the JBIG2Decode stream filter.

Key contents:
- Defines `stream_jbig2decode_state` with optional global context, decoder context, current image, image output offset, and error code.
- Declares helpers for creating and attaching a global context.
- Declares GC structure macro and `s_jbig2decode_template`.

Notable dependencies:
- External `jbig2.h`.
- `scommon.h` stream-state definitions.

Research notes:
- The global context pointer is not owned by the stream state; the implementation comments say interpreter code frees it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpeg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpeg.h

Header declaring Ghostscript wrapper entry points for IJG libjpeg operations.

Key contents:
- Common wrappers for error setup/logging, quant/huffman table allocation, and JPEG destroy.
- Encode wrappers for compressor creation, defaults, colorspace, quality, start/write/finish.
- Decode wrappers for decompressor creation, header reading, start/read/finish.

Notable dependencies:
- Requires `sdct.h` and IJG `jpeglib.h` context in users.

Research notes:
- The wrappers convert IJG `longjmp` error exits into Ghostscript-style return codes.
- Allocation wrappers return `NULL` for VM-style allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpeg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegc.c

Common JPEG wrapper implementation for IJG encode/decode integration and memory management.

Key behavior:
- Installs Ghostscript error handlers over IJG’s `jpeg_error_mgr`.
- `gs_jpeg_error_exit` converts IJG fatal errors to `longjmp` through the enclosing stream data.
- `gs_jpeg_emit_message` ignores warnings unless `Picky` is set, in which case warnings become errors.
- `gs_jpeg_log_error` formats IJG error text through the stream’s `report_error` callback.
- Wrapper functions around quant/huffman table allocation and `jpeg_destroy` isolate `setjmp`.
- Overrides IJG memory-manager entry points (`jpeg_get_small`, `jpeg_get_large`, frees, availability, backing store) to allocate through Ghostscript memory and track blocks.

Notable dependencies:
- IJG headers via `jpeglib_.h`, `jerror_.h`.
- DCT stream state from `sdct.h`.
- Optional `jmemsys.h` prototypes controlled by `gconfig_.h`.

Research notes:
- Uses a private linked list of `jpeg_block_t` records to track allocations for cleanup/debugging.
- Backing store is deliberately unsupported and raises IJG `JERR_NO_BACKING_STORE`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegd.c

JPEG decode-side IJG wrapper functions.

Key behavior:
- `gs_jpeg_create_decompress` installs error handling, initializes common JPEG stream data, and calls `jpeg_create_decompress`.
- `gs_jpeg_read_header`, `gs_jpeg_start_decompress`, `gs_jpeg_read_scanlines`, and `gs_jpeg_finish_decompress` wrap their IJG counterparts in `setjmp` protection.
- Handles IJG version difference where `jpeg_start_decompress` did not return a value in version 5.

Notable dependencies:
- Common JPEG wrapper support from `sjpeg.h`/`sjpegc.c`.
- DCT stream state from `sdct.h`.

Research notes:
- This file contains no decompression logic itself; it is an error-translation boundary around libjpeg.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpege.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpege.c

JPEG encode-side IJG wrapper functions.

Key behavior:
- `gs_jpeg_create_compress` installs error handling, initializes common JPEG stream data, and calls `jpeg_create_compress`.
- Wraps IJG compressor operations for defaults, colorspace, linear quality, quality, start, scanline writing, and finish.
- Every entry point establishes `setjmp` protection and returns Ghostscript error codes on IJG failure.

Notable dependencies:
- Common JPEG wrapper support from `sjpeg.h`/`sjpegc.c`.
- DCT stream state from `sdct.h`.

Research notes:
- This file is strictly a side-effect containment layer for IJG calls; actual stream buffering and DCT behavior live elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpege.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.c

JPXDecode/JPEG 2000 stream filter adapter around the external JasPer library.

Key behavior:
- `s_jpxd_init` initializes JasPer, allocates a temporary compressed-data buffer, and chooses non-GC memory for external-library objects.
- Optional debug code dumps decoded image geometry, colorspace, components, precision, signedness, and subsampling.
- Row-copy helpers emit gray, RGB, YCbCr-to-RGB, or generic component data from a JasPer image into Ghostscript output buffers.
- `s_jpxd_buffer_input` spools all compressed input into a growable buffer because the code does not feed JasPer incrementally.
- `s_jpxd_decode_image` wraps the buffer in a JasPer memory stream, decodes the image, optionally converts multicomponent non-RGB images to sRGB, and closes the JasPer stream.
- `s_jpxd_process` buffers input until `last`, decodes on demand, and outputs one row fragment at a time.
- `s_jpxd_release` frees JasPer image/stream resources and the temporary buffer.

Notable dependencies:
- External `jasper/jasper.h`.
- Ghostscript non-GC allocator access through `gsmalloc.h`.

Research notes:
- `s_jpxd_buffer_input` has a TODO for allocation failure; if growth allocation fails, the following `memcpy` would use a null buffer.
- The memory stream is opened with `state->bufsize` rather than `state->buffill`, so unused buffer tail bytes may be visible to JasPer.
- As with JBIG2, the implementation intentionally relies on external-library allocation and release cleanup rather than normal GC enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.h

Header for the JPXDecode stream filter.

Key contents:
- Defines `stream_jpxd_state` with JasPer image/stream pointers, output offset, non-GC memory pointer, compressed-data buffer, buffer size, and bytes filled.
- Declares GC structure macro and `s_jpxd_template`.

Notable dependencies:
- External JasPer API.
- `scommon.h` stream-state definitions.

Research notes:
- The comments document the central design constraint: JasPer lacks a public API for incremental pieces in this code path, so the full compressed stream is spooled before decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwc.c

Shared LZW stream support code.

Key behavior:
- Defines the public GC structure for `stream_LZW_state`.
- `s_LZW_set_defaults` applies default decode parameters and clears the table pointer.
- `s_LZW_release` frees the allocated LZW table storage through `table.decode`, shared with the union used by encode/decode state.

Notable dependencies:
- LZW state definitions from `slzwx.h`.
- Ghostscript stream implementation macros.

Research notes:
- The release routine depends on encode and decode table pointers sharing the same union slot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwd.c

LZWDecode stream filter implementation.

Key behavior:
- Defines reset, EOD, and first assignable codes relative to `InitialCodeLength`.
- Allocates a 4097-entry decode table and initializes literal codes, reset/EOD sentinels, bit state, and code-size state.
- `s_LZWD_process` reads variable-width codes in high- or low-bit-first order, supports GIF block data, handles reset and EOD codes, grows the dictionary, expands strings back-to-front, and preserves partial string copies when output buffers fill.
- Handles the classic anomalous LZW case where the next code equals the next dictionary slot.
- Includes compatibility behavior for non-GIF streams with one extra data item before reset near full dictionary.

Notable dependencies:
- Shared LZW state from `slzwx.h`.
- Debug output through `gdebug.h`.

Research notes:
- Allocation failure is marked with historical “WRONG” comment because it returns `ERRC`.
- The decoder supports both PostScript/PDF-style LZW and GIF-style block data parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwe.c

LZWEncode stream filter implementation.

Key behavior:
- Defines fixed PostScript LZW special codes: reset `256`, EOD `257`, first assignable `258`.
- Uses an open-addressed hash table to map `(prefix code, byte)` sequences to dictionary codes.
- `lzw_put_code` writes variable-width codes into the output bit buffer.
- `lzw_reset_encode` resets dictionary state and preloads all single-byte codes.
- `s_LZWE_init` allocates the encoding table, emits initial reset on first process call, and initializes bit state.
- `s_LZWE_process` recognizes longest existing sequences, emits codes, adds dictionary entries, increases code width at thresholds, resets at the dictionary limit, and emits final code/EOD/final byte on `last`.

Notable dependencies:
- Shared LZW state/release from `slzwx.h`/`slzwc.c`.

Research notes:
- This older file carries the Aladdin Ghostscript public-license notice style rather than the later common license header.
- Allocation failure is marked “WRONG” because it returns `ERRC`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwx.h

Shared LZW encode/decode stream state and templates.

Key contents:
- Forward declares decode and encode table types.
- Defines `stream_LZW_state` with client parameters (`InitialCodeLength`, `FirstBitLowOrder`, `BlockData`, `EarlyChange`) and dynamic bit/dictionary/copy state.
- Defines default parameter macro: initial code length 8, high-bit-first, no block data, early change 1, cleared table pointer.
- Declares encode/decode templates and shared default/release procedures.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- The shared state supports both decoder and encoder even though some parameters are decode-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.c

MD5Encode stream filter.

Key behavior:
- `s_MD5E_init` initializes the MD5 state.
- `s_MD5E_process` consumes all input into `md5_append`; when `last` is true and 16 output bytes are available, emits the digest with `md5_finish` and returns `EOFC`.
- `s_MD5E_make_stream` allocates a stream and state, initializes an MD5 filter over a caller-supplied digest buffer, and returns the stream.

Notable dependencies:
- MD5 implementation from `md5.h`.
- Ghostscript stream allocation and filter initialization APIs.

Research notes:
- The filter emits no output until close/final input.
- `s_MD5E_make_stream` cleans up both stream and state on initialization failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.h

Header for the MD5Encode stream filter.

Key contents:
- Defines `stream_MD5E_state` with common stream state plus `md5_state_t`.
- Declares GC state macro, `s_MD5E_template`, and `s_MD5E_make_stream`.

Notable dependencies:
- `md5.h`.
- Stream types from `scommon.h`/`strimpl.h` in users.

Research notes:
- The header documents filter semantics: arbitrary input, 16-byte digest on close.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.c

Move-to-front encode/decode stream filters.

Key behavior:
- `s_MTF_init` initializes the 256-byte symbol list in identity order.
- `s_MTFE_process` encodes each input byte as its current index, shifting preceding entries toward the byte’s previous position.
- `s_MTFD_process` decodes indexes back to bytes, optimized for frequent zero indexes and caching the first four entries in local variables.
- Decode has additional optimized paths for small indexes and long-sized chunk shifting for larger indexes.

Notable dependencies:
- State definition from `smtf.h`.
- Architecture constants for endian and long size.

Research notes:
- The comment notes zeros dominate in the BWBS code, motivating the decode fast path.
- Decode template provides `s_MTF_init` as reinitialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.h

Header for MoveToFront encode/decode filters.

Key contents:
- Defines `stream_MTF_state` with a 256-byte previous-symbol list stored as a union of bytes and machine words.
- Aliases encode and decode state types to the same structure.
- Declares GC structure macro and stream templates.

Notable dependencies:
- Requires stream common definitions.

Research notes:
- The union supports the word-sized shifting optimization in the decoder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiff.c

PixelDifferenceEncode/Decode stream filters for component-wise horizontal differencing.

Key behavior:
- Initializes row byte count, trailing-bit mask, and a case-dispatch index based on `BitsPerComponent`, color count, and encode/decode mode.
- `s_PDiff_process` resets previous samples at row boundaries and handles encode/decode in one large switch.
- Supports 1-, 2-, 4-, 8-, and nominally 16-bit components, with specialized paths for common color counts and aligned/unaligned packing.
- Encoding computes current sample minus previous sample; decoding adds previous sample back.
- Preserves untouched trailing bits in the last row byte through `end_mask`.

Notable dependencies:
- State and defaults from `spdiffx.h`.

Research notes:
- The file is heavily macro-optimized and difficult to modify safely.
- The 16-bit component paths contain suspicious typos: `ENCODE16` writes `q[d] = t & 0xff` rather than using `ti`, and `DECODE16` writes `q[d] = s && 0xff`; the non-macro 16-bit decode path also uses `*++p >> 8` where a high-byte shift-left would be expected. These are high-risk areas if 16-bit pixel differencing is used.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiffx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiffx.h

Header for PixelDifference encode/decode filters.

Key contents:
- Defines `s_PDiff_max_Colors` as 16.
- Defines `stream_PDiff_state` with client parameters (`Colors`, `BitsPerComponent`, `Columns`), computed row metadata, dispatch index, row bytes left, and previous samples.
- Provides default parameters: 1 color, 8 bits/component, 1 column.
- Declares encode and decode stream templates.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- The comment says `BitsPerComponent` supports 1, 2, 4, 8, while the implementation also contains 16-bit cases; this mismatch is worth checking before using 16-bit mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spdiffx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngp.c

PNGPredictorEncode/Decode stream filters implementing PNG row predictors.

Key behavior:
- Initializes bytes per row, trailing-bit mask, bytes per pixel, optional previous-row buffer, and row state.
- Supports PNG predictor algorithms: None, Sub, Up, Average, Paeth, and an `Optimum` placeholder.
- Encoding writes a predictor algorithm byte at the start of each row, then filters row bytes against left/up/upper-left references.
- Decoding reads the row predictor byte and reconstructs bytes using the corresponding inverse operation.
- Maintains `prev` bytes for left-pixel history and `prev_row` storage for Up/Average/Paeth predictors across rows.
- `paeth_predictor` implements PNG’s Paeth predictor.

Notable dependencies:
- State definition from `spngpx.h`.

Research notes:
- `optimum_predictor` is a stub that always selects Sub.
- Allocation and overflow error paths are marked “WRONG” because they return `ERRC` rather than a more specific Ghostscript error.
- The code uses Ghostscript cursor convention carefully, but the row-history memmove/copy sections are sensitive to partial buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngpx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngpx.h

Header for PNGPredictor encode/decode filters.

Key contents:
- Defines `stream_PNGP_state` with predictor parameters, computed row size/mask/bytes-per-pixel, previous-row pointer, dispatch index, row bytes left, and previous sample bytes.
- Default parameters: 1 color, 8 bits/component, 1 column, predictor 15.
- Declares GC pointer tracing for `prev_row` and encode/decode stream templates.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- `prev` is fixed at 32 bytes, sufficient for documented `Colors` 1..16 with up to 16 bits/component.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spngpx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.c

Small formatted-printing utilities for writing ASCII values to Ghostscript streams.

Key behavior:
- `stream_write` and `stream_puts` write byte arrays and C strings to a stream.
- `pprintf_scan` writes literal format text through the next substitution marker, treating `%%` as a literal `%`.
- `pprintd*`, `pprintld*`, `pprintg*`, and `pprints*` provide fixed-arity substitutions for ints, longs, floats, and strings.
- Floating-point printing uses `%g`, but if exponential notation appears it retries with fixed formatting because PDF disallows exponent notation in this context.

Notable dependencies:
- `stream.h` output APIs.
- `math_.h` for `fabs`.

Research notes:
- These helpers exist because older C varargs support was inconsistent across target compilers.
- Format validation is debug-only and assumes callers pass matching fixed-arity formats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.h

Header for ASCII stream printing helpers.

Key contents:
- Opaque `stream` declaration.
- `stream_putc`, `stream_write`, and `stream_puts`.
- Fixed-arity printing declarations for float, int, long, and string values.
- Comments explain the PDF restriction against exponential float notation and the portability reason for avoiding general varargs.

Notable dependencies:
- Uses `uint` and `floatp` from Ghostscript type context.

Research notes:
- The API returns a pointer to the next format substitution marker so calls can be chained for multi-argument printing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.c

Common PostScript/PDF output syntax utilities and parameter-printing support.

Key behavior:
- `s_write_ps_string` writes bytes as either a literal PostScript string or hex string, choosing the shorter permitted form unless binary or hex restrictions force a choice.
- Binary string mode escapes only `(`, `)`, backslash, CR, and LF.
- Non-binary mode estimates literal-string escape overhead and uses `PSStringEncode` or `ASCIIHexEncode`.
- `s_alloc_position_stream` creates a write stream that tracks position only.
- Parameter-printer setup creates a `gs_param_list` implementation that writes non-default parameter key/value pairs to a stream.
- `param_print_typed` prints null, bool, int, long, float, string, name, int array, and float array values in PostScript/PDF-like syntax.

Notable dependencies:
- Printing helpers from `spprint.h`.
- String/hex filters from `sstring.h`, `sa85x.h`.
- Ghostscript parameter list APIs from `gsparam.h`.

Research notes:
- ASCII85 string output is noted but not implemented.
- Name printing has a comment that PDF `#` escaping should be used but is not.
- In `param_print_typed`, the long case uses format `" %l"` even though `pprintld1` debug-checks for `%ld`; this looks suspicious in debug builds and may omit the expected `d`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.h

Header for common PostScript/PDF output syntax and parameter printer utilities.

Key contents:
- Defines string-printing flags: `PRINT_BINARY_OK`, `PRINT_ASCII85_OK`, `PRINT_HEX_NOT_OK`.
- Declares `s_write_ps_string` and `s_alloc_position_stream`.
- Defines `param_printer_params_t` for prefix/suffix/item formatting and string print permissions.
- Defines stack-allocatable `printer_param_list_t`.
- Declares allocation, initialization, release, and free helpers for parameter printers.

Notable dependencies:
- Ghostscript parameter API from `gsparam.h`.

Research notes:
- The implementation structure is intentionally exposed because some callers stack-allocate it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/spsdf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srdline.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srdline.h

Interface declaration for Ghostscript readline support.

Key contents:
- Defines `sreadline_proc` signature for reading a prompted line from an input stream to a growable buffer.
- Documents buffer-growth behavior, EOL handling, `^M`/`^J` suppression via `pin_eol`, and `is_stdin` callback use.
- Declares the default implementation `sreadline`.

Notable dependencies:
- Requires `gsmemory.h` and `gstypes.h` according to the header comment.
- Uses opaque `stream`.

Research notes:
- This file contains only the interface contract; implementation is elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srdline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srld.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srld.c

RunLengthDecode stream filter.

Key behavior:
- Initializes defaults and dynamic copy state from `srlx.h` inline macros.
- `s_RLD_process` decodes PackBits/PostScript-style run-length records:
  - control byte `<128`: copy the next `b+1` literal bytes;
  - control byte `128`: EOD if `EndOfData` is true;
  - control byte `>128`: repeat next byte `257-b` times.
- Preserves partial literal or repeat runs across output-buffer exhaustion.

Notable dependencies:
- Shared run-length state from `srlx.h`.

Research notes:
- Literal-copy suspension uses `copy_data = -1`; repeat suspension stores the repeated byte in `copy_data`.
- If `EndOfData` is false, byte 128 is ignored rather than ending the stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srld.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srle.c

RunLengthEncode stream filter.

Key behavior:
- Initializes record size/remaining bytes and copy state from `srlx.h` inline macros.
- `s_RLE_process` emits optimal PackBits/PostScript-style run-length output by looking ahead enough to avoid prematurely breaking repeated runs.
- Encodes repeated runs as `257-run_length, byte`; literal runs as `run_length-1` followed by literal bytes.
- Supports logical record boundaries via `record_size`.
- Handles partial literal copying when the output buffer cannot hold a full literal record.
- Emits EOD byte `128` on final input when `EndOfData` is true.

Notable dependencies:
- Shared run-length state from `srlx.h`.

Research notes:
- The encoder intentionally does extra lookahead to generate optimal output for old conformance expectations.
- Minimum input size in the template is 129 to support lookahead and max literal-run decisions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srlx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/srlx.h

Shared header for RunLength encode/decode filters.

Key contents:
- Defines common `EndOfData` parameter.
- Defines `stream_RLE_state` with `record_size`, `record_left`, and delayed literal copy count.
- Provides RLE default/init macros, with zero `record_size` normalized to `max_uint`.
- Defines `stream_RLD_state` with delayed output count and repeat/literal indicator.
- Provides RLD default/init macros, including `min_left` setup based on `EndOfData`.
- Declares encode and decode templates.

Notable dependencies:
- Requires stream common definitions.

Research notes:
- Both filters expose inline init macros so clients can avoid procedure-call overhead.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/srlx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.c

String and hex-string stream filters plus shared hex decode utility.

Key behavior:
- `ASCIIHexEncode` emits uppercase hex, inserts newlines after 32 source bytes, and optionally appends `>`.
- `ASCIIHexDecode` uses `s_hex_process`, handles odd final hex digits by padding the low nibble, scans for `>`, and returns `EOFC` at EOD.
- `PSStringEncode` escapes PostScript literal-string special characters, control characters, and non-ASCII bytes, appending `)` on final input.
- `PSStringDecode` parses literal strings, escape sequences, octal escapes, line continuations, nested parentheses, CR/LF normalization, and scanner-specific `from_string` mode.
- `s_hex_process` is a reusable hex scanner supporting whitespace-ignore, leading-whitespace-only, and garbage-ignore modes while preserving odd digit state across calls.

Notable dependencies:
- Scanner character table from `scanchar.h`.
- Stream state definitions from `sstring.h`.

Research notes:
- The decoder relies on the Ghostscript cursor convention and backs up input when it needs more bytes to complete an escape.
- `PSStringDecode` treats `)` at depth zero as `EOFC`, matching PostScript literal string termination.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.h

Header for ASCIIHex and PostScript string stream filters.

Key contents:
- Defines `stream_AXE_state` with `EndOfData` and line-count state.
- Defines `stream_AXD_state` with odd hex digit state.
- Defines `stream_PSSD_state` with `from_string` and parenthesis depth.
- Declares init macros, concrete init for `PSStringDecode`, and stream templates for ASCIIHexEncode/Decode and PSStringEncode/Decode.

Notable dependencies:
- Requires stream common definitions in users.

Research notes:
- `s_PSSD_partially_init_inline` intentionally does not initialize `from_string`, allowing scanner-specific setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stat_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stat_.h

Portable wrapper/substitute header around Unix `sys/stat.h`.

Key behavior:
- Includes `std.h` before platform stat headers to satisfy systems where `sys/types.h` ordering matters.
- Includes `<stat.h>` for Metrowerks, otherwise `<sys/stat.h>`.
- Defines `stat_blocks` using `st_blocks` where available, or approximates blocks from file size for many platforms including Plan9.
- Maps Microsoft `_stat` to `stat`.
- Defines `stat_is_dir` using `S_ISDIR` when available or mode-bit fallbacks otherwise.
- Defines missing `S_ISCHR`, `S_ISREG`, `S_IRUSR`, and `S_IWUSR` portability macros.

Notable dependencies:
- Platform/compiler preprocessor symbols.

Research notes:
- This is portability infrastructure rather than filesystem logic.
- Plan9 is explicitly included in the `stat_blocks` fallback path because its stat structure lacks portable `st_blocks`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stat_.h -->