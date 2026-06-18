# Group Research: group_1534_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_devs_mak_sources_os_2d59c5acbc77

Scope checked against `Docs/research_subset_a.md`. All six listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/devs.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/devs.mak

## Purpose

`devs.mak` is Ghostscript's device-driver makefile catalog. It does not implement runtime logic; it declares device names, object dependencies, build recipes, module composition, and library/includes needed to compile display, printer, high-level writer, and raster-output devices.

## Main Structure

- Defines common dependency bundles such as `GDEVH`, `GDEV`, and `PDEVH`.
- Documents the device catalog and conventional `DEVICE_DEVS*` grouping used by higher-level makefiles.
- Provides rules for display devices: DOS EGA/VGA/SVGA, DLL display, Linux `vgalib`, and X11 plus alternate X11 testing devices.
- Provides printer and writer devices: HP PCL/LaserJet, IJS, `rinkj`, PostScript/EPS/PDF writers, and PCL XL writers.
- Provides raster file devices: raw bits, BMP, CGM, DeviceN, XCF, PSD, JPEG, MIFF, PCX, PBM/PGM/PPM/PAM, Plan 9 bitmap, PNG, PostScript image, fax, and TIFF variants.

## Plan 9 / Filesystem Relevance

The file lives in the Plan 9 source tree because this tree vendors Ghostscript. The direct Plan 9-related entry is `plan9bm.dev`, listed as the Plan 9 bitmap format device. It is built from the shared PNM/PBM driver object group `pxm_`, meaning Plan 9 bitmap output is handled by the common portable-map raster driver family rather than a separate large device module.

## Important Build Relationships

- `display.dev` packages `gdevdsp`, color mapping, DeviceN/equivalent color, and CRD support for platforms using Ghostscript's display callback API.
- `x11_.dev` composes X11 core objects and links external X libraries via `XLIBDIRS`/`XLIBS`.
- `pdfwrite.dev` is a large module composed from many `gdevpdf*` objects, compression/filter modules, `psdf.dev`, and `pdtext.dev`.
- `pdtext.dev` / `pdxtext.dev` isolate PDF text extraction/embedding support as a separate logical module used by `pdfwrite`.
- `png*.dev` depends on generated `libpng.dev` and includes the libpng module.
- TIFF fax variants are layered through `fax.dev`, `tfax.dev`, and `tiffs.dev`.

## Dependencies / Interfaces

This makefile relies on Ghostscript make variables supplied elsewhere, including `GLSRC`, `GLOBJ`, `DD`, `GLD`, `OBJ`, `GLCC`, `SETDEV`, `SETPDEV`, `SETMOD`, `ADDMOD`, `ECHOGS_XE`, `XINCLUDE`, `XLIBS`, `PNGGENDIR`, and many header-path variables.

## Research Notes

- This file is mostly build metadata, but it is central to which Ghostscript devices are available in a Plan 9 build.
- Device modules are often hierarchical: small `.dev` targets include common `.dev` modules rather than duplicating object lists.
- Any attempt to add/remove Ghostscript output devices in this tree must update this catalog consistently with the surrounding makefile macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/devs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dirent_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dirent_.h

## Purpose

`dirent_.h` is a Ghostscript portability wrapper for directory-entry headers. It gives the rest of the codebase a single `dir_entry` type regardless of whether the platform exposes POSIX `struct dirent` or older `struct direct` headers.

## Behavior

- Includes `std.h` before any platform header that may include `sys/types.h`.
- Includes `gconfig_.h`, where the build system defines header-availability switches.
- If `HAVE_DIRENT_H` is defined, includes `<dirent.h>` and aliases `struct dirent` to `dir_entry`.
- Otherwise conditionally includes `<sys/dir.h>`, `<sys/ndir.h>`, and/or `<ndir.h>`, then aliases `struct direct` to `dir_entry`.

## Dependencies / Interfaces

- Depends on build-time feature macros from `gconfig_.h`.
- Exports only one public compatibility typedef: `dir_entry`.

## Filesystem Relevance

This is filesystem-adjacent portability infrastructure: it abstracts directory enumeration structure names for Ghostscript code that scans directories. It does not itself open directories, read entries, or implement filesystem behavior.

## Research Notes

The header is intentionally narrow. Its correctness depends entirely on configure/makefile detection setting exactly the right `HAVE_*` macros for the target platform.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dirent_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dmmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dmmain.c

## Purpose

`dmmain.c` is a Macintosh Classic/Carbon example wrapper for running Ghostscript through the shared-library API using Metrowerks CodeWarrior SIOUX. It connects Ghostscript stdio, polling, and display callbacks to a Mac event loop and QuickDraw window.

## Main Components

- Global display format requests 32-bit RGB-style output with unused first byte, 8-bit components, big-endian layout, and top-first rows.
- `IMAGE` tracks one Ghostscript display device instance: handle, device pointer, Mac window, scrollbars, PixMap handle, update timing, and linked-list membership.
- `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr` bridge Ghostscript stdio to SIOUX/std C streams.
- `gsdll_poll` processes Mac events cooperatively and returns `e_Fatal` when the app is quitting.
- `display_callback display` implements Ghostscript display-device hooks.
- Window helpers create, invalidate, resize, scroll, and repaint QuickDraw-backed image windows.
- `main` initializes Mac/SIOUX state, injects `-sDEVICE=display` and `-dDisplayFormat=...`, creates a Ghostscript instance, runs startup PostScript, exits, and then waits for user dismissal.

## Display Flow

1. `display_open` allocates and links an `IMAGE`, then creates a window.
2. `display_presize` rejects incompatible display formats.
3. `display_size` maps Ghostscript's raster buffer into a Mac `PixMap` and updates scrollbars.
4. `display_sync` and `display_page` invalidate the window and poll events.
5. `display_update` rate-limits redraws based on elapsed time.
6. `doUpdateWindow` copies visible pixels from the source PixMap into the window port, respecting scrollbar offsets.

## Filesystem Relevance

There is no filesystem implementation. The file is relevant to the broader Plan 9 tree only as vendored Ghostscript platform glue. It may read from stdin or non-interactive streams, but it does not manage filesystems or storage.

## Risks / Portability Notes

- This code is tied to deprecated Classic Mac OS / Carbon APIs, QuickDraw, and SIOUX.
- The display format is strict; mismatches return `e_rangecheck`.
- User input handling uses a custom SIOUX event-loop workaround to avoid modal console behavior.
- Image lifetime is manual: PixMaps, windows, and heap allocations are disposed in display close paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dmmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dos_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dos_.h

## Purpose

`dos_.h` is a Ghostscript compatibility wrapper for MS-DOS compiler differences. It normalizes port I/O, interrupt helpers, pointer construction, and file-enumeration APIs across Microsoft C, Watcom, and Borland compilers.

## Behavior

- Always includes `<dos.h>`.
- For Watcom or Microsoft compilers:
  - Includes `<conio.h>` for `inp/outp` prototypes.
  - Maps `inport`, `outport`, `inportb`, `outportb`, `enable`, and `disable`.
  - Defines file enumeration wrappers around `_dos_findfirst` and `_dos_findnext`.
  - Splits Watcom-specific flat-model definitions from Microsoft segmented-pointer conventions.
- For other DOS compilers, assumed Borland:
  - Includes `<dir.h>`.
  - Uses `MK_FP`/`FP_OFF`.
  - Uses `findfirst`/`findnext` and `struct ffblk`.

## Dependencies / Interfaces

Exports macros and typedef-like aliases used by DOS-specific Ghostscript device code, especially old display drivers and PC framebuffer support.

## Filesystem Relevance

The file includes DOS file enumeration wrappers, but it is only a portability shim. It does not perform enumeration itself.

## Research Notes

This is legacy platform infrastructure. Modern builds outside DOS should avoid including it unless guarded by device-specific build rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dos_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dpmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dpmain.c

## Purpose

`dpmain.c` is the OS/2 Ghostscript DLL loader and display bridge for a console-mode application. It dynamically loads `GSDLL2.DLL`, resolves the Ghostscript API, and exposes a display callback backed by shared memory and a separate Presentation Manager driver process, `gspmdrv.exe`.

## Main Components

- `GSDLL` stores the loaded DLL module handle and resolved function pointers for revision, instance lifecycle, stdio, display callback, initialization, execution, and exit.
- `gs_load_dll` locates and loads the DLL, tries executable-relative fallback paths, resolves symbols, and checks `GS_REVISION`.
- `IMAGE` tracks one OS/2 display session: shared bitmap memory, semaphores, mutex, queue, PM session/process IDs, image dimensions, raster format, and linked-list state.
- `run_gspmdrv` starts the PM display process with an ID used to share semaphore and memory names.
- `image_color` and `image_palette_size` synthesize palettes for native and grayscale display formats.
- Display callbacks implement open, preclose, close, presize, size, sync, page, update, memory allocation, and memory free.
- `main` determines display depth, injects `-dDisplayFormat=...`, creates a Ghostscript instance, runs startup PostScript, exits, unloads the DLL, and maps Ghostscript result codes to process exit status.

## Display / IPC Flow

1. `display_open` allows only one image window, creates named event/mutex semaphores, allocates up to 13 MiB shared memory, commits an initial page, and writes an empty `BITMAPINFO2`.
2. `display_presize` validates supported display formats and locks the bitmap mutex before resize.
3. `display_size` writes the bitmap header and optional palette, then releases the mutex.
4. `display_memalloc` does not allocate fresh memory; it commits more of the preallocated shared segment and returns a pointer after the BMP header/palette.
5. `display_sync` lazily starts `gspmdrv.exe` once dimensions are known and posts the update event semaphore.
6. `display_preclose` stops the PM session, waits on the termination queue, and closes semaphores.
7. `display_close` frees shared memory.

## Filesystem Relevance

No filesystem implementation is present. The file uses OS/2 module-path discovery and process launching to find `GSDLL2.DLL` and `gspmdrv.exe`, but its main role is display IPC for Ghostscript.

## Risks / Portability Notes

- Multiple image windows are deliberately disabled due to OS/2 child-session termination-queue behavior.
- Shared memory is preallocated large and committed in chunks; failure paths must avoid leaking semaphores or memory.
- The code depends on OS/2 APIs, named semaphores, queues, and Presentation Manager behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dpmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.c

## Purpose

`dscparse.c` implements a streaming parser for Adobe Document Structuring Convention comments, based mainly on DSC 3.0 with selected DSC 2.1 and DCS extensions. It extracts document/page metadata, section offsets, media, bounding boxes, page order, orientation, preview information, color separations, and error/fixup state.

## Public API

- `dsc_init`, `dsc_init_with_alloc`, `dsc_new`, `dsc_ref`, `dsc_unref`, and `dsc_free` manage parser lifetime.
- `dsc_set_length` optionally constrains parsing to a known document length.
- `dsc_scan_data` accepts incremental buffers and advances the parser state.
- `dsc_fixup` finalizes partial or malformed DSC and reconciles section/page metadata.
- `dsc_set_error_function` and `dsc_set_debug_function` install caller callbacks.
- `dsc_add_page`, `dsc_add_media`, and `dsc_set_page_bbox` let callers augment parsed data, including PDF-derived metadata.
- `dsc_find_platefile` maps DCS separation pages to external EPS filenames.
- `dsc_stricmp` provides local case-insensitive comparison.

## Parser Architecture

- The parser is state-machine based, with sections for type detection, comments, preview, defaults, prolog, setup, pages, trailer, and EOF.
- Input is buffered in `CDSC_DATA_LENGTH` chunks, with offsets tracked so section/page byte ranges can be reported.
- `dsc_scan_type` detects PostScript/DSC, EPSF, PJL wrappers, Control-D prefix, DOS EPS headers, PDF headers, MacBinary EPSF, and AppleSingle/AppleDouble wrappers.
- `dsc_read_line` handles CR, LF, CRLF, DOS Ctrl-Z, embedded `%%BeginData`, `%%BeginBinary`, and nested `%%BeginDocument` skipping.
- Metadata parsing functions handle pages, bounding boxes, floating bounding boxes, orientation, page order, media, viewing orientation, and page labels.
- `dsc_scan_*` functions parse allowed comments per DSC section and propagate lines when a section boundary is encountered.

## Metadata Handled

- Document identity: title, creator, creation date, `%%For`, language level, document data mode.
- Page structure: `%%Pages`, `%%Page`, page labels, ordinals, begin/end byte offsets, page order.
- Geometry: `%%BoundingBox`, `%%HiResBoundingBox`, `%%CropBox`, page bounding boxes, page crop boxes, viewing orientation.
- Media: `%%DocumentMedia`, `%%PageMedia`, and older DSC 2.1 paper size/color/form/weight comments.
- Preview/container formats: EPSI, DOS EPS TIFF/WMF, Mac PICT previews.
- Color/separations: `%%DocumentProcessColors`, `%%DocumentCustomColors`, `%%CMYKCustomColor`, `%%RGBCustomColor`, DCS 1.0 plate comments, and DCS 2.0 `%%PlateFile`.

## Error Handling / Fixups

- Error severities are table-driven via `dsc_severity`.
- If no error callback is installed, errors default to “assume DSC was correct” behavior.
- `dsc_fixup` handles common malformed inputs: early trailers/EOF, page-count mismatches, missing EPS bounding boxes, EPS files with multiple pages, missing default media, unlabeled pages, and DCS 2.0 page exposure.
- Begin/end counters validate font, feature, resource, and procset blocks.

## Memory Model

- Supports caller-supplied allocators.
- Uses chunked string storage (`CDSCSTRING`) for persistent parsed strings.
- Dynamically grows page and media arrays.
- Frees per-page boxes/orientation, media boxes, DCS lists, color lists, Mac/DOS wrapper metadata, and string chunks during reset/free.

## Filesystem Relevance

This is document-structure parsing, not filesystem code. It is relevant to file-oriented workflows because it records byte offsets for document sections/pages and can identify external DCS plate filenames, but it does not open, read, or write files directly.

## Research Notes

- The parser is deliberately tolerant of real-world malformed PostScript/EPS files.
- Streaming behavior is central: callers can feed partial buffers, and the parser requests more data when container headers or lines are incomplete.
- `%%+` continuation support is intentionally limited to comments where repeated parameter sets are expected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dscparse.c -->