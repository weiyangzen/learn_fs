# subset-b-007772 Research

Grouped research for OpenAFS comerr scanner/test files and platform configuration/build headers. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_lex.lex_nt.c -->
# sources/distributed-fs/openafs/src/comerr/et_lex.lex_nt.c

Purpose: checked-in flex 2.5 scanner output for the OpenAFS `compile_et` error-table grammar on NT/Windows-oriented builds. It tokenizes `.et` input for the yacc parser, preserving an old generated C scanner so Windows builds do not need to regenerate it.

Important APIs/types/functions: exports `yylex`, `yyrestart`, `yy_switch_to_buffer`, buffer helpers such as `yy_create_buffer`, `yy_delete_buffer`, `yy_scan_string`, and `yy_scan_bytes`, the globals `yyin`, `yyout`, `yytext`, `yyleng`, and `yylineno`, and a local `yywrap` returning EOF. The semantic actions return parser tokens `ERROR_TABLE`, `ERROR_CODE_ENTRY`, `END`, `QUOTED_STRING`, `STRING`, or a literal character, and store copied strings in `yylval.dynstr`.

Control flow: `yylex` initializes the current input buffer, drives the generated DFA tables, updates line numbers on matched newlines, and dispatches eleven rule actions originally from `et_lex.lex.l`. Keyword spellings for error-table declarations return grammar tokens; whitespace and comments are skipped; quoted strings are duplicated after stripping the closing quote; ordinary identifiers are duplicated as `STRING`; punctuation is returned as its character value; unmatched text is echoed by the flex default action. End of input runs the generated end-of-buffer path and terminates through `yywrap`.

State and persistence: scanner state is entirely process-local: current buffer, start state, line number, hold character, `yytext`, and allocated scan buffers. It persists no disk or registry state, but string tokens allocated with `strdup` become parser-owned memory and generated buffers must be released by callers when alternate scan APIs are used.

Dependencies and integration: integrates with the comerr yacc parser through token constants and `yylval`, and with `compile_et` grammar support through standard flex globals. It depends on libc stdio/stdlib/string handling and the parser headers that define tokens and semantic value layout.

Risks and test signals: because this is old generated scanner code, the main risks are drift from the source `.l` file, non-reentrant global state, fixed `YYLMAX` token length, unescaped quoted-string handling, and unchecked `strdup` allocation. Useful tests are regenerating error tables from `.et` files, quoted and unquoted token cases, malformed punctuation, comments/whitespace, long tokens, and a Windows build that uses this checked-in scanner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_lex.lex_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_name.c -->
# sources/distributed-fs/openafs/src/comerr/et_name.c

Purpose: converts an encoded comerr error number back into its short error-table name.

Important APIs/types/functions: exports `afs_error_table_name(int num)`. It uses `ERRCODE_RANGE` and `BITS_PER_CHAR` from the comerr headers, a 64-character table of uppercase, lowercase, digit, and underscore symbols, a static six-byte output buffer, and `lcstring` to lower-case the generated name.

Control flow: the function discards the low error-code bits, masks the remaining table-number field to 25 bits, decodes five six-bit character slots from high to low, skips zero slots, stores nonzero characters indexed as `ch - 1`, NUL-terminates the static buffer, lowercases it in place, and returns the buffer pointer.

State and persistence: state is limited to the file-static `buf`, so the returned pointer is overwritten by the next call and is not thread-safe. No external state is persisted.

Dependencies and integration: used by `afs_error_message` and diagnostics to report the table name for generated comerr bases. It depends on `error_table.h`, `mit-sipb-cr.h`, `internal.h`, roken, and OpenAFS parameter/config headers.

Risks and test signals: risks include static-buffer reuse in concurrent callers and incorrect names if the error-number encoding constants change. Test signals include known Kerberos/comerr table bases, ordinary UNIX errno values, zero/unknown table numbers, and repeated calls that verify expected overwrite semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/internal.h -->
# sources/distributed-fs/openafs/src/comerr/internal.h

Purpose: private include for the AFS com_err package.

Important APIs/types/functions: includes the MIT SIPB copyright header plus `errno.h`, `stdlib.h`, and `stdio.h`, and declares `yyerror(const char *s)` plus `xmalloc(unsigned int size)` for parser/compiler support.

Control flow: this header has no executable control flow; it standardizes private declarations shared by generated parser/scanner and comerr tooling.

State and persistence: no state is defined. The declarations imply error-reporting and allocation behavior implemented elsewhere.

Dependencies and integration: bridges lexer/parser code with local comerr helpers and libc error/allocation/stdio APIs. It is included by comerr implementation files such as `et_name.c` and generated grammar support.

Risks and test signals: risks are prototype drift, especially around old K&R-era generated C and `unsigned int` allocation sizes. Compile coverage of the comerr tools and parser error paths is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/mit-sipb-cr.h -->
# sources/distributed-fs/openafs/src/comerr/mit-sipb-cr.h

Purpose: carries the MIT Student Information Processing Board permission notice used by the original com_err sources.

Important APIs/types/functions: defines no C symbols; the whole file is a comment block granting copy, modify, and distribution permission with attribution and no-warranty terms.

Control flow: no executable control flow.

State and persistence: no runtime state or persisted data.

Dependencies and integration: included from comerr source files to keep licensing text associated with derived MIT SIPB code.

Risks and test signals: the risk is legal/attribution drift if the header is removed or altered. Build tests do not exercise behavior, but source audits should confirm files derived from the MIT com_err package retain this notice.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/mit-sipb-cr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/test/Makefile.in -->
# sources/distributed-fs/openafs/src/comerr/test/Makefile.in

Purpose: Autoconf Makefile template for the comerr self-test program.

Important APIs/types/functions: defines `srcdir`, includes `Makefile.config`, sets library search paths in `LDIRS`, builds `test` from `test.o`, `test1.o`, and `test2.o`, and relies on suffix rules from the surrounding build to generate `test1.c/.h` and `test2.c/.h` from `.et` files via `compile_et`.

Control flow: the default `all` target builds `test`; object dependencies force generated headers/sources to exist; `clean` removes generated `.et` outputs, objects, local tools, and test binaries. `install` and `dest` are intentionally no-op for this test directory.

State and persistence: writes only build artifacts in the object directory, notably generated error-table C/header files and the `test` executable. No installed state is produced.

Dependencies and integration: integrates the comerr test into the OpenAFS build rules through `AFS_LDRULE`, `${TOP_LIBDIR}`, `${DESTDIR}/lib/afs`, and `-lafscom_err`.

Risks and test signals: risks are stale generated files under parallel make, missing `compile_et` generation rules, and link-path mismatches. A successful `make test` build and execution of the resulting binary are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/test/test.c -->
# sources/distributed-fs/openafs/src/comerr/test/test.c

Purpose: runtime smoke test for generated comerr tables, system error fallback, and formatted `afs_com_err` output.

Important APIs/types/functions: calls `afs_error_table_name`, `afs_error_message`, `initialize_KRB_error_table`, `initialize_QUUX_error_table`, and `afs_com_err`, using generated constants from `test1.h` and `test2.h`. It also references `sys_nerr` and `errno` for system error boundary checks.

Control flow: prints messages before table initialization, initializes the KRB table twice to confirm duplicate registration is tolerated, initializes the QUUX table, prints messages for table entries, system errors, unknown codes, and then exercises `afs_com_err` with and without supplemental format strings.

State and persistence: modifies only the in-process comerr table registry through generated initializer calls and writes diagnostic text to stdout/stderr. No persistent state is created.

Dependencies and integration: depends on the generated test error tables, `afs/com_err.h`, standard stdio/errno, and `afs/afsutil.h` on NT builds. It is built by the sibling test Makefile against `libafscom_err`.

Risks and test signals: old-style `main()` and direct `sys_nerr` declarations are portability risks on modern libc implementations. Useful signals are correct table-name decoding before/after initialization, idempotent initializer behavior, graceful unknown-code messages, and formatted `afs_com_err` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/test/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.config.in -->
# sources/distributed-fs/openafs/src/config/Makefile.config.in

Purpose: central Autoconf-generated make fragment that defines OpenAFS installation paths, tool substitutions, compiler/linker flags, pretty-build wrappers, and shared compile/link recipes.

Important APIs/types/functions: provides variables such as `TOP_OBJDIR`, `TOP_INCDIR`, `SYS_NAME`, `AFS_PARAM`, `COMPILE_ET`, `RXGEN`, `LWPTOOL`, `CC_WRAPPER`, and `LD_WRAPPER`; common flags `COMMON_CFLAGS`, `LWP_CFLAGS`, `PTH_CFLAGS`, and `COMMON_LDFLAGS`; command wrappers `RUNCMD`, `RUN_CC`, and `RUN_LD`; and build recipes `LWP_CCRULE`, `PTH_CCRULE`, `LT_CCRULE`, `LT_LDLIB_*`, `LT_LDRULE*`, and default `AFS_LDRULE`.

Control flow: makefiles include this first, then optionally include LWP, pthread, libtool, or lwptool fragments to bind generic `AFS_*` rules. The `V=0` path hides raw commands and emits concise `CC`/`LD` lines while preserving failure diagnostics. The file also creates independent `COMPILE_ET_H` and `COMPILE_ET_C` commands to support parallel error-table generation.

State and persistence: no state itself, but it controls where builds install headers/libraries, where generated helper binaries are found, and how objects/libraries/executables are produced.

Dependencies and integration: fed by `configure` substitutions and included throughout the OpenAFS tree. It integrates roken, hcrypto, Kerberos/GSSAPI, pthread, PAM, Linux kernel, libtool, LWP, CTF, and architecture flags.

Risks and test signals: a wrong substitution can break the whole tree. Risks include quoting in `RUNCMD`, duplicated flag ordering, incorrect wrapper selection, stale `AFS_PARAM`, and libtool symbol-list assumptions. Full-tree builds with `V=0` and `V=1`, LWP and pthread targets, shared-library targets, and generated `.et` sources are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.config.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.in -->
# sources/distributed-fs/openafs/src/config/Makefile.in

Purpose: Makefile template for the `src/config` directory, building configuration helper tools and installing core public configuration headers.

Important APIs/types/functions: builds `config` from `config.o mc.o`, builds `mkvers`, generates `Makefile.version`, generates `AFS_component_version_number.c`, creates `param.h.new` by concatenating `AFS_PARAM_COMMON` and `AFS_PARAM`, and installs headers such as `afs/param.h`, `afs_sysnames.h`, `stds.h`, `icl.h`, `afs_args.h`, `venus.h`, and `vioc.h`.

Control flow: `all` builds helper tools and top-level include headers. `buildtools` builds the subset needed during early build. `Makefile.version` selects the CML or non-CML version fragment based on `CML/state`. Install and dest targets copy generated and static headers into configured include trees. `clean` removes local objects, tools, generated version files, and `param.h.new`.

State and persistence: produces build tools, generated `AFS_component_version_number.c`, `Makefile.version`, and installed/cached headers under `${TOP_INCDIR}`, `${DEST}`, and `${DESTDIR}${includedir}`.

Dependencies and integration: includes `Makefile.config` and `Makefile.lwp`, relies on Autoconf variables `AFS_PARAM` and `AFS_PARAM_COMMON`, and is required before kernel/libafs builds that need `param.h` and `afs_sysnames.h`.

Risks and test signals: risks include stale `param.h.new`, wrong CML selection, object-directory vs source-directory path mistakes, and non-atomic generated header updates. Signals are clean config-directory builds, header installation into all three include targets, and downstream libafs compilation using the generated platform header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.libtool.in -->
# sources/distributed-fs/openafs/src/config/Makefile.libtool.in

Purpose: small make fragment that defines suffix rules for modules that build libtool objects.

Important APIs/types/functions: maps `.c.lo`, `%.lo: %.c`, and `.m.lo` to `$(LT_CCRULE)`.

Control flow: included after `Makefile.config` by module Makefiles that need libtool `.lo` output; make suffix/pattern rules invoke the shared libtool compile recipe for C and Objective-C sources.

State and persistence: creates `.lo` and libtool side artifacts controlled by the common `LT_CLEAN` rule.

Dependencies and integration: depends on `LT_CCRULE` from `Makefile.config` and on configured libtool, pthread compiler, and wrappers.

Risks and test signals: risks are rule conflicts with module-specific patterns and Objective-C availability. Libtool library builds and `make clean` removal of `.lo/.libs` artifacts are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.libtool.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.lwp.in -->
# sources/distributed-fs/openafs/src/config/Makefile.lwp.in

Purpose: make fragment that selects LWP-flavored compile and link rules as the generic `AFS_*` rules.

Important APIs/types/functions: assigns `AFS_CFLAGS`, `AFS_LDFLAGS`, `AFS_CCRULE`, and `AFS_CCRULE_NOQ` from the LWP variables, and provides `.c.o`, `%.o: %.c`, and `.m.o` rules.

Control flow: after inclusion, ordinary object builds use the LWP compiler flags and `CCOBJ` wrapper path from `Makefile.config`.

State and persistence: creates standard `.o` files for LWP builds.

Dependencies and integration: depends on `LWP_CFLAGS`, `LWP_LDFLAGS`, and `LWP_CCRULE` from `Makefile.config`. Used by legacy single-threaded OpenAFS components and config tools.

Risks and test signals: risks are accidental inclusion in pthread-only modules and rule conflicts. Successful LWP object builds and links are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.lwp.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.lwptool.in -->
# sources/distributed-fs/openafs/src/config/Makefile.lwptool.in

Purpose: make fragment for libraries that need both LWP static objects and pthread/libtool objects from one source list.

Important APIs/types/functions: defines `.lo` suffix/pattern rules that call `$(LTLWP_CCRULE)`.

Control flow: included by hybrid modules; `lwptool` compiles a hidden `.lwp/*.o` copy and a libtool `.lo` copy for the same source.

State and persistence: creates `.lo` files plus mirrored `.lwp/*.o` files used later for static LWP libraries.

Dependencies and integration: depends on `LTLWP_CCRULE` and the `lwptool` script configured in `Makefile.config`.

Risks and test signals: risks include stale `.lwp` mirrors, filename assumptions during `.lo` to `.o` conversion, and missing libtool. Hybrid library builds and archives containing the `.lwp` objects are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.lwptool.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.pthread.in -->
# sources/distributed-fs/openafs/src/config/Makefile.pthread.in

Purpose: make fragment that selects pthread-aware compile and link rules as the generic `AFS_*` rules.

Important APIs/types/functions: assigns `AFS_CFLAGS`, `AFS_LDFLAGS`, `AFS_CCRULE`, and `AFS_LDRULE` from pthread variables and `MT_CC`, with quiet and non-quiet variants plus `.c.o`, `%.o: %.c`, and `.m.o` rules.

Control flow: modules including this fragment compile with `MT_CFLAGS` and link with `MT_CC`, overriding the default single-threaded link recipe from `Makefile.config`.

State and persistence: creates pthread-compatible object files and executables.

Dependencies and integration: depends on configured pthread compiler and flags from `Makefile.config`. Used by threaded OpenAFS daemons, libraries, and tools.

Risks and test signals: risks are missing thread flags at either compile or link time and inclusion order issues. Threaded component builds and runtime smoke tests for pthreaded daemons are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.pthread.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.version-CML.in -->
# sources/distributed-fs/openafs/src/config/Makefile.version-CML.in

Purpose: version-generation make fragment for builds using the historical CML state/stamps mechanism.

Important APIs/types/functions: defines `PACKAGE`, `VERSION`, and rules for `AFS_component_version_number.c`, `AFS_component_version_number.h`, `version.txt`, and `version.xml`, all produced by `config/mkvers`.

Control flow: targets invoke `mkvers` with output-format switches: default C source, `-v` for NT version info header, `-t` for text, and `-x` for XML. Comments note mkvers performs timestamp checks.

State and persistence: writes generated version files reflecting CML state and stamps.

Dependencies and integration: selected by `src/config/Makefile.in` when `CML/state` exists. Consumed by object files embedding OpenAFS component version strings and release metadata.

Risks and test signals: risks include absent CML files, stale timestamp comparisons, and format drift. Signals are correct generated C/header/text/XML version outputs for a CML checkout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.version-CML.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.version-NOCML.in -->
# sources/distributed-fs/openafs/src/config/Makefile.version-NOCML.in

Purpose: version-generation make fragment for normal non-CML builds.

Important APIs/types/functions: defines `PACKAGE`, generates `AFS_component_version_number.c` using `build-tools/git-version`, honors `SOURCE_DATE_EPOCH` for reproducible dates, writes `AFSVersion`, and creates simple `version.xml` and fallback `version.txt`.

Control flow: the C target writes a `.NEW` file, compares it with the current generated source, and moves it only when content changes. Without `SOURCE_DATE_EPOCH`, the string includes current date, user, and hostname; with it, the date comes from the epoch using GNU or BSD `date` syntax.

State and persistence: writes generated version C/XML/text files in the object directory.

Dependencies and integration: selected by `Makefile.in` when no `CML/state` exists; depends on `build-tools/git-version`, shell, date, cmp, and mv. The generated C is compiled into components that expose version strings.

Risks and test signals: risks include reproducibility breaks, date portability, missing git metadata, and non-atomic failure around `.NEW`. Signals are deterministic output with `SOURCE_DATE_EPOCH`, correct package/version strings, and no rebuild when content is unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/Makefile.version-NOCML.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afs_args.h -->
# sources/distributed-fs/openafs/src/config/afs_args.h

Purpose: public kernel/user ABI header for OpenAFS syscall opcodes, syscall classes, initialization structures, proc/ioctl replacements, and socket-proxy payloads.

Important APIs/types/functions: defines `AFSOP_*` operation codes for afsd startup, cache setup, cell configuration, RX daemon control, shutdown, and socket proxy; `AFSCALL_*` syscall classes; RX stats flags; `afs_umv_param`, `afs_usp_param`, `afs_uspc_param`, `afs_cacheParams`, `cm_initparams_v1`, Linux proc ioctl names and `VIOC_SYSCALL*`, Darwin/Solaris syscall argument layouts, cache inode sentinels, socket-proxy structures, and `AFS_SETINT_ATSYS` values.

Control flow: no executable flow, but consumers dispatch on these numeric opcodes. Comments explicitly require updating `afsd_init_syscall_opcodes()` when new `AFSOP_*` values are added.

State and persistence: defines the shape of state passed between afsd, kernel modules, proc/ioctl shims, callback interfaces, and socket proxy helpers. Cache parameter structures describe persistent cache sizing choices but do not store them themselves.

Dependencies and integration: included by kernel code, afsd, pioctl/syscall wrappers, rxstats tools, and platform-specific syscall implementations. It relies on configured `afs_int32`, `afs_uint32`, platform `_IOW/_IOWR` macros, and environment macros from `param.h`.

Risks and test signals: numeric ABI drift is the major risk. Structure size changes require versioning via `AFS_CLIENT_RETRIEVAL_VERSION`. Signals include afsd startup on each platform, syscall tracing opcode names, pioctl/proc ioctl compatibility, RX stats toggles, shutdown opcodes, and socket-proxy send/receive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afs_args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afs_sysnames.h -->
# sources/distributed-fs/openafs/src/config/afs_sysnames.h

Purpose: assigns stable numeric IDs to OpenAFS `SYS_NAME` platform strings.

Important APIs/types/functions: defines `SYS_NAME_ID_*` constants for historical and current AFS platforms, including Darwin, AIX, Solaris, Linux architectures, FreeBSD/NetBSD/OpenBSD/DragonFly, HP-UX, Windows, ARM, and ppc64le, plus realm-size constants `AFS_REALM_SZ` and `AFS_NUM_LREALMS`.

Control flow: no runtime flow. Platform `param.*.h` files set `SYS_NAME` and `SYS_NAME_ID` to one of these constants, allowing conditional compilation and system-name exchange to use stable IDs.

State and persistence: no runtime state; the file is a persistent registry of ABI/build identifiers.

Dependencies and integration: installed as `afs/afs_sysnames.h` by `src/config/Makefile.in` and included by generated `param.h` consumers.

Risks and test signals: risks are duplicate IDs, missing IDs for new `param.*.h` files, and accidental renumbering that breaks compatibility. Signals are compiling every platform header and verifying each `SYS_NAME_ID` reference resolves uniquely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afs_sysnames.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afsconfig-windows.h -->
# sources/distributed-fs/openafs/src/config/afsconfig-windows.h

Purpose: hand-maintained Windows replacement for the Autoconf-generated `afsconfig.h`.

Important APIs/types/functions: defines Windows feature availability and portability shims such as `SIZEOF_LONG 4`, `inline __inline`, `HAVE_ERROR_MESSAGE`, Winsock and Windows headers, POSIX mode constants, `socklen_t`, older MSVC `errno_t`, roken/directory/string/time feature macros, `AFS_NAMEI_ENV`, `RENAME_DOES_NOT_UNLINK`, Heimdal credential fields, and `ROKEN_LIB_DYNAMIC`.

Control flow: no executable flow; it drives conditional compilation in Windows builds.

State and persistence: no runtime state. It fixes the compile-time feature matrix for Windows/Win2000-style builds.

Dependencies and integration: included as the Windows `afsconfig.h` equivalent across OpenAFS NT code and shared libraries. It integrates with roken, Heimdal, Winsock, and OpenAFS namei cache code.

Risks and test signals: risks include stale feature declarations as Windows SDK/MSVC behavior changes, duplicate `#undef` sections, and type conflicts for `socklen_t` or `errno_t`. Signals are full Windows builds across supported compiler versions and runtime smoke tests for networking, directory, rename, lstat, and Heimdal integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/afsconfig-windows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/cc-wrapper.in -->
# sources/distributed-fs/openafs/src/config/cc-wrapper.in

Purpose: shell wrapper around compiler and linker invocations that optionally adds CTF debug type conversion/merging.

Important APIs/types/functions: accepts `cc` or `ld` mode followed by the real command, substitutes `CTFCONVERT`, `CTFMERGE`, `RM`, and `AFS_SYSNAME`, parses `-o` and `-g`, honors `OPENAFS_CC_WRAPPER_DEBUG_FLAG`, and defines helper functions `echo_run` and `cleanup`.

Control flow: runs the wrapped command first. If CTF tools are unavailable or no debug flag is present, exits successfully. For compile mode it optionally skips empty Solaris 11.1 objects after `elfdump`, then runs `ctfconvert`. For link mode it gathers `.o`/`.a` inputs, converts the executable itself if needed, and runs `ctfmerge`. Errors trigger cleanup of the target.

State and persistence: mutates only the build target by adding CTF data or removing it on post-processing failure. No persistent config is written.

Dependencies and integration: configured into `CC_WRAPPER` and `LD_WRAPPER` in `Makefile.config`; integrates Solaris CTF tools with OpenAFS builds.

Risks and test signals: risks are shell quoting for unusual paths, target extraction failures, Solaris-specific `elfdump` assumptions, and missing `.o/.a` detection for direct source links. Signals include debug and non-debug builds, Solaris kernel module builds, empty compilation units, and failure cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/cc-wrapper.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/config.c -->
# sources/distributed-fs/openafs/src/config/config.c

Purpose: command-line driver for generating platform-specific makefiles from prototype files.

Important APIs/types/functions: `main` validates `config <from file> <to file> <system name>`, opens input/output files, constructs an option list containing the full sysname, `all`, and split architecture/OS-version tokens, then calls `mc_copy(FILE *, FILE *, char **)`.

Control flow: after file setup, the sysname is duplicated and split on the first underscore so a platform such as `amd64_linux26` can match full-name, architecture-only, or OS-version-only sections in a Makefile prototype. `mc_copy` performs the conditional copy; errors print diagnostics and exit nonzero.

State and persistence: writes the generated output makefile. It includes `AFS_component_version_number.c`, embedding build version state into the tool binary.

Dependencies and integration: built by `src/config/Makefile.in` with `mc.o`; used for kernel/libafs MakefileProto conversion where conditional sections are tagged by sysname tokens.

Risks and test signals: risks include output truncation only through libc errors, leaked duplicated sysname on exit, and simplistic first-underscore splitting. Signals are generated Makefiles for full sysname, architecture-only, OS-only, and `all` sections, plus failure behavior for missing files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/icl.h -->
# sources/distributed-fs/openafs/src/config/icl.h

Purpose: public/private definitions for the OpenAFS in-core logging (ICL) tracing package.

Important APIs/types/functions: defines `struct afs_icl_set`, `struct afs_icl_log`, set/log flags, default log sizes, syscall operation numbers `ICL_OP_*`, trace macros `afs_Trace0` through `afs_Trace4`, parameter types such as `ICL_TYPE_STRING`, `ICL_TYPE_FID`, and `ICL_TYPE_INT64`, size macro `ICL_SIZEHACK`, create flags, copyout flags, lock aliases, global ICL lists/locks, and error/info constants.

Control flow: trace macros check whether a set is active via `ICL_SETACTIVE` and call the corresponding `afs_icl_Event*` function with packed parameter-type bits. ICL syscall operation constants drive control paths in fstrace/kernel handlers for copyout, clear, enumerate, set status, resize, and version queries.

State and persistence: declares global in-memory state for all logs and sets: refcounts, locks, linked lists, circular log buffers, event flags, timestamps, and cookies. Persistent flags mark long-lived sets/logs in memory; the header itself writes no storage.

Dependencies and integration: included by kernel and user-space tracing code. Kernel builds include `afs/param.h`, `afs_osi.h`, `afs/lock.h`, and generated trace IDs; user builds use `afs/afs_lock.h`.

Risks and test signals: risks include ABI/layout drift for fstrace copyout, long-size differences captured by `ICL_LONG` and `afs_icl_sizeofLong`, packed parameter-type overflow, and disabled/default state surprises. Signals are fstrace event creation, copyout/clear operations, 32/64-bit offset tracing, string/FID formatting, and concurrent log/set refcount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/icl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/linux-version -->
# sources/distributed-fs/openafs/src/config/linux-version

Purpose: shell validation script for legacy Linux kernel header trees listed in `LINUX_VERS`.

Important APIs/types/functions: reads `LINUX_VERS` and `LINUX_SRCDIR`, checks each `$LINUX_SRCDIR$VERS` or fallback source directory, reads `include/linux/version.h`, extracts `UTS_RELEASE` with `fgrep` and `awk`, and accumulates buildable versions.

Control flow: missing environment variables are treated as non-fatal skips. For each requested version, missing directories or headers report errors. A matching `UTS_RELEASE` marks the version buildable; mismatches are tolerated only if the release string contains the requested subversion. At the end, if any errors occurred, it reports whether some or no kernels can be built and exits nonzero only when none are valid.

State and persistence: no persistent state; it only reports validation status.

Dependencies and integration: used from config/kernel build contexts to verify Linux header availability before building libafs for specified kernels.

Risks and test signals: risks include unquoted paths, obsolete `version.h`/`UTS_RELEASE` assumptions for modern kernels, typoed comments, and `exit -1` shell portability. Signals are header-tree checks with exact matches, Red Hat multi-version strings, missing headers, and unset environment variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/linux-version -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/lwptool -->
# sources/distributed-fs/openafs/src/config/lwptool

Purpose: helper script that builds LWP static objects and pthread/libtool objects from the same source list.

Important APIs/types/functions: supports `--mode compile|link`, `--lwpcc`, `--mtcc`, `--linker`, `--ranlib`, `-o`, `--quiet`, and `--` option termination. `_run_cmd` echoes commands unless quiet and fails fast.

Control flow: compile mode maps output `.lo` to hidden `.lwp/*.o`, creates `.lwp`, invokes the LWP compiler for the static object, then invokes the pthread/libtool compiler for the requested object. Link mode maps each `.lo` argument to its `.lwp/*.o` counterpart, removes the target archive, invokes the linker/ar command, and runs ranlib.

State and persistence: creates `.lwp` object mirrors and static archives alongside libtool outputs.

Dependencies and integration: driven by `Makefile.config` `LTLWP_CCRULE` and `LT_LDLIB_lwp` rules. Depends on shell, sed, mkdir, rm, ar/linker, ranlib, and libtool compiler commands.

Risks and test signals: risks include shell-special filenames, missing `.lwp` directory handling, a usage typo in link mode, and naive `.lo` suffix substitution. Signals are hybrid library builds where both libtool `.lo` and LWP archive members are produced and link failures show the failed command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/lwptool -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/make_libafs_tree.pl -->
# sources/distributed-fs/openafs/src/config/make_libafs_tree.pl

Purpose: Perl utility that constructs a standalone `libafs_tree` by copying source/object files listed in `libafsdep` dependency manifests.

Important APIs/types/functions: parses `-t`, `-p`, `-o`, `-sn`, `-os`, `-q`, and `-n`; uses `File::Find` to locate `libafsdep`; `process_libafsdep` expands manifest entries and `MKAFS_OSTYPE`; `mkfullpath` recreates source-relative directories; `copyit` copies files with `cp -p` when size or mtime differ.

Control flow: validates required project directory, tree directory, sysname, and ostype, scans the source tree for dependency manifests, copies each listed source/object file or glob, manually copies `configure-libafs`, `Makefile-libafs.in`, and the OS-specific `src/libafs/MakefileProto`, writes `.version` via `build-tools/git-version` unless dry-run, and removes generated `include/afs/param.h` so the target tree regenerates it.

State and persistence: creates or updates the libafs tree directory and its copied files. Dry-run mode prints actions without copying.

Dependencies and integration: used by libafs packaging/build workflows; depends on Perl core modules, `cp`, OpenAFS `libafsdep` manifests, build-tools git versioning, and source/object directory layout.

Risks and test signals: risks include commented-out tree cleanup leaving stale files, glob overreach, path quoting in printed/system commands, and copy freshness based only on size/mtime. Signals are dry-run output, complete libafs tree generation, regenerated `param.h`, and successful standalone libafs build from the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/make_libafs_tree.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/mc.c -->
# sources/distributed-fs/openafs/src/config/mc.c

Purpose: conditional copier used by `config.c` to turn Makefile prototypes into concrete platform Makefiles.

Important APIs/types/functions: defines token list `struct token`, `ParseLine`, `GetLine`, `FreeTokens`, and exported `mc_copy(FILE *ain, FILE *aout, char *alist[])`. Tags beginning with `-` become `TOK_DONTUSE` exclusions.

Control flow: `mc_copy` reads input line by line. Lines beginning with `<` are parsed as option tags, reset copying to false, and enable copying if any requested token matches unless a matching negative token disables it. Ordinary lines are written to the output only while copying is enabled. The initial mode copies until the first tag line.

State and persistence: state is local to the current copy operation: active token list and copying flag. Output persistence is the generated file written by the caller.

Dependencies and integration: linked into the `config` tool and used with sysname token lists generated from `config.c`.

Risks and test signals: risks include fixed `MAXLINELEN` and `MAXTOKLEN`, simplistic token delimiters, comments only handled indirectly by prototype format, and memory allocation without null checks. Signals are prototype sections selected by full sysname, `all`, architecture-only, OS-only, and negative tags, plus overlong-line handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/mkvers.c -->
# sources/distributed-fs/openafs/src/config/mkvers.c

Purpose: C version-file generator for CML-based builds, kept in C so NT platforms do not need Perl.

Important APIs/types/functions: parses `-d`, `-o`, `-c`, `-v`, `-t`, and `-x`; reads `state` and `stamps` files under a CML directory; stores deltas in `stateDeltas`; and `PrintStamps` emits C source, NT version-info header, text, or XML revision output.

Control flow: `main` finds the CML directory by walking up to six `../` levels unless `-d` is given, chooses the default output file by format, rebuilds only when output is missing or older than `state`/`stamps`, reads state lines whose type is `I`, `N`, `C`, or `O`, and writes formatted version data. If CML data is unavailable, it writes a fallback message when possible and exits nonzero.

State and persistence: writes generated version files such as `AFS_component_version_number.c/.h`, `.txt`, or `.xml`. Runtime state is process-local arrays of up to 128 deltas.

Dependencies and integration: invoked by `Makefile.version-CML.in`; generated C is included/compiled into OpenAFS components for embedded build identification.

Risks and test signals: risks include fixed-size arrays and strings, truncation at output maxima, modifying the selected base-configuration string in place, incomplete XML escaping, and timestamp-only rebuild decisions. Signals include all output formats, prefixed component variable names, missing CML fallback, too-long delta lists, and up-to-date no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/mkvers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_linux_26.h -->
# sources/distributed-fs/openafs/src/config/param.alpha_linux_26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.alpha_linux_26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "alpha_linux_26", `SYS_NAME_ID` = SYS_NAME_ID_alpha_linux_26, `AFS_SYSCALL` = 338, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_ALPHA_LINUX_ENV, and feature macros including AFS_LINUX_64BIT_KERNEL, AFS_SYSCALL. It contains 35 source lines and 11 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_linux_26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_nbsd15.h -->
# sources/distributed-fs/openafs/src/config/param.alpha_nbsd15.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.alpha_nbsd15.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "alpha_nbsd15", `SYS_NAME_ID` = SYS_NAME_ID_alpha_nbsd15, `AFS_SYSCALL` = 210, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ALPHA_ENV, AFS_ALPHA_XBSD_ENV, AFS_ENV, AFS_KERBEROS_ENV, AFS_NAMEI_ENV, AFS_NBSD15_ENV, AFS_NBSD_ENV, AFS_VFSINCL_ENV, and feature macros including AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL, AFS_UIOSYS, AFS_UIOUSER. It contains 79 source lines and 35 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_nbsd15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_nbsd16.h -->
# sources/distributed-fs/openafs/src/config/param.alpha_nbsd16.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.alpha_nbsd16.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "alpha_nbsd16", `SYS_NAME_ID` = SYS_NAME_ID_alpha_nbsd16, `AFS_SYSCALL` = 210, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ALPHA_ENV, AFS_ALPHA_XBSD_ENV, AFS_ENV, AFS_KERBEROS_ENV, AFS_NAMEI_ENV, AFS_NBSD15_ENV, AFS_NBSD_ENV, AFS_VFSINCL_ENV, and feature macros including AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL, AFS_UIOSYS, AFS_UIOUSER. It contains 79 source lines and 35 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.alpha_nbsd16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_100.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_100.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_100.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_100", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_100, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, and feature macros including none. It contains 23 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_101.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_101.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_101.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_101", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_101, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_USR_FBSD101_ENV, AFS_X86_FBSD101_ENV, and feature macros including none. It contains 29 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_101.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_102.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_102.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_102.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_102", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_102, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, and feature macros including none. It contains 32 source lines and 12 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_102.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_103.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_103.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_103.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_103", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_103, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, AFS_X86_FBSD103_ENV, and feature macros including none. It contains 35 source lines and 15 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_103.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_104.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_104.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_104.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_104", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_104, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD104_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, and feature macros including none. It contains 38 source lines and 18 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_104.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_110.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_110.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_110.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_110", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_110, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD110_ENV, AFS_USR_FBSD110_ENV, AFS_X86_FBSD110_ENV, and feature macros including none. It contains 29 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_111.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_111.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_111.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_111", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_111, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD110_ENV, AFS_USR_FBSD111_ENV, and feature macros including none. It contains 41 source lines and 21 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_111.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_112.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_112.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_112.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_112", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_112, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD112_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD110_ENV, and feature macros including none. It contains 44 source lines and 24 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_112.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_113.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_113.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_113.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_113", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_113, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD112_ENV, AFS_FBSD113_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, and feature macros including none. It contains 47 source lines and 27 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_113.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_120.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_120.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_120.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_120", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_120, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, and feature macros including none. It contains 47 source lines and 27 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_121.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_121.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_121.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_121", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_121, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, and feature macros including none. It contains 50 source lines and 30 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_121.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_122.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_122.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_122.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_122", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_122, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_USR_FBSD101_ENV, and feature macros including none. It contains 53 source lines and 33 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_122.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_123.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_123.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_123.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_123", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_123, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, and feature macros including none. It contains 56 source lines and 36 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_123.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_130.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_130.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_130.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_130", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_130, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, and feature macros including none. It contains 58 source lines and 39 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_130.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_131.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_131.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_131.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_131", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_131, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, and feature macros including none. It contains 61 source lines and 42 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_131.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_140.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_140.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_140.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_140", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_140, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, and feature macros including none. It contains 64 source lines and 45 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_140.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_141.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_141.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_141.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_141", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_141, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, and feature macros including none. It contains 67 source lines and 48 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_fbsd_141.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_linux26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.amd64_linux26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_linux26", `SYS_NAME_ID` = SYS_NAME_ID_amd64_linux26, `AFS_SYSCALL` = 183, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_AMD64_LINUX_ENV, AFS_MAXVCOUNT_ENV, and feature macros including AFS_LINUX_64BIT_KERNEL, AFS_SYSCALL. It contains 39 source lines and 12 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd20.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd20.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd20.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd20", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd20, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 21 source lines and 7 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd30.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd30.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd30.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd30", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd30, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 22 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd40.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd40.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd40.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd40", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd40, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 22 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd50.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd50.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd50.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd50", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd50, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 22 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd60.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd60.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd60.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd60", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd60, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 22 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd70.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_nbsd70.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_nbsd70.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_nbsd70", `SYS_NAME_ID` = SYS_NAME_ID_amd64_nbsd70, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 22 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_nbsd70.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd36.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd36.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd36.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd36", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd36, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 18 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd37.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd37.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd37.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd37", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd37, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 18 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd37.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd38.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd38.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd38.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd38", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd38, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 18 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd38.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd39.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd39.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd39.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd39", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd39, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd39.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd40.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd40.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd40.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd40", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd40, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd41.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd41.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd41.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd41", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd41, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd41.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd42.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd42.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd42.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd42", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd42, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd43.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd43.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd43.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd43", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd43, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd44.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd44.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd44.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd44", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd44, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd44.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd45.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd45.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd45.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd45", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd45, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd45.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd46.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd46.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd46.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd46", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd46, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd46.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd47.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd47.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd47.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd47", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd47, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd47.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd48.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd48.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd48.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd48", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd48, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd48.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd49.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd49.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd49.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd49", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd49, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd49.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd50.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd50.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd50.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd50", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd50, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd51.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd51.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd51.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd51", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd51, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd51.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd52.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd52.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd52.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd52", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd52, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd52.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd53.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd53.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd53.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd53", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd53, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd53.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd54.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_obsd54.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.amd64_obsd54.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_obsd54", `SYS_NAME_ID` = SYS_NAME_ID_amd64_obsd54, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_AMD64_PARAM_H. It contains 19 source lines and 9 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_obsd54.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_w2k.h -->
# sources/distributed-fs/openafs/src/config/param.amd64_w2k.h

Purpose: Windows/NT parameter header for OpenAFS, selected during `param.h` generation for `param.amd64_w2k.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It maps OpenAFS Windows builds onto the NT/W2K sysname family and namei/64-bit-I/O assumptions used by the Windows cache manager and utility code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = not defined, `SYS_NAME_ID` = SYS_NAME_ID_amd64_w2k, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_KRB5_ERROR_ENV, AFS_NAMEI_ENV, AFS_NT40_ENV, and feature macros including AFS_HAVE_STATVFS. It contains 74 source lines and 11 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.amd64_w2k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm64_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.arm64_linux26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.arm64_linux26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "arm64_linux26", `SYS_NAME_ID` = SYS_NAME_ID_arm64_linux26, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_ARM64_LINUX_ENV, AFS_MAXVCOUNT_ENV, and feature macros including AFS_LINUX_64BIT_KERNEL. It contains 38 source lines and 11 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm64_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm_darwin_100.h -->
# sources/distributed-fs/openafs/src/config/param.arm_darwin_100.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.arm_darwin_100.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "ppc_darwin_100", `SYS_NAME_ID` = SYS_NAME_ID_ppc_darwin_100, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN70_ENV, AFS_DARWIN80_ENV, AFS_DARWIN90_ENV, AFS_DARWIN_ENV, AFS_ENV, AFS_NAMEI_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NONFSTRANS, AFS_SYSCALL. It contains 255 source lines and 81 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm_darwin_100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.arm_linux26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.arm_linux26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "arm_linux26", `SYS_NAME_ID` = SYS_NAME_ID_arm_linux26, `AFS_SYSCALL` = 137, endian mode = little-endian, environment macros including AFS_ARM_LINUX_ENV, and feature macros including AFS_SYSCALL. It contains 37 source lines and 8 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.arm_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_200.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_200.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_200.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_200", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_200, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 185 source lines and 100 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_210.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_210.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_210.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_210", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_210, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 189 source lines and 104 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_220.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_220.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_220.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_220", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_220, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 193 source lines and 108 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_220.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_230.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_230.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_230.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_230", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_230, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 197 source lines and 112 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_230.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_240.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_240.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_240.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_240", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_240, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 201 source lines and 116 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_240.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_250.h -->
# sources/distributed-fs/openafs/src/config/param.darwin_250.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_250.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_250", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_250, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 205 source lines and 120 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.darwin_250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.generic_fbsd.h -->
# sources/distributed-fs/openafs/src/config/param.generic_fbsd.h

Purpose: shared platform configuration for OpenAFS, selected during `param.h` generation for `param.generic_fbsd.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It provides common platform definitions included by thinner version or architecture headers.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = not defined, `SYS_NAME_ID` = not defined, `AFS_SYSCALL` = 339, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ENV, AFS_FBSD_ENV, AFS_GREEDY43_ENV, AFS_NAMEI_ENV, AFS_USR_FBSD_ENV, AFS_VFSINCL_ENV, AFS_VFS_ENV, AFS_X86_ENV, AFS_X86_FBSD_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_FBSD_NET_FOREACH, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS. It contains 211 source lines and 64 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.generic_fbsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux102.h -->
# sources/distributed-fs/openafs/src/config/param.hp_ux102.h

Purpose: HP-UX platform configuration for OpenAFS, selected during `param.h` generation for `param.hp_ux102.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It defines both kernel and, where present, user-space-kernel settings for HP-UX, including syscall slot 48, big-endian layout, VFS/UIO constants, allocator mappings, and HP-UX generation flags.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "hp_ux102", `SYS_NAME_ID` = SYS_NAME_ID_hp_ux102, `AFS_SYSCALL` = 48, endian mode = big-endian, environment macros including AFS_ENV, AFS_GREEDY43_ENV, AFS_HPUX100_ENV, AFS_HPUX101_ENV, AFS_HPUX102_ENV, AFS_HPUX90_ENV, AFS_HPUX_64BIT_ENV, AFS_HPUX_ENV, AFS_TEXT_ENV, AFS_USR_HPUX_ENV, AFS_VFS_ENV, and feature macros including AFS_3DISPARES, AFS_CLBYTES, AFS_DIRENT, AFS_FSNO, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_KALLOC, AFS_KFREE. It contains 160 source lines and 47 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux102.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux110.h -->
# sources/distributed-fs/openafs/src/config/param.hp_ux110.h

Purpose: HP-UX platform configuration for OpenAFS, selected during `param.h` generation for `param.hp_ux110.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It defines both kernel and, where present, user-space-kernel settings for HP-UX, including syscall slot 48, big-endian layout, VFS/UIO constants, allocator mappings, and HP-UX generation flags.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "hp_ux110", `SYS_NAME_ID` = SYS_NAME_ID_hp_ux110, `AFS_SYSCALL` = 48, endian mode = big-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_ENV, AFS_GREEDY43_ENV, AFS_HPUX100_ENV, AFS_HPUX101_ENV, AFS_HPUX102_ENV, AFS_HPUX110_ENV, AFS_HPUX90_ENV, AFS_HPUX_64BIT_ENV, AFS_HPUX_ENV, AFS_TEXT_ENV, AFS_USR_HPUX_ENV, and feature macros including AFS_3DISPARES, AFS_CLBYTES, AFS_DIRENT, AFS_FSNO, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_KALLOC, AFS_KFREE. It contains 165 source lines and 49 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux1123.h -->
# sources/distributed-fs/openafs/src/config/param.hp_ux1123.h

Purpose: HP-UX platform configuration for OpenAFS, selected during `param.h` generation for `param.hp_ux1123.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It defines both kernel and, where present, user-space-kernel settings for HP-UX, including syscall slot 48, big-endian layout, VFS/UIO constants, allocator mappings, and HP-UX generation flags.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "hp_ux1123", `SYS_NAME_ID` = SYS_NAME_ID_hp_ux1123, `AFS_SYSCALL` = 48, endian mode = big-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_HPUX100_ENV, AFS_HPUX101_ENV, AFS_HPUX102_ENV, AFS_HPUX110_ENV, AFS_HPUX1111_ENV, AFS_HPUX1122_ENV, AFS_HPUX1123_ENV, AFS_HPUX90_ENV, AFS_HPUX_64BIT_ENV, AFS_HPUX_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_KALLOC, AFS_KFREE, AFS_MINCHANGE. It contains 101 source lines and 44 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux1123.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux11i.h -->
# sources/distributed-fs/openafs/src/config/param.hp_ux11i.h

Purpose: HP-UX platform configuration for OpenAFS, selected during `param.h` generation for `param.hp_ux11i.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It defines both kernel and, where present, user-space-kernel settings for HP-UX, including syscall slot 48, big-endian layout, VFS/UIO constants, allocator mappings, and HP-UX generation flags.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "hp_ux11i", `SYS_NAME_ID` = SYS_NAME_ID_hp_ux11i, `AFS_SYSCALL` = 48, endian mode = big-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_64BIT_IOPS_ENV, AFS_ENV, AFS_GREEDY43_ENV, AFS_HPUX100_ENV, AFS_HPUX101_ENV, AFS_HPUX102_ENV, AFS_HPUX110_ENV, AFS_HPUX1111_ENV, AFS_HPUX90_ENV, AFS_HPUX_64BIT_ENV, and feature macros including AFS_3DISPARES, AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_FSNO, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_KALLOC. It contains 169 source lines and 53 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.hp_ux11i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_dfbsd_23.h -->
# sources/distributed-fs/openafs/src/config/param.i386_dfbsd_23.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_dfbsd_23.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_dfbsd_23", `SYS_NAME_ID` = SYS_NAME_ID_i386_dfbsd_23, `AFS_SYSCALL` = 339, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_DFBSD22_ENV, AFS_DFBSD23_ENV, AFS_DFBSD_ENV, AFS_ENV, AFS_FAKEOPEN_ENV, AFS_GREEDY43_ENV, AFS_NAMEI_ENV, AFS_USR_DFBSD22_ENV, AFS_USR_DFBSD23_ENV, AFS_USR_DFBSD_ENV, AFS_VFSINCL_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL. It contains 153 source lines and 65 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_dfbsd_23.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_100.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_100.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_100.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_100", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_100, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, and feature macros including none. It contains 19 source lines and 4 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_101.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_101.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_101.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_101", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_101, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_USR_FBSD101_ENV, AFS_X86_FBSD101_ENV, and feature macros including none. It contains 25 source lines and 7 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_101.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_102.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_102.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_102.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_102", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_102, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, and feature macros including none. It contains 28 source lines and 10 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_102.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_103.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_103.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_103.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_103", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_103, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, AFS_X86_FBSD103_ENV, and feature macros including none. It contains 31 source lines and 13 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_103.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_104.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_104.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_104.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_104", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_104, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD104_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, AFS_X86_FBSD103_ENV, and feature macros including none. It contains 34 source lines and 16 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_104.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_110.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_110.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_110.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_110", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_110, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD110_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD110_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD110_ENV, and feature macros including none. It contains 28 source lines and 10 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_111.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_111.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_111.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_111", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_111, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD110_ENV, AFS_USR_FBSD111_ENV, AFS_X86_FBSD101_ENV, and feature macros including none. It contains 37 source lines and 19 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_111.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_112.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_112.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_112.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_112", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_112, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD112_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD110_ENV, AFS_USR_FBSD111_ENV, and feature macros including none. It contains 40 source lines and 22 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_112.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_113.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_113.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_113.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_113", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_113, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD112_ENV, AFS_FBSD113_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD110_ENV, and feature macros including none. It contains 43 source lines and 25 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_113.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_120.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_120.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_120.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_120", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_120, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD104_ENV, and feature macros including none. It contains 43 source lines and 25 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_121.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_121.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_121.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_121", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_121, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, and feature macros including none. It contains 46 source lines and 28 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_121.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_122.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_122.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_122.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_122", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_122, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, and feature macros including none. It contains 49 source lines and 31 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_122.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_123.h -->
# sources/distributed-fs/openafs/src/config/param.i386_fbsd_123.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_fbsd_123.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_fbsd_123", `SYS_NAME_ID` = SYS_NAME_ID_i386_fbsd_123, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_FAKEOPEN_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_FBSD110_ENV, AFS_FBSD111_ENV, AFS_FBSD120_ENV, AFS_FBSD121_ENV, AFS_FBSD122_ENV, AFS_FBSD123_ENV, AFS_USR_FBSD101_ENV, and feature macros including none. It contains 52 source lines and 34 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_fbsd_123.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.i386_linux26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.i386_linux26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_linux26", `SYS_NAME_ID` = SYS_NAME_ID_i386_linux26, `AFS_SYSCALL` = 137, endian mode = little-endian, environment macros including AFS_I386_LINUX_ENV, and feature macros including AFS_SYSCALL. It contains 31 source lines and 7 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd15.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd15.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd15.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd15", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd15, `AFS_SYSCALL` = 210, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ENV, AFS_KERBEROS_ENV, AFS_NAMEI_ENV, AFS_NBSD15_ENV, AFS_NBSD_ENV, AFS_VFSINCL_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL, AFS_UIOSYS, AFS_UIOUSER. It contains 81 source lines and 34 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd16.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd16.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd16.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd16", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd16, `AFS_SYSCALL` = 210, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ENV, AFS_KERBEROS_ENV, AFS_NAMEI_ENV, AFS_NBSD15_ENV, AFS_NBSD_ENV, AFS_VFSINCL_ENV, AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL, AFS_UIOSYS, AFS_UIOUSER. It contains 83 source lines and 34 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd20.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd20.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd20.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd20", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd20, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 21 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd21.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd21.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd21.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd21", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd21, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 21 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd30.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd30.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd30.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd30", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd30, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 21 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd40.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd40.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd40.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd40", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd40, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 20 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd50.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd50.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd50.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd50", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd50, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 20 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd60.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd60.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd60.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd60", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd60, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 20 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd70.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nbsd70.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd70.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd70", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd70, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 20 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nbsd70.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nt40.h -->
# sources/distributed-fs/openafs/src/config/param.i386_nt40.h

Purpose: Windows/NT parameter header for OpenAFS, selected during `param.h` generation for `param.i386_nt40.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It maps OpenAFS Windows builds onto the NT/W2K sysname family and namei/64-bit-I/O assumptions used by the Windows cache manager and utility code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = not defined, `SYS_NAME_ID` = SYS_NAME_ID_i386_nt35, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_KRB5_ERROR_ENV, AFS_NAMEI_ENV, AFS_NT40_ENV, and feature macros including AFS_HAVE_STATVFS. It contains 64 source lines and 10 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_nt40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd31.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd31.h

Purpose: OpenBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_obsd31.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It is intentionally small, setting the OpenBSD sysname/ID and XBSD/x86 architecture flags consumed by shared OpenBSD build code.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_obsd31", `SYS_NAME_ID` = SYS_NAME_ID_i386_obsd31, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 16 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd31.h -->
