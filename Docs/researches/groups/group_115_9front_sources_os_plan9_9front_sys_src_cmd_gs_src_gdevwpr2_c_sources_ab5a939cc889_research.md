# Group Research: group_115_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevwpr2_c_sources_ab5a939cc889

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwpr2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwpr2.c

Newer Ghostscript Microsoft Windows printer device `mswinpr2`. It uses the generic printer-device framework (`gdev_prn_*`) and sends rendered page rasters to a Windows printer DC as DIB slices.

Key responsibilities:
- Defines `gx_device_win_pr2` with printer `HDC`, cancellation dialog state, `UserSettings`, DEVMODE/DEVNAMES handles, duplex/tumble state, DPI limiting, and copy-device handle duplication.
- `win_pr2_open` obtains or creates the printer DC, starts a Windows print document, derives physical size/margins/resolution, applies max-DPI scaling, chooses bits-per-pixel, and opens Ghostscript printer buffering.
- `win_pr2_print_page` copies Ghostscript scan lines into a BMP/DIB buffer, builds a palette for <=8 bpp, and outputs chunks through `SetDIBitsToDevice` or `StretchDIBits`.
- `win_pr2_set_bpp`, `win_pr2_map_rgb_color`, and `win_pr2_map_color_rgb` support 1, 4, 8, and 24-bit printer color modes.
- `win_pr2_get_params` / `win_pr2_put_params` expose `NoCancel`, `QueryUser`, `Tumble`, and nested `UserSettings`.
- `win_pr2_getdc` parses `\\spool\...` and `%printer%...`, queries Windows printer capabilities, matches PostScript page size to printer paper, updates DEVMODE, and creates the DC.
- `win_pr2_print_setup_interaction` drives Print/Print Setup/default-printer dialogs and stores user choices.
- `CancelDlgProc` and `AbortProc2` implement cancellation and interrupt polling.

Notable implementation details:
- Page size/resolution come primarily from the Windows printer, not `-g`/`-r`, though `PageSize` affects clipping and paper selection attempts.
- `MaxResolution` reduces effective device DPI by an integer ratio and scales output back up when printing.
- The driver copies `HGLOBAL` DEVMODE/DEVNAMES handles on `copydevice` to avoid shared mutable Windows handles.

Filesystem relevance:
- Minimal. It creates/deletes a scratch printer buffer filename through `gp_open_scratch_file` and `unlink`, but its real focus is Windows printer I/O and raster transfer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwpr2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwprn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwprn.c

Older Ghostscript Windows 3.x printer driver `mswinprn`. The file notes it is very slow and, as of 2002-09-14, does not work.

Key responsibilities:
- Defines `gx_device_win_prn`, extending the Windows common device state with printer/metafile HDCs, scratch metafile name, palette, pens, brushes, and a small mono staging bitmap.
- `win_prn_open` prompts with `PrintDlg`, creates a printer DC, starts a document, creates a scratch metafile, derives margins/resolution/page size, chooses 1/4/8-bit color behavior, creates palette/tools, and initializes a mono bitmap DC.
- `win_prn_output_page` closes the metafile, replays it into printer bands using `NEXTBAND`, then creates a new metafile for the next page.
- Drawing procs implement fill rectangles, tile rectangles, mono bitmap copies, color bitmap copies, and lines with Windows GDI operations.
- `win_prn_maketools` / `win_prn_destroytools` manage per-color pens and brushes.
- `AbortProc` polls Ghostscript interrupts and cancels on out-of-disk spooler status.

Notable implementation details:
- Rendering is recorded to a Windows metafile (`CreateMetaFile`) instead of sending full page bitmaps.
- Mono tile/copy paths optimize small bitmaps through a cached 32x32-ish staging bitmap.
- Color copy is pixel-by-pixel for 4/8-bit color via `SetPixel`, which explains the driver’s poor performance.

Filesystem relevance:
- Uses a scratch metafile path and unlinks it after creating/playing the metafile. No filesystem architecture logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwprn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.c

Main Ghostscript X11 display renderer. It defines public X devices `x11` and `x11alpha` and implements the drawing/update operations; initialization and color management are split into companion files.

Key responsibilities:
- Device descriptors wire Ghostscript device procedures to X11 operations.
- `x_open` / `x_close` delegate lifecycle to `gdev_x_open` / `gdev_x_close`.
- `x_sync`, `x_output_page`, and `gdev_x_send_event` flush display output and coordinate with Ghostview client messages.
- `x_fill_rectangle`, `x_copy_mono`, `x_copy_color`, and `x_copy_image` render fills and image transfers into the destination window/pixmap.
- `x_strip_tile_rectangle` maps Ghostscript halftone tiles into X pixmaps and uses tiled fills when possible.
- `x_begin_typed_image` optimizes ImageType 2 `PixelCopy` with X `CopyArea` when source/destination devices and transforms match.
- `x_get_bits_rectangle` reads pixels back with `XGetImage`, normalizing supported 16/24-bit server layouts.
- Update machinery (`update_init`, `x_update_add`, `update_do_flush`) coalesces writes and copies from backing pixmap or memory buffer to the visible window.
- BBox callback procs integrate buffered rendering with Ghostscript’s bounding-box device.
- `alt_put_image` emulates a subset of `XPutImage` with rectangles for broken X servers.

Notable implementation details:
- Transparent mono writes have optimized boolean-function cases (`GXand`/`GXor`) and a hard path using a 1-bit clip pixmap.
- The renderer tracks `colors_or`/`colors_and` to optimize monochrome writes over known-color regions.
- Backing pixmap and memory-buffer modes affect when writes hit the visible window.
- Text buffering is flushed before graphics operations that would invalidate GC assumptions.

Filesystem relevance:
- None beyond being part of the Ghostscript source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.h

Shared declarations for the Ghostscript X11 drivers.

Key contents:
- Defines `x_pixel` and includes bbox/color-management declarations.
- Declares resource tables from `gdevxres.c`.
- Defines X11 font mapping structs `x11fontlist` and `x11fontmap`, including GC descriptor macro.
- Defines `gx_device_X`, the central X11 device state structure.
- Device state includes bbox forwarding fields, optional memory buffer, `XImage`, `Display`, `Screen`, visual/colormap/window/GC handles, Ghostview atoms, update coalescing state, backing pixmap, temporary mono pixmap, halftone tile cache, GC cache, colors, resources, font maps, update thresholds, and buffered text state.
- Provides macros for cached GC updates: fill style, function, font, background, and foreground.
- Declares inter-module procedures for events, updates, clearing, open/close, color setup/freeing, params, xfont procs, and copydevice finalization.
- Defines `FAKE_RES` used to distinguish nominal command-line/default resolution.

Notable implementation details:
- `is_buffered` is separate from `target` because bbox wrapping may temporarily clear the target.
- `DRAW_TEXT` depends on GC state remaining valid from the first buffered text item.
- `gx_device_X` embeds `x11_cman_t` from `gdevxcmp.h`, keeping color management logically isolated but physically part of the device.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxalt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxalt.c

Alternative/debug X11 devices that wrap a real `x11` target while exposing different Ghostscript color models.

Key responsibilities:
- Defines `gx_device_X_wrapper`, a forwarding device with a 16-entry color cache and an `alt_map_color` procedure.
- Lazily creates a real `gs_x11_device` target with `gs_copydevice`.
- Generic wrapper procs forward open/close/output/sync/get-bits/get-params/put-params and remap color arguments before forwarding drawing calls.
- `x_wrap_copy_color` can remap source pixels into the target byte layout in blocks when target pixels are byte-aligned.
- `x_alt_map_color` maps wrapper color indices to target X pixels, caching small color values.
- Public devices include `x11cmyk`, `x11cmyk2`, `x11cmyk4`, `x11cmyk8`, `x11mono`, `x11gray2`, `x11gray4`, `x11rg16x`, and `x11rg32x`.

Color behavior:
- CMYK variants encode fake CMYK pixels and convert them back to RGB for the target X device.
- Mono and gray variants map fake gray/black-white pixels to RGB values.
- `x11rg16x` and `x11rg32x` use deliberately permuted RGB bit layouts for debugging byte/component handling.
- Alpha color mapping packs complemented alpha into the high byte for alpha-capable paths.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxalt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcf.c

Ghostscript printer-style export device for GIMP XCF files, with DeviceN/spot color support.

Key responsibilities:
- Defines `xcf_device`, extending printer-device state with color model, bits per component, process colorant names, separation names/order, and optional ICC profile lookup objects.
- Public devices: `xcf` default RGB plus spot support, and `xcfcmyk` default CMYK/DeviceN-oriented output.
- Color mapping procs convert Gray/RGB/CMYK input color spaces into RGB, CMYK, or DeviceN output components, clearing spot components when not explicitly set.
- Optional ICC profiles (`ProfileOut`, `ProfileRgb`, `ProfileCmyk`) are opened via Argyll-style ICC APIs and used for color conversion.
- `xcf_encode_color` / `xcf_decode_color` pack and unpack component values into `gx_color_index`.
- Params expose CRD defaults, separations, color profiles, process color model, and separation color names.
- `xcf_put_params` updates process model, separation list, component count, depth, and profile state.
- `xcf_get_color_comp_index` maps named process or separation components to component indices.
- XCF writer emits header, layer hierarchy, tile offsets, base image tile data, extra separation channels, fake reduced hierarchies, and channel metadata.

Notable implementation details:
- Tile size is fixed at 64x64.
- Base image data is stored as 3-byte RGB; extra separations are stored as separate channel planes.
- Extra channel bytes are inverted with `255 ^ value`, matching XCF channel semantics.
- `bpc_to_depth` rounds component packing to byte-compatible Ghostscript depths.
- Several `TO_DO_DEVICEN` comments indicate incomplete `SeparationOrder` behavior.

Filesystem relevance:
- Writes the final XCF stream through Ghostscript printer output `FILE *`. No filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.c

X11 color setup, allocation, and pixel/RGB mapping for the Ghostscript X driver.

Key responsibilities:
- Initializes color management based on X visual class, requested palette, Ghostview color properties, depth, and standard colormap availability.
- Supports standard X colormaps when available, including fast shift/table paths for power-of-two component ranges.
- Allocates synthetic standard colormaps for TrueColor/StaticGray visuals when needed.
- Builds reverse pixel-to-RGB table for small pixel values.
- Allocates dither ramps/cubes for writable colormaps without suitable standard maps.
- Maintains a dynamic color hash table for exact color allocations beyond fixed ramp/cube entries.
- Frees dither, dynamic, reverse-map, and standard-map resources on erase/close.
- `gdev_x_map_rgb_color` maps Ghostscript RGB values to X pixels through foreground/background shortcuts, standard cmap, dither ramp/cube, then dynamic allocation.
- `gdev_x_map_color_rgb` maps X pixels back to Ghostscript RGB via foreground/background, reverse table, standard cmap, dither ramp/cube, or dynamic table.

Notable implementation details:
- Foreground maps to RGB black and background maps to RGB white, preserving Ghostscript device conventions even if X pixels differ.
- `match_mask` may be narrower than `color_mask` when halftoning is not required.
- Dynamic color misses are cached as failed entries too, avoiding repeated allocation attempts.
- The code updates `color_to_rgb` on successful X color allocation/free.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.h

Header for the X11 color-management data embedded in `gx_device_X`.

Key contents:
- `x11_rgb_t`: reverse-map entry containing RGB values plus a defined flag.
- `x11_color_t`: dynamic color hash entry containing an `XColor` and next pointer.
- `X_color_value` aliases X color component values to `ushort`, matching Ghostscript color values.
- Optional `x11_cmap_values_t` stores precomputed standard-colormap conversion shifts and nearest-value tables.
- `x11_cman_t` groups all color state:
  - visual RGB count,
  - color and match masks,
  - optional standard colormap metadata,
  - reverse pixel-to-RGB table,
  - dither ramp/cube pixels,
  - dynamic color hash table.

Notable implementation details:
- `CUBE_INDEX` indexes an RGB cube using the owning device’s `dither_colors`.
- Reverse mapping only covers pixel values up to `min(1 << depth, 256)`; larger pixels rely on colormap logic or server/query-derived structures.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxcmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxini.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxini.c

X11 driver initialization, parameter handling, buffering setup, font mapping, and cleanup.

Key responsibilities:
- `gdev_x_open` opens the X display, handles Ghostview and explicit `WindowID`, selects visual/colormap, reads Xt resources, reserves foreground/background, sets up colors and font maps, creates or adopts a window, builds GC state, clears the window, and initializes Ghostview atoms/window if needed.
- Handles Ghostview geometry/orientation properties and computes the initial matrix/imaging bbox.
- Uses Xt resource tables from `gdevxres.c` for defaults such as palette, font resources, backing pixmap, XPutImage/XSetTile flags, and resolution.
- `x_set_buffer` optionally allocates a memory device buffer up to `MaxBitmap`, forwards drawing through bbox/memory when buffered, and switches device procs accordingly.
- `gdev_x_clear_window` allocates/frees backing pixmap, initializes destination, clears background, and resets color tracking.
- Font map parsing builds `x11fontmap` linked lists from resource strings.
- `gdev_x_finish_copydevice` clears pointer fields after copydevice to avoid dangling X/font/buffer references.
- `gdev_x_get_params` / `gdev_x_put_params` expose `WindowID`, `.IsPageDevice`, `MaxBitmap`, and buffered update limits; put-params can resize an open non-Ghostview window.
- `gdev_x_close` sends Ghostview DONE, frees visual info/colors/font maps/colormap, and closes the display.

Notable implementation details:
- X error handling for backing pixmap allocation and `XFreeColors` uses static globals due to Xlib API limitations.
- Default DPI is inferred from screen dimensions when the device still has `FAKE_RES`.
- Closing the Xt resource display is deliberately delayed until after resource-dependent initialization.
- `MaxBitmap` changes can toggle memory-buffered rendering while the device is open.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxres.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxres.c

Static Xt resource definitions for the Ghostscript X11 device.

Key contents:
- `gdev_x_resources[]` maps Xt resource names/classes to fields inside `gx_device_X`.
- Resources cover background/foreground/border, geometry, logging, max gray/RGB ramp sizes, palette mode, font map strings, X-font behavior, backing pixmap, XPutImage/XSetTile workarounds, and x/y resolution.
- Large default PostScript-to-X11 font mappings are embedded for standard fonts, Symbol, and ZapfDingbats.
- `gdev_x_resource_count` exports table length.
- `gdev_x_fallback_resources` provides default white background and black foreground.

Notable implementation details:
- The table is isolated because Xt declares resource strings as mutable `char *`, creating noisy cast-qual warnings.
- Comments note Xt may actually write into these structures, so they are not `const`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxres.c -->