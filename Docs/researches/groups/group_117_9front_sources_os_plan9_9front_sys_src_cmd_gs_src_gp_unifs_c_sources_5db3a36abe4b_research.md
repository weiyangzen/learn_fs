# Group Research: group_117_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gp_unifs_c_sources_5db3a36abe4b

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifs.c

Purpose: Unix-like filesystem platform layer for Ghostscript.

Key behavior: Defines Unix defaults for scratch prefix, `/dev/null`, and current directory. `gp_open_scratch_file` builds a temporary pathname from an absolute prefix or `gp_gettmpdir`, falls back to `/tmp/`, appends `XXXXXX`, and uses `mkstemp` when available or `mktemp` plus `gp_fopentemp` otherwise. `gp_fopen` is a direct `fopen`, and `gp_setmode_binary` is a no-op.

File enumeration: Implements `gp_enumerate_files_init/next/close` using `opendir`, `readdir`, `stat`, and a GC-visible `dirstack`. It rejects overlong and NUL-containing patterns, truncates the working path after the first wildcard directory segment, walks directories depth-first, skips `.` and `..`, uses `string_match`, and returns `~(uint)0` when enumeration is exhausted or cannot start.

Dependencies and notes: Uses Ghostscript memory descriptors for `file_enum` and `dirstack`, plus `gpmisc.h` temp/path helpers. Important edge cases are `FILENAME_MAX` normalization, root-directory handling, recursive wildcard path segments, and stack cleanup on enumeration close.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unifs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix.c

Purpose: Unix-specific non-filesystem platform routines for Ghostscript.

Key behavior: `gp_init` and `gp_exit` are no-ops; `gp_do_exit` delegates to C `exit`. `gp_strerror` returns `NULL`, so callers cannot rely on platform error text here. `gp_read_macresource` is stubbed out and returns zero.

Time, display, printer: `gp_get_realtime` uses `gettimeofday`, adapting to old SVR4 signatures and converting microseconds to nanoseconds. `gp_get_usertime` either uses `times` when configured or aliases realtime. `gp_getenv_display` reads `DISPLAY`. `gp_open_printer` opens a named file with text/binary write mode and returns null for an empty name; `gp_close_printer` uses `pclose` for pipe-like names and `fclose` otherwise.

Font enumeration: `gp_enumerate_fonts_init/next/free` are stubs, returning no native font list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix_cache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix_cache.c

Purpose: Generic POSIX persistent-cache implementation for Ghostscript.

Data model: A `gp_cache_entry` records cache type, key bytes, MD5 hash, filename, payload buffer/length, dirty state, and last-used time. Cache files are named as two hex type digits plus a dot plus the 16-byte MD5 digest in hex. The index file is `gs_cache` under the cache prefix.

Path and persistence flow: `gp_cache_prefix` gets `GS_CACHE_DIR`, falls back to compile-time `GS_CACHE_DIR` or `.cache`, and expands leading `~` using `HOME`. `gp_cache_indexfilename` and `gp_cache_itempath` use `gp_file_name_combine`. `gp_cache_saveitem` writes version, key length, key, data length, and data; `gp_cache_loaditem` verifies version, key length, and full key despite locating by hash.

Public operations: `gp_cache_insert` writes the payload file, rewrites the index to update or append the entry, then replaces the old index with `rename`. `gp_cache_query` loads a matching payload, updates last-used metadata in the index, and returns the loaded length plus allocated buffer.

Dependencies and notes: Uses `malloc/free`, `fopen`, `unlink`, `rename`, `time`, Ghostscript getenv/path helpers, and `md5.h`. It assumes the cache directory and index already exist; several failure paths return without freeing all intermediate allocations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_unix_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_vms.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_vms.c

Purpose: VAX/VMS platform implementation for Ghostscript.

Platform services: Provides no-op init/exit, VMS-convention exit mapping in `gp_do_exit`, VMS time conversion from quadword system time to seconds/nanoseconds since January 1, 1980, and `DECW$DISPLAY` lookup. Persistent cache routines are unimplemented stubs.

File and printer behavior: Defines VMS filename constants, list separator `,`, null device `NLA0:`, current directory `[]`, and binary modes. `gp_open_printer` uses VMS-specific `fopen` record options for binary pass-through or text records. `gp_open_scratch_file` combines temp directory and prefix, appends `XXXXXX`, calls `mktemp`, and opens the file.

File enumeration: Wraps VMS `LIB$FIND_FILE` with descriptor-based `file_enum`. Initialization translates Ghostscript `?` wildcards to VMS `%`, strips backslash quoting, and appends `.*` for trailing `*` without an extension. `gp_enumerate_files_next` returns VMS names from `LIB$FIND_FILE` until RMS no-more-files/error, then frees enumeration state.

Path combination: Implements VMS-specific roots and separators for device/logical names, `[`/`]` directories, `.` directory separators, and `-` parent references. `gp_file_name_combine` handles roots, device-relative concatenation, bracket unclosing, and then delegates to `gp_file_name_combine_generic`.

Dependencies and notes: Depends on VMS system calls/descriptors and Ghostscript generic path helpers. Parent traversal is reported as not allowed, and empty path items are meaningful.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_vms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wgetv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wgetv.c

Purpose: MS Windows implementation of `gp_getenv`.

Key behavior: `gp_getenv` first checks the process environment. It follows the Ghostscript buffer contract: return `0` when copied, `-1` when present but buffer is too small, and `1` when missing.

Registry fallback: On Win32, excluding Win32s, it builds `Software\<gs_productfamily>\<revision>` and checks `HKEY_CURRENT_USER` then `HKEY_LOCAL_MACHINE`. `gp_getenv_registry` reads a named `REG_SZ` value and maps Windows registry return codes to the same buffer contract.

Dependencies and notes: Uses Windows registry APIs, `gscdefs.h` product metadata, and standard `getenv`. Missing values clear the caller buffer to an empty string when possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wgetv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_win32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_win32.c

Purpose: Common Win32 platform routines.

Key behavior: `gp_strerror` delegates to ANSI `strerror`. `gp_get_realtime` uses `GetSystemTime` and computes seconds/nanoseconds since January 1, 1980 in UTC. `gp_get_usertime` aliases realtime.

Console and naming: `gp_file_is_console` treats stdin/stdout/stderr file descriptors as console, with DLL-specific handling for null `FILE *`. `gp_getenv_display` returns `NULL`. It defines Windows scratch prefix `_temp_`, null device `nul`, and current directory `.`.

Dependencies and notes: Includes Ghostscript memory/error headers and `windows_.h`. This file supplies only shared Win32 basics; file enumeration, printing, and environment details live elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wsync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wsync.c

Purpose: Win32 synchronization and thread primitive implementation for Ghostscript.

Semaphores: Wraps `CreateSemaphore`, `CloseHandle`, `WaitForSingleObject`, and `ReleaseSemaphore`. `gp_semaphore_open(NULL)` reports that semaphore storage may be moved.

Monitors: Wraps Win32 `CRITICAL_SECTION` as `gp_monitor`. `gp_monitor_open(NULL)` reports that monitor storage must not be moved because critical sections are address-sensitive.

Threads: `gp_create_thread` allocates a small closure containing callback and data, starts `gp_thread_begin_wrapper` via `BEGIN_THREAD`, frees the closure in the new thread, invokes the callback, and calls `_endthread`.

Dependencies and notes: Uses `gpsync.h`, Ghostscript error codes, `windows_.h`, and `<process.h>`. Failure reporting maps Windows API failures to Ghostscript VM or unknown errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpcheck.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpcheck.h

Purpose: Interrupt-check interface for long-running Ghostscript operations.

Key behavior: Declares `gs_return_check_interrupt`. When `CHECK_INTERRUPTS` is defined, declares `gp_check_interrupts` and provides macros to process, return on, or store interrupt status. A positive interrupt result maps to `gs_error_interrupt`; negative results pass through via `gs_note_error`.

Fallback behavior: Without `CHECK_INTERRUPTS`, all interrupt macros become no-ops or return the original code. This keeps call sites portable without platform conditionals.

Dependencies and notes: The comments identify Microsoft Windows as the current platform requiring periodic user-action checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpgetenv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpgetenv.h

Purpose: Interface contract for platform-specific environment lookup.

Key behavior: Declares `gp_getenv(const char *key, char *ptr, int *plen)`. The header documents the three-way contract: found and copied returns `0`; found but too large returns `-1` and required size; missing returns `1`, clears output when possible, and sets size to 1.

Dependencies and notes: The documented buffer size includes the terminating NUL, which is important for all implementations and callers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpgetenv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.c

Purpose: Shared platform utility implementation for temp files and generic path normalization.

Temp helpers: `gp_gettmpdir` checks `TMPDIR` then `TEMP` using `gp_getenv`. `gp_fopentemp` converts stdio mode strings to `open` flags, uses `O_EXCL` with user read/write permissions, then wraps the descriptor with `fdopen`.

Path combining: `gp_file_name_combine_generic` concatenates prefix and filename, handles absolute filename roots, inserts platform separators, removes current-directory items, resolves parent-directory items when allowed, honors `no_sibling`, and returns small-buffer/cannot-handle statuses. It delegates platform-specific syntax decisions to functions such as `gp_file_name_root`, `gs_file_name_check_separator`, and `gp_file_name_is_parent`.

Other helpers: `gp_file_name_reduce` normalizes a single path by combining it with an empty suffix. `gp_file_name_is_absolute` checks for a nonzero root. `gp_file_name_parents` and `gp_file_name_cwds` compute leading parent/current-reference spans.

Dependencies and notes: This is deliberately shared across platforms; comments direct platform-specific changes into each platform’s `gp_file_name_combine` and syntax predicates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.h

Purpose: Declarations for shared platform utility routines.

Exports: Declares temp-directory lookup, exclusive temporary file open, generic path combine/reduce, absolute-path test, and leading parent/current-reference span helpers.

Contract notes: `gp_gettmpdir` follows the same return convention as `gp_getenv`. Path functions append a trailing zero byte and report `gp_file_name_combine_result`.

Dependencies and notes: The header relies on platform implementations of syntax-specific path helpers declared elsewhere in Ghostscript’s platform interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpmisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpsync.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gpsync.h

Purpose: Platform-independent interface for synchronization and thread creation.

Types and API: Defines opaque placeholder structs for `gp_semaphore` and `gp_monitor`, size queries, open/close/wait/signal or enter/leave operations, and `gp_create_thread`.

Important convention: Calling `gp_semaphore_open(NULL)` or `gp_monitor_open(NULL)` reports whether the memory manager may move the object after creation. This supports GC-aware placement of platform synchronization objects.

Dependencies and notes: Thread callbacks have type `void (*)(void *)`; platform implementations must bridge this to native thread entry APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gpsync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.c

Purpose: Main program entry point for the Ghostscript executable.

Flow: Allocates a `gs_main_instance` using `gs_malloc_init`, initializes it with command-line arguments, optionally runs compile-time `RUN_STRINGS` test strings, then calls `gs_main_run_start`.

Exit mapping: Converts interpreter return codes into process status: success for `0`, `e_Info`, and `e_Quit`; failure for `e_Fatal`; `255` for other errors. It calls `gs_to_exit_with_code` before converting `0/1` to platform `exit_OK/exit_FAILED`.

Dependencies and notes: This is a thin shell around the interpreter API in `imain*` and `iapi.h`; platform exit behavior may still be adjusted by lower-level gp routines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.mak

Purpose: Generic Ghostscript makefile included by platform-specific makefiles.

Configuration surface: Documents required platform variables such as executable names, library/cache/doc paths, third-party library source paths, shared-library toggles, devices, features, initialization behavior, band-list settings, file/stdio implementation choices, and VM/name-table options.

Build structure: Defines generated/object directories, executable/tool paths, generated configuration headers, default/clean targets, and macros for constructing `.dev` module files using `echogs`.

Generated files: Builds `devs.tr` from platform, feature, and device `.dev` lists. Builds linker/configuration traces via `genconf`. Emits `gconfigd.h` with runtime path/version constants using `echogs`.

Dependencies and notes: This file is intentionally platform-neutral and assumes platform makefiles provide command syntax macros such as compiler invocations, delete/copy commands, object suffixes, and shell/executable prefixes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs16spl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs16spl.c

Purpose: Win32s/Win16 helper program that sends a Ghostscript output file to the 16-bit Windows spooler.

Flow: `WinMain` parses command line into `port` and `filename`, creates a modeless dialog, then calls `spoolfile`. `spoolfile` opens the file, starts a 16-bit spool job with `OpenJob`/`StartSpoolPage`, streams data in 16 KiB chunks via `WriteSpool`, updates dialog progress, pumps messages, and closes or deletes the job depending on error state.

UI behavior: `SpoolDlgProc` sets the dialog title and treats cancel as an error, destroying the dialog and posting quit. On failure, the window displays an error message and waits for user dismissal.

Dependencies and notes: Uses legacy Win16 spooler APIs declared manually from print headers. It exists because Win32s lacked both direct 16-bit spooler access and implemented 32-bit spooler APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs16spl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs_dll_call.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs_dll_call.h

Purpose: Calling-convention macros for Ghostscript DLL APIs.

Platform behavior: On Windows, defines `GSDLLEXPORT` as `__declspec(dllexport)` and `GSDLLAPI`/`GSDLLCALL` as `__stdcall` unless already defined. On IBM C for OS/2, maps calling conventions to `_System`. On Mac OS, enables export pragmas.

Pointer macros: Defines `GSDLLAPIPTR` and `GSDLLCALLPTR` with compiler-specific placement of calling-convention attributes around function pointers.

Dependencies and notes: Falls back to empty macros on unsupported platforms, keeping public headers portable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gs_dll_call.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.c

Purpose: Standard Ghostscript GC-aware reference memory allocator.

Allocator state: Defines structure descriptors for `gs_ref_memory_t` and chunks, allocator procedure tables, GC status accessors, stable-memory access, root registration, and initialization via `ialloc_alloc_state`. `ialloc_solo` creates allocator/chunk storage outside the GC-managed object space while still giving it a GC-visible object header.

Allocation model: Uses chunks with object allocation growing upward from `cbot` and string allocation growing downward from `ctop`. Small objects use size-indexed freelists, large objects use a large freelist or one-object chunks, and strings can get dedicated chunks. Controlled allocators can accept externally supplied chunks and disable further acquisition.

Free/resize/consolidation: `i_free_object` finalizes objects, performs LIFO rollback when possible, frees one-object chunks, or links reusable blocks to freelists. `i_resize_object` and `i_resize_string` attempt in-place growth/shrink before allocating replacements. `ialloc_consolidate_free`, `consolidate_chunk_free`, `remove_range_from_freelist`, `trim_obj`, and `scavenge_low_free` reclaim contiguous free ranges.

Chunk management: `alloc_acquire_chunk` enforces GC/max-VM thresholds, can signal the GC, allocates raw chunk metadata/data from non-GC memory, initializes string marking/relocation tables, and links chunks in address order. `alloc_close_chunk` and `alloc_open_chunk` synchronize cached current-chunk state; `alloc_free_chunk` releases chunk data and metadata.

GC/debug support: `ialloc_gc_prepare` unlinks streams before collection. Debug builds include object/chunk/memory dump utilities and pointer-finding helpers. Allocation tracing marks space, movable/immovable state, operation kind, allocation type, and source path such as freelist, LIFO, large chunk, or lost space.

Dependencies and notes: Central to Ghostscript memory semantics and save/restore/GC interaction. Key invariants are chunk ordering, object headers preceding user pointers, accurate freelist membership, and respecting older save levels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.h

Purpose: Public/internal extensions for the standard Ghostscript allocator.

Exports: Defines `gs_memory_gc_status_t` with VM threshold, max VM, GC signal pointer/value, enabled flag, and last requested size. Declares getters/setters for GC status and VM reclaim/threshold.

Allocator lifecycle API: Declares `ialloc_alloc_state`, `ialloc_add_chunk`, `ialloc_gc_prepare`, reset helpers, allocation-limit recomputation, and free-space consolidation.

Dependencies and notes: Exposes `gs_ref_memory_t` as an incomplete type. These routines are used by interpreter memory spaces, save/restore, and GC code rather than ordinary clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.c

Purpose: Graphics-state alpha accessors.

Key behavior: `gs_setalpha` clamps a floating-point alpha to `[0,1]`, converts it to `gx_color_value`, stores it in `pgs->alpha`, and invalidates the cached device color with `gx_unset_dev_color`. `gs_currentalpha` converts the stored fixed-range alpha back to a float.

Dependencies and notes: This is deliberately tiny so alpha initialization/access can exist even without full alpha-compositing support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.h

Purpose: Header for graphics-state alpha value access.

Exports: Declares `gs_setalpha(gs_state *, floatp)` and `gs_currentalpha(const gs_state *)`.

Dependencies and notes: The comments explain the separate header exists so `gsstate.c` can initialize alpha even in builds without full alpha compositing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.c

Purpose: Alpha-compositing implementation for Ghostscript compositors and forwarding devices.

Compositor object: Defines `gs_composite_alpha_type`, creates `gs_composite_alpha_t` objects with operation/dissolve parameters, compares them by operation and dissolve delta, and serializes/deserializes them for command lists.

Device wrapper: `c_alpha_create_default_compositor` returns the original target for `composite_Copy`; otherwise it allocates a forwarding device whose color representation is chunky 8-bit color plus alpha. It forwards most operations to the target and intercepts fill/color mapping paths.

Color mapping: `dca_map_rgb_alpha_color` stores premultiplied color values with alpha in the low byte; grayscale uses luminance weights. `dca_map_color_rgb` reverses premultiplication, with special handling for zero alpha and optional `PREMULTIPLY_TOWARDS_WHITE`.

Compositing core: `composite_values` combines source and destination rows of premultiplied samples. It supports Porter-Duff style operations (`Clear`, `Copy`, `Sover`, `Dover`, `Sin`, `Dout`, `Xor`, etc.), `PlusD`, `PlusL`, `Highlight`, and floating-point `Dissolve`. It handles constant-color sources, optional first/last alpha channels, variable bits per value, and rejects operations that could create non-unity alpha when the destination lacks alpha storage.

Dependencies and notes: Uses image alpha metadata, sample load/store macros, `gx_get_bits` row conversion, and device forwarding. The implementation is explicitly simple rather than optimized; CMYK handling is noted as incomplete in fill color extraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.h

Purpose: Alpha-compositing public interface.

Exports: Defines `gs_composite_op_t` values matching `dpsNeXT.h`, including normal composite operators, `Highlight`, and `Dissolve`. Defines `gs_composite_alpha_params_t` with operation and dissolve delta. Declares `gs_create_composite_alpha`.

Dependencies and notes: Includes `gscompt.h`; operation ordering is part of the serialized/compatible interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalphac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.c

Purpose: Command-line argument list and `@file` expansion support.

Initialization and cleanup: `arg_init` sets initial `argv` traversal, expansion behavior, and file opener callback. `arg_push_memory_string` pushes an in-memory argument source, enforcing `arg_depth_max`. `arg_finit` unwinds open files and heap strings.

Parsing behavior: `arg_next` returns argv entries or tokens from nested file/string sources. For `@` files, it skips leading whitespace, supports comments beginning with `#` at line start, supports quoted whitespace only in file input, treats backslash-newline as continuation, and detects unterminated quotes or overlong commands as fatal errors.

Expansion: If `expand_ats` is true and an argument starts with `@`, `arg_next` opens that file through the configured callback, pushes it as a new source, and continues parsing recursively.

Dependencies and notes: `arg_copy` copies an argument into Ghostscript memory. The parser does not heap-copy normal returned tokens; callers must copy if they need persistence.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.h

Purpose: Data structures and API for Ghostscript command-line argument management.

Types: Defines fixed limits `arg_str_max` and `arg_depth_max`. `arg_source` represents either an open file or an in-memory string source. `arg_list` stores expansion settings, file opener callback, argv cursor, nesting depth, scratch token buffer, and source stack.

Exports: Declares initialization, memory-string push/unread, cleanup, next-argument parsing, and heap-copy helpers.

Dependencies and notes: The fixed buffer/depth design avoids dynamic allocation in the parser except for optional caller-owned pushed strings and explicit `arg_copy`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsargs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitcom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitcom.c

Purpose: Oversampled bitmap compression into alpha maps.

Key algorithm: `bits_compress_scaled` reduces an X-by-Y oversampled 1-bit source bitmap into `N` alpha bits per output pixel by counting set source bits over each cell. X/Y scale factors are powers of two from `gs_log2_scale_point`, and output depth can be 1, 2, or 4 bits.

Tables and optimization: Uses small lookup tables for bit counts, trailing/leading edge runs, and count compression from oversample count to output alpha value. It has fast all-zero/all-one source-byte paths when alignment and scaling allow.

Dropout handling: When a nonzero source count would map to zero alpha, it inspects neighboring cells above, below, left, and right to add connected runs and reduce dropout during downsampling.

Dependencies and notes: Supports optional `ALPHA_LSB_FIRST` nibble ordering. Width/height/source x are expected to align to the relevant scale factors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitmap.h

Purpose: Public client bitmap structure definitions.

Bitmap model: Documents Ghostscript bitmap storage as bit-big-endian byte sequences, with y=0 at the first scanline and no alignment assumptions for client bitmaps. Defines `gs_bitmap_id` and `gs_no_bitmap_id` for optional identity caching.

Structures: Defines basic mutable/const bitmaps, tiled bitmaps with true replication dimensions, depth-aware bitmaps with pixel depth and component count, and tiled depth-aware bitmaps.

Memory descriptors: Declares structure descriptors and macros for bitmap GC metadata, implemented elsewhere in `gspcolor.c`. The structures intentionally mirror aligned `gxbitmap.h` layouts where safe casts are possible.

Dependencies and notes: This header is for library clients; internal optimized bitmap routines use aligned gx structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.c

Purpose: Low-level bitmap fill, copy, replication, bounding-box, and plane transform operations.

Bit operations: Defines endian-specific mono masks, `bits_fill_rectangle`, and `bits_fill_rectangle_masked`, operating chunk-wise with special cases for one, two, three, or many chunks and optimized all-zero/all-one patterns.

Replication and bounds: `bits_replicate_horizontally` expands bitmap tiles in place using byte-aligned or bit-level paths; `bits_replicate_vertically` repeats scanline blocks. `bits_bounding_box` scans long-aligned raster data to find nonzero row and column extents, using nibble lookup tables for edge bits.

Plane transforms: `bits_extract_plane` extracts a component plane from interleaved pixels, with fast cases for 4-to-1 and 32-to-8 CMYK-like layouts and a generic sample macro path. `bits_expand_plane` writes a plane back into interleaved pixels, with fast 8-to-32 expansion and generic fallback.

Byte operations: `bytes_fill_rectangle` and `bytes_copy_rectangle` provide simple row-wise byte fill/copy helpers.

Dependencies and notes: Relies heavily on architecture constants, sample load/store macros, and gx bit-operation headers. Correctness depends on raster alignment assumptions called out in the individual routines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsbitops.c -->