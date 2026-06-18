# Research Group subset-b-008337

This grouped report covers the ima-evm-utils checkpatch helper and the src Automake build manifest. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/scripts/checkpatch.pl -->
# sources/security-integrity/ima-evm-utils/scripts/checkpatch.pl

## Purpose
`checkpatch.pl` is a Perl patch and source-file style checker derived from the Linux kernel checkpatch script. It validates unified diffs, git commits, stdin patches, and optionally whole files against kernel coding-style, commit-message, metadata, licensing, macro, API, permission, and security-oriented conventions. It can also emit filtered diagnostics, list available diagnostic types, and create experimental mechanical fixes through `--fix` or `--fix-inplace`.

## Important APIs, Types, And Functions
The script is organized around global option/state variables, compiled regular-expression "types", diagnostic emitters, patch-context helpers, and one large `process()` pass. `help()` prints the CLI contract; `list_types()` introspects the script for message types; `load_docs()` reads verbose diagnostic explanations from `Documentation/dev-tools/checkpatch.rst`; `hash_save_array_words()` and `hash_show_words()` handle `--types` and `--ignore`; `build_types()` constructs the core C declaration regexes from type/modifier tables and optional typedef files.

Patch and source parsing helpers include `sanitise_line_reset()`, `sanitise_line()`, `get_quoted_string()`, `line_stats()`, `ctx_statement_block()`, `ctx_statement_full()`, `ctx_block_get()`, `ctx_locate_comment()`, `raw_line()`, `get_stat_real()`, and `get_stat_here()`. These functions hide comments and strings, track block/statement boundaries across diff hunks, and recover raw context for diagnostics.

Reporting and fixing are centralized in `show_type()`, `report()`, `ERROR()`, `WARN()`, `CHK()`, `fix_insert_line()`, `fix_delete_line()`, `fixup_current_range()`, and `fix_inserted_deleted_lines()`. Git/tree integration is handled by `top_of_kernel_tree()`, `git_is_single_file()`, `git_commit_info()`, `is_maintained_obsolete()`, `is_SPDX_License_valid()`, `seed_camelcase_file()`, and `seed_camelcase_includes()`.

## Control Flow
Startup initializes defaults, reads `.checkpatch.conf` from the current directory, home directory, or `.scripts`, normalizes `--color`, parses options with `Getopt::Long`, validates incompatible modes, loads verbose docs and diagnostic filters, enforces a minimum Perl version unless overridden, and resolves the kernel tree root unless `--no-tree` is used. It then builds type regexes, loads local spelling data, optionally loads codespell and const-struct dictionaries, and expands `--git` revision/range expressions into individual non-merge commits.

For each input, the script chooses an input stream: `git format-patch` for `--git`, `diff -u /dev/null` for `--file` or recognized tracked single files, stdin for `-`, or direct patch-file open otherwise. It records raw lines, sets a display name, and invokes `process($filename)`. After each file/commit it resets per-input arrays, fix queues, file-local inferred types/modifiers, and restores file mode state.

`process()` first pre-scans raw lines into sanitized lines, tracking hunk line numbers, comment state, setup-documentation snippets, and a parallel fixed-output array when fixing is enabled. The main scan then walks each line, updating real file and line numbers from diff metadata, detecting commit-log and patch boundaries, maintaining function context, and emitting diagnostics. It initially handles patch metadata and commit-message checks, then hunk-level checks, then narrows by file extension into generic source, C/Perl/device-tree, and C-specific rule sets. At the end it reports missing unified-diff shape, missing signoffs, missing `Fixes:` tags, summaries, cleaner hints, and optional experimental fixed output.

## State And Persistence Behavior
Most state is process-local global state rather than persistent application data. Key persistent side effects are optional: `seed_camelcase_includes()` writes `.checkpatch-camelcase.git.<commit>` or `.checkpatch-camelcase.date.<timestamp>` caches in the current directory and removes old `.checkpatch-camelcase.*` files; `--fix` writes `<input>.EXPERIMENTAL-checkpatch-fixes`; `--fix-inplace` overwrites the input file. The script also reads `.checkpatch.conf`, `spelling.txt`, `const_structs.checkpatch`, optional codespell dictionaries, optional typedef files, kernel docs, git history, `MAINTAINERS`, SPDX tooling, and devicetree binding files.

Within one checked input, mutable arrays `@rawlines`, `@lines`, `@fixed`, `@fixed_inserted`, and `@fixed_deleted` carry the original, sanitized, and proposed fixed versions. Counters track errors, warnings, checks, and checked lines. Commit-message state tracks signoff presence, author/signoff match class, `Fixes:` presence, revert status, possible stack traces, mail headers, and charset concerns. Source-analysis state tracks real file, real line, hunk count, previous/stashed lines, inferred file-local typedefs/modifiers, comments, function context, suppressions, and value annotations.

## Dependencies And Integration Points
The script depends on core Perl modules `strict`, `warnings`, `POSIX`, `File::Basename`, `Cwd`, `Term::ANSIColor`, `Encode`, and `Getopt::Long`. It integrates heavily with external tools and tree layout: `git` for commit expansion, file lookup, and commit title resolution; `diff` for whole-file mode; `find` and `grep` for include and devicetree checks; `python3`, `codespell_lib`, and `scripts/spdxcheck.py` for optional dictionaries and SPDX validation; `scripts/get_maintainer.pl` for obsolete-maintainer checks; and kernel directories such as `include`, `Documentation/devicetree/bindings`, `LICENSES`, and `MAINTAINERS`.

It is intended to be invoked from a Linux-kernel-like source tree, but `--no-tree` allows looser operation with reduced validation. In ima-evm-utils it likely serves as a vendored contributor/CI style checker rather than runtime code. The message-type filter API (`--types`, `--ignore`, `--show-types`, `--list-types`) provides integration points for targeted policy lanes and automated patch review.

## Risks And Edge Cases
The implementation is regex-driven and global-state-heavy, so false positives and false negatives are expected around complex C syntax, macros, generated code, Rust/device-tree edge cases, and incomplete patch context. Several helper regexes require Perl 5.10 features; `--ignore-perl-version` can continue with reduced safety but may trigger runtime failures. Tree-sensitive checks can misbehave when run outside a matching kernel tree, with stale git state, localized git output despite the language override, or missing helper files.

Fixing is explicitly risky. The script may rewrite spacing, signatures, comments, macros, conditionals, string fragments, allocation calls, permissions, and other constructs using regex substitutions, and it warns not to trust generated output. In-place fixes can overwrite user input. The camelcase cache writer deletes matching cache files in the working directory. Some external checks execute shell commands with paths or regex fragments from tree content, so robustness depends on trusted repository paths and ordinary kernel-style filenames.

## Test Signals
Strong signals come from running the script on representative patch fixtures with `--show-types`, filtered `--types`/`--ignore`, `--file`, stdin, and `--git` modes. Useful assertions include exit status changes on errors, exact diagnostic type counts, summary counts, detection of malformed patches, signoff/Fixes validation, SPDX and UTF-8 warnings, long-line and whitespace errors, macro and allocation API warnings, permission checks, and safe behavior when optional files or tools are absent. For fix paths, compare generated `.EXPERIMENTAL-checkpatch-fixes` hunks and adjusted hunk ranges against expected outputs, but also compile or re-run style checks because the script itself treats fixes as experimental.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/scripts/checkpatch.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/Makefile.am -->
# sources/security-integrity/ima-evm-utils/src/Makefile.am

## Purpose
`src/Makefile.am` is the Automake manifest for building ima-evm-utils' library and command-line tool from the `src` directory. It declares the installed `libimaevm.la` shared library, the `evmctl` binary, generated hash metadata sources, installed public headers, optional feature defines, TPM/TSS backend source selection, and cleanup/dist rules.

## Important APIs, Types, And Functions
The primary Automake targets are `lib_LTLIBRARIES = libimaevm.la`, `bin_PROGRAMS = evmctl`, and `include_HEADERS = imaevm.h`. The library source is `libimaevm.c` plus generated `hash_info.h` and `hash_info.c` listed in `nodist_libimaevm_la_SOURCES`. The binary sources are `evmctl.c` and `utils.c`, with one PCR backend selected from `pcr_tss.c`, `pcr_ibmtss.c`, or `pcr_tsspcrread.c`.

Important build variables include `libimaevm_la_CPPFLAGS`, `libimaevm_la_LDFLAGS`, `libimaevm_la_LIBADD`, `libimaevm_la_CFLAGS`, `evmctl_CPPFLAGS`, `evmctl_LDFLAGS`, `evmctl_LDADD`, `evmctl_CFLAGS`, `AM_CPPFLAGS`, `BUILT_SOURCES`, `EXTRA_DIST`, `CLEANFILES`, and `DISTCLEANFILES`. Conditional Automake blocks consume configuration symbols such as `CONFIG_SIGV1`, `CONFIG_IMA_EVM_ENGINE`, `CONFIG_IMA_EVM_PROVIDER`, `USE_PCRTSS`, and `USE_IBMTSS`.

## Control Flow
Automake translates this manifest into make rules. A normal build first generates `hash_info.h` and `hash_info.c` by running `hash_info.gen` and `hash_info.genc` with `$(KERNEL_HEADERS)`, then compiles `libimaevm.la` with OpenSSL/libcrypto flags and optional feature defines. It then compiles `evmctl` with libcrypto, keyutils, the local library, optional readline flags, and exactly one PCR/TSS source path depending on configured TSS support.

Feature conditionals append preprocessor defines to both the library and `evmctl` so that signature version 1, OpenSSL engine support, and OpenSSL provider support remain consistent between library code and the CLI. TPM conditionals choose Intel TSS, IBM TSS, or command-line PCR reader integration, and the IBM TSS branch also adds `-libmtss`.

## State And Persistence Behavior
The file itself persists no runtime state, but the generated build creates and removes generated sources. `hash_info.h` and `hash_info.c` are build products derived from kernel headers, while `hash_info.gen` and `hash_info.genc` are distributed helper scripts. `CLEANFILES` removes generated hash files and `tmp_hash_info.h`; `DISTCLEANFILES` defers additional cleanup to configure-time substitution. The shared library ABI is controlled through libtool `-version-info 5:0:0`, so changes here influence installed soname/version behavior.

## Dependencies And Integration Points
The build integrates with Autotools conditionals and substitutions produced by `configure.ac` or included m4 macros. External dependencies include OpenSSL/libcrypto through `$(LIBCRYPTO_CFLAGS)` and `$(LIBCRYPTO_LIBS)`, `keyutils` through `-lkeyutils`, optional readline through `$(LDFLAGS_READLINE)`, optional IBM TSS through `-libmtss`, optional Intel TSS source support, and kernel headers through `$(KERNEL_HEADERS)` for generated hash algorithm metadata. `AM_CPPFLAGS = -I$(top_srcdir) -include config.h` makes the project root and generated configuration header visible to all targets in this directory.

`include_HEADERS = imaevm.h` installs the public API header alongside `libimaevm.la`, while `evmctl_LDADD` links the CLI against the just-built library, keeping command behavior aligned with exported library implementation. Distribution integration is explicit: generated outputs are `nodist`, but generator scripts are included in `EXTRA_DIST`.

## Risks And Edge Cases
`BUILT_SOURCES = hash_info.h hash_info.h` lists `hash_info.h` twice and omits `hash_info.c`; if intentional build ordering is expected for `hash_info.c`, this duplicate may be a latent Automake mistake even though `nodist_libimaevm_la_SOURCES` can still force generation. Both generated files depend only on `Makefile`, not the generator scripts or `$(KERNEL_HEADERS)`, so changes to kernel headers or generator scripts may not automatically regenerate outputs unless another dependency path exists. The generator commands use `$(srcdir)/...`, which is good for out-of-tree builds, but generated outputs land in the build directory and must be found correctly by include paths.

The TSS selection is mutually exclusive through nested conditionals, so a configuration with both `USE_PCRTSS` and `USE_IBMTSS` selects Intel TSS and ignores IBM TSS. The IBM link flag spelling `-libmtss` assumes the linker library name and platform conventions are correct. ABI version `5:0:0` requires deliberate maintenance when public library interfaces change; incorrect version-info can break downstream packaging expectations.

## Test Signals
Build-system signals include `autoreconf`/`configure` success across feature combinations, `make V=1` showing expected feature defines, generated `hash_info.h` and `hash_info.c` creation from selected kernel headers, successful `make distcheck`, and clean removal of generated files through `make clean` and `make distclean`. Matrix builds should cover default PCR command backend, `USE_PCRTSS`, `USE_IBMTSS`, `CONFIG_SIGV1`, engine support, provider support, and out-of-tree builds. Runtime smoke tests should confirm `evmctl` links against the local `libimaevm.la` and resolves libcrypto, keyutils, and optional TSS symbols.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/Makefile.am -->
