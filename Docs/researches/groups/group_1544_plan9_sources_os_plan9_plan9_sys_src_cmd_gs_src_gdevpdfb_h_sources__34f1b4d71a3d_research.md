# Group Research: group_1544_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevpdfb_h_sources__34f1b4d71a3d

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.h

Ghostscript `pdfwrite`/`ps2write` device body template. This header is intentionally included with caller-defined macros to instantiate concrete PDF-like vector devices.

Key contents:
- Defines a `const gx_device_pdf PDF_DEVICE_IDENT` initializer using the macro-supplied device name, identifier, inline-image threshold, and OPDF-read flag.
- Wires the PDF device procedure table to open/close/page output, parameters, rectangle/path/stroke/mask/image/text/compositor/transparency/pattern/color-space entry points.
- Initializes PDF writer defaults for compatibility level, page selection, optimization, DSC/EPS behavior, font compression, encryption, PDF/X, clipping/shading/image limits, resource tables, object IDs, outlines, named objects, graphics-state stacks, substreams, and image-mask state.
- Sets `MaxClipPathSize` to `12000`, with a comment noting a LaserJet compatibility failure at `14000`.

Research notes:
- This is a static device initializer rather than executable logic.
- It is not guarded by include macros because repeated inclusion is part of the design.
- This is Ghostscript PDF output infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.c

Ghostscript `pdfwrite` color-space management. It maps Ghostscript/PostScript color spaces into PDF color-space names, arrays, resource objects, and ProcSet flags.

Key behavior:
- Detects CIE spaces that can be represented directly as `/CalGray`, `/CalRGB`, or `/Lab`.
- Provides `pdf_cspace_init_Device` for DeviceGray/RGB/CMYK initialization by component count.
- Emits `/Separation` and `/DeviceN` color spaces with colorant names, alternate spaces, and scaled tint functions.
- Emits `/Indexed` spaces, including procedure-derived palettes, PostScript string encoding, PDF 1.2 restrictions, and RGB-to-gray palette optimization.
- Serializes Ghostscript color spaces with `cs_serialize` and deduplicates matching `resourceColorSpace` resources by serialized bytes.
- `pdf_color_space_named` handles Device, Pattern, CIEICC, CIEA, CIEABC, CIEDEF, CIEDEFG, Indexed, DeviceN, and Separation cases.
- Falls back from unsupported ICC or older-PDF ICC paths to alternate spaces when possible.
- Creates cached Pattern color-space resources and sets image ProcSet bits for gray/indexed/color images.

Research notes:
- General CIEBased spaces are not native PDF spaces. This file recognizes direct calibrated/Lab subsets and delegates broader ICC/Lab conversion to `gdevpdfk.c`.
- Most non-parameterless spaces become named PDF resources so they can be reused and registered in resource dictionaries.
- Some unsupported older compatibility-level cases return `rangecheck`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.h

Private cross-file interface for PDF color-space writing, focused on CIE, Lab, and ICCBased conversion.

Key contents:
- Defines `cie_cache_one_step_t` with `ONE_STEP_NOT`, `ONE_STEP_LMN`, and `ONE_STEP_ABC`.
- Exports `pdf_finish_cie_space` from `gdevpdfc.c`.
- Declares `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space` from `gdevpdfk.c`.

Research notes:
- This header is a narrow contract between `gdevpdfc.c` and `gdevpdfk.c`.
- The enum identifies simple CIE pipelines that can be represented with TRC/XYZ ICC tables instead of a sampled lookup table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfd.c

Ghostscript `pdfwrite` path drawing implementation. It emits PDF rectangles, fills, strokes, clipping paths, and bitmap fallbacks for older PDF compatibility levels.

Key behavior:
- `gdev_pdf_fill_rectangle` skips the initial white page fill, opens page contents, clears clipping, sets fill color, and emits a rectangle fill.
- Defines `pdf_vector_procs`, adapting generic vector output with PDF-specific line width, high-level colors, rectangle clamping, and path completion behavior.
- Tracks clipping paths by ID and copied path content to avoid redundant clip emission.
- Emits clip paths from clip-path enumeration or path-list elements, including even-odd/nonzero rules.
- Rescales very large coordinates to avoid Acrobat user-coordinate limits.
- `prepare_fill_with_clip` handles empty clips, initial white-fill suppression, page/content opening, graphics-state prep, and clip output.
- Implements `pdf_lcvd_t`, a local converter backed by memory devices and optional masks.
- Converts mask bitmaps into bounded clipping paths so generated path complexity stays under `MaxClipPathSize`.
- `pdf_dump_converted_image` writes converted content as a full image, an imagemask using a pattern color, or an image clipped by a mask-derived path.
- `gdev_pdf_fill_path` handles vector fills, initial viewer-state synchronization, transparency fallback, old-PDF pattern/shading conversion, clipping, flatness, scaling, and fill operators.
- `gdev_pdf_stroke_path` handles clip setup, transparency fallback, nonuniform CTM stroke compensation, degenerate matrix workarounds, stroke clipping, line parameters, and stroke operators.
- `gdev_pdf_fill_rectangle_hl_color` handles high-level-color rectangle fills and delegates to path fill when old-PDF PatternType 2 conversion is needed.

Research notes:
- This file contains several viewer compatibility workarounds for Acrobat coordinate limits, negative line widths, singular CTMs, and old-PDF shading support.
- The local converter is shared with image handling for masked-image and shading fallbacks.
- This is rendering/output code, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.c

Ghostscript `pdfwrite` graphics-state management. It tracks the PDF viewer state implied by emitted content and writes only the needed color and ExtGState changes.

Key behavior:
- Saves/restores viewer graphics state in `pdev->vgstack`, including transfers, alpha, blend mode, halftones, BG/UCR, overprint, smoothness, text knockout, stroke adjustment, colors, line parameters, and dash data.
- Initializes/reset viewer state from Ghostscript imager state and default black colors.
- Writes colors through DeviceGray/RGB/CMYK operators, resource color spaces with `scn`/`SCN`, colored/uncolored patterns, PatternType 2 shadings, or process-color fallback.
- Converts colorant strings into COS names.
- Serializes transfer maps, black generation, and undercolor removal into sampled PDF Functions.
- Recognizes many predefined spot halftone functions; otherwise emits sampled spot functions.
- Writes spot, screen, colorscreen, threshold, threshold2, multiple, and multiple-colorscreen halftones.
- Creates, deduplicates, registers, and emits ExtGState resources with `/R... gs`.
- `pdf_prepare_drawing` updates transparency, alpha, blend mode, halftone, transfer, BG/UCR, halftone phase, overprint mode, smoothness, and text knockout.
- Fill/stroke/image/imagemask wrappers add operation-specific overprint, stroke adjustment, and fill color handling.

Research notes:
- The file is mainly a state-delta engine that avoids re-emitting unchanged graphics-state commands.
- Transparency requires PDF 1.4+; older compatibility levels return `rangecheck` for unrepresentable alpha/mask/transparency stack state.
- PDF/X suppresses some preservation paths such as halftone and transfer emission.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.h

Internal graphics interface header for the Ghostscript `pdfwrite` driver. It gathers declarations shared by color-space, graphics-state, image, pattern, and bitmap-copy modules.

Key contents:
- Defines full and abbreviated PDF color-space name sets.
- Defines `pdf_color_space_t`, a PDF resource subclass carrying range-scaling data plus serialized color-space bytes for deduplication.
- Declares Device-space initialization, generic/named PDF color-space conversion, Pattern color spaces, and image ProcSet updates.
- Declares graphics-state functions for viewer-state copy/reset, initial colors, color setting, drawing preparation, viewer save/restore, ExtGState finalization, and COS-name conversion.
- Defines `pdf_pattern_t` with a `substitute` pointer for deduplicated pattern resources.
- Defines image dictionary name sets and `pdf_image_writer`, including support for up to four alternative writer streams.
- Declares image matrix, XObject, bitmap-copy, filter, compression-choice, and charproc-resource helpers.
- Declares PatternType 1 storage and colored/uncolored/shading pattern color emission hooks.

Research notes:
- This is a private cross-module contract, organized by the implementation file that exports each group.
- The image writer supports primary image data, alternative compression, compression chooser, and optional mask streams.
- It exposes no filesystem interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfi.c

Ghostscript `pdfwrite` high-level image handling. It decides whether images can be emitted directly to PDF, need masks/resources/patterns, or must fall back to the default renderer.

Key behavior:
- Defines `pdf_image_enum`, an image enumerator tracking geometry, rows remaining, bits per pixel, placement matrix, and `pdf_image_writer`.
- Supports ImageType 1, ImageType 3 masked images, ImageType 3x soft-mask images, and ImageType 4 color-key masked images within compatibility constraints.
- Converts some 1-bit ImageType 4 color-key images into Type 1 imagemasks when RasterOp/color conditions allow.
- Falls back for unsupported alpha, subrectangles, formats, zero-size images, components over 8 bits, singular matrices, unsupported color spaces, and unsupported PDF versions.
- Handles NI-named images and keeps the `NI_stack` synchronized even when falling back.
- Chooses inline images only for unnamed default Type 1 images below `MaxInlineImageSize`; otherwise emits XObject resources.
- Computes PDF image matrices from bitmap geometry, inverse image matrices, and current CTM.
- Sets up lossless or image-compression filters, optional alternative compression streams, process-color conversion, and mask extraction streams.
- Writes planar data by flipping planes into chunky rows for each active binary stream.
- Finalizes images by completing/padding data, choosing compression, adding `/Mask` or `/SMask`, drawing XObjects, or saving mask IDs for later use.
- Implements dummy devices for ImageType 3/3x mask/data callbacks.
- Uses image-as-pattern fallback for older PDF levels when masks/patterns must simulate unsupported forms.
- Implements `gdev_pdf_pattern_manage` for pattern accumulation, deduplication/substitution, resource loading, and cache dropping after many substitutions.

Research notes:
- Compatibility branches distinguish PDF 1.2, 1.3, and 1.4 behavior for masks and soft masks.
- The fallback path explicitly notes incomplete cleanup in some failure cases.
- Mask handling is delayed to account for image merging/deduplication.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfj.c

Ghostscript `pdfwrite` image-writing utilities. This file owns image dictionaries, inline/XObject setup, placement matrices, raw bitmap copying, filter output, stream finalization, and alternative compression selection.

Key behavior:
- Defines full and abbreviated image dictionary key sets.
- Implements GC tracing/relocation for `pdf_image_writer`.
- `pdf_put_image_values` writes image mask, dimensions, bits per component, color space, decode arrays, interpolation, and ImageType 4 `/Mask` arrays when supported.
- `pdf_put_image_filters` transfers active image filter settings through common PDF filter output.
- `pdf_make_bitmap_matrix` and `pdf_put_image_matrix` create top-to-bottom PDF image matrices, adjusted for short image data.
- `pdf_do_image_by_id` and `pdf_do_image` emit XObject `Do` calls and register XObject use for charprocs.
- `pdf_begin_write_image` creates inline streams or XObject image resources, handles named image dictionaries, and initializes binary writers.
- `pdf_make_alt_stream` creates an extra stream for alternative compression trials.
- `pdf_begin_image_data` writes dictionary values and filter dictionaries for each active writer stream.
- `pdf_complete_image_data` pads incomplete DCT/PNG streams with neutral bytes before close.
- `pdf_end_image_binary` closes binary streams, chooses compression when needed, and corrects `/Height` for short data.
- `pdf_end_write_image` writes inline `BI`/`ID`/`EI` images or registers XObject resources, handles NI dictionary merging, disables encryption for inline image bytes, and supports resource substitution.
- `pdf_copy_mask_bits` and `pdf_copy_color_bits` copy raw monobit and device-pixel rows.
- `pdf_choose_compression` compares Flate and alternative streams, discards the loser, and rewires the winning stream into the image resource.

Research notes:
- Inline image bytes are written with `KeyLength` temporarily set to zero so they are not encrypted.
- The alternative compression path assumes stream roles for Flate, DCT/other, and chooser streams.
- Named images from NI pdfmarks are merged into the real image stream object.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfk.c

Ghostscript `pdfwrite` Lab and ICCBased color-space writer. It copies existing ICC profiles and synthesizes ICC profiles for CIEBased spaces that cannot be represented directly as PDF Cal/Lab spaces.

Key behavior:
- Adds `/Range` arrays to CIE-derived dictionaries, optionally clamping to ICC-compatible `[0,1]`.
- Uses Ghostscript CIE-to-XYZ concretization for Lab range discovery and ICC lookup-table generation.
- Provides XYZ-to-Lab helpers and `pdf_put_lab_color_space`.
- Keeps arbitrary CIE-to-Lab conversion disabled, returning `rangecheck`.
- `pdf_make_iccbased` constructs a PDF `/ICCBased` array and stream dictionary with `/N`, optional `/Range`, and optional `/Alternate`.
- `pdf_iccbased_color_space` copies an existing ICC profile stream from a Ghostscript CIEICC space into PDF.
- Synthesizes ICC profiles manually because the available ICC library requires random access to output streams.
- Emits ICC headers, table directories, description, white point, copyright, TRC/XYZ tables, or sampled `A2B0` mft2 lookup tables.
- Uses TRC plus XYZ tables for simple one-step CIEBasedABC cases; otherwise samples a multidimensional A2B lookup table into XYZ output.
- Returns range-scaling information for CIE inputs outside `[0,1]` so callers can adjust image Decode values.
- `pdf_convert_cie_space` chooses Lab conversion for PDF < 1.3 and synthesized ICCBased conversion for PDF 1.3+.

Research notes:
- Synthesized ICC profiles are small ad hoc profiles with required tags and fixed metadata.
- The A2B lookup limits total CLUT entries with `MAX_CLUT_ENTRIES`.
- For PDF 1.2 or earlier, general CIE conversion remains effectively unsupported because Lab conversion immediately returns `rangecheck`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfk.c -->