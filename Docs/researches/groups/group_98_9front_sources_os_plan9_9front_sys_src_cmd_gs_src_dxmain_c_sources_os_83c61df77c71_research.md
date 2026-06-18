# Group Research: group_98_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_dxmain_c_sources_os_83c61df77c71

Scope: subset A from `Docs/research_subset_a.md`, covering the listed Ghostscript sources under `sources/os/plan9/9front/sys/src/cmd/gs/src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmain.c

## Scope

GTK-based Ghostscript shared-library frontend that installs stdio callbacks, optionally creates a GUI display callback, injects `-dDisplayFormat=...`, initializes the Ghostscript API, runs `systemdict /start get exec`, exits, and maps Ghostscript return codes to process exit status.

## Key Behavior

- `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr` bridge Ghostscript I/O to Unix stdio while pumping GTK events.
- Maintains an `IMAGE` list keyed by Ghostscript display `handle` and `device`.
- Implements the `display_callback` table for open, close, resize, sync, page, update, and separation metadata.
- Creates GTK windows with scrollable drawing areas and optional CMYK/separation controls.
- Converts display-device buffers into GDK-compatible RGB/gray/indexed output for native 8-bit, native 16-bit, gray, RGB, CMYK, and separation formats.

## Dependencies

Uses GTK/GDK, Unix `read`, Ghostscript client API `iapi.h`, error constants from `ierrors.h`, and display-device format definitions from `gdevdsp.h`.

## Risks And Invariants

- Display buffers are owned by Ghostscript; `display_size` stores `pimage` and must not free it.
- `rgbbuf` and `cmap` are per-image conversion resources and must be freed on resize/preclose.
- Separation handling assumes at most `IMAGE_DEVICEN_MAX` components.
- There is a likely off-by-one guard issue: `display_separation` rejects `comp_num > IMAGE_DEVICEN_MAX`, but valid indices are `< IMAGE_DEVICEN_MAX`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmainc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmainc.c

## Scope

Console-only Ghostscript shared-library frontend. It runs Ghostscript through `gsapi_*` without a display callback.

## Key Behavior

- Provides stdin/stdout/stderr callbacks using `read`, `fwrite`, and `fflush`.
- Calls `gsapi_new_instance`, `gsapi_set_stdio`, `gsapi_init_with_args`, `gsapi_run_string`, `gsapi_exit`, and `gsapi_delete_instance`.
- Runs the same startup PostScript string as `dxmain.c`: `systemdict /start get exec`.
- Treats `e_Quit` as normal termination and maps `e_Fatal` to process exit code 1, other errors to 255.

## Dependencies

Uses Unix stdio/read APIs and Ghostscript headers `iapi.h` and `ierrors.h`.

## Risks And Invariants

- No GUI or display-device support is installed; graphical output requires another frontend.
- `read` return values are passed directly to Ghostscript, so stdin errors propagate as negative callback returns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/dxmainc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/echogs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/echogs.c

## Scope

Portable build utility similar to `echo`, used to work around shell and utility incompatibilities when generating Ghostscript build artifacts.

## Key Behavior

- Supports output to stdout, write, append, binary file modes, optional filename extension, hex output, and newline suppression.
- Parses command switches for literal strings, spaces, uppercase conversion, dates, output filename/base-name insertion, reading arguments from stdin/files, raw file copying, and treating literals as hex.
- Uses `hputc` and `hputs` for hex-encoded output mode.
- Interactive mode reads one line at a time from stdin or a named file and treats each line as an argument.

## Dependencies

Uses `stdpre.h`, stdio/stdlib, ctype/string/time APIs, and Ghostscript-style `exit_OK` / `exit_FAILED` constants.

## Risks And Invariants

- Fixed-size `fname[100]` and `line[1000]` buffers require generated inputs to stay within expected build-system limits.
- Hex parsing emits a byte every two hex digits but does not explicitly reject odd-length hex strings.
- File option parsing mutates the argument vector for the `-w-` / `-a-` form.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/echogs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/errno_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/errno_.h

## Scope

Portable wrapper around system `errno.h`.

## Key Behavior

- Includes Ghostscript `std.h` before system headers.
- Includes `<errno.h>`.
- Declares `extern int errno` if `errno` was not provided as a macro.

## Dependencies

Depends on Ghostscript portability header `std.h` and the platform C library `errno.h`.

## Risks And Invariants

- Exists for old environments where `<errno.h>` defines error constants but does not declare `errno`.
- The `extern int errno` fallback must not conflict with platforms where `errno` is thread-local macro state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/errno_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/errors.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/errors.h

## Scope

Backward-compatibility header for Ghostscript client API error codes.

## Key Behavior

- Documents that client API error codes were moved to `ierrors.h`.
- Includes `ierrors.h` under the old `errors.h` name.

## Dependencies

Depends only on `ierrors.h`.

## Risks And Invariants

- Kept to avoid breaking older clients that include `errors.h`.
- New code should include `ierrors.h` directly to avoid namespace ambiguity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/estack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/estack.h

## Scope

Execution-stack definitions for the Ghostscript PostScript interpreter.

## Key Behavior

- Defines cached current-file access macros and operator-visible execution stack pointers.
- Documents e-stack contents: executable procedure tails, control-flow arguments, looping state, and continuation frames.
- Provides macros for e-stack marks and pseudo-operator continuations: `make_mark_estack`, `push_mark_estack`, `make_op_estack`, and `push_op_estack`.
- Provides stack capacity/underflow checks with `check_estack` and `check_esp`.
- Declares `pop_estack`, which pops stack entries and runs cleanup procedures as needed.

## Dependencies

Includes `iestack.h` and `icstate.h`, and depends on interpreter context `i_ctx_p`, refs, ref stacks, and Ghostscript error constants.

## Risks And Invariants

- Continuation frames must keep marks and associated state together across linked-list stack blocks.
- E-stack marks are executable null refs; cleanup behavior depends on their `opproc`.
- Operators returning `o_push_estack` / `o_pop_estack` rely on exact frame layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/estack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fapi_ft.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fapi_ft.c

## Scope

Ghostscript FAPI plugin that renders fonts through FreeType.

## Key Behavior

- Defines `FF_server`, `FF_face`, and FreeType incremental-interface state for Ghostscript-supplied glyph data.
- Opens fonts from filesystem paths or from Ghostscript-serialized in-memory Type 1, Type 2, and TrueType data.
- Uses FreeType incremental callbacks to request glyph data and optionally override glyph metrics.
- Decomposes Ghostscript transforms into FreeType size and transform components for hinting and rendering.
- Provides FAPI callbacks for decoding ID, font bbox, glyph-name lookup, metrics replacement, character width, raster generation, outline generation, char-data release, and typeface release.
- Converts FreeType outlines into Ghostscript `FAPI_path` operations, including quadratic-to-cubic conversion.

## Dependencies

Uses Ghostscript FAPI/plugin headers, Type 1/Type 2 serialization helpers, and FreeType headers including incremental, glyph, outline, and trigonometry APIs.

## Risks And Invariants

- `char_data` may be cleared by Ghostscript glyph fetching hacks and is saved/restored around repeated loads.
- Incremental glyph buffers have one reusable buffer plus heap allocation for nested composite glyph requests.
- Raster and outline glyphs are stored on the server between paired metrics/data calls and must be released.
- FreeType errors are mapped coarsely to Ghostscript errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fapi_ft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fapiufst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fapiufst.c

## Scope

Ghostscript FAPI plugin for Agfa UFST font rendering.

## Key Behavior

- Initializes UFST through `CGIFinit`, `CGIFconfig`, and `CGIFenter`.
- Builds UFST font data for disk fonts, FCO fonts, embedded Type 1 fonts, and embedded TrueType fonts.
- Implements glyph callback paths for PCLEO/PCL Type 1 and TrueType glyph retrieval from Ghostscript FAPI.
- Chooses decoding IDs from translation maps for PostScript and TrueType fonts.
- Sets UFST `FONTCONTEXT` transforms, resolution, subpixel settings, symbol set, cmap platform/specific IDs, and vertical-writing flags.
- Provides FAPI operations for scaled-font preparation, bbox retrieval, proportional-font detection, name lookup capability, metrics replacement capability, width lookup, raster generation, outline generation, and resource release.

## Dependencies

Uses Ghostscript FAPI/plugin APIs plus UFST headers and functions such as `CGIFfont`, `CGIFchar_with_design_bbox`, `CGIFwidth`, `CGIFtt_query`, `CGIFtt_cmap_query`, `CGIFfco_Open`, and `gx_set_UFST_Callbacks`.

## Risks And Invariants

- The plugin assumes only one active UFST font context at a time because UFST caches `FONTCONTEXT` internally.
- Character raster/outline data is retained across paired calls and defensively released at later entry points to avoid leaks after Ghostscript-side errors.
- Many generated PCLEO header fields are marked approximate or “wrong” but apparently unused by UFST.
- Metrics replacement is limited to non-disk TrueType with skipped metrics and exact replacement semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fapiufst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fcntl_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fcntl_.h

## Scope

Portable wrapper for `open` flag constants.

## Key Behavior

- Includes Ghostscript `std.h` before `<fcntl.h>`.
- Maps Microsoft `_O_*` constants to standard `O_*` names when missing.

## Dependencies

Depends on platform `<fcntl.h>` and Ghostscript portability conventions.

## Risks And Invariants

- Exists because some Microsoft C environments omit standard `O_*` names.
- Only aliases a fixed set of flags: append, binary, create, exclusive, read-only, read-write, truncate, and write-only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/fcntl_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/files.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/files.h

## Scope

Interpreter support declarations and macros for PostScript file objects.

## Key Behavior

- Defines file refs as refs whose `value.pfile` points to a Ghostscript `stream`.
- Validates file refs by comparing ref size against stream `read_id` / `write_id`.
- Provides macros for checking read/write file access and switching bidirectional streams between read and write modes.
- Declares accessors for stdin/stdout/stderr refs and lazy stream retrieval.
- Declares file opening, closing, stream allocation, filter opening, string reading, line reading, and line-edit helpers.

## Dependencies

Requires `stream.h`-style stream definitions, interpreter context refs, Ghostscript memory types, IODevice types, and zfile/zfileio/zfilter/ziodev implementations.

## Risks And Invariants

- File validity depends on stream generation IDs; reusing streams after close must update IDs.
- Bidirectional streams may switch mode when a read/write ID check fails.
- `file_is_invalid` is required instead of negating `file_is_valid` due to historical compiler behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/files.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.c

## Scope

Build-configuration table generator source for Ghostscript resources.

## Key Behavior

- Includes generated `gconf.h` repeatedly with different macro definitions.
- Declares configured compositors, devices, halftones, image classes, image types, init procedures, and IODevices.
- Builds null-terminated tables: compositor list, device list, halftone list, image class table, image type table, init table, and IODevice table.
- Forces `%os%` (`gs_iodev_os`) to be first in the IODevice table.
- Implements `gs_find_compositor` and `gs_lib_device_list`.

## Dependencies

Uses generated `gconf.h` / `gconfig.h` and Ghostscript graphics, device, halftone, image, IODevice, parameter, and compositor headers.

## Risks And Invariants

- The macro names in generated configuration headers are part of the build ABI.
- Table count constants intentionally use `unsigned` to match `gscdefs.h`.
- `%os%` must remain first for default file-device resolution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.h

## Scope

Wrapper for including the generated Ghostscript configuration header.

## Key Behavior

- Includes `gconfig.h` by default.
- If `GCONFIG_H` is defined, includes the header named by that macro.
- Intentionally has no include guard because it is included repeatedly with different macro definitions.

## Dependencies

Depends on either `gconfig.h` or a build-provided alternate config header.

## Risks And Invariants

- Adding double-inclusion protection would break `gconf.c` / generated-table macro expansion.
- Supports preprocessors that do not implement non-quoted include arguments unless `GCONFIG_H` is used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.c

## Scope

Configuration table builder identical in content and behavior to `gconf.c`.

## Key Behavior

- Re-includes `gconf.h` under multiple macro definitions to declare configured resources and construct runtime tables.
- Builds compositor, device, halftone, image class, image type, init, and IODevice tables.
- Exposes `gs_find_compositor` and `gs_lib_device_list`.

## Dependencies

Same as `gconf.c`: generated config macros plus Ghostscript graphics/device/resource headers.

## Risks And Invariants

- Must remain synchronized with build-generated resource declarations.
- Runtime resource discovery depends on null-terminated tables and correct generated macro ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.h

## Scope

Generated Ghostscript configuration inventory.

## Key Behavior

- Lists configured compositors, devices, operators, PostScript initialization files, IODevices, emulators, function types, image types, image classes, and init procedures behind conditional macros.
- Includes Plan 9 relevant devices such as `gs_plan9_device` and `gs_plan9bm_device`, along with printer, image, PDF/PostScript, and nullpage devices.
- Enumerates interpreter operator sets for PostScript levels, PDF support, filters, font formats, color spaces, DPS, FAPI, and image handling.
- Lists init/runtime PostScript resources such as `gs_init.ps`-related support files, PDF files, CMap/CID files, Type 1/42 files, and FAPI/PDF writer support.

## Dependencies

Consumed by `gconf.h` and table-building sources through macro redefinition.

## Risks And Invariants

- Generated file; manual edits would likely be overwritten.
- Each item only emits when the including source defines its corresponding macro.
- Length arguments in `psfile_` / `emulator_` entries must match literal lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig_.h

## Scope

Generated platform feature header fragment from `unix-aux.mak`.

## Key Behavior

- Defines `HAVE_DIRENT_H`.
- Defines `HAVE_SYS_TIME_H`.
- Defines `HAVE_SYS_TIMES_H`.

## Dependencies

Included by generated or platform configuration logic.

## Risks And Invariants

- Represents detected platform headers for this build target.
- Should be regenerated by the build system rather than edited manually.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigd.h

## Scope

Generated Ghostscript directory, library, revision, and startup configuration.

## Key Behavior

- Sets default library path to `/sys/lib/ghostscript:/sys/lib/ghostscript/font:/sys/lib/postscript/font`.
- Sets an empty cache directory and `SEARCH_HERE_FIRST`.
- Defines documentation directory, init file name, revision number `853`, and revision date `20051020`.

## Dependencies

Consumed by Ghostscript platform/config headers and startup path logic.

## Risks And Invariants

- Paths are Plan 9 / 9front specific.
- Revision constants describe the bundled Ghostscript source snapshot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigv.h

## Scope

Generated low-level build-option header fragment.

## Key Behavior

- Defines `USE_ASM` as disabled expression `(-0)`.
- Defines `USE_FPU` as enabled expression `(1-0)`.
- Defines `EXTEND_NAMES` as 0.
- Defines `SYSTEM_CONSTANTS_ARE_WRITABLE` as 0.

## Dependencies

Consumed by Ghostscript core configuration headers.

## Risks And Invariants

- Encodes target build assumptions; changing it affects portability and interpreter semantics.
- `SYSTEM_CONSTANTS_ARE_WRITABLE` controls whether system constants can be modified.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfxx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfxx.h

## Scope

Generated configuration inventory equivalent to `gconfig.h`.

## Key Behavior

- Lists the same configured resources as `gconfig.h`: compositors, devices, operators, PostScript files, IODevices, emulators, function types, image types, image classes, and init procedures.
- Intended for macro-driven inclusion by configuration table builders or alternate build paths.
- Contains the same Plan 9, printer, image/PDF/PostScript, FAPI, and interpreter-resource entries.

## Dependencies

Used through conditional macro definitions by Ghostscript build/configuration code.

## Risks And Invariants

- Generated content must stay synchronized with the configured build.
- The file has no traditional declarations unless macros like `device_`, `oper_`, or `psfile_` are defined by the includer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfxx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdebug.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdebug.h

## Scope

Ghostscript debug/tracing macro definitions.

## Key Behavior

- Declares `gs_debug[128]` and `gs_debug_c`, with uppercase flags enabling corresponding lowercase flags.
- Aliases `gs_log_errors` to `gs_debug['#']`.
- Redirects diagnostic streams to `gs_debug_out` when `DEBUG` is enabled.
- Defines `if_debug0` through `if_debug12` macros that compile to debug printing under `DEBUG` and `DO_NOTHING` otherwise.
- Declares byte, bitmap, and string debug dump helpers.

## Dependencies

Depends on Ghostscript debug print helpers such as `dlprintfN`, `dprintfN`, and `DO_NOTHING`.

## Risks And Invariants

- Debug code inclusion is compile-unit-specific via `DEBUG`; runtime output still depends on flags.
- `gs_debug_c` flag semantics are relied on by many call sites for selective tracing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3852.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3852.c

## Scope

IBM 3852 JetPrinter color inkjet Ghostscript printer driver.

## Key Behavior

- Defines `gs_jetp3852_device` at 84x84 DPI with 3-bit PCL-style color mapping.
- `jetp3852_print_page` initializes the printer, scans each line, skips blank lines, transposes pixel data into color planes, complements bytes, and emits printer commands.
- Uses RGB plane order expected by the printer after transforming Ghostscript scanline data.

## Dependencies

Uses Ghostscript printer helpers from `gdevprn.h` and PCL color mapping from `gdevpcl.h`.

## Risks And Invariants

- `LINE_SIZE` is rounded for 8-byte transposition units.
- Output protocol relies on printer-specific escape sequences and line/plane byte counts.
- Blank-line skipping differs for top-of-page and mid-page positions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3852.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3b1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3b1.c

## Scope

Interactive console-display driver for AT&T 3B1/7300/UnixPC.

## Key Behavior

- Defines a custom `gx_device_att3b1` with a framebuffer, console window fd, line size, page number, and optional performance-disable flags.
- Opens `/dev/tty`, verifies UnixPC window support with `WIOCGETD`, allocates a page-sized monochrome framebuffer, and draws into it.
- Implements rectangle fill and monochrome bitmap copy directly into the framebuffer using word masks, bit reversal, and rotate operations.
- On output, saves the window image, changes terminal/window modes, displays a screen-sized view into the page, and lets the user scroll/navigate with vi keys, arrows, page keys, and window icons.
- Restores terminal state, border flags, soft label text, cursor mode, and saved screen image on exit.

## Dependencies

Uses Ghostscript device APIs plus UnixPC-specific `<sys/window.h>` and `<sys/termio.h>` ioctls.

## Risks And Invariants

- Assumes console window semantics and fixed screen constants such as `WINWIDTH` / `WINHEIGHT`.
- `copy_mono` assumes short-aligned input bitmap data and even raster alignment.
- Output is interactive and blocks for keyboard input per page.
- Window save/restore behavior is documented as unreliable on some 3B1 window-manager states.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3b1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4081.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4081.c

## Scope

Ricoh 4081 laser printer driver.

## Key Behavior

- Defines `gs_r4081_device` at 300x300 DPI with standard monochrome printer procs.
- Allocates one output scanline buffer.
- Finds first and last nonblank scanlines to reduce transmitted data.
- Emits printer initialization/start-position command with width, height, and vertical offset.
- Writes scanline graphics, then formfeeds and reinitializes the printer.

## Dependencies

Uses Ghostscript printer APIs from `gdevprn.h`.

## Risks And Invariants

- Nonblank detection compares the first byte against the rest of the line, effectively detecting all-zero lines.
- Output command syntax is Ricoh-specific.
- Allocation failure returns `-1` rather than a named Ghostscript VM error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4081.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4693.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4693.c

## Scope

Tektronix 4693d color plotter driver.

## Key Behavior

- Defines 8-bit, 16-bit, and 24-bit color devices: `t4693d2`, `t4693d4`, and `t4693d8`.
- Maps Ghostscript RGB values into packed device color indices based on bits per color.
- Builds and writes a binary print-request header with checksum.
- Streams each scanline in device pixel-size chunks, adjusting packed bytes for 8-bit and 16-bit modes and host endianness.
- Ends scanlines with `0x02` and page data with `0x01`.

## Dependencies

Uses Ghostscript printer APIs, color mapping procs, allocation helpers, and `arch_is_big_endian`.

## Risks And Invariants

- 16-bit depth treats five bits per channel as four usable bits.
- Header checksum and byte-coded protocol must match Tektronix expectations exactly.
- Write failures return `gs_error_ioerror`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev4693.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8510.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8510.c

## Scope

C.Itoh M8510 printer driver.

## Key Behavior

- Defines `gs_m8510_device` at 160x144 DPI.
- Allocates two 8-scanline input passes and one transposed output buffer.
- Initializes printer mode, copies alternating scanlines into two pass buffers, transposes 8x8 blocks, and emits each pass.
- `m8510_output_run` trims trailing zero 8-byte groups and writes `ESC g` run commands followed by carriage return/newline handling.
- Resets printer at page completion.

## Dependencies

Uses Ghostscript printer helpers including `gdev_prn_copy_scan_lines` and `gdev_prn_transpose_8x8`.

## Risks And Invariants

- Processes 16 source scanlines per loop: two interleaved 8-line passes.
- Output buffer width must be a multiple of 8 for trailing-zero trimming.
- Allocation failures are reported as `gs_error_VMerror`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8510.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.c

## Scope

Shared dynamic color-map implementation for 8-bit display devices.

## Key Behavior

- `gx_8bit_map_init` clears a hash table and sets maximum dynamic colors.
- `gx_8bit_map_rgb_color` hashes a 15-bit RGB key into an open-addressed map and returns either an index or a negative insertion slot.
- `gx_8bit_add_rgb_color` adds a previously missing RGB key and assigns the next dynamic color index.

## Dependencies

Uses declarations from `gdev8bcm.h` and Ghostscript color value types.

## Risks And Invariants

- The negative “not found” return encodes an insertion slot by subtracting from the end of the map array.
- Callers must honor `max_count`; the map table has capacity beyond the configured dynamic color count.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.h

## Scope

Header for shared 8-bit dynamic color-map support.

## Key Behavior

- Defines map size `323` and hash spreader `123`.
- Defines compact RGB keying using the top 5 bits of each Ghostscript color channel.
- Defines `gx_8bit_map_entry` and `gx_8bit_color_map`.
- Declares initialization, lookup, fullness test, and add functions.

## Dependencies

Requires `gxdevice.h` color value definitions.

## Risks And Invariants

- Top-5-bit RGB keying trades precision for speed.
- `gx_8bit_no_rgb` is `0xffff`, outside the 15-bit key space.
- The map includes an extra sentinel-sized entry in its array definition.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev8bcm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevabuf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevabuf.c

## Scope

Alpha memory devices and alpha-buffering device for antialiased rasterization.

## Key Behavior

- `gs_make_mem_alpha_device` creates 2-bit or 4-bit alpha devices that behave like black/white for color mapping but store multiple bits per pixel.
- Alpha color mapping forwards to the target device and converts nonzero colors into alpha levels.
- `gs_make_mem_abuf_device` creates an oversampled monobit buffer that compresses accumulated bits into alpha scanlines for a lower-resolution target.
- Maintains a sliding mapped Y window to avoid copying band storage as rendering advances.
- Flushes full alpha blocks with `bits_bounding_box`, `bits_compress_scaled`, and target `copy_alpha`.
- Implements `copy_mono`, `fill_rectangle`, close/flush, and scaled clipping-box behavior.

## Dependencies

Uses Ghostscript memory-device internals, bitmap compression/scaling helpers, forwarding color mapping, and target `copy_alpha`.

## Risks And Invariants

- Client rendering must visit bands mostly top-to-bottom and not repaint arbitrary old bands.
- Buffer height must be compatible with Y scale; blocks flush at scale-factor boundaries.
- Only single-color output is supported; `save_color` carries the target color through flush.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevabuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevadmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevadmp.c

## Scope

Apple Dot Matrix Printer and ImageWriter family driver.

## Key Behavior

- Defines devices `appledmp`, `iwlo`, `iwhi`, and `iwlq` with different horizontal/vertical resolutions.
- `dmp_print_page` chooses a device mode from resolution, initializes the printer, and processes the page in 8-, 16-, or 24-scanline groups.
- Copies scanlines in reversed vertical order for printer bit ordering, transposes 8x8 blocks, and packs data differently for DMP/IW low, IW high, and ImageWriter LQ.
- Trims leading/trailing blank data and emits printer commands for skips and graphics data.
- Applies ImageWriter end-of-page workaround before formfeed/reset.

## Dependencies

Uses Ghostscript printer helpers and transposition routines from `gdevprn.h`.

## Risks And Invariants

- Different device modes use different pass counts and packing layout.
- The ImageWriter paper-position workaround is printer-behavior-specific.
- Allocation cleanup must free three large buffers on error and success.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevadmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevatx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevatx.c

## Scope

Practical Automation ATX-23, ATX-24, and ATX-38 printer driver.

## Key Behavior

- Defines three printer devices with model-specific page widths, DPI, and margins.
- Emits ATX commands for page length, vertical tab, uncompressed data, compressed data, and end page.
- `atx_compress` encodes even-byte scanline data as repeated-pair compressed segments or literal pair segments.
- `atx_print_page` computes capped page height, enforces minimum page length, skips blank lines, truncates to model maximum width, compresses when beneficial, and writes page data.
- Per-model print functions call common output with maximum byte widths.

## Dependencies

Uses Ghostscript printer APIs, allocation helpers, `math_.h` for `ceil`, and raster access helpers.

## Risks And Invariants

- Compressed data command has a one-byte word count, so compressed scanlines are capped at 510 bytes.
- Input and output compression sizes are assumed even.
- Comments note margin handling is conceptually wrong because coordinates are treated as printable-area coordinates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevatx.c -->