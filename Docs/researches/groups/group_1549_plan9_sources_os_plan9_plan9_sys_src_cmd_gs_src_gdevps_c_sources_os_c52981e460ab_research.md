# Group Research: group_1549_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevps_c_sources_os_c52981e460ab

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevps.c

## Purpose
Implements Ghostscript’s `pswrite` and `epswrite` PostScript-writing vector devices. It converts Ghostscript graphics operations into compact PostScript/EPS output, including document/page structure, paths, colors, masks, bitmaps, high-level images, image caching, and DSC-safe binary data emission.

## Main Structures And Devices
- `gx_device_pswrite`: extends `gx_device_psdf_common` with PostScript writer parameters, page state, an image binary writer, fixed-size image cache, deferred page-fill tracking, and compact path state.
- `gs_pswrite_device`: normal PostScript writer device.
- `gs_epswrite_device`: EPS writer with `ProduceEPS` enabled.
- `psw_path_state_t`: tracks compact path/polygon output and operand-stack limits.
- `psw_image_params_t`: stores cached bitmap id, bit width, and height.

## Key Behavior
- Defines PostScript ProcSet fragments for compact color, path, rectangle, clipping, image, ASCII85/hex, and CCITT Fax operators.
- Emits file/page headers and trailers through `psw_begin_file`, `psw_write_page_header`, `psw_write_page_trailer`, and `psw_end_file`.
- Supports separate-page output filenames by closing and reopening the vector output stream per page.
- Defers initial erasepage-like rectangle fills until page content begins, preserving transfer-function behavior.
- Emits compact path syntax by rounding coordinates to two decimals, batching line deltas, using shortcuts for repeated/reversed deltas, and flushing before operand-stack assumptions are exceeded.
- Implements `fill_rectangle`, `copy_mono`, `copy_color`, `fill_path`, `stroke_path`, `fill_mask`, and high-level image enumeration.
- Writes image data through psdf binary writer filters, choosing ASCIIHex/ASCII85/binary and bracketing binary data with DSC `%%BeginData` / `%%EndData`.
- Maintains a small open-addressed image cache for reusable small bitmap/image data.
- Falls back to default Ghostscript image handling for unsupported image formats, color spaces, decode arrays, indexed-color cases, and high-level color cases.

## Dependencies
Uses vector-device infrastructure, bbox devices, Ghostscript stream filters, ASCII85/hex encoders, CCITT Fax encoding, `gdevpsdf.h` / `gdevpsdu.c` common psdf utilities, and PostScript header helpers from `gdevpsu.h`.

## Research Notes
This is the concrete PostScript vector writer front end. The risk surface is mostly stream-state correctness and fallback behavior: unsupported high-level color is rejected, some image support is intentionally narrow, and binary images are buffered to compute DSC byte counts before output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsd.c

## Purpose
Implements Photoshop PSD raster export devices with RGB, CMYK, DeviceN, and spot-color support. Despite the `gdevpsd` prefix, this is a printer/raster output device, not the shared PostScript/PDF distiller layer.

## Main Structures And Devices
- `psd_device`: combines common device/printer state, DeviceN parameters, equivalent CMYK spot-color metadata, selected PSD process color model, and disabled-by-default ICC profile fields.
- `gs_psdrgb_device`: RGB PSD export device.
- `gs_psdcmyk_device`: CMYK/DeviceN PSD export device with spot separations.
- `psd_write_ctx`: per-page writer context for dimensions, channel counts, separation/channel mapping, and output file state.

## Key Behavior
- Defines device procedures for open, get/put parameters, print-page output, color mapping, component lookup, color encode/decode, and equivalent spot-color updates.
- Supports `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN` through `ProcessColorModel`.
- Uses DeviceN helpers for separation names, separation order, component lookup, and equivalent CMYK colors.
- Encodes multiple 8-bit components into `gx_color_index` according to active bits-per-component and component count.
- Writes PSD data directly:
  - `8BPS` signature and version,
  - channel count, dimensions, depth, and mode,
  - image resources for channel names,
  - display color metadata for spot channels,
  - resolution resource,
  - raw uncompressed planar image data.
- Converts Ghostscript interleaved printer rows into PSD channel planes; CMYK data is inverted because Photoshop stores channel values additively.
- ICC profile code exists behind `ENABLE_ICC_PROFILE`, but that macro is `0` in this file.

## Dependencies
Uses printer-device infrastructure, DeviceN and separation helpers, equivalent CMYK spot-color logic, color conversion helpers, and optional ICC types.

## Research Notes
`psd_write` checks `fwrite` with `< 0`, but `fwrite` reports write failure through a short item count rather than a negative value, so short writes are not robustly surfaced. The disabled ICC path also contains code that appears to use converted output before calling `lookup`; this is inactive with `ENABLE_ICC_PROFILE == 0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdf.h

## Purpose
Defines the common PostScript/PDF “psdf” output interface: distiller parameters, shared vector-device fields, binary/image stream writer APIs, color-setting helpers, and stubs for unsupported bitmap readback.

## Main Definitions
- `psdf_image_params`: per-image-class settings for filter dictionaries, antialiasing, autofiltering, depth, downsampling, encoding, resolution, and selected stream template.
- `psdf_distiller_params`: full Distiller-like parameter block for page compression, image compression, color conversion, font embedding, and related policy controls.
- `psdf_version`: PostScript/PDF capability levels from Level 1 through LanguageLevel 3.
- `gx_device_psdf_common` / `gx_device_psdf`: common vector-device extension used by pswrite/pdfwrite-like devices.
- `psdf_binary_writer`: filter-chain helper for binary or ASCII-encoded image streams.
- `psdf_set_color_commands_t`: command-name bundle for fill/stroke color operators.

## Key Behavior Exposed
- Provides defaults for general distiller parameters, color/gray/mono image parameters, and font-embedding policy.
- Declares get/put parameter entry points implemented by `gdevpsdp.c`.
- Declares vector output helpers for line state, paths, rectangles, logical operations, and color setting.
- Declares binary stream setup, filter insertion, CCITT/DCT setup, image filter pipelines, compression chooser setup, image-to-mask conversion, and image color conversion.
- Declares unsupported `get_bits` / `get_bits_rectangle` stubs and overprint compositor handling.

## Dependencies
Includes vector device APIs, parameter APIs, stream infrastructure, ASCII85, CCITT Fax, and psdf stream helpers.

## Research Notes
This header is the central contract shared by `gdevps.c`, `gdevpsdu.c`, `gdevpsdi.c`, and `gdevpsdp.c`. It intentionally carries many Distiller parameters that are only partially implemented in the surrounding code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdi.c

## Purpose
Builds image compression, downsampling, bit-depth conversion, and color-conversion filter chains for PostScript/PDF output devices.

## Key Behavior
- Adds pixel resize filters between 1/2/4/12-bit samples and 8-bit samples using stream templates from `gdevpsds.c`.
- Chooses DCT/JPEG parameters heuristically based on whether a 3-component color space behaves like RGB, Lab, or an unknown space.
- Sets up image compression:
  - DCTEncode for suitable 8-bit non-indexed data,
  - CCITTFaxEncode for mono defaults,
  - LZWEncode or FlateEncode depending on version and settings,
  - optional PNG predictor for LanguageLevel 3 lossless streams.
- Implements downsampling filter setup with `Subsample` or `Average`; `Bicubic` is treated as average.
- Computes effective image resolution from image matrix, CTM, and device resolution to decide whether downsampling should apply.
- Supports optional CMYK-to-RGB conversion through `s_C2R_template` when `ConvertCMYKImagesToRGB` is enabled.
- Provides lossless-only filter setup by copying the psdf device and overriding image parameters.
- Creates compression chooser, image-to-mask, and image-color conversion filter chains.

## Dependencies
Uses `gdevpsdf.h`, `gdevpsds.h`, memory device helpers, color-space APIs, DCT/JPEG, CCITT Fax, LZW, RunLength, PNG predictor, and zlib stream templates.

## Research Notes
The filter pipeline is built back-to-front and may mutate `gs_pixel_image_t` metadata such as dimensions, bits per component, image matrix, decode array, and color space. Several comments mark incomplete behavior, including no true antialiasing in downsampling and image-color conversion being a limited/stub conversion path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdp.c

## Purpose
Implements get/put handling for shared Distiller-style PostScript/PDF parameters.

## Key Behavior
- Maps parameter names to `psdf_distiller_params` fields using `gs_param_item_t` tables.
- Defines supported image filter names and minimum psdf versions:
  - color/gray: DCT, Flate, LZW,
  - mono: CCITT Fax, Flate, LZW, RunLength.
- Writes current image parameters, image dictionaries, enum names, profile strings, and font embedding lists.
- Reads and validates image dictionaries immediately by allocating stream state and applying filter-specific parameter setters.
- Handles enum parameters such as `AutoRotatePages`, `Binding`, `DefaultRenderingIntent`, `ColorConversionStrategy`, `TransferFunctionInfo`, `UCRandBGInfo`, `DownsampleType`, and `CannotEmbedFontPolicy`.
- Implements incremental and complete update semantics for `AlwaysEmbed` and `NeverEmbed` using the public, deletion, and complete-list parameter names.
- Honors `LockDistillerParams` by ignoring psdf-specific updates while still allowing standard vector-device parameters.
- Clamps or normalizes image settings such as resolution, downsample threshold, and supported output depths.

## Dependencies
Uses Ghostscript parameter-list APIs, C parameter lists, DCT/CCITT validation hooks, stream templates, vector-device parameter handling, and psdf declarations.

## Research Notes
The top comment notes that `ColorConversionStrategy` behavior is largely not implemented. Parameter validation is stricter than runtime use in some places because dictionaries are checked by constructing actual stream states before accepting them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.c

## Purpose
Implements custom stream filters used by PostScript/PDF image processing.

## Main Stream Families
- Bit-depth conversion: `s_1_8_template`, `s_2_8_template`, `s_4_8_template`, `s_12_8_template`, `s_8_1_template`, `s_8_2_template`, `s_8_4_template`.
- CMYK-to-RGB conversion: `s_C2R_template`.
- Indexed conversion: `s_IE_template`.
- Downsampling: `s_Subsample_template`, `s_Average_template`.
- Compression chooser: `s_compr_chooser_template`.
- Image color/mask conversion: `s__image_colors_template`.

## Key Behavior
- Expands packed 1/2/4/12-bit image samples to 8-bit values and reduces 8-bit samples to packed 1/2/4-bit values.
- Converts 8-bit CMYK samples to RGB using Ghostscript color conversion and imager state.
- Builds an indexed palette on the fly by hashing component tuples into a caller-provided table.
- Implements center-point subsampling and averaging downsampling.
- Samples horizontal gradients and plateaus to heuristically classify image data as photo-like or line-art-like.
- Converts images either to 1-bit masks using `MaskColor` ranges or to device color components through color-space remapping.

## Dependencies
Uses Ghostscript stream cursor infrastructure, memory management, bitmap raster helpers, color conversion, color-space remapping, and device APIs.

## Research Notes
This is stateful cursor-driven streaming code. The apparent `p[1]` / `q[1]` access pattern is consistent with Ghostscript stream cursors, where `ptr` points before the next byte. Some in-code comments mark rough or incomplete behavior, including “WRONG” error returns, heuristic compression choice, and a “fixme” around input pointer handling in image-color conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.h

## Purpose
Declares the custom image-processing stream states and templates implemented in `gdevpsds.c`.

## Main Definitions
- `stream_1248_state`: shared state for 1/2/4/12-bit to 8-bit expansion and 8-bit to 1/2/4-bit reduction.
- `stream_C2R_state`: CMYK-to-RGB conversion state carrying an imager-state pointer.
- `stream_IE_state`: IndexedEncode-like palette construction state with decode array, palette table, hash table, and bit packing state.
- `stream_Downsample_state_common`, `stream_Subsample_state`, `stream_Average_state`: downsampling states for subsample and average filters.
- `stream_compr_chooser_state`: heuristic image classifier state for compression selection.
- `stream_image_colors_state`: color-to-mask or color-space-to-device conversion state.

## Key API
- Declares stream templates for bit-depth conversion, CMYK-to-RGB, indexed conversion, subsampling, averaging, compression choosing, and image color conversion.
- Exposes initialization and setup helpers:
  - `s_1248_init`,
  - `s_C2R_init`,
  - `s_Downsample_size_out`,
  - `s_compr_chooser_set_dimensions`,
  - `s_compr_chooser__get_choice`,
  - `s_image_colors_set_dimensions`,
  - `s_image_colors_set_mask_colors`,
  - `s_image_colors_set_color_space`.

## Dependencies
Includes stream implementation headers and image parameter definitions; forward-declares `gx_device`.

## Research Notes
The header exposes both `s_image_colors_template` and `s__image_colors_template`, while the implementation defines `s__image_colors_template`. The single-underscore declaration appears stale or unused in this source snapshot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdu.c

## Purpose
Provides shared PostScript/PDF writer utilities for vector state emission, color setting, binary data stream setup, DCT/CCITT filter setup, unsupported readback stubs, and overprint compositor handling.

## Key Behavior
- Defines GC descriptors for `gx_device_psdf` and `psdf_binary_writer`.
- Provides standard fill and stroke color command names for PDF/PostScript-like color operators.
- Emits vector graphics state operations:
  - line width, cap, join, miter limit,
  - dash pattern,
  - flatness,
  - rectangles and path operators.
- Implements `psdf_set_color`, including compact gray/RGB/CMYK output and adjustment for the `gx_no_color_index` sentinel collision.
- Implements `psdf_round` and byte-color rounding for compact numeric output.
- Implements `psdf_begin_binary`, optionally wrapping output in ASCII85 when binary output is disabled.
- Adds arbitrary stream filters through `psdf_encode_binary`.
- Builds DCTEncode state through `psdf_DCT_filter`, injecting `Rows`, `Columns`, and `Colors`, allocating JPEG compression data, and ensuring scan-line/user-marker buffer sizing.
- Builds CCITTFaxEncode state through `psdf_CFE_binary`.
- Closes binary filter chains through `psdf_end_binary`.
- Rejects `get_bits` / `get_bits_rectangle` for high-level vector devices.
- Treats overprint compositors as natively supported and otherwise delegates compositor creation to the default device.

## Dependencies
Uses vector-device APIs, stream filter APIs, ASCII85, CCITT Fax, DCT/JPEG, PostScript string writing, and overprint compositor helpers.

## Research Notes
Logical-operation output is effectively ignored except for a comment noting that set-0/set-1 should be detected. Many output functions do not check stream error status locally; callers that require hard I/O error propagation must rely on later stream/file checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf.h

## Purpose
Declares the PostScript/PDF embedded font-writing interface used by Type 1, Type 2/CFF, CIDFont, CMap, TrueType, and stripped-font writers.

## Main Definitions
- `psf_glyph_enum_t`: stack-allocatable glyph enumeration state for list, range, bitmap, CID, and TrueType subset traversal.
- `psf_outline_glyphs_t`: collected outline-glyph subset state, including `.notdef` and optional subset data.
- `glyph_data_proc_t`: callback type for retrieving outline glyph data and the owning Type 1/Type 2 font.
- Write-option flags for Type 1, Type 2/CFF, TrueType, and CID font serialization.

## Key API
- Glyph enumeration:
  - `psf_enumerate_list_begin`,
  - `psf_enumerate_bits_begin`,
  - `psf_enumerate_glyphs_reset`,
  - `psf_enumerate_glyphs_next`.
- Subset helpers:
  - `psf_add_subset_pieces`,
  - `psf_sort_glyphs`,
  - `psf_sorted_glyphs_index_of`,
  - `psf_sorted_glyphs_include`.
- Outline glyph gathering:
  - `psf_check_outline_glyphs`,
  - `psf_get_outline_glyphs`,
  - Type 1-specific adapters from `gdevpsf1.c`.
- Font writers:
  - Type 1,
  - Type 2/CFF,
  - CIDFontType 0,
  - CMap,
  - TrueType/Type 42,
  - CIDFontType 2,
  - stripped TrueType/CID2,
  - Type 1 to Type 2 charstring conversion.

## Dependencies
Uses Ghostscript character code, glyph data, font, stream, CMap, Type 1, Type 42, and CID font types.

## Research Notes
This header is a cross-file contract. In this work item, only the Type 1 adapter/writer implementation is included; the Type 2, CMap, TrueType, CID, and conversion implementations are declared here but live in sibling files outside this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf1.c

## Purpose
Implements embedded Type 1 font serialization for PostScript/PDF output.

## Key Behavior
- `psf_type1_glyph_data` adapts Type 1 font glyph callbacks to the generic outline-glyph interface.
- `psf_get_type1_glyphs` gathers selected Type 1 outline glyphs via the shared outline-glyph helper.
- Writes Type 1 font program components:
  - `%!FontType1` header,
  - `FontInfo`,
  - `FontName`,
  - `Encoding`,
  - `FontMatrix`,
  - `UniqueID` / `XUID`,
  - `FontBBox`,
  - main font dictionary values,
  - Private dictionary,
  - Subrs,
  - CharStrings,
  - final `definefont`.
- Handles subset-aware `Encoding` and `CharStrings` emission using sorted subset lookup.
- Writes Private dictionary values through the parameter-printer path and emits Type 1 private arrays such as blue values and stem snap arrays.
- Writes all Subrs even for subsets, with an explicit note that this could be improved.
- Supports eexec wrapping, optional ASCIIHex output, optional 512-zero padding or mark handling, and reports three segment lengths for embedding contexts.
- If source `lenIV < 0` but output requires `lenIV`, encrypts CharStrings with `lenIV = 0`.

## Dependencies
Uses Type 1 font internals, glyph data callbacks, glyph enumeration helpers, PostScript string writing, parameter printer support, eexec and ASCIIHex stream filters, and declarations from `gdevpsf.h`.

## Research Notes
The implementation is serialization-focused and does not allocate/free font data itself beyond temporary glyph collection through shared helpers. Error handling is mostly return-code based, but several stream writes are not immediately checked for stream failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf1.c -->