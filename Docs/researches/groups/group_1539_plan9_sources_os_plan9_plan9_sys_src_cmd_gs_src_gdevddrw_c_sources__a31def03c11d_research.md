# Group Research: group_1539_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevddrw_c_sources__a31def03c11d

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.c

Implements Ghostscript default drawing procedures for trapezoids, parallelograms, triangles, thin lines, linear-color shaded fills, and image begin/data/end compatibility dispatch.

Key structures are `trap_line`, which stores exact fixed-point edge stepping state for trapezoid scan conversion, and `trap_gradient`, which stores integer/fractional color-gradient state. The file repeatedly includes `gxdtfill.h` under different macro configurations to generate fill variants for swapped axes, direct/non-direct fills, contiguous fills, and linear-color fills.

Public entry points include `gx_default_fill_trapezoid`, `gx_fill_trapezoid_cf_fd`, `gx_fill_trapezoid_cf_nd`, `gx_default_fill_linear_color_trapezoid`, `gx_default_fill_linear_color_triangle`, `gx_default_fill_parallelogram`, `gx_default_fill_triangle`, `gx_default_draw_thin_line`, `gx_default_begin_image`, `gx_default_begin_typed_image`, `gx_default_image_data`, and `gx_default_end_image`.

Control flow is mostly dispatch and decomposition: rectangles use rectangle fill fast paths, parallelograms and triangles are split into trapezoids, thin horizontal/vertical lines become rectangles, and general thin lines become one-pixel-wide trapezoids. Linear-color trapezoids and triangles check X-gradient overflow, split triangles when needed, and defer scanline painting to device `fill_linear_color_scanline`.

Important dependencies are Ghostscript fixed-point geometry (`gxfixed.h`), device color and procedure tables (`gxdevice.h`, `gxdcolor.h`), image enumeration, and `gxdtfill.h`.

Risks and invariants: fixed-point arithmetic and gradient division are delicate; overflow checks are explicit but narrow. The temporary replacement of device procedures avoids recursion in image dispatch and must be restored on every path. The generated fill variants depend on macro state being correctly undefined between includes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.h

Declares shared default trapezoid-fill interfaces used by Ghostscript drawing code.

It defines `enum fill_trap_flags` with `ftf_peak0`, `ftf_peak1`, and `ftf_pseudo_rasterization`, then exposes `gx_fill_trapezoid_cf_fd` and `gx_fill_trapezoid_cf_nd`. These are the contiguous-fill, non-axis-swapped trapezoid implementations generated in `gdevddrw.c` through `gxdtfill.h`.

The header depends on surrounding Ghostscript types already visible to includers: `gx_device`, `gs_fixed_edge`, `fixed`, `gx_device_color`, and `gs_logical_operation_t`.

Risk is low; this is a narrow prototype header. Correctness depends on the generated implementations in `gdevddrw.c` matching the declared signatures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevddrw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.c

Implements common DeviceN/spot-color utilities and two example printer devices: `spotcmyk` and `devicen`.

The shared utilities convert Gray/RGB/CMYK input into DeviceN component arrays using a separation-order map, compute device depth from component count and bits per component, match process/separation colorant names, auto-add spot separations, read/write `SeparationColorNames`, `SeparationOrder`, `MaxSeparations`, and wrap printer parameter updates with rollback on failure.

Device definitions use `spotcmyk_device`, with GC pointer relocation for allocated separation-name strings. `gs_spotcmyk_device` is a 1-bit-per-component CMYK-plus-spot sample; `gs_devicen_device` is an 8-bit DeviceN sample. Both use separation-aware color mapping procs, custom `encode_color`/`decode_color`, and `spotcmyk_get_color_comp_index`.

`spotcmyk_print_page` demonstrates output decomposition: it extracts process-color-model data and individual spot planes from packed scan lines using `repack_data`, writes raw sidecar files, then converts those files to PCX through local PCX header, palette, page, and RLE helpers.

Important dependencies are printer devices (`gdevprn.h`), CRD params, DeviceN declarations in `gdevdevn.h`, equivalent CMYK tracking (`gsequivc.h`), and standard Ghostscript parameter APIs.

Risks: many allocations for separation names are appended without local cleanup on parameter replacement paths. Output filenames are built with `sprintf` from `pdevn->fname`. PCX support is intentionally incomplete for many plane/depth combinations. The sample print path creates multiple files and assumes normal filesystem output, not stdout-like targets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.h

Defines shared DeviceN data structures, limits, constants, and utility prototypes.

Core limits are `GX_DEVICE_MAX_SEPARATIONS` at 16 spot colors and `MAX_DEVICE_PROCESS_COLORS` at 6 process colorants. `gs_devn_params_t` stores bits per component, standard process colorant names, `MaxSeparations`, separation-name arrays, and the separation-order map. The header also declares `DeviceCMYKComponents`.

It exposes color-space conversion helpers, automatic spot-color policy constants (`NO_AUTO_SPOT_COLORS`, `ENABLE_AUTO_SPOT_COLORS`, `ALLOW_EXTRA_SPOT_COLORS`), colorant lookup, parameter get/put routines, process/separation name checking, `repack_data`, and `bpc_to_depth`.

Integration is broad: DeviceN-capable devices embed `gs_devn_params` and optionally `equivalent_cmyk_color_params`, then delegate their parameter and colorant-name behavior to these helpers.

Risks: the APIs assume callers maintain consistent `color_info`, separation maps, and allocation lifetime. The comments document that some routines may modify device state without rollback unless callers use the printer wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdfax.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdfax.c

Defines DigiBoard DigiFAX low- and high-resolution fax devices.

The file declares `gx_device_dfax`, adding a page counter and image width field to printer-device state. It registers `gs_dfaxlow_device` at 204 x 98 dpi and `gs_dfaxhigh_device` at 204 x 196 dpi. Both share `dfax_prn_open` and `dfax_print_page`.

`dfax_prn_open` resets `pageno` and delegates setup to `gdev_fax_open`. `dfax_print_page` initializes CCITT fax encoding state with EOL and byte alignment enabled, writes a DigiFAX-specific header, emits the fax page via `gdev_fax_print_page`, then seeks back to update the total page count in the file header.

Dependencies are Ghostscript printer/fax infrastructure: `gdevprn.h`, `scfx.h`, `gdevfax.h`, and `gdevtfax.h`.

Risks: the format relies on seekable output because it rewrites the page count at offset 24. The static header is mutated per page. There is no explicit checking of `fseek`/`fwrite` failures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdflt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdflt.c

Provides Ghostscript’s default device procedure implementation and color-model inference/fallback logic.

The file derives default `encode_color` and `decode_color` procedures from device color information, old-style mapping procs, polarity, and separable/linear flags. It can recognize DeviceRGB-like and DeviceCMYK-like mappings by probing sample colors, includes gray and CMYK fallback decoders, and has a special 1-bit CMYK decoder.

`set_linear_color_bits_mask_shift` initializes per-component bit fields for separable linear devices. `check_device_separable` probes `encode_color` with zero and max component values to infer non-overlapping component masks, shifts, and bit widths.

`gx_device_fill_in_procs` fills missing device procs with defaults: open/close/output, matrix, copy/fill/path/stroke, trapezoid/parallelogram/triangle/thin-line from `gdevddrw.c`, image begin/data/end compatibility wrappers, get-bits routines, compositors, pattern management, color-space inclusion, linear-color fills, and spot-equivalent-color update. It also installs default color mapping and component-index procedures for Gray, RGB, CMYK, or error cases.

Other defaults include initial matrices for inverted/upright Y, sync/output/close stubs, clipping boxes, compositor creation, copydevice validation, page install/begin/end hooks, and no-op pattern/color-space handlers.

Risks: this file is central to device behavior. Incorrect inferred polarity or separability affects overprint, halftoning, shading, and color encoding. Many defaults are intentionally best-effort compatibility paths for older devices and may be approximate.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdflt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdgbr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdgbr.c

Implements default `get_bits` and `get_bits_rectangle` behavior, including conversion between native device pixels and standard Gray/RGB/CMYK representations.

`gx_default_get_bits` converts a one-scanline request into `get_bits_rectangle`, temporarily replacing `get_bits` with `gx_no_get_bits` to avoid recursion. `gx_default_get_bits_rectangle` does the reverse when possible, using `get_bits` for simple one-row native chunky requests, otherwise recursively pulling rows and calling `gx_get_bits_copy`.

`gx_get_bits_return_pointer` checks whether requested options are compatible with stored representation and, if alignment permits, returns direct pointers into stored data. `gx_get_bits_copy` handles direct bit copies, shifted bit copies through a memory device, planar extraction, and native/standard color conversion.

Conversion helpers map standard colors to native by using device color mapping and `encode_color`, and native to standard by using `map_color_rgb_alpha`. There is a dedicated 4-bit CMYK to 24-bit RGB fast path for common PCL usage.

Dependencies include bitmap sample load/store macros, memory devices, `gxgetbit.h`, luminance weights, and device color mapping procs.

Risks: option handling is complex and alignment-sensitive. Several paths allocate temporary row buffers. Only 8-bit standard output depth is supported for native-to-standard conversion, with rangecheck for unsupported cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdgbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjet.c

Defines a family of monochrome HP DeskJet, LaserJet, Kyocera FS-600, HP 2563B, and OCE 9050 printer devices.

The custom `gx_device_hpjet` extends printer state with `MediaPosition` and `ManualFeed` parameters plus “set” flags. Device descriptors include `deskjet`, `djet500`, `fs600`, `laserjet`, `ljetplus`, `ljet2p`, `ljet3`, `ljet3d`, `ljet4`, `ljet4d`, `lp2563`, and `oce9050`.

`hpjet_open` selects margins based on device family and paper size, enables duplex defaults for duplex models, and delegates to `gdev_prn_open`. `hpjet_close` emits final form/reset behavior, including odd duplex page ejection logic. `hpjet_make_init` injects paper tray/manual feed selection into page initialization strings.

Each `*_print_page_copies` routine supplies model-specific PCL initialization, resolution, and feature flags to `dljet_mono_print_page_copies` from `gdevdljm.c`. OCE output additionally switches between HPGL/2 and PCL modes.

Parameter handling exposes `ManualFeed` and reads `%MediaSource`, preserving values only after `gdev_prn_put_params` succeeds.

Risks: PCL command strings are device-specific and tightly coupled to feature flags. Init buffers are fixed-size but appear sized for local strings. Some devices leave margins to be filled dynamically, so open-time setup is required.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjtc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjtc.c

Implements the HP DeskJet 500C color printer device.

The device `gs_djet500c_device` is a 300 dpi, 3-bit RGB PCL printer using `gdev_pcl_3bit_map_rgb_color` and `gdev_pcl_3bit_map_color_rgb`. Compile-time defaults control shingling and depletion.

`djet500c_print_page` sends printer reset/setup commands, configures RGB raster mode, depletion, shingling, cursor position, and mode 2 compression. For each scan line it reads packed 3-bit RGB pixels, trims trailing zeros, transposes bytes into separate R, G, and B one-bit planes, skips blank lines, compresses each plane, and writes PCL raster-transfer commands in R/G/B order.

`mode2compress` is a local PackBits-style PCL mode 2 compressor supporting literal and repeated byte runs up to 127 bytes.

Dependencies are Ghostscript printer/PCL helpers plus direct `malloc`/`free`.

Risks: allocations use C library `malloc` rather than Ghostscript memory management. The print routine returns success even if allocation of plane buffers fails later would be problematic; it assumes allocations succeed after size checks. It is tuned for 300 dpi DeskJet 500C behavior and PCL mode 2.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.c

Provides the generic monochrome HP DeskJet/LaserJet PCL page emitter used by `gdevdjet.c`.

`dljet_mono_print_page` is a one-copy wrapper. `dljet_mono_print_page_copies` allocates working rows, initializes the printer and page, sets paper size/duplex/copy count when supported, starts raster graphics, reads each printer scan line, skips blank lines, chooses cursor movement or blank raster rows, and writes compressed or raw raster data.

Compression logic selects PCL mode 3 vs mode 2 per nonblank row when both are available, accounting for the cost of switching modes. It uses `gdev_pcl_mode3compress`, `gdev_pcl_mode2compress`, and a previous-row seed buffer. Unsupported printer-copy hardware falls back to default software copy output.

Important inputs are `dots_per_inch`, feature bit flags from `gdevdljm.h`, and a model-specific page initialization string.

Risks: the routine assumes enough memory for four row buffers and uses many PCL side effects. Correct blank-line skipping depends on printer feature flags, especially mode 3 seed-row clearing and no-spacing variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.h

Defines the interface and feature matrix for the generic monochrome HP DeskJet/LaserJet PCL driver.

The header documents that “PCL printer” support is feature-based rather than uniform. It defines spacing modes (`PCL_NO_SPACING`, `PCL3_SPACING`, `PCL4_SPACING`, `PCL5_SPACING`), compression support (`PCL_MODE_2_COMPRESSION`, `PCL_MODE_3_COMPRESSION`), and device properties such as raster reset behavior, duplex, paper size setting, and hardware copies.

It then composes known feature sets for DeskJet, DeskJet 500, FS-600, LaserJet variants, HP 2563B, and OCE 9050. These constants are consumed by `gdevdjet.c`.

Exports are `dljet_mono_print_page` and `dljet_mono_print_page_copies`.

Risk is low in code terms, but incorrect feature flags directly produce invalid printer command sequences or inefficient output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdljm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdm24.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdm24.c

Implements high-resolution 24-pin dot-matrix printer drivers for NEC P6-compatible and Epson LQ850-compatible devices.

The file registers `gs_necp6_device` and `gs_lq850_device`, both 360 x 360 dpi monochrome printer devices with shared `dot24_print_page` and model-specific initialization strings.

`dot24_print_page` allocates input scanline blocks and output column buffers, initializes the printer, skips blank vertical space, gathers 24 or 48 scan lines depending on Y resolution, uses `memflip8x8` to rotate raster bits into 24-pin vertical columns, trims trailing zeros, optionally tabs across long blank horizontal runs, emits graphics runs, and ejects/reset the page.

`dot24_improve_bitmap` handles 360 dpi horizontal limitations by clearing the second-last pixel in adjacent runs so the last pixel remains printable. `dot24_output_run` writes the ESC `*` graphics command.

Risks: this is hardware-tuned raster emission. Memory allocation uses older `gs_malloc`/`gs_free` style. Correct output depends on printer emulation supporting the exact ESC/P-like commands and on `memflip8x8` semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdm24.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdrop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdrop.c

Implements default device-independent RasterOp (`copy_rop` / `strip_copy_rop`) algorithms.

For non-memory devices, `gx_default_strip_copy_rop` reads destination pixels with `get_bits_rectangle` when the RasterOp uses destination data, performs the operation on a temporary memory device, then writes results back with `copy_color`. Work is chunked by `max_rop_bitmap` to bound temporary allocation.

For memory devices, `mem_default_strip_copy_rop` converts destination/source/texture operands into standard 8-bit gray or 24-bit RGB memory-device form when needed, delegates the operation to the standard memory-device RasterOp, then packs results back into the original device format. It special-cases 1-bit CMYK packing and maps color constants through standard RGB.

The file also adapts tile-based `copy_rop` to strip texture form, handles unaligned source data by offset/raster adjustment or one-line fallback, and computes effective transparent RasterOps in `gs_transparent_rop`.

Debug builds include `trace_copy_rop` for logging operand geometry and optional bitmap dumps.

Risks: RasterOp semantics are subtle, especially transparency masking and standard/native color conversions. Temporary memory use is bounded but still allocation-dependent. Unaligned source adjustment has special cases for 24-bit data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsha.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsha.c

Provides the default linear-color scanline fill procedure used by shading fallback paths.

`gx_default_fill_linear_color_scanline` receives a scanline span, starting component colors, fractional gradient state, gradient numerators, and denominator. It walks pixels left to right, incrementally updates each component, encodes component values into a `gx_color_index` using the device’s `comp_shift` and `comp_bits`, and groups consecutive pixels with identical encoded color into rectangle fills.

The function honors clipping and supports `swap_axes`, emitting either horizontal rectangles or transposed vertical rectangles through the device `fill_rectangle` proc. It also emits visual-debug rectangle traces through `vd_rect`.

Dependencies are the device color-info bit layout initialized by separable/linear color setup and default rectangle fill support.

Risks: this fallback assumes meaningful `comp_shift`/`comp_bits` for the target device. It is correct but potentially slow because it decomposes gradients into many constant-color rectangles rather than writing pixels directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsha.c -->