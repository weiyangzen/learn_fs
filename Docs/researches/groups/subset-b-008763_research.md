# subset-b-008763 research

Grouped research for selected SQLite build, pkg-config, multiprocess-test, and ALTER TABLE implementation files. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/main.mk -->
# sources/storage-engines/sqlite/main.mk

## Purpose

`main.mk` is SQLite's central POSIX-compatible makefile include. It is not a standalone configured makefile; it expects an outer makefile or configure-generated wrapper to provide host/target compiler variables, package version, Tcl settings, feature flags, installation prefixes, platform suffixes, and optional linkage choices. Its job is to build the generated SQLite artifacts (`sqlite3.c`, `sqlite3.h`, `shell.c`, parser/opcode tables, FTS5 amalgamation), static and shared libraries, the CLI shell, Tcl extension, test fixture, fuzzers, developer tools, release archives, install targets, and cleanup targets.

## Important APIs, Targets, and Variables

The file exposes configuration variables rather than C APIs. Important build inputs include `TOP`, `PACKAGE_VERSION`, `B.cc`, `T.cc`, `AR`, `B.exe`, `T.exe`, `T.dll`, `T.lib`, `HAVE_TCL`, `TCLSH_CMD`, `TCL_CONFIG_SH`, `ENABLE_LIB_SHARED`, `ENABLE_LIB_STATIC`, `USE_AMALGAMATION`, `LINK_TOOLS_DYNAMICALLY`, `AMALGAMATION_GEN_FLAGS`, `OPT_FEATURE_FLAGS`, `OPTS`, `SHELL_OPT`, and feature-scoped flag buckets such as `LDFLAGS.pthread`, `LDFLAGS.zlib`, `LDFLAGS.readline`, and `CFLAGS.icu`. The makefile deliberately separates common compiler flags, SQLite-library flags, extension flags, Tcl flags, and feature libraries so that different deliverables do not inherit inappropriate options.

Core targets include `all`, `lib`, `so`, `sqlite3.c`, `sqlite3.h`, `.target_source`, `sqlite3.o`, `$(libsqlite3.LIB)`, `$(libsqlite3.DLL)`, `sqlite3$(T.exe)`, `sqlite3d$(T.exe)`, `testfixture$(T.exe)`, `fuzzcheck$(T.exe)`, `sessionfuzz$(T.exe)`, `mptester$(T.exe)`, `sqlite3_analyzer$(T.exe)`, `sqldiff$(T.exe)`, `dbhash$(T.exe)`, `sqlite3_rsync$(T.exe)`, `tclsqlite3$(T.exe)`, `$(libtclsqlite3.DLL)`, `install`, `install-dll-*`, `install-lib`, `install-headers`, `install-pc`, `install-man1`, `devtest`, `releasetest`, `mptest`, `tidy`, `clean`, `distclean`, and `show-variables`.

## Control Flow and Build Graph

The file starts with defaulted variables and sanity checks, then defines source inventories (`LIBOBJS0`, `LIBOBJS1`, `SRC`, `TESTSRC`, `TESTSRC2`, extension headers, test programs, fuzz data). `LIBOBJ` switches between the full object list and the amalgamation object using `USE_AMALGAMATION`. `MAKE_SANITY_CHECK` validates essential variables and the top source directory before object builds.

Generated-code flow is: build `jimsh` or use `B.tclsh`, generate `sqlite3.h` with `mksqlite3h.tcl`, copy sources into `tsrc`, compress VDBE code, generate parser/opcode/pragma/keyword files using Lemon and Tcl/C tools, then run `mksqlite3c.tcl` to produce the amalgamation. FTS5 has its own Lemon grammar and `mkfts5c.tcl` amalgamation flow. The shell is assembled by `mkshellc.tcl` from `shell.c.in` and extension sources. Test fixture and tools either compile `sqlite3.c` directly or link against `libsqlite3` depending on target semantics and `LINK_TOOLS_DYNAMICALLY`.

The install graph is additive: `install` depends on enabled shared-library, static-library, header, Tcl, shell, manpage, and pkg-config install targets. Shared-library installation has platform-specific rules for Unix generic, Darwin, MSYS, MinGW, and Cygwin, including compatibility symlinks for historical `libsqlite3.so.0` and optional `libsqlite3.so.0.8.6`.

## State and Persistence Behavior

The makefile produces persistent build outputs in the build directory: generated C/header files, object files, static and shared libraries, test binaries, tool binaries, Tcl package files, zip/tar archives, and temporary source directories such as `tsrc`. It installs files under `DESTDIR` plus `bindir`, `libdir`, `includedir`, `mandir`, and `libdir/pkgconfig`. It also writes helper files such as `.main.mk.checks`, `.target_source`, `has_tclsh84`, `has_tclsh85`, `pkgIndex.tcl`, `.tclenv.sh`, and generated resource headers.

Cleanup state is separated by target. `tidy` removes build products but preserves configure outputs and test logs; `clean` additionally removes test directories/log artifacts; `distclean` delegates full cleanup expectations to `Makefile.in` while depending on `clean`. This split is important for out-of-tree builds and package builds that should not discard configure results unnecessarily.

## Dependencies and Integration Points

The file integrates with SQLite's source tree (`src`, `ext`, `tool`, `test`, `autosetup`) and with configure/autosetup wrappers. It depends on a POSIX shell, install-compatible `install`, C compiler(s), `ar`, Tcl or JimTcl for code generation, Lemon for parser generation, optional readline/linenoise, zlib, pthread, dlopen, math, ICU, Valgrind for selected tests, `nm`, `egrep`, `sed`, `strip`, and platform linkers. It also integrates with generated `sqlite3.pc` for pkg-config, Tcl's `tclConfig.sh`, source verification tools, release packaging scripts, and SQLite's `testrunner.tcl`.

Cross-build integration is explicit: `B.cc` builds host tools such as Lemon, `mkkeywordhash`, `mksourceid`, `src-verify`, and JimTcl, while `T.cc` builds target deliverables. `HAVE_WASI_SDK` disables shell build/install paths that do not apply to WASI. `LINK_TOOLS_DYNAMICALLY` changes whether tools embed or dynamically link SQLite.

## Risks and Edge Cases

The largest risk is portability. The file is intentionally POSIX make compatible and warns against GNU make-isms, so adding GNU-only syntax can break BSD make or downstream package builds. A second risk is flag scoping: applying `CFLAGS`, `LDFLAGS`, Tcl, readline, ICU, or sanitizer flags too broadly can break shared-library PIC requirements, cross-compilation, or tool linkage. Generated parser-related flags must be present when Lemon and keyword generation run, not just when compiling the final amalgamation.

Install risks include platform-specific shared-library naming, stale `libsqlite3.la`, historical symlink compatibility, unquoted spaces in install paths, and import-library handling on Unix-like Windows environments. Test and release targets have duplicated behavior in Tcl runner scripts, so updating make recipes without updating scheduler metadata can desynchronize CI behavior. `mptester`, fuzzers, and testfixture targets rely on static/internal SQLite symbols and specific compile-time options; changing `USE_AMALGAMATION` or symbol visibility can break them.

## Test Signals

Primary build signals are successful `all`, `lib`, `so`, `sqlite3$(T.exe)`, generated amalgamation, and install target completion. Source integrity signals include `srctree-check`, `sourcetest`, `verify-source`, and `checksymbols`. Runtime and regression signals include `devtest`, `mdevtest`, `sdevtest`, `releasetest`, `tcltest`, `testrunner`, `smoketest`, `fuzztest`, `valgrindfuzz`, `mptest`, and `threadtest`. Packaging signals are successful `amalgamation-tarball`, `snapshot-tarball`, `sqlite-src.zip`, `sqlite-amalgamation.zip`, `tool-zip`, and `snapshot-zip`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/main.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/mptest/mptest.c -->
# sources/storage-engines/sqlite/mptest/mptest.c

## Purpose

`mptest.c` is a standalone SQLite multiprocess test harness. It executes a custom script language against a shared SQLite database and starts child client processes so independent OS processes concurrently read and write the same database. The harness is designed to stress locking, busy handling, journal modes, WAL behavior, crash-like exits, and VFS behavior.

## Important APIs, Types, and Functions

The file uses the public SQLite C API: `sqlite3_open_v2`, `sqlite3_close`, `sqlite3_exec`, `sqlite3_prepare_v2`, `sqlite3_step`, `sqlite3_finalize`, `sqlite3_busy_handler`, `sqlite3_busy_timeout`, `sqlite3_create_function`, `sqlite3_enable_load_extension`, `sqlite3_trace`, `sqlite3_config(SQLITE_CONFIG_LOG)`, `sqlite3_file_control(SQLITE_FCNTL_VFSNAME)`, compile-option and source-id APIs, and SQLite allocation/formatting helpers.

Important local types and helpers include the global `g` struct for process-wide state, the dynamic `String` accumulator, `strglob()` for test-pattern matching, `printWithPrefix()`, `errorMessage()`, `fatalError()`, `logMessage()`, `busyHandler()`, `sqlTraceCallback()`, `sqlErrorCallback()`, `prepareSql()`, `runSql()`, `trySql()`, `evalSql()`, `evalFunc()`, `vfsNameFunc()`, `startScript()`, `finishScript()`, `startClient()`, `readFile()`, tokenizer helpers (`tokenLength`, `extractToken`, `findEnd`, `findEndif`), `waitForClient()`, `runScript()`, option parsing helpers, and `main()`.

## Control Flow

`main()` parses `DATABASE ?OPTIONS? ?SCRIPT?`, rejects script-looking database names, validates that the linked library and header source IDs match, opens logs, configures SQLite logging, and opens the database. The supervisor process deletes and recreates the test database, creates coordination tables (`task`, `counters`, `client`), reads the script, and runs it one or more times. Client processes are started with `--client N`, connect to the same database, claim tasks from `task`, execute their script fragments, and record completion.

Script execution alternates between raw SQL and meta-commands. SQL text accumulated before a command is evaluated and captured into `sResult` for assertions. Supported commands include sleeps, process exits, test-case markers, explicit finish, result reset/output, exact and glob assertions, nested script sourcing, printing, conditional blocks, client start/wait, task assignment, breakpoint, and SQL-error display toggling. Supervisor-only `--task` blocks insert work into the shared `task` table and ensure a client process exists. Clients claim work with `BEGIN IMMEDIATE`, update counters, honor `wantHalt`, mark task start/end timestamps, then loop.

## State and Persistence Behavior

The test database is both the subject under test and the scheduler. Persistent coordination tables store queued task text, client IDs, start/end times, halt requests, and aggregate error/test counters. The supervisor removes the database before starting, unless running as a client. Child startup uses shell backgrounding on Unix and `CreateProcessA` on Windows, so client lifetime is external to the supervisor process.

Global state controls tracing, SQL trace, error suppression, busy timeout, VFS name, database filename, log files, sync mode, task identity, and accumulated error/test counts. `fatalError()` attempts to update `client.wantHalt` before exit so other processes stop. `--exit N` can exit without `sqlite3_close()` when `N>0`, simulating a process crash after optional task-finish marking. Journal mode and synchronous mode are set by options, allowing the same script to test DELETE, WAL, PERSIST, TRUNCATE, and no-sync configurations.

## Dependencies and Integration Points

The harness depends on `sqlite3.h` and a SQLite object/library built with compatible `SQLITE_SOURCE_ID`. It uses standard C library headers plus POSIX `unistd.h` or Windows process APIs. The makefile builds it as `mptester$(T.exe)` and the `mptest` target runs bundled scripts such as `crash01.test` and `multiwrite01.test` under several journal modes. The script language exposes `vfsname()` and `eval()` SQL functions to tests, and integrates with SQLite's global error log callback.

## Risks and Edge Cases

Concurrency correctness is intentionally sensitive: scheduler tables are updated through a database that is also under locking stress, so busy-handler behavior and timeouts affect both test orchestration and test subject. The supervisor waits with fixed timeouts and reports errors if clients stall. `startClient()` builds command lines with quoted database and VFS names, but still uses `system()` on Unix, so unusual executable paths or shell metacharacters are a portability concern. The script tokenizer is custom and supports comments, strings, semicolon boundaries, nested `--if`, and `--task` blocks; malformed or unusual quoting can affect line accounting and command extraction.

Windows behavior differs for process spawning and for unsupported PERSIST/TRUNCATE journal-mode requests, which are coerced to DELETE. `readFile()` reads whole scripts into memory and assumes `ftell()`/`fread()` success. `tokenLength()` string handling and glob matching are test-language infrastructure, so bugs there can create false positives or false failures independent of SQLite itself.

## Test Signals

The harness reports `Summary: N errors out of M tests` and returns nonzero if errors were accumulated. Positive signals are successful exact `--match` and pattern `--glob` assertions, task completion timestamps, clients shutting down after `wantHalt`, and absence of timeouts or SQLite error-log events. The `main.mk` `mptest` target is the canonical integration signal because it repeats crash and multi-writer scripts under several journal modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/mptest/mptest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/sqlite.pc.in -->
# sources/storage-engines/sqlite/sqlite.pc.in

## Purpose

`sqlite.pc.in` is a pkg-config template for a library named `sqlite`. It describes include and linker flags for consumers that expect the legacy or alternate `-lsqlite` library name rather than SQLite 3's normal `-lsqlite3`.

## Important Fields and Substitutions

The template defines `prefix`, `exec_prefix`, `libdir`, and `includedir` using configure substitution variables. It publishes `Name: SQLite`, `Description: SQL database engine`, `Version: @RELEASE@`, `Libs: -L${libdir} -lsqlite`, `Libs.private: @LIBS@`, and `Cflags: -I${includedir}`.

## Control Flow and Generation

There is no runtime control flow. A configure or packaging step substitutes `@prefix@`, `@exec_prefix@`, `@libdir@`, `@includedir@`, `@RELEASE@`, and `@LIBS@` to produce an installable `.pc` file. pkg-config consumers then use the generated metadata to compile and link client programs.

## State and Persistence Behavior

The generated file is installed under a pkg-config directory, typically `${libdir}/pkgconfig`. It persists build-time installation paths and private linker dependencies. `Libs.private` is only used by pkg-config for static linking, so it can affect whether static consumers pull in math, pthread, zlib, dlopen, or other platform libraries.

## Dependencies and Integration Points

The template integrates with autotools-style substitution variables and downstream `pkg-config` tooling. It is separate from the `main.mk` `install-pc` target, which installs `sqlite3.pc`; this template may be used by another compatibility packaging path. The important downstream integration point is the library name: it advertises `-lsqlite`, so it is only correct for builds that actually produce or package that library name.

## Risks and Test Signals

The main risk is divergence from the SQLite 3 pkg-config file. `@RELEASE@` and `@LIBS@` differ from the newer `sqlite3.pc.in` variables, and the library flag is `-lsqlite`, not `-lsqlite3`. If a package installs this file without a matching library, pkg-config checks may pass compilation flags but fail at link time. Test signals are successful substitution, `pkg-config --cflags --libs` output pointing at the intended prefix, and a small consumer program linking successfully with both dynamic and static pkg-config modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/sqlite.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/sqlite3.pc.in -->
# sources/storage-engines/sqlite/sqlite3.pc.in

## Purpose

`sqlite3.pc.in` is the primary pkg-config template for SQLite 3. It tells downstream build systems how to compile against installed SQLite headers and link against `libsqlite3`.

## Important Fields and Substitutions

The template defines standard installation variables `prefix`, `exec_prefix`, `libdir`, and `includedir`. Public metadata is `Name: SQLite`, `Description: SQL database engine`, and `Version: @PACKAGE_VERSION@`. The dynamic link line is `Libs: -L${libdir} -lsqlite3`. Static/private dependencies are expanded into `Libs.private` from `@LDFLAGS_MATH@`, `@LDFLAGS_ZLIB@`, `@LDFLAGS_DLOPEN@`, `@LDFLAGS_PTHREAD@`, and `@LDFLAGS_ICU@`. Header discovery is `Cflags: -I${includedir}`.

## Control Flow and Generation

The template is processed by SQLite's configure/build system into `sqlite3.pc`, which `main.mk` can install through `install-pc`. It contains no executable logic, but its substitutions must reflect the configured library feature set and install prefix.

## State and Persistence Behavior

The generated `sqlite3.pc` persists the configured version, install directories, public link flag, and private static-link dependencies. Consumers invoking `pkg-config sqlite3 --libs` get only the public `-L`/`-lsqlite3` flags, while `pkg-config sqlite3 --static --libs` also receives the `Libs.private` dependencies.

## Dependencies and Integration Points

This file integrates with `pkg-config`, `main.mk` install paths, configure-detected feature libraries, and downstream C/C++ build systems. Its private dependency list mirrors feature-specific linker buckets in the makefile, including math, zlib, dlopen, pthread, and ICU. Correctness depends on the generated file matching how `libsqlite3` was actually linked and installed.

## Risks and Test Signals

Risks are mostly packaging-related: missing private libraries break static linking, stale `@PACKAGE_VERSION@` misleads dependency checks, and incorrect `libdir`/`includedir` causes consumers to use a different SQLite than intended. ICU and zlib settings are especially sensitive because they may be optional at configure time. Test signals are successful `pkg-config --modversion sqlite3`, correct `pkg-config --cflags --libs sqlite3` output, successful dynamic consumer link, and successful static consumer link when static packages are expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/sqlite3.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/alter.c -->
# sources/storage-engines/sqlite/src/alter.c

## Purpose

`alter.c` implements SQLite's `ALTER TABLE` support when `SQLITE_OMIT_ALTERTABLE` is not defined. It generates VDBE bytecode and internal SQL rewrites for table rename, column rename, add column, drop column, drop constraint, add check constraint, set/drop not-null constraints, and the internal helper SQL functions used to safely rewrite `sqlite_schema` text.

## Important APIs, Types, and Functions

Externally visible parser/codegen entry points include `sqlite3AlterRenameTable()`, `sqlite3AlterBeginAddColumn()`, `sqlite3AlterFinishAddColumn()`, `sqlite3AlterRenameColumn()`, `sqlite3AlterDropColumn()`, `sqlite3AlterDropConstraint()`, `sqlite3AlterSetNotNull()`, `sqlite3AlterAddConstraint()`, and `sqlite3AlterFunctions()`.

Important local helpers include `isAlterableTable()`, `isRealTable()`, `renameTestSchema()`, `renameFixQuotes()`, `renameReloadSchema()`, `sqlite3ErrorIfNotEmpty()`, token-map management (`RenameToken`, `RenameCtx`, `sqlite3RenameTokenMap()`, `sqlite3RenameTokenRemap()`, `sqlite3RenameExprUnmap()`, `sqlite3RenameExprlistUnmap()`, `renameTokenFind()`), parse/rewrite helpers (`renameParseSql()`, `renameEditSql()`, `renameResolveTrigger()`, `renameWalkTrigger()`, `renameParseCleanup()`), and constraint-token helpers (`getConstraintToken()`, `getWhitespace()`, `getConstraint()`, `quotedCompare()`, `skipCreateTable()`, `alterFindCol()`, `alterFindTable()`, `alterRtrimConstraint()`).

Internal SQL functions registered by `sqlite3AlterFunctions()` are `sqlite_rename_column`, `sqlite_rename_table`, `sqlite_rename_test`, `sqlite_drop_column`, `sqlite_rename_quotefix`, `sqlite_drop_constraint`, `sqlite_fail`, `sqlite_add_constraint`, and `sqlite_find_constraint`. These are internal-only functions used by nested SQL generated by the parser.

## Control Flow

The table-rename path locates and validates the table, rejects system/shadow/eponymous tables and views, checks name collisions and authorization, optionally prepares a virtual-table `xRename`, then updates `sqlite_schema` SQL text using `sqlite_rename_table()`. It updates `tbl_name` and object names, adjusts `sqlite_sequence`, rewrites temp views/triggers when needed, invokes `OP_VRename` for virtual tables, reloads schema cookies, and runs `sqlite_rename_test()` over affected schema objects.

The add-column path has a two-phase parser flow. `sqlite3AlterBeginAddColumn()` copies the table into `Parse.pNewTable` with an `sqlite_altertab_` prefix so normal column parsing can append the new column without colliding with user tables. `sqlite3AlterFinishAddColumn()` validates restrictions: no primary-key or unique column, not-null requires non-null default or an empty table, foreign-key references with non-null defaults require an empty table, non-constant defaults are rejected unless the table is empty, and stored generated columns cannot be added to non-empty tables. It splices the new column text into the original `CREATE TABLE`, updates file-format cookie to at least 3, reloads the schema, and runs `pragma_quick_check()` when checks, generated not-null, or STRICT typing require validation.

The column-rename path validates the table, finds the old column index, normalizes double-quoted string literals through `renameFixQuotes()`, and updates schema SQL with `sqlite_rename_column()`. That internal function reparses each schema object in rename mode, uses parse-tree token maps and walkers to find references to the renamed column in tables, views, indexes, triggers, generated columns, check constraints, foreign keys, `UPDATE OF`, UPSERT clauses, and expression lists, then edits only those tokens. Schema reload and `renameTestSchema()` catch unresolved names or invalid rewrites.

The drop-column path validates the table and column, rejects primary-key/unique drops and dropping the final column, rewrites the `CREATE TABLE` text through `sqlite_drop_column()`, reloads and validates the schema, then rewrites each record on disk if the dropped column is not virtual. For rowid tables it rebuilds records with the rowid preserved; for WITHOUT ROWID tables it respects primary-key index layout. It handles virtual columns, REAL affinity conversion during extraction, and an edge case where all remaining columns are virtual by storing one NULL field.

Constraint editing is text-based but token-aware. `sqlite_drop_constraint()` can remove a named CHECK constraint or a column NOT NULL constraint, preserving valid comma/space layout and rejecting constraints that may not be dropped. `sqlite_add_constraint()` appends a new table-level or column-level constraint. `sqlite3AlterSetNotNull()` first checks for NULL data, then drops any existing not-null clause for the column and adds the new constraint text. `sqlite3AlterAddConstraint()` resolves the new CHECK expression as a self-reference, checks duplicate constraint names with `sqlite_find_constraint()`, verifies existing rows satisfy the new check, appends the constraint, and reloads the schema.

## State and Persistence Behavior

ALTER operations persist by editing the `sql`, `name`, and `tbl_name` columns of `sqlite_schema` or `sqlite_temp_schema`, updating `sqlite_sequence` for renamed autoincrement tables, changing schema cookies, and reparsing schemas through VDBE operations. Drop-column additionally rewrites table btree records to physically remove stored column values. Add-column usually changes only schema text and file format cookie, relying on default-value semantics for existing rows unless validation requires scans.

The code temporarily mutates parser state (`Parse.pNewTable`, `Parse.pRename`, `Parse.eParseMode`, `db->init.iDb`, `db->flags`, `db->xAuth`) and restores it after nested parsing. Internal rewrite functions enter all btrees while reparsing schema SQL and suppress authorization callbacks during internal analysis. `PRAGMA writable_schema` changes failure behavior: some rewrite/test functions return original SQL instead of raising parse errors.

## Dependencies and Integration Points

The file depends heavily on SQLite internals from `sqliteInt.h`: parser structures, `Table`, `Column`, `Index`, `Trigger`, `TriggerStep`, `Select`, `Expr`, `ExprList`, `FKey`, `SrcList`, `Vdbe`, `Walker`, `NameContext`, tokenizer token codes, schema table names, VDBE opcodes, authorization, virtual-table support, generated-column support, foreign-key support, writable-schema mode, and database flags such as `SQLITE_LegacyAlter`, `SQLITE_ForeignKeys`, DQS flags, and `SQLITE_Comments`.

It integrates with parser reductions in `parse.y`, code generation in VDBE, schema initialization/reload, nested SQL generation, the name resolver, trigger/view/index/table parsers, virtual-table `xRename`, `pragma_quick_check`, btree record operations, and SQLite's builtin function registry. Compile-time options (`SQLITE_OMIT_ALTERTABLE`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_GENERATED_COLUMNS`) change available paths.

## Risks and Edge Cases

Schema text rewriting is the core risk. The code must distinguish identifiers from string literals, comments, aliases, trigger pseudo-columns, generated expressions, table/column names inside foreign keys, view/query references, and CTE/subquery scopes. Token mapping uses pointers into parsed SQL, so invalid remapping or stale parse-tree pointers can produce undefined behavior; debug-only `renameTokenCheckAll()` is specifically there to catch this. DQS handling is delicate: rename-column and drop-column first convert double-quoted strings to single-quoted strings and later schema tests can disable DQS to avoid silently accepting broken rewrites.

Backward compatibility creates additional risk. `SQLITE_LegacyAlter` changes how aggressively views, triggers, FKs, indexes, and checks are rewritten/resolved. `writable_schema` can suppress parse errors. Virtual tables are partially supported for table rename only if `xRename` exists; virtual tables and views are rejected for column rename, drop column, and constraint edits. Shadow and eponymous tables are protected depending on read-only shadow-table settings.

Data integrity risks are highest in `DROP COLUMN` and constraint changes because they scan or rewrite table content. WITHOUT ROWID record reconstruction must preserve primary-key ordering and index payload layout. Adding not-null/check constraints must reject existing violating rows before modifying schema. Add-column restrictions avoid old-row incompatibilities with primary keys, uniqueness, non-constant defaults, stored generated columns, strict typing, and foreign-key semantics.

## Test Signals

Useful test signals include parser tests for all ALTER syntaxes, schema reparse failures from `sqlite_rename_test`, quick-check failures after add-column, data-preservation checks after drop-column on rowid and WITHOUT ROWID tables, virtual table rename tests including modules without `xRename`, foreign-key/view/trigger/index/generated-column rename tests, writable-schema and legacy-alter compatibility tests, DQS quote-fix regression tests, authorization callback tests, constraint duplicate/missing/violation tests, and fuzz tests that mutate `CREATE TABLE` syntax around comments, quoted identifiers, nested parentheses, and unusual constraints.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/alter.c -->
