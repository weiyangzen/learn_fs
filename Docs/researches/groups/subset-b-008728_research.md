# subset-b-008728 Research

Grouped research for the listed RocksDB and SQLite build/test files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc -->
# sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc

## Purpose
This is RocksDB's broad regression suite for `WriteBatchWithIndex`, its indexed write-batch iterators, point lookups, merge handling, timestamped column-family behavior, wide-column/entity reads, and the `WBWIMemTable` adapter. It validates both overwrite-key and keep-all-updates modes via the parameterized `WriteBatchWithIndexTest`, plus overwrite-specific mutation tests and separate memtable tests.

## Important APIs, Types, And Functions
Key local helpers are `ColumnFamilyHandleImplDummy`, `Entry`, `TestHandler`, and `KVIter`. `ColumnFamilyHandleImplDummy` supplies column-family IDs and comparators without a real DB column family. `TestHandler` replays the underlying `WriteBatch` and counts per-key updates. `KVIter` is a map-backed `Iterator` with optional `allow_unprepared_value` and forced `PrepareValue()` corruption paths, used to model base iterators.

The tests exercise `WriteBatchWithIndex` APIs including `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `SetSavePoint`, `RollbackToSavePoint`, `Clear`, `NewIterator`, `NewIteratorWithBase`, `GetFromBatch`, `GetFromBatchAndDB`, `GetEntityFromBatch`, `GetEntityFromBatchAndDB`, `MultiGetFromBatchAndDB`, `MultiGetEntityFromBatchAndDB`, `GetCFStats`, and access to the underlying `WriteBatch`. Internal-facing coverage reaches `WBWIIteratorImpl::NextKey`, `PrevKey`, `FindLatestUpdate`, `GetUpdateCount`, and `WBWIMemTable::{Get,MultiGet,NewIterator,AssignSequenceNumbers}`.

## Control Flow
`WBWIBaseTest` creates a temporary per-thread DB path, installs the string-append merge operator, and constructs `batch_` with the parameterized overwrite setting. Its destructor checks that WBWI operation count matches the write-batch count and destroys any opened DB. Many tests build an expected `KVMap` or vector of expected internal keys, then compare iterator walks, seeks, reverse seeks, and point lookups against that expected state.

Early tests cover secondary-index ordering, column-family-specific comparators, duplicate-key overwrite behavior, `WBWIIteratorImpl` key-level navigation, and random base/delta iterator interleavings. Mid-file tests cover `GetFromBatch*`, merge resolution with and without DB state, snapshots, pinned results, mutation while iterating, `ReadOptions` bounds, savepoints, single-delete semantics, and `MultiGet`. Later tests cover merge edge cases, bad merge operators, timestamp update/index behavior, wide-column `PutEntity` and entity read APIs, invalid-argument sanity checks, and column-family statistics. The final `WBWIMemTableTest` section treats a `WriteBatchWithIndex` as a memtable, assigning sequence number ranges and verifying point reads, `MultiGet`, internal iterators, overwritten single-delete emission, and merge operand propagation.

## State And Persistence Behavior
Most state is in-memory in `WriteBatchWithIndex`, its skip-list/index, the underlying `WriteBatch`, local maps, merge contexts, iterator objects, and `WBWIMemTable`. Several tests open an actual temporary RocksDB instance at `test::PerThreadDBPath("write_batch_with_index_test")`, write/flush data, use snapshots, and then clean up the DB in the fixture destructor. Savepoint tests verify that rollback restores indexed state as well as batch state. Memtable tests assign synthetic sequence ranges and inspect internal keys to ensure updates, deletions, overwritten single deletes, and merges get correct visibility and ordering.

## Dependencies And Integration Points
The file depends on RocksDB test infrastructure (`db_test_util`, `testharness`, `testutil`, `SyncPoint`, stack traces), core DB APIs, column-family internals, `WBWIMemTable`, merge operators, wide-column support, timestamp comparators, internal keys, arenas, and `MultiGetContext`. It integrates directly with the public `WriteBatchWithIndex` API and with internal implementation details from `write_batch_with_index_internal.h`, making it a compatibility guard for both user-visible behavior and internal iterator/memtable contracts.

## Risks
The suite is intentionally high-blast-radius: small ordering changes in `WriteBatchWithIndex`, comparator handling, merge operand order, savepoint restoration, timestamp stripping, or base/delta iterator bounds can break many assertions. Tests that mutate a batch while iterating validate single-thread behavior but should not be read as a thread-safety guarantee. The memtable tests rely on detailed sequence-number assignment conventions; implementation changes there require carefully updating expected internal keys. Randomized loops use fixed seeds, giving reproducible coverage but not exhaustive fuzzing.

## Test Signals
The file itself is a test binary: `main()` installs the RocksDB stack trace handler, initializes GoogleTest, and runs all tests. Strong signals include parameterized execution for overwrite modes, deterministic random seeds, explicit status checks, DB-backed merge/snapshot/flush scenarios, SyncPoint corruption injection for blob-backed `PrepareValue`, million-iteration mutation stress, and direct validation of `WBWIMemTable` `Get`, `MultiGet`, and iterator results.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/Makefile.in -->
# sources/storage-engines/sqlite/Makefile.in

## Purpose
This is the autosetup-generated Makefile template for SQLite's canonical source tree. It defines configure-substituted toolchain variables, installation directories, feature flags, Tcl integration, reconfiguration rules, ancillary targets, and then delegates most build recipes to `$(TOP)/main.mk`.

## Important APIs, Types, And Functions
The public interface is POSIX make variables and targets. Key variables include `TOP`, autotools-style directories (`prefix`, `datadir`, `mandir`, `includedir`, `exec_prefix`, `bindir`, `libdir`), toolchain variables (`CC`, `B.cc`, `T.cc`, `AR`, `INSTALL`), feature/link flags (`CFLAGS`, `CFLAGS.core`, `OPT_FEATURE_FLAGS`, `LDFLAGS.*`), shared/static library controls, Tcl controls (`HAVE_TCL`, `TCLSH_CMD`, `TCL_CONFIG_SH`, `TCLLIBDIR`, `TCL_EXT_DLL_BASENAME`), autosetup controls (`AS_AUTO_DEF`, `AS_AUTORECONFIG`), and build-mode toggles such as `USE_AMALGAMATION`, `LINK_TOOLS_DYNAMICALLY`, `STATIC_TCLSQLITE3`, and `STATIC_CLI_SHELL`.

## Control Flow
`all:` is initialized early and later extended by included rules. `config`/`reconfigure`, `Makefile`, `sqlite3.pc`, and `sqlite_cfg.h` all rerun the original configure command through `$(AS_AUTORECONFIG)` and touch generated outputs. The `fiddle` target requires `EMCC_WRAPPER`, then delegates to `ext/wasm` with GNU make. `misspell` builds `custom.rws` with aspell and runs `tool/spellsift.tcl`. `distclean-autosetup` removes autosetup-specific generated files before `distclean`. `version-info$(T.exe)` links `tool/version-info.c`. The final `include $(TOP)/main.mk` supplies the main SQLite build/install/test rules.

## State And Persistence Behavior
This template is transformed by configure into a concrete `Makefile`. Generated or persistent artifacts controlled here include `Makefile`, `sqlite3.pc`, `sqlite_cfg.h`, `config.log`, `config.status`, `config.defines.*`, `jimsh0*`, `libsqlite3*$(T.dll)`, `tool/emcc.sh`, `custom.rws`, and `version-info$(T.exe)`. The file distinguishes build-machine outputs (`B.*`) from target outputs (`T.*`) for cross-compilation.

## Dependencies And Integration Points
It depends on SQLite autosetup substitutions, `auto.def`, `main.mk`, Tcl configuration, platform linker flags, optional Emscripten, aspell, and the repository's build tools. It is the bridge between configure-time detection and the canonical SQLite make rules, preserving autotools-compatible install variables while using autosetup instead of GNU Autotools.

## Risks
The file is intentionally POSIX-make-oriented; adding GNU make-only syntax would break supported environments. Passing `CFLAGS` at make time can override configure-expanded values, so the template uses indirection and documents legacy `CPPFLAGS` behavior. Directory variable remapping, Tcl library installation paths, OS-specific shared-library flags, and reconfiguration dependencies are sensitive integration points.

## Test Signals
Useful validation signals are successful `./configure && make`, regeneration through `make reconfigure`, presence of generated `sqlite3.pc` and `sqlite_cfg.h`, `make fiddle` failure/success depending on `EMCC_WRAPPER`, `make misspell` when Tcl and aspell are present, and `make distclean` removing autosetup products without disturbing source files.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/Makefile.in -->
# sources/storage-engines/sqlite/autoconf/Makefile.in

## Purpose
This is the trimmed Makefile template for SQLite's autoconf/amalgamation bundle. Unlike the canonical template, it contains direct rules for building and installing the amalgamated `sqlite3` shell, shared library, static library, headers, pkg-config file, man page, and distribution archive.

## Important APIs, Types, And Functions
Important make variables include `TOP`, `PACKAGE_VERSION`, `B.*`/`T.*` filename extensions, install directories, `INSTALL`, `AR`, `CC`, `ENABLE_LIB_SHARED`, `ENABLE_LIB_STATIC`, `HAVE_WASI_SDK`, `CFLAGS`, `LDFLAGS.*`, `OPT_FEATURE_FLAGS`, `libsqlite3.*`, `ENABLE_STATIC_SHELL`, and `STATIC_CLI_SHELL`. Key targets include `sqlite3.o`, `$(libsqlite3.DLL)`, `$(libsqlite3.LIB)`, `sqlite3$(T.exe)`, `install-dll-*`, `install-lib`, `install-shell`, `install-headers`, `install-pc`, `install-man1`, `clean`, `distclean`, and `dist`.

## Control Flow
Configure substitutes platform and feature values into this template. `sqlite3.o` compiles `$(TOP)/sqlite3.c`. Shared-library and static-library targets are gated into `all` via suffix targets keyed by `ENABLE_LIB_SHARED` and `ENABLE_LIB_STATIC`. The shell link path switches between directly linking `sqlite3.c` and linking against the produced shared library using `ENABLE_STATIC_SHELL`; fully static shell flags are controlled by `STATIC_CLI_SHELL`. Install targets create destination directories, install artifacts, and platform-specific DLL rules create Unix, Darwin, MSYS, MinGW, or Cygwin layouts. `dist` copies `DIST_FILES` into `sqlite-$(PACKAGE_VERSION)` and creates a `.tar.gz`.

## State And Persistence Behavior
Build artifacts include `sqlite3.o`, `libsqlite3$(T.dll)` variants, `libsqlite3$(T.lib)`, optional import libraries, `sqlite3$(T.exe)`, `sqlite3.pc`, `sqlite_cfg.h`, `Makefile`, `config.*`, and `jimsh0$(T.exe)`. Install rules write into `$(DESTDIR)`-prefixed bin/lib/include/pkgconfig/man directories and may replace or create shared-library symlinks such as `.0`, `.$(PACKAGE_VERSION)`, and optional legacy `.0.8.6` links.

## Dependencies And Integration Points
The file integrates the autoconf bundle with autosetup reconfiguration (`AS_AUTORECONFIG`), SQLite amalgamation files (`sqlite3.c`, `sqlite3.h`, `sqlite3ext.h`, `shell.c`), pkg-config, man-page installation, platform linkers, and OS-specific shared-library naming. It carries compatibility behavior for libtool-era SQLite shared-object names and Windows-style import libraries.

## Risks
Shared-library install rules are platform-sensitive and can delete/relink legacy symlinks. Link flag ordering is explicitly important on some platforms. The shell gating through `HAVE_WASI_SDK` is non-obvious: the target suffix rules decide whether the shell is built/installed. The bundle is trimmed from canonical `main.mk`, so changes must stay synchronized with canonical install and link behavior.

## Test Signals
Primary signals are successful configure, `make all` under shared/static combinations, correct `sqlite3` shell linkage, `make install DESTDIR=...` producing the expected platform layout, `pkg-config` file installation, clean/distclean removal of generated artifacts, and `make dist` producing `sqlite-$(PACKAGE_VERSION).tar.gz`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/Makefile.in -->
# sources/storage-engines/sqlite/autoconf/tea/Makefile.in

## Purpose
This is the `teaish` POSIX make template used to build, test, install, uninstall, and package Tcl extensions configured by SQLite's autosetup-based TEA-like framework. A filtered copy is generated per extension with `@TEAISH_*@` substitutions and optional `@if ...@` blocks.

## Important APIs, Types, And Functions
The public make API is the `tx.*` extension variable family and selected Tcl/autotools variables. `tx.name`, `tx.version`, `tx.name.pkg`, `tx.libdir`, `tx.loadPrefix`, `tx.dll8`, `tx.dll9`, `tx.dll`, `tx.dir`, optional `tx.tm`, `tx.src`, `tx.CFLAGS`, `tx.CPPFLAGS`, `tx.LDFLAGS`, `tx.dist.files`, and `tx.dist.basename` describe the extension. `teaish.*` and `teaish__*` variables describe framework internals and autogeneration dependencies. Compiler macros include `CC.tcl` and `CC.dll`. Major target families are build (`all`, `$(tx.dll)`), reconfigure (`config.log`, `reconfigure`), test (`test-prepre`, `test-core`, `test-gdb`, `test-vg`, `test`), cleanup, install, uninstall, and distribution (`dist.zip`, `dist.tgz`, `undist`).

## Control Flow
Autogenerated dependencies funnel through `config.log` to avoid parallel reconfigure races. If DLL support is enabled, `$(tx.dll)` depends on `$(tx.src)` and `config.log`, validates that `tx.src` is non-empty, then links with Tcl stub flags. Test flow builds the DLL when needed, constructs `test-core.args` as tester script, DLL path/load prefix, and test utility script, then invokes `$(TCLSH)`. Install flow creates `$(DESTDIR)$(TCLLIBDIR)`, installs DLL, `pkgIndex.tcl`, package init scripts, optional Tcl module files, and runs a post-install `package require` smoke test. Dist flow uses temporary directories and tar/zip commands, optionally reconfiguring a full teaish installation into the archive.

## State And Persistence Behavior
Generated state includes the extension shared library, `tclsh` wrapper, `Makefile`, `config.log`, `config.defines.txt`, generated tester/pkgIndex/pkgInit/test/tm files, distribution archives, and temporary `teaish__dist_*` directories. Install and uninstall operate under `DESTDIR`, `TCLLIBDIR`, and optional Tcl module install directories.

## Dependencies And Integration Points
The template depends on autosetup/teaish filtering, Tcl's `tclConfig.sh`, `TCLSH`, Tcl stub libraries, platform shared-library flags, extension-provided `teaish.tcl` and optional `teaish.make`, generated `pkgIndex.tcl`, test utility scripts, `gdb`, `valgrind`, `tar`, and `zip`. It exposes extension hooks through reserved targets like `test-extension`, `install-extension`, `clean-extension`, and `distclean-extension`, plus injected `TEAISH_MAKEFILE_CODE` and included extension makefiles.

## Risks
The file must remain POSIX make-compatible, so conditional inclusion and distclean shortcuts are constrained. Parallel reconfiguration is explicitly guarded through `config.log`; adding additional autoreconfigure paths can reintroduce races. Install rules recursively remove `$(DESTDIR)$(TCLLIBDIR)` for DLL uninstall, so incorrect substitution can remove too much. The dist tarball recipe contains a suspicious `--t-e-d=$(teaish__dist.tmp.zip)` reference inside the tgz branch, making archive reconfiguration paths a point to inspect when modifying distribution behavior.

## Test Signals
Signals include successful extension DLL build, `make test`, `make test-gdb`/`test-vg` invocation shape, post-install `package require $(tx.name.pkg) $(tx.version)`, correct `pkgIndex.tcl` and optional `.tm` placement, `make uninstall` removing installed files, and zip/tgz archive generation when tar/zip support is configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in -->
# sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in

## Purpose
This is the template for the Tcl wrapper script invoked by teaish's `make test` recipe. It loads the extension DLL when one exists, sources teaish test utilities, optional package initialization/module scripts, and then runs extension test scripts or a default load-only smoke test.

## Important APIs, Types, And Functions
The script consumes three argv values: DLL name, Tcl `load` prefix, and path to `teaish/tester.tcl`. Conditional substitutions inject `TEAISH_VSATISFIES_CODE`, `TEAISH_PKGINIT_TCL`, `TEAISH_TM_TCL`, `TEAISH_TEST_TCL`, `TEAISH__DEFINES_MAP`, `TEAISH_NAME`, `TEAISH_VERSION`, and `TEAISH_TESTER_TCL`. It uses Tcl built-ins `llength`, `lindex`, `load`, `file normalize`, `lassign`, `source -encoding utf-8`, `apply`, `join`, and `array set`.

## Control Flow
The script optionally evaluates version-satisfaction code, loads the extension from a normalized path when argv0 is non-empty, removes the DLL and load-prefix args from `::argv`, sources the tester utility script, sources generated package init and Tcl module scripts if configured, and then sources each extension test file. Before each test script it populates `::teaish__BuildFlags` so test utilities can query build flags. If no test scripts are configured, it prints a default successful-load message.

## State And Persistence Behavior
It does not persist files. Runtime state changes are the loaded Tcl extension, rewritten `::argv`, local `dir` variables for sourced scripts, and global `::teaish__BuildFlags`. It deliberately normalizes the DLL path for platforms such as Haiku where a bare filename may not load.

## Dependencies And Integration Points
The file is generated and invoked from teaish `Makefile.in` test targets. It depends on Tcl, the built extension DLL when enabled, generated tester/test/pkginit/tm files, and teaish's tester utility API. Extension test files can rely on the loaded package and build flag array.

## Risks
Argument ordering must remain synchronized with `Makefile.in`'s `test-core.args`; otherwise the wrong script could be sourced or the wrong DLL loaded. Since sourced scripts run in the test process, bad generated paths or malicious test content execute directly. The load-prefix and Tcl version-satisfaction substitutions must match generated package metadata.

## Test Signals
The direct signal is `make test` under teaish. A successful no-test extension prints the default load message. Configured tests should observe a loaded extension, valid `::argv` after stripping teaish's internal args, and populated `::teaish__BuildFlags`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/_teaish.tester.tcl.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/configure -->
# sources/storage-engines/sqlite/autoconf/tea/configure

## Purpose
This shell wrapper locates the appropriate autosetup directory for a teaish extension and execs autosetup through a discovered Tcl/Jim interpreter. It lets extension-local `configure` work whether teaish is in a local copy, SQLite autoconf bundle, or canonical SQLite source tree.

## Important APIs, Types, And Functions
The script is pure POSIX shell. It uses `dirname "$0"` to derive `dir0`, probes `$dirA/autosetup`, `$dirA/../autosetup`, and `$dirA/../../autosetup`, exports `WRAPPER="$0"`, invokes `"$dirA/autosetup-find-tclsh"` in command substitution, and execs `"$dirA/autosetup"` with `--teaish-extension-dir="$dir0"` plus all user arguments.

## Control Flow
The wrapper starts with the extension directory, checks the three supported autosetup locations in order, and exits with an error if none exists. On success it transfers control with `exec` to the interpreter returned by `autosetup-find-tclsh`, passing autosetup itself and extension-dir metadata.

## State And Persistence Behavior
The only state is environment variable `WRAPPER`, which autosetup uses to identify invocation through a configure wrapper and locate `auto.def`. No files are created by this wrapper directly.

## Dependencies And Integration Points
It depends on the autosetup launcher, `autosetup-find-tclsh`, a usable `tclsh`/`jimsh` or bootstrap path, and the teaish autosetup modules. It integrates extension configuration with SQLite's bundled autosetup layouts.

## Risks
The directory tests are unquoted (`[ -d $dirA/... ]`), so paths with spaces can break. Failure to find autosetup yields an immediate error. Because it uses `exec`, any interpreter lookup failure or autosetup error becomes the configure result.

## Test Signals
Useful checks are running this `configure` from each supported tree layout, verifying that `WRAPPER`-based source directory detection works, and confirming `--teaish-extension-dir` reaches autosetup-generated teaish configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in -->
# sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in

## Purpose
This is the Tcl package index template generated for teaish-built extensions. It registers `package ifneeded` scripts that load the correct Tcl 8 or Tcl 9 extension library and optionally source package initialization code.

## Important APIs, Types, And Functions
The template uses Tcl package APIs: `package vsatisfies`, `package provide Tcl`, and `package ifneeded`. Generated values include `TEAISH_PKGNAME`, `TEAISH_VERSION`, `TEAISH_DLL9`, `TEAISH_DLL8`, `TEAISH_LOAD_PREFIX`, `TEAISH_PKGINIT_TCL_TAIL`, `TEAISH_ENABLE_DLL`, and optional `TEAISH_VSATISFIES_CODE`. Runtime code uses `apply`, `file join`, `file extension`, `string tolower`, `load`, `file exists`, and `source -encoding utf-8`.

## Control Flow
The index first runs optional version-satisfaction code, then branches on whether the running Tcl version satisfies `9.0-`. The Tcl 9 branch loads the Tcl 9 DLL name when DLL support is enabled and sources optional init script. The Tcl 8 branch loads the Tcl 8 DLL when its extension looks like a native shared library; otherwise it calls `load {}` with the load prefix, supporting statically linked or non-library cases. Both branches register deferred code with `package ifneeded` rather than loading immediately.

## State And Persistence Behavior
This file is installed as package metadata under `TCLLIBDIR`. Runtime state is Tcl's package registry entry and, when requested, the loaded native extension and sourced init script. It does not mutate persistent files after installation.

## Dependencies And Integration Points
It is produced by teaish configuration and installed by teaish `Makefile.in`. Tcl's package loader discovers it through `auto_path`. It must match generated DLL names, package names, versions, and init-script tails.

## Risks
Incorrect Tcl major-version detection or DLL substitution will make `package require` fail. The Tcl 8 fallback `load {}` behavior is subtle and depends on load-prefix semantics for statically linked extensions. Optional init script sourcing is conditional on file existence, so missing init files can fail silently when they are expected to provide commands.

## Test Signals
The strongest signal is a clean `package require @TEAISH_PKGNAME@ @TEAISH_VERSION@` under Tcl 8 and Tcl 9 layouts, including installed-tree tests from `make install-test`. Inspecting `auto_path` discovery and load errors helps diagnose bad substitution.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autoconf/tea/pkgIndex.tcl.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup -->
# sources/storage-engines/sqlite/autosetup/autosetup

## Purpose
This is SQLite's bundled standalone autosetup Tcl script. It is both the autosetup driver and a self-contained module bundle that parses configure options, loads `auto.def`, manages definitions/substitutions, reports help/reference text, installs local/system autosetup copies, and provides portability helpers for Tcl and Jim Tcl.

## Important APIs, Types, And Functions
The top-level `main` proc determines autosetup directories, source directory, build directory, wrapper invocation, option state, dependencies, and command-line definitions. Core option APIs are `options-add`, `options`, `options-defaults`, `opt-bool`, `opt-val`, `opt-str`, and `option-check-names`. Definition APIs are `define`, `undefine`, `define-push`, `define-append`, `define-append-argv`, `get-define`, `is-defined`, `is-define-set`, and `all-defines`. Environment/path/logging APIs include `get-env`, `env-is-set`, `readfile`, `writefile`, `quote-if-needed`, `quote-argv`, `find-executable*`, `configlog`, `msg-checking`, `msg-result`, `msg-quiet`, `user-error`, `autosetup-error`, `relative-path`, `autosetup_add_dep`, `use`, and `autosetup_load_module`.

Embedded modules include formatting backends (`asciidoc-formatting`, `markdown-formatting`, `text-formatting`, `wiki-formatting`, and shared `formatting`), `getopt`, `help`, `init`, `install`, `misc`, and `util`. The install module exposes `autosetup_install`, `autosetup_create_configure`, `autosetup_install_file`, and `autosetup_install_readme`. Utility functions include `compare-versions`, `suffix`, `prefix`, and `lpop`.

## Control Flow
The shell/Tcl polyglot header uses `autosetup-find-tclsh` to exec a working interpreter. `main` initializes `autosetup(libdir)` enough to load `misc`, normalizes script paths, decides whether it was invoked directly or via a `configure` wrapper, initializes option/default/help dictionaries, loads `util` and `getopt`, registers core options, processes early exits (`--version`, `--help`, `--license`, `--reference`, `--install`, `--init`, `--sysinstall`), validates `auto.def`, converts trailing `NAME=VALUE` arguments to definitions, logs invocation details, loads local and auto modules, then sources `auto.def` as a module.

Option declaration is two-phase: `getopt` first captures syntactic options without knowing their validity, then `options-add` registers declared options and maps user-provided values into `autosetup(optset)`. When `auto.def` calls `options`, unknown options are rejected if `option-checking` is enabled. Module loading checks embedded `modsource(...)` first, then external module files under the installed libdir and project `autosetup` directory. The final entrypoint catches errors and formats them through `error-dump` unless debug mode is enabled.

## State And Persistence Behavior
Runtime state is stored in global `autosetup(...)`, `define(...)`, `libmodule(...)`, and `modsource(...)` arrays/dicts. Persistent outputs include `config.log` via `configlog`, files written by configure modules through `writefile`, generated `configure` wrappers from install mode, installed autosetup support files, and project-local `autosetup/README.autosetup`. Dependency state is accumulated in `autosetup(deps)` for generated make/config files to know what should trigger reconfiguration.

## Dependencies And Integration Points
The script depends on a Tcl or Jim Tcl interpreter, the companion `autosetup-find-tclsh`, optional `jimsh0.c` bootstrap support, optional `autosetup-config.guess`/`autosetup-config.sub`, project `auto.def`, external autosetup modules, environment variables, and platform shell utilities such as `chmod`, `uname`, and install-time file operations. SQLite's `configure` wrappers export `WRAPPER`, which changes source-directory discovery. The command surface exposed by this script is what SQLite `auto.def` and teaish extension configs consume.

## Risks
Because it is a configure driver, errors in option parsing, wrapper path normalization, module lookup, or definition quoting can affect all generated build files. `define-append` is not safe for values containing spaces; callers must use `define-append-argv`. The script supports both Tcl and Jim Tcl, so portability helpers in `misc` are sensitive. Install mode can overwrite `configure` when `--force` is used. Error-location logic tries to suppress framework stack traces, which is good for users but can hide details unless `--autosetup-debug` is used.

## Test Signals
Strong signals are `autosetup --version`, `--help`, `--reference` in text/markdown/asciidoc/wiki modes, `--init`, local `--install`, `--sysinstall` from a development tree, successful configure wrapper invocation with `WRAPPER`, unknown-option rejection after `auto.def` declares options, correct `config.log` creation, and module loading from both embedded and project-local module paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup-find-tclsh -->
# sources/storage-engines/sqlite/autosetup/autosetup-find-tclsh

## Purpose
This shell helper locates a usable Tcl/Jim Tcl interpreter for autosetup, or bootstraps a local `jimsh0` from source when no installed interpreter passes the test script.

## Important APIs, Types, And Functions
The script uses POSIX shell, `dirname "$0"`, the optional environment variables `autosetup_tclsh`, `CC_FOR_BUILD`, and `CC`, candidate interpreters `./jimsh0`, `jimsh`, `tclsh`, `tclsh8.5`, `tclsh8.6`, and `tclsh8.7`, and the test script argument defaulting to `autosetup-test-tclsh`. It emits the selected interpreter name/path to stdout by exiting from the tested interpreter path behavior, or prints `false` after compiler failure.

## Control Flow
It derives the autosetup directory, loops through candidate interpreters, and runs each with the test script while suppressing output. The first interpreter that exits successfully causes the helper to exit success. If none works, it logs that it is building `jimsh0`, tries `${CC_FOR_BUILD:-cc}` and `gcc` to compile `jimsh0.c`, then runs the generated `./jimsh0` against the same test. If compilation also fails, it prints an error and outputs `false`.

## State And Persistence Behavior
The only persistent artifact it may create is `jimsh0` in the current working directory. It otherwise reads the autosetup test script and `jimsh0.c`, uses environment variables, and writes diagnostics to stderr.

## Dependencies And Integration Points
It is called by autosetup shell wrappers and configure scripts in command substitution to choose the interpreter for running `autosetup`. It depends on a working installed Tcl/Jim interpreter or a build compiler capable of compiling `jimsh0.c`.

## Risks
Candidate interpreter words are unquoted when executed, so unusual paths in `autosetup_tclsh` can fail. Bootstrapping writes `jimsh0` into the caller's current directory, which is intentional for configure flows but can surprise callers. If no compiler exists, it prints `false`; wrappers that exec that result will fail downstream rather than getting a structured shell error here.

## Test Signals
Signals include successful selection of an installed interpreter, honoring `autosetup_tclsh`, successful bootstrap build with `CC_FOR_BUILD`, and failure output when neither interpreter nor compiler is available. Running it with an alternate test-script argument verifies the optional argument path.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup-find-tclsh -->
