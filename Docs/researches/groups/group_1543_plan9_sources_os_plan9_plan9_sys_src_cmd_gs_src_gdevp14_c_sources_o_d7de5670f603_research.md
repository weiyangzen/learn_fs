# Group Research: group_1543_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevp14_c_sources_o_d7de5670f603

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.c

This file implements Ghostscript’s PDF 1.4 transparency compositing devices. It is not a filesystem component; it is part of the Plan 9 source tree’s bundled Ghostscript graphics stack. Its role is to provide an intermediate compositing device that can emulate the PDF 1.4 imaging model, including transparency groups, soft masks, blend modes, knockout behavior, and command-list banding support.

The core data model is a stack of `pdf14_buf` buffers owned by `pdf14_ctx`. Each buffer stores pixel planes in planar form: process color components, alpha, optional shape, and optional `alpha_g`. `pdf14_buf_new`, `pdf14_ctx_new`, and corresponding free routines manage buffer allocation, row strides, plane strides, bounding boxes, and GC descriptors. The base buffer is initialized to transparent pixels; group and mask operations push additional buffers.

Transparency group handling is centered on `pdf14_push_transparency_group` and `pdf14_pop_transparency_group`. A pushed group may copy a backdrop unless isolated, tracks shape/alpha/blend mode, and composites back into the saved buffer using `art_pdf_composite_*` helpers. The file explicitly forces knockout groups to isolated groups as a known correctness compromise. Transparency masks are pushed with `pdf14_push_transparency_mask`, saved in `ctx->maskbuf`, and consumed during group pop by applying the mask transfer function to the effective alpha.

The direct device path defines Gray, RGB, and CMYK `pdf14_device` prototypes. `pdf14_open` allocates the compositing context; `pdf14_put_image` flattens the planar alpha buffer over a solid white/black background and emits it to the target device as an image. `pdf14_fill_rectangle`, `pdf14_mark_fill_rectangle`, and `pdf14_mark_fill_rectangle_ko_simple` are the low-level marking paths used after higher-level fills/strokes/images/text are funneled through default Ghostscript rasterization.

A second major section implements PDF 1.4 compositor objects: `gs_create_pdf14trans`, `send_pdf14trans`, `c_pdf14trans_write`, and `c_pdf14trans_read`. These serialize compositor operations into Ghostscript command lists, including push/pop device, begin/end groups, begin/end masks, and parameter updates.

The final section implements the clist-writing compositor device. `pdf14_clist_device` exists because banded rendering needs one compositor in front of the clist writer and another on the clist reader/output side. It tracks blend parameters, keeps the clist writer’s color model synchronized with the PDF 1.4 blending space, forwards most graphics operations, and injects `PDF14_SET_BLEND_PARAMS` operations before fills, strokes, text, and images when state changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.h

This header defines the public/internal structures and entry points for the PDF 1.4 transparency rendering device implemented in `gdevp14.c`.

It declares `pdf14_default_colorspace_t` with `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`, matching the default blending-space choices used by the compositor. The central structure is `pdf14_buf`, a saved-buffer stack node containing group flags (`isolated`, `knockout`), compositing state (`alpha`, `shape`, `blend_mode`), flags for extra planes, rectangle bounds, row/plane strides, total channel/plane counts, image data, optional mask transfer function, and a touched bounding box. Pixel data is explicitly documented as planar: pixel values, alpha, optional shape, optional `alpha_g`.

`pdf14_ctx` owns the current buffer stack, an optional pending mask buffer, allocator, device rectangle, additive/subtractive polarity, and channel count. `pdf14_device` extends `gx_device_forward_common`, adds the active transparency context, current opacity/shape/alpha/blend mode, saved color-mapping callback, and saved clist color info.

The exported functions are `gs_pdf14_device_push`, which installs a PDF 1.4 compositor device over a target device, and `send_pdf14trans`, which creates and sends a PDF 1.4 transparency compositor operation to a device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp14.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp2up.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp2up.c

This file implements `pcx2up`, a test Ghostscript printer device that saves two rendered pages and emits them side-by-side into one PCX output page. It is a graphics/printer-device utility, not a filesystem implementation.

The device extends the generic printer structure with `have_odd_page` and `odd_page`. `pcx2up_open` temporarily changes printer space parameters to force banding and delayed rasterization. It sets a band width large enough for two pages plus spacing, caps band buffer space with `RENDER_BUFFER_SPACE`, calls `gdev_prn_open`, restores the caller-visible space parameters, and clears the odd-page flag.

`pcx2up_print_page` alternates behavior by page parity. On the first page, it saves the rendered page into `odd_page` with `gdev_prn_save_page`. On the second page, it saves the even page, builds two `gx_placed_page` descriptors with horizontal offsets, allocates a temporary printer device cloned from `gs_pcx2up_device`, swaps in the open and print procedures from `gs_pcx256_device`, opens the temporary render device, and calls `gdev_prn_render_pages` to paint both saved pages into the final PCX stream.

Important details: output is hardwired around the `pcx256` backend, the device forces banding to preserve pages for later placement, and cleanup avoids closing the original output file by clearing `prdev->file` before closing the temporary device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevp2up.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpbm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpbm.c

This file implements Ghostscript output devices for PBM, PGM, PPM, PNM, PKM, PKSM, PAM, and Plan 9 bitmap output. It is a file-format printer backend in the bundled Ghostscript tree. The only Plan 9-specific format here is `plan9bm`, which reuses the PBM-style device framework but emits a Plan 9 bitmap header and defaults to 100 dpi.

The shared device type is `gx_device_pbm`, which extends `gx_device_printer` with a magic PNM type byte, optional comment, raw/plain flag, optimization flag, color-usage tracking, planar-buffer choice, and saved alpha/image procedures. Device descriptors are generated by `pbm_prn_device`; exported instances include `gs_pbm_device`, `gs_pbmraw_device`, `gs_pgm_device`, `gs_pgmraw_device`, `gs_pgnm_device`, `gs_ppm_device`, `gs_pnm_device`, `gs_pkm_device`, `gs_pksm_device`, `gs_pam_device`, and `gs_plan9bm_device`.

`ppm_open` opens the printer with optional planar buffering, marks the color model as separable/linear, resets color-use tracking, and installs special mapping/image hooks. `ppm_output_page` resets color-use state after flushed pages. `ppm_get_params` and `ppm_put_params` expose planar buffering and support changing gray/R/G/B value counts, recalculating device depth and color maxima.

The mapping routines track whether output can be reduced. `pgm_map_rgb_color` maps RGB to grayscale and notes non-B/W gray usage. `ppm_map_rgb_color` maps RGB into an old Ghostscript RGB color index and records B/W, gray, or color. `pkm_map_cmyk_color` and `pkm_map_color_rgb` encode/decode CMYK-like packed pixels. `pnm_copy_alpha` and `pnm_begin_typed_image` conservatively mark alpha/image operations as gray or color so optimized PNM output does not choose too narrow a format.

Output is centralized in `pbm_print_page_loop`, which writes format headers and iterates scan lines through row callbacks. For Plan 9 bitmap magic `'9'`, it writes five 11-character decimal fields before raster data. For PAM magic `'7'`, it writes `WIDTH`, `HEIGHT`, `DEPTH`, `MAXVAL`, `TUPLTYPE`, optional comment, and `ENDHDR`.

Row emitters cover raw/plain PBM, PGM, PPM, PAM, faux CMYK-to-RGB PKM, and PKSM separations. Optimized PGM/PPM/PNM output can downgrade color output to PGM or PBM when `uses_color` indicates the page only contains gray or bilevel content. PKSM emits one PBM/PGM stream per component plane using `gx_render_plane_t`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpbm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.c

This file contains shared PC-style color mapping helpers used by EGA/VGA framebuffer and PCX-style devices.

For 4-bit EGA/VGA color, `pc_4bit_map_rgb_color` thresholds each RGB component at half intensity, encodes blue/green/red in bits 0/1/2, and sets the high intensity bit for any non-black color. `pc_4bit_map_color_rgb` decodes those color bits back into full-on/full-off RGB values. The comment notes that Ghostscript’s halftoning expects equal shade counts for each component, so only eight colors are actually used despite the 4-bit code space.

For 8-bit SVGA-style color, `pc_8bit_map_rgb_color` maps RGB into a 6x6x6 color cube, producing 216 usable indices. `pc_8bit_map_color_rgb` decodes those indices using a six-step ramp and maps out-of-range palette entries to black. `pc_write_palette` iterates device color indices, calls the device’s `map_color_rgb`, converts color values to 8-bit components, and writes RGB palette triples to a file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.h

This header declares the shared PC color-mapping interface implemented by `gdevpccm.c`.

It exposes 4-bit EGA/VGA mapping procedures `pc_4bit_map_rgb_color` and `pc_4bit_map_color_rgb`, plus `dci_pc_4bit`, a device color-info macro for three components at four bits with two dither levels per color. It also exposes fixed-palette 8-bit mapping procedures `pc_8bit_map_rgb_color` and `pc_8bit_map_color_rgb`, plus `dci_pc_8bit`, describing three components at eight bits with a 6x6x6 cube. Finally, it declares `pc_write_palette`, used by PCX output to serialize palette entries.

The header requires Ghostscript device definitions from `gxdevice.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.c

This file implements Ghostscript IBM PC EGA/VGA/SVGA16 framebuffer devices. It directly manipulates VGA/EGA graphics registers and frame-buffer memory through helpers declared in `gdevpcfb.h`. It is platform/display-driver code, not filesystem code.

The device prototypes are `gs_ega_device`, `gs_vga_device`, and `gs_svga16_device`, with `svga16` exposing a `DisplayMode` parameter through `svga16_get_params` and `svga16_put_params`. `ega_open` adjusts resolution according to the selected video mode, saves BIOS/display state once, initializes signal handling, sets the graphics mode, and enables all VGA planes. `ega_close` restores the saved state.

Color mapping can be compiled as monochrome, one-bit-per-component, or full 4-bit EGA mapping depending on `ega_bits_of_color`. The active configuration in the header uses `ega_bits_of_color 2`, so it maps through `pc_4bit_map_rgb_color`.

The central raster operation type is `rop_params`, shared with optional assembly routines. The C fallback routines include `cmemsetcol`, `cmemsetrect`, `cmemrwcol`, `cmemrwcol0`, and `cmemrwcol2`, which write columns/rectangles and shifted source data into planar VGA memory.

Drawing primitives include `ega_write_dot`, `ega_copy_mono`, `ega_copy_color`, `ega_fill_rectangle`, and `ega_tile_rectangle`. `ega_copy_mono` contains detailed case analysis for black, white, transparent, and arbitrary EGA colors. It chooses VGA logical functions, set/reset maps, masks, and sometimes two passes to implement transparent source or nontrivial color combinations. `ega_copy_color` copies 4-bit pixel data into planar memory by selecting bit masks and using VGA latches. `ega_tile_rectangle` has an optimized path for byte-aligned monochrome tiles with opaque colors and falls back to Ghostscript’s default tiler for harder cases.

`ega_get_bits` reads four VGA planes back into a chunky 4-bit-per-pixel row using a lookup table. Fill helpers `fill_rectangle` and `fill_row_only` optimize masked byte/column writes and special black/white one-row cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.h

This header defines the IBM PC framebuffer interface for the EGA/VGA Ghostscript devices.

It declares device procedures for opening, closing, filling rectangles, tiling, copying mono/color data, and reading scan lines. `pcfb_bios_state` records display mode, text page, cursor mode, font, text attribute, and border color so `gdevpcfb.c` can restore text mode after graphics use. The platform hooks `pcfb_set_signals`, `pcfb_get_state`, `pcfb_set_mode`, and `pcfb_set_state` are declared here.

`gx_device_ega` extends `gx_device_common` with framebuffer raster, segmented-address multipliers, and video mode. The `mk_fb_ptr` macro computes framebuffer addresses either through segmented DOS-style pointers or, on Unix/Linux/SVR4-like builds, through a flat `fb_addr`.

The `ega_device` macro builds device descriptors with screen dimensions, computed DPI, color-component counts, depth, dither levels, raster, addressing multipliers, and video mode. The header also defines VGA/EGA register ports and indices: sequencer map mask, graphics set/reset, function, read plane, mode, bit mask, and frame-buffer base `0xa000`.

For Unix-like builds, the header supplies inline GCC assembly for `outportb` and `outport2`; for DOS, it uses `dos_.h` port I/O. The `byte_discard` macro intentionally reads volatile framebuffer bytes to trigger VGA latch behavior and prevent compiler removal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.c

This file provides shared utility routines for PCL-based Ghostscript printer drivers.

`gdev_pcl_paper_size` computes a PCL paper-size code from the device width, height, and resolution. It chooses the smallest standard size whose width and height are at least the requested page size, prioritizing close width matches because many printers center paper in the tray. It supports Executive, Letter, Legal, Ledger, A-series, JIS B sizes, Japanese postcards, Monarch, COM10, DL, C5, and B5.

The color helpers implement a 3-bit RGB plane model used by PaintJet/DeskJet-style devices. `gdev_pcl_3bit_map_rgb_color` takes the high bit of each RGB component, packs R/G/B into three bits, and complements the result because the buffering convention uses zero as white. `gdev_pcl_3bit_map_color_rgb` reverses this encoding.

The compression helpers implement multiple PCL raster compression modes. `gdev_pcl_mode2compress_padded` and `gdev_pcl_mode2compress` implement PackBits-like run/literal compression for DeskJet/LaserJet IIp output, with an optional padding behavior that preserves trailing zeros. `gdev_pcl_mode3compress` implements LaserJet III delta compression by comparing the current row to a mutable previous row and emitting changed spans with offsets. `gdev_pcl_mode9compress` implements a 2D DeskJet compression mode using unchanged-row skips, uncompressed dissimilar spans, and run-length encoded similar spans. These functions operate at byte/word row level and return compressed byte counts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.h

This header exposes common definitions for PCL printer drivers.

It defines PCL paper-size numeric constants for Executive, Letter, Legal, Ledger, A0-A4, JIS B4/B5, Japanese postcards, Monarch, COM10, DL, C5, and B5. It declares `gdev_pcl_paper_size`, the helper that selects one of those codes from a Ghostscript device’s size and resolution.

It also declares 3-bit RGB printer color mapping procedures, `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`, and the row-compression entry points for PCL modes 2, 3, and 9. The header aliases `word` to `ulong` for mode 2 compression input.

The file depends on `gdevprn.h` for printer-device and Ghostscript type definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcx.c

This file implements Ghostscript PCX output devices. It provides monochrome, grayscale, EGA/VGA 16-color, 256-color fixed-palette, 24-bit, and 4-bit CMYK PCX variants.

Device descriptors include `gs_pcxmono_device`, `gs_pcxgray_device`, `gs_pcx16_device`, `gs_pcx256_device`, `gs_pcx24b_device`, and `gs_pcxcmyk_device`. Most use `prn_color_procs`; the CMYK variant provides explicit CMYK mapping through `cmyk_1bit_map_*`. Shared PC color helpers from `gdevpccm.c` are used for EGA/VGA and 8-bit palette modes.

The file defines the 128-byte PCX header layout in `pcx_header`, including manufacturer, version, RLE encoding flag, bits-per-pixel per plane, extents, resolution, 16-color palette, number of planes, bytes-per-line, and palette interpretation. `assign_ushort` handles the little-endian PCX header fields across host endian variants. A DCX header format is documented but not implemented.

Each print routine prepares a header and delegates to `pcx_write_page`: `pcxmono_print_page` writes a bilevel palette, `pcx16_print_page` writes an EGA palette and planar data, `pcx256_print_page` writes an 8-bit image followed by a 256-entry palette, `pcx24b_print_page` writes three 8-bit planes, and `pcxcmyk_print_page` writes a custom CMYK palette.

`pcx_write_page` fills header fields, writes the header, then iterates printer rows through `gdev_prn_get_bits`. Non-planar data is padded to even byte length and RLE encoded directly. Planar depth 4 data is split into four bit planes; depth 24 data is emitted as separate R/G/B planes. `pcx_write_rle` performs PCX run-length encoding, limiting runs to 15 bytes for compatibility with fragile readers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdf.c

This file is the main Ghostscript PDF-writing driver. It defines the `pdfwrite` and `ps2write` device prototypes through repeated inclusion of `gdevpdfb.h` with different macros, then implements device open, output-page, close, PDF object initialization, page state reset, encryption setup, color model switching, and final PDF assembly.

The file starts with GC descriptors for `gx_device_pdf`, page arrays, and substream-save structures. It enumerates and relocates device-owned pointers, resource chains, outline action pointers, parameter strings, constant strings, and the base `st_device_psdf` fields.

Temporary-file handling is central. `pdf_open_temp_file` and `pdf_open_temp_stream` create scratch files/streams for xref, asides, streams, and pictures. `pdf_close_temp_file` flushes and frees stream state, closes the file, and unlinks the scratch path. `pdf_close_files` closes all temporary storage paths.

`pdf_initialize_ids` initializes object numbering, creates named Catalog and Info dictionaries, stores default `/Producer`, sets creation/modification dates, and allocates the Pages tree. `pdf_compute_fileID` hashes timing, output filename, and Info dictionary contents to create a document ID. `pdf_compute_encryption_data` implements Standard Security Handler setup for revisions 2 and 3 with MD5 and RC4, validates PDF/X and compatibility constraints, computes owner/user keys, permissions, and encryption key material.

`pdf_set_process_color_model` switches device color info and mapping procedures among DeviceGray, DeviceRGB, DeviceCMYK, and DeviceN-as-CMYK. It updates separable/linear component masks and encode/decode procedures.

`pdf_open` creates temporary storage, opens the vector output file, initializes vector state, named-object dictionaries, IDs, file ID, optional encryption, text data, substream stack, page array, resource chains, outlines, articles, destinations, page labels, and per-page graphics/text state. `pdf_reset_page` restores per-page state, resets graphics, text-page tracking, procsets, patterns, and clipping.

Page lifecycle is handled by `pdf_output_page` and `pdf_close_page`. Closing a page ensures the document is open, closes contents, records media box, contents ID, copy count, resources, text data, dominant rotation, DSC-derived page info, and then resets state. `pdf_write_page` later emits the actual `/Page` object with `/MediaBox`, optional `/TrimBox`, `/Rotate`, `/Parent`, `/Group`, resources, annotations, contents, and extra pdfmark-inserted dictionary entries.

`pdf_close` completes the document: it ensures at least one page exists, writes all page objects, writes/free resource objects, builds the `/Pages` tree, closes outlines/articles/destinations/page labels, writes the Catalog, writes named objects, copies aside resources into the main stream, writes the encryption dictionary if needed, emits the xref table and trailer with `/ID`, frees resource records and named objects, closes vector filters, warns on pdfmark destinations beyond the last page, and closes temporary files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.c

This file implements low-level bitmap and image handling for the Ghostscript PDF-writing driver. It turns Ghostscript raster operations into PDF image XObjects, inline images, image masks, CharProc bitmaps, and tiling pattern resources.

`pdf_make_bitmap_image` fills width, height, and image matrix for bitmap-derived images. `pdf_copy_mask_data` writes 1-bit mask data either inline or as a reusable resource, with special row ordering for pattern images. It initializes an image mask, chooses inline output based on `MaxInlineImageSize`, optionally reuses an XObject by Ghostscript bitmap ID, sets up lossless filters, copies mask bits, and finalizes the image writer.

`pdf_copy_mono` is the main monochrome/mask path. It updates clipping when needed and distinguishes transparent masks, inverse masks, solid bilevel images, and two-color indexed images. If a mask has a bitmap ID and no source offset, it treats it as a possible character bitmap: it looks for an existing `resourceCharProc`, or creates a CharProc in an embedded font with appropriate metrics and CCITTFax encoding. Otherwise it emits inline or XObject images and may call `pdf_do_image` or `pdf_do_char_image` to paint the resulting resource. The public device wrapper is `gdev_pdf_copy_mono`.

`pdf_copy_color_data` handles color bitmap data. It creates a Device color space matching bytes per pixel, chooses inline vs XObject emission, reuses XObjects by bitmap ID, writes image matrix, configures lossless or image filters depending on pattern/shading context and size, copies color bits, and finalizes the writer. `gdev_pdf_copy_color` opens a page stream, clears clipping, delegates to `pdf_copy_color_data`, and paints the resulting resource if needed.

`gdev_pdf_fill_mask` maps 1-bit pure-color masks into `pdf_copy_mono`; unsupported masks fall back to Ghostscript default filling. `gdev_pdf_strip_tile_rectangle` optimizes bitmap strip tiles into PDF tiling patterns. It only handles reusable, unshifted tiles where the tile is large enough and `color0` is transparent. It creates colored or uncolored pattern color spaces, optionally creates an image XObject for the tile, builds a Pattern resource with image drawing commands or inline image content, marks it written, and fills the requested rectangle using `/Pattern` color. If constraints fail, it falls back to `gx_default_strip_tile_rectangle`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.c -->