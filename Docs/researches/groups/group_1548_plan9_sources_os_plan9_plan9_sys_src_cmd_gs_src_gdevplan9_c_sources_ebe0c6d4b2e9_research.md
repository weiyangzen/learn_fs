# Group Research: group_1548_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevplan9_c_sources_ebe0c6d4b2e9

Scope: `Docs/research_subset_a.md`, specifically the `sources/os/plan9/plan9` source tree. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplan9.c

This file implements the Ghostscript `plan9` printer device, producing Plan 9 compressed image/bitmap output. It is a Ghostscript printer device built on `gdevprn.h`, but contains substantial Plan 9 image format logic rather than delegating to a library.

The device type is `plan9_device`, extending `gx_device_common` and `gx_prn_device_common` with `dither`, current/last `ldepth`, and a `cmapcall` flag. `gs_plan9_device` is configured as an RGB printer device at 100 DPI with 24-bit color information and `plan9_print_page` as the page writer. The active procedure vector uses the standard printer open/output/close path plus Plan 9 color mapping procedures.

Color mapping uses 8 bits per component. `plan9_rgb2cmap` packs RGB as `0xBBGGRR` and also infers the minimal Plan 9 bitmap depth required for the page: 1-bit black/white, 4-bit grayscale, or 24-bit true color. `plan9_cmap2rgb` reverses that mapping and rejects values above 24 bits.

`plan9_print_page` reads Ghostscript raster lines through `gdev_prn_get_bits`, chooses the Plan 9 channel string (`k1`, `k4`, or `r8g8b8`), repacks rows for 1-bit or 4-bit output, pads trailing partial bytes, and writes compressed image blocks to the output `FILE`. Anti-aliasing forces at least 4-bit grayscale when needed.

The lower half of the file is an embedded Plan 9 compressed-image writer adapted from `fb/bit2enc`. It defines `WImage`, hash chains, dump buffers, a 1024-byte sliding window, and block output framing. `initwriteimage` writes the Plan 9 `compressed` image header, `gobbleline` performs LZ-style match/dump encoding, `writeimageblock` streams rows and finalizes/free the writer, and `bytesperline`/`unitsperline` mirror Plan 9 drawing-library scanline sizing.

Filesystem relevance: this is output-format code inside the Plan 9 Ghostscript tree. It writes a Plan 9 compressed bitmap stream to Ghostscript's output file path, but it is not a filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.c

This file implements Ghostscript's plane extraction forwarding device. A plane extraction device presents the same color-capable interface as its target, but redirects rendering for one selected bit plane into a separate plane device, normally a memory device.

The core public initializer is `plane_device_init`, which clones the target device parameters, stores the target and plane device, records the requested `gx_render_plane_t`, opens the wrapper, and optionally clears the plane device to white. The device prototype `gs_plane_extract_device` overrides drawing procedures such as rectangle fill, monochrome/color copies, alpha copy, path fill/stroke, masks, parallelograms, triangles, tiled rectangles, RasterOp copies, typed images, and get-bits rectangle.

The main reduction mechanism is `reduce_drawing_color`. It attempts to transform a Ghostscript drawing color into an equivalent color for the selected plane. It handles pure colors, binary halftones, and colored halftones. It can skip operations that would only write plane-white before any marks have occurred, using `any_marks` as an optimization. It also accounts for RasterOp texture transparency, rejecting cases where plane-only reduction would be semantically unsafe.

For source pixmaps and tiles, the file defines `tiling_state_t` and helpers `begin_tiling`, `extract_partial_tile`, `next_tile`, and `end_tiling`. These allocate or reuse small local buffers, extract the requested plane with `bits_extract_plane`, and process large operands in subtiles when required.

Most drawing procedures reduce colors and forward to the plane device when safe, otherwise they fall back to Ghostscript defaults so the full target semantics are preserved. `plane_copy_color` has a direct fast path when the plane device is a compatible memory device. `plane_strip_copy_rop` reduces source/texture colors when possible, but punts to the default implementation for transparency-heavy RasterOps.

The image path wraps a target image enumerator with `plane_image_enum_t`, replaces color-map procedures so image colors are reduced as they are produced, and frees copied imager state on image end. The readback path supports planar single-plane retrieval and can expand a plane back into chunky pixels for default RasterOp use.

Filesystem relevance: none directly. This is raster-buffer infrastructure used by printer and banding devices, including files in this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.h

This header declares the plane extraction device implemented in `gdevplnx.c`. It describes the purpose and constraints of `gx_device_plane_extract`: to appear like a normal color-capable target while rendering only one selected color plane into another device.

The main structure embeds `gx_device_forward_common`, then stores a `gx_device *plane_dev`, a `gx_render_plane_t plane`, computed open-time fields `plane_white`, `plane_mask`, and `plane_dev_is_memory`, plus the dynamic `any_marks` optimization flag. The comments explain that the original use case is band-list rendering for plane-oriented color printers, where each plane is rasterized separately and operations writing only white can often be skipped before any non-white mark appears.

The header also declares `public_st_device_plane_extract()` for Ghostscript structure/GC metadata and exposes:

- `plane_device_init(gx_device_plane_extract *edev, gx_device *target, gx_device *plane_dev, const gx_render_plane_t *render_plane, bool clear)`

The documented depth constraints are important for callers: target and plane-extract depths are limited to 32 bits, while each extracted plane is limited to 8 bits.

Filesystem relevance: none directly. It is printer/raster device infrastructure, especially for banded and planar rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.c

This file implements the OS/2 Presentation Manager display device for Ghostscript. Despite being in the Plan 9 source tree copy, it is OS/2-specific display integration, not Plan 9 code.

The file defines `gx_device_pm`, which embeds Ghostscript device state, PM-specific control fields, and a `gx_device_memory` backing device. The PM-specific fields include `BitsPerPixel`, `UpdateInterval`, `GSVIEW`, `dll`, palette size, update timer, shared-memory bitmap pointer, semaphores, mutexes, queues, session IDs, process IDs, and a `BITMAPINFO2` header.

Two devices are defined: `gs_os2pm_device` for the outboard PM driver model and, under `__DLL__`, `gs_os2dll_device` for DLL embedding. `pm_open` creates or opens the necessary OS/2 shared memory and synchronization objects. In non-DLL mode it can either cooperate with PM GSview via pre-existing queue/semaphore names or start `gspmdrv.exe` as a child PM session using `DosStartSession`. It allocates a large shared bitmap region, commits pages on demand, initializes BMP header fields, palette data, and the Ghostscript memory device.

Rendering operations (`pm_fill_rectangle`, `pm_copy_mono`, `pm_copy_color`) delegate to the embedded memory device, then call `pm_update`, which either posts a timer/event or sends queue messages so the display process refreshes. `pm_sync_output`, `pm_output_page`, and `pm_close` coordinate page display, foregrounding the PM session, GSview begin/end/page events, and cleanup.

Color support is parameterized by `BitsPerPixel` values 1, 4, 8, and 24. `pm_set_bits_per_pixel` updates Ghostscript color info and encode/decode procedures; `pm_makepalette` builds OS/2 BMP palettes; 8-bit mode dynamically adds palette colors until reserving entries for PM and other apps.

`pm_get_params`/`pm_put_params` expose `UpdateInterval`, `GSVIEW`, and `BitsPerPixel`, resizing/reinitializing the bitmap while holding the bitmap mutex if dimensions or depth change. Debug-only `pm_write_bmp` can dump `out.bmp`.

Filesystem relevance: limited to file/process interfaces. The driver uses OS/2 shared memory, queues, semaphores, session control, and optionally writes a BMP for testing, but does not implement filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.h

This header contains constants shared by the OS/2 PM Ghostscript display driver, the external `gspmdrv` process, and PM GSview.

It defines named object format strings for OS/2 interprocess communication:

- `SHARED_NAME` for shared bitmap memory.
- `SYNC_NAME` and `NEXT_NAME` for event semaphores.
- `MUTEX_NAME` for the bitmap mutex semaphore.
- `QUEUE_NAME` for driver message queues.

It also defines integer message IDs exchanged over the queues:

- `GS_UPDATING`
- `GS_SYNC`
- `GS_PAGE`
- `GS_CLOSE`
- `GS_ERROR`
- `GS_PALCHANGE`
- `GS_BEGIN`
- `GS_END`

These values are consumed by `gdevpm.c` when it posts display-update, synchronization, page, palette-change, and lifecycle events to GSview or `gspmdrv.exe`.

Filesystem relevance: none. This is OS/2 IPC naming and message protocol metadata for a display driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpng.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpng.c

This file implements Ghostscript PNG output devices using libpng. It defines printer-style devices for monochrome, indexed color, grayscale, RGB, high-depth RGB, and RGBA-with-coverage output.

The standard devices are:

- `pngmono`: 1-bit grayscale.
- `png16`: 4-bit palette color using PC-style 4-bit mapping.
- `png256`: 8-bit palette color using PC-style 3/3/2 mapping.
- `pnggray`: 8-bit grayscale.
- `png16m`: 24-bit RGB.
- `png48`: 48-bit RGB.
- `pngalpha`: 32-bit RGBA, with alpha representing pixel coverage rather than full PDF transparency.

All normal devices use `png_print_page`, which allocates one raster row, creates libpng write/info structures, initializes output to the Ghostscript printer `FILE`, writes pHYs resolution metadata, selects PNG color type/bit depth from `pdev->color_info.depth`, emits a palette when needed, adds a `Software` text chunk, then streams scanlines from `gdev_prn_copy_scan_lines` to `png_write_rows`. It handles alpha inversion for `pngalpha`, mono inversion for 1-bit output, and byte swapping for 16-bit RGB on little-endian platforms.

`pngalpha` has its own device structure containing the original fill-rectangle procedure and a `BackgroundColor` parameter. `pngalpha_open` installs a custom buffer-device creation hook and intercepts full-page white fills. `pngalpha_fill_rectangle` converts a full-page white erase into a transparent fill. `pngalpha_encode_color` stores pixels as `0xRRGGBB00`, with inverted coverage in the low byte so fully opaque white does not collide with `gx_no_color_index`. `pngalpha_copy_alpha` implements coverage compositing into an RGBA memory buffer by reading old pixels, computing new coverage, blending color components, and writing accumulated pixels back.

Filesystem relevance: output file serialization only. The code writes PNG data through Ghostscript's printer output file abstraction; it does not implement storage or filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpnga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpnga.c

This file is a test driver for PDF 1.4 transparency rendering to PNG. It is separate from `pngalpha` in `gdevpng.c`: it builds a custom PDF 1.4-style compositing stack and outputs RGBA PNG data from that stack.

The central data structures are `pdf14_buf` and `pdf14_ctx`. A `pdf14_buf` represents one transparency group buffer in planar layout: pixel planes, alpha, optional shape, and optional group alpha. It records isolation, knockout, group alpha/shape, blend mode, rectangle, rowstride, planestride, channel count, plane count, and data pointer. `pdf14_ctx` owns a stack of these buffers for the current page.

Buffer management includes Ghostscript GC metadata, `pdf14_buf_new/free`, `pdf14_ctx_new/free`, and group stack operations. `pdf14_push_transparency_group` creates a new buffer, optionally initializes it from the backdrop, treats knockout groups as isolated via a documented hack, and sets shape/alpha plane requirements. `pdf14_pop_transparency_group` composites the top buffer back into the saved buffer using functions from `gxblend.h`, including isolated group, recomposite group, and simplified knockout paths.

The exported device `gs_pnga_device` uses `pnga_procs`, with handlers for open, close, output_page, path fill/stroke, typed image begin, text begin, and transparency group begin/end. `pnga_open` allocates the base RGBA context. `pnga_output_page` writes the current planar RGBA buffer to a scratch file via libpng using `gp_open_scratch_file` rather than the normal `OutputFile` path; a comment notes this as a TODO.

Marking is routed through a temporary `pnga_mark_device` produced by `pnga_get_marking_device`. Path, image, and text operations are delegated to Ghostscript defaults on that marking device, whose fill-rectangle operations composite into the active PDF14 buffer. Text uses a wrapper `pnga_text_enum_t` to forward text enum operations to the target enumerator while preserving Ghostscript text state.

Filesystem relevance: only scratch-file output. This is transparency/raster compositing test infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpnga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.c

This file implements helper support for Ghostscript printer devices that want planar buffering. It is a small adapter layer over the generic printer buffer hooks and memory planar-device support.

`gdev_prn_set_procs_planar` replaces a printer device's buffer creation and sizing procedures with `gdev_prn_create_buf_planar` and `gdev_prn_size_buf_planar`. `gdev_prn_open_planar` conditionally installs those hooks based on a `UsePlanarBuffer` boolean before calling `gdev_prn_open`.

`gdev_prn_get_params_planar` and `gdev_prn_put_params_planar` augment standard printer get/put parameter handling with the `UsePlanarBuffer` parameter. The put path only reads the parameter for multi-component devices, delegates ordinary printer params to `gdev_prn_put_params`, and commits the new boolean only if parameter handling succeeds.

The private helper `gdev_prn_set_planar` configures a `gx_device_memory` as a planar memory device. It supports 3- or 4-component color, computes per-plane depth from total color depth, rounds depth up to a power of two if necessary, and orders planes so the most significant plane is emitted first.

`gdev_prn_create_buf_planar` first uses `gx_default_create_buf_device`, then converts memory buffer devices to planar mode. `gdev_prn_size_buf_planar` mirrors the memory sizing calculation for planar layout, computing bit storage, line pointer storage, and raster size for the first plane.

Filesystem relevance: none. This is raster memory layout support for printer buffering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.h

This header declares the planar printer buffering helper API implemented by `gdevppla.c`.

The exposed functions are:

- `gdev_prn_set_procs_planar(gx_device *pdev)`, which installs planar buffer procedure hooks in a printer device.
- `gdev_prn_open_planar(gx_device *pdev, bool upb)`, which conditionally enables planar buffering and then opens the printer.
- `gdev_prn_get_params_planar(...)` and `gdev_prn_put_params_planar(...)`, which add the `UsePlanarBuffer` parameter around the standard printer parameter API.
- `gdev_prn_create_buf_planar(...)`, a replacement buffer-device creation hook for planar mode.
- `gdev_prn_size_buf_planar(...)`, a replacement buffer-size hook for planar mode.

The header notes that it requires `gdevprn.h` and is intended for printer devices that choose planar buffers instead of the default chunky memory buffer.

Filesystem relevance: none. It is a declaration-only printer/raster support header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.c

This file is Ghostscript's generic printer driver support layer. It manages printer device opening/closing, output files, memory-vs-banded rendering, command-list setup, buffer devices, scanline extraction, printer parameters, and page output dispatch.

Printer devices are implemented as a union-like structure that can behave either as a memory device or a command-list device. `gdev_prn_open` allocates rendering memory via `gdev_prn_allocate_memory` and optionally opens the output file. `gdev_prn_close` frees memory and closes the current file. `gdev_prn_allocate` is the core allocator: it computes required memory, asks device-specific `get_space_params`/buffer hooks for effective sizing, decides between full-page memory rendering and command-list banding, allocates or resizes backing memory, initializes clist or memory buffer devices, and synthesizes the live device procedure vector by combining render procedures from the selected buffer type with non-rendering procedures from the printer device.

Command-list setup is handled by `gdev_prn_setup_as_command_list`, which allocates command-list buffer space with fallback sizing and opens the clist writer. `gdev_prn_tear_down` reverses either command-list or memory-buffer setup and restores original procedures. Reallocation on parameter changes is handled by `gdev_prn_maybe_realloc_memory`.

Parameter handling exposes `MaxBitmap`, `BufferSpace`, band dimensions, `BandBufferSpace`, `OpenOutputFile`, `ReopenPerPage`, `PageUsesTransparency`, optional `Duplex`, and `OutputFile`. It validates output-file format strings and reads media dictionaries for type checking.

`gdev_prn_output_page` opens the printer file, optionally upgrades `copypage` to `buffer_page`, invokes `print_page_copies`, flushes and checks file errors, closes/reopens per output policy, finishes command-list pages, and calls `gx_finish_output_page`.

The file also supplies public services for printer drivers: rendering plane initialization, colors-used queries for clist bands, buffer-device creation/destruction, memory buffer setup, scanline retrieval (`gdev_prn_get_lines`, `gdev_prn_get_bits`, deprecated `gdev_prn_copy_scan_lines`), trailing-bit clearing, print-scan-line count calculation, output-file open/close helpers, and default async-rendering stubs.

Filesystem relevance: this is the main file-output abstraction for Ghostscript printer devices in this group. It opens/closes named output files through Ghostscript's platform layer, but its core subject is raster printer buffering, not filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.h

This header defines the common API, state layout, procedure vectors, and construction macros for Ghostscript memory-buffered printer devices.

It begins by defining memory policy constants for small and large-memory systems: `PRN_MAX_BITMAP`, `PRN_BUFFER_SPACE`, `PRN_MIN_MEMORY_LEFT`, and `PRN_MIN_BUFFER_SPACE`. These determine when a printer renders a full bitmap in memory versus using command-list banding.

`gx_printer_device_procs` is the printer-specific procedure table. It includes `print_page`, `print_page_copies`, buffer-device procedures, `get_space_params`, async render-thread/open/close hooks, and `buffer_page`. This is layered alongside the normal Ghostscript `gx_device_procs`.

`gdev_prn_space_params` stores `MaxBitmap`, `BufferSpace`, `gx_band_params_t`, a read-only flag, and explicit banding mode (`BandingAuto`, `BandingAlways`, `BandingNever`). `gx_prn_device_common` defines the common printer device fields: space parameters, `OutputFile` name, output-file flags, transparency/duplex flags, file state, command-list buffer state, async-rendering state, memory allocators, page queue, clist disable mask, and original device procedures. `gx_device_printer` embeds `gx_device_common` plus these fields.

The header declares standard printer procedures (`gdev_prn_open`, `gdev_prn_output_page`, `gdev_prn_close`, get/put params), default printer-specific callbacks, and procedure-vector construction macros such as `prn_procs`, `prn_color_procs`, and `prn_color_params_procs`.

A large macro section builds printer device descriptors with margins, resolution, color depth, process color fields, and default printer state. These macros are used by nearby devices such as PNG and Plan 9 output.

The utility declarations cover output-file opening/closing, file-new checks, raster size, colors-used queries, rectangle rendering, scanline retrieval, trailing-bit clearing, print-scan-line count, memory allocation/reallocation/free, and buffer-device creation. Compatibility aliases preserve older Ghostscript driver names.

Filesystem relevance: the header defines how printer drivers name and open output files, but otherwise represents raster/printer infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.c

This file implements generic asynchronous printer support for Ghostscript. It allows interpretation/writing of command lists and rasterization/printing to overlap using two device instances: a writer and a renderer.

`gdev_prn_async_write_open` is the main entry for concrete async printer drivers. It allocates a fixed-size renderer memory arena, creates a locked band-list allocator shared by writer and renderer, forces banding mode to `BandingAlways`, copies the device for the renderer, opens the writer as a command-list printer, initializes async-specific writer procedures, allocates and initializes a shared page queue, configures renderer band parameters from the writer, starts the render thread through the driver's `start_render_thread` callback, waits for renderer open completion via semaphore, and installs a memory-recovery callback.

The writer side overrides close, output_page, put_params, and hardware-param procedures. `gdev_prn_async_write_output_page` ends the current command-list page, queues it as full-page or copy-page work, finishes the Ghostscript page if flushed, and reopens new band files, waiting for the renderer to free memory if needed. `flush_page` queues partial or full page data without closing band files normally. `gdev_prn_async_write_put_params` distinguishes geometry/space changes, which require flushing and reallocating clist memory, from parameter changes that can be emitted into the command list with `cmd_put_params`.

The renderer side is driven by `gdev_prn_async_render_thread`. It opens the renderer device, verifies clist tile-cache compatibility, marks the renderer as open, then loops on page-queue entries until a terminate action arrives. For each queued page it copies page info to the renderer clist, sets up clist parameters, and dispatches output-page work according to full, partial, or copy-page action. It closes the renderer and acknowledges termination before returning.

Memory management is central. `alloc_bandlist_memory` wraps a data allocator in `gs_memory_locked_t` because band-list allocation happens on the writer thread and deallocation on the renderer thread. `alloc_render_memory` creates a fixed-limit allocator and disables normal GC assumptions for the renderer arena. `prna_mem_recover` lets the writer wait for queued pages to render when ordinary allocation fails.

Filesystem relevance: indirect. It manages command-list/band-list files and page queues for asynchronous raster output, but the code is about printer scheduling and memory isolation, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.h

This header documents and declares the asynchronous printer support implemented in `gdevprna.c`.

The long design comment is the most important content. It explains that async drivers create two instances of the same printer device: a writer instance used by the interpreter to build command lists, and a renderer instance used by a separate thread to rasterize queued command-list pages. The normal path queues complete pages, while low-memory situations can queue partial pages so the renderer can free command-list memory and let interpretation continue.

The header documents the memory-safety model: the writer reserves enough band-list memory to queue partial pages, while the renderer runs in a fixed memory space. To make this practical, the writer restricts command-list content by avoiding complex paths, pre-clipping output unless the clip path is simple, and limiting high-level images. This is described as a "restricted bandlist format."

The opening protocol requires concrete drivers to call `gdev_prn_async_write_open` instead of `gdev_prn_open`, after installing required callbacks such as `start_render_thread`, `buffer_page`, and `print_page_copies`, and setting band sizing parameters. The render thread must call `gdev_prn_async_render_thread` with the start-render parameter block.

`gdev_prn_start_render_params_s` carries the writer device pointer, an open semaphore for synchronization, and the renderer open status. `init_async_render_procs` is a convenience macro for installing the driver callbacks required by the async layer.

The declared public functions are:

- `gdev_prn_async_write_open(...)`
- `gdev_prn_async_render_open(...)`
- `gdev_prn_async_render_thread(...)`

Filesystem relevance: indirect through command-list/band-list file management. The header is primarily concurrency, memory, and printer-driver architecture documentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.h -->