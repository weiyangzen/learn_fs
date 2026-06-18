# Group Research: group_1550_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevpsf2_c_sources__3cd74dc5d847

Scope checked against `Docs/research_subset_a.md`: this group is within `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf2.c

This file writes embedded Compact Font Format (CFF) fonts containing Type 1, Type 2, and CIDFontType 0 charstrings for Ghostscript's PostScript/PDF font-output path. It is not filesystem code; it serializes font resources to Ghostscript `stream` objects.

The central state is `cff_writer_t`, carrying output options, the target stream, source base font, glyph-data callback, active CFF offset width, standard/private string tables, and the font bounding box. `cff_string_table_t` implements a compact open-addressed SID table: lookups first try the standard CFF string set and then enter nonstandard strings into the private string INDEX.

Major responsibilities:
- Encode CFF primitive structures: integers, reals, booleans, operators, offsets, INDEXes, string SIDs, charstrings, and dict entries.
- Write Top DICT variants for simple Type 1/Type 2 fonts, CIDFontType 0 top dictionaries, and FDArray subfont dictionaries.
- Write Private DICT data including BlueValues, stem data, width defaults, lenIV policy, language group, expansion factor, and local Subrs offsets.
- Serialize CharStrings INDEX, local/global Subrs INDEXes, simple-font Encoding, simple charset, CID charset, FDSelect, and FDArray.
- Convert Type 1 charstrings to Type 2 through `psf_convert_type1_to_type2` when requested; otherwise copy encrypted/decrypted charstrings depending on `lenIV` and `WRITE_TYPE2_NO_LENIV`.
- Use `psf_get_type1_glyphs`, `psf_check_outline_glyphs`, and glyph enumerators from sibling utility code to validate and order subsets.

For simple fonts, `psf_write_type2_font` normalizes glyph ordering to `.notdef`, encoded glyphs, then unencoded glyphs. It explicitly stores Encoding and charset data rather than relying on predefined tables. For CIDFontType 0, `psf_write_cid0_font` enumerates selected CIDs, writes ROS information, builds FDSelect mappings from `cidata.glyph_data`, and uses each selected FDArray subfont as the Private DICT/Subrs owner for its glyphs.

A key design point is offset convergence. CFF offsets and DICT sizes depend on one another because integer encodings are variable length. Both public writers first emit to a position-only stream using large placeholder offsets, recompute section sizes, loop until offsets stabilize, and only then replay the same write to the real output stream.

Notable constraints and risks:
- Some fixed arrays are tight: CID FDArray/subrs arrays are capped at 256, CID string table storage is fixed, and simple-font string tables are sized from glyph count plus `MAX_CFF_MISC_STRINGS`.
- The code mutates Type 1 private width fields when emitting Type 2 charstrings, setting `defaultWidthX` and `nominalWidthX` to zero for non-`ft_encrypted2` sources.
- Subr subsetting is not implemented; comments state all Subrs are written even for subsets unless charstrings are converted and Subrs are expanded inline.
- Stream write helpers mostly rely on final `check_ioerror` calls rather than checking every byte emission.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfm.c

This file writes Ghostscript CMap objects in standard PostScript resource syntax. It serializes CMap headers, code space ranges, notdef mappings, CID mappings, bfchar/bfrange mappings, font-index switches, and CIDSystemInfo dictionaries.

Key helpers:
- `pput_string_entry` writes a `gs_const_string` after a literal prefix.
- `pput_hex` emits bytes as lowercase hexadecimal strings.
- `cmap_put_ranges` writes `begincodespacerange` blocks, with callers batching up to 100 ranges.
- `cmap_put_system_info` writes either `null` or a `Registry`/`Ordering`/`Supplement` dictionary.
- `cmap_put_code_map` enumerates CMap lookup ranges and emits mappings in blocks of at most 100 entries.

`psf_write_cmap` is the public entry point. It validates that `CMapType` is 0, 1, or 2; emits a Resource-CMap DSC header unless writing a ToUnicode CMap; writes fixed CMap dictionary fields; emits code-space ranges; emits notdef then normal mappings; and closes the CMap resource.

Important behavior:
- Multi-font CMaps emit `usefont` whenever the lookup font index changes.
- `font_index_only` restricts output to one descendant font and selects the corresponding CIDSystemInfo.
- `CODE_VALUE_GLYPH` values are converted to glyph names through the CMap callback and emitted through the caller-provided `put_name_chars` function.
- Range/char operators are selected from CID, notdef, bfchar, and bfrange variants based on lookup key shape and value type.

This is a serialization utility only. Its main dependencies are Ghostscript CMap enumeration APIs in `gxfcmap.h`, stream formatting helpers, and PostScript string/name writers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsft.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsft.c

This file writes embedded TrueType/sfnt data from Ghostscript Type 42 and CIDFontType 2 fonts. It can write normal TrueType subsets, stripped TrueType fonts, CIDFontType 2 fonts, and stripped CIDFontType 2 fonts.

Core responsibilities:
- Read and filter the source sfnt table directory through `pfont->data.string_proc`.
- Copy existing tables while omitting/replacing tables that must be synthesized (`glyf`, `loca`, selected generated cmap/name/OS/2/post/metrics tables).
- Rebuild `glyf` and `loca` from selected glyph outlines.
- Generate Macintosh and Windows cmap subtables when requested or required.
- Generate `name`, `OS/2`, metrics (`hmtx`/`vmtx`), and `post` tables when absent or requested.
- Sort the final table directory and write a complete sfnt header and table directory.
- Expand subset glyphs with composite pieces through `psf_add_subset_pieces` before writing Type 42 subsets.

Important helper groups:
- Big-endian table writers: `put_ushort`, `put_ulong`, `put_loca`, `put_u16`, and `put_u32`.
- Safe table copying: `write_range` repeatedly calls `string_proc` and handles segmented font data by shrinking reads.
- Generated cmap support: `write_cmap_0`, `write_cmap_6`, `write_cmap`, and `size_cmap`.
- Metrics support: `size_mtx` computes compact metric-table length and `write_mtx` emits widths and side bearings.
- Name/OS2/post support: `write_name`, `write_OS_2`, `update_OS_2`, `compute_post`, and `write_post`.

The main implementation, `psf_write_truetype_data`, scans existing tables, captures `head` and `maxp`, computes glyph and loca sizes, chooses short or long `loca`, builds generated table records with placeholder checksums, writes copied tables, emits generated glyph/location/support tables, and finally writes the corrected `head` table.

Plan 9-specific robustness changes are visible in `limdbl2ushort` and `limdbl2long`, which clamp floating-point metric conversions to avoid exceptions when large doubles are stored into integer fields.

Public entry points:
- `psf_write_truetype_font`
- `psf_write_truetype_stripped`
- `psf_write_cid2_font`
- `psf_write_cid2_stripped`

Notable constraints and risks:
- Comments explicitly say generated table checksums are not computed.
- Subset fonts do not trim `maxp`/related tables down to the highest used glyph because doing so would require broad table rewriting.
- `MAX_NUM_TABLES` limits output to 40 table records.
- Generated cmap handling uses private-use bias `0xf000` by default and may adjust OS/2 range bits for symbolic/private-use output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfu.c

This file provides shared PostScript/PDF font-writing utilities, mostly for glyph enumeration, glyph subset normalization, and outline-font validation.

Enumeration paths:
- `psf_enumerate_list_begin` enumerates an explicit glyph list, a CID range, or all font glyphs.
- `psf_enumerate_bits_begin` enumerates selected CIDs/TrueType glyph indices from a bit vector, a range, or all font glyphs.
- `psf_enumerate_glyphs_reset` and `psf_enumerate_glyphs_next` expose a common iterator API used by the CFF and TrueType writers.

Subset utilities:
- `psf_add_subset_pieces` appends composite glyph components, supporting Type 1 `seac` pieces and TrueType composite pieces.
- `psf_sort_glyphs` sorts glyph IDs and removes duplicates.
- `psf_sorted_glyphs_index_of` and `psf_sorted_glyphs_include` provide binary-search membership checks.

Outline validation and collection:
- `psf_check_outline_glyphs` verifies selected glyphs are writable as outline charstrings. It rejects procedure-backed CharStrings, unsupported nonstandard OtherSubrs, and CDevProc-dependent glyphs through the font's `glyph_data` and `glyph_info` callbacks.
- `psf_get_outline_glyphs` copies subset lists into owned storage when needed, validates writability, detects `.notdef`, adds subset component pieces, removes undefined glyphs, sorts the result, and guarantees `.notdef` for subsets.

This file is pure support code for font embedding. It does no direct output-format work beyond preparing the glyph order and metadata that the sibling writers serialize.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfx.c

This file converts Type 1 charstrings to unencrypted Type 2 charstrings. The converter expands local Subrs inline, collects hints, rewrites Type 1-only constructs, and opportunistically uses compact Type 2 operators.

Parsing layer:
- `type1_next_init` initializes a Ghostscript Type 1 interpreter state over one glyph data buffer.
- `skip_iv` decrypts/skips initial charstring random bytes according to `lenIV`.
- `type1_next` parses operands/operators, executes `callsubr` and `return`, handles `div`, blend OtherSubrs, pop suppression, and reports relevant operators to the converter.
- `type1_callsubr` loads local Subr data onto the Type 1 instruction stack.

Hint handling:
- `cv_stem_hint_table` stores horizontal and vertical stem hints, replacement state, and hint indices.
- `type1_stem1` and `type1_stem3` collect ordered/deduplicated hints.
- The first pass over the charstring gathers all hints and detects hint replacement/dotsection use.
- The second pass emits initial stem operators and `hintmask` bytes when active hints change.

Output layer:
- `type2_put_op`, `type2_put_int`, and `type2_put_fixed` encode Type 2 operators and operands.
- `type2_put_stems` emits compact stem hint data while respecting operand stack limits.
- `type2_put_hintmask` writes hintmask operators and active-hint bitmaps.

`psf_convert_type1_to_type2` is the main entry point. It handles width normalization from `hsbw`/`sbw`, initial side-bearing adjustment, moveto conversion, `seac` conversion through Type 2 `endchar` operands, flex OtherSubrs, dotsection replacement, stem replacement, and path operators.

Optimizations include combining repeated or compatible `rlineto`, `rrcurveto`, `hlineto`, `vlineto`, `hvcurveto`, and `vhcurveto` sequences; converting eligible curves to `hhcurveto` or `vvcurveto`; and using `rlinecurve`/`rcurveline` when a line/curve sequence permits it.

Notable limits:
- General unsupported OtherSubrs return `rangecheck`.
- Subrs are expanded inline rather than preserved.
- Counter control OtherSubrs are acknowledged but not implemented.
- Several comments identify further curve optimizations that were intentionally left out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsim.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsim.c

This file implements bitmap-only PostScript printer devices:
- `psmono`: 1-bit monochrome Level 1 PostScript.
- `psgray`: 8-bit grayscale Level 1 PostScript using the same encoder.
- `psrgb`: 24-bit RGB Level 2 PostScript.

Shared setup is handled by `ps_image_write_headers`, which writes the DSC file header on first use, computes a page bounding box from printer dimensions/resolution, emits device-specific setup procedures, and writes each page header through the `gdevpsu.c` helpers.

`psmono`/`psgray` path:
- Device descriptors are `gs_psmono_device` and `gs_psgray_device`.
- `psmono_setup` defines PostScript procedures for decoding a custom compact run-length/hex image stream.
- `psmono_print_page` reads each scanline with `gdev_prn_get_bits`, detects repeated-byte runs of at least 10 bytes, emits repeat-run codes, and sends literal data through `write_data_run`.
- `write_data_run` writes count codes and hexadecimal data, optionally inverting bytes for 1-bit output.
- `psmono_close` writes the final DSC trailer with `psw_end_file`.

`psrgb` path:
- Device descriptor is `gs_psrgb_device`.
- `psrgb_setup` defines an `rgbimage` PostScript procedure using `ASCII85Decode` and `RunLengthDecode`.
- `psrgb_print_page` builds Ghostscript stream filters `RunLengthEncode -> ASCII85Encode -> file`, writes planar R, G, and B data for every scanline, closes filters, and emits the page trailer.
- `psrgb_close` writes the final DSC trailer.

Filesystem relevance is limited to writing printer output through `FILE *` and Ghostscript printer abstractions. The code is an output device, not storage or VFS logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.c

This file provides shared utilities for Ghostscript PostScript-writing devices, especially DSC file/page headers and trailers.

Low-level support:
- `psw_print_lines` writes a null-terminated array of strings to a `FILE *`.
- `psw_put_procset_name` and `psw_print_procset_name` generate a ProcSet name from device name, language level, and ProcSet version.
- `psw_print_bbox` writes DSC `BoundingBox` and `HiResBoundingBox` comments.
- `is_seekable` uses `fstat(fileno(f))` and `S_ISREG` to determine whether an output `FILE *` can be rewound to patch a placeholder bounding box.

File-level API:
- `psw_begin_file_header` writes `%!PS-Adobe-3.0` or EPS headers, bounding-box comments or placeholders, creator/date/document/language comments, prolog boilerplate, copyright text, ProcSet resource setup, and page-size-setting procedures.
- `psw_end_file_header` closes the prolog/resource setup.
- `psw_end_file` writes the trailer and page count, patches or appends bounding boxes when needed, and writes `%%EOF` for non-EPS output.

Page-level API:
- `psw_write_page_header` writes DSC page setup, begins the ProcSet, sets page size for non-EPS output, creates page save/dictionary state, optionally scales from device pixels to PostScript points, and starts page content with `gsave mark`.
- `psw_write_page_trailer` clears/restores page state, handles copy count, and emits `showpage` or `copypage`.

The only direct filesystem-like behavior is seeking within regular output files to fill fixed-width bounding-box placeholder lines. Otherwise, this is a presentation-format helper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.h

This header declares the shared PostScript-writing utility interface used by bitmap and vector PostScript output devices.

Main type:
- `gx_device_pswrite_common_t` stores `LanguageLevel`, `ProduceEPS`, `ProcSet_version`, and `bbox_position`.
- `PSWRITE_COMMON_PROCSET_VERSION` and `PSWRITE_COMMON_VALUES` provide consistent initializer support.

Declared APIs:
- `psw_print_lines`
- `psw_begin_file_header`
- `psw_end_file_header`
- `psw_end_file`
- `psw_write_page_header`
- `psw_write_page_trailer`

The header documents an important split between `FILE *` and Ghostscript `stream *`: some trailer/finalization operations must work after stream state is unavailable, so the API intentionally keeps file-level operations on `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpx.c

This file implements Ghostscript's HP PCL XL vector output devices:
- `pxlmono`: 8-bit grayscale PCL XL.
- `pxlcolor`: 24-bit RGB PCL XL.

`gx_device_pclxl` extends `gx_device_vector_common` with selected media state, `ManualFeed` and `%MediaSource` handling, current fill/clip rules, cached PCL XL color space/palette state, buffered path points, a downloaded bitmap-character cache, and a flag recording whether the bitmap font is selected.

Open/page/close flow:
- `pclxl_open_device` opens a sequential vector output file, initializes vector procedures and page state, writes the PCL XL/PJL file header, and initializes the bitmap-character cache.
- `pclxl_beginpage` writes page orientation, media size/source selection, and `BeginPage`, mapping `ManualFeed` and `%MediaSource` into PCL XL media source values.
- `pclxl_output_page` emits `EndPage`, flushes, resets page state, and completes Ghostscript page output.
- `pclxl_close_device` writes a pending `EndPage` if needed, emits the PCL XL trailer, and closes the vector file.

Color and paint handling:
- `pclxl_set_color_space` and `pclxl_set_color_palette` suppress redundant color-space/palette emissions.
- `pclxl_set_color` emits gray, RGB, null brush, or null pen source commands.
- `pclxl_can_handle_color_space` rejects ICCBased, Separation, Pattern, and procedure-backed Indexed spaces.
- `pclxl_set_paints` synchronizes brush/pen nulling and fill-rule state before painting paths.

Vector path handling:
- `pclxl_vector_procs` supplies callbacks for line width, caps, joins, miter limit, dash, logical operation, fill/stroke colors, rectangles, and path construction.
- `pclxl_flush_points` batches line and Bezier points in `NUM_POINTS` buffers, choosing compact relative byte, signed-byte, or signed-16-bit point-list encodings before emitting `LinePath`, `LineRelPath`, `BezierPath`, or `BezierRelPath`.
- `pclxl_endpath` emits paint and/or clip operations, including even-odd vs nonzero winding updates.

Images and masks:
- `pclxl_copy_mono`, `pclxl_copy_color`, and `pclxl_fill_mask` emit PCL XL images for direct or indexed raster data.
- `pclxl_write_image_data` tries RunLengthEncode compression for image blocks, falling back to uncompressed data if allocation fails or compression does not fit the temporary buffer.
- High-level `pclxl_begin_image` accepts only chunky, byte-aligned, orthogonal portrait images with 1, 4, or 8 bits per pixel; unsupported cases fall back to Ghostscript default image handling.
- `pclxl_image_plane_data` buffers rows into strips, and `pclxl_image_end_image` flushes final rows and frees buffers.

Bitmap font optimization:
- Monochrome masks with stable `gx_bitmap_id` can be downloaded as bitmap font characters.
- `pclxl_define_bitmap_font`, `pclxl_define_bitmap_char`, and `pclxl_copy_text_char` define and reuse cached glyph bitmaps as PCL XL text, avoiding repeated image emission for small reused masks.
- The cache uses open addressing plus FIFO eviction with caps for character count, total bytes, and per-character byte size.

Parameters:
- `pclxl_get_params` exposes `ManualFeed`.
- `pclxl_put_params` reads `ManualFeed` and `%MediaSource`, delegates standard vector parameters, and records which page/media inputs were explicitly set.

Notable incomplete areas:
- `pclxl_strip_copy_rop` is marked work-in-progress and returns success without emitting general RasterOp output.
- Some comments mark vector-device memory integration as "WRONG", reflecting this Ghostscript vintage.
- High-level color handling through `pclxl_can_handle_hl_color` always returns false.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxat.h

This header defines PCL XL attribute IDs as `px_attribute_t`. The numeric values are protocol identifiers that the driver writes directly to output streams.

Covered attribute groups include:
- Color and palette data: `pxaPaletteDepth`, `pxaColorSpace`, `pxaRGBColor`, `pxaGrayLevel`, and `pxaPaletteData`.
- Page and media controls: `pxaMediaSize`, `pxaMediaSource`, `pxaMediaType`, `pxaOrientation`, `pxaPageCopies`, simplex/duplex fields, and destination fields.
- Path and drawing state: `pxaBoundingBox`, `pxaEndPoint`, `pxaFillMode`, `pxaLineCapStyle`, `pxaLineJoinStyle`, `pxaMiterLength`, `pxaLineDashStyle`, `pxaPenWidth`, `pxaClipRegion`, and `pxaClipMode`.
- Raster/image fields: `pxaColorDepth`, `pxaColorMapping`, `pxaCompressMode`, `pxaDestinationSize`, `pxaSourceHeight`, `pxaSourceWidth`, `pxaStartLine`, `pxaBlockByteLength`, and `pxaNumberOfScanLines`.
- Data/session fields: `pxaCommentData`, `pxaDataOrg`, `pxaMeasure`, `pxaSourceType`, `pxaUnitsPerMeasure`, stream fields, and error reporting.
- Font/text fields: `pxaCharAngle`, `pxaCharCode`, `pxaCharDataSize`, `pxaCharSize`, `pxaFontHeaderLength`, `pxaFontName`, `pxaFontFormat`, `pxaSymbolSet`, `pxaTextData`, writing mode, spacing data, and bold value.

Comments identify attributes introduced in later PCL XL versions. This is a protocol vocabulary header for `gdevpx.c` and `gdevpxut.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxen.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxen.h

This header defines PCL XL enumerated attribute values. The values are written directly into the PCL XL stream, so enum numeric layout is part of the protocol contract.

Major enum groups:
- Geometry and drawing: arc direction, clip/fill mode, clip region, line cap, line join, pattern persistence, source transparency, and paint transparency.
- Color/image: color depth, color mapping, color space, compression mode, color treatment, halftone, trapping, and neutral-axis values.
- Data encoding: byte order/data organization, data source, and numeric data type.
- Page/media: measure units, media destination, media size, media source, media type, orientation, simplex/duplex modes, and duplex side.
- Text/font: character substitution and writing mode.
- Error reporting and device behavior.

Important macros:
- `pxeLineCap_to_library` maps PCL XL cap styles to Ghostscript line-cap values.
- `pxeLineJoin_to_library` maps PCL XL join styles to Ghostscript line-join values.
- `pxeMeasure_to_points` maps measure units to point conversion factors.
- `px_enumerate_media(m)` enumerates known paper sizes with size codes and width/height dimensions; `gdevpxut.c` uses this to match device dimensions to media-size codes.

This is protocol vocabulary, not executable logic, but it directly controls emitted PCL XL values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxop.h

This header defines PCL XL operator and data tag byte values in `px_tag_t`. The enum covers the full one-byte tag space, including placeholders for unassigned values, so byte positions remain protocol-stable.

Covered tag families include:
- Session/page/data-source operators such as `pxtBeginSession`, `pxtEndSession`, `pxtBeginPage`, `pxtEndPage`, `pxtOpenDataSource`, and `pxtCloseDataSource`.
- Font and downloaded-character operators such as `pxtBeginFontHeader`, `pxtReadFontHeader`, `pxtBeginChar`, `pxtReadChar`, `pxtEndChar`, `pxtRemoveFont`, and `pxtSetFont`.
- Graphics-state operators such as `pxtPushGS`, `pxtPopGS`, clipping, cursor, color space, halftone, fill mode, line state, ROP, and transparency mode.
- Path and painting operators such as `pxtLinePath`, `pxtBezierPath`, `pxtRectangle`, `pxtText`, and related relative/list forms.
- Raster/image operators such as `pxtBeginImage`, `pxtReadImage`, `pxtEndImage`, raster pattern operators, and scan operators.
- Data type tags for unsigned/signed integers, real values, arrays, xy pairs, boxes, attribute tags, and data-length markers.

The driver writes these values directly as bytes; this header is the low-level opcode table for `gdevpx.c` and `gdevpxut.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.c

This file provides low-level PCL XL generation helpers used by the `gdevpx.c` driver.

High-level constructs:
- `px_write_file_header` writes the PJL prologue, selects grayscale or color render mode, enters PCL XL, writes session setup, writes device resolution, sets inch measure units, enables back-channel/error-page reporting, selects little-endian data organization, and opens the data source.
- `px_write_page_header` currently emits portrait orientation.
- `px_write_select_media` matches device width/height in inches against `px_enumerate_media` with a 5/72 inch tolerance, emits `MediaSize` and `MediaSource`, and returns the selected media code through `pms`.
- `px_write_file_trailer` emits `CloseDataSource`, `EndSession`, and PJL reset bytes. It takes `FILE *` because close/finalization may occur after stream teardown.

Low-level writers:
- `px_put_bytes` writes raw bytes to a Ghostscript stream.
- `px_put_a` and `px_put_ac` write attributes and attribute-plus-operator pairs.
- `px_put_ub`, `px_put_uba`, `px_put_us`, `px_put_usa`, and `px_put_u` emit compact unsigned values.
- `px_put_s`, `px_put_usp`, `px_put_usq_fixed`, `px_put_ss`, `px_put_ssp`, and `px_put_l` emit little-endian scalar, point, box, signed, and long values.
- `px_put_r` converts a floating-point value to single-precision IEEE-style bytes in little-endian order; `px_put_rl` adds the real32 tag.
- `px_put_data_length` chooses byte or long data-length tags.

The file centralizes the PCL XL endian assumption used by the driver: HP printers on this path only support little-endian data, so all numeric helpers emit low-byte-first operands.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.h

This header declares PCL XL generation utilities and compact operand macros. It requires the PCL XL attribute, enum, and operator headers.

Declared high-level API:
- `px_write_file_header`
- `px_write_page_header`
- `px_write_select_media`
- `px_write_file_trailer`

Declared low-level API:
- `px_put_bytes`
- `px_put_a`, `px_put_ac`
- `px_put_ub`, `px_put_uba`
- `px_put_s`, `px_put_us`, `px_put_usa`, `px_put_u`
- `px_put_usp`, `px_put_usq_fixed`
- `px_put_ss`, `px_put_ssp`
- `px_put_l`
- `px_put_r`, `px_put_rl`
- `px_put_data_length`

Macros such as `PX_PUT_LIT`, `DA`, `DUB`, `DS`, `DUS`, and `DUSP` support static byte arrays containing typed PCL XL operands and attributes. The header documents the key encoding rule used throughout the driver: emitted data is little-endian because HP printers only support little-endian data in this path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxut.h -->