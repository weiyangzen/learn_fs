# Group Research: group_133_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gximag3x_c_sources_4de58dea2992

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.c

Ghostscript ImageType 3x implementation, an extension of ImageType 3-style masked images with two optional masks: opacity and shape. The file explicitly notes that the real work is not fully implemented; the default soft-mask clip path is mostly a structural wrapper that ignores the soft mask.

Key behavior:
- Defines `gs_image_type_3x` and the ImageType 3x enumerator procedure table.
- Initializes `gs_image3x_t` and its opacity/shape mask dictionaries.
- `gx_begin_image3x_generic` validates masks, computes mask/data rectangles and transforms, allocates an enumerator, creates intermediate mask devices, starts mask image enumerators, then starts the pixel image through a caller-provided mask clip/device setup callback.
- Supports omitted masks, chunky interleaved masks, and separate-source masks. Scan-line interleaving is rejected.
- `check_image3x_mask` validates mask geometry, bit depth, matrix compatibility, and allocates per-row buffers for chunky masks.
- `gx_image3x_plane_data` splits chunky data into mask and pixel buffers, feeds mask images first, flushes masks before pixel rows, and tracks row usage carefully for resumable error paths.
- `gx_image3x_planes_wanted` coordinates requested planes so opacity, shape, and pixel data stay in proportional row order.
- `gx_image3x_end_image` ends nested mask/pixel enumerators, closes intermediate devices, and frees buffers/devices/enumerator state.

Notable dependencies:
- Image definitions from `gximag3x.h` / `gsipar3x.h`.
- Memory devices from `gxdevmem.h`.
- Image state and CTM helpers from `gxistate.h`.
- `gdevbbox.h` for the default forwarding device used by the placeholder soft-mask implementation.
- Sample packing helpers from the image/sample subsystem.

Research notes:
- The default `make_mcdex_default` says there is no soft-mask analogue of the normal mask clip setup and simply forwards through a bbox device; this means ImageType 3x soft-mask behavior is incomplete in the default renderer.
- There are comments noting color-space lifetime gaps for allocated DevicePixel color spaces.
- Error cleanup is partially centralized, but a few early returns inside mask setup occur after allocation and before the normal cleanup labels, so this legacy code needs care if modified.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.h

Internal API for Ghostscript ImageType 3x processing.

Key contents:
- Includes ImageType 3x parameter definitions and generic image implementation declarations.
- Defines callback signatures for creating mask image devices and mask clipping devices/enumerators.
- Exports `gx_begin_image3x_generic`, which lets clients reuse the ImageType 3x splitting/orchestration logic while supplying custom mask-device and mask-compositing setup.

Notable dependencies:
- `gsipar3x.h` for ImageType 3x public parameter structures.
- `gxiparam.h` for image enumerator and typed image interfaces.

Research notes:
- This mirrors `gximage3.h` but expands the mask device callback for mask depth and two-mask arrays.
- The header is renderer/writer infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximag3x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.c

Generic Ghostscript image support shared by multiple image types.

Key behavior:
- Provides structure descriptors for common, data, and pixel image objects.
- Initializes common image fields, explicit-data image defaults, and pixel image defaults.
- `gx_image_enum_common_init` initializes common enumerator metadata and derives plane counts, widths, and depths for chunky, component-planar, and bit-planar input formats.
- Client helpers forward image data to an enumerator: `gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, and `gx_image_end`.
- Provides dummy stream serialization handlers for image types that cannot be serialized.
- Implements compact stream serialization/deserialization of generic pixel image parameters, including image matrix, bits per component, format, decode arrays, interpolation, and CombineWithColor.
- Provides variable-length unsigned integer encoding helpers and default image matrix detection/setup.

Notable dependencies:
- Color-space APIs from `gscspace.h`.
- Matrix and stream helpers from `gsmatrix.h` and `stream.h`.
- Image type definitions from `gxiparam.h`.

Research notes:
- Serialization is designed for Ghostscript banding/internal streams, not external image formats.
- The decode serialization is compact and special-cases default, inverted default, `(0,V)`, and `(U,V)` decode pairs.
- 12-bit pixel serialization is accepted for some formats; 16-bit support is handled elsewhere through unpack procedure availability.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.h

Internal image rendering state header for Ghostscript’s default image pipeline.

Key contents:
- Defines `sample_map`, sample decoding modes, decode macros, and declarations for optional 12-bit/16-bit sample unpacking procedures.
- Defines `image_posture` for portrait, landscape, and skewed image transforms.
- Defines color lookup “clue” entries used to cache mapped device colors.
- Defines the large `gx_image_enum` state object used by ImageType 1 and 4 rendering, including image format, alpha/mask state, matrix/posture, clipping, RasterOp state, buffers, scaling state, DDA state, decode maps, and color clues.
- Declares GC pointer enumeration macros for `gx_image_enum`.
- Declares shared initialization APIs: `gx_image_enum_alloc`, `gx_image_enum_begin`, `image_init_clues`, and `gx_image_scale_mask_colors`.

Notable dependencies:
- Image parameter definitions from `gsiparam.h` and `gxiparam.h`.
- Color-space and sample helpers from `gxcspace.h` and `gxsample.h`.
- Interpolation state from stream interpolation headers.

Research notes:
- This header exposes many implementation details because image class strategy functions and renderers operate directly on `gx_image_enum`.
- The clue cache is central to mono/color image performance, avoiding repeated color remapping for repeated sample values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage1.c

Ghostscript ImageType 1 initialization and serialization.

Key behavior:
- Defines separate `gx_image_type_t` records for ordinary ImageType 1 images and ImageMask images, both using `gx_begin_image1`.
- Initializes `gs_image_t` values with color space, mask flag, adjustment flag, and alpha.
- `gx_begin_image1` allocates the shared image enumerator, sets mask/alpha/adjust fields, and delegates to `gx_image_enum_begin`.
- Serializes ordinary images through generic pixel image serialization with alpha as extra control bits.
- Serializes image masks with a compact control word containing matrix presence, decode inversion, interpolation, adjustment, alpha, and bits per component.
- Releases ordinary ImageType 1 objects via generic pixel image release; mask image type uses default release because masks do not own a color space.

Notable dependencies:
- Shared image pipeline from `gximage.h`.
- Image type/procedure declarations from `gxiparam.h`.
- Stream helpers from `stream.h`.

Research notes:
- The image-mask encoding allows non-1-bit mask component depth for soft masks, even though ordinary image masks are constrained later by renderer setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage2.c

Ghostscript ImageType 2 implementation, which copies pixels from an existing graphics state/device region rather than consuming explicit source data.

Key behavior:
- Defines `gs_image_type_2` with custom source-size and begin-image procedures, and no stream serialization support.
- `image2_set_data` transforms the source rectangle from the source graphics state into device bounds and synthesizes an ImageType 1-style image descriptor.
- `gx_image2_source_size` reports the computed source width/height.
- `gx_begin_image2` validates PixelCopy compatibility, computes source and destination matrices, allocates a row buffer, and then either direct-copies pixels or re-emits them through the normal typed image pipeline.
- Supports optional `UnpaintedPath` population using unread rectangles reported by `get_bits_rectangle`.
- Handles RGB/alpha conversion for non-PixelCopy mode and direct native-color copying for simple PixelCopy cases.

Notable dependencies:
- Graphics state and device APIs: `gscoord.h`, `gsdevice.h`, `gxgetbit.h`, `gxpath.h`.
- Image type definitions from `gsiparm2.h` and `gxiparam.h`.

Research notes:
- The file contains explicit limitations: PixelCopy depth handling is incomplete, only simple cases are supported, and one Y computation is marked as rounded/wrong.
- On success, `gx_begin_image2` performs all rendering immediately and returns `1` because ImageType 2 has no caller-supplied data stream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.c

Ghostscript ImageType 3 implementation for images with an explicit 1-bit mask and pixel data.

Key behavior:
- Defines `gs_image_type_3` and the ImageType 3 enumerator procedure table.
- Initializes ImageType 3 objects with color space, interleave type, and default mask dictionary decode.
- Implements the default path by rendering the mask into a monochrome memory device, then wrapping the target in a mask clipping device for pixel rendering.
- `gx_begin_image3_generic` validates mask/data geometry, interleave mode, image matrices, and optional subrectangles; creates mask and pixel image descriptors; starts nested mask/pixel image enumerators; and exposes combined plane metadata.
- Supports chunky, scan-line, and separate-source interleaving.
- `gx_image3_plane_data` splits chunky data, alternates scan-line data based on proportional mask/pixel progress, processes mask rows first, flushes masks before pixels, and tracks rows used across interruptions.
- `gx_image3_planes_wanted` indicates whether mask or pixel planes should be supplied next, including dynamic width/depth changes for scan-line interleaving.
- `gx_image3_end_image` ends nested enumerators, closes/frees the mask clip and mask memory devices, and frees row buffers.

Notable dependencies:
- Internal API from `gximage3.h`.
- Mask clipping from `gxclipm.h`.
- Memory devices from `gxdevmem.h`.
- Image state from `gxistate.h`.

Research notes:
- The implementation builds masks incrementally row by row, so flush order matters: mask rows must reach the mask device before corresponding pixel rows render.
- Chunky splitting uses simple sample load/store loops and is explicitly not optimized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.h

Internal API for Ghostscript ImageType 3 processing.

Key contents:
- Defines callback signatures for creating the mask image device and the mask clipping device/enumerator.
- Documents that the ImageType 3 splitter is used both for rendering and high-level output writers.
- Exports `gx_begin_image3_generic`, parameterized by the mask-device and mask-clip setup callbacks.

Notable dependencies:
- `gsiparm3.h` for ImageType 3 public parameters.
- `gxiparam.h` for typed image and enumerator interfaces.

Research notes:
- This is a small virtualized setup layer that lets output devices reuse mask/pixel splitting without necessarily using the default memory-mask clipping device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage4.c

Ghostscript ImageType 4 implementation for color-key masked images.

Key behavior:
- Defines `gs_image_type_4`, using the same lower-level enumerator/rendering machinery as ImageType 1.
- Initializes ImageType 4 objects with a color space and default non-range `MaskColor`.
- `gx_begin_image4` allocates the shared image enumerator, validates `MaskColor` values against `BitsPerComponent`, normalizes exact or ranged mask colors into enumerator ranges, and disables masking if a range is impossible.
- Delegates rendering setup to `gx_image_enum_begin`.
- Serializes/deserializes generic pixel image parameters plus MaskColor values; the generic extra control bit stores `MaskColor_is_range`.

Notable dependencies:
- Public ImageType 4 parameters from `gsiparm4.h`.
- Shared image pipeline from `gximage.h`.
- Stream helpers from `stream.h`.

Research notes:
- Out-of-range mask colors produce `rangecheck`.
- If a mask-color range has `c0 > c1`, the implementation treats the image as fully opaque because no pixel can match that range.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximono.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximono.c

General mono-component image renderer for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_3_mono`, selected when an image has one sample per pixel.
- Chooses slow loops for image masks with halftone colors or non-default RasterOps, and otherwise can bypass some X clipping for portrait mono images.
- Precomputes DDA/fixed-point state and mask-color scaling.
- `image_render_mono` renders one scanline for single-component DeviceGray/DevicePixel/CIE/Separation/Indexed-style inputs and masks.
- Uses cached device-color “clues” so repeated sample values avoid repeated color remapping.
- Implements slow paths for masked/non-masked, portrait/landscape/skewed cases using `fill_parallelogram`.
- Implements a fast portrait path using run detection and `fill_rectangle` / device RasterOp rectangle fills.
- Saves source offset on error so image processing can resume.

Notable dependencies:
- Image state from `gximage.h`.
- Color mapping and device color helpers from `gxcmap.h`, `gxdcolor.h`, and `gxistate.h`.
- Halftone/cache state from `gzht.h`.

Research notes:
- This is performance-sensitive legacy raster code with hand-unrolled run skipping for common mono cases.
- Some comments call out limitations, such as missing adjustment in one slow orthogonal non-mask path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gximono.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino12b.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino12b.c

Dummy build-time stub for unsupported 12-bit image sample unpacking.

Key behavior:
- Includes the sample unpacking type definition.
- Defines `sample_unpack_12_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The shared image pipeline checks this pointer when 12-bit samples are requested; a null value makes unsupported cases fail with rangecheck.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino12b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino16b.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino16b.c

Dummy build-time stub for unsupported 16-bit image sample unpacking.

Key behavior:
- Includes the sample unpacking type definition.
- Defines `sample_unpack_16_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The common image setup code consults this pointer for 16-bit samples; this stub disables 16-bit unpacking in builds that include it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino16b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiodev.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiodev.h

Internal Ghostscript IODevice structure and procedure interface.

Key contents:
- Documents that IODevices are PostScript file/resource abstractions, distinct from Ghostscript output devices.
- Defines opaque references for file enumerators, parameter lists, and streams.
- Defines `gx_io_device_procs`, including initialization, opening device/file streams, OS `FILE *` open/close, delete, rename, status, file enumeration, and parameter get/put hooks.
- Declares default no-op/error implementations and OS-backed fopen/fclose helpers.
- Declares IODevice lookup and parameter APIs: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, `gs_putdevparams`.
- Defines the concrete `gx_io_device` structure with name, type, procedure table, and implementation state pointer.
- Provides GC structure descriptor macro for IODevice state.

Notable dependencies:
- `stat_.h` for file status structure.
- Ghostscript memory, stream, and parameter types supplied by surrounding headers.

Research notes:
- This is one of the files in the group most directly related to file abstraction: IODevices may map names to non-OS-backed streams and do not need to implement OS `fopen`.
- File-name arguments for many procedures are C strings, while `open_file` and enumeration patterns carry explicit lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiodev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiparam.h

Internal definitions for implementors of Ghostscript image types and image enumerators.

Key contents:
- Defines `gx_image_type_t`, the virtual table for image parameter storage type, begin procedure, source-size procedure, stream put/get, release, and PostScript ImageType index.
- Declares common source-size and dummy serialization/release helpers.
- Declares generic pixel image stream serialization helpers and variable-length integer helpers.
- Defines `gx_image_enum_procs_t`, the virtual table for feeding plane data, ending an image, optional flushing, and optional wanted-plane negotiation.
- Defines the common prefix for all image enumerators: image type, procs, target device, unique id, plane counts/depths/widths.
- Declares common enumerator initialization and shared ImageType 1 procedures.

Notable dependencies:
- Ghostscript structure descriptors from `gsstype.h`.
- Device client types from `gxdevcli.h`.

Research notes:
- The `planes_wanted` contract is important for ImageType 3/3x, where mask and pixel planes may be requested in changing proportions.
- The enum common ID exists so banding machinery can distinguish simultaneous image enumerations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxipixel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxipixel.c

Common Ghostscript ImageType 1 and 4 image enumerator initialization code.

Key behavior:
- Defines the GC descriptor for `gx_image_enum`, including special enumeration/relocation of cached device-color clue entries.
- `gx_image_enum_alloc` validates image dimensions, bits-per-component, image format, and optional subrectangle, then allocates and initializes the source rectangle.
- `gx_image_enum_begin` computes the image-to-device matrix, initializes plane metadata, validates image masks, configures decode/sample maps, normalizes image format, optimizes RasterOps, and allocates the unpack buffer.
- Determines image posture, extents, clipping state, DDA row/strip/pixel origins, and special one-pixel-wide/high adjustment for old TeX/dvips line images.
- Chooses an unpack procedure for 1/2/4/8/12/16-bit input, with interleaved variants when necessary.
- Selects an image class renderer from the global image class table.
- Sets up clip forwarding devices and RasterOp texture devices when needed.
- `image_init_clues`, `image_init_colors`, and `image_init_map` initialize device-color caches and sample decode expansion tables.
- `gx_image_scale_mask_colors` scales ImageType 4 mask-color ranges to 8-bit sample values and accounts for Decode inversion.

Notable dependencies:
- Image class table from `gscdefs.h`.
- Graphics/image state from `gximage.h`, `gxistate.h`, `gzstate.h`.
- Clipping, memory, and RasterOp devices from `gzcpath.h`, `gxdevmem.h`, and `gdevmrop.h`.

Research notes:
- This is the central setup path for ordinary and color-key masked images.
- 12-bit and 16-bit handling depends on external `sample_unpack_12_proc` and `sample_unpack_16_proc`; the stub files in this group set them to null.
- RasterOp rewrites can transform some 1-bit image operations into imagemask-style rendering for cheaper execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxipixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiscale.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiscale.c

Interpolated image rendering support for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_0_interpolate`.
- Enables interpolation only for a limited set of cases: interpolated, non-mask, portrait images without mask color, alpha, or low-capability target color depth.
- Uses Mitchell filtering by default via `s_IScale_template`; spatial interpolation code path is present but disabled.
- Allocates a source/destination line buffer and a stream image scale state.
- Converts input rows to concrete color values when needed, optionally mirrors rows for negative X scale, and feeds the scaling stream.
- `image_render_interpolate` drains scaled rows, remaps concrete output samples to device colors, packs pure colors into scanlines, and falls back to per-pixel rectangle fills for non-pure device colors.

Notable dependencies:
- Stream scaling/interpolation templates from `siinterp.h` and `siscale.h`.
- Image state from `gximage.h`.
- Device/color mapping helpers from `gxdevice.h`, `gxcmap.h`, and `gxdcolor.h`.

Research notes:
- If interpolation setup is unsupported or allocation/init fails, the strategy clears `penum->interpolate` and lets another renderer handle the image.
- Conservative filtering rules are compiled out by default.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiscale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxistate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxistate.h

Ghostscript imager state definition.

Key contents:
- Documents the subset of PostScript graphics state retained by the language-independent imager library.
- Defines opaque color rendering state dependencies: halftones, device colors, device halftones.
- Defines `gx_transfer` and macros for the color rendering state: halftone, screen phase, device halftone, CIE rendering, black generation, undercolor removal, transfer maps, CIE joint caches, color map procs, DeviceN component map, and pattern cache.
- Defines GC/reference-count pointer enumeration macros for color rendering state.
- Defines `gs_imager_state_common`, including memory, client data, line parameters, CTM, current point, RasterOp, alpha/blend/transparency/soft-mask fields, text knockout, overprint settings, flatness/fill/stroke/curve/shading controls, color map proc hook, and color rendering state.
- Provides CTM access macros and inline accessors for flatness, line params, and logical operation.
- Declares initialization, copy, reference-count, assignment, release, and screen phase APIs.

Notable dependencies:
- Line parameters from `gxline.h`.
- Fixed matrices from `gxmatrix.h`.
- Color, transfer, transparency, and RasterOp headers.

Research notes:
- The CTM is stored as `gs_matrix_fixed`, so callers must use `ctm_only` when APIs require a plain `gs_matrix`.
- Effective transfer pointers are relocated specially but not enumerated for GC because they alias owned/reference-counted objects elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxistate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxline.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxline.h

Private Ghostscript line parameter definitions.

Key contents:
- Defines `gx_dash_params`, including dash pattern storage, offset, adaptive flag, and computed dash state.
- Defines `gx_line_params`, including half-width, cap/join, curve join override, miter limit/check, dot length/orientation, and dash parameters.
- Provides macros for setting/current line width, miter limit access, dash adapt flag, and default initializers.
- Declares setters for miter limit, dash pattern, and dot length.

Notable dependencies:
- Public line parameter types from `gslparam.h`.
- Matrix type from `gsmatrix.h`.

Research notes:
- `gx_dash_params` is embedded in `gx_line_params` rather than meant for standalone allocation.
- The default miter check constant is precomputed and documented as tied to `gx_set_miter_limit` / stroke behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxlum.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxlum.h

Small Ghostscript luminance constants header.

Key contents:
- Defines RGB luminance weights: red 30, green 59, blue 11.
- Defines `lum_all_weights` as the total weight.

Notable dependencies:
- None beyond the surrounding C preprocessor environment.

Research notes:
- These integer weights approximate common 30/59/11 grayscale conversion behavior and are used by color/printer code elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxlum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmatrix.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmatrix.h

Internal Ghostscript matrix/fixed-point transformation header.

Key contents:
- Defines `PRECISE_CURRENTPOINT` as enabled.
- Defines `gs_matrix_fixed`, a matrix with cached fixed-point translation and a validity flag.
- Declares conversion from plain matrix to fixed matrix and point/distance transforms to fixed point.
- Declares a rounded fixed-point transform when precise currentpoint support is enabled.
- Defines `fixed_coeff`, used to avoid floating point in selected coordinate transforms.
- Declares `fixed_coeff_mult` and defines `m_fixed`, a macro that chooses a faster integer path when a fixed value is in range.

Notable dependencies:
- Plain matrix definitions from `gsmatrix.h`.

Research notes:
- The comments warn that disabling precise currentpoint should not go to production because it drops clamping.
- The fixed coefficient machinery is specialized and primarily called out for Type 1 font interpreter use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmatrix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.c

Implementation of Ghostscript mask clipping device initialization and GC support.

Key behavior:
- Defines the public structure descriptor for `gx_device_mask_clip`.
- Enumerates and relocates pointers inside the mask clip device, including embedded strip bitmap, embedded memory device, and forwarding-device prefix.
- Relocation adjusts memory-device line pointers specially because they point into the mask clip device’s own embedded buffer.
- `gx_mask_clip_initialize` initializes a forwarding mask clip device against a target, sets dimensions/color info/phase, creates an embedded monochrome memory device for tile buffering, and sizes the buffer to fit within a small fixed internal buffer.
- If the mask tile is too wide to buffer even one scanline, it sets `mdev.base = 0` and returns success, leaving callers to use a slower fallback.

Notable dependencies:
- Device and memory device APIs from `gxdevice.h` and `gxdevmem.h`.
- Structure definition from `gxmclip.h`.

Research notes:
- The implementation uses an embedded buffer rather than allocating tile-buffer memory separately.
- The “too wide” case is intentionally supported by punting to default slow `copy_mono` behavior via the header macro.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.h

Mask clipping device structure and helper interface.

Key contents:
- Documents mask clipping use for ImageType 3 images and Patterns that do not fill their bounding box.
- Defines a small aligned tile clip buffer size.
- Defines `gx_device_mask_clip`, a forwarding device containing a mask bitmap, embedded memory device, phase, and aligned buffer.
- Declares the structure descriptor and `gx_mask_clip_initialize`.
- Defines `setup_mask_copy_mono`, a macro used by copy-mono implementations to choose colors and fallback behavior for mask clipping.

Notable dependencies:
- `gxclip.h` and required device/memory-device definitions from including context.

Research notes:
- The structure is logically private, but exposed so clients can allocate instances directly.
- The phase is described as a device-space origin relative to the tile, opposite of graphics state phase semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxobj.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxobj.h

Ghostscript memory manager object header definitions.

Key contents:
- Defines object mark/back field bit layout and distinguished GC values for unmarked local objects and untraced global objects.
- Defines macros for setting/testing unmarked, untraced, and marked object states.
- Defines `obj_header_data_t`, including alone flag, mark/back union, object size, and type/relocation union.
- Computes object alignment modulus from memory, bitmap, and back-pointer alignment constraints.
- Defines alignment/rounding macros and the padded real `obj_header_t`.
- Defines field abbreviations for object header access.
- Defines macros to compute object content size, rounded object size, and next object when scanning storage linearly.
- Defines `chunk_head_t`, containing the relocation destination and a free object header.

Notable dependencies:
- Bitmap alignment definitions from `gxbitmap.h`.

Research notes:
- This is low-level allocator/GC metadata, not image rendering logic.
- Comments explain the dual use of mark/back during mark and compaction phases; interpreting object headers requires chunk context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.c

Generic overprint fill-rectangle implementation for Ghostscript devices.

Key behavior:
- Provides scanline pack/unpack helpers for depths below 8 bits and depths that are multiples of 8.
- `gx_overprint_generic_fill_rectangle` handles non-separable color encodings by reading target pixels, decoding source and destination colors, replacing selected process components, re-encoding pixels, and copying modified scanlines back.
- Selects `get_bits_rectangle` options to retrieve native chunky color data without alpha and with standard alignment/raster behavior.
- Provides replicated fill patterns for 2-bit and 4-bit depths and `replicate_color`.
- `gx_overprint_sep_fill_rectangle_1` handles separable encodings efficiently when color depth divides the fill chunk size, using `bits_fill_rectangle_masked`.
- `gx_overprint_sep_fill_rectangle_2` handles other separable byte-depth cases by byte-wise retain-mask/color merging.
- All routines fit the requested rectangle to the target device and allocate temporary scanline buffers.

Notable dependencies:
- Device APIs from `gxdevice.h`, `gsdevice.h`, and `gxgetbit.h`.
- Bit/bitmap helpers from `gsbitops.h`.
- Public declarations from `gxoprect.h`.

Research notes:
- The file describes itself as a “very slow” generic implementation; faster overprint should be implemented directly in target devices when possible.
- The generic non-separable path is necessarily per-pixel because it must decode/modify/re-encode component values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.h

Public/internal interface for generic overprint rectangle fills.

Key contents:
- Declares `gx_overprint_generic_fill_rectangle` for non-separable color encodings.
- Declares `gx_overprint_sep_fill_rectangle_1` for separable encodings where depth can use fill-chunk masking.
- Declares `gx_overprint_sep_fill_rectangle_2` for separable byte-oriented cases such as 24-bit depth.
- Documents byte-swapping expectations for color and retain masks on little-endian machines.

Notable dependencies:
- Requires Ghostscript device, color index, and memory types from including context.

Research notes:
- The header preserves implementation split by target color encoding, not by high-level drawing operation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxoprect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1fill.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1fill.c

PatternType 1 rectangle filling algorithms for Ghostscript.

Key behavior:
- Defines `tile_fill_state_t`, carrying original fill arguments, tile/mask clip setup, phase, RasterOp source state, and offsets for non-simple tiles.
- `tile_fill_init` initializes optional tile mask clipping and computes mask phase for simple masked tiles.
- `tile_by_steps` handles non-standard pattern step matrices by transforming the filled rectangle into pattern step space, iterating all overlapping tile placements, clipping each tile copy, updating mask phase/offsets, and calling a supplied fill callback.
- `tile_colored_fill` fills a clipped piece of a colored pattern using either `copy_color` or `strip_copy_rop`.
- `gx_dc_pattern_fill_rectangle` handles colored Pattern fills, choosing fast simple-tile paths or `tile_by_steps` for non-simple patterns.
- `tile_masked_fill` adapts source offsets for uncolored masked pattern pieces.
- `gx_dc_pure_masked_fill_rect`, `gx_dc_binary_masked_fill_rect`, and `gx_dc_colored_masked_fill_rect` wrap pure, binary halftone, and colored halftone rectangle fills with mask-tile handling.

Notable dependencies:
- Pattern/color definitions from `gxpcolor.h` and `gxp1impl.h`.
- Tile clipping from `gxclip2.h`.
- Device color and RasterOp APIs from `gxdcolor.h`, `gxdevcli.h`, and `gsrop.h`.

Research notes:
- Non-simple pattern tiling is intentionally conservative for partly transparent patterns, expanding the iteration range so every overlapping pattern copy affects the fill.
- A local comment questions a possible leak/memory pointer choice in `tile_fill_init`; the call currently passes `dev->memory` to `tile_clip_initialize`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1fill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1impl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1impl.h

PatternType 1 implementation interface.

Key contents:
- Declares fill rectangle procedures implemented in `gxp1fill.c` for colored patterns and masked pure/binary/colored device colors.
- Declares Pattern color mapping procedures exported by `gxpcmap.c`: `gx_pattern_load` and `gs_pattern1_remap_color`.

Notable dependencies:
- Requires Pattern color definitions from `gxpcolor.h`.

Research notes:
- Uses shortened `masked_fill_rect` naming to stay within historical 32-character identifier limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.c

Ghostscript page queue implementation for coordinating queued band/page rendering work.

Key behavior:
- Defines `gx_page_queue_s`, containing allocator, monitor, queue count, dequeue-in-progress flag, render request/done semaphores, FIFO entry links, and a reserve entry.
- Allocates queue objects and queue entries using Ghostscript memory descriptors.
- `gx_page_queue_init` creates the monitor, semaphores, and reserve entry; `gx_page_queue_dnit` drains queued entries, closes page info resources, and frees synchronization objects/reserve entry.
- Low-level add/remove helpers maintain FIFO ordering under the monitor.
- `gx_page_queue_wait_one_page` and `gx_page_queue_wait_until_empty` let producers wait until pending or in-progress rendering completes.
- `gx_page_queue_enqueue` adds an entry and signals the render request semaphore.
- `gx_page_queue_add_page` allocates or consumes the reserve entry, fills action/page info/copy count, enqueues it, then waits as needed until a new reserve entry can be allocated.
- `gx_page_queue_start_dequeue` waits for render requests, marks dequeue in progress, and removes the first entry.
- `gx_page_queue_finish_dequeue` optionally signals render completion, clears dequeue-in-progress, closes clist page resources, frees the entry, and exits the monitor.

Notable dependencies:
- Page queue declarations from `gxpageq.h`.
- Band/page info and clist cleanup from `gxclist.h`.
- Ghostscript monitor/semaphore primitives via device infrastructure.

Research notes:
- The reserve-entry design provides a fallback path when entry allocation fails, ensuring a page can still be queued before waiting for memory to become available.
- `gx_page_queue_add_page` documents that an entry may have been queued even if it later returns an error while trying to restore the reserve entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.c -->