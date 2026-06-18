# Group Research: group_106_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevpdfb_h_sources_c053f112986f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfb.h

Ghostscript `pdfwrite`/`ps2write` device body template. This header is deliberately included multiple times with caller-defined macros to instantiate concrete PDF-like vector devices.

Key contents:
- Defines a `const gx_device_pdf PDF_DEVICE_IDENT` object using `std_device_dci_type_body` and the macro-supplied device name, identity, inline-image limit, and OPDF-read mode.
- Wires the PDF device procedure table to open/close/page output, parameter handling, rectangle/path/stroke/mask/image/text/compositor/transparency/pattern/color-space entry points.
- Initializes `psdf` common defaults, PDF compatibility and page-selection parameters, DSC/EPS handling, optimization flags, character/font options, compression flags, encryption fields, PDF/X/transparency options, clipping/shading/image limits, overprint and transfer identifiers, resource tables, object IDs, page/resource stacks, outline/article/name structures, viewer graphics state, substream state, image-mask state, and other runtime fields.
- Uses `PDF_DEVICE_MaxInlineImageSize` to choose per-device inline image behavior and `PDF_FOR_OPDFREAD` to mark the open-PDF-reader oriented variant.

Notable dependencies:
- Requires surrounding compilation context to define `gx_device_pdf`, `st_device_pdfwrite`, device procedure implementations such as `pdf_open`, `gdev_pdf_fill_path`, `gdev_pdf_begin_typed_image`, and the `psdf_initial_values` macro.
- Assumes macros such as `PDF_DEVICE_NAME`, `PDF_DEVICE_IDENT`, `PDF_DEVICE_MaxInlineImageSize`, and `PDF_FOR_OPDFREAD` are defined before inclusion.

Research notes:
- This is not a conventional guarded header; the leading comment explicitly permits repeated inclusion in a single C file.
- It is a large static initializer rather than executable logic, so behavior comes from the procedure pointers and from the default field values established here.
- The default `MaxClipPathSize` is set to `12000` with a comment noting HP LaserJet 1320 hangs at `14000`.
- This file is Ghostscript PDF output infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.c

Ghostscript `pdfwrite` color-space management and color-space resource emission. It maps Ghostscript/PostScript color spaces into PDF color space names, arrays, resources, and supporting functions.

Key behavior:
- Detects simple CIE cases that PDF can represent as `/CalGray`, `/CalRGB`, or `/Lab`, using cached CIE identity/exponential tests and special Lab-space recognition.
- Provides `pdf_cspace_init_Device` for local DeviceGray/RGB/CMYK color-space initialization based on component count.
- Builds `/Separation` and `/DeviceN` color spaces by writing colorant names, alternate spaces, and scaled tint-transform functions.
- Builds `/Indexed` color spaces, including procedure-derived palettes, PostScript string encoding, PDF 1.2 compatibility restrictions, and a gray-palette optimization for RGB indexed data.
- Serializes Ghostscript color-space objects with `cs_serialize`, deduplicates them against existing `resourceColorSpace` entries by serialized bytes, and stores serialized data in `pdf_color_space_t`.
- `pdf_color_space_named` handles DeviceGray/RGB/CMYK, Pattern, CIEICC, CIEA, CIEABC, CIEDEF, CIEDEFG, Indexed, DeviceN, and Separation cases; parameterized spaces become PDF resources and can be returned by resource name.
- Falls back from unsupported CIEICC or unavailable ICC profiles to alternate color spaces when appropriate.
- Creates cached colored and uncolored Pattern color-space resources through `pdf_cs_Pattern_colored`, `pdf_cs_Pattern_uncolored`, and high-level color-space handling for uncolored patterns.
- Updates PDF ProcSet bits for image color spaces, distinguishing bitmap/gray/indexed/color image usage.

Notable dependencies:
- Ghostscript color-space APIs: `gscspace.h`, `gscdevn.h`, `gscie.h`, `gscindex.h`, `gscsepr.h`, `gxcspace.h`, and `gsicc.h`.
- PDF object/resource helpers from `gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfc.h`, and `gdevpdfo.h`.
- CIE conversion and ICCBased creation are split with `gdevpdfk.c` via `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space`.

Research notes:
- The top comment documents a key design limitation: general CIEBased spaces are not native PDF spaces, so the driver either recognizes direct Cal/Lab subsets or emits ICCBased spaces for PDF 1.3+.
- Lab conversion for arbitrary CIE spaces is intentionally not implemented here; unsupported PDF 1.2-or-earlier CIE conversions return rangecheck through `gdevpdfk.c`.
- `pdf_color_space_named` has several early returns for parameterless Device spaces; most other spaces are resource-backed to allow reuse and resource-dictionary registration.
- Some error paths after allocating serialized color-space bytes return directly without freeing all transient allocations, but the main success path transfers ownership into the `pdf_color_space_t` resource.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.h

Internal cross-file interface for `pdfwrite` color-space writing, focused on CIE, Lab, and ICCBased color-space conversion.

Key contents:
- Defines `cie_cache_one_step_t` with `ONE_STEP_NOT`, `ONE_STEP_LMN`, and `ONE_STEP_ABC` to describe CIEBasedABC spaces that can be represented as one decode/cache step plus a matrix.
- Exports `pdf_finish_cie_space` from `gdevpdfc.c` for finalizing CIE-derived PDF dictionaries with white/black points.
- Declares `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space` from `gdevpdfk.c` for ICCBased copying/synthesis, CIE-to-Lab/ICCBased conversion, and Lab object creation.

Research notes:
- This is a narrow private header between `gdevpdfc.c` and `gdevpdfk.c`; it is not a broad public API.
- The enum is part of an optimization path that lets synthesized ICC profiles use TRC/XYZ tables instead of a sampled A2B lookup table when the CIE pipeline is simple enough.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfd.c

Ghostscript `pdfwrite` path drawing implementation. It emits PDF rectangle, fill, stroke, clipping, and older-PDF shading fallback output from Ghostscript vector drawing calls.

Key behavior:
- `gdev_pdf_fill_rectangle` suppresses the initial white page fill, opens page contents, clears clipping, sets fill color, and emits a PDF `re f` rectangle.
- Defines `pdf_vector_procs`, adapting generic `psdf` vector output with PDF-specific line width normalization, high-level fill/stroke color setting, rectangle clipping/clamping, and path completion.
- Tracks clipping paths by ID and by copied path content to avoid redundant clip emission; restores/saves viewer graphics state with `Q`/`q` when replacing active clips.
- Emits clipping paths from regular clip-path enumeration or from path-list elements, including reverse path-list order and even-odd/nonzero clipping rules.
- `make_rect_scaling` and the fill/stroke paths rescale very large coordinates to stay within Acrobat user-coordinate limits.
- `prepare_fill_with_clip` handles empty clips, skipped initial white fills, page/content opening, graphics-state preparation, and clip emission.
- Implements a local converter device (`pdf_lcvd_t`) backed by memory devices and optional masks for converting unsupported shadings/masked images into image or imagemask output.
- Converts mask bitmaps into clipping paths in bounded subimages so generated clip path complexity stays under `MaxClipPathSize`.
- `pdf_dump_converted_image` writes converted content either as a full image, an imagemask using a pattern color, or an image clipped by a bitmap-derived path.
- `gdev_pdf_fill_path` handles ordinary vector fills, initial graphics-state synchronization hacks, transparency fallback, pattern/shading conversion for PDF 1.2 compatibility, clipping intersections, flatness updates, path scaling, and `f`/`f*` fill operators.
- `gdev_pdf_stroke_path` handles clip setup, transparency fallback, nonuniform CTM stroke compensation, Acrobat matrix edge cases, stroke-bounds intersection with the clip box, line-parameter preparation, and `S`/`s` output.
- `gdev_pdf_fill_rectangle_hl_color` implements high-level-color rectangle filling and delegates to the path fill path when old-PDF pattern2 conversion is needed.

Notable dependencies:
- Ghostscript geometry/path/clip/imager internals: `gxfixed.h`, `gxistate.h`, `gxpaint.h`, `gxcoord.h`, `gzpath.h`, `gzcpath.h`, `gxdevmem.h`.
- PDF graphics/color/image helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.
- Uses `pdf_copy_color_data` from image-writing support to turn memory-device raster content into PDF images.

Research notes:
- This file encodes several PDF viewer compatibility workarounds, especially Acrobat coordinate limits, negative line widths, and singular/degenerate CTM behavior.
- The `pdf_lcvd_t` converter is shared with image handling and is central to compatibility fallback for masked images and shadings that cannot be represented directly.
- Several comments describe intentional hacks required by Ghostscript’s pdfmark/high-level rendering interface, such as empty-path fills for initial state and clipping synchronization.
- This is rendering/output code, not filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.c

Ghostscript `pdfwrite` graphics-state management. It tracks the PDF viewer state that the emitted content stream will produce, writes color and ExtGState changes, and preserves selected imager state such as transfer functions and halftones.

Key behavior:
- Saves/restores viewer graphics state in `pdev->vgstack`, including transfer IDs, alpha, blend mode, halftone/BG/UCR IDs, overprint, smoothness, text knockout, stroke adjustment, colors, line parameters, and dash pattern.
- Initializes and resets PDF viewer state from Ghostscript imager state, including black/white colors and default line/text state.
- Writes high-level client colors through `pdf_reset_color`, supporting direct DeviceGray/RGB/CMYK operators, PDF color-space resources plus `scn`/`SCN`, colored/uncolored patterns, PatternType 2 shadings, and process-color fallback.
- Converts colorant strings to PDF COS names with `pdf_string_to_cos_name`.
- Serializes transfer maps, black generation, and undercolor removal into sampled PDF Functions, with identity detection and special signed-range handling for UCR.
- Recognizes many predefined spot halftone functions by resampling them against Ghostscript halftone orders; otherwise writes sampled spot functions.
- Writes spot, screen, colorscreen, threshold, threshold2, multiple, and multiple-colorscreen halftones as PDF halftone dictionaries or streams.
- Opens and finalizes ExtGState resources, substitutes duplicate resources, registers them in the page resource dictionary, and emits `/R... gs`.
- `pdf_prepare_drawing` updates common state for fill/stroke/image operations: transparency/blend/alpha, halftone, transfer, BG/UCR, halftone phase, overprint mode, smoothness, and text knockout.
- `pdf_prepare_fill`, `pdf_prepare_stroke`, `pdf_prepare_image`, and `pdf_prepare_imagemask` provide operation-specific wrappers, including fill/stroke overprint and stroke-adjust handling.

Notable dependencies:
- Ghostscript state/halftone/function APIs: `gsstate.h`, `gsfunc0.h`, `gxdht.h`, `gxht.h`, `gzht.h`, `gxfmap.h`, `gxdcolor.h`, and `gxpcolor.h`.
- PDF color-space and pattern helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.
- Stream compression support from `szlibx.h` for sampled function streams.

Research notes:
- The file is largely a state-delta engine: it avoids re-emitting color and graphics-state commands when saved IDs and saved high-level colors match current viewer state.
- Transparency is only emitted for PDF 1.4+; earlier compatibility levels return rangecheck when alpha, masks, or transparency stack state cannot be represented.
- PDF/X suppresses some preservation paths such as halftone/transfer emission.
- The `pdf_open_gstate` interrupt convention is used to request stream-context changes before writing `gs` commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.h

Internal graphics interface header for the Ghostscript `pdfwrite` driver. It gathers declarations shared by color-space, graphics-state, image, pattern, and bitmap-copy modules.

Key contents:
- Defines full and abbreviated PDF color-space name sets and the `pdf_color_space_names_t` structure.
- Defines `pdf_color_space_t`, a PDF resource subclass that retains CIE range scaling data plus serialized color-space bytes for deduplication.
- Declares color-space creation functions: Device-space initialization, generic/named PDF color-space conversion, Pattern color spaces, and image ProcSet updates.
- Declares graphics-state functions from `gdevpdfg.c`: viewer-state copy/reset, initial colors, pure/high-level color setting, drawing/fill/stroke/image/imagemask preparation, viewer save/restore, ExtGState finalization, and string-to-COS-name conversion.
- Defines `pdf_pattern_t`, a resource wrapper with a `substitute` pointer for deduplicated pattern resources, and declares `pdf_substitute_pattern`.
- Defines image dictionary name sets, `pdf_image_writer`, its GC descriptor, and image-writing helper declarations used by `gdevpdfi.c`, `gdevpdfj.c`, and bitmap copy paths.
- Declares PatternType 1 parameter storage and colored/uncolored/shading pattern color emission from `gdevpdfv.c`.
- Declares `pdf_copy_color_data`, the bitmap-to-PDF-image helper exported by the bitmap/copy code.

Research notes:
- The header is a cross-module private contract for the PDF-writing device; many declarations are intentionally grouped by the implementation file that exports them.
- `pdf_image_writer_num_alt_streams` is `4`, covering main image data, an alternative compression stream, a compression chooser stream, and optional mask stream.
- The resource descriptors are public/private through Ghostscript GC macros because resource objects need tracing/relocation across modules.
- The file exposes no filesystem interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfi.c

Ghostscript `pdfwrite` high-level image handling. It decides when images can be emitted directly to PDF, when they need masks/resources/patterns, and when to fall back to Ghostscript’s default image rendering.

Key behavior:
- Defines `pdf_image_enum`, a Ghostscript image enumerator that tracks image geometry, rows remaining, bits per pixel, transformation matrix, and a `pdf_image_writer`.
- Supports ImageType 1, ImageType 3 masked images, ImageType 3x soft-mask images, and ImageType 4 color-key masked images under PDF compatibility constraints.
- Converts certain 1-bit ImageType 4 color-key images into ImageType 1 imagemasks when RasterOp and colors permit, avoiding PDF color-key-mask problems.
- Falls back to default rendering for unsupported alpha, subrectangles, formats, zero-size images, components over 8 bits, singular matrices, unsupported color spaces, or unsupported compatibility-level combinations.
- Handles named images from the `NI_stack`, keeping the stack synchronized even when image handling falls back.
- Chooses inline images only for default ImageType 1 cases without names and below `MaxInlineImageSize`; otherwise creates XObject image resources.
- Computes PDF image matrices from bitmap coordinates, inverse image matrices, and current CTM.
- Sets up lossless or image-compression filters, optional alternative compression streams, process-color conversion filters, and optional mask extraction streams.
- Writes planar image data by flipping component planes into chunky row data before writing to each active binary stream.
- Finalizes images by completing data, padding incomplete DCT/PNG streams as needed through `gdevpdfj.c`, choosing compression, attaching `/Mask` or `/SMask`, drawing XObjects, or saving mask IDs for later use.
- Implements ImageType 3/3x dummy devices that route mask/data begin-image calls back into `pdf_begin_typed_image`.
- Uses image-as-pattern fallback for old PDF levels when masks and patterns need to simulate unsupported image forms.
- Implements `gdev_pdf_pattern_manage`, including pattern accumulation, Pattern resource deduplication/substitution, resource loading, and resource-cache dropping after many substituted patterns.

Notable dependencies:
- Ghostscript image APIs: `gximage3.h`, `gximag3x.h`, `gsiparm4.h`, `gsflip.h`, and image enum procedures.
- Drawing/color/pattern interfaces from `gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfo.h`, `gxdcolor.h`, `gxpcolor.h`, and `gxhldevc.h`.
- Shared local converter device functions from `gdevpdfd.c` through `pdf_setup_masked_image_converter`, `pdf_dump_converted_image`, and `pdf_remove_masked_image_converter`.

Research notes:
- The file has multiple compatibility branches keyed on PDF 1.2, 1.3, and 1.4: color-key masks require newer PDF unless converted, and soft masks require PDF 1.4.
- The fallback label notes that cleanup is incomplete in some failure paths: “SHOULD FREE STRUCTURES AND CLEAN UP HERE.”
- Image merging/deduplication affects mask handling, so the code delays adding `/Mask` or `/SMask` until final image completion.
- This is image/PDF output infrastructure rather than filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfj.c

Ghostscript `pdfwrite` image-writing utility implementation. It owns PDF image dictionary fields, image XObject/inline setup, image matrices, raw bitmap copying, filter dictionaries, binary stream finalization, and alternative compression selection.

Key behavior:
- Defines full and short image dictionary key sets, including abbreviated names for inline images.
- Implements GC tracing/relocation for `pdf_image_writer`, including active binary writers, image resources, data streams, named dictionaries, and mask resources.
- `pdf_put_image_values` writes `/ImageMask`, `/Width`, `/Height`, `/BitsPerComponent`, `/ColorSpace`, `/Decode`, `/Interpolate`, and ImageType 4 `/Mask` arrays when supported.
- `pdf_put_image_filters` transfers active filter settings, currently including CCITTFaxDecode parameters through common `pdf_put_filters`.
- `pdf_make_bitmap_matrix` and `pdf_put_image_matrix` create top-to-bottom PDF image placement matrices, adjusting for images that ended before their declared height.
- `pdf_do_image_by_id` and `pdf_do_image` emit image XObject `Do` calls and register image resources for charprocs when needed.
- `pdf_begin_write_image` creates inline COS streams or XObject image resources, handles NI-named image dictionaries, initializes binary writers, and records specified/data image height.
- `pdf_make_alt_stream` creates an additional image stream for alternative compression trials.
- `pdf_begin_image_data` writes image dictionary fields and filter dictionaries for a specific writer stream.
- `pdf_complete_image_data` pads incomplete DCT/PNG image streams with neutral bytes because those encoders cannot safely close with short data.
- `pdf_end_image_binary` closes binary streams or invokes compression selection, then corrects `/Height` if the image data ended early.
- `pdf_end_write_image` writes inline `BI`/`ID`/`EI` images or registers XObject resources, handles named-image dictionary merging, disables encryption for inline image bytes, and supports resource substitution/deduplication.
- `pdf_copy_mask_bits` and `pdf_copy_color_bits` copy raw monobit and device-pixel rows with bit offset/inversion handling.
- `pdf_choose_compression` compares Flate and DCT/alternative streams using a compression chooser and stream lengths, discards the loser, rewires the winning stream into the image resource, and preserves optional mask writer state.

Notable dependencies:
- PDF object/resource helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.
- PS/PDF binary writer and image filter setup from `gdevpsds.h`.
- PNG predictor/filter support from `spngpx.h`.

Research notes:
- Inline image writing explicitly sets `pdev->KeyLength = 0` while writing contents so encryption is disabled for inline image data.
- The alternative-compression path assumes stream roles: primary Flate, secondary DCT/other, and a chooser stream; it also contains heuristics for very large size differences.
- Named images created by NI pdfmarks are handled by moving dictionary entries and replacing the NI object contents with the actual image stream object.
- The code comments warn that substituted images with alternate streams may leave unused bytes in `pdev->streams.strm`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfk.c

Ghostscript `pdfwrite` Lab and ICCBased color-space writer. It copies existing ICC profiles and synthesizes minimal ICC profiles for CIEBased color spaces that cannot be represented directly as PDF Cal/Lab spaces.

Key behavior:
- Adds `/Range` arrays to CIE-derived dictionaries, with optional clamping to ICC-compatible `[0,1]` component ranges.
- Uses Ghostscript CIE-to-XYZ concretization to evaluate arbitrary CIE color spaces for Lab range discovery or ICC lookup-table generation.
- Provides Lab helpers for XYZ-to-Lab conversion and `pdf_put_lab_color_space`; arbitrary CIE-to-Lab conversion is present but intentionally disabled with a rangecheck.
- `pdf_make_iccbased` constructs a PDF `/ICCBased` array and stream dictionary, writes `/N`, optional `/Range`, and optional `/Alternate`, and reports when input scaling is needed.
- `pdf_iccbased_color_space` copies an existing ICC profile stream from a Ghostscript CIEICC color space into a PDF ICCBased stream.
- Builds synthesized ICC profiles by hand because the comment says the available `icclib` requires random access to the output stream.
- Emits ICC header, table directory, description, white-point, copyright, TRC/XYZ tables, or a sampled `A2B0` mft2 lookup table.
- Uses TRC plus XYZ tables for simple CIEBasedABC cases described by `ONE_STEP_ABC` or `ONE_STEP_LMN`; otherwise samples a multidimensional A2B0 lookup table into XYZ output.
- Handles CIE input ranges that exceed `[0,1]` by returning range-scaling information to callers, allowing image Decode values to be adjusted upstream.
- `pdf_convert_cie_space` chooses Lab conversion for PDF < 1.3 and synthesized ICCBased conversion for PDF 1.3+.

Notable dependencies:
- CIE and ICC internals from `gxcspace.h`, `gxcie.h`, and `gsicc.h`.
- Cross-file interfaces from `gdevpdfc.h`, color-space declarations from `gdevpdfg.h`, and object writing from `gdevpdfo.h`.

Research notes:
- The synthesized ICC profile is intentionally small and “adhoc”; it includes required tags and fixed metadata but is constructed directly into the COS stream.
- The A2B lookup table limits total CLUT entries with `MAX_CLUT_ENTRIES` and computes per-axis sample counts based on component count.
- The code includes a subtle ICC-specific normalization note: A2B0 XYZ table values are scaled against `1 + 32767/32768`, not exactly `[0,1]`.
- For PDF 1.2 or earlier, general CIE conversion effectively remains unsupported because `pdf_convert_cie_to_lab` immediately returns rangecheck.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfk.c -->