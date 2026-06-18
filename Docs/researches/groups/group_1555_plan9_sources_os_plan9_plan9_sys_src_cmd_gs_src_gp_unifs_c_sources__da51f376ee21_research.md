# Group Research: group_1555_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gp_unifs_c_sources__da51f376ee21

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifs.c

Purpose: Implements Unix-like filesystem support routines for Ghostscript: scratch-file creation, binary/text stream handling, and wildcard file enumeration over POSIX directories.

Key interfaces: `gp_scratch_file_name_prefix`, `gp_null_file_name`, `gp_current_directory_name`, `gp_open_scratch_file`, `gp_fopen`, `gp_setmode_binary`, `gp_enumerate_files_init`, `gp_enumerate_files_next`, and `gp_enumerate_files_close`.

Control flow: scratch-file creation combines an absolute prefix or temp directory from `gp_gettmpdir`, appends a safe template, then uses `mkstemp` when available or `mktemp` plus `gp_fopentemp` otherwise. Enumeration stores the original pattern and mutable work path in GC-managed memory, opens directories lazily, matches path segments with `string_match`, recursively descends through matching directories using a `dirstack`, and unwinds/cleans state on exhaustion.

Dependencies: Uses Ghostscript memory/GC descriptors, `gp.h`, `gpmisc.h`, `gsutil.h`, POSIX `opendir/readdir/closedir/stat`, and fallback path-length handling around `FILENAME_MAX`.

Risks and notes: The `mkstemp` failure check uses `file < -1`, which will not catch normal `-1` failure. The non-`mkstemp` fallback relies on `mktemp`, though `gp_fopentemp` mitigates race/symlink risk with `O_EXCL`. Allocation failures during enumeration initialization can leak earlier allocations because the partially allocated `file_enum` is not fully cleaned before returning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unifs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix.c

Purpose: Provides Unix-specific Ghostscript platform hooks for initialization, exit, clocks, display environment, printer files, and placeholder font enumeration.

Key interfaces: `gp_init`, `gp_exit`, `gp_do_exit`, `gp_strerror`, `gp_read_macresource`, `gp_get_realtime`, `gp_get_usertime`, `gp_getenv_display`, `gp_open_printer`, `gp_close_printer`, and `gp_enumerate_fonts_*`.

Control flow: initialization and cleanup are no-ops; program termination delegates to `exit`. Real time uses `gettimeofday`, with a compatibility branch for old SVR4 signatures and validation of `tv_usec`. User time either sums `times()` counters when configured or falls back to real time. Printer open simply opens a named file in text or binary write mode, while close conditionally uses `pclose` for pipe-style names.

Dependencies: Uses Unix headers via Ghostscript wrappers, `gsexit.h`, `gp.h`, `getenv`, `fopen`, `pclose`, `times`, and `gettimeofday`.

Risks and notes: `gp_open_printer` does not actually open pipe commands even though `gp_close_printer` checks `fname[0] == '|'`; pipe opening likely belongs to another platform variant or is incomplete here. `gp_strerror` returns `NULL`, so callers must tolerate missing OS error text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix_cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix_cache.c

Purpose: Implements a generic POSIX persistent cache for Ghostscript, storing typed key/value buffers on disk and maintaining an index file.

Key interfaces: `gp_cache_insert` and `gp_cache_query`; internal helpers compute cache directory prefixes, index filenames, MD5-derived item filenames, index entries, and serialized item payloads.

Control flow: the cache directory comes from `GS_CACHE_DIR`, compiled `GS_CACHE_DIR`, or `.cache`, with leading `~` expanded against `HOME`. Each entry hashes `(type,key)` with MD5, writes payload files named as type plus hash, and rewrites the `gs_cache` index through a `+` temporary file. Query loads and validates the payload version, key length, full key bytes, data length, and data buffer allocated by caller-supplied callback.

Dependencies: Uses `gp_getenv`, `gp_file_name_combine`, `gconfigd.h`, `md5.h`, stdio, `malloc/free/strdup`, `time`, `unlink`, and `rename`.

Risks and notes: The code assumes the index file already exists and does not create the cache directory. Several error paths leak allocated strings or open files. `gp_cache_read_entry` allocates `strlen(fn)+1` but does not copy the terminating NUL. `gp_cache_loaditem` can `memcmp` a `NULL` `filekey` if malloc fails, and read/write return values are mostly ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_unix_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_vms.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_vms.c

Purpose: Provides VAX/VMS-specific Ghostscript platform support: process exit conventions, time conversion, printer/file handling, wildcard enumeration via RMS, and VMS path-combining semantics.

Key interfaces: `gp_do_exit`, `gp_get_realtime`, `gp_cache_insert`, `gp_cache_query`, `gp_getenv_display`, `gp_open_printer`, `gp_open_scratch_file`, `gp_fopen`, file enumeration functions, `gp_file_name_root`, separator/current/parent helpers, and `gp_file_name_combine`.

Control flow: VMS exit maps Ghostscript success/failure to VMS status constants. Time is computed by subtracting a VMS binary time for 1-Jan-1980 from current VMS system time. Wildcard enumeration rewrites `?` to `%`, removes backslash quoting, appends `.*` for bare `*`, then drives `LIB$FIND_FILE`. Path combining handles device/logical roots, bracketed directories, `]`, `.`, and `-` parent-like syntax before delegating difficult reduction to `gp_file_name_combine_generic`.

Dependencies: Uses VMS descriptors and system services (`SYS$BINTIM`, `SYS$GETTIM`, `LIB$SUBX`, `LIB$EDIV`, `LIB$FIND_FILE`), Ghostscript memory descriptors, and VMS-specific `fopen` record attributes.

Risks and notes: Persistent cache functions are stubs. Scratch-file creation uses `mktemp`. Some VMS path logic is highly specialized and includes comments about Ghostscript-specific extended syntax, so changes need cross-platform path regression coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_vms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wgetv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wgetv.c

Purpose: Implements Windows `gp_getenv`, combining process environment lookup with registry fallback for Ghostscript configuration values.

Key interfaces: `gp_getenv` and `gp_getenv_registry`.

Control flow: `gp_getenv` first calls C `getenv`; if found, it either copies the value or reports required buffer length. If absent on Win32, it builds a Ghostscript product/version registry key and checks `HKEY_CURRENT_USER` then `HKEY_LOCAL_MACHINE`. Missing values return 1 with an empty one-byte result contract.

Dependencies: Uses Windows registry APIs, `gscdefs.h` product family/revision globals, `getenv`, and the `gpgetenv.h` contract.

Risks and notes: Registry key and version buffers are fixed-size stack arrays. The code excludes Win32s based on `GetVersion`. It only handles string registry values expected as `REG_SZ`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wgetv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_win32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_win32.c

Purpose: Supplies common Win32 platform helpers for Ghostscript: OS error strings, time, console detection, display environment, and standard filename constants.

Key interfaces: `gp_strerror`, `gp_get_realtime`, `gp_get_usertime`, `gp_file_is_console`, `gp_getenv_display`, `gp_scratch_file_name_prefix`, `gp_null_file_name`, and `gp_current_directory_name`.

Control flow: time uses UTC `GetSystemTime` and computes seconds since 1-Jan-1980 plus millisecond nanoseconds. User time is approximated by real time. Console detection treats `NULL` differently for DLL vs non-DLL builds and otherwise considers descriptors `<=2` console streams.

Dependencies: Uses Windows API wrappers, `strerror`, `fileno`, Ghostscript types/errors, and `gp.h`.

Risks and notes: Timezone is intentionally ignored. `gp_getenv_display` returns `NULL`, so display discovery is not supported here. Console detection is descriptor-based and may not cover redirected handles perfectly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_win32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wsync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wsync.c

Purpose: Implements Win32 synchronization and threading primitives behind the portable `gpsync.h` interface.

Key interfaces: `gp_semaphore_sizeof/open/close/wait/signal`, `gp_monitor_sizeof/open/close/enter/leave`, and `gp_create_thread`.

Control flow: semaphores wrap `CreateSemaphore`, `WaitForSingleObject`, `ReleaseSemaphore`, and `CloseHandle`. Monitors wrap `CRITICAL_SECTION`. Thread creation allocates a closure, starts a wrapper with `BEGIN_THREAD`, invokes the callback, frees the closure in the thread, and terminates with `_endthread`.

Dependencies: Uses Windows synchronization APIs, `<process.h>`, Ghostscript error codes, `gpsync.h`, and `windows_.h` for compiler-specific `BEGIN_THREAD`.

Risks and notes: `gp_monitor_open(NULL)` reports monitors as fixed because critical sections must not move. A thread-start failure leaks the closure because it is freed only by the wrapper. The semaphore maximum uses `max_int`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpcheck.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpcheck.h

Purpose: Defines the portable interrupt-check interface for long-running Ghostscript operations.

Key interfaces: `gs_return_check_interrupt`, optional `gp_check_interrupts`, and macros `process_interrupts`, `return_if_interrupt`, `return_check_interrupt`, and `set_code_on_interrupt`.

Behavior: When `CHECK_INTERRUPTS` is defined, callers periodically invoke platform checks and map positive interrupt results to `gs_error_interrupt`; otherwise all macros compile to no-ops or direct return of the supplied code.

Dependencies: Expects `gs_memory_t`, Ghostscript error constants, and `gs_note_error`.

Risks and notes: Correctness depends on long-running loops calling these macros consistently. Platforms without `CHECK_INTERRUPTS` cannot asynchronously interrupt through this mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpgetenv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpgetenv.h

Purpose: Declares the platform-specific `gp_getenv` routine and documents its buffer-size contract.

Key interface: `int gp_getenv(const char *key, char *ptr, int *plen)`.

Behavior: Missing keys return 1, write an empty string when possible, and set required length to 1. Present keys return 0 if the value plus terminator fits, or -1 with the required size if it does not fit.

Dependencies: Included by platform and miscellaneous code that needs consistent environment lookup semantics.

Risks and notes: Callers must treat `*plen` as buffer capacity on input and required/actual storage size on output, including the terminating NUL.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpgetenv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.c

Purpose: Provides generic platform support helpers shared by Ghostscript `gp_` implementations: temporary directory lookup, safe temp-file opening, and portable pathname combination/reduction.

Key interfaces: `gp_gettmpdir`, `gp_fopentemp`, `gp_file_name_combine_generic`, `gp_file_name_reduce`, `gp_file_name_is_absolute`, `gp_file_name_parents`, and `gp_file_name_cwds`.

Control flow: temp lookup checks `TMPDIR` then `TEMP` using the `gp_getenv` contract. `gp_fopentemp` parses stdio mode flags into `open` flags and uses `O_EXCL` plus user-only permissions before `fdopen`. Path combination walks prefix and filename components with platform-provided root/separator/current/parent hooks, collapses current and parent references when allowed, handles buffer-size reporting, and appends a NUL.

Dependencies: Relies on platform-specific functions from `gp.h` such as `gp_file_name_root`, separator predicates, current/parent rules, and `gp_file_name_combine`.

Risks and notes: The path reducer is shared across platforms and intentionally delegates syntax details. `gp_fopentemp` is safer than `mktemp`, but callers still must provide a unique name template.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.h

Purpose: Declares shared platform utility functions implemented in `gpmisc.c`.

Key interfaces: `gp_gettmpdir`, `gp_fopentemp`, `gp_file_name_combine_generic`, `gp_file_name_reduce`, `gp_file_name_is_absolute`, `gp_file_name_parents`, and `gp_file_name_cwds`.

Integration: Included by platform files such as Unix-like and VMS implementations to share temporary-file and path-combining behavior.

Risks and notes: The header exposes `gp_file_name_combine_generic`, but comments explicitly direct platform-specific changes to the platform wrapper rather than the generic routine.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpsync.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpsync.h

Purpose: Defines Ghostscript’s portable synchronization and thread-creation abstraction.

Key interfaces: opaque storage structs `gp_semaphore` and `gp_monitor`; size/open/close/wait/signal/enter/leave functions; `gp_thread_creation_callback_t`; and `gp_create_thread`.

Behavior: Size functions tell callers how much platform-specific storage to allocate. Passing `NULL` to open probes whether the object may be moved by the memory manager.

Dependencies: Implemented by platform files such as `gp_wsync.c`.

Risks and notes: The dummy structs are placeholders, so users must allocate storage based on runtime `sizeof` functions rather than C `sizeof(gp_semaphore)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpsync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.c

Purpose: Defines the Ghostscript executable `main`.

Key interface: `main(int argc, char *argv[])`.

Control flow: allocates a `gs_main_instance` using `gs_malloc_init`, initializes it with command-line arguments, optionally runs compiled test strings when `RUN_STRINGS` is enabled, starts interpretation, maps interpreter status to process exit status, calls `gs_to_exit_with_code`, and returns platform exit constants for success/failure.

Dependencies: Uses interpreter main APIs from `imain*`, `iapi`, `iminst`, error constants, and `gsmalloc`.

Risks and notes: There is no check that `gs_main_alloc_instance` succeeds before use. Exit-code mapping distinguishes normal/info/quit, fatal, and other errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.mak

Purpose: Generic Ghostscript makefile fragment included by platform-specific makefiles.

Key definitions: documents required platform variables, normalizes generated/object directories for bundled libraries, defines executable and auxiliary tool paths, declares generated headers, and builds generated `.dev`, `ld.tr`, `obj.tr`, and `gconfigd.h` files.

Control flow: `all/default` depend on `$(GS_XE)`. `clean`, `mostlyclean`, and `config-clean` remove generated objects, devices, config headers, helper executables, and temporary files. Device and feature lists are assembled into `devs.tr` using `echogs`; `genconf` turns those into configuration/linker/object tables; `gconfigd.h` records runtime defaults such as library paths, cache dir, doc dir, init file, revision, and revision date.

Dependencies: Requires platform makefiles to define compiler/linker/tool commands, paths, devices, features, third-party source locations, and deletion/copy utilities. Depends heavily on `echogs`, `genconf`, and generated `.dev` files.

Risks and notes: Comments mark some clean rules as not subsystem-specific. Many feature/device lists are spread over numbered variables, so platform makefiles must maintain ordering and line-length constraints carefully.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs16spl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs16spl.c

Purpose: Win32s/Win16 helper application that sends Ghostscript printer output files to the 16-bit Windows spooler.

Key interfaces: `spoolfile`, `SpoolDlgProc`, `init_window`, and `WinMain`.

Control flow: parses command-line `port filename`, creates a modeless dialog, opens the file, opens a spool job, starts a spool page, streams the file in 16 KiB chunks with progress UI updates, pumps window messages, and either closes or deletes the spool job depending on errors/cancel.

Dependencies: Uses Win16 spooler APIs (`OpenJob`, `WriteSpool`, etc.), Windows dialog/message APIs, and C stdio.

Risks and notes: Command-line parsing is space-delimited and does not support quoted filenames. Global state (`error`, `hJob`, buffers, window handle) is used throughout. Error handling reports only coarse messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs16spl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs_dll_call.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs_dll_call.h

Purpose: Defines portable DLL export and calling-convention macros for Ghostscript public APIs.

Key macros: `GSDLLEXPORT`, `GSDLLAPI`, `GSDLLCALL`, `GSDLLAPIPTR`, and `GSDLLCALLPTR`.

Behavior: Windows builds default to `__declspec(dllexport)` and `__stdcall`; OS/2 IBM C builds use `_System`; MacOS enables pragma export; all other platforms default to empty calling-convention/export macros.

Dependencies: Consumed by public headers that must expose stable ABI declarations across Windows, OS/2, MacOS, and generic C platforms.

Risks and notes: Function pointer macro spelling differs for IBM C vs other compilers, which is important for ABI-correct typedefs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs_dll_call.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.c

Purpose: Implements Ghostscript’s standard reference-aware memory allocator, including object/string allocation, freelists, chunk management, GC status integration, roots, and debug dumping.

Key interfaces: `gs_ref_memory_procs`, `ialloc_alloc_state`, `ialloc_add_chunk`, `ialloc_gc_prepare`, `ialloc_reset`, `ialloc_reset_free`, `ialloc_set_limit`, `ialloc_consolidate_free`, chunk helpers (`alloc_link_chunk`, `alloc_init_chunk`, `alloc_close_chunk`, `alloc_open_chunk`, `alloc_unlink_chunk`, `alloc_free_chunk`, `chunk_locate_ptr`), and debug helpers under `DEBUG`.

Control flow: allocator state is allocated as a solo object with a manually built header. Small objects use size-class freelists, large free objects use a large freelist, normal objects allocate upward from chunk bottom, and strings allocate downward from chunk top. Large or immovable allocations get dedicated chunks. Freeing finalizes objects, reclaims LIFO top objects, puts reusable objects on freelists, frees dedicated chunks when possible, or accounts lost space. Consolidation scans chunks for adjacent free objects and whole-free chunks. GC status computes limits from `max_vm`, `vm_threshold`, previous status, and signal fields.

Dependencies: Deeply tied to Ghostscript GC/structure descriptors (`gsstruct.h`, `gxalloc.h`), raw memory, stream lists, save/restore state, object headers, string mark/relocation tables, and debug infrastructure.

Risks and notes: This is allocator core code with many pointer and size invariants. Controlled-memory behavior differs from normal GC memory. Some debug paths return instead of aborting on allocator corruption. Integer overflow checks exist in key places but callers and structure descriptors must still provide sane sizes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.h

Purpose: Declares extensions and internal hooks for the standard Ghostscript allocator.

Key interfaces: `gs_memory_gc_status_t`, GC status getters/setters, VM threshold/reclaim setters, allocator-state creation, controlled-chunk addition, GC preparation, reset functions, allocation-limit setup, and free-space consolidation.

Integration: Used by allocator users, GC, save/restore logic, and subsystems that need to adjust VM behavior.

Risks and notes: Exposes internal allocator lifecycle functions; misuse can break chunk/freelist/GC invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.c

Purpose: Implements graphics-state alpha accessors.

Key interfaces: `gs_setalpha` and `gs_currentalpha`.

Control flow: `gs_setalpha` clamps a floating alpha to [0,1], converts it to `gx_color_value`, stores it in the graphics state, and invalidates the current device color. `gs_currentalpha` converts the stored integer alpha back to float.

Dependencies: Uses `gsalpha.h`, `gxdcolor.h`, `gzstate.h`, and `gx_max_color_value`.

Risks and notes: Alpha change correctly unsets cached device color; callers relying on cached colors must expect recomputation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.h

Purpose: Public API header for reading and setting the graphics-state alpha value.

Key interfaces: `gs_setalpha(gs_state *, floatp)` and `gs_currentalpha(const gs_state *)`.

Integration: Kept small so state initialization code can include alpha access even in builds without full alpha compositing support.

Risks and notes: Does not define `gs_state`; it assumes surrounding Ghostscript headers provide the type.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.c

Purpose: Implements Ghostscript alpha-compositing objects, default compositor device, color packing/unpacking, rectangle compositing, and the per-pixel compositing operation engine.

Key interfaces: `gs_composite_alpha_type`, `gs_create_composite_alpha`, compositor serialization/deserialization helpers, device procedures for alpha compositor forwarding, and `composite_values`.

Control flow: composite objects store operation and optional dissolve delta. `composite_Copy` bypasses wrapping; other ops create a forwarding device that reads target rows into standard chunky alpha-capable form, composites a constant fill source over destination rows via `composite_values`, then writes changed rows back. Color mapping uses premultiplied alpha. `composite_values` handles alpha-first/alpha-last/no-alpha layouts, constant or data-backed sources, bit depths, and operators such as Clear, Copy, source/destination over/in/out/atop, XOR, PlusD, PlusL, Highlight, and Dissolve.

Dependencies: Uses Ghostscript compositor/device framework, `gxgetbit` sample load/store macros, `gxalpha`, `gxcomp`, `gxlum`, image alpha enums, and reference-counted allocation.

Risks and notes: Comments mark implementation as simple and inefficient. Some device operations (`copy_mono`, `copy_color`, `copy_alpha`) temporarily fall back to defaults. Fill path has an explicit “doesn't handle CMYK” note for extracting constant RGBA values, even though depth selection includes a CMYK case.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.h

Purpose: Declares the alpha-compositing API and operation enum.

Key interfaces: `gs_composite_op_t`, `gs_composite_alpha_params_t`, and `gs_create_composite_alpha`.

Behavior: Operation values are fixed to match NeXT Display PostScript definitions; range macros identify normal composite, rectangle-only highlight, and dissolve extension limits.

Dependencies: Includes `gscompt.h` for the generic compositor type.

Risks and notes: Enum numeric compatibility is part of the interface contract, so reordering would break serialized/compositor semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalphac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.c

Purpose: Implements Ghostscript command-line argument list parsing with nested `@` file expansion.

Key interfaces: `arg_init`, `arg_push_memory_string`, `arg_finit`, `arg_next`, and `arg_copy`.

Control flow: initialization points at `argv[1]` and enables `@` expansion. Sources can be argv, files, or pushed memory strings. `arg_next` reads tokens, skips whitespace, supports comments beginning with `#` at line start in `@` files, supports quote-protected whitespace in `@` files, treats backslash-newline as continuation, expands leading `@` by opening another file, and enforces max argument length/depth. Cleanup closes open files and frees owned memory strings.

Dependencies: Uses Ghostscript memory allocation, error constants, stdio, ctype, and caller-supplied `arg_fopen`.

Risks and notes: Arguments longer than 2048 bytes or nesting deeper than 10 levels are fatal. Quoting is only honored for file-backed sources, not raw argv.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.h

Purpose: Declares command-line argument parsing structures and functions.

Key interfaces: `arg_str_max`, `arg_depth_max`, `arg_source`, `arg_list`, `arg_init`, `arg_push_memory_string`, `arg_push_string`, `arg_finit`, `arg_next`, and `arg_copy`.

Integration: Used by Ghostscript startup code to manage argv plus nested `@` files without dynamic parser state except optional pushed strings.

Risks and notes: Fixed-size `cstr` and source stack define hard limits by design.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsargs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitcom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitcom.c

Purpose: Compresses oversampled 1-bit bitmaps into lower-resolution alpha maps by counting set bits.

Key interface: `bits_compress_scaled`.

Control flow: lookup tables count half-byte bits, edge-adjacent bits, and map counts from oversampling factors to 1/2/4-bit alpha values. The main loop walks scaled source cells, fast-paths all-zero and all-one aligned source bytes, otherwise counts set bits over X/Y oversampling cells, optionally adds adjacent-cell evidence to reduce dropouts, clamps to maximum count, and packs alpha output.

Dependencies: Uses `gs_log2_scale_point`, `gsbitops.h`, debug logging, byte-oriented bitmap layout, and optional `ALPHA_LSB_FIRST`.

Risks and notes: Supports X/Y scale factors 1, 2, or 4 and output bits 1, 2, or 4. In-place compression is only safe when output bits do not exceed X oversampling. Comments note LSB-first mode is specialized and does not interact well with the rest of the code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitmap.h

Purpose: Defines public/client bitmap structures for Ghostscript APIs that do not require aligned bitmap data.

Key interfaces: `gs_bitmap_id`, `gs_no_bitmap_id`, `gs_bitmap`, `gs_const_bitmap`, `gs_tile_bitmap`, `gs_const_tile_bitmap`, `gs_depth_bitmap`, `gs_const_depth_bitmap`, `gs_tile_depth_bitmap`, `gs_const_tile_depth_bitmap`, and structure descriptor declaration/definition macros.

Behavior: Bitmaps are bit-big-endian byte sequences with y=0 first. Tile bitmaps record true replicated dimensions. Depth variants add bits-per-sample and component count for interleaved data. Structure descriptors are declared here but implemented through macros expected in `gspcolor.c`.

Dependencies: Uses `gsstype.h`, `gs_id`, `gs_int_point`, and Ghostscript structure descriptor macros.

Risks and notes: Comments warn that core aligned bitmap structures in `gxbitmap.h` have identical contents but stricter alignment assumptions; casting unaligned data to aligned structures is only safe when alignment is known.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.c

Purpose: Implements bitmap bit/byte operations: monochrome rectangle fill, masked fill, horizontal/vertical replication, bounding-box detection, plane extraction/expansion, and byte rectangle fill/copy.

Key interfaces: `mono_copy_masks`, `mono_fill_masks`, `bits_fill_rectangle`, `bits_fill_rectangle_masked`, `bits_replicate_horizontally`, `bits_replicate_vertically`, `bits_bounding_box`, `bits_extract_plane`, `bits_expand_plane`, `bytes_fill_rectangle`, and `bytes_copy_rectangle`.

Control flow: bit fills align to machine chunks and specialize one-, two-, three-, and many-chunk spans. Replication doubles/copies bitmap rows where byte-aligned and uses bit placement otherwise. Bounding-box detection skips blank rows and scans left/right edges by longs with endian-specific bit subdivision. Plane extraction/expansion use fast cases for common CMYK-style 4-to-1 and 32-to-8 / 8-to-32 operations, otherwise fall back to generic sample load/store macros.

Dependencies: Uses Ghostscript bit tables, endian/word-size architecture macros, sample access macros from `gxbitops.h`, color-index types, and memory/string routines.

Risks and notes: Several algorithms depend on raster alignment assumptions, especially bounding-box scanning by `ulong`. Horizontal replication comments call the current algorithm inefficient. Fast paths are architecture-sensitive and need endian coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsbitops.c -->