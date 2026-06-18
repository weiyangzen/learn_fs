# subset-b-000294 Research

Grouped research report for the subset B work item. Each section preserves the original source path and is wrapped with file-specific reconciliation markers so it can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/signals.c -->
# sources/compression/xz/src/xz/signals.c

Purpose: implements process signal handling for the full `xz` command so long operations can be interrupted, incomplete output can be cleaned up, and the process can finally exit with the original terminating signal where the platform supports it.

Important APIs and functions: exports `user_abort`, `signals_init()`, `signals_block()`, `signals_unblock()`, and `signals_exit()` from `signals.h`. POSIX builds install `signal_handler()` for `SIGINT`, `SIGTERM`, optional `SIGHUP`, `SIGPIPE`, `SIGXCPU`, and `SIGXFSZ`; optional progress and `SIGTSTP` handlers are also folded into the blocked-signal mask. Native Windows uses `SetConsoleCtrlHandler()` instead of C signals.

Control flow: `signals_init()` builds `hooked_signals`, skips signals already ignored by the parent, installs handlers without `SA_RESTART`, and marks the subsystem initialized. The handler records `exit_signal`, sets `user_abort`, and notifies the user-abort pipe on non-DOS-like systems. `signals_block()` and `signals_unblock()` maintain a recursive block count around `mythread_sigmask()`. `signals_exit()` resets the original signal to default and re-raises it after cleanup.

State and persistence: process-local global state includes `user_abort`, `exit_signal`, `hooked_signals`, `signals_are_initialized`, and `signals_block_count`. No persistent files are written here, but this module directly affects cleanup decisions elsewhere by flipping `user_abort`.

Dependencies and integration: depends on `private.h`, message reporting, `io_write_to_user_abort_pipe()`, `mythread_sigmask()`, `set_exit_status()`, and optional `mytime_sigtstp_handler()`. It integrates with I/O loops that poll `user_abort` and with final process termination in `main()`.

Risks: async-signal-safety is central; the handler only updates atomics and writes to a pipe. The recursive signal block counter is not thread-safe by itself and assumes disciplined pairing. Platform branches change semantics: Windows cannot re-raise the original signal, while POSIX does. Calling block/unblock before initialization is intentionally a no-op.

Test signals: this file is not directly unit-tested in this subset. Coverage is indirect through command interruption behavior, I/O cleanup paths, and platform builds. Regression focus should include EINTR handling, nested block/unblock balance, ignored-parent-signal preservation, and exit status/signal propagation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/signals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/signals.h -->
# sources/compression/xz/src/xz/signals.h

Purpose: public internal header for the `xz` command signal-abort subsystem.

Important APIs and types: declares the volatile `sig_atomic_t user_abort` flag, `signals_init()`, optional `signals_block()`/`signals_unblock()`, and optional `signals_exit()`. On native Windows and VMS, block/unblock are compiled as no-op macros. On native Windows, `signals_exit()` is also a no-op macro because `signals.c` cannot preserve and re-raise a POSIX-style signal number.

Control flow and integration: consumers initialize handlers early with `signals_init()`, poll `user_abort` from long-running compression/decompression loops, use block/unblock around critical regions that should not be interrupted by handled signals, and call `signals_exit()` after cleanup to preserve signal termination semantics on POSIX.

State and persistence: no state is defined here besides the external `user_abort` declaration. The header controls platform-specific API availability through preprocessor macros.

Dependencies: requires signal-related types to be visible through the command's shared private headers before inclusion. It is part of the internal `src/xz` API, not liblzma's public API.

Risks: platform no-op macros mean callers must not rely on block/unblock for correctness on Windows or VMS. Callers must treat `user_abort` as a poll-only signal flag and avoid using it as a substitute for immediate cleanup in unsafe contexts.

Test signals: validation is mostly compile- and integration-level. Useful checks are platform builds that verify declarations/macros match `signals.c`, plus command tests that abort during reads, writes, and output-file cleanup.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/signals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/suffix.c -->
# sources/compression/xz/src/xz/suffix.c

Purpose: derives output filenames for compression and decompression in the full `xz` command, including built-in suffix rules, custom `--suffix`, format-specific defaults, and DOS 8.3 short-filename behavior.

Important functions: `suffix_get_dest_name()` is the exported entry point and dispatches to `compressed_name()` or `uncompressed_name()` based on global `opt_mode`. `suffix_set()` validates and stores `custom_suffix`; `suffix_is_set()` reports whether it exists. Internal helpers include `test_suffix()`, `msg_suffix()`, `is_dir_sep()`, `has_dir_sep()`, and DJGPP-only `has_sfn_suffix()`.

Control flow: decompression tests known compressed suffixes such as `.xz`, `.txz`, `.lzma`, `.tlz`, optional `.lz`, and DJGPP `.lzm`/short suffixes, then falls back to the custom suffix. Compression selects the suffix table from `opt_format`, rejects already-compressed names, handles `.tar` abbreviations, and appends or replaces suffixes. DJGPP adds short-filename truncation and special dash suffix policy.

State and persistence: owns one process-global heap string, `custom_suffix`, replacing it on each `suffix_set()`. Destination names are heap-allocated and returned to the caller. It does not write files.

Dependencies and integration: depends on global command options from `private.h`/coder state (`opt_mode`, `opt_format`), `xmalloc()`, `xstrdup()`, message warning/fatal APIs, gettext, and nonprint masking. It integrates with file-opening code that needs a destination path before creating output.

Risks: path separator handling differs on DOS-like systems and VMS; custom suffixes with separators are rejected to avoid path injection. Incorrect suffix-table order would change user-visible naming, especially `.txz`/`.tlz`. The raw format requires a custom suffix or stdout, so callers must enforce that higher-level rule.

Test signals: the tests list includes `test_suffix.sh` in `Makefile.am`, although it is outside this work item. Compression shell tests indirectly exercise default suffix-free stdout behavior; filename edge cases need dedicated CLI coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/suffix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/suffix.h -->
# sources/compression/xz/src/xz/suffix.h

Purpose: internal header for `xz` filename suffix policy.

Important APIs: declares `suffix_get_dest_name(const char *)`, `suffix_set(const char *)`, and `suffix_is_set(void)`. `suffix_get_dest_name()` returns a newly allocated destination filename or `NULL` after printing a warning; `suffix_set()` copies the supplied suffix and may terminate via `message_fatal()` if the suffix is invalid.

Control flow and integration: callers configure optional suffix policy once through `suffix_set()`, then ask for a destination path per input file. The result depends on global command mode and format in `suffix.c`; the header deliberately does not expose those globals.

State and persistence: hides the `custom_suffix` allocation behind the three functions. No persistent state exists outside process memory.

Dependencies: consumers need standard `bool` and command-private memory/message conventions. The allocation contract means callers must free successful return values.

Risks: the API depends on side-effectful global options rather than explicit mode arguments, so call order matters. `suffix_set()` being fatal on invalid data is appropriate for option parsing but unsuitable for non-fatal validation use.

Test signals: suffix CLI tests should verify custom suffix replacement, invalid empty/path suffixes, compression suffix collision warnings, and decompression unknown-suffix skipping.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/suffix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/util.c -->
# sources/compression/xz/src/xz/util.c

Purpose: provides utility routines for the full `xz` command: fatal allocation wrappers, numeric option parsing, human-readable formatting, bounded string construction, and terminal detection.

Important APIs: implements `xrealloc()`, `xstrdup()`, `str_to_uint64()`, `round_up_to_mib()`, `uint64_to_str()`, `uint64_to_nicestr()`, `my_snprintf()`, `is_tty()`, `is_tty_stdin()`, and `is_tty_stdout()`. The formatting functions share four static 128-byte buffers indexed by caller-supplied slot.

Control flow: allocation failures free the old pointer before `message_fatal()` to increase the chance that diagnostics can allocate memory. `str_to_uint64()` manually parses non-negative decimal text, accepts `"max"`, supports binary `K/M/G` suffix variants, checks overflow before each multiply/add, and enforces `[min, max]`. Formatting probes thousands-separator support at runtime except on known-broken platforms. TTY wrappers report user-facing errors for terminal stdin/stdout.

State and persistence: state is process-local: `bufs[4][128]` and a cached thousand-separator status. No persistent files are affected.

Dependencies and integration: depends on `private.h`, gettext/message helpers, `tuklib_mask_nonprint()`, libc allocation and formatting, POSIX `isatty()`, and Windows console APIs. It is used throughout option parsing, progress/status output, and safety checks that prevent binary data from being read from or written to terminals.

Risks: static buffers are not thread-safe and are overwritten by subsequent calls using the same slot. `xmalloc`/`xrealloc` must not be used while incomplete output needs cleanup, as documented in `util.h`. Locale-dependent thousands formatting is probed defensively but still depends on `snprintf()` behavior.

Test signals: no direct unit test in this subset. Indirect coverage comes through command option parsing, memlimit strings, messages, and shell tests. High-value tests would include overflow suffix parsing, malformed suffix diagnostics, Windows TTY handling, and buffer truncation behavior in `my_snprintf()`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xz/util.h -->
# sources/compression/xz/src/xz/util.h

Purpose: declares miscellaneous utility functions and formatting enums for the full `xz` command.

Important APIs and types: defines `xmalloc(size)` as `xrealloc(NULL, size)`, declares `xrealloc()`, `xstrdup()`, `str_to_uint64()`, `round_up_to_mib()`, `uint64_to_str()`, `uint64_to_nicestr()`, `my_snprintf()`, `is_tty()`, `is_tty_stdin()`, and `is_tty_stdout()`. `enum nicestr_unit` controls minimum and maximum display units from bytes through TiB.

Control flow and integration: the header documents fatal behavior for allocation and numeric parsing helpers. Formatting APIs return pointers to shared internal buffers selected by a slot. Terminal helpers centralize CLI safety policy for stdin/stdout.

State and persistence: no state is defined here, but the comments document hidden static buffers in `util.c` and the cleanup hazard of fatal allocation wrappers.

Dependencies: uses liblzma attributes such as `lzma_attr_alloc_size` and printf-format annotations. Consumers must include the command's common type setup first.

Risks: misuse of `xmalloc()` while output cleanup is required can bypass cleanup because failures are fatal. Reusing formatting slots can overwrite strings before they are printed. `my_snprintf()` silently stops appending after truncation or formatting error by setting `left` to zero.

Test signals: compile coverage plus integration tests for option parsing and terminal checks. Focused tests should validate the documented allocation and static-buffer contracts.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xz/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xzdec/Makefile.am -->
# sources/compression/xz/src/xzdec/Makefile.am

Purpose: Automake build definition for the small `xzdec` and `lzmadec` decompressor binaries and their man-page installation behavior.

Important build targets and variables: defines shared sources (`xzdec.c`, `tuklib_progname.c`, `tuklib_mbstr_nonprint.c`, `tuklib_exit.c`), optional Windows resource files, `xzdec_CPPFLAGS`, `xzdec_LDADD`, and `lzmadec_*` aliases. `lzmadec` is built from the same C file with `-DLZMADEC`. Conditional `bin_PROGRAMS` entries depend on `COND_XZDEC` and `COND_LZMADEC`.

Control flow: the `.rc.o` rule compiles Windows resources. Build flags disable gettext in tuklib for the tiny tools and include common/liblzma API headers. Optional gnulib and intl libraries are linked. Install hooks install translated `xzdec.1` man pages when available and create `lzmadec.1` symlinks only when both tools are enabled and the target man page exists.

State and persistence: affects generated build artifacts, installed binaries, installed man pages, and symlinks. It does not define runtime state.

Dependencies and integration: integrates with top-level configure conditionals, liblzma, optional gnulib, Windows resource compiler, NLS man-page directories, and Automake install/uninstall hooks.

Risks: the install hook intentionally uses Automake internals by overriding man variables, so Automake changes could break it. The symlink logic must honor transformed program names and avoid dangling links. `lzmadec` inherits most `xzdec` settings, so link flag changes must remain compatible with both formats.

Test signals: build-system validation should cover `--enable/disable-xzdec`, `--enable/disable-lzmadec`, Windows resources, NLS man-page installs, and uninstall cleanup.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xzdec/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/xzdec/xzdec.c -->
# sources/compression/xz/src/xzdec/xzdec.c

Purpose: implements the tiny single-threaded `xzdec`/`lzmadec` command that only decompresses to stdout and never deletes input files.

Important functions: `main()`, `parse_options()`, `uncompress()`, `my_errorf()`, `help()`, `version()`, and optional `sandbox_enter()`. `TOOL_FORMAT` and decoder choice switch between `.xz` stream decoding and `.lzma` alone decoding using `LZMADEC`.

Control flow: `main()` initializes program name, locale, optional sandbox prerequisites, parses options, sets binary mode on DOS-like systems, and reuses one `lzma_stream` across all input files. Each file is opened, optionally enters a strict sandbox for the last file, then `uncompress()` streams BUFSIZ chunks through `lzma_code()` and writes BUFSIZ output chunks to stdout. `.xz` uses `LZMA_CONCATENATED` and `LZMA_FINISH` at EOF; `.lzma` manually rejects trailing garbage after `LZMA_STREAM_END`.

State and persistence: process-local `display_errors` is decremented by `-q` and affects diagnostics and final `tuklib_exit()`. The reused `lzma_stream` preserves allocations between files but is reset by decoder initialization. No output files are created; stdout is the only data sink.

Dependencies and integration: depends on liblzma, tuklib program-name/nonprint/exit helpers, bundled getopt, optional Capsicum, OpenBSD `pledge()`, and Linux Landlock. Test scripts use this binary as an independent decoder oracle when built.

Risks: all decoding exits immediately on first read, write, allocation, or data error. On native Windows broken pipe can appear as `EINVAL` and suppresses an error message. The strict sandbox is only entered for the final named file so earlier files can still be opened.

Test signals: `test_compress.sh` compares `xzdec` decompression output against original generated inputs when `xzdec` exists. `test_files.sh` feeds good, bad, and unsupported `.xz` files to `xzdec`, with special handling for unsupported checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/xzdec/xzdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/Makefile.am -->
# sources/compression/xz/tests/Makefile.am

Purpose: Automake test-suite definition for liblzma, command, generated-file, script, and optional MicroLZMA tests.

Important variables: `EXTRA_DIST` packages fixtures and scripts; `AM_CPPFLAGS` points tests at common and liblzma headers; `LDADD` links liblzma plus optional intl and Windows resources. `check_PROGRAMS` lists C test binaries and `TESTS` defines the executable test order for Automake.

Control flow: all core C tests are built as check programs. Shell tests cover known files, suffixes, generated compression files, and optionally scripts. `test_microlzma` is conditional on `COND_MICROLZMA`; `test_scripts.sh` is conditional on `COND_SCRIPTS`. `clean-local` removes generated compression fixtures and xzgrep temporaries.

State and persistence: test runs create generated files (`compress_generated_*`) and temporary outputs in the tests build directory, then clean selected artifacts.

Dependencies and integration: integrates with configure feature macros, liblzma build artifacts, optional Windows resources, Automake's parallel test harness, and shell scripts that locate built binaries relative to the build tree.

Risks: feature-disabled builds may skip tests or execute only partial assertions, so coverage depends on configure flags. Generated compression files are cached to avoid repeated creation, which is efficient but can hide stale-fixture issues unless cleaned.

Test signals: this file is the top-level signal for which tests are expected in normal `make check`. It explicitly includes the files researched in this subset and shows which behavior has C-level versus shell-level coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/code_coverage.sh -->
# sources/compression/xz/tests/code_coverage.sh

Purpose: convenience script to configure and run xz tests with gcov-style coverage flags, then generate HTML coverage reports with `lcov` and `genhtml`.

Important behavior: validates that `lcov` and `genhtml` exist, derives `top_srcdir` from the script location, runs `autogen.sh` if `configure` is missing, configures the current directory if no `Makefile` exists, runs `make "$@" check`, captures coverage for `src/liblzma` and `src/xz`, and writes reports under `coverage/liblzma` and `coverage/xz`.

Control flow: `set -e` makes failures abort. The configure invocation disables `xzdec`, `lzmadec`, and `lzmainfo`, disables shared libraries, enables silent rules, and appends `--coverage --no-inline -O0` to `CFLAGS` to improve coverage fidelity.

State and persistence: creates or overwrites a local `coverage/` directory, may generate configure/build files, and runs the test suite in the current build directory.

Dependencies and integration: depends on Autotools, make, lcov, genhtml, compiler coverage support, and the xz test suite. It is developer tooling, not part of installed runtime.

Risks: because it disables xzdec/lzmadec, coverage for the lightweight decoder path is intentionally absent. It removes `coverage/` unconditionally. Existing `CFLAGS` are preserved but appended, which can interact with user-supplied flags.

Test signals: successful completion prints file URLs to both HTML reports. Failures identify missing coverage tools, configure/test failures, or lcov/genhtml errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/code_coverage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/create_compress_files.c -->
# sources/compression/xz/tests/create_compress_files.c

Purpose: generates deterministic input files used by compression/decompression round-trip tests, reducing source package size by avoiding checked-in large fixtures.

Important functions and macros: `maybe_create_test()` conditionally creates one named fixture; `file_exists()`, `file_create()`, and `file_finish()` provide portable file handling; `write_abc()`, `write_random()`, and `write_text()` generate the three data profiles. `main()` creates all files or only the requested `compress_generated_<name>`.

Control flow: the generator skips existing files, supports one optional filename argument, writes to `compress_generated_abc`, `compress_generated_random`, and `compress_generated_text`, and exits nonzero on I/O failure. `write_random()` uses a fixed linear congruential sequence for reproducibility. `write_text()` emits one original lorem paragraph followed by deterministic randomized word sequences.

State and persistence: writes generated fixture files in the current tests build directory. There is no persistent internal state beyond deterministic seeds.

Dependencies and integration: used by `test_compress.sh` when a `compress_generated_*` test is requested. Depends only on `sysdefs.h` and stdio, making it portable across the supported test environments.

Risks: `maybe_create_test()` only compares `argv[1]`, so it intentionally supports one selected fixture at a time. Existing fixture files are trusted and not regenerated unless cleaned, which can leave stale/corrupt files after interrupted runs.

Test signals: downstream shell tests compress/decompress each generated profile with multiple presets and filters, so this generator's correctness is observed through round-trip comparisons.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/create_compress_files.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/Makefile -->
# sources/compression/xz/tests/ossfuzz/Makefile

Purpose: minimal OSS-Fuzz build recipe for fuzz targets in the `tests/ossfuzz` directory.

Important targets: `FUZZ_TARGET_SRCS` discovers all `.c` files, `FUZZ_TARGET_BINS` strips suffixes, `all` builds each target, pattern rule `%: %.c` compiles C to object with liblzma API includes and links with `$(CXX)`, `$(LIB_FUZZING_ENGINE)`, and static `liblzma.a`. `clean` removes local objects but leaves binaries under `$(OUT)`.

Control flow: OSS-Fuzz supplies compiler variables, fuzzing engine, and `OUT`. Each target is built independently from one C file plus shared header code.

State and persistence: creates object files in the source directory and fuzz target binaries in `$(OUT)`. `clean` intentionally does not remove `$(OUT)` artifacts because the fuzzing framework owns them.

Dependencies and integration: depends on a prebuilt `../../src/liblzma/.libs/liblzma.a`, liblzma API headers, and OSS-Fuzz environment variables.

Risks: wildcard discovery will build every `.c` file in the directory; adding helper `.c` files would accidentally create targets. The Makefile assumes liblzma has already been built in the expected relative path.

Test signals: successful build produces one binary per fuzz source. Runtime signal comes from fuzzers aborting on `LZMA_PROG_ERROR` or target initialization failures.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_common.h -->
# sources/compression/xz/tests/ossfuzz/fuzz_common.h

Purpose: shared helper code for liblzma OSS-Fuzz targets, especially chunked execution of `lzma_code()` with bounded memory.

Important constants and functions: `MEM_LIMIT` is 300 MiB to prevent pathological allocations from fuzzed headers. `IN_CHUNK_SIZE` is 2047 bytes. `fuzz_code(lzma_stream *, const uint8_t *, size_t)` feeds input through a prepared encoder or decoder and discards output into a 4096-byte stack buffer.

Control flow: `fuzz_code()` starts by giving half the input to the stream, then feeds remaining data in chunks. When input is exhausted it switches to `LZMA_FINISH`; when the output buffer fills it resets and overwrites it. The loop stops on any `lzma_code()` return other than `LZMA_OK`; `LZMA_PROG_ERROR` is treated as a target or library bug and aborts.

State and persistence: no persistent state. The function mutates the supplied `lzma_stream` and local input pointers only.

Dependencies and integration: included by decode and encode fuzz targets after they initialize the appropriate liblzma coder. Depends on `lzma.h`, stdint/inttypes, stdlib, and stdio.

Risks: the helper does not assert semantic success; it is designed to find crashes, memory errors, and illegal program-error returns. The unusual half-input first call improves state-machine coverage but must not be mistaken for normal streaming policy.

Test signals: fuzzer failures are crashes, sanitizer reports, or explicit abort on `LZMA_PROG_ERROR`.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_alone.c -->
# sources/compression/xz/tests/ossfuzz/fuzz_decode_alone.c

Purpose: OSS-Fuzz target for legacy `.lzma` "alone" decoding through liblzma.

Important API: exposes `LLVMFuzzerTestOneInput(const uint8_t *, size_t)`. It initializes `lzma_stream` with `lzma_alone_decoder(&strm, MEM_LIMIT)`, passes the fuzzer input to `fuzz_code()`, then calls `lzma_end()`.

Control flow: initialization failures are considered unexpected except for extreme environment exhaustion, so the target prints the return code and aborts. Decode results other than `LZMA_PROG_ERROR` are allowed by `fuzz_code()` because malformed fuzz input is normal.

State and persistence: allocates decoder state inside `lzma_stream` and releases it every fuzz iteration. No persistent state exists.

Dependencies and integration: depends on `fuzz_common.h`, `lzma.h`, and OSS-Fuzz's `LLVMFuzzerTestOneInput` ABI. It exercises the `.lzma` decoder independently from `.xz` container parsing.

Risks: `MEM_LIMIT` must stay low enough for fuzzing infrastructure yet high enough to reach meaningful decoder states. Aborting on initialization failure may expose environment setup problems as crashes.

Test signals: sanitizer findings, crashes, and `LZMA_PROG_ERROR` aborts are meaningful. Successful fuzz cases return zero regardless of normal decode errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_alone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_stream.c -->
# sources/compression/xz/tests/ossfuzz/fuzz_decode_stream.c

Purpose: OSS-Fuzz target for single-threaded `.xz` stream decoding.

Important API: `LLVMFuzzerTestOneInput()` initializes `lzma_stream_decoder(&strm, MEM_LIMIT, flags)` and delegates execution to `fuzz_code()`. The flags include concatenated-stream handling and, when built for fuzzing, options that can relax checksum work to improve fuzz throughput.

Control flow: malformed inputs are expected and simply drive liblzma to non-OK returns. Initialization errors are printed and abort. After fuzz execution, `lzma_end()` releases state.

State and persistence: per-call stream state only. No output is retained; decompressed data is discarded by the common helper.

Dependencies and integration: covers xz container parsing, stream headers/footers, blocks, indexes, checks, and filter initialization reachable through the public decoder.

Risks: fuzzing with reduced check behavior can miss checksum-specific bugs, but it expands structural coverage. The 300 MiB limit bounds adversarial dictionary sizes.

Test signals: crashes, sanitizer reports, and unexpected `LZMA_PROG_ERROR` aborts. It complements deterministic tests like `test_files.sh`, `test_stream_flags.c`, and `test_index.c`.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_stream_mt.c -->
# sources/compression/xz/tests/ossfuzz/fuzz_decode_stream_mt.c

Purpose: OSS-Fuzz target for multithread-capable `.xz` stream decoding through `lzma_stream_decoder_mt()`.

Important API and configuration: `LLVMFuzzerTestOneInput()` sets up an `lzma_mt` struct with bounded threading and stop memory limits derived from `MEM_LIMIT`, initializes `lzma_stream_decoder_mt()`, runs `fuzz_code()`, and ends the stream.

Control flow: like the single-threaded stream fuzzer, it accepts arbitrary decode errors but aborts on initialization failure or `LZMA_PROG_ERROR`. The common helper feeds input in partial chunks and switches to `LZMA_FINISH` at the end.

State and persistence: per-iteration decoder/threading state only. No persistent state or output files.

Dependencies and integration: exercises threaded decoder paths, block scheduling, and memory-limit behavior that deterministic tests also touch in `test_check.c` and `test_memlimit.c`.

Risks: actual concurrency behavior depends on liblzma build options and OSS-Fuzz runtime. Memory limits are split between threading and stop conditions; setting them too low would reduce state coverage.

Test signals: thread sanitizer and address sanitizer reports are especially useful here, along with explicit aborts on program errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_decode_stream_mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_encode_stream.c -->
# sources/compression/xz/tests/ossfuzz/fuzz_encode_stream.c

Purpose: OSS-Fuzz target for `.xz` stream encoding with LZMA2 presets.

Important API: `LLVMFuzzerTestOneInput()` uses the first input byte as a preset selector, initializes `lzma_options_lzma`, creates a two-entry filter chain (`LZMA_FILTER_LZMA2`, terminator), starts `lzma_stream_encoder()` with `LZMA_CHECK_CRC64`, and passes the remaining bytes to `fuzz_code()`.

Control flow: empty input returns after printing a diagnostic. Only selected decider values are accepted to guide coverage toward valid preset levels: 0, 1, 5, and extreme variants derived from 6 and 7. Preset or encoder initialization failure aborts. All encoded output is discarded.

State and persistence: per-call encoder state only. It does not persist corpora or output streams.

Dependencies and integration: covers LZMA2 encoding, stream encoding, check generation, and action handling through the shared chunked helper.

Risks: the target deliberately limits the option space to presets, so it does not fuzz arbitrary filter-chain parsing or custom LZMA parameters. It still exercises critical compression paths with fuzzed payload bytes.

Test signals: crashes, sanitizer reports, and `LZMA_PROG_ERROR` aborts. Deterministic generated compression tests provide complementary round-trip correctness.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/ossfuzz/fuzz_encode_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_bcj_exact_size.c -->
# sources/compression/xz/tests/test_bcj_exact_size.c

Purpose: regression tests for BCJ decoding when the exact output size is known or zero, historically failing in older xz releases.

Important functions: `test_exact_size()` compresses a small buffer with PowerPC BCJ plus LZMA2, then decodes with exactly one byte of input/output exposed at a time. `test_empty_block()` decodes a fixture containing an empty PowerPC BCJ+LZMA2 block with zero output capacity.

Control flow: tests skip when encoder/decoder or PowerPC BCJ support is disabled. `test_exact_size()` uses `lzma_stream_buffer_encode()` to build input, initializes `lzma_stream_decoder()`, loops until `LZMA_STREAM_END`, and asserts total input/output sizes. `test_empty_block()` uses `lzma_stream_buffer_decode()` with output limit zero and expects success with zero output.

State and persistence: uses stack buffers and one fixture loaded from `files/good-1-empty-bcj-lzma2.xz`. No files are written.

Dependencies and integration: depends on `tests.h`, liblzma stream buffer APIs, PowerPC BCJ filter support, LZMA2 preset setup, and test fixture loading.

Risks: exact-size bugs often appear at filter boundaries, especially BCJ alignment and empty output. Feature skips can leave this regression untested in minimal builds.

Test signals: successful assertions prove no extra output space is needed at stream end and empty BCJ blocks decode cleanly.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_bcj_exact_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_block_header.c -->
# sources/compression/xz/tests/test_block_header.c

Purpose: validates liblzma Block Header sizing, encoding, and decoding for `.xz` Blocks.

Important helpers and data: global `opt_lzma`, filter chains with zero, one, four, and five filters, and `RESET_BLOCK()` for clearing decoded state while preserving allocated filter arrays. `compare_blocks()` compares key `lzma_block` fields and filter IDs.

Control flow: `test_lzma_block_header_size()` checks valid size ranges, invalid version/size/filter cases, and cases intentionally ignored by size calculation. `test_lzma_block_header_encode()` validates bad header sizes, bad block fields, invalid filters, and exact encoded bytes including flags, VLI filter ID/property size, padding, and CRC32. `test_lzma_block_header_decode()` round-trips simple and multi-filter headers, validates decoder version adjustment, then corrupts check type, CRC, padding, and flags to assert correct errors.

State and persistence: stack buffers hold encoded headers. Decoded filters allocate option memory that is freed with `lzma_filters_free()`.

Dependencies and integration: uses liblzma block, filter, VLI, property, and CRC APIs. Requires x86 BCJ support for multi-filter tests and LZMA preset initialization in `main()`.

Risks: Block Headers are compact binary contracts; off-by-one header size, bad padding, or missing CRC validation can corrupt downstream decoding. Some option validation is intentionally deferred outside header-size calculation.

Test signals: strong byte-level checks and corruption tests. Skips on missing encoder/decoder/filter support.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_block_header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_check.c -->
# sources/compression/xz/tests/test_check.c

Purpose: tests integrity check APIs and decoder check-reporting behavior for `.xz` streams.

Important data and functions: EBCDIC-safe byte arrays for `"123456789"` vectors, generated random buffers, fixture pointers for no-check, unsupported-check, CRC32, CRC64, and SHA-256 streams. Tests include `test_lzma_crc32()`, `test_lzma_crc64()`, `test_lzma_supported_checks()`, `test_lzma_check_size()`, `test_lzma_get_check_st()`, and `test_lzma_get_check_mt()`.

Control flow: CRC tests verify standard vectors, unaligned input, incremental byte-at-a-time updates, and varied buffer alignments. Supported-check tests compare enabled compile-time features to `lzma_check_is_supported()`. Decoder tests initialize single-threaded or multithreaded decoders with `LZMA_TELL_ANY_CHECK`, `LZMA_TELL_UNSUPPORTED_CHECK`, and `LZMA_TELL_NO_CHECK`, then assert `LZMA_NO_CHECK`, `LZMA_UNSUPPORTED_CHECK`, or `LZMA_GET_CHECK` before `LZMA_STREAM_END`.

State and persistence: fixture data is loaded into process memory. Threaded decoder options carry memlimits but no persistent state.

Dependencies and integration: depends on liblzma check APIs, stream decoders, optional `MYTHREAD_ENABLED`, and fixture files in `tests/files`.

Risks: check availability is build-config-dependent, so assertions are guarded by macros. The tests deliberately avoid text literals for cross-character-set portability.

Test signals: detects CRC implementation regressions, check-size table drift, unsupported-check reporting bugs, and parity issues between single-threaded and threaded decoders.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_compress.sh -->
# sources/compression/xz/tests/test_compress.sh

Purpose: shell round-trip test driver for generated or prepared compression inputs using `xz` and optionally `xzdec`.

Important functions and variables: resolves `XZ` and `XZDEC`, validates build/feature availability, defines `test_xz()` for compress/decompress/compare cycles, sets conservative memlimits and `--threads=1`, and derives temporary names from the input fixture.

Control flow: skips if `xz` is missing, if required encoder/decoder support is disabled, or if the shell lacks functions. For `compress_generated_*`, invokes `create_compress_files`; for `compress_prepared_*`, reads from `$srcdir`. It then tests presets `-1` through `-4` and selected filters when both encoder and decoder macros are present: delta distances, x86, powerpc, ia64, arm, armthumb, arm64, sparc, and riscv. Each compression is decompressed with `xz -cd`, and also `xzdec` if built.

State and persistence: creates temporary compressed/uncompressed outputs and removes them via trap. Generated fixtures may persist in the build directory.

Dependencies and integration: integrates generated fixture wrappers, `xz`, `xzdec`, `config.h`, shell `cmp`, and Automake parallel tests.

Risks: filter availability detection is macro-based and acknowledged as imperfect when partial support is configured. Ancient shell behavior around empty `"$@"` is avoided by always passing arguments.

Test signals: any compression failure, decompression failure, or byte mismatch exits 1; unsupported configuration exits 77.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_compress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_abc -->
# sources/compression/xz/tests/test_compress_generated_abc

Purpose: Automake-executable wrapper that runs `test_compress.sh` against the deterministic `compress_generated_abc` fixture.

Important behavior: uses `exec "$srcdir/test_compress.sh" compress_generated_abc`, so the wrapper process becomes the main compression test script and propagates its exit status.

Control flow: all substantive work occurs in `test_compress.sh`; this file only selects the repeated `"abc\n"` generated data profile.

State and persistence: causes `create_compress_files` to create `compress_generated_abc` if it does not already exist. Temporary compression outputs are managed by the shared script.

Dependencies and integration: listed in `TESTS` by `Makefile.am`; relies on `$srcdir`, executable shell, and the shared compression script.

Risks: if `$srcdir` is unset or points incorrectly, the wrapper cannot find `test_compress.sh`. Since it uses `exec`, there is no wrapper-specific cleanup after launch.

Test signals: inherits success, failure, or skip status from `test_compress.sh`. This fixture is useful for highly compressible repeated data and run-length-like behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_abc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_random -->
# sources/compression/xz/tests/test_compress_generated_random

Purpose: wrapper for running the compression round-trip suite against deterministic pseudo-random data.

Important behavior: executes `test_compress.sh compress_generated_random` through `$srcdir`, inheriting all logic and exit statuses from the shared script.

Control flow: the shared script invokes `create_compress_files` for `compress_generated_random`, compresses with presets and supported filters, decompresses with `xz`, optionally verifies with `xzdec`, and compares bytes.

State and persistence: may create the `compress_generated_random` fixture in the build tests directory. Temporary round-trip files are cleaned by the shared script trap.

Dependencies and integration: part of Automake `TESTS`; depends on generated-file support, `xz`, optional `xzdec`, and shell tools.

Risks: the fixture is intentionally hard to compress, so it can expose expansion and buffer-size behavior. Runtime may be larger than the tiny abc fixture but remains deterministic.

Test signals: inherited exit 0/1/77 from the shared script. Byte-for-byte comparison is the key correctness signal.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_random -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_text -->
# sources/compression/xz/tests/test_compress_generated_text

Purpose: wrapper for running compression round-trip tests against deterministic lorem-like text.

Important behavior: executes `test_compress.sh compress_generated_text`, selecting the generated text fixture from `create_compress_files.c`.

Control flow: all logic is delegated to the shared compression script, including build-feature skips, fixture generation, preset/filter matrix, decompression, optional `xzdec` validation, and cleanup.

State and persistence: may create `compress_generated_text` in the build tests directory. Temporary compressed and uncompressed outputs are deleted by trap.

Dependencies and integration: included in `TESTS` and intended to run in parallel with other generated fixture wrappers.

Risks: `$srcdir` must be available. Generated text uses deterministic word selection, so stale fixture files can remain if not cleaned.

Test signals: round-trip byte equality over text-like data, covering a workload distinct from repeated and random inputs.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_compress_generated_text -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_files.sh -->
# sources/compression/xz/tests/test_files.sh

Purpose: shell validation of known-good, known-bad, and unsupported compressed fixtures for `xz` and optionally `xzdec`.

Important functions and variables: resolves `XZ` and `XZDEC`, skips when neither exists or decoder support is disabled, defines `have_feature()` to skip feature-specific fixtures while returning final status 77 if anything was skipped, and uses `NO_WARN` when check types are disabled.

Control flow: loops over good `.xz` files with per-filter feature gates and expects decode success from available tools. Bad `.xz` files must fail; unsupported files must fail for `xz`; unsupported-check is expected to pass under `-Q` and with `xzdec -qQ`. It also tests a historical `xz -l` index overflow fixture. `.lzma` good/bad fixtures are tested with `xz`; `.lz` fixtures run only when `HAVE_LZIP_DECODER` is enabled.

State and persistence: no output files are retained; all decoded data goes to `/dev/null`.

Dependencies and integration: depends on fixture naming conventions in `tests/files`, built tools, `config.h` macros, and shell globbing.

Risks: comments note partial decoder configurations can still produce failures because availability is checked coarsely. xzdec has different unsupported-check warning behavior, so assertions diverge by tool.

Test signals: unexpected success on bad/unsupported input or unexpected failure on good input exits 1. Skipped feature cases leave final status 77.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_filter_flags.c -->
# sources/compression/xz/tests/test_filter_flags.c

Purpose: tests `.xz` Filter Flags size, encoding, and decoding APIs.

Important data and helpers: defines `LZMA_FILTER_RESERVED_START`, global LZMA1/LZMA2/delta filter structs, compile-time lists of enabled BCJ encoders/decoders, `verify_filter_flags_encode()`, and `verify_filter_flags_decode()`.

Control flow: size tests verify supported filters produce reasonable lengths, LZMA1 is rejected for `.xz`, and invalid/reserved IDs fail. Encode tests check NULL/invalid options, BCJ default and start-offset properties, delta bounds, output-buffer size errors, and reserved ID errors. Decode tests construct Filter Flags manually using VLI and property APIs, then verify decoded option structs for LZMA2 dict size, BCJ start offset, and delta options; malformed IDs and truncated data assert correct errors.

State and persistence: allocates option structs in `main()` and decoded option structs in tests, freeing them after use. No files are used.

Dependencies and integration: uses liblzma filter support predicates, property coders, VLI coders, and `tests.h`. Compile-time macros determine which filters are present.

Risks: encode/decode of Filter Flags intentionally does not fully validate every filter option; chain initialization catches some invalid BCJ alignment later. Feature-disabled builds reduce coverage.

Test signals: catches binary encoding drift, reserved-ID handling, property-size bugs, and option allocation/freeing regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_filter_flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_filter_str.c -->
# sources/compression/xz/tests/test_filter_str.c

Purpose: tests string conversion APIs for liblzma filter chains: parsing, formatting, and listing filters.

Important functions and data: `test_lzma_str_to_filters()`, `test_lzma_str_from_filters()`, `test_lzma_str_list_filters()`, plus compile-time arrays of supported encoder, decoder, and combined filter names.

Control flow: parsing tests cover NULL inputs, unsupported flags, empty and invalid names, invalid option names/values, presets, `LZMA_STR_ALL_FILTERS`, `LZMA_STR_NO_VALIDATION`, chain length limits, options via `key=value`, BCJ and delta options, leading/trailing spaces, `--` separators, and binary multiplier suffixes. Formatting tests check bad inputs/flags, empty arrays, encoder/decoder/getopt/no-space modes, BCJ default option elision, too many filters, NULL required options, and bad IDs. Listing tests validate flag errors, filter-specific listing, and expected supported names by build configuration.

State and persistence: repeatedly allocates filter option arrays and output strings, then frees them with `lzma_filters_free()` and `free()`. No files are read.

Dependencies and integration: exercises public filter-string APIs, filter support macros, and option structs. It mirrors CLI `--filters=`-style parsing semantics.

Risks: error-position assertions are fragile but valuable because they lock parser diagnostics. Contains a noted weak substring check where `"arm"` can match longer names.

Test signals: detects parser grammar regressions, option validation errors, string formatting drift where exact output is promised, and listing omissions.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_filter_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_hardware.c -->
# sources/compression/xz/tests/test_hardware.c

Purpose: smoke tests for hardware-information APIs in `lzma/hardware.h`.

Important functions: `test_lzma_physmem()` calls `lzma_physmem()` and skips if the platform cannot determine memory. `test_lzma_cputhreads()` calls `lzma_cputhreads()` when threading is enabled and skips if CPU count is unavailable.

Control flow: `main()` starts the tuktest harness and runs the two tests. Results are intentionally tolerant because zero can mean unsupported platform introspection, not a library bug.

State and persistence: no state or files.

Dependencies and integration: depends on `tests.h`, `mythread.h`, and liblzma hardware APIs. Thread count testing is gated by `MYTHREAD_ENABLED`.

Risks: these tests are intentionally shallow and cannot assert specific values because results are hardware and OS dependent. They mainly catch crashes or impossible zero results on supported platforms.

Test signals: pass when nonzero values are returned, skip when the platform cannot report them, and fail only through harness/assertion errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_hardware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_index.c -->
# sources/compression/xz/tests/test_index.c

Purpose: comprehensive tests for `lzma_index` data structures, accounting, iteration, concatenation, duplication, encoding, decoding, and buffer APIs.

Important helpers and state: `MEMLIMIT`, optional global `decode_buffer`, `decode_buffer_size`, and `decode_test_index`; `generate_index_decode_buffer()` builds a reference encoded Index; `index_is_equal()` compares stream/block offsets and sizes; `verify_index_buffer()` validates raw Index bytes; `my_alloc()` simulates allocation failure for `lzma_index_dup()`.

Control flow: early tests cover memory usage estimates, actual memory used, appending records, stream flags/check masks, stream padding, stream/block counts, index size, stream size, total compressed size, file size, and uncompressed size. Iterator tests validate init, rewind, block/stream/any/nonempty iteration modes, offsets, empty streams, padding, and locating uncompressed offsets across large allocation group boundaries. Concatenation and duplication tests check overflow and historical empty-stream/memory-leak regressions. Encoder/decoder tests cover streaming and buffer APIs, NULL arguments, memlimits, corrupt indicators, corrupt middle bytes, CRC errors, nonzero padding, too-short input, extra input, and appending after decoding an empty Index.

State and persistence: all state is in heap-allocated `lzma_index` objects and in-memory buffers. No files are used. Ownership transfer matters: `lzma_index_cat(dest, src)` consumes `src` on success.

Dependencies and integration: includes internal `common/index.h` for constants and `vli_ceil4()`, plus public liblzma Index APIs, VLI, CRC, stream coders, and the tuktest harness.

Risks: this file guards size arithmetic and offset accounting, a high-risk area for overflows and out-of-bounds access. Feature-disabled encoder/decoder builds skip serialization tests. The simulated allocator has static count state, so it is suitable only for the one failure scenario.

Test signals: broad regression coverage, including named historical fixes for append overflow, duplication of empty streams, decoder NULL-output cleanup, and appending to decoded empty indexes.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_index_hash.c -->
# sources/compression/xz/tests/test_index_hash.c

Purpose: tests `lzma_index_hash`, the lightweight structure used to verify decoded Index records against expected block sizes.

Important helpers: `fill_index_hash()` appends expected records. `generate_index()` manually writes an `.xz` Index byte sequence: indicator, record count, VLI records, padding, and CRC32.

Control flow: init tests verify NULL creates a new hash and non-NULL reinitializes the same pointer. Append tests cover NULL hash, invalid unpadded/uncompressed sizes, successful records, and compressed-size overflow. Decode tests generate indexes for two, three, five, and six records; verify buffer-size errors, bad indicator, byte-at-a-time decode, mismatched unpadded sizes, corrupt CRC, and mismatched record content. Size tests assert expected encoded Index sizes for empty, one-record, two-record, and larger-VLI cases.

State and persistence: all data is heap memory owned by the test and `lzma_index_hash`. No files.

Dependencies and integration: includes internal `common/index.h` for `UNPADDED_SIZE_MIN`, `UNPADDED_SIZE_MAX`, `INDEX_INDICATOR`, `vli_ceil4()`, and index sizing semantics. Uses VLI and CRC public helpers.

Risks: manual Index generation must stay synchronized with the `.xz` specification. Encoder support is required for VLI generation in decode tests, even though `lzma_index_hash` itself is decoder-oriented.

Test signals: detects record-hash mismatches, streaming decode state bugs, padding/CRC validation problems, and size-accounting regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_index_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_lzip_decoder.c -->
# sources/compression/xz/tests/test_lzip_decoder.c

Purpose: tests liblzma's optional lzip decoder for v0/v1 files, concatenation, trailing data, checksum handling, malformed headers, and memlimit recovery.

Important helpers: `basic_lzip_decode()` decodes good fixtures one byte at a time and verifies output by CRC32. `trailing_helper()` decodes with `LZMA_CONCATENATED` and verifies trailing bytes remain readable. `decode_expect_error()` decodes bad fixtures and checks the expected `lzma_ret`.

Control flow: tests validate options errors, v0 and v1 decode, v0/v1 trailing behavior including magic-byte prefixes, concatenated member combinations, CRC error and `LZMA_IGNORE_CHECK`, `LZMA_TELL_ANY_CHECK`, invalid magic bytes, unsupported version, invalid dictionary size, invalid uncompressed/member sizes, and raising memlimit after `LZMA_MEMLIMIT_ERROR`.

State and persistence: loads fixture files into memory and uses stack output buffers. No files are written.

Dependencies and integration: gated by `HAVE_LZIP_DECODER`. Uses `lzma_lzip_decoder()`, `lzma_code()`, `lzma_memlimit_set()`, `lzma_get_check()`, fixture files, and CRC32.

Risks: lzip support is optional, so the entire file early-skips when disabled. CRCs are used instead of text comparisons for EBCDIC portability.

Test signals: covers both normal and adversarial lzip streams, with special attention to trailing input semantics and post-memlimit continuation.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_lzip_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_memlimit.c -->
# sources/compression/xz/tests/test_memlimit.c

Purpose: tests decoder memory-limit errors and recovery for `.xz`, threaded `.xz`, `.lzma` alone, and auto decoders.

Important constants and state: `MEMLIMIT_TOO_LOW` is 1234 bytes; `MEMLIMIT_HIGH_ENOUGH` is 2 MiB; `in`/`in_size` hold a known-good `.xz` fixture; `out` is an 8192-byte decode buffer.

Control flow: each decoder is initialized with too-low memory, fed a complete known-good stream, and expected to return `LZMA_MEMLIMIT_ERROR`. The test asserts `lzma_memlimit_get()`, verifies a tiny increase still fails, then raises to a high-enough limit and expects `LZMA_STREAM_END`. Separate functions cover `lzma_stream_decoder()`, `lzma_stream_decoder_mt()`, `lzma_alone_decoder()`, and `lzma_auto_decoder()`.

State and persistence: decoder state is reset per function and freed with `lzma_end()`. Fixtures are memory-loaded only.

Dependencies and integration: uses `tests.h`, `mythread.h`, fixture files, and memory-limit APIs. Threaded test skips if `MYTHREAD_ENABLED` is absent.

Risks: recovery after memlimit failure is subtle because decoder state must preserve enough context to continue after the limit is raised. Minimal builds skip relevant paths.

Test signals: explicitly references a historical stream-decoder recovery bug fixed after liblzma 5.2.6/5.3.3alpha.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_memlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_microlzma.c -->
# sources/compression/xz/tests/test_microlzma.c

Purpose: tests MicroLZMA encoder and decoder APIs, including option validation, exact compressed/uncompressed-size handling, action constraints, and property-byte behavior.

Important helpers and data: `BUFFER_SIZE`, `ENCODED_OUTPUT_SIZE`, `hello_world`, expected encoded CRC, local `lzma_lzma_lclppb_decode()` for verifying MicroLZMA property-byte negation, `goodbye_world`, generated `goodbye_world_encoded`, and `basic_microlzma_encode()`.

Control flow: encoder tests validate NULL stream, invalid lc/lp/pb combinations, dictionary limits, basic encode output and property byte, too-small output buffers, and unsupported actions other than `LZMA_FINISH`. Decoder tests, when both LZMA1 encoder and decoder exist, verify correct size decode with exact and inexact modes, too-large and too-small uncompressed sizes, wrong compressed size behavior, invalid LZMA properties, and valid-but-wrong properties leading to data errors.

State and persistence: encoded data is heap-allocated for decoder tests and stored in globals. No files are used.

Dependencies and integration: gated by `HAVE_ENCODER_LZMA1` and `HAVE_DECODER_LZMA1`. Uses MicroLZMA public APIs, LZMA presets, CRC32, and tuktest.

Risks: exact-size semantics are nuanced; one FIXME notes a case where repeated `LZMA_FINISH` eventually returns `LZMA_BUF_ERROR` instead of an immediate data error. The expected encoded CRC locks output stability and may need deliberate updates if encoder tuning changes.

Test signals: catches MicroLZMA regression in output format, unsupported action handling, size-boundary errors, and property validation.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_microlzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_scripts.sh -->
# sources/compression/xz/tests/test_scripts.sh

Purpose: shell tests for installed-style helper scripts `xzdiff` and `xzgrep`.

Important variables and flow: resolves `XZ`, `XZDIFF`, and `XZGREP` from an optional executable directory or build defaults, skips if any required executable is missing, and skips when decompression support is disabled. It prepends the xz binary directory to `PATH` so scripts find the local tool.

Control flow: `xzdiff` is run on two equivalent decompressed files and expected to exit 0, on differing files and expected to exit 1, and with a missing operand and expected to exit 2. `xzgrep` copies two fixtures to temporary names, runs combinations of patterns (`el`, `Hello`, `NOMATCH`) and options (``, `-l`, `-h`, `-H`), captures stdout/stderr and return values, then compares against `xzgrep_expected_output`.

State and persistence: creates `xzgrep_test_1.xz`, `xzgrep_test_2.xz`, and `xzgrep_test_output`; `Makefile.am clean-local` removes them.

Dependencies and integration: gated by `COND_SCRIPTS` in `Makefile.am`. Depends on fixture files, local scripts, local xz, shell utilities, and expected-output fixture.

Risks: exact expected output can be sensitive to script diagnostics and grep behavior. PATH manipulation is necessary but can hide external tool differences.

Test signals: verifies script exit-status contract and stable xzgrep output across option combinations.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_scripts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_stream_buffer_decode.c -->
# sources/compression/xz/tests/test_stream_buffer_decode.c

Purpose: tests `lzma_stream_buffer_decode()` success and failure-position behavior.

Important constants and state: `UNCOMP_SIZE` is 13; `xz_data` and `xz_data_size` are loaded from `files/good-1-check-crc32.xz`.

Control flow: `test_success()` decodes the full fixture with `LZMA_CONCATENATED`, expecting `LZMA_OK`, full input consumption, and output size 13. `test_data_error()` truncates input by one byte and expects `LZMA_DATA_ERROR` with both `in_pos` and `out_pos` reset to zero. `test_buf_error()` provides one byte too little output capacity and expects `LZMA_BUF_ERROR`, also with positions reset.

State and persistence: in-memory fixture and stack output buffers only.

Dependencies and integration: depends on decoder support and stream-buffer API. Complements streaming decoder tests by exercising the convenience API's all-or-nothing position semantics.

Risks: comments note the truncated-input case failed in xz 5.8.3 and older, making this an explicit regression guard. Position reset behavior is important for callers that retry or report offsets.

Test signals: clear return-code and position assertions for success, corrupt data, and insufficient output.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_stream_buffer_decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_stream_flags.c -->
# sources/compression/xz/tests/test_stream_flags.c

Purpose: tests `.xz` Stream Header/Footer encoding, decoding, and comparison.

Important constants and helpers: `XZ_STREAM_FLAGS_SIZE`, header magic bytes, footer magic bytes, `stream_header_encode_helper()`, `stream_footer_encode_helper()`, `stream_header_decode_helper()`, and `stream_footer_decode_helper()`.

Control flow: header/footer encode tests iterate check IDs, verify magic bytes, stream flag bits, backward-size encoding, CRC32, and footer magic; they reject unsupported versions, invalid check IDs, and invalid backward sizes where applicable. Decode tests round-trip encoded data, then mutate magic, reserved bits, upper check bits, stream flags, and CRC fields to assert `LZMA_FORMAT_ERROR`, `LZMA_OPTIONS_ERROR`, or `LZMA_DATA_ERROR`. Compare tests validate version, check, backward-size equality, `LZMA_VLI_UNKNOWN` handling, and invalid backward-size detection.

State and persistence: all buffers are stack-local. No files are used.

Dependencies and integration: uses liblzma stream flag APIs, CRC32, endian helpers, and build-gated encoder/decoder support. It protects the container-level metadata that decoders use before block processing.

Risks: stream flags are compact and CRC-protected; tests must recompute CRCs after intentional semantic mutations to ensure the intended validation layer fails. Some loops use `LZMA_CHECK_ID_MAX` boundaries, so API constant changes matter.

Test signals: byte-level validation of container metadata and robust corruption classification.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_stream_flags.c -->
