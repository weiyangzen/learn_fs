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
