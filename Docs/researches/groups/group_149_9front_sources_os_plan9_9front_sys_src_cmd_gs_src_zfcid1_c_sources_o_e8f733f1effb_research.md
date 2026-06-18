# Group Research: group_149_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_zfcid1_c_sources_o_e8f733f1effb

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid1.c

## Purpose
Implements Ghostscript interpreter operators for CIDFontType 1 and CIDFontType 2 fonts: `.buildfont10`, `.buildfont11`, CID-to-TrueType glyph mapping, and CIDMap construction support.

## Key Functions
- `zbuildfont10()` builds FontType 10 user-defined CID fonts, collecting build procedures and `CIDSystemInfo`.
- `z11_CIDMap_proc()` maps CID glyphs to TrueType glyph numbers from a string, integer offset, dictionary, or string-array CIDMap.
- `zbuildfont11()` builds CIDFontType 2 / FontType 11 TrueType CID fonts, including optional disk-file glyph caching and CIDMap validation.
- `ztype11mapcid()` exposes CID-to-GID mapping to PostScript.
- `zfillCIDMap()` delegates CIDMap population to `cid_fill_CIDMap()`.

## Important Behavior
- FontType 11 accepts CIDMap data as string/string-array, dictionary, or integer offset; string-based maps require nonzero `GDBytes`.
- `MetricsCount` must be 0, 2, or 4 and causes glyph data accessors to skip leading metric words.
- If the font dictionary has `File` and table offsets for `loca`/`glyf`, the font can cache glyph data from the TrueType file.

## Research Notes
This file bridges PostScript CID font dictionaries to Ghostscript's Type 42 TrueType engine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcmap.c

## Purpose
Creates internal Adobe CMap structures from PostScript CMap dictionaries and exposes `ztype0_get_cmap()` for Type 0 composite font construction.

## Key Functions
- `acquire_code_ranges()` converts `.CodeMapData` code-space ranges into `gx_code_space_range_t` entries.
- `acquire_code_map()` converts definition/notdef code maps into `gx_cmap_lookup_range_t` arrays.
- `ztype0_get_cmap()` extracts a built `CodeMap` struct from a Type 0 font dictionary.
- `zbuildcmap()` allocates and fills `gs_cmap_adobe1_t`, stores it under `CodeMap`, and makes the dictionary readonly.

## Important Behavior
- `.CodeMapData` must be a three-element array: code ranges, def ranges, and notdef ranges.
- Code-map entries are five-tuples: prefix, misc bytes, key bytes, value data, and font index.
- Missing `CIDSystemInfo` is tolerated by fabricating a zero-element array.
- CIDSystemInfo compatibility checking is compiled out by default.

## Research Notes
This is a parser/validator for the compact CMap representation prepared by Ghostscript PostScript support code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdctd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdctd.c

## Purpose
Creates the `DCTDecode` JPEG decompression filter for the PostScript interpreter.

## Key Functions
- `zDCTD()` allocates IJG decompression data, initializes `stream_DCT_state`, reads dictionary parameters, creates the JPEG decompressor, and wraps it in a read filter.

## Important Behavior
- Uses immovable allocation for `jpeg_decompress_data`.
- Parameter parsing is delegated to `s_DCTD_put_params()`.
- Error exits destroy the JPEG state and free auxiliary data if filter creation did not complete.

## Research Notes
This file is thin interpreter glue around the JPEG stream implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdctd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdcte.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdcte.c

## Purpose
Creates the `DCTEncode` JPEG compression filter for the PostScript interpreter.

## Key Functions
- `zDCTE()` allocates IJG compression data, initializes `stream_DCT_state`, reads encoder parameters, adjusts template buffer sizes, and opens a write filter.

## Important Behavior
- Uses stable, immovable memory for `jpeg_compress_data`.
- Parameter parsing is delegated to `s_DCTE_put_params()`.
- The copied stream template is adjusted so input buffering can hold a full scanline and output buffering can hold marker data.

## Research Notes
Mostly lifecycle and PostScript parameter plumbing for the JPEG stream layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdcte.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdecode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdecode.c

## Purpose
Registers additional decoding and predictor filters, plus ASCII85 encode/decode support.

## Key Functions
- `zA85E()` and `zA85D()` create ASCII85 encode/decode filters.
- `zcf_setup()` reads CCITT fax parameters.
- `zCFD()` creates `CCITTFaxDecode`.
- `filter_read_predictor()` optionally cascades decompression with PixelDifference or PNG predictor decode filters.
- `zlz_setup()` reads LZW/GIF-style parameters.
- `zLZWD()` creates `LZWDecode`.
- `zpd_setup()` and `zpp_setup()` parse PixelDifference and PNG predictor dictionaries.

## Important Behavior
- Predictor values 0/1 mean identity; 2 selects componentwise differencing; 10-15 select PNG prediction.
- Predictor cascades mark the compression stream temporary and propagate `CloseSource`.
- Pixel and PNG setup validate color counts, columns, and power-of-two `BitsPerComponent`.

## Research Notes
Shares setup routines with encoder-side support in `zfilter2.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdecode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile.c

## Purpose
Implements non-I/O PostScript file operators, file-name parsing, library-path file opening, safe-mode permission checks, temp-file handling, and low-level file stream allocation/closing.

## Key Functions
- `zfile()` opens files or IODevices, including special `%statementedit%` and `%lineedit%` handling.
- `zdeletefile()`, `zrenamefile()`, and `zstatus()` implement file-control/status operators.
- `zfilenameforall()` enumerates matching files via IODevice callbacks.
- `zexecfile()` executes a file and guarantees close through e-stack cleanup.
- `zlibfile()` searches the Ghostscript library path.
- `ztempfile()` creates scratch files with restricted prefix/absolute-path checks.
- `parse_file_name()`, `parse_real_file_name()`, and `parse_file_access_string()` validate file operands.
- `file_alloc_stream()`, `file_close_file()`, and `file_close()` manage stream lifetime and reuse.

## Important Behavior
- Stream objects carry serial ids; closing increments ids so stale PostScript file objects cannot access reused streams.
- Safe mode blocks `%pipe%` and applies permit-list matching after path reduction.
- Temp files created by `.tempfile` are allowed selected control operations through `SAFETY/tempfiles`.
- Library search checks reduced names before returning an opened file.

## Research Notes
This is the central file object infrastructure used by the interpreter, filters, startup library loading, and IODevices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile1.c

## Purpose
Provides small file-name utility operators backed by platform path helpers.

## Key Functions
- `zfile_name_combine()` combines prefix and file-name strings using `gp_file_name_combine()`.
- `zfile_name_is_absolute()` tests whether a string is an absolute path.
- `zfile_name_separator()`, `zfile_name_directory_separator()`, `zfile_name_current()`, and `zfile_name_parent()` expose platform path constants.

## Important Behavior
- Combination returns a `gp_file_name_combine_result` plus the actual combined string.
- Output strings are allocated in the current VM space.

## Research Notes
Nonstandard convenience operators for portable path manipulation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfileio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfileio.c

## Purpose
Implements PostScript file I/O operators: reads, writes, line and string operations, flushing, seeking, filename lookup, proc-filter checks, and stdin/stdout/stderr callouts.

## Key Functions
- `zclosefile()`, `zread()`, `zwrite()`, `zwritestring()`, `zprint()`, `zflush()`, and `zflushfile()` implement basic I/O.
- `zreadhexstring_at()`, `zwritehexstring_at()`, `zreadstring_at()`, and `zreadline_at()` perform partial I/O with continuation support.
- `zbytesavailable()`, `zfileposition()`, `zxfileposition()`, and `zsetfileposition()` expose stream availability and seek state.
- `zfilename()`, `zisprocfilter()`, `zpeekstring()`, `zunread()`, and `zwritecvp()` implement Ghostscript extensions.
- `handle_read_status()` and `handle_write_status()` translate `INTC`/`CALLC` stream statuses into continuations.

## Important Behavior
- Partial reads/writes store an index or residual substring and resume through internal continuation operators.
- Stream error strings are copied into `$error.errorinfo` once.
- `readstring` intentionally returns `rangecheck` for zero-length strings to match Adobe behavior.
- `.peekstring` does not consume buffered bytes.

## Research Notes
Tightly coupled to `zfproc.c` because procedure streams use `CALLC` continuations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfileio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter.c

## Purpose
Creates common PostScript stream filters and provides generic filter-open machinery for string, file, and procedure sources/targets.

## Key Functions
- `zAXE()`, `zAXD()`, `zNullE()`, `zPFBD()`, `zPSSE()`, `zRLE()`, `zRLD()`, `zSFD()`, and `zEOFD()` create filters.
- `filter_read()` and `filter_write()` create filter file objects over source/target strings, files, or procedures.
- `filter_ensure_buf()` inserts or allocates intermediate buffering when needed.
- `filter_mark_temp()` and `filter_mark_strm_temp()` mark temporary filter streams for close cleanup.

## Important Behavior
- Optional filter dictionaries can supply `CloseSource` or `CloseTarget`.
- Procedure operands are converted through `sread_proc()` / `swrite_proc()`.
- String sources/targets are wrapped as temporary streams.
- `SubFileDecode` supports the LL3 dictionary form with `EODCount`/`EODString`.

## Research Notes
Shared interpreter-side filter framework used by the specialized filter files in this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter2.c

## Purpose
Adds encoder-side CCITT Fax and LZW filters and implements predictor cascade support for write filters.

## Key Functions
- `zCFE()` creates `CCITTFaxEncode`.
- `filter_write_predictor()` optionally wraps compression output with PixelDifference or PNG predictor encode filters.
- `zLZWE()` creates `LZWEncode`.

## Important Behavior
- Predictor handling mirrors `filter_read_predictor()` in `zfdecode.c`.
- Predictor 0/1 means no predictor; 2 selects PixelDifference; 10-15 selects PNG prediction.
- Cascaded predictor setup marks the compression stream temporary so close semantics remain correct.

## Research Notes
Most parameter parsing is shared with decoder-side helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilterx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilterx.c

## Purpose
Registers nonstandard extended filters: bounded Huffman, Burrows-Wheeler block sorting, byte translation, move-to-front, plus a code-table computation operator.

## Key Functions
- `bhc_setup()` validates bounded Huffman dictionaries and constructs count/value tables.
- `zBHCE()` and `zBHCD()` create bounded Huffman encode/decode filters.
- `zcomputecodes()` computes canonical Huffman code counts and values from frequencies.
- `zBWBSE()` / `zBWBSD()` handle Burrows-Wheeler block sorting filters.
- `zBTE()` / `zBTD()` handle 256-byte translation tables.
- `zMTFE()` / `zMTFD()` create move-to-front filters.

## Important Behavior
- Bounded Huffman tables must fill the code space exactly.
- `.computecodes` replaces array entries in-place.
- Byte translation requires an exact 256-byte string.

## Research Notes
Ghostscript extension filters using the same `filter_read`/`filter_write` infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilterx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjbig2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjbig2.c

## Purpose
Implements interpreter support for `JBIG2Decode` and parsed JBIG2 global contexts.

## Key Functions
- `z_jbig2decode()` creates the JBIG2 decode filter and attaches an optional parsed global context.
- `z_jbig2makeglobalctx()` builds a `Jbig2GlobalCtx` from bytes and wraps it in an interpreter `astruct`.
- `jbig2_global_data_finalize()` releases the external JBIG2 global context.

## Important Behavior
- JBIG2 global context memory is not directly GC-managed, so a finalizer frees it.
- Invalid or unparseable global data returns `unknownerror`.

## Research Notes
PostScript code is expected to resolve `JBIG2Globals` and call `.jbig2makeglobalctx` before invoking the filter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjbig2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjpx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjpx.c

## Purpose
Creates the `JPXDecode` filter for JPEG 2000 data.

## Key Functions
- `z_jpx_decode()` initializes `stream_jpxd_state`, notes but does not implement `Colorspace`, and opens the read filter.

## Important Behavior
- Uses `imemory->non_gc_memory` for JPX decoder allocations.
- The `Colorspace` parameter is detected only for diagnostic logging.

## Research Notes
Minimal interpreter wrapper around the JPX stream decoder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjpx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfmd5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfmd5.c

## Purpose
Registers the `MD5Encode` write filter.

## Key Functions
- `zMD5E()` delegates directly to `filter_write_simple()` with `s_MD5E_template`.

## Important Behavior
- Only an encoder is registered; there is no MD5 decode counterpart.

## Research Notes
Thin filter registration file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfmd5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont.c

## Purpose
Implements generic PostScript font operators, global font-directory initialization, transformed font dictionary creation, font cache parameters, restore cleanup, and Unicode decoder setup.

## Key Functions
- `zfont_init()` allocates `ifont_dir` and registers it as a GC root.
- `zscalefont()`, `zmakefont()`, and `make_font()` create transformed fonts.
- `zsetfont()` and `zcurrentfont()` update/query the graphics-state font.
- Cache operators expose font/character cache controls.
- `font_param()` validates a PostScript font dictionary and extracts its `gs_font`.
- `zdefault_make_font()` builds transformed font dictionaries with `FontMatrix`, `OrigFont`, `ScaleMatrix`, and new `FID`.
- `font_restore()` purges fonts/cache entries invalidated by VM restore.
- `setup_unicode_decoder()` stores a glyph-to-Unicode decoding dictionary.

## Important Behavior
- `font_param()` checks that `FID` points back to the same dictionary.
- `make_font()` temporarily substitutes the caller's dictionary so changed encodings can affect transformed fonts.
- Restore cleanup purges fonts, xfonts, and cached characters whose glyph names were allocated after the save.

## Research Notes
Common font operator layer used by all font-type-specific builders.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont0.c

## Purpose
Builds Type 0 composite fonts and handles composite font define/make-font adjustments.

## Key Functions
- `zbuildfont0()` validates `FMapType`, `FDepVector`, encoding data, and FMap-specific parameters.
- `ztype0_adjust_FDepVector()` rewrites the parent dictionary's `FDepVector` if subfonts changed.
- `ztype0_define_font()` and `ztype0_make_font()` wrap Type 0 define/scale logic.
- `ensure_char_entry()` inserts or validates `EscChar`, `ShiftIn`, and `ShiftOut`.

## Important Behavior
- Enforces Type 0 inheritance rules for nested composite subfonts.
- `fmap_CMap` uses `ztype0_get_cmap()`.
- Saves and restores an existing `FID` if build failure requires backing out dictionary mutation.
- Encoding entries must be integer indices into `FDepVector`.

## Research Notes
Ties the CMap builder in `zfcmap.c` to Ghostscript's composite font engine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont1.c

## Purpose
Builds Type 1 and Type 4 CharString fonts and provides shared CharString-font parameter parsing used by Type 2/CID font code.

## Key Functions
- `charstring_font_get_refs()` extracts `Private`, `OtherSubrs`, `Subrs`, and initializes `GlobalSubrs`.
- `charstring_font_params()` reads Type 1 private dictionary hinting and interpreter parameters.
- `charstring_font_init()` fills `gs_font_type1` data and installs glyph procedures.
- `build_charstring_font()` builds and defines Type 1-like fonts.
- `zbuildfont1()` and `zbuildfont4()` build Type 1 encrypted and Type 4 disk-based fonts.
- `z1_same_font()` compares outline, metrics, and encoding identity.

## Important Behavior
- Missing `OtherSubrs`/`Subrs` become empty arrays.
- Out-of-range `BlueScale` is clamped.
- Non-0/1 `LanguageGroup` values are normalized to 0 for compatibility.
- `same_font` comparisons inspect `CharStrings`, `Private`, metrics dictionaries, and `Encoding`.

## Research Notes
Shared base for CharString-based font families; `zfont2.c` adds Type 2-specific parameters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont2.c

## Purpose
Builds Type 2 / CFF CharString fonts.

## Key Functions
- `subr_bias()` computes CFF local/global subroutine bias from subroutine count.
- `type2_font_params()` sets Type 2 interpreter parameters, reads `GlobalSubrs`, width defaults, and random seed.
- `zbuildfont2()` builds a Type 2 font using `%Type2BuildChar` and `%Type2BuildGlyph`.

## Important Behavior
- Type 2 fonts use `gs_type2_interpret`, default `lenIV` 0, and CFF subroutine bias rules.
- `GlobalSubrs` must be an array if present.
- `defaultWidthX` and `nominalWidthX` are converted to fixed-point values.

## Research Notes
Relies on the Type 1 shared CharString builder from `zfont1.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont32.c

## Purpose
Builds Type 32 bitmap CID fonts.

## Key Functions
- `zfont_no_encode_char()` returns `gs_no_glyph`; Type 32 encode-char should not be called.
- `zbuildfont32()` builds a bitmap CID font using `%Type32BuildGlyph`.

## Important Behavior
- `BuildChar` is absent; only `BuildGlyph` is supplied.
- Bitmap width/size behavior is set to always transform cached bitmaps.
- The font's `encode_char` procedure is replaced with a no-glyph stub.

## Research Notes
Compact builder for Ghostscript's bitmap CID font type.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont42.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont42.c

## Purpose
Builds Type 42 TrueType fonts and provides shared TrueType access helpers for CIDFontType 2.

## Key Functions
- `build_gs_TrueType_font()` validates `sfnts` and `GlyphDirectory`, builds Type 42/Type 11 fonts, initializes TrueType data, and installs glyph access procedures.
- `zbuildfont42()` defines a regular Type 42 font.
- `font_string_array_param()` validates string-array parameters.
- `font_GlyphDirectory_param()` accepts dictionary/array glyph directories or null.
- `string_array_access_proc()` accesses byte spans across an array of strings.
- `glyph_to_index()` maps glyph names through `CharStrings` to GID glyphs.
- `font_gdir_get_outline()` gets glyph data from `GlyphDirectory`.

## Important Behavior
- `sfnts` is checked immediately by reading the first array element as a string.
- If `GlyphDirectory` is present, it replaces `loca`/`glyf` outline access and glyph enumeration.
- Missing glyph-directory outlines return null glyph data rather than immediate failure.
- GID glyphs are represented with `GS_MIN_GLYPH_INDEX` offset.

## Research Notes
Main bridge between PostScript Type 42 dictionaries and the graphics library's TrueType engine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont42.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfontenum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfontenum.c

## Purpose
Exposes platform native font enumeration to PostScript as `.getnativefonts`.

## Key Functions
- `z_fontenum()` calls `gp_enumerate_fonts_init/next/free`, copies returned name/path pairs, and returns `[ [name path] ... ] true` or `false`.

## Important Behavior
- Uses non-GC memory for the temporary linked list and interpreter memory for returned PostScript strings/arrays.
- Returns `false` when native enumeration is unavailable.
- Treats null font names or paths from the platform enumerator as I/O errors.

## Research Notes
Platform-integration glue for populating Fontmap-like data from system fonts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfontenum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfproc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfproc.c

## Purpose
Implements procedure-backed stream support, allowing PostScript procedures to serve as filter sources or sinks and to resume I/O after callouts.

## Key Functions
- `s_proc_init()` allocates a stream and `stream_proc_state`.
- `sread_proc()` and `swrite_proc()` create procedure read/write streams.
- `s_proc_read_process()` and `s_proc_write_process()` move data between stream buffers and procedure-provided strings.
- `s_handle_read_exception()` and `s_handle_write_exception()` build e-stack continuation frames.
- `s_proc_read_continue()` and `s_proc_write_continue()` resume after callbacks.
- `s_is_proc()` identifies procedure-backed streams.

## Important Behavior
- Procedure stream state contains PostScript refs and has custom GC mark/relocate procedures.
- `CALLC` asks the interpreter to execute the stored procedure; `INTC` pushes an interrupt continuation.
- Stdin/stdout/stderr streams add `.needstdin`, `.needstdout`, or `.needstderr` callouts.
- Read procedures return strings; zero-length strings mark EOF.

## Research Notes
Continuation engine behind procedure filters and stream statuses handled in `zfileio.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfrsd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfrsd.c

## Purpose
Provides internal support for `ReusableStreamDecode`: parameter normalization and creation of reusable streams from strings, bytes, seekable files, and certain subfile filters.

## Key Functions
- `zrsdparams()` normalizes `Filter` and `DecodeParms` into arrays/null and validates decode filter names.
- `zreusablestream()` validates reusable sources and delegates to string or file stream constructors.
- `make_rss()` creates a reusable string stream.
- `make_rfs()` reopens a named file and wraps a subfile slice as a reusable stream.

## Important Behavior
- Filter names must end in `Decode`.
- `DecodeParms` must be null, a dictionary for a single filter, or an array matching the filter array length.
- Reusable file sources must be readable and seekable.
- A `SubFileDecode` source is reusable only when its `EODString` is empty.
- `%stdin%`-like device-only streams cannot be reopened as reusable files.

## Research Notes
The surrounding reusable-stream construction is mostly in PostScript; this file handles C-level source inspection and reopening.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfrsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfsample.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfsample.c

## Purpose
Samples an arbitrary PostScript procedure over a hypercube and converts it into a FunctionType 0 sampled function.

## Key Functions
- `zbuildsampledfunction()` reads the source procedure and sampled-function dictionary and starts sampling.
- `valid_cube_size()` ensures requested sample data fits within the 64 KiB string limit.
- `determine_sampled_data_size()` chooses default per-input sample counts.
- `cube_build_func0()` validates parameters and allocates sample storage.
- `sampled_data_setup()` allocates the sampling enumerator and pushes protected e-stack state.
- `sampled_data_sample()` pushes input coordinates and executes the procedure.
- `sampled_data_continue()` validates stack balance, clamps/scales outputs, stores samples, and advances indexes.
- `sampled_data_finish()` rebuilds the final sampled function and returns an executable closure.

## Important Behavior
- Sample data is capped at `MAX_DATA_SIZE` (`0x10000`), with up to 16 inputs and 128 outputs.
- Default cube side lengths shrink as dimensionality increases.
- Three padding operands are placed below procedure inputs to tolerate malformed tint transforms.
- Outputs are clamped to `Range` before quantization.

## Research Notes
Continuation-heavy bridge from executable PostScript procedures to static sampled function data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc.c

## Purpose
Implements the generic PostScript interface to PDF/PostScript functions: building function structures, wrapping them as executable closures, executing them, and recognizing encapsulated functions.

## Key Functions
- `make_function_proc()` creates an executable closure containing the function struct and `%execfunction`.
- `zbuildfunction()` builds a function from a dictionary.
- `zexecfunction()` reads inputs from the operand stack, evaluates the function, and writes outputs back.
- `zisencapfunction()` tests whether a procedure is a Ghostscript function closure.
- `fn_build_function()` and `fn_build_sub_function()` dispatch by `FunctionType`.
- `fn_build_float_array()` and `fn_build_float_array_forced()` read numeric arrays/scalars.
- `ref_function()` recognizes closures produced by `.buildfunction`.

## Important Behavior
- Nested subsidiary functions are limited by `MAX_SUB_FUNCTION_DEPTH` (3).
- Common `Domain` and optional `Range` are collected before type-specific dispatch.
- `%execfunction` uses a stack buffer for small input/output counts and heap allocation for larger functions.

## Research Notes
Type-specific builders are registered elsewhere, including FunctionType 0 support in `zfunc0.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc0.c

## Purpose
Builds FunctionType 0 sampled functions from PostScript dictionaries.

## Key Functions
- `gs_build_function_0()` fills `gs_function_Sd_params_t` from a dictionary and initializes a sampled data function.

## Important Behavior
- `DataSource` must be a string or a readable, seekable file.
- Optional `Order` defaults to 1 and is restricted to 1-3.
- `BitsPerSample` must be 1-32.
- Optional `Encode` length must be `2*m`; optional `Decode` length must be `2*n`.
- `Size` is required and must contain `m` integers.
- Failure paths call `gs_function_Sd_free_params()`.

## Research Notes
Direct FunctionType 0 builder used by generic function dispatch in `zfunc.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc0.c -->