# Group Research: group_116_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevxxf_c_sources__96f20f5f2ed7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxxf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxxf.c

Ghostscript X11 external-font implementation. It lets the X11 display device substitute suitable X server fonts for Ghostscript fonts.

Key behavior:
- Exposes `gdev_x_get_xfont_procs` with lookup, glyph conversion, metrics, render, and release callbacks.
- Maps PostScript font names to configured X11 font names, choosing Adobe-fontspecific or ISO8859-1 encodings and fixed/scalable X font instances.
- Accepts only simple non-skewed transforms: upright, mirrored, or 90-degree rotations when font extensions are enabled.
- Rejects too-small and too-large X fonts to avoid bad metrics or server lockups.
- Converts Ghostscript character codes across StandardEncoding and ISO encodings when needed.
- Renders directly to an unbuffered X11 device with batched `XTextItem`s, or rasterizes into a 1-bit X pixmap and copies bits to other devices.

Notable dependencies:
- X11 APIs and Ghostscript X device structures from `x_.h`, `gdevx.h`, and `gxxfont.h`.
- Uses configured `x11fontmap` lists from the X device.

Research notes:
- The file is display/font acceleration code, not filesystem logic.
- `x_release` intentionally does not free the X font because the device may not be open reliably at release time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genarch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genarch.c

Build-time generator for `arch.h`, deriving compiler and machine architecture parameters.

Key behavior:
- Writes scalar alignment macros for short, int, long, pointer, float, double, and `jmp_buf`.
- Writes scalar size macros, float/double mantissa estimates, and unsigned max-value macros.
- Detects IEEE float representation by inspecting bit patterns for 0, 1, and -1.
- Estimates primary and secondary cache sizes by timing repeated `memset` calls across larger buffers.
- Emits endian, pointer signedness, arithmetic right-shift behavior, full-width long shift behavior, and negative-division semantics.

Notable dependencies:
- Uses `stdpre.h` and standard C headers including `string.h`, `time.h`, and `setjmp.h`.
- Relies on Ghostscript build macros such as `private`, `size_of`, `exit_OK`, and `exit_FAILED`.

Research notes:
- It writes to the output file named by `argv[1]` rather than stdout for old make-tool compatibility.
- The cache-size detection is heuristic and build-host dependent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genconf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genconf.c

Build-time `.dev` configuration merger. It reads Ghostscript module definition files and emits configuration headers and object/library transfer files.

Key behavior:
- Parses `.dev` token streams with categories such as `-dev`, `-dev2`, `-comp`, `-font`, `-functiontype`, `-halftone`, `-imageclass`, `-imagetype`, `-include`, `-init`, `-iodev`, `-lib`, `-libpath`, `-link`, `-obj`, `-oper`, `-plugin`, `-ps`, and `-replace`.
- Recursively reads included `.dev` files, caching file contents and avoiding duplicate work when possible.
- Tracks each resource with its source-file index so `-replace` can remove all entries contributed by a replaced module.
- Maintains resource lists with uniqueness policies: first occurrence, last occurrence, or all occurrences.
- Emits `gconfig.h` style macro calls, `gconfigf.h` font entries, and object/library/linker lists depending on command-line output switches.
- Supports formatting patterns for object/library outputs, with uppercase and extension-dropping options.

Notable dependencies:
- Standard C file/string allocation APIs only; this is a standalone build utility.
- Output macro names must match consumers documented in `gsconfig.c` and the Ghostscript make rules.

Research notes:
- `mrealloc` intentionally allocates/copies instead of using `realloc` for portability across older systems.
- Pattern substitution uses `%s` internally and repeats the item up to three times for patterns needing multiple substitutions.
- This is build configuration infrastructure, not runtime filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gendev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gendev.c

Build-time `.dev` file generator. It creates per-module `.dev` fragments from command-line category/item pairs.

Key behavior:
- Accepts device, module, and append modes through `-d`, `-m`, and `-a`.
- Supports name-prefix and file-prefix switches for generated symbols and object paths.
- Writes include-guarded `.dev` output containing category-specific macro calls.
- Handles categories such as `dev`, `dev2`, `emulator`, `font`, `include`, `init`, `iodev`, `lib`, `obj`, `oper`, and `ps`.
- Uses a `RES_SCAN` pass to handle `uniq_last` semantics for libraries, recording the last contributing file/item marker.

Notable dependencies:
- Standalone C build tool using standard headers and Ghostscript `stdpre.h`.

Research notes:
- Comments note unimplemented behaviors: no `-replace` handling and no merge of `device` and `device2`.
- The generated output is consumed by `genconf.c` and the build system.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gendev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genht.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genht.c

Build-time generator for compiling PostScript halftone resources into C data.

Key behavior:
- Reads a constrained PostScript halftone resource file into memory.
- Parses HalftoneType 5 prefixes and HalftoneType 3 halftone entries with Width, Height, and ASCIIHex Thresholds.
- Converts threshold bytes into Ghostscript halftone order data through `ht_order_procs_short.construct_order`.
- Emits C arrays for levels and bit data plus `gx_device_halftone_resource_t` structures.
- Writes a `gs_dht_<prefix>` procedure returning the static halftone-resource table.

Notable dependencies:
- Uses Ghostscript halftone and stream code: `gxdhtres.h`, `gxhttile.h`, `gxtmap.h`, `strimpl.h`, `sstring.h`.
- Includes implementation files directly (`gxhtbit.c`, `scantab.c`, `sstring.c`) to avoid a separate link step.

Research notes:
- The parser is intentionally narrow and ignores most PostScript that does not match the expected resource shape.
- It includes GC and stream stubs required by the included implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/genht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/geninit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/geninit.c

Build-time utility for merging Ghostscript initialization PostScript files into one PostScript file or a C byte array.

Key behavior:
- Supports output as merged PostScript or `const unsigned char gs_init_string[]`.
- Opens input files with an optional prefix and Mac path translation.
- Reads lines with explicit Unix, Mac, and PC end-of-line handling instead of `fgets`.
- Recognizes `%% Replace` directives to include named files or all `INITFILES` from a generated config file.
- Strips comments and whitespace when safe while preserving strings and special `%END` comments.
- Detects LanguageLevel 2 object-format sections and can convert ASCIIHex strings into binary string tokens.
- Stops at `currentfile closefile`, treating the rest of an init file as debugging code.

Notable dependencies:
- Standalone C build utility with `stdpre.h` and standard C headers.
- Reads config lines containing `psfile_(...)` generated by the configuration system.

Research notes:
- `LINE_SIZE` is fixed at 128, so path and directive parsing is intentionally bounded.
- It logs input byte positions and output positions to stderr while merging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/geninit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ghost.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ghost.h

Minimal interpreter common header.

Key contents:
- Include guard `ghost_INCLUDED`.
- Includes `gx.h` and `iref.h`.

Research notes:
- This header only establishes common interpreter definitions through other headers.
- It contains no executable logic and no filesystem-specific behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ghost.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp.h

Ghostscript platform-abstraction interface header. It declares the cross-platform API implemented by the many `gp_*.c` files.

Key contents:
- Initialization and exit hooks: `gp_init`, `gp_exit`, `gp_do_exit`.
- Error string, realtime/usertime, readline, and stdin-read interfaces.
- Display environment lookup for X-like display devices.
- File naming constants and platform-specific file mode strings.
- Scratch-file creation, byte-oriented `gp_fopen`, binary/text mode switching, and path-combination helpers.
- Mac resource-fork access through `gp_read_macresource`.
- Persistent cache API for typed key/value buffers.
- Printer open/close abstraction.
- File enumeration API for wildcard expansion.
- Native font enumeration API.

Research notes:
- `gp_getenv` lives in `gpgetenv.h` and synchronization lives in `gpsync.h`; this header deliberately excludes those.
- Path helper comments document Unix, Windows, Mac, and VMS semantics.
- Several comments contain historical misspellings such as “partent” and “meanful”; corresponding API names preserve them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfe.c

MS-DOS file enumeration implementation.

Key behavior:
- Defines `file_enum_s` with DOS find state, original and translated patterns, directory-prefix size, and allocator.
- Translates Ghostscript wildcard patterns into DOS-compatible patterns, including converting bare `*` to `*.*`.
- Uses `dos_findfirst` and `dos_findnext` to enumerate directory entries.
- Reattaches the original directory prefix and strips spaces from DOS file names.
- Uses Ghostscript `string_match` as a post-filter to enforce the original pattern.

Notable dependencies:
- DOS compatibility wrappers from `dos_.h`.
- Ghostscript GC descriptors and `gsutil.h` string matching.

Research notes:
- The comment notes DOS limitations with wildcards in directory components and backslash escaping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfs.c

Common MS-DOS and DesqView/X filesystem helper routines.

Key behavior:
- Uses DOS ioctl interrupt calls to set device file handles into binary or text mode.
- Provides `gp_setmode_binary`.
- Defines DOS-style file-list separator `;`, binary suffix `b`, and binary modes `rb`/`wb`.
- Implements Windows/DOS path root detection including drive letters, root slashes, and UNC paths.
- Provides path separator, parent/current directory, and path-combination helper functions that delegate to `gp_file_name_combine_generic`.

Notable dependencies:
- DOS register APIs from `dos_.h`.
- Generic path-combination helper from `gpmisc.h`.

Research notes:
- This is path and file-mode glue, not file enumeration; DOS enumeration is in `gp_dosfe.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dvx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dvx.c

DesqView/X-specific Ghostscript platform routines.

Key behavior:
- Provides no-op init/exit and `exit`-based termination.
- Uses `strerror` for OS error strings.
- Implements realtime through `gettimeofday`, with user time as realtime approximation.
- Stubs persistent cache insert/query.
- Opens the default printer as `stdprn`/`PRN` or a named file, setting binary mode when needed.
- Stubs native font enumeration.

Notable dependencies:
- Uses common MS-DOS printer binary-mode helper `gp_set_file_binary`.
- Includes `time_.h`, `gsexit.h`, and `gp.h`.

Research notes:
- Cache functions are marked “not yet implemented” but return success for insert and failure for query.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dvx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_getnv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_getnv.c

Standard `gp_getenv` implementation.

Key behavior:
- Wraps the C library `getenv`.
- Copies the environment value into the supplied buffer when it fits.
- Returns `0` on success, `-1` when the buffer is too small, and `1` when the key is missing.
- Always updates `*plen` to the required length including the null terminator.

Research notes:
- Missing variables produce an empty string if the caller supplied a nonzero buffer length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_getnv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_iwatc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_iwatc.c

Intel/Watcom C platform routines for DOS-like Ghostscript builds.

Key behavior:
- Initializes a SIGFPE handler that reports numeric exceptions and exits.
- Provides no-op cleanup and direct `exit` termination.
- Stubs persistent cache operations.
- Opens printer output through `stdprn`, `PRN`, or a named file, with special handling to reopen `stdprn` in binary mode for Watcom newline behavior.
- Creates scratch files under the configured temp directory using `mktemp` and `gp_fopentemp`.
- Provides plain `fopen` as `gp_fopen`.
- Stubs native font enumeration.

Notable dependencies:
- Uses DOS/Watcom file APIs, `setmode`, `dup`, and `fdopen`.
- Relies on replacement `mktemp` from `gp_mktmp.c`.

Research notes:
- Persistent cache and native font enumeration are not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_iwatc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.c

Classic/Carbon MacOS platform core routines.

Key behavior:
- Provides basic init/exit/termination hooks and a DLL-instance identifier `hwndtext`.
- Implements Mac-oriented time functions using `time`, `GetDateTime`, `SecondsToDate`, and `Microseconds`.
- Provides realtime and usertime approximations.
- Returns no platform error string.
- Stubs persistent cache operations.
- Provides no-op console initialization and display-env lookup.
- Contains older alternate clock implementations for days since January 1, 1980 and nanosecond-style fractions.

Notable dependencies:
- Classic Mac and Carbon headers, `gsdll.h`, `gpcheck.h`, and `gp_mac.h`.

Research notes:
- Several blocks are disabled or legacy, including default library path initialization.
- The active `gp_get_usertime` subtracts a random byte from seconds, apparently to perturb random seeds on very fast systems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.h

Small Mac platform support header.

Key contents:
- Include guard `gp_mac_INCLUDED`.
- Defines `HWND` as `int`.
- Declares `hwndtext`, used as a DLL/application instance identifier by Mac polling and callback code.

Research notes:
- This is a compatibility shim so code shared with Windows-style callback paths can compile on Mac.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macio.c

MacOS file, stdio, resource, path, and native-font platform implementation.

Key behavior:
- Converts between Mac `FSSpec` objects and colon-delimited HFS paths.
- Supplies a custom `getenv` for `GS_LIB`, deriving paths under the system Application Support folder.
- Installs a `macstdio` pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` to route through the Ghostscript DLL callback.
- Opens printer output as a scratch file or regular file.
- Creates scratch files in the temporary folder using `tmpnam`, `FindFolder`, and `FSMakeFSSpec`.
- Reads Mac resource-fork data by type/id through `FSpOpenResFile` and `Get1Resource`.
- Provides a placeholder file enumeration implementation that never returns matches.
- Implements Mac path-combination helpers using `:` separators and Carbon volume root detection when available.
- Enumerates native fonts with Font Manager APIs, generating PostScript-like names and paths, including `%macresource%...#sfnt+id` references from FOND resources.

Notable dependencies:
- Classic MacOS/Carbon file, resource, folder, and font APIs.
- Ghostscript callback interface from `gsdll.h`.

Research notes:
- Comments explicitly say file enumeration is unsupported on Macintosh systems.
- Font enumeration caches the last font container and parsed FOND table to avoid reparsing.
- Several comments flag incomplete Unicode and LWFN handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macpoll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macpoll.c

Mac platform polling and interrupt callback support.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts`.
- Throttles polling using `TickCount`, only yielding after more than two ticks.
- Calls the deprecated `pgsdll_callback` poll path if present, passing `hwndtext`.
- Otherwise falls back to the newer `gs_lib_ctx->poll_fn` callback.

Notable dependencies:
- Carbon or Classic Mac timer headers.
- Ghostscript interpreter/library context headers.

Research notes:
- Comments warn that static state and fallback global memory lookup are not thread-safe.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macpoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mktmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mktmp.c

Replacement `mktemp` implementation for platforms lacking one.

Key behavior:
- Requires a filename ending in `XXXXXX`.
- Replaces the suffix with `AA.AAA`.
- Uses `stat` to test for existing files.
- Increments alphabetic characters, skipping dots, until an unused name is found or the space is exhausted.

Research notes:
- This only generates a candidate name; it does not atomically create the file, so callers must open carefully.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mktmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdll.c

Windows DLL entry point support.

Key behavior:
- Defines `DllEntryPoint` for Borland C++ and `DllMain` for Microsoft Visual C++.
- Records the DLL instance handle in `phInstance`.
- Detects Win32s by inspecting `GetVersion` high-word bits and sets `is_win32s`.

Notable dependencies:
- Windows headers and shared declarations from `gp_mswin.h`.
- Export macros from `iapi.h`.

Research notes:
- This file only initializes global DLL platform state; it does not implement I/O itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdos.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdos.c

Common MS-DOS platform routines.

Key behavior:
- Uses `strerror` for OS error strings.
- Computes realtime from DOS date/time interrupts, using an epoch of January 1, 1980 and hundredths of seconds.
- Uses realtime as usertime approximation.
- Detects console files through DOS ioctl device-info bits.
- Provides no display environment variable.
- Defines scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Notable dependencies:
- DOS register interface from `dos_.h`.

Research notes:
- Console detection has a special DLL behavior where `NULL` is considered console.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mshdl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mshdl.c

Windows `%handle%` IODevice implementation.

Key behavior:
- Registers `gs_iodev_handle` as a FileSystem IODevice named `%handle%`.
- Parses a hexadecimal OS handle from the filename suffix.
- Converts the OS handle to a C file descriptor with `_open_osfhandle`.
- Wraps the descriptor in a `FILE *` using `fdopen`.
- Closes the stream on IODevice close.

Notable dependencies:
- Windows/MS C runtime `<io.h>` handle functions.
- Ghostscript IODevice interfaces from `gxiodev.h`.

Research notes:
- Comments note the handle-size assumptions are correct for Win32 and maybe wrong for Win64.
- Intended for callers that pass pipe or file handles to Ghostscript output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mshdl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msio.c

Windows text-window stdio stream substitution.

Key behavior:
- Registers a pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` open procedures when the corresponding C stream is a console.
- Replaces stream processing with callback-based stdin and stdout/stderr handlers using `pgsdll_callback`.
- Marks stream availability as unknown/EOF-like with `*pl = -1`.
- Overrides `fprintf` for supported Windows compilers so console writes go through the Ghostscript DLL callback instead of stdio.

Notable dependencies:
- Ghostscript stream and IODevice interfaces.
- Windows platform declarations from `gp_mswin.h` and callback constants from `gsdll.h`.

Research notes:
- The file contains an MSVC `/MD` workaround to avoid `fprintf` import/export conflicts.
- It assumes `pgsdll_callback` is valid on the callback paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mslib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mslib.c

Windows graphics-library-specific polling stub.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts` to return `0`.

Research notes:
- This differs from interpreter polling: the graphics library variant intentionally performs no callback polling here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mspol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mspol.c

Windows interpreter polling support.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts`.
- Uses the provided memory context, or falls back to `gs_lib_ctx_get_non_gc_memory_t`.
- Invokes `gs_lib_ctx->poll_fn(caller_handle)` if present.
- Returns `0` when no polling callback exists.

Notable dependencies:
- Ghostscript interpreter/library context headers: `iapi.h`, `iref.h`, `iminst.h`, `imain.h`.

Research notes:
- A comment marks the fallback memory lookup as a major non-thread-safe hack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mspol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msprn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msprn.c

Windows `%printer%` IODevice implementation.

Key behavior:
- Registers a FileSystem IODevice named `%printer%`.
- Validates the requested printer name with `OpenPrinter`.
- Creates a binary pipe and returns a `FILE *` for the write end.
- Starts a background thread that reads the printer name and print bytes from the pipe.
- The thread opens the printer, starts a RAW document, writes data with `WritePrinter`, and ends or aborts the job.
- Close waits up to 60 seconds for the print thread and closes its duplicated handle.

Notable dependencies:
- Windows spooler APIs and Microsoft runtime `_pipe`, `_beginthread`, and handle duplication.
- Ghostscript IODevice and product-name definitions.

Research notes:
- Win32s is rejected because it lacks required pipe and printer APIs.
- The printer name is sent through the pipe to avoid more complex thread synchronization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msprn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.c

Microsoft Windows platform support for Ghostscript DLL builds.

Key behavior:
- Provides basic init/exit/termination hooks and unimplemented persistent cache stubs.
- Opens printer destinations by writing to a scratch file first, then spooling it on close.
- Detects printer names from empty output names, win.ini `[ports]`, or `\\spool` prefixes.
- Enumerates printer queues/ports and prompts through dialog boxes when needed.
- Spools via Win32 `OpenPrinter`/`StartDocPrinter`/`WritePrinter` for Win95/NT-class systems.
- Falls back to launching `gs16spl.exe` for Win32s or port-style printing.
- Implements a custom write-only `mswin_popen` using `CreatePipe`, inheritable handles, and `CreateProcess`.
- Creates scratch files using `GetTempPath`, `GetTempFileName`, `CreateFile`, `_open_osfhandle`, and `fdopen`.
- Provides plain `fopen` as `gp_fopen`.
- Stubs native font enumeration.

Notable dependencies:
- Windows shell/spooler APIs and shared declarations from `gp_mswin.h`.
- Path helpers from `gpmisc.h`.

Research notes:
- Printing behavior preserves legacy `\\spool\...` semantics while newer `%printer%` support lives in `gp_msprn.c`.
- The custom `popen` only supports mode `wb`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.h

Shared Windows platform/resource header.

Key contents:
- Defines resource/control IDs for Ghostscript text/image icons, spool dialog controls, and cancel controls.
- Defines image-window system-menu command `M_COPY_CLIP`.
- Handles `_export` compatibility for 32-bit MSVC.
- Declares `phInstance`, `szAppName`, `is_win32s`, and `is_spool`.
- Defines `DLGRETURN` as `INT_PTR` on Win64 and `BOOL` otherwise.

Research notes:
- The header is designed for use by both C code and Windows resource scripts, so declarations are hidden under `!RC_INVOKED`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_nsync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_nsync.c

Dummy synchronization and threading implementation.

Key behavior:
- Represents semaphores as a simple integer counter.
- `wait` fails with `unknownerror` when the counter is zero instead of blocking.
- Represents monitors with a dummy owner pointer and detects simple enter/leave misuse.
- `gp_create_thread` always returns `unknownerror`.

Research notes:
- This is for single-threaded or no-thread builds where real synchronization is unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_nsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_ntfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_ntfs.c

Windows NT/Win32 filesystem support, adapted from DOS filesystem support.

Key behavior:
- Sets binary/text file mode through `_setmode` or `setmode`.
- Defines Windows-style file-list separator, binary suffix, and binary modes.
- Implements file enumeration with `FindFirstFile` and `FindNextFile`.
- Removes Ghostscript escape backslashes before passing patterns to the OS.
- Skips `.` and `..` and directory entries during enumeration.
- Reattaches the directory prefix to returned file names.
- Provides Windows/DOS path root and separator helpers and delegates path combination to `gp_file_name_combine_generic`.

Notable dependencies:
- Windows file APIs and Ghostscript GC descriptors.

Research notes:
- Directory wildcard limitations are documented in comments.
- The enumeration truncation behavior returns `maxlen` or `0` depending on whether any prefix can fit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.c

OS/2 and EMX/GCC platform support, with DOS fallback paths.

Key behavior:
- Provides error strings, realtime/usertime via `gettimeofday`, and console detection.
- Defines OS/2/DOS filename constants, binary modes, null device, and current directory.
- Enumerates files with `DosFindFirst`/`DosFindNext` on OS/2; DOS fallback returns the pattern once.
- Initializes EMX DLL environment from the process environment and installs a SIGFPE handler.
- Opens printers as OS/2 spool scratch files, pipes, `PRN`, or normal files.
- Finds and validates spool queues with `SplEnumQueue`.
- Spools scratch-file data through `SplQmOpen`, `SplQmStartDoc`, `SplQmWrite`, and `SplQmEndDoc`.
- Creates scratch files with `_tempnam` for IBM C or `mktemp`/`gp_fopentemp` otherwise.
- Implements Windows/DOS-like path-combination helpers.
- Stubs persistent cache and native font enumeration.

Notable dependencies:
- OS/2 spooler and DOS APIs, EMX support, `gdevpm.h`, and `gp_os2.h`.

Research notes:
- `\\spool\queue` is the OS/2 queue naming convention for printer output.
- Comments warn that user CPU time is approximated by realtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.h

OS/2 platform support header.

Key contents:
- Include guard `gp_os2_INCLUDED`.
- Includes OS/2 API headers with spooler and windowing feature macros enabled.
- Declares `HWND hwndtext` for DLL builds.
- Declares `pm_find_queue` and `pm_spool`, implemented in `gp_os2.c`.

Research notes:
- This header exposes printer queue/spooling helpers used by OS/2 printer IODevice code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2pr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2pr.c

OS/2 `%printer%` IODevice implementation.

Key behavior:
- Registers a FileSystem IODevice named `%printer%`.
- Allocates per-device state containing the target queue and scratch filename.
- Validates the requested queue through `pm_find_queue`.
- Opens output as a scratch file with `gp_open_scratch_file`.
- On close, spools the scratch file with `pm_spool` and unlinks it.

Notable dependencies:
- OS/2 spooler support functions from `gp_os2.c`.
- Ghostscript IODevice interfaces from `gxiodev.h`.

Research notes:
- Comments say a pipe/thread implementation was considered but did not work properly for the second Ghostscript thread.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2pr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os9.c

OS-9/OSK-specific platform routines.

Key behavior:
- Installs a signal handler through `intercept`, setting a global `interrupted` flag for interrupt/quit/FPE.
- Computes realtime from OS-9 `_sysdate` and `_julian`, using a January 1, 1980 base.
- Uses realtime as usertime approximation.
- Stubs persistent cache operations.
- Opens printer output as a pipe or a raw-buffered file; empty printer name returns `NULL`.
- Sets raw-buffered mode through the C library `_RBF` flag.
- Stubs native font enumeration.

Research notes:
- The code references `file->_flag` inside `gp_setmode_binary`, though the parameter is named `pfile`, indicating a likely historical typo or platform macro expectation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_psync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_psync.c

POSIX pthread synchronization and detached-thread implementation.

Key behavior:
- Implements semaphores with a count, `pthread_mutex_t`, and `pthread_cond_t`.
- `wait` blocks while count is zero, then decrements.
- `signal` increments count and signals the condition when transitioning from zero.
- Implements monitors as plain pthread mutexes.
- Creates detached threads by wrapping Ghostscript’s callback signature in a `void *` pthread start routine.
- Maps pthread errors coarsely to `gs_error_ioerror`.

Notable dependencies:
- POSIX pthreads and Ghostscript `gpsync.h`.

Research notes:
- A comment notes error handling should inspect `errno` more precisely.
- The thread wrapper heap-allocates a closure and frees it at thread start.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_psync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdia.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdia.c

Unbuffered stdin reader for platforms supporting `read`.

Key behavior:
- Implements `gp_stdin_read` by calling `read(fileno(f), buf, len)`.
- Ignores the `interactive` flag because unbuffered reads are available.

Notable dependencies:
- `unistd_.h` and standard file descriptors.

Research notes:
- Intended for console input and pipes where buffered stdio behavior is undesirable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdin.c

Portable buffered stdin reader for platforms without unbuffered reads.

Key behavior:
- Implements `gp_stdin_read` with `fread`.
- Reads one byte when `interactive` is true, otherwise reads up to the requested length.

Research notes:
- Comments note this is portable but slow for interactive stdin because it reads one byte at a time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_strdl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_strdl.c

Default stream-based readline implementation.

Key behavior:
- `gp_readline_init` returns success without allocating state.
- `gp_readline` delegates directly to `sreadline`.
- `gp_readline_finit` is a no-op.

Notable dependencies:
- Stream readline API from `srdline.h` through `gp.h`.

Research notes:
- This is the fallback implementation when no enhanced platform readline package is used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_strdl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_sysv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_sysv.c

Compatibility implementations for older System V Unix platforms.

Key behavior:
- Provides `rename` using `access`, `unlink`, `link`, and final `unlink` of the source.
- Provides `gettimeofday` using `times`, `time`, and a cached offset from process ticks to wall-clock seconds.
- Uses `HZ` from system headers or defaults to 100.

Research notes:
- Comments state this file is not used for SVR4 platforms.
- The fallback `rename` is not equivalent to modern atomic `rename`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_sysv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifn.c

Unix-like filename syntax helpers.

Key behavior:
- Defines `:` as file-list separator.
- Defines no binary-mode suffix and uses `r`/`w` for binary read/write modes.
- Treats `/` as the root and path separator.
- Recognizes `..` as parent and `.` as current directory.
- Delegates full path combination to `gp_file_name_combine_generic`.

Research notes:
- This is path syntax glue for Unix-like platforms, not file I/O or enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifn.c -->