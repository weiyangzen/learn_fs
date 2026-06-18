# Group Research: group_1547_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevpdtt_c_sources__a6ca9933fc9a

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`, files under the vendored Ghostscript command source tree. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.c

## Role

`gdevpdtt.c` is the main pdfwrite text-processing implementation. It bridges Ghostscript text enumeration to PDF text/font resources, choosing whether text can be represented directly in PDF or must fall back to the default renderer.

## Main Entry Points

- `gdev_pdf_text_begin()` creates `pdf_text_enum_t`, tracks page text rotation, handles stringwidth special cases, and decides whether pdfwrite text handling can start.
- `pdf_text_process()` is the enumerator process function. It dispatches text to CID, CMap/composite, or plain text processors, manages fallback to default rendering, and handles Type 3 charproc accumulation and CDevProc restart behavior.
- `pdf_default_text_begin()` wraps fallback default text processing, forcing real drawing for Type 3 charproc accumulation when needed.

## Font Resource Flow

- `pdf_obtain_font_resource()`, `pdf_obtain_font_resource_unencoded()`, and `pdf_obtain_cidfont_resource()` find or allocate compatible font resources and mark glyph usage.
- `pdf_find_font_resource()` and `pdf_find_type0_font_resource()` search existing resource chains for reusable font resources by type, encoding compatibility, CMap name, descendant font, and copyable glyph outlines.
- `pdf_make_font_resource()` creates standard, simple, CID, TrueType, CFF, or Type 3 font resources, including embed-policy checks and PDF-version/CID-system capability checks.
- `pdf_make_font3_resource()` creates synthesized Type 3 resources with cached glyph state, base encoding, font bbox, and adjusted FontMatrix precision.
- `pdf_attach_font_resource()` stores resource associations in a device font cache and registers font-removal notification callbacks.

## Text And Glyph State

- `pdf_char_glyph_pairs_t` tables are allocated per text run to record all glyph/code pairs and the unused glyphs needing copy or embedding.
- `pdf_make_text_glyphs_table()` scans encoded text through `next_char_glyph`; `pdf_make_text_glyphs_table_unencoded()` rewrites glyphshow data into a compatible known PostScript encoding.
- `pdf_mark_text_glyphs()` and `pdf_mark_text_glyphs_unencoded()` update per-font glyph usage bitmaps.
- `pdf_text_release_cgp()` frees per-enumerator glyph-pair storage.

## Coordinate And Width Handling

- `pdf_font_orig_matrix()` reconstructs the original font matrix, including Type 1/TrueType/CID special cases and heuristics for scaled Type 1 fonts.
- `pdf_update_text_state()` computes PDF text state values from font matrices, the Ghostscript CTM, text current point, spacing deltas, render mode, and selected PDF font.
- `pdf_set_text_process_state()` emits stroke/text state updates, taking care that stroke setup may leave text mode.
- `pdf_glyph_widths()` obtains both copied-font widths for PDF Widths arrays and original-font widths for rendering, including missing-width fallback, vertical metrics, CID v-vector compatibility, and CDevProc callouts.

## Fallback And Type 3 Accumulation

The file has intricate Type 3 behavior. `pdf_text_process()` may render until a glyph cannot be copied, then fall back to default interpretation so BuildChar/BuildGlyph can execute. `pdf_text_set_cache()` captures `setcharwidth` / `setcachedevice` data, starts or cancels charproc resource accumulation, installs clipping needed by the interpreter fallback, and resumes the normal text pass once widths and charproc attributes are known.

## Dependencies

This file depends on Ghostscript text, font, CMap, glyph, matrix, path, graphics-state, resource, PDF output, font descriptor, bitmap font, and high-level device APIs. It calls implementation layers declared in `gdevpdtt.h`, including `process_plain_text()`, `process_cid_text()`, `process_cmap_text()`, and `process_composite_text()`.

## Risks And Invariants

- Correctness depends on preserving the relationship between current font, original font, copied font, glyph usage, and PDF resource encoding.
- Type 3 fallback is intentionally two-pass: first to execute charproc/cache callbacks, second to emit text with known metrics.
- CDevProc handling relies on restarting with `cdevproc_result` rather than requerying font metrics.
- `pdf_free_font_cache()` only nulls the cache root and has a FIXME about releasing elements, so lifetime ownership is external or intentionally leaky at close time.
- Encoding compatibility is conservative and may reject reusable resources if glyph/name mappings conflict.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.h

## Role

`gdevpdtt.h` is the internal interface between pdfwrite text processing files: `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.

## Key Definitions

- Documents six coordinate systems used by pdfwrite text: PostScript user space, device space, PDF user space, font design space, PDF unscaled text space, and PDF text space.
- Defines `pdf_char_glyph_pairs_t`, a variable-length glyph/code table with no pointers.
- Defines `pdf_text_enum_t`, extending Ghostscript text enumeration with fallback enumerator state, origin, Type 3 charproc flags, CDevProc result storage, and glyph-pair collection.
- Defines `pdf_text_process_state_t` for stack-only derived font/text state.
- Defines `pdf_glyph_width_t` and `pdf_glyph_widths_t` for PDF width-array widths and real rendering widths.

## Exported Interfaces

The header declares utilities for font matrices, encoding compatibility, font-resource lookup/allocation, CID/Type 0 resource creation, attached-resource cache access, Type 3 resource creation, text state update, glyph widths, fallback setup, font-kind checks, glyph-to-char encoding, ToUnicode additions, text width modification, and current-point shifting.

## Dependencies

It assumes prior definitions from the pdfwrite text/font stack, especially `gdevpdt.h`, `pdf_font_resource_t`, `pdf_text_state_values_t`, Ghostscript font/text types, and the process-text implementations in sibling files.

## Risks And Invariants

- The coordinate-system comments are operational design documentation; changing text matrix or width code without preserving these mappings risks subtle PDF text placement bugs.
- `pdf_char_glyph_pairs_t` must remain pointer-free because it is variable length and managed as a raw allocation.
- The process procedure signature must remain compatible across `gdevpdtt.c`, `gdevpdtc.c`, and `gdevpdte.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.c

## Role

`gdevpdtv.c` is generated glyph metadata for pdfwrite. It contains `gs_c_pdf_glyph_type[]`, a packed table of glyph attributes for glyph IDs up to `GS_C_PDF_MAX_GOOD_GLYPH`.

## Data Layout

- The table is generated from encoding sources through `toolbin/encs2c.ps`.
- Attributes are packed four glyphs per byte, least-significant bits first.
- Consumers test masks declared in `gdevpdtv.h` to decide whether a glyph is safe enough to omit a ToUnicode CMap.

## Dependencies

`gdevpdtw.c` uses this table in `pdf_simple_font_needs_ToUnicode()` when deciding whether simple fonts need explicit Unicode mapping. The table has no functions and no local includes.

## Risks And Invariants

- This file is mechanically generated data; manual edits would be high risk unless regenerated from the source encoding files.
- The packing convention must match the lookup expression in `gdevpdtw.c`.
- The max glyph constant in the header must remain consistent with the table length and generation inputs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.h

## Role

`gdevpdtv.h` declares the generated glyph-attribute table used by pdfwrite font-resource writing.

## Definitions

- `GS_C_PDF_MAX_GOOD_GLYPH` is `21894`.
- `GS_C_PDF_GOOD_GLYPH_MASK` marks glyphs considered acceptable generally.
- `GS_C_PDF_GOOD_NON_SYMBOL_MASK` marks glyphs acceptable for non-symbol handling.
- `gs_c_pdf_glyph_type[]` is the external packed attribute table defined in `gdevpdtv.c`.

## Dependencies

Included by `gdevpdtw.c`. It has no Ghostscript type dependencies beyond standard C declarations.

## Risks And Invariants

The masks and max glyph value are part of the packed-table contract. Any regeneration of `gdevpdtv.c` must update this header consistently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.c

## Role

`gdevpdtw.c` writes pdfwrite font and CMap resources. It serializes simple fonts, Type 0 fonts, Type 3 fonts, CIDFonts, Encodings, ToUnicode resources, CIDSystemInfo dictionaries, and CMaps.

## Font Writing

- `pdf_write_Widths()` writes `/FirstChar`, `/LastChar`, and `/Widths`.
- `pdf_write_encoding()`, `pdf_write_encoding_ref()`, and `pdf_different_encoding_index()` build Encoding objects and Differences arrays.
- `pdf_write_contents_type0()`, `pdf_finish_write_contents_type3()`, `pdf_write_contents_std()`, `pdf_write_contents_simple()`, `pdf_write_contents_cid0()`, and `pdf_write_contents_cid2()` implement per-font-type resource content writers.
- `pdf_write_contents_cid2()` emits a compressed `/CIDToGIDMap` stream only when the map is non-identity.
- `pdf_write_font_resource()` writes common font dictionary keys: `/BaseFont`, `/FontDescriptor`, `/ToUnicode`, `/Type`, and OPDF `.Global`.

## Width And ToUnicode Decisions

- `pdf_compute_CIDFont_default_widths()` builds a width histogram to choose default CID widths and vertical metrics.
- `pdf_write_CIDFont_widths()` writes `/DW`, `/W`, `/DW2`, and `/W2`, skipping undefined copied-font glyphs but preserving used zero widths.
- `pdf_simple_font_needs_ToUnicode()` uses encoding entries and `gs_c_pdf_glyph_type[]` to determine whether a simple font can safely omit ToUnicode.

## Document Close Flow

`pdf_close_text_document()` cleans standard fonts, drops the font cache, writes charprocs, finishes embedded font descriptors, writes CIDFont and Font resources, writes descriptors, then writes bitmap-font Encoding resources.

## CMap Writing

- `pdf_write_cid_system_info()` writes Registry/Ordering/Supplement, encrypting strings if required.
- `pdf_write_cmap()` creates a data stream, fills CMap dictionary metadata for non-ToUnicode maps, writes the CMap with `psf_write_cmap()`, and ends the stream.

## Dependencies

This file depends on Ghostscript font/CMap APIs, PostScript font writer helpers, PDF object/resource/data-stream code, font descriptor code, bitmap font code, generated glyph attributes from `gdevpdtv.h`, and ARC4 encryption support.

## Risks And Invariants

- Encoding Difference generation must match the selected BaseEncoding and Type 3 compatibility behavior.
- ToUnicode omission depends on the generated glyph table and glyph-name normalization; mistakes affect text extraction/search.
- CID width emission assumes used-glyph bitmaps and width arrays are aligned by CID.
- CMap streams are deliberately not encrypted during temporary-file writing; encryption is handled through the surrounding PDF data path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.h

## Role

`gdevpdtw.h` declares the font and CMap resource writing API for pdfwrite. Its comments state these procedures are intended only for use from `gdevpdtf.c`.

## Exported API

- Font content writers matching `pdf_font_write_contents_proc_t`: Type 0, Type 3 finalization, standard/simple fonts, CIDFontType0, and CIDFontType2.
- Encoding helpers: `pdf_different_encoding_index()`, `pdf_write_encoding()`, and `pdf_write_encoding_ref()`.
- CID/CMap helpers: `pdf_write_cid_system_info()` and `pdf_write_cmap()`.

## Dependencies

The header forward-declares `gs_cid_system_info_t` and `gs_cmap_t`; it requires pdfwrite font/resource types from surrounding includes.

## Risks And Invariants

Callers must pass fully initialized `pdf_font_resource_t` structures whose subtype-specific fields match the writer selected during allocation. The API is intentionally narrow and internal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtx.h

## Role

`gdevpdtx.h` is the shared internal header for pdfwrite text and fonts. It documents the layer split across text processing, font resources, font descriptors, base fonts, and bitmap fonts.

## Key Definitions

- Describes the layer structure: `gdevpdtt.c`, `gdevpdtc.c`, `gdevpdte.c`, `gdevpdts.c`, `gdevpdtf.c`, `gdevpdtw.c`, `gdevpdtd.c`, `gdevpdtb.c`, and bitmap font files.
- Forward-declares opaque `pdf_bitmap_fonts_t`, `pdf_outline_fonts_t`, and `pdf_text_state_t`.
- Defines `pdf_text_data_t`, holding pointers to outline-font, bitmap-font, and text-state subcomponents.
- Provides the GC descriptor macro `private_st_pdf_text_data()`.
- Declares `pdf_font_id()` and `pdf_used_charproc_resources()`.

## Dependencies

Includes `gdevpdt.h` and depends on pdfwrite resource and Ghostscript GC descriptor infrastructure.

## Risks And Invariants

The layering comments are a design contract: higher text layers should not reach around lower font/resource abstractions. The `pdf_text_data_t` GC descriptor must stay synchronized with its pointer fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpe.c

## Role

`gdevpe.c` is the Ghostscript display driver for the Reflection Technology “Private Eye” hardware display.

## Device Model

- Defines `gx_device_pe`, extending `gx_device_common` with a framebuffer address and I/O register base.
- Exposes `gs_pe_device` with fixed geometry `720x280`, 1-bit framebuffer layout, and default framebuffer/register addresses.
- `PEFBADDR` and `PEREGS` environment variables can override hardware addresses.

## Control Flow

- `pe_open()` parses environment overrides and writes the `peinit` register sequence through `outportb()`.
- `pe_close()` restores registers with `pedone` and clears 4000 bytes of framebuffer memory.
- `pe_fill_rectangle()` clips rectangles to the display and sets or clears bits in the framebuffer.
- `pe_copy_mono()` copies 1-bit source bitmaps to the framebuffer with clipping-ish setup, alignment/skew handling, and zero/one color masks.

## Dependencies

Uses low-level hardware I/O (`outportb()`), environment variables, direct memory writes, Ghostscript device procedures, and C runtime parsing/memory functions.

## Risks And Invariants

- This is hardware-specific code that assumes direct access to physical framebuffer memory and VGA-like I/O ports.
- Rectangle loops use `for (; h >= 0; h--)` after computing inclusive bounds; this appears to write one more row than a conventional height loop.
- `pe_copy_mono()` does minimal clipping compared with `pe_fill_rectangle()` and computes destination pointers before fully normalizing negative coordinates.
- Environment parse failures call `exit(1)`, which is unusual for a device open path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevperm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevperm.c

## Role

`gdevperm.c` implements the `permute` printer device, a regression/testing device for DeviceN and unusual color-component layouts.

## Device Behavior

By default it behaves like a CMYK contone printer and outputs PPM. With `Permute=1`, it reports a six-component DeviceN model and stores colors as a permuted tuple roughly `(yellow, cyan, cyan2, magenta, zero, black)`, then converts back to RGB for PPM output.

## Main Functions

- `perm_print_page()` reads rendered component rows, unpermutes CMYK/CMY as needed, converts to RGB, and writes binary PPM.
- `perm_get_color_mapping_procs()` selects mapping tables for mode 0 or mode 1.
- `gray_cs_to_perm_cm_*()`, `rgb_cs_to_perm_cm_*()`, and `cmyk_cs_to_perm_cm_*()` map Ghostscript color spaces to the current permuted color model.
- `perm_get_color_comp_index()` resolves separation colorant names.
- `perm_encode_color()` and `perm_decode_color()` pack/unpack 8-bit components into `gx_color_index`.
- `perm_set_color_model()` switches between DeviceCMYK, DeviceCMY, and DeviceN component lists.
- `perm_get_params()` and `perm_put_params()` expose `Permute`, `Mode`, and separation names.

## Dependencies

Uses Ghostscript printer-device APIs, color conversion helpers from `gxdcconv.h`, parameter-list APIs, and standard PPM output through `FILE`.

## Risks And Invariants

- This is intentionally a test device; output should remain visually comparable across normal/permuted modes.
- `perm_print_page()` allocates `raw_line` and `cooked_line` but does not check allocation failures before use.
- Color model changes must update component count, depth, polarity, colorant names, and Ghostscript printer parameters consistently.
- Duplicate colorant names in DeviceN are intentional and test code paths that assume standard Gray/RGB/CMYK layouts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevperm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevphex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevphex.c

## Role

`gdevphex.c` is a Ghostscript ESC/P Raster printer driver for Epson Color Photo, Photo EX, and Photo 700 devices. It implements color mapping, microweave line scheduling, halftoning, raw device packing, RLE compression, and printer command emission.

## Device And Parameters

- Exposes `gs_photoex_device` named `photoex`.
- Supports `360x360`, `720x720`, and `1440x720` resolutions.
- Device parameters include `Depletion`, `Shingling`, `Render`, `Splash`, `Leakage`, `Binhibit`, and `DotSize`.
- Internal rendered color is CMYK; output device inks are six channels: black, cyan, magenta, yellow, light cyan, and light magenta.

## Color Mapping

- `photoex_map_rgb_color()` maps RGB to CMYK with black extraction, empirical transfer through `xtrans[]`, and hue-based compensation through `ctable[]`.
- `photoex_map_color_rgb()` maps packed CMYK back to RGB for Ghostscript queries, but intentionally is not the inverse transform.
- `Cmy2A()` computes a hue-angle-like value from CMY components for compensation interpolation.

## Page Pipeline

- `photoex_open()` sets margins based on physical printer width constraints, then calls `gdev_prn_open()`.
- `photoex_print_page()` validates resolution, clips printable width, allocates a large `RENDER` state, emits printer setup commands, chooses dot size, disables printer microweave, enables unidirectional mode, calls `RenderPage()`, ejects paper, resets, and frees buffers.
- `RenderPage()` repeatedly schedules head passes, ensures needed lines are halftoned, emits per-color band data, handles delayed vertical movement, horizontal offsets, and RLE output.

## Scheduling

- `SchedulerInit()`, `ScheduleLines()`, `ScheduleLeading()`, `ScheduleMiddle()`, `ScheduleTrailing()`, and `ScheduleBand()` implement line/nozzle assignment for 360, 720, and 1440 dpi.
- `start_720` and `start_1440` tables handle the leading edge of pages.
- The scheduler tracks which lines/phases have already printed with a modulo `MAX_MARK` mark array.

## Halftoning And Packing

- `HalftoneLine()` dispatches each CMYK channel through the selected halftoner, optionally letting black block color deposition, then packs output into raw six-ink bitplanes.
- `FloydSLine()` implements Floyd-Steinberg diffusion.
- `DitherLine()` implements 16x16 ordered dither using `dmatrix`.
- `BendorLine()` implements an experimental larger-kernel error diffusion with splash/leakage controls.
- `PackLine()` converts thresholded byte pixels into 1-bit raw lines and records active byte ranges.

## Printer Encoding

- `RleCompress()` and `RleFlush()` implement ESC/P Raster RLE packets.
- `SendReset()`, `SendMargin()`, `SendPaper()`, `SendGmode()`, `SendUnit()`, `SendUnidir()`, `SendMicro()`, `SendInk()`, `SendDown()`, `SendRight()`, `SendColour()`, and `SendData()` emit low-level ESC/P commands.

## Dependencies

Uses Ghostscript printer APIs, parameter APIs, `FILE` output, math helpers, direct raster access through `gdev_prn_get_bits()`, and static device-specific tables.

## Risks And Invariants

- The file itself notes several limitations: monochrome device incomplete, no TIFF compression, shingling/depletion unimplemented, hardcoded transfer/compensation, and experimental Bendor diffusion.
- Memory demand is high because `RENDER` contains large line caches and error buffers.
- Scheduling correctness depends on the constants for 32 nozzles and 8-line spacing.
- `RleCompress()` contains suspicious pointer/value handling in the repetitive sequence path, making this compression logic a risk area.
- `BendorLine()` assigns `leakage` from `dev->splash`, not `dev->leakage`, which appears inconsistent with the parameter documentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevphex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpipe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpipe.c

## Role

`gdevpipe.c` implements Ghostscript’s `%pipe%` IODevice using `popen()` and `pclose()`.

## API

- Exposes `gs_iodev_pipe` with device name `%pipe%` and category `Special`.
- `pipe_fopen()` rejects access modes containing `+`, opens a process pipe with `popen()`, maps `errno` to Ghostscript errors, and copies the resolved name when requested.
- `pipe_fclose()` closes the pipe with `pclose()`.

## Dependencies

Uses Ghostscript IODevice interfaces, `pipe_.h`, `stdio_.h`, `errno_.h`, string helpers, and Ghostscript error mapping.

## Risks And Invariants

- Pipes are explicitly treated as non-positionable by rejecting read/write update modes.
- The command string is passed directly to `popen()`, so security depends on Ghostscript’s broader `%pipe%` access policy and sandbox settings outside this file.
- `pipe_fclose()` ignores the process exit status from `pclose()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpjet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpjet.c

## Role

`gdevpjet.c` implements Ghostscript printer drivers for HP PaintJet, PaintJet XL, and DEC LJ250 color printers.

## Devices

- `gs_lj250_device`
- `gs_paintjet_device`
- `gs_pjetxl_device`

All use 3-bit PCL color mapping, 8.5x11 defaults, 180 dpi, and a common print routine with device-specific setup/end strings and vertical origin.

## Print Flow

- `lj250_print_page()` enters and exits PCL emulation mode around common printing.
- `paintjet_print_page()` emits PaintJet raster setup and form feed.
- `pjetxl_print_page()` resets the XL and uses a different vertical origin.
- `pj_common_print_page()` allocates scanline and plane buffers, emits PCL raster setup, walks scanlines, skips blank lines by vertical movement, transposes chunky color pixels into RGB planes, compresses each plane row, and writes raster transfer commands.
- `compress1_row()` performs PaintJet run-length compression and complements bytes because the image was accumulated in complemented form.

## Dependencies

Uses Ghostscript printer APIs, PCL color mapping helpers from `gdevpcl.h`, scanline copy/raster helpers, `FILE` output, and Ghostscript memory allocation.

## Risks And Invariants

- `X_DPI` and `Y_DPI` must match and be either 90 or 180 per the source comment.
- `LINE_SIZE` is rounded to an 8-byte multiple because transposition operates in 8-byte blocks.
- Buffer allocation handles partial allocation cleanup.
- Compression worst case can double row size, and the temporary compression buffer is sized accordingly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpjet.c -->