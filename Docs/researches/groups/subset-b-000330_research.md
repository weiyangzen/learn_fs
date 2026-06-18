# Research: subset-b-000330

Grouped source research for the zstd gzip-compatibility tests, standalone zstd test programs, and broad CLI test harness files in `sources/compression/zstd/tests`. Each section is source-tree-aligned and bounded for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/Makefile -->
## sources/compression/zstd/tests/gzip/Makefile

Purpose: Drives zstd's imported gzip compatibility regression tests. It builds the zstd program, symlinks it as `gzip`, prepends the local directory to `PATH`, and runs selected gzip shell tests through the bundled Automake-style `test-driver.sh`.

Important APIs and targets: `PRGDIR = ../../programs` points at the zstd CLI build directory. `all` depends on individual `test-*` targets for gzip behavior regressions; `test-gzip-env` is present but commented out from the default list. `zstd` invokes `$(MAKE) -C $(PRGDIR) zstd`, creates `gzip -> ../../programs/zstd`, prints `PATH`, and runs `gzip --version`. `clean` delegates to the programs clean target and removes `.trs` and `.log` files.

Control flow: On supported Unix-like systems, the pattern rule `test-%: zstd` first ensures the symlinked gzip-compatible zstd binary is built, then executes `./test-driver.sh` with test name, log path, result path, hard-error handling, and the corresponding `./$*.sh` script.

State and persistence: Writes the local `gzip` symlink and per-test `.log`/`.trs` files. `clean` removes logs and delegates binary cleanup. No source files are modified.

Dependencies and integration points: Integrates zstd's `programs/zstd` with GNU gzip test scripts by relying on argv name/format compatibility. It depends on POSIX `make`, `uname`, `ln -sf`, shell execution, and the local `test-driver.sh`. The OS filter limits execution to Linux, Darwin, GNU variants, FreeBSD, DragonFly, and NetBSD-style environments.

Risks: Because `PATH` starts with `.`, any helper script or symlink in the test directory can shadow host tools. The OS filter omits unsupported platforms instead of failing, so coverage is conditional. The commented `test-gzip-env` means GZIP environment variable behavior may not run under the default `all` target.

Test signals: A successful run emits `PASS` lines from `test-driver.sh` and ends with `Testing completed`. Expected artifacts include one `.log` and `.trs` per `test-*` target.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/gzip-env.sh -->
## sources/compression/zstd/tests/gzip/gzip-env.sh

Purpose: Tests the obsolete `GZIP` environment variable handling for gzip-compatible invocation.

Important APIs and functions: Sources `init.sh`, calls `path_prepend_ .`, uses `gzip`, `compare`, and `Exit`. It creates a compressed stdin fixture from `exp`, then runs decompression with environment-supplied options.

Control flow: First validates that `GZIP=-qv` does not break `gzip -d` decompression. It then iterates over options that must be rejected when supplied through `GZIP`, including mode-changing, output-changing, suffix, recursive, help/version, and force/keep flags. Finally it iterates over allowed options such as name/no-name, quiet/verbose, and compression levels.

State and persistence: Creates temporary files under the `init.sh` test directory: `exp`, `in`, `out`, and `err`. State is local to the spawned test process and removed by the harness trap.

Dependencies and integration points: Depends on zstd's gzip-compatible CLI honoring the imported GNU gzip policy for `GZIP`. It also depends on the shared `compare` helper and shell variable assignment syntax immediately before a command.

Risks: This test is commented out in the Makefile default target, likely because zstd may intentionally limit or differ in `GZIP` envvar support. Any implementation accepting dangerous options from `GZIP` can alter files or test process behavior unexpectedly.

Test signals: Allowed options must exit successfully and reproduce `exp` in `out`; disallowed options must fail. Any mismatch sets `fail=1`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/gzip-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/helin-segv.sh -->
## sources/compression/zstd/tests/gzip/helin-segv.sh

Purpose: Regression test for a historical gzip decompression segfault on a short `.Z`/compress-style input provided by Aki Helin.

Important APIs and functions: Sources `init.sh`, uses `printf` to create byte-exact `helin.gz` and expected output, invokes `gzip -dc`, compares with `compare`, and exits through `Exit`.

Control flow: The script writes a seven-byte compressed fixture, writes two NUL bytes as the expected decoded stream, then decompresses to `out` and requires success plus byte-identical output.

State and persistence: Creates `helin.gz`, `exp`, and `out` in the temporary test directory. No external state persists beyond harness cleanup.

Dependencies and integration points: Exercises gzip-format compatibility in the zstd CLI when invoked through the `gzip` symlink. It specifically reaches legacy decompress paths that must not crash on tiny crafted input.

Risks: The fixture is byte-oriented; shell or platform `printf` differences would be risky, but POSIX octal escapes are used. The test only checks stdout content, not stderr silence.

Test signals: `gzip -dc helin.gz` must exit zero and produce exactly two NUL bytes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/helin-segv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/help-version.sh -->
## sources/compression/zstd/tests/gzip/help-version.sh

Purpose: Imported GNU test ensuring built programs behave correctly for `--help`, `--version`, and a minimal normal invocation. In this zstd gzip test directory it primarily validates gzip-family wrapper behavior when included in `built_programs`.

Important APIs and functions: Requires `built_programs`, `VERSION`, and `PACKAGE_BUGREPORT` environment variables. Sources `init.sh` and uses `path_prepend_ .`, program-specific setup functions such as `zcat_setup`, `zdiff_setup`, `zgrep_setup`, and generic helpers like `grep`, `compare`, and `Exit`.

Control flow: It first extracts the version from the first built program and checks it against `$VERSION`. For locales `C`, `fr`, and `da`, it runs each program with `--help` and `--version`, verifies help mentions the bug-report address, and checks that writes to `/dev/full` fail with expected statuses. It then creates per-program fixtures and runs each program once with minimal arguments, skipping programs known to be unsuitable.

State and persistence: Creates a nested temporary directory plus files such as `zin.gz`, `zin2.gz`, `bigZ-in.Z`, input/output fixtures, and helper directories. All are under the `init.sh` temporary directory.

Dependencies and integration points: Integrates with Automake/Coreutils-style test variables and host tools. It expects gzip helper programs (`zcat`, `zcmp`, `zdiff`, `zgrep`, etc.) to be discoverable through `PATH`, with compressed fixtures produced by the tested `gzip`.

Risks: This file is more generic than the zstd gzip subset and contains many setup functions for programs zstd may not build. Incorrect `built_programs` can make the test irrelevant or fail on unrelated utility behavior. Locale-dependent output is intentionally tested, so translated builds must still include bug-report text.

Test signals: Version mismatch, missing bug-report text, unexpected success writing to `/dev/full`, bad exit status, or failed minimal command invocation sets `fail=1`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/help-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/hufts.sh -->
## sources/compression/zstd/tests/gzip/hufts.sh

Purpose: Regression test for invalid deflate input that historically made gzip misbehave or crash in Huffman table handling.

Important APIs and functions: Sources `init.sh`, uses `gzip -dc`, normalizes stderr with `sed`, and compares stdout/stderr through `compare`.

Control flow: It prepares expected stderr text, decompresses `$abs_srcdir/hufts-segv.gz`, requires exit status `1`, requires empty stdout, rewrites the variable filename prefix in stderr to a stable `...:` prefix, and compares against the expected diagnostic.

State and persistence: Creates `exp`, `out`, `err`, and temporary `k` in the test directory. Reads the immutable fixture `hufts-segv.gz` from the source directory.

Dependencies and integration points: Depends on `abs_srcdir` from the test environment and on gzip-compatible error wording for invalid compressed data.

Risks: Diagnostic text matching is exact after filename normalization, so wording changes can fail this test even if behavior is otherwise correct. Missing `abs_srcdir` or fixture breaks setup.

Test signals: Expected failure status `1`, empty output, and normalized stderr `invalid compressed data--format violated`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/hufts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.cfg -->
## sources/compression/zstd/tests/gzip/init.cfg

Purpose: Local extension point loaded by `init.sh` after its generic shell-test harness setup.

Important APIs and functions: Defines `testdir_prefix_()` to print `gz`, overriding the default `gt` prefix for temporary directories.

Control flow: `init.sh` sources this file if present before calling `setup_ "$@"`. The overridden function is then used by `setup_` to construct temp directory templates such as `gz-$ME_.XXXX`.

State and persistence: Does not write state directly. It changes temporary directory naming for every gzip test sourcing `init.sh`.

Dependencies and integration points: Depends on the `init.sh` documented override hook. It integrates with cleanup, diagnostics, and temp directory creation indirectly through the harness.

Risks: Minimal risk; any syntax error here breaks all gzip tests. A non-unique prefix would not be enough to cause collisions because random suffixes are still used.

Test signals: Temporary directories created by gzip tests should use the `gz-` prefix.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.sh -->
## sources/compression/zstd/tests/gzip/init.sh

Purpose: Shared POSIX shell harness for the imported gzip tests. It normalizes shell behavior, provides diagnostics and comparison helpers, creates an isolated temporary directory, manages cleanup traps, and supports `$EXEEXT` executable shims.

Important APIs and functions: Test scripts use `Exit`, `fail_`, `skip_`, `fatal_`, `framework_failure_`, `returns_`, `compare`, and `path_prepend_`. Internal helpers include `warn_`, `emit_diff_u_header_`, `compare_dev_null_`, `find_exe_basenames_`, `create_exe_shims_`, `setup_`, `remove_tmp_`, `rand_bytes_`, and `mktempd_`.

Control flow: The script computes `ME_`, defines helpers, sanitizes zsh/POSIX shell mode, and if necessary re-execs under a shell that supports command substitution, `local`, and extra `$EXEEXT` features. It enables `MALLOC_PERTURB_`, chooses a portable `compare` implementation from `diff -u`, other diff modes, or `cmp`, sources `init.cfg`, calls `setup_`, and installs an exit trap to remove the temporary directory.

State and persistence: Exports `MALLOC_PERTURB_`, possibly `gl_set_x_corrupts_stderr_`, `PATH` changes from `path_prepend_`, and `$re_shell` on re-exec. It creates a per-test temporary directory with restrictive permissions and removes it on exit or signals. Cleanup can be customized through `cleanup_`.

Dependencies and integration points: Depends on common shell utilities (`expr`, `sed`, `diff`, `cmp`, `mktemp`, `dd`, `tr`, `mkdir`, `chmod`, `rm`) and optionally `/dev/urandom`. Test files rely on its temp-directory isolation, output comparison, skip/fail exit codes, and `EXEEXT` aliasing for Windows-like builds.

Risks: This harness is intentionally broad and portable but fragile if shell feature probes are changed. `rand_bytes_` fallback can run host inspection commands and pipe through `gzip`; this matters if `gzip` on `PATH` is the program under test. Signal traps and re-exec logic are order-dependent. `returns_` uses `local`, which is why shell selection enforces that extension.

Test signals: Test scripts exiting through `Exit` should preserve status through cleanup. `compare /dev/null file` should emit useful diffs for non-empty files. `path_prepend_` should make local symlinked test programs win over system programs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/keep.sh -->
## sources/compression/zstd/tests/gzip/keep.sh

Purpose: Tests gzip `--keep` behavior for both compression and decompression, plus verbose logging for kept inputs.

Important APIs and functions: Sources `init.sh`; uses `gzip`, `compare`, shell `eval` for source-existence assertions, and `Exit`.

Control flow: It creates `in` and `orig`, then loops over `--keep` and default behavior. For compression, `--keep` must retain `in` while default compression must remove it; for decompression, `--keep` must retain `in.gz` while default decompression must remove it. It then checks that `gzip -kv in` logs creation of `in.gz`.

State and persistence: Creates and removes `in`, `orig`, and `in.gz` within the temp directory. `orig` persists until cleanup as the comparison source.

Dependencies and integration points: Exercises zstd's gzip-compatible source removal/retention and verbose messages when invoked as `gzip`.

Risks: Uses `eval` to apply `&&`/`||` logic stored in `op`; safe here because values are hardcoded. Exact verbose substring `created in.gz` can be sensitive to message changes.

Test signals: File existence must match keep/default semantics and decompressed `in` must match `orig`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/keep.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/list.sh -->
## sources/compression/zstd/tests/gzip/list.sh

Purpose: Exercises gzip `--list`/`-l` behavior on invalid and valid inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip -l`, `gzip -9`, `compare`, and `Exit`.

Control flow: It writes a plain input file, requires `gzip -l in` to fail, compresses it at level 9, then runs `gzip -l in.gz` directly and through a pipe to `cat`. The two outputs must be identical.

State and persistence: Creates `in`, `orig`, `in.gz`, `out1`, and `out2` under the temporary directory.

Dependencies and integration points: Validates the zstd CLI list mode under gzip-compatible naming, including stdout behavior when output is piped.

Risks: Does not assert exact list content, only consistency between TTY-like and piped output paths. If both paths are consistently wrong, this test will not catch it.

Test signals: Listing a non-compressed file fails; listing a valid `.gz` succeeds and produces stable output independent of being piped.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/list.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/memcpy-abuse.sh -->
## sources/compression/zstd/tests/gzip/memcpy-abuse.sh

Purpose: Regression test for historical gzip inflate code using `memcpy` on overlapping regions.

Important APIs and functions: Sources `init.sh`, generates a slightly non-uniform input larger than 32 KiB with `printf` and `tee`, compresses with `gzip`, decompresses with `gzip -dc`, and compares.

Control flow: It creates `in` and `in.gz` from the same generated stream. Decompression must succeed and produce byte-identical output.

State and persistence: Creates `in`, `in.gz`, and `out` in the temporary test directory.

Dependencies and integration points: Exercises deflate match copying behavior in the gzip-compatible decompressor. The generated size targets internal gzip buffer edges.

Risks: The `printf %032767d` format is deliberate; changing it can stop hitting the overlap-sensitive path. This test checks correctness, not memory sanitizer diagnostics.

Test signals: `gzip -dc in.gz` exits zero and `out` equals `in`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/memcpy-abuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/mixed.sh -->
## sources/compression/zstd/tests/gzip/mixed.sh

Purpose: Tests `gzip -cdf` pass-through behavior for mixed compressed and uncompressed input, including edge sizes around internal buffers.

Important APIs and functions: Sources `init.sh`, uses pipelines to create compressed/uncompressed concatenations, invokes `gzip -cdf`, and compares with `compare`.

Control flow: It verifies plain input is copied, compressed data followed by plain data yields combined plaintext, and concatenated compressed members yield combined plaintext. A known failing case, plain data followed by compressed data, remains commented out. It then generates a range of small, 32 KiB boundary, and 128 KiB boundary plain inputs and requires `gzip -cdf` to act like `cat`.

State and persistence: Creates expected files `exp2` and `exp3`, repeatedly rewrites `in` and `out`, and emits size values to stdout.

Dependencies and integration points: Exercises force-decompress plus stdout mode (`-cdf`) where gzip-compatible zstd must decide whether to decompress or pass data through.

Risks: One mixed-order case is explicitly skipped, so coverage is asymmetric. The test relies on host `printf` supporting precision formatting for arbitrary generated sizes.

Test signals: All active comparisons must match expected plaintext, especially sizes `32831`, `32832`, `32833`, `131071`, `131072`, and `131073`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/mixed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/null-suffix-clobber.sh -->
## sources/compression/zstd/tests/gzip/null-suffix-clobber.sh

Purpose: Regression test ensuring an empty suffix supplied with `-S ''` is rejected without clobbering the input file.

Important APIs and functions: Sources `init.sh`, creates a gzip file, invokes `gzip ---presume-input-tty -d -S ''`, and compares stdout/stderr.

Control flow: It writes `F.gz`, prepares `yes` stdin and expected stderr `gzip: invalid suffix ''`, then runs decompression with empty suffix. The command must fail, produce no stdout, emit the expected error, and leave `F.gz` intact.

State and persistence: Creates `F.gz`, `yes`, `expected-err`, `out`, and `err` under the test temp directory.

Dependencies and integration points: Checks suffix validation and interactive prompt handling in gzip-compatible mode.

Risks: Exact stderr text is required. The triple-dash long option `---presume-input-tty` is unusual and assumes compatibility with GNU gzip's test-only option parsing.

Test signals: Failed exit, empty stdout, exact invalid-suffix diagnostic, and retained source archive.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/null-suffix-clobber.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/stdin.sh -->
## sources/compression/zstd/tests/gzip/stdin.sh

Purpose: Ensures gzip-compatible argument `-` is treated as stdin and can be interleaved with named inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip -dc in - in < in`, `compare`, and `Exit`.

Control flow: It compresses a single `a` byte to `in`, prepares expected output `aaa`, then asks gzip to decompress named file `in`, stdin `-`, and named file `in` again. Output must be three decoded copies with no stderr.

State and persistence: Creates `in`, `exp`, `out`, and `err` in the temporary test directory.

Dependencies and integration points: Exercises file iteration and stdin sentinel behavior in zstd's gzip mode.

Risks: If stdin handling consumes too much or too little, the final named input can still run, so the exact output comparison is the key signal.

Test signals: Exit zero, `out` equals `aaa`, and `err` is empty.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/stdin.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/test-driver.sh -->
## sources/compression/zstd/tests/gzip/test-driver.sh

Purpose: Automake-compatible test driver that runs one test script, captures its log, writes `.trs` metadata, and maps exit statuses into PASS/FAIL/SKIP/ERROR/XFAIL/XPASS outcomes.

Important APIs and functions: Supports `--test-name`, `--log-file`, `--trs-file`, `--expect-failure`, `--color-tests`, and `--enable-hard-errors`. Internal helpers are `usage_error` and `print_usage`; the main body parses options, installs signal traps, runs the test command, classifies status, writes the log and `.trs`, and exits with the tweaked status.

Control flow: Mandatory options are validated first. The selected test command is executed with stdout/stderr redirected to the log file. Exit status `99` can be downgraded to failure if hard errors are disabled. Result classification follows Automake conventions: `0` is PASS unless expected failure, `77` is SKIP, `99` is ERROR, other statuses are FAIL unless expected failure.

State and persistence: Writes the requested log file and `.trs` file. On signals 1, 2, 13, or 15 it removes those files and exits with the signal-derived status.

Dependencies and integration points: Used by `gzip/Makefile` pattern targets. Downstream automation reads `.trs` keys `:test-result:`, `:global-test-result:`, `:recheck:`, and `:copy-in-global-log:`.

Risks: `set -u` makes missing variables fatal, which is useful but can make option parsing brittle. Color codes include literal escape sequences. The driver does not append the test command itself to metadata, only the result.

Test signals: Console receives a single colored or plain `PASS: name`-style line. The log ends with result and exit status, and `.trs` contains matching metadata.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/test-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/trailing-nul.sh -->
## sources/compression/zstd/tests/gzip/trailing-nul.sh

Purpose: Verifies gzip behavior with trailing bytes after a compressed member, especially accepted trailing NUL bytes.

Important APIs and functions: Sources `init.sh`, creates three compressed files with appended bytes, runs `gzip -d`, and uses `compare`.

Control flow: `0.gz` has one trailing NUL and should exit `0`; `00.gz` has two trailing NULs and should exit `0`; `1.gz` has a trailing byte `\1` and should exit `1`. For non-error cases, the decompressed file content must equal the corresponding line.

State and persistence: Creates `0.gz`, `00.gz`, `1.gz`, decompressed outputs `0`, `00`, `1` as applicable, and `exp`.

Dependencies and integration points: Exercises trailing-garbage policy in gzip-compatible decompression and source removal behavior after `gzip -d`.

Risks: The script compares numeric return code to the loop variable, so the file names deliberately encode expected status. A behavior change around multiple trailing NULs will be caught.

Test signals: Exit status equals `0`, `0`, and `1` respectively; successful outputs match their expected line.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/trailing-nul.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/unpack-invalid.sh -->
## sources/compression/zstd/tests/gzip/unpack-invalid.sh

Purpose: Regression test for invalid legacy `unpack`/gzip-like input that gzip 1.5 mishandled by outputting invalid data.

Important APIs and functions: Sources `init.sh`, writes byte-exact fixtures with `printf`, runs `gzip -d <in >out 2>err`, and exits through `Exit`.

Control flow: For each crafted byte string, it writes `in` and requires decompression to fail. If any input succeeds, `fail` becomes `1`.

State and persistence: Reuses `in`, `out`, and `err` in the temporary test directory.

Dependencies and integration points: Targets invalid stream detection in gzip-compatible decompression paths.

Risks: The loop resets `fail` to `0` on each failing input, so only the last case's result is authoritative unless an earlier success is followed by a later failure. That is a test weakness inherited from the script.

Test signals: Each active crafted input should make `gzip -d` return nonzero; the intended final result is failure if any invalid stream is accepted.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/unpack-invalid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/z-suffix.sh -->
## sources/compression/zstd/tests/gzip/z-suffix.sh

Purpose: Checks custom suffix handling with `-Sz`.

Important APIs and functions: Sources `init.sh`, uses `gzip -Sz`, `gzip -dSz`, `test -f`, `compare`, and `Exit`.

Control flow: It creates `F` and copy `G`, compresses `F` using suffix `z`, requires original `F` removed and `Fz` created, then decompresses using the same suffix and requires `Fz` removed and regenerated `F` equal to `G`.

State and persistence: Creates `F`, `G`, and `Fz` in the temporary test directory.

Dependencies and integration points: Exercises gzip-compatible suffix parsing, output naming, and source removal.

Risks: The last comparison line contains `fail\1`, which appears to be a typo for `fail=1`; if the comparison fails, shell behavior may not set the failure flag as intended. The earlier file-existence checks still cover part of the flow.

Test signals: Correct behavior removes the source on compression, creates `Fz`, removes `Fz` on decompression, and restores content identical to `G`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/z-suffix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zdiff.sh -->
## sources/compression/zstd/tests/gzip/zdiff.sh

Purpose: Exercises `zdiff` with two compressed inputs and with equal inputs.

Important APIs and functions: Sources `init.sh`, uses `gzip`, `zdiff`, shell status checks, and `compare`.

Control flow: It creates files `a` and `b`, compresses both, prepares expected classic diff output, and runs `zdiff a.gz b.gz`. Status must be `1` and output must match the expected difference. It then runs `zdiff a.gz a.gz` and requires success with empty stdout and stderr.

State and persistence: Creates `a.gz`, `b.gz`, `exp`, `out`, and `err`.

Dependencies and integration points: Depends on `zdiff` being available in `PATH` and using the tested gzip-compatible decompressor for `.gz` inputs.

Risks: Exact diff output assumes default `diff` formatting. Host-specific `zdiff` implementations can vary if not the intended wrapper.

Test signals: Different compressed files yield status `1` and expected diff; identical compressed files yield zero status and no output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zdiff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-context.sh -->
## sources/compression/zstd/tests/gzip/zgrep-context.sh

Purpose: Ensures `zgrep -15` context option handling works on compressed stdin.

Important APIs and functions: Sources `init.sh`, defines a small `seq` replacement, uses `${GREP:-grep}` to probe host grep support, runs `zgrep`, and compares output.

Control flow: It creates numbers `1..40`, compresses them, and expects `2..32` when searching for `17` with 15 lines of context. If host grep lacks the context option, it skips with exit `77`. Otherwise it requires `zgrep -15 17 - < in.gz` to match expected output.

State and persistence: Creates `in`, `in.gz`, `exp`, and `out`.

Dependencies and integration points: Tests option forwarding/parsing in `zgrep`, including compressed stdin through `-`.

Risks: Relies on host grep supporting the compact numeric context form. The local `seq` uses awk and assumes basic awk availability.

Test signals: Either SKIP due to unsupported grep context options or PASS with exact `2..32` output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-context.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-f.sh -->
## sources/compression/zstd/tests/gzip/zgrep-f.sh

Purpose: Tests `zgrep -f -` pattern-file-from-stdin behavior and related edge cases.

Important APIs and functions: Sources `init.sh`, uses `zgrep`, `gzip`, `compare`, and optionally bash process substitution.

Control flow: It writes pattern file `n`, duplicates it as `haystack`, compresses `haystack`, then runs `zgrep -f - haystack.gz < n` and requires output equal to `n`. In bash outside POSIX mode it additionally checks process substitution with two compressed haystacks. Finally it checks `echo a-b | zgrep -e -` succeeds, covering literal dash patterns.

State and persistence: Creates `n`, `haystack.gz`, optional `nn`, and `out`.

Dependencies and integration points: Exercises `zgrep` stdin handling where both the pattern source and compressed data may involve `-` semantics or shell redirection.

Risks: The process-substitution branch is bash-specific and skipped in most POSIX shells. `compare out n` intentionally reverses expected/actual names but comparison is symmetric for equality.

Test signals: `zgrep -f -` must return zero and output the two matching lines; dash pattern handling must not be mistaken for an option.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-f.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-signal.sh -->
## sources/compression/zstd/tests/gzip/zgrep-signal.sh

Purpose: Verifies `zgrep` terminates gracefully when its output pipeline gets a signal such as SIGPIPE.

Important APIs and functions: Sources `init.sh`; uses Perl with POSIX `dup2` to implement `write_to_dangling_pipe`; invokes `cat` and `zgrep`; uses `skip_`, `framework_failure_`, and `Exit`.

Control flow: It creates `f.gz`, verifies Perl can manipulate file descriptors, then runs `cat f.gz f.gz` with stdout connected to a pipe with the read end closed to learn the host's signal exit status. It then runs `zgrep a f.gz f.gz` in the same dangling-pipe setup and requires the same signal-derived status.

State and persistence: Creates `f.gz` in the temporary test directory.

Dependencies and integration points: Depends on a suitable Perl and POSIX signal semantics. Exercises `zgrep`'s pipeline signal propagation rather than content correctness.

Risks: Signal status conventions vary; the script calibrates with `cat`, but shells or Perl implementations that ignore SIGPIPE can cause skip or framework failure. This is intentionally Unix-specific.

Test signals: `zgrep` must exit with the calibrated signal status greater than `128`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-signal.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/znew-k.sh -->
## sources/compression/zstd/tests/gzip/znew-k.sh

Purpose: Checks that `znew -K` works without invoking a failing `compress(1)` program.

Important APIs and functions: Sources `init.sh`, creates a local executable `compress` that fails, uses `gzip -c` to create a `.Z`-named file, runs `znew -K`, and checks file existence.

Control flow: The script shadows `compress` in `PATH`, creates `123456.Z` from a large blank input, runs `znew -K 123456.Z`, and requires both command success and original `.Z` file retention.

State and persistence: Creates local `compress` shim and `123456.Z` in the temp directory.

Dependencies and integration points: Tests `znew` conversion semantics and `PATH` shadowing through `path_prepend_ .`.

Risks: Requires basename length at least six for znew behavior. It only checks original retention, not the exact `.gz` output.

Test signals: `znew -K` succeeds, does not call the failing `compress`, and leaves `$name` present.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/znew-k.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/invalidDictionaries.c -->
## sources/compression/zstd/tests/invalidDictionaries.c

Purpose: Standalone C test ensuring malformed dictionary bytes are rejected by both compression and decompression dictionary constructors.

Important APIs and types: Defines `dictionary { const char *data; size_t size; }`, a static `invalidRepCode` byte array, and a sentinel-terminated `dictionaries` array. Uses `ZSTD_createCDict`, `ZSTD_freeCDict`, `ZSTD_createDDict`, and `ZSTD_freeDDict`.

Control flow: `main` iterates over dictionaries until `data == NULL`. For each invalid dictionary, it attempts to create a `ZSTD_CDict` at compression level `1`; if creation succeeds, it frees it and returns `1`. It then attempts to create a `ZSTD_DDict`; if creation succeeds, it frees it and returns `2`. Success is returning `0` after all invalid dictionaries are rejected.

State and persistence: No persistent state. Allocations are internal to libzstd dictionary creation and freed on unexpected success.

Dependencies and integration points: Includes public `zstd.h` and links against libzstd. The invalid fixture targets dictionary parsing validation around repeat codes.

Risks: If libzstd starts accepting this byte sequence as a raw content dictionary instead of a zstd dictionary, the test will fail. Return codes distinguish compressor dictionary acceptance from decompressor dictionary acceptance.

Test signals: Process exit `0` means both constructors rejected the invalid dictionary; exit `1` or `2` identifies the side that incorrectly accepted it.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/invalidDictionaries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/largeDictionary.c -->
## sources/compression/zstd/tests/largeDictionary.c

Purpose: Stress test for streaming compression with a very large window/dictionary-like history and immediate round-trip decompression of emitted chunks.

Important APIs and functions: `compress()` wraps `ZSTD_compressStream2` with `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_decompressStream`, and `ZSTD_EndDirective`. `main()` configures `ZSTD_CCtx` and `ZSTD_DCtx` using `ZSTD_CCtx_setParameter` and `ZSTD_DCtx_setParameter`, generates data with `RDG_genBuffer`, and cleans up contexts and buffers.

Control flow: The program allocates a 2 GiB source buffer, a 1 GiB round-trip buffer, and an output buffer sized by `ZSTD_compressBound(1 GiB)`. It sets `windowLog=31`, one worker, maximum overlap, checksum, `btopt`, and tuned low hash/chain/search values, then sets decoder `windowLogMax=31`. It generates deterministic data and compresses ten 1 GiB chunks with `ZSTD_e_continue`, then a final 1 GiB chunk with `ZSTD_e_end`; every compressed output chunk is immediately fed to the streaming decoder and the final call must finish the frame.

State and persistence: Heavy heap allocation is the main state. Compression and decompression contexts persist across all chunks until cleanup. No files are written.

Dependencies and integration points: Requires static-linking-only zstd parameters, `datagen.h`, and enough memory/address space for multi-gigabyte allocations. It exercises multithreaded compression settings and large window decode limits.

Risks: Very high memory use makes this unsuitable for normal CI unless gated. The comment says "Compress 30 GB" but the visible loop compresses eleven 1 GiB chunks total. Round-trip validation checks decoder errors and frame completion but does not compare decoded bytes against the original buffer.

Test signals: Stderr progress messages for each GiB and final `Success!`; exit `0` on success, `1` on allocation, parameter, compression, decompression, or incomplete-frame failure.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/largeDictionary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/legacy.c -->
## sources/compression/zstd/tests/legacy.c

Purpose: Verifies libzstd can decode hard-coded frames produced by legacy zstd versions `v0.4.3` through `v0.8.0`.

Important APIs and functions: `testSimpleAPI()` uses `ZSTD_decompress` and `ZSTD_getErrorName`. `testStreamingAPI()` uses `ZSTD_createDStream`, `ZSTD_initDStream`, `ZSTD_decompressStream`, `ZSTD_DStreamOutSize`, and `ZSTD_freeDStream`. `testFrameDecoding()` uses `ZSTD_decompressBound` and `ZSTD_findFrameCompressedSize`.

Control flow: `main()` runs simple one-shot decode, streaming decode, and frame-size traversal in order. The simple API allocates the exact expected size and compares full output. The streaming API decodes into chunks, reinitializing the stream when a frame ends, and compares each produced range against `EXPECTED`. Frame decoding walks all concatenated frames by repeatedly finding compressed frame sizes until no bytes remain.

State and persistence: Uses static `COMPRESSED` and `EXPECTED` string constants; heap allocations are per test and freed. No files are read or written.

Dependencies and integration points: Requires libzstd built with legacy decompression support. Includes `ZSTD_STATIC_LINKING_ONLY` for `ZSTD_decompressBound` and `zstd_errors.h` for legacy-specific error comparison.

Risks: Without legacy support, the simple API reports prefix unknown and fails. `strlen(EXPECTED)` assumes no embedded NULs in expected text. Streaming comparison depends on correct `outputPos` tracking across concatenated frames.

Test signals: Prints `Simple API OK`, `Streaming API OK`, `Frame Decoding OK`, and `OK`; exits nonzero on any decode, size, frame-bound, or content mismatch.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/libzstd_builds.sh -->
## sources/compression/zstd/tests/libzstd_builds.sh

Purpose: Validates libzstd build feature switches by inspecting generated library objects and executable-stack metadata.

Important APIs and functions: Shell helpers `die`, `isPresent`, and `mustBeAbsent` check `tmplog` produced by `nm`. The script repeatedly runs `make -C ../lib libzstd` or `libzstd.a` with different environment variables and verifies object presence.

Control flow: It builds the default library and requires compression, decompression, and dictionary builder objects while excluding legacy and deprecated zbuff objects. It checks `readelf -lW libzstd.so` for a non-executable `GNU_STACK`. It then rebuilds static library variants with compression disabled, decompression disabled, deprecated disabled/enabled, dictionary builder disabled, decompression plus dictionary builder disabled, and legacy support enabled, cleaning artifacts between cases.

State and persistence: Produces and removes `../lib/libzstd.a`, `../lib/libzstd.so*`, and local `tmplog`. Build products in the lib directory are mutated repeatedly.

Dependencies and integration points: Depends on `make`, `nm`, `grep`, `readelf`, and zstd's makefile feature variables: `ZSTD_LIB_COMPRESSION`, `ZSTD_LIB_DECOMPRESSION`, `ZSTD_LIB_DEPRECATED`, `ZSTD_LIB_DICTBUILDER`, and `ZSTD_LEGACY_SUPPORT`.

Risks: `readelf` is assumed available. Object names are implementation details, so source-file renames can break this test even if feature behavior remains correct. `mustBeAbsent` intentionally echoes on success due to shell behavior noted in the script.

Test signals: Each feature combination must include/exclude the expected `.o` names; `GNU_STACK` must not contain `RWE`; any mismatch calls `die`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/libzstd_builds.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/longmatch.c -->
## sources/compression/zstd/tests/longmatch.c

Purpose: Stress test for long-match compression paths that historically risked crashes when compressing more than 8 GiB with repeated distant matches.

Important APIs and functions: `compress()` wraps `ZSTD_compressStream` and `ZSTD_flushStream` on a `ZSTD_CStream`. `main()` creates a compression context, sets parameters with `ZSTD_CCtx_setParameter`, fills a window-sized buffer with fixed matching prefixes/suffixes and random middle bytes, and repeatedly compresses variable slices.

Control flow: It configures `windowLog=18`, chain/hash/search/minmatch/targetLength, and `ZSTD_fast`. It creates a buffer containing a repeated marker at both ends to encourage long matches. It compresses one full window, then loops until `compressed` reaches `1 << 33`, choosing random block lengths from the current position and wrapping when the position reaches the window size.

State and persistence: Uses heap source and destination buffers and a single streaming compression context. No decompression or file persistence is performed.

Dependencies and integration points: Includes `mem.h` for `U64`, static zstd parameters, and libc `rand`. Exercises streaming compression state across many calls.

Risks: The test name `compressed` actually tracks source bytes consumed, not compressed byte count. Destination output buffer reuse assumes each flush drains fully into a buffer sized for one window. No output correctness is checked beyond absence of zstd errors or crashes.

Test signals: Prints setup/progress messages and exits `0` after "Compression completed successfully"; exits `1` for compression/flush error and `2` for parameter setup error.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/longmatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.c -->
## sources/compression/zstd/tests/loremOut.c

Purpose: Implements a stdout generator for large lorem-ipsum-style compressible data streams.

Important APIs and functions: Exposes `LOREM_genOut(unsigned long long size, unsigned seed)`. Internally uses `LOREM_genBlock`, `SET_BINARY_MODE(stdout)`, a 1 KiB stack buffer, `fwrite`, and assertions.

Control flow: The function sets stdout to binary mode, chooses an initial block size of `min(size, 1024)`, then loops until exactly `size` bytes are emitted. Each iteration calls `LOREM_genBlock` with incrementing seed and a first-block flag, writes the generated bytes, updates the total, and shrinks the final block size if fewer bytes remain.

State and persistence: Writes generated bytes to stdout. Maintains only local counters and buffer state; no heap or files are used.

Dependencies and integration points: Used by test tools needing deterministic, compressible, potentially larger-than-4-GiB output without holding the data in memory. Depends on `lorem.h` and platform binary-mode handling.

Risks: The code notes it does not check `fwrite` errors, so broken pipes or disk-full stdout may not be reported. Assertions catch generator overshoot in debug builds only. Output differs from `LOREM_genBuffer` after the first paragraph even with the same seed.

Test signals: Consumers should verify exact byte count and deterministic stream behavior; direct function failure is not signaled except through assertions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.h -->
## sources/compression/zstd/tests/loremOut.h

Purpose: Declares the large lorem-output generator API for zstd tests.

Important APIs and types: Declares `void LOREM_genOut(unsigned long long size, unsigned seed);`.

Control flow and integration: Test programs include this header and call `LOREM_genOut` when they want compressible bytes streamed directly to stdout instead of an in-memory buffer.

State and persistence: The declaration implies stdout side effects implemented in `loremOut.c`; the header owns no state.

Dependencies and integration points: Must remain in sync with `loremOut.c`. Uses only standard integer types available without including extra headers because `unsigned long long` and `unsigned` are built-in C types.

Risks: No include guard is present, though the header only contains one compatible declaration. Repeated inclusion is unlikely to break but is not ideal.

Test signals: Compile-time linkage should resolve `LOREM_genOut` exactly once from `loremOut.c`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/paramgrill.c -->
## sources/compression/zstd/tests/paramgrill.c

Purpose: Benchmark and optimization tool for exploring zstd compression parameters, generating candidate compression-level tables, and finding parameter sets that satisfy speed, ratio, and memory constraints.

Important APIs and types: Core parameter modeling uses `varInds_t`, `paramValues_t`, `constraint_t`, `winnerInfo_t`, `memoTable_t`, and `buffers_t`/`contexts_t`. Parameter conversion helpers include `rangeMap`, `invRangeMap`, `sanitizeParams`, `pvalsToCParams`, `cParamsToPVals`, `adjustParams`, `paramValid`, `emptyParams`, and `overwriteParams`. Benchmark integration uses `BMK_benchMemInvertible`, `BMK_benchParam`, `allBench`, and `benchMemo`. Search logic uses `BMK_seed`, `playAround`, `BMK_generate_cLevelTable`, `climbOnce`, `optimizeFixedStrategy`, and `optimizeForSize`. CLI parsing uses `longCommandWArg`, `readU32FromChar`, `readDoubleFromChar`, and `parse_params`.

Control flow: `main()` parses modes, parameter constraints, display options, dictionaries, block size, time limit, and input files. With no input and no optimizer, it generates a 10 MiB sample and either benchmarks one configuration or generates a level table. With files, it loads data into block buffers, optionally loads a dictionary, and either runs a single benchmark, generates a table, or performs optimizer hill climbing. The optimizer first benchmarks default levels to seed strategy selection, then climbs within and around strategies using memoized candidate rejection until time or try limits stop the search.

State and persistence: Global state controls runtime (`g_timeLimit_s`, `g_time`, `g_blockSize`, `g_rand`), display (`g_displayLevel`, `g_silenceParams`), modes (`g_singleRun`, `g_optimizer`, `g_optmode`), optimizer targets (`g_target`, `g_strictness`, `g_lvltarget`, `g_ratioMultiplier`), and winner lists. `BMK_generate_cLevelTable` writes `grillResults.txt` with intermediate and final proposed configurations. Input file contents, dictionaries, contexts, destination buffers, result buffers, memo tables, and winner lists are heap allocated.

Dependencies and integration points: Includes zstd static-linking-only APIs, internal `zstd_internal.h`, benchmark helpers (`benchfn.h`, `benchzstd.h`), random data generation, xxhash, time utilities, and file utilities. It emits `--zstd=...` command lines compatible with the zstd CLI advanced-parameter syntax.

Risks: This is resource- and time-intensive by design. Several paths call `exit(1)` directly on parse or output errors. Memoization may use direct arrays or lossy xxhash tables, so collisions can suppress candidates. `readU32FromChar` accepts signed values by unsigned wrap for parameters such as force attach dict. Many globals make reentrancy impossible. `BMK_findMaxMem` probes large allocations and can affect hosts under memory pressure.

Test signals: Useful checks include `--zstd=` single-run output, `--optimize=` constraint parsing, dictionary and block-size operation, `grillResults.txt` creation for table generation, nonzero returns on invalid parameters, and stable round-trip validation inside `BMK_benchMemInvertible`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/paramgrill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/playTests.sh -->
## sources/compression/zstd/tests/playTests.sh

Purpose: Broad end-to-end zstd CLI acceptance suite covering compression, decompression, file handling, threading, recursion, dictionaries, alternative formats, list mode, trace mode, long distance matching, async I/O, patch mode, and optional large-data paths.

Important APIs and functions: Shell helpers include `die`, `datagen`, `sudoZstd`, `roundTripTest`, `fileRoundTripTest`, `truncateLastByte`, `println`, `assertSameMTime`, `assertFilePermissions`, and `assertSamePermissions`. It uses aliases around `$ZSTD_BIN`, `$DATAGEN_BIN`, `$EXE_PREFIX`, platform-specific `MD5SUM`, `DIFF`, `stat`, and optional `sudo`.

Control flow: Startup normalizes environment, detects platform, terminal state, zstd binary, datagen binary, and multithreading support. The default path runs many bounded tests: basic CLI options, stdout and `-o` precedence, terminal refusal, suffix and overwrite protections, memory limits, progress flags, checksums, executable stack, multithreading arguments, recursive and output-directory modes, file removal, golden decompression cases, multiple-file behavior, FIFOs, permissions, timestamps, filelists, content-size flags, advanced parameters, pass-through, frame concatenation, sparse output, stream-size and size-hint modes, dictionaries and dictionary builders, integrity tests, golden files, benchmark mode, compatibility with gzip/xz/lz4 formats, suffix lists, tar suffixes, round trips, long-distance matching, list mode, trace mode, and asyncio. If invoked with `--test-large-data`, it continues into adaptive, rsyncable, patch-from, very large round trips, and cover dictionary builder tests; otherwise it exits after asyncio checks.

State and persistence: Creates and removes many `tmp*` files and directories, symlinks such as `zstdcat`, `zcat`, `xz`, `lzma`, output dictionaries, traces, and compressed artifacts. It changes `umask` temporarily and restores it in the permissions section. Optional block-device and `/dev/null` permission tests can require sudo and affect system devices if explicitly enabled.

Dependencies and integration points: Integrates the zstd CLI with `datagen`, host `grep`, `diff`, `md5/md5sum`, `stat`, `tar`, optional `readelf`, optional format tools (`gzip`, `xz`, `lzma`, `lz4`), filesystem features such as symlinks and FIFOs, and zstd golden test data directories. It is the primary high-level test signal for many CLI modules.

Risks: The script runs with `set -e` and `set -x`, so command ordering and shell portability matter. It is platform-conditional but still broad enough to be flaky on minimal systems lacking optional tools. Many tests rely on exact diagnostics or mtime/permission behavior. Large-data mode can allocate or stream hundreds of MB to multiple GB and should be opt-in. The `zstd` alias does not affect all non-interactive shells equally, though the script also invokes `$EXE_PREFIX $ZSTD_BIN` in helper paths.

Test signals: Default success reaches the asyncio checks and exits `0` after "Skipping large data tests". With `--test-large-data`, success reaches the final cover dictionary builder cleanup. Any unexpected CLI success/failure, diff mismatch, missing file, permission/mtime mismatch, or grep mismatch aborts via `set -e` or `die`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/playTests.sh -->
