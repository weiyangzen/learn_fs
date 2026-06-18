# Group Research: subset-b-006333

This grouped report covers the requested Ceph client kernel `scripts/` and `scripts/kconfig/` files. Each source file has its own marked section for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.c

## Purpose
`nconf.c` implements the ncurses-based `nconfig` frontend for Kconfig. It parses the Kconfig tree through the shared `lkc` API, displays menus and symbols in a terminal UI, lets users change bool/tristate/string/int/hex values, performs symbol searches, loads alternate `.config` files, and writes the selected configuration plus autoconf output on exit.

## Important APIs, Types, and Functions
The central local type is `struct mitem`, which binds an ncurses `ITEM` string/tag to a `struct menu *` and visibility flag. Global UI state includes `main_window`, `curses_menu`, `curses_menu_items`, `k_menu_items`, `items_num`, `current_menu`, `show_all_items`, `single_menu_mode`, and `global_exit`.

Key handlers are represented by `struct function_keys` and dispatch to `handle_f1()` through `handle_f9()` for global help, symbol help, instructions, show-all toggle, back, save, load, search, and exit. Menu construction and interaction live in `build_conf()`, `selected_conf()`, `conf()`, `conf_choice()`, and `conf_string()`. Persistence entry points are `conf_load()`, `conf_save()`, `do_exit()`, and `set_config_filename()`.

Search uses `search_conf()`, `sym_re_search()`, `get_relations_str()`, and `show_scroll_win_ext()` with `handle_search_keys()` from the shared menuconfig/nconfig support. Incremental in-menu matching is handled by `struct match_state`, `do_match()`, and `get_mext_match()`.

## Control Flow
`main()` optionally silences early parser messages for `-s`, calls `conf_parse()` and `conf_read(NULL)`, reads `NCONFIG_MODE`, initializes curses/color/menu settings, builds the root window, and loops through `conf(&rootmenu)` until `global_exit` is set. `conf()` calls `selected_conf()`, which repeatedly rebuilds the visible item list, posts the menu, handles navigation and special keys, and applies symbol changes or enters submenus.

`build_conf()` recursively converts the Kconfig `struct menu` tree into ncurses items. It distinguishes ordinary symbols, menus, comments, choices, invisible entries, menuconfig submenus, and string-like symbols. Value changes route into shared Kconfig functions such as `sym_toggle_tristate_value()`, `sym_set_tristate_value()`, `choice_set_value()`, and `sym_set_string_value()`, which then invalidate and recalculate symbol state.

## State and Persistence
Terminal state is managed through ncurses windows, panels, and menu items and is cleaned up before exit. Configuration state is held by the shared Kconfig symbol/menu graph. The currently selected config filename is stored in static `filename` and displayed in `menu_backtitle`. `conf_write()` writes the chosen configuration and `conf_write_autoconf(0)` refreshes generated autoconf state.

`dialog_input_result` is a reusable heap buffer grown by `dialog_inputbox()`. `single_menu_mode` uses `menu->data` as a fold/unfold flag, which is a UI-specific reuse of a generic menu data field and must not collide with other frontends in the same process.

## Dependencies and Integration Points
The file depends on ncurses menu/form/panel APIs via `nconf.h`, shared Kconfig internals from `lkc.h`, `mnconf-common.h`, and helper functions implemented in `nconf.gui.c`. It integrates with the Kconfig parser, config file reader/writer, symbol calculation engine, and relation/help rendering utilities.

## Risks and Edge Cases
`MAX_MENU_ITEMS` caps displayed items at 4096; large Kconfig trees can be truncated silently by `item_make()`. Several fixed 256 byte item buffers can truncate prompts or values. Source contains duplicated statements/braces in a few places, such as a duplicate `continue`, suggesting this tree may include accidental merge artifacts that should be compile-tested. Terminal size below 75x20 is rejected. Interactive save paths call `conf_write_autoconf(0)` even after a failed write attempt in `do_exit()`, which is worth checking against expected build behavior.

## Test Signals
Coverage comes indirectly from Kconfig frontend use, `make nconfig`, and the Kconfig pytest fixtures in this subset for choices, transitional symbols, visibility, and recursive dependency handling. Manual tests should exercise resize, search, F-key fallback, alternate save/load, single menu mode, choice menus, invalid numeric input, and write failure dialogs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.gui.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.gui.c

## Purpose
`nconf.gui.c` provides reusable ncurses UI primitives for `nconf.c`: color/theme initialization, centered titles, text filling, button dialogs, input boxes, full-window refresh, and scrollable help/search windows.

## Important APIs, Types, and Functions
The file exports global attribute variables declared in `nconf.h`, including `attr_normal`, `attr_main_heading`, dialog attributes, scroll window attributes, and function-key attributes. `struct nconf_attr_param` describes one theme entry, with separate color and no-color tables. Public helpers include `set_colors()`, `print_in_middle()`, `get_line_no()`, `get_line()`, `get_line_length()`, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win()`, and `show_scroll_win_ext()`.

## Control Flow
`set_colors()` selects either color-capable or monochrome attributes and initializes curses color pairs. Dialog helpers compute dimensions from message text and terminal size, create windows/subwindows/panels, post menu or input UI, handle navigation keys, then free curses resources. `show_scroll_win_ext()` creates a pad for arbitrary text, tracks horizontal and vertical offsets, handles scroll keys, and optionally delegates unknown keys to a caller callback.

## State and Persistence
Most state is transient curses state. `dialog_inputbox()` grows and reuses a caller-owned result buffer through `resultp` and `result_len`, preserving input text across calls in the caller. Scroll offsets can persist across repeated `show_scroll_win_ext()` calls through optional `vscroll` and `hscroll` pointers.

## Dependencies and Integration Points
The file depends on ncurses menu/panel/form support via `nconf.h`, `xalloc.h`, and shared Kconfig string helpers indirectly. It is tightly coupled to `nconf.c` for attribute globals and function-key constants.

## Risks and Edge Cases
Dialog sizing can produce very small derived windows if the terminal is near the lower bound; input code must guard cursor positions against `prompt_width - 1`. `dialog_inputbox()` uses plain `realloc()` in the character insertion path rather than `xrealloc()`, so allocation failure would be less controlled there. The file contains a duplicate `menu_opts_off(menu, O_SHOWDESC)` call. `print_in_middle()` does not clamp negative x coordinates for strings wider than the target width.

## Test Signals
Manual `make nconfig` testing should cover color and monochrome terminals, long help text, horizontal scrolling, text insertion/deletion/home/end in input boxes, ESC/F-key exit paths, and terminal resize from the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.gui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.h

## Purpose
`nconf.h` is the shared header for the ncurses Kconfig frontend. It includes curses dependencies, declares UI attribute globals, defines small `max`/`min` helper macros and function-key constants, and publishes the dialog/window helper API implemented by `nconf.gui.c`.

## Important APIs, Types, and Functions
The `function_key` enum maps `F_HELP` through `F_EXIT` to F1-F9 behavior. `extra_key_cb_fn` defines callbacks used by scroll windows for search-result jump handling. Extern attributes cover all color/style roles in the main menu, scroll windows, dialogs, inputs, and function key bar.

Published functions include `set_colors()`, `print_in_middle()`, line-count/line-length utilities, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win_ext()`, and `show_scroll_win()`.

## Control Flow
The header has no runtime control flow. Its macros evaluate operands once using GNU statement expressions and `typeof`, making it tied to GNU C-compatible host compilers.

## State and Persistence
It declares process-global style state, owned and initialized by `nconf.gui.c`, then consumed by `nconf.c`.

## Dependencies and Integration Points
It includes `<ncurses.h>`, `<menu.h>`, `<panel.h>`, and `<form.h>`, making frontend compilation dependent on full ncurses development headers. It also pulls standard headers used by the implementation.

## Risks and Edge Cases
The `max` and `min` macro names are broad and can conflict if included with other headers that define them. The exported globals make style state mutable from any translation unit. GNU-only macro syntax reduces portability but matches kernel host-tool expectations.

## Test Signals
Successful `nconf` build against ncurses and runtime exercise of dialogs, scroll windows, and function-key handling validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/nconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/parser.y -->
# sources/distributed-fs/ceph-client/scripts/kconfig/parser.y

## Purpose
`parser.y` is the Bison grammar and parse driver for Kconfig files. It recognizes Kconfig statements, creates the menu/symbol/property tree, handles variable assignment syntax used by the preprocessor, validates structural constraints, and exposes `conf_parse()` and `zconfdump()`.

## Important APIs, Types, and Functions
The grammar defines tokens for Kconfig keywords, expression operators, words, quoted words, help text, and assignment values. Semantic types cover strings, symbols, expressions, menus, symbol types, and variable flavors.

Important parser actions call shared APIs such as `menu_add_entry()`, `menu_add_prompt()`, `menu_set_type()`, `menu_add_expr()`, `menu_add_symbol()`, `menu_add_dep()`, `menu_add_visibility()`, `menu_add_menu()`, `menu_end_menu()`, `sym_lookup()`, and expression constructors. Post-parse validation is implemented by `transitional_check_sanity()`, `choice_check_sanity()`, and dependency checks through `sym_check_deps()`. `zconf_endtoken()`, `zconf_error()`, and `yyerror()` handle diagnostics. `zconfdump()` emits a normalized view of the parsed tree.

## Control Flow
Parsing starts in `conf_parse(name)`: initialize autoconf dependency text, initialize scanning, initialize the root menu, run `yyparse()`, append autoconf dependency rules and environment-variable dependency rules, delete preprocessor variables, check errors, ensure `modules_sym`, install a default root prompt if needed, finalize menus, then walk each menu entry for recursive dependencies, transitional sanity, and choice-member sanity.

The grammar supports `mainmenu`, `config`, `menuconfig`, `choice`, `if`, `menu`, `source`, `comment`, help blocks, `depends on`, `visible if`, prompts, defaults, `select`, `imply`, `range`, `modules`, `transitional`, boolean/tristate/int/hex/string types, expressions, and `=`, `:=`, `+=` assignments.

## State and Persistence
Global parser state includes `current_menu`, `current_entry`, `current_choice`, `cdebug`, and Bison error count `yynerrs`. Parse results persist in the process-global Kconfig menu/symbol graph. `autoconf_cmd` records dependency rules for generated config outputs. Variable definitions persist only for parse time and are freed after parsing.

## Dependencies and Integration Points
The grammar integrates with scanner functions such as `zconf_initscan()`, `zconf_nextfile()`, and `zconf_starthelp()`, the preprocessor API in `preprocess.h`, shared Kconfig internals, and expression/menu/symbol modules. It feeds every Kconfig frontend and noninteractive config mode.

## Risks and Edge Cases
Because this is the grammar root, parse errors abort configuration. The source contains duplicated statements, including duplicate `menu_add_symbol(P_SELECT, ...)` and duplicate `return 0` in `transitional_check_sanity()`, which should be checked against intended behavior. Transitional symbols are constrained to help-only plus no non-yes dependencies/visibility; this is validated only after `menu_finalize()`. Source/end blocks must be in the same file, and recursive or repeated includes depend on scanner-side detection.

## Test Signals
The requested tests cover auto submenu construction, choices, randomized choice dependencies, conditional dependencies, recursive dependency errors, include recursion/repetition errors, transitional validation, and preprocessing syntax. Parser-specific validation should also include malformed end tokens, blank help text, duplicate help text, invalid choice defaults, and menuconfig without prompts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.c

## Purpose
`preprocess.c` implements Kconfig's make-like variable and function expansion layer. It expands `$()` references in tokens and assignment values, supports simple/recursive/append variables, user-defined functions, selected built-in functions, and tracks referenced environment variables so generated config dependencies can notice environment changes.

## Important APIs, Types, and Functions
Internal types are `struct env`, `struct function`, and `struct variable`. Exported functions are `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

Built-ins in `function_table` are `error-if`, `filename`, `info`, `lineno`, `shell`, and `warning-if`. Expansion internals include `env_expand()`, `function_expand()`, `variable_lookup()`, `variable_expand()`, `eval_clause()`, `expand_dollar_with_args()`, `__expand_string()`, and `expand_string_with_args()`.

## Control Flow
The parser adds variables through `variable_add()` for `=`, `:=`, and `+=`. Simple variables are expanded at assignment time; recursive variables store the raw text and expand when referenced. `__expand_string()` scans for `$`, delegates `$(`...`)` clauses to `expand_dollar_with_args()`, and appends expanded text. `eval_clause()` splits comma-separated function arguments while respecting nested parentheses, expands the callee name and arguments, then resolves in order: user variable/function, built-in function, environment variable, empty string.

## State and Persistence
Variables live in `variable_list` until `variable_all_del()` is called by `conf_parse()`. Referenced environment variables live in `env_list` until `env_write_dep()` writes dependency snippets to `autoconf_cmd` and deletes them. Recursive expansion is protected by `exp_count` and a hard depth limit.

## Dependencies and Integration Points
The file depends on `list.h`, `xalloc.h`, `array_size.h`, scanner globals `cur_filename` and `yylineno`, and shared string type `struct gstr`. It is called by the lexer/parser to expand Kconfig input and to produce dependency metadata for `include/config/auto.conf.cmd`.

## Risks and Edge Cases
`do_shell()` reads at most 4096 bytes from command output and ignores further output, so long shell outputs are truncated. It executes arbitrary shell commands from Kconfig files, which is expected but security-sensitive when parsing untrusted trees. The file contains a duplicate `v = variable_lookup(name);`, harmless but suspicious. Comma splitting supports nesting but not escape syntax beyond Kconfig's variable tricks. Undefined variables collapse to empty strings.

## Test Signals
Tests in `tests/preprocess/builtin_func`, `circular_expansion`, `escape`, and `variable` directly exercise built-ins, recursive detection, quoting/escaping, simple versus recursive variables, appends, left-hand-side expansion, and user-defined function arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.h

## Purpose
`preprocess.h` declares the Kconfig preprocessor interface used by the parser and scanner.

## Important APIs, Types, and Functions
`enum variable_flavor` defines `VAR_SIMPLE`, `VAR_RECURSIVE`, and `VAR_APPEND`, matching `:=`, `=`, and `+=`. The header forward-declares `struct gstr` and exposes `env_write_dep()`, `variable_add()`, `variable_all_del()`, `expand_dollar()`, and `expand_one_token()`.

## Control Flow
The header has no runtime control flow; it binds parser token actions and scanner token expansion to `preprocess.c`.

## State and Persistence
It exposes operations over process-global variable and environment-reference lists owned by `preprocess.c`.

## Dependencies and Integration Points
Included by `parser.y` and scanner/preprocessor consumers. It depends on the shared Kconfig string API only through a forward declaration.

## Risks and Edge Cases
Callers must free strings returned by `expand_dollar()` and `expand_one_token()`. Callers must also call `variable_all_del()` after parsing to avoid stale variables across parses in one process.

## Test Signals
The preprocessor pytest fixtures validate the public behavior behind this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/preprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf-cfg.sh -->
# sources/distributed-fs/ceph-client/scripts/kconfig/qconf-cfg.sh

## Purpose
`qconf-cfg.sh` discovers Qt build flags for the graphical `xconfig` frontend and writes three output files: compiler flags, linker flags, and the Qt host binary directory.

## Important APIs, Types, and Functions
The script takes positional outputs `cflags`, `libs`, and `bin`. It uses `${HOSTPKG_CONFIG}` to query `Qt6Core Qt6Gui Qt6Widgets` first, then `Qt5Core Qt5Gui Qt5Widgets`. Qt6 receives an extra `-std=c++17` line.

## Control Flow
With `set -eu`, the script validates that `${HOSTPKG_CONFIG}` exists, checks Qt6 package availability, writes cflags/libs/libexecdir and exits on success, then falls back to Qt5 cflags/libs/host_bins. If neither Qt version is found, it prints guidance and exits 1.

## State and Persistence
The only persistent state is the three generated files specified by arguments. It does not mutate repository source files directly.

## Dependencies and Integration Points
Called by Kbuild while building `scripts/kconfig/qconf`. It depends on host `pkg-config` or a compatible tool named by `HOSTPKG_CONFIG`, and on Qt development metadata.

## Risks and Edge Cases
`${HOSTPKG_CONFIG}` is expanded unquoted in several command positions, which is conventional for build variables but sensitive to spaces. The script assumes it is invoked with all three output paths. Qt6 and Qt5 package names must match distribution pkg-config metadata.

## Test Signals
Test by running under environments with Qt6, Qt5-only, missing pkg-config, and missing Qt packages. Kbuild `make xconfig` is the integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf-cfg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf.cc -->
# sources/distributed-fs/ceph-client/scripts/kconfig/qconf.cc

## Purpose
`qconf.cc` implements the Qt graphical Kconfig frontend used by `make xconfig`. It displays the Kconfig menu graph in multiple views, edits symbol values, shows help and debug dependency information, searches symbols, loads/saves `.config`, and persists UI settings with `QSettings`.

## Important APIs, Types, and Functions
`ConfigSettings` wraps `QSettings` and serializes splitter sizes. `ConfigItem` maps a `struct menu *` to a `QTreeWidgetItem`, updates prompt/name/value/icon columns, and links multiple UI items through `menu->data`. `ConfigItemDelegate` enables in-place editing for int/hex/string value cells.

`ConfigList` is the main tree widget. Important methods include `menuSkip()`, `reinit()`, `setOptionMode()`, `saveSettings()`, `findConfigItem()`, `updateSelection()`, `updateList()`, `updateMenuList()`, `setValue()`, `changeValue()`, `setRootMenu()`, `setParentMenu()`, `setAllOpen()`, and Qt event handlers for keyboard, mouse, focus, and context menus.

`ConfigInfoView` renders HTML help/debug information with `menuInfo()`, `symbolInfo()`, `debug_info()`, `print_filter()`, `expr_print_help()`, and `clicked()`. `ConfigSearchWindow` provides regex symbol search. `ConfigMainWindow` assembles actions, menus, toolbar, splitters, views, load/save/search, view switching, close confirmation, and settings persistence. `fixup_rootmenu()` marks menu roots for split view.

## Control Flow
`main()` parses `-s`/help, calls `conf_parse()`, marks root menus, creates `QApplication`, settings, and `ConfigMainWindow`, then enters the Qt event loop. The main window loads icons from `$srctree/scripts/kconfig/icons`, calls `conf_read(NULL)`, restores view mode and splitter geometry, and wires Qt signals among tree selections, help text, and navigation.

User edits flow from keyboard/mouse/delegate events into `sym_set_tristate_value()`, `sym_toggle_tristate_value()`, `choice_set_value()`, or `sym_set_string_value()`, then refresh all live `ConfigList` instances. Saving calls `conf_write()` and `conf_write_autoconf(0)`.

## State and Persistence
Kconfig state lives in the shared menu/symbol graph. UI state is persisted under `kernel.org/qconf` group `/kconfig/qconf`, including window position/size, list mode, split sizes, list option modes, show-name flags, search window geometry, and debug-help state. `menu->data` stores linked `ConfigItem` instances, so item destruction carefully unlinks itself.

## Dependencies and Integration Points
The file depends on Qt Widgets/Core/Gui, `lkc.h`, `qconf.h`, Kconfig icons, and shared Kconfig expression/symbol/menu APIs. It integrates with Kbuild through `qconf-cfg.sh` and with all config readers/writers.

## Risks and Edge Cases
Several suspicious duplicate or malformed fragments are visible in this tree, including duplicate `return false`, duplicate local `QAction *action`, duplicated `list = configList`, and an extra-looking brace near `ConfigInfoView::clicked()` in the read output; this file should be compile-tested. The HTML renderer escapes text through `print_filter()`, which reduces injection risk from prompts/help. The delegate calls the parent `setModelData()` after custom value handling, so behavior should be checked for invalid edits. `menu->data` sharing is fragile if multiple frontends ran in one process, though this binary only uses qconf.

## Test Signals
Build `make xconfig`, launch with a representative Kconfig, switch single/split/full views, edit bool/tristate/int/hex/string values, search symbols, click debug hyperlinks, save/load alternate configs, and verify settings restore. The Kconfig pytest fixtures validate much of the backend behavior that qconf displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf.h -->
# sources/distributed-fs/ceph-client/scripts/kconfig/qconf.h

## Purpose
`qconf.h` declares the Qt classes and enums used by the graphical Kconfig frontend.

## Important APIs, Types, and Functions
Enums define tree columns (`promptColIdx`, `nameColIdx`, `dataColIdx`), list modes (`singleMode`, `menuMode`, `symbolMode`, `fullMode`, `listMode`), and option modes (`normalOpt`, `allOpt`, `promptOpt`). Classes declared are `ConfigSettings`, `ConfigList`, `ConfigItem`, `ConfigItemDelegate`, `ConfigInfoView`, `ConfigSearchWindow`, and `ConfigMainWindow`.

The header exposes Qt signals and slots for menu navigation, item selection, option-mode changes, help/debug display, search, view switching, config loading/saving, and settings persistence.

## Control Flow
The header itself has no runtime flow, but Qt's meta-object system uses `Q_OBJECT`, signals, and slots declared here to route UI events in `qconf.cc`.

## State and Persistence
Class members define persistent UI state: root menu pointers, mode flags, option-mode flags, selected menus, search results, splitter pointers, saved actions, and static icons/actions. `ConfigSettings` persists state through QSettings.

## Dependencies and Integration Points
It includes Qt Widgets classes and `expr.h` for Kconfig types. It is consumed by `qconf.cc` and by Qt's moc generation during build.

## Risks and Edge Cases
The class declarations hold raw `struct menu *` and `struct symbol **` pointers into global Kconfig state; lifetime must remain process-wide. `ConfigItem` stores linked items in `menu->data`, so any change to menu data ownership must update the destructor logic. Qt API compatibility depends on the Qt5/Qt6 flags produced by `qconf-cfg.sh`.

## Test Signals
Successful moc/Qt compilation and interactive `xconfig` use validate this interface. Settings persistence, search windows, help panes, and tree updates are the important behavioral surfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/qconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/streamline_config.pl -->
# sources/distributed-fs/ceph-client/scripts/kconfig/streamline_config.pl

## Purpose
`streamline_config.pl` implements `localmodconfig`/`localyesconfig` style pruning. It reads an existing kernel config and currently loaded modules, maps modules to Kbuild objects and Kconfig symbols, preserves needed dependencies/selects, and emits a reduced config that disables unused modules.

## Important APIs, Types, and Functions
Major functions are `read_config()`, `read_kconfig()`, `convert_vars()`, `parse_config_depends()`, `parse_config_selects()`, `loop_depend()`, `loop_select()`, and `in_preserved_kconfigs()`. Important data maps include `%depends`, `%selects`, `%prompts`, `%objects`, `%config2kfile`, `%defaults`, `%modules`, `%configs`, `%orig_configs`, `%setconfigs`, and `%process_selects`.

Options are `--localmodconfig` and `--localyesconfig`. Inputs include source tree path, top Kconfig path, `LSMOD`, `LMC_KEEP`, `objtree`, and existing config locations such as `.config`, `/proc/config.gz`, `/boot/config-*`, `vmlinux`, or `configs.ko`.

## Control Flow
The script reads the base config, parses options, finds all `Makefile`/`Kbuild` files, optionally parses Kconfig dependencies and selects, maps `obj-$(CONFIG_*) += foo.o` lines to module names, reads loaded modules from `lsmod` or an override, marks configs required by loaded modules, repeatedly adds dependencies and selected hidden configs, then streams the original config while turning unused `=m` options into unset lines. It performs a final integrity check that loaded modules have at least one retained config.

## State and Persistence
The script emits the transformed config on stdout and diagnostics on stderr. It does not write `.config` itself. It may read host system state from `/proc`, `/boot`, loaded module lists, and source/build trees.

## Dependencies and Integration Points
It depends on Perl, `Getopt::Long`, `find`, `lsmod`, optional `scripts/extract-ikconfig`, Kbuild makefile syntax, and Kconfig syntax. It integrates with `make localmodconfig` and related targets.

## Risks and Edge Cases
The parsing is intentionally approximate and regex-based, so complex Kbuild/Kconfig constructs can be missed. Running against untrusted trees can execute helper commands from the configured search list. It only keeps dependencies already enabled as modules and avoids enabling unrelated options. It has special cases for `CONFIG_IKCONFIG`, module signing keys, and trusted keys to avoid broken follow-up builds. Module names and object names are normalized by replacing hyphens with underscores.

## Test Signals
Useful tests include fake `LSMOD` files, synthetic Makefiles/Kconfigs with dependencies/selects/defaults, `LMC_KEEP`, missing signing/trusted key files, and comparison against expected reduced configs for localmodconfig/localyesconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/streamline_config.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/symbol.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/symbol.c

## Purpose
`symbol.c` is the core Kconfig symbol engine. It stores symbols, calculates visibility and values, handles bool/tristate/string/int/hex validation, implements choice resolution, applies defaults/selects/implies/ranges/transitional behavior, performs regex symbol search, and detects recursive dependency cycles.

## Important APIs, Types, and Functions
Global constant symbols are `symbol_yes`, `symbol_mod`, and `symbol_no`; `modules_sym` tracks the symbol that enables module support. Public APIs include `sym_get_type()`, `sym_type_name()`, `sym_get_prompt_menu()`, `sym_get_choice_menu()`, `sym_get_range_prop()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_dep_errors()`, `sym_calc_value()`, `sym_clear_all_valid()`, `sym_tristate_within_range()`, `sym_set_tristate_value()`, `choice_set_value()`, `sym_toggle_tristate_value()`, `sym_string_valid()`, `sym_string_within_range()`, `sym_set_string_value()`, `sym_get_string_default()`, `sym_get_string_value()`, `sym_is_changeable()`, `sym_is_choice_value()`, `sym_lookup()`, `sym_find()`, `sym_re_search()`, `sym_check_deps()`, `prop_get_symbol()`, and `prop_get_type_name()`.

Internal dependency-cycle state uses `struct dep_stack`. Search sorting uses `struct sym_match` and `sym_rel_comp()`.

## Control Flow
Symbol calculation starts by checking `SYMBOL_VALID`, initializing a default `newval`, calculating visibility, then applying user values, choice state, defaults, reverse dependencies from `select`, `imply`, direct dependencies, range validation, and module restrictions. Changes mark associated menus as changed and can invalidate all symbols when module support changes.

Choice resolution prioritizes visible user-selected `y`, then visible default, then first visible user-unspecified symbol, then a reverse-order fallback. Dependency checking recursively traverses direct dependencies, reverse dependencies, implied dependencies, property visibility, defaults, and choice members while maintaining a stack for diagnostic output.

## State and Persistence
Symbols are stored in `sym_hashtable`; individual symbols hold current values, user/default values, flags, property lists, menu links, and dependency expressions. Validity and changed flags cache calculations until invalidated. `modules_val` mirrors `modules_sym` and influences tristate-to-bool coercion. Warnings accumulate in `sym_warnings`.

## Dependencies and Integration Points
The file depends on `hash.h`, `xalloc.h`, Kconfig expression/menu/property definitions, and list helpers. It is used by parsers, frontends, config readers/writers, search dialogs, and test harnesses.

## Risks and Edge Cases
This file is highly stateful; missed invalidation can produce stale UI/config output. Transitional symbols are treated as always visible and not writable, and defaults from a single user-set transitional symbol can mark the new symbol as user-valued to avoid prompting. The source contains duplicated lines in several places, including duplicated `if (sym->implied.tri != tri)`, duplicated `if (menu->sym->curr.tri != val)`, and duplicated `continue`; these should be compile- and behavior-tested. Recursive dependency diagnostics are complex and can be sensitive to choice relationships.

## Test Signals
The requested tests exercise choices, randomized choice dependency recalculation, conditional dependencies, no-write behavior for unmet choice dependencies, transitional migration, invalid transitional properties, and recursive dependency errors. Additional tests should cover range validation, `KCONFIG_WERROR`, regex search order, modules disabled behavior, `select` unmet dependency warnings, and `imply`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/symbol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/Kconfig

## Purpose
This fixture verifies automatic submenu creation when a visible symbol depends on the immediately preceding symbol.

## Important APIs, Types, and Functions
It defines `A`, dependent `A0`, dependent nested `A0_0`, sibling `A1`, a choice depending on `A1`, independent `B`, and nonconsecutive dependent `C`.

## Control Flow
When parsed and rendered by `oldaskconfig`, menu finalization should nest `A0` under `A`, `A0_0` under `A0`, and the choice under `A1`, while leaving `B` and nonconsecutive `C` at the appropriate level.

## State and Persistence
Defaults set `A` and `A0` to `y`. The fixture has no persistent state beyond generated `.config` during tests.

## Dependencies and Integration Points
It targets menu finalization and text frontend display ordering/indentation.

## Risks and Edge Cases
The key edge is that `C` depends on `A` but is not adjacent, so it must not be auto-nested merely because of dependency.

## Test Signals
The paired Python test expects `oldaskconfig()` success and stdout matching `expected_stdout`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/__init__.py

## Purpose
This pytest module validates the auto-submenu fixture.

## Important APIs, Types, and Functions
The only test function calls `conf.oldaskconfig()` and `conf.stdout_contains('expected_stdout')`.

## Control Flow
Pytest injects the `conf` fixture from `conftest.py`; the test runs the interactive frontend with automatic enter input and compares stdout against the expected output file.

## State and Persistence
Temporary output is managed by the `Conf` helper. No module-level mutable state is used.

## Dependencies and Integration Points
Depends on `scripts/kconfig/conf`, the local `Kconfig`, and expected-output files in the same test directory.

## Risks and Edge Cases
The test is output-format sensitive, so harmless UI text changes can require expected fixture updates.

## Test Signals
Pass means automatic submenu rendering still matches expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/Kconfig

## Purpose
This fixture defines a minimal boolean choice with a default member to test baseline choice semantics.

## Important APIs, Types, and Functions
The `choice` has prompt `boolean choice`, default `BOOL_CHOICE1`, and two bool members `BOOL_CHOICE0` and `BOOL_CHOICE1`.

## Control Flow
Kconfig should select the default when appropriate and emit exactly one selected choice member across oldask/allyes/allmod/allno/alldef modes.

## State and Persistence
Generated `.config` content records the selected choice symbol. The source has no external state.

## Dependencies and Integration Points
Targets choice parsing, default selection, and all*config modes in `conf`.

## Risks and Edge Cases
Module mode should not create invalid `m` values because members are boolean.

## Test Signals
The paired tests compare stdout/config against expected files for multiple config modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/__init__.py

## Purpose
This pytest module verifies basic choice behavior across interactive and generated config modes.

## Important APIs, Types, and Functions
It defines `test_oldask0`, `test_allyes`, `test_allmod`, `test_allno`, and `test_alldef`, each using `Conf` runner methods and expected stdout/config helpers.

## Control Flow
Each test runs a different `scripts/kconfig/conf` mode and compares the resulting stdout or `.config` against expected fixtures.

## State and Persistence
Each run happens in a temporary directory through `conftest.py`, so `.config` state is isolated per test.

## Dependencies and Integration Points
Depends on expected fixture files and the `choice/Kconfig` source.

## Risks and Edge Cases
Mode-specific expectations can break if default choice or all*config policy changes.

## Test Signals
Passing all functions indicates baseline boolean choice behavior is stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/Kconfig

## Purpose
This fixture tests randconfig across dependent choices where the second choice is visible only when member `B` of the first choice is selected.

## Important APIs, Types, and Functions
It defines a first choice between `A` and `B`, then a second choice between `X` and `Y` with `depends on B`.

## Control Flow
During randconfig, the first choice is randomized. If `B` is selected, the second choice becomes visible and must also be randomized consistently.

## State and Persistence
Only the generated `.config` from each seed persists during a test iteration.

## Dependencies and Integration Points
Targets `sym_calc_choice()`, visibility recalculation, and randconfig randomness.

## Risks and Edge Cases
The dependency of one choice on another choice member can expose stale visibility or insufficient recalculation.

## Test Signals
The paired test expects all three possible output patterns across 100 seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/__init__.py

## Purpose
This pytest module verifies randconfig can produce all valid patterns for dependent choices.

## Important APIs, Types, and Functions
`test(conf)` loops seeds 0 through 99, calls `conf.randconfig(seed=i)`, and matches output against `expected_config0`, `expected_config1`, or `expected_config2`.

## Control Flow
The loop stops early after all expected patterns are observed. Any unexpected config causes an assertion failure.

## State and Persistence
Boolean flags track which expected patterns have appeared. Config output is isolated by the `Conf` temporary directory.

## Dependencies and Integration Points
Depends on deterministic seed support through `KCONFIG_SEED`.

## Risks and Edge Cases
Random tests can be brittle if valid output patterns change or if randomization policy changes.

## Test Signals
Pass means all dependent-choice variants remain reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/Kconfig

## Purpose
This fixture tests randconfig choice recalculation when invisible choices and dependencies can affect later visible choices.

## Important APIs, Types, and Functions
It defines an always-invisible choice (`depends on n`), a visible `A`/`B` choice, `FOO` depending on `A`, and a final choice containing `X` depending on `FOO`.

## Control Flow
Randconfig must ignore the invisible dummy choice, randomize the visible choice, recalculate `FOO`, and only make the final choice visible when dependencies are met.

## State and Persistence
Generated configs vary by seed but remain local to the test temp directory.

## Dependencies and Integration Points
Targets choice shuffling and dependency recalculation after choice decisions.

## Risks and Edge Cases
If choice randomization changes symbol order without recalculating values, the final choice can be emitted inconsistently.

## Test Signals
The paired test accepts exactly three expected valid configurations for 20 seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/__init__.py

## Purpose
This pytest module checks that randconfig respects dependencies after choice shuffling.

## Important APIs, Types, and Functions
`test(conf)` loops 20 seeds, runs `conf.randconfig(seed=i)`, and asserts the result matches one of three expected configs.

## Control Flow
Every seed must produce a valid expected pattern; unlike the first randomize test, it does not require observing all patterns.

## State and Persistence
No persistent state beyond temporary configs.

## Dependencies and Integration Points
Uses `Conf.randconfig()` and expected config fixture files.

## Risks and Edge Cases
The test guards against invalid combinations rather than distribution quality.

## Test Signals
Passing indicates choice dependency recalculation is sound for this pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/Kconfig

## Purpose
This fixture validates conditional dependency syntax `depends on X if Y` for bool and tristate symbols.

## Important APIs, Types, and Functions
It defines `MODULES`, bool `FOO`/`BAR`, bool `TEST_BASIC` and `TEST_COMPLEX`, tristate `BAZ`, and tristate `TEST_OPTIONAL`.

## Control Flow
The parser must turn conditional dependencies into equivalent expressions, and symbol calculation must apply the dependency only when the condition is true.

## State and Persistence
The generated `.config` changes based on supplied test configs.

## Dependencies and Integration Points
Targets parser grammar for `depends`, expression construction, tristate behavior, and oldconfig.

## Risks and Edge Cases
Conditional dependencies can be misinterpreted as unconditional dependencies or lose tristate semantics.

## Test Signals
The paired Python test runs three input configs and compares each output to expected configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/__init__.py

## Purpose
This pytest module validates conditional dependency output for three scenarios.

## Important APIs, Types, and Functions
The single `test(conf)` calls `conf.oldconfig('test_config1')`, `test_config2`, and `test_config3`, then checks `expected_config1`, `expected_config2`, and `expected_config3`.

## Control Flow
Each oldconfig run starts from a fixture `.config` and must complete successfully.

## State and Persistence
Temporary `.config` output is recreated per call.

## Dependencies and Integration Points
Depends on the conditional dependency Kconfig and fixture config files.

## Risks and Edge Cases
If `Conf._run_conf()` reused mutable `extra_env` across calls unexpectedly, tests could leak environment, but these calls do not pass custom env.

## Test Signals
Pass means conditional dependencies work across all provided bool/tristate combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conditional_dep/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conftest.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/conftest.py

## Purpose
`conftest.py` provides the pytest fixture framework for Kconfig unit tests. It runs `scripts/kconfig/conf` in isolated temporary directories and offers helpers to compare stdout, stderr, and generated config output with expected fixtures.

## Important APIs, Types, and Functions
`CONF_PATH` points at `scripts/kconfig/conf`. Class `Conf` stores test directory, return code, stdout, stderr, and config content. Runner methods include `_run_conf()`, `oldaskconfig()`, `oldconfig()`, `olddefconfig()`, `defconfig()`, `_allconfig()`, `allyesconfig()`, `allmodconfig()`, `allnoconfig()`, `alldefconfig()`, and `randconfig()`. Checker methods continue below the displayed portion and include content/match helpers referenced by tests, such as `stdout_contains()`, `stderr_contains()`, `stderr_matches()`, `config_contains()`, `config_matches()`. A pytest fixture returns `Conf(request)`.

## Control Flow
`_run_conf()` builds `[CONF_PATH, mode, 'Kconfig']`, sets `srctree` to the test directory, clears `KCONFIG_DEFCONFIG_LIST`, creates a temporary directory, optionally copies an input `.config`, starts `conf`, feeds explicit keys and/or repeated newlines for interactive modes, waits, captures stdout/stderr, reads the generated config if expected, and prints captured diagnostics for pytest failure output.

## State and Persistence
All generated files are isolated in `tempfile.TemporaryDirectory()` and removed after each run. Test output is stored on the `Conf` instance for assertions. Environment overrides are passed to child processes.

## Dependencies and Integration Points
Depends on pytest, Python stdlib, and a built `scripts/kconfig/conf` binary. It integrates all Kconfig test packages in this tree through the `conf` fixture.

## Risks and Edge Cases
Interactive handling writes repeated newlines until the process exits; if `conf` blocks without consuming stdin correctly, tests can hang. The default argument `extra_env={}` is mutable and can leak modifications between calls in Python, though current usage typically overwrites deterministic keys. The fixture assumes expected files are named consistently in each test directory.

## Test Signals
Every Kconfig pytest module in this subset depends on this file. Failures in process launching, env setup, stdin handling, or expected matching will surface broadly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/Kconfig

## Purpose
This fixture defines multiple invalid recursive dependency patterns that Kconfig must reject.

## Important APIs, Types, and Functions
It covers self-dependency (`A depends on A`), self-select (`B select B`), mutual depends (`C1`/`C2`), depends plus select (`D1`/`D2`), depends plus imply (`E1`/`E2`), default dependency (`F1`/`F2`), and a menu depending on its own content (`G`).

## Control Flow
During post-parse dependency validation, `sym_check_deps()` should find recursion and emit diagnostics.

## State and Persistence
No persistent state beyond a failed temporary config run.

## Dependencies and Integration Points
Targets symbol dependency graph traversal and diagnostic formatting.

## Risks and Edge Cases
The fixture contains several independent recursive cases; diagnostic ordering can be implementation-dependent.

## Test Signals
The paired test expects `oldaskconfig()` to fail with stderr matching `expected_stderr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/__init__.py

## Purpose
This pytest module asserts recursive dependency errors are fatal.

## Important APIs, Types, and Functions
The test calls `conf.oldaskconfig()` and checks for return code 1 plus expected stderr.

## Control Flow
The run should fail during parse/finalization before normal configuration output.

## State and Persistence
Only captured stderr/return code are used.

## Dependencies and Integration Points
Depends on recursive dependency diagnostics from `symbol.c`.

## Risks and Edge Cases
Error text is precise, so formatting changes require fixture updates.

## Test Signals
Pass indicates recursive dependencies remain hard errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_dep/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/Kconfig

## Purpose
This fixture starts a recursive include chain by sourcing `Kconfig.inc1`.

## Important APIs, Types, and Functions
It contains only `source "Kconfig.inc1"`.

## Control Flow
The scanner/source stack should follow the include and detect recursion in the included files.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Targets scanner include handling rather than symbol calculation.

## Risks and Edge Cases
The real recursion pattern is in adjacent include fixtures not listed here; this top-level file is the entry point.

## Test Signals
The paired test expects nonzero exit and expected stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/__init__.py

## Purpose
This pytest module verifies recursive Kconfig inclusion is detected.

## Important APIs, Types, and Functions
`test(conf)` runs `conf.oldaskconfig()` and checks nonzero return plus expected stderr.

## Control Flow
The parser should fail while traversing `source` statements.

## State and Persistence
Only return code and stderr are asserted.

## Dependencies and Integration Points
Depends on scanner include-stack diagnostics.

## Risks and Edge Cases
Include path resolution must be stable relative to the test `srctree`.

## Test Signals
Pass indicates recursive includes cannot hang or overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/Kconfig

## Purpose
This fixture starts a repeated include scenario by sourcing `Kconfig.inc1`.

## Important APIs, Types, and Functions
The file contains one source statement.

## Control Flow
The scanner should detect repeated inclusion through included fixture files and fail.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Targets source include tracking.

## Risks and Edge Cases
The repeated include details are in files outside this work item; this file is the test entry.

## Test Signals
The paired test expects nonzero exit and matching stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/__init__.py

## Purpose
This pytest module verifies repeated Kconfig inclusion errors.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()` and checks stderr against `expected_stderr`.

## Control Flow
The Kconfig run should fail during include processing.

## State and Persistence
No persistent state besides captured stderr.

## Dependencies and Integration Points
Depends on scanner repeated-include detection.

## Risks and Edge Cases
Expected output is sensitive to path and line diagnostics.

## Test Signals
Pass means repeated includes are rejected as designed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/Kconfig

## Purpose
This fixture validates that transitional symbols may only have type and help, and no other properties.

## Important APIs, Types, and Functions
It defines invalid transitional symbols with default, prompt, select, imply, depends, range, and missing type cases, plus `OTHER_SYMBOL`.

## Control Flow
`parser.y` accepts the syntax, then post-parse `transitional_check_sanity()` should reject each invalid property/condition.

## State and Persistence
No persistent state; the run should fail before producing a valid config.

## Dependencies and Integration Points
Targets parser transitional-property validation and diagnostics.

## Risks and Edge Cases
Only the first or a subset of errors may be emitted depending on validation flow; expected stderr must match implementation order.

## Test Signals
The paired test expects `olddefconfig()` exit code 1 and expected transitional-symbol stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/__init__.py

## Purpose
This pytest module asserts invalid transitional symbol properties are rejected.

## Important APIs, Types, and Functions
The test calls `conf.olddefconfig()` and `conf.stderr_contains('expected_stderr')`.

## Control Flow
The noninteractive config run should terminate with code 1 during parser sanity checks.

## State and Persistence
Only stderr and return code are examined.

## Dependencies and Integration Points
Depends on transitional checks in `parser.y`.

## Risks and Edge Cases
The assertion uses containment, giving some tolerance for additional diagnostics.

## Test Signals
Pass confirms transitional help-only rules are enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/Kconfig

## Purpose
This fixture tests prompting for newly visible choice values when dependencies are introduced.

## Important APIs, Types, and Functions
It defines `A`, a choice depending on `A` with `CHOICE_B` and new `CHOICE_C`, plus an independent choice with `CHOICE_D`, `CHOICE_E`, and `CHOICE_F` depending on `A`.

## Control Flow
Starting from an existing config, `oldconfig` receives input enabling `A`; newly visible choice members should be recognized as new and prompt appropriately.

## State and Persistence
The paired `config` file provides initial choice selections.

## Dependencies and Integration Points
Targets oldconfig prompting, choice visibility, and `sym_has_value()` behavior.

## Risks and Edge Cases
Choice members can become newly visible due to parent or member dependencies, which historically caused missed prompts.

## Test Signals
The paired test expects `oldconfig('config', 'y')` success and expected stdout prompts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/__init__.py

## Purpose
This pytest module verifies oldconfig asks about new choice values after dependencies make them visible.

## Important APIs, Types, and Functions
The test calls `conf.oldconfig('config', 'y')` and checks `stdout_contains('expected_stdout')`.

## Control Flow
The input `y` answers the prompt for new symbol `A`, after which choice prompt behavior is validated.

## State and Persistence
Initial config state is read from the local `config` file and copied to the temp directory.

## Dependencies and Integration Points
Depends on oldconfig prompting and expected stdout fixture.

## Risks and Edge Cases
Output is interaction-order sensitive.

## Test Signals
Pass means newly visible choices are prompted rather than silently defaulted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/config -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/config

## Purpose
This is the initial `.config` fragment for the `new_choice_with_dep` test.

## Important APIs, Types, and Functions
It sets `CONFIG_CHOICE_B=y`, leaves `CONFIG_CHOICE_D` unset, and sets `CONFIG_CHOICE_E=y`.

## Control Flow
The fixture represents a previous configuration before symbol `A` and dependency-related choice changes become visible.

## State and Persistence
It is copied to a temporary `.config` by `Conf.oldconfig()`.

## Dependencies and Integration Points
Used only by the paired pytest module.

## Risks and Edge Cases
The fragment intentionally lacks `CONFIG_A`, driving the new prompt path.

## Test Signals
Correct output depends on this starting state being preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/Kconfig

## Purpose
This fixture verifies choice values are not written to `.config` when the enclosing choice dependency is unmet.

## Important APIs, Types, and Functions
It defines bool `A` and a choice depending on `A` with members `CHOICE_B` and `CHOICE_C`.

## Control Flow
Starting from `CONFIG_A=y`, oldaskconfig answers `n` to turn off `A`; the choice becomes invisible and its member unset lines should not be emitted.

## State and Persistence
The paired `config` file provides the initial state.

## Dependencies and Integration Points
Targets symbol write flags and choice-value calculation in `symbol.c`.

## Risks and Edge Cases
Choice values have special computation paths, making them prone to writing stale `# CONFIG_... is not set` entries.

## Test Signals
The paired test compares generated config to `expected_config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/__init__.py

## Purpose
This pytest module checks that unmet dependency choice values are omitted from output.

## Important APIs, Types, and Functions
The test calls `conf.oldaskconfig('config', 'n')` and `conf.config_matches('expected_config')`.

## Control Flow
The input disables `A`, then the expected output verifies no unnecessary choice-member unset lines are written.

## State and Persistence
Initial state comes from the local `config` fixture.

## Dependencies and Integration Points
Depends on `Conf.oldaskconfig()` interactive behavior and config output comparison.

## Risks and Edge Cases
The docstring contains a typo `COFIG`, but the test behavior is unaffected.

## Test Signals
Pass guards a regression in choice write suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/config -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/config

## Purpose
This initial config enables `A` for the no-write-if-dependency-unmet test.

## Important APIs, Types, and Functions
It contains `CONFIG_A=y`.

## Control Flow
The paired test starts from this state and then answers `n` in oldaskconfig.

## State and Persistence
Copied as temporary `.config` by the test runner.

## Dependencies and Integration Points
Used by the local pytest module only.

## Risks and Edge Cases
Minimal fixture; any added choice member state would change the test intent.

## Test Signals
Pass depends on this fragment making the choice initially visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/Kconfig

## Purpose
This fixture tests Kconfig preprocessor built-in functions.

## Important APIs, Types, and Functions
It invokes `$(info,...)`, `$(warning-if,...)`, `$(error-if,...)`, `$(shell,...)`, `$(filename)`, and `$(lineno)`, and defines a shorthand `warning = $(warning-if,y,$(1))`.

## Control Flow
Parsing expands each built-in; info prints to stdout, warning prints to stderr with file/line, false `error-if` is a no-op, shell output is transformed by trimming trailing newlines and replacing internal newlines with spaces.

## State and Persistence
No config symbols are defined; output streams are the observable state.

## Dependencies and Integration Points
Targets `preprocess.c` built-ins and parser line/file tracking.

## Risks and Edge Cases
The shell command behavior depends on host `echo`/`printf` but uses simple POSIX-like commands.

## Test Signals
The paired test checks stdout and regex-matched stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/__init__.py

## Purpose
This pytest module validates built-in preprocessor output.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()`, checks stdout containment, and matches stderr with `expected_stderr`.

## Control Flow
The Kconfig parse completes successfully because the only `error-if` condition is false.

## State and Persistence
Only stdout/stderr are inspected.

## Dependencies and Integration Points
Depends on the built-in function fixture and expected output files.

## Risks and Edge Cases
Line-number expectations can change if the Kconfig fixture is edited.

## Test Signals
Pass means built-in function expansion and diagnostics remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/builtin_func/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/Kconfig

## Purpose
This fixture verifies recursive variable expansion is detected and rejected.

## Important APIs, Types, and Functions
It defines `X = $(Y)`, `Y = $(X)`, then expands `$(X)` through `$(info $(X))`.

## Control Flow
Because both variables are recursive, expansion enters a cycle and `variable_expand()` should raise a fatal preprocessor error.

## State and Persistence
No config state; failure is observable via stderr and exit status.

## Dependencies and Integration Points
Targets `preprocess.c` recursion tracking.

## Risks and Edge Cases
If recursion detection only catches direct self-reference, this indirect cycle would hang or hit depth limits.

## Test Signals
The paired test expects nonzero exit and matching stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/__init__.py

## Purpose
This pytest module verifies circular variable expansion fails cleanly.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()` and checks nonzero exit plus regex-matched stderr.

## Control Flow
The run should abort during preprocessing before configuration interaction.

## State and Persistence
No persistent state beyond captured stderr.

## Dependencies and Integration Points
Depends on `preprocess.c` error messages.

## Risks and Edge Cases
Expected regex must match file/line diagnostics.

## Test Signals
Pass means indirect recursive expansion is caught.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/Kconfig

## Purpose
This fixture validates escaping and literal handling in Kconfig preprocessor expressions.

## Important APIs, Types, and Functions
It defines helper variables `warning`, `comma`, `$`, `dollar`, `left_paren`, `Y`, and `unterminated`, then emits warnings containing commas, quotes, dollar signs, literal `$(`, and unbalanced parentheses.

## Control Flow
The parser expands simple and recursive variables and built-in warnings while preserving intended literal characters.

## State and Persistence
Observable state is stderr warning output.

## Dependencies and Integration Points
Targets `expand_dollar_with_args()`, argument splitting, simple vs recursive variable expansion, and warning built-ins.

## Risks and Edge Cases
Literal `$(` and unbalanced parentheses are especially important because naive parsing would treat them as unterminated references.

## Test Signals
The paired test expects successful parse and stderr matching expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/__init__.py

## Purpose
This pytest module validates preprocessor escaping behavior.

## Important APIs, Types, and Functions
The test runs `conf.oldaskconfig()` and matches stderr against `expected_stderr`.

## Control Flow
All warnings should be emitted, and parsing should exit successfully.

## State and Persistence
Only stderr output is checked.

## Dependencies and Integration Points
Depends on the escape Kconfig fixture and preprocessor implementation.

## Risks and Edge Cases
Text expectations are sensitive to quote and whitespace preservation.

## Test Signals
Pass means literal dollar/paren/comma handling remains correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/escape/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/Kconfig

## Purpose
This fixture tests Kconfig variable flavor semantics and user-defined functions.

## Important APIs, Types, and Functions
It exercises simple `:=`, recursive `=`, append `+=` for defined and undefined variables, variable references on the left-hand side, and user-defined function arguments through `greeting = $(1), my name is $(2).`.

## Control Flow
Warnings emit each expansion result after changing underlying variables, demonstrating when values are captured and when they are deferred.

## State and Persistence
Variable state exists only during parsing and is deleted by `variable_all_del()`.

## Dependencies and Integration Points
Targets parser assignment rules and `preprocess.c` variable expansion.

## Risks and Edge Cases
Undefined `+=` must become recursive, and missing function parameters must expand to empty strings without arity errors.

## Test Signals
The paired test matches stderr warnings to expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/__init__.py

## Purpose
This pytest module validates Kconfig variable and user-defined function semantics.

## Important APIs, Types, and Functions
It calls `conf.oldaskconfig()` and `conf.stderr_matches('expected_stderr')`.

## Control Flow
Parsing should complete successfully and emit deterministic warnings.

## State and Persistence
No persistent state beyond captured stderr.

## Dependencies and Integration Points
Depends on `preprocess.c` and expected stderr fixture.

## Risks and Edge Cases
Whitespace in appended variables and function output is significant.

## Test Signals
Pass means simple/recursive/append/function expansion matches expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/pytest.ini -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/pytest.ini

## Purpose
`pytest.ini` configures pytest discovery for Kconfig unit tests.

## Important APIs, Types, and Functions
It sets `addopts = --verbose` and `python_files = __init__.py`.

## Control Flow
Pytest imports each test package's `__init__.py` as the test module, avoiding duplicate test module basenames across directories.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Applies to the entire `scripts/kconfig/tests` pytest suite.

## Risks and Edge Cases
Because every test file is named `__init__.py`, changing this setting would make pytest miss the suite or collide imports.

## Test Signals
Running pytest from this directory should discover all package-level test modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/Kconfig

## Purpose
This fixture validates transitional symbol migration for all Kconfig value types and precedence cases.

## Important APIs, Types, and Functions
It defines `MODULES`, new symbols defaulting to old transitional symbols for bool, tristate, string, hex, and int, precedence variants where new user values should win, `OLD_WITH_HELP`, disabled/default edge cases, a conditional default case, and `REGULAR_OPTION`.

## Control Flow
`olddefconfig` should read old transitional values from an initial config, transfer values to new symbols through defaults, omit old transitional symbols from output, avoid prompting when transitional defaults provide values, and still prompt when conditional defaults are not visible.

## State and Persistence
The paired test uses an `initial_config` fixture outside this requested list and compares generated `.config` with expected output.

## Dependencies and Integration Points
Targets parser transitional syntax, symbol calculation in `symbol.c`, config reading/writing, and oldconfig prompting.

## Risks and Edge Cases
Transitional defaults must not override explicit new values, must handle all value types, and must not be written back. Conditional default visibility is a subtle prompt path.

## Test Signals
The paired test checks olddefconfig output and oldconfig stdout for conditional prompting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/__init__.py

## Purpose
This pytest module validates transitional symbol migration behavior.

## Important APIs, Types, and Functions
The test runs `conf.olddefconfig(dot_config='initial_config')`, checks `expected_config`, then runs `conf.oldconfig(dot_config='initial_config', in_keys='n\n')` and checks `expected_stdout`.

## Control Flow
The first run validates noninteractive migration. The second run validates prompt suppression for transitional defaults except the conditional-default case.

## State and Persistence
Initial state comes from `initial_config`; generated configs are isolated in temporary directories.

## Dependencies and Integration Points
Depends on config reader/writer, symbol defaults, and oldconfig prompting.

## Risks and Edge Cases
The test spans many symbol types, so failures need careful attribution to parser, symbol calculation, or writer behavior.

## Test Signals
Pass means transitional migration is working across types and precedence cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/util.c -->
# sources/distributed-fs/ceph-client/scripts/kconfig/util.c

## Purpose
`util.c` provides two shared Kconfig utility areas: tracking parsed Kconfig files to reject repeated includes, and implementing the `struct gstr` growable string helper used for generated dependency text and diagnostics.

## Important APIs, Types, and Functions
`file_hashtable` stores every parsed Kconfig file. `struct file` records a file name plus the parent file and line number of the first inclusion. `die_duplicated_include()` emits a repeated-include diagnostic and exits. `file_lookup()` canonicalizes/stores file names, recursively records parent names, rejects a second include with parent context, and appends the file to `autoconf_cmd`.

The growable string API is `str_new()`, `str_free()`, `str_append()`, `str_printf()`, and `str_get()`. `str_new()` starts with a 64 byte buffer, `str_append()` reallocates to exact required size when needed, and `str_printf()` formats through a 10000 byte stack buffer before appending.

## Control Flow
During scanning, each source file is passed to `file_lookup()`. First inclusion allocates and hashes a `struct file`; repeated inclusion through a parent path triggers `die_duplicated_include()`. Gstr helpers are leaf routines: callers allocate with `str_new()`, append strings/formatted text, read `gs.s` with `str_get()`, and release with `str_free()`.

## State and Persistence
Parsed file state persists in the process-global `file_hashtable` for the duration of the Kconfig parse. Each file entry stores heap memory for the flexible-array name. `str_printf(&autoconf_cmd, ...)` also persists include dependency lines in the global autoconf command string. Each `struct gstr` owns heap memory that callers must free.

## Dependencies and Integration Points
The file depends on `hash.h`, `hashtable.h`, `xalloc.h`, and `lkc.h`. It integrates with scanner include handling and with `parser.y`/`preprocess.c` through the shared `autoconf_cmd` and `struct gstr` API.

## Risks and Edge Cases
Repeated include handling exits immediately, so diagnostics must be precise enough for users to fix include loops or duplicate sources. `str_printf()` truncates any single formatted append over 9999 bytes before appending. `str_append()` grows to exactly the requested length, which is simple but may reallocate frequently for many small appends. There is no reset API for `file_hashtable`, so repeated parses in one process would retain file entries.

## Test Signals
The `err_repeated_inc` fixture directly tests repeated include diagnostics. Parser and preprocessor tests indirectly exercise `struct gstr` through `autoconf_cmd`, environment dependencies, warnings, and help/config output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kconfig/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kernel-doc -->
# sources/distributed-fs/ceph-client/scripts/kernel-doc

## Purpose
`kernel-doc` is the Python 3 frontend for extracting formatted kernel documentation comments from C source/header files and emitting ReST, man page, none, or YAML output.

## Important APIs, Types, and Functions
`main()` builds an `argparse` interface. `MsgFormatter` capitalizes log level names to match historic output. Important options include verbosity/debug, module name, line numbers, warning controls (`-Wreturn`, `-Wshort-desc`, `-Wall`, `-Werror`), export-file filtering, output modes (`--man`, `--rst`, `--none`, `--yaml`, `--kdoc-item`), symbol selection (`--export`, `--internal`, `--symbol`, `--nosymbol`), `--no-doc-sections`, and input files.

The script imports `KernelFiles`, `RestFormat`, and `ManFormat` from `scripts/lib/python/kdoc` after version checks.

## Control Flow
`main()` parses args, expands `--wall`, configures logging, checks Python version, imports parser/output libraries, chooses output style and YAML content, instantiates `KernelFiles`, parses files, emits messages from `kfiles.msg()`, and exits 0, 1/2 via argparse/abnormal errors, or 3 when `--werror` sees warnings.

## State and Persistence
The script writes documentation output to stdout or a YAML file path via the library. It does not persist state otherwise. `WERROR_RETURN_CODE` is 3.

## Dependencies and Integration Points
Depends on Python 3.6+ for normal operation and warns below 3.7. It modifies `sys.path` to load in-tree `kdoc` libraries. It is used by kernel documentation builds and by `kernel-doc --none` checks during compilation.

## Risks and Edge Cases
For Python older than 3.6, `--none` exits 0 to avoid breaking builds, while other modes abort. Output-mode exclusivity has an exception for YAML content selection. There are visible typos in help strings, but they do not affect behavior. Library import is delayed to keep old-Python failure graceful.

## Test Signals
Run with ReST, man, none, YAML, export/internal/symbol filtering, warnings, and `--werror`. Build-system use of `kernel-doc --none` is the critical integration check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/kernel-doc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ld-version.sh -->
# sources/distributed-fs/ceph-client/scripts/ld-version.sh

## Purpose
`ld-version.sh` identifies the linker implementation and verifies it meets the minimum kernel build version, printing a canonical name and numeric version.

## Important APIs, Types, and Functions
`get_canonical_version()` converts `x.y.z` to `10000*x + 100*y + z`. The script recognizes GNU ld as `BFD`, rejects GNU gold, and recognizes LLVM LLD as `LLD`. It calls `scripts/min-tool-version.sh` for minimum `binutils` or `llvm` versions.

## Control Flow
With `set -e`, the script captures the first line of `$@ --version`, tokenizes it, selects the linker family, strips non-version suffixes, canonicalizes detected and minimum versions, fails if too old, and prints `BFD <version>` or `LLD <version>`.

## State and Persistence
No persistent state; output is stdout and diagnostics are stderr.

## Dependencies and Integration Points
Called by Kbuild host/toolchain checks. Depends on shell arithmetic, the linker executable passed as arguments, and `min-tool-version.sh`.

## Risks and Edge Cases
Version parsing assumes recognizable first-line formats. Gold is explicitly unsupported. Distribution suffixes are stripped after digits/dots. The `[` expressions use `-a`, which is portable enough for `/bin/sh` here but can be brittle with unusual tokens.

## Test Signals
Test with GNU ld, gold, LLD, unknown commands, old-version mocks, and version strings with package suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ld-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/leaking_addresses.pl -->
# sources/distributed-fs/ceph-client/scripts/leaking_addresses.pl

## Purpose
`leaking_addresses.pl` scans a running system's `/proc`, `/sys`, and `dmesg` output for strings that look like leaked kernel addresses, with optional raw-output capture and summary reporting.

## Important APIs, Types, and Functions
Options include `--output-raw`, `--input-raw`, `--raw`, `--suppress-dmesg`, `--squash-by-path`, `--squash-by-filename`, `--kernel-config-file`, `--kallsyms`, `--32-bit`, `--page-offset-32-bit`, `--debug`, and `--help`.

Important functions are `help()`, `dprint()`, architecture helpers, `get_kernel_config_option()`, `option_from_file()`, `is_false_positive()`, `is_false_positive_32bit()`, `get_page_offset()`, `is_in_vsyscall_memory_region()`, `may_leak_address()`, `get_address_re()`, `get_x86_64_re()`, `parse_dmesg()`, `skip()`, `timed_parse_file()`, `parse_binary()`, `parse_file()`, `check_path_for_leaks()`, `walk()`, `format_output()`, `dump_raw_output()`, `parse_raw_file()`, `print_dmesg()`, `squash_by()`, and cache helpers.

## Control Flow
The script parses options, handles raw-input formatting mode, validates architecture support, optionally redirects stdout to a raw output file, optionally loads nonzero kallsyms addresses for binary scanning, scans `dmesg`, then recursively walks `/proc` and `/sys`. Each readable text file is scanned line by line; selected binary paths are ignored or scanned for packed kallsyms addresses. Formatting mode reads a prior raw file and either dumps raw output or prints summaries.

## State and Persistence
Runtime state includes skip lists, loaded kallsyms, architecture/config-derived regex decisions, and summary caches. Persistent outputs are optional raw result files. It reads live system state and kernel config sources such as `/proc/config.gz` or `/boot/config-*`.

## Dependencies and Integration Points
Depends on Perl modules `POSIX`, `File::Basename`, `File::Spec`, `File::Temp`, `Cwd`, `Term::ANSIColor`, `Getopt::Long`, `Config`, `bigint`, and `feature state`; external commands include `uname`, `dmesg`, and `gunzip`. It is a kernel hardening/debugging utility rather than a build dependency.

## Risks and Edge Cases
Scanning `/proc` and `/sys` can block or be expensive, so per-file alarm timeout is used. PID directories except `/proc/1` are skipped by design. Address regexes are architecture-specific and can generate false positives/negatives. The source contains a duplicated `push @dirs, $path;`, causing directories to be queued twice and potentially increasing scan cost. Binary scanning with large files and many kallsyms can be slow.

## Test Signals
Use raw input fixtures for summary modes, synthetic text containing known false positives and true positives, mocked config files for 32-bit/5-level paging, and limited directory trees for walk/skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/leaking_addresses.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/link-vmlinux.sh -->
# sources/distributed-fs/ceph-client/scripts/link-vmlinux.sh

## Purpose
`link-vmlinux.sh` performs final kernel image linking. It links `vmlinux`, handles kallsyms multi-pass generation, optional BTF generation and BTF ID patching, System.map generation, optional built-time table sorting, map-file generation, and cleanup.

## Important APIs, Types, and Functions
Inputs are `LD`, `KBUILD_LDFLAGS`, `LDFLAGS_vmlinux`, and output `VMLINUX`. Functions include `is_enabled()`, `info()`, `vmlinux_link()`, `kallsyms()`, `sysmap_and_kallsyms()`, `mksysmap()`, `sorttable()`, and `cleanup()`.

Important variables include `arch_vmlinux_o`, `btf_vmlinux_bin_o`, `btfids_vmlinux`, `kallsymso`, `strip_debug`, and `generate_map`. It checks many configs: `CONFIG_LTO_CLANG`, `CONFIG_X86_KERNEL_IBT`, `CONFIG_KLP_BUILD`, `CONFIG_GENERIC_BUILTIN_DTB`, `CONFIG_ARCH_WANTS_PRE_LINK_VMLINUX`, `CONFIG_KALLSYMS`, `CONFIG_DEBUG_INFO_BTF`, `CONFIG_KALLSYMS_ALL`, `CONFIG_64BIT`, `CONFIG_RELOCATABLE`, `CONFIG_VMLINUX_MAP`, and `CONFIG_BUILDTIME_TABLE_SORT`.

## Control Flow
After optional `clean`, it builds `init/version-timestamp.o`, selects architecture and BTF/kallsyms setup, optionally runs tracepoint update, creates a dummy kallsyms object, links temporary vmlinux images for kallsyms and/or BTF, runs `gen-btf.sh`, performs kallsyms passes until size stabilizes or an extra pass is requested, links final `vmlinux`, patches BTF IDs, writes `System.map`, sorts tables if configured, verifies final System.map against kallsyms, and writes a dependency file for fixdep.

## State and Persistence
It creates and removes temporary `.tmp_vmlinux*`, `.btf.*`, `vmlinux.map`, `System.map`, and `.${VMLINUX}.d` files in the object tree. Final persistent outputs are `vmlinux`, `System.map`, optional `vmlinux.map`, and dependency metadata.

## Dependencies and Integration Points
Called by Kbuild. Depends on linker/compiler variables, `${MAKE}`, `${CC}`, `${NM}`, `${RESOLVE_BTFIDS}`, `scripts/kallsyms`, `scripts/mksysmap`, `scripts/file-size.sh`, `scripts/gen-btf.sh`, `scripts/sorttable`, architecture pre-link objects, linker script `${KBUILD_LDS}`, and `include/config/auto.conf`.

## Risks and Edge Cases
Final link behavior is configuration-sensitive. Kallsyms convergence may need `KALLSYMS_EXTRA_PASS=1`; mismatch is a hard error. BTF failure suggests disabling `CONFIG_DEBUG_INFO_BTF`. User-mode Linux uses `CC` as linker with different flags/libs. Temporary files must be cleaned when switching configs. Any quoting mistake around flags/libs can affect unusual paths or flags.

## Test Signals
Kernel build configurations with and without KALLSYMS, BTF, LTO, KLP, built-in DTBs, UML, map generation, and table sorting validate this script. `clean` mode should remove its generated artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/link-vmlinux.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/Makefile -->
# sources/distributed-fs/ceph-client/scripts/livepatch/Makefile

## Purpose
This standalone Makefile supports livepatch developer tooling checks and is not part of kbuild proper.

## Important APIs, Types, and Functions
It defines `SHELLCHECK`, `SRCS := klp-build`, default target `help`, and target `check`.

## Control Flow
`make` defaults to `help`, printing available targets. `make check` verifies `shellcheck` was found and runs it over `klp-build` with optional `SHELLCHECK_OPTIONS`.

## State and Persistence
No persistent state; it only runs shellcheck.

## Dependencies and Integration Points
Depends on `shellcheck` for the check target and a sibling `klp-build` script. It is developer-facing under `scripts/livepatch`.

## Risks and Edge Cases
`which shellcheck` is used at parse time; PATH changes after make starts will not be reflected. The target only checks `klp-build`, not `fix-patch-lines` or `init.c`.

## Test Signals
Run `make -C scripts/livepatch help` and `make -C scripts/livepatch check` with and without shellcheck installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/fix-patch-lines -->
# sources/distributed-fs/ceph-client/scripts/livepatch/fix-patch-lines

## Purpose
`fix-patch-lines` is an awk filter that inserts `#line` directives into C/header patch hunks so compiled patched code preserves original `__LINE__` values where possible.

## Important APIs, Types, and Functions
It tracks `in_hunk`, `skip`, old-file current line `cur`, hunk end `last`, and `need_line_directive`. It recognizes `--- ` file headers, `@@` hunk headers, changed lines, context lines, and `\ No newline at end of file`.

## Control Flow
For non-C/header files, it prints lines unchanged. For C/header hunks, it parses the old-file line range from the hunk header. After each group of added/removed lines, before the next context line, it emits `+#line <cur>` into the patch, then resumes copying and updating the old-line counter.

## State and Persistence
All state is streaming awk state; no files are written directly by the script.

## Dependencies and Integration Points
Used in livepatch tooling pipelines that transform unified diffs before compilation. Depends on awk with `match(..., array)` support.

## Risks and Edge Cases
Only `.c` and `.h` files are processed. Hunk header parsing must match standard unified diff format. The inserted directive is an added line in the patch and may interact with style checks or unusual preprocessor contexts.

## Test Signals
Feed patches with additions, removals, mixed hunks, non-C files, one-line hunks, and no-newline markers; verify generated patched source reports original line numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/fix-patch-lines -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/init.c -->
# sources/distributed-fs/ceph-client/scripts/livepatch/init.c

## Purpose
`init.c` is generic init/exit code for a generated livepatch kernel module. It builds a runtime `struct klp_patch` from linker-provided `.init.klp_objects` metadata and enables the livepatch.

## Important APIs, Types, and Functions
Global `static struct klp_patch *patch` stores the enabled patch. `livepatch_mod_init()` uses `klp_find_section_by_name()`, `kzalloc_obj()`, `kzalloc()`, `memcpy()`, and `klp_enable_patch()`. `livepatch_mod_exit()` iterates with `klp_for_each_object_static()` and frees allocated function arrays, objects, and patch. Module metadata is set with `MODULE_LICENSE`, `MODULE_INFO(livepatch, "Y")`, and `MODULE_DESCRIPTION`.

## Control Flow
On init, the module locates `.init.klp_objects`, computes object count, rejects empty patches, allocates patch and object arrays with sentinel entries, allocates each object's function array with a sentinel, copies old function names, replacement function pointers, symbol positions, object names, and callbacks, sets `patch->mod` and `patch->objs`, chooses replace behavior based on `KLP_NO_REPLACE`, and calls `klp_enable_patch()`. Error paths free partially allocated state. On exit, the module frees per-object function arrays and top-level allocations.

## State and Persistence
Patch state persists for the lifetime of the loaded module in `patch` and in livepatch core after enablement. Allocated arrays are freed on module exit.

## Dependencies and Integration Points
Depends on Linux kernel livepatch APIs, generated section data types `struct klp_object_ext` and `struct klp_func_ext`, module loader section lookup, and generated livepatch build tooling.

## Risks and Edge Cases
The error path inside function allocation appears to free `objs[i].funcs` in a loop over `j < i`, likely intending `objs[j].funcs`; this would leak earlier allocations and may double-check as a bug. The code assumes `.init.klp_objects` size is an exact multiple of the metadata struct. `patch->states` is TODO. Replace behavior defaults true unless `KLP_NO_REPLACE` is defined.

## Test Signals
Build and load generated livepatch modules with zero objects, one object, multiple objects/functions, allocation failure injection, callbacks, replace/no-replace modes, and unload after enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/init.c -->
