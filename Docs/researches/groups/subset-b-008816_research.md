# subset-b-008816 research

Grouped research report for subset B item `subset-b-008816`. Each section preserves the source path and is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqlite3_rsync.c -->
# sources/storage-engines/sqlite/tool/sqlite3_rsync.c

## Purpose
`sqlite3_rsync.c` is a standalone SQLite utility that copies a live SQLite database from an origin to a replica using a custom rsync-like protocol. It minimizes bandwidth by comparing page hashes, then sending only pages that differ. It supports local-to-remote, remote-to-local, and local-to-local operation, with SSH used for remote execution of the same binary in `--origin` or `--replica` mode.

## Important APIs, types, and functions
The central state carrier is `SQLiteRsync`, which stores origin/replica paths, streams, debug/error files, the SQLite connection, verbosity, protocol version, WAL-only policy, byte counters, page metadata, and hash/page statistics. Protocol constants define origin messages (`ORIGIN_BEGIN`, `ORIGIN_DETAIL`, `ORIGIN_PAGE`, `ORIGIN_TXN`, `ORIGIN_END`, etc.) and replica messages (`REPLICA_HASH`, `REPLICA_CONFIG`, `REPLICA_READY`, etc.).

Process integration is handled by `popen2()`/`pclose2()`, with Unix pipe/fork/exec support and a Windows `CreateProcessW` implementation. `append_escaped_arg()` and `add_path_argument()` build shell-safe SSH commands, including a retry path for remote shells with limited `PATH`.

The file embeds a reduced-round Keccak hash engine exposed to SQLite as `hash(X)` and `agghash(X)` through `hashRegister()`. SQL helpers (`prepareStmt()`, `runSql()`, `runSqlReturnUInt()`, `runSqlReturnText()`) centralize statement preparation and error reporting. Wire helpers (`readUint32()`, `writeUint32()`, `readByte()`, `writeByte()`, `readBytes()`, `writeBytes()`, `readPow2()`, `writePow2()`) implement the binary protocol. The core protocols are `originSide()` and `replicaSide()`, while `sendHashMessages()` and `subdivideHashRange()` drive hash batching.

## Control flow
`main()` parses options, determines which of `ORIGIN` or `REPLICA` is remote using `hostSeparator()`, launches the remote side with SSH or a local child process, then runs either `originSide()` or `replicaSide()` locally. Direct `--origin` and `--replica` modes run over stdin/stdout for remote invocation.

On the origin side, the tool opens the origin database read/write, starts a transaction, registers hash functions, reads `page_count` and `page_size`, sends `ORIGIN_BEGIN`, then receives replica hashes. Mismatched hashes are stored in a temp `badHash` table. For protocol v2, multi-page hash mismatches produce `ORIGIN_DETAIL` requests so the replica can subdivide ranges. Once detail is sufficient, the origin reads changed pages from `sqlite_dbpage('main')`, skips the lock-byte page, sends `ORIGIN_PAGE` records, then sends `ORIGIN_TXN` and `ORIGIN_END`.

On the replica side, `ORIGIN_BEGIN` causes an in-memory SQLite database to attach the replica file as schema `replica`. It creates a `sendHash` table, checks page size and WAL policy, builds initial hash ranges, and sends hashes. When pages arrive, it writes them through `sqlite_dbpage(pgno,data,schema)`. At `ORIGIN_TXN`, it truncates if needed by inserting `NULL` at page `nOPage+1`, then commits.

## State and persistence behavior
Persistent state is the replica database file and possibly its WAL/journal files. The origin runs inside a read transaction to observe a stable snapshot. The replica uses `BEGIN IMMEDIATE` and writes raw database pages with `PRAGMA writable_schema=ON` and `sqlite_dbpage`; this is intentionally low-level and bypasses normal table-level SQL semantics. Debug/error/log files are appended or written when configured. Counters in `SQLiteRsync` are runtime-only.

If the replica started in WAL mode, page 1 header bytes are adjusted to avoid switching it out of WAL mode. `--wal-only` rejects synchronization when the origin or existing replica is not WAL. The protocol may retry remote command startup with a `PATH=...` prefix if the first SSH invocation yields no hashes.

## Dependencies and integration points
The utility depends on SQLite core APIs, the `sqlite_dbpage` virtual table, SQLite string builders, SQLite VFS time, the `sha1` extension initializer declaration, standard C/POSIX or Win32 process APIs, and SSH for remote operation. It integrates with SQLite build tooling as a command-line binary and with remote systems by invoking the same binary with `--origin`/`--replica`.

## Risks and edge cases
The protocol is binary and stateful; any desynchronization can produce confusing message errors. It relies on raw page writes, so page size mismatches, encoding attach failures, WAL mode transitions, interrupted writes, or missing `sqlite_dbpage` support are high-risk. The reduced-round hash is for change detection, not cryptographic authentication. Command construction is careful, but remote path parsing still treats `HOST:PATH` syntax specially and can be ambiguous with unusual filenames. `pclose2()` waits for any child with `waitpid(0,...)`, which is acceptable for this utility but broad. Error handling counts write failures separately and loops while `nErr <= nWrErr`, so communication failures are central to correctness.

## Test signals
Useful test signals include `--commcheck`, `--arg-escape-check`, protocol downgrade via `--protocol`, `--wal-only` rejection cases, verbose counters (`hashes`, rounds, page updates), local-to-local sync, remote-origin and remote-replica modes, page-size mismatch tests, and database content verification after sync. Debug logs from `--debugfile` expose exact message flow.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqlite3_rsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqltclsh.c.in -->
# sources/storage-engines/sqlite/tool/sqltclsh.c.in

## Purpose
`sqltclsh.c.in` is an input template for building a Tcl shell with SQLite compiled in. It embeds `sqlite3.c`, SQLite append VFS support, the Tcl SQLite extension wrapper, and optionally ZIP/SQL archive extensions, then returns the startup Tcl script from `tool/sqltclsh.tcl`.

## Important APIs, types, and functions
The template defines `TCLSH_INIT_PROC` as `sqlite3_tclapp_init_proc`, adjusts SQLite compile-time options for a small single-threaded shell, and uses template `INCLUDE` directives for generated amalgamation input. `sqlite3_tclapp_init_proc(Tcl_Interp*)` initializes `appendvfs` and registers `sqlar`/`zipfile` auto-extensions when zlib is enabled.

## Control flow
Generated code starts through the Tcl shell harness. During initialization, the custom init proc registers SQLite-related extensions, then returns an embedded Tcl startup script using the `BEGIN_STRING`/`END_STRING` template mechanism.

## State and persistence behavior
This file itself persists no state. At runtime, it registers process-global SQLite auto-extensions and uses append VFS to locate startup scripts in an appended SQLite database, a database passed as the first argument, a `.tcl` file, or falls back to interactive Tcl.

## Dependencies and integration points
It depends on the SQLite source-generation system that expands `INCLUDE`, Tcl headers/runtime via `tclsqlite-ex.c`, `appendvfs.c`, and optional zlib-backed `zipfile.c` and `sqlar.c`. It is integrated with the SQLite build as a specialized shell target.

## Risks and edge cases
Compile-time options deliberately disable SQLite threadsafety and several metadata/deprecated APIs, so this binary is purpose-built and not a general embedded SQLite distribution. Optional archive features depend on `SQLITE_HAVE_ZLIB`. Startup script lookup relies on append VFS behavior and the generated template expansion.

## Test signals
Build success of the generated shell, startup from an appended database, startup from a database argument, direct `.tcl` execution, interactive fallback, and zlib/no-zlib builds are the main validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqltclsh.c.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/src-verify.c -->
# sources/storage-engines/sqlite/tool/src-verify.c

## Purpose
`src-verify.c` verifies that a Fossil-generated SQLite source checkout matches its `manifest` and `manifest.uuid`. It recomputes the check-in SHA3-256 hash from the manifest, verifies every listed file against its SHA1 or SHA3 hash, and reports either an OK version or changed/missing files.

## Important APIs, types, and functions
The file is self-contained and implements SHA1 (`SHA1Context`, `SHA1Transform()`, `SHA1Init()`, `SHA1Update()`, `SHA1Final()`) and SHA3-256 (`SHA3Context`, `KeccakF1600Step()`, `SHA3Init()`, `SHA3Update()`, `SHA3Final()`). `DigestToBase16()` serializes digests. `sha1sum_file()` and `sha3sum_file()` hash disk files. `defossilize()` decodes Fossil filename escapes. `errorMsg()` and `errorMsgNH()` produce human and script-oriented error output.

## Control flow
`main()` handles debug hash modes (`--sha1`, `--sha3`) or normal verification. In normal mode it opens `<ROOT>/manifest`, hashes its pre-comment lines to derive `zVers`, then rewinds and processes `F` records. Each file path is appended to the root path, defossilized, checked for readability, and hashed according to the manifest hash length. It finally verifies `<ROOT>/manifest.uuid` is a 64-character SHA3 line equal to `zVers`.

## State and persistence behavior
No persistent state is modified. The program reads the manifest, manifest.uuid, and source files. Runtime state is bounded to fixed-size path/hash/line buffers plus hash contexts.

## Dependencies and integration points
The utility uses only the C standard library plus `access()` compatibility wrappers on Windows. It is meant to run in SQLite/Fossil release or source-integrity checks and can be compiled independently.

## Risks and edge cases
Path and line buffers are large but fixed; extremely long manifest records are truncated into `zFile`/`zHash` and treated as manifest errors or incorrect files. The code assumes the check-in hash is SHA3-256 and only accepts file hashes of length 40 or 64. Option parsing checks `argv[1]` for `--sha1`/`--sha3` inside the loop, so those modes are intended only as first-argument modes.

## Test signals
Signals include `src-verify ROOT` printing `OK <hash>`, `-x` first-line hash plus changed files, `-v` manifest debug listing, `--sha1 FILE...` and `--sha3 FILE...` outputs, deliberate modified/missing files, malformed manifest hashes, and mismatched `manifest.uuid`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/src-verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/srcck1.c -->
# sources/storage-engines/sqlite/tool/srcck1.c

## Purpose
`srcck1.c` is a small static-analysis utility for `sqlite3.c`. It detects side effects inside `assert()`, `ALWAYS()`, `NEVER()`, and `testcase()` arguments so debug-only or test-only expressions do not alter program behavior.

## Important APIs, types, and functions
`readFile()` loads the complete input file. `hasSideEffect()` scans an expression for assignment, increment, or decrement operators, unless it sees `/*side-effects-ok*/`. `findCloseParen()` finds the matching end of a macro argument by counting nested parentheses. `findAllSideEffects()` scans source text, tracks line numbers, identifies target macro invocations, and reports suspicious expressions.

## Control flow
`main()` requires one filename, reads it, invokes `findAllSideEffects()`, frees the buffer, and exits nonzero if any undesirable side effects were found.

## State and persistence behavior
No files are written. The entire source file is held in memory for scanning. The only state is the line counter and error count.

## Dependencies and integration points
It depends only on standard C headers and is integrated as a source-quality gate for SQLite amalgamation checks.

## Risks and edge cases
The analyzer is heuristic, not a C parser. It can miss effects hidden behind function calls and can misread tokens in comments or strings. It deliberately allows annotated cases with `/*side-effects-ok*/`. Its parenthesis matcher ignores C lexical states, so malformed or unusual macro arguments can skew results.

## Test signals
Useful tests include macros with plain comparisons, assignment, `++`, `--`, nested parentheses, annotated `/*side-effects-ok*/`, and a clean `sqlite3.c` scan returning zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/srcck1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/stripccomments.c -->
# sources/storage-engines/sqlite/tool/stripccomments.c

## Purpose
`stripccomments.c` filters stdin to stdout while removing C (`/* ... */`) and C++ (`// ...`) comments. It optionally preserves the first N comments via repeated `--keep-first`/`-k`, typically for license headers.

## Important APIs, types, and functions
Global `App` stores input/output streams, return code, and keep count. `do_it_all()` implements a character-level state machine with states `S_NONE`, `S_SLASH1`, `S_CPP`, and `S_C`. It preserves string-like literals delimited by single quote, double quote, or backtick, treating backslash as an escape marker. `usage()` reports valid flags.

## Control flow
`main()` parses only `-k`/`--keep-first`, assigns stdin/stdout to `App`, and calls `do_it_all()`. The filter scans one character at a time, delaying output of `/` until it knows whether it begins a comment. When inside comments, it either suppresses output or passes through preserved comments. Newlines end `//` comments and update line/column counters.

## State and persistence behavior
The program is streaming and writes only stdout. It maintains parser state, previous character, line/column counters, and a `state3Col` workaround for a corner case involving `/*/`.

## Dependencies and integration points
It uses only standard C and is a source preprocessing helper for build or analysis pipelines that need comment-stripped input.

## Risks and edge cases
The tool assumes legal C-like code and is intentionally limited. It can strip comment-looking text inside heredocs or language-specific constructs. Regex handling is only a narrow workaround for slash-asterisk preceded by backslash. Unterminated string literals are reported as errors, but unterminated comments receive little special handling.

## Test signals
Tests should cover normal block and line comments, repeated `-k`, strings containing comment markers, backtick literals, escaped quotes, the documented `/*/` corner case, and unexpected EOF inside a string.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/stripccomments.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/symbols-mingw.sh -->
# sources/storage-engines/sqlite/tool/symbols-mingw.sh

## Purpose
`symbols-mingw.sh` builds SQLite amalgamation objects under selected feature combinations and prints exported and undefined symbols, with settings suited to a MinGW/GCC environment.

## Important APIs, types, and functions
The script has no shell functions. It runs `make sqlite3.c`, compiles `sqlite3.c` with feature defines such as FTS3, RTREE, memory management, STAT3, MEMSYS5, unlock notify, column metadata, and atomic write, then uses `nm`/`grep` to report text/data exports and undefined dependencies.

## Control flow
It first reports exports for an extension-enabled build, then surplus exports not matching `sqlite3_`, then dependencies for a core build with `SQLITE_OS_OTHER` and no threads, then dependencies for the feature-enabled build.

## State and persistence behavior
It creates or overwrites `sqlite3.o` in the current build directory and may generate `sqlite3.c` through make. It does not persist reports except stdout.

## Dependencies and integration points
It depends on a valid SQLite makefile, `gcc`, `nm`, `grep`, and shell. It is a manual symbol-audit tool for release/build verification.

## Risks and edge cases
The script assumes GCC-style flags and `nm` output. It has no `set -e`, so later commands may run after earlier failures. Filtering is simple and can produce false positives or miss symbols with platform-specific naming.

## Test signals
Expected signals are generated `sqlite3.o`, visible `sqlite3_` exports, an empty or reviewed surplus-symbol list, and acceptable undefined dependencies for core and extension builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/symbols-mingw.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/symbols.sh -->
# sources/storage-engines/sqlite/tool/symbols.sh

## Purpose
`symbols.sh` is the Unix-oriented symbol audit script for SQLite amalgamation builds. It verifies exported public symbols and undefined dependencies under feature-rich and core configurations.

## Important APIs, types, and functions
The script runs `make sqlite3.c`, compiles with GCC and feature defines including FTS3, RTREE, STAT3, MEMSYS5, unlock notify, column metadata, preupdate hook, session, FTS5, and GEOPOLY, then uses `nm`, `grep`, `egrep`, and `sort`.

## Control flow
It prints four reports: exported symbols from the extension-rich object, surplus exported symbols excluding accepted `sqlite3`, session, rebaser, changeset, and changegroup prefixes, undefined dependencies for a no-OS/no-thread core build, and undefined dependencies for an RTREE/FTS4 build.

## State and persistence behavior
The script regenerates `sqlite3.c` and repeatedly overwrites `sqlite3.o` in the working directory. Output is stdout-only.

## Dependencies and integration points
It depends on make, GCC, nm, grep/egrep/sort, and SQLite amalgamation build rules. It is a release engineering and ABI hygiene helper.

## Risks and edge cases
No strict error mode is set. Regex allowlists encode policy and may need updates when new public APIs are added. Results depend on compiler, platform object format, and `nm` formatting.

## Test signals
A clean run should show only intentional public exports, no unexpected surplus symbols, and dependency lists consistent with the selected core/extension builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/symbols.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/tclConfigShToMake.sh -->
# sources/storage-engines/sqlite/tool/tclConfigShToMake.sh

## Purpose
`tclConfigShToMake.sh` converts selected variables from a Tcl `tclConfig.sh` file into Makefile assignments for SQLite build logic.

## Important APIs, types, and functions
The script has no functions. If given a path, it sources that file and emits `TCL_INCLUDE_SPEC`, `TCL_LIB_SPEC`, `TCL_STUB_LIB_SPEC`, `TCL_EXEC_PREFIX`, and `TCL_VERSION`. If no path is provided, it emits empty assignments for the same variables.

## Control flow
It conditionally sources `$1`, then writes a here-document containing Makefile variable assignments.

## State and persistence behavior
No persistent state is modified. It reads a caller-validated config file and writes generated make syntax to stdout.

## Dependencies and integration points
It depends on POSIX shell and a trusted/readable Tcl config script. It is used by `main.mk` as an indirection when configure did not provide Tcl build settings.

## Risks and edge cases
Sourcing an arbitrary file executes shell code, so the caller must validate and trust the input. Values are emitted without escaping beyond shell expansion, so embedded newlines or Make-special syntax could affect the generated makefile fragment.

## Test signals
Test with no argument, with a normal `tclConfig.sh`, and with values containing spaces or flags. The expected output is five Makefile assignments.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/tclConfigShToMake.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/varint.c -->
# sources/storage-engines/sqlite/tool/varint.c

## Purpose
`varint.c` is a command-line converter between SQLite varint byte sequences and decimal integers.

## Important APIs, types, and functions
`hexValue()` parses one hex digit, `toHex()` formats a nibble, and `putVarint()` encodes a `u64` using SQLite's 1-to-9-byte varint representation. `main()` chooses decode mode when multiple arguments or a two-character hex byte is provided; otherwise it parses a signed or unsigned decimal and encodes it.

## Control flow
In hex-to-decimal mode, the program consumes up to 9 hex-byte arguments, accumulating seven payload bits per byte until a byte without the high bit appears, with the ninth byte contributing eight bits. In decimal-to-varint mode, it parses optional `+` or `-`, builds a `u64`, maps negative values through two's-complement representation, then calls `putVarint()` and prints decimal plus hex bytes.

## State and persistence behavior
No persistence. All conversion state is local variables and a 20-byte output buffer.

## Dependencies and integration points
It uses only standard C and is a developer/debugging helper for SQLite record/key encoding.

## Risks and edge cases
Decimal parsing does not detect overflow. Hex decode validates argument length but not that `hexValue()` returned nonnegative for both characters in every path, so invalid hex can produce nonsensical accumulation. Negative conversion depends on 8-byte `i64`/`u64` representation.

## Test signals
Known SQLite varint examples, 1-byte values, 9-byte max values, signed negative inputs, invalid hex bytes, extra arguments, and usage with no arguments are useful tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/varint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/version-info.c -->
# sources/storage-engines/sqlite/tool/version-info.c

## Purpose
`version-info.c` emits SQLite library version metadata, especially JSON consumed by the sqlite3 JavaScript API build.

## Important APIs, types, and functions
It includes `sqlite3.h` unless `TEST_VERSION` is set, then uses `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, and SCM macros (`SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, `SQLITE_SCM_DATETIME`). `usage()` documents flags. `main()` parses `--version`, `--version-number`, `--download-version`, `--source-id`, `--json`, and `--quote`.

## Control flow
With no information flags, it defaults to JSON. It computes the download-page integer form from `SQLITE_VERSION_NUMBER`, then either emits a compact JSON object with version/source/SCM fields or one selected scalar, optionally quoted.

## State and persistence behavior
No persistence. Output is stdout only.

## Dependencies and integration points
It depends on SQLite compile-time version macros and standard C. It is integrated into JS/release build steps that need machine-readable version information.

## Risks and edge cases
The JSON path assumes `SQLITE_SOURCE_ID+20` points at the SHA3 portion, which depends on SQLite source ID format. Multiple scalar flags are counted but the output uses the first matching branch in fixed order. Unknown flags print usage and fail.

## Test signals
Run with no flags, each scalar flag, `--quote`, `--json`, and `TEST_VERSION` compilation. Validate JSON fields and download-version arithmetic.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/version-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/warnings-clang.sh -->
# sources/storage-engines/sqlite/tool/warnings-clang.sh

## Purpose
`warnings-clang.sh` runs Clang Static Analyzer (`scan-build`) over selected SQLite amalgamation builds to detect warnings.

## Important APIs, types, and functions
The script removes generated `sqlite3.c` and `shell.c`, rebuilds them with make, then invokes `scan-build gcc -c` for an FTS4/RTREE debug build and a STAT3 threadsafe-off build. It filters out `ANALYZE:` lines.

## Control flow
Execution is linear: clean generated files, make amalgamation and shell, run two analyzer compile commands, print labeled sections.

## State and persistence behavior
It deletes and regenerates `sqlite3.c` and `shell.c`, then creates compiler outputs as side effects. Reports go to stdout/stderr.

## Dependencies and integration points
It depends on shell, make, scan-build, gcc, and SQLite build rules. It is a manual static-analysis helper.

## Risks and edge cases
The shebang is written as `#/bin/sh` rather than `#!/bin/sh`, so direct execution may fail unless invoked through `sh`. No strict error handling is enabled. Analyzer availability and GCC/Clang wrapper behavior are environment-specific.

## Test signals
Successful make generation and analyzer output with no actionable warnings are the primary signals. Direct execution should also verify whether the shebang is tolerated by the caller.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/warnings-clang.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/warnings.sh -->
# sources/storage-engines/sqlite/tool/warnings.sh

## Purpose
`warnings.sh` compiles SQLite amalgamation variants with strict GCC warning flags to check for compiler warnings across feature configurations.

## Important APIs, types, and functions
The script determines warning flags by platform and GCC version. It builds `sqlite3.c`, then compiles feature-rich, Android-like Linux, STAT4 threadsafe-off, and optimized FTS/GEOPOLY configurations.

## Control flow
It sets `WARNING_OPTS` and `WARNING_ANDROID_OPTS`, removes `sqlite3.c`, runs `make sqlite3.c`, prints labeled sections, and invokes `gcc -c` with selected macro sets. On Linux it also compiles `sqlite3.c shell.c` with Android-oriented defines and ICU/load-extension omissions.

## State and persistence behavior
It regenerates `sqlite3.c` and produces object files in the current directory. It emits diagnostics to stdout/stderr but does not write reports.

## Dependencies and integration points
It depends on shell, uname, GCC, make, and SQLite generated sources. It is a local warning-gate helper used by maintainers.

## Risks and edge cases
The shebang is `#/bin/sh`, so direct execution may not select a shell. GCC version comparison is lexical and can be fragile. The `SQLITE_ENABLE_MATH_FUNCTIONS_fixme` define looks intentionally nonstandard and may be used to test warning behavior rather than enable the feature. No `set -e` means failures may cascade.

## Test signals
Expected test signals are warning-free compiler output in all labeled sections, correct OpenBSD/Linux/macOS flag selection, and Android configuration compilation on Linux.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/warnings.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/winmain.c -->
# sources/storage-engines/sqlite/tool/winmain.c

## Purpose
`winmain.c` provides a Windows Unicode command-line entry point that converts `wchar_t**` arguments to UTF-8 and calls a conventional `utf8_main(int,char**)`.

## Important APIs, types, and functions
It declares `extern int utf8_main(int,char**)` and implements `wmain()`. `WideCharToMultiByte(CP_UTF8,...)` is used first to size and then to populate each UTF-8 argument. Allocated argument strings are freed after `utf8_main()` returns.

## Control flow
`wmain()` allocates an argv array, converts each wide argument, null-terminates the array, calls `utf8_main(argc, argv)`, frees the allocated strings and array, and returns the wrapped program's exit code.

## State and persistence behavior
No persistent state. It only allocates transient process memory.

## Dependencies and integration points
It depends on Win32 APIs and standard C allocation/stdio. Programs include it after redefining `main` to `utf8_main` under `_WIN32`, allowing portable source to receive UTF-8 arguments on Windows.

## Risks and edge cases
If conversion fails for an argument, that argv slot becomes NULL; wrapped programs may not expect NULL inside `argv[0..argc)`. Allocation failures exit immediately. This file is Windows-only because it includes `windows.h`.

## Test signals
Tests should invoke a wrapped tool with ASCII, non-ASCII, and conversion-edge command lines, verifying `utf8_main()` receives UTF-8 bytes and exit codes propagate.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/winmain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/.config/nextest.toml -->
# sources/storage-engines/tikv/.config/nextest.toml

## Purpose
This Nextest configuration defines TiKV's `ci` test profile behavior.

## Important APIs, types, and functions
The `[profile.ci]` table sets `retries = 2`, disables fail-fast, sets a slow timeout of 60 seconds with termination after 2 periods, and limits failure output to final output. `[profile.ci.junit]` writes `junit.xml`.

## Control flow
Nextest reads this declarative configuration when invoked with the `ci` profile. There is no executable control flow in the file.

## State and persistence behavior
It causes test retry behavior and JUnit XML output. It does not persist application state.

## Dependencies and integration points
It integrates with `cargo nextest` and CI systems that collect JUnit output.

## Risks and edge cases
Retries can hide flaky tests if CI only inspects final success. Slow-timeout settings may terminate legitimate long-running tests. The JUnit path is fixed relative to the invocation directory.

## Test signals
Run `cargo nextest run --profile ci` and verify retries, non-fail-fast behavior, timeout handling, and `junit.xml` generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/.config/nextest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/.github/workflows/tikv-clippy-darwin.yml -->
# sources/storage-engines/tikv/.github/workflows/tikv-clippy-darwin.yml

## Purpose
This GitHub Actions workflow runs TiKV's clippy checks on macOS Intel and Apple Silicon pull requests.

## Important APIs, types, and functions
The workflow is named `Clippy (Darwin)`. It triggers on pull requests to `master` and `feature/**`, ignoring documentation/image and selected metadata-only changes. It defines `CMAKE_VERSION=3.28.0` and `GO_VERSION=1.25.7`, uses `actions/checkout@v4`, `actions/cache@v4`, and `dtolnay/rust-toolchain@stable` with `nightly-2025-02-28` plus rustfmt, clippy, rust-src, and rust-analyzer.

## Control flow
The job matrix runs on `macos-15-intel` for amd64 and `macos-15` for arm64. Steps install architecture-specific Go, install universal CMake under `/usr/local`, set Rust nightly components, cache Cargo registry/git/target by `Cargo.lock`, then run `make clippy`.

## State and persistence behavior
State is CI workspace files and cache entries. The job modifies `/usr/local/go`, installs CMake symlinks, and writes environment/GitHub path variables for later steps.

## Dependencies and integration points
It depends on GitHub-hosted macOS runners, network access to Go and CMake release artifacts, Rustup, Cargo, and TiKV's Makefile/scripts clippy pipeline.

## Risks and edge cases
Manual installation of Go and CMake can break if download URLs or runner permissions change. Cache includes `target/`, which can be large or stale across toolchain changes. The workflow is pull-request path-filtered, so ignored-file-only changes skip clippy.

## Test signals
Successful matrix completion, correct `go version` and `cmake --version`, Rust nightly availability, cache restore/save behavior, and `make clippy` success are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/.github/workflows/tikv-clippy-darwin.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/Cargo.toml -->
# sources/storage-engines/tikv/Cargo.toml

## Purpose
The root `Cargo.toml` defines the TiKV library package, workspace membership, feature topology, dependency graph, crates.io patches, workspace dependency aliases, and build/test/release profiles.

## Important APIs, types, and functions
The package is `tikv` version `9.0.0-beta.2`, Rust edition 2021, unpublished. Key features select allocators (`tcmalloc`, `jemalloc`, `mimalloc`, `snmalloc`), RocksDB portability/SSE, memory profiling, failpoints, test exports, test engines, frame-pointer pprof, and vendored OpenSSL. The `[workspace]` uses resolver 2, includes command crates, components, fuzz crates, and tests, excludes selected component folders, and defaults to `cmd/tikv-server` and `cmd/tikv-ctl`.

Dependencies span TiKV internal workspace crates for engines, raftstore, PD, security, resource control, backup, SQL coprocessor components, and utility crates, plus external crates for async, gRPC, protobuf, metrics, HTTP, crypto, serialization, and profiling. `[patch.crates-io]` redirects several crates to TiKV/PingCAP forks or local patches. Profiles tune compile speed and release size/performance.

## Control flow
Cargo uses this manifest to resolve feature propagation and workspace builds. Resolver 2 is explicitly required so features requested at the root propagate to command-crate direct dependencies as intended. Build behavior is further shaped by Makefile-provided features and environment variables.

## State and persistence behavior
The manifest itself does not write runtime state, but it controls compilation artifacts under Cargo target directories and the linked runtime behavior of TiKV binaries, including selected allocator, storage engine test features, OpenSSL linkage, and profiling support.

## Dependencies and integration points
It integrates every major TiKV component crate, command crates, fuzz/test crates, git dependencies (`raft-engine`, `kvproto`, `tipb`, `yatp`, patched protobuf/raft), and tooling such as cargo-machete. It is consumed by Cargo, Makefile targets, CI, Docker builds, and release scripts.

## Risks and edge cases
Large feature surfaces can produce accidental feature combinations, especially around allocator and RocksDB options. Git patches and forks increase supply-chain and reproducibility sensitivity. `openssl-vendored` is used to support static/FIPS-related builds but can lengthen builds. Profile choices disable some debug/overflow checks in dev for speed, which may hide issues outside tests.

## Test signals
Signals include `cargo metadata`, `cargo build --workspace --no-default-features --features ...`, `make clippy`, `make test`, cargo-machete ignored-dependency behavior, and release/profile builds for both `tikv-server` and `tikv-ctl`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/Dockerfile -->
# sources/storage-engines/tikv/Dockerfile

## Purpose
This Dockerfile builds a TiKV release image by compiling TiKV in a Rocky Linux builder and copying `tikv-server` and `tikv-ctl` into a runtime base image.

## Important APIs, types, and functions
It has three stages: `builder` from Rocky Linux 8.10 UBI, `building` that copies the source and runs `ROCKSDB_SYS_STATIC=1 make dist_release`, and final image from `ghcr.io/pingcap-qe/bases/tikv-base:v1.9.2`. It installs compiler/build tools, Go, OpenSSL development headers, CMake dependencies, protobuf `protoc`, and rustup.

## Control flow
The builder stage upgrades packages and installs dependencies, downloads architecture-specific protobuf compiler artifacts, and installs rustup without a default toolchain. The building stage compiles release binaries and verifies `tikv-server --version`. The final stage sets `MALLOC_CONF`, copies binaries to `/tikv-server` and `/tikv-ctl`, exposes ports 20160/20180, and sets `/tikv-server` as entrypoint.

## State and persistence behavior
The build creates Cargo/target artifacts in a cached mount and final image layers containing only runtime base plus two binaries. Runtime persistent data is external to this Dockerfile.

## Dependencies and integration points
It depends on public base images, DNF repositories, GitHub protobuf releases, rustup, TiKV Makefile release targets, and the PingCAP QE runtime base image.

## Risks and edge cases
The header notes the file may be outdated versus PingCAP QE artifacts. Network downloads and package repo availability affect reproducibility. Rust toolchain selection is delegated to repository configuration/Makefile. Static RocksDB and release builds are resource-intensive.

## Test signals
Docker build success, `/tikv/bin` copy success during build, `tikv-server --version`, final container startup, exposed service/status ports, and `tikv-ctl` presence validate this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/Makefile -->
# sources/storage-engines/tikv/Makefile

## Purpose
The TiKV Makefile wraps Cargo and project scripts for development, testing, static analysis, Docker images, release binaries, and distribution artifacts while injecting TiKV-specific feature and environment policy.

## Important APIs, types, and functions
Major variables include `ENABLE_FEATURES`, `TIKV_FRAME_POINTER`, allocator selectors, `ROCKSDB_SYS_PORTABLE`, `ROCKSDB_SYS_SSE`, `FAIL_POINT`, test-engine selectors, Docker image variables, build metadata exports, `CARGO_TARGET_DIR`, and `DIST_CONFIG`. Important targets include `build`, `release`, `dist_release`, `build_dist_release`, `test`, `test_with_nextest`, `format`, `clippy`, `audit`, `ctl`, `docker`, `docker_test`, `docker_shell`, `error-code`, and `x-build-dist`.

## Control flow
The Makefile computes default features based on OS/architecture and environment. Frame pointers are enabled by default and cause Rust standard library rebuild with nightly `-Z build-std`. Allocator features default to jemalloc, with Linux memory profiling. FIPS switches Dockerfile/tag and enables `gcp_v2/fips`; otherwise `openssl-vendored` is enabled. Build targets call Cargo directly or route distribution builds through `scripts/run-cargo.sh`. Clippy target chains project validation scripts before `scripts/clippy-all`.

## State and persistence behavior
Targets write Cargo target artifacts, `bin/`, `dist/`, Docker images/tags, generated `etc/error_code.toml`, cargo-sort installations, Rustup components/overrides, and possibly compressed/debug-optimized binaries via `dwz`/`objcopy`.

## Dependencies and integration points
It integrates Cargo, Rustup, project scripts, Docker, Python, Linux binary tools, cargo-audit, cargo-sort, cargo-udeps, and platform toolchains. It is the central entry point for CI and developer workflows.

## Risks and edge cases
Default frame-pointer behavior uses nightly-only build-std and can surprise local builds. Feature composition depends on environment variables and platform probes. Some recursive `make` calls do not pass `$(MAKE)`. Docker/release targets assume Linux tools for validation/compression. `cargo search cargo-audit` in `pre-audit` uses network and may be slow or flaky.

## Test signals
`make build`, `make release`, `make dist_release`, `make clippy`, `make test`, `make test_with_nextest`, `make ctl`, and Docker targets are direct signals. Build logs should show expected `TIKV_ENABLE_FEATURES`, frame-pointer flags, allocator selection, and generated binaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/ci-build/Makefile -->
# sources/storage-engines/tikv/ci-build/Makefile

## Purpose
`ci-build/Makefile` defines legacy CI preparation, test, and coverage targets for Linux/macOS environments.

## Important APIs, types, and functions
It defines `CI_BUILD_DIR` and targets for building `gflags`, building/installing `kcov`, preparing Linux/macOS dependencies, running tests, and collecting coverage. Targets use `LOCAL_DIR`, `TRAVIS_OS_NAME`, and `TRAVIS_JOB_ID`.

## Control flow
Dependency targets download archives into `/tmp`, build with CMake/make or Xcode on macOS, and install into `LOCAL_DIR`. `test_linux`/`test_osx` set `CI=true` and call `ci-build/test.sh`. Coverage targets parse `tests.out` for test binaries and run `kcov` with include/exclude/strip settings.

## State and persistence behavior
It writes downloaded/build artifacts under `/tmp`, installs into `LOCAL_DIR`, writes coverage data under `target/kcov`, and relies on `tests.out` from the test script.

## Dependencies and integration points
It depends on curl, tar, CMake, make, Xcode on macOS, Homebrew, kcov, gflags/snappy/gperftools, Travis-style environment variables, and TiKV test output conventions.

## Risks and edge cases
Downloaded dependencies are unauthenticated archives. Travis-specific variables suggest this may be historical. Coverage parsing from `tests.out` is brittle. The Makefile assumes `LOCAL_DIR` is defined by the caller.

## Test signals
Successful dependency preparation, `CI=true ci-build/test.sh`, and coverage upload/coverage directory generation validate these targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/ci-build/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/ci-build/test.sh -->
# sources/storage-engines/tikv/ci-build/test.sh

## Purpose
`ci-build/test.sh` is a CI test driver that enforces formatting, clippy, test execution, dirty-worktree checks, and panic extraction from logs.

## Important APIs, types, and functions
`panic()` prints an error and exits. The script sets `set -eo pipefail`, changes to the repository root, optionally runs `make format`, uses `git diff-index` to enforce formatting/test cleanliness, traps exit to kill background jobs, sets `RUST_TEST_THREADS` on Travis, and forces `RUSTFLAGS=-Dwarnings`.

## Control flow
After format validation, it runs `make clippy`. It then either runs `make test 2>&1 | tee tests.out` or, with `SKIP_TESTS`, runs `EXTRA_CARGO_ARGS=--no-run make test`. It parses `tests.out` with Python for panic thread names, greps `tests.log` for corresponding cases, and marks status failed if thread panics are found. It cleans logs and exits with accumulated status.

## State and persistence behavior
It writes `tests.out` and `tests.log`, removes `tests.log`, and removes `tests.out` outside Travis. It can leave formatted files changed if `make format` modifies the tree before dirty check.

## Dependencies and integration points
It depends on Bash, make targets, git, Python, and TiKV logging conventions. Environment flags (`SKIP_FORMAT_CHECK`, `SKIP_TESTS`, `SKIP_CHECK_DIRTY_TESTS`, `TRAVIS`) modify behavior.

## Risks and edge cases
The trap kills all background jobs from the shell. Panic-case parsing assumes a specific Rust panic line format and log file field layout. `RUSTFLAGS=-Dwarnings` can fail builds on newly introduced warnings, which is intended but environment-sensitive.

## Test signals
Clean `make format`, `make clippy`, and `make test` runs; dirty-tree detection after formatting/tests; panic extraction from synthetic `tests.out`/`tests.log`; and skip-mode behavior are key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/ci-build/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/clippy.toml -->
# sources/storage-engines/tikv/clippy.toml

## Purpose
`clippy.toml` configures TiKV-specific Clippy policy, primarily banning unsafe or project-incompatible APIs.

## Important APIs, types, and functions
It sets `avoid-breaking-exported-api = false`. `[[disallowed-methods]]` bans direct thread/runtime hook APIs that bypass TiKV system hooks, unsound `time` functions, and OpenSSL APIs affected by RUSTSEC advisories. `[[disallowed-types]]` bans OpenSSL types that may reach unsound `MemBio` behavior or use-after-free paths. `[[await-holding-invalid-types]]` flags holding `dashmap::mapref::one::Ref` across `.await`.

## Control flow
Clippy reads this declarative configuration during lint runs. The Makefile's `clippy` target is the main integration path.

## State and persistence behavior
No state is written. It affects compile-time lint failures and developer workflow.

## Dependencies and integration points
It depends on Clippy support for configured lints and integrates with TiKV utility wrapper APIs, security advisory policy, and the `scripts/clippy-all` pipeline.

## Risks and edge cases
Advisory comments must stay current with dependency versions. Banning types/methods may require explicit exceptions or wrapper APIs for legitimate low-level code. The referenced reason for `openssl::x509::store::X509StoreRef::objects` mentions an older RUSTSEC ID in text while the section header cites 2023-0072, so documentation consistency should be checked.

## Test signals
`make clippy` should fail on direct use of banned methods/types and pass when wrapper APIs are used. Async tests should catch holding DashMap refs across await.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/clippy.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/build.rs -->
# sources/storage-engines/tikv/cmd/build.rs

## Purpose
`cmd/build.rs` is a shared build script for TiKV command binaries. It embeds build time and tries to statically link the C++ standard library for GNU/Clang-like toolchains.

## Important APIs, types, and functions
`main()` prints `cargo:rustc-env=TIKV_BUILD_TIME=<UTC time>`, gets the C compiler from `cc::Build`, and calls `link_cpp()`. `link_cpp()` selects `libstdc++.a` for GNU-like tools, `libc++.a` for Clang-like tools, and skips Windows/unknown tools. `link_sys_lib()` asks the compiler for `--print-file-name <lib>`, validates an absolute path, then emits `cargo:rustc-link-lib=static:-bundle,+whole-archive=<name>` and `cargo:rustc-link-search`.

## Control flow
Cargo runs the build script before compiling the command crate. The script's printed lines become Cargo build instructions and environment variables for Rust code.

## State and persistence behavior
It does not write files, but it injects `TIKV_BUILD_TIME` into compiled binaries and changes linker behavior.

## Dependencies and integration points
It depends on the `cc` crate, workspace `time` crate, the host compiler, and Cargo build-script protocol. `cmd/tikv-ctl/build.rs` includes this file directly.

## Risks and edge cases
`output().unwrap()` can panic if invoking the compiler fails. Static C++ linking is skipped if the path is non-absolute or lookup fails. Link modifiers are specialized to avoid rlib bundle/whole-archive conflicts and may need updates for new Rust/Cargo linker behavior.

## Test signals
Build logs should show `TIKV_BUILD_TIME`, static C++ link directives on GNU/Clang, no C++ static link on Windows, and successful command binary linking.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/Cargo.toml -->
# sources/storage-engines/tikv/cmd/tikv-ctl/Cargo.toml

## Purpose
This manifest defines the `tikv-ctl` command crate, its feature forwarding, operational dependencies, and shared build script dependencies.

## Important APIs, types, and functions
The package is `tikv-ctl` version `0.0.1`, edition 2024, unpublished. Features forward allocator, RocksDB portability/SSE, memory profiling, failpoints, vendored OpenSSL, and test engine choices to the root `tikv` crate or engine crates. `nortcheck` forwards to `engine_rocks/nortcheck`.

Dependencies include clap/structopt for CLI parsing, TiKV engine/storage/security/PD/raft crates, `raft-engine-ctl`, `compact-log-backup`, protobuf, grpcio, logging, base64/hex/regex/toml/tempfile, and tokio. Build dependencies are `cc` and workspace `time`.

## Control flow
Cargo uses this manifest to compile `tikv-ctl`. Feature selections from the root Makefile or Cargo invocation propagate into this crate and its dependencies. The build script includes shared command build logic.

## State and persistence behavior
No runtime state is defined here, but dependencies enable `tikv-ctl` to inspect and mutate local/remote TiKV state, RocksDB data, raft logs, encryption metadata, and backup logs.

## Dependencies and integration points
It is a default workspace member and release binary target. It integrates with TiKV's root package, workspace dependencies, Makefile `ctl`/release targets, and operational components for recovery, compaction, metrics, encryption, and raft-engine control.

## Risks and edge cases
Edition 2024 can impose newer compiler requirements than the root edition 2021. Feature forwarding must stay aligned with root features. Because the binary exposes destructive recovery/compaction operations, dependency version and feature drift can affect operational safety.

## Test signals
`cargo build -p tikv-ctl`, `make ctl`, feature-specific builds, CLI help generation, and command parser tests from `cmd.rs` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/build.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/build.rs

## Purpose
`cmd/tikv-ctl/build.rs` reuses the shared command build script for the `tikv-ctl` crate.

## Important APIs, types, and functions
It contains only `include!("../build.rs");`, so all behavior comes from `cmd/build.rs`: build time embedding and optional static C++ standard library link directives.

## Control flow
Cargo executes this build script for `tikv-ctl`; macro inclusion expands the parent build script at compile time.

## State and persistence behavior
It writes no files directly but causes `TIKV_BUILD_TIME` and linker instructions to be emitted by the included script.

## Dependencies and integration points
It depends on the parent `cmd/build.rs` remaining path-stable and on the `cc`/`time` build dependencies declared in `tikv-ctl/Cargo.toml`.

## Risks and edge cases
Relative include paths are fragile if the command directory layout changes. Debugging points to included code rather than local code.

## Test signals
`cargo build -p tikv-ctl` should execute the included script and show the same build-script behavior as other command crates using `cmd/build.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/cmd.rs -->
# sources/storage-engines/tikv/cmd/tikv-ctl/src/cmd.rs

## Purpose
`cmd.rs` defines the complete `tikv-ctl` command-line schema using `StructOpt`. It maps global options and subcommands for inspecting, repairing, compacting, recovering, encrypting, and operating TiKV data and clusters.

## Important APIs, types, and functions
`Opt` holds global flags: PD address, log level/format, remote host, TLS paths, config/data-dir, RocksDB paranoid-check skip, deprecated `db`/`raftdb`, key conversion helpers (`--to-escaped`, `--to-hex`, `--decode`, `--encode`), and optional `Cmd`. `VERSION_INFO` lazily calls `tikv::tikv_version_info()` with `TIKV_BUILD_TIME`.

`Cmd` enumerates operational subcommands: raft log/region inspection, region size, MVCC/raw scans and prints, region diff, compaction, tombstone, MVCC recovery, unsafe recovery, recreate region, metrics, consistency check, bad region/SST inspection, config modification, snapshot metadata dump, cluster-wide compaction, region/range properties, split region, failpoint control, store/cluster IDs, file decryption, encryption metadata cleanup/dump, reset/flashback, raft-engine passthrough, readonly-remains reuse, compact-log-backup, and region read progress.

Nested enums are `RaftCmd`, `FailCmd`, `EncryptionMetaCmd`, and `UnsafeRecoverCmd`. The test module validates parser behavior for `compact-log-backup` flags such as default `gcp_v2_enable`, explicit false, `cal_shift_ts`, and omitting `--until` when a replication-status prefix is provided.

## Control flow
There is no executor logic here; control flow is declarative parser construction. `StructOpt` derives generate clap parsing with conflicts, required-unless rules, defaults, aliases, value delimiters, possible values, and external subcommand capture. Later executor modules match on `Opt.cmd` and run the actual operations.

## State and persistence behavior
This file does not persist state directly, but many parsed commands authorize state-changing operations: writing RocksDB pages/metadata, tombstoning regions, removing failed stores, dropping unapplied raft logs, compaction, config modification, decryption output, encryption metadata cleanup, reset/flashback, and backup-log compaction. Parser constraints are therefore an important safety boundary.

## Dependencies and integration points
It depends on `clap`, `structopt`, `compact_log_backup::ShardConfig`, `engine_traits` constants/types, `raft_engine::ReadableSize`, and `tikv` version reporting. It integrates with the rest of `tikv-ctl` by providing the typed command contract consumed by executor code and tests.

## Risks and edge cases
Parser-level safety is only as strong as declared conflicts and requirements. Several destructive commands include `all-regions`, `force`, or recovery semantics; accidental defaults or missing confirmations can be dangerous downstream. `External(Vec<String>)` captures unknown subcommands and may defer errors. Some deprecated fields remain with validators that always error, preserving visible compatibility while blocking use. Value delimiters and `possible_values` protect some fields but not all path/key inputs.

## Test signals
Existing tests cover a subset of `compact-log-backup`. Additional useful tests include command conflict rules, deprecated flag errors, required-unless behavior for unsafe recovery/recover MVCC/diff, value delimiter parsing, `possible_values` rejection, key conversion flag conflicts, external subcommand handling, and help/version output.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/cmd/tikv-ctl/src/cmd.rs -->
