# subset-b-006326 Research

Grouped code research for `sources/distributed-fs/ceph-client/scripts`. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkkconfigsymbols.py -->
# sources/distributed-fs/ceph-client/scripts/checkkconfigsymbols.py

## Purpose
`checkkconfigsymbols.py` is a repository scanner for Kconfig hygiene. It finds Kconfig symbols that are referenced from source files or Kconfig expressions but are not defined by any `config` or `menuconfig` entry in the current Git tree, or in a selected commit/range. It also supports similarity lookup for a single symbol and optional history lookup for commits that mention a newly undefined symbol.

## Important APIs, Types, And Functions
The script is command-line oriented rather than import-oriented. `parse_options()` defines the user interface: `--commit`, `--diff`, `--find`, `--ignore`, `--sim`, `--force`, and `--no-color`. `print_undefined_symbols()` is the main driver and performs either current-tree scanning or commit/range comparison. `check_symbols()` and `check_symbols_helper()` coordinate multiprocessing over source and Kconfig files and return `(undefined, defined_symbols)`.

Parsing is split by file type. `parse_source_file()` extracts `CONFIG_FOO` and `DCONFIG_FOO` style references from non-Kconfig files with `REGEX_SOURCE_SYMBOL`. `parse_kconfig_file()` extracts definitions with `REGEX_KCONFIG_DEF` and references from `if`, `select`, `imply`, `depends on`, and `default ... if ...` statements with `REGEX_KCONFIG_STMT`. `find_sims()` uses `difflib.get_close_matches()` against the defined symbol set. Git helpers include `get_files()`, `tree_is_dirty()`, `get_head()`, `reset()`, `find_commits()`, and the common `execute()` wrapper.

## Control Flow
Execution starts in `main()`, which calls `print_undefined_symbols()` and handles broken stdout pipes cleanly. Option parsing rejects simultaneous `--commit` and `--diff`, validates `commit1..commit2` syntax, refuses destructive Git reset operations on a dirty tree unless `--force` is passed, and prevents `--commit HEAD...` usage because that mode compares a commit against its parent by resetting the tree.

For a plain current-tree run, `check_symbols()` creates a `multiprocessing.Pool`, then `check_symbols_helper()` enumerates `git ls-files`, partitions Kconfig files from all other source files, parses both groups in parallel, builds an inverse `symbol -> referencing files` map, filters known placeholders and `_MODULE` aliases, and returns undefined symbols. For `--commit` and `--diff`, the driver saves the current HEAD, resets to the earlier revision to collect baseline undefined symbols, resets to the later revision to collect candidate undefined symbols and definitions, reports symbols or referencing files newly introduced in the later tree, and resets back to the original HEAD. When `--find` is combined with `--diff`, it runs `git log -G <symbol>` over the diff range for likely introducing commits.

## State And Persistence
The script keeps all scan data in memory: dictionaries for defined and undefined symbols, file-to-reference maps, and sets for inverse lookup. It does not write cache files or persistent reports. The major persistent side effect is in commit/range modes: `reset()` executes `git reset --hard <commit>`, mutating the worktree and index. The dirty-tree guard reduces the risk but `--force` intentionally bypasses it. Color state is held in the global `COLOR`.

## Dependencies And Integration Points
The script depends on Python standard library modules: `argparse`, `difflib`, `os`, `re`, `signal`, `subprocess`, `sys`, and `multiprocessing`. It integrates tightly with Git through `git ls-files`, `git status --porcelain`, `git rev-parse HEAD`, `git reset --hard`, and `git log -G`. It assumes it is executed inside the Linux-style source tree represented by the Ceph client checkout, with Kconfig files named `Kconfig`, `Kconfig.*`, or similar.

## Risks And Edge Cases
The most important operational risk is destructive checkout behavior in `--commit` and `--diff`; interrupted runs after a reset can leave the worktree at an older revision. The scanner also assumes all relevant files are tracked by Git and ignores directories, files containing `.git`, `ChangeLog`, `.log`, and paths under `tools/`, so generated or untracked references are invisible. Kconfig parsing is regex based and does not fully parse nested Kconfig grammar, continuation edge cases, quoted expressions beyond simple removal, or every possible symbol-producing construct. `partition(lst, size)` can create empty worker chunks when there are fewer files than CPUs, which is safe but wasteful. Multiprocessing pools are explicitly terminated on `KeyboardInterrupt` for full checks, but `find_sims()` does not wrap its pool in the same interrupt cleanup path.

## Test Signals
Useful validation starts with `--sim KNOWN_SYMBOL` to confirm Kconfig definition extraction without tree mutation. Current-tree scans should be run from a clean tree and compared against known intentionally undefined placeholders. Commit/range modes need tests on disposable clones to verify reset-back-to-HEAD behavior and the dirty-tree guard. Parser tests should cover `CONFIG_FOO`, `DCONFIG_FOO`, Kconfig `depends on`, `select`, `imply`, `default ... if`, multiline continuations, numeric literals, quoted strings, `_MODULE` suffix handling, ignored paths, and invalid ignore regex handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkkconfigsymbols.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkpatch.pl -->
# sources/distributed-fs/ceph-client/scripts/checkpatch.pl

## Purpose
`checkpatch.pl` is the Linux kernel patch and source-file style checker. It reads unified diffs, Git commits, stdin patches, or whole source files, reports style and process defects as errors, warnings, or strict checks, and can optionally write experimental mechanical fixes. In this Ceph client source tree it provides the kernel-derived review gate for commit message conventions, patch structure, SPDX tags, Kconfig help, MAINTAINERS formatting, C style, macro style, allocation patterns, logging, locking annotations, Device Tree bindings, permissions, and deprecated API usage.

## Important APIs, Types, And Functions
The script is a Perl CLI tool with a large global grammar. Options are parsed with `Getopt::Long` and include `--patch`, `--file`, `--git`, `--strict`, `--types`, `--ignore`, `--show-types`, `--list-types`, `--fix`, `--fix-inplace`, `--root`, `--no-tree`, `--codespell`, `--typedefsfile`, `--color`, and `--kconfig-prefix`. `help()`, `list_types()`, and `load_docs()` implement discovery and verbose descriptions.

The type grammar is built from global regexes such as `$Ident`, `$Storage`, `$Sparse`, `$Attribute`, `$Type`, `$Declare`, `$Constant`, `$Operators`, `$Lval`, `$balanced_parens`, and `$FuncArg`. `build_types()` regenerates those regexes after file-local typedef or modifier discoveries. Input and context helpers include `sanitise_line()`, `annotate_values()`, `ctx_statement_block()`, `ctx_statement_full()`, `ctx_block_get()`, `raw_line()`, `get_stat_real()`, `get_stat_here()`, `line_stats()`, `get_quoted_string()`, and `ctx_has_comment()`.

Report emission is centralized in `report()`, `ERROR()`, `WARN()`, and `CHK()`, with filtering through `show_type()`. Fix support is handled by `fix_insert_line()`, `fix_delete_line()`, `fix_inserted_deleted_lines()`, and direct edits to the `@fixed` line buffer. The main checker is `process($filename)`, which owns almost all patch scanning and report generation.

## Control Flow
Startup discovers the script directory, loads `.checkpatch.conf` from the current directory, home directory, or `.scripts`, expands configuration arguments into `@ARGV`, resolves spelling dictionaries, parses options, validates mutually exclusive modes, sets color and strict-check behavior, verifies the kernel tree root unless `--no-tree` is used, loads optional docs, type dictionaries, const-struct lists, and spelling data, then normalizes input filenames. In `--git` mode, revision expressions are expanded to non-merge commits with `git log`, and each commit is later converted to a patch with `git format-patch -M --stdout -1`.

For each input, the script opens either a Git-generated patch, a synthetic `diff -u /dev/null <file>` for `--file`, stdin, or the named patch file. It stores all raw lines, calls `process()`, then clears per-input arrays and file-local type/modifier discoveries.

`process()` performs a first pass that sanitizes strings and comments, tracks hunk real line numbers, detects whether a hunk begins inside a block comment, stores a parallel `@lines` view with comments and strings masked, and collects `__setup` documentation snippets. The second pass walks each line with state for the current real file, real line, patch header versus commit log versus hunk body, current function, signoffs, Fixes tags, namespace-like file context, comment state, and suppression maps. It checks commit metadata before source hunks, then file-level and line-level rules. For C-like source hunks, it gathers full statements and blocks with context helpers, annotates operator/value roles, and runs hundreds of pattern checks against only added lines where appropriate.

After scanning, `process()` applies final patch-level checks: unified-diff detection, missing `Fixes:` suggestions, missing or mismatched signoffs, summary output, optional notes, and optional experimental fix-file writing. The return value is whether the input was clean; the top-level loop converts any dirty input into process exit status `1`.

## State And Persistence
Runtime state is intentionally global and line-oriented. `@rawlines`, `@lines`, `@fixed`, `@fixed_inserted`, and `@fixed_deleted` persist for one input file or commit. `%use_type` and `%ignore_type` persist across all inputs and govern message filtering. `%camelcase` and `%maintained_status` cache expensive include and maintainer lookups. `$prefix`, `$vname`, `$check`, `$file`, `$root`, `$gitroot`, and color/settings globals alter reporting behavior across helpers.

Persistent filesystem effects are opt-in. `--fix` writes `<input>.EXPERIMENTAL-checkpatch-fixes`; `--fix-inplace` overwrites the source or patch path. CamelCase seeding may create `.checkpatch-camelcase.git.<commit>` or `.checkpatch-camelcase.date.<timestamp>` cache files in the working directory and removes older `.checkpatch-camelcase.*` caches. The script also reads `.checkpatch.conf`, `spelling.txt`, optional codespell dictionaries, `const_structs.checkpatch`, `Documentation/dev-tools/checkpatch.rst`, and optional typedef files.

## Dependencies And Integration Points
Core Perl dependencies are `POSIX`, `File::Basename`, `Cwd`, `Term::ANSIColor`, `Encode`, and `Getopt::Long`. Repository integration is deep: tree validation expects kernel top-level files and directories, Git commands provide commit expansion and commit-title lookup, `scripts/get_maintainer.pl` marks obsolete maintained files, `scripts/spdxcheck.py` validates SPDX identifiers, `Documentation/dev-tools/checkpatch.rst` provides verbose message text, and `Documentation/devicetree/bindings` plus `vendor-prefixes.yaml` are searched for compatible strings. External optional integration includes `codespell` dictionaries and system tools such as `grep`, `find`, and `diff`.

Within the source tree, `checkpatch.pl` is normally invoked by developers, CI, or pre-submit scripts rather than imported. Its message type system is part of that integration surface: `--list-types`, `--types`, `--ignore`, `--show-types`, and `--test-only` let callers gate only selected classes.

## Risks And Edge Cases
The checker is intentionally heuristic. Many rules use regexes over sanitized diff lines, so false positives and false negatives are expected around complex macros, nested declarations, preprocessor conditionals, comments that resemble code, multiline strings, and incomplete patch context. Several checks depend on a valid kernel tree; running with `--no-tree` disables or weakens SPDX validation, maintainer status, Device Tree compatible lookup, include substitution checks, and some cache seeding.

Fix mode is explicitly risky: it performs local string substitutions based on the same heuristics, writes experimental output, and may be wrong for multiline constructs or unusual context. `--fix-inplace` is especially high impact because it overwrites the input. The script can run external Git and helper commands in backticks; unusual locales are partly handled by forcing Git language, but command availability and repository shape still affect results. Performance can degrade on large patches because statement extraction, spelling dictionaries, Device Tree greps, maintainer lookups, and CamelCase include scans are repeated across many lines, although several caches reduce repeated work.

## Test Signals
Basic smoke tests are `perl scripts/checkpatch.pl --no-tree --list-types --no-color`, stdin patch checking, `--file` checking on a small source file, and `--git` checking on a disposable repository commit. Message filtering should be validated with `--types`, `--ignore`, `--show-types`, `--strict`, and `--test-only`. Fix-mode tests should compare generated `.EXPERIMENTAL-checkpatch-fixes` files for whitespace, simple spacing, signature, SPDX, and macro cases, without assuming semantic correctness.

Higher-value regression tests should cover commit-message rules, signoff parsing including encoded names and stable addresses, Fixes tag formatting with valid and invalid Git IDs, corrupted patch detection, UTF-8 and DOS line endings, Kconfig help length, MAINTAINERS entry ordering, SPDX placement by file type, line length exceptions, operator spacing, open-brace rules, macro argument reuse and precedence, do-while macro checks, logging format specifiers, allocation-size recommendations, Device Tree compatible/vendor lookup, permission octal checks, `MODULE_LICENSE`, missing sentinel tables, and optional tree-dependent checks with and without `--no-tree`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkpatch.pl -->
