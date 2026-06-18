# Group Research: group_111_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevps_c_sources_o_1f72306d4a61

Scope: `Docs/research_subset_a.md` covers `sources/os/plan9/9front`. This grouped report covers the listed Ghostscript PostScript/PDF/PSD writer source files under `sources/os/plan9/9front/sys/src/cmd/gs/src`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevps.c

## Purpose
Implements the Ghostscript `pswrite` and `epswrite` vector devices. It converts Ghostscript drawing operations into PostScript/EPS output, including file/page structure, path syntax, image emission, simple bitmap caching, and device parameters.

## Main Concepts
- Defines `gx_device_pswrite`, extending `gx_device_psdf_common` with `pswrite_common`, image writer state, an image cache, deferred page fill state, and temporary path compression state.
- Registers two devices: `gs_pswrite_device` and `gs_epswrite_device`.
- Provides the PostScript procset used by generated output, including compact operators for colors, paths, rectangles, clipping, cached image data, ASCIIHex/ASCII85, CCITT Fax, and image/colorimage/imagemask helpers.
- Uses a vector device procedure table to translate high-level vector actions into PostScript fragments.

## Key Functions
- `psw_open`, `psw_close`, `psw_output_page`: device lifecycle, page finalization, image cache reset, and per-page/per-file output handling.
- `psw_open_printer`, `psw_close_printer`: open/close vector output files, write deferred headers/trailers, and account for separate page output filenames.
- `psw_begin_file`: emits PostScript headers and level-dependent procsets.
- `psw_get_params`, `psw_put_params`: exposes `LanguageLevel` and shared psdf parameters; maps language level to `psdf_version`.
- `psw_beginpage`, `psw_check_erasepage`: starts pages lazily and handles deferred erasepage rectangles.
- `psw_setcolors`, `psw_dorect`, `psw_beginpath`, `psw_moveto`, `psw_lineto`, `psw_curveto`, `psw_closepath`, `psw_endpath`: PostScript vector syntax generation, with compact polygon and relative-path encoding.
- `psw_copy_mono`, `psw_copy_color`, `psw_fill_mask`: emit simple raster operations as PostScript images where possible.
- `psw_begin_image`, `psw_image_plane_data`, `psw_image_end_image`: handle high-level images, including Device/Indexed color spaces, masks, binary buffering, clipping, transforms, and fallback to default raster paths.
- `psw_image_write`, `psw_put_image`, `psw_image_stream_setup`, `psw_image_cleanup`: manage image data streams, ASCII/binary encodings, optional CCITT compression, DSC `%%BeginData` comments, and small-image cache definitions.

## Dependencies and Interactions
Uses the shared psdf layer from `gdevpsdf.h`/`gdevpsdu.c`, vector-device helpers, Ghostscript stream filters, ASCII85/ASCIIHex, CCITT Fax, bbox devices, and PostScript header helpers from `gdevpsu.h`.

## Notes
High-level color handling is deliberately not implemented and pure device colors are required. The writer falls back to default image handling for unsupported image formats/color spaces. Binary image output may require a pre-pass or whole-image buffer so the emitted DSC data length is correct.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsd.c

## Purpose
Implements Photoshop PSD export devices with support for RGB, CMYK, and DeviceN/spot-color channel output.

## Main Concepts
- Defines `psd_device`, a printer device with `gs_devn_params`, equivalent CMYK spot-color metadata, a selected process color model, and optional ICC lookup handles.
- Provides `gs_psdrgb_device` and `gs_psdcmyk_device`.
- Writes PSD files directly from printer raster rows, separating interleaved Ghostscript device pixels into Photoshop channel planes.
- Supports process color model selection through `ProcessColorModel` and DeviceN-related parameters.

## Key Functions
- `psd_prn_open`: opens printer output and sets separable/linear color metadata.
- Color mapping procedures:
  - `gray_cs_to_psdrgb_cm`, `rgb_cs_to_psdrgb_cm`, `cmyk_cs_to_psdrgb_cm`
  - `gray_cs_to_psdcmyk_cm`, `rgb_cs_to_psdcmyk_cm`, `cmyk_cs_to_psdcmyk_cm`
  - `gray_cs_to_spotn_cm`, `rgb_cs_to_spotn_cm`, `cmyk_cs_to_spotn_cm`
- `get_psdrgb_color_mapping_procs`, `get_psd_color_mapping_procs`: choose color mapping based on current model.
- `psd_encode_color`, `psd_decode_color`, `psd_map_color_rgb`: pack/unpack color components into `gx_color_index`.
- `psd_get_params`, `psd_put_params`: expose printer and DeviceN parameters, accept process color model changes, and optionally support ICC profile names when enabled at compile time.
- `psd_get_color_comp_index`, `psd_update_spot_equivalent_colors`: DeviceN spot-color integration.
- `psd_setup`: determines output channel order, process channels, and requested spot separations.
- `psd_write_header`: writes PSD signature/version, channel count, image dimensions, color mode, image resources, spot channel names, display info, and resolution.
- `psd_write_image_data`: emits uncompressed channel-plane image data.
- `psd_print_page`: coordinates PSD setup, header writing, and image data writing.

## Dependencies and Interactions
Relies on Ghostscript printer-device infrastructure, DeviceN color handling, equivalent CMYK spot-color support, color conversion helpers, and optional ICC APIs guarded by `ENABLE_ICC_PROFILE`.

## Notes
All multi-byte PSD fields are written big-endian. ICC profile support is compiled out by default. PSD output is uncompressed and plane-based; process CMYK channels are preserved in Photoshop order while spot separations can be selected/reordered through DeviceN separation order parameters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdf.h

## Purpose
Central shared interface for PostScript/PDF writer devices. It declares psdf distiller parameters, shared device structure fields, vector helpers, binary writer APIs, image filter setup APIs, and color/output utility procedures.

## Main Concepts
- Defines `psdf_image_params` for sampled image controls such as antialiasing, autofiltering, depth, downsampling, filter name/template, resolution, and JPEG/CCITT dictionaries.
- Defines `psdf_distiller_params`, including general Distiller-like options, color conversion/profile options, image options, and font embedding options.
- Defines `psdf_version` values for PostScript/PDF feature levels.
- Defines `gx_device_psdf_common`, used by concrete psdf-style vector devices.
- Defines `psdf_binary_writer`, the stream-chain wrapper used for encoded image/binary data.

## Public APIs
- Parameter handling: `gdev_psdf_get_params`, `gdev_psdf_put_params`.
- Vector state/path helpers: line width/cap/join/miter/dash/flat/logop, rectangle and path operators.
- Binary/image writing: `psdf_begin_binary`, `psdf_encode_binary`, `psdf_CFE_binary`, `psdf_DCT_filter`, `psdf_setup_image_filters`, `psdf_setup_lossless_filters`, `psdf_end_binary`.
- Special image filters: compression chooser, image-to-mask, and image color conversion filter setup.
- Color utilities: standard fill/stroke command tables, `psdf_adjust_color_index`, `psdf_set_color`, `psdf_round`.
- Unsupported raster access stubs: `psdf_get_bits`, `psdf_get_bits_rectangle`.
- Overprint compositor interception: `psdf_create_compositor`.

## Dependencies and Interactions
This header binds together concrete writers such as `gdevps.c`, shared utilities in `gdevpsdu.c`, image compression in `gdevpsdi.c`, parameter handling in `gdevpsdp.c`, and stream implementations in `gdevpsds.c`.

## Notes
The header includes many default macros, so device structs can embed initialized Distiller-like defaults consistently. Some declared behavior is intentionally partial, such as several color conversion strategies and filter-management comments noting unfinished functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdi.c

## Purpose
Builds image compression, downsampling, bit-depth conversion, and color-conversion filter chains for PostScript/PDF writer image output.

## Main Concepts
- Constructs stream filter chains backward, because encoded output filters must be added in reverse processing order.
- Mutates `gs_pixel_image_t` metadata when filters change image width, height, matrix, bits per component, or color space.
- Chooses between no compression, JPEG/DCT, CCITT Fax, LZW, Flate/zlib, PNG predictor, and custom psdf streams.

## Key Functions
- `pixel_resize`: inserts 1/2/4/12-to-8 or 8-to-1/2/4 bit-depth conversion streams from `gdevpsds.c`.
- `choose_DCT_params`: heuristically adjusts JPEG parameters based on whether a 3-component color space behaves like RGB, Lab, or something unknown.
- `setup_image_compression`: picks and configures DCT, lossless, CCITT, LZW, Flate, PNG predictor, and AutoFilter alternatives.
- `do_downsample`: decides whether configured downsampling applies based on effective image resolution and threshold.
- `setup_downsampling`: inserts Subsample or Average downsampling, adjusts image size/matrix, and combines resizing with compression.
- `psdf_is_converting_image_to_RGB`: checks whether CMYK image conversion to RGB is active.
- `psdf_setup_image_filters`: main public filter-pipeline builder for mono, mask, gray, color, and CMYK-to-RGB cases.
- `psdf_setup_lossless_filters`: constructs a constrained lossless no-downsample/no-color-conversion pipeline.
- `psdf_setup_compression_chooser`: installs the lineart/photo heuristic stream.
- `psdf_setup_image_to_mask_filter`: installs the image-colors stream configured as an image-to-mask converter.
- `psdf_setup_image_colors_filter`: installs a color-space conversion stream and rewrites image metadata to the device process color space.

## Dependencies and Interactions
Uses filter templates and stream states from `gdevpsds.c`/`gdevpsds.h`, JPEG/DCT, CCITT Fax, LZW, RunLength, PNG predictor, zlib, Ghostscript color space APIs, and shared psdf binary writer APIs from `gdevpsdf.h`.

## Notes
AutoFilter does not fully analyze entire images; it sets up alternative streams and a chooser. Some comments mark heuristics and incomplete behavior. The code is sensitive to image metadata consistency because downstream PDF/PostScript object generation assumes the modified image description matches the filter chain.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdp.c

## Purpose
Implements Distiller-style parameter get/put handling for PostScript/PDF writer devices.

## Main Concepts
- Defines recognized image filter names and minimum psdf versions.
- Maps public parameter names to fields in `psdf_distiller_params` and `psdf_image_params`.
- Handles image dictionaries, enum-like name parameters, font embedding lists, profile strings, and general psdf writer settings.
- Supports incremental `AlwaysEmbed`/`NeverEmbed` semantics through public add/delete/full-list parameter variants.

## Key Functions
- `gdev_psdf_get_params`: writes shared vector parameters plus psdf general, color, gray, mono, color-conversion, profile, and font embedding parameters.
- `gdev_psdf_put_params`: reads and validates psdf parameters, respects `LockDistillerParams`, then delegates standard vector parameters.
- `psdf_get_image_params`, `psdf_put_image_params`: get/put image-specific options including filters, dictionaries, downsampling, depth, encode, and resolution.
- `psdf_put_image_dict_param`: validates filter dictionary contents immediately by applying them to temporary stream state.
- `psdf_DCT_put_params`, `psdf_CF_put_params`: validate DCT and CCITT parameter dictionaries.
- `psdf_put_enum`: reads name-valued enum parameters.
- `psdf_read_string_param`, `psdf_write_string_param`: persist profile strings.
- `psdf_put_embed_param`, `add_embed`, `delete_embed`: implement replacement or incremental mutation of font embedding name arrays.

## Dependencies and Interactions
Uses stream templates from DCT, CCITT, LZW, RunLength, and zlib filters; uses shared declarations in `gdevpsdf.h`; delegates base vector device parameters to `gdev_vector_get_params`/`gdev_vector_put_params`.

## Notes
Flate filters are rejected unless the psdf version supports them. The code normalizes out-of-range image parameter values after reading. Some documented Adobe Distiller color conversion strategy behavior is explicitly not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.c

## Purpose
Implements custom image-processing stream filters used by the PostScript/PDF writer image pipeline.

## Main Concepts
- Cursor-based stream filters operate on Ghostscript `stream_cursor_read`/`stream_cursor_write` buffers.
- Provides bit-depth conversion, CMYK-to-RGB conversion, indexed color conversion, downsampling, compression-choice heuristics, and generic image color/mask conversion.

## Key Implementations
- Bit-depth conversion:
  - `s_1_8_template`, `s_2_8_template`, `s_4_8_template`, `s_12_8_template`
  - `s_8_1_template`, `s_8_2_template`, `s_8_4_template`
  - `s_1248_init`, `s_N_8_process`, `s_12_8_process`, `s_8_N_process`
- CMYK-to-RGB:
  - `s_C2R_template`, `s_C2R_init`, `s_C2R_process`
- Indexed conversion:
  - `s_IE_template`, `s_IE_init`, `s_IE_process`
  - Maintains a palette table and hash table, failing when too many distinct values exist.
- Downsampling:
  - `s_Subsample_template`, `s_Subsample_process`
  - `s_Average_template`, `s_Average_init`, `s_Average_process`, `s_Average_release`
  - `s_Downsample_size_out`
- Compression chooser:
  - `s_compr_chooser_template`
  - Tracks plateaus and gradients to distinguish likely photo versus line art.
  - `s_compr_chooser__get_choice` returns undecided/photo/lineart.
- Image color conversion:
  - `s__image_colors_template`
  - Converts arbitrary image samples either into a mask or into the current device process color model.

## Dependencies and Interactions
Declared by `gdevpsds.h` and consumed mainly by `gdevpsdi.c`. Uses Ghostscript device color conversion, color spaces, bitmap helpers, and imager state APIs.

## Notes
Several algorithms are heuristic or marked with comments indicating incomplete behavior. These filters are stateful, row-aware, and sensitive to exact cursor advancement, padding, and bit-buffer state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.h

## Purpose
Declares stream state structures and stream templates for image-processing filters implemented in `gdevpsds.c`.

## Main Declarations
- `stream_1248_state`: common state for 1/2/4/12-bit to 8-bit expansion and 8-bit to 1/2/4-bit reduction.
- Bit-depth conversion templates: `s_1_8_template`, `s_2_8_template`, `s_4_8_template`, `s_12_8_template`, `s_8_1_template`, `s_8_2_template`, `s_8_4_template`.
- `stream_C2R_state`: CMYK-to-RGB stream state, preserving `gs_imager_state` for UCR/BG behavior.
- `stream_IE_state`: IndexedEncode state with decode array, palette table, hash table, bit packing, and row position.
- `stream_Downsample_state_common`: common downsampling fields.
- `stream_Subsample_state`, `stream_Average_state`: downsampling stream states.
- `stream_compr_chooser_state`: photo/lineart compression decision state.
- `stream_image_colors_state`: generic image color or mask conversion state.

## Public APIs
- `s_1248_init`
- `s_C2R_init`
- `s_Downsample_size_out`
- `s_compr_chooser_set_dimensions`
- `s_compr_chooser__get_choice`
- `s_image_colors_set_dimensions`
- `s_image_colors_set_mask_colors`
- `s_image_colors_set_color_space`

## Dependencies and Interactions
This header is the contract between image pipeline construction in `gdevpsdi.c` and concrete stream implementations in `gdevpsds.c`.

## Notes
The file includes GC descriptor macros for stream states with pointers. The final image-colors template is named `s__image_colors_template`, with a double underscore, and the comment typo “Am image color conversion filter” appears in both header and implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdu.c

## Purpose
Implements shared utility functions for PostScript/PDF vector writers, including vector syntax helpers, color output, binary writer stream management, DCT/CCITT filter setup, raster-access stubs, and overprint compositor handling.

## Main Concepts
- Provides structure descriptors declared in `gdevpsdf.h`.
- Defines standard PDF-style fill and stroke color command names.
- Supplies generic vector output procedures used by psdf devices.
- Wraps binary/image data streams and optional ASCII85 encoding.

## Key Functions
- Vector syntax:
  - `psdf_setlinewidth`, `psdf_setlinecap`, `psdf_setlinejoin`, `psdf_setmiterlimit`, `psdf_setdash`, `psdf_setflat`
  - `psdf_dorect`, `psdf_beginpath`, `psdf_moveto`, `psdf_lineto`, `psdf_curveto`, `psdf_closepath`
- Color utilities:
  - `psdf_adjust_color_index`: restores the special all-components-full CMYK color case.
  - `psdf_round`
  - `psdf_set_color`: writes gray/RGB/CMYK values using compact rounded byte-derived color components.
- Binary/image streams:
  - `psdf_begin_binary`: initializes a binary writer and wraps ASCII85 when binary output is disabled.
  - `psdf_encode_binary`: pushes an encoding filter onto the writer.
  - `psdf_DCT_filter`: configures and optionally installs DCTEncode/JPEG compression with Rows/Columns/Colors.
  - `psdf_CFE_binary`: configures CCITTFaxEncode.
  - `psdf_end_binary`: closes filter chains.
- Unsupported operations:
  - `psdf_get_bits`, `psdf_get_bits_rectangle`: return unregistered errors for vector devices.
- `psdf_create_compositor`: consumes overprint compositors directly, otherwise delegates to the default compositor creation.

## Dependencies and Interactions
Used by concrete PostScript/PDF writers through `gdevpsdf.h`. Relies on Ghostscript stream filters, JPEG/DCT support, CCITT Fax, ASCII85, string/parameter printers, and overprint compositor helpers.

## Notes
Path output here is generic and less compact than the specialized `pswrite` path compressor in `gdevps.c`. Logical operation output is effectively a stub.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf.h

## Purpose
Declares the PostScript/PDF font writing interface, including glyph enumeration, outline glyph collection, Type 1/Type 2/CID/TrueType writing APIs, CMap writing, and font conversion utilities.

## Main Concepts
- Defines `psf_glyph_enum_t`, an opaque-enough stack-allocatable glyph enumerator supporting explicit glyph lists and bit-vector subsets.
- Defines `psf_outline_glyphs_t`, a container for outline font subset information and `.notdef`.
- Defines common glyph data callback type `glyph_data_proc_t`.
- Provides writer option bit flags for Type 1, Type 2/CFF, and TrueType output.

## Public APIs
- Glyph enumeration:
  - `psf_enumerate_list_begin`
  - `psf_enumerate_bits_begin`
  - `psf_enumerate_glyphs_reset`
  - `psf_enumerate_glyphs_next`
- Glyph set utilities:
  - `psf_add_subset_pieces`
  - `psf_sort_glyphs`
  - `psf_sorted_glyphs_index_of`
  - `psf_sorted_glyphs_include`
- Outline glyph collection:
  - `psf_check_outline_glyphs`
  - `psf_get_outline_glyphs`
- Type 1 support from `gdevpsf1.c`:
  - `psf_type1_glyph_data`
  - `psf_get_type1_glyphs`
  - `psf_write_type1_font`
- CFF/Type 2/CID/CMap/TrueType support declared for sibling implementation files:
  - `psf_write_type2_font`
  - `psf_write_cid0_font`
  - `psf_write_cmap`
  - `psf_write_truetype_font`
  - `psf_write_truetype_stripped`
  - `psf_write_cid2_font`
  - `psf_write_cid2_stripped`
  - `psf_convert_type1_to_type2`

## Dependencies and Interactions
Used by PostScript/PDF font embedding code. This grouped work item includes the Type 1 implementation in `gdevpsf1.c`; other declared APIs are implemented in sibling files outside this batch.

## Notes
The interface is allocation-conscious: writer procedures generally state that they do not allocate or free data. Subsets are represented either as sorted glyph lists or bit vectors depending on font family.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf1.c

## Purpose
Implements Type 1 embedded font serialization for PostScript/PDF output.

## Main Concepts
- Gathers Type 1 glyph data and writes a complete Type 1 font program.
- Supports optional subsetting, alternate font names, eexec encryption, ASCIIHex wrapping, eexec padding/mark handling, and forced `lenIV` behavior.
- Uses Ghostscript parameter-printer infrastructure to emit dictionaries and arrays.

## Key Functions
- `psf_type1_glyph_data`: obtains glyph outline data from a Type 1 font.
- `psf_get_type1_glyphs`: delegates outline glyph collection through the generic `psf_get_outline_glyphs`.
- `write_float_array`: writes named float arrays into a parameter list.
- `write_uid`: emits `UniqueID` or `XUID`.
- `write_font_name`: writes either an alternate name or the font’s original name.
- `write_Encoding`: emits StandardEncoding, ISOLatin1Encoding when allowed, or a generated 256-entry encoding array filtered by subset membership.
- `write_Private`: writes the Type 1 Private dictionary, private parameters, Subrs, and CharStrings.
- `stream_write_encrypted`: encrypts CharStrings when needed.
- `write_font_info`: emits selected FontInfo strings.
- `psf_write_type1_font`: top-level Type 1 writer that emits the font header, FontInfo, main dictionary, Encoding, matrix, bbox, private data, eexec-wrapped encrypted data, and length outputs.

## Dependencies and Interactions
Uses Ghostscript Type 1 font internals, glyph data APIs, Type 1 encryption, stream filters, ASCIIHex and eexec filters, PostScript string writing, parameter printers, and declarations from `gdevpsf.h`.

## Notes
Subrs are always written in full even when a subset is requested. If the source font has `lenIV < 0` but the caller requires `WRITE_TYPE1_WITH_LENIV`, the writer re-encrypts CharStrings using `lenIV = 0`. The `lengths[3]` output records cleartext/eexec/trailing sections for embedding contexts that need explicit stream lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf1.c -->