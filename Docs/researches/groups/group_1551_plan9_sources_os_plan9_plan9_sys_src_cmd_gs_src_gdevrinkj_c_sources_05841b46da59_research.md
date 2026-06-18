# Group Research: group_1551_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevrinkj_c_sources_05841b46da59

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrinkj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrinkj.c

Purpose: Ghostscript printer device glue for the Rinkj inkjet pipeline, defaulting to a CMYK/DeviceN-style `rinkj` device at 720 dpi.

Key behavior:
- Defines `rinkj_device`, extending Ghostscript printer device state with color model, component names, separations, ICC output profile, setup file, and Rinkj setup state.
- Registers a mostly printer-forwarding device proc table, with custom params, color mapping, component lookup, color encode/decode, and `rinkj_print_page`.
- Supports `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN` color model selection via `ProcessColorModel`.
- Exposes and reads `ProfileOut`, `SetupFile`, `SeparationColorNames`, and separation-related params.
- Converts Ghostscript colorants to packed color indices and back, and provides mapping procs for RGB/CMYK/DeviceN workflows.
- Opens ICC profiles with the Argyll/ICC API and uses lookup objects for RGB/CMYK-to-CMYK conversion during output.
- Parses a Rinkj setup/config file, applying printer params and chained LUTs for planes named `KkCMcmY`.
- Builds an output chain `FILE -> RinkjByteStream -> Epson870 device -> screen/error-diffusion device`.
- During page output, pulls printer raster rows, splits planes, optionally applies ICC conversion with a 64K direct-mapped color cache, handles a 5th spot channel blend case, and writes split plane data.

Important dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gsparam.h`, color mapping structs, `gxdcconv.h`.
- ICC API: `icc.h`.
- Bundled Rinkj APIs: `rinkj-device`, `rinkj-byte-stream`, `rinkj-screen-eb`, `rinkj-epson870`.

Notable risks / findings:
- `rinkj_color_hash(color)` is called before `color` is assigned in the 3-plane and 5-plane ICC paths; this makes cache lookup undefined.
- `plane_data` allocates `n_planes_out` entries but frees only `n_planes_in`; RGB input with four output planes can leak.
- `gs_rinkj_device` initialization appears structurally suspicious: the initializer sequence after `bitspercomponent` does not visibly account for `n_planes_out`.
- LUT chain allocations are acknowledged as not freed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrinkj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrops.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrops.c

Purpose: Implements a small forwarding “RasterOp source” device used to combine a target device, texture device color, source pixels, and a logical operation.

Key behavior:
- Defines GC enum/relocation support for `gx_device_rop_texture`.
- Provides `gx_alloc_rop_texture_device` and `gx_make_rop_texture_device` to allocate and initialize the wrapper around a target device.
- The device forwards non-drawing operations to the target and intercepts rectangle fill, mono copy, and color copy.
- `rop_texture_fill_rectangle` builds a constant-color source and calls `gx_device_color_fill_rectangle`.
- `rop_texture_copy_mono` builds a bitmap source and adjusts the logical operation when either mono color is transparent.
- `rop_texture_copy_color` builds a color bitmap source with `use_scolors = false`.

Important dependencies:
- Ghostscript device/color internals: `gxdcolor.h`, `gxdevice.h`, `gdevmrop.h`.

Notable risks / findings:
- This file is infrastructure-only and has no filesystem relevance beyond being part of the Plan 9 Ghostscript source tree.
- Correctness depends on the target device and `gx_device_color_fill_rectangle` honoring the composed RasterOp semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevrops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevs3ga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevs3ga.c

Purpose: Ghostscript display driver for S3 86C911/S3 VGA hardware acceleration.

Key behavior:
- Defines `gs_s3vga_device` using shared SVGA support and VESA mode get/set hooks.
- Supports fixed enhanced modes 640x480, 800x600, and 1024x768; uses a 1024-pixel framebuffer raster.
- Tracks a bitmap/character cache in off-screen memory with 32x32 cells.
- Drives S3 registers directly through port I/O for rectangle fills and mono bitmap copies.
- `s3_fill_rectangle` emits hardware rectangle fill commands.
- `s3_copy_mono` handles transparent foreground/background colors, source bit alignment, direct CPU-to-screen transfer, and cached screen-to-screen character blits.

Important dependencies:
- PC framebuffer/SVGA support: `gdevpcfb.h`, `gdevsvga.h`.
- Low-level port I/O macros/functions from the PC framebuffer layer.

Notable risks / findings:
- Hardware-specific driver using direct I/O ports; not portable and only meaningful on old S3 VGA environments.
- Cache placement assumes off-screen memory at y offset 768 and a 1024-pixel raster.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevs3ga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsco.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsco.c

Purpose: SCO Xenix/Unix and SVR4 console/framebuffer backend for Ghostscript PC framebuffer devices.

Key behavior:
- Opens the console device from `GSDEVICE` or defaults to `/dev/tty`.
- Provides non-GCC port output helpers using `CONSIO` ioctl.
- Installs signal handlers to restore video mode on interrupt/termination and exits on stop/continue signals rather than trying to resume graphics state.
- `pcfb_get_state` maps SCO console modes to BIOS-like display modes.
- `pcfb_set_mode` maps BIOS-like modes to SCO/SVR4 console mode ioctls, requests VGA I/O privilege when available, and maps console framebuffer memory via `MAPCONS`.
- `pcfb_set_state` restores the saved display mode.

Important dependencies:
- SCO/Xenix or SVR4 console headers and ioctls: `sys/console.h`, `sys/machdep.h`, `sys/kd.h`.
- Shared Ghostscript PC framebuffer API from `gdevpcfb.h`.

Notable risks / findings:
- Uses process-global console state and exits the process on many errors.
- Signal handling is intentionally crude for stop/continue cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsco.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.c

Purpose: Ghostscript printer-style output device that writes SGI RGB raster image files.

Key behavior:
- Defines `sgirgb`, a 24-bit RGB printer device at 72 dpi.
- Implements RGB color index packing/unpacking according to device depth.
- Writes an SGI image header with magic `IMAGIC`, RLE type, dimensions, 3 channels, and normal colormap.
- Reserves row-start and row-size tables, then emits channel-separated RLE data bottom-up.
- Encodes each R/G/B separation independently with SGI-style RLE packets and later seeks back to fill the offset/size tables in big-endian byte order.

Important dependencies:
- Ghostscript printer API and SGI image definitions from `gdevsgi.h`.

Notable risks / findings:
- Allocation failure paths can return without freeing allocations already made in `sgi_begin_page`.
- Uses `bzero` and manual `fseek`/`fwrite` table patching typical of older C code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.h

Purpose: Header for SGI raster file constants and the SGI `IMAGE` structure used by `gdevsgi.c`.

Key contents:
- Defines SGI image magic `IMAGIC`, colormap constants, type masks, RLE/verbatim encoding macros, and helper macros for image stream buffering.
- Defines `IMAGE`, containing the on-disk SGI header fields followed by in-core state used by SGI image routines.

Important dependencies:
- Consumed directly by `gdevsgi.c`.

Notable risks / findings:
- `IMAGE` mixes serialized fields and runtime-only fields; `gdevsgi.c` writes `sizeof(IMAGE)` then pads to 512 bytes, so structure layout and host ABI affect the emitted header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsj48.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsj48.c

Purpose: Ghostscript printer driver for the StarJet SJ48 printer.

Key behavior:
- Defines `sj48`, an 8x10.5 inch monochrome printer device defaulting to 360x360 dpi.
- Supports only 180/360 dpi combinations in each axis and chooses SJ48 graphics modes 39, 40, 71, or 72.
- Allocates input scanline and transposed output buffers.
- Skips blank scanlines vertically using `ESC J`.
- Converts scanlines into vertical column graphics blocks using `gdev_prn_transpose_8x8`.
- Skips blank horizontal column groups with `ESC \`.
- Emits graphics blocks with `ESC *`, carriage returns after passes, and form feed at page end.

Important dependencies:
- Ghostscript printer helpers: raster sizing, scanline copying, 8x8 transpose.

Notable risks / findings:
- Strictly printer-protocol code; no local filesystem logic.
- Error path flushes/ejects via form feed once output has begun.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsj48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsnfb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsnfb.c

Purpose: Sony NEWS framebuffer output device for Ghostscript.

Key behavior:
- Defines `sonyfb`, a 1-bit printer-style framebuffer device sized for a 1024x1032-ish 100 dpi surface.
- Opens `/dev/fb`, obtains screen type with `FBIOCGETSCRTYPE`, and stores the visible rectangle.
- On output, maps Ghostscript printer memory as a monochrome memory bitmap.
- Builds a `sPrimRect` operation from memory bitmap to framebuffer bitmap using `BF_S`.
- Issues `FBIOCRECTANGLE` to copy the rendered page into the framebuffer, then finishes the Ghostscript output page.

Important dependencies:
- Sony NEWS framebuffer API: `<newsiop/framebuf.h>`.
- Ghostscript printer memory buffer internals.

Notable risks / findings:
- If `/dev/fb` open or ioctls fail, the code prints `perror` but may continue to printer open/output paths.
- Uses GCC-style `typeof`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsnfb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsppr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsppr.c

Purpose: Ghostscript driver for Sun SPARCprinter devices using the LPVI ioctl interface.

Key behavior:
- Defines `sparc`, a 400 dpi monochrome printer device.
- `sparc_open` chooses A4 vs letter-style margins from page height and opens the printer device.
- `sparc_print_page` obtains and sets LPVI page metadata, copies the whole rendered bitmap into memory, and writes it to the printer file descriptor.
- On partial/failed writes, polls `LPVIIOC_GETERR`.
- Treats warning errors as retryable after sleeping 5 seconds; fatal/interface errors abort.
- Maintains a global `warning` flag to print “OK” after recovery.

Important dependencies:
- Sun printer ioctls from `<unbdev/lpviio.h>`.
- Ghostscript printer buffer copy helpers.

Notable risks / findings:
- If write fails after `out_buf` allocation and an error path returns, the buffer is not freed.
- Uses a global warning state and blocking sleeps inside output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsppr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.c

Purpose: Main Ghostscript Epson Stylus Color / ESC/P2 printer driver.

Key behavior:
- Defines `stcolor`, defaulting to a CMYK direct 360x360 dpi printer device with configurable margins.
- Maintains a table of dithering algorithms: built-ins `gscmyk`, `hscmyk`, plus algorithms declared in `gdevstc.h` (`gsmono`, `gsrgb`, `fsmono`, `fsrgb`, `fsx4`, `fscmyk`, `fs2`).
- Builds default ESC/P2 initialization and release command strings when user params do not provide them.
- Main `stc_print_page` allocates scanline, algorithm, dither buffer, printer line buffers, seed rows, and ESC/P2 command buffer.
- Reads Ghostscript scanlines, detects white rows, converts input depth to algorithm data, invokes dithering, splits output into mono/RGB/CMYK printer planes, and emits printer bands.
- Supports plain, run-length, and delta-row output encodings.
- Implements software weave/multipass printing, single-pass bands, and delta-row printing.
- Builds ESC/P2 positioning/color/data commands, including color selection and linefeed adjustments.
- Generates transfer/code lookup arrays from user-provided coding/transfer curves and optional color adjustment matrices.
- Dynamically installs appropriate color mapping procs for gray, RGB, CMYK, or special CMYK10 modes.
- Provides parameter get/put support for version, algorithm list, model, output coding, weave flags, ESC/P2 control values, custom init/release strings, color adjustment matrix, and component coding/transfer arrays.
- Includes built-in direct 1-bit CMYK splitting (`stc_gscmyk`) and experimental CMYK10 halftone/dither (`stc_hscmyk`).

Important dependencies:
- Shared declarations and algorithm registry in `gdevstc.h`.
- Algorithm implementations in `gdevstc1.c`, `gdevstc2.c`, `gdevstc3.c`, and `gdevstc4.c`.
- Ghostscript printer, parameter, and device color APIs.

Notable risks / findings:
- `stc_freedata(gs_memory_t *mem, stc_t *stc)` references `sd->stc.alg_item` even though `sd` is not in scope, which appears to be a compile-time defect in this source as read.
- Many error paths manually unwind allocations; this file is high-risk for leaks or stale pointers if modified.
- `put_params` mutates complex device state, then conditionally restores or frees old state; changes here need careful open/close lifecycle testing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.h

Purpose: Shared declarations and constants for the Epson Stylus Color driver family.

Key contents:
- Defines `stc_pixel`, `stc_t`, and `stcolor_device`.
- `stc_t` holds flags, bits/component, current dither algorithm, color adjustment matrix, coding/transfer arrays, computed lookup arrays, white-line patterns, exposed algorithm list, ESC/P2 strings/settings, print buffer sizes/state, buffered raster data, and delta-row seed buffers.
- Defines driver flags for algorithm selection bits, CMYK10, weave modes, compression modes, model variants, explicit ESC/P2 parameter overrides, and print state.
- Defines `stc_dither_t` and `stc_proc_dither`.
- Declares color constants for gray/RGB/CMYK output bytes.
- Provides `STC_TYPESWITCH` for byte/long/float algorithm buffer handling.
- Declares external dithering algorithms and assembles them into `STC_MODI`.
- Defines defaults for 360 dpi and paper margins.

Important dependencies:
- Included by the main driver and all Stylus dithering implementation files.

Notable risks / findings:
- Central coupling point: changes to flags, `STC_MODI`, or `stc_t` affect all Stylus driver files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc1.c

Purpose: Simple monochrome “dithering” algorithm for `stcolor`, exposed as `gsmono`.

Key behavior:
- For positive `npixel`, copies byte input directly to output.
- For white-line notifications (`in == NULL`), clears the output line.
- For initialization calls (`npixel <= 0`), clears any algorithm buffer and validates that the device has one component, uses byte data, and is not direct.
- Intended to let Ghostscript perform the actual 1-bit monochrome work.

Important dependencies:
- `gdevstc.h` for device state, algorithm contract, and flags.

Notable risks / findings:
- Minimal algorithm; behavior is intentionally pass-through.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc2.c

Purpose: Floyd-Steinberg error diffusion algorithms for the Epson Stylus Color driver.

Key behavior:
- Provides `stc_fs` for gray/RGB/CMYK-style per-component Floyd-Steinberg dithering using long error buffers.
- Converts internal bit decisions to driver output bytes with gray, RGB, or CMYK conversion tables.
- Alternates scan direction forward/backward using buffer state.
- Initializes threshold, spot size, and randomized or zeroed error buffers depending on `Flag0`.
- Provides `stc_fscmyk`, a modified CMYK algorithm that handles black first, then colors differently depending on whether black fires.
- `stc_fscmyk` validates four components, long data, sufficient buffer, and no direct/white flags.

Important dependencies:
- `gdevstc.h`, plus `rand()` from `<stdlib.h>`.

Notable risks / findings:
- Randomized initial error state means output can depend on C library RNG state unless `Flag0` disables it.
- CMYK behavior is specialized and documented as experimental/bad for some modes in the comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc3.c

Purpose: Simple RGB pass-through/merge algorithm for `stcolor`, exposed as `gsrgb`.

Key behavior:
- For each pixel, consumes three byte components and emits one output byte containing `RED`, `GREEN`, and `BLUE` bits.
- On initialization, validates no white-line callbacks, byte data, exactly three color components, and non-direct input.

Important dependencies:
- `gdevstc.h`.

Notable risks / findings:
- No actual error diffusion; Ghostscript is expected to provide already-thresholded component bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc4.c

Purpose: Byte-oriented Floyd-Steinberg-style RGB dithering algorithm for `stcolor`, exposed as `fs2`.

Key behavior:
- Chooses nearest printable color among 8 RGB cube corners with a custom distance metric intended to avoid color artifacts in gray areas.
- Converts RGB triplets into `stcolor` bit-coded output bytes.
- Maintains byte error buffer and alternates direction between scanlines using a static `dir`.
- Handles white-line callbacks by clearing the error buffer.
- During processing, applies accumulated error to input, clamps values, selects nearest output color, diffuses error horizontally and to the next row, and writes compact output.
- Initialization validates RGB mode, byte algorithm type, and at least one scanline of buffer.

Important dependencies:
- `gdevstc.h`.

Notable risks / findings:
- Uses a static `dir`, so direction state is global across device instances/jobs rather than per-device.
- Mutates the input scanline buffer during dithering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsun.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsun.c

Purpose: Ghostscript display driver for SunView windows.

Key behavior:
- Defines `sunview`, a display device sized like paper at default 75 dpi.
- Creates a SunView frame and canvas, optionally requesting 24-bit color support.
- Detects monochrome, 8-bit pseudo-color, and true-color display depths and installs matching Ghostscript color info.
- For pseudo-color, allocates a private colormap with black/white plus a preallocated RGB cube, then dynamically allocates exact colors until the map fills.
- For true-color, encodes RGB components directly into the color index.
- Prevents user window close through a destroy hook.
- Implements sync, close, RGB color mapping, reverse color mapping, rectangle fill, mono bitmap stencil copy, color bitmap copy, and line draw.
- On little-endian systems, reverses mono bitmap bit order before Sun pixrect stencil operations and restores it after drawing.

Important dependencies:
- SunView/SunWindows APIs: `suntool/sunview.h`, `suntool/canvas.h`, `sunwindow/cms_mono.h`.
- Ghostscript device API and pixrect memory operations.

Notable risks / findings:
- `sun_copy_mono` intentionally casts away const and mutates caller-provided bitmap data temporarily.
- Comments warn pseudo-color fallback can loop forever if Ghostscript requests colors outside the preallocated cube after the colormap is full.
- The `#endif ./* FAKE_TRUE_COLOR */` directive has unusual trailing tokens.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsun.c -->