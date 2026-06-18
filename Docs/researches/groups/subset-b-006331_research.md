# subset-b-006331 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_initcall_order.pl -->
# sources/distributed-fs/ceph-client/scripts/generate_initcall_order.pl

## Purpose
Generates a linker script fragment that preserves deterministic kernel initcall ordering after LTO or archive aggregation by discovering `__initcall__...` symbols in object files and emitting ordered `SECTIONS` entries.

## APIs, Control Flow, and State
The script is a Perl host-build tool driven by `NM`, `objtree`, optional `PARALLELISM`, and command-line object paths. `process_files()` forks bounded child workers, each running `find_initcalls()` against `$objtree/$file`. Children parse `nm --defined-only` output, detect archive member boundaries, collect initcall records keyed by the compiler counter embedded in symbol names, and stream `<file-index> <level> <section-name>` lines to the parent. `wait_for_results()` uses `IO::Select` and `waitpid(WNOHANG)` to drain child pipes without deadlocking. `generate_initcall_lds()` reorders child results by input object index, groups by initcall level, and prints linker script sections such as `.initcall0.init` and `.con_initcall.init`.

## Dependencies and Integration
It integrates with kbuild linker-script generation and depends on GNU-compatible `nm`, Perl `IO::Handle`, `IO::Select`, and POSIX wait APIs. Its state is in-memory only: active child filehandles in `%$jobs` and collected records in `%$results`.

## Risks and Test Signals
The output is sensitive to exact symbol naming (`__initcall__module__counter_line_functionlevel`), input object ordering, archive formatting from `nm`, and child stdout protocol correctness. Test signals are a successful non-empty linker script, stable ordering for repeated object lists, failure on malformed child output, and failure on missing `NM` or empty initcall sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_initcall_order.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_rust_analyzer.py -->
# sources/distributed-fs/ceph-client/scripts/generate_rust_analyzer.py

## Purpose
Builds `rust-project.json` for `rust-analyzer` so kernel Rust crates, generated bindings, sysroot crates, proc macros, scripts, samples, drivers, and optional external modules can be indexed without Cargo metadata.

## APIs, Control Flow, and State
The main API is `generate_crates(srctree, objtree, sysroot_src, external_src, cfgs, core_edition)`, returning a list of typed crate dictionaries. It reads `include/generated/rustc_cfg`, parses `--cfgs crate=values` with `args_crates_cfgs()`, shells out through `invoke_rustc()` using `$RUSTC` for crate names and proc-macro dylib names, then registers crates in dependency order. Helpers create sysroot crates (`core`, `alloc`, `std`, `proc_macro`), vendored support crates (`compiler_builtins`, `proc_macro2`, `quote`, `syn`), proc macros, generated crates (`bindings`, `uapi`, `kernel` with `OBJTREE` and include/exclude source metadata), Rust scripts referenced from `scripts/Makefile`, and root crates under `samples`/`drivers` or `exttree` when matching Makefile/Kbuild targets exist.

## Dependencies and Integration
It depends on Python 3, `RUSTC`, kernel Rust source layout, generated object-tree files, sysroot source layout, and `rust-analyzer`'s JSON schema. State is transient in the `crates` list and emitted JSON only.

## Risks and Test Signals
Risks include stale generated cfgs, missing proc-macro dylibs, mismatched sysroot editions, false positives/negatives in root-crate detection, and JSON paths that are valid only for the current tree. Test signals are valid JSON, rust-analyzer loading without unresolved core/kernel crates, `--verbose` logs for discovered external crates, and build-system tests that regenerate project metadata after Rust layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_rust_analyzer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_rust_target.rs -->
# sources/distributed-fs/ceph-client/scripts/generate_rust_target.rs

## Purpose
Creates the custom Rust target specification JSON consumed by kernel Rust builds for architectures that cannot rely solely on rustc built-in targets.

## APIs, Control Flow, and State
The file implements a tiny JSON emitter with `Value`, `Object`, `TargetSpec`, and `Display` impls, intentionally avoiding a serde dependency in the build host tool. `KernelConfig::from_stdin()` parses `include/config/auto.conf` from stdin into a `HashMap`. `KernelConfig::has()` checks `CONFIG_` options while avoiding literal config names in comments that would confuse `fixdep`, and `rustc_version_atleast()` compares `CONFIG_RUSTC_VERSION`. `main()` selects architecture behavior: ARM, ARM64, 64-bit RISC-V, and LoongArch panic because they use built-in targets; 32-bit RISC-V and non-UML i386 panic as unsupported; x86_64 and UML i386 emit architecture, data-layout, target features, LLVM target, sanitizer, pointer-width, endian, frame-pointer, stack-probe, and debug-script settings.

## Dependencies and Integration
The tool depends only on Rust stdlib and kbuild piping `auto.conf` to stdin. It integrates with Rust compilation flags and must track rustc target-spec schema changes.

## Risks and Test Signals
The hand-written JSON generator does not escape strings, which is acceptable for fixed internal keys but risky if arbitrary values are added. Version-gated pointer-width typing and x86 ABI features are brittle across rustc releases. Test signals include rustc accepting the generated target file, architecture build coverage, and negative tests for unsupported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_rust_target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/Makefile -->
# sources/distributed-fs/ceph-client/scripts/genksyms/Makefile

## Purpose
Defines the host-build rules for the `genksyms` tool that computes exported symbol ABI CRCs.

## APIs, Control Flow, and State
The Makefile adds `genksyms` to `hostprogs-always-y` and composes it from `genksyms.o`, generated parser object `parse.tab.o`, and generated lexer object `lex.lex.o`. It adds `-I $(src)` to parser and lexer host C flags so generated C files can include source-tree headers. It also declares that `lex.lex.o` depends on `parse.tab.h`, ensuring flex output sees bison token definitions before compilation.

## Dependencies and Integration
This integrates with kbuild host tools, bison/yacc-generated parser headers, flex-generated lexers, and the local `scripts/include` helpers. It has no runtime state.

## Risks and Test Signals
The key risk is stale generated lexer/parser ordering if dependencies are incorrect. Build success of `scripts/genksyms/genksyms`, correct regeneration after `parse.y` changes, and modversion build tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.c -->
# sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.c

## Purpose
Implements the `genksyms` host program, which parses preprocessed C declarations and emits `#SYMVER name crc` lines for exported symbols. The CRC encodes ABI-relevant type information for module versioning.

## APIs, Control Flow, and State
Public functions shared with the lexer/parser are `find_symbol()`, `add_symbol()`, `export_symbol()`, `free_node()`, `free_list()`, `copy_node()`, `copy_list_range()`, and `error_with_pos()`. Global state includes `cur_line`, `cur_filename`, `in_source_file`, CLI flags, a 4096-bucket symbol hashtable, and traversal lists for expansion and dump output. `main()` parses flags (`--debug`, `--dump`, `--reference`, `--dump-types`, `--preserve`, warnings), reads an optional reference type dump, invokes `yyparse()`, optionally writes expanded type dumps, and exits nonzero on accumulated errors.

`__add_symbol()` handles namespace mapping, redefinition detection, reference override preservation, enum constant value synthesis, and declaration status tracking. `expand_and_crc_sym()` recursively expands typedef, enum, struct, and union references into a CRC stream while detecting cycles through `expansion_trail`. `export_symbol()` finds the normal symbol, expands it, reports reference changes, and prints the final CRC.

## Dependencies and Integration
It depends on generated lexer/parser code, `genksyms.h`, local hashtable/list helpers, and kbuild piping preprocessed sources containing rewritten export markers.

## Risks and Test Signals
Risks include segfaults on malformed reference files, stack use from `alloca()` for large type lists, C-parser incompleteness, namespace collision behavior, and ABI churn if formatting changes. Test signals are stable `#SYMVER` values, `--dump-types` round trips, warning behavior under `--preserve`, and module build tests with changed exported prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.h -->
# sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.h

## Purpose
Defines shared types and interfaces for the genksyms lexer, parser, and C implementation.

## APIs, Control Flow, and State
The header defines symbol namespaces (`SYM_NORMAL`, `SYM_TYPEDEF`, `SYM_ENUM`, `SYM_STRUCT`, `SYM_UNION`, `SYM_ENUM_CONST`), symbol change statuses, `struct string_list` token nodes, and `struct symbol` entries carrying hash linkage, definition token lists, expansion/visited links, declaration flags, and override metadata. It sets bison `YYSTYPE` to `struct string_list **`, exposing parser semantic values as mutable list splice points. It declares scanner/parser entry points, global source-position state, symbol-table operations, export handling, list memory helpers, and `dont_want_type_specifier`.

## Dependencies and Integration
It depends on `list_types.h` for `hlist_node` and standard C headers. It is the contract joining `genksyms.c`, `lex.l`, `parse.y`, and `keywords.c`.

## Risks and Test Signals
The pointer-to-pointer parser value convention is compact but fragile: lexer and grammar actions must agree on list ownership. Test signals are clean parser generation, valgrind or sanitizer runs for list ownership changes, and unchanged modversion CRCs after parser refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/genksyms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/keywords.c -->
# sources/distributed-fs/ceph-client/scripts/genksyms/keywords.c

## Purpose
Maps C, GNU C, kernel, and architecture-specific reserved words to genksyms parser tokens.

## APIs, Control Flow, and State
The file defines a static `keywords[]` table and `is_reserved_word(str, len)`. The function linearly scans the table, compares length and bytes, and returns the parser token or `-1`. Covered tokens include asm/attribute/typeof forms, qualifiers, integer builtins, C storage/type keywords, `_Static_assert`, x86 segment qualifiers, and the internal `__GENKSYMS_EXPORT_SYMBOL` marker.

## Dependencies and Integration
It is textually included by `lex.l`, so it relies on token macros from `parse.tab.h` already being visible. It stores no mutable state.

## Risks and Test Signals
Risks are missing newly introduced compiler keywords or mapping a common identifier as a keyword, which changes ABI CRC parsing. Test signals are lexer/parser tests with modern compiler output and stable genksyms CRCs across kernel headers using new C syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/keywords.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/lex.l -->
# sources/distributed-fs/ceph-client/scripts/genksyms/lex.l

## Purpose
Provides genksyms lexical analysis, converting preprocessed C into parser tokens and token-list fragments suitable for ABI hashing.

## APIs, Control Flow, and State
Flex rule `yylex1()` performs primitive tokenization for identifiers, numbers, strings, chars, preprocessor line markers, operators, and whitespace. The exported `yylex()` is a second-stage state machine. It tracks source file and line markers, populates `cur_filename`, `cur_line`, and `in_source_file`, appends tokens into `struct string_list` nodes, and returns higher-level phrase tokens for attributes, asm blocks, `typeof`, bracket/brace bodies, expressions, and static assertions. It consults `is_reserved_word()` and `find_symbol()` to distinguish typedef names from identifiers, using `dont_want_type_specifier` and internal suppression counters to resolve grammar context.

## Dependencies and Integration
It depends on flex, `genksyms.h`, generated `parse.tab.h`, and textual inclusion of `keywords.c`. The parser consumes token-list splice points via `yylval`.

## Risks and Test Signals
Risks include mis-nesting phrase states, incorrect source-file ownership for included declarations, typedef ambiguity, and token accumulation leaks on parse errors. Test signals are successful parsing of complex preprocessed headers, correct error locations, and unchanged CRC output for declarations with attributes, anonymous structs, arrays, and initializers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/lex.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/parse.y -->
# sources/distributed-fs/ceph-client/scripts/genksyms/parse.y

## Purpose
Defines the genksyms grammar for ABI-relevant C global declarations and export markers.

## APIs, Control Flow, and State
The bison grammar tracks `is_typedef`, `is_extern`, `current_name`, and reusable `decl_spec`. Helper actions remove or splice `struct string_list` nodes, and `record_compound()` records struct/union/enum definitions unless the tag originates from the primary source file, where a tagged reference is kept instead. Grammar rules handle simple declarations, typedefs, function definitions, storage classes, type specifiers, qualifiers, declarators, nested declarators, parameter lists, class bodies, enum bodies, asm definitions, static assertions, and `EXPORT_SYMBOL` markers. On export markers, it calls `export_symbol()`.

## Dependencies and Integration
It depends on tokenization from `lex.l`, symbol and list APIs from `genksyms.c`, and bison-generated parser code. It is integrated into the kbuild modversion path.

## Risks and Test Signals
The grammar intentionally ignores many expression and initializer details while preserving ABI-affecting declaration shape. Risks include rejecting new C syntax, mishandling typedef-vs-identifier context, or over-recording included compound definitions. Test signals include parser generation with no unexpected conflicts, module export CRC stability, and regression cases for enums, bitfields, attributes, function pointers, and static assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/genksyms/parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/get_dvb_firmware -->
# sources/distributed-fs/ceph-client/scripts/get_dvb_firmware

## Purpose
Downloads, verifies, extracts, and assembles legacy DVB firmware blobs from vendor archives or known firmware URLs for many supported device components.

## APIs, Control Flow, and State
The script dispatches a single component argument through `@components` and `eval($cid)`, so every component name corresponds to a Perl subroutine. Firmware subroutines define source URLs, expected MD5 hashes, output filenames, temporary directories, and extraction steps. Common helpers check for `unzip`, `md5sum`, `wget`, and `unshield`; download files if missing; unzip or unshield archives; verify MD5 hashes; copy files; extract byte ranges; append fragments; and remove zero padding. More complex components synthesize firmware streams from multiple fragments and embedded command bytes.

## Dependencies and Integration
It depends on network availability, vendor URLs, `/tmp`, Perl `File::Temp`, external `wget`, `unzip`, `unshield`, `md5sum`, `cp`, and kernel media firmware naming conventions. Outputs are files in the current directory for users to install under firmware search paths.

## Risks and Test Signals
Risks are high because many vendor URLs are obsolete, MD5 is only an integrity check, `eval($cid)` relies on the curated component list, file paths contain spaces, some tempdirs disable cleanup, and several helpers use global bareword filehandles. Test signals are successful extraction for each component, exact hash matches, output names matching driver expectations, and failure on missing tools or corrupted downloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/get_dvb_firmware -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/get_maintainer.pl -->
# sources/distributed-fs/ceph-client/scripts/get_maintainer.pl

## Purpose
Selects maintainers, reviewers, lists, SCM trees, status, web links, bug links, and optional VCS-derived contributors for patches or source paths by interpreting Linux `MAINTAINERS` metadata.

## APIs, Control Flow, and State
The script is a large Perl CLI. It loads defaults, `.get_maintainer.conf`, `.get_maintainer.ignore`, `.mailmap`, and one or more MAINTAINERS files. `read_maintainer_file()` stores raw type/value rows while converting `F:` and `X:` globs into regex fragments and collecting `K:` keyword patterns. Input handling either treats `-f` arguments as files/directories or parses patches for diff paths, rename/mode lines, hunk ranges, and `Fixes:` tags. `get_maintainers()` scans matching MAINTAINERS sections, applies excludes, pattern-depth ranking, keywords, file-local emails, git/hg signers, blame, fixes commit signers, and optional interactive selection. Address helpers parse, format, validate RFC822-like addresses, apply mailmap, deduplicate, attach roles/statistics, and emit multiline or separator-delimited output.

## Dependencies and Integration
It depends on Perl core modules, optional `git`, `hg`, `wget` for self-tests, repository layout checks, MAINTAINERS syntax, and VCS history. It is used by patch submission workflows, `git send-email --cc-cmd`, CI checks, and maintainer self-tests.

## Risks and Test Signals
Risks include regex injection through metadata, slow blame/history scans, brittle parsing of patches and email syntax, stale URLs, duplicate or malformed MAINTAINERS sections, and surprising directory behavior. Test signals include `--self-test` categories, known patch/file outputs, mailmap/dedup regressions, VCS fallback behavior, and performance on large trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/get_maintainer.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gfp-translate -->
# sources/distributed-fs/ceph-client/scripts/gfp-translate

## Purpose
Translates a numeric GFP allocation mask into named `___GFP_*` flag bits using the kernel source tree's own headers.

## APIs, Control Flow, and State
The bash script accepts `--source DIRECTORY`, `-h/--help`, and one mask expression. It guesses the source tree from `/usr/src/linux` or the current directory, creates a temporary C file, extracts bit enum names from `include/linux/gfp_types.h` with `sed`, emits a C program that includes generated autoconf and GFP type headers, compiles it with `${CC:-gcc}`, and runs it. The generated program evaluates `unsigned long long mask = <GFPMASK>` and prints every set bit with a known name or `*** INVALID ***`.

## Dependencies and Integration
It depends on bash, `mktemp`, `sed`, a C compiler, generated kernel config headers, and an in-tree include layout. It is a debugging/diagnostic tool rather than a build dependency.

## Risks and Test Signals
The mask expression is embedded directly into generated C, so this should be treated as local trusted input. It also assumes generated headers exist. Test signals are successful compilation, correct names for known GFP masks, invalid-bit reporting, and cleanup of temporary files on normal or error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gfp-translate -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/git-resolve.sh -->
# sources/distributed-fs/ceph-client/scripts/git-resolve.sh

## Purpose
Resolves abbreviated commit IDs, optionally paired with commit subjects, into full SHA-1 hashes for fixing or validating commit references in messages.

## APIs, Control Flow, and State
The shell script exposes `git_resolve_commit [--force] <id> [subject]`, `convert_to_grep_pattern()`, `run_selftest()`, and CLI dispatch. Normal resolution uses `git rev-parse --disambiguate`. If exactly one match exists, it prints it. If multiple matches exist and a subject is present, it converts the subject into a Perl-regex anchored grep pattern, supporting escaped ellipsis as a wildcard, and checks candidate commit subjects. In `--force` mode, if no ID matches, it searches recent git log subjects directly.

## Dependencies and Integration
It depends on bash, git, sed, grep with `-P`, and repository history containing expected commits. It has no persistent state; self-tests hard-code representative commit references.

## Risks and Test Signals
Risks include regex escaping gaps, subject ambiguity, limited `git log -10` search in force mode, unquoted expansion in self-tests by design, and SHA-1-specific assumptions. Test signals are `--selftest`, exact single-match resolution, failure on wrong subject, wildcard subject matching, and force-mode fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/git-resolve.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/headerdep.pl -->
# sources/distributed-fs/ceph-client/scripts/headerdep.pl

## Purpose
Builds a header include dependency graph and either reports recursive include cycles or emits GraphViz DOT output.

## APIs, Control Flow, and State
Options include `--all`, `--graph`, `-I`, help, and version. `strip()` normalizes input paths relative to include roots, `search()` resolves headers in include directories, and `parse_all()` recursively reads `#include <...>` directives into `%deps` keyed by normalized header names. `detect_cycles()` walks dependency chains from requested headers and calls `print_cycle()` for the first or all detected cycles. `graph()` prints vertices and edges with sanitized node names from `mangle()`.

## Dependencies and Integration
It depends on Perl `Getopt::Long`, readable include trees, and optional GraphViz downstream. It is a developer diagnostic utility and stores graph state only in memory.

## Risks and Test Signals
It only parses angle-bracket includes and ignores preprocessor conditionals, quoted includes, macro includes, and generated headers not present on disk. Test signals include cycle warnings with line numbers, `--all` reporting multiple cycles, DOT accepted by `dot`, and include-root normalization for `-I`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/headerdep.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/headers_install.sh -->
# sources/distributed-fs/ceph-client/scripts/headers_install.sh

## Purpose
Sanitizes exported kernel UAPI headers for userspace installation.

## APIs, Control Flow, and State
The shell script takes exactly `INFILE OUTFILE`, creates `$OUTFILE.tmp`, and registers a trap to remove partial outputs. It first enforces that GPL SPDX identifiers for syscall headers include `WITH Linux-syscall-note`. It then runs `sed` rewrites to remove selected annotations/includes, convert `__packed`, wrap `inline/asm/volatile` as underscored names, and normalize `_UAPI` guard markers. `scripts/unifdef` removes `__KERNEL__` code and applies `__EXPORTED_HEADERS__`. A final sed program strips block comments and scans remaining code for leaked `CONFIG_*` tokens, failing if any are found.

## Dependencies and Integration
It depends on POSIX shell, sed with extended regex, `scripts/unifdef`, and kbuild header-install targets. Persistent state is only the generated output header.

## Risks and Test Signals
Risks include sed patterns missing new annotations, false positives/negatives in CONFIG leak detection, and output deletion by trap on errors. Test signals are header-install target success, missing syscall-note failure, no leaked config names, and userspace compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/headers_install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/array_size.h -->
# sources/distributed-fs/ceph-client/scripts/include/array_size.h

## Purpose
Provides a small host-tool copy of the common `ARRAY_SIZE()` macro.

## APIs, Control Flow, and State
The header defines `ARRAY_SIZE(arr)` as `sizeof(arr) / sizeof((arr)[0])` under an include guard. It has no functions, state, or runtime behavior.

## Dependencies and Integration
It is used by host tools and helper headers such as `hashtable.h` where the full kernel header stack is not available or appropriate.

## Risks and Test Signals
The macro does not reject pointers, so misuse can silently compute pointer-size ratios. Test signals are host-tool compilation and review of callers that pass actual arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/array_size.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/hash.h -->
# sources/distributed-fs/ceph-client/scripts/include/hash.h

## Purpose
Supplies lightweight hash helpers for host tools.

## APIs, Control Flow, and State
`hash_str()` implements FNV-1a-like 32-bit string hashing. `hash_32()` multiplies by the 32-bit golden-ratio constant, and `hash_ptr()` casts a pointer through `unsigned long` to `unsigned int` before hashing. There is no mutable state.

## Dependencies and Integration
The header is standalone and mirrors simplified kernel hash helpers for scripts-side code that cannot include full kernel internals.

## Risks and Test Signals
The functions are non-cryptographic and `hash_ptr()` loses high pointer bits on 64-bit hosts. Test signals are compile coverage in host tools and acceptable distribution for small in-memory tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/hashtable.h -->
# sources/distributed-fs/ceph-client/scripts/include/hashtable.h

## Purpose
Provides a compact kernel-style hash table API for host utilities.

## APIs, Control Flow, and State
The header defines table declaration/definition macros, `HASH_SIZE`, bucket selection by `key % HASH_SIZE(table)`, initialization, add/delete helpers, and iteration macros for all buckets or a specific bucket with safe-removal variants. It builds on `struct hlist_head` and `struct hlist_node`.

## Dependencies and Integration
It includes `array_size.h` and `list.h`. `genksyms.c` uses it for the symbol table, but it is generic enough for other host tools.

## Risks and Test Signals
Risks include modulo-based distribution depending entirely on caller hash quality, macro assumptions that `table` is a true array, and C99 loop variable declarations. Test signals are host-tool compilation, add/find/delete behavior, and safe iteration while removing entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/hashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/list.h -->
# sources/distributed-fs/ceph-client/scripts/include/list.h

## Purpose
Implements a scripts-side subset of Linux doubly linked list and hlist primitives for host tools.

## APIs, Control Flow, and State
The header provides `container_of()`, list poisons, `LIST_HEAD` initializers, add/delete/replace/move helpers, empty/position tests, entry accessors, forward/reverse/safe typed iteration macros, and hlist initialization, deletion, add-head, entry, and iteration helpers. State is held by caller-owned `struct list_head` or `struct hlist_node` links.

## Dependencies and Integration
It depends on `stddef.h` and `list_types.h`, and uses GCC extensions such as `typeof`, statement expressions, and `_Static_assert`. It supports host utilities such as `genksyms`.

## Risks and Test Signals
Risks are typical intrusive-list hazards: deleting uninitialized nodes, using entries after poison, empty-list misuse with first/last accessors, and compiler incompatibility outside GCC/Clang-like hosts. Test signals are host-tool builds with warnings enabled and focused add/delete/iteration tests if helpers change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/list_types.h -->
# sources/distributed-fs/ceph-client/scripts/include/list_types.h

## Purpose
Defines the minimal intrusive list node types used by scripts-side list and hashtable helpers.

## APIs, Control Flow, and State
The header declares `struct list_head` with `next`/`prev`, `struct hlist_head` with `first`, and `struct hlist_node` with `next` and `pprev`. It has no functions or behavior; callers manage node lifetime.

## Dependencies and Integration
It is included by `list.h` and by code that embeds list nodes in host-tool structures, notably genksyms symbols.

## Risks and Test Signals
The types are intentionally ABI-local to host tools. Test signals are successful compilation and no accidental mixing with incompatible full-kernel list definitions in the same translation unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/list_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/xalloc.h -->
# sources/distributed-fs/ceph-client/scripts/include/xalloc.h

## Purpose
Provides fail-fast allocation wrappers for host utilities.

## APIs, Control Flow, and State
`xmalloc()`, `xcalloc()`, `xrealloc()`, `xstrdup()`, and `xstrndup()` call the matching libc allocator and `exit(1)` on null results. They return allocated memory on success and do not print diagnostics.

## Dependencies and Integration
It includes `stdlib.h` and `string.h`. Tools such as `kallsyms.c` use it to simplify error handling in build-time utilities.

## Risks and Test Signals
The wrappers treat `malloc(0)` returning null as fatal, unlike some local wrappers elsewhere. They also make cleanup impossible on OOM. Test signals are host-tool compile coverage and intentional OOM handling expectations documented by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/include/xalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/insert-sys-cert.c -->
# sources/distributed-fs/ceph-client/scripts/insert-sys-cert.c

## Purpose
Patches a built `vmlinux` image by inserting an extra system certificate into the reserved `system_extra_cert` area and updating related size/used symbols.

## APIs, Control Flow, and State
The tool accepts `-b <vmlinux> -c <certfile> [-s <System.map>]`. It reads the certificate into memory, mmaps `vmlinux` read-write, validates ELF magic, host-matching ELF class, endianness, and section header range, then locates symbols either through `.symtab` or by translating System.map addresses into file offsets. It resolves `system_extra_cert`, `system_extra_cert_used`, and `system_certificate_list_size`, verifies the reserved area can hold the cert, avoids rewriting if identical, zero-fills unused space, adjusts certificate-list size by the delta, and writes the used byte count.

## Dependencies and Integration
It depends on ELF headers, `mmap(MAP_SHARED)`, writable build artifacts, optional System.map, and the kernel link reserving the three symbols. It integrates with certificate insertion flows after kernel image linking.

## Risks and Test Signals
Risks include host/target ELF class mismatch for cross builds, unchecked pointer arithmetic over malformed ELF files, symbol size inference from System.map, and mutating `vmlinux` in place. Test signals include symbol-resolution logs, rejection of oversized certs, idempotent reinsertion, boot-time trust of the inserted cert, and successful fallback when `.symtab` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/insert-sys-cert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/install.sh -->
# sources/distributed-fs/ceph-client/scripts/install.sh

## Purpose
Provides common kernel install dispatch logic for architectures that delegate installation to user or arch-specific scripts.

## APIs, Control Flow, and State
The shell script requires `KBUILD_IMAGE` and `System.map` to exist, creates `INSTALL_PATH` if set and missing, then searches executable install scripts in `${HOME}/bin/${INSTALLKERNEL}`, `/sbin/${INSTALLKERNEL}`, `${srctree}/arch/${SRCARCH}/install.sh`, and `${srctree}/arch/${SRCARCH}/boot/install.sh`. The first executable script is `exec`ed with `KERNELRELEASE`, image, `System.map`, and install path. If none are found, it exits with an error.

## Dependencies and Integration
It depends on kbuild environment variables and external installkernel-compatible scripts. It has no persistent state beyond creating the install directory.

## Risks and Test Signals
Risks include missing environment variables, custom scripts with incompatible semantics, and no fallback copy behavior. Test signals are `make install` after a build, correct argument order, and clear failure when artifacts or scripts are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/Makefile -->
# sources/distributed-fs/ceph-client/scripts/ipe/Makefile

## Purpose
Registers the IPE scripts subdirectory for host build traversal.

## APIs, Control Flow, and State
The Makefile contains `subdir-y := polgen`, causing kbuild to descend into `scripts/ipe/polgen`. It has no runtime behavior or mutable state.

## Dependencies and Integration
It depends on kbuild subdir processing and integrates the IPE policy generator into the scripts host-tool build.

## Risks and Test Signals
The only practical risk is accidentally omitting `polgen` from host builds. Test signals are `scripts/ipe/polgen/polgen` being built when the scripts tree is processed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/polgen/Makefile -->
# sources/distributed-fs/ceph-client/scripts/ipe/polgen/Makefile

## Purpose
Defines the IPE boot policy generator as an always-built host program.

## APIs, Control Flow, and State
The Makefile sets `hostprogs-always-y := polgen` and adds host extra include paths for kernel and UAPI headers. It has no runtime state.

## Dependencies and Integration
It depends on kbuild host program rules and includes from `$(srctree)/include` and `$(srctree)/include/uapi`, matching the generated C output from `polgen.c`.

## Risks and Test Signals
Risks are limited to missing include paths or the host tool not being built when IPE build rules need it. Test signals are successful host build and generated boot policy C compiling against included headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/polgen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/polgen/polgen.c -->
# sources/distributed-fs/ceph-client/scripts/ipe/polgen/polgen.c

## Purpose
Converts an optional plaintext IPE policy file into a generated C source file containing `const char *const ipe_boot_policy`.

## APIs, Control Flow, and State
`main()` requires an output path and optionally a policy input path. `policy_to_buffer()` opens the input, measures it with `fseek`/`ftell`, allocates an exact-size buffer, reads the file, and returns buffer plus length. `write_boot_policy()` writes a generated C file, includes `<linux/stddef.h>`, declares and defines `ipe_boot_policy`, emits `NULL` when no policy is supplied, or emits an escaped string literal. Escaping handles quotes, backslashes, tabs, question marks, and newlines by splitting the string across lines.

## Dependencies and Integration
It depends on libc file APIs and kernel headers for the generated C include. It integrates with IPE build logic that compiles the generated boot policy into the kernel.

## Risks and Test Signals
Risks include `ftell()` errors not being separately checked, text-mode I/O, partial-read failure returning `-1`, and generated C invalidity if unusual bytes are present. Test signals are successful generation for empty and non-empty policies, compilation of generated C, and byte-for-byte policy recovery from the escaped literal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ipe/polgen/polgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/jobserver-exec -->
# sources/distributed-fs/ceph-client/scripts/jobserver-exec

## Purpose
Runs a subprocess after reserving all available GNU make jobserver tokens and passes the reserved capacity via `PARALLELISM`.

## APIs, Control Flow, and State
The Python CLI expects `command [args ...]`. It prepends `../tools/lib/python` relative to the script location to `sys.path`, imports `JobserverExec`, and uses it as a context manager. Inside the context, `jobserver.run(sys.argv[1:])` executes the requested command. The context manager owns token acquisition/release and environment setup; this wrapper stores no state itself.

## Dependencies and Integration
It depends on Python 3, the kernel `tools/lib/python/jobserver.py` implementation, GNU make jobserver file descriptors/environment, and the child command honoring `PARALLELISM`.

## Risks and Test Signals
Risks include incorrect relative library paths, running outside make without jobserver metadata, or child commands ignoring the variable. Test signals are child execution under parallel make, no token leaks after failures, and fallback behavior from `JobserverExec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/jobserver-exec -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kallsyms.c -->
# sources/distributed-fs/ceph-client/scripts/kallsyms.c

## Purpose
Converts a linker map into assembly data tables used by the kernel `kallsyms` runtime for compressed symbol lookup.

## APIs, Control Flow, and State
`main()` parses `--all-symbols` and `--pc-relative`, reads the map with `read_map()`, prunes invalid symbols with `shrink_table()`, sorts by address, optimizes the token table, and writes assembly. `read_symbol()` parses `addr type name`, ignores undefined/debug/most absolute symbols, tracks text/inittext ranges, and stores type plus name in `struct sym_entry`. `symbol_valid()` filters to text ranges unless all symbols are requested, preserving `__start_`/`__stop_`. Compression counts two-byte token profit, inserts real byte codes, repeatedly selects profitable tokens, rewrites symbols, and emits compressed names, markers, token tables, offsets, and name-order sequence tables.

## Dependencies and Integration
It depends on libc, `xalloc.h`, linker map format, kernel symbol range conventions, and assembly syntax expected by the kernel build. Persistent output is generated assembly on stdout.

## Risks and Test Signals
Risks include map format drift, symbol length limit mismatches with the kernel, address truncation when not PC-relative, relative offset overflow, and compression table regressions. Test signals are successful boot/runtime symbol lookup, stable table generation across kallsyms passes, and explicit failure on overlong symbols or out-of-range relative addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/Makefile -->
# sources/distributed-fs/ceph-client/scripts/kconfig/Makefile

## Purpose
Defines kbuild targets and host programs for all kernel configuration front ends and configuration maintenance modes.

## APIs, Control Flow, and State
The Makefile derives `Kconfig`, `KBUILD_DEFCONFIG`, default config search paths, warning environment variables, and unexports stray `CONFIG_`. It defines rules for `config`, `menuconfig`, `nconfig`, `gconfig`, and `xconfig`, maps simple targets to `conf` command-line modes, handles `localmodconfig/localyesconfig`, defconfig and config-fragment workflows, `tinyconfig`, `testconfig`, and help text. It declares common parser/config objects and host programs `conf`, `nconf`, `mconf`, `qconf`, and `gconf`, including generated parser/lexer dependencies, ncurses/lxdialog/Qt/GTK package probing files, moc generation, and clean files.

## Dependencies and Integration
It is central to top-level `make *config` flows and depends on kbuild macros, Perl, Python/pytest for tests, ncurses, Qt, GTK, flex/bison outputs, and arch config fragments.

## Risks and Test Signals
Risks include target/CLI drift with `conf.c`, stale generated dependency files, optional UI package detection failures, and architecture config-fragment ambiguity. Test signals are successful `make olddefconfig`, UI config targets, `make testconfig`, fragment merges, and accurate `make help` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/conf.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/conf.c

## Purpose
Implements the line-oriented `conf` frontend that reads Kconfig files, updates `.config`, generates auto configuration files, and supports noninteractive modes such as allnoconfig, randconfig, olddefconfig, and savedefconfig.

## APIs, Control Flow, and State
Global state tracks `input_mode`, indentation, tty echoing, sync mode, restart count, input line buffer, and current root menu. User interaction flows through `conf()`, `conf_sym()`, `conf_string()`, and `conf_choice()`, which prompt for visible symbols, strings, tristates, and choices. `check_conf()` detects unset changeable symbols and either lists/help-prints them or restarts configuration from the containing menu. Noninteractive helpers include `set_randconfig_seed()`, `randomize_choice_values()`, `conf_set_all_new_symbols()`, and `conf_rewrite_tristates()`. `main()` parses long modes, loads existing/default/allconfig inputs, applies mode-specific symbol values, checks dependency errors, writes `.config`, writes autoconf data for syncconfig, or saves minimal defconfig.

## Dependencies and Integration
It depends on Kconfig library headers (`internal.h`, `lkc.h`) and functions for menu traversal, symbol evaluation, config I/O, and dependency diagnostics. It is invoked by `scripts/kconfig/Makefile` and top-level kbuild targets.

## Risks and Test Signals
Risks include incorrect tty/non-tty prompting, random probability parsing errors, choice priority mishandling, accidental config rewrites during sync, and mode drift with Makefile targets. Test signals are Kconfig pytest coverage, `oldconfig` prompt behavior, deterministic `KCONFIG_SEED`, all*config output expectations, `KCONFIG_NOSILENTUPDATE` enforcement, and generated `include/config/auto.conf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/conf.c -->
