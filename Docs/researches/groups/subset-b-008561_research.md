# subset-b-008561 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/targets_builder.py -->
# sources/storage-engines/rocksdb/buckifier/targets_builder.py research

Purpose: `targets_builder.py` is the imperative writer used by RocksDB's buckifier flow to emit a generated Buck `TARGETS` file. It wraps string templates from `targets_cfg.py`, normalizes list formatting, and appends Buck macro invocations for libraries, RocksDB libraries, binaries, tests, benches, exported files, and oncall ownership.

Important APIs: `LiteralValue` marks values that must be emitted without quoting. `smart_quote_value()` and `pretty_list()` convert Python lists into deterministic Buck list fragments, sorting multi-item lists. `TARGETSBuilder.__init__()` creates/truncates the output file and writes the generated-file header. Builder methods include `add_oncall()`, `add_library()`, `add_rocksdb_library()`, `add_binary()`, `add_c_test()`, `add_test_header()`, `add_fancy_bench_config()`, `register_test()`, and `export_file()`.

Control flow: callers construct `TARGETSBuilder(path, extra_argv)` once and call append methods in generation order. Each method opens the same file in append mode, formats a template with normalized arguments, writes bytes or text, and updates simple counters for libraries, binaries, and tests.

State and persistence: persistent state is the generated file at `self.path`; in-memory state is limited to `total_lib`, `total_bin`, `total_test`, and an unused `tests_cfg` string. The output is not transactional beyond the initial truncating header write.

Dependencies and integration: the file imports `targets_cfg` template constants and `pprint` for bench configuration rendering. It is designed for the Meta-specific `buckifier/buckify_rocksdb.py` pipeline and generated Buck macros loaded by the header template.

Risks and test signals: generated syntax depends on template correctness and manual quoting rules. Sorting `pretty_list()` makes output stable but changes caller ordering. `LiteralValue` bypasses quotes, so unsafe input can inject arbitrary Buck expressions. Test signals are generated-file diffs, Buck parser failures, and successful Buck builds/tests consuming the generated `TARGETS`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/targets_builder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/targets_cfg.py -->
# sources/storage-engines/rocksdb/buckifier/targets_cfg.py research

Purpose: `targets_cfg.py` is a template-only companion to the RocksDB buckifier. It centralizes generated Buck syntax snippets used by `targets_builder.py`, including the file header, load statements, and macro call bodies for libraries, binaries, tests, benches, exports, and oncall metadata.

Important APIs: the module exposes constants rather than functions: `rocksdb_target_header_template`, `library_template`, `rocksdb_library_template`, `binary_template`, `unittests_template`, `fancy_bench_template`, `export_file_template`, and `oncall_template`. These constants are Python `str.format()` templates whose placeholders must match the arguments supplied by `TARGETSBuilder`.

Control flow: there is no runtime control flow beyond module import. The builder imports these strings and formats them during generation. The header template records the invoking buckifier command and loads wrapper macros from `//rocks/buckifier:defs.bzl` plus `export_file`.

State and persistence: the module is stateless and does not write files. Persistent output is produced only by consumers that format these templates into `TARGETS`.

Dependencies and integration: template bodies assume Buck/Starlark macro names such as `cpp_library_wrapper`, `rocks_cpp_library_wrapper`, `cpp_binary_wrapper`, `cpp_unittest_wrapper`, `fancy_bench_wrapper`, and `add_c_test_wrapper`. The header explicitly describes the generated file as Meta-specific and not generally validated outside Meta.

Risks and test signals: placeholder drift between `targets_cfg.py` and `targets_builder.py` will fail at generation time with `KeyError` or produce malformed Buck code. Some builder arguments, such as `extra_external_deps`, are accepted by builder APIs but not represented in the current template, which is a maintenance signal. Tests should compare generated `TARGETS` snapshots and run Buck parsing/build validation in the Meta environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/targets_cfg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/util.py -->
# sources/storage-engines/rocksdb/buckifier/util.py research

Purpose: `util.py` provides small shared helpers for RocksDB buckifier scripts: terminal coloring and shell-command execution with optional verbose logging. It supports both Python 2 and Python 3 compatibility.

Important APIs: `ColorString` exposes ANSI color constants plus static methods `ok()`, `info()`, `header()`, `error()`, and `warning()`. The class-level flag `ColorString.is_disabled` disables coloring. `run_shell_command(shell_cmd, cmd_dir=None)` runs a single shell command and returns `(returncode, stdout, stderr)`. `run_shell_commands(shell_cmds, cmd_dir=None, verbose=False)` executes a sequence and returns a boolean success indicator.

Control flow: `run_shell_command()` optionally creates `cmd_dir`, starts `subprocess.Popen(shell=True)`, captures stdout/stderr, waits for completion, and reports elapsed time for commands running longer than five minutes. `run_shell_commands()` iterates commands, prints captured output only when verbose or failing, and stops at the first nonzero return code.

State and persistence: no persistent state is maintained except directories created for `cmd_dir`. The main mutable state is the global color-disable flag. Commands can mutate the filesystem depending on their shell text.

Dependencies and integration: it depends on `os`, `subprocess`, `sys`, and `time`. The helper is intended for other buckifier scripts that need simple command orchestration and colored status output.

Risks and test signals: `shell=True` plus string interpolation is command-injection prone if untrusted input reaches these helpers. Automatic `mkdir -p` is also built from a raw shell string. Captured output is bytes under Python 3, so downstream formatting can differ from text expectations. Tests should cover command success/failure, verbose output behavior, disabled colors, Python 2/3 byte/text behavior, and missing-directory creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/amalgamate.py -->
# sources/storage-engines/rocksdb/build_tools/amalgamate.py research

Purpose: `amalgamate.py` converts a RocksDB unity-build source into an amalgamated C++ source and header. It recursively expands quoted `#include` directives, sending public headers to the generated header and private headers/source content to the generated source.

Important APIs: `find_header(name, abs_path, include_paths)` resolves includes relative to the current file first and then configured include paths. `expand_include()` guards against repeated expansion with the global `included` set and calls `process_file()`. `process_file()` is the recursive include expander. `main()` defines CLI arguments for source, private include paths `-I`, public include paths `-i`, excluded headers `-x`, source output `-o`, and header output `-H`.

Control flow: `main()` normalizes paths, seeds the global `excluded` set, opens output files, writes initial `#line` and header include directives, and processes the root source. `process_file()` scans each line; matching quoted includes are resolved first as private, then public. Expanded private includes are written to the source stream; expanded public includes are written to the header stream. `#pragma once` is dropped.

State and persistence: global `included` and `excluded` sets control expansion across the run. Persistent artifacts are the generated source and header. The script exits immediately if an include cannot be resolved.

Dependencies and integration: it uses `argparse`, `re`, `sys`, and `os.path`. It integrates with RocksDB release/build packaging where a single-file amalgamation is useful.

Risks and test signals: the single global include set can break code that intentionally includes the same header under different preprocessor branches. Angle-bracket includes are ignored by the regex. Public/private classification depends entirely on include path ordering. Test signals include compiling the generated amalgamation, checking stable output, and exercising excluded-header behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/amalgamate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/benchmark_log_tool.py -->
# sources/storage-engines/rocksdb/build_tools/benchmark_log_tool.py research

Purpose: `benchmark_log_tool.py` parses RocksDB benchmark TSV output and optionally uploads sanitized benchmark records to an OpenSearch/Elasticsearch document endpoint.

Important APIs: `Configuration` reads `ES_USER` and `ES_PASS` at class-definition time. `BenchmarkResultException` carries parser error content. `BenchmarkUtils.sanity_check(row)` validates required benchmark fields, integer `ops_sec`, and parseable dates. `BenchmarkUtils.conform_opensearch(row)` normalizes date fields and replaces dots in keys. `ResultParser` tokenizes benchmark lines with configurable field, whitespace, and separator regexes. Top-level functions include `load_report_from_tsv()`, `push_report_to_opensearch()`, and `push_report_to_null()`.

Control flow: the CLI parses `--tsvfile`, `--esdocument`, and `--upload`. The TSV loader reads all lines and parses records using the first non-comment row as the header. Upload mode filters rows through `sanity_check()`, conforms them, posts each JSON record using `requests.post()`, and raises on HTTP errors. Null mode validates and logs the conformed records without network writes.

State and persistence: local state is in parsed row dictionaries, which are mutated by `conform_opensearch()`. Persistence is external: HTTP writes to OpenSearch and log output. Credentials are read from environment variables.

Dependencies and integration: external dependencies are `requests` and `python-dateutil`. The script is aimed at benchmark automation, historically CircleCI scraper inputs, and OpenSearch graphing.

Risks and test signals: importing the module without `ES_USER`/`ES_PASS` can fail because `Configuration` reads environment variables eagerly even if upload is disabled. Parser behavior is custom and may mishandle quoted TSV fields. Upload performs one POST per row with no retry/backoff. Tests should cover TSV parsing edge cases, bad rows, date normalization, null upload, missing credentials, and mocked HTTP status failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/benchmark_log_tool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/build_detect_platform -->
# sources/storage-engines/rocksdb/build_tools/build_detect_platform research

Purpose: `build_detect_platform` is the Makefile-facing platform detection script for RocksDB. It detects compilers, OS, CPU architecture, optional libraries, feature macros, Java/link settings, and writes a make-include file named by its first argument.

Important APIs: this is a shell script rather than a sourced function library. Its "API" is the generated variable file containing `CC`, `CXX`, `AR`, `PLATFORM`, `PLATFORM_*FLAGS`, Java flags, shared-library settings, version numbers, analyzer paths, feature flags, and dependency paths. It is configured through many environment variables, including `ROCKSDB_CXX_STANDARD`, `USE_CLANG`, `TARGET_OS`, `TARGET_ARCHITECTURE`, `PORTABLE`, `LIB_MODE`, `COMPILE_WITH_TSAN`, and `ROCKSDB_DISABLE_*`.

Control flow: the script validates the output path, initializes C++ standard and POSIX flags, optionally sources Meta fbcode config on internal hosts, chooses compiler tools, detects target OS, probes a faster linker on Linux, sets OS-specific flags, and then runs many compile/link probes unless cross-compiling or using fbcode. It detects fallocate, compression libraries, gflags namespace, NUMA, TBB, jemalloc/tcmalloc, memkind, adaptive mutexes, backtrace, profiling, sync_file_range, sched_getcpu, getauxval, aligned new, benchmark, folly, io_uring, warning support, CPU tuning, uint128, and dynamic loading. Finally it reads RocksDB version components and appends key-value lines to the output file.

State and persistence: it removes and recreates the output file, creates temporary compile artifacts such as `test.o` and `test_dl.o`, and derives state from the host compiler, libraries, filesystem, and environment. It cleans temporary test objects near the end.

Dependencies and integration: it relies on POSIX shell tools, `uname`, `hostname`, compilers, `build_tools/version.sh`, optional Homebrew, optional Meta `/mnt/gvfs` third-party trees, and the RocksDB Makefile consuming the generated variables.

Risks and test signals: feature detection is host-sensitive and can silently change build behavior. Compile probes may be skipped for cross/fbcode builds, so defaults must remain correct. There is a typo-like variable use `PLATFORM_CXXFALGS` in the `F_FULLFSYNC` probe, which can weaken that test. Tests should run the script under controlled env combinations, inspect generated variables, and verify representative Linux/macOS/internal-platform builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/build_detect_platform -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-public-header.sh -->
# sources/storage-engines/rocksdb/build_tools/check-public-header.sh research

Purpose: `check-public-header.sh` is a lightweight guard for public RocksDB headers. It detects preprocessor conditionals that could create ODR violations when public headers compile differently in RocksDB and in downstream applications.

Important APIs: the script accepts header paths as command-line arguments. It has no functions; the observable contract is exit status 0 for clean input and 1 for detected issues.

Control flow: it initializes `BAD`, runs `grep -nHE '^#if' -- "$@"`, filters out known-safe or intentional patterns such as `ROCKSDB_NAMESPACE`, `ROCKSDB_ASSERT_STATUS_CHECKED`, Windows macros, `ODR-SAFE`, `__cplusplus`, and DLL export macros. If suspicious matches remain, it prints guidance and sets `BAD=1`; the final block exits nonzero when `BAD` is set.

State and persistence: there is no persistent state. It reads only the files named on the command line and writes diagnostics to stdout.

Dependencies and integration: it depends on `bash` and `grep`. It fits pre-commit, CI, or `make check` style validation for public API headers.

Risks and test signals: the grep pattern only sees lines beginning with `#if`, not all conditional forms or multi-line macros. False positives are expected and are suppressed with an `ODR-SAFE` marker after manual review. False negatives are possible for conditionals hidden behind formatting or macros. Tests should include safe and unsafe header snippets and validate the expected exit code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-public-header.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-sources.sh -->
# sources/storage-engines/rocksdb/build_tools/check-sources.sh research

Purpose: `check-sources.sh` is a repository hygiene guard for RocksDB source files. It blocks common mistakes before commit or push, including hardcoded namespace names, `nocommit` markers, incorrect include styles, broad `using namespace`, and non-ASCII source bytes.

Important APIs: the script takes no explicit arguments and reports violations through stdout plus its exit status. It uses the current Git repository as its input.

Control flow: it initializes `BAD`, runs a sequence of `git grep` checks, and treats any grep result other than "no matches" as a violation. It excludes itself and selected third-party/docs paths for some checks. At the end it exits 1 if any check set `BAD`.

State and persistence: it does not mutate files. It reads tracked Git content and relies on Git pathspec filtering. Output is diagnostic text.

Dependencies and integration: dependencies are `bash`, `git grep`, `grep` semantics, and locale control for the non-ASCII scan. It integrates naturally with CI and developer pre-submit checks.

Risks and test signals: checks are intentionally simple and can produce both false positives and false negatives. `git grep` only searches Git-visible content. The `*.[ch]*` pattern is broad and may include unexpected file extensions. Tests should run in a fixture Git repo with known violations and verify that each check toggles the exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-sources.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-workflow-yaml.sh -->
# sources/storage-engines/rocksdb/build_tools/check-workflow-yaml.sh research

Purpose: `check-workflow-yaml.sh` validates GitHub Actions workflow YAML files before CI runtime. It catches syntax-level YAML parsing errors under `.github/workflows`.

Important APIs: the script has no arguments and exits 0 only when Ruby and the `psych` YAML library are available and every workflow `.yml` or `.yaml` parses successfully.

Control flow: `set -euo pipefail` enables strict shell behavior. The script first checks for `ruby`, then checks that Ruby can `require "psych"`. It runs an embedded Ruby program that gathers workflow files, errors if none exist, parses each file with `Psych.parse_file`, prints `OK` for valid files, records failures, and exits nonzero if any parse failed.

State and persistence: it is read-only. State is limited to the Ruby-local `bad` flag and the list of discovered workflow files.

Dependencies and integration: it depends on Bash, Ruby, and Ruby's Psych package. It is intended for developer or CI validation around GitHub Actions configuration.

Risks and test signals: this validates YAML syntax, not GitHub Actions schema semantics. It will fail on systems without Ruby even if workflows are valid. Glob behavior is limited to direct files under `.github/workflows`. Tests should cover valid YAML, malformed YAML, empty workflow directory, missing Ruby/Psych environments, and expected exit codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check-workflow-yaml.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check_progress.sh -->
# sources/storage-engines/rocksdb/build_tools/check_progress.sh research

Purpose: `check_progress.sh` emits a JSON progress summary for RocksDB builds/tests. It is designed for machine polling while tests are being generated, compiled, linked, or executed.

Important APIs: the command takes no arguments and writes one JSON object to stdout. Helper functions are `json_escape()`, `output_json()`, and `get_failed_tests_json()`. Output fields include `status`, optional `phase`, `completed`, `total`, `failed`, `percent`, `eta_seconds`, `avg_time`, `last_item`, and optional `failed_tests`.

Control flow: if `LOG` exists, the script treats the run as test execution. It counts generated `t/run-*` files, completed rows in `LOG`, failures by exit/signal columns, failed-test logs from `t/log-run-*`, percentage, last test, average runtime, ETA, and status. Without `LOG`, it estimates compile/link progress from `src.mk`, object files in known source directories, and executable `*_test` binaries. If no artifacts exist, it reports `not_started`.

State and persistence: it reads build artifacts but does not write them. It shells out to Python 3 for robust JSON escaping when available, otherwise uses sed/awk fallback escaping. Failed test output is capped at 50 lines and 10 failures.

Dependencies and integration: it depends on Bash, coreutils, find, awk, sed, optional Python 3, the RocksDB parallel test `LOG` format, `t/` test scripts, and `src.mk`.

Risks and test signals: JSON correctness depends on escape fallback quality and unescaped numeric assumptions for exit/signal values. Compile progress is heuristic and tied to a hardcoded directory list. `find -printf` is GNU-specific. Tests should simulate LOG rows, failed logs, missing logs, generation phase, compile artifacts, and environments without Python 3.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/check_progress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/dependencies_platform010.sh -->
# sources/storage-engines/rocksdb/build_tools/dependencies_platform010.sh research

Purpose: `dependencies_platform010.sh` pins Meta internal third-party dependency roots for platform010 RocksDB builds. It is generated by `update_dependencies.sh` and consumed by fbcode configuration scripts.

Important APIs: the script exposes shell variables such as `GCC_BASE`, `CLANG_BASE`, `LIBGCC_BASE`, `GLIBC_BASE`, `SNAPPY_BASE`, `ZLIB_BASE`, `BZIP2_BASE`, `LZ4_BASE`, `ZSTD_BASE`, `GFLAGS_BASE`, `JEMALLOC_BASE`, `NUMA_BASE`, `LIBUNWIND_BASE`, `TBB_BASE`, `LIBURING_BASE`, `BENCHMARK_BASE`, `KERNEL_HEADERS_BASE`, `BINUTILS_BASE`, and `VALGRIND_BASE`.

Control flow: there is no branching or function logic. Sourcing the file assigns fixed absolute `/mnt/gvfs/third-party2/...` paths.

State and persistence: it does not write files. The effective state is the sourced shell environment and its pinned dependency versions/hashes.

Dependencies and integration: it assumes Meta's GVFS third-party tree exists. `fbcode_config_platform010.sh` sources it to construct compiler, include, and linker flags. `build_detect_platform` sources the platform010 config when it detects an internal host with the expected third-party directory.

Risks and test signals: paths are environment-specific and will fail outside Meta. Because it is generated, hand edits risk being overwritten. Stale pins can break builds or produce ABI mismatches. Test signals are successful sourcing, path existence checks in internal CI, and platform010 RocksDB builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/dependencies_platform010.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/dockerbuild.sh -->
# sources/storage-engines/rocksdb/build_tools/dockerbuild.sh research

Purpose: `dockerbuild.sh` is a minimal convenience wrapper for building RocksDB inside a Docker container based on the `buildpack-deps` image.

Important APIs: it exposes one command-line behavior: run `docker run -v $PWD:/rocks -w /rocks buildpack-deps make`. Any arguments passed to the script are ignored.

Control flow: there is no branching. The current working directory is bind-mounted into `/rocks`, the container working directory is set to `/rocks`, and `make` is invoked.

State and persistence: build artifacts are persisted in the host working directory because of the bind mount. Docker image pulls and container lifecycle are handled externally by Docker.

Dependencies and integration: it depends on Bash, Docker, network/image availability for `buildpack-deps`, and a Makefile in the current directory. It is a developer helper rather than a configurable CI entrypoint.

Risks and test signals: `$PWD` is unquoted, so paths containing spaces can break. Running as Docker's default user can create root-owned artifacts on the host. The image tag is not pinned, so build environments can change over time. Tests are basic: run in a disposable checkout, verify Docker starts, make executes, and host artifacts are usable afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/dockerbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/error_filter.py -->
# sources/storage-engines/rocksdb/build_tools/error_filter.py research

Purpose: `error_filter.py` reduces noisy CI/test output to known error lines for a named RocksDB test job. It reads merged stdout/stderr on stdin and prints matching error summaries.

Important APIs: `ErrorParserBase` defines the parser interface. `GTestErrorParser` tracks the most recent `[ RUN ]` test and reports GoogleTest failure locations. `MatchErrorParser` returns lines matching a regex. Specialized subclasses match compiler, scan-build, db crash, write stress, ASAN, UBSAN, Valgrind, compatibility, and TSAN errors. `_TEST_NAME_TO_PARSERS` maps CI job names to parser classes. `main()` validates the test name and streams stdin through parser instances.

Control flow: after argument validation, the script instantiates the parser list for the requested job. Each stripped input line is offered to each parser in order; any non-`None` parsed message is printed. `GTestErrorParser` updates internal last-test state on run lines and emits that test name on failure lines.

State and persistence: parser state is in memory only, primarily the last GoogleTest name. There are no file writes. Exit status is driven by `sys.exit(main())`; usage and unknown-test strings become nonzero process exits.

Dependencies and integration: it depends only on Python stdlib `re` and `sys`. It integrates with CI jobs that know their RocksDB job name and pipe test logs through this filter.

Risks and test signals: regexes are anchored and may miss format changes in tool output. Unknown job names produce an error instead of falling back to generic parsing. Stripping lines can alter spacing-sensitive diagnostics. Tests should feed representative logs for every parser class and verify output lines and unknown-job behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/error_filter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fb_compile_mongo.sh -->
# sources/storage-engines/rocksdb/build_tools/fb_compile_mongo.sh research

Purpose: `fb_compile_mongo.sh` builds MongoDB against a RocksDB checkout using Meta fbcode compiler and dependency settings. It is a specialized integration helper for the historical MongoDB/RocksDB storage engine path.

Important APIs: configuration is through environment variables and script arguments. `ROCKSDB_PATH` defaults to `~/rocksdb`. `ALLOC` selects allocator behavior; `jemalloc` is translated to Mongo's `system` allocator plus explicit whole-archive jemalloc linking. Remaining command-line arguments are forwarded to `scons`.

Control flow: the script exits on error, sources `fbcode_config4.8.1.sh` from the RocksDB path, prepares a static dependency directory with symlinks to snappy and lz4 libraries, builds extra linker flags, detects older Mongo 3.0 by absence of `version.json`, and then invokes `scons` with compiler, linker, library, include, optimization, allocator, and warning options.

State and persistence: it creates `build/static_library_dependencies` and symlinks inside it. The main persistence is Mongo build output created by `scons`.

Dependencies and integration: it depends on shell, fbcode config files, RocksDB static/shared libraries, MongoDB's `scons` build, snappy/lz4 libraries, and a Mongo source checkout as current directory.

Risks and test signals: the script is tightly coupled to old Mongo and old fbcode config names. Several variables are unquoted. `source` is used under `/bin/sh`, which assumes a shell compatible with that builtin. Tests require an internal environment; practical signals are successful `scons` configuration, symlink creation, and Mongo binaries linking with RocksDB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fb_compile_mongo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fbcode_config.sh -->
# sources/storage-engines/rocksdb/build_tools/fbcode_config.sh research

Purpose: `fbcode_config.sh` prepares environment variables for building RocksDB with Meta internal fbcode toolchains and dependency paths. It targets an older non-platform010 layout and is intended to be sourced by build scripts.

Important APIs: the script exports compiler variables `CC`, `CXX`, `AR`, flags `CFLAGS`, `CXXFLAGS`, `EXEC_LDFLAGS`, `EXEC_LDFLAGS_SHARED`, dependency-specific include/lib variables, `VALGRIND_VER`, `JEMALLOC_LIB`, `JEMALLOC_INCLUDE`, `CLANG_ANALYZER`, and `CLANG_SCAN_BUILD`. Behavior is controlled by `PIC_BUILD`, `USE_CLANG`, `ROCKSDB_DISABLE_*`, `USE_SSE`, and `PORTABLE`.

Control flow: it derives `BASEDIR`, sources `dependencies.sh`, builds include/lib variables for libgcc, glibc, compression libraries, gflags, jemalloc, numa, libunwind, and TBB, sets default portability/SSE options, selects GCC or Clang toolchain branches, appends RocksDB feature macros, constructs linker flags including dynamic linker/rpath, and exports the resulting environment.

State and persistence: it mutates only the current shell environment when sourced. It does not write files.

Dependencies and integration: it assumes Meta third-party dependency variables from `dependencies.sh`. It is consumed by internal build flows and older scripts such as `fb_compile_mongo.sh`.

Risks and test signals: this file is highly environment-specific and appears fragile: the `CLANG_SCAN_BUILD` assignment is missing a closing quote in the viewed source, which can break sourcing. It also uses `$BASH_SOURCE` while declaring `/bin/sh`, and many unquoted variables. Test signals are successful sourcing in both GCC and Clang modes and successful RocksDB internal builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fbcode_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fbcode_config_platform010.sh -->
# sources/storage-engines/rocksdb/build_tools/fbcode_config_platform010.sh research

Purpose: `fbcode_config_platform010.sh` is the platform010 successor to `fbcode_config.sh`. It sets compilers, sysroot-like include restrictions, dependency paths, RocksDB feature macros, and linker flags for Meta internal platform010 builds.

Important APIs: when sourced, it exports `CC`, `CXX`, `AR`, `AS`, `CFLAGS`, `CXXFLAGS`, `EXEC_LDFLAGS`, `EXEC_LDFLAGS_SHARED`, `VALGRIND_VER`, `JEMALLOC_LIB`, `JEMALLOC_INCLUDE`, `CLANG_ANALYZER`, and `CLANG_SCAN_BUILD`. It consumes `PIC_BUILD`, `USE_CLANG`, `ROCKSDB_DISABLE_*`, `USE_SSE`, and `PORTABLE`.

Control flow: the script sources `dependencies_platform010.sh`, starts with an invalid sysroot to prevent accidental default-library use, selects `_pic` variants when `PIC_BUILD` is set, builds include/lib variables for compression, gflags, benchmark, jemalloc, numa, libunwind, TBB, liburing, and kernel headers, defaults SSE and portability, selects GCC or Clang compiler branches, appends POSIX and RocksDB feature macros including io_uring, constructs static dependency linker flags and platform linker flags, then exports the environment.

State and persistence: there are no file writes; the sourced shell environment is the state. The dependency versions are pinned indirectly through `dependencies_platform010.sh`.

Dependencies and integration: it assumes Meta GVFS third-party roots, binutils, GCC/Clang layouts, platform010 runtime paths, and RocksDB's Makefile/build scripts. `build_detect_platform` sources this file for internal platform010 host builds.

Risks and test signals: it is not portable outside Meta. The deliberate `/DOES/NOT/EXIST` sysroot improves hermeticity but makes missing includes fail hard. ABI correctness depends on consistent pinned paths. Tests should source under GCC/Clang and PIC/non-PIC combinations and verify a complete RocksDB build with compression, benchmark, and io_uring features.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/fbcode_config_platform010.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/format-diff.sh -->
# sources/storage-engines/rocksdb/build_tools/format-diff.sh research

Purpose: `format-diff.sh` checks or applies clang-format changes only to modified lines, and additionally adds standard copyright headers to newly added `.h`, `.cc`, and `.py` files.

Important APIs: options are `-c` for check-only, `-y` for non-interactive auto-apply, and `-h` for usage. Environment variables include `CLANG_FORMAT_DIFF`, `PYTHON`, `FORMAT_REMOTE`, `FORMAT_UPSTREAM`, `VERBOSE_CHECK`, and normal Git state.

Control flow: it parses options, resolves repo root, locates a working `clang-format-diff` command or script, validates Python support when needed, then enables `set -e`. If there are uncommitted changes, it formats diff hunks against `HEAD`; otherwise it formats changes since the merge base with the RocksDB upstream branch. It detects newly added files and prepends copyright headers when missing. If clang-format produces no diff, it exits cleanly. In check-only mode it exits 1 for needed formatting. Otherwise it prints a colored diff, prompts unless `-y`, applies formatting, and can optionally amend the last commit in post-commit mode.

State and persistence: it can modify source files by adding headers and applying clang-format diffs. It can also run `git commit --amend` after user confirmation. Temporary files are created via `mktemp` for header insertion.

Dependencies and integration: it depends on Git, Bash, clang-format-diff, clang-format, optional Python, sed, curl instructions for missing tools, and repository remote metadata. It is used by developer formatting workflows and possibly `make format`.

Risks and test signals: the script mutates files even before final formatting decisions when adding copyright headers. Some variables and test expressions are unquoted. It only excludes `third-party/`. Interactive `/dev/tty` reads fail in non-interactive contexts unless `-y` or `-c` is used. Tests should cover check-only, auto-apply, uncommitted and post-commit modes, missing tool resolution, and new-file header insertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/format-diff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/getdeps_fallback_mirror.py -->
# sources/storage-engines/rocksdb/build_tools/getdeps_fallback_mirror.py research

Purpose: `getdeps_fallback_mirror.py` pre-downloads selected getdeps packages from fallback mirrors when canonical GNU mirrors are unreliable. It reads package manifests from Folly/getdeps metadata and prepares validated downloads for a single build.

Important APIs: constants define timeouts, chunk size, maximum download size, known mirror patterns, and packages to check. Functions include `sha256_file()`, `parse_manifest()`, `file_size()`, `get_fallback_mirrors()`, `download_url()`, `prepare_download()`, and `main()`.

Control flow: `main()` expects `download_dir`, `cache_dir`, and `manifests_dir`, creates the first two, loops over `PACKAGES_TO_CHECK`, parses each manifest's `[download]` URL and sha256, verifies a known fallback mirror exists, and calls `prepare_download()`. `prepare_download()` validates any existing download, repairs from cache when possible, tries mirror URLs in order, verifies SHA256 after each download, copies successful downloads into cache, and reports ready/checked counts.

State and persistence: it writes package files into `download_dir`, opportunistically writes/copies cache files in `cache_dir`, and uses temporary `.tmp` files that are removed on success or failure. Invalid existing files are deleted.

Dependencies and integration: it uses Python stdlib only: `configparser`, `hashlib`, `os`, `shutil`, `sys`, and `urllib.request`. It integrates with RocksDB/Folly getdeps workflows that expect downloaded files named `{package}-{basename(url)}`.

Risks and test signals: cache use is explicitly not concurrency-safe without external locking. Only known GNU mirror URL patterns and selected packages are handled. The 50 MiB cap can reject legitimate future package sizes. Tests should mock manifests, mirrors, checksum mismatch, partial download cleanup, existing valid downloads, cache repair, and network failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/getdeps_fallback_mirror.py -->
