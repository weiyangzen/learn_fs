# Group Research: group_112_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevpsf2_c_sources_7c8020506237

Scope checked against `Docs/research_subset_a.md`: this group is within `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf2.c

This file writes embedded CFF fonts containing either Type 1 or Type 2 charstrings, including ordinary Type 1/Type 2 fonts and CIDFontType 0 fonts. It is part of Ghostscript's PostScript/PDF font-output layer, not a filesystem implementation, but it uses Ghostscript streams as a binary serialization layer.

The central state is `cff_writer_t`, which carries output options, target stream, source base font, glyph-data callback, active CFF offset size, string tables, and font bounding box. `cff_string_table_t` implements a small open-addressed string table used to map CFF strings to SIDs, first checking the standard CFF string set and then entering private strings.

Important functionality:
- Encodes CFF integer, real, boolean, operator, offset, INDEX, string, and charstring structures.
- Converts Type 1 charstrings to Type 2 when `WRITE_TYPE2_CHARSTRINGS` is requested, otherwise copies encrypted or decrypted charstrings depending on `lenIV` options.
- Writes Top DICT variants for simple fonts, CIDFonts, and FDArray entries.
- Writes Private DICTs, local/global Subrs, Encoding, charset, CID charset, FDSelect, and CharStrings INDEX data.
- Uses `psf_get_type1_glyphs`, `psf_check_outline_glyphs`, and glyph enumerators from sibling utility code to validate and order subsets.
- For simple fonts, glyph ordering is normalized to `.notdef`, encoded glyphs, then unencoded glyphs.
- For CIDFontType 0, `cid0_glyph_data` dispatches CID glyph data through `FDArray` and records the correct subfont for FDSelect.

A major design point is offset convergence. CFF offsets and DICT sizes depend on each other because integer encodings are variable length. The writer first emits to a position-only stream with deliberately large placeholder offsets, recomputes sizes, loops until offsets stabilize, then writes the same content to the actual stream.

Notable constraints and risks:
- Several fixed-size tables are used, especially for CID string items and FD arrays; overflow returns Ghostscript errors such as `limitcheck` or `rangecheck`.
- The code mutates Type 1 private width fields when writing Type 2 charstrings to normalize widths.
- Comments note incomplete behavior: all Subrs are written even for subsets, with a note to optimize later.
- I/O failure is detected via `check_ioerror` on streams, but many helper writes are void-style stream emissions and rely on final checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfm.c

This file writes Ghostscript CMap objects in standard PostScript resource format. It serializes code space ranges, CID mappings, notdef mappings, bfchar/bfrange mappings, font-index switches, and CIDSystemInfo dictionaries.

Key helpers:
- `pput_string_entry` writes a `gs_const_string` with a literal prefix.
- `pput_hex` emits bytes as lowercase hexadecimal.
- `cmap_put_ranges` emits `begincodespacerange` blocks.
- `cmap_put_system_info` emits either `null` or a `Registry`/`Ordering`/`Supplement` dictionary.
- `cmap_put_code_map` enumerates CMap lookup ranges and writes entries in blocks of up to 100, selecting `begincidchar`, `begincidrange`, `beginbfchar`, `beginbfrange`, or notdef equivalents based on key/range and value type.

The public entry point is `psf_write_cmap`. It validates `CMapType`, writes the resource header unless the CMap is a ToUnicode map, writes fixed CMap dictionary fields, emits code-space ranges, emits notdef and normal mappings, then closes the CMap resource.

Important behavior:
- Multi-font CMaps emit `usefont` when the lookup font index changes.
- `font_index_only` can restrict output to one descendant font's mappings and CIDSystemInfo.
- Glyph value mappings call the CMap's `glyph_name` callback and then emit names through the caller-supplied `put_name_chars` function.
- Code-space ranges are buffered in groups of 100 before emission.

This is a serialization utility only. Its main dependencies are Ghostscript CMap enumeration APIs in `gxfcmap.h` and stream/PS string helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsft.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsft.c

This file writes embedded TrueType data from Ghostscript Type 42 and CIDFontType 2 fonts. It can output normal TrueType fonts, stripped TrueType fonts, CIDFontType 2 fonts, and stripped CIDFontType 2 fonts.

Core responsibilities:
- Copy existing TrueType tables through `string_proc`.
- Rebuild `glyf` and `loca` tables from selected glyph outlines.
- Synthesize missing `cmap`, `name`, `OS/2`, `hmtx`/`vmtx`, and `post` tables when requested or needed.
- Sort table-directory records and write a complete sfnt header/table directory.
- Support subset glyph closure by adding composite glyph pieces before writing subsets.

Important helper groups:
- Big-endian table writing: `put_ushort`, `put_ulong`, `put_loca`, `put_u16`, `put_u32`.
- Table copying: `write_range` reads segmented font data safely through `pfont->data.string_proc`.
- Generated cmap support: writes Macintosh format 0 or 6 tables plus Windows format 4 table, with optional private-use bias `0xf000`.
- Metrics: `size_mtx` computes compact metrics table size from glyph metrics; `write_mtx` emits h/v metrics.
- Name/OS2/post: `write_name`, `write_OS_2`, `update_OS_2`, `compute_post`, and `write_post`.

Main implementation is `psf_write_truetype_data`. It:
1. Reads and filters the existing table directory.
2. Extracts `head`, `maxp`, existing table presence, and original table offsets.
3. Enumerates glyphs to compute `glyf` and `loca` sizes.
4. Decides short vs long loca format.
5. Builds generated table-directory entries with placeholder checksum handling.
6. Writes the sfnt header, sorted directory, copied tables, generated glyph/location data, generated support tables, and final `head`.

Public entry points:
- `psf_write_truetype_font`
- `psf_write_truetype_stripped`
- `psf_write_cid2_font`
- `psf_write_cid2_stripped`

Notable constraints and risks:
- Several comments state checksums are not computed for generated tables.
- The subset writer does not trim `maxp`/related metrics tables to the subset, because that would require broader table rewriting.
- `MAX_NUM_TABLES` limits output tables to 40.
- Generated `OS/2` range bits are adjusted for symbolic/private-use biased fonts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfu.c

This file provides shared PostScript/PDF font-writing utilities, mostly around glyph enumeration and subset normalization.

Key enumeration paths:
- `psf_enumerate_list_begin` starts enumeration over an explicit glyph list, a CID range, or the full font.
- `psf_enumerate_bits_begin` starts enumeration over a bit vector of selected CIDs/TT glyphs, a CID range, or the full font.
- `psf_enumerate_glyphs_reset` and `psf_enumerate_glyphs_next` provide the common iteration API.

Subset utilities:
- `psf_add_subset_pieces` appends component glyphs for composite glyphs, ensuring pieces needed by `seac` or composite TrueType glyphs are present.
- `psf_sort_glyphs` sorts glyph IDs and removes duplicates.
- `psf_sorted_glyphs_index_of` and `psf_sorted_glyphs_include` provide binary-search lookup.

Outline validation:
- `psf_check_outline_glyphs` verifies selected glyphs can be represented as outline charstrings and do not depend on unsupported behavior such as PostScript-procedure CharStrings, non-standard OtherSubrs, or CDevProc.
- `psf_get_outline_glyphs` gathers Type 1/Type 2 outline glyph metadata, detects `.notdef`, copies subset lists into owned storage, adds subset pieces, removes undefined glyphs, sorts, and guarantees `.notdef` for subsets.

This file is pure support code for font embedding. It does no direct device or filesystem work beyond participating in serialized output managed elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfx.c

This file converts Type 1 charstrings to unencrypted Type 2 charstrings. It expands Subrs inline and attempts several Type 2 operator optimizations.

Parsing layer:
- `type1_next_init` initializes a Ghostscript Type 1 interpreter state over a glyph data buffer.
- `skip_iv` skips/decrypts initial encrypted charstring bytes according to `lenIV`.
- `type1_next` parses numbers and operators, executes `callsubr`/`return`, handles `div`, blend OtherSubrs, pop suppression, and reports relevant operators to the converter.
- `type1_callsubr` loads local Subr data onto the Type 1 instruction stack.

Hint handling:
- `cv_stem_hint_table` stores horizontal and vertical stem hints, including replacement state.
- `type1_stem1` and `type1_stem3` collect and deduplicate hints, keeping them ordered.
- The converter first scans the charstring to gather all hints and detect whether hint replacement/dotsection handling is needed.
- The second pass emits initial stems and hint masks when active hints change.

Output layer:
- `type2_put_op`, `type2_put_int`, and `type2_put_fixed` encode Type 2 operators and operands.
- `type2_put_stems` emits compact stem hint data.
- `type2_put_hintmask` emits a hintmask operator plus active-hint bits.

Main entry point:
- `psf_convert_type1_to_type2` performs two passes. It handles width normalization, `hsbw`/`sbw`, moveto adjustment, `seac` conversion through Type 2 `endchar` operands, flex OtherSubrs, dotsection replacement, stem replacement, and path operators.

Optimizations:
- Combines repeated `rlineto`, `rrcurveto`, `hlineto`, `vlineto`, `hvcurveto`, and `vhcurveto` patterns.
- Converts eligible curves to `hhcurveto`, `vvcurveto`, `rlinecurve`, or `rcurveline`.
- Delays operator emission while tracking operand-stack depth to avoid overflowing Type 2 stack limits.

Notable limits:
- General unsupported OtherSubrs produce `rangecheck`.
- Subrs are expanded inline rather than preserved.
- The code has explicit comments for unimplemented counter control and possible future curve optimizations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsim.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsim.c

This file implements bitmap-only PostScript output devices:
- `psmono`: 1-bit monochrome Level 1 PostScript.
- `psgray`: 8-bit grayscale using the same Level 1 path.
- `psrgb`: 24-bit RGB Level 2 PostScript.

Shared logic:
- `ps_image_write_headers` writes the DSC file header once per output file using `gdevpsu.c` helpers, computes a page bounding box from printer dimensions/resolution, emits device-specific setup procedures, and writes each page header.

`psmono`/`psgray`:
- Device descriptors are `gs_psmono_device` and `gs_psgray_device`.
- `psmono_setup` defines PostScript procedures for decoding a custom compact run-length/hex image stream.
- `psmono_print_page` reads each scanline with `gdev_prn_get_bits`, detects repeated byte runs of at least 10 bytes, emits repeat-run codes, and sends other bytes via `write_data_run`.
- `write_data_run` writes compact count codes followed by hexadecimal data, optionally inverting bytes for 1-bit output.
- `psmono_close` writes the final DSC trailer through `psw_end_file`.

`psrgb`:
- Device descriptor is `gs_psrgb_device`.
- `psrgb_setup` defines a `rgbimage` PostScript procedure using `ASCII85Decode` and `RunLengthDecode`.
- `psrgb_print_page` builds Ghostscript stream filters `RunLengthEncode -> ASCII85Encode -> file`, writes planar R, G, B data per scanline, then emits the page trailer.
- `psrgb_close` writes the final DSC trailer.

Filesystem relevance is limited to writing printer output through `FILE *` and Ghostscript printer-device abstractions. The file does not implement storage logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.c

This file provides shared utilities for PostScript-writing devices.

Low-level support:
- `psw_print_lines` writes a null-terminated array of strings to a `FILE *`.
- `psw_put_procset_name` and `psw_print_procset_name` generate a ProcSet name from device name, language level, and ProcSet version.
- `psw_print_bbox` writes DSC `BoundingBox` and `HiResBoundingBox` comments.
- `is_seekable` uses `fstat(fileno(f))` and `S_ISREG` to decide whether a `FILE *` can be rewound to patch the bounding box.

File-level API:
- `psw_begin_file_header` writes `%!PS-Adobe-3.0` or EPS header, bounding box placeholder/atend/fixed bbox, creator/date/document data/language comments, prolog, copyright, ProcSet resource, and shared page-size-setting procedures.
- `psw_end_file_header` closes the prolog/resource setup.
- `psw_end_file` writes trailer and page count, patches or appends bounding box if necessary, and writes `%%EOF` for non-EPS output.

Page-level API:
- `psw_write_page_header` writes DSC page setup, begins the ProcSet, sets page size for non-EPS output, creates the page save/dict, optionally scales from device pixels to PostScript points, and starts page content with `gsave mark`.
- `psw_write_page_trailer` clears/restores page state, handles copy count, and emits `showpage` or `copypage`.

The file is an output-format helper. Its only direct filesystem-like behavior is checking whether the output file is seekable and patching fixed-width bounding-box placeholder lines later.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.h

This header declares the shared PostScript-writing utility interface.

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

The header documents an important stream/file split: some operations require `FILE *` rather than Ghostscript `stream *` because they may be called during finalization after stream state is unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpx.c

This file implements Ghostscript's HP PCL XL vector output devices:
- `pxlmono`: 8-bit grayscale PCL XL.
- `pxlcolor`: 24-bit RGB PCL XL.

Device state:
- `gx_device_pclxl` extends `gx_device_vector_common`.
- Tracks selected media, manual feed/media source parameters, fill/clip rules, current color space, cached palette, buffered path points, downloaded bitmap-character cache, and whether the bitmap font is selected.
- The bitmap-character cache uses a small hash table plus FIFO eviction, with limits for count, total bytes, and per-character size.

Open/page/close:
- `pclxl_open_device` opens a sequential vector output file, initializes state, writes the PCL XL/PJL file header, and initializes the character cache.
- `pclxl_beginpage` writes page header, media selection, and `BeginPage`, mapping `ManualFeed` and `%MediaSource` into PCL XL media source.
- `pclxl_output_page` emits `EndPage`, flushes, resets page state, and calls Ghostscript page completion.
- `pclxl_close_device` writes any pending `EndPage`, emits the PCL XL trailer, and closes the vector file.

Color and paint:
- `pclxl_set_color_space` and `pclxl_set_color_palette` avoid redundant color-space/palette emissions.
- `pclxl_set_color` emits gray or RGB brush/pen source, or null brush/pen.
- `pclxl_can_handle_color_space` rejects ICCBased, Separation, and Pattern spaces, and indexed spaces backed by a procedure.

Vector paths:
- Uses `gx_device_vector_procs` with custom line width, line cap/join, miter, dash, logical operation, fill/stroke color, rectangles, and path callbacks.
- Buffers line and Bezier points in `NUM_POINTS` batches.
- `pclxl_flush_points` chooses compact relative byte, signed-byte, or signed-16-bit point list encodings and emits `LinePath`, `LineRelPath`, `BezierPath`, or `BezierRelPath`.
- `pclxl_endpath` emits paint and/or clip operations with winding/even-odd handling.

Images and masks:
- `pclxl_copy_mono`, `pclxl_copy_color`, and `pclxl_fill_mask` emit direct or indexed PCL XL images.
- `pclxl_write_image_data` attempts RunLengthEncode compression for image blocks, falling back to uncompressed data if compression cannot fit the temporary buffer.
- High-level `begin_image` supports only chunky, byte-aligned, orthogonal portrait images with 1/4/8 bits per pixel; unsupported cases fall back to default Ghostscript image handling.
- `pclxl_image_plane_data` buffers rows and writes strips; `pclxl_image_end_image` flushes final rows and frees buffers.

Bitmap font optimization:
- Monochrome masks with stable `gx_bitmap_id` may be downloaded as bitmap font characters.
- `pclxl_define_bitmap_font`, `pclxl_define_bitmap_char`, and `pclxl_copy_text_char` emit font headers/chars and then draw them as text.
- This avoids repeated image emission for reused small bitmaps.

Parameters:
- `pclxl_get_params` exposes `ManualFeed`.
- `pclxl_put_params` reads `ManualFeed` and `%MediaSource`, then delegates standard vector parameters.

Notable incomplete areas:
- `pclxl_strip_copy_rop` is marked work-in-progress and returns success without emitting a general RasterOp.
- Some comments mark memory ownership or device integration as "WRONG", inherited from this Ghostscript vintage.
- High-level color handling always returns false for `pclxl_can_handle_hl_color`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxat.h

This header defines PCL XL attribute IDs as `px_attribute_t`.

It includes attributes for:
- Color and palette data: `pxaPaletteDepth`, `pxaColorSpace`, `pxaRGBColor`, `pxaGrayLevel`, `pxaPaletteData`.
- Page/media controls: `pxaMediaSize`, `pxaMediaSource`, `pxaMediaType`, `pxaOrientation`, `pxaPageCopies`, duplex/simplex fields.
- Path and drawing state: `pxaBoundingBox`, `pxaEndPoint`, `pxaFillMode`, `pxaLineCapStyle`, `pxaLineJoinStyle`, `pxaMiterLength`, `pxaLineDashStyle`, `pxaPenWidth`, `pxaClipRegion`, `pxaClipMode`.
- Raster/image fields: `pxaColorDepth`, `pxaColorMapping`, `pxaCompressMode`, `pxaDestinationSize`, `pxaSourceHeight`, `pxaSourceWidth`, `pxaStartLine`, `pxaBlockByteLength`, `pxaNumberOfScanLines`.
- Data/source/session fields: `pxaCommentData`, `pxaDataOrg`, `pxaMeasure`, `pxaSourceType`, `pxaUnitsPerMeasure`, stream fields, and error reporting.
- Font/text fields: `pxaCharAngle`, `pxaCharCode`, `pxaCharDataSize`, `pxaCharSize`, `pxaFontHeaderLength`, `pxaFontName`, `pxaFontFormat`, `pxaSymbolSet`, `pxaTextData`, writing mode, spacing data, and bold value.

The enum mirrors numeric PCL XL protocol attribute IDs, including comments for version-specific values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxen.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxen.h

This header defines PCL XL enumerated attribute values.

Major enum groups:
- Geometry and drawing: arc direction, clip/fill mode, clip region, line cap, line join, pattern persistence, source/paint transparency.
- Color/image: color depth, color mapping, color space, compression mode, color treatment, halftone/trapping values.
- Data encoding: byte order/data organization, data source, numeric data type.
- Page/media: measure units, media destination, media size, media source, media type, orientation, simplex/duplex modes, duplex side.
- Text/font: character substitution and writing mode.
- Error reporting and device behavior.

Important macros:
- `pxeLineCap_to_library`, `pxeLineJoin_to_library`, and `pxeMeasure_to_points` map protocol values to Ghostscript/library values.
- `px_enumerate_media(m)` enumerates known paper sizes with dimensions and resolution basis. `gdevpxut.c` uses this macro to match device dimensions to PCL XL media size codes.

This is a protocol vocabulary header for `gdevpx.c` and `gdevpxut.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxop.h

This header defines PCL XL operator and data tag byte values in `px_tag_t`.

The enum covers the full byte tag space:
- Session/page/data-source tags such as `pxtBeginSession`, `pxtEndSession`, `pxtBeginPage`, `pxtEndPage`, `pxtOpenDataSource`, and `pxtCloseDataSource`.
- Font and character download operators such as `pxtBeginFontHeader`, `pxtReadFontHeader`, `pxtBeginChar`, `pxtReadChar`, and `pxtSetFont`.
- Graphics state operators such as `pxtPushGS`, `pxtPopGS`, clipping, color space, cursor, halftone, fill mode, line state, ROP, and transparency mode.
- Path construction and painting operators such as `pxtLinePath`, `pxtBezierPath`, `pxtRectangle`, `pxtText`, and related relative/list forms.
- Raster/image operators such as `pxtBeginImage`, `pxtReadImage`, `pxtEndImage`, raster pattern and scan operators.
- Data type tags for unsigned/signed integers, real values, arrays, xy pairs, boxes, attribute tags, and data length markers.

The numeric order is intentionally protocol-defined; the driver writes these enum values directly as bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.c

This file provides low-level PCL XL generation helpers.

High-level constructs:
- `px_write_file_header` writes the PJL prologue, sets render mode to grayscale or color, enters PCL XL, writes session setup, resolution, measure units, error reporting, binary low-byte-first data organization, and opens the data source.
- `px_write_page_header` currently emits portrait orientation.
- `px_write_select_media` matches device width/height in inches against `px_enumerate_media` with a 5/72 inch tolerance, emits `MediaSize` and `MediaSource`, and returns the selected media code.
- `px_write_file_trailer` emits `CloseDataSource`, `EndSession`, and PJL reset.

Low-level writers:
- `px_put_bytes` writes raw bytes.
- `px_put_a`, `px_put_ac` write attributes and attribute+operator combinations.
- `px_put_ub`, `px_put_uba`, `px_put_us`, `px_put_usa`, `px_put_u` emit compact unsigned values.
- `px_put_s`, `px_put_usp`, `px_put_usq_fixed`, `px_put_ss`, `px_put_ssp`, `px_put_l` emit little-endian scalar, point, box, signed, and long values.
- `px_put_r` converts a floating-point value to single-precision IEEE-style bytes in little-endian order; `px_put_rl` adds the real32 tag.
- `px_put_data_length` chooses byte or long data-length tag.

The file assumes HP PCL XL printers support little-endian data and centralizes that encoding assumption for the driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.h

This header declares PCL XL generation utilities and operand macros.

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

Macros such as `PX_PUT_LIT`, `DA`, `DUB`, `DS`, `DUS`, and `DUSP` support compact literal byte arrays containing PCL XL typed operands and attributes.

The header documents the important encoding rule used throughout the PCL XL driver: emitted data is little-endian because HP printers only support little-endian data in this path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxut.h -->