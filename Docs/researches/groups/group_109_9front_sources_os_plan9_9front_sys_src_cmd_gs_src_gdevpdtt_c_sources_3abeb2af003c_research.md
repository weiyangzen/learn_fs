# Group Research: group_109_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevpdtt_c_sources_3abeb2af003c

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.c

Text-processing implementation for Ghostscript `pdfwrite`. It owns the PDF text enumerator, bridges Ghostscript text enumeration to PDF font resources, and decides when source text can remain PDF text versus falling back to default rendering or Type 3 charproc accumulation.

Key behavior:
- Defines the `pdf_text_enum_t` GC descriptor and text enum procedures: resync, width-only checks, current-width forwarding, cache/setcachedevice handling, retry, release, and main `pdf_text_process`.
- `gdev_pdf_text_begin` tracks dominant page text rotation, rejects unsupported charpath/no-current-point cases into default text handling, and sets up special Type 3 behavior while charprocs are being accumulated.
- Maintains a font-resource cache keyed by Ghostscript font id, with glyph usage bitsets, real-width arrays, attach/lookup helpers, and font-finalization callbacks. `pdf_free_font_cache` currently only drops the top-level pointer and has a FIXME about releasing elements.
- Normalizes original font matrices for Type 1, TrueType, CID, composite, and Type 3 fonts via `pdf_font_orig_matrix` and `font_orig_scale`.
- Selects compatible font resources by checking encoding compatibility, copied-font glyph-copy ability, CIDSystemInfo compatibility, Type 0 parent reuse, standard/base-14 reuse, embedding eligibility, PDF version limits, CFF availability, and OPDFRead constraints.
- Builds `pdf_char_glyph_pairs_t` tables for all chars/glyphs and not-yet-used glyphs so resource creation can test compatibility before writing text.
- Supports both encoded text and glyphshow-style unencoded text; unencoded glyphs are translated through a usable known PostScript encoding when possible.
- Marks used glyphs into cached bitsets after resource selection.
- Computes PDF text state from current point, CTM, font matrix, PDF resolution scaling, font size, spacing operations, paint/render mode, and PDF text-state values.
- Writes stroke state before text state when text rendering uses strokes because stroke synchronization may leave PDF text mode.
- `pdf_glyph_widths` obtains copied-font widths and original-font real widths, handles MissingWidth defaults, vertical metrics, CID v-vector compatibility, and CDevProc metric callouts.
- `pdf_text_process` dispatches to `process_plain_text`, `process_cid_text`, `process_cmap_text`, or `process_composite_text`, using a small aligned stack buffer and heap allocation for larger strings.
- Type 3 handling is staged: normal PDF text processing runs until a missing glyph requires interpreter rendering, default processing calls BuildChar/BuildGlyph, `setcachedevice` records charproc attributes, the charproc is accumulated, and the glyph is processed again once widths/resources are known.
- CDevProc handling returns `TEXT_PROCESS_CDEVPROC`, lets the interpreter compute metrics, then restarts using `cdevproc_result`.

Notable dependencies:
- Text/font-resource headers: `gdevpdtx.h`, `gdevpdtd.h`, `gdevpdtf.h`, `gdevpdts.h`, `gdevpdtt.h`, `gdevpdti.h`.
- Ghostscript font/text internals: `gxfont.h`, `gxfont0.h`, `gxfcid.h`, `gxfcopy.h`, `gxfcmap.h`, `gxchar.h`, `gxstate.h`.
- PDF graphics helpers: `gdevpdfx.h`, `gdevpdfg.h`.

Research notes:
- This is PDF text/font infrastructure inside imported Ghostscript code, not filesystem code.
- Comments document many Acrobat compatibility constraints and historical Ghostscript bugs around Type 1 matrices, TrueType embedding, Type 3 clipping, and CDevProc metrics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.h

Internal pdfwrite text-processing interface shared by `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.

Key behavior:
- Documents the six coordinate systems used by pdfwrite text handling: PostScript user space, device space, PDF user space, font design space, PDF unscaled text space, and PDF text space.
- Defines `pdf_char_glyph_pairs_t`, a variable-length character/glyph collection used for all chars and not-yet-used glyphs.
- Defines `pdf_text_enum_t`, extending Ghostscript text enumeration with a fallback/default enumerator, origin, charproc accumulation flags, CDevProc result storage, and char/glyph pair table.
- Defines stack-only `pdf_text_process_state_t` for derived PDF text state values and current font.
- Defines `pdf_glyph_width_t` and `pdf_glyph_widths_t` for width values, real rendering widths, vertical origin shifts, and replaced-v-vector state.
- Declares process entry signatures and shared helpers for font matrix calculation, encoding compatibility, font resource lookup/creation, CID/Type 0 resources, Type 3 resources, text-state sync, glyph widths, default fallback, font-type tests, Type 3 scaling, ToUnicode mapping, glyph encoding, and current-point shifts.

Research notes:
- The coordinate-system comment is essential context for the matrix math in `gdevpdtt.c`.
- This header is the boundary between text enumeration, font-resource management, and downstream plain/composite text processors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.c

Generated glyph-class data for pdfwrite font emission.

Key behavior:
- Defines `const unsigned char gs_c_pdf_glyph_type[]`.
- Stores glyph attributes for every glyph up to `GS_C_PDF_MAX_GOOD_GLYPH`.
- Packs attributes four glyphs per byte, least-significant bits first.
- Generated mechanically from Ghostscript encoding sources by `toolbin/encs2c.ps`.
- Used by `gdevpdtw.c` when deciding whether simple-font glyph mappings are safe enough to omit a ToUnicode CMap.

Research notes:
- This file is almost entirely generated numeric data, not executable logic.
- The companion header defines the maximum glyph id and bit masks used to interpret the table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.h

Header for the generated pdfwrite glyph-attribute table.

Key behavior:
- Defines `GS_C_PDF_MAX_GOOD_GLYPH` as `21894`.
- Defines `GS_C_PDF_GOOD_GLYPH_MASK` and `GS_C_PDF_GOOD_NON_SYMBOL_MASK`.
- Declares `extern const unsigned char gs_c_pdf_glyph_type[]`.

Research notes:
- Used by font-writing code to interpret `gdevpdtv.c`.
- Supports ToUnicode omission decisions for simple fonts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.c

Font and CMap resource writer for pdfwrite text output. This is the serialization stage for PDF font dictionaries, widths, encodings, ToUnicode resources, CID metadata, CIDToGID maps, descriptors, and CMap streams.

Key behavior:
- Writes simple-font `/FirstChar`, `/LastChar`, and `/Widths` arrays with rounded PDF numbers.
- Detects encoding differences against a base encoding and emits `/Encoding` dictionaries with `/BaseEncoding` and `/Differences`.
- Uses `gs_c_pdf_glyph_type[]` and masks from `gdevpdtv.h` to decide whether simple fonts need ToUnicode CMaps.
- Handles Type 3 compatibility behavior by forcing differences for used chars when needed.
- Writes Type 0 font dictionaries with `/Encoding`, `/DescendantFonts`, and `/Subtype/Type0`.
- Finishes Type 3 dictionaries by writing FontBBox, Widths, and `/Subtype/Type3`.
- Writes standard/simple Type 1 and TrueType dictionaries, including widths for non-standard simple fonts.
- Computes CIDFont default widths by histogramming used glyph widths, then writes `/DW`, `/W`, `/DW2`, and `/W2`.
- Writes CIDFontType0 and CIDFontType2 common content, including optional `/CIDSystemInfo`.
- For CIDFontType2, detects non-identity `/CIDToGIDMap`, emits a compressed binary stream, and writes two-byte GID entries.
- `pdf_write_font_resource` computes/writes ToUnicode resources as required, opens the font object, writes BaseFont, FontDescriptor, ToUnicode, Type/Name, OPDFRead global marker, and delegates to the per-font write proc.
- `pdf_close_text_document` finalizes text resources in order: clean standard fonts, free font cache, write CharProcs, finish descriptors/embedded fonts, write CIDFonts, write Fonts, write FontDescriptors, then bitmap-font Encoding.
- Writes CIDSystemInfo dictionaries, encrypting Registry and Ordering strings when object encryption is active.
- `pdf_write_cmap` creates compressed CMap streams, fills COS dictionary metadata for non-ToUnicode CMaps, and delegates CMap body writing to `psf_write_cmap`.

Research notes:
- This file serializes resources selected by the text/font layers; it does not choose font resources itself.
- It is tightly coupled to PDF compatibility and Acrobat historical behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.h

Private font and CMap resource-writing API for pdfwrite.

Key behavior:
- Declares font content writers matching `pdf_font_write_contents_proc_t`: Type 0, Type 3 finish, standard, simple, CIDFontType0, and CIDFontType2.
- Declares encoding helpers for finding differing encoding indexes and writing encoding objects/references.
- Forward-declares `gs_cid_system_info_t` and `gs_cmap_t`.
- Declares CIDSystemInfo and CMap writing functions.

Research notes:
- Comments state these procedures are intended to be called only from `gdevpdtf.c`.
- This is the public edge of `gdevpdtw.c`; most implementation detail remains private.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtx.h

Shared pdfwrite text/font implementation definitions.

Key behavior:
- Includes `gdevpdt.h`.
- Documents the layering of pdfwrite text code: text processing, font resources, font descriptors, base fonts, and bitmap font processing.
- Forward-declares opaque text/font state components: `pdf_bitmap_fonts_t`, `pdf_outline_fonts_t`, and `pdf_text_state_t`.
- Defines `pdf_text_data_s`, grouping outline font data, bitmap font data, and text-state data.
- Provides the GC descriptor macro for `pdf_text_data_t`.
- Forward-declares `pdf_font_resource_t`.
- Declares `pdf_font_id` and `pdf_used_charproc_resources`.

Research notes:
- This is a small architectural header; its layer comment maps the `gdevpdt*` text/font subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpe.c

Ghostscript display driver for the Reflection Technology “Private Eye” display.

Key behavior:
- Defines `gx_device_pe`, extending `gx_device_common` with a framebuffer address and register base.
- Registers a device named `pe` with fixed geometry `720x280`, byte raster `90`, and default resolution `160x96`.
- Uses default framebuffer address `0xb8000000` and register base `0x3d0`, overrideable with `PEFBADDR` and `PEREGS`.
- `pe_open` parses environment overrides and writes initialization register/value pairs with `outportb`.
- `pe_close` writes restore register/value pairs and clears 4000 bytes of framebuffer memory.
- `pe_fill_rectangle` clips rectangles and sets or clears bits in the 1-bit framebuffer with first/last-byte masks.
- `pe_copy_mono` copies monochrome bitmap data into the framebuffer, handling aligned and skewed source/destination bit offsets, no-color behavior, inversion, and partial-byte masking.

Research notes:
- This is a hardware/display driver, not pdfwrite code and not filesystem code.
- It assumes direct port I/O and memory-mapped framebuffer access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevperm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevperm.c

Ghostscript printer test device that permutes color components to exercise DeviceN and component-assumption paths.

Key behavior:
- Defines a `permute` printer device that normally behaves like CMYK contone output and emits binary PPM (`P6`).
- With `Permute=1`, changes the internal model to DeviceN with six components arranged as yellow, cyan, cyan2, magenta, zero, black, then converts back to RGB for output.
- Supports `Mode=0` for CMYK-like behavior and `Mode=1` for CMY behavior.
- `perm_print_page` reads rendered component data, optionally unpermutes components, converts CMYK/CMY to RGB, and writes PPM rows.
- Provides gray/RGB/CMYK color mapping procs for both modes, with optional permutation through `perm_permute_cm`.
- Implements component-name lookup against active colorant names.
- Implements generic 8-bit-per-component `encode_color` and `decode_color`.
- `perm_get_params` writes `Permute`, `Mode`, and, when permuting, `SeparationColorNames`.
- `perm_set_color_model` switches color model metadata, component count, depth, polarity, and colorant names.
- `perm_put_params` reads and validates parameters, updates color model, delegates printer parameter handling, and restores old color info on failure.

Research notes:
- This is explicitly a regression-test device for DeviceN/color-cleanliness paths.
- It is useful for finding code that assumes only DeviceGray, DeviceRGB, or DeviceCMYK.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevperm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevphex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevphex.c

Ghostscript printer driver for Epson Stylus Color Photo / Photo EX / Photo 700 class printers using ESC/P Raster.

Key behavior:
- Defines the `photoex` device with CMYK internal pixels, default `720x720` dpi, margins, and options for depletion, shingling, render method, splash, leakage, black inhibition, light ink levels, and dot size.
- Supports only `360x360`, `720x720`, and `1440x720`; other resolutions return `rangecheck`.
- Implements RGB-to-CMYK mapping with a hardcoded ink transfer curve, black extraction, hue-angle color compensation table, and empirical constants.
- Implements reverse device-color-to-RGB mapping for Ghostscript color queries.
- Handles device parameters: `Depletion`, `Shingling`, `Render`, `Splash`, `Leakage`, `Binhibit`, and `DotSize`.
- `photoex_print_page` validates resolution and width, allocates a large render context, initializes ESC/P Raster printer state, sets units/page/margins/dot size, renders the page, ejects, resets, and frees memory.
- `RenderPage` drives the print pipeline: schedule nozzle lines, render/halftone needed scanlines, compute active byte ranges per color, move the print head, select ink, send ESC/P raster headers, RLE-compress each nozzle row, and write data.
- `RenderLine` skips expensive halftoning for long blank runs while respecting halftoner restart thresholds.
- The scheduler handles leading, middle, and trailing page regions; it supports 720 dpi microweave and 1440 dpi two-phase horizontal weaving via precomputed start tables and band sizes.
- `PackLine` converts halftoned byte-per-pixel results into 1-bit packed raw device lines and records first/last active bytes.
- `RleCompress` and `RleFlush` implement ESC/P Raster run-length encoding for empty, repeated, and literal byte runs.
- ESC/P helpers emit reset, margins, paper length, graphics mode, unit, unidirectional mode, microweave, ink amount, vertical/horizontal movement, ink selection, raster header, and raw strings.
- Halftoning is abstracted through a function table with Floyd-Steinberg error diffusion, ordered clustered dither, and experimental Bendor error diffusion.
- `HalftoneLine` renders black first, optionally uses black output to inhibit color inks, handles light cyan/light magenta levels, and packs normal and 1440-phase raw lines for six device inks.
- Floyd-Steinberg uses a one-line error buffer and the classic 7/16, 3/16, 5/16, 1/16 diffusion pattern.
- Ordered dither uses a 16x16 threshold matrix.
- Bendor error diffusion uses two error lines, splash compensation, and leakage-style error reduction; the implementation assigns `leakage` from `splash`, matching the source as read.

Research notes:
- The top-of-file comments document protocol assumptions, limitations, scheduling/weaving theory, color transformation, halftoning, compression, and known missing features.
- Shingling and depletion options exist structurally but are marked not implemented.
- This is printer/protocol logic, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevphex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpipe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpipe.c

Ghostscript `%pipe%` IODevice implementation.

Key behavior:
- Defines `gs_iodev_pipe` with device name `%pipe%` and type `Special`.
- Disables most filesystem-like operations: delete, rename, status, enumeration, params, and direct device open.
- `pipe_fopen` rejects access modes containing `+` because pipes are not positionable even if some platforms accept such modes.
- Opens the named command with `popen`, mapping `errno` to Ghostscript file errors on failure.
- Copies the resolved name into `rfname` when provided.
- `pipe_fclose` closes the pipe with `pclose`.

Research notes:
- This is an IODevice bridge to OS pipes; it is the only file in this group with direct process/pipe behavior.
- It does not implement general filesystem semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpjet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpjet.c

Ghostscript printer drivers for H-P PaintJet, PaintJet XL, and DEC LJ250 color printers using PCL-style raster output.

Key behavior:
- Defines three devices: `lj250`, `paintjet`, and `pjetxl`, all using 3-bit RGB color mapping via `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`.
- Uses compile-time `X_DPI` and `Y_DPI` of `180`; comments note both axes must match and may be `90` or `180`.
- `lj250_print_page` enters PCL emulation mode, resets raster graphics, delegates to the common page writer, then exits PCL emulation.
- `paintjet_print_page` resets raster graphics and delegates to the common writer.
- `pjetxl_print_page` sends printer reset/init and uses a different vertical origin before delegating.
- `pj_common_print_page` allocates scanline and plane buffers, emits PCL commands for raster resolution, line width, color planes, origin, compression, and raster start.
- For each scan line, it copies rendered data, trims trailing zeros, counts blank lines, and emits vertical movement for skipped blank runs.
- Converts packed 3-bit pixel data into separate R/G/B plane buffers using 8-byte transposition blocks and lookup tables.
- Sends planes in R, G, B order using PCL transfer commands with row compression.
- `compress1_row` implements PaintJet row compression as repeat-count/data-byte pairs and complements bytes because the image is accumulated in complemented form.

Research notes:
- This is legacy printer protocol code, not filesystem code.
- The implementation is compact but depends on Ghostscript printer-device scanline layout and PCL/PaintJet raster conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpjet.c -->