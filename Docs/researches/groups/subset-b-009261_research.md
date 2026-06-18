# sources/test-tools/kdevops scripts and kconfig research: subset-b-009261

Grouped research report for work item `subset-b-009261`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mconf.c -->
# sources/test-tools/kdevops/scripts/kconfig/mconf.c

## Purpose
`mconf.c` implements the classic `menuconfig` terminal user interface for the vendored Linux Kconfig engine. It parses a Kconfig tree, loads the active `.config`, renders menus through `lxdialog`, lets users toggle symbols or enter string/int/hex values, supports symbol search, and writes `.config` plus generated autoconf output when the user exits.

## Important APIs, Types, And Functions
The UI is built around Kconfig `struct menu`, `struct symbol`, `struct property`, and `struct gstr` objects from `lkc.h`, plus the local search helpers in `mnconf-common.h`. Key functions are `main()`, `conf()`, `build_conf()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `search_conf()`, `show_help()`, `handle_exit()`, and `conf_message_callback()`. Global UI state includes `filename`, `indent`, `current_menu`, `child_count`, `single_menu_mode`, `show_all_options`, `save_and_exit`, `silent`, and a subtitle trail list.

## Control Flow
`main()` optionally enables silent mode, calls `conf_parse()` and `conf_read()`, checks `MENUCONFIG_MODE=single_menu`, initializes the dialog library, sets the config filename/backtitle, installs a Kconfig message callback, and repeatedly calls `conf(&rootmenu, NULL)` until exit is accepted. `conf()` rebuilds menu items with `build_conf()`, calls `dialog_menu()`, dispatches button/action return codes, and recurses into submenus or specialized editors. `build_conf()` filters invisible nodes unless show-all is enabled, formats menu items according to symbol type and dependency state, and recursively emits child entries. Search uses `sym_re_search()`, `get_relations_str()`, `handle_search_keys()`, and jump-key callbacks to move from results into the menu tree.

## State And Persistence
Interactive state is process-local: subtitle list, current menu path, scroll position, single-menu expansion stored in `menu->data`, and `show_all_options`. Persistent state is configuration data read through `conf_read()`, modified through `sym_set_*()`/`choice_set_value()`, saved via `conf_write()`, and finalized through `conf_write_autoconf(0)`. Alternate load/save dialogs can switch `filename` to a different config path.

## Dependencies And Integration Points
This file depends on the Kconfig core (`conf_parse`, `conf_read`, symbol/menu APIs), `lxdialog` widgets, ncurses through the dialog layer, `list.h`, `xalloc.h`, and shared search jump helpers from `mnconf-common.c`. It is normally built by Kconfig make rules as the `mconf` frontend and consumed through `make menuconfig`-style targets.

## Risks And Edge Cases
Terminal size and dialog initialization failures prevent use. User input validation depends on `sym_set_string_value()` and `sym_set_tristate_value()`, so dependency logic errors surface here as unchangeable or rejected options. Search allocates relation strings and jump entries per loop and must free them on every path. The local source contains duplicated text in `search_help` and a duplicated `if (sym->rev_dep.tri == mod)` line in the tristate renderer; these are likely copy artifacts and should be checked against upstream before changing behavior.

## Test Signals
Useful checks include building `mconf`, running it on a small Kconfig with bool/tristate/string/choice/menu entries, toggling `MENUCONFIG_MODE=single_menu`, exercising search and jump keys, saving/loading alternate configs, verifying `-s` silent behavior, and confirming invalid int/hex/string input is rejected without corrupting `.config`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/menu.c -->
# sources/test-tools/kdevops/scripts/kconfig/menu.c

## Purpose
`menu.c` builds, finalizes, traverses, validates, and describes the in-memory Kconfig menu tree. It receives parse-time events from `parser.y`, attaches properties to symbols, propagates dependencies, creates automatic submenus, flattens promptless containers, validates symbol properties, and formats extended help/search relationship text used by `mconf` and `nconf`.

## Important APIs, Types, And Functions
Core exports include `_menu_init()`, `menu_add_entry()`, `menu_add_menu()`, `menu_end_menu()`, `menu_add_dep()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_visibility()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_finalize()`, `menu_next()`, `menu_is_visible()`, `menu_is_empty()`, `menu_get_prompt()`, `menu_get_parent_menu()`, `get_relations_str()`, and `menu_get_ext_help()`. Important globals are `rootmenu`, `current_menu`, `current_entry`, `last_entry_ptr`, and the weak `get_jump_key_char()` hook overridden by menu UIs.

## Control Flow
During parsing, `menu_add_entry()` appends a new `struct menu` under `current_menu`, `menu_add_menu()` descends into the current entry, and `menu_end_menu()` returns to the parent. Properties are appended to the owning symbol and current menu node. `menu_finalize()` recursively calls `_menu_finalize()`, which rewrites `m` dependencies through `MODULES`, applies parent dependencies to child menus and property visibility, records reverse dependencies for `select` and `imply`, creates automatic submenus for consecutive dependent nodes, flattens invisible/promptless containers, and validates type/default/select/range consistency. Runtime helpers evaluate prompt visibility and build relation/help text.

## State And Persistence
The file mutates the global menu tree and symbol property lists in memory. No disk persistence occurs directly, but finalized dependencies drive later `.config`, autoconf, search, and UI behavior. Search result jump keys allocate `struct jump_key` entries into a caller-provided list; callers own cleanup.

## Dependencies And Integration Points
`parser.y` is the primary producer of calls into this file. `symbol.c` consumes finalized dependencies and visibility. UI frontends consume `menu_is_visible()`, `menu_get_prompt()`, `menu_get_ext_help()`, and `get_relations_str()`. It depends on expression helpers (`expr_*`), symbols (`sym_*`), linked lists, hashtable-backed symbols indirectly, and `xalloc`.

## Risks And Edge Cases
Dependency propagation uses copied expressions in places to avoid shared-expression mutation; regressions here can silently alter Kconfig semantics. Automatic submenu creation is subtle and can restructure the tree based on expression superset checks. Property validation is warning-oriented for many cases, so invalid Kconfig may proceed. The local source shows a duplicated nested `prop_warn(prop,` fragment in `sym_check_prop()`, which appears syntactically suspicious and should be verified by compilation or upstream comparison.

## Test Signals
Test with Kconfig snippets covering nested `menu`, `if`, `visible if`, `depends on m`, duplicate types/prompts, ranges, `select`, `imply`, choice defaults, promptless symbols, automatic submenu creation, and search/help output. Build tests should catch the apparent duplicated `prop_warn` artifact.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/menu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/merge_config.sh -->
# sources/test-tools/kdevops/scripts/kconfig/merge_config.sh

## Purpose
`merge_config.sh` merges a base Kconfig `.config` with one or more fragment files, warns about overrides or redundant entries, optionally prevents `y` to `m` demotion, optionally runs a Kconfig make target to resolve defaults/dependencies, and reports requested values that do not survive into the final `.config`.

## Important APIs, Types, And Functions
This is a POSIX shell script. Functional units are `usage()`, `clean_up()`, option parsing, config-symbol extraction via two `sed` expressions, fragment merge loop, optional strict-mode failure, optional `make KCONFIG_ALLCONFIG=... alldefconfig|allnoconfig`, and final requested-versus-actual verification. Options include `-m`, `-n`, `-r`, `-y`, `-O`, `-s`, and `-Q`.

## Control Flow
The script initializes defaults, parses options, chooses `KCONFIG_CONFIG`, creates missing base files, creates temporary merge files, and copies the base into `TMP_FILE`. For each fragment it extracts symbols, detects prior values in the merged temp file, warns or marks strict violations on redefinition, handles `-y` by deleting the demoting value from the fragment instead of the previous built-in value, then appends the fragment. If `-m` is set it copies the merged file directly; otherwise it runs the selected Kconfig target and compares each requested symbol against the resulting config.

## State And Persistence
Temporary files are created in the current directory and removed by an EXIT trap. Persistent output is `KCONFIG_CONFIG`, defaulting to `.config` or `$OUTPUT/.config`. With `-O`, an `O=` make argument is passed and `readlink -m` is used to compute the config path.

## Dependencies And Integration Points
Depends on `/bin/sh`, `mktemp`, `sed`, `grep`, `readlink`, `cp`, and `make`. It is used by build automation that composes kernel/kdevops config fragments before invoking Kconfig resolution.

## Risks And Edge Cases
Many variable expansions are unquoted in `cat`, `grep`, and `sed` commands, so spaces or glob characters in file names can break behavior. Regex deletion with `sed -i "/$CFG[ =]/d"` relies on config symbol safety. `STRICT_MODE_VIOLATED` is only set dynamically. `-Q` sets `WARNOVERRIDE=true`, relying on shell `true` as a no-op command. Output directory handling assumes GNU `readlink -m`.

## Test Signals
Run merges with duplicate symbols, redundant symbols, `# CONFIG_FOO is not set`, `-m`, `-n`, `-s`, `-r`, `-y`, and `-O`. Include fragments whose requested values are rejected by dependencies and verify warnings. Test paths without special characters unless the script is hardened.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/merge_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mnconf-common.c -->
# sources/test-tools/kdevops/scripts/kconfig/mnconf-common.c

## Purpose
`mnconf-common.c` provides shared search-result jump-key behavior for the `mconf` and `nconf` Kconfig UIs. It cycles numeric jump labels from `1` through `9` and maps numeric key presses in visible search result ranges back to menu targets.

## Important APIs, Types, And Functions
Exports are `next_jump_key(int key)`, `handle_search_keys(int key, size_t start, size_t end, void *data)`, `get_jump_key_char(void)`, and global `int jump_key_char`. It uses `struct search_data` and `struct jump_key` from Kconfig headers/list types.

## Control Flow
`next_jump_key()` normalizes non-numeric or out-of-range input to `'1'`, increments numeric keys, and wraps after `'9'`. `get_jump_key_char()` advances the global jump key and returns it. `handle_search_keys()` rejects non-numeric input, then walks `data->head`, assigns the same cyclic index sequence used for rendering, ignores jump offsets before the current viewport, stops at offsets after the viewport, and fills `data->target` when the pressed key matches.

## State And Persistence
Only `jump_key_char` is global process state. Search callers reset it to zero before rendering a result page. There is no persistence beyond process memory.

## Dependencies And Integration Points
Depends on `list.h`, `expr.h`, and `mnconf-common.h`. `menu.c` calls `get_jump_key_char()` while formatting search relation text. `mconf.c` and `nconf.c` call `handle_search_keys()` from scrollable search result dialogs.

## Risks And Edge Cases
The key labels repeat every nine visible jump targets, so ambiguous labels can occur in large result sets. Correctness depends on the offsets recorded in `get_prompt_str()` matching the text window viewport byte offsets passed by each UI.

## Test Signals
Search for a term with more than nine visible locations, scroll result windows, press numeric jump keys, and confirm the target menu opens only for locations visible in the current viewport.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mnconf-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mnconf-common.h -->
# sources/test-tools/kdevops/scripts/kconfig/mnconf-common.h

## Purpose
`mnconf-common.h` declares shared search navigation helpers used by both menuconfig frontends and by menu relation rendering.

## Important APIs, Types, And Functions
It defines `struct search_data { struct list_head *head; struct menu *target; }`, declares `extern int jump_key_char`, and prototypes `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`.

## Control Flow
The header has no control flow, but it establishes the callback contract: scrollable windows pass key input plus text viewport offsets and a `search_data` pointer; the implementation may set `target` and return nonzero to request a jump.

## State And Persistence
The shared global `jump_key_char` is process-local UI rendering state. No persistence is defined.

## Dependencies And Integration Points
Includes `<stddef.h>` and `<list_types.h>`. It forward-uses `struct menu` without defining it, relying on Kconfig consumers to include full menu declarations where needed.

## Risks And Edge Cases
The public global means multiple search renderers in the same process must reset and use it carefully. The callback data is untyped `void *` at call sites, so misuse can crash.

## Test Signals
Header-level validation is compile coverage for `mconf.c`, `nconf.c`, `menu.c`, and `mnconf-common.c`, plus runtime search jump behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/mnconf-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf-cfg.sh -->
# sources/test-tools/kdevops/scripts/kconfig/nconf-cfg.sh

## Purpose
`nconf-cfg.sh` detects compiler and linker flags needed to build the ncurses-based `nconf` frontend. It writes cflags and libs to output files provided as arguments.

## Important APIs, Types, And Functions
The script takes two positional arguments: output cflags path and output libs path. It checks `${HOSTPKG_CONFIG}` for `ncursesw menuw panelw`, then `ncurses menu panel`, then falls back to default include locations under `/usr/include`.

## Control Flow
With `set -eu`, the script first probes pkg-config. If wide-character ncurses packages exist, it writes their flags and exits. Otherwise it tries non-wide packages. If pkg-config is unavailable or unhelpful, it tests three header paths and emits hardcoded flags. On failure it prints installation guidance and exits nonzero.

## State And Persistence
Persistent output is limited to the two generated flag files. No temporary files or environment mutations are used.

## Dependencies And Integration Points
Depends on shell, `command -v`, optional pkg-config via `HOSTPKG_CONFIG`, and installed ncurses/menu/panel development headers/libraries. Build rules call this before compiling `nconf.c` and `nconf.gui.c`.

## Risks And Edge Cases
`HOSTPKG_CONFIG` is referenced under `set -u`; callers must define it or the script will fail. Positional arguments are not validated. Nonstandard ncurses installations without pkg-config files and outside checked include paths will fail.

## Test Signals
Run with `HOSTPKG_CONFIG=pkg-config` on systems with `ncursesw`, with only `ncurses`, and with no headers. Verify output files contain usable flags and that missing dependencies produce a clear nonzero failure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf-cfg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.c -->
# sources/test-tools/kdevops/scripts/kconfig/nconf.c

## Purpose
`nconf.c` implements the ncurses menu/form/panel Kconfig frontend. It offers richer keyboard navigation than `mconf`, including function-key commands, incremental menu search, symbol search, single-menu mode, save/load dialogs, and choice/string editors.

## Important APIs, Types, And Functions
Key state includes `struct mitem`, `MAX_MENU_ITEMS`, `show_all_items`, `indent`, `current_menu`, `child_count`, `single_menu_mode`, `main_window`, `curses_menu`, `curses_menu_items`, `k_menu_items`, `items_num`, `global_exit`, `dialog_input_result`, and `dialog_input_result_len`. Key functions include `main()`, `setup_windows()`, `selected_conf()`, `conf()`, `build_conf()`, `show_menu()`, `do_match()`, `get_mext_match()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `search_conf()`, `do_exit()`, and the F1-F9 handlers.

## Control Flow
`main()` parses Kconfig and config state, reads `NCONFIG_MODE`, initializes curses, verifies terminal size, configures the curses menu, creates windows, installs message callbacks, and loops through `conf(&rootmenu)` until `global_exit`. `selected_conf()` rebuilds menu items, restores active item selection, renders via `show_menu()`, handles incremental search and special keys, then toggles symbols or enters submenus/editors. `build_conf()` mirrors `mconf` rendering but creates ncurses `ITEM`s. `conf_choice()` renders a choice list and applies `choice_set_value()`. F-key handlers invoke help, symbol info, show-all toggle, save, load, search, and exit.

## State And Persistence
Process state is mostly global UI state plus allocated curses items/windows. Menu expansion in single-menu mode is stored in `menu->data`. Persistent config changes are made through Kconfig symbol setters and saved with `conf_write()`/`conf_write_autoconf()`. Dialog input storage is dynamically resized and reused.

## Dependencies And Integration Points
Depends on Kconfig core APIs, `mnconf-common.c` for search jumps, `nconf.gui.c`/`nconf.h` for dialogs/colors, and ncurses `menu`, `panel`, and `form` libraries. It integrates with build detection through `nconf-cfg.sh`.

## Risks And Edge Cases
The local source contains apparent copy damage: a duplicated brace in `function_keys`, duplicated `switch (res)`, and a double opening brace in `build_conf()`. These may prevent compilation. `MAX_MENU_ITEMS` silently caps item creation. Incremental search manipulates `pattern[strlen(pattern)-1]` on backspace without an explicit non-empty guard. UI behavior depends heavily on terminal capabilities and dimensions.

## Test Signals
Compile `nconf`; run with small and large Kconfig trees; exercise F1-F9, no-function-key fallback, incremental search/backspace, symbol search jump keys, save/load, choice editing, string/int/hex editing, terminal resize, `NCONFIG_MODE=single_menu`, and show-all toggling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.gui.c -->
# sources/test-tools/kdevops/scripts/kconfig/nconf.gui.c

## Purpose
`nconf.gui.c` contains reusable ncurses UI primitives for `nconf`: color attribute setup, centered headings, text wrapping helpers, button dialogs, input dialogs, scrollable text windows, and window refresh orchestration.

## Important APIs, Types, And Functions
Exports include global `attr_*` variables declared in `nconf.h`, `set_colors()`, `print_in_middle()`, `get_line_no()`, `get_line()`, `get_line_length()`, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win()`, and `show_scroll_win_ext()`. It uses `struct nconf_attr_param` to initialize color/no-color themes.

## Control Flow
`set_colors()` detects color support, initializes default-color pairs, and writes each attribute global. Text helpers count and slice newline-delimited strings. `btn_dialog()` creates a centered window with optional button menu, handles left/right/enter/escape/function-key input, and returns the selected index or `KEY_EXIT`. `dialog_inputbox()` creates a prompt and editable single-line input area with cursor movement, insertion, deletion, dynamic buffer expansion, and help/exit signaling. `show_scroll_win_ext()` creates a pad for text, copies viewport slices into a bordered window, supports vertical/horizontal scrolling, and delegates extra keys to an optional callback.

## State And Persistence
State is curses window/panel/menu/item objects and caller-owned input buffers. The only exported persistent process state is the color attribute globals. No disk persistence occurs.

## Dependencies And Integration Points
Depends on `nconf.h`, `lkc.h`, `xalloc.h`, and ncurses menu/panel APIs. `nconf.c` uses these routines for all dialogs, help panes, and search result panes. `show_scroll_win_ext()` integrates with `mnconf-common` through an extra-key callback signature.

## Risks And Edge Cases
The local source shows a duplicated `int win_lines = 0;` declaration in `show_scroll_win_ext()`, likely a compile error. In `fill_window()`, `tmp[len] = '\0'` can write past the copied width if `len > x` because the copy length is clamped but the terminator index is not. `dialog_inputbox()` uses plain `realloc()` without the xalloc exit-on-failure behavior in one path. Very small terminal sizes can produce zero/negative derived dimensions.

## Test Signals
Compile with warnings, run under color and monochrome terminals, test long lines, long input, backspace/delete/home/end, scrollable content larger than the screen, search-result numeric callbacks, ESC/F5/F9 exits, and terminal resize paths through `nconf.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.gui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.h -->
# sources/test-tools/kdevops/scripts/kconfig/nconf.h

## Purpose
`nconf.h` is the shared header for the ncurses Kconfig frontend. It centralizes system includes, min/max macros, color attribute externs, function-key identifiers, callback typedefs, and GUI helper prototypes.

## Important APIs, Types, And Functions
It declares the `function_key` enum (`F_HELP` through `F_EXIT`), all `attr_*` globals, `extra_key_cb_fn`, and prototypes for color setup, text helpers, button/input dialogs, scroll windows, and refresh orchestration.

## Control Flow
There is no runtime control flow. The header defines compile-time contracts used by `nconf.c` and implemented by `nconf.gui.c`.

## State And Persistence
The declared `attr_*` variables are global process state initialized by `set_colors()`. No persistent storage is involved.

## Dependencies And Integration Points
Includes standard C headers and ncurses headers `ncurses.h`, `menu.h`, `panel.h`, and `form.h`. Build integration depends on `nconf-cfg.sh` producing matching library flags. The `extra_key_cb_fn` type lets scroll windows call back into search jump logic.

## Risks And Edge Cases
The `max` and `min` macros use GNU statement expressions and `typeof`, so they are not strict ISO C. Headers expose many globals, making initialization order important. Consumers must link against the full ncurses menu/panel/form stack.

## Test Signals
Compile both `nconf.c` and `nconf.gui.c` with the detected flags; run basic UI smoke tests and confirm all declared attributes are initialized before use.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/nconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/parser.y -->
# sources/test-tools/kdevops/scripts/kconfig/parser.y

## Purpose
`parser.y` is the Bison grammar for Kconfig files. It turns lexer tokens into menu tree entries, symbol properties, dependency expressions, variable assignments, source inclusions, help text, and parse-time validation state.

## Important APIs, Types, And Functions
The grammar emits `conf_parse(const char *name)` and `zconfdump(FILE *out)`. Internal helpers include `choice_check_sanity()`, `zconf_endtoken()`, `zconfprint()`, `zconf_error()`, `yyerror()`, `print_quoted_string()`, and `print_symbol()`. It uses `%union` values for strings, symbols, expressions, menus, symbol types, and variable flavors.

## Control Flow
Grammar actions call `menu_add_entry()`, `menu_set_type()`, `menu_add_prompt()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_add_dep()`, `menu_add_visibility()`, `menu_add_menu()`, and `menu_end_menu()` as statements are parsed. `source` delegates to `zconf_nextfile()`. Assignment statements call `variable_add()`. `conf_parse()` initializes scanning and menus, runs `yyparse()`, writes autoconf dependency commands including environment dependencies, deletes variables, ensures `modules_sym` and root menu prompt defaults, finalizes menus, checks recursive dependencies and choice sanity, and exits on parse errors.

## State And Persistence
Parse state includes global `current_menu`, `current_entry`, `current_choice`, `cdebug`, lexer globals (`cur_filename`, `cur_lineno`, `yylineno`), `modules_sym`, `autoconf_cmd`, and `yynerrs`. It builds persistent in-memory menu/symbol structures used by later config I/O; it also prepares dependency command text for generated autoconf metadata.

## Dependencies And Integration Points
Depends on Bison, the Kconfig lexer (`lexer.l` via `zconf_*` scanner functions), `preprocess.c` for variable/function expansion, menu/symbol/expression APIs, and `xalloc`. Frontends and config tools call `conf_parse()` before reading/writing configs.

## Risks And Edge Cases
Nested end-token validation catches mismatched `endif`/`endmenu`/`endchoice` and cross-file endings. Choice members must be bool and prompted. The local source contains duplicated `config_option: T_IMPLY...`, duplicated `fprintf` arguments in `choice_check_sanity()`, and possible copy artifacts that should be compile-checked. Grammar changes can alter Kconfig language compatibility and should be compared to upstream Linux Kconfig.

## Test Signals
Run parser generation/build tests, parse representative Kconfig files with nested menus/ifs/choices, invalid statements, mismatched end tokens, blank/multiple help, `source`, variable assignments, `option modules`, `output yaml`, recursive dependencies, and choice-value defaults outside choices.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/preprocess.c -->
# sources/test-tools/kdevops/scripts/kconfig/preprocess.c

## Purpose
`preprocess.c` implements Kconfig variable, environment, and function expansion. It supports make-like `$(...)` references, recursive/simple/append variables, user-defined function arguments, built-in functions, shell command expansion, and dependency emission for referenced environment variables.

## Important APIs, Types, And Functions
Public functions are `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`. Internal functions include `env_expand()`, `do_error_if()`, `do_filename()`, `do_info()`, `do_lineno()`, `do_shell()`, `do_warning_if()`, `function_expand()`, `variable_lookup()`, `variable_expand()`, `eval_clause()`, `expand_dollar_with_args()`, and `__expand_string()`.

## Control Flow
Lexer/parser code calls expansion helpers when scanning tokens and assignments. `eval_clause()` splits a `$(name,arg,...)` body on top-level commas, recursively expands name and arguments, then tries local numeric arguments, user variables/functions, built-in functions, and finally environment variables. Recursive variables expand at use time; simple variables expand at assignment time; `+=` inherits existing flavor or defaults to recursive. `env_write_dep()` writes makefile-style guards for each referenced environment variable and frees the environment list.

## State And Persistence
Two global linked lists track referenced environment variables and defined variables. Variables are freed after parse via `variable_all_del()`. Environment references persist into `autoconf_cmd` dependency text rather than files directly. Built-in `$(shell,...)` can observe external system state.

## Dependencies And Integration Points
Depends on Kconfig lexer globals (`cur_filename`, `yylineno`), `struct gstr` helpers from `util.c`, list utilities, `array_size.h`, `xalloc.h`, standard C, and `popen()`. `parser.y` uses `variable_add()` and `env_write_dep()`, while lexer logic typically calls token expansion.

## Risks And Edge Cases
`$(shell,...)` executes arbitrary commands from Kconfig input. Expansion has recursion protection but still allows deep work up to 1000 expansions. `do_shell()` reads only the first 4096 bytes of command output. The local source contains duplicated `struct list_head node;` and an extra closing brace after `expand_dollar()`, likely compile-breaking artifacts. Undefined variables silently expand to empty strings.

## Test Signals
Test recursive/simple/append assignments, positional arguments, nested function calls, built-ins, environment references and dependency output, recursion detection, unterminated references, too many function arguments, shell output newline normalization, and compilation against the lexer/parser.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/preprocess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/preprocess.h -->
# sources/test-tools/kdevops/scripts/kconfig/preprocess.h

## Purpose
`preprocess.h` declares the public Kconfig preprocessor interface used by the parser and lexer.

## Important APIs, Types, And Functions
It defines `enum variable_flavor` with `VAR_SIMPLE`, `VAR_RECURSIVE`, and `VAR_APPEND`, forward-declares `struct gstr`, and prototypes `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

## Control Flow
The header has no control flow. It establishes that callers can add variables during parse, expand `$()` references while scanning, write environment dependencies after parsing, and release variables after parse completion.

## State And Persistence
State is owned by `preprocess.c`; this header exposes mutation functions without exposing the underlying lists.

## Dependencies And Integration Points
Included by `parser.y` and likely the generated lexer. It depends only on the enum and `struct gstr` forward declaration.

## Risks And Edge Cases
Callers must free strings returned from expansion functions. Flavor semantics must match parser assignment tokens exactly or Kconfig variable behavior changes.

## Test Signals
Compile parser/lexer/preprocess together and exercise assignment plus expansion cases from Kconfig syntax.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/preprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/setlocalversion -->
# sources/test-tools/kdevops/scripts/kconfig/setlocalversion

## Purpose
`setlocalversion` emits a version suffix derived from the current source control state. This copy is derived from Linux kernel tooling and simplified for kdevops/Coccinelle-style trees.

## Important APIs, Types, And Functions
The main shell function is `scm_version()`. Global variables include `TAGS="--tags"`, `srctree=.`, and accumulated `res`. Git handling uses `git rev-parse`, `git describe`, `git diff-index`, and `awk`; Mercurial handling uses `hg id` and `hg log`.

## Control Flow
`scm_version()` first checks for a Git repository at the root. If HEAD is not exactly at a tag, it emits a formatted distance/hash from `git describe --tags` or `-g<hash>` if no tag exists. It appends `-dirty` when tracked changes exist outside `scripts/package`. If not Git, it checks Mercurial, emits tag or changeset suffixes, and appends `-dirty` for modified state. The script prints the resulting suffix.

## State And Persistence
No files are written. Output depends on repository tags, current HEAD, VCS metadata, and dirty working-tree state.

## Dependencies And Integration Points
Depends on `/bin/sh`, Git and/or Mercurial, `awk`, `cut`, and `sed`. Build systems can call it to embed local version suffixes into generated metadata.

## Risks And Edge Cases
The script uses `--tags`, so lightweight tags affect version selection. Dirty detection ignores only `scripts/package` and may be noisy in this repository. Mercurial branch uses `==` in `/bin/sh`, which is not portable to all shells. Repositories with no tags fall back to a hash suffix.

## Test Signals
Run in clean tagged Git, clean commits after a tag, dirty Git, tagless Git, outside a repository, and Mercurial if supported. Verify exact suffix formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/setlocalversion -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/symbol.c -->
# sources/test-tools/kdevops/scripts/kconfig/symbol.c

## Purpose
`symbol.c` implements Kconfig symbol semantics: type names, visibility calculation, defaults, ranges, choice resolution, user value setters, string validation, symbol lookup/search, reverse dependency warnings, and recursive dependency detection.

## Important APIs, Types, And Functions
Exports include fixed symbols `symbol_yes`, `symbol_mod`, `symbol_no`, global `modules_sym`, `sym_get_type()`, `sym_type_name()`, `sym_get_choice_menu()`, `sym_get_range_prop()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_dep_errors()`, `sym_calc_value()`, `sym_clear_all_valid()`, `sym_tristate_within_range()`, `sym_set_tristate_value()`, `choice_set_value()`, `sym_toggle_tristate_value()`, `sym_string_valid()`, `sym_string_within_range()`, `sym_set_string_value()`, `sym_get_string_default()`, `sym_get_string_value()`, `sym_is_changeable()`, `sym_is_choice_value()`, `sym_lookup()`, `sym_find()`, `sym_re_search()`, `sym_check_deps()`, `prop_get_symbol()`, and `prop_get_type_name()`.

## Control Flow
`sym_calc_value()` is central: it initializes type-appropriate defaults, recalculates visibility/direct/reverse/implied dependencies, applies user values when visible, resolves choices, applies defaults and implies, warns when `select` violates direct dependencies, folds module values to yes for booleans/no-modules, validates ranges, marks menus changed, and invalidates all symbols when `MODULES` changes. Choice resolution prioritizes visible user-selected yes, visible default, first visible unspecified, then least-prioritized visible no. Lookup uses a hashtable, while regex search compiles a case-insensitive regex, evaluates matching symbols, and sorts exact matches before alphabetical results. Dependency checks recurse through expression graphs and print explanatory cycles.

## State And Persistence
Symbol state is in global symbol objects, hashtable entries, per-symbol flags, current/default values, visibility caches, dependency expressions, menus lists, and choice member lists. No direct disk writes occur, but computed `SYMBOL_WRITE` and values drive config output.

## Dependencies And Integration Points
Depends on expression APIs, menu APIs, `conf_set_changed()`, Linux-style hashtable/list utilities, regex, and `xalloc`. `menu.c` builds properties and dependencies; frontends call setters/getters; config I/O reads/writes user defaults and current values.

## Risks And Edge Cases
This is high-risk semantic code: small changes can alter Kconfig resolution globally. Reverse dependencies can force values beyond direct dependencies and only warn unless `KCONFIG_WERROR` is set. String/range validation relies on `strtoll()` and current default symbols. The local source contains duplicated lines in `sym_calc_visibility()`, `sym_clear_all_valid()`, and `sym_lookup()`, likely copy artifacts but not all necessarily compile-breaking.

## Test Signals
Use Kconfig cases for bool/tristate with and without modules, `select`, `imply`, hidden defaults, range checks, hex normalization, invalid strings, choices with user/default/visibility combinations, regex search ordering, recursive dependency errors, and `KCONFIG_WERROR`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/symbol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/update-upstream-kconfig.sh -->
# sources/test-tools/kdevops/scripts/kconfig/update-upstream-kconfig.sh

## Purpose
`update-upstream-kconfig.sh` synchronizes this vendored Kconfig subtree from a local Linux `linux-next` checkout. It copies selected Kconfig sources, include headers, and lxdialog files into the current directory.

## Important APIs, Types, And Functions
This is a shell copy script with variables `UPSTREAM`, `KCONFIG_UPSTREAM`, `KCONFIG_UPSTREAM_INC`, and `KCONFIG_UPSTREAM_LX`. It runs `cp -a` loops from `$UPSTREAM/scripts/kconfig`, `$UPSTREAM/scripts/include`, and `$UPSTREAM/scripts/kconfig/lxdialog`.

## Control Flow
The script builds whitespace-separated file lists, copies each top-level Kconfig file from upstream into `.`, then copies include support headers into `.`, then copies selected lxdialog sources into `lxdialog`.

## State And Persistence
It overwrites local files in the current working directory. There are no backups, checksums, or version records.

## Dependencies And Integration Points
Depends on Bash, a local Linux tree at `$HOME/linux-next/`, `cp`, and an existing `lxdialog` destination directory. It is a maintainer tool, not a runtime dependency.

## Risks And Edge Cases
Running from the wrong directory can overwrite unrelated files. The upstream path is hardcoded. Local modifications to vendored Kconfig files can be lost. There is no error handling around missing files or upstream drift. Given the copy artifacts observed in several files, this script is an important way to refresh and compare against upstream.

## Test Signals
Run in a disposable clone with a known Linux-next checkout, inspect `git diff`, verify all listed files were copied, and build Kconfig frontends after synchronization.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/update-upstream-kconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/util.c -->
# sources/test-tools/kdevops/scripts/kconfig/util.c

## Purpose
`util.c` provides small Kconfig utility functions: filename string interning and a growable string buffer (`struct gstr`) used to assemble help, relation, and generated dependency text.

## Important APIs, Types, And Functions
Exports are `file_lookup()`, `str_new()`, `str_free()`, `str_append()`, `str_printf()`, and `str_get()`. It uses `HASHTABLE_DEFINE(file_hashtable, 1U << 11)` and `struct file` entries for interned names.

## Control Flow
`file_lookup()` hashes a filename, returns an existing interned pointer if found, otherwise allocates a `struct file`, duplicates the name, adds it to the hashtable, and returns the stable pointer. `str_new()` creates an empty growable buffer. `str_append()` extends capacity in 64-byte chunks when needed and appends text. `str_printf()` formats into a temporary stack buffer then appends. `str_free()` frees the buffer contents. `str_get()` returns the current char pointer.

## State And Persistence
The file has process-global interned filename storage that is never freed during normal execution. `struct gstr` instances are caller-owned heap buffers. No disk persistence occurs.

## Dependencies And Integration Points
Depends on `hashtable.h`, `xalloc.h`, standard allocation/formatting APIs, and Kconfig `internal.h` definitions. Used by parser/autoconf dependency generation, menu help/search formatting, symbol warnings, and any code needing stable filename pointers.

## Risks And Edge Cases
`str_printf()` uses a fixed 4096-byte temporary buffer, truncating longer formatted strings. `file_lookup()` intentionally leaks interned names for process lifetime. Callers must call `str_free()` for owned `gstr` buffers.

## Test Signals
Unit-style tests can intern duplicate filenames, append many strings across capacity boundaries, format long text, free empty/non-empty buffers, and verify relation/help generation does not truncate unexpectedly.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/xalloc.h -->
# sources/test-tools/kdevops/scripts/kconfig/xalloc.h

## Purpose
`xalloc.h` defines fail-fast allocation wrappers for the Kconfig code. These wrappers remove repetitive null checks by exiting the process on allocation failure.

## Important APIs, Types, And Functions
Static inline functions are `xmalloc()`, `xcalloc()`, `xrealloc()`, `xstrdup()`, and `xstrndup()`.

## Control Flow
Each wrapper calls the corresponding libc allocation/string duplication function, checks for null, calls `exit(1)` on failure, and otherwise returns the allocated pointer.

## State And Persistence
No state is stored. Allocations are caller-owned unless intentionally process-lifetime interned elsewhere.

## Dependencies And Integration Points
Includes `<stdlib.h>` and `<string.h>`. Used throughout the vendored Kconfig implementation.

## Risks And Edge Cases
Fail-fast behavior is simple but prevents graceful cleanup or detailed diagnostics on OOM. `xrealloc(ptr, 0)` inherits libc-specific behavior and may exit if it returns null. Consumers must still avoid integer overflows when calculating sizes.

## Test Signals
Compile coverage is usually sufficient. Fault-injection allocation tests can verify exit behavior if the project has an allocation shim.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/kconfig/xalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/korg-releases.py -->
# sources/test-tools/kdevops/scripts/korg-releases.py

## Purpose
`korg-releases.py` queries `https://www.kernel.org/releases.json` and prints release references for a requested moniker such as `mainline`, `stable`, `longterm`, or `linux-next`. It is suitable for Kconfig shell-generated choices or automation that needs current kernel release tags.

## Important APIs, Types, And Functions
Functions are `parser()`, `_check_connection()`, `kreleases(args)`, and `main()`. Command-line options include `--moniker` (required), `--pname`, `--pversion`, and `--debug`.

## Control Flow
`main()` configures logging, parses known args, and calls `kreleases()`. `kreleases()` first checks TCP connectivity to `kernel.org:80`, then fetches the HTTPS releases JSON with a project User-Agent. It filters releases by moniker, prefixes semantic versions with `v`, preserves non-matching version strings as-is, and prints each reference.

## State And Persistence
No persistent state is written. Runtime output depends on network reachability and the current kernel.org JSON.

## Dependencies And Integration Points
Depends on Python standard libraries `argparse`, `json`, `urllib.request`, `socket`, `logging`, and `re`. It integrates with any Kconfig or build logic that shells out to populate kernel version options.

## Risks And Edge Cases
Connectivity is checked on port 80 while data is fetched over HTTPS port 443, so the precheck can be misleading. Network errors raise and are caught only at the top level, printing a traceback and exiting 1. The regex only handles `x.y`, `x.y.z`, and `x.y-rcN`.

## Test Signals
Mock `urllib.request.urlopen` and `_check_connection()` for online/offline paths, moniker filtering, semantic tag prefixing, linux-next strings, debug logging, and exception exit behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/korg-releases.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambda-cli -->
# sources/test-tools/kdevops/scripts/lambda-cli

## Purpose
`lambda-cli` is a Python command-line interface for Lambda Labs cloud data used by kdevops. It lists instance types and regions, reports pricing, chooses simple automatic instance/region selections, checks availability, and generates Kconfig fragments.

## Important APIs, Types, And Functions
The main type is `LambdaCLI`, with methods `output()`, `list_instance_types()`, `list_regions()`, `get_cheapest_instance()`, `get_pricing()`, `smart_select()`, `check_availability()`, and `generate_kconfig()`. `main()` builds an argparse command tree for `instance-types`, `regions`, `pricing`, `smart-select`, `check-availability`, and `generate-kconfig`.

## Control Flow
`LambdaCLI.__init__()` loads an API key through `lambdalabs_api.get_api_key()`. Each command queries API helpers and formats JSON or text. `get_cheapest_instance()` filters available capacity and minimum GPU count, then chooses the lowest hardcoded price. `smart_select()` currently implements `cheapest` and a simplified `balanced` mode, while `closest` returns a placeholder error. `generate_kconfig()` writes generated compute/location/mapping files.

## State And Persistence
Runtime state is the output format and API key. Persistent writes occur only in `generate_kconfig()`, which creates an output directory and writes generated Kconfig files. No credentials are written by this script.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, `sys`, and standard typing/path libraries. Wrapper scripts `lambdalabs_smart_inference.py` and `lambdalabs_infer_region.py` call it as a subprocess. Kconfig generation integrates with `terraform/lambdalabs/kconfigs`.

## Risks And Edge Cases
The local source contains apparent syntax errors: duplicated `def get_pricing(...)` and an extra `)` after `kconfig_parser.add_argument(...)`. If present, the CLI cannot run, which also breaks wrapper scripts. Pricing is hardcoded and may drift from Lambda Labs. Minimum GPU parsing assumes names like `gpu_8x_*`. Text output tables can become wide.

## Test Signals
Run `python3 -m py_compile scripts/lambda-cli`, then mock API helpers for each subcommand, no-API-key paths, JSON/text output, cheapest selection with filters, Kconfig generation file writes, and wrapper-script subprocess behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambda-cli -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_api.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_api.py

## Purpose
`lambdalabs_api.py` is the Lambda Labs API/Kconfig generation library. It fetches instance type capacity, derives regions, fetches images, provides hardcoded pricing, sanitizes names into Kconfig symbols, and emits generated Kconfig choices and mappings for kdevops Terraform configuration.

## Important APIs, Types, And Functions
Exports include `get_api_key()`, `make_api_request()`, `get_instance_types_with_capacity()`, `get_regions()`, `get_images()`, `sanitize_kconfig_name()`, `get_instance_pricing()`, `generate_instance_types_kconfig()`, `generate_instance_type_mappings()`, `generate_regions_kconfig()`, `generate_images_kconfig()`, and `main()`. Constant `LAMBDALABS_API_BASE` points at `https://cloud.lambdalabs.com/api/v1`.

## Control Flow
API helpers issue authenticated GET requests with urllib and return parsed JSON or safe empty collections on failure. Instance Kconfig generation fetches instance data and capacity, falls back to default choices when unavailable, sorts available/unavailable types, emits `choice` entries with region dependencies and help text, and omits the final string config because it is defined elsewhere. Region generation derives capacity counts and defaults to the most-capable region. Image generation mostly documents that current Terraform provider OS image selection is unsupported. `main()` prints requested generated content or writes all generated files to an output directory.

## State And Persistence
No module-level mutable state beyond constants. `main all` writes `Kconfig.compute.generated`, `Kconfig.location.generated`, and `Kconfig.images.generated`. API key retrieval delegates to the credentials module.

## Dependencies And Integration Points
Depends on `lambdalabs_credentials.py`, Python standard `urllib`, `json`, `os`, `sys`, and typing. It is imported by `lambda-cli`, capacity/tier scripts, SSH tooling patterns, and Kconfig generation workflows.

## Risks And Edge Cases
Pricing is hardcoded and labeled as 2025 data, so it can drift. API schema assumptions vary between dict and string region representations. Fallbacks hide API failures by generating default options. `get_api_key()` docstring mentions environment variables, but current credentials helper does not read `LAMBDALABS_API_KEY` directly. The generated Kconfig depends on external symbol names like `TERRAFORM_LAMBDALABS_REGION_MANUAL`.

## Test Signals
Mock `make_api_request()` for available/unavailable capacity, missing data, region dict/string shapes, empty images, and API failures. Validate generated Kconfig syntax, symbol sanitization, default selection, mapping lines, and `main all` output files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_api.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_check_capacity.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_check_capacity.py

## Purpose
`lambdalabs_check_capacity.py` reports Lambda Labs GPU instance capacity across regions, checks a specific instance type, and can print the first available region for scripting.

## Important APIs, Types, And Functions
Functions are `_build_region_map()`, `check_availability(instance_type=None, json_output=False, pick_first=False)`, and `main()`. CLI options are `--instance-type/-i`, `--json/-j`, and `--pick-first`.

## Control Flow
The script loads an API key, fetches `capacity_map` via `get_instance_types_with_capacity()`, and either handles a specific instance type or all GPU instances. Specific checks print a first region, JSON, or human text and return 0 only when capacity exists. Global checks filter `gpu_` instance types with non-empty regions, optionally emit JSON grouped by region, or print a human region list.

## State And Persistence
No state is written. Exit status is meaningful for automation.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, and `sys`. It is usable from shell/Kconfig command substitutions to avoid selecting unavailable Lambda Labs capacity.

## Risks And Edge Cases
No API key or empty API results exit nonzero. Human output includes Unicode bullets/location markers, which may be unsuitable for strict ASCII parsers. The example help mentions `gpu_1x_h100_sxm5`; names must match API data exactly.

## Test Signals
Mock capacity maps for no key, API failure, empty capacity, specific instance with/without regions, `--pick-first`, JSON all-capacity output, and exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_check_capacity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_credentials.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_credentials.py

## Purpose
`lambdalabs_credentials.py` manages Lambda Labs API keys stored in INI-style credentials files, with a CLI for get/set/check/test/path operations.

## Important APIs, Types, And Functions
Exports are `get_credentials_file_path()`, `read_credentials_file(path=None, profile="default")`, `get_api_key(profile="default")`, `create_credentials_file(api_key, path=None, profile="default")`, and `main()`. The default path is `~/.lambdalabs/credentials`.

## Control Flow
Credential reading checks the default file, then a custom `LAMBDALABS_CREDENTIALS_FILE`, and looks for `lambdalabs_api_key` or `api_key` under the requested profile or `DEFAULT`. Creation ensures the parent directory, updates the profile, writes the file, and chmods it `0600`. CLI `test` calls the Lambda Labs `/instances` endpoint with the key and reports validity.

## State And Persistence
Persistent state is the credentials file on disk. `set` writes or updates it with restrictive permissions. Other commands read and print status or secret values.

## Dependencies And Integration Points
Depends on `configparser`, `Path`, `os`, and optional urllib/json in `test`. Imported by Lambda Labs API and SSH key modules. External scripts expect `get_api_key()` to be the central credential source.

## Risks And Edge Cases
Despite callers' comments, this module does not read `LAMBDALABS_API_KEY` directly. Parse errors are silently ignored. `get` prints the raw API key to stdout. `test` distinguishes HTTP 403 but other failures are generic. Existing file comments/order may be rewritten by `configparser`.

## Test Signals
Test missing file, profile-specific key, DEFAULT key, custom credentials path, file creation permissions, parse failure, CLI get/check/path/set, and mocked API test success/403/other error.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_credentials.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_infer_region.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_infer_region.py

## Purpose
`lambdalabs_infer_region.py` is a backward-compatible wrapper that chooses a Lambda Labs region for a requested instance type by invoking `lambda-cli`.

## Important APIs, Types, And Functions
Functions are `get_best_region_for_instance(instance_type)` and `main()`. It shells out to the sibling `lambda-cli` executable.

## Control Flow
The wrapper runs `lambda-cli --output json instance-types list`, parses the JSON, and if the requested instance name is present, runs `lambda-cli --output json smart-select --mode cheapest`. If that succeeds without an error field, it returns the selected region. Any subprocess or JSON failure falls back to `us-west-1`. With no exact CLI argument, `main()` prints `us-west-1` and exits success.

## State And Persistence
No files are written. Output is a single region string intended for shell/Kconfig consumption.

## Dependencies And Integration Points
Depends on `subprocess`, `json`, `os`, `sys`, and a working `lambda-cli`. Used by older Kconfig shell commands that expect a region inference helper.

## Risks And Edge Cases
The selected region is not specifically guaranteed to support the requested instance; it only checks that the instance exists before returning the global cheapest smart selection. If `lambda-cli` has syntax/runtime errors, this silently returns `us-west-1`. No stderr diagnostics are emitted.

## Test Signals
Mock subprocess outputs for matching instance, missing instance, CLI failure, invalid JSON, smart-select error, no arguments, and verify fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_infer_region.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_select_tier.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_select_tier.py

## Purpose
`lambdalabs_select_tier.py` selects the highest available Lambda Labs GPU instance from predefined performance fallback tiers, supporting single-GPU and 8-GPU groups.

## Important APIs, Types, And Functions
Important data structures are `GPU_TIERS_1X`, `TIER_ORDER_1X`, `GPU_TIERS_8X`, `TIER_ORDER_8X`, `TIER_GROUPS_1X`, `TIER_GROUPS_8X`, and combined `TIER_GROUPS`. Functions are `get_capacity_map()`, `check_instance_availability()`, `select_instance_from_tiers()`, `list_tier_groups()`, and `main()`.

## Control Flow
`select_instance_from_tiers()` validates the tier group, loads an API key, fetches the capacity map, optionally prints available GPU capacity, chooses the correct tier table based on `8x-` prefix, then walks tiers from highest to lowest and returns the first instance type with any region. `main()` either lists tiers or prints `instance_type region` for the selected result.

## State And Persistence
No persistence. Exit status indicates whether a tier selection was found.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, `sys`, and typing. Integrates with provisioning scripts that can accept a selected instance and region pair from stdout.

## Risks And Edge Cases
Tier instance names are hardcoded and must match Lambda Labs API names. The first region in API order is chosen without latency/cost preference. Verbose output contains Unicode check/cross marks. No API key or no matching capacity returns failure with minimal machine-readable detail.

## Test Signals
Mock capacity maps for each tier group, unavailable high tiers with fallback, unknown group, missing API key, `--list-tiers`, verbose output, and 8x group selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_select_tier.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_smart_inference.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_smart_inference.py

## Purpose
`lambdalabs_smart_inference.py` is a backward-compatible Kconfig shell helper that exposes the `lambda-cli smart-select --mode cheapest` result as individual `instance`, `region`, or `price` values.

## Important APIs, Types, And Functions
Functions are `get_smart_selection()` and `main()`. It shells out to sibling `lambda-cli` and returns a small dict with `instance_type`, `region`, and `price_per_hour` keys.

## Control Flow
`get_smart_selection()` invokes `lambda-cli --output json smart-select --mode cheapest`, parses stdout, and returns the data if no `error` field is present. On subprocess or JSON failure it returns defaults: `gpu_1x_a10`, `us-west-1`, `$0.75`. `main()` requires a query type and prints the requested field or errors on unknown query types.

## State And Persistence
No persistence. Output is a single text value for use in Kconfig or shell contexts.

## Dependencies And Integration Points
Depends on `subprocess`, `json`, `os`, and `sys`, plus a working `lambda-cli`. It bridges newer CLI logic into older Kconfig shell snippets.

## Risks And Edge Cases
If `lambda-cli` is broken or unauthenticated, defaults are silently used, which can lead to provisioning unavailable capacity. Price default is static. Unknown query types exit nonzero.

## Test Signals
Mock subprocess success, CLI error JSON, invalid JSON, subprocess failure, missing query type, valid `instance`/`region`/`price`, and unknown query type.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_smart_inference.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_ssh_key_name.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_ssh_key_name.py

## Purpose
`lambdalabs_ssh_key_name.py` generates a deterministic, unique Lambda Labs SSH key name based on the current working directory. This helps separate kdevops deployments by workspace.

## Important APIs, Types, And Functions
Functions are `get_directory_hash(path, length=8)`, `get_project_name(path)`, `generate_ssh_key_name(prefix="kdevops", include_project=True)`, and `main()`.

## Control Flow
The generator hashes the absolute current directory with SHA256, derives a project label from the last two non-generic path components, sanitizes underscores/dots and non-alphanumeric characters to hyphens, joins prefix/project/hash, collapses duplicate hyphens, and shortens to `prefix-hash` if longer than 50 characters. CLI `--simple` omits the project component.

## State And Persistence
No files are written. Output depends deterministically on `os.getcwd()`.

## Dependencies And Integration Points
Depends on Python standard `hashlib`, `os`, and `sys`. It integrates with Lambda Labs SSH key provisioning/validation scripts and Terraform/Kconfig identity settings.

## Risks And Edge Cases
Directory-derived names can change if a workspace is moved. Generic path filtering is simple and may produce surprising labels. Hash length of 8 hex chars is usually enough for local uniqueness but not collision-proof. Provider-side naming constraints beyond length/alphanumeric/hyphen are not checked.

## Test Signals
Test stable hashes for fixed paths, project extraction from root/generic/non-generic paths, sanitization, long-name truncation, `--simple`, `--help`, and unknown-option exit.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_ssh_key_name.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_ssh_keys.py -->
# sources/test-tools/kdevops/scripts/lambdalabs_ssh_keys.py

## Purpose
`lambdalabs_ssh_keys.py` manages Lambda Labs SSH keys through the cloud API: list, add, delete, check existence, read public key files, and validate that a named key is available for kdevops provisioning.

## Important APIs, Types, And Functions
Exports include `get_api_key()`, `make_api_request()`, `list_ssh_keys()`, `add_ssh_key()`, `delete_ssh_key()`, `read_public_key_file()`, `check_ssh_key_exists()`, `validate_ssh_setup()`, and `main()`. Constant `LAMBDALABS_API_BASE` points at the v1 API.

## Control Flow
`make_api_request()` builds authenticated requests, optionally encodes JSON for write methods, and returns parsed JSON or `None`. Listing expects `{"data": [...]}` but accepts list responses. Adding tries `{"name","public_key"}` then an alternate `{"name","key"}` payload. Deleting resolves names to IDs by listing keys before issuing `DELETE /ssh-keys/<id>`. Validation lists keys, handles unsupported API/no keys/missing expected key cases, and returns a success flag with human guidance.

## State And Persistence
No local files are written. The script mutates remote Lambda Labs SSH key state on `add` and `delete`. It reads local public key files for `add`.

## Dependencies And Integration Points
Depends on `lambdalabs_credentials.py`, `urllib.request`, `urllib.error`, `json`, `os`, `sys`, and typing. It supports Terraform identity workflows that require SSH keys to exist in Lambda Labs.

## Risks And Edge Cases
Remote API schema support is uncertain, reflected by fallback payloads and manual-console guidance. HTTP errors print details but return only `None`. `delete_ssh_key()` only treats 32-character hex strings as IDs. `except:` around error-body reading is broad. Adding duplicate keys or names depends on remote API behavior.

## Test Signals
Mock API responses for list data/list/raw/none, add first-format success, alternate-format success, delete by ID/name/not-found, public key missing/read error, validate unsupported/no keys/missing/found, no credentials, and CLI exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/lambdalabs_ssh_keys.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ld-version.sh -->
# sources/test-tools/kdevops/scripts/ld-version.sh

## Purpose
`ld-version.sh` is an awk filter that extracts a linker version string from stdin and converts it into a single sortable numeric value.

## Important APIs, Types, And Functions
The awk script performs `gsub()` cleanup, `split($1,a,".")`, then prints `major*100000000 + minor*1000000 + patch*10000` and exits after the first input record.

## Control Flow
For the first line, it strips everything through a closing parenthesis, strips everything through `version `, strips suffixes after `-`, splits the first token on dots, prints the computed integer, and exits.

## State And Persistence
No state is persisted. Output depends only on the first line of linker version text.

## Dependencies And Integration Points
Depends on awk. Build scripts can pipe linker `--version` output into it for numeric version comparisons.

## Risks And Edge Cases
Missing patch components evaluate as zero in awk arithmetic. Non-GNU or unusual linker banners may not match the cleanup assumptions. Only the first input line is considered.

## Test Signals
Pipe sample GNU ld, gold, lld, version strings with suffixes, two-component versions, and malformed input; verify numeric output matches build comparisons.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/ld-version.sh -->
