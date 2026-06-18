# Group Research: group_1554_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevxxf_c_sources_o_e603099b1b93

This group covers Ghostscript source files vendored under the Plan 9 source tree. The files are primarily Ghostscript build generators, X11 font support, and platform abstraction implementations for DOS, Windows, Mac OS, OS/2, OS-9, Unix-like systems, and synchronization/stdin helpers. They are in subset A because they live under `sources/os/plan9/plan9`, but most are portability and runtime support rather than Plan 9 kernel or VFS code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxxf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxxf.c

Read status: complete.

Purpose: implements Ghostscript external font (`xfont`) support for X11 devices. It lets Ghostscript use server-side X fonts for selected PostScript fonts and sizes instead of rasterizing glyphs internally.

Key structures and interfaces:
- Defines `x_xfont`, wrapping `gx_xfont_common`, `gx_device_X *`, `XFontStruct *`, encoding index, mirror flag, and rotation angle.
- Exposes `gdev_x_get_xfont_procs`, returning an X font procedure table with lookup, glyph mapping, metrics, rendering, and release callbacks.
- Uses Ghostscript GC metadata via `gs_private_st_dev_ptrs1`.

Main logic:
- `find_fontmap` locates a PostScript-to-X11 font mapping in linked `x11fontmap` lists.
- `find_x_font` lists matching X fonts lazily with `XListFonts`, detects exact bitmap sizes, and constructs scalable XLFD names when enabled.
- `x_lookup_font` accepts only axis-aligned or 90-degree rotated matrices, rejects very small or very large fonts, checks font extension/scalable support for rotation, mirroring, or non-square scaling, and loads the X font with `XLoadQueryFont`.
- `x_char_xglyph` maps Ghostscript character codes into X glyph byte codes, including standard/ISO remapping through `gs_map_std_to_iso` and `gs_map_iso_to_std`.
- `x_char_metrics` converts X font metrics into Ghostscript widths and bounding boxes, adjusting the advance vector for rotation.
- `x_render_char` either buffers direct X text drawing for X11 devices or renders through a 1-bit X pixmap, reads back with `XGetImage`, and calls the target device’s `copy_mono`.

Filesystem/storage relevance:
- No filesystem implementation. It is graphics/font runtime code, but it is part of the Ghostscript platform/device layer inside the Plan 9 source tree.

Notable behavior and risks:
- Font use is intentionally bounded to sizes 6 through 35 pixels to avoid poor small-font metrics and expensive large server rasterization.
- 16-bit/two-byte X fonts are rejected.
- `x_release` frees only the Ghostscript wrapper object; X font freeing is disabled because the device may not be open.
- If wrapper allocation fails after `XLoadQueryFont`, the loaded X font is not freed in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genarch.c

Read status: complete.

Purpose: build-time generator for `arch.h`, a mechanically generated header describing compiler and machine architecture properties needed by Ghostscript.

Main logic:
- Opens the output file named by `argv[1]`.
- Emits scalar alignment constants by measuring offsets in small structs.
- Emits scalar size constants, pointer size, float/double size, and mantissa-bit assumptions.
- Detects IEEE single-precision floats by inspecting bit patterns for `0.0`, `1.0`, and `-1.0`.
- Emits unsigned maximum constants using textual hexadecimal masks to avoid compiler warning/extension problems.
- Estimates primary and secondary cache sizes by timing repeated `memset` calls over increasing buffer sizes.
- Emits endian, signed-pointer comparison, arithmetic right-shift behavior, full-width shift behavior, and negative division truncation behavior.

Important functions:
- `section` prints comment section headers.
- `time_clear` times zero-filling a buffer.
- `define` and `define_int` write `#define` lines.
- `print_ffs` prints all-`ff` byte masks.
- `ilog2` computes rounded-up log2-style size encodings used by Ghostscript.

Filesystem/storage relevance:
- No runtime filesystem behavior. It writes a generated header at build time.

Notable behavior and risks:
- Assumes `argv[1]` exists; no `argc` validation.
- Cache-size detection is heuristic and time-sensitive.
- Some emitted architecture facts are derived from implementation-defined C behavior, such as signed right shifts and pointer comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genconf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genconf.c

Read status: complete.

Purpose: build-time generator that reads Ghostscript `.dev` module description files and emits merged configuration outputs such as `gconfig.h`, `gconfigf.h`, object lists, library lists, and linker switch lists.

Input model:
- `.dev` files contain switches like `-dev`, `-dev2`, `-include`, `-init`, `-oper`, `-ps`, `-font`, `-lib`, `-obj`, `-replace`, and other resource categories.
- `-include` recursively reads another `.dev` file, adding `.dev` if no suffix is present.
- `-replace` removes resources associated with a replaced module.

Main data structures:
- `string_item_t` records a string, source file index, and insertion index.
- `string_list_t` stores resource lists with uniqueness modes: keep all, keep first, or keep last.
- `string_pattern_t` controls output pattern formatting, uppercase conversion, and extension dropping.
- `config_t` owns all accumulated file names, file contents, replacement declarations, resource lists, and output patterns.

Main logic:
- `main` initializes lists, parses command-line switches, reads `.dev` files, and writes requested outputs.
- `read_file` loads each `.dev` file into memory and caches contents by file name.
- `read_dev` tokenizes a `.dev` file and calls `add_entry` for each resource.
- `add_entry` maps categories to generated macros such as `device_(...)`, `init_(...)`, `oper_(...)`, `psfile_(...)`, `function_type_(...)`, and `image_type_(...)`.
- `process_replaces` removes all resource entries originating from files named by `-replace`.
- `sort_uniq` sorts by string, removes duplicates according to uniqueness policy, and optionally restores insertion order.
- `write_list_pattern` expands formatted output and wraps macro-like resources in matching `#ifdef` / `#endif` guards.

Filesystem/storage relevance:
- Reads build-description files and writes generated build/config files.
- Implements build dependency flattening and resource list generation rather than runtime filesystem code.

Notable behavior and risks:
- Uses fixed-size buffers such as `MAX_STR` and unchecked `strcpy`/`strcat` in several places, relying on historical build inputs.
- `mrealloc` allocates/copies but does not free the old allocation, acceptable only because this is a short-lived generator.
- Tokenization is whitespace-based and does not implement quoting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gendev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gendev.c

Read status: complete.

Purpose: build-time tool that generates `.dev` configuration files from command-line resource arguments.

Usage model:
- Supports `-d <devfile>`, `-m <modfile>`, and `-a <modfile>` for device/module file generation or append mode.
- Supports options `-Z`, `-n`, and `-C`.
- Accepts resource category switches followed by item names.

Main logic:
- Creates or appends to `<name>.dev`.
- Emits an include guard using the output file name and current file position.
- Optionally adds the device itself when generating a device file.
- Writes generated resource macros under `#ifndef RES_SCAN`.
- For `uniq_last` resources, emits a second `RES_SCAN` pass to track the final occurrence.
- Handles categories including `dev`, `dev2`, `emulator`, `font`, `include`, `init`, `iodev`, `lib`, `obj`, `oper`, and `ps`.

Important functions:
- `add_entry` maps category/item pairs into generated macro lines.
- `write_item` emits normal resource lines with category `#ifdef` guards and uniqueness guards.
- `write_scan_item` emits `SEEN` definitions for last-occurrence detection.

Filesystem/storage relevance:
- Writes build module-description files.
- No runtime filesystem implementation.

Notable behavior and risks:
- Source comments state it does not handle `-replace` and does not merge `device` and `device2`.
- Uses fixed 80/100 byte buffers for generated strings and names.
- `main` has old-style implicit `int` declaration style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gendev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genht.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/genht.c

Read status: complete.

Purpose: build-time generator that compiles constrained PostScript halftone resource files into C data structures for Ghostscript ROM/shared read-only use.

Input format:
- Parses a restricted PostScript-like resource syntax.
- Supports `HalftoneType 5` as a prefix/resource grouping marker.
- Supports `HalftoneType 3` resources with `Width`, `Height`, and `Thresholds`.
- Decodes ASCII hex threshold data.

Main logic:
- `read_file` loads the entire resource file.
- `parse_line` trims whitespace and returns one logical line at a time.
- `parse_halftone` scans for resource names and halftone parameters, validates width/height, allocates level/bit arrays, and decodes thresholds via `s_AXD_template`.
- `write_halftone` emits static C arrays for levels and bit data plus a `gx_device_halftone_resource_t`.
- `main` writes generated C comments/includes, constructs threshold orders with `ht_order_procs_short.construct_order`, emits all resources, and writes a `gs_dht_<prefix>` accessor procedure.

Dependencies:
- Includes halftone/device headers and stream/string internals.
- Includes `gxhtbit.c`, `scantab.c`, and `sstring.c` directly to avoid a separate link step.
- Provides minimal stubs for Ghostscript structure relocation/enumeration and threshold completion.

Filesystem/storage relevance:
- Reads a halftone resource file and writes generated C.
- No runtime storage behavior.

Notable behavior and risks:
- Assumes small/simple input grammar.
- Width and height are capped at `0x4000`, but `Width * Height` is held in `uint`/`int` style variables.
- Allocations are not comprehensively freed because the process is a short-lived generator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/genht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/geninit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/geninit.c

Read status: complete.

Purpose: build-time utility that merges Ghostscript initialization PostScript files into a single PostScript file or a C byte array.

Inputs and outputs:
- Usage: `geninit [-(I|i) prefix] gs_init.ps gconfig.h gs_xinit.ps`.
- Or emits C with `-c`.
- Reads `gconfig.h` to discover `psfile_("...")` entries for `INITFILES`.

Main logic:
- `prefix_open` opens files under an optional library prefix, with Mac path translation under `__MACOS__`.
- `rl` reads lines while normalizing Unix, Mac, and DOS line endings.
- `doit` strips comments and whitespace outside string literals unless an included file is marked intact.
- `mergefile` processes special `%% Replace` directives, recursively includes named files, expands `INITFILES`, stops at `currentfile closefile`, and merges/minifies PostScript.
- `hex_string_to_binary` converts ASCII hex strings into binary object tokens for object-format sections.
- `merge_to_c` writes `const unsigned char gs_init_string[]`.
- `merge_to_ps` writes merged PostScript output.

Filesystem/storage relevance:
- Reads multiple initialization/config files and writes merged generated output.
- Handles path-prefixing and platform path translation.

Notable behavior and risks:
- Uses fixed `LINE_SIZE` of 128 for file names and lines.
- Relies on exact `psfile_("...")` formatting in generated config.
- Uses in-place mutation of line buffers while stripping comments/whitespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/geninit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ghost.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ghost.h

Read status: complete.

Purpose: minimal common interpreter header.

Contents:
- Include guard `ghost_INCLUDED`.
- Includes `gx.h` and `iref.h`.

Filesystem/storage relevance:
- No filesystem behavior. It provides common interpreter type dependencies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ghost.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp.h

Read status: complete.

Purpose: central Ghostscript interface for platform-specific routines. Implementations live in `gp_*.c` files.

Major API areas:
- Initialization and exit: `gp_init`, `gp_exit`, `gp_do_exit`.
- Error and time: `gp_strerror`, `gp_get_realtime`, `gp_get_usertime`.
- Line reading and stdin: `gp_readline_*`, `gp_stdin_read`.
- Display environment: `gp_getenv_display`.
- File constants: name-list separator, scratch prefix, null file name, current directory name, binary-mode suffixes.
- File access: `gp_open_scratch_file`, `gp_fopen`, `gp_setmode_binary`.
- Path combining: `gp_file_name_combine` plus helper callbacks for platform root/separator/current/parent semantics.
- Mac resource access: `gp_read_macresource`.
- Persistent cache: `gp_cache_insert`, `gp_cache_query`, cache type IDs.
- Printer access: `gp_open_printer`, `gp_close_printer`.
- File enumeration: `gp_enumerate_files_init`, `gp_enumerate_files_next`, `gp_enumerate_files_close`.
- Native font enumeration: `gp_enumerate_fonts_init`, `gp_enumerate_fonts_next`, `gp_enumerate_fonts_free`.

Filesystem/storage relevance:
- This is the key abstraction boundary for file naming, scratch files, printer pseudo-files, file enumeration, resource-fork access, and persistent caches.
- Platform implementations in this group fill in DOS, Windows, Mac, OS/2, OS-9, Unix-like, and stub variants.

Notable behavior:
- Comments document platform-specific semantics for roots, separators, parent/current references, and empty path items.
- The misspelled functions `gp_file_name_is_partent_allowed` and `gp_file_name_is_empty_item_meanful` are part of the declared ABI here and mirrored in implementations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfe.c

Read status: complete.

Purpose: MS-DOS file enumeration implementation for Ghostscript.

Main logic:
- Defines `file_enum_s` containing DOS find state, original and translated patterns, header length, first-time flag, and Ghostscript memory pointer.
- `gp_enumerate_files_init` copies the original pattern and builds a DOS-compatible pattern after it in the same allocation.
- Translates `*` to DOS-friendly matching and adds `*.*` when needed because DOS does not treat bare `*` as all files.
- Tracks the directory/header portion through the last `:`, `/`, or `\`.
- `gp_enumerate_files_next` calls `dos_findfirst`/`dos_findnext`, reconstructs the full returned name, removes DOS space padding, and filters with Ghostscript `string_match`.
- `gp_enumerate_files_close` frees pattern and enumerator through Ghostscript memory.

Filesystem/storage relevance:
- Implements wildcard file enumeration over DOS filesystems for the `%os%` file device layer.

Notable behavior:
- Comments note DOS wildcard limitations in directory components and backslash handling.
- Returns `~(uint)0` when enumeration is complete.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfs.c

Read status: complete.

Purpose: common filesystem routines for MS-DOS-like platforms, including DesqView/X.

Main logic:
- `gp_set_file_binary` uses DOS ioctl interrupt `0x44` to set or clear binary mode on device handles.
- `gp_setmode_binary` applies that operation to a `FILE *`.
- Defines DOS filename constants: list separator `;`, binary suffix `b`, modes `rb` and `wb`.
- Implements path-combine helper functions for DOS/Windows-style roots, separators, parent/current directory items, and empty item behavior.
- `gp_file_name_combine` delegates to shared `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Supplies DOS path syntax and binary/text mode behavior for Ghostscript file handling.

Notable behavior:
- Recognizes UNC-like network paths, absolute slash/backslash paths, and drive-letter roots.
- Treats both `/` and `\` as separators.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dosfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dvx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dvx.c

Read status: complete.

Purpose: DesqView/X-specific Ghostscript platform routines.

Main logic:
- Provides no-op `gp_init` and `gp_exit`, and `gp_do_exit` wrapping `exit`.
- `gp_strerror` delegates to C `strerror`.
- `gp_get_realtime` uses `gettimeofday` and returns seconds plus nanoseconds.
- `gp_get_usertime` approximates user time with real time.
- Persistent cache functions are stubs: insert returns `0`, query returns `-1`.
- `gp_open_printer` maps empty name or `PRN` to `stdprn`, optionally binary, otherwise opens a named file.
- `gp_close_printer` flushes `stdprn` or closes file.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides printer/file opening behavior and cache stubs for a DOS-like platform.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_dvx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_getnv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_getnv.c

Read status: complete.

Purpose: standard implementation of `gp_getenv` using the C library `getenv`.

Main logic:
- Looks up `key` with `getenv`.
- If found and output buffer is large enough, copies value, sets required length including NUL, and returns `0`.
- If found but buffer is too small, sets required length and returns `-1`.
- If missing, stores an empty string when possible, sets length to `1`, and returns `1`.

Filesystem/storage relevance:
- Environment variables commonly affect Ghostscript file search paths, temporary directories, and platform configuration.

Notable behavior:
- Expects `*plen` to be the caller-provided buffer size on input and required/actual size on output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_getnv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_iwatc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_iwatc.c

Read status: complete.

Purpose: Intel/Watcom C-specific platform routines for Ghostscript on DOS-like systems.

Main logic:
- `gp_init` initializes a private `gs_stdprn` pointer and installs a `SIGFPE` handler.
- Floating-point exceptions print “Numeric exception” and exit.
- Persistent cache functions are stubs.
- `gp_open_printer` handles `PRN`/empty printer output, including special binary handling for Watcom `stdprn`; otherwise opens a named file.
- `gp_close_printer` closes non-`stdprn` streams and resets `gs_stdprn`.
- `gp_open_scratch_file` builds a temporary filename from a prefix and temp directory, lowercases the temp path to protect `X` placeholders, appends `XXXXXX`, calls `mktemp`, and opens with `gp_fopentemp`.
- `gp_fopen` delegates to `fopen`.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Implements scratch file creation and printer file access for Watcom/DOS builds.

Notable behavior:
- Uses `mktemp`, which is inherently race-prone on modern systems.
- Uses fixed `gp_file_name_sizeof` limits and DOS path assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_iwatc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.c

Read status: complete.

Purpose: Classic Mac OS / Carbon platform support routines excluding the larger file-I/O implementation in `gp_macio.c`.

Main logic:
- Includes Classic Mac toolbox headers or Carbon.
- Defines global `HWND hwndtext` used as a DLL-instance-style identifier.
- `mygetenv` returns `NULL`.
- `gp_init`, `gp_exit`, and `gp_do_exit` provide minimal lifecycle behavior.
- Implements a `gettimeofday` shim and Ghostscript real/user time functions.
- `gp_get_usertime` approximates user time from real time and subtracts a random byte, apparently for seed variation on fast systems.
- `gp_strerror` returns `NULL`.
- Provides alternate clock helpers `gp_get_clock`, `gpp_get_clock`, `gpp_get_realtime`, and `gpp_get_usertime`.
- Persistent cache functions are stubs.
- Console/display helpers are no-ops or return `NULL`.

Filesystem/storage relevance:
- Minimal. Mac filesystem/resource work is in `gp_macio.c`.
- Cache stubs mean no persistent storage backing here.

Notable behavior:
- Contains legacy/commented code and old Mac date conversion logic.
- Error-string support is unimplemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.h

Read status: complete.

Purpose: Mac platform header placeholder.

Contents:
- Include guard `gp_mac_INCLUDED`.
- Comment states there are no special definitions for Mac OS.

Filesystem/storage relevance:
- None directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macio.c

Read status: complete.

Purpose: Classic Mac OS / Carbon file, stdio, resource, path, and font-enumeration support for Ghostscript.

Major areas:
- HFS path conversion between `FSSpec` and colon-separated Mac paths.
- Mac-specific environment behavior for `GS_LIB`.
- Redirection of Ghostscript stdin/stdout/stderr streams through the DLL callback.
- Printer/scratch/file handling.
- Mac resource fork reads.
- Mac path-combine helper semantics.
- Native font enumeration through Font Manager and FOND resources.

Main logic:
- `convertSpecToPath` walks parent directories with `PBGetCatInfoSync` and builds a colon-separated HFS path.
- `convertPathToSpec` creates an `FSSpec` from a path string.
- `getenv("GS_LIB")` builds an Application Support based Ghostscript library/font path.
- `gs_iodev_macstdio` is a pseudo IODevice that patches `%stdin`, `%stdout`, and `%stderr` open routines.
- `mac_stdin_read_process`, `mac_stdout_write_process`, and `mac_stderr_write_process` route data through `pgsdll_callback`.
- `gp_open_printer` uses a scratch file for default output or opens a named file.
- `gp_open_scratch_file` creates a temporary name, resolves the Mac temporary folder when no volume separator is present, and opens it.
- `gp_read_macresource` opens a file resource fork, loads a resource by type/id, returns its size, and optionally copies its bytes into the caller buffer.
- File enumeration is effectively unsupported: it stores the pattern and then returns no entries.
- Mac path helpers use `:` as separator, `::` for parent, and treat empty path items as meaningful.
- Font enumeration uses `FMCreateFontIterator`, `FMGetNextFont`, Font Manager metadata, and FOND resource parsing to return PostScript-ish names and paths, including `%macresource%...#sfnt+id` or `%macresource%...#POST`.

Filesystem/storage relevance:
- This is the main Mac filesystem abstraction for Ghostscript in this group.
- It covers HFS path syntax, temporary files, resource forks, and native font file/resource discovery.

Notable behavior and risks:
- Uses many fixed 256-byte buffers.
- File enumeration is declared unsupported and always ends immediately.
- `getenv("GS_LIB")` allocates a returned string and does not provide ownership clarity.
- FOND parsing directly interprets resource bytes by offset because the Carbon API deprecated the struct view.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macpoll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macpoll.c

Read status: complete.

Purpose: Mac polling/interrupt support for Ghostscript when `CHECK_INTERRUPTS` is enabled.

Main logic:
- Uses `TickCount` to throttle polling to roughly every few ticks.
- If legacy `pgsdll_callback` is installed, calls it with `GSDLL_POLL` and `hwndtext`.
- Otherwise, falls back to the newer `gs_lib_ctx->poll_fn` callback, obtaining non-GC memory context when `mem == NULL`.
- Returns the callback’s interrupt value or `0`.

Filesystem/storage relevance:
- None. This is event/poll integration.

Notable behavior:
- Comments explicitly warn that static state and the `mem == NULL` fallback are not thread-safe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macpoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mktmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mktmp.c

Read status: complete.

Purpose: replacement `mktemp` implementation for platforms that lack one.

Main logic:
- Requires the input filename to end in `XXXXXX`.
- Replaces that suffix with `AA.AAA`.
- Calls `stat` repeatedly and increments characters from the end, skipping dots and rolling `Z` back to `A`, until it finds a non-existing name.
- Returns `NULL` for invalid input or exhausted name space.

Filesystem/storage relevance:
- Generates temporary file names for platform scratch-file code.

Notable behavior:
- Name generation is race-prone because existence checking and later opening are separate.
- The suffix pattern is DOS-like (`AA.AAA`) rather than preserving six contiguous characters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mktmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdll.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdll.c

Read status: complete.

Purpose: Microsoft Windows DLL entry-point support for Ghostscript.

Main logic:
- `DllEntryPoint` checks `GetVersion` bits to detect Win32s and sets global `is_win32s`.
- Stores the DLL instance handle in global `phInstance`.
- `DllMain` delegates to `DllEntryPoint`.

Filesystem/storage relevance:
- None directly. The instance handle is used by Windows UI/resource code such as printer dialogs.

Notable behavior:
- Provides both Borland-style and Microsoft Visual C++ DLL entry points.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdos.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdos.c

Read status: complete.

Purpose: common MS-DOS platform routines.

Main logic:
- `gp_strerror` delegates to C `strerror`.
- `gp_get_realtime` uses DOS interrupt calls to read date and time, converts to seconds since January 1, 1980, and returns hundredths as nanoseconds.
- `gp_get_usertime` approximates user time with real time.
- `gp_file_is_console` uses DOS ioctl device info to detect console/device handles, with DLL-specific handling for `NULL`.
- `gp_getenv_display` returns `NULL`.
- Defines DOS scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Filesystem/storage relevance:
- Provides console detection, null device naming, scratch prefix, and time support for DOS file/printer abstractions.

Notable behavior:
- Date conversion uses hand-coded leap-year arithmetic.
- Epoch differs from Unix; comments state January 1, 1980.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mshdl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mshdl.c

Read status: complete.

Purpose: `%handle%` IODevice for MS-Windows, allowing callers to pass an existing OS file handle to Ghostscript.

Main logic:
- Defines `gs_iodev_handle` with `%handle%` prefix.
- `get_os_handle` validates that the filename suffix is all hex digits and parses it as an unsigned long.
- `mswin_handle_fopen` converts the OS handle to a C file descriptor with `_open_osfhandle`, wraps it with `fdopen`, and returns the resulting `FILE *`.
- `mswin_handle_fclose` closes the stream.

Filesystem/storage relevance:
- Bridges Ghostscript file output to externally-created Windows handles, commonly pipes created by a parent process.

Notable behavior:
- Comments note the handle-width assumption is correct for Win32 and may be wrong for Win64.
- Invalid handles map through `gs_fopen_errno_to_code(EBADF)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mshdl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msio.c

Read status: complete.

Purpose: Microsoft Windows text-window stdio integration for Ghostscript DLL-style use.

Main logic:
- Defines a pseudo IODevice `gs_iodev_wstdio` whose init patches `%stdin`, `%stdout`, and `%stderr` if the underlying file is a console.
- Replacement stream open procedures attach custom process/available callbacks and detach from ordinary `FILE *`.
- `win_std_read_process` requests input through `pgsdll_callback(GSDLL_STDIN, ...)`.
- `win_std_write_process` sends output through `pgsdll_callback(GSDLL_STDOUT, ...)`.
- `win_std_available` reports EOF/unknown availability.
- Overrides `fprintf` on Windows compiler configurations: console output is formatted into a local buffer and sent to the DLL callback; non-console files use `vfprintf`.

Filesystem/storage relevance:
- Affects standard streams and console-backed file devices.
- No filesystem enumeration or path handling.

Notable behavior:
- Uses a 1024-byte local buffer with `vsprintf` in `fprintf`, so long formatted messages can overflow in historical builds.
- The pseudo-IODevice init is described in comments as poor architecture.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mslib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mslib.c

Read status: complete.

Purpose: Microsoft Windows platform support variant for the Ghostscript graphics library rather than the interpreter.

Main logic:
- Under `CHECK_INTERRUPTS`, defines `gp_check_interrupts` to always return `0`.

Filesystem/storage relevance:
- None. It is a polling stub for library builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mspol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mspol.c

Read status: complete.

Purpose: Microsoft Windows polling support for Ghostscript interpreter builds.

Main logic:
- Under `CHECK_INTERRUPTS`, `gp_check_interrupts` uses the passed `gs_memory_t` context, or falls back to `gs_lib_ctx_get_non_gc_memory_t` when `mem == NULL`.
- If a `poll_fn` is registered in the library context, calls it with `caller_handle`.
- Returns `0` when no polling callback is available.

Filesystem/storage relevance:
- None. This is interrupt/event integration.

Notable behavior:
- Source comments call the `mem == NULL` fallback a major hack and not multithread-safe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mspol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msprn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msprn.c

Read status: complete.

Purpose: `%printer%` IODevice for MS-Windows, allowing `-sOutputFile="%printer%Printer Name"`.

Main logic:
- Defines `gs_iodev_printer` with `%printer%` prefix.
- Allocates per-device state containing a duplicated thread handle.
- `mswin_printer_fopen` validates the printer with `OpenPrinter`, creates a binary pipe, exposes the pipe write end as `FILE *`, starts a thread for the pipe read end, duplicates the thread handle, and writes the printer name into the pipe.
- `mswin_printer_thread` reads the printer name, lazily opens the Windows printer, starts a RAW print job, copies pipe data through `WritePrinter`, and ends or aborts the job.
- `mswin_printer_fclose` closes the pipe stream, waits up to 60 seconds for the print thread, closes the handle, and clears state.

Filesystem/storage relevance:
- Implements printer output as a Ghostscript file device over Windows spooler APIs.
- Uses pipes to bridge C `FILE *` output to printer APIs.

Notable behavior:
- Explicitly rejects Win32s because pipes and Win32 printers are unsupported there.
- Uses `gp_file_name_sizeof` bytes at the start of the pipe as an ad hoc printer-name message.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msprn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.c

Read status: complete.

Purpose: Microsoft Windows platform support for Ghostscript, mainly legacy printer spooling, temporary files, process pipes, and lifecycle/cache stubs.

Main logic:
- Defines global DLL/application state: `phInstance`, `is_win32s`, `szAppName`, and `win_prntmp`.
- Lifecycle functions are minimal; `gp_do_exit` calls `exit`.
- Persistent cache functions are stubs.
- `gp_open_printer` detects printer targets and writes to a scratch spool file, handles pipe targets with `popen`, otherwise opens normal files.
- `gp_close_printer` sends scratch output to the selected printer and deletes the temporary file.
- `is_spool` recognizes `\\spool` pseudo-prefixes.
- `is_printer` treats empty names, `win.ini` ports, and `\\spool` names as printers.
- `gp_printfile` chooses Win32 spooler APIs or the legacy `gs16spl.exe` path depending on Win32s and target syntax.
- `get_queues`, `get_ports`, `get_queuename`, and `get_portname` enumerate/select printer queues or ports, including dialogs and `FILE:` save selection.
- `gp_printfile_win32` copies a temporary file to a printer using `OpenPrinter`, `StartDocPrinter`, `WritePrinter`, `EndDocPrinter`, and `ClosePrinter`.
- `gp_printfile_gs16spl` launches `gs16spl.exe` for Win32s/Win16-style spooling.
- `mswin_popen` implements a write-only binary pipe to a child process using inheritable handles and `CreateProcess`.
- `gp_open_scratch_file` uses temp directory discovery, `GetTempFileName`, `CreateFile`, `_open_osfhandle`, and `fdopen`.
- `gp_fopen` delegates to `fopen`.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides Windows scratch-file creation, pipe-backed process output, printer pseudo-files, and ordinary file open behavior.
- This is a major platform file-device support implementation.

Notable behavior and risks:
- Contains legacy Win32s and `win.ini` support.
- Uses several fixed-size buffers and string concatenation.
- Temporary printer output is staged through a global filename, not thread-safe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.h

Read status: complete.

Purpose: shared Windows constants and extern declarations for C code and Windows resources.

Contents:
- Resource/control IDs for icons, spool dialog, and cancel dialog states.
- System menu constant `M_COPY_CLIP`.
- Defines `_export` away for Win32 MSVC.
- Declares `phInstance`, `szAppName`, `is_win32s`, and `is_spool`.
- Defines `DLGRETURN` as `INT_PTR` on Win64 and `BOOL` otherwise.

Filesystem/storage relevance:
- Supports Windows printer/spool UI integration but contains no implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_nsync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_nsync.c

Read status: complete.

Purpose: dummy thread/semaphore/monitor implementation for builds without real threading.

Main logic:
- Semaphores are represented as an integer count.
- `gp_semaphore_wait` fails with `gs_error_unknownerror` if the count is zero; it does not block.
- `gp_semaphore_signal` increments the count.
- Monitors store a dummy owner marker and fail if entered twice or left without ownership.
- `gp_create_thread` always returns `gs_error_unknownerror`.

Filesystem/storage relevance:
- None directly. It affects concurrency availability for any shared cache or device code compiled with this backend.

Notable behavior:
- This is intentionally not a real synchronization implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_nsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_ntfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_ntfs.c

Read status: complete.

Purpose: Win32/Windows NT filesystem support for Ghostscript.

Main logic:
- Provides binary/text mode switching via `_setmode`/`setmode`.
- Defines Windows/DOS file constants: list separator `;`, binary suffix `b`, modes `rb`/`wb`.
- Implements file enumeration with `FindFirstFile` and `FindNextFile`.
- Enumeration preprocesses patterns by removing Ghostscript backslash escapes, tracks directory head length, excludes `.`/`..` and directory entries, and returns full names.
- Cleans up with `FindClose` and Ghostscript memory free calls.
- Implements DOS/Windows path-combine helper functions for roots, separators, parent/current references, and empty item semantics.
- `gp_file_name_combine` delegates to `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Main Win32 filesystem enumeration and path-syntax layer for Ghostscript.

Notable behavior:
- Directory entries are skipped; enumeration is file-oriented.
- If a returned name is too long, it truncates/copies up to `maxlen` and returns `maxlen`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.c

Read status: complete.

Purpose: OS/2 and MS-DOS platform support for Ghostscript when compiled with GCC/EMX or IBM C.

Major areas:
- OS/2/DOS platform lifecycle and environment setup.
- File enumeration.
- Printer and spooler support.
- Scratch file creation.
- Path-combine helper semantics.
- Cache and font enumeration stubs.

Main logic:
- Provides `gp_strerror`, `gp_get_realtime`, and `gp_get_usertime`.
- `gp_file_is_console` detects DOS console via ioctl when not OS/2; OS/2 treats descriptors 0-2 as console.
- Cache functions are stubs.
- Defines path/file constants: list separator `;`, scratch prefix `gs`, null `nul`, current directory `.`, binary suffix/modes.
- `gp_enumerate_files_init` stores OS/2 pattern and path head.
- `gp_enumerate_files_next` uses `DosFindFirst`/`DosFindNext` in OS/2 mode, but in DOS mode can only return the pattern once.
- `gp_init` may reconstruct DLL environment from the OS/2 process information block, invokes `_emxload_env("GS_LOAD")`, and installs a `SIGFPE` handler.
- `gp_exit` frees reconstructed environment for EMX DLL builds.
- `gp_open_printer` handles default spool, `\\spool\queue`, pipe commands, normal files, ports, and DOS `PRN`.
- `gp_close_printer` closes/pcloses and spools/deletes temporary files for spool targets.
- `pm_find_queue` enumerates OS/2 print queues and resolves default/specific queues and drivers.
- `pm_spool` opens an OS/2 spool queue, copies a temporary file to it with `SplQmWrite`, and ends/aborts the job.
- `gp_open_scratch_file` uses `_tempnam` under IBM C or `gp_gettmpdir` + `mktemp` + `gp_fopentemp` otherwise.
- Path helpers implement DOS/Windows-like root/separator/current/parent behavior.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Full platform file, temporary-file, enumeration, pipe, and printer-spool backend for OS/2.

Notable behavior:
- Supports both OS/2 and DOS behavior paths via `isos2`.
- Uses legacy OS/2 spooler APIs and manual memory allocation with `DosAllocMem`.
- Uses `mktemp` in non-IBM-C scratch path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.h

Read status: complete.

Purpose: OS/2 printer/spool helper declarations.

Contents:
- Declares `pm_find_queue`, which lists queues, finds the default queue, or resolves a supplied queue to a driver.
- Declares `pm_spool`, which spools a file to a queue or validates a queue when filename is `NULL`.

Filesystem/storage relevance:
- Header for OS/2 printer file-device support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2pr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2pr.c

Read status: complete.

Purpose: `%printer%` IODevice implementation for OS/2.

Main logic:
- Defines `gs_iodev_printer` with `%printer%` prefix.
- Device state stores selected queue name and temporary filename.
- `os2_printer_init` allocates and zeroes device state.
- `os2_printer_fopen` validates the queue through `pm_find_queue`, reports valid queue names on failure, creates a scratch file with `gp_open_scratch_file`, and returns it as the output stream.
- `os2_printer_fclose` closes the scratch stream, spools it with `pm_spool`, and unlinks it.

Filesystem/storage relevance:
- Implements OS/2 printer output as a Ghostscript file device staged through a temporary file.

Notable behavior:
- Comments mention a pipe/thread approach was preferable but did not work reliably in Ghostscript’s second thread on OS/2.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2pr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os9.c

Read status: complete.

Purpose: OS-9/OSK-specific Ghostscript platform routines.

Main logic:
- `gp_init` installs `signalhandler` via `intercept`.
- Signal handler clears stdin errors and records interrupt/FPE state in global `interrupted`.
- `gp_do_exit` calls `exit`.
- `gp_get_realtime` uses OS-9 `_sysdate` and `_julian` to compute seconds since January 1, 1980.
- `gp_get_usertime` approximates user time with real time.
- Cache functions are stubs.
- `gp_open_printer` rejects empty names, opens `|command` through `popen`, otherwise opens a file with `rbfopen`.
- `rbfopen` opens a file and sets the `_RBF` raw/binary flag.
- `gp_close_printer` uses `pclose` for pipe targets and `fclose` otherwise.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides OS-9 printer/file opening and raw/binary file flag handling.

Notable behavior:
- `gp_setmode_binary(FILE *pfile, bool binary)` appears to reference `file->_flag` instead of `pfile->_flag`, which looks like a source-level bug unless hidden by platform macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_psync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_psync.c

Read status: complete.

Purpose: POSIX pthread-backed synchronization and thread implementation for Ghostscript.

Main logic:
- Defines `pt_semaphore_t` with count, mutex, and condition variable.
- `gp_semaphore_open/close/wait/signal` implement counting semaphore semantics using pthread mutex/cond.
- `gp_monitor_*` maps monitors to pthread mutexes.
- `gp_create_thread` allocates a closure containing the Ghostscript callback and data, initializes detached pthread attributes, and starts a detached thread.
- `gp_thread_begin_wrapper` copies the closure, frees it, invokes the callback, and returns `NULL`.

Filesystem/storage relevance:
- No direct filesystem behavior, but it provides concurrency primitives for runtime components that may include caches or devices.

Notable behavior:
- Error mapping is coarse: most pthread failures become `gs_error_ioerror`.
- Thread attributes are not explicitly destroyed after `pthread_create`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_psync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdia.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdia.c

Read status: complete.

Purpose: stdin-read implementation for platforms with unbuffered `read`.

Main logic:
- `gp_stdin_read` calls `read(fileno(f), buf, len)` directly.

Filesystem/storage relevance:
- Provides low-level unbuffered standard-input reading for file/pipe/console streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdin.c

Read status: complete.

Purpose: portable stdin-read implementation for platforms without unbuffered read support.

Main logic:
- `gp_stdin_read` uses `fread`.
- If `interactive` is nonzero, reads at most one byte.
- Otherwise reads up to `len` bytes.

Filesystem/storage relevance:
- Standard-input abstraction for portable builds.

Notable behavior:
- Comments note it is slow for stdin because interactive reads are byte-at-a-time.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_strdl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_strdl.c

Read status: complete.

Purpose: default stream-based readline implementation.

Main logic:
- `gp_readline_init` returns success without allocating state.
- `gp_readline` delegates to `sreadline`.
- `gp_readline_finit` is a no-op.

Filesystem/storage relevance:
- None directly. It supports interpreter input reading through Ghostscript streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_strdl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_sysv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_sysv.c

Read status: complete.

Purpose: compatibility routines for older System V Unix platforms that lack standard library functions.

Main logic:
- Implements `rename` by checking source existence, unlinking destination, linking source to destination, and unlinking source.
- Implements `gettimeofday` using `times`, `time`, and `HZ`, maintaining a static offset from process ticks to wall time.

Filesystem/storage relevance:
- `rename` directly affects filesystem behavior on old System V systems.
- `gettimeofday` supports time APIs used elsewhere.

Notable behavior:
- The `rename` implementation is not atomic and may briefly remove the destination before linking.
- On failure after linking, it attempts to unlink the new destination.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_sysv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifn.c

Read status: complete.

Purpose: Unix-like filename syntax helpers for Ghostscript.

Main logic:
- Defines file-list separator `:`.
- Defines no binary mode suffix and text-equivalent modes `r` and `w`.
- `gp_file_name_root` recognizes `/` as root.
- `gs_file_name_check_separator` recognizes `/` forward and backward.
- Parent is `..`; current directory is `.`.
- Separators are `/`.
- Parent references are allowed; empty path items are not meaningful.
- `gp_file_name_combine` delegates to `gp_file_name_combine_generic`.

Filesystem/storage relevance:
- Provides Unix path syntax for Ghostscript file-name normalization and combination.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifn.c -->