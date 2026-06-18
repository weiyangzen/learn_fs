# subset-b-006332 Research

Grouped source research for the Ceph-client copy of Linux kconfig persistence, expression/menu model, lexer interfaces, GTK/ncurses frontends, and lxdialog widgets. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/confdata.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/confdata.c

## Purpose

`confdata.c` is the kconfig persistence layer. It reads user and generated configuration files, tracks whether the in-memory symbol graph differs from disk, writes `.config`/defconfig output, and emits generated build artifacts such as `include/config/auto.conf`, `include/generated/autoconf.h`, and `include/generated/rustc_cfg`.

## Important APIs, Types, and Functions

Public entry points include `conf_get_configname()`, `conf_read_simple()`, `conf_read()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, `conf_set_changed()`, `conf_get_changed()`, `conf_set_changed_callback()`, `conf_set_message_callback()`, and `conf_errors()`. Internal helpers handle filesystem safety and formatting: `make_parent_dir()`, `is_same()`, `conf_set_sym_val()`, `getline_stripped()`, `escape_string_value()`, `__print_symbol()`, `print_symbol_for_c()`, `print_symbol_for_rustccfg()`, `conf_write_autoconf_cmd()`, and `conf_touch_deps()`. `struct comment_style` abstracts generated-file headers, and global `autoconf_cmd` is written into the `.cmd` dependency file.

## Control Flow

Read flow starts with `conf_read()`, which clears the changed flag, delegates parsing of `.config` or default files to `conf_read_simple()`, recalculates `modules_sym` and all symbols, and marks the configuration dirty when saved user values no longer match calculated values or write eligibility. `conf_read_simple()` parses both `CONFIG_FOO=value` and `# CONFIG_FOO is not set`, validates values by symbol type, warns on malformed/unknown/reassigned lines, and reorders choice members so the last selected choice has priority.

Write flow is split by target. `conf_write()` traverses `rootmenu` depth-first, emits visible menu headings and writable non-choice symbols, writes to a temporary file unless `KCONFIG_OVERWRITECONFIG` is set, avoids replacing identical files, and renames the old file to `.old`. `conf_write_defconfig()` emits only user-changeable values that differ from defaults. `conf_write_autoconf()` writes the command dependency file, recalculates symbols, touches per-symbol dependency sentinels, then writes the C header, Rust cfg file, and finally `auto.conf` as the success marker.

## State and Persistence Behavior

The file owns the process-global changed flag, warning counters, message/change callbacks, and depfile prefix buffer. It persists configuration to user-selected paths, `.old` backups, generated headers/cfg, `auto.conf`, `auto.conf.cmd`, and empty include/config dependency files whose timestamps notify kbuild when individual symbols changed or disappeared. Environment variables alter paths and behavior: `KCONFIG_CONFIG`, `KCONFIG_AUTOCONFIG`, `KCONFIG_AUTOHEADER`, `KCONFIG_RUSTCCFG`, `KCONFIG_DEFCONFIG_LIST`, `KCONFIG_WERROR`, `KCONFIG_WARN_UNKNOWN_SYMBOLS`, and `KCONFIG_OVERWRITECONFIG`.

## Dependencies and Integration Points

It depends on the shared symbol/menu/expression model from `lkc.h`/`internal.h`, allocation helpers from `xalloc.h`, `zconf_fopen()` from the lexer, symbol APIs from `symbol.c`, and menu traversal from `menu.c`. It is called by command-line config tools, `mconf`, `gconf`, and build automation through the lkc API.

## Risks and Edge Cases

Path truncation and parent-directory creation errors can prevent writes; `is_same()` mmaps files and does not unmap before close, which is acceptable for a short-lived tool but worth noting. Generated files rely on rename ordering, with `auto.conf` intentionally last. String parsing differs for `S_DEF_AUTO` versus user config, so escaping bugs can cause mismatches. Unknown symbols in `auto.conf` trigger dependency touches; disabling that behavior would break incremental rebuilds. `KCONFIG_WERROR` promotes warnings into errors only through `conf_errors()`, so callers must check it.

## Test Signals

Good coverage includes kconfig parser tests for invalid values, duplicate assignments, unknown-symbol warnings, CRLF lines, choice override ordering, defconfig minimization, no-rewrite-on-identical-output, generated C/Rust/autoconf formatting, dependency touch behavior after symbol removal, and environment-variable path overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/confdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/expr.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/expr.c

## Purpose

`expr.c` implements kconfig's expression graph: allocation/interning, equality and simplification, dependency transformation, value calculation, cache invalidation, and printable forms for diagnostics and help text.

## Important APIs, Types, and Functions

Allocation APIs are `expr_alloc_symbol()`, `expr_alloc_one()`, `expr_alloc_two()`, `expr_alloc_comp()`, `expr_alloc_and()`, and `expr_alloc_or()`, all backed by `expr_lookup()` and `expr_hashtable`. Simplification and dependency APIs include `expr_eq()`, `expr_eliminate_eq()`, `expr_eliminate_dups()`, `expr_transform()`, `expr_contains_symbol()`, `expr_depends_symbol()`, and `expr_trans_compare()`. Evaluation and output APIs include `expr_calc_value()`, `expr_invalidate_all()`, `expr_print()`, `expr_fprint()`, `expr_gstr_print()`, and `expr_gstr_print_revdep()`.

## Control Flow

Expressions are immutable-ish interned nodes keyed by type and child pointers. Parser/menu code constructs raw trees, `expr_transform()` rewrites boolean comparisons and pushes negations through compound expressions, and `expr_eliminate_dups()` repeatedly joins redundant operands until no transformation occurred. `expr_calc_value()` lazily evaluates tristate logic or relational comparisons, using cached `val` until invalidated. Printing recurses with precedence tracking so generated text is both compact and correctly parenthesized.

## State and Persistence Behavior

The file owns `expr_hashtable` and cached expression values. There is no file persistence, but cached values are semantic state; callers must use `expr_invalidate_all()` after user/default values change. `trans_count` is a process-global simplification counter used during transformations and temporarily restored by equality checks.

## Dependencies and Integration Points

It integrates with `symbol.c` via `sym_calc_value()` and `sym_get_string_value()`, with `menu.c` for dependency propagation and automatic submenu creation, and with UI/help code through `expr_gstr_print*()`. It relies on `hash.h`, `xalloc.h`, `internal.h`, and the types declared in `expr.h`.

## Risks and Edge Cases

The intern table makes pointer identity meaningful for equality and hash lookup. Because nodes are reused, callers should treat expressions as persistent trees and rebuild rather than mutate fields. Cached values can go stale if invalidation is missed. Numeric comparison falls back to string comparison when parsing fails, which is correct for mixed string cases but can surprise callers expecting strict numeric validation. The simplifier has special tristate/boolean assumptions; incorrect symbol typing can change dependency results.

## Test Signals

Useful tests cover boolean and tristate simplifications, De Morgan rewrites, duplicate elimination, choice dependency comparisons, relational comparisons for signed/unsigned/string values, cache invalidation after `conf_read_simple()`, and printed expression precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/expr.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/expr.h

## Purpose

`expr.h` is the core public data model for kconfig expressions, symbols, properties, and menu nodes. It defines the contracts shared by parser, symbol evaluation, menu finalization, persistence, and frontends.

## Important APIs, Types, and Functions

Key types are `enum tristate`, `enum expr_type`, `union expr_data`, `struct expr`, `struct expr_value`, `struct symbol_value`, `enum symbol_type`, `struct symbol`, `enum prop_type`, `struct property`, `enum menu_type`, `struct menu`, and `struct jump_key`. Important flags include `SYMBOL_CONST`, `SYMBOL_VALID`, `SYMBOL_TRANS`, `SYMBOL_WRITE`, `SYMBOL_WRITTEN`, `SYMBOL_WARNED`, `SYMBOL_DEF_*`, `MENU_CHANGED`, and `MENU_ROOT`. It declares the expression APIs implemented by `expr.c`, global const symbols `symbol_yes`, `symbol_no`, `symbol_mod`, and `modules_sym`.

## Control Flow

This header has no executable control flow beyond `expr_is_yes()` and tristate macros. Its structures drive runtime flow elsewhere: parser creates `struct menu`/`struct property`, symbol code computes `struct symbol.curr`, expression code evaluates `struct expr`, and UI code traverses menu nodes.

## State and Persistence Behavior

The header defines in-memory state layout. `struct symbol` stores current calculated value, external/default values, visibility, menu instances, reverse dependencies, and flags used by reads/writes. `struct menu` stores tree structure, prompt, inherited dependencies, visibility clauses, help text, source location, and frontend scratch data. Persistence is performed by `confdata.c`, but it relies on these fields being stable.

## Dependencies and Integration Points

It includes list and C/C++ compatibility headers and is included by nearly all kconfig sources. The structures are tightly coupled with `parser.y`, `symbol.c`, `menu.c`, `confdata.c`, `expr.c`, `mconf.c`, and `gconf.c`.

## Risks and Edge Cases

This is a central ABI within the tool; changing enum values, flag bits, or struct fields has broad blast radius. Choices are represented as symbols with `name == NULL`, so null-name handling is required throughout. `union expr_data` stores const-typed views plus `_initdata` for interning; unsafe mutation can break hash identity.

## Test Signals

Compile coverage across all kconfig frontends is the first signal. Behavioral signals include choices, multi-definition symbols, `select`/`imply`, visibility inheritance, transitional symbols, and config write/read round trips that exercise the flags declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/expr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf-cfg.sh -->
# sources/distributed-fs/ceph-client/scripts/kconfig/gconf-cfg.sh

## Purpose

`gconf-cfg.sh` is a build-time probe for the GTK frontend. It verifies that host `pkg-config` is available and that GTK+ 3 development files can be found, then writes compiler and linker flags to files provided by the caller.

## Important APIs, Types, and Functions

The script is linear shell code with inputs `cflags=$1` and `libs=$2`. It uses `HOSTPKG_CONFIG`, package name `gtk+-3.0`, `command -v`, `pkg-config --exists`, `pkg-config --cflags`, and `pkg-config --libs`.

## Control Flow

With `set -eu`, missing variables or failed commands abort. The script first checks for `${HOSTPKG_CONFIG}` in `PATH`, prints a user-facing diagnostic and exits on absence, then checks for GTK+ 3. If found, it writes cflags and libs to the requested output files.

## State and Persistence Behavior

It persists only two generated build fragments: the host compiler flags file and host libraries file. It does not mutate repository sources.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile when building `gconfig`. It depends on host GTK+ 3 development packages and the build-system-provided `HOSTPKG_CONFIG` variable.

## Risks and Edge Cases

Because `set -u` is active, an unset `HOSTPKG_CONFIG` fails before the friendly diagnostic. The script has no fallback include/library probing, unlike the ncurses cfg scripts, so environments without pkg-config cannot build `gconfig` even if GTK headers are manually available.

## Test Signals

Test with valid GTK/pkg-config, missing pkg-config, missing GTK package, and output paths in generated build directories. Build-level signal is successful compilation/linking of `gconf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf-cfg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/gconf.c

## Purpose

`gconf.c` implements the GTK 3 graphical kconfig frontend. It renders the shared kconfig menu tree into one or two `GtkTreeView` widgets, shows symbol help, edits symbol values, loads/saves config files, and coordinates visible/full/split/single view modes.

## Important APIs, Types, and Functions

Important state includes `enum view_mode`, option-display modes, global GTK widgets, tree stores `tree1`/`tree2`, `pix_menu`, and menu pointers `browsed`/`selected`. Core functions include `set_node()`, `display_tree()`, `recreate_tree()`, `fixup_rootmenu()`, `set_view_mode()`, `update_tree()`, `visible_func()`, `change_sym_value()`, `toggle_sym_value()`, `renderer_edited()`, `init_main_window()`, `init_left_tree()`, `init_right_tree()`, and `main()`. Callback functions handle menu actions, toolbar buttons, tree clicks/keys, cursor changes, window deletion, and save prompts.

## Control Flow

`main()` initializes GTK, locates `gconf.ui`, parses Kconfig with `conf_parse()`, tags root menus for split view, builds the main window from GtkBuilder XML, initializes tree columns/models, reads `.config`, chooses the starting view, and enters `gtk_main()`. Tree creation walks `rootmenu` and stores `struct menu *` in each row. Selection updates help text through `menu_get_ext_help()`. User clicks or keypresses call symbol setters, then refresh tree row values and visibility filters. Save/load callbacks delegate to `conf_read()`, `conf_write()`, and `conf_write_autoconf()`.

## State and Persistence Behavior

UI state is process-global: view mode, option visibility mode, selected/browsed menu pointers, dirty button sensitivity, text tags, model contents, and loaded pixbufs. Persistent output is handled by `confdata.c`; `gconf` only chooses filenames through dialogs and triggers writes. The changed callback updates Save affordances when symbol APIs mark the configuration dirty.

## Dependencies and Integration Points

It depends on GTK/GDK/Pango, `gconf.ui`, XPM icons under `scripts/kconfig/icons`, `SRCTREE` for resource lookup, and shared kconfig APIs from `lkc.h`. It is built only when `gconf-cfg.sh` finds GTK+ 3.

## Risks and Edge Cases

Resource path construction depends on `SRCTREE`, `argv[0]`, or current directory matching the kernel script layout. Missing icons produce warnings; missing UI XML is fatal. `renderer_edited()` ignores the return value from `sym_set_string_value()`, so invalid values are not explicitly surfaced in this frontend. `gtk_tree_model_get()` ownership for string columns needs care; the current code fetches `old_def` but does not use/free it. Filtering calls `menu_is_visible()`, which recalculates symbol state and can be expensive on large trees.

## Test Signals

Build and launch `gconfig` with GTK+ 3, exercise load/save/save-as, dirty-state button toggling, single/split/full view switching, show-name/range/data toggles, normal/all/prompt filters, boolean/tristate edits, string/int/hex edits including invalid inputs, and resource lookup with and without `SRCTREE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf.ui -->
# sources/distributed-fs/ceph-client/scripts/kconfig/gconf.ui

## Purpose

`gconf.ui` is the GtkBuilder XML layout consumed by `gconf.c`. It declares the main GTK window, menubar, toolbar, split panes, tree views, and help text view for the graphical kconfig frontend.

## Important APIs, Types, and Functions

There are no functions. Important object IDs are `window1`, `menubar1`, `load1`, `save1`, `save_as1`, `quit1`, `show_name1`, `show_range1`, `show_data1`, `set_option_mode1/2/3`, `introduction1`, `about1`, `license1`, toolbar buttons `button1` through `button8`, `hpaned1`, `vpaned1`, `treeview1`, `treeview2`, and `textview3`.

## Control Flow

Runtime flow is declarative: `gtk_builder_new_from_file()` loads this file, then `init_main_window()` looks up object IDs and attaches C callbacks. Accelerators for load/save/quit/introduction/about are declared here; all dynamic behavior is implemented in `gconf.c`.

## State and Persistence Behavior

The file stores static UI defaults such as window size, widget visibility, labels, tooltips, active radio/check menu defaults, paned layout, and text view wrapping. It has no runtime persistence; user configuration persistence is handled by `confdata.c`.

## Dependencies and Integration Points

It must remain synchronized with the object IDs expected by `gconf.c`. GTK stock IDs and deprecated widget names indicate it targets older GTK 3 compatibility. It is located through `SRCTREE` or an executable-relative path in `gconf.c`.

## Risks and Edge Cases

Renaming an object ID silently breaks callback wiring because `gtk_builder_get_object()` may return NULL and later GTK calls can fail. UI changes must preserve the two-tree plus help-pane structure assumed by the C code. Deprecated GTK constructs can create portability warnings or future compatibility issues.

## Test Signals

Load the file with GtkBuilder, launch `gconfig`, verify all menu items and toolbar buttons are connected, switch option radio modes, toggle visible columns, and confirm tree/help panes resize without missing widget warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/gconf.ui -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/internal.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/internal.h

## Purpose

`internal.h` declares non-public shared state for the kconfig implementation: symbol and expression hash tables, iteration helpers, expression cache invalidation, current parser/menu pointers, and current source location.

## Important APIs, Types, and Functions

Key definitions are `SYMBOL_HASHSIZE`, `EXPR_HASHSIZE`, `HASHTABLE_DECLARE(sym_hashtable, ...)`, `HASHTABLE_DECLARE(expr_hashtable, ...)`, `for_all_symbols(sym)`, `expr_invalidate_all()`, `current_menu`, `current_entry`, `cur_filename`, and `cur_lineno`.

## Control Flow

No runtime flow is implemented. The header enables global traversal and coordination between parser, menu construction, expression interning, symbol evaluation, and config persistence.

## State and Persistence Behavior

It declares process-global in-memory state only. The hash tables are the authoritative registries for symbols and expressions; parser globals identify where new menu entries/properties are being attached.

## Dependencies and Integration Points

It includes `hashtable.h` and is used by `confdata.c`, `expr.c`, `menu.c`, symbol code, and parser/lexer components that need implementation internals not exposed through `lkc.h`.

## Risks and Edge Cases

The globals make kconfig effectively single-context and not thread-safe. Changing hash sizes or traversal macro semantics affects all symbols/expressions. Parser location globals must be kept accurate by the lexer or diagnostics and property locations become misleading.

## Test Signals

Compile all kconfig tools and run parser tests involving nested includes, warnings, symbol traversal, and expression cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lexer.l -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lexer.l

## Purpose

`lexer.l` is the flex scanner for Kconfig syntax. It tokenizes keywords, operators, words, quoted strings, assignments, help text, variable expansion, and source-file inclusion while maintaining parser-facing file and line state.

## Important APIs, Types, and Functions

Generated scanner entry is wrapped by `yylex()`, which calls `yylex1()` and normalizes statement newlines. Public helpers are `zconf_starthelp()`, `zconf_fopen()`, `zconf_initscan()`, and `zconf_nextfile()`. Internal helpers include `new_string()`, `append_string()`, `alloc_string()`, `expand_token()`, `append_expanded_string()`, `zconf_endhelp()`, and `zconf_endfile()`. `struct buffer` stores include-stack state.

## Control Flow

The scanner uses start states `INITIAL`, `ASSIGN_VAL`, `HELP`, and `STRING`. Top-level rules ignore comments/whitespace, emit tokens for Kconfig keywords and operators, expand `$` tokens, and warn on unsupported characters. `STRING` removes escape backslashes and expands `$...`. `HELP` preserves indentation relative to the first help line. `yylex()` suppresses repeated end-of-line tokens, records `cur_lineno` at statement start, and enters `ASSIGN_VAL` after top-level variable assignment operators. EOF either pops an included file buffer or terminates scanning.

## State and Persistence Behavior

The lexer owns current source filename/line globals, previous-token tracking, temporary string buffers, help indentation state, and the include stack. It does not persist files, but it opens Kconfig and sourced files using current directory or `$srctree`.

## Dependencies and Integration Points

It includes `lkc.h`, `preprocess.h`, and `parser.tab.h`. It feeds the bison parser, uses preprocessing helpers for variable expansion, and uses `file_lookup()` for stable filename records.

## Risks and Edge Cases

Missing source files and recursive inclusion call `exit(1)`, so callers cannot recover. `zconf_nextfile()` compares include names against stored filenames, which makes path normalization important. Multi-line strings are warned and truncated back to parser flow. Help indentation is stateful and sensitive to tabs. Unsupported characters are warnings rather than fatal errors.

## Test Signals

Parser tests should cover variables, quoted strings, escaped newlines, help indentation, no-newline-at-EOF warnings, missing include errors, recursive include errors, `$srctree` lookup, and preprocessing expansion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lkc.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lkc.h

## Purpose

`lkc.h` is the main internal public header for kconfig C sources. It ties together `expr.h`, generated prototypes, lexer/parser entry points, string-buffer utilities, menu APIs, and symbol APIs.

## Important APIs, Types, and Functions

It defines `SRCTREE`, the runtime `CONFIG_` prefix via `CONFIG_prefix()`, `xfwrite()`, and `struct gstr`. It declares parser/lexer hooks (`zconfdump()`, `zconf_starthelp()`, `zconf_fopen()`, `zconf_initscan()`, `zconf_nextfile()`, `yylex()`), file lookup, string builder functions, menu traversal/finalization/help functions, root menu state, and symbol helper functions such as `sym_clear_all_valid()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_get_range_prop()`, and inline choice/value predicates.

## Control Flow

This header supplies inline helpers and macros rather than full algorithms. `menu_for_each_entry()` expands into depth-first traversal using `menu_next()`. `xfwrite()` centralizes fwrite error reporting for expression/config printing.

## State and Persistence Behavior

It declares shared state such as `rootmenu`, `autoconf_cmd`, and parser line globals. It does not persist data directly, but its APIs are used by config persistence and UI frontends.

## Dependencies and Integration Points

Every major kconfig source includes this header. It bridges `confdata.c`, `expr.c`, `menu.c`, `symbol.c`, parser/lexer code, and `mconf`/`gconf` frontends. `CONFIG_` may be overridden by the environment, and code using the macro must tolerate a function-like runtime prefix.

## Risks and Edge Cases

The `CONFIG_` macro is redefined to call `CONFIG_prefix()`, so it is not a string literal in all contexts. `xfwrite()` asserts nonzero element length but only prints on error. Inline choice checks rely on the null-name convention from `expr.h`.

## Test Signals

Compile all tools with default and overridden `CONFIG_`, run menu traversal/help generation, and exercise frontends that include this shared header from C and C++ compilation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lkc_proto.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lkc_proto.h

## Purpose

`lkc_proto.h` centralizes function prototypes for config persistence, symbol manipulation, and expression printing that are consumed through `lkc.h`.

## Important APIs, Types, and Functions

It declares `conf_parse()`, `conf_read()`, `conf_read_simple()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, dirty/message callbacks, `conf_errors()`, symbol lookup/search/value setters, choice setters, string validation, changeability checks, menu lookup helpers, `sym_get_string_value()`, `prop_get_type_name()`, and `expr_print()`.

## Control Flow

No executable flow exists in the header. It defines the callable surface used by command-line and UI frontends to parse Kconfig, read/write configuration, search symbols, and mutate user selections.

## State and Persistence Behavior

The declared functions operate on the global kconfig symbol/menu/expression state and the `.config`/generated-file state owned by `confdata.c`.

## Dependencies and Integration Points

It requires types from `expr.h` and `stdarg.h`. It is included by `lkc.h`, making it a central integration point between parser, symbol, expression, persistence, and frontend implementations.

## Risks and Edge Cases

Prototype drift breaks all tools at compile time. Several setters return `bool` for success/failure and frontends must honor those results to avoid displaying invalid state as accepted. `conf_parse()` is declared here but implemented outside this subset.

## Test Signals

Compile coverage, frontend load/save/edit paths, regex symbol search, and invalid string/tristate setter behavior are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lkc_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/checklist.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/checklist.c

## Purpose

`lxdialog/checklist.c` implements the ncurses radiolist/checklist dialog used by `mconf` for choice menus. In this kconfig usage, it presents one selectable item plus a Help button.

## Important APIs, Types, and Functions

The exported function is `dialog_checklist()`. Internal helpers are `print_item()`, `print_arrows()`, and `print_buttons()`. It consumes the global item list API from `dialog.h`/`util.c` (`item_foreach()`, `item_set()`, `item_set_selected()`, `item_is_tag()`, `item_str()`, and related helpers).

## Control Flow

`dialog_checklist()` chooses an initial item from the active or preselected tag, sizes and centers the dialog, creates a list subwindow, renders items and scroll arrows, and enters a key loop. Arrow keys and `+`/`-` move or scroll; hotkeys jump within visible rows; `s`, space, or Enter marks the current item selected and returns the current button; `h`/`?` returns Help; resize recreates the dialog; ESC is passed through `on_key_esc()`.

## State and Persistence Behavior

It uses static layout fields `list_width`, `check_x`, and `item_x`, and mutates selection flags in the global dialog item list. It has no file persistence.

## Dependencies and Integration Points

It depends on ncurses, global `dlg` theme colors, drawing helpers from `util.c`, and the item list built by `mconf` before calling `dialog_checklist()`.

## Risks and Edge Cases

Small terminals return `-ERRDISPLAYTOOSMALL`. Long labels are truncated to `list_width - item_x`. It allocates a temporary string for each printed item; allocation failure is not checked. Because selection is stored globally, callers must `item_reset()` before building each list.

## Test Signals

Exercise choices with no default, default selected item, comments, long labels, hotkeys, scrolling, Help, resize, small terminal failure, and ESC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/checklist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/dialog.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/dialog.h

## Purpose

`lxdialog/dialog.h` is the common declaration header for the ncurses dialog toolkit used by `mconf`. It defines shared key constants, minimum sizes, color/theme structures, global dialog state, item-list structures, and widget function prototypes.

## Important APIs, Types, and Functions

Important constants include `KEY_ESC`, `TAB`, `MAX_LEN`, `BUF_SIZE`, `ERRDISPLAYTOOSMALL`, and per-widget minimum dimensions. Key types are `struct dialog_color`, `struct subtitle_list`, `struct dialog_info`, `struct dialog_item`, and `struct dialog_list`. It declares global `dlg`, `dialog_input_result`, `saved_x`, `saved_y`, item-list APIs, drawing helpers, generic key handlers, lifecycle functions, and dialog functions such as `dialog_yesno()`, `dialog_textbox()`, `dialog_menu()`, `dialog_checklist()`, and `dialog_inputbox()`.

## Control Flow

No runtime flow is implemented. The header establishes the call contract between `mconf.c` and lxdialog implementation files.

## State and Persistence Behavior

It exposes process-global UI state: theme colors, backtitle/subtitles, input buffer, saved cursor coordinates, and the current linked list of menu items. There is no file persistence.

## Dependencies and Integration Points

It includes system headers and `<ncurses.h>`, with ACS fallback macros for terminals or curses variants missing line-drawing constants. `mconf.c` includes it directly and relies on the return-code convention of each dialog.

## Risks and Edge Cases

The shared item list and input buffer are global and not reentrant. `dialog_msgbox()` is prototyped here but not implemented in the files in this subset, so either another object provides it or the prototype is legacy. Static buffer sizes cap input and displayed line lengths.

## Test Signals

Compile/link `mconf`, verify no unresolved dialog symbols, run all dialog types, and test terminal variants with missing ACS macros, small sizes, resize events, ESC handling, and long strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/dialog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/inputbox.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/inputbox.c

## Purpose

`lxdialog/inputbox.c` implements the ncurses input dialog used by `mconf` for string, int, hex, load-file, save-file, and search-entry prompts.

## Important APIs, Types, and Functions

The exported function is `dialog_inputbox()`, and the global output buffer is `dialog_input_result[MAX_LEN + 1]`. `print_buttons()` renders Ok and Help controls.

## Control Flow

The dialog copies the initial value into `dialog_input_result`, draws the prompt, input field, and buttons, then processes keyboard input. When the input field is active, printable characters insert at the cursor, backspace deletes, left/right move with horizontal scrolling, and max length is enforced with `flash()`. Tab and arrow keys cycle focus between input, Ok, and Help. `o`/Enter/space return success, `h` returns Help, resize redraws, and ESC exits through `on_key_esc()`.

## State and Persistence Behavior

Input persists only in the global `dialog_input_result` buffer until the next input dialog. Cursor position, visible horizontal offset, and selected button are local state. There is no file persistence.

## Dependencies and Integration Points

It depends on ncurses drawing helpers and theme attributes from `util.c`. `mconf.c` reads `dialog_input_result` after return and validates through `sym_set_string_value()`, `conf_read()`, `conf_write()`, or search APIs.

## Risks and Edge Cases

Input is byte-oriented and limited to `MAX_LEN`, so multibyte terminal input may not behave as a user expects. The code manually redraws the field and must keep `pos`, `len`, `input_x`, and `show_x` consistent. Small terminals return `-ERRDISPLAYTOOSMALL`.

## Test Signals

Test insertion/deletion in middle of text, long input horizontal scrolling, empty input, Help, load/save filenames, invalid symbol values, resize, ESC, and terminal small-size returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/inputbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/menubox.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/menubox.c

## Purpose

`lxdialog/menubox.c` implements the main ncurses menu dialog for `mconf`, including scrolling lists, hotkeys, command buttons, and kconfig-specific key returns for Y/N/M/search/show-all actions.

## Important APIs, Types, and Functions

The exported API is `dialog_menu()`. Internal helpers include `do_print_item()`, `print_arrows()`, `print_buttons()`, and `do_scroll()`. It reads items from the global dialog item list and returns numeric action codes consumed by `mconf.c`.

## Control Flow

`dialog_menu()` sizes the dialog from current terminal geometry, creates a menu subwindow, chooses the initial item based on a selected menu pointer and saved scroll offset, renders visible rows, and enters a key loop. Arrow, page, `+`, `-`, and hotkey navigation update `choice` and `scroll`. Enter returns the active button. Direct keys map to actions: `y`/`s` set yes, `n` set no, `m` set module, space toggles, `/` searches, `z` toggles hidden options, `h`/`?` shows help, and ESC exits. Resize rebuilds from scratch.

## State and Persistence Behavior

Static `menu_width` and `item_x` hold layout. The caller-owned `s_scroll` stores scroll position across invocations. Current selection is written into the global item list. No filesystem state is touched.

## Dependencies and Integration Points

It depends on ncurses, lxdialog theme/drawing helpers, and the item list populated by `mconf build_conf()`. Return codes are tightly coupled to the switch in `mconf.c::conf()`.

## Risks and Edge Cases

Menu labels are truncated to fit; hotkey detection skips bracketed option state and exempt letters. The return-code protocol is numeric and implicit. Very small terminals return `-ERRDISPLAYTOOSMALL`. Callers must reset item state and preserve `s_scroll` appropriately.

## Test Signals

Exercise large menus, page scrolling, preserved scroll after returning from submenus, hotkeys, Y/N/M/space actions, search key, show-all key, resize handling, small terminal failure, and empty item lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/menubox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/textbox.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/textbox.c

## Purpose

`lxdialog/textbox.c` implements the scrollable ncurses text viewer used by `mconf` for help, README, search results, and status messages.

## Important APIs, Types, and Functions

The exported function is `dialog_textbox()`. Internal helpers are `back_lines()`, `get_line()`, `print_line()`, `print_page()`, `print_position()`, and `refresh_text_box()`. Optional callback `extra_key_cb` lets search results handle jump-key navigation.

## Control Flow

The dialog initializes page pointers and optional saved vertical/horizontal scroll, sizes and draws the window, renders a page, then processes movement keys. Home/end, vi-style keys, arrows, page up/down, space, and horizontal scroll keys adjust `page` and `hscroll`; ESC exits through `on_key_esc()`. Unknown keys are offered to `extra_key_cb`, which can request dialog exit. On close, optional scroll pointers are updated for caller reuse.

## State and Persistence Behavior

Static file-local state tracks current buffer, page pointer, scroll offsets, page length, and visible start/end offsets. It persists only during the dialog call, except scroll offsets returned to the caller.

## Dependencies and Integration Points

It uses ncurses drawing helpers and theme colors. `mconf` uses it directly for help/search and passes `handle_search_keys()` from `mnconf-common.c` to make numbered search jump entries actionable.

## Risks and Edge Cases

Line buffers are capped at `MAX_LEN`, so very long lines are truncated for display. Percent calculation divides by `strlen(buf)` and expects non-null text; an empty buffer can be risky. Scrolling is pointer-based, so newline accounting is important when preserving positions. Resize rebuilds and backs up by the old height.

## Test Signals

Test empty and long text, long single lines, vertical and horizontal scrolling, saved scroll restoration, jump-key callbacks, resize, ESC, first/last page, and terminal sizes near minimum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/textbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/util.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/util.c

## Purpose

`lxdialog/util.c` provides shared ncurses infrastructure for `mconf`: theme selection, color initialization, screen clearing, dialog lifecycle, drawing primitives, ESC/resize handling, and the global linked list of dialog items.

## Important APIs, Types, and Functions

Public functions include `init_dialog()`, `set_dialog_backtitle()`, `set_dialog_subtitles()`, `end_dialog()`, `attr_clear()`, `dialog_clear()`, `print_title()`, `print_autowrap()`, `print_button()`, `draw_box()`, `draw_shadow()`, `first_alpha()`, `on_key_esc()`, `on_key_resize()`, `item_reset()`, `item_make()`, `item_add_str()`, `item_set_tag()`, `item_set_data()`, `item_set_selected()`, `item_activate_selected()`, `item_data()`, `item_tag()`, `item_count()`, `item_set()`, `item_n()`, `item_str()`, `item_is_selected()`, and `item_is_tag()`. Internal theme helpers configure mono, classic, black background, and blue-title themes.

## Control Flow

`init_dialog()` starts curses, saves cursor position, validates minimum terminal size, configures theme/color from `MENUCONFIG_COLOR`, enables keypad/cbreak/noecho, and clears the screen. Drawing functions are called by every widget. `on_key_esc()` temporarily disables keypad and drains pending bytes to distinguish standalone ESC from escape sequences. Item-list functions build and traverse a simple linked list that dialog widgets render.

## State and Persistence Behavior

Global state includes `saved_x`, `saved_y`, `dlg`, `item_head`, `item_cur`, and `item_nil`. Theme and subtitle state persist for the life of the dialog session. No files are written.

## Dependencies and Integration Points

It depends on ncurses and is linked into `mconf` with all other lxdialog widgets. `mconf.c` uses `saved_x/saved_y` during signal exit, supplies backtitles/subtitles, and repeatedly rebuilds the item list before menus/checklists.

## Risks and Edge Cases

The item list uses unchecked `malloc()` and fixed-size item strings. Global state makes the library non-reentrant. `print_autowrap()` copies prompts into a fixed buffer, truncating long prompts. Color-pair numbering assumes enough curses color pairs. ESC handling is delicate because terminal escape sequences and user double-ESC share input timing.

## Test Signals

Run menuconfig under supported color themes, monochrome/limited terminals, small terminals, terminal resize, ESC/double-ESC, long prompts/items, repeated menu rebuilds with leak checks, and signal-triggered exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/yesno.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/yesno.c

## Purpose

`lxdialog/yesno.c` implements the two-button confirmation dialog used by `mconf`, most importantly for the exit/save prompt.

## Important APIs, Types, and Functions

The exported function is `dialog_yesno()`. Internal `print_buttons()` renders Yes and No through the shared `print_button()` helper.

## Control Flow

`dialog_yesno()` validates terminal size, centers and draws the dialog, prints the prompt and buttons, and loops for key input. `y` returns 0, `n` returns 1, Tab/left/right toggles the selected button, Enter/space returns the selected button, resize redraws, and ESC exits through `on_key_esc()`.

## State and Persistence Behavior

All state is local to the call except shared theme/backdrop state from `dlg`. It has no persistence.

## Dependencies and Integration Points

It uses ncurses and drawing/key helpers from `util.c`. `mconf.c::handle_exit()` interprets return 0 as save, 1 as discard, and `KEY_ESC` as continue configuration.

## Risks and Edge Cases

Return-code meaning is caller convention, so changes must be coordinated with `mconf`. Small terminal sizes return `-ERRDISPLAYTOOSMALL`, which callers should treat intentionally. Prompt wrapping depends on the fixed dialog dimensions passed by the caller.

## Test Signals

Test y/n shortcuts, selected-button return, ESC/double-ESC, resize, small terminal return, and integration with menuconfig exit flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/yesno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mconf-cfg.sh -->
# sources/distributed-fs/ceph-client/scripts/kconfig/mconf-cfg.sh

## Purpose

`mconf-cfg.sh` is the build-time probe for the `menuconfig` ncurses frontend. It discovers usable ncurses compiler and linker flags and writes them to caller-provided files.

## Important APIs, Types, and Functions

The script accepts output files `cflags` and `libs`. It probes `HOSTPKG_CONFIG` packages `ncursesw` then `ncurses`, checks default include directories `/usr/include/ncursesw` and `/usr/include/ncurses`, and finally asks `${HOSTCC} -E` whether `<ncurses.h>` is available.

## Control Flow

With `set -eu`, it first prefers pkg-config if available, then filesystem fallbacks, then a compiler preprocessor fallback. On success it writes flags and exits 0. On failure it prints package-install guidance and exits 1.

## State and Persistence Behavior

It creates or overwrites only the generated cflags/libs files passed by the build. It does not write source or user configuration files.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile before building `mconf`. It depends on `HOSTPKG_CONFIG` when available and `HOSTCC` for the final fallback.

## Risks and Edge Cases

`set -u` makes unset `HOSTPKG_CONFIG` or `HOSTCC` hazardous depending on the path taken. Library detection is intentionally simple and may miss sysroot or nonstandard installs if neither pkg-config nor `HOSTCC` exposes them. The fallback links plain `-lncurses`, not menu/panel libraries, because `mconf` uses only base ncurses.

## Test Signals

Test with ncursesw pkg-config, ncurses pkg-config, no pkg-config but standard headers, sysroot compiler fallback, and complete absence of ncurses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mconf-cfg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mconf.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/mconf.c

## Purpose

`mconf.c` implements the terminal `menuconfig` frontend. It traverses the shared kconfig menu tree, renders menus via lxdialog, edits symbol values, shows help/search results, loads/saves alternate config files, and handles exit/save behavior.

## Important APIs, Types, and Functions

Important functions are `set_config_filename()`, `set_subtitle()`, `reset_subtitle()`, `show_textbox_ext()`, `show_help()`, `search_conf()`, `build_conf()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `conf()`, `conf_message_callback()`, `handle_exit()`, `sig_handler()`, and `main()`. Process-global state tracks current filename, subtitle trail, current menu, indentation, child count, single-menu mode, show-all mode, save-and-exit, and silent mode.

## Control Flow

`main()` parses optional silent mode, parses Kconfig, reads `.config`, initializes curses, installs config/message callbacks, then enters `conf(&rootmenu)`. `conf()` rebuilds the lxdialog item list from visible menu nodes, invokes `dialog_menu()`, and interprets returned actions. It descends into menus, opens choices, edits string/int/hex values, applies Y/N/M/toggle to tristate symbols, opens search/help dialogs, toggles hidden options, or loads/saves configs. `handle_exit()` prompts to save when dirty, writes `.config`, writes autoconf output, ends curses, and prints final status.

## State and Persistence Behavior

UI state is global and session-scoped: subtitle trail, single-menu expanded flags in `menu->data`, scroll positions, and current filename. Persistent behavior is delegated to `conf_read()`, `conf_write()`, and `conf_write_autoconf()`. `sig_handler()` exits through `handle_exit()` so SIGINT still offers save behavior.

## Dependencies and Integration Points

It depends on `lkc.h`, `lxdialog/dialog.h`, `mnconf-common.h`, locale/signal/system headers, and the menu/symbol/conf APIs. `MENUCONFIG_MODE=single_menu` changes navigation. `MENUCONFIG_COLOR` is consumed by lxdialog initialization.

## Risks and Edge Cases

The numeric return contract with `menubox.c` is implicit and fragile. Signal handling calls complex UI/save logic from a signal context, which is historically accepted here but not async-signal-safe. `build_conf()` relies on `menu_is_visible()` recalculation side effects. `single_menu_mode` stores booleans in `menu->data`, sharing a field that other frontends could also use in the same process.

## Test Signals

Run `menuconfig` through navigation, Y/N/M/toggle edits, choice menus, string/int/hex validation, search and jump keys, load/save alternate config, dirty exit save/discard/cancel, single-menu mode, show-all toggle, silent mode, SIGINT, resize, and small terminal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/menu.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/menu.c

## Purpose

`menu.c` builds, finalizes, validates, traverses, and describes the shared kconfig menu tree. It is the bridge between parser-created raw entries and frontend-ready menu structures with inherited dependencies, visibility, selects/implies, automatic submenus, and help/search text.

## Important APIs, Types, and Functions

Public APIs include `menu_next()`, `menu_warn()`, `_menu_init()`, `menu_add_entry()`, `menu_add_menu()`, `menu_end_menu()`, `menu_add_dep()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_visibility()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_finalize()`, `menu_has_prompt()`, `menu_is_empty()`, `menu_is_visible()`, `menu_get_prompt()`, `menu_get_parent_menu()`, `menu_get_menu_or_parent_menu()`, `get_jump_key_char()`, `get_relations_str()`, `menu_get_ext_help()`, and `menu_dump()`. Internal helpers validate properties and format symbol/location/dependency strings.

## Control Flow

During parsing, `_menu_init()` sets the root insertion point, and `menu_add_*()` functions append entries and properties under `current_menu`. `menu_finalize()` recursively propagates parent dependencies, rewrites literal `m` to depend on `MODULES`, simplifies expressions, records reverse dependencies for `select`/`imply`, creates automatic submenus for consecutive dependents, flattens promptless/if nodes, and warns about invalid types/properties. Runtime frontends then use `menu_is_visible()`, traversal helpers, and help-generation functions.

## State and Persistence Behavior

The file owns `rootmenu` and parser build pointers (`current_menu`, `current_entry` are declared in `internal.h`). It mutates symbol dependency fields (`dir_dep`, `rev_dep`, `implied`), menu parent/list/next links, prompt visibility, flags, and frontend jump-key records. It does not write files.

## Dependencies and Integration Points

It depends on `expr.c` for dependency transformations, `symbol.c` for symbol typing/value/default helpers, parser globals from the lexer, list helpers, and `gstr` string utilities. `mconf` and `gconf` depend on its visibility, help, search relation, and parent-menu APIs.

## Risks and Edge Cases

Automatic submenu creation is subtle and can change frontend structure without explicit `menu` blocks. Flattening promptless nodes rewrites tree links, so stale parent/list assumptions are dangerous during finalization. Select/imply expressions must include the selecting symbol and condition or dependency diagnostics become wrong. `menu_is_visible()` has side effects through symbol calculation and prompt visibility caching.

## Test Signals

Parser tests for auto submenu, conditional dependencies, visible-if, select/imply, invalid ranges/defaults, unknown types, choice defaults, prompt redefinition warnings, help/search relation text, and tree dump shape are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/menu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/merge_config.sh -->
# sources/distributed-fs/ceph-client/scripts/kconfig/merge_config.sh

## Purpose

`merge_config.sh` merges a base config and one or more config fragments, warns about overrides/redundancy/effective-value mismatches, optionally enforces strict mode, and optionally runs `make` to expand the merged fragment through Kconfig defaults.

## Important APIs, Types, and Functions

The script exposes options `-m`, `-n`, `-r`, `-y`, `-O`, `-s`, `-Q`, and `-h`. Internal shell variables include `RUNMAKE`, `ALLTARGET`, `WARNREDUN`, `BUILTIN`, `OUTPUT`, `STRICT`, `CONFIG_PREFIX`, `WARNOVERRIDE`, `KCONFIG_CONFIG`, `TMP_FILE`, and `PROCESSED_FILES`. AWK blocks implement config-name extraction, override warnings, strict detection, builtin-demotion prevention, redundant warnings, and final effective-config comparison.

## Control Flow

After option parsing and `KCONFIG_CONFIG` setup, the script copies the base file to a temp file. For each fragment, it validates readability, warns on duplicate input, uses AWK to remove overridden base entries while appending the fragment, honors `-y` by preserving `=y` over incoming `=m`, and records strict violations. With `-m`, it writes the merged temp config directly. Otherwise it runs `make KCONFIG_ALLCONFIG=$TMP_FILE ... alldefconfig` or `allnoconfig`, then AWK-compares requested values against the final `.config`.

## State and Persistence Behavior

It creates temporary `.tmp.config.*` files in the current directory and removes them through a trap. It writes the target `$KCONFIG_CONFIG` either directly in merge-only mode or indirectly through `make`. It may use `readlink -m` for `-O` output paths.

## Dependencies and Integration Points

It depends on POSIX shell plus common utilities `mktemp`, `cp`, `mv`, `readlink`, `make`, and `awk` (or `$AWK`). It integrates with Kconfig targets via `KCONFIG_ALLCONFIG`, `KCONFIG_CONFIG`, and optional `O=`.

## Risks and Edge Cases

`STRICT_MODE_VIOLATED` is read before explicit initialization in some shells when no violation occurred; because the script does not use `set -u`, this is tolerated. Fragment iteration uses unquoted `$MERGE_LIST`, so filenames with whitespace are unsupported. AWK matching is line-oriented and intentionally limited to `CONFIG_*` and `# CONFIG_* is not set` forms. `-O` requires an existing directory.

## Test Signals

Test override warnings, strict failures, duplicate fragments, redundant warnings, `-Q`, `-y` demotion prevention, `-m`, `-n`, custom `CONFIG_` prefix, output directory behavior, missing fragment/base file handling, and final mismatch warnings for unmet dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/merge_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.c

## Purpose

`mnconf-common.c` provides shared search-result jump-key handling for menuconfig-style ncurses frontends.

## Important APIs, Types, and Functions

It defines global `jump_key_char` and implements `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`. It consumes `struct search_data` and `struct jump_key` lists.

## Control Flow

`get_jump_key_char()` cycles jump labels through `1` to `9`. `handle_search_keys()` receives a pressed key plus the visible text range from `dialog_textbox()`, scans jump entries whose offsets are visible, and when the key matches the visible ordinal it stores the target menu and returns 1 to close the textbox for navigation.

## State and Persistence Behavior

Only `jump_key_char` persists between calls; `mconf` resets it before rendering search results. No files are read or written.

## Dependencies and Integration Points

It depends on list iteration from `list.h`, expression/menu types from `expr.h`, and declarations in `mnconf-common.h`. `menu.c` calls weak/overridden `get_jump_key_char()` during relation-string generation, while `mconf.c` uses `handle_search_keys()` as a textbox callback.

## Risks and Edge Cases

Only nine jump keys are available per visible page. Offsets must match the generated `gstr` exactly; changes in help formatting can affect jump behavior. The implementation assumes callers reset `jump_key_char` at appropriate boundaries.

## Test Signals

Search results with more than nine matches, scrolled results, hidden/non-visible offsets, repeated searches, and jump-to-location behavior from `mconf` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.h

## Purpose

`mnconf-common.h` declares shared data and functions for ncurses frontend search jump-key support.

## Important APIs, Types, and Functions

It defines `struct search_data` with a jump-entry list head and selected target menu pointer. It declares `jump_key_char`, `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`.

## Control Flow

No flow is implemented in the header. It gives `mconf.c`, `mnconf-common.c`, and menu help generation a common contract for numbered search-result navigation.

## State and Persistence Behavior

The header exposes only process-global jump-key state. It has no persistence.

## Dependencies and Integration Points

It includes `stddef.h` and `list_types.h`, and forward-uses `struct menu` through the pointer in `struct search_data`. It is included by `mconf.c` and `mnconf-common.c`.

## Risks and Edge Cases

Any change to `struct search_data` must be coordinated with the textbox callback and search-result generation. The global jump-key counter remains non-reentrant.

## Test Signals

Compile coverage and menuconfig search/jump behavior are sufficient signals for this small header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf-cfg.sh -->
# sources/distributed-fs/ceph-client/scripts/kconfig/nconf-cfg.sh

## Purpose

`nconf-cfg.sh` is the build-time probe for the `nconfig` frontend. It discovers ncurses menu, panel, and curses libraries and writes host compiler/linker flags for the build.

## Important APIs, Types, and Functions

The script accepts `cflags=$1` and `libs=$2`. It probes pkg-config packages `menuw panelw ncursesw`, then `menu panel ncurses`, then standard include directories for wide and non-wide ncurses, and finally `/usr/include/ncurses.h`.

## Control Flow

With `set -eu`, the script prefers pkg-config and preserves library order for static linking. If pkg-config cannot find packages, it writes fallback include and library flags based on header locations. On failure it prints install guidance and exits 1.

## State and Persistence Behavior

It writes only generated cflags/libs files supplied by the caller and does not touch configs or source files.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile for `nconfig`. It depends on `HOSTPKG_CONFIG` if available and ncurses menu/panel development libraries.

## Risks and Edge Cases

`set -u` means unset build variables can abort. Unlike `mconf-cfg.sh`, there is no compiler-preprocessor fallback. Nonstandard sysroots require pkg-config or matching standard header paths. Static link order is intentionally encoded and should not be reordered casually.

## Test Signals

Test pkg-config wide and non-wide library paths, standard include fallback paths, static host compiler linking, missing package diagnostics, and successful `nconfig` build/link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf-cfg.sh -->
