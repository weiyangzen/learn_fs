# Group Research: group_110_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevplan9_c_source_e78e8efdb1b4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplan9.c

Ghostscript printer device that writes Plan 9 compressed bitmap images. It defines the `plan9` device, Plan 9-style point/rectangle helpers, RGB color mapping, a `Dither` parameter, page raster conversion, and an embedded Plan 9 image compressor adapted from `fb/bit2enc`.

Key behavior:
- `gs_plan9_device` is a 24-bit RGB printer device at 100 DPI with zero margins.
- `plan9_rgb2cmap` maps Ghostscript RGB values into packed low-byte red, middle-byte green, high-byte blue pixels and watches requested colors to infer a Plan 9 output depth.
- `plan9_cmap2rgb` decodes packed colors back to Ghostscript RGB values and rejects indexes above 24 bits.
- `plan9_get_params` and `plan9_put_params` expose a boolean-ish `Dither` parameter, although the current page writer does not visibly use it for a dithering algorithm.
- `plan9_open` initializes Plan 9 color tables through `init_p9color()` and opens the generic printer backing device.
- `plan9_print_page` chooses `k1`, `k4`, or `r8g8b8` channel strings from inferred `ldepth`, reads rendered Ghostscript scan lines, repacks grayscale depths when needed, and sends each line to the compressed Plan 9 image writer.
- The local `WImage` compressor keeps a sliding 1024-byte input window, hash chains, raw dump runs, and compressed match records, flushing fixed-size compressed blocks to the output stream.

Notable dependencies:
- Ghostscript printer and parameter APIs: `gdevprn.h`, `gsparam.h`.
- Color/luminance and stdio wrappers: `gxlum.h`, `gxstdio.h`.
- External Plan 9 color support from `init_p9color()` in `gdevifno.c`.

Research notes:
- This is output-format code in the in-scope 9front Ghostscript tree, not filesystem logic.
- `ldepth == 1` currently returns a fatal error even though 2-bit-per-pixel metadata arrays exist.
- Error paths after `initwriteimage` failure do not free the scanline buffer before returning fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.c

Implementation of Ghostscript's plane extraction forwarding device. It reduces drawing into a selected bit plane and forwards reduced operations to a plane device, normally a memory device used by planar printer band rendering.

Key behavior:
- Defines the `gs_plane_extract_device` prototype, GC hooks, and driver procedures for rectangles, masks, paths, images, RasterOps, tiles, alpha copies, and get-bits.
- `plane_device_init` initializes forwarding-device state, copies target parameters, stores the plane target, opens plane extraction state, and optionally clears the plane device to white.
- `reduce_drawing_color` rewrites pure, binary-halftone, and colored-halftone drawing colors into plane-local colors and skips early all-white drawing until any non-white mark has appeared.
- Rectangle, monochrome, alpha, path, stroke, mask, parallelogram, and triangle handlers either skip white-only work, forward reduced operations, or fall back to Ghostscript defaults when reduction is unsafe.
- Tiling helpers split chunky source tiles into temporary plane tiles using `bits_extract_plane`, with stack buffers first and heap buffers when needed.
- `plane_begin_typed_image` wraps image rendering with modified color-map procs so image colors are reduced before the plane device sees them.
- `plane_get_bits_rectangle` supports selected planar retrieval and can expand the single plane back into chunky pixels.

Notable dependencies:
- Ghostscript device, memory, clist/image, color, halftone, RasterOp, bit-plane, and get-bits APIs.
- Public interface and state definition from `gdevplnx.h`.

Research notes:
- The `any_marks` optimization is central: before a plane has any non-white marks, white-only operations are discarded.
- In `begin_tiling`, the partial-buffer branch computes a smaller raster/width, but later unconditionally resets `pts->buffer.raster = width_raster`; this looks inconsistent.
- In `plane_strip_copy_rop`, the source tiling call passes `w, y` as width/height, which appears suspicious because the requested height is `h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.h

Public header for the Ghostscript plane extraction device.

Key contents:
- Documents the plane extraction model: the client sees a color-capable forwarding device, while a selected group of bits is rendered into a separate plane device.
- Defines `gx_device_plane_extract`, embedding `gx_device_forward_common`, the destination `plane_dev`, selected `plane`, derived plane white/mask information, memory-device detection, and dynamic `any_marks` state.
- Declares the GC structure descriptor `st_device_plane_extract`.
- Declares `plane_device_init()` for initializing a plane extraction device around a target, plane device, selected plane, and optional clear operation.

Notable dependencies:
- Requires Ghostscript forwarding-device definitions from the including context and `gx_render_plane_t` from `gxrplane.h`.

Research notes:
- The header states important limits: target and extraction device depths are limited to 32 bits, and each plane is limited to 8 bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.c

OS/2 Presentation Manager display driver for Ghostscript. It backs rendering with a BMP bitmap in shared memory or DLL-local memory, then communicates updates to either an outboard `gspmdrv.exe` process, PM GSview, or a DLL callback.

Key behavior:
- Defines `gx_device_pm`, containing regular device state, PM parameters, synchronization handles, process/session ids, shared bitmap memory, committed size, BMP header pointer, and an embedded memory device.
- Exports `gs_os2pm_device`, and conditionally `gs_os2dll_device`, defaulting to 24-bit color at 96 DPI.
- `pm_open` creates or opens shared memory/semaphores/queues/mutexes, initializes BMP metadata, sets color depth, allocates the memory-backed bitmap, and starts `gspmdrv.exe` unless GSview or DLL callback mode owns display.
- `pm_sync_output`, `pm_do_output_page`, and `pm_output_page` signal screen updates, page boundaries, GSview begin/end markers, session foreground selection, and output-page completion.
- Drawing operations delegate to the embedded memory device and then schedule asynchronous display updates.
- `pm_get_params` and `pm_put_params` expose `UpdateInterval`, `GSVIEW`, and `BitsPerPixel`, while handling size/depth changes without the default close/reopen path.
- `pm_run_gspmdrv`, `pm_alloc_bitmap`, `pm_makepalette`, `pm_update`, and `pm_set_bits_per_pixel` handle process startup, BMP backing storage, palette, timer, and color-info setup.

Notable dependencies:
- OS/2 APIs and types from `<os2.h>`.
- Ghostscript device, memory-device, parameter, platform, and PC palette APIs.
- Shared PM naming/message constants from `gdevpm.h`.

Research notes:
- This is platform display plumbing, not filesystem logic.
- `pm_put_params` explicitly says its recovery after failed bitmap reallocation is wrong because other parameters may already have changed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.h

Small shared header for the OS/2 Presentation Manager Ghostscript driver, its companion `gspmdrv.c`, and PM GSview integration.

Key contents:
- Defines named shared-memory, semaphore, mutex, and queue path templates: `SHARED_NAME`, `SYNC_NAME`, `NEXT_NAME`, `MUTEX_NAME`, and `QUEUE_NAME`.
- Defines queue message codes: `GS_UPDATING`, `GS_SYNC`, `GS_PAGE`, `GS_CLOSE`, `GS_ERROR`, `GS_PALCHANGE`, `GS_BEGIN`, and `GS_END`.

Notable dependencies:
- No included Ghostscript types; this header is only constants and include guards.

Research notes:
- The file is tightly coupled to `gdevpm.c` and the outboard OS/2 display process.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpng.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpng.c

Ghostscript PNG output devices backed by libpng. It provides monochrome, indexed-color, grayscale, RGB, high-depth RGB, and RGBA-with-coverage devices, all using the generic printer framework.

Key behavior:
- Defines `pngmono`, `png16`, `png256`, `pnggray`, `png16m`, and `png48` printer devices with appropriate color mapping and depths.
- Defines `pngalpha`, a 32-bit RGBA printer device whose alpha channel represents pixel coverage rather than general transparency.
- `png_print_page` is shared by all PNG devices: it creates libpng state, sets resolution metadata, selects PNG color type/bit depth, writes palette metadata when needed, emits a `Software` text chunk, streams rendered scanlines, then finalizes.
- For 32-bit alpha output, it uses `PNG_COLOR_TYPE_RGB_ALPHA`, inverts alpha for libpng output, and writes a `bKGD` chunk from `BackgroundColor`.
- `pngalpha_open`, `pngalpha_create_buf_device`, `pngalpha_fill_rectangle`, and `pngalpha_copy_alpha` customize memory-buffer behavior for coverage compositing and transparent full-page erase.
- `pngalpha_get_params` and `pngalpha_put_params` expose `BackgroundColor`.

Notable dependencies:
- Ghostscript printer/memory/palette/version APIs.
- libpng through `png_.h`.

Research notes:
- The file directly manipulates older libpng struct fields, reflecting the vendored Ghostscript era.
- If `png_create_write_struct` fails, `png_create_info_struct(png_ptr)` is still called before the null check; with libpng APIs that require a non-null write struct, that ordering is fragile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpnga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpnga.c

Experimental/test Ghostscript PNG alpha driver for PDF 1.4 transparency. It maintains a planar RGBA transparency stack, composites groups with `gxblend` helpers, and writes the final result as a scratch PNG.

Key behavior:
- Defines `pdf14_buf`, a planar buffer with saved-stack pointer, isolated/knockout flags, group alpha/shape, blend mode, rectangle, row/plane strides, channel/plane counts, and backing data.
- Defines `pdf14_ctx`, which owns the current buffer stack, allocator, page rectangle, and channel count.
- Defines the `pnga` device and a transient `pnga_mark` device used for actual marks under the current imager state's opacity, shape, and blend mode.
- `pdf14_push_transparency_group` creates a new group buffer, forces knockout groups isolated as a simplifying hack, copies backdrop data when needed, and records group compositing parameters.
- `pdf14_pop_transparency_group` composites the top group into its parent using PDF 1.4 blend helpers.
- `pnga_output_page` writes the current top buffer as 8-bit RGBA PNG through libpng, but opens a scratch file with `gp_open_scratch_file` rather than using the normal printer `OutputFile`.
- Path, stroke, image, and text entry points render through temporary marking devices so normal Ghostscript rendering lands in `pnga_mark_fill_rectangle` paths.
- Transparency group begin/end hooks push and pop PDF 1.4 transparency groups.

Notable dependencies:
- Ghostscript printer/device/text/memory APIs.
- PDF 1.4 blending helpers from `gxblend.h`.
- libpng through `png_.h`.

Research notes:
- The file labels itself as a test driver; it is not a general production PNG device.
- `pnga_output_page` contains a TODO noting it should use `OutputFile` rather than a scratch file.
- `pdf14_ctx_new` allocates `result` and then calls `pdf14_buf_new` before checking whether `result` is null.
- In both rectangle marking routines, the y lower-bound clamp checks `y < buf->rect.p.x` rather than `y < buf->rect.p.y`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpnga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.c

Helper implementation for printer devices that can use planar buffering instead of chunky memory buffering.

Key behavior:
- `gdev_prn_set_procs_planar` replaces a printer device's buffer creation and sizing callbacks with planar-aware variants.
- `gdev_prn_open_planar` conditionally installs planar buffer callbacks before calling `gdev_prn_open`.
- `gdev_prn_get_params_planar` and `gdev_prn_put_params_planar` wrap generic printer parameter handling with a `UsePlanarBuffer` boolean for multi-component devices.
- `gdev_prn_set_planar` configures a memory device into 3- or 4-plane layout by deriving a per-plane depth, rounding it up to a power of two, and assigning shifts so the most significant component plane comes first.
- `gdev_prn_create_buf_planar` creates the default buffer device and then converts memory buffers to planar layout.
- `gdev_prn_size_buf_planar` computes planar buffer storage, line-pointer storage, and raster requirements.

Notable dependencies:
- Generic printer framework from `gdevprn.h`.
- Planar memory-device support from `gdevmpla.h`.
- Public declarations from `gdevppla.h`.

Research notes:
- Planar buffering is restricted to 3- or 4-component devices; other component counts return `rangecheck`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.h

Public header for planar-buffer support in Ghostscript printer devices.

Key contents:
- Declares `gdev_prn_set_procs_planar()` to replace printer buffer callbacks with planar variants.
- Declares `gdev_prn_open_planar()` to conditionally enable planar buffering before opening a printer.
- Declares `gdev_prn_get_params_planar()` and `gdev_prn_put_params_planar()` for adding `UsePlanarBuffer` to a printer's parameter surface.
- Declares `gdev_prn_create_buf_planar()` and `gdev_prn_size_buf_planar()` as planar replacements for default buffer-device creation and sizing.

Notable dependencies:
- Requires `gdevprn.h` in the including compilation unit.

Research notes:
- This header is a thin opt-in extension for printer drivers; the implementation lives in `gdevppla.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.c

Generic Ghostscript printer-device support. It decides whether pages render into full memory buffers or command-list bands, manages printer parameters and output files, synthesizes procedure vectors, and exposes scanline retrieval helpers used by concrete printer drivers.

Key behavior:
- Defines GC hooks for printer devices, treating the underlying storage as either a clist device or forwarding/memory device depending on `buffer_space`.
- `gdev_prn_open` initializes printer memory and optionally opens `OutputFile`; `gdev_prn_close` frees memory and closes an open output stream.
- `gdev_prn_allocate` computes buffer requirements, accounts for PDF 1.4 transparency scratch space, asks driver-specific `get_space_params` for overrides, chooses full bitmap or command-list banding, allocates or resizes storage, opens clist devices when needed, and splices printer procedures with memory/clist rendering procedures.
- `gdev_prn_get_params` and `gdev_prn_put_params` expose printer controls: `MaxBitmap`, `BufferSpace`, band sizing, `OpenOutputFile`, `ReopenPerPage`, `PageUsesTransparency`, optional `Duplex`, and `OutputFile`.
- `gdev_prn_output_page` opens output, optionally upgrades `copypage` to `buffer_page`, calls the concrete `print_page_copies`, flushes and checks file errors, closes per-page files, finalizes clists, and calls `gx_finish_output_page`.
- `gx_default_create_buf_device` creates memory buffer devices and optionally wraps them in a plane extraction device for selected-plane rendering.
- `gdev_prn_get_lines`, `gdev_prn_get_bits`, and `gdev_prn_copy_scan_lines` retrieve rendered scanlines from full memory or clist-backed devices, with trailing-bit cleanup.

Notable dependencies:
- Printer declarations from `gdevprn.h`.
- Ghostscript filename, device, parameter, clist I/O, get-bits, plane extraction, and transparency support.

Research notes:
- This file is a central integration layer for many printer backends in the Ghostscript tree.
- The printer object overlays memory-device and clist-device storage via the `skip` area defined in `gdevprn.h`; procedure-vector restoration is therefore a key invariant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.h

Common Ghostscript header for memory-buffered printer devices. It defines printer storage policy, device structures, printer-specific procedure vectors, device-construction macros, output-file helpers, buffer-device helpers, scanline access APIs, and compatibility aliases used by many printer backends.

Key contents:
- Defines memory/banding defaults for small and large-memory systems.
- Defines `gx_printer_device_procs`, including `print_page`, `print_page_copies`, buffer-device callbacks, `get_space_params`, async render thread/open/close hooks, and `buffer_page`.
- Defines `gdev_prn_space_params` with `MaxBitmap`, `BufferSpace`, band parameters, read-only flag, and banding policy.
- Defines `gx_prn_device_common`, the common embedded state for printer devices: output filename/stream flags, duplex parameters, page transparency flag, clist/memory buffer fields, async rendering state, clist disable mask, and saved original procs.
- Declares standard printer procedures, output-file APIs, color-use APIs, rectangle rendering, scanline reading, trailing-bit clearing, memory allocation/reallocation/freeing, and buffer-device creation.
- Provides macro families for constructing monochrome, color, extended-color, margins, and copies-capable printer devices.

Notable dependencies:
- Core Ghostscript platform, memory, matrix, utility, device, memory-device, clist, render-plane, and parameter headers.

Research notes:
- This header is foundational for most printer output devices in this group, including Plan 9 bitmap and PNG devices.
- Async fields are present in the base printer struct even when normal synchronous printers do not use them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.c

Generic asynchronous printer support for Ghostscript. It creates a writer device that records command lists and a renderer device running in another thread or rendezvous context, connected by a page queue and shared band-list allocator.

Key behavior:
- `gdev_prn_async_write_open` allocates fixed-size renderer memory, allocates locked bandlist memory, forces banding and read-only space parameters, copies the writer device to create the renderer instance, opens the writer as a command-list device, initializes a shared page queue, starts the renderer thread through the driver-supplied hook, waits on an open semaphore, and installs a memory-recovery callback.
- `gdev_prn_async_write_close_device` queues a terminate action, waits for the renderer to drain, closes the writer, and frees async allocations.
- `gdev_prn_async_render_thread` opens the renderer, signals open status, loops over queued full/partial/copy page entries, installs queued `page_info`, runs clist setup, calls output-page behavior according to queue action, finalizes queue entries, and shuts down on terminate.
- `gdev_prn_async_write_put_params` cascades to the original put-params without closing, flushes/reallocates when geometry or space parameters changed, or emits parameter changes into the command list when no reallocation is needed.
- `gdev_prn_async_write_output_page` ends the writer clist page, enqueues a full or copy page, finishes the writer page when appropriate, and reopens new band files, waiting for rendered pages if memory is tight.
- Allocator helpers build a monitor-locked bandlist allocator and a fixed-limit non-GC renderer allocator.

Notable dependencies:
- Async printer API from `gdevprna.h`.
- Ghostscript allocator, device, memory-locking/retry, no-GC, clist, page queue, path, and halftone-cache internals.

Research notes:
- The async implementation relies on concrete drivers supplying `start_render_thread`.
- Comments emphasize deadlock avoidance under low memory.
- Some renderer output errors are mostly ignored because the loop has no clear recovery path.
- `reopen_clist_after_flush` is defined but not used in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.h

Public header and design notes for Ghostscript asynchronous printer rendering.

Key contents:
- Explains the async model: a writer instance records command lists during interpretation, while a renderer instance consumes completed or partial page command lists in another thread/context.
- Documents partial-page behavior under memory pressure and the use of reserve bandlist memory to avoid deadlocks.
- Describes driver obligations for async open: initialize render-thread, buffer-page, print-page-copies, space parameters, and optional parameter/hardware/render open hooks before calling `gdev_prn_async_write_open`.
- Defines `gdev_prn_start_render_params`, carrying the writer device pointer, open semaphore, and renderer open status.
- Provides `init_async_render_procs` macro to install async render-thread, buffer-page, and print-page-copies callbacks.
- Declares `gdev_prn_async_write_open`, `gdev_prn_async_render_open`, and `gdev_prn_async_render_thread`.

Notable dependencies:
- Generic printer support from `gdevprn.h`.
- Semaphore abstraction from `gxsync.h`.

Research notes:
- This header is unusually documentation-heavy and is the best guide for concrete async printer driver integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.h -->