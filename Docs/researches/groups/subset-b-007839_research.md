# Research: subset-b-007839

Grouped research for the OrangeFS files listed in work item `subset-b-007839`. Each section is source-tree-aligned and bounded for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.c

Purpose: Implements small support routines for the OrangeFS Windows client test programs: path generation, zero-byte file creation, and standardized result/performance reporting.

Important APIs/functions: `quickcat()` allocates and concatenates two strings. `randdir()` and `randfile()` normalize a root path with `SLASH_CHAR`/`SLASH_STR`, append randomized names, and return caller-owned strings. `quick_create()` creates an empty file via `fopen(..., "w")`. `report_error()`, `report_result()`, and `report_perf()` route formatted messages to console and/or a report file according to `global_options.report_flags`.

Control flow: Reporting is synchronous and simple. `report_result()` compares `actual_code` to `expected_code` using the requested operator, constructs a line with test name, subtest, expectation, expected code, actual code, and `OK`/`NOT_OK`, then writes to enabled sinks.

State/persistence: No durable state besides files created by `quick_create()` and output appended through `freport`. All generated path strings are heap-allocated and must be freed by callers.

Dependencies/integration: Includes `test-support.h` for constants and `timer.h` though this file does not call timer functions. Integrates with the broader client-test framework through the shared `global_options` struct.

Risks: `quickcat()` does not check `malloc()` before `sprintf()`. Random name formatting uses fixed 16-byte buffers and unseeded/global `rand()`. `report_result()` lacks a default case if `code_operation` is invalid, leaving `comp` undefined. `_snprintf()` truncation handling falls back to a fixed overflow message.

Test signals: Exercise all report flags, each comparison operator, report file flushing, null roots in `randdir()`/`randfile()`, and creation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.h

Purpose: Declares the shared client-test support interface and cross-platform compatibility macros for Windows-style test code.

Important APIs/types: `global_options` carries `root_dir`, `tab_file`, filesystem selector, output flags, and report stream. Constants define fatal sentinel `CODE_FATAL`, expected result enums, comparison operation indexes, and output sinks. Function prototypes cover string/path helpers, file creation, error/result/performance reporting.

Control flow: This header does not implement behavior, but it defines the operation index contract consumed by `test-support.c` and test modules.

State/persistence: The only state shape is `global_options`, whose `freport` pointer is used by report functions to persist logs.

Dependencies/integration: On non-Windows builds it maps `_rmdir`, `_mkdir`, `_strdup`, `_unlink`, `_stricmp`, `_stat`, and `_snprintf` to POSIX equivalents, and defines slash constants. It expects `FILE` to be visible through included standard headers in consumers.

Risks: The include guard name `__TESTS_H` is generic. Function prototypes use mutable `char *` for some input strings even when implementations do not modify them. The non-Windows compatibility macros may hide signature differences, especially `_mkdir(dir)` expanding to `mkdir(dir, 0777)`.

Test signals: Compile both Windows and POSIX client-test paths, and verify operation constants still match the `ops[]` array order in `test-support.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-test.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/test-test.c

Purpose: Provides a minimal self-test/test-harness smoke test named `test_test()`.

Important APIs/functions: `test_test(global_options *options, int fatal)` calls `report_result(options, "test-test", "main", RESULT_SUCCESS, 0, OPER_EQUAL, 0)` and returns success.

Control flow: There is no branching. The test always records one successful result and returns `0`.

State/persistence: The only externally visible effect is the report line written through `report_result()` to console and/or file according to `options`.

Dependencies/integration: Includes `test-support.h` and is intended to be discovered/called by the client test runner as one of many test modules.

Risks: The `fatal` parameter is unused, so this test cannot exercise fatal-mode behavior. It does not validate that reporting actually succeeded because `report_result()` has no return value.

Test signals: Useful as a harness sanity check: if this test does not emit one `OK`, the test runner or report configuration is broken.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/test-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/thread.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/thread.c

Purpose: Implements Win32 thread waiting helpers for the client-test framework.

Important APIs/functions: `thread_wait()` wraps `WaitForSingleObject()`. `thread_wait_multiple()` wraps `WaitForMultipleObjects()`. `get_thread_exit_code()` wraps `GetExitCodeThread()`. A portable `thread_create()` implementation is present but commented out.

Control flow: Each wait helper forwards the input handle(s) and timeout to the Win32 API. On `WAIT_FAILED`, it returns the negated `GetLastError()` value; otherwise it returns the Win32 wait status.

State/persistence: No persistent state. It operates on caller-owned `uintptr_t` handles.

Dependencies/integration: Compiled only under `WIN32`; includes `<Windows.h>` and `thread.h`. `thread.h` exposes status constants such as `THREAD_WAIT_TIMEOUT` and `THREAD_WAIT_INFINITE`.

Risks: Casting `uintptr_t *` to `HANDLE *` assumes compatible representation and alignment. `get_thread_exit_code()` returns Win32 boolean success/failure rather than normalizing errors like the wait helpers. The commented-out creation routine suggests ownership/closing of handles may be handled elsewhere or incomplete.

Test signals: Use real thread handles, timeout cases, signaled cases, `WAIT_FAILED` invalid handles, and multiple-wait all/any paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/thread.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/thread.h

Purpose: Declares Win32-only thread wait helpers and constants for the client-test code.

Important APIs/types: Defines `THREAD_WAIT_SIGNALED`, `THREAD_WAIT_TIMEOUT`, and `THREAD_WAIT_INFINITE`, then declares `thread_wait()`, `thread_wait_multiple()`, and `get_thread_exit_code()`. The thread creation prototype is commented out.

Control flow: No implementation, but consumers rely on these constants matching Win32 `WAIT_*` values.

State/persistence: None.

Dependencies/integration: The declarations are guarded by `#ifdef WIN32`; non-Windows consumers see only the include guard. The prototypes use `uintptr_t`, so callers must include a header that defines it before or through this header.

Risks: Missing explicit `<stdint.h>`/`<stdint>` include for `uintptr_t`. The disabled `thread_create()` API means callers must obtain handles by some other means.

Test signals: Compile Windows client tests with strict include ordering to ensure `uintptr_t` is available, and validate constants against Win32 wait return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/timer.c -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/timer.c

Purpose: Provides elapsed-time measurement helpers for client tests on Windows and POSIX.

Important APIs/functions: On Windows, `timer_start()` returns a `QueryPerformanceCounter()` tick value and `timer_elapsed()` converts the difference to seconds using `QueryPerformanceFrequency()`. On POSIX, `timer_start(struct timeval *)` stores `gettimeofday()`, and `timer_elapsed(struct timeval *)` computes wall-clock seconds.

Control flow: Platform-specific compilation selects one signature set. Error handling returns `0` seconds/ticks when Windows high-resolution counter calls fail.

State/persistence: No global state; callers hold the start timestamp.

Dependencies/integration: Paired with `timer.h`. Used by performance-oriented client tests and by report helpers through `report_perf()` formatting conventions.

Risks: POSIX timing uses wall-clock time, so clock adjustments can skew elapsed values. Windows path recomputes frequency on every elapsed call. Failure is indistinguishable from true zero elapsed time.

Test signals: Verify monotonic positive elapsed values after sleeps on both platforms and format output through `report_perf()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/timer.h -->
# sources/distributed-fs/orangefs/src/client/windows/client-test/timer.h

Purpose: Declares platform-specific timer helper signatures.

Important APIs/types: Windows exports `unsigned __int64 timer_start()` and `double timer_elapsed(unsigned __int64 start)`. POSIX includes `<sys/time.h>` and exports `void timer_start(struct timeval *start)` plus `double timer_elapsed(struct timeval *start)`.

Control flow/state: Header-only declarations; the API shape changes by platform instead of hiding timestamp storage behind one type.

Dependencies/integration: Included by client-test timing code and `test-support.c`.

Risks: The header has no include guard, so repeated inclusion is tolerated only because it contains declarations but is still non-ideal. Cross-platform call sites need conditional code because function signatures differ.

Test signals: Build on Windows and POSIX with `-Wmissing-prototypes`/similar warnings to catch signature mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/windows/client-test/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/dotconf.c -->
# sources/distributed-fs/orangefs/src/common/dotconf/dotconf.c

Purpose: Implements the bundled dot.conf configuration parser used by OrangeFS. It opens config files, reads logical lines, parses typed command arguments, applies defaults, dispatches callbacks, and supports internal `Include`/`IncludePath` directives with wildcard expansion.

Important APIs/functions: `PINT_dotconf_create()` allocates a `configfile_t`, opens the input, registers built-in and caller options, and selects case-sensitive or case-insensitive comparison. `PINT_dotconf_command_loop()` and `_until_error()` read lines and call `PINT_dotconf_handle_command()`. `PINT_dotconf_set_command()` populates `command_t` for `ARG_TOGGLE`, `ARG_INT`, `ARG_STR`, `ARG_LIST`, `ARG_NAME`, `ARG_RAW`, and `ARG_NONE`. `PINT_dotconf_read_arg()` handles quotes, backslash escaping, inline comments, and environment substitution. Include handling is split across `dotconf_cb_include()`, `dotconf_cb_includepath()`, wildcard discovery, `PINT_dotconf_handle_star()`, and `PINT_dotconf_handle_question_mark()`.

Control flow: The parser loops over physical lines via `fgets()`, joins backslash-continued lines, skips blank/comment lines, extracts the first token into a static option-name buffer, searches registered option tables, optionally applies an `ARG_NAME` fallback, invokes context checking, then invokes the option callback. Include callbacks recursively create a child parser, copy later option tables and callbacks, parse included files, and clean up.

State/persistence: `configfile_t` stores stream, filename, line number, flags, include path, registered option-table pointers, and callback pointers. The parser has a file-static `name` buffer for the current option. It does not persist settings itself; caller callbacks own configuration state.

Dependencies/integration: Uses POSIX/Win32 filesystem APIs for access and directory scanning, `pvfs2-internal.h`, and the public declarations in `dotconf.h`. `module.mk.in` adds it to library and server sources.

Risks: Fixed-size buffers dominate (`CFG_BUFSIZE`, `CFG_MAX_VALUE`, `CFG_MAX_FILENAME`, `CFG_VALUES`). Recursive includes have no explicit cycle/depth guard. Some realloc calls assign/check incorrectly in wildcard handlers. `PINT_dotconf_substitute_env()` can advance output pointers by full environment value length even when `strncat()` truncates. The static `name` buffer makes parsing state process-global and not reentrant. `id`/line reporting paths often warn and continue, so callers need strict error handlers if malformed config should fail.

Test signals: Cover quote/escape parsing, inline comment flags, `${VAR:-default}` substitution, here-docs, defaults, unknown options, context rejection, nested includes, wildcard includes on POSIX and Windows, and include-path environment override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/dotconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/dotconf.h -->
# sources/distributed-fs/orangefs/src/common/dotconf/dotconf.h

Purpose: Public interface and data model for the OrangeFS-bundled dot.conf parser.

Important APIs/types: Defines parser limits, option type constants, runtime flags, error codes, logging levels, callback typedefs, and macros for option-table termination and callback declarations. `configfile_t` describes parser state and registered options. `configoption_t` describes one option name, type, callback, auxiliary info, context mask, and default value. `command_t` carries parsed command name, option descriptor, typed data, arg list/count, error bit, and context pointers.

Control flow contract: Applications create a parser with `PINT_dotconf_create()`, optionally register callbacks/options, run `PINT_dotconf_command_loop()` or `_until_error()`, and call `PINT_dotconf_cleanup()`. Callback return strings become parser errors.

State/persistence: The header exposes many `configfile_t` fields as read-only by convention, not type-enforced. Parsed arguments in `command_t` are transient and freed after callback invocation.

Dependencies/integration: C/C++ compatible with `extern "C"`. Includes `stdio.h` for `FILE *` and optionally syslog constants. Integrated into OrangeFS config consumers through `PINT_`-prefixed parser APIs.

Risks: Struct internals are public, so consumers can accidentally depend on layout. Parser limits are compile-time constants. `FUNC_ERRORHANDLER` macro uses `long dc_errno` while typedef uses `unsigned long`, a small signature inconsistency.

Test signals: Compile C and C++ consumers, validate option-table termination macros, and test every option type against callback-visible `command_t` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/dotconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/dotconf/module.mk.in

Purpose: Build-fragment registration for the dotconf parser.

Important build variables: Sets `DIR := src/common/dotconf`, then appends `$(DIR)/dotconf.c` to `LIBSRC` and `SERVERSRC`.

Control flow/state: Makefile fragment only; it contributes source paths to higher-level build aggregation.

Dependencies/integration: Ensures the parser is linked into OrangeFS common library and server builds.

Risks: Does not add headers explicitly, relying on normal dependency scanning. Client or BMI builds that need dotconf would need separate source-list inclusion.

Test signals: Configure/build targets that consume `LIBSRC` and `SERVERSRC`, then confirm `dotconf.c` is compiled once per target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/dotconf/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/debug.h -->
# sources/distributed-fs/orangefs/src/common/events/debug.h

Purpose: Tiny debug-print macro layer for the TAU event tracing code.

Important APIs/macros: Defines `PFX` as `TAU_NAME`. With `TAU_DEBUG`, `dbg()` and `info()` print prefixed messages; otherwise they compile to empty `do {} while (0)` blocks. `err()` and `warn()` always print prefixed error/warning messages.

Control flow/state: No state; compile-time macro selection controls emission.

Dependencies/integration: Requires including code to define `TAU_NAME` and include/declare `printf()`. Used by `pvfs_tau_api.c`.

Risks: Macro uses GNU variadic syntax `arg...`, which is not strict ISO C/C++. Always-on `err()`/`warn()` write to stdout via `printf()`, not stderr or OrangeFS gossip logging.

Test signals: Compile TAU event code with and without `TAU_DEBUG`, and verify format strings compile in C++ mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_api.h -->
# sources/distributed-fs/orangefs/src/common/events/fmt_api.h

Purpose: Declares shared TAU trace-format helper structures and global variables used by the PVFS/TAU event API.

Important APIs/types: Defines thread/event/string limits, `TAU_Log_get_event_number()`, `Ttf_closed_event_def` with start/end `ff_format` parsers and event IDs, and `Ttf_thread_bundle` with event table, TAU file handle, event counters, scratch buffer, and scratch position. Declares `g_t_bundles`, `g_pid`, `g_traceloc`, `g_filepfx`, and `g_defbufsz`.

Control flow contract: Event definitions are parsed into `ff_format` objects, copied into per-thread bundles, and used to encode varargs into fixed scratch storage before writing TAU events.

State/persistence: Exposes global process and per-thread trace state. Each thread bundle owns its event table and TAU output handle.

Dependencies/integration: Includes TAU writer headers and `fmt_fsm.h`; it is C++-style despite `.h` extension, with constructors and assignment operators.

Risks: Duplicates structure definitions also present in `pvfs_tau_api.c`, which can drift. `strncpy()` calls do not always force termination when inputs are long. Scratch buffer size is fixed.

Test signals: Build with `BUILD_TAU`, define events with multiple format strings, and validate per-thread refresh copies all event metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_fsm.c -->
# sources/distributed-fs/orangefs/src/common/events/fmt_fsm.c

Purpose: Implements a small C++ format-string finite-state parser and serializer for TAU trace event varargs.

Important APIs/functions: `ff_format::parse()` scans `v_fmt` and fills up to 16 `ff_pattern` entries. `ff_pattern::parse()` recognizes `%u`, `%d`, `%f`, `%c`, and up to two `l` length modifiers. `ff_format::suck()` and `ff_pattern::suck()` pull typed values from a `va_list` into a byte buffer. `bfprint()` variants print values back from a byte buffer.

Control flow: The parser walks the format string looking for `%`, transitions through pattern/length/type states, records type size, and returns the number of characters consumed. Higher-level `ff_format::parse()` keeps advancing even on bad patterns, accumulating valid ones. Serialization iterates parsed patterns and advances a byte offset by each pattern size.

State/persistence: Parsed state is stored in `ff_format` fields: raw format, parsed format, pattern array, count, total byte size, and initialized flag. No disk persistence.

Dependencies/integration: Built as C++ via module flags. Used by `pvfs_tau_api.c` to encode start/stop event payloads into TAU user events.

Risks: No guard against more than 16 patterns, so long formats can overflow `patns`. `strncat(v_parsed_fmt, ..., 255)` ignores remaining capacity. Byte-buffer casts can violate alignment on strict platforms. `bfprint()` loop permits `totwrote <= src_sz`, which can enter with no remaining bytes.

Test signals: Unit-test supported formats, invalid formats, many-pattern overflow boundaries, vararg promotion for `float` and `char`, and round-trip encode/print across 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_fsm.h -->
# sources/distributed-fs/orangefs/src/common/events/fmt_fsm.h

Purpose: Declares the `ff_format` and nested `ff_pattern` C++ classes used to parse and encode TAU event format descriptors.

Important APIs/types: `ff_pattern` stores the textual pattern, length modifier count, stored size, unsigned flag, parser state, error/end flags, and type. `ff_format` stores raw/parsed formats, an array of 16 patterns, pattern count, total size, and initialization flag. Template `promoteIntegral()` helpers decode stored bytes into caller-requested integral types.

Control flow contract: Call `init()` with a format string, `parse()` to populate patterns, `suck()` to encode varargs, `bfprint()` to print stored bytes, and `promoteIntegral()` to extract one integral pattern.

State/persistence: Objects hold parsed metadata and are copied into event definition structures. No external persistence.

Dependencies/integration: Includes C/C++ standard headers and is consumed by TAU event files that are compiled as C++.

Risks: Constructors accept non-const `char *`, limiting use with string literals under stricter C++ compilers. Fixed arrays and `strncpy()` may truncate silently. Template decoding assumes stored byte layout and endian match the writing process.

Test signals: Compile under the repository's C++ mode, exercise copy construction/assignment through event bundle refresh, and validate `promoteIntegral()` for signed/unsigned width variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/fmt_fsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/events/module.mk.in

Purpose: Conditional build registration for TAU event tracing support.

Important build variables: Under `BUILD_TAU`, adds `pvfs_tau_api.c` and `fmt_fsm.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`. When `@TAU_INCS@` is non-empty, sets per-file compile flags to `-x c++ @TAU_INCS@`.

Control flow/state: Make conditional only; no runtime state.

Dependencies/integration: Integrates TAU tracing into common/server/BMI builds only when configured. The `-x c++` flag is essential because the `.c` files contain C++ constructs.

Risks: Toolchains that do not accept `-x c++` or mixed C/C++ linking may fail. The conditional excludes all event code when `BUILD_TAU` is unset, so consumers must guard references.

Test signals: Configure with and without `BUILD_TAU`; verify TAU include substitution and C++ linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.c -->
# sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.c

Purpose: Implements a C-callable PVFS/OrangeFS tracing API backed by TAU trace files and the local format FSM.

Important APIs/functions: `Ttf_init()` records process/file settings, initializes TAU, creates the master bundle, resets per-thread bundles, and initializes thread 0. `Ttf_thread_start()` registers a TAU thread group, initializes a per-thread trace file, and refreshes event definitions from the master bundle. `Ttf_event_define()` allocates event IDs and start/stop user-event IDs in the master bundle, parses format descriptors, and refreshes the local bundle. `Ttf_EnterState_info_va()` and `Ttf_LeaveState_info_va()` write state enter/leave records and encode event IDs plus formatted varargs into scratch space as `x_uint64` user-event triggers. `Ttf_finalize()` exits dummy states and closes trace files.

Control flow: Global event definitions are serialized by a pthread mutex around the master bundle. Per-thread bundles lazily allocate and are refreshed when an event type is missing or after definitions change. Trace files are named from configured folder, prefix, process id, and TAU thread id.

State/persistence: Persistent output is TAU `.trc` and `.edf` files. In-memory state includes `g_master_bundle`, `g_t_bundles[1024]`, process identifiers, trace path/prefix, default buffer size, and per-thread event counters/scratch buffers.

Dependencies/integration: Requires TAU headers/libraries, pthreads, `fmt_fsm.h`, `pvfs_tau_api.h`, and debug macros. Exposes `extern "C"` symbols for C callers.

Risks: Thread IDs index a fixed 1024-entry array without bounds checks. Memory allocated for bundles/events is not freed in `Ttf_finalize()`. Scratch buffer size is fixed and not checked against encoded payload size. Some API parameters (`process_id`, `thread_id`, start/end times in `Ttf_LogEvent_info`) are ignored or only partly used. Format and event structure definitions duplicate `fmt_api.h`.

Test signals: TAU-enabled integration tests should cover multiple threads, event definition before/after thread start, vararg payload formats, finalization, and oversized format rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.h -->
# sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.h

Purpose: Public C interface for PVFS/OrangeFS TAU trace instrumentation.

Important APIs/types: Defines limits and `tau_thread_group_info` with group name, max, blocking flag, and buffer size. Declares initialization/finalization, thread start/stop, event definition, and enter/leave state functions including `va_list` variants.

Control flow contract: Call `Ttf_init()`, optionally `Ttf_thread_start()`, define event types, wrap operations with enter/leave calls, then call `Ttf_finalize()`.

State/persistence: The header itself holds no state but its API drives TAU trace file creation and per-thread event state in `pvfs_tau_api.c`.

Dependencies/integration: C++ compatible `extern "C"`, includes `<stdarg.h>` and TAU writer definitions for handle/integer types.

Risks: API names are generic `Ttf_*` and may collide with TAU/trace naming. It exposes varargs functions without compile-time format checking. `tau_thread_group_info.name` is only 20 bytes.

Test signals: Compile C and C++ instrumentation callers, and verify event enter/leave calls produce matching TAU records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/events/pvfs_tau_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.c -->
# sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.c

Purpose: Implements POSIX-backed generic mutex and condition-variable wrappers for OrangeFS.

Important APIs/functions: Mutex functions initialize normal, recursive, and process-shared pthread mutexes; lock, unlock, trylock, destroy, and return `pthread_self()`. Condition functions initialize normal/shared pthread conditions, wait/timedwait, signal, broadcast, and destroy.

Control flow: Thin wrappers forward to pthread APIs, adding null-pointer validation for destroy paths and attribute setup for recursive/process-shared initialization.

State/persistence: No module global state. All state lives in caller-provided pthread mutex/condition objects.

Dependencies/integration: Included through `gen-locks.h`, which maps portable `gen_*` macros to these POSIX functions when `__GEN_POSIX_LOCKING__` is selected. Used by common infrastructure such as gossip and id-generator.

Risks: Checks `pthread_*attr_*` return values with `rc < 0`, but pthread APIs return positive errno-style values; failures may be missed. If `gen_posix_shared_cond_init()` fails after creating a local attr, it can return without destroying it. Return semantics are mixed between pthread positive error codes and documented `-errno` comments.

Test signals: Build/run with normal, recursive, process-shared locks, timed waits, and failure injection for attr setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.h -->
# sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.h

Purpose: Defines OrangeFS's portable locking abstraction across POSIX pthreads, Win32 handles, and null-lock builds.

Important APIs/types: Selects default locking at compile time unless `__GEN_NULL_LOCKING__` is set: Win32 selects `__GEN_WIN_LOCKING__`, other platforms select `__GEN_POSIX_LOCKING__`. Defines `gen_mutex_t`, `gen_thread_t`, `gen_cond_t`, initializer macros, and `gen_mutex_*`, `gen_cond_*`, `gen_thread_self()` mappings.

Control flow contract: Callers use `gen_*` APIs without knowing the platform implementation. Static initializers are provided for mutexes/conditions; Windows implementation lazily initializes sentinel values.

State/persistence: Header does not persist state, but type selection determines ABI and static initializer values.

Dependencies/integration: Includes `pvfs2-internal.h`, pthreads or Windows headers, and is used widely in common OrangeFS code.

Risks: Null-lock branch contains an apparent typo in `gen_cond_timedwait(gen_cond_t *cond, gen_mutex_t *mutex\`, ...)`, which would break compilation if `__GEN_NULL_LOCKING__` is enabled. Some null-lock init/destroy macros expand to `do{}while(0)` and do not return an int despite call sites possibly expecting one. POSIX initializer macros include trailing semicolons.

Test signals: Compile all three locking modes, including `__GEN_NULL_LOCKING__`, and run contention/condition-variable tests on POSIX and Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-win-locks.c -->
# sources/distributed-fs/orangefs/src/common/gen-locks/gen-win-locks.c

Purpose: Implements Win32 generic mutexes and a condition-variable emulation for OrangeFS, modeled after pthreads-win32 semantics.

Important APIs/functions: `gen_win_mutex_init/lock/unlock/trylock/destroy()` wrap Win32 mutex handles with lazy static-initializer support. `gen_win_cond_init/destroy/wait/timedwait/signal/broadcast()` manage a custom `gen_cond_t_` containing waiter counts, semaphores, an unblock mutex, and global linked-list membership. Internal helpers include `cond_check_need_init()`, `cond_timedwait()`, `cond_wait_cleanup()`, and `cond_unblock()`.

Control flow: Waiters increment `nWaitersBlocked`, release the caller mutex, wait on `semBlockQueue`, perform cleanup to adjust waiter counters, then reacquire the caller mutex. Signal/broadcast computes how many waiters to release under `mtxUnblockLock` and posts to the queue semaphore.

State/persistence: Maintains process-global critical sections for lazy initialization and condition-list locking, plus global condition-list head/tail. Mutex and condition objects own Win32 handles until destroyed.

Dependencies/integration: Selected by `gen-locks.h` on Windows. Uses Windows synchronization APIs, `_ftime_s()`, and errno translation via `SET_ERROR`.

Risks: Lazy initialization of global critical sections is itself racy before the lock exists. Several functions return positive errno values while mutex wrappers often return `-1` and set `errno`. `gen_win_thread_self()` returns a pseudo-handle from `GetCurrentThread()`, not a stable numeric ID. Destroy while waiters exist is complex and must be carefully tested.

Test signals: Windows tests should cover static initializer use, simultaneous lazy init, timed wait timeout, signal, broadcast, destroy-with-waiters, abandoned mutex behavior, and invalid handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/gen-win-locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/gen-locks/module.mk.in

Purpose: Build-fragment registration for generic lock support.

Important build variables: Sets `DIR := src/common/gen-locks` and appends `gen-locks.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Ensures POSIX generic locks are available in common, server, and BMI library builds. Windows-specific `gen-win-locks.c` is not listed here, implying it is registered by another platform-specific path or build mechanism.

Risks: If no other fragment adds `gen-win-locks.c`, Windows builds using `__GEN_WIN_LOCKING__` will have unresolved symbols.

Test signals: Inspect configured Windows build source lists and POSIX/BMI link outputs for expected lock implementation objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gen-locks/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/gossip.c -->
# sources/distributed-fs/orangefs/src/common/gossip/gossip.c

Purpose: Implements the OrangeFS `gossip` logging interface for debug and error output to stderr, files, or syslog.

Important APIs/functions: `gossip_enable_stderr()`, `gossip_enable_file()`, `gossip_enable_syslog()`, `gossip_reopen_file()`, and `gossip_disable()` switch facilities while preserving debug mask state. `gossip_set_debug_mask()`/`gossip_get_debug_mask()` control global debug enablement and bitmask. `__gossip_debug()`/`__gossip_debug_va()` route debug messages after macro-level filtering. `gossip_err()` logs unmasked errors. `gossip_debug_fp_va()` formats prefixes and timestamps; syslog helpers wrap `syslog()`. Optional `gossip_backtrace()` emits stack traces and exits after repeated backtraces.

Control flow: Facility enablement first disables the current facility, then activates the new sink and restores debug flags. Debug calls are filtered by macros on GCC builds, normalized to prefix `D` if `?`, then dispatched by `gossip_facility`. File/stderr messages are buffered into `GOSSIP_BUF_SIZE`, timestamped, written, and flushed.

State/persistence: Global mutable state includes `gossip_debug_on`, `gossip_debug_mask`, `gossip_facility`, `internal_log_file`, syslog priority, and timestamp mode. File logging persists to the configured filename.

Dependencies/integration: Uses `gen-locks.h` only for thread-stamp IDs, syslog on POSIX, `wincommon.h` on Windows, and optional execinfo. `gossip.h` provides macros used broadly by OrangeFS.

Risks: Global state is not protected by locks, so concurrent facility changes/logging can race. File logging flushes every line, impacting performance. Timestamp formatting uses `localtime()` which is not thread-safe on many platforms. Windows syslog functions are stubs.

Test signals: Verify all facilities, timestamp modes, mask filtering, reopen behavior, disabled facility behavior, long messages/truncation, and optional backtrace builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/gossip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/gossip.h -->
# sources/distributed-fs/orangefs/src/common/gossip/gossip.h

Purpose: Public declarations and macros for OrangeFS logging.

Important APIs/types: Declares global debug state, buffer size, timestamp enum, facility control functions, debug/error functions, and `gossip_backtrace()`. Provides kernel-mode simplified macros and user-mode GCC/non-GCC macro variants. `gossip_debug_enabled()`, `gossip_debug()`, `gossip_perf_log()`, `gossip_ldebug()`, and `gossip_lerr()` are the main call-site APIs.

Control flow contract: Call sites normally use macros, which avoid function-call overhead when debugging is disabled. Error macros always call `gossip_err()` and, on GCC user-mode builds, `gossip_lerr()` also emits a backtrace.

State/persistence: Header exposes global variables for direct reads/writes by macros and possibly callers.

Dependencies/integration: Includes `pvfs2-config.h`, syslog on POSIX user builds, and `wincommon.h` on Windows. Performance logging depends on `GOSSIP_PERFCOUNTER_DEBUG` being defined elsewhere.

Risks: Macro syntax differs by compiler/Windows branch and may hide format-checking differences. Direct global exposure makes it easy to bypass setters. Kernel and user semantics differ significantly.

Test signals: Compile with GCC, non-GCC, Windows, kernel, `GOSSIP_DISABLE_DEBUG`, and performance-counter configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/gossip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/gossip/module.mk.in

Purpose: Build-fragment registration for the gossip logging implementation and optional backtrace support.

Important build variables: Substitutes `GOSSIP_ENABLE_BACKTRACE`, adds `gossip.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`, and adds `-DGOSSIP_ENABLE_BACKTRACE` to `MODCFLAGS_$(DIR)/gossip.c` when enabled.

Control flow/state: Make configuration only.

Dependencies/integration: Ties configure-time backtrace detection/choice into the C preprocessor path in `gossip.c`.

Risks: Optional backtrace requires compatible execinfo support and correct link flags from elsewhere. The make variable name being set to `@GOSSIP_ENABLE_BACKTRACE@` must evaluate as intended.

Test signals: Configure both backtrace-on and backtrace-off builds; confirm `gossip_backtrace()` either emits stack frames or compiles to a no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/gossip/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/hash/module.mk.in

Purpose: Build-fragment registration for the MurmurHash3 implementation.

Important build variables: Sets `DIR := src/common/hash`, then appends `murmur3.c` to `SERVERSRC` and `LIBSRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes MurmurHash3 available to server and common library consumers, but not explicitly to BMI.

Risks: If BMI code needs Murmur3, this fragment will not include it in `LIBBMISRC`. There are no per-file flags for endian/alignment portability.

Test signals: Link targets that call `MurmurHash3_*` from library/server code and compare known hash vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/murmur3.c -->
# sources/distributed-fs/orangefs/src/common/hash/murmur3.c

Purpose: Public-domain MurmurHash3 reference implementation providing 32-bit and 128-bit non-cryptographic hashes.

Important APIs/functions: `MurmurHash3_x86_32()`, `MurmurHash3_x86_128()`, and `MurmurHash3_x64_128()` implement platform-tuned variants. Helpers include rotate functions/macros, `getblock()`, `fmix32()`, and `fmix64()`.

Control flow: Each hash function initializes seed-derived hash state, processes fixed-size body blocks, folds in tail bytes with fall-through `switch` logic, xors length, applies avalanche finalization, and writes the result to caller-provided output storage.

State/persistence: Stateless and deterministic. No memory allocation or persistent state.

Dependencies/integration: Includes `murmur3.h` for fixed-width integer types and prototypes. Used wherever OrangeFS needs stable non-cryptographic hashing.

Risks: `getblock(p, i) (p[i])` assumes native endian and tolerates whatever alignment the platform allows; strict-alignment or cross-endian portability may need adjustment. The x86 and x64 128-bit variants intentionally produce different results. Fall-through switch cases rely on compiler acceptance without annotations.

Test signals: Compare known MurmurHash3 vectors for each variant, test empty input, unaligned input buffers, tail lengths 1-15, and deterministic seed behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/murmur3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/murmur3.h -->
# sources/distributed-fs/orangefs/src/common/hash/murmur3.h

Purpose: Declares MurmurHash3 hash functions.

Important APIs/functions: `MurmurHash3_x86_32()`, `MurmurHash3_x86_128()`, and `MurmurHash3_x64_128()` accept key pointer, byte length, 32-bit seed, and output buffer.

Control flow/state: Header only; all functions are stateless and write into caller-owned `out`.

Dependencies/integration: Includes `<stdint.h>`. Consumers must allocate appropriately sized output buffers: 4 bytes for x86_32 and 16 bytes for 128-bit variants.

Risks: The API does not encode output size in the type system, so undersized `out` buffers are caller bugs. No `extern "C"` guard for C++ consumers.

Test signals: Compile C and C++ consumers if needed, and validate output buffer sizes at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/hash/murmur3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/id-generator.c -->
# sources/distributed-fs/orangefs/src/common/id-generator/id-generator.c

Purpose: Implements the "safe" opaque ID registry that maps generated integer IDs to arbitrary pointers using a quickhash table.

Important APIs/functions: `id_gen_safe_initialize()` creates the hash table and increments an init count. `id_gen_safe_finalize()` decrements the count and destroys the table when it reaches zero. `id_gen_safe_register()` allocates an entry, assigns a monotonically increasing nonzero ID, stores the item pointer, and inserts it. `id_gen_safe_lookup()` returns the registered pointer. `id_gen_safe_unregister()` removes and frees an entry. `hash_key()` and `hash_key_compare()` adapt IDs to quickhash.

Control flow: Register/lookup/unregister take `s_id_gen_safe_mutex` around hash operations. Finalize locks only around destruction. Initialize is not locked.

State/persistence: Process-global registry state includes the mutex, init count, next tag, and hash table pointer. No disk persistence. IDs remain valid until unregistered/finalized.

Dependencies/integration: Uses `quickhash`, `qlist`, `gen-locks`, `pvfs2-internal.h`, and `BMI_id_gen_t` from the header. Likely used by BMI/common code that cannot safely expose raw pointers as IDs.

Risks: `id_gen_safe_register()` leaks the mutex lock if `malloc()` fails after locking. Initialize/finalize reference counting is not fully synchronized and can race. ID wraparound only skips zero, not collisions with still-live IDs after wrap. Assertions enforce initialization in register but disappear under `NDEBUG`.

Test signals: Concurrent register/lookup/unregister, init/finalize nesting, allocation-failure path, null item rejection, ID wrap simulation, and hash collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/id-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/id-generator.h -->
# sources/distributed-fs/orangefs/src/common/id-generator/id-generator.h

Purpose: Declares fast and safe pointer-to-ID mechanisms for OrangeFS.

Important APIs/types: `BMI_id_gen_t` is `PVFS_id_gen_t` when PVFS types are already included, otherwise `int64_t`. `id_gen_fast_register()` casts a pointer directly into an integer ID, `id_gen_fast_lookup()` casts back, and `id_gen_fast_unregister()` is a no-op. Safe registry functions are declared for indirect ID mapping.

Control flow contract: Fast IDs require no initialization but expose pointer values. Safe IDs require initialize/register/lookup/unregister/finalize lifecycle.

State/persistence: Fast IDs encode process-local pointer addresses and are not stable across processes/runs. Safe IDs are process-global registry keys.

Dependencies/integration: Includes `pvfs2-config.h` for `SIZEOF_VOID_P`, and `<stdint.h>/<errno.h>`.

Risks: Fast registration truncates/casts pointers on 32-bit through `int32_t`, then back through `uint32_t`; it is process-local and unsafe for untrusted handles. The typedef changes based on include order if `__PVFS2_TYPES_H` is defined.

Test signals: Validate fast round-trip on 32-bit and 64-bit builds, and safe lifecycle under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/id-generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/id-generator/module.mk.in

Purpose: Build-fragment registration for the ID generator implementation.

Important build variables: Sets `DIR := src/common/id-generator`, then appends `id-generator.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes safe ID registry available to common, server, and BMI targets.

Risks: None beyond normal source-list duplication concerns.

Test signals: Link all three target families with ID generator call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/id-generator/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/llist.c -->
# sources/distributed-fs/orangefs/src/common/llist/llist.c

Purpose: Implements a simple singly linked list abstraction with a sentinel head node for OrangeFS common code.

Important APIs/functions: `PINT_llist_new()`, `PINT_llist_empty()`, `PINT_llist_add_to_head()`, `PINT_llist_add_to_tail()`, `PINT_llist_head()`, `PINT_llist_tail()`, `PINT_llist_search()`, `PINT_llist_rem()`, `PINT_llist_count()`, `PINT_llist_doall()`, `PINT_llist_doall_arg()`, `PINT_llist_free()`, and `PINT_llist_next()`.

Control flow: Lists always start with a sentinel whose `item` is `NULL`; add/remove/search/count skip that sentinel. Search/removal use caller-provided comparison functions that return `0` on match. `doall` saves the next pointer before invoking callbacks so callbacks may destroy the current item.

State/persistence: Heap-allocated list nodes contain only `void *item` and `next`. The list does not own item memory except when `PINT_llist_free()` calls the provided free callback.

Dependencies/integration: Includes `llist.h` and `pvfs2-internal.h`. Used as a generic container in common code.

Risks: No internal locking. Tail insertion is O(n). `PINT_llist_free()` returns without freeing nodes if `free_item` is NULL, so callers cannot free a list of non-owned items with this API. `PINT_llist_next()` exposes internal nodes and can bypass abstraction safety.

Test signals: Empty-list operations, head/tail ordering, search/remove comparator semantics, callback deletion during `doall`, and freeing with owned item data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/llist.h -->
# sources/distributed-fs/orangefs/src/common/llist/llist.h

Purpose: Declares the simple OrangeFS linked-list container API.

Important APIs/types: `PINT_llist` node contains `void *item` and `PINT_llist_p next`. Macro `PINT_llist_add()` aliases head insertion. Prototypes cover creation, emptiness, insertion, traversal callbacks, free, search, remove, head/tail access, count, and raw next traversal.

Control flow contract: Callers create a sentinel list with `PINT_llist_new()` and should treat the first node as non-data. Comparator callbacks return zero for equality.

State/persistence: Header defines only in-memory list shape.

Dependencies/integration: Includes `<stdio.h>` and `<stdlib.h>` for C consumers.

Risks: Exposes struct internals, so callers can corrupt links. No const-correct variants. No API to free only nodes without item callback.

Test signals: Compile consumers using macro alias and direct traversal; static analysis for callers that assume first node contains data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/llist/module.mk.in

Purpose: Build-fragment registration for the linked-list implementation.

Important build variables: Sets `DIR := src/common/llist`, then appends `llist.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes the generic list available to common, server, and BMI targets.

Risks: None specific; callers must include `llist.h` through normal dependency tracking.

Test signals: Link all target families that use `PINT_llist_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/llist/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/lmdb.h -->
# sources/distributed-fs/orangefs/src/common/lmdb/lmdb.h

Purpose: Vendored LMDB 0.9.21 public API header for the Lightning Memory-Mapped Database library. It documents and declares the environment, transaction, database, cursor, copy, stats, reader, and error APIs used by LMDB consumers.

Important APIs/types: Opaque handles `MDB_env`, `MDB_txn`, `MDB_cursor`, and `MDB_dbi`; value container `MDB_val`; callback types for comparison, relocation, assertions, and message output; `MDB_stat` and `MDB_envinfo`; version macros and error codes. Major function families include `mdb_env_*` lifecycle/config/sync/copy/status calls, `mdb_txn_*` transaction calls, `mdb_dbi_*` database handle calls, `mdb_get/put/del`, cursor open/get/put/del/count/renew/close, comparison helpers, and reader lock-table inspection/checking.

Control flow contract: Typical use is create environment, set mapsize/maxreaders/maxdbs if needed, open environment, begin transactions, open database handles, perform get/put/cursor operations, commit or abort, close cursors/database handles as required, then close the environment. Read transactions provide snapshots; write transactions are serialized; cursors are transaction-bound.

State/persistence: LMDB persists data in memory-mapped database files plus a lock file. Copy-on-write pages provide MVCC. Header caveats emphasize reader slots, stale readers, mapsize growth, filesystem/locking constraints, and durability tradeoffs controlled by flags such as `MDB_NOSYNC`, `MDB_NOMETASYNC`, `MDB_WRITEMAP`, and `MDB_MAPASYNC`.

Dependencies/integration: Includes `<sys/types.h>` and offers C++ linkage. Platform abstractions define `mdb_mode_t` and `mdb_filehandle_t` for POSIX/Windows. In this repository it sits under `src/common/lmdb`, so OrangeFS code can build against a pinned LMDB API.

Risks: Many APIs return pointers into mmap-owned memory that become invalid after updates or transaction end; callers must not modify them. Long-lived readers can prevent free-page reuse and grow the database. `MDB_NOLOCK`, remote filesystems, mixed `MDB_WRITEMAP` usage, wrong custom compare functions, or closing DB handles while in use can corrupt or destabilize the environment. This header is an older pinned LMDB version, so security/bug fixes depend on the matching implementation version in the tree.

Test signals: Integration tests should cover environment lifecycle, readonly/readwrite transactions, map-full handling, stale reader checks, named DB maxdbs, duplicate-sort cursor paths, backup copy, durability flag combinations, and multi-process reader/writer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/lmdb.h -->
