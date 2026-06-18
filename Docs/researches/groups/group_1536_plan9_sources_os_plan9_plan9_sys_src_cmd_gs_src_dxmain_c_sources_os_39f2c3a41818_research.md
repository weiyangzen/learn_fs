# Group Research: group_1536_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_dxmain_c_sources_os_39f2c3a41818

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/plan9` under the bundled Ghostscript source tree. I read all 29 listed files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers Ghostscript client front ends, generated configuration tables, interpreter file/execution-stack headers, Font API plug-ins, memory alpha-buffer devices, dynamic 8-bit color maps, and several historical display/printer output devices. Most files are Ghostscript application/device code rather than Plan 9 kernel or filesystem code; OS/file relevance is mainly through stdio, file opening, terminal/window ioctls, and Ghostscript IODevice/file-object contracts.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmain.c

GTK+ Ghostscript shared-library front end with display-device callbacks.

Key points:
- Builds a graphical `libgs` client using `gsapi_new_instance`, `gsapi_set_stdio`, `gsapi_set_display_callback`, `gsapi_init_with_args`, and `gsapi_run_string`.
- Registers stdin/stdout/stderr callbacks; stdin is integrated with the GTK/GDK event loop via `gdk_input_add`.
- Implements a `display_callback` for the Ghostscript display device: open, preclose, close, presize, size, sync, page, update, and separation callbacks.
- Maintains a linked list of `IMAGE` objects keyed by Ghostscript handle/device.
- Creates GTK windows, scrolled drawing areas, and optional CMYK/DeviceN separation controls.
- Converts Ghostscript raster formats into GdkRgb-friendly buffers for native 8-bit, 16-bit RGB/BGR, RGB with alpha padding, CMYK, and DeviceN separations.
- Adds a default `-dDisplayFormat=` argument requesting big-endian 8-bit RGB display output.
- Maps Ghostscript exit codes to process exit status, treating `e_Quit` as normal.

Dependencies and interactions:
- Depends on GTK/GDK, Ghostscript public API headers `iapi.h`, `ierrors.h`, and display-device constants from `gdevdsp.h`.
- Receives raster memory owned by Ghostscript; it allocates only conversion buffers and UI structures.
- DeviceN separation names and CMYK component values come through `display_separation`.

OS/filesystem relevance:
- Uses POSIX `read`, `fileno`, stdio writes, and dynamic GUI event handling.
- No Plan 9 filesystem/VFS behavior; this is a GUI client embedded in the Plan 9 Ghostscript tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmainc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmainc.c

Console-only Ghostscript shared-library front end.

Key points:
- Minimal `libgs` client for command-line execution without the display callback.
- Provides stdio callbacks using POSIX `read` for stdin and `fwrite`/`fflush` for stdout/stderr.
- Runs Ghostscript startup by invoking `systemdict /start get exec`.
- Uses the same `gsapi_*` lifecycle and exit-code mapping pattern as `dxmain.c`.

Dependencies and interactions:
- Includes `iapi.h` and `ierrors.h`.
- Does not create or configure a display device.

OS/filesystem relevance:
- Direct use of process stdio only.
- No filesystem-specific logic beyond Ghostscript’s arguments being handled by the library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmainc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/echogs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/echogs.c

Portable Ghostscript build utility similar to `echo`.

Key points:
- Exists to avoid shell and utility incompatibilities in Ghostscript builds.
- Supports output to stdout, overwrite/append files, optional binary mode, extension suffixing, hex output, newline suppression, and literal/quoted/space insertion modes.
- Can insert the output file name, base name, date/time, uppercase strings, literal strings, hex-decoded bytes, stdin lines, interpreted file lines, or raw file contents.
- `hputc`/`hputs` implement hex-encoded output mode.
- Returns Ghostscript-style build utility exit constants `exit_OK` and `exit_FAILED`.

Dependencies and interactions:
- Uses stdio, ctype, string, time, and `stdpre.h`.
- Used by makefiles/build scripts to generate small files predictably.

OS/filesystem relevance:
- Opens output and input files using `fopen`, copies raw file data with `fread`, and reads stdin with `fgets`.
- Relevant as a build-time file generation/copy helper, not as runtime filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/echogs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/errno_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/errno_.h

Portable wrapper for `errno.h`.

Key points:
- Includes Ghostscript `std.h` before system headers.
- Includes `<errno.h>`.
- Declares `extern int errno` if `errno` is not already a macro.

Dependencies and interactions:
- Provides a compatibility layer for old or nonconforming C libraries where `<errno.h>` defines error numbers but not the `errno` object.

OS/filesystem relevance:
- Supports portable reporting of OS/file errors across Ghostscript code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/errno_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/errors.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/errors.h

Backward-compatibility wrapper for Ghostscript API errors.

Key points:
- Explains that old client API error definitions moved to `ierrors.h`.
- Includes `ierrors.h` to preserve compatibility with older code including `errors.h`.

Dependencies and interactions:
- No definitions of its own beyond the include guard and compatibility include.

OS/filesystem relevance:
- None directly; it keeps error-code includes stable for client code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/estack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/estack.h

Interpreter execution-stack helper header.

Key points:
- Defines convenient access macros for the current interpreter context’s execution stack.
- Exposes cached current-file helpers: `esfile`, `esfile_clear_cache`, `esfile_set_cache`, `esfile_check_cache`.
- Documents Ghostscript’s execution stack model for procedures, control operators, and continuations.
- Defines e-stack mark and continuation operator macros:
  - `make_mark_estack`, `push_mark_estack`
  - `r_is_estack_mark`
  - `make_op_estack`, `push_op_estack`
- Provides stack capacity/underflow macros `check_estack` and `check_esp`.
- Defines mark types `es_other`, `es_show`, `es_for`, and `es_stopped`.
- Declares `pop_estack`.

Dependencies and interactions:
- Includes `iestack.h` and `icstate.h`.
- Used by interpreter operators that call out to PostScript procedures or need continuation state.
- Coupled to current-file lookup and e-stack block splitting invariants.

OS/filesystem relevance:
- Relevant to file execution indirectly because executable file refs on the execution stack feed `currentfile` behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/estack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapi_ft.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapi_ft.c

Ghostscript Font API plug-in backed by FreeType.

Key points:
- Implements an `FAPI_server` named `FreeType`.
- Lazily initializes an `FT_Library`.
- Supports fonts loaded from disk paths via `FT_New_Face` and embedded fonts loaded from serialized in-memory Type 1, Type 2, or TrueType data.
- Uses FreeType’s incremental interface to ask Ghostscript callbacks for glyph data and replacement metrics.
- Converts FreeType errors to Ghostscript error codes.
- Handles font scaling by decomposing the Ghostscript matrix into size and rotation/shear components for FreeType hinting and transforms.
- Provides FAPI callbacks for:
  - scaled font acquisition
  - decoding ID (`Unicode`)
  - font bounding box
  - glyph-name lookup
  - metric replacement decisions
  - character width
  - raster metrics/raster retrieval
  - outline metrics/outline retrieval
  - char data and typeface release
- Converts FreeType quadratic outlines to cubic curves for Ghostscript path callbacks.
- Plugin lifecycle is exposed through `gs_fapi_ft_instantiate` and `gs_freetype_destroy`.

Dependencies and interactions:
- Includes Ghostscript FAPI headers and Type 1/Type 2 serialization helpers.
- Includes FreeType headers for face loading, incremental fonts, glyphs, outlines, and transforms.
- Stores `FF_face` in `FAPI_font.server_font_data`.

OS/filesystem relevance:
- Uses FreeType disk font loading when `font_file_path` is present.
- Otherwise primarily in-memory serialization and callback-driven glyph retrieval.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapi_ft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapiufst.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapiufst.c

Ghostscript Font API plug-in backed by Agfa UFST.

Key points:
- Implements an `FAPI_server` named `AgfaUFST`.
- Lazily initializes UFST with `CGIFinit`, `CGIFconfig`, and `CGIFenter`.
- Tracks server state in `fapi_ufst_server`, including UFST `IF_STATE`, current `FONTCONTEXT`, cached glyph/raster data, client memory callbacks, FCO font handles, transform state, and metric replacement state.
- Detects disk font type by reading leading bytes from the font file: FCO, PostScript Type 1, or TrueType.
- Builds UFST-compatible font data for embedded Type 1 and TrueType fonts, including PCL/PCLEO/PSEO headers and serialized subr/glyph data.
- Provides callback bridges `gs_PCLchId2ptr` and `gs_PCLglyphID2Ptr` so UFST can request glyph data from Ghostscript.
- Chooses decoding IDs from an `xlatmap`, including TrueType cmap platform/specific IDs.
- Handles FCO file open/reference counting through `CGIFfco_Open` and `CGIFfco_Close`.
- Provides FAPI callbacks for scaled fonts, decoding IDs, bounding boxes, proportional feature detection, glyph-name support, metric replacement, width metrics, raster/outline metrics, raster/outline retrieval, char-data release, and typeface release.
- Cleans stale UFST char data defensively because Ghostscript cannot always signal interrupted raster/outline sequences.

Dependencies and interactions:
- Uses UFST headers and APIs plus Ghostscript FAPI/plugin headers.
- Stores `ufst_common_font_data` in `FAPI_font.server_font_data`.
- Uses Ghostscript client memory alloc/free functions for font data, glyph caches, and FCO tracking.

OS/filesystem relevance:
- Opens disk fonts with `fopen(..., "rb")`; the comment notes `gp_fopen` is not better because UFST itself uses `fopen`.
- Disk font paths, FCO handle tracking, and font type probing are the main file-facing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapiufst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fcntl_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fcntl_.h

Portable wrapper for `fcntl.h` open flags.

Key points:
- Includes Ghostscript `std.h` before `<fcntl.h>`.
- Maps Microsoft-style `_O_*` constants to standard `O_*` names when missing:
  - `O_APPEND`, `O_BINARY`, `O_CREAT`, `O_EXCL`
  - `O_RDONLY`, `O_RDWR`, `O_TRUNC`, `O_WRONLY`

Dependencies and interactions:
- Used by code that wants portable `open` mode flags.

OS/filesystem relevance:
- Directly supports portable low-level file opening.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/fcntl_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/files.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/files.h

Interpreter support declarations for PostScript file objects.

Key points:
- Defines `fptr` and `make_file` for refs that wrap Ghostscript streams.
- Declares lazy stdio accessors `zget_stdin`, `zget_stdout`, `zget_stderr`, and `zis_stdin`.
- Defines `ref_stdin`, `ref_stdout`, and `ref_stderr` access macros.
- Documents the read/write ID scheme used to detect closed or reused stream objects.
- Provides validation macros for file refs:
  - `check_file`
  - `check_read_file`
  - `check_read_known_file`
  - `check_write_file`
  - `check_write_known_file`
- Declares mode switching helpers `file_switch_to_read` and `file_switch_to_write`.
- Declares library/file open helpers, stream filter opening, stream-backed file ref creation, close helpers, stream allocation, `zreadline_from`, line editing, and stdio-needed pseudo-operators.

Dependencies and interactions:
- Used by interpreter file, filter, IODevice, and main argument modules.
- Depends on Ghostscript `stream`, `ref`, VM memory, IODevice, and file path abstractions.

OS/filesystem relevance:
- This is the central interpreter contract between PostScript file objects and Ghostscript streams/IODevice-backed file access.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/files.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.c

Builds Ghostscript configuration/resource tables from `gconf.h`/`gconfig.h`.

Key points:
- Includes generated configuration entries multiple times with different macro definitions.
- Declares configured devices, image types/classes, compositor types, halftones, init procs, and IODevices.
- Builds:
  - compositor list
  - device prototype list
  - device halftone list
  - image class table and count
  - image type table and count
  - initialization procedure table
  - IODevice table and count
- Ensures `%os%` (`gs_iodev_os`) is first in the IODevice table.
- Implements `gs_find_compositor`.
- Implements `gs_lib_device_list`.

Dependencies and interactions:
- Depends on `gconf.h`, which wraps generated `gconfig.h`.
- Exports tables consumed by Ghostscript core initialization and device lookup.

OS/filesystem relevance:
- IODevice registration includes file-related devices such as `%os%`, stdin/stdout/stderr, pipe, null, static, etc., depending on generated config.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.h

Wrapper for the generated Ghostscript configuration header.

Key points:
- Intentionally has no double-inclusion guard because it is included repeatedly with different macro definitions.
- Includes `gconfig.h` by default.
- If `GCONFIG_H` is defined, includes that macro-specified header instead.

Dependencies and interactions:
- Used by `gconf.c`/`gconfig.c` to generate tables from macro entries.

OS/filesystem relevance:
- Indirect; configuration entries include IODevices and initialization files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.c

Duplicate configuration table builder matching `gconf.c`.

Key points:
- Contents are effectively the same as `gconf.c`.
- Repeatedly includes `gconf.h` under different macro definitions to declare and populate Ghostscript resource tables.
- Exports configured compositor, device, halftone, image class/type, initialization, and IODevice tables.
- Implements `gs_find_compositor` and `gs_lib_device_list`.

Dependencies and interactions:
- Uses generated `gconfig.h` through `gconf.h`.
- Provides global configuration data for Ghostscript startup and device lookup.

OS/filesystem relevance:
- Includes the IODevice table, with `%os%` first as the default file device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.h

Generated Ghostscript feature/configuration manifest.

Key points:
- Generated by `genconf.c`.
- Contains macro-guarded entries for configured components:
  - compositor types
  - output devices, including Plan 9, Inferno, printer, bitmap, JPEG, PDF/PS writers, TIFF, and nullpage devices
  - PostScript operator definition sets
  - PostScript initialization files
  - IODevices
  - emulators
  - function types
  - image types and image classes
  - initialization procedures
- Uses `#ifdef <macro>_` blocks so the same file can instantiate declarations, tables, resource lists, and init sequences.

Dependencies and interactions:
- Consumed by `gconf.h` and table-generation code.
- Encodes the compiled-in Ghostscript feature set for this Plan 9 build.

OS/filesystem relevance:
- Lists IODevices including stdin/stdout/stderr, lineedit/statementedit, null/calendar/static, and pipe.
- Lists initialization PostScript files that will be searched under Ghostscript library paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig_.h

Generated platform capability header.

Key points:
- Generated by `unix-aux.mak`.
- Defines availability of `dirent.h`, `sys/time.h`, and `sys/times.h`.

Dependencies and interactions:
- Used by Ghostscript portability code to conditionally compile Unix-like system support.

OS/filesystem relevance:
- `HAVE_DIRENT_H` affects directory traversal support in OS/file code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigd.h

Generated Ghostscript default path/version header for Plan 9.

Key points:
- Defines `GS_LIB_DEFAULT` as `/sys/lib/ghostscript:/sys/lib/ghostscript/font:/sys/lib/postscript/font`.
- Defines empty `GS_CACHE_DIR`.
- Enables `SEARCH_HERE_FIRST`.
- Defines documentation directory `/sys/src/cmd/gs/doc`.
- Defines init file `gs_init.ps`.
- Defines revision `853` and revision date `20051020`.

Dependencies and interactions:
- Used by Ghostscript startup path and version logic.

OS/filesystem relevance:
- Directly defines default filesystem search paths for Ghostscript libraries and fonts on Plan 9.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigv.h

Generated Ghostscript build option header.

Key points:
- Defines assembly and FPU use: `USE_ASM (-0)`, `USE_FPU (1-0)`.
- Disables extended names with `EXTEND_NAMES 0`.
- Defines `SYSTEM_CONSTANTS_ARE_WRITABLE 0`.

Dependencies and interactions:
- Used by Ghostscript core configuration and portability logic.

OS/filesystem relevance:
- None directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfxx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfxx.h

Generated configuration manifest matching `gconfig.h`.

Key points:
- Contains the same generated component entries as `gconfig.h`.
- Macro-guarded entries cover compositor types, devices, operator sets, initialization PostScript files, IODevices, emulators, function types, image types, init procedures, and image classes.
- Used as an alternate generated config include when selected by build macros.

Dependencies and interactions:
- Compatible with `gconf.h`’s `GCONFIG_H` override mechanism.

OS/filesystem relevance:
- Same as `gconfig.h`: includes IODevices and init/library file names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfxx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdebug.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdebug.h

Ghostscript debugging/tracing macro header.

Key points:
- Declares global debug flag array `gs_debug[128]` and `gs_debug_c`.
- Uppercase debug flags also enable corresponding lowercase flags.
- Defines `gs_log_errors` as `gs_debug['#']`.
- Declares `gs_debug_out` and redirects `dstderr`/`estderr` to it when compiled with `DEBUG`.
- Provides `if_debug0` through `if_debug12` macros that emit debug output only when `DEBUG` is compiled in and the flag is set.
- When `DEBUG` is absent, debug macros compile to `DO_NOTHING`.
- Declares debug dump helpers for bytes, bitmaps, strings, and hex strings.

Dependencies and interactions:
- Used throughout Ghostscript for selective runtime tracing.

OS/filesystem relevance:
- Debug output destination may be a file stream, but this header has no file-opening logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3852.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3852.c

IBM 3852 JetPrinter color inkjet Ghostscript driver.

Key points:
- Defines `gs_jetp3852_device` at 84x84 DPI with 3-bit PCL color mapping.
- Uses `prn_color_procs` with PCL 3-bit RGB mapping helpers.
- `jetp3852_print_page` initializes the printer, copies Ghostscript scan lines, skips blank lines, transposes raster bytes into color planes, complements bytes, writes printer escape sequences/data, and formfeeds at the end.
- Assumes RGB plane ordering and works around printer-specific scanline/plane layout.

Dependencies and interactions:
- Depends on `gdevprn.h` and `gdevpcl.h`.
- Uses Ghostscript printer buffer helpers such as `gdev_prn_copy_scan_lines`.

OS/filesystem relevance:
- Writes printer data to a `FILE *` stream supplied by Ghostscript’s printer device framework.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3852.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3b1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3b1.c

AT&T 3B1/7300/UnixPC console display device.

Key points:
- Defines a display device `gs_att3b1_device` that renders a full page into an in-memory 1-bit screen buffer.
- Opens `/dev/tty`, validates it as a console window with `WIOCGETD`, and allocates a page-sized bitmap buffer.
- Implements device procs for open, close, fill rectangle, copy mono, and output page.
- `att3b1_fill_rectangle` and `att3b1_copy_mono` manipulate the packed bitmap buffer directly using masks, bit reversal, rotation, and logical operations.
- `att3b1_do_output_page` saves/restores window state, changes terminal mode, copies the rendered page into the visible screen window with `WIOCRASTOP`, and lets the user scroll/pan/invert/help/exit via keyboard controls.
- Handles arrow/help/cancel/next escape sequences in `getKeyboard`.
- Optional `ATT3B1_PERF` environment variables can disable output/fill/copy sections for profiling.

Dependencies and interactions:
- Includes Ghostscript device headers plus legacy UnixPC headers `<sys/window.h>` and `<sys/termio.h>`.
- Uses low-level `open`, `close`, `read`, `write`, and `ioctl`.

OS/filesystem relevance:
- Strong OS-device interaction through `/dev/tty`, terminal ioctls, and window raster operations.
- Not portable Plan 9 code; this is for AT&T UnixPC console hardware.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3b1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4081.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4081.c

Ricoh 4081 laser printer driver.

Key points:
- Defines `gs_r4081_device`, 300x300 DPI, letter-sized with margins.
- `r4081_print_page` allocates an output scanline buffer, trims leading and trailing blank scanlines, emits Ricoh initialization/positioning commands, writes raw raster lines, ejects the page, and reinitializes the printer.
- Uses simple blank-line detection by comparing each scanline to repeated zero bytes.

Dependencies and interactions:
- Depends on `gdevprn.h`.
- Uses Ghostscript printer memory allocation and scanline copy helpers.

OS/filesystem relevance:
- Streams printer command/raster bytes to `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4081.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4693.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4693.c

Tektronix 4693d color plotter/printer driver.

Key points:
- Defines 8-bit, 16-bit, and 24-bit devices: `t4693d2`, `t4693d4`, and `t4693d8`.
- Provides RGB color mapping and reverse mapping based on device depth.
- Builds a Tektronix print-request header with encoded width, height, depth, mode fields, and checksum.
- Writes per-pixel raster data line by line, with endian/depth adjustments for 8-bit and 16-bit modes.
- Emits EOL and EOT markers and reports I/O/range errors on failed writes or bad depth.

Dependencies and interactions:
- Depends on `gdevprn.h`.
- Uses Ghostscript scanline copy and memory allocation/free helpers.

OS/filesystem relevance:
- Writes binary protocol data to a `FILE *` printer stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev4693.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8510.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8510.c

C.Itoh M8510 printer driver.

Key points:
- Defines `gs_m8510_device` at 160x144 DPI.
- Allocates two 8-line input buffers and one transposed output buffer.
- Initializes printer for NLQ/proportional graphics mode.
- Processes raster data in two interleaved passes, transposes 8x8 blocks, trims trailing zero blocks, writes graphics commands/data, and resets the printer.
- `m8510_output_run` emits graphics runs and controls pass-specific newlines.

Dependencies and interactions:
- Depends on `gdevprn.h`.
- Uses `gdev_prn_copy_scan_lines` and `gdev_prn_transpose_8x8`.

OS/filesystem relevance:
- Outputs printer control/data bytes to `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8510.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.c

Dynamic color-map implementation for 8-bit display devices.

Key points:
- `gx_8bit_map_init` initializes a fixed-size open-addressing hash table.
- `gx_8bit_map_rgb_color` hashes a reduced 5-bit-per-channel RGB key and returns an existing color index or a negative insertion slot.
- `gx_8bit_add_rgb_color` inserts a new RGB key when space remains and returns its assigned dynamic index.
- Uses a prime-ish map size and spreader to reduce clustering.

Dependencies and interactions:
- Implements declarations from `gdev8bcm.h`.
- Shared by display drivers that need fast lookup for dynamic 8-bit colormaps.

OS/filesystem relevance:
- None; purely in-memory color lookup support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.h

Header for dynamic 8-bit color-map support.

Key points:
- Documents use by MS-DOS, MS Windows, and X Windows drivers.
- Defines map size `323`, spreader `123`, no-RGB sentinel `0xffff`, and `gx_8bit_rgb_key`.
- Defines `gx_8bit_map_entry` and `gx_8bit_color_map`.
- Declares init, lookup, and add functions.
- Defines `gx_8bit_map_is_full`.

Dependencies and interactions:
- Requires `gxdevice.h` for `gx_color_value`.
- Paired with `gdev8bcm.c`.

OS/filesystem relevance:
- None; display color-cache data structures only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev8bcm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevabuf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevabuf.c

Alpha and alpha-buffer memory devices.

Key points:
- `gs_make_mem_alpha_device` creates a 2-bit or 4-bit alpha-capable memory device by patching a standard memory device descriptor.
- Reimplements color mapping so nonzero target colors map to maximum alpha or alpha-derived values.
- Implements alpha copying through fill/copy-color behavior.
- `gs_make_mem_abuf_device` creates an oversampled alpha-buffer device that accumulates high-resolution bits and flushes compressed alpha rows to a lower-resolution target.
- `gs_device_is_abuf` identifies the alpha-buffer device by device-name identity.
- Maintains a sliding Y-window over a limited-height band buffer to avoid copying while processing top-to-bottom bands.
- `abuf_flush_block` computes a bounding box, compresses scaled bits into alpha data, and forwards to the target device’s `copy_alpha`.
- `mem_abuf_copy_mono` and `mem_abuf_fill_rectangle` map incoming operations into the sliding buffer.
- `mem_abuf_close` flushes before closing.
- `mem_abuf_get_clipping_box` scales the target clipping box up by the supersampling scale.

Dependencies and interactions:
- Uses Ghostscript memory device internals from `gxdevmem.h` and `gdevmem.h`.
- Calls bit helpers such as `bits_bounding_box` and `bits_compress_scaled`.
- Intended for antialiased text/graphics and masked image cases with constrained band-order assumptions.

OS/filesystem relevance:
- None; in-memory rendering device support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevabuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevadmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevadmp.c

Apple DMP and ImageWriter printer drivers.

Key points:
- Defines four devices:
  - `appledmp` at 120x72 DPI
  - `iwlo` at 160x72 DPI
  - `iwhi` at 160x144 DPI
  - `iwlq` at 320x216 DPI
- `dmp_print_page` selects device type from resolution.
- Allocates input, output, and printer data buffers.
- Initializes printer modes differently for DMP, ImageWriter low/high, and ImageWriter LQ.
- Processes raster data in 8-, 16-, or 24-line groups depending on device type.
- Reverses scanline order for DMP bit ordering, transposes 8x8 blocks, trims blank leading/trailing printer data, and emits device-specific graphics/skip commands.
- Works around ImageWriter formfeed behavior by backing up before formfeed for non-DMP modes.
- Resets printer state and frees buffers.

Dependencies and interactions:
- Depends on `gdevprn.h`.
- Uses Ghostscript printer scanline copy, transpose, and memory allocation helpers.

OS/filesystem relevance:
- Writes printer escape sequences and raster data to `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevadmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevatx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevatx.c

Practical Automation ATX-23, ATX-24, and ATX-38 printer driver.

Key points:
- Defines `atx23`, `atx24`, and `atx38` devices with model-specific page widths, DPI, and margins.
- Encodes ATX printer commands for page length, vertical tab, compressed/uncompressed data, and end page.
- `fput_atx_command` writes a command plus little-endian 16-bit argument.
- `atx_compress` implements pair-oriented run-length compression for repeated byte pairs and uncompressed segments.
- `atx_print_page` computes legal page length, enforces minimum 3-inch page length, allocates scanline/compression buffers, skips blank lines, truncates to maximum printable width, writes compressed or raw scanline data, and ends the page.
- Model wrappers pass maximum pixel widths for the three printers.

Dependencies and interactions:
- Includes `math_.h` and `gdevprn.h`.
- Uses `gdev_prn_get_bits`, Ghostscript allocation helpers, and printer stream writes.

OS/filesystem relevance:
- Streams printer command/raster data through `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevatx.c -->