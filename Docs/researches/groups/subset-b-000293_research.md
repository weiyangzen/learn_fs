# Research: subset-b-000293

Grouped source research for the xz command-line front-end files in `sources/compression/xz/src/xz`. Each section is source-tree-aligned and bounded for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/args.c -->
## sources/compression/xz/src/xz/args.c

Purpose: Implements command-line and environment argument parsing for the `xz` executable. It owns global option flags such as `opt_stdout`, `opt_force`, `opt_keep_original`, `opt_synchronous`, `opt_robot`, and `opt_ignore_check`, plus the `stdin_filename` sentinel used by the rest of the program.

Important APIs and functions: `args_parse()` initializes an `args_info`, derives defaults from the invoked program name (`xzcat`, `unxz`, `lzma`, etc.), parses `XZ_DEFAULTS`, `XZ_OPT`, then parses real `argv`. `parse_real()` is the `getopt_long()` switch for operation modes, file modifiers, formats, checks, memory limits, threads, filter-chain options, list/test modes, help/version exits, and filename-list options. `parse_memlimit()` accepts byte values or percentages and forwards normalized limits to `hardware_memlimit_set()`. `parse_block_list()` parses `--block-list`, including optional single-digit filter-chain prefixes, repeated empty entries, final zero-as-infinity, and derived globals `block_list_chain_mask` and `block_list_largest`. `parse_environment()` tokenizes environment variables on whitespace and deliberately ignores non-option filename operands there.

Control flow: Parsing happens in three phases: executable-name defaults, environment defaults, then command-line overrides. Post-parse normalization enforces build-time encoder/decoder availability, converts test/stdout modes into keep/stdout behavior, disables synchronous removal when keeping originals, defaults compression `FORMAT_AUTO` to `FORMAT_XZ`, drops incompatible `--block-list`, validates raw-format suffix requirements, and calls `coder_set_compression_settings()` for compression or raw decoding. It finally chooses either command-line filenames or an implicit `"-"` stdin entry.

State and persistence: This file mutates process-wide options consumed by `coder.c`, `file_io.c`, `suffix.c`, `message.c`, `hardware.c`, and `main.c`. `args_info` holds command-line filename pointers plus optional `--files`/`--files0` state. `args_free()` only frees `opt_block_list` in debug builds; normal process exit owns cleanup.

Dependencies and integration points: Uses `getopt_long`, locale, `str_to_uint64()`, `message_*()` fatal/error paths, `suffix_set()`/`suffix_is_set()`, `options_*()` parser helpers through `coder_add_filter()`, hardware limit/thread setters, and liblzma check capability queries. The `--filters1` through `--filters9` options are paired with `--block-list` filter chain numbers and later validated in `coder_set_compression_settings()`.

Risks: Environment parsing is intentionally shell-like only for whitespace and does not support quoting, so tests must capture documented behavior. `parse_block_list()` accepts only one-digit chain prefixes; changing chain count requires coordinated parser, help, coder, and format semantics. Raw format without suffix is guarded to avoid ambiguous output names. Memory percentage parsing depends on `hardware_init()` having already set total RAM, which `main.c` guarantees. Fatal parse paths exit the process, so unit tests need subprocess or harness support.

Test signals: Exercise precedence between `XZ_DEFAULTS`, `XZ_OPT`, and CLI; invoked-name defaults; `--files` versus `--files0` mutual exclusion; raw-format suffix rejection; block-list edge cases including leading comma, empty repeat, zero not final, and missing filter chains; `-T+1`, `-T0`, percentage memlimits, unsupported checks, and build configurations without encoders or decoders.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/args.h -->
## sources/compression/xz/src/xz/args.h

Purpose: Declares the argument parsing contract for the xz front end.

Important APIs and types: `args_info` carries `arg_names`, `arg_count`, optional `files_name`, `files_file`, and `files_delim`. The header exports process-wide flags set by `args.c`: `opt_stdout`, `opt_force`, `opt_keep_original`, `opt_synchronous`, `opt_robot`, and `opt_ignore_check`. It also exports `stdin_filename`, `args_parse()`, and debug-only `args_free()`.

Control flow and integration: `main.c` creates an `args_info`, passes it to `args_parse()`, then uses the resulting arrays and optional `files_file` stream to drive `coder_run()` or `list_file()`. Other modules test the exported booleans directly: `file_io.c` uses force/stdout/keep/sync semantics, `message.c` uses robot mode, `coder.c` uses ignore-check, and `list.c` mutates stdout/force for listing.

State and persistence: The struct references existing `argv` storage except for duplicated `--files` names from environment parsing. The `stdin_filename` sentinel is a stable global pointer used for identity checks, not just string comparison.

Risks: The API is heavily global and order-dependent; callers must run `hardware_init()` before `args_parse()` and must not treat `stdin_filename` as mutable. `files_file` ownership is split: `args.c` opens it, while `main.c` closes non-stdin streams.

Test signals: Header-level tests are integration tests: verify implicit stdin, `--files` stream handling, and that exported flags cause expected I/O and coder behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/coder.c -->
## sources/compression/xz/src/xz/coder.c

Purpose: Owns compression, decompression, test-mode processing, passthrough mode, and liblzma stream setup for each input file.

Important APIs and functions: Public setters include `coder_set_check()`, `coder_set_preset()`, `coder_set_extreme()`, `coder_add_filter()`, `coder_add_filters_from_str()`, `coder_add_block_filters()`, `coder_set_compression_settings()`, and `coder_run()`. Internal state includes a global `lzma_stream strm`, input/output `io_buf`s, up to ten filter chains, preset/check selection, `opt_block_size`, `opt_block_list`, `block_list_largest`, `block_list_chain_mask`, and `allow_trailing_input`. `get_chains_memusage()` computes encoder/decoder memory use for selected chains. `coder_init()` detects formats and initializes the right liblzma encoder/decoder. `coder_normal()` drives `lzma_code()` and I/O. `split_block()` coordinates `--block-size` and `--block-list` in single-threaded xz encoding. `coder_passthru()` copies unrecognized input with `--decompress --stdout --force`.

Control flow: `args.c` populates global mode/format/filter/memory options and calls `coder_set_compression_settings()` before file processing. `coder_run()` opens the source, pre-reads a chunk for decoding, calls `coder_init()`, opens the destination unless testing, starts progress, runs either normal coding or passthrough, then closes the `file_pair` with success/failure. `coder_init()` chooses encoder paths for xz/lzma/raw and decoder paths for auto/xz/lzma/lzip/raw, including threaded xz decode when available. `coder_normal()` repeatedly fills input through `io_read()`, chooses `LZMA_RUN`, `LZMA_FINISH`, `LZMA_SYNC_FLUSH`, or `LZMA_FULL_BARRIER`, writes full output buffers, handles unsupported-check warnings, memlimit errors, stream-end/trailing-input policy, and progress updates.

State and persistence: Filter chains and liblzma stream state persist across files within the process, while `lzma_code()` state is reset by encoder/decoder initialization for each file. Options are global and set once before the processing loop. Debug `coder_free()` frees non-default chains and ends the global stream. No on-disk state is written directly; persistence is delegated to `file_io.c`.

Dependencies and integration points: Depends on liblzma encoders/decoders, string filter APIs, memory-usage APIs, `hardware.c` for threads and memlimits, `file_io.c` for all reads/writes/open/close, `message.c` for warnings/progress, `mytime.c` for flush timing, and option globals from `args.c`. It also consumes `opt_block_list` parsed by `args.c` and filter option structures allocated by `options.c`.

Risks: The global `lzma_stream` and filter-chain arrays assume single-file-at-a-time processing. Memory auto-adjustment can change output by lowering dictionary size or switching from threaded to single-threaded mode unless `--no-adjust` blocks it. Format detection for legacy `.lzma` uses heuristics and can have false positive/negative edge cases. `--single-stream` and lzip trailing-data behavior must not leak into normal xz/lzma/raw trailing-garbage detection. Block-list chain validation and runtime `lzma_filters_update()` are critical for correctness.

Test signals: Cover each format path, auto-detection failures, passthrough conditions, unsupported check warnings, memlimit-too-small paths, `--no-adjust`, threaded fallback, raw preset warning, block-size and block-list interactions, `--flush-timeout` compatibility and sync flush behavior, trailing garbage, concatenated streams, lzip trailing data, and broken output pipe handling through `file_io.c`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/coder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/coder.h -->
## sources/compression/xz/src/xz/coder.h

Purpose: Defines the public coder interface and shared compression-mode globals for the xz command-line front end.

Important APIs and types: `enum operation_mode` distinguishes compress, decompress, test, and list. `enum format_type` distinguishes auto, xz, lzma, optional lzip, and raw. `block_list_entry` pairs an uncompressed block size with a filter chain number. The header exports mode/format flags, auto-adjust and single-stream flags, block-list state, and coder setup/run functions.

Control flow and integration: `args.c` sets almost every exported variable or invokes the setters. `main.c` ultimately calls `coder_run()` for non-list operations. `file_io.c`, `message.c`, `hardware.c`, `suffix.c`, and `list.c` read the mode/format globals to select I/O safety, progress formatting, memlimit class, suffixes, and list-mode behavior.

State and persistence: This header intentionally exposes process-global mutable state. The block-list pointer is allocated by `args.c`, validated and consumed by `coder.c`, and freed only by debug cleanup.

Risks: Since the globals are not encapsulated, new call sites can observe partially initialized state if added before `args_parse()` completes. The enum ordering for `format_type` is significant to `suffix.c`, so reordering is a compatibility risk.

Test signals: Build all optional macro combinations (`HAVE_LZIP_DECODER`, `HAVE_ENCODERS`, `HAVE_DECODERS`, `MYTHREAD_ENABLED`) and run mode/format combinations through `args_parse()` and `coder_run()`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/coder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/file_io.c -->
## sources/compression/xz/src/xz/file_io.c

Purpose: Implements source/destination opening, signal-aware nonblocking reads/writes, sparse output, attribute copying, synchronization, safe unlinking, and final close behavior.

Important APIs and functions: `io_init()` validates stdio descriptors and creates the POSIX self-pipe used for abort wakeups. `io_write_to_user_abort_pipe()` is signal-handler support. `io_no_sparse()` disables sparse output. `io_open_src()` and `io_open_dest()` wrap signal-blocked `io_open_src_real()` and `io_open_dest_real()`. `io_close()` finalizes sparse holes, copies attributes, optionally fsyncs file and directory, closes destination first, then closes and maybe removes the source. `io_read()`, `io_write()`, `io_seek_src()`, `io_pread()`, and `io_fix_src_pos()` provide the streaming and random-access primitives used by `coder.c` and `list.c`.

Control flow: Source open handles stdin specially, otherwise opens with safe flags, optional `O_NOFOLLOW`, nonblocking mode, regular-file restrictions, setuid/setgid/sticky/hardlink checks when removing originals, and optional `posix_fadvise()`. Destination open either binds stdout or creates an exclusive new output path from `suffix_get_dest_name()`, opening the parent directory for later sync when `opt_synchronous` is true. Reads and writes retry `EINTR`, use `poll()` with the self-pipe for `EAGAIN`/`EWOULDBLOCK`, and integrate `--flush-timeout` by returning partial input with `flush_needed`. Close removes incomplete destination files or successful source files according to `opt_keep_original`.

State and persistence: Uses static `file_pair pair` because processing is sequential. Tracks stdin/stdout original flags for restoration, `try_sparse`, pending sparse-hole length, destination and source `stat` structures, and a POSIX user-abort pipe. Persistent filesystem effects include creating destination files, copying permissions/timestamps, fsyncing, unlinking sources or failed outputs, and sparse-file holes.

Dependencies and integration points: Depends on `args.c` globals (`opt_stdout`, `opt_force`, `opt_keep_original`, `opt_synchronous`), `coder.c` mode, `mytime.c` flush timeout, `signals.c` blocking and `user_abort`, `suffix.c` destination names, `sandbox.c` strict sandbox transition after source open, and `message.c` for diagnostics. `list.c` uses seek/pread support to inspect xz metadata.

Risks: Race windows around unlinking are mitigated with device/inode checks but cannot be eliminated. Nonblocking stdio flag restoration must happen on all paths. Sparse output must avoid stdout append-mode corruption and must materialize trailing holes. Directory fsync portability is handled with platform exclusions. Hardlink/setuid/sticky safeguards differ by `--force`, `--keep`, stdout, and platform macros.

Test signals: Cover stdin/stdout flag restore, regular versus special files, symlink and hardlink rejection/acceptance, force overwrite, source equals destination, directory sync failures, sparse decompression with all-zero buffers and trailing holes, EPIPE behavior, read timeout flushes, signal abort during blocking I/O, list-mode seeks, and sandbox enablement after opening exactly one source.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/file_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/file_io.h -->
## sources/compression/xz/src/xz/file_io.h

Purpose: Declares the file I/O buffer type, `file_pair` state object, and public I/O routines for the xz front end.

Important APIs and types: `IO_BUFFER_SIZE` is derived from `BUFSIZ` and rounded to a multiple of eight for sparse detection. `io_buf` aliases bytes, 32-bit words, and 64-bit words safely through a union. `file_pair` stores source/destination names and descriptors, optional directory fd, EOF/flush flags, sparse-output state, and source/destination `stat` snapshots. Public functions cover initialization, abort-pipe signaling, sparse disabling, open/close, read/write, seeking, pread-like reads, and source-position rewind.

Control flow and integration: `main.c` calls `io_init()`. `coder.c` uses open/read/write/close for data transformation. `list.c` uses source open, `io_pread()`, and close for metadata listing. `signals.c` calls `io_write_to_user_abort_pipe()` on POSIX.

State and persistence: The struct fields are the authoritative per-file state passed between `file_io.c`, `coder.c`, and `list.c`. File removal decisions depend on the stored `stat` snapshots and success flag.

Risks: Callers must respect `IO_BUFFER_SIZE` bounds, must not keep `file_pair` beyond the next `io_open_src()` because the implementation uses static storage, and must pass the correct success flag to avoid deleting good sources or retaining bad destinations.

Test signals: Compile on POSIX, Windows/MSVC, and DOS-like configurations; validate struct behavior for stdin/stdout, regular files, sparse paths, and list-mode random access.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/file_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/hardware.c -->
## sources/compression/xz/src/xz/hardware.c

Purpose: Detects hardware resources and manages thread and memory-limit policy for compression, decompression, and threaded decompression.

Important APIs and functions: `hardware_init()` sets `total_ram`, default threaded memory limit, resource-limit caps, 32-bit ceilings, and default automatic thread mode. `hardware_threads_set()`, `hardware_threads_get()`, and `hardware_threads_is_mt()` manage explicit, automatic, and `-T+1` multi-thread mode. `hardware_memlimit_set()` applies byte or percentage limits to compression, decompression, and threaded decompression. `hardware_memlimit_get()`, `hardware_memlimit_mtenc_get()`, `hardware_memlimit_mtenc_is_default()`, and `hardware_memlimit_mtdec_get()` expose hard and soft limits. `hardware_memlimit_show()` prints human or robot memory information and exits.

Control flow: `main.c` calls `hardware_init()` before `args_parse()`. `args.c` updates limits and thread count while parsing. `coder.c` queries limits and thread mode while validating settings and initializing threaded encoders/decoders. `--info-memory` exits through `hardware_memlimit_show()`.

State and persistence: Static state includes `threads_max`, whether thread count was automatic, whether to use threaded mode with one thread, compression/decompression/threaded-decompression limits, default threaded limit, and total RAM. There is no external persistence.

Dependencies and integration points: Uses liblzma CPU/RAM detection, optional `getrlimit()`, gettext/message helpers, `opt_robot`, and `opt_mode`. It provides the policy that lets automatic `-T0` reduce threads without failing simply because the default soft limit is too low.

Risks: Resource-limit margin is heuristic. Percentage limits on 32-bit systems need caps to avoid address-space exhaustion. The distinction between hard decompression limit and soft threaded-decompression limit is subtle and must remain aligned with `coder.c` use of `memlimit_stop` and `memlimit_threading`.

Test signals: Run with `-T0`, `-T1`, `-T+1`, explicit memlimits, percentage memlimits, `--info-memory` robot/human, artificial `RLIMIT_AS`/`RLIMIT_DATA`, 32-bit builds, and builds without threading.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/hardware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/hardware.h -->
## sources/compression/xz/src/xz/hardware.h

Purpose: Declares the hardware resource and memory-limit interface.

Important APIs: Exposes initialization, thread setter/getter/multithread predicate, generic memory-limit setter, hard compression/decompression limit getter, threaded encoder default-limit getter/predicate, threaded decompression soft-limit getter, and the noreturn `hardware_memlimit_show()`.

Control flow and integration: `main.c` initializes hardware early; `args.c` mutates it; `coder.c` consumes it; `message.c` indirectly queries it through `message_mem_needed()`.

State and persistence: All state is private to `hardware.c`; consumers only see computed values.

Risks: The API depends on `enum operation_mode` from `coder.h`, so include ordering through `private.h` matters. Misusing `hardware_memlimit_mtdec_get()` as a hard limit would change decoder behavior.

Test signals: Header coverage comes from CLI integration around threads, memlimits, and `--info-memory`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/list.c -->
## sources/compression/xz/src/xz/list.c

Purpose: Implements `xz --list` metadata inspection for `.xz` files, including basic, verbose, debug, and robot output formats.

Important APIs and functions: Public `list_file()` lists one file and `list_totals()` prints aggregate totals. Internal `xz_file_info` holds combined liblzma index metadata, stream padding, max decoder memory use, header-size completeness, and minimum XZ Utils version. `block_header_info` holds per-block header details. `parse_indexes()` uses `lzma_file_info_decoder()` to build a combined `lzma_index`. `parse_block_header()`, `parse_check_value()`, and `parse_details()` read block-level details through `io_pread()`. Printing helpers include `print_info_basic()`, `print_info_adv()`, `print_info_robot()`, and totals variants.

Control flow: `main.c` selects `list_file()` when `opt_mode == MODE_LIST`. `list_file()` rejects non-xz/non-auto formats and stdin, initializes translated field widths, forces source-open behavior to follow symlinks while rejecting special files, parses indexes, prints according to robot and verbosity mode, updates totals only on successful print, frees the index, and closes the source without removing it. `list_totals()` prints always in robot mode and only for multiple files in human mode.

State and persistence: Static totals accumulate across listed files until process exit. Formatting width state is recomputed per `list_file()` call but stored statically. `check_value` is a static buffer for detailed check output. Listing does not write persistent files and calls `io_close(pair, false)` to avoid source deletion.

Dependencies and integration points: Depends heavily on liblzma index, block, filter-string, check-size, and file-info decoder APIs. Uses `file_io.c` for safe open/seek/read, `message.c` for verbosity and diagnostics, `hardware.c` list-mode memlimit, `args.c` globals for robot/stdout/force, and `tuklib` multibyte width helpers.

Risks: Detailed mode can be slow because it seeks and parses each block header and check value. Totals have TODO overflow checks. `list_file()` mutates global `opt_stdout` and `opt_force`; that is safe in list-only execution but would be risky if reused in a mixed-mode future. Robot output masks filenames but still has a stable tab-delimited schema that tests must preserve. Minimum-version logic must track new filters and decoder quirks.

Test signals: Use empty, too-small, corrupt, multi-stream, stream-padding, no-check, CRC/SHA, unknown-check, blocks with and without size fields, empty LZMA2 block, ARM64/RISC-V filter chains, huge block counts, multi-file totals, robot modes at `-l`, `-lv`, `-lvv`, and memory-limit failures in index parsing.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/list.h -->
## sources/compression/xz/src/xz/list.h

Purpose: Declares the public list-mode entry points.

Important APIs: `list_file(const char *filename)` lists one `.xz` file. `list_totals(void)` emits aggregate totals after all list-mode files have been processed.

Control flow and integration: `main.c` switches the per-file runner from `coder_run` to `list_file` when decoder support is built and `opt_mode` is `MODE_LIST`, then calls `list_totals()` after the loop.

State and persistence: State is internal to `list.c`; callers only trigger per-file and final aggregate output.

Risks: The header is only included when `HAVE_DECODERS` through `private.h`, matching the fact that list mode requires decoder support.

Test signals: Build without decoders and ensure list paths are unavailable; build with decoders and verify `main.c` dispatch.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/main.c -->
## sources/compression/xz/src/xz/main.c

Purpose: Provides the `main()` entry point, process initialization, file iteration, `--files`/`--files0` handling, exit-status policy, and high-level dispatch between coding and listing.

Important APIs and functions: `set_exit_status()` upgrades global exit status to warning or error, preserving errors over warnings and using a Windows critical section when needed. `set_exit_no_warn()` suppresses warning exit status. `read_name()` reads one delimited filename from a `--files` stream into a growing static buffer. `main()` wires together all modules.

Control flow: Startup initializes Windows synchronization, program name, stdio/file I/O, early sandbox, gettext, messages, hardware defaults, and arguments. It rejects unsupported `--robot` compression/decompression, tells `message.c` the file count, prevents compressed binary output to a terminal, installs signal handlers for non-list modes, optionally tightens sandbox for read-only/stdout-only operation, picks `coder_run()` or `list_file()`, processes command-line filenames with special `"-"` handling, then processes names from `--files`/`--files0`. After list mode it prints totals, runs debug cleanup, honors pending signals through `signals_exit()`, applies `--no-warn`, and exits via `tuklib_exit()`.

State and persistence: Maintains process exit status and `no_warn`. `read_name()` keeps a static reusable filename buffer until exit. Persistent work is delegated to coder/list/file I/O; `main.c` decides iteration and when streams close.

Dependencies and integration points: It is the central orchestrator for `io`, `sandbox`, `gettext`, `message`, `hardware`, `args`, `signals`, `coder`, and `list`. It enforces sequencing that other modules rely on, especially hardware before argument parsing and signal setup before actual I/O.

Risks: `read_name()` can read arbitrarily large filename lists into memory one name at a time with no configured cap. Handling stdin both as data and as filename list is explicitly rejected. Terminal checks must prevent compressed output to TTY and compressed input from TTY in decode/test paths. Sandbox decisions depend on the complete argument set and must stay aligned with file-open behavior.

Test signals: Cover no arguments, `"-"` inputs, stdout terminal refusal, stdin terminal refusal for decompression/test, `--files` from stdin conflict, long filename entries, embedded NUL in `--files`, `--files0` consecutive delimiters, list-mode totals, `--robot` rejection outside list/info/version, warning suppression, and signal exit behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/main.h -->
## sources/compression/xz/src/xz/main.h

Purpose: Declares process exit-status values and mutators.

Important APIs and types: `enum exit_status_type` matches gzip/bzip2-compatible codes: success 0, error 1, warning 2. `set_exit_status()` records warning/error status, and `set_exit_no_warn()` allows warnings to exit as success.

Control flow and integration: `message_warning()` and `message_error()` update status through this API. `args.c` calls `set_exit_no_warn()` for `--no-warn`. `main.c` reads the final status at shutdown.

State and persistence: State is private to `main.c` and persists for the whole process.

Risks: Only warning and error are valid inputs to `set_exit_status()`; assertions catch misuse in debug builds. Windows signal handling requires synchronized access in `main.c`.

Test signals: Validate that warnings do not override errors, `--no-warn` maps warning-only runs to success, and fatal errors exit immediately.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/message.c -->
## sources/compression/xz/src/xz/message.c

Purpose: Handles diagnostics, verbosity, progress display, help/version/filter-help output, liblzma return-code messages, and memory/filter reporting.

Important APIs and functions: Public API includes `message_init()`, verbosity setters/getter, `message_set_files()`, `message_filename()`, progress start/update/end, `message()`, `message_warning()`, `message_error()`, `message_fatal()`, `message_bug()`, `message_signal_handler()`, `message_strm()`, `message_mem_needed()`, `message_filters_show()`, `message_try_help()`, `message_version()`, `message_help()`, and `message_filters_help()`. Progress helpers compute percentage, size/ratio, speed, elapsed time, ETA, and positions via `lzma_get_progress()`.

Control flow: `main.c` initializes messages before parsing and processing. Each file calls `message_filename()`, then `coder_run()` starts progress with the active `lzma_stream`, periodically calls `message_progress_update()`, and ends progress. Diagnostics call `vmessage()`, which blocks signals and flushes any active progress line before printing. Help, version, and filter-help functions print to stdout and exit.

State and persistence: Static state tracks current file index/total, verbosity, current filename, whether filenames/progress have printed, terminal-based automatic progress mode, progress stream pointer, passthrough flag, expected input size, signal-triggered update flag or polling timestamp. No persistent storage is written.

Dependencies and integration points: Uses `mytime.c` for elapsed timing, `hardware.c` for memlimit display, `main.c` for exit status, `signals.c` for output atomicity, liblzma progress and filter string APIs, `tuklib` wrapping/multibyte/nonprint helpers, `opt_mode`, `opt_robot`, and `stdin_filename`.

Risks: Progress state assumes one active coder at a time and a valid `lzma_stream` until `message_progress_end()`. `SIGALRM` paths must reset update flags before scheduling the next alarm. Help text wrapping is translation-sensitive. Robot version output is machine-readable and should not be casually changed. `message_mem_needed()` reports the generic hard mode limit, so callers must choose context carefully.

Test signals: Exercise verbosity levels, quiet twice, progress on TTY and non-TTY, SIGALRM/SIGUSR1/SIGINFO progress trigger, passthrough progress, diagnostics during active progress, all `lzma_ret` mappings, memlimit formatting below/above MiB and disabled, help/long-help/filter-help wrapping, robot version output, and translation-width fallbacks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/message.h -->
## sources/compression/xz/src/xz/message.h

Purpose: Declares the messaging, verbosity, progress, help, and liblzma error-reporting interface.

Important APIs and types: `enum message_verbosity` defines silent, error, warning, verbose, and debug levels. The header exports progress signal list, initialization, verbosity controls, formatted message variants with printf attributes, fatal/bug/signal helpers, `message_strm()`, memory/filter display, help/version functions, file count/name registration, and progress lifecycle calls.

Control flow and integration: All modules use this API for diagnostics. `coder.c` owns the progress lifecycle. `main.c` initializes messages and sets file counts. `args.c`, `hardware.c`, `file_io.c`, `list.c`, `sandbox.c`, and `options.c` call fatal/error/warning helpers.

State and persistence: State is internal to `message.c`; callers must only respect progress start/end pairing.

Risks: Format-string attributes help compile-time checking, but translated strings and variadic calls still need care. `message_progress_start()` must follow `message_filename()` and must end before the stream becomes invalid.

Test signals: Compile with format warnings, run progress lifecycle tests, and verify message calls update exit status through `main.c` as expected.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/mytime.c -->
## sources/compression/xz/src/xz/mytime.c

Purpose: Provides portable millisecond timing for progress reporting, SIGTSTP pause accounting, and `--flush-timeout` scheduling.

Important APIs and functions: Exports `opt_flush_timeout`, `mytime_set_start_time()`, `mytime_get_elapsed()`, `mytime_set_flush_time()`, `mytime_get_flush_timeout()`, and optional `mytime_sigtstp_handler()`. Internal `mytime_now()` chooses `GetTickCount64()`, `clock_gettime()`, or `gettimeofday()` depending on platform and threading configuration.

Control flow: `coder_run()` calls `mytime_set_start_time()` just before processing a file. `message.c` calls `mytime_get_elapsed()` for progress. `io_read()` calls `mytime_set_flush_time()` when first input arrives after a flush and uses `mytime_get_flush_timeout()` as the `poll()` timeout for nonblocking input. Optional SIGTSTP handling shifts `start_time` forward by stopped duration.

State and persistence: Static `start_time` and `next_flush` live for the process. `opt_flush_timeout` is set by `args.c`. There is no external persistence.

Dependencies and integration points: Uses `signals_block()`/`signals_unblock()` when SIGTSTP handler support makes `start_time` asynchronously mutable. Reads `opt_mode` to make flush timeouts compression-only.

Risks: `gettimeofday()` fallback is not monotonic, so wall-clock changes can affect progress/flush timing. SIGTSTP handling uses `SIGSTOP` and has documented POSIX caveats. Very large timeout values are capped to `INT_MAX` for `poll()`.

Test signals: Cover timing backends by platform, flush timeout disabled/enabled, immediate timeout, large timeout cap, compression-only behavior, progress elapsed after start, and SIGTSTP pause adjustment where supported.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/mytime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/mytime.h -->
## sources/compression/xz/src/xz/mytime.h

Purpose: Declares timing and flush-timeout functions.

Important APIs: Exports mutable `opt_flush_timeout`, optional SIGTSTP handler, start-time setter, elapsed-time getter, flush-time setter, and `poll()` timeout getter.

Control flow and integration: `args.c` sets `opt_flush_timeout`; `coder.c`, `message.c`, `file_io.c`, and `signals.c` consume the timing API.

State and persistence: State is private to `mytime.c` except for the exported timeout option.

Risks: The header documents "start time is also stored as the time of the first flush"; implementation currently sets operation start while first flush scheduling is updated when input is seen, so readers should verify behavior before relying on that wording.

Test signals: Build with and without `USE_SIGTSTP_HANDLER`; verify flush timeout integration with nonblocking reads.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/mytime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/options.c -->
## sources/compression/xz/src/xz/options.c

Purpose: Parses filter-specific option strings for Delta, BCJ, LZMA1, and LZMA2 old-style filter options.

Important APIs and functions: Public parsers are `options_delta()`, `options_bcj()`, and `options_lzma()`, each returning an allocated liblzma option struct. Internal `parse_options()` splits comma-separated `name=value` entries, validates option names, maps string values or bounded integer values, and dispatches to filter-specific setters. `set_delta()`, `set_bcj()`, and `set_lzma()` mutate option structs. `error_lzma_preset()` handles invalid preset strings.

Control flow: `args.c` invokes these functions when parsing `--delta`, BCJ filters, `--lzma1`, and `--lzma2`, then passes returned option pointers to `coder_add_filter()`. `coder.c` owns eventual filter-chain cleanup for dynamically allocated filter options.

State and persistence: Functions allocate option structs with `xmalloc()` and return ownership to the filter chain. There is no static parser state.

Dependencies and integration points: Uses liblzma option constants and `lzma_lzma_preset()`, `str_to_uint64()` for numeric parsing, and `message_fatal()` for validation failures. Complements newer `--filters` string parsing handled directly in `coder.c` through liblzma.

Risks: The generic parser does not support escaping or quoted commas. Optional filter arguments with null/empty strings keep defaults. LZMA `lc + lp <= 4` is validated here; other semantic validation occurs later through liblzma memory usage or encoder init. Returned allocations must remain valid for the lifetime of the filter chain.

Test signals: Cover empty option strings, missing values, invalid option names, invalid map values, bounds for delta distance, BCJ start offset, LZMA dict/lc/lp/pb/nice/depth, preset `0-9` and `e`, bad preset modifiers, and `lc + lp` overflow.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/options.h -->
## sources/compression/xz/src/xz/options.h

Purpose: Declares old-style filter option parsers.

Important APIs: `options_delta()`, `options_bcj()`, and `options_lzma()` return allocated `lzma_options_delta`, `lzma_options_bcj`, and `lzma_options_lzma` structures respectively, exiting on invalid input.

Control flow and integration: `args.c` calls these parser functions while assembling custom filter chains for `coder.c`.

State and persistence: The allocated return values become filter-chain option pointers and persist until filter cleanup or process exit.

Risks: Callers must treat returned pointers as owned by the filter chain and not stack-allocate substitutes with shorter lifetime.

Test signals: Integration tests through CLI old-style filter options and debug cleanup with leak checking.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/private.h -->
## sources/compression/xz/src/xz/private.h

Purpose: Central private include for the xz command-line front-end implementation.

Important contents: Includes generated/system definitions, threading abstraction, liblzma, common POSIX/stdio headers, gettext/progname/exit/multibyte tuklib helpers, Windows headers when needed, stdio descriptor fallbacks, `USE_SIGTSTP_HANDLER` feature detection, and all local module headers (`main`, `mytime`, `coder`, `message`, `args`, `hardware`, `file_io`, `options`, `sandbox`, `signals`, `suffix`, `util`, optional `list`).

Control flow and integration: Nearly every `.c` file in this set includes `private.h`, making it the compile-time dependency hub and enforcing header ordering.

State and persistence: No runtime state, but it defines macros and declarations that shape runtime behavior, especially SIGTSTP support and Windows descriptor compatibility.

Risks: Include-order changes can break dependencies such as `hardware.h` needing `enum operation_mode`, list declarations only with decoders, or Windows macro setup before `windows.h`. Broad inclusion increases rebuild and coupling.

Test signals: Build matrix across POSIX, Windows/MSVC, MinGW, decoder/encoder disabled, threading enabled/disabled, SIGALRM/SIGTSTP availability, and NLS/multibyte configurations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/sandbox.c -->
## sources/compression/xz/src/xz/sandbox.c

Purpose: Implements optional platform sandboxing for OpenBSD pledge, Linux Landlock, and FreeBSD Capsicum.

Important APIs and functions: Public functions are `sandbox_init()`, `sandbox_enable_read_only()`, `sandbox_allow_strict()`, and `sandbox_enable_strict_if_allowed()`. `prepare_for_strict_sandbox()` preloads translation, strerror, and multibyte/iconv resources and checks whether strict mode was allowed. Landlock support uses `enable_landlock()` to build a restrictive ruleset minus required rights.

Control flow: `main.c` calls `sandbox_init()` early when enabled. After argument parsing, if operation is stdout-only/test/list/read-only, `main.c` calls `sandbox_enable_read_only()` and may call `sandbox_allow_strict()` for exactly one source to stdout. `file_io.c` calls `sandbox_enable_strict_if_allowed()` after opening the source and creating the abort pipe, so strict sandboxing can deny future opens.

State and persistence: Static `strict_sandbox_allowed` gates strict mode. Sandbox effects persist at kernel/process level and are intentionally irreversible.

Dependencies and integration points: Depends on platform feature macros from `sandbox.h`, `private.h`, `message_fatal()`, file descriptors from `file_io.c`, and Landlock helper wrappers. Pledge profiles distinguish full initial access, read-only access, and strict stdio-only access. Capsicum limits rights on source/stdin/stdout/stderr and abort pipe fds.

Risks: Strict sandboxing can fail if locale, gettext, iconv, or other lazy-loaded files were not preloaded. Landlock ABI differences require careful rights masks. Capsicum silently ignores ENOSYS but fatals on other failures. Error messages in `sandbox_init()` are intentionally untranslated because gettext is not initialized yet.

Test signals: Run on OpenBSD, Linux with/without Landlock and different ABI versions, FreeBSD with/without Capsicum, stdout-only compression/decompression/test/list, one-file strict mode, `--files` disabling strict mode, and locale/translations under strict sandbox.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/sandbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/sandbox.h -->
## sources/compression/xz/src/xz/sandbox.h

Purpose: Declares sandbox feature detection and public sandbox lifecycle functions.

Important APIs: Defines `ENABLE_SANDBOX` when pledge, Linux Landlock, or Capsicum support is configured. Declares early `sandbox_init()`, read-only `sandbox_enable_read_only()`, strict-mode permission flag `sandbox_allow_strict()`, and `sandbox_enable_strict_if_allowed(src_fd, pipe_event_fd, pipe_write_fd)`.

Control flow and integration: `main.c` controls early and read-only sandbox phases; `file_io.c` invokes strict mode after source open. The pipe fd parameters tie strict sandboxing to the self-pipe signal design in `file_io.c`.

State and persistence: Runtime state is internal to `sandbox.c`; process sandbox restrictions persist after enabling.

Risks: Consumers must pass valid fds and only call strict enable after all future file opens are unnecessary. The macro enables code paths in multiple modules, so build coverage is important.

Test signals: Compile with each sandbox backend and without sandbox support; exercise read-only and strict transitions through CLI modes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/sandbox.h -->
