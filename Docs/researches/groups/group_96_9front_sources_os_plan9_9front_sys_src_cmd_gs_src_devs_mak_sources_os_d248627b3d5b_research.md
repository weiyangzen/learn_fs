# Group Research: group_96_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_devs_mak_sources_os_d248627b3d5b

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/devs.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/devs.mak

This is Ghostscript's central makefile fragment for Aladdin/Artifex-maintained device drivers. It catalogs display, printer, high-level writer, raster image, fax, TIFF, PNG, JPEG, and utility devices, then defines the object/module rules used by platform makefiles to include those devices in a build.

Key responsibilities:
- Defines common device dependencies through `GDEVH`, `GDEV`, and printer dependency `PDEVH`.
- Documents the intended `DEVICE_DEVS` through `DEVICE_DEVS20` grouping convention, partly constrained by MS-DOS command-line length limits.
- Lists supported driver names and their user-facing purpose, including MS-DOS EGA/VGA/SVGA, X11, label printers, HP PCL devices, fax/TIFF devices, PNG/JPEG/BMP/PCX/PBM/PNM file devices, and high-level PDF/PS/PCL XL writers.
- Builds shared support objects such as `gdevpccm`, `gdevpcfb`, `gdevpsu`, `gdevdcrd`, `gdevdevn`, `gsequivc`, and format-specific helper objects.
- Uses Ghostscript build tools/macros such as `$(SETDEV)`, `$(SETDEV2)`, `$(SETPDEV)`, `$(SETPDEV2)`, `$(SETMOD)`, and `$(ADDMOD)` to assemble `.dev` modules.
- Pulls in external or separately built libraries for some devices, such as X11 libraries, vgalib, IJS, libpng, zlib filters, JPEG/DCT filters, LZW/RLE/CCITT filters, and ICC-enabled code.

Major device groups:
- Display devices: `ega`, `vga`, `svga16`, chipset-specific SVGA devices, `s3vga`, `display`, `lvga256`, `vgalib`, and X11 variants including CMYK/gray/mono/testing modes.
- Printer devices: Practical Automation `atx*`, HP DeskJet/LaserJet/PCL devices, `lj5mono`, `lj5gray`, and the IJS and Rinkj client paths.
- High-level output: shared `psdf`, `epswrite`, `pswrite`, `pdfwrite`, `ps2write`, `pdtext`/`pdxtext`, and `pxlmono`/`pxlcolor`.
- Raster/file outputs: `bit*`, `bmp*`, `cgm*`, `spotcmyk`, `devicen`, `xcf`, `psd*`, `perm`, `jpeg*`, `miff24`, `pcx*`, `pbm`/`pgm`/`ppm`/`pnm`/`pam`, `plan9bm`, `png*`, `pnga`, `psmono`/`psgray`/`psrgb`, fax, and TIFF variants.

Notable implementation details:
- `plan9bm.dev` is present as a Ghostscript raster output device for Plan 9 bitmap format, but this file itself is still generic Ghostscript build metadata.
- PNG devices depend on generated `libpng.dev` and include libpng via `png_i_`.
- `pdfwrite.dev` also creates `ps2write` and includes a large set of filter, color, text, and `psdf` modules.
- The PDF text subsystem is split into its own `pdtext`/`pdxtext` module due to size and complexity.
- Some devices are explicitly marked as contributed or hardware-dependent, and the comments direct users away from Aladdin support for those cases.
- Several historical platform assumptions are embedded, including MS-DOS, SCO/Xenix direct framebuffer notes, vgalib, and legacy printer guidance.

Filesystem relevance:
- This is build orchestration, not filesystem implementation.
- It defines output devices that may write files, including `plan9bm`, PNG/JPEG/TIFF/BMP/PNM/PDF/PS outputs, but file I/O behavior lives in the corresponding C device implementations and Ghostscript I/O layers.
- Its relevance to subset A is source-tree inventory coverage under the 9front Ghostscript tree, not OS VFS or storage behavior.

Research classification: Ghostscript device build catalog and module recipe file, broad build-surface metadata for display/printer/file-format drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/devs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dirent_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dirent_.h

This is a portability shim for Unix directory-entry headers in Ghostscript.

Key responsibilities:
- Includes `std.h` before any system header that may include `sys/types.h`.
- Includes `gconfig_.h`, whose configure/build-time macros describe which directory-entry header exists on the target.
- If `HAVE_DIRENT_H` is set, includes `<dirent.h>` and typedefs `struct dirent` as `dir_entry`.
- Otherwise conditionally includes older alternatives `<sys/dir.h>`, `<sys/ndir.h>`, or `<ndir.h>`, then typedefs `struct direct` as `dir_entry`.

Important dependencies:
- The header is declared in `lib.mak` as `dirent__h=$(GLSRC)dirent_.h $(std_h) $(gconfig__h)`.
- It is used by Unix filesystem portability code such as `gp_unifs.c`.

Notable implementation details:
- The public abstraction is intentionally tiny: one normalized `dir_entry` typedef.
- Header selection is entirely macro-driven; no runtime behavior is present.
- It supports older Unix systems that predate or do not expose POSIX `dirent.h`.

Filesystem relevance:
- This is adjacent to filesystem portability because it normalizes directory enumeration structures for Ghostscript's platform layer.
- It does not implement directory traversal, path lookup, VFS behavior, or storage logic itself.

Research classification: small Ghostscript portability header for directory-entry type normalization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dirent_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dmmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dmmain.c

This is a Macintosh Classic/Carbon example wrapper for running Ghostscript through the shared-library API with the `display` device. It was contributed by Nigel Hathaway and uses Metrowerks CodeWarrior SIOUX for command-line console behavior.

Key responsibilities:
- Initializes the Mac operating environment, SIOUX console, AppleEvent quit handler, cursor/event state, and scrollbar callback.
- Creates a Ghostscript instance with `gsapi_new_instance`, configures stdio, polling, and display callbacks, then runs normal Ghostscript startup via `gsapi_init_with_args` and `gsapi_run_string("systemdict /start get exec\n")`.
- Forces `-sDEVICE=display` and injects `-dDisplayFormat=<display_format>` into the command-line arguments.
- Implements Ghostscript stdio callbacks: `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr`.
- Implements cooperative polling with `gsdll_poll`, forwarding pending Mac events into the local event loop.
- Implements `display_callback` functions for open, preclose, close, presize, size, sync, page, and update events.
- Maintains a linked list of `IMAGE` records, each binding a Ghostscript display handle/device pair to a Mac `WindowRef`, scrollbars, `PixMapHandle`, and update timing state.

Display behavior:
- Uses `DISPLAY_COLORS_RGB | DISPLAY_UNUSED_FIRST | DISPLAY_DEPTH_8 | DISPLAY_BIGENDIAN | DISPLAY_TOPFIRST`.
- `display_presize` rejects incompatible display formats.
- `display_size` binds Ghostscript's raster pointer directly into a QuickDraw `PixMap`, checks the QuickDraw row-byte limit, and refreshes scrollbars/window invalidation.
- `display_sync`, `display_page`, and `display_update` invalidate or throttle window redraws and process events.
- `doUpdateWindow` paints the current PixMap into the visible window area, with scrollbar offsets and gray fill outside the image bounds.

UI/event behavior:
- `get_input` works around SIOUX modal input by collecting console text through an event loop and returning buffered line data to Ghostscript.
- `window_create`, `window_invalidate`, and `window_adjust_scrollbars` manage Carbon/Classic window and scrollbar state.
- `doEvents`, `doMouseDown`, `doUpdate`, `doOSEvent`, `doInContent`, and `actionFunctionScroll` handle menus, dragging, resizing, zooming, update events, OS suspend/resume, and scrollbar tracking.
- `quitAppEventHandler` marks the global quit flag when the application receives a valid quit AppleEvent.

Notable implementation details and risks:
- This is highly platform-specific historical Mac code, dependent on Carbon, QuickDraw, SIOUX, and CodeWarrior target macros.
- It assumes a 32-bit-style QuickDraw PixMap layout and explicitly rejects rasters too large for QuickDraw row-byte encoding.
- The display memory is owned by Ghostscript; this wrapper only points QuickDraw at it.
- The code uses global process state (`gDone`, `instance`, `first_image`, SIOUX globals) rather than an isolated application object.
- It contains old C idioms such as assignment in conditions and minimal error recovery, appropriate to its historical sample-wrapper role.

Filesystem relevance:
- This file does not implement filesystem behavior.
- It only reads command-line arguments and delegates Ghostscript input/output through stdio callbacks.
- Its relevance is as a platform wrapper in the 9front-vendored Ghostscript tree.

Research classification: historical Mac Classic/Carbon Ghostscript shared-library display wrapper and event-loop integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dmmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dos_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dos_.h

This is a Ghostscript portability header for MS-DOS compiler differences. It normalizes low-level DOS I/O, interrupt, pointer, and file-enumeration interfaces across Microsoft C, Watcom C, and Borland C.

Key responsibilities:
- Includes `<dos.h>` and, for Microsoft/Watcom, `<conio.h>` because port I/O prototypes are there for those compilers.
- Maps port I/O APIs to common names: `inport`, `inportb`, `outport`, and `outportb`.
- Maps interrupt enable/disable calls to `_enable()` and `_disable()` on Microsoft/Watcom.
- Defines segment/pointer helpers `MK_PTR` and `PTR_OFF`, with different behavior for Watcom flat model, Microsoft, and Borland segmented model.
- Normalizes register-union field selection through `rshort`.
- Normalizes DOS file enumeration structures and functions:
  - Microsoft/Watcom use `_dos_findfirst`, `_dos_findnext`, `struct find_t` or `struct _find_t`, and `ff_name name`.
  - Borland uses `<dir.h>`, `findfirst`, `findnext`, and `struct ffblk`.

Important dependencies:
- Declared in `lib.mak` as `dos__h=$(GLSRC)dos_.h`.
- Used by DOS/platform files such as `gp_iwatc.c`, `gp_dosfs.c`, `gp_dosfe.c`, `gp_msdos.c`, `zdosio.c`, and hardware/display-related code such as `gdevherc.c` and `gdevpcfb.h`.

Notable implementation details:
- The file deliberately abstracts several incompatible DOS compiler memory models.
- It includes direct I/O port support, which is relevant to old display/printer hardware paths.
- It defines `O_BINARY`, `fdopen`, `stdprn`, and related aliases for Microsoft C compatibility.

Filesystem relevance:
- The file touches file enumeration abstractions for DOS builds, but it does not perform enumeration itself.
- It is a portability layer used by Ghostscript's DOS filesystem/platform code.
- No Plan 9 filesystem, VFS, or storage logic is present.

Research classification: historical MS-DOS compiler compatibility shim for Ghostscript platform and device code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dos_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dpmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dpmain.c

This is the OS/2 Ghostscript DLL loader for a console-compatible executable. It dynamically loads `GSDLL2.DLL`, drives Ghostscript through the DLL API, and uses a separate Presentation Manager helper process, `gspmdrv.exe`, to display rendered pages.

Key responsibilities:
- Loads and unloads the Ghostscript DLL with `DosLoadModule` and `DosFreeModule`.
- Resolves required GS API entry points by name: revision, instance lifecycle, stdio, poll, display callback, init, run string, and exit.
- Verifies that the loaded DLL revision matches the build's `GS_REVISION`.
- Implements stdio callbacks backed by `read`, `fwrite(stdout)`, and `fwrite(stderr)`.
- Determines display depth/capabilities from OS/2 PM/GPI calls and prepends a suitable `-dDisplayFormat=` argument.
- Runs Ghostscript startup with `gsdll.init_with_args`, then executes `systemdict /start get exec\n`, exits the instance, unloads the DLL, and maps Ghostscript return codes to process exit status.

Display architecture:
- `display_open` creates one `IMAGE` record, disallows multiple windows, derives a per-device ID from process/device values, and creates named OS/2 semaphores and shared memory.
- Shared memory is allocated under `\SHAREMEM\...` and initially committed in `MIN_COMMIT` chunks.
- `run_gspmdrv` starts `gspmdrv.exe` as a related child PM session using `DosStartSession`, passing the generated display ID.
- `display_preclose` stops the PM session, waits on its termination queue, and closes synchronization objects.
- `display_close` frees shared bitmap memory.
- `display_presize` validates supported formats and locks the bitmap mutex while size parameters are changing.
- `display_size` writes an OS/2 `BITMAPINFO2` header and optional palette into shared memory.
- `display_memalloc` does not allocate fresh memory; it commits more of the preallocated shared memory and returns a pointer just past the BMP header/palette for Ghostscript's raster.
- `display_sync` lazily starts `gspmdrv.exe` after the image size is known and posts the update semaphore.
- `display_update` is a no-op because the PM helper process owns repaint behavior.

Supported display formats:
- Native or gray 1/4/8-bit indexed formats.
- RGB 8-bit-per-component without alpha.
- The chosen default depends on desktop display depth and palette-manager availability.

Notable implementation details and risks:
- Multiple display windows are intentionally disabled because OS/2 related child sessions and termination queues do not handle the old one-session-per-window design safely.
- The shared memory reservation is fixed at about 13 MB, with chunked commit.
- The code assumes the Ghostscript memory device places the raster immediately at the memory pointer returned by `display_memalloc`.
- There is limited cleanup on some mid-`display_open` failure paths; this is historical sample/platform code.
- `display_memfree` is declared `int` but does not return a value, reflecting old C/platform code style.

Filesystem relevance:
- This file uses OS/2 module loading, process/session creation, queues, semaphores, and shared memory.
- It does not implement filesystem logic, beyond locating/loading DLLs and helper executables via OS/2 APIs.
- Its relevance is platform integration for Ghostscript in the vendored 9front tree.

Research classification: OS/2 Ghostscript DLL loader and Presentation Manager shared-memory display bridge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dpmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.c

This is Russell Lang/Ghostgum's DSC parser implementation for Ghostscript and GSview integration. It parses Adobe Document Structuring Conventions comments in streaming PostScript/EPS input, records document/page metadata and byte offsets, handles several wrapper formats, and repairs common DSC errors after scanning.

Key responsibilities:
- Provides public parser lifecycle and API functions:
  - `dsc_init`, `dsc_init_with_alloc`, `dsc_new`, `dsc_ref`, `dsc_unref`, and `dsc_free`.
  - `dsc_set_length` to bound parsing when the caller knows file length.
  - `dsc_scan_data` to stream chunks of input through the parser.
  - `dsc_fixup` to finalize partial state, repair offsets, and validate consistency.
  - `dsc_set_error_function` and `dsc_set_debug_function`.
  - `dsc_add_page`, `dsc_add_media`, `dsc_set_page_bbox`, and `dsc_find_platefile`.
- Detects document type and wrappers: `%!PS-Adobe`, EPSF, generic PostScript, PDF marker, PJL prefix, DOS EPS binary header, MacBinary EPSF, AppleSingle/AppleDouble, and leading Ctrl-D.
- Tracks DSC sections and byte offsets for comments, preview, defaults, prolog, setup, pages, trailer, and EOF.
- Parses high-value DSC comments: page count/order/orientation, bounding boxes, hires bounding boxes, crop boxes, document media, page media, page labels/ordinals, viewing orientation, document data type, DCS plate files, process colors, and custom colors.
- Skips embedded data safely through `%%BeginData`, `%%BeginBinary`, and recursive `%%BeginDocument`/`%%EndDocument` tracking.
- Supports several DSC 2.1 paper/media comments discontinued in DSC 3.0, including paper sizes, forms, colors, weights, and `%%PaperSize:`.
- Converts DCS 2.0 single-file and multi-file plate information into page-like records for separation extraction.

Parsing architecture:
- `dsc_scan_data` appends caller data into an internal fixed buffer, moves consumed data forward, identifies type on first input, then repeatedly reads complete lines and dispatches them to section-specific scanners.
- `dsc_read_line` handles CR, LF, CRLF, partial lines, Ctrl-Z, long-line warnings, skipped binary bytes, skipped lines, and embedded-document boundaries.
- Section scanners are state-machine functions:
  - `dsc_scan_comments`
  - `dsc_scan_preview`
  - `dsc_scan_defaults`
  - `dsc_scan_prolog`
  - `dsc_scan_setup`
  - `dsc_scan_page`
  - `dsc_scan_trailer`
- `CDSC_PROPAGATE` lets a line that begins a new section be reprocessed by the next section scanner.
- `CDSC_NEEDMORE` is used when a wrapper/header or partial line needs more bytes.
- `CDSC_NOTDSC` tells callers to ignore DSC metadata for the document.

Important data handling:
- Strings are stored in chunked arenas via `dsc_alloc_string`; parsed line snippets are normalized by `dsc_add_line`.
- Pages grow in chunks of `CDSC_PAGE_CHUNK`.
- Media records are deep-copied into parser-owned allocations.
- Known built-in media include Letter, Legal, Ledger, A3/A4/A5, B4/B5, Note, and 11x17.
- `dsc_copy_string` handles DSC/PostScript-style parenthesized strings and escape sequences.
- Numeric helpers parse integers/reals from bounded line fragments.
- Endian helpers decode DOS EPS little-endian and Mac formats big-endian headers.

Error and fixup behavior:
- Error severity defaults are stored in `dsc_severity`; actual user policy is delegated to the optional `dsc_error_fn`.
- Without an error callback, `dsc_error` silently returns `CDSC_RESPONSE_CANCEL`, effectively assuming DSC comments are correct.
- `dsc_fixup` flushes final data, repairs unfinished embedded sections, joins adjacent sections, handles code between setup and first page, extends a last page to the final trailer, validates page counts, checks EPS bounding-box/page rules, assigns default media, and fills missing page labels.
- The parser detects and reports duplicate header/trailer comments, early trailer/EOF, page ordinal errors, incorrect `atend` usage, unmatched Begin/End blocks, long lines, and bad section placement.

DCS/color support:
- `dsc_parse_platefile` parses DCS 2.0 `%%PlateFile:` lines for single-file offset/length separations or multi-file local EPS separations.
- `dsc_parse_dcs1plate` maps `%%CyanPlate:`, `%%MagentaPlate:`, `%%YellowPlate:`, and `%%BlackPlate:` into DCS-like records.
- `dsc_dcs2_fixup` exposes DCS separations as pages and adjusts composite-page boundaries.
- `dsc_parse_process_colours`, `dsc_parse_custom_colours`, `dsc_parse_cmyk_custom_colour`, and `dsc_parse_rgb_custom_colour` maintain linked `CDSCCOLOUR` metadata.

Important relationships:
- Built by `int.mak` as part of `dscparse.dev` with `zdscpars.c`; `usedsc.dev` includes it with PostScript support code.
- `zdscpars.c` uses this C parser as one part of Ghostscript's higher-level DSC parsing interface.
- The parser is independent of direct file I/O: it consumes caller-provided buffers and stores offsets relative to the stream.

Notable implementation details and risks:
- It is robust against many historical malformed DSC/EPS cases, but also preserves permissive behavior through caller decisions or default silent handling.
- It uses fixed-size local buffers (`MAXSTR`, `DSC_LINE_LENGTH`, `CDSC_DATA_LENGTH`) and truncation/long-line handling rather than unbounded allocations.
- `dsc_scan_type` treats PDF only as a marker and does not parse PDF content; public helpers let GSview add PDF-derived pages/media externally.
- The code contains old C idioms and manual memory management, with correctness depending on the `CDSC` structure contract in `dscparse.h`.
- The parser is byte-offset oriented, so callers can later extract page ranges, previews, or DCS plate sections from the original document stream.

Filesystem relevance:
- There is no filesystem implementation or storage-layer behavior.
- The file is relevant to file-format parsing in Ghostscript: it interprets PostScript/EPS document structure and records byte ranges, but all I/O is external to the parser.

Research classification: streaming DSC/EPS metadata parser and repair layer used by Ghostscript's PostScript interpreter integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dscparse.c -->