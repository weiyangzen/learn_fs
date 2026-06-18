# Group Research: group_113_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevrinkj_c_source_b643ff543dfa

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrinkj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrinkj.c

## Purpose
Ghostscript printer device for the Rinkj “resplendent inkjet” pipeline. It exposes a DeviceN-capable `rinkj` printer device, maps Ghostscript color spaces into RGB/CMYK/DeviceN colorants, optionally applies an ICC output profile, reads an external setup file for Rinkj/Epson parameters and LUTs, and writes raster planes through the Rinkj device stack.

## Main Structures And Entry Points
- `rinkj_device` extends `gx_device_common` and `gx_prn_device_common`.
- Tracks color model, bits per component, standard colorant names, separation names/order, ICC profile filename/object, and setup filename.
- Public device instance: `gs_rinkj_device`.
- Device procedures:
  - `rinkj_get_params`
  - `rinkj_put_params`
  - `rinkj_print_page`
  - `rinkj_map_color_rgb`
  - `get_rinkj_color_mapping_procs`
  - `rinkj_get_color_comp_index`
  - `rinkj_encode_color`
  - `rinkj_decode_color`

## Behavior
- Defaults to CMYK DeviceN-like output with 8 bits per component and 720 DPI unless overridden.
- Supports `ProcessColorModel` values `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN`.
- Filters `SeparationColorNames` so process colorants are not duplicated as spots.
- `ProfileOut` opens an ICC profile via `icc.h` APIs and stores an output lookup object.
- `SetupFile` is parsed by `rinkj_set_luts`; keys such as `AddLut`, `Dither`, and `Aspect` configure either the screening device or Epson device.
- `rinkj_init` builds a byte-stream-backed Epson 870 device and wraps it with `rinkj_screen_eb`.
- `rinkj_write_image_data` copies Ghostscript scanlines into planar arrays, optionally performs ICC conversion with a small direct-mapped cache, replicates CMYK planes into CMYKcmk output, and calls `rinkj_device_write`.

## Dependencies
- Ghostscript printer/color infrastructure: `gdevprn.h`, `gsparam.h`, `gscrd.h`, `gdevdcrd.h`, `gxdcconv.h`.
- ICC support: `icc.h`.
- Rinkj internals:
  - `rinkj/rinkj-device.h`
  - `rinkj/rinkj-byte-stream.h`
  - `rinkj/rinkj-screen-eb.h`
  - `rinkj/rinkj-epson870.h`

## Notable Risks
- `rinkj_set_luts` calls `fopen(config_fn, "r")` but does not check for `NULL` before `fgets`; an unset or invalid `SetupFile` can crash.
- In the ICC conversion branches for 3-plane and 5-plane input, `bits32 color` is hashed before it is assigned, so cache lookup uses an uninitialized key.
- `n_planes` is computed as `n_planes_in + separation_names.num_names`, although `color_info.num_components` already appears to include separations after `rinkj_put_params`; this can make row indexing inconsistent for spot-color cases.
- Only four `plane_data` buffers are allocated, but freeing loops over `n_planes_in`; DeviceN configurations with more than four components can free uninitialized pointers.
- Setup-file LUT chains are explicitly not freed.
- Several allocation failures in LUT construction are not fully unwound.

## Filesystem Relevance
Not filesystem code. It is part of the bundled Ghostscript command source tree and performs printer output file/stream writes plus optional configuration/profile file reads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrinkj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrops.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrops.c

## Purpose
Implements a Ghostscript forwarding source device used for RasterOp texture/source composition. It wraps a target device and a `gx_device_color` texture, then translates fill/copy operations into `gx_device_color_fill_rectangle` calls with a raster-op source descriptor.

## Main Structures And Entry Points
- Device type: `gx_device_rop_texture`.
- Static descriptor: `gs_rop_texture_device`.
- Allocation and initialization:
  - `gx_alloc_rop_texture_device`
  - `gx_make_rop_texture_device`
- Drawing callbacks:
  - `rop_texture_fill_rectangle`
  - `rop_texture_copy_mono`
  - `rop_texture_copy_color`
- Includes GC pointer enumeration/relocation for embedded texture and forwarding device fields.

## Behavior
- For solid fills, builds a `gx_rop_source_t` with both source colors set to the fill color.
- For monochrome copy, stores bitmap pointer, source offset, raster, bitmap id, and source colors.
- Transparent mono colors adjust the logical operation through `rop3_use_D_when_S_0` or `rop3_use_D_when_S_1`.
- For color copies, passes raw source bitmap data and disables source-color use.

## Dependencies
- Ghostscript device internals: `gxdevice.h`, `gxdcolor.h`.
- RasterOp helpers: `gdevmrop.h`.

## Notable Risks
- This device assumes the target and texture are valid and initialized by callers.
- `gx_no_copy_rop` and related callbacks are marked “shouldn't be called”; misuse through unexpected device procedure paths would fail.

## Filesystem Relevance
No filesystem logic. This is an in-memory Ghostscript compositing helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevrops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevs3ga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevs3ga.c

## Purpose
Ghostscript display driver for S3 86C911 VGA hardware. It uses VESA/SVGA setup and direct hardware port I/O to accelerate fills and monochrome bitmap copies.

## Main Structures And Entry Points
- Public device: `gs_s3vga_device`.
- Device procedures:
  - `s3_open`
  - `s3_fill_rectangle`
  - `s3_copy_mono`
- Uses `svga_close`, `svga_map_rgb_color`, `svga_map_color_rgb`, `svga_copy_color`, and `svga_get_bits` from shared SVGA code.
- Maintains an off-screen character bitmap cache with `cache_ids`.

## Behavior
- `s3_open` selects one of 640x480, 800x600, or 1024x768 enhanced modes and assumes a 1024-pixel raster.
- `s3_fill_rectangle` programs foreground mix/color, multi-function control, rectangle coordinates, and S3 command register.
- `s3_copy_mono` supports direct CPU-to-screen transfers and cached glyph transfers from off-screen memory.
- Handles transparent foreground/background colors by choosing S3 foreground/background mix values.
- Accounts for unaligned source bits with masks and merge behavior.

## Dependencies
- Ghostscript PC framebuffer/SVGA support: `gdevpcfb.h`, `gdevsvga.h`.
- Shared VESA functions: `vesa_get_mode`, `vesa_set_mode`.
- Low-level port I/O macros/functions such as `inport`, `outport`, `outportb`.

## Notable Risks
- Requires direct VGA/S3 register access; unsafe or non-portable on protected modern systems.
- Hardware wait loop `s3_wait_fifo()` busy-waits without timeout.
- Cache uses bitmap id modulo cache capacity; collisions invalidate previous entries but are otherwise expected.
- Source alignment handling is delicate; transparent-color and partial-byte cases can alter behavior.

## Filesystem Relevance
No filesystem logic. This is a hardware display driver.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevs3ga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsco.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsco.c

## Purpose
SCO Xenix/Unix and AT&T SVR4 console/framebuffer support for Ghostscript PC framebuffer devices. It opens a console device, maps display memory, provides port-output helpers when inline assembly is unavailable, handles signals, and switches/restores video modes.

## Main Structures And Entry Points
- Global state:
  - `console_fd`
  - `fb_addr`
  - `cur_mode`
- Console/device helpers:
  - `open_console`
  - `outportb`
  - `outport2`
- Signal handlers:
  - `ega_int_handler`
  - `ega_tstp_handler`
  - `ega_cont_handler`
- Public PC framebuffer hooks:
  - `pcfb_set_signals`
  - `pcfb_get_state`
  - `pcfb_set_mode`
  - `pcfb_set_state`

## Behavior
- Chooses console path from `GSDEVICE`, defaulting to `/dev/tty`.
- Uses `CONSIO` ioctl for port I/O if not using GCC inline assembly.
- Reads current console mode with `CONS_CURRENT`.
- Maps Ghostscript video modes to SCO/SVR console switch ioctls.
- Requests I/O privilege with `VGA_IOPRIVL` where available.
- Maps display memory with `MAPCONS` and stores address in `fb_addr`.
- Restores video mode and exits on interrupt/termination; suspend/continue support is mostly disabled in favor of exit.

## Dependencies
- SCO/Xenix headers: `sys/console.h`, `sys/machdep.h`, `prototypes.h`.
- SVR4 header: `sys/kd.h`.
- Ghostscript PC framebuffer support: `gdevpcfb.h`.

## Notable Risks
- Uses global process-wide console and signal state.
- On many errors, calls `ega_close`, prints diagnostics, and exits the process.
- Opening a path from `GSDEVICE` gives user-controlled device selection.
- Requires console ioctls and direct device access; not portable beyond intended Unix console environments.

## Filesystem Relevance
Touches device files such as `/dev/tty` or a `GSDEVICE` path, but implements display/console hardware support rather than filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsco.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.c

## Purpose
Ghostscript printer device that writes SGI raster image files. It emits an SGI RGB image header, per-row RLE tables, and RLE-compressed channel-separated image data.

## Main Structures And Entry Points
- Public device: `gs_sgirgb_device`.
- Device procedures:
  - `sgi_map_rgb_color`
  - `sgi_map_color_rgb`
  - `sgi_print_page`
- Helper cursor:
  - `sgi_cursor`
  - `sgi_begin_page`
  - `sgi_next_row`

## Behavior
- Uses a 24-bit RGB device at 72 DPI.
- `sgi_begin_page` allocates a scanline buffer and SGI `IMAGE` header, fills header fields, writes the 512-byte SGI header area.
- `sgi_print_page` reserves row-start and row-size tables, writes channel data in separation order R, G, B, bottom-to-top.
- Extracts RGB components from Ghostscript scanlines according to bits per pixel.
- Implements SGI-style RLE packets and patches row offsets/sizes after data emission.

## Dependencies
- Ghostscript printer framework: `gdevprn.h`.
- SGI raster definitions from `gdevsgi.h`.

## Notable Risks
- Allocation failure paths do not consistently free earlier allocations.
- The allocated SGI header object is not freed after writing.
- Uses `long` for row offset/size tables and manually writes big-endian table values.
- RLE encoder has hand-rolled pointer arithmetic; malformed dimensions could expose edge cases.

## Filesystem Relevance
Writes an image file/stream, but no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.h

## Purpose
Header defining SGI raster image constants and the `IMAGE` structure used by `gdevsgi.c`.

## Main Contents
- Magic/type constants:
  - `IMAGIC`
  - `ITYPE_VERBATIM`
  - `ITYPE_RLE`
  - `RLE(bpp)`
  - `VERBATIM(bpp)`
- Colormap constants:
  - `CM_NORMAL`
  - `CM_DITHERED`
  - `CM_SCREEN`
  - `CM_COLORMAP`
- Utility macros for image type and pixel I/O style access.
- `IMAGE` structure containing on-disk SGI header fields plus in-memory fields for file state, buffers, offsets, and RLE row tables.

## Dependencies
No includes inside this header; it is expected to be consumed by SGI raster code that provides needed base types.

## Notable Risks
- Mixes on-disk fields with in-memory-only fields in one struct; callers must only write the intended header subset or account for padding/size.
- Old-style file-buffer macros reference fields such as `cnt`, `ptr`, and functions like `ifilbuf`/`iflsbuf`, but this group only uses the header layout.

## Filesystem Relevance
Image file format support only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsj48.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsj48.c

## Purpose
Ghostscript printer driver for the StarJet SJ48. It converts raster scanlines into ESC/P-like graphics commands for 180/360 DPI modes.

## Main Structures And Entry Points
- Public device: `gs_sj48_device`.
- Print callback: `sj48_print_page`.

## Behavior
- Supports x/y resolutions of 180 or 360 DPI.
- Selects graphics mode:
  - 39: 180x180
  - 40: 360x180
  - 71: 180x360
  - 72: 360x360
- Uses 3 bytes per column at 180 vertical DPI and 6 bytes per column at 360 vertical DPI.
- Skips blank input scanlines with ESC `J` linefeed commands.
- Transposes blocks of scanlines using `gdev_prn_transpose_8x8`.
- Emits horizontal skips with ESC `\`.
- Emits graphics with ESC `*`.
- Ends page with form feed.

## Dependencies
- Ghostscript printer framework: `gdevprn.h`.
- Standard Ghostscript scanline helpers.

## Notable Risks
- Only validates resolution after allocating buffers.
- Uses `fprintf` with `%c` to emit binary command bytes.
- Output assumptions are very printer-specific; unsupported resolutions return `rangecheck`.

## Filesystem Relevance
Writes a printer command stream; no filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsj48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsnfb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsnfb.c

## Purpose
Ghostscript framebuffer output device for Sony NEWS systems. It renders the Ghostscript page memory into `/dev/fb` using NEWS framebuffer ioctls.

## Main Structures And Entry Points
- Public device: `gs_sonyfb_device`.
- Device callbacks:
  - `sonyfb_open`
  - `sonyfb_output_page`
  - `sonyfb_close`
- Global state:
  - `fb_file`
  - `prect` rectangle command structure.

## Behavior
- Opens `/dev/fb` read/write.
- Reads screen type with `FBIOCGETSCRTYPE` and stores visible rectangle.
- Uses Ghostscript printer memory as a 1-bit memory bitmap.
- Builds an `sPrimRect` from Ghostscript memory to framebuffer draw bitmap.
- Issues `FBIOCRECTANGLE` to blit the page to the screen.
- Closes framebuffer fd on device close.

## Dependencies
- Ghostscript printer framework: `gdevprn.h`.
- NEWS headers:
  - `sys/uio.h`
  - `newsiop/framebuf.h`

## Notable Risks
- If opening `/dev/fb` or querying screen type fails, the code prints `perror` but still proceeds to `gdev_prn_open`; later output may use invalid `fb_file` or stale `prect`.
- Uses nonportable `typeof`.
- Assumes `prn_dev->mem.base` layout can be passed directly as framebuffer source data.

## Filesystem Relevance
Opens and ioctls a framebuffer device file, but is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsnfb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsppr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsppr.c

## Purpose
Ghostscript SPARCprinter driver using Sun LPVI printer ioctls. It configures page geometry and sends the rendered bitmap directly to the printer device.

## Main Structures And Entry Points
- Public device: `gs_sparc_device`.
- Device procedures:
  - `sparc_open`
  - `sparc_print_page`
- Error helpers:
  - `errmsg`
  - `err_code_string`
  - global `warning`

## Behavior
- `sparc_open` sets margins based on paper size and opens the Ghostscript printer device.
- `sparc_print_page`:
  - obtains current page settings with `LPVIIOC_GETPAGE`
  - sets bitmap width, page width/length, and resolution
  - applies settings with `LPVIIOC_SETPAGE`
  - copies all scanlines into one large buffer
  - writes the buffer to the printer fd
  - on failed writes, queries `LPVIIOC_GETERR`
  - retries warning/unknown conditions after `sleep(5)`
  - returns fatal errors immediately.

## Dependencies
- Ghostscript printer framework: `gdevprn.h`.
- Sun LPVI headers: `sys/ioccom.h`, `unbdev/lpviio.h`.
- Host APIs: `ioctl`, `write`, `sleep`, `fileno`.

## Notable Risks
- `out_buf` allocation is not checked before `gdev_prn_copy_scan_lines` and `write`.
- Fatal/error returns after allocation do not always free `out_buf`.
- Partial writes are treated the same as failed full writes, then printer error state is queried.
- Static `warning` and `err_buffer` are process-global.

## Filesystem Relevance
Operates on an already-open printer stream fd and issues device ioctls; no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsppr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.c

## Purpose
Main Ghostscript Epson Stylus Color printer driver. It manages device parameters, color mapping, transfer/coding arrays, dithering algorithm selection, scanline conversion, ESC/P2 initialization, band output, weaving, run-length compression, and delta-row compression.

## Main Structures And Entry Points
- Public device: `gs_stcolor_device`.
- Device procedures:
  - `stc_open`
  - `stc_close`
  - `stc_get_params`
  - `stc_put_params`
  - `stc_print_page`
- Local dithering algorithms:
  - `stc_gscmyk`
  - `stc_hscmyk`
- Algorithm table includes local algorithms plus `STC_MODI` from `gdevstc.h`.

## Print Pipeline
- `stc_print_setup` computes ESC/P2 parameters:
  - vertical/horizontal unit sizes
  - microweave/no-weave settings
  - band height
  - page width/height/top/bottom
  - initialization and release command strings.
- `stc_print_page`:
  - allocates input scanline, algorithm line, dither buffer, color line, printer buffers, seed rows, and ESC/P2 buffer
  - selects a conversion function based on color model, depth, direct mode, and CMYK10 mode
  - initializes the chosen dithering algorithm
  - reads Ghostscript scanlines
  - skips detected white lines
  - converts scanline data into algorithm format
  - runs dithering
  - splits dither output into black-only or CMYK plane bytes
  - emits output via `stc_print_delta`, `stc_print_weave`, or `stc_print_bands`
  - writes release string if data was printed
  - frees dynamic buffers.

## Compression And Output
- `stc_rle` implements Epson ESC/P2 RLE packetization.
- `stc_print_escpcmd` emits initialization, position movement, color selection, and ESC `.` raster command headers.
- `stc_print_weave` handles multi-pass software weaving.
- `stc_print_bands` handles single-pass band output.
- `stc_deltarow` compares current rows against seed rows and emits delta-row move/data/clear commands.
- `stc_print_delta` wraps delta-row output and emits ESC `. 3`.

## Color Mapping
- Supports grayscale, RGB, CMYK, and special 10-bit CMYK encodings.
- `stc_truncate` maps Ghostscript color values into configured component bit depth, optionally through coding arrays.
- `stc_expand` maps encoded component values back to Ghostscript color values.
- RGB and CMYK mapping can use `ColorAdjustMatrix`.
- CMYK mapping performs black extraction/separation.
- CMYK10 packs color data into `stc_pixel` with a mode field and 10-bit values, with endian swapping on little-endian systems.

## Parameter Surface
`stc_get_params` and `stc_put_params` expose and accept:
- `Version`
- `BitsPerComponent`
- `Algorithms`
- `OutputCode`
- `Model`
- `Unidirectional`
- `Microweave`
- `Softweave`
- `noWeave`
- `Flag0` to `Flag4`
- `escp_Band`, `escp_Width`, `escp_Height`, `escp_Top`, `escp_Bottom`
- `escp_Init`, `escp_Release`
- `Dithering`
- `ColorAdjustMatrix`
- per-channel coding/transfer arrays for RGB, CMYK, or K.

## Dependencies
- Shared STC definitions and external algorithms from `gdevstc.h`.
- Ghostscript printer/device parameter framework.
- Optional POSIX signal handling with `STC_SIGNAL`.

## Notable Risks
- Build-level defect: `stc_freedata(gs_memory_t *mem, stc_t *stc)` references `sd->stc.alg_item`, but `sd` is not in scope. This should not compile as written unless hidden by unavailable configuration or external patching.
- Memory ownership is complex: parameter arrays may be shared across components, copied on put, and freed with alias checks.
- Several paths set `SORRY` after allocation failures, then continue to centralized cleanup; correctness depends on all pointer fields being initialized.
- ESC/P2 command construction is manual binary byte emission and sensitive to dimensions/compression sizes.
- Optional signal handling can abort output mid-page.
- Many parameters can force device closure/reopen.

## Filesystem Relevance
No filesystem implementation logic. It writes printer command streams and manages raster buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.h

## Purpose
Shared header for the Epson Stylus Color Ghostscript driver and its separately compiled dithering algorithms.

## Main Structures
- `stc_pixel`: unsigned integer type large enough for packed pixel values.
- `stc_t`: all STC driver state, including flags, bits/component, algorithm pointer, color adjustment matrix, coding/transfer arrays, ESC/P2 strings and geometry, printer buffers, and seed rows.
- `stcolor_device`: Ghostscript printer device plus `stc_t`.
- `stc_dither_t`: algorithm name, function pointer, flags, buffer requirements, and min/max value range.

## Main Definitions
- Driver flags for algorithm bits, CMYK10, unidirectional/microweave/no-weave, compression mode, model, page geometry, init/release strings, and print state.
- Output component bit constants:
  - `BLACK`
  - `RED`
  - `GREEN`
  - `BLUE`
  - `CYAN`
  - `MAGENTA`
  - `YELLOW`
- Algorithm flags:
  - `DeviceGray`, `DeviceRGB`, `DeviceCMYK`
  - `STC_BYTE`, `STC_LONG`, `STC_FLOAT`
  - `STC_CMYK10`, `STC_DIRECT`, `STC_WHITE`, `STC_SCAN`
- Declares external dithering procedures:
  - `stc_gsmono`
  - `stc_fs`
  - `stc_fscmyk`
  - `stc_gsrgb`
  - `stc_fs2`
- `STC_MODI` registers the external dithering modes.

## Defaults
- Default DPI: 360x360 unless overridden.
- Default margins tuned for Epson Stylus Color, with A4-specific right margin option.

## Dependencies
- Ghostscript headers: `gdevprn.h`, `gsparam.h`, `gsstate.h`.

## Notable Risks
- The algorithm registry is macro-based, so adding/removing algorithms requires coordinated edits in the header, source files, and build metadata.
- Many flags share one integer bitfield; invalid combinations are mostly validated later by algorithm initialization or `stc_put_params`.

## Filesystem Relevance
No filesystem logic; shared printer-driver definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc1.c

## Purpose
Simple monochrome “dithering” algorithm for the Epson Stylus Color driver. It lets Ghostscript produce 1-bit monochrome data and copies that data through.

## Main Entry Point
- `stc_gsmono(stcolor_device *sdev, int npixel, byte *in, byte *buf, byte *out)`

## Behavior
- For positive `npixel`, copies `in` to `out` for normal lines.
- For white-line notifications (`in == NULL`), clears `out`.
- For initialization (`npixel <= 0`), clears the optional buffer and validates:
  - exactly one component
  - byte algorithm type
  - not direct mode.

## Dependencies
- `gdevstc.h`.

## Notable Risks
- Minimal algorithm; assumes caller passes valid output buffer.
- Returns negative algorithm-specific validation errors that cause print aborts.

## Filesystem Relevance
No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc2.c

## Purpose
Floyd-Steinberg error diffusion algorithms for the Epson Stylus Color driver.

## Main Entry Points
- `stc_fs`: generic monochrome/RGB/CMYK Floyd-Steinberg over components.
- `stc_fscmyk`: modified CMYK Floyd-Steinberg that treats black specially.

## Behavior
- `stc_fs`:
  - Alternates scan direction using state in the buffer.
  - Applies per-component error diffusion.
  - Converts internal component bits to STC output pixel codes using conversion tables.
  - Initializes threshold, spot size, and randomized or zeroed error buffers.
- `stc_fscmyk`:
  - Requires 4 components.
  - Processes black first.
  - If black fires, forces color handling accordingly.
  - If black does not fire, only colors above black value may fire.
  - Supports a threshold variant controlled by `STCDFLAG1`.
- `STCDFLAG0` disables randomized initial errors.

## Dependencies
- `gdevstc.h`.
- `stdlib.h` for `rand`.

## Notable Risks
- Works on `long` buffers and assumes caller allocated enough state according to `stc_dither_t`.
- White-line calls are ignored or disallowed depending on flags.
- Error diffusion arithmetic is hand-tuned and sensitive to component count and buffer stride.

## Filesystem Relevance
No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc3.c

## Purpose
Simple RGB pass-through/packing algorithm for the Epson Stylus Color driver. Like `gsmono`, it relies on Ghostscript to produce 1-bit component values and packs them into STC RGB bit flags.

## Main Entry Point
- `stc_gsrgb(stcolor_device *sdev, int npixel, byte *ip, byte *buf, byte *out)`

## Behavior
- For each pixel, reads three input component bytes and sets `RED`, `GREEN`, and `BLUE` bits in one output byte.
- Initialization validates:
  - no white-line calls
  - byte algorithm type
  - exactly three components
  - not direct mode.

## Dependencies
- `gdevstc.h`.

## Notable Risks
- Assumes input is exactly three bytes per pixel.
- No handling for `in == NULL` during scanline processing; flags are expected to prevent such calls.

## Filesystem Relevance
No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc4.c

## Purpose
Byte-oriented Floyd-Steinberg RGB dithering algorithm for the Epson Stylus Color driver, derived from `escp2cfs2`.

## Main Entry Point
- `stc_fs2(stcolor_device *sd, int npixel, byte *in, byte *buf, byte *out)`

## Helper Functions
- `escp2c_pick_best`: chooses the closest of eight RGB cube colors using a custom weighted distance metric.
- `escp2c_conv_stc`: converts full RGB triplets to STC output bit flags.

## Behavior
- Maintains per-line error in `buf`.
- On white-line notification (`in == NULL`), clears the error buffer.
- Otherwise applies previous error to input, chooses best output color, diffuses error in alternating left-to-right/right-to-left directions, and packs output bits.
- Initialization validates:
  - exactly three components
  - byte algorithm type
  - at least one scanline of buffer
  - then clears buffer.

## Dependencies
- `gdevstc.h`.

## Notable Risks
- Uses a static `dir` variable shared across calls/devices, so multiple devices or concurrent printing would share dithering direction.
- Modifies the input scanline buffer while dithering.
- Pointer arithmetic around `buf - 3` / `buf + fullcolor_line_size + 2` is tightly coupled to the algorithm’s access pattern and buffer sizing.

## Filesystem Relevance
No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsun.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsun.c

## Purpose
Ghostscript SunView display driver. It creates a SunView frame/canvas, manages mono/pseudocolor/truecolor mappings, and renders Ghostscript drawing operations to a Sun pixwin.

## Main Structures And Entry Points
- Device type: `gx_device_sun`.
- Public device: `gs_sunview_device`.
- Device procedures:
  - `sun_open`
  - `sun_sync`
  - `sun_close`
  - `sun_map_rgb_color`
  - `sun_map_color_rgb`
  - `sun_fill_rectangle`
  - `sun_copy_mono`
  - `sun_copy_color`
  - `sun_draw_line`
- Window destroy interposer:
  - `destroy_func`

## Behavior
- Creates SunView frame and canvas with page-sized canvas dimensions and scrollbars.
- Detects display depth:
  - 1-bit mono
  - 8-bit pseudocolor
  - 24/32-bit truecolor
- For pseudocolor:
  - allocates RGB colormap arrays
  - reserves black/white compatibility entries
  - pre-populates a color cube
  - allocates further colors on demand until colormap is full
- For truecolor:
  - encodes RGB values directly into color index bits.
- `sun_copy_mono` creates a memory pixrect view of caller data and uses `pw_stencil`.
- On little-endian systems, reverses bits in source bytes before and after mono copy.
- `sun_copy_color` writes color pixrect data directly.
- `sun_fill_rectangle` and `sun_draw_line` call Sun pixwin drawing APIs.

## Dependencies
- SunView/SunWindow headers:
  - `suntool/sunview.h`
  - `suntool/canvas.h`
  - `sunwindow/cms_mono.h`
- Ghostscript device headers.
- Host `malloc`/`free`.

## Notable Risks
- `sun_copy_mono` temporarily mutates the caller’s supposedly const bitmap data to reverse/invert bits, then restores it; comments acknowledge this as unsafe.
- Colormap exhaustion returns `gx_no_color_index` and relies on Ghostscript dithering behavior; comments warn of possible loops if requested colors do not match the cube.
- The destroy interposer vetoes user window close to preserve device bookkeeping.
- Old SunView-only APIs make this highly platform-specific.

## Filesystem Relevance
No filesystem logic. It is a window/display backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsun.c -->