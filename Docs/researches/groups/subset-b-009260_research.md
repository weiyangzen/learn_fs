# Research Group: subset-b-009260

This grouped report covers the requested kdevops scripts and embedded Kconfig sources. Each file section is bounded by the required reconciliation markers and preserves the source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_maintainer.pl -->
# sources/test-tools/kdevops/scripts/get_maintainer.pl

## Purpose
This Perl script is the Linux `get_maintainer.pl` helper carried into kdevops. It maps a patch or a `-f` file/directory argument to maintainers, reviewers, mailing lists, status, SCM, web, bug, and subsystem information from `MAINTAINERS`, optionally augmented with git or Mercurial history, blame data, `Fixes:` commit signers, keywords, `.mailmap`, and file-local email extraction.

## Important APIs, Types, And Functions
The script is procedural, with global option/state variables set by `Getopt::Long`. The central API is `get_maintainers()`, fed by `@files`, `@fixes`, `@range`, parsed `@typevalue`, and keyword state. `read_all_maintainer_files()` discovers one or more MAINTAINERS files, while `read_maintainer_file()` records raw section lines and converts `F:`/`X:` glob-like patterns to regexes. Matching is handled by `file_match_pattern()`, `find_starting_index()`, `find_ending_index()`, `add_categories()`, `push_email_addresses()`, and role helpers. VCS integration is abstracted through `%VCS_cmds_git` and `%VCS_cmds_hg`, with `vcs_exists()`, `vcs_file_signoffs()`, `vcs_file_blame()`, `vcs_find_signers()`, and `vcs_assign()` doing command dispatch and ranking.

## Control Flow
Startup loads optional `.get_maintainer.conf` and `.get_maintainer.ignore`, parses options, enforces mode constraints, verifies the kernel tree unless `--no-tree`, and reads MAINTAINERS data. Arguments are either treated as files/directories under `-f` or parsed as patches; patch parsing extracts changed filenames, hunk ranges for blame, `Fixes:` hashes, and keyword hits. `get_maintainers()` scans every MAINTAINERS section for matching `F:`, `X:`, and `N:` rules, records exact pattern matches, adds selected categories, scans file-local addresses, adds keyword matches, then optionally adds history/blame/fixes-derived identities. Interactive mode loops over a numbered list and can toggle sources or rerun discovery. Output is role-annotated or plain, multiline or separator-joined.

## State And Persistence
Persistent inputs are `.get_maintainer.conf`, `.get_maintainer.ignore`, `.mailmap`, MAINTAINERS files, and VCS history. Runtime state is global and reset inside `get_maintainers()` before each run. There is no durable output file; results are printed to stdout and warnings to stderr. Self-test mode caches MAINTAINERS line metadata in `@self_test_info` and probes links/SCM endpoints.

## Dependencies And Integration Points
It depends on Perl core modules `Getopt::Long`, `Cwd`, `File::Find`, `File::Spec::Functions`, external `git`, `hg`, and `wget` for optional probes, and the Linux MAINTAINERS schema. It is intended for mail tooling such as `git send-email --cc-cmd`, but `--roles`/`--rolestats` may break consumers expecting bare addresses.

## Risks And Test Signals
VCS commands are built as shell strings with interpolated filenames and commits; quoting depends on upstream assumptions and unusual paths can be risky. Regex-converted MAINTAINERS patterns are powerful but can overmatch or under-match. Network self-tests are slow and flaky. `--git-blame` is explicitly expensive and can surface stale owners. Test signals include `--self-test`, known MAINTAINERS pattern fixtures, mailmap cases, patch parsing with renames/hunks/Fixes, and running with/without git and hg repositories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_maintainer.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_target_arch.sh -->
# sources/test-tools/kdevops/scripts/get_target_arch.sh

## Purpose
This shell helper maps the host machine architecture from `uname -m` to a kdevops target architecture token. It currently emits `TARGET_ARCH_X86_64`, `TARGET_ARCH_ARM64`, or `TARGET_ARCH_PPC64LE`.

## Important APIs, Types, And Functions
There are no functions. The whole interface is the script output on stdout. The `case` statement recognizes `x86_64`, `aarch64`, and `ppc64le`.

## Control Flow
The script invokes `uname -m`, matches the result, and echoes the corresponding target token. Unsupported architectures fall through silently and exit with the shell's default successful status because there is no default case.

## State And Persistence
It has no persistent state and reads no files. Its only dependency is the current kernel-reported machine architecture.

## Dependencies And Integration Points
Callers likely consume the token in Make, CI, or GitHub Actions logic to pick kdevops target configuration. It assumes GNU/POSIX shell basics and `/bin/bash`.

## Risks And Test Signals
The silent success on unsupported architectures is the main risk because downstream code may receive an empty value without an immediate failure. Tests should cover each recognized architecture by stubbing `uname`, plus an unknown architecture to decide whether empty output is intended or should become an explicit error.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/get_target_arch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/github_output.sh -->
# sources/test-tools/kdevops/scripts/github_output.sh

## Purpose
This GitHub Actions helper appends a `key=value` pair to the path in `$GITHUB_OUTPUT`, which is the modern workflow mechanism for setting step outputs.

## Important APIs, Types, And Functions
There are no functions. It expects exactly two positional arguments: `key="$1"` and `value="$2"`. It runs with `set -euxo pipefail`, so missing arguments, unset `GITHUB_OUTPUT`, and failed writes abort.

## Control Flow
The script assigns the first two positional parameters and appends a single line using `echo "$key=$value" >> "$GITHUB_OUTPUT"`.

## State And Persistence
The persistent side effect is appending to the file named by `GITHUB_OUTPUT`. It does not validate or sanitize the key or value and does not handle multiline GitHub output syntax.

## Dependencies And Integration Points
It integrates directly with GitHub Actions. The surrounding workflow must set `GITHUB_OUTPUT`, pass safe single-line values, and ensure the output file is writable.

## Risks And Test Signals
Values containing newlines, percent-like content, or names that collide with other step outputs can create ambiguous workflow output. `set -x` may echo sensitive values in CI logs. Tests should run with a temporary `GITHUB_OUTPUT`, verify append semantics, and cover missing arguments/unset environment behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/github_output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/honey-badger.py -->
# sources/test-tools/kdevops/scripts/honey-badger.py

## Purpose
This Python tool discovers Ubuntu mainline kernel builds, lists recent stable versions, downloads the image/modules/headers `.deb` packages, and installs or extracts them. It supports Debian systems through `dpkg` and non-Debian or alternate roots through manual `ar` plus tar extraction.

## Important APIs, Types, And Functions
`KERNEL_PPA_URL`, `ARCH`, and `KERNEL_DIR` define the source and local cache. `is_dpkg_installed()` probes `dpkg`. `parse_version()` parses `vX.Y[.Z][-rcN]` into a sortable tuple. `get_kernel_versions()` fetches the index with `requests`, parses links via BeautifulSoup, sorts them, and calls `group_versions()` to group by major/minor. `verify_kernel_files()` checks whether a version has both `linux-image-unsigned` and `linux-modules` packages. `download_and_install()` downloads matching `.deb` files and delegates to `install_kernel_packages()`. `extract_deb()` manually unpacks the `ar` archive and extracts `data.tar*`.

## Control Flow
`main()` parses CLI options, discovers grouped versions, takes the latest candidate per major/minor group until `--count` valid versions are found, lists them if `--list`, installs a supplied `--use-file` package if requested, or downloads `linux-modules`, `linux-image-unsigned`, and `linux-headers` packages for each valid version. `--dest` is passed to manual extraction.

## State And Persistence
Network state comes from `https://kernel.ubuntu.com/mainline/`. Downloaded packages are persisted in `/tmp/kernels`. Installation mutates the host through `sudo dpkg -i` or writes extracted package payloads into `dest`, defaulting to `/`. Temporary manual extraction directories are removed.

## Dependencies And Integration Points
It requires `requests`, `bs4`, `ar`, `tarfile`, filesystem write access, and optionally `sudo dpkg`. It integrates with kdevops workflows that need quickly available stable kernels for testing.

## Risks And Test Signals
The `--use-ar` default is set to `dpkg_installed`, despite the help text saying "Do not use dpkg even if present", which means systems with dpkg default to manual extraction rather than `dpkg`; that is worth verifying. `tar.extractall()` extracts archive paths without filtering, so untrusted `.deb` content is a path traversal risk. Downloads use `r.content`, loading entire packages into memory. `--dest` can be `None` in the `--use-file` path, which later reaches tar extraction as the extraction path. Test with mocked HTTP indexes, temporary kernel directories, a fake `.deb`, and both dpkg/manual code paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/honey-badger.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/infer_last_stable_kernel.sh -->
# sources/test-tools/kdevops/scripts/infer_last_stable_kernel.sh

## Purpose
This shell helper infers a conservative recent stable Linux kernel tag from a local git object directory, intended as a default kernel reference for A/B testing.

## Important APIs, Types, And Functions
The script takes one optional argument, `GIT_TREE`, defaulting to `/mirror/linux.git`. It uses `git --git-dir="$GIT_TREE" tag --list`, `grep -v -- '-rc'`, `sort -V`, and `tail -2 | head -1`.

## Control Flow
If the git tree directory is missing, it emits `v6.12`. Otherwise it lists stable `v6.*` tags, excludes release candidates, sorts by version, and deliberately selects the second-to-last stable tag. If none exists, it repeats the process for `v5.*`. If still empty, it emits `v6.12`.

## State And Persistence
It reads only the local git repository metadata. It writes no files and prints the selected tag to stdout.

## Dependencies And Integration Points
It depends on `git`, `grep`, `sort -V`, `tail`, and `head`. Consumers likely use the emitted tag as a kdevops kernel version default.

## Risks And Test Signals
Choosing `tail -2 | head -1` means "previous stable", not the latest stable, which matches a conservative testing stance but conflicts with the file name if interpreted literally. Lightweight/malformed tags or an empty mirror can force fallback. Tests should create temporary bare repositories with v5/v6 and rc tags and assert the second-latest stable behavior and fallbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/infer_last_stable_kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/Makefile -->
# sources/test-tools/kdevops/scripts/kconfig/Makefile

## Purpose
This simplified Makefile builds the embedded standalone Kconfig tools (`conf`, `mconf`, `nconf`) for subtree use in kdevops. It keeps local build rules small while using upstream-like Kconfig source files.

## Important APIs, Types, And Functions
`common-objs` lists shared lexer/parser/configuration objects. `lxdialog` collects ncurses dialog objects for `mconf`. Generated sources are `lexer.lex.c` from `lexer.l` using `flex` and `parser.tab.c/parser.tab.h` from `parser.y` using `bison`. `mconf-cfg.sh` and `nconf-cfg.sh` produce `*conf-cflags`, `*conf-libs`, and `*conf-bin` metadata through `cmd_conf_cfg`.

## Control Flow
The default `kconfig` target builds `conf`, `mconf`, and `nconf`. `conf` links common objects plus `conf.o`; `mconf` and `nconf` depend on discovered curses/menu flags and link their frontend-specific objects. `include $(CURDIR)/Kbuild.include` supplies helper macros such as `read-file` and `cmd`.

## State And Persistence
Build outputs include binaries, objects, generated parser/lexer sources, dependency files, and `*conf-*` flag files. `clean` removes those generated artifacts.

## Dependencies And Integration Points
The Makefile depends on a C compiler, `flex`, `bison`, pkg-config/curses discovery scripts, and the local Kconfig sources. It is the integration point that turns the source bundle into kdevops configuration frontends.

## Risks And Test Signals
The `clean-files += parser.tab.c parser.tab.h .lex.c` entry appears to miss `lexer.lex.c`, leaving a generated file behind. Builds can fail when ncurses discovery scripts cannot find packages or when `Kbuild.include` is missing. Test signals are `make clean`, `make conf`, `make mconf`, `make nconf`, and dependency rebuilds after touching `lexer.l` or `parser.y`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/array_size.h -->
# sources/test-tools/kdevops/scripts/kconfig/array_size.h

## Purpose
This header provides the standard `ARRAY_SIZE(arr)` macro for compile-time-ish array element counting.

## Important APIs, Types, And Functions
`ARRAY_SIZE(arr)` expands to `sizeof(arr) / sizeof((arr)[0])`.

## Control Flow
There is no runtime control flow; the macro is evaluated by the C compiler wherever used.

## State And Persistence
It has no state and no side effects.

## Dependencies And Integration Points
`hashtable.h` uses this macro for `HASH_SIZE(name)`. Any C file including the Kconfig utility headers can depend on it.

## Risks And Test Signals
The macro does not protect against pointer arguments, so passing a pointer returns a bogus size ratio. Compile tests should include a real array user such as `HASHTABLE_DEFINE` and avoid pointer misuse.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/array_size.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/checklist.c -->
# sources/test-tools/kdevops/scripts/kconfig/checklist.c

## Purpose
This file implements an ncurses checklist/radiolist dialog for the Kconfig menu frontend. It displays items maintained by the shared lxdialog item list and lets the user select exactly one item or request help.

## Important APIs, Types, And Functions
The exported API is `dialog_checklist(title, prompt, height, width, list_height)`. Internal helpers are `print_item()`, `print_arrows()`, and `print_buttons()`. It relies on global dialog theme state `dlg`, item-list functions such as `item_foreach()`, `item_set()`, `item_str()`, `item_is_tag()`, `item_set_selected()`, and ncurses `WINDOW` objects.

## Control Flow
The dialog selects an initial highlighted row from an item tagged `X` or an item already selected. On each resize it validates minimum terminal dimensions, centers a dialog, draws a bordered list subwindow, computes checkbox and item columns, scrolls to keep the selected choice visible, renders visible items, then enters a key loop. Arrow keys, `+`, `-`, and first-letter hotkeys move the highlight. Space, Enter, or `s` selects the current item; `h`/`?` returns the Help button; Tab and horizontal arrows switch buttons; ESC and resize are handled through common helpers.

## State And Persistence
State is in local `choice`, `scroll`, and `button` variables, plus static layout globals `list_width`, `check_x`, and `item_x`. The persistent side effect is updating the selected flag in the global item list. No files are touched.

## Dependencies And Integration Points
It integrates with `mconf` through `dialog.h` and `util.c` item-list and drawing utilities. Return values are button indices or key/error codes consumed by menuconfig logic.

## Risks And Test Signals
The file is similar to `lxdialog/checklist.c`, so duplicate maintenance is a risk. `malloc()` return values are unchecked. Long item strings are truncated; empty strings can still index `list_item[0]`. Curses tests should exercise resize, scrolling boundaries, hotkeys, tagged separators, selected item persistence, and too-small terminal returns.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/checklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/conf.c -->
# sources/test-tools/kdevops/scripts/kconfig/conf.c

## Purpose
`conf.c` is the line-oriented Kconfig frontend. It parses Kconfig files, reads existing configuration, applies one of many configuration modes, prompts or auto-answers for new symbols, checks dependency errors, and writes `.config` plus generated autoconf outputs when appropriate.

## Important APIs, Types, And Functions
The main exported entry is `main()`. `enum input_mode` defines modes including `oldaskconfig`, `syncconfig`, `oldconfig`, `allnoconfig`, `allyesconfig`, `allmodconfig`, `alldefconfig`, `randconfig`, `defconfig`, `savedefconfig`, `listnewconfig`, `helpnewconfig`, and tristate rewrite modes. Key helpers are `set_randconfig_seed()`, `randomize_choice_values()`, `conf_set_all_new_symbols()`, `conf_rewrite_tristates()`, `conf_askvalue()`, `conf_string()`, `conf_sym()`, `conf_choice()`, recursive `conf()`, and `check_conf()`.

## Control Flow
`main()` parses long options, calls `conf_parse()` on the Kconfig file, then reads input configuration according to mode. Auto modes may load `KCONFIG_ALLCONFIG` seed files. It exits on read warnings when `KCONFIG_WERROR` is active. It applies defaults, random values, or tristate rewrites; interactive modes recursively prompt visible menu entries and repeatedly call `check_conf()` until no newly changeable symbols remain. Finally it checks dependency errors, writes a savedefconfig or `.config`, and for sync/build modes writes `auto.conf`, `autoconf.h`, and Rust cfg outputs via `conf_write_autoconf()`.

## State And Persistence
Global state includes `input_mode`, `indent`, `tty_stdio`, `sync_kconfig`, `conf_cnt`, reusable input buffer `line`, and `rootEntry`. It mutates symbol user defaults and flags in the shared Kconfig symbol table. Persistent outputs are written by `confdata.c`; this file decides when to call those writers. Environment variables such as `KCONFIG_SEED`, `KCONFIG_PROBABILITY`, `KCONFIG_ALLCONFIG`, and `KCONFIG_NOSILENTUPDATE` influence behavior.

## Dependencies And Integration Points
It depends on `internal.h`, `lkc.h`, menu traversal APIs, symbol APIs, expression/dependency checks, and configuration persistence APIs. It is linked by the Kconfig Makefile into the `conf` binary and also built as a prerequisite for menu frontends.

## Risks And Test Signals
Random configuration depends on environment parsing and can exit on invalid probabilities. `oldaskconfig` and `oldconfig` behavior differs depending on TTY detection. `syncconfig` with `KCONFIG_NOSILENTUPDATE` refuses implicit changes. Test signals include each mode, choice randomization respecting `KCONFIG_ALLCONFIG`, dependency error fixtures, stdin prompt scripts, and file outputs for syncconfig.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/confdata.c -->
# sources/test-tools/kdevops/scripts/kconfig/confdata.c

## Purpose
`confdata.c` owns Kconfig configuration persistence. It reads `.config`-style files into symbol defaults, tracks whether configuration changed, writes normal and minimal configs, optionally writes YAML, and generates build-time autoconf files and dependency stamp files.

## Important APIs, Types, And Functions
Public functions include `conf_get_configname()`, `conf_read_simple()`, `conf_read()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, `conf_set_changed()`, `conf_get_changed()`, `conf_set_changed_callback()`, `conf_set_message_callback()`, and `conf_errors()`. Important internal helpers include `is_same()`, `make_parent_dir()`, `conf_set_sym_val()`, `getline_stripped()`, `escape_string_value()`, `__print_symbol()`, YAML helpers, `print_symbol_for_c()`, `print_symbol_for_rustccfg()`, `conf_touch_deps()`, and `__conf_write_autoconf()`.

## Control Flow
Reading starts with `conf_read_simple()`, which opens an explicit config or falls back to `KCONFIG_CONFIG` and `KCONFIG_DEFCONFIG_LIST`, clears prior defaults for the selected definition slot, then parses `CONFIG_FOO=value` and `# CONFIG_FOO is not set` lines. Unknown symbols either warn or touch dependency files when reading `auto.conf`. `conf_read()` calculates all symbols and marks changed when saved and calculated values differ. Writing `.config` creates a temp file unless `KCONFIG_OVERWRITECONFIG` is set, walks the menu tree in display order, writes headings and symbol values, compares with the existing file, renames `.old`, and clears changed state. Autoconf generation writes a `.cmd` depfile, touches changed include/config dependency files, calculates symbols, writes C header, Rust cfg, then writes `auto.conf` last.

## State And Persistence
Persistent paths are controlled by `KCONFIG_CONFIG`, `KCONFIG_AUTOCONFIG`, `KCONFIG_AUTOHEADER`, `KCONFIG_RUSTCCFG`, and `KCONFIG_YAMLCFG`. YAML all-symbol behavior comes from `KCONFIG_YAMLCFG_ALL`. The file uses global `autoconf_cmd`, warning counters, `conf_changed`, callbacks, and dependency path buffers. It mutates `sym->def[]`, `sym->flags`, and choice member ordering.

## Dependencies And Integration Points
It depends on POSIX file APIs, `mmap`, Kconfig symbols/menus, `xalloc`, `zconf_fopen()`, and string builders from `lkc.h`. `conf.c` and frontends call it to load, save, and sync generated configuration state.

## Risks And Test Signals
`is_same()` maps zero-length files without a special case, which can be platform-sensitive. YAML string output performs simple quoting and does not escape embedded quotes. `conf_name_to_yaml()` currently lowercases names but leaves underscores, despite a redundant branch. Atomicity relies on rename in the same filesystem. Tests should cover malformed configs, unknown symbols with warning envs, string escaping, YAML output, no-change detection, overwrite mode, autoconf ordering, and dependency touch behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/confdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/expr.c -->
# sources/test-tools/kdevops/scripts/kconfig/expr.c

## Purpose
`expr.c` implements Kconfig expression allocation, copying, freeing, normalization, simplification, comparison, evaluation, dependency queries, and printing. It is the dependency logic substrate for menus, symbols, visibility, reverse dependencies, and help output.

## Important APIs, Types, And Functions
Allocation APIs are `expr_alloc_symbol()`, `expr_alloc_one()`, `expr_alloc_two()`, `expr_alloc_comp()`, `expr_alloc_and()`, and `expr_alloc_or()`. Lifecycle APIs are `expr_copy()` and `expr_free()`. Simplification includes `expr_eliminate_eq()`, `expr_eliminate_dups()`, `expr_transform()`, `expr_join_or()`, `expr_join_and()`, and `expr_eliminate_yn()`. Query/evaluation APIs include `expr_eq()`, `expr_contains_symbol()`, `expr_depends_symbol()`, `expr_trans_compare()`, and `expr_calc_value()`. Printing APIs include `expr_print()`, `expr_fprint()`, `expr_gstr_print()`, and `expr_gstr_print_revdep()`.

## Control Flow
Expressions are binary trees with symbol and comparison leaves. Simplification recursively descends through `&&`/`||` levels, compares leaves, replaces common operands with constant `y` or `n`, removes constant identities, folds boolean comparisons, applies De Morgan transforms, and joins redundant tristate comparisons. Evaluation recursively calculates symbol values, applies tristate `AND`/`OR`/`NOT`, and compares numeric or string values for relation nodes. Printing walks the tree with precedence checks to insert parentheses and can annotate symbols with current values in `gstr` output.

## State And Persistence
The file has no durable persistence. It allocates heap expression nodes and uses global symbols such as `symbol_yes`, `symbol_mod`, and `symbol_no` from the symbol subsystem. A static `trans_count` controls repeated simplification loops and is saved/restored around recursive equality checks.

## Dependencies And Integration Points
It depends on `lkc.h`, `xalloc`, symbol calculation/string APIs, and the `struct expr` definitions in `expr.h`. Menu and symbol code use it to represent `depends on`, `visible if`, `select`, `imply`, range, and prompt conditions.

## Risks And Test Signals
Many transforms mutate trees in place and sometimes replace nodes by structure assignment, so ownership bugs are possible if callers share expression subtrees unexpectedly. Boolean comparisons to `m` print warnings and force constants. Numeric parsing falls back to string comparison on parse failure. Tests should cover duplicate elimination, tristate truth tables, De Morgan transforms, relation comparisons across int/hex/string, printed precedence, and memory-sanitizer runs on complex dependency graphs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/expr.h -->
# sources/test-tools/kdevops/scripts/kconfig/expr.h

## Purpose
`expr.h` defines the core Kconfig data model for tristate values, dependency expressions, configuration symbols, properties, menus, and jump keys, plus the public expression API.

## Important APIs, Types, And Functions
Key types are `tristate`, `enum expr_type`, `struct expr`, `struct expr_value`, `struct symbol_value`, `enum symbol_type`, `struct symbol`, `enum prop_type`, `struct property`, `struct menu`, and `struct jump_key`. Important flags include `SYMBOL_CONST`, `SYMBOL_VALID`, `SYMBOL_WRITE`, `SYMBOL_YAML`, `SYMBOL_WRITTEN`, `SYMBOL_DEF_USER`, and menu flag `MENU_CHANGED`. Iteration macros include `for_all_properties()`, `for_all_defaults()`, and `for_all_prompts()`. Expression prototypes expose allocation, simplification, evaluation, dependency query, and printing functions.

## Control Flow
The header has no runtime flow but defines the object graph traversed by parser, menu, symbol, conf, and expression modules. Symbols own lists of menu definitions and properties; menus form a parent/child/next tree and may reference symbols; properties link prompts/defaults/selects/ranges back to menus.

## State And Persistence
The structures hold all in-memory Kconfig state: current symbol values, user/default values, visibility, direct and reverse dependencies, menu hierarchy, source locations, help text, and frontend data. Persistence is implemented elsewhere by reading/writing these fields.

## Dependencies And Integration Points
It includes `list_types.h` and is included by `lkc.h` and almost every Kconfig implementation file. Changes to these structures affect parser, frontend, config I/O, and expression logic.

## Risks And Test Signals
Flag bit compatibility is important because many modules test and mutate the same fields. `SYMBOL_DEF3` and `SYMBOL_DEF4` comments appear to reference old names (`S_DEF_3`, `S_DEF_4`) while the enum uses `S_DEF_DEF3` and `S_DEF_DEF4`. Structural changes require full Kconfig parser, conf, menuconfig, and serialization tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/expr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/hashtable.h -->
# sources/test-tools/kdevops/scripts/kconfig/hashtable.h

## Purpose
This header provides a tiny Linux-style hash table macro layer over `hlist_head` lists for Kconfig symbol lookup.

## Important APIs, Types, And Functions
Macros include `HASH_SIZE(name)`, `HASHTABLE_DECLARE(name, size)`, `HASHTABLE_DEFINE(name, size)`, `hash_head(table, key)`, `hash_add(table, node, key)`, `hash_for_each(table, obj, member)`, and `hash_for_each_possible(table, obj, member, key)`.

## Control Flow
All behavior expands inline at compile time. Insertion hashes a key modulo array size and prepends an hlist node. Iteration either walks all buckets or a single key bucket.

## State And Persistence
The table is caller-owned static or external memory. The macros mutate hlist links but have no persistence.

## Dependencies And Integration Points
It depends on `array_size.h` and `list.h`. `internal.h` uses it to declare `sym_hashtable` and `for_all_symbols()`.

## Risks And Test Signals
The hash function is only `key % size`; quality depends entirely on caller-provided keys. There is no deletion wrapper here. Macro arguments may be evaluated in ways callers must understand. Test by inserting known symbol structures and iterating all and bucket-local paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/hashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/internal.h -->
# sources/test-tools/kdevops/scripts/kconfig/internal.h

## Purpose
`internal.h` declares internal Kconfig parser/symbol globals shared across implementation files but not intended as the public frontend API.

## Important APIs, Types, And Functions
It defines `SYMBOL_HASHSIZE` as `1U << 14`, declares `sym_hashtable`, and provides `for_all_symbols(sym)` as a hash-table iteration macro. It forward declares `struct menu` and exposes `current_menu`, `current_entry`, `cur_filename`, and `cur_lineno`.

## Control Flow
There is no runtime control flow; the header supplies declarations and iteration macros.

## State And Persistence
It references global parser/menu construction state and the global symbol hash table. The state is in-memory only but feeds all later configuration persistence.

## Dependencies And Integration Points
It includes `hashtable.h` and is included by parser, conf, confdata, and symbol/menu implementation files that need global Kconfig internals.

## Risks And Test Signals
Because it exposes mutable globals, ordering and initialization are important. The symbol hash size affects lookup performance. Test signals are successful parser initialization, symbol lookup coverage, and full config reads/writes after parsing nested Kconfig files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/kconf_id.c -->
# sources/test-tools/kdevops/scripts/kconfig/kconf_id.c

## Purpose
This file maps Kconfig language keywords to lexer/parser token metadata. It is a compact replacement for generated perfect-hash keyword lookup.

## Important APIs, Types, And Functions
`kconf_id_array[]` contains entries for commands and options such as `mainmenu`, `menu`, `choice`, `config`, `default`, `bool`, `tristate`, `select`, `imply`, `range`, `modules`, `defconfig_list`, and `allnoconfig_y`. Each entry carries a token, flags like `TF_COMMAND`, `TF_PARAM`, `TF_OPTION`, and for type/default tokens a symbol type. `kconf_id_lookup(str, len)` linearly searches the array.

## Control Flow
Lookup iterates the array, compares requested length with `strlen(id->name)`, and then `memcmp()`s the bytes. It returns the matching descriptor or `NULL`.

## State And Persistence
The keyword array is static read-only data at runtime. It has no persistent side effects.

## Dependencies And Integration Points
It requires the `struct kconf_id`, token constants, and flags from parser/lexer headers. The lexer/parser uses it to classify words when parsing Kconfig syntax.

## Risks And Test Signals
Linear lookup is fine for this small table but depends on all keywords being kept in sync with grammar tokens. Missing newer tokens will parse as ordinary words. Tests should parse Kconfig snippets for every listed keyword and reject/handle unknown keywords as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/kconf_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lexer.l -->
# sources/test-tools/kdevops/scripts/kconfig/lexer.l

## Purpose
This Flex lexer tokenizes Kconfig files, handles quoted strings, assignment values, help text indentation, variable expansion, and nested `source` inclusions.

## Important APIs, Types, And Functions
The generated scanner exposes `yylex()`. Internal helpers include `new_string()`, `append_string()`, `alloc_string()`, `warn_ignored_character()`, `expand_token()`, `append_expanded_string()`, `zconf_starthelp()`, `zconf_endhelp()`, `zconf_fopen()`, `zconf_initscan()`, `zconf_nextfile()`, and `zconf_endfile()`. `struct buffer` stores nested scanner state. Start conditions are `ASSIGN_VAL`, `HELP`, and `STRING`.

## Control Flow
The first-stage lexer recognizes Kconfig keywords, operators, comments, whitespace, bare words, expandable `$` words, quoted strings, assignment-value lines, and help blocks. `yylex()` is a second-stage wrapper that suppresses repeated blank-line tokens, updates parser line numbers at statement starts, and switches to `ASSIGN_VAL` after top-level assignment operators. Includes push the current Flex buffer onto a parent stack, open the next file, detect recursive inclusion, and restore the previous buffer at EOF.

## State And Persistence
Global scanner state includes `cur_filename`, `cur_lineno`, previous token tracking, dynamic `text` buffer, current buffer stack, and help indentation counters. It reads Kconfig source files, including paths relative to `srctree`, and writes only diagnostics.

## Dependencies And Integration Points
It depends on Flex, `parser.tab.h`, `lkc.h`, `preprocess.h`, and `xalloc`. The parser calls `zconf_initscan()` and consumes tokens from `yylex()`.

## Risks And Test Signals
String and variable expansion push unused characters back into the scanner, so boundary cases around `$`, quotes, and assignments need coverage. Help indentation handling is sensitive to tabs and blank lines. Recursive include detection compares filenames as passed, so different path spellings could evade it. Tests should parse nested sources, assignments, variable expansions, multiline strings, help text, missing newline EOF, and recursive inclusion.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/list.h -->
# sources/test-tools/kdevops/scripts/kconfig/list.h

## Purpose
This header implements a small subset of Linux kernel doubly linked list and hlist primitives for standalone Kconfig builds.

## Important APIs, Types, And Functions
It provides `container_of()`, list poison constants, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD()`, `list_add()`, `list_add_tail()`, `list_del()`, `list_move()`, `list_move_tail()`, `list_is_head()`, `list_empty()`, entry accessors, forward/reverse/safe iteration macros, `HLIST_HEAD_INIT`, `hlist_add_head()`, `hlist_entry()`, `hlist_entry_safe()`, and `hlist_for_each_entry()`.

## Control Flow
All functions are static inline or macros. List insertion links a new node between known neighbors; deletion reconnects neighbors and poisons the deleted node; movement combines delete and insert. Iteration macros use `container_of()` to recover the parent object from embedded list nodes.

## State And Persistence
State is stored entirely in caller-owned embedded list nodes. There is no persistence and no allocation.

## Dependencies And Integration Points
It depends on `stddef.h`, compiler support for `typeof`, `_Static_assert`, and `__builtin_types_compatible_p`, plus `list_types.h`. Kconfig symbols, menus, properties, choices, and hash tables use these list primitives.

## Risks And Test Signals
The macros assume non-empty lists for first/last entry helpers and require nodes to be initialized. Poison values can expose use-after-delete in debugging but are not portable safety. Tests should exercise empty checks, insertion order, move order, safe deletion during iteration, hlist insertion/iteration, and compiler compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/list_types.h -->
# sources/test-tools/kdevops/scripts/kconfig/list_types.h

## Purpose
This header declares the minimal list node structures shared by list and hash table utilities.

## Important APIs, Types, And Functions
It defines `struct list_head` with `next` and `prev`, `struct hlist_head` with `first`, and `struct hlist_node` with `next` and `pprev`.

## Control Flow
There is no runtime flow; it is type-only.

## State And Persistence
Instances of these structs are embedded in higher-level objects and hold in-memory linkage state only.

## Dependencies And Integration Points
It is included by `list.h` and `expr.h`, making it foundational for symbol/menu/property collections.

## Risks And Test Signals
Any ABI or field-name change breaks all list macros. Compile tests across all Kconfig objects are the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/list_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lkc.h -->
# sources/test-tools/kdevops/scripts/kconfig/lkc.h

## Purpose
`lkc.h` is the central public/internal umbrella header for the standalone Kconfig library. It gathers expression definitions, generated prototypes, scanner interfaces, utility string builders, menu APIs, and symbol APIs.

## Important APIs, Types, And Functions
It includes `expr.h` and `lkc_proto.h`, defines `SRCTREE`, and implements `CONFIG_prefix()` so the `CONFIG_` prefix can be overridden by an environment variable named `CONFIG_`. It declares lexer/parser functions (`zconfdump`, `zconf_starthelp`, `zconf_fopen`, `zconf_initscan`, `zconf_nextfile`, `yylex`), `xfwrite()`, `strhash()`, `file_lookup()`, `struct gstr` and string builder functions, menu construction/query APIs, root menu, and symbol calculation/query APIs.

## Control Flow
The header itself has no control flow except inline helpers. `xfwrite()` asserts nonzero element size and reports write failures. `CONFIG_prefix()` reads the environment at call time, so `CONFIG_` behaves as a dynamic macro.

## State And Persistence
It exposes global `yylineno`, `autoconf_cmd`, and `rootmenu`. Most declared functions mutate parser, menu, symbol, or configuration state elsewhere.

## Dependencies And Integration Points
Every Kconfig implementation file depends on this header for shared prototypes and types. Frontend binaries link code that implements these declarations.

## Risks And Test Signals
The `CONFIG_` environment override is unusual and can alter all config serialization. `xfwrite()` only prints an error rather than aborting. Header changes require full rebuilds of lexer/parser, conf, menuconfig, nconfig, and config I/O tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lkc_proto.h -->
# sources/test-tools/kdevops/scripts/kconfig/lkc_proto.h

## Purpose
`lkc_proto.h` provides forward declarations for Kconfig persistence, symbol, property, and expression functions used across compilation units.

## Important APIs, Types, And Functions
It declares config I/O functions from `confdata.c`, symbol lookup/search/type/value functions from `symbol.c`, property type naming, and `expr_print()` from `expr.c`.

## Control Flow
There is no runtime flow; it is a prototype surface.

## State And Persistence
The declared config functions read and write persistent configuration files. The header itself has no state.

## Dependencies And Integration Points
It is included by `lkc.h` after standard variadic support. It keeps compiler checking consistent across Kconfig modules.

## Risks And Test Signals
Prototype drift causes build failures or worse if declarations stop matching definitions. Full `make conf mconf nconf` is the primary signal, plus warnings with strict prototype flags.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lkc_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/checklist.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/checklist.c

## Purpose
This lxdialog file implements the checklist/radiolist widget used by menuconfig to select one option from a list and optionally request help.

## Important APIs, Types, And Functions
The public function is `dialog_checklist()`. Internal helpers `print_item()`, `print_arrows()`, and `print_buttons()` render list rows, scroll indicators, and Select/Help buttons. It uses the shared item-list API and global `dlg` color/attribute state from `dialog.h` and `util.c`.

## Control Flow
The function selects an initial item, verifies terminal dimensions, creates a centered dialog and list subwindow, computes checkbox/item positions, renders visible rows, then loops on keyboard input. Movement keys update `choice` and `scroll`; selection keys clear all item selections and mark the current item; Help returns button 1; resize recreates the windows; ESC uses the common escape filter.

## State And Persistence
All persistent UI state lives in the shared item list selection flags. Local layout state is static for the current module. No disk state is touched.

## Dependencies And Integration Points
It is linked into `mconf` through the Makefile's `lxdialog` object list. Return values are consumed by menuconfig's control logic.

## Risks And Test Signals
The source duplicates the top-level `kconfig/checklist.c`, so fixes must stay synchronized. Unchecked allocation and truncation behavior mirror the other copy. Test with curses-driven key sequences for scrolling, selection, help, resize, too-small terminal, and tagged separator items.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/checklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/dialog.h -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/dialog.h

## Purpose
`dialog.h` is the common lxdialog interface for menuconfig's ncurses widgets. It defines colors, global dialog state, item-list structures, minimum window sizes, key constants, and widget/drawing function prototypes.

## Important APIs, Types, And Functions
Important types are `struct dialog_color`, `struct subtitle_list`, `struct dialog_info`, `struct dialog_item`, and `struct dialog_list`. It declares global `dlg`, `dialog_input_result`, `saved_x`, and `saved_y`. It exposes item-list builders/accessors, common handlers `on_key_esc()` and `on_key_resize()`, initialization functions `init_dialog()`, `dialog_clear()`, `end_dialog()`, drawing helpers, and widget APIs `dialog_yesno()`, `dialog_msgbox()`, `dialog_textbox()`, `dialog_menu()`, `dialog_checklist()`, and `dialog_inputbox()`.

## Control Flow
The header has no runtime flow. Its macros and prototypes define how widget modules share state and return key/button codes.

## State And Persistence
It centralizes global ncurses state and the transient item list. There is no persistent storage.

## Dependencies And Integration Points
It includes POSIX headers and `ncurses.h`. All lxdialog C files include it, and menuconfig code uses the declared widget APIs.

## Risks And Test Signals
Global mutable state means widgets are not reentrant. `MAX_LEN` and `MAXITEMSTR` bound input/text and item display. Minimum-size constants affect resize behavior. Compile/link tests plus curses UI smoke tests cover this header.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/dialog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/inputbox.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/inputbox.c

## Purpose
`inputbox.c` implements a menuconfig text input dialog, used for editing string, int, or hex configuration values from the curses frontend.

## Important APIs, Types, And Functions
It defines global `dialog_input_result[MAX_LEN + 1]` and exports `dialog_inputbox(title, prompt, height, width, init)`. `print_buttons()` renders Ok and Help buttons.

## Control Flow
The dialog copies the initial value into `dialog_input_result`, validates terminal size, draws the prompt and input field, displays a horizontally scrolled view when the string exceeds field width, and enters a key loop. When the input field is active, printable keys insert at the cursor, backspace deletes, and left/right move or scroll. Tab/up/down/left/right cycle focus between input, Ok, and Help. Enter or Space returns the focused action; `o` and `h` are shortcuts; resize recreates the window.

## State And Persistence
The edited value persists in the global `dialog_input_result` buffer after return. Local state tracks cursor position, visible offset, length, and active button. No files are written.

## Dependencies And Integration Points
It uses ncurses and common drawing/helpers from `dialog.h`/`util.c`. Menuconfig reads `dialog_input_result` after a successful return.

## Risks And Test Signals
`strcpy(instr, init)` can overflow if the caller passes an initial value longer than `MAX_LEN`. Editing is byte-oriented and not multibyte-aware. Tests should cover long initial values, insertion/deletion in the middle, horizontal scrolling, focus cycling, Help return, ESC, and resize.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/inputbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/menubox.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/menubox.c

## Purpose
`menubox.c` implements the main menu list widget for menuconfig. It shows selectable menu entries, supports scrolling, hotkeys, page navigation, and command buttons for select, exit, help, save, and load.

## Important APIs, Types, And Functions
The exported function is `dialog_menu(title, prompt, selected, s_scroll)`. Helpers include `do_print_item()`, `print_item` macro, `print_arrows()`, `print_buttons()`, and `do_scroll()`. It uses global item-list data and the `void *data` field to match the selected menu item.

## Control Flow
On resize it sizes the dialog to the current terminal, draws the prompt/list/buttons, restores a valid scroll offset from `*s_scroll`, and places the selected item in view. The key loop normalizes alphabetic hotkeys, searches visible entries, handles arrows, plus/minus, PageUp/PageDown, and updates scroll/highlight. Command keys return distinct codes for help, yes/no/module/toggle/search, button selection, and exit while saving the scroll position.

## State And Persistence
It mutates `*s_scroll` so callers can preserve scroll location across invocations and marks the selected item in the global item list. No disk state is used.

## Dependencies And Integration Points
It links into `mconf` and depends on shared lxdialog utilities. Return codes are part of the menuconfig frontend contract and must match caller expectations.

## Risks And Test Signals
The widget assumes item count and scroll math remain consistent while displayed. Return code meanings are implicit and easy to break. Tests should drive hotkeys, scrolling near boundaries, page navigation, saved scroll validation, each command key, resize, and empty list behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/menubox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/textbox.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/textbox.c

## Purpose
`textbox.c` implements a scrollable read-only text dialog for help and informational content in menuconfig.

## Important APIs, Types, And Functions
The public function is `dialog_textbox(title, tbuf, initial_height, initial_width, _vscroll, _hscroll, extra_key_cb, data)`. Internal state and helpers include static `hscroll`, `begin_reached`, `end_reached`, `page_length`, `buf`, `page`, `start`, `end`, `back_lines()`, `get_line()`, `print_line()`, `print_page()`, `print_position()`, and `refresh_text_box()`.

## Control Flow
The dialog initializes `page` into the text buffer, applies optional saved vertical/horizontal scroll, sizes/draws the window, prints the first page, and loops on keys. Home/End jump to top/bottom; up/down and page keys move vertically; left/right and `0` control horizontal scroll; exit keys close; resize recreates the window after backing up; unknown keys may be delegated to `extra_key_cb`, which can request exit.

## State And Persistence
Scroll state is stored back through `_vscroll` and `_hscroll` pointers. The text buffer is caller-owned and read-only. Static module variables mean simultaneous textboxes are not reentrant.

## Dependencies And Integration Points
It depends on lxdialog drawing functions, ncurses, and optional caller callbacks. Menuconfig uses it for help text and extended descriptions.

## Risks And Test Signals
`print_position()` divides by `strlen(buf)`, so an empty buffer risks division by zero. Lines longer than `MAX_LEN` are truncated. Scrolling works by pointer arithmetic over bytes, not characters. Tests should cover empty text, long lines, saved scroll restore, top/bottom boundaries, horizontal scrolling, callback exit, and resize.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/textbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/util.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/util.c

## Purpose
`util.c` provides common ncurses setup, color themes, drawing primitives, text wrapping, ESC/resize handling, and item-list management shared by all lxdialog widgets.

## Important APIs, Types, And Functions
It defines global `saved_x`, `saved_y`, `dlg`, `item_cur`, `item_nil`, and `item_head`. Theme helpers include `set_mono_theme()`, `set_classic_theme()`, `set_blackbg_theme()`, `set_bluetitle_theme()`, `set_theme()`, `init_one_color()`, `init_dialog_colors()`, and `color_setup()`. Public utilities include `attr_clear()`, `dialog_clear()`, `init_dialog()`, `set_dialog_backtitle()`, `set_dialog_subtitles()`, `end_dialog()`, `print_title()`, `print_autowrap()`, `print_button()`, `draw_box()`, `draw_shadow()`, `first_alpha()`, `on_key_esc()`, `on_key_resize()`, and all `item_*` functions.

## Control Flow
`init_dialog()` initializes curses, validates terminal size, stores cursor position, selects a color theme from `MENUCONFIG_COLOR`, enables keypad/cbreak/noecho, and clears the background. Drawing helpers are called by widgets to render consistent boxes, titles, prompts, buttons, and shadows. `on_key_esc()` temporarily disables keypad and drains pending input to distinguish a real ESC from escape sequences. Item functions manage a singly linked list, append formatted text, set tags/data/selection, iterate, and retrieve current item fields.

## State And Persistence
All state is process-local ncurses and heap state. `item_reset()` frees the item list. There is no file persistence.

## Dependencies And Integration Points
It depends on ncurses and `dialog.h`, and every lxdialog widget depends on it. Menuconfig signal handling uses `saved_x`/`saved_y`.

## Risks And Test Signals
Several string operations assume prompt/item lengths fit fixed buffers (`strcpy` in `print_autowrap`, `vsnprintf` truncation for items). `item_make()` does not check allocation failure. `init_one_color()` monotonically consumes color pairs. Test signals include theme selection, no-color terminals, too-small terminal initialization, ESC behavior, text wrapping with long prompts, item reset/rebuild, and memory checking.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/yesno.c -->
# sources/test-tools/kdevops/scripts/kconfig/lxdialog/yesno.c

## Purpose
`yesno.c` implements a simple two-button confirmation dialog for menuconfig.

## Important APIs, Types, And Functions
The exported function is `dialog_yesno(title, prompt, height, width)`. `print_buttons()` renders Yes and No buttons using common button drawing.

## Control Flow
The function validates terminal size, centers and draws a dialog, prints title and prompt, renders buttons, and loops on input. `y` returns 0, `n` returns 1, Tab/left/right toggles the active button, Enter/Space returns the selected button, ESC uses the common handler, and resize recreates the dialog.

## State And Persistence
Only local `button` and `key` state is used. No persistent state or global item list is changed.

## Dependencies And Integration Points
It depends on ncurses and lxdialog utilities. Callers interpret 0 as Yes and 1 as No, with ESC/error codes passed through.

## Risks And Test Signals
The return convention is positional rather than symbolic, so callers must stay aligned. Tests should cover y/n shortcuts, button toggling, Enter/Space selection, ESC, resize, and too-small terminals.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/lxdialog/yesno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mconf-cfg.sh -->
# sources/test-tools/kdevops/scripts/kconfig/mconf-cfg.sh

## Purpose
This shell script discovers compiler and linker flags for ncurses so the Makefile can build the `mconf` menuconfig frontend.

## Important APIs, Types, And Functions
It takes two positional output files: a cflags file and a libs file. It checks `$HOSTPKG_CONFIG` for `ncursesw` then `ncurses`, then probes common include directories, then tests whether `$HOSTCC -E` can include `<ncurses.h>`.

## Control Flow
With `set -eu`, it aborts on missing variables or failed unguarded commands. Successful detection writes compiler flags to the cflags path and linker flags to the libs path, then exits 0. If all checks fail, it prints an explanatory error and exits 1.

## State And Persistence
The script writes the two files passed by the Makefile. It reads host include paths and uses environment variables `HOSTPKG_CONFIG` and `HOSTCC`.

## Dependencies And Integration Points
It is invoked by the Kconfig Makefile pattern rule for `mconf-cflags` and `mconf-libs`. It integrates with pkg-config and host C compiler discovery.

## Risks And Test Signals
Unset `HOSTCC` can fail the final fallback under `set -u` if pkg-config and include checks do not succeed. Include directory checks are distro-specific. Tests should run with fake/pkg-config-controlled environments, with only `/usr/include/ncursesw`, only `/usr/include/ncurses`, compiler fallback, and a no-ncurses failure case.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mconf-cfg.sh -->
