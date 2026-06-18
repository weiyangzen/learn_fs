# Group Research: group_1571_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gximag3x_c_sources__32d22b3e3356

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.c

Ghostscript ImageType 3x implementation, extending ImageType 3-style masked images with separate optional opacity and shape masks. The file explicitly says the real soft-mask work is not yet implemented; the default path mostly orchestrates data splitting and forwards pixel rendering through a bbox device.

Key behavior:
- Defines `gs_image_type_3x`, ImageType 3x enumerator procs, and initialization for `gs_image3x_t` plus opacity/shape mask dictionaries.
- `gx_begin_image3x_generic` validates mask geometry, interleave modes, matrix compatibility, allocates the combined enumerator, creates mask devices, starts nested mask image enumerators, and starts the pixel image through a caller-supplied mask-compositing callback.
- Supports omitted masks, chunky masks interleaved with pixel samples, and separate-source masks; scan-line interleaving is rejected.
- `check_image3x_mask` validates mask dimensions/depths and computes proportional subrectangles for masks.
- `gx_image3x_plane_data` splits chunky mask/pixel rows, feeds masks before pixel rows, flushes mask enumerators before pixel rendering, and tracks row usage/skips for resumable error paths.
- `gx_image3x_planes_wanted` coordinates opacity, shape, and pixel planes so earlier channels stay at least as far progressed as later channels.
- `gx_image3x_end_image` ends nested enumerators, closes devices, and frees row buffers/devices/enumerator state.

Notable dependencies:
- ImageType 3x declarations from `gximag3x.h` and public parameters from `gsipar3x.h`.
- Memory/image devices from `gxdevmem.h`.
- Image state helpers from `gxistate.h`.
- `gdevbbox.h` for the default forwarding device used by the placeholder soft-mask path.
- Sample load/store macros from Ghostscript’s sample subsystem.

Research notes:
- The default `make_mcdex_default` says there is no soft-mask analogue of ImageType 3 mask clipping and simply ignores the soft mask while forwarding through a bbox device.
- The file allocates DevicePixel color spaces for mask rendering and has an inline comment noting missing color-space lifetime cleanup on error/end paths.
- Several early returns in mask setup happen after allocation, so cleanup/error maintenance is delicate.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.h

Internal API for Ghostscript ImageType 3x processing.

Key contents:
- Includes ImageType 3x public parameter definitions and generic image enumerator interfaces.
- Defines `IMAGE3X_MAKE_MID_PROC`, the callback signature for creating opacity/shape mask image devices at a requested width, height, and depth.
- Defines `IMAGE3X_MAKE_MCDE_PROC`, the callback signature for creating a mask-compositing/clip device and the pixel image enumerator, with both mask devices/enumerators and origins passed in.
- Exports `gx_begin_image3x_generic`, allowing renderers and high-level output writers to reuse ImageType 3x splitting while supplying custom mask handling.

Notable dependencies:
- `gsipar3x.h` for `gs_image3x_t` and mask parameter structures.
- `gxiparam.h` for image type/enumerator interfaces.

Research notes:
- This mirrors the ImageType 3 internal API but generalizes it for two masks and arbitrary mask bit depth.
- It is rendering/output infrastructure, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximag3x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.c

Generic Ghostscript image support shared by multiple image types.

Key behavior:
- Defines structure descriptors for common, data, and pixel image objects.
- Initializes common image matrices, explicit-data defaults, pixel-image defaults, formats, decode arrays, color spaces, and `CombineWithColor`.
- `gx_image_enum_common_init` initializes common enumerator metadata and derives plane counts, widths, and depths for chunky, component-planar, and bit-planar formats.
- Provides client wrappers for feeding data and ending images: `gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, and `gx_image_end`.
- Supplies dummy stream serialization functions for image types that cannot be serialized.
- Implements compact stream serialization/deserialization of generic pixel image parameters, including matrix, bits/component, format, decode arrays, interpolation, and CombineWithColor.
- Provides variable-length unsigned integer stream encoding and helpers for default ImageMatrix detection/setup.

Notable dependencies:
- Color-space APIs from `gscspace.h`.
- Matrix and utility helpers from `gsmatrix.h` and `gsutil.h`.
- Stream APIs from `stream.h`.
- Image type definitions from `gxiparam.h`.

Research notes:
- Serialization is for Ghostscript internal/banding streams, not image file formats.
- Decode serialization special-cases default, inverted default, `(0,V)`, and `(U,V)` forms to keep streams compact.
- Generic serialization accepts 12-bit image parameters for some formats; actual 12/16-bit unpack availability is controlled elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.h

Internal image rendering state header for Ghostscript’s default image pipeline.

Key contents:
- Defines `sample_map`, decode modes, and macros for decoding byte or frac samples into client colors.
- Declares optional external 12-bit and 16-bit sample unpack procedure pointers.
- Defines `image_posture` for portrait, landscape, and skewed image transforms.
- Defines `gx_image_clue`, a cached device-color lookup entry.
- Defines the large `gx_image_enum` structure used by ImageType 1 and 4 rendering, including source format, mask/alpha state, matrix/posture, clip flags, RasterOp state, DDA state, buffers, sample maps, scaler state, and 256 color clues.
- Declares GC pointer enumeration macros and core initialization APIs: `gx_image_enum_alloc`, `gx_image_enum_begin`, `image_init_clues`, and `gx_image_scale_mask_colors`.

Notable dependencies:
- Public image parameters from `gsiparam.h`.
- Color-space and sample helpers from `gxcspace.h` and `gxsample.h`.
- Interpolation stream state via `strimpl.h` and `sisparam.h`.
- Image class interfaces from `gxiclass.h`.

Research notes:
- The header exposes implementation state because image class strategy functions and renderers operate directly on `gx_image_enum`.
- The clue cache is a performance feature for mono/color image rendering, avoiding repeated color remapping for recurring sample values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage1.c

Ghostscript ImageType 1 initialization and serialization.

Key behavior:
- Defines separate `gx_image_type_t` records for ordinary ImageType 1 images and ImageMask images.
- Initializes `gs_image_t` with color space, ImageMask flag, adjustment flag, type pointer, and alpha.
- `gx_begin_image1` allocates the shared image enumerator, sets alpha/mask/adjust fields, and delegates to `gx_image_enum_begin`.
- Serializes ordinary images through generic pixel image serialization, using the extra control bits for alpha.
- Serializes image masks with a compact mask-specific control word containing matrix presence, decode inversion, interpolation, adjustment, alpha, and bits/component.
- Releases ordinary ImageType 1 pixel image objects through `gx_pixel_image_release`; mask images use default release because they do not own a color space.

Notable dependencies:
- Shared image pipeline from `gximage.h`.
- Image type/enumerator declarations from `gxiparam.h`.
- Stream helpers from `stream.h`.

Research notes:
- ImageMask serialization carries bits/component for soft masks even though normal imagemasks are later constrained by renderer setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage2.c

Ghostscript ImageType 2 implementation, copying pixels from an existing graphics state/device region rather than consuming explicit source data.

Key behavior:
- Defines `gs_image_type_2` with custom source-size and begin procedures, and no stream serialization support.
- `image2_set_data` transforms a source rectangle from the source graphics state into device bounds and synthesizes ImageType 1-style image metadata.
- `gx_image2_source_size` reports the computed source width/height.
- `gx_begin_image2` validates PixelCopy compatibility, computes source/destination matrices, allocates a row buffer, and renders immediately.
- Supports direct native-color copy for simple PixelCopy cases, or re-emits rows through the normal typed-image pipeline for converted RGB/alpha cases.
- Optionally records unread rectangles into `UnpaintedPath` when `get_bits_rectangle` reports gaps.

Notable dependencies:
- Graphics state/device APIs from `gscoord.h`, `gsdevice.h`, and `gxgetbit.h`.
- Path updates via `gxpath.h`.
- ImageType 2 public parameters from `gsiparm2.h`.

Research notes:
- Comments document limitations: PixelCopy depth handling is incomplete, only simple cases are supported, and one Y computation is marked rounded/wrong.
- On success it returns `1` because ImageType 2 has no later caller-supplied data stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.c

Ghostscript ImageType 3 implementation for images with an explicit 1-bit mask plus pixel data.

Key behavior:
- Defines `gs_image_type_3` and the ImageType 3 enumerator procedure table.
- Initializes ImageType 3 images with color space, interleave type, and default inverted mask decode.
- Default rendering creates a monochrome memory device for the mask and a mask clipping device in front of the target for pixel rendering.
- `gx_begin_image3_generic` validates mask/data dimensions, interleave modes, matrix compatibility, optional subrectangles, and starts nested mask/pixel ImageType 1 enumerators.
- Supports chunky interleaving, scan-line interleaving, and separate-source interleaving.
- `gx_image3_plane_data` splits chunky data, alternates scan-line data, processes mask rows before pixel rows, flushes mask data before pixel drawing, and preserves resumability with `mask_skip`.
- `gx_image3_planes_wanted` reports current plane needs and updates width/depth for scan-line interleave.
- `gx_image3_end_image` ends nested enumerators, closes mask clip and mask memory devices, and frees row buffers/state.

Notable dependencies:
- Internal API from `gximage3.h`.
- Mask clipping from `gxclipm.h`.
- Memory devices from `gxdevmem.h`.
- Image state and CTM helpers from `gxistate.h`.

Research notes:
- The mask is built incrementally row by row, so mask flushing order is essential before corresponding pixels are rendered.
- Chunky sample splitting is intentionally simple and not optimized.
- There is an Alpha/gcc padding workaround when copying `gs_pixel_image_t` into `gs_image_t`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.h

Internal API for Ghostscript ImageType 3 processing.

Key contents:
- Defines callback signatures for creating the mask image device and the mask clipping device/enumerator.
- Documents that ImageType 3 mask/pixel splitting is used both for actual imaging and for high-level output writers.
- Exports `gx_begin_image3_generic`, parameterized by mask-device and mask-clip setup callbacks.

Notable dependencies:
- `gsiparm3.h` for public ImageType 3 parameter structures.
- `gxiparam.h` for typed image and enumerator interfaces.

Research notes:
- This is a small virtualization layer for mask/pixel orchestration; clients can reuse splitting without using the default memory-mask clipping device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage4.c

Ghostscript ImageType 4 implementation for color-key masked images.

Key behavior:
- Defines `gs_image_type_4`, reusing the lower-level ImageType 1 enumerator/rendering machinery.
- Initializes ImageType 4 images with a color space and non-range `MaskColor` mode by default.
- `gx_begin_image4` allocates the shared image enumerator, validates mask color values against `BitsPerComponent`, normalizes exact/ranged mask colors into enumerator ranges, and disables masking if a range is impossible.
- Delegates rendering setup to `gx_image_enum_begin`.
- Serializes/deserializes generic pixel image parameters plus `MaskColor` values; the generic extra control bit stores `MaskColor_is_range`.

Notable dependencies:
- Public ImageType 4 parameters from `gsiparm4.h`.
- Shared image pipeline from `gximage.h`.
- Stream helpers from `stream.h`.

Research notes:
- Out-of-range mask colors produce `rangecheck`.
- A `c0 > c1` mask range is treated as fully opaque because no source sample can match it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximono.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximono.c

General mono-component image renderer for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_3_mono`, selected for one-sample-per-pixel images.
- Chooses slower loops for imagemasks with halftone colors or non-default RasterOps; otherwise it can bypass X clipping for portrait mono images.
- Precomputes fixed-point DDA values and scales ImageType 4 mask-color ranges to byte sample space.
- `image_render_mono` handles single scanlines for DeviceGray, DevicePixel, CIEBasedA, Separation, Indexed-style inputs, and imagemasks.
- Uses cached device-color clues so repeated sample values avoid repeated remapping.
- Has slow paths for masked/non-masked portrait, landscape, and skewed images using `fill_parallelogram`.
- Has a fast portrait path using run detection and rectangle/RasterOp fills.
- Saves source offset in `penum->used` on error so rendering can resume.

Notable dependencies:
- Image state from `gximage.h`.
- Color mapping/device color helpers from `gxcmap.h`, `gxdcolor.h`, and `gxistate.h`.
- Halftone/cache support from `gzht.h`.
- Fixed-point/DDA helpers from `gxmatrix.h`, `gxarith.h`, and `gxfixed.h`.

Research notes:
- This is performance-sensitive legacy raster code with manually optimized run skipping.
- A comment notes the slow orthogonal non-mask path does not apply adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximono.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino12b.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino12b.c

Dummy build-time stub for unsupported 12-bit image sample unpacking.

Key behavior:
- Includes Ghostscript base/sample type headers.
- Defines `sample_unpack_12_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The shared image setup code consults this pointer for 12-bit samples; null makes unsupported 12-bit cases fail with `rangecheck`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino12b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino16b.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino16b.c

Dummy build-time stub for unsupported 16-bit image sample unpacking.

Key behavior:
- Includes Ghostscript base/sample type headers.
- Defines `sample_unpack_16_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The common image setup path checks this pointer for 16-bit samples; this stub disables 16-bit unpacking in builds that use it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino16b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiodev.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiodev.h

Internal Ghostscript IODevice structure and procedure interface.

Key contents:
- Documents that IODevices are PostScript file/resource abstractions and distinct from Ghostscript output devices.
- Defines opaque references for file enumerators, parameter lists, and streams.
- Defines `gx_io_device_procs`, covering initialization, device/file stream opening, OS `FILE *` open/close, delete, rename, status, file enumeration, and parameter get/put hooks.
- Declares default no-op/error implementations and OS-backed `fopen`/`fclose` helpers.
- Declares IODevice lookup and parameter APIs: `gs_getiodevice`, `gs_findiodevice`, `gs_getdevparams`, and `gs_putdevparams`.
- Defines the concrete `gx_io_device` with name, type, procedure table, and optional state pointer.
- Provides a GC descriptor macro for IODevice state.

Notable dependencies:
- `stat_.h` for `struct stat`.
- Ghostscript memory, stream, and parameter types supplied by surrounding headers.

Research notes:
- This is the most file-abstraction-related file in the group: IODevices can return streams unrelated to the host OS filesystem.
- Some APIs take C strings while `open_file` and enumeration patterns include explicit lengths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiodev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiparam.h

Internal definitions for implementors of Ghostscript image types and image enumerators.

Key contents:
- Defines `gx_image_type_t`, the virtual table for image storage type, begin procedure, source-size procedure, stream put/get, release, and PostScript ImageType index.
- Declares common source-size and dummy serialization/release helpers.
- Declares generic pixel image stream serialization helpers and variable-length integer helpers.
- Defines `gx_image_enum_procs_t`, the virtual table for feeding plane data, ending an image, optional flushing, and optional plane-wanted negotiation.
- Defines the common prefix for all image enumerators, including image type, procs, target device, unique id, plane counts, plane depths, and plane widths.
- Declares common enumerator initialization and the shared ImageType 1 procedures used by ImageType 4.

Notable dependencies:
- Structure descriptor declarations from `gsstype.h`.
- Device client types from `gxdevcli.h`.

Research notes:
- The `planes_wanted` contract is central for ImageType 3/3x, where mask and pixel planes can be requested in changing proportions.
- The unique enumerator ID is intended for banding machinery that may track simultaneous image enumerations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxipixel.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxipixel.c

Common Ghostscript ImageType 1 and 4 image enumerator initialization code.

Key behavior:
- Defines the GC descriptor for `gx_image_enum`, including special enumeration/relocation for cached device-color clue entries.
- `gx_image_enum_alloc` validates dimensions, bits/component, image format, optional subrectangle, and allocates the enumerator.
- `gx_image_enum_begin` computes the image-to-device matrix, initializes common plane metadata, validates imagemasks, configures decode/sample maps, normalizes image format, optimizes RasterOps, and allocates the unpack buffer.
- Determines image posture, extents, clipping flags, DDA origins, one-pixel-wide/high adjustment for old TeX/dvips line images, and renderer strategy.
- Chooses sample unpack procedures for 1/2/4/8/12/16-bit input, including interleaved variants.
- Sets up clipping forwarding devices and RasterOp texture devices when needed.
- `image_init_clues`, `image_init_colors`, and `image_init_map` initialize color clue caches and sample expansion/decode tables.
- `gx_image_scale_mask_colors` scales ImageType 4 mask color ranges into 8-bit sample space and handles Decode inversion.

Notable dependencies:
- Image class table from `gscdefs.h`.
- Graphics/image state from `gximage.h`, `gxistate.h`, and `gzstate.h`.
- Clipping and RasterOp devices from `gzcpath.h`, `gxdevmem.h`, and `gdevmrop.h`.

Research notes:
- This is the central setup path for ordinary and color-key masked image rendering.
- 12-bit and 16-bit support depends on external `sample_unpack_12_proc` and `sample_unpack_16_proc`; the stub files in this group set them to null.
- RasterOp rewrites can transform some 1-bit image operations into imagemask-style rendering for cheaper execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxipixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiscale.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiscale.c

Interpolated image rendering support for Ghostscript.

Key behavior:
- Provides image class strategy `gs_image_class_0_interpolate`.
- Enables interpolation only for requested, non-mask, portrait images without mask color, alpha, or low-capability target color depth.
- Uses Mitchell filtering by default through `s_IScale_template`; spatial interpolation support is present but disabled.
- Computes stream scale parameters, concrete output color component count, and source/destination dimensions.
- Allocates a combined source/destination line buffer and a stream image scale state.
- Converts input rows to concrete color values when needed, mirrors rows for negative X scale, and feeds the scaling stream.
- `image_render_interpolate` drains scaled rows, remaps concrete samples to device colors, packs pure colors into scanline buffers, and falls back to per-pixel rectangle fills for non-pure device colors.

Notable dependencies:
- Stream interpolation/scaling templates from `siinterp.h` and `siscale.h`.
- Image state from `gximage.h`.
- Device/color mapping helpers from `gxdevice.h`, `gxcmap.h`, and `gxdcolor.h`.

Research notes:
- If interpolation setup is unsupported or allocation/init fails, the strategy clears `penum->interpolate` and lets another renderer handle the image.
- Conservative filtering rules are compiled out by default.
- This Plan 9 version differs from the sibling 9front file in the negative-X 8-bit mirror path: after copying mirrored data it sets `out = q` rather than rounding `out` up to `align_bitmap_mod`, which may matter for the following output-buffer placement.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiscale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxistate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxistate.h

Ghostscript imager state definition.

Key contents:
- Documents the language-independent subset of PostScript graphics state retained by the imager library.
- Defines opaque color rendering dependencies: halftones, device colors, device halftones.
- Defines `gx_transfer` and macros for color rendering state: halftone, screen phase, device halftone, CIE rendering, black generation, undercolor removal, transfer maps, CIE caches, color mapping procs, DeviceN component map, and pattern cache.
- Defines GC/reference-count pointer enumeration macros for color rendering state.
- Defines `gs_imager_state_common`, including memory/client data, line params, CTM, current point, RasterOp, alpha/blend/transparency/soft-mask fields, text knockout, overprint state, flatness/fill/stroke/curve/shading controls, color map proc hook, and color rendering state.
- Provides CTM access macros and inline accessors for flatness, line params, and logical operation.
- Declares initialization, copy, reference-count, assignment, release, and screen phase APIs.

Notable dependencies:
- Line parameters from `gxline.h`.
- Fixed matrices from `gxmatrix.h`.
- Color, transfer, transparency, and RasterOp headers.

Research notes:
- The CTM is stored as `gs_matrix_fixed`, so callers must use `ctm_only` when an API needs a plain `gs_matrix`.
- `effective_transfer` pointers are relocated specially but not GC-enumerated because they alias objects owned/reference-counted elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxistate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxline.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxline.h

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
- `gx_dash_params` is embedded in `gx_line_params` rather than intended for standalone allocation.
- The default miter check constant is precomputed and tied to `gx_set_miter_limit` / stroke behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxlum.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxlum.h

Small Ghostscript luminance constants header.

Key contents:
- Defines RGB luminance weights: red 30, green 59, blue 11.
- Defines `lum_all_weights` as the sum of those weights.

Notable dependencies:
- None beyond normal C preprocessing context.

Research notes:
- These integer weights approximate the common 30/59/11 grayscale conversion convention and are used by color/printer code elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxlum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmatrix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmatrix.h

Internal Ghostscript matrix/fixed-point transformation header.

Key contents:
- Defines `PRECISE_CURRENTPOINT` as enabled.
- Defines `gs_matrix_fixed`, a matrix with cached fixed-point translation values and a validity flag.
- Declares conversion from plain matrix to fixed matrix and coordinate/distance transforms to fixed point.
- Declares rounded fixed-point point transformation when precise currentpoint support is enabled.
- Defines `fixed_coeff`, used to avoid floating point in selected coordinate transformations.
- Declares `fixed_coeff_mult` and defines `m_fixed`, a macro that chooses a faster integer path when the fixed value is in a safe range.

Notable dependencies:
- Plain matrix definitions from `gsmatrix.h`.

Research notes:
- Comments warn that disabling precise currentpoint should not go to production because it drops clamping.
- Fixed coefficient machinery is specialized and called out as primarily used by the Type 1 font interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmatrix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.c

Implementation of Ghostscript mask clipping device initialization and GC support.

Key behavior:
- Defines the public structure descriptor for `gx_device_mask_clip`.
- Enumerates and relocates pointers inside the mask clip device, including embedded strip bitmap, embedded memory device, and forwarding-device prefix.
- Relocation adjusts memory-device line pointers specially because they point into the mask clipping device’s embedded buffer.
- `gx_mask_clip_initialize` initializes a forwarding mask clip device against a target, copies dimensions/color info, sets phase, creates an embedded monochrome memory device, and sizes its buffer within a small fixed internal buffer.
- If the mask tile is too wide to buffer even one scanline, it sets `mdev.base = 0` and returns success so callers can use a slower fallback.

Notable dependencies:
- Device and memory device APIs from `gxdevice.h` and `gxdevmem.h`.
- Structure definition from `gxmclip.h`.

Research notes:
- The implementation avoids separate allocation for the tile buffer by using storage embedded in `gx_device_mask_clip`.
- The too-wide case is intentional and handled by header-side copy-mono fallback logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.h

Mask clipping device structure and helper interface.

Key contents:
- Documents mask clipping use for ImageType 3 images and Patterns that do not fill their bounding box.
- Defines a small aligned tile clip buffer size.
- Defines `gx_device_mask_clip`, a forwarding device containing a mask bitmap, embedded memory device, phase, and aligned buffer.
- Declares the structure descriptor and `gx_mask_clip_initialize`.
- Defines `setup_mask_copy_mono`, a macro for copy-mono implementations to choose mask colors or fall back to default copy-mono behavior.

Notable dependencies:
- `gxclip.h` plus device/memory-device definitions supplied by including context.

Research notes:
- The structure is logically private but exposed so clients can allocate it directly.
- The phase is described as a device-space origin relative to the tile, opposite of graphics state phase semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxobj.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxobj.h

Ghostscript memory manager object header definitions.

Key contents:
- Defines object mark/back field layout and distinguished GC values for unmarked local objects and untraced global objects.
- Defines macros for setting/testing unmarked, untraced, and marked object states.
- Defines `obj_header_data_t`, including alone flag, mark/back union, object size, and type/relocation union.
- Computes object alignment modulus from memory, bitmap, and back-pointer alignment constraints.
- Defines alignment/rounding macros and padded `obj_header_t`.
- Defines object-header field abbreviations and macros to compute object content size, rounded size, and next object when scanning linearly.
- Defines `chunk_head_t`, containing relocation destination and a free object header.

Notable dependencies:
- Bitmap alignment definitions from `gxbitmap.h`.

Research notes:
- This is low-level allocator/GC metadata, not image rendering logic.
- Comments explain the dual use of mark/back data during marking and compaction; interpreting headers requires chunk context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.c

Generic overprint fill-rectangle implementation for Ghostscript devices.

Key behavior:
- Provides scanline pack/unpack helpers for depths below 8 bits and depths that are multiples of 8.
- `gx_overprint_generic_fill_rectangle` handles non-separable color encodings by reading target pixels, decoding source/destination colors, replacing selected process components, re-encoding pixels, and copying modified scanlines back.
- Uses `get_bits_rectangle` options to retrieve native chunky color data without alpha and with standard alignment/raster behavior.
- Provides replicated fill patterns for 2-bit and 4-bit depths plus `replicate_color`.
- `gx_overprint_sep_fill_rectangle_1` handles separable encodings efficiently when color depth divides the fill chunk size, using `bits_fill_rectangle_masked`.
- `gx_overprint_sep_fill_rectangle_2` handles other separable byte-depth cases by byte-wise retain-mask/color merging.
- All routines clip/fix the fill rectangle and allocate temporary scanline buffers.

Notable dependencies:
- Device APIs from `gxdevice.h`, `gsdevice.h`, and `gxgetbit.h`.
- Bitmap/bit helpers from `gsbitops.h`.
- Public declarations from `gxoprect.h`.

Research notes:
- The file describes itself as a very slow generic implementation; faster overprint support should be implemented directly in devices when possible.
- The generic non-separable path is necessarily per-pixel because it decodes, modifies, and re-encodes components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.h

Public/internal interface for generic overprint rectangle fills.

Key contents:
- Declares `gx_overprint_generic_fill_rectangle` for non-separable color encodings.
- Declares `gx_overprint_sep_fill_rectangle_1` for separable encodings where depth can use fill-chunk masking.
- Declares `gx_overprint_sep_fill_rectangle_2` for separable byte-oriented cases such as 24-bit depth.
- Documents byte-swapping expectations for color and retain masks on little-endian machines.

Notable dependencies:
- Requires Ghostscript device, color index, and memory types from including context.

Research notes:
- The interface preserves implementation split by target color encoding rather than by high-level drawing operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxoprect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1fill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1fill.c

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
- Non-simple pattern tiling is conservative for partly transparent patterns: it expands iteration ranges so every overlapping pattern copy can affect the fill.
- A local comment questions a possible leak/memory pointer choice in `tile_fill_init`; the call currently passes `dev->memory` to `tile_clip_initialize`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1fill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1impl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1impl.h

PatternType 1 implementation interface.

Key contents:
- Declares fill rectangle procedures implemented in `gxp1fill.c` for colored patterns and masked pure/binary/colored device colors.
- Declares Pattern color mapping procedures exported by `gxpcmap.c`: `gx_pattern_load` and `gs_pattern1_remap_color`.

Notable dependencies:
- Requires Pattern color definitions from `gxpcolor.h`.

Research notes:
- Uses shortened `masked_fill_rect` naming to stay within historical 32-character identifier limits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxp1impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.c

Ghostscript page queue implementation for coordinating queued band/page rendering work.

Key behavior:
- Defines `gx_page_queue_s`, containing allocator, monitor, queue count, dequeue-in-progress flag, render request/done semaphores, FIFO entry links, and a reserve entry.
- Allocates queue objects and queue entries using Ghostscript memory descriptors.
- `gx_page_queue_init` creates the monitor, semaphores, and reserve entry.
- `gx_page_queue_dnit` drains queued entries, closes page info resources, and frees synchronization objects and reserve entry.
- Low-level add/remove helpers maintain FIFO ordering under the monitor.
- `gx_page_queue_wait_one_page` and `gx_page_queue_wait_until_empty` let producers wait until pending or in-progress rendering completes.
- `gx_page_queue_enqueue` adds an entry and signals the render request semaphore.
- `gx_page_queue_add_page` allocates or consumes the reserve entry, fills action/page info/copy count, enqueues it, then waits until a new reserve entry can be allocated.
- `gx_page_queue_start_dequeue` waits for render requests, marks dequeue in progress, and removes the first entry.
- `gx_page_queue_finish_dequeue` optionally signals render completion, clears dequeue-in-progress, closes clist page resources, frees the entry, and exits the monitor.

Notable dependencies:
- Page queue declarations from `gxpageq.h`.
- Band/page info and clist cleanup from `gxclist.h`.
- Ghostscript monitor/semaphore primitives via device infrastructure.

Research notes:
- The reserve-entry design gives a fallback path when entry allocation fails, allowing a page to still be queued before waiting for memory.
- `gx_page_queue_add_page` documents that an entry may have been queued even if it later returns an error while trying to restore the reserve entry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.c -->